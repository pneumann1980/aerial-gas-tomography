function d = calculateDistance(lon1,lat1,lon2,lat2)
    lon1_rad = degtorad(lon1);
    lat1_rad = degtorad(lat1);  
    
    lon2_rad = degtorad(lon2);
    lat2_rad = degtorad(lat2);

    d = 2*asin(sqrt(sin((lat1_rad-lat2_rad)/2)^2+cos(lat1_rad)*cos(lat2_rad)*sin((lon1_rad-lon2_rad)/2)^2))*6378137;
end