function measurement_path = GetMeasurementCone(start_x,end_x,start_y,end_y,cell_coords_x,cell_coords_y)

%% Step 1: compute the new end vertices of the cone by approximating it by a triangle

fBeamLength = sqrt((start_x - end_x)^2 + (start_y - end_y)^2);
fFinalDeviation = fBeamLength * 0.17/20; 	

%conical beam, width 0.17 m at 20 m LMm-G
%conical beam, width 0.56 m at 30 m RMLD

end_x_plus = end_x - fFinalDeviation * (-(start_y - end_y))/fBeamLength;
end_y_plus = end_y - fFinalDeviation * (start_x - end_x)/fBeamLength;

end_x_minus = end_x + fFinalDeviation * (-(start_y - end_y))/fBeamLength;
end_y_minus = end_y + fFinalDeviation * (start_x - end_x)/fBeamLength;

% define the triangle polygon
fConeX = [start_x end_x_plus end_x_minus start_x];
fConeY = [start_y end_y_plus end_y_minus start_y];

%% Step 2: intersect cone polygon with grid cell polygon and compute the area of the intersection

cellsize = cell_coords_x(2) - cell_coords_x(1);
measurement_path = zeros(1,(length(cell_coords_x))*(length(cell_coords_y)));

for i = 1:length(cell_coords_x)
    x_pos = cell_coords_x(i);
    areas = zeros(length(cell_coords_y),1);
    for j = 1:length(cell_coords_y)    %parfor          
        y_pos = cell_coords_y(j);        
        % define the cell polygon
        fCellX = [(x_pos) (x_pos) (x_pos + cellsize) (x_pos + cellsize) (x_pos)];
        fCellY = [(y_pos) (y_pos + cellsize) (y_pos + cellsize) (y_pos) (y_pos)];

        % compute intersection and area
        [fInterX, fInterY] = polybool('intersection',fConeX, fConeY, fCellX, fCellY);
        if(isempty(fInterX))
           areas(j) = 0;
         else
           areas(j) = polyarea(fInterX, fInterY);
        end
    end % for j
    
    for j = 1:length(cell_coords_y) 
        measurement_path(j + (i-1)*length(cell_coords_y)) = areas(j);
    end
end % for i

measurement_path = sparse(measurement_path);

% for i = 1:length(cell_coords_x)
%     x_pos = cell_coords_x(i);
%     for j = 1:length(cell_coords_y)        
%         y_pos = cell_coords_y(j);        
%         % define the cell polygon
%         fCellX = [(x_pos) (x_pos) (x_pos + cellsize) (x_pos + cellsize) (x_pos)];
%         fCellY = [(y_pos) (y_pos + cellsize) (y_pos + cellsize) (y_pos) (y_pos)];
%         % compute intersection and area
%         [fInterX, fInterY] = polybool('intersection',fConeX, fConeY, fCellX, fCellY);
%         measurement_path(j + (i-1)*length(cell_coords_y)) = polyarea(fInterX, fInterY);
%     end % for j
% end % for i
