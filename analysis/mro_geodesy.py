import numpy
import pygeodesy
import sympy

class CartesianConverter:
    def __init__(self, *args):
        if len(args) == 1:
            if not isinstance(args[0], pygeodesy.namedTuples.LatLon3Tuple):
                raise ValueError('Usage: CartesianConverter(LatLon3Tuple)')
            lat0 = args[0].lat
            lon0 = args[0].lon
            height0 = args[0].height
        elif len(args) == 3:
            if not all(isinstance(x, float) for x in args):
                raise ValueError('Usage: CartesianConverter(lat0, lon0, height0)')
            lat0 = args[0]
            lon0 = args[1]
            height0 = args[2]
        else:
            raise ValueError('CartesianConverter constructor arguments mismatch')
        
        self.converter = pygeodesy.deprecated.EcefCartesian(lat0, lon0, height0)
    
    def toCartesian(self, lat, lon, height):
        x, y, z, _, _, _, _, _, _ = self.converter.forward(lat, lon, height)
        return (x,y,z)
    
    def toCartesianFromLatLon3Tuple(self, coord: pygeodesy.namedTuples.LatLon3Tuple):
        return self.toCartesian(coord.lat, coord.lon, coord.height)
    
    def toCartesianAsNumpyArray(self, lat, lon, height):
        x, y, z, _, _, _, _, _, _ = self.converter.forward(lat, lon, height)
        return numpy.array([x,y,z])
    
    def toCartesianAsPoint3D(self, lat, lon, height):
        x, y, z, _, _, _, _, _, _ = self.converter.forward(lat, lon, height)
        return sympy.Point3D(x,y,z, evaluate=False)
    
    def toCartesianAsPoint3DFromLatLon3Tuple(self, coord: pygeodesy.namedTuples.LatLon3Tuple):
        return self.toCartesianAsPoint3D(coord.lat, coord.lon, coord.height)

def toLatLon3Tuple(data):
    return pygeodesy.namedTuples.LatLon3Tuple(data.latitude, data.longitude, data.altitude)
    #if hasattr(data, 'latitude') and hasattr(data, 'longitude') and hasattr(data, 'altitude'):
    #    return pygeodesy.named.LatLon3Tuple(data.latitude, data.longitude, data.altitude)
    #else:
    #    raise ValueError('Cannot convert', type(data), 'to LatLon3Tuple', data)
