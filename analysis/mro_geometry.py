import numpy as np

# function to calculate the indexes of beams intersecting a circle
def line_circle_intersection(beam_coordinates, circle_center, circle_radius):
    idx = []

    for i in range(len(beam_coordinates)):
        start_x, start_y, end_x, end_y = beam_coordinates.iloc[i][['sx', 'sy', 'ex', 'ey']]
        
        dx = end_x - start_x
        dy = end_y - start_y
        fx = start_x - circle_center[0]
        fy = start_y - circle_center[1]
        
        a = dx**2 + dy**2
        b = 2 * (dx * fx + dy * fy)
        c = fx**2 + fy**2 - circle_radius**2
        
        discriminant = b**2 - 4 * a * c
        
        if discriminant >= 0:
            idx.append(i)
            
    return idx

# function to calculate the intersecting area of a cell with a rectangle
def intersecting_area(cell_center, cell_size, rect_center, rect_size):
    # calculate the half sizes of the cell and rectangle
    cell_half_size = cell_size / 2
    rect_half_size = rect_size / 2

    # calculate the coordinates of the top-left and bottom-right corners of the cell
    cell_top_left = (cell_center[0] - cell_half_size, cell_center[1] + cell_half_size)
    cell_bottom_right = (cell_center[0] + cell_half_size, cell_center[1] - cell_half_size)

    # calculate the coordinates of the top-left and bottom-right corners of the rectangle
    rect_top_left = (rect_center[0] - rect_half_size, rect_center[1] + rect_half_size)
    rect_bottom_right = (rect_center[0] + rect_half_size, rect_center[1] - rect_half_size)

    # calculate the coordinates of the intersection area
    intersection_top_left = (max(cell_top_left[0], rect_top_left[0]), min(cell_top_left[1], rect_top_left[1]))
    intersection_bottom_right = (min(cell_bottom_right[0], rect_bottom_right[0]), max(cell_bottom_right[1], rect_bottom_right[1]))

    # calculate the width and height of the intersection area
    intersection_width = max(0, intersection_bottom_right[0] - intersection_top_left[0])
    intersection_height = max(0, intersection_top_left[1] - intersection_bottom_right[1])

    # calculate the intersecting area
    intersecting_area = intersection_width * intersection_height
    return intersecting_area

class Point3d(np.ndarray):
    def __new__(cls, x=0, y=0, z=0):
        return np.array([x, y, z]).view(cls)

class Plane():
    def __init__(self, p0, p1, p2):
        assert isinstance(p0, Point3d)
        assert isinstance(p1, Point3d)
        assert isinstance(p2, Point3d)
        n = np.cross(p1-p0, p2-p0)
        if np.dot(n, p0) >= 0:
            self.n0 = n / np.linalg.norm(n)
        else:
            self.n0 = -n / np.linalg.norm(n)
        self.d = np.dot(self.n0, p0)
    
    def __repr__(self):
        return 'n0=' + str(self.n0) + ' d=' + str(self.d)
    
    def distance(self, obj):
        #if isinstance(obj, Point3d):
        return np.dot(obj, self.n0) - self.d
        #else:
        #    raise ValueError('Type', type(obj), 'not supported')
    
    def getProjectionPointOf(self, obj):
        #if isinstance(obj, Point3d):
        r = self.d - np.dot(obj, self.n0)
        return obj + r*self.n0
        #else:
        #    raise ValueError('Type', type(obj), 'not supported')
