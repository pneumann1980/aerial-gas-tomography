clear;
clc;
%close all;


%% Step 0: load file and variable initialization
fprintf('Step 0: load file and variable initialization"\n');

INPUT_FILE_NAME = 'data_pn\output\13_out.csv';
CELL_SIZE = 0.5;
LAMBDA = 1e-5;

ESPSILON = 0.001;
Q = 2000;

data = dlmread(INPUT_FILE_NAME, ';');
fprintf('\nLoading: %s', INPUT_FILE_NAME);


start_x = data(:,1);
start_y = data(:,2);
end_x = data(:,3);
end_y = data(:,4);
ppmm = data(:,5);

tic;

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
B = sparse(tot_num_measurements,tot_num_cells);


%% Step 1: compute initial concentrations "smart guesses"
fprintf('\n\nStep 1: compute initial concentrations "smart guesses"\n');

sum_A_ij = zeros(tot_num_cells,1);                  %sum of intersection areas of all beams intersecting cell i
sum_p_j = zeros(tot_num_cells,1);                   %sum of the average concentrations for each cell c_i
k = zeros(tot_num_cells,1);                         %number of times cell c_i is hit by a beam

c_init = zeros(tot_num_cells,1);                    %initial concentration values


for j = 1:tot_num_measurements        
    A(j,:) = GetMeasurementCone(start_x(j),end_x(j),start_y(j),end_y(j),cell_coords_x,cell_coords_y);      %calculate intersecting areas A_ij of cells i that intersect with ray j and store their index in y
    B(j,:) = GetMeasurementPath(start_x(j),end_x(j),start_y(j),end_y(j),cell_coords_x,cell_coords_y);
    [x,y,s] = find(A(j,:));
        
    for i = 1:size(y,2)
        sum_p_j(y(i)) = sum_p_j(y(i)) + ppmm(j) / sqrt((end_x(j) - start_x(j))^2 + (end_y(j) - start_y(j))^2); 
                
        sum_A_ij(y(i)) = sum_A_ij(y(i)) + s(i); 	%--> equivalent to sum_A_ij = sum(A,1); after the for-loop
        k(y(i)) = k(y(i)) + 1;
    end
    
    if (mod(j,100) == 0)
            fprintf('\n[Step 1] %d measurements processed!',j);
    end
end

for i = 1:tot_num_cells                             %finalize "smart guesses" calculation
    if k(i) > 0
        c_init(i) = sum_p_j(i) / k(i);              
    end     
end  
    

%% Step 2: update
fprintf('\n\nStep 2: update\n');

c_q_old = c_init; 
c_q_new = c_q_old;

converge = [];
residual_projection_error = [];

for q = 1:Q 
    fprintf('\nIteration: %d of %d',q,Q);
    
    p_q = zeros(tot_num_measurements,1);            %reprojection values: calculated beam sum
    tmp_c = zeros(tot_num_cells,1);
    sum_s = zeros(tot_num_measurements,1);
    
    %% Step 2.1: for each iteration q calculate the reprojection values  
    for j = 1:tot_num_measurements     
        [x,y,s] = find(A(j,:));                                            %CHANGE from A to B, when not using Step 2.1.1                                                                                                                 	
        
        for i = 1:size(y,2)
            p_q(j) = p_q(j) + s(i) * c_q_old(y(i));     
            sum_s(j) = sum_s(j) + s(i);
        end
        
        if (mod(j,100) == 0)
            fprintf('\n[Step 2.1] %d measurements processed!',j);
        end
    end
   
    %% Step 2.1.1: correct values using Eq. 2b from IEEE Sensors paper 
    for j = 1:tot_num_measurements
     	p_q(j) = sqrt((end_x(j) - start_x(j))^2 + (end_y(j) - start_y(j))^2) * p_q(j) / sum_s(j);
    end
    
    %% Step 2.2: calculate second sum of the equation
    for j = 1:tot_num_measurements
        for i = 1:tot_num_cells
            %if p_q(j) > 0
                tmp_c(i) = tmp_c(i) + (A(j,i) * ppmm(j)) / p_q(j); 
            %end
        end   
        
        if (mod(j,100) == 0)
            fprintf('\n[Step 2.2] %d measurements processed!',j);
        end
    end
    
    %% Step 2.3: calculate final cell concentration
    for i = 1:tot_num_cells
        if sum_A_ij(i) > 0 
            c_q_new(i) = (c_q_old(i) / sum_A_ij(i)) * tmp_c(i);         
        end
    end
    
    stop = max(abs(c_q_new-c_q_old));
    
    if(stop < ESPSILON) 
    	break;
    else
        converge = [converge; stop];
     	residual_projection_error = [residual_projection_error; rms(ppmm-p_q)];
    end

    fprintf('\n\nResidual projection error (RMSE):');                      %added
    fprintf('\n%d ppm x m',min(residual_projection_error));

    c_q_old = c_q_new; 
end

fprintf('\n\n');
toc

fprintf('\nAlgorithm finished after:');
fprintf('\n%d iterations',size(converge,1));

fprintf('\n\nResidual projection error (RMSE):');
fprintf('\n%d ppm x m',min(residual_projection_error));


%% Step 3: calculate variance map from process noise
fprintf('\n\nStep 3: calculate variance map\n');

%MEAN MAP
mean_map_vector = c_q_new;

%PROCESS NOISE
[num_measurements, num_cells] = size(A);
res = ppmm - A*mean_map_vector;
%k = rank(full(A));
var_process_noise = res'*res/(num_measurements - num_cells);
    
%VARIANCE MAP
inv_des = inv(A'*A + LAMBDA*eye(num_cells));
variance_map_vector = var_process_noise./diag(inv_des);


%% Step 4: done!
fprintf('\n\nStep 4: show map --> done!\n');

[X, Y] = meshgrid(cell_coords_x,cell_coords_y);
mean_map = reshape(mean_map_vector,num_cells_y,num_cells_x);
variance_map = reshape(variance_map_vector,num_cells_y,num_cells_x);

drawMap(X,Y,mean_map,variance_map,'MLEM',min_x,max_x,min_y,max_y);