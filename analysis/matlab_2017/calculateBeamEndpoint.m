function [lon2,lat2,alt2] = calculateBeamEndpoint(lon1,lat1,alt1,distance,angle)
    lon1_rad = degtorad(lon1);
    lat1_rad = degtorad(lat1);
    alpha = degtorad(angle);
    
    r = distance / 6378137;

    lat2_rad = asin(sin(lat1_rad)*cos(r)+cos(lat1_rad)*sin(r)*cos(alpha));
    d_lon2 = atan2(sin(alpha)*sin(r)*cos(lat1_rad),cos(r)-sin(lat1_rad)*sin(lat2_rad));
    lon2_rad = mod(lon1_rad+d_lon2+pi,2*pi)-pi;

    lon2 = radtodeg(lon2_rad);
    lat2 = radtodeg(lat2_rad);
    alt2 = alt1;
end