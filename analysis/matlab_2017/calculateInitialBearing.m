function b = calculateInitialBearing(lon1,lat1,lon2,lat2)
    lon1_rad = degtorad(lon1);
    lat1_rad = degtorad(lat1);  
    
    lon2_rad = degtorad(lon2);
    lat2_rad = degtorad(lat2);
    
    y = sin(lon2_rad-lon1_rad)*cos(lat2_rad);
    x = cos(lat1_rad)*sin(lat2_rad)-sin(lat1_rad)*cos(lat2_rad)*cos(lon2_rad-lon1_rad);
    
    b = mod(radtodeg(atan2(y,x))+360,360);
end