clear;
clc;
%close all;

INPUT_FILE_NAME = 'data_pn\output\13_out.csv';
CELL_SIZE = 0.5;
LAMBDA = 1e-5;

data = dlmread(INPUT_FILE_NAME, ';');

fprintf('\nLoading: %s', INPUT_FILE_NAME);


start_x = data(:,1);
start_y = data(:,2);
end_x = data(:,3);
end_y = data(:,4);
ppmm = data(:,5);

% calculate boundaries
min_x = min(vertcat(min(start_x),min(end_x)))-0.5;
max_x = max(vertcat(max(start_x),max(end_x)))+0.5;
min_y = min(vertcat(min(start_y),min(end_y)))-0.5;
max_y = max(vertcat(max(start_y),max(end_y)))+0.5;

num_cells_x = ceil((max_x - min_x)./CELL_SIZE);
num_cells_y = ceil((max_y - min_y)./CELL_SIZE);

fprintf('\n ---> Min, Max X coordinates (%f,%f)',min_x,max_x);
fprintf('\n ---> Min, Max Y coordinates (%f,%f)',min_y,max_y);
fprintf('\n ---> Total cells %d',num_cells_x*num_cells_y);


cell_coords_x = min_x + CELL_SIZE*(0:num_cells_x-1);
cell_coords_y = min_y + CELL_SIZE*(0:num_cells_y-1);

tot_num_cells = num_cells_x * num_cells_y;
tot_num_measurements = size(ppmm,1);
A = sparse(tot_num_measurements,tot_num_cells);

%build the design matrix
for m = 1:tot_num_measurements
    A(m,:) = GetMeasurementPath(start_x(m),end_x(m),start_y(m),end_y(m),cell_coords_x,cell_coords_y);
	%A(m,:) = GetMeasurementCone(start_x(m),end_x(m),start_y(m),end_y(m),cell_coords_x,cell_coords_y);
    
    if (mod(m,100) == 0)
        fprintf('\n%d measurements processed!',m);
    end
end
%A(m,:) contains intersecting areas of each cell

[mean_map_vector, lm] = SolveQP(A,ppmm,LAMBDA);
[mean_map_vector,variance_map_vector,var_process_noise] = calculateGDM(mean_map_vector,A,ppmm,LAMBDA);
invalid_variance_entry = logical(lm > 1e-10);

[X, Y] = meshgrid(cell_coords_x,cell_coords_y);
mean_map = reshape(mean_map_vector,num_cells_y,num_cells_x);
variance_map = reshape(variance_map_vector,num_cells_y,num_cells_x);

%[Xq,Yq] = meshgrid(min_x:0.1:max_x,min_y:0.1:max_y);
%Vq = interp2(X,Y,mean_map,Xq,Yq,'linear');

h = figure('visible','on','units','normalized','position',[0 0 1 1]);
hold on
grid on
axis equal
xlim([min_x max_x]);
ylim([min_y max_y]);
%xlim([0 max_x]);
%ylim([0 max_y]);

subplot(2,1,1);
pcolor(X,Y,mean_map);
%pcolor(Xq,Yq,Vq);
daspect([1 1 1])
colorbar;
xlabel('y (m)');
ylabel('z (m)');
str_mean = ['Mean Map (c = ' num2str(CELL_SIZE,'%.1f') ' m)'];
title(str_mean);


subplot(2,1,2);
pcolor(X,Y,variance_map);
daspect([1 1 1])
colorbar;
str_var = ['Variance Map (c = ' num2str(CELL_SIZE,'%.1f') ' m)'];
title(str_var);
xlabel('y (m)');
ylabel('z (m)');

colormap hot;
colormap(flipud(colormap));

saveas(h, [INPUT_FILE_NAME '_c=' num2str(CELL_SIZE,'%.1f') 'm_CT.png']);

hold off

