clear;
clc;
close all;

%% Step 0: load file and variable initialization
fprintf('Step 0: load file and variable initialization"\n');

INPUT_FILE_NAME = 'data_pn\87_out.csv';
CELL_SIZE = 1;
LAMBDA = 1e-5;

MART_MU = 1.0;
ESPSILON = 0.0001;
Q = 500;

fprintf('\nLoading: %s', INPUT_FILE_NAME);
data = dlmread(INPUT_FILE_NAME, ';');


start_x = data(:,1);
start_y = data(:,2);
end_x = data(:,3);
end_y = data(:,4);
ppmm = data(:,5);

% calculate boundaries
min_x = min(vertcat(min(start_x),min(end_x)))-0.5;
max_x = max(vertcat(max(start_x),max(end_x)))+0.5;
min_y = min(vertcat(min(start_y),min(end_y)))-0.5;
max_y = max(vertcat(max(start_y),max(end_y)))+0.5;                         %needs modification..proper boundary calculation needed

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

ART_c_q_old = c_init; 
MART_c_q_old = c_init;
ASIRT_c_q_old = c_init;
MSIRT_c_q_old = c_init;
MLEM_c_q_old = c_init;

ART_c_q_new = ART_c_q_old;
MART_c_q_new = MART_c_q_old;
ASIRT_c_q_new = ASIRT_c_q_old;
MSIRT_c_q_new = MSIRT_c_q_old;
MLEM_c_q_new = MLEM_c_q_old;
    
ART_converge = [];
MART_converge = [];
ASIRT_converge = [];
MSIRT_converge = [];
MLEM_converge = [];

ART_residual_projection_error = [];
MART_residual_projection_error = [];
ASIRT_residual_projection_error = [];
MSIRT_residual_projection_error = [];
MLEM_residual_projection_error = [];

ART_b = true;
MART_b = true;
ASIRT_b = true;
MSIRT_b = true;
MLEM_b = true;


for q = 1:Q 
    fprintf('\nIteration: %d of %d',q,Q);
    
    ART_p_q = zeros(tot_num_measurements,1);        %reprojection values: calculated beam sum
    MART_p_q = zeros(tot_num_measurements,1);
    ASIRT_p_q = zeros(tot_num_measurements,1);
    MSIRT_p_q = zeros(tot_num_measurements,1);
    MLEM_p_q = zeros(tot_num_measurements,1);
    
    ART_tmp_c = zeros(tot_num_cells,1);
    MART_tmp_c = ones(tot_num_cells,1);                                    %CHANGED 
    ASIRT_tmp_c = zeros(tot_num_cells,1);
    MSIRT_tmp_c1 = zeros(tot_num_cells,1);
    MSIRT_tmp_c2 = zeros(tot_num_cells,1);
    MLEM_tmp_c = zeros(tot_num_cells,1);
    
    sum_s = zeros(tot_num_measurements,1);
    
    %% Step 2.1: for each iteration q calculate the reprojection values  
    for j = 1:tot_num_measurements     
        [x,y,s] = find(B(j,:));                                            %CHANGED from A to B                                                                                                                	
        
        for i = 1:size(y,2)
            if(ART_b) 
                ART_p_q(j) = ART_p_q(j) + s(i) * ART_c_q_old(y(i)); 
            end
            
            if(MART_b) 
                MART_p_q(j) = MART_p_q(j) + s(i) * MART_c_q_old(y(i)); 
            end
            
            if(ASIRT_b) 
                ASIRT_p_q(j) = ASIRT_p_q(j) + s(i) * ASIRT_c_q_old(y(i)); 
            end
            
            if(MSIRT_b) 
                MSIRT_p_q(j) = MSIRT_p_q(j) + s(i) * MSIRT_c_q_old(y(i)); 
            end
            
            if(MLEM_b) 
                MLEM_p_q(j) = MLEM_p_q(j) + s(i) * MLEM_c_q_old(y(i)); 
            end
            
            sum_s(j) = sum_s(j) + s(i);
        end
        
        if (mod(j,100) == 0)
            fprintf('\n[Step 2.1] %d measurements processed!',j);
        end
    end
    
    %% Step 2.2: calculate second sum of the equation
    for j = 1:tot_num_measurements
        for i = 1:tot_num_cells
            if(ART_b) 
                if(sum_s(j) > 0)
                    ART_tmp_c(i) = ART_tmp_c(i) + A(j,i) * (ppmm(j) - ART_p_q(j)) / sum_s(j); 
                end
            end
            
            if(MART_b)
                if (MART_p_q(j) > 0)
                    MART_tmp_c(i) = MART_tmp_c(i) * power(ppmm(j) / MART_p_q(j),MART_MU*A(j,i)); 
                end
            end
            
            if(ASIRT_b)
                if(sum_s(j) > 0)
                    ASIRT_tmp_c(i) = ASIRT_tmp_c(i) + A(j,i) * (ppmm(j) - ASIRT_p_q(j)) / sum_s(j); 
                end
            end
            
            if(MSIRT_b)
                if(sum_s(j) > 0)
                    MSIRT_tmp_c1(i) = MSIRT_tmp_c1(i) + A(j,i) * ppmm(j) / sum_s(j); 
                end
            end
            
            if(MSIRT_b) 
                if(sum_s(j) > 0)
                    MSIRT_tmp_c2(i) = MSIRT_tmp_c2(i) + A(j,i) * MSIRT_p_q(j) / sum_s(j); 
                end
            end
            
            if(MLEM_b) 
                if(MLEM_p_q(j) > 0)
                    MLEM_tmp_c(i) = MLEM_tmp_c(i) + (A(j,i) * ppmm(j)) / MLEM_p_q(j); 
                end
            end
        end   
        
        if (mod(j,100) == 0)
            fprintf('\n[Step 2.2] %d measurements processed!',j);
        end
    end
    
    %% Step 2.3: calculate final cell concentration
    for i = 1:tot_num_cells
        if(ART_b) 
        	ART_c_q_new(i) = max(ART_c_q_old(i) + ART_tmp_c(i),0); 
        end
            
      	if(MART_b) 
            MART_c_q_new(i) = MART_c_q_old(i) * MART_tmp_c(i); 
        end
            
      	if(ASIRT_b) 
            if(sum_A_ij(i) > 0)
            	ASIRT_c_q_new(i) = max(ASIRT_c_q_old(i) + ASIRT_tmp_c(i) / sum_A_ij(i),0); 
            end
        end
            
      	if(MSIRT_b) 
        	if(MSIRT_tmp_c2(i) > 0)
             	MSIRT_c_q_new(i) = MSIRT_c_q_old(i) * MSIRT_tmp_c1(i) / MSIRT_tmp_c2(i); 
        	end
        end
            
        if(MLEM_b) 
            if(sum_A_ij(i) > 0)
                MLEM_c_q_new(i) = (MLEM_c_q_old(i) / sum_A_ij(i)) * MLEM_tmp_c(i); 
            end
        end
    end
    
    ART_stop = max(abs(ART_c_q_new-ART_c_q_old));                          %stop criteria 
    MART_stop = max(abs(MART_c_q_new-MART_c_q_old));
    ASIRT_stop = max(abs(ASIRT_c_q_new-ASIRT_c_q_old));
    MSIRT_stop = max(abs(MSIRT_c_q_new-MSIRT_c_q_old));
    MLEM_stop = max(abs(MLEM_c_q_new-MLEM_c_q_old));
    
   if(ART_stop < ESPSILON) 
       ART_b = false;
   else
        ART_converge = [ART_converge; ART_stop];
        ART_residual_projection_error = [ART_residual_projection_error; rms(ppmm-ART_p_q)];
   end
    
   if(MART_stop < ESPSILON) 
       MART_b = false;
   else
        MART_converge = [MART_converge; MART_stop];
        MART_residual_projection_error = [MART_residual_projection_error; rms(ppmm-MART_p_q)];
   end
    
    if(ASIRT_stop < ESPSILON) 
        ASIRT_b = false;
    else
        ASIRT_converge = [ASIRT_converge; ASIRT_stop];
        ASIRT_residual_projection_error = [ASIRT_residual_projection_error; rms(ppmm-ASIRT_p_q)];
    end
    
    if(MSIRT_stop < ESPSILON) 
        MSIRT_b = false;
    else
        MSIRT_converge = [MSIRT_converge; MSIRT_stop];
        MSIRT_residual_projection_error = [MSIRT_residual_projection_error; rms(ppmm-MSIRT_p_q)];
    end
    
    if(MLEM_stop < ESPSILON) 
        MLEM_b = false;
    else
        MLEM_converge = [MLEM_converge; MLEM_stop];
        MLEM_residual_projection_error = [MLEM_residual_projection_error; rms(ppmm-MLEM_p_q)];
    end

    
    if(ART_b) 
        ART_c_q_old = ART_c_q_new; 
    end
    
    if(MART_b) 
        MART_c_q_old = MART_c_q_new; 
    end
    
    if(ASIRT_b) 
        ASIRT_c_q_old = ASIRT_c_q_new; 
    end
    
    if(MSIRT_b) 
        MSIRT_c_q_old = MSIRT_c_q_new; 
    end
    
    if(MLEM_b) 
        MLEM_c_q_old = MLEM_c_q_new; 
    end
end

fprintf('\n\nAlgorithms finished after:');
fprintf('\n%d iterations (ART)',size(ART_converge,1));
fprintf('\n%d iterations (MART)',size(MART_converge,1));
fprintf('\n%d iterations (ASIRT)',size(ASIRT_converge,1));
fprintf('\n%d iterations (MSIRT)',size(MSIRT_converge,1));
fprintf('\n%d iterations (MLEM)',size(MLEM_converge,1));


%% Step 3: calculate mean variance maps (from process noise)
fprintf('\n\nStep 3: calculate mean and variance maps\n');


%% Step 3.1: RAGT_cone
[RAGT_cone_mean_map_vector, lm] = SolveQP(A,ppmm,LAMBDA);
[RAGT_cone_mean_map_vector,RAGT_cone_variance_map_vector,RAGT_cone_var_process_noise] = calculateGDM(RAGT_cone_mean_map_vector,A,ppmm,LAMBDA);
RAGT_cone_invalid_variance_entry = logical(lm > 1e-10);

RAGT_cone_mean_map = reshape(RAGT_cone_mean_map_vector,num_cells_y,num_cells_x);
RAGT_cone_variance_map = reshape(RAGT_cone_variance_map_vector,num_cells_y,num_cells_x);


%% Step 3.2: RAGT_line
[RAGT_line_mean_map_vector, lm] = SolveQP(B,ppmm,LAMBDA);
[RAGT_line_mean_map_vector,RAGT_line_variance_map_vector,RAGT_line_var_process_noise] = calculateGDM(RAGT_line_mean_map_vector,B,ppmm,LAMBDA);
RAGT_line_invalid_variance_entry = logical(lm > 1e-10);

RAGT_line_mean_map = reshape(RAGT_line_mean_map_vector,num_cells_y,num_cells_x);
RAGT_line_variance_map = reshape(RAGT_line_variance_map_vector,num_cells_y,num_cells_x);


%% Step 3.3: ART
[ART_mean_map_vector,ART_variance_map_vector,ART_var_process_noise] = calculateGDM(ART_c_q_new,A,ppmm,LAMBDA);
ART_mean_map = reshape(ART_mean_map_vector,num_cells_y,num_cells_x);
ART_variance_map = reshape(ART_variance_map_vector,num_cells_y,num_cells_x);


%% Step 3.4: MART
[MART_mean_map_vector,MART_variance_map_vector,MART_var_process_noise] = calculateGDM(MART_c_q_new,A,ppmm,LAMBDA);
MART_mean_map = reshape(MART_mean_map_vector,num_cells_y,num_cells_x);
MART_variance_map = reshape(MART_variance_map_vector,num_cells_y,num_cells_x);


%% Step 3.5: ASIRT
[ASIRT_mean_map_vector,ASIRT_variance_map_vector,ASIRT_var_process_noise] = calculateGDM(ASIRT_c_q_new,A,ppmm,LAMBDA);
ASIRT_mean_map = reshape(ASIRT_mean_map_vector,num_cells_y,num_cells_x);
ASIRT_variance_map = reshape(ASIRT_variance_map_vector,num_cells_y,num_cells_x);


%% Step 3.6: MSIRT
[MSIRT_mean_map_vector,MSIRT_variance_map_vector,MSIRT_var_process_noise] = calculateGDM(MSIRT_c_q_new,A,ppmm,LAMBDA);
MSIRT_mean_map = reshape(MSIRT_mean_map_vector,num_cells_y,num_cells_x);
MSIRT_variance_map = reshape(MSIRT_variance_map_vector,num_cells_y,num_cells_x);


%% Step 3.7: MLEM
[MLEM_mean_map_vector,MLEM_variance_map_vector,MLEM_var_process_noise] = calculateGDM(MLEM_c_q_new,A,ppmm,LAMBDA);
MLEM_mean_map = reshape(MLEM_mean_map_vector,num_cells_y,num_cells_x);
MLEM_variance_map = reshape(MLEM_variance_map_vector,num_cells_y,num_cells_x);


%% Step 4: calculate Kullback Leibler distances and other metrics
fprintf('\n\nStep 4: calculate Kullback Leibler distances and other metrics\n');

%ART
[ART_MART_meanKLD ART_MART_varKLD] = calculateKullbackLeiblerDistance(ART_mean_map,ART_variance_map,MART_mean_map,MART_variance_map);
[ART_ASIRT_meanKLD ART_ASIRT_varKLD] = calculateKullbackLeiblerDistance(ART_mean_map,ART_variance_map,ASIRT_mean_map,ASIRT_variance_map);
[ART_MSIRT_meanKLD ART_MSIRT_varKLD] = calculateKullbackLeiblerDistance(ART_mean_map,ART_variance_map,MSIRT_mean_map,MSIRT_variance_map);
[ART_MLEM_meanKLD ART_MLEM_varKLD] = calculateKullbackLeiblerDistance(ART_mean_map,ART_variance_map,MLEM_mean_map,MLEM_variance_map);

[ART_RAGT_cone_meanKLD ART_RAGT_cone_varKLD] = calculateKullbackLeiblerDistance(ART_mean_map,ART_variance_map,RAGT_cone_mean_map,RAGT_cone_variance_map);
[ART_RAGT_line_meanKLD ART_RAGT_line_varKLD] = calculateKullbackLeiblerDistance(ART_mean_map,ART_variance_map,RAGT_line_mean_map,RAGT_line_variance_map);


%MART
[MART_ART_meanKLD MART_ART_varKLD] = calculateKullbackLeiblerDistance(MART_mean_map,MART_variance_map,ART_mean_map,ART_variance_map);
[MART_ASIRT_meanKLD MART_ASIRT_varKLD] = calculateKullbackLeiblerDistance(MART_mean_map,MART_variance_map,ASIRT_mean_map,ASIRT_variance_map);
[MART_MSIRT_meanKLD MART_MSIRT_varKLD] = calculateKullbackLeiblerDistance(MART_mean_map,MART_variance_map,MSIRT_mean_map,MSIRT_variance_map);
[MART_MLEM_meanKLD MART_MLEM_varKLD] = calculateKullbackLeiblerDistance(MART_mean_map,MART_variance_map,MLEM_mean_map,MLEM_variance_map);

[MART_RAGT_cone_meanKLD MART_RAGT_cone_varKLD] = calculateKullbackLeiblerDistance(MART_mean_map,MART_variance_map,RAGT_cone_mean_map,RAGT_cone_variance_map);
[MART_RAGT_line_meanKLD MART_RAGT_line_varKLD] = calculateKullbackLeiblerDistance(MART_mean_map,MART_variance_map,RAGT_line_mean_map,RAGT_line_variance_map);


%ASIRT
[ASIRT_ART_meanKLD ASIRT_ART_varKLD] = calculateKullbackLeiblerDistance(ASIRT_mean_map,ASIRT_variance_map,ART_mean_map,ART_variance_map);
[ASIRT_MART_meanKLD ASIRT_MART_varKLD] = calculateKullbackLeiblerDistance(ASIRT_mean_map,ASIRT_variance_map,MART_mean_map,MART_variance_map);
[ASIRT_MSIRT_meanKLD ASIRT_MSIRT_varKLD] = calculateKullbackLeiblerDistance(ASIRT_mean_map,ASIRT_variance_map,MSIRT_mean_map,MSIRT_variance_map);
[ASIRT_MLEM_meanKLD ASIRT_MLEM_varKLD] = calculateKullbackLeiblerDistance(ASIRT_mean_map,ASIRT_variance_map,MLEM_mean_map,MLEM_variance_map);

[ASIRT_RAGT_cone_meanKLD ASIRT_RAGT_cone_varKLD] = calculateKullbackLeiblerDistance(ASIRT_mean_map,ASIRT_variance_map,RAGT_cone_mean_map,RAGT_cone_variance_map);
[ASIRT_RAGT_line_meanKLD ASIRT_RAGT_line_varKLD] = calculateKullbackLeiblerDistance(ASIRT_mean_map,ASIRT_variance_map,RAGT_line_mean_map,RAGT_line_variance_map);


%MSIRT
[MSIRT_ART_meanKLD MSIRT_ART_varKLD] = calculateKullbackLeiblerDistance(MSIRT_mean_map,MSIRT_variance_map,ART_mean_map,ART_variance_map);
[MSIRT_MART_meanKLD MSIRT_MART_varKLD] = calculateKullbackLeiblerDistance(MSIRT_mean_map,MSIRT_variance_map,MART_mean_map,MART_variance_map);
[MSIRT_ASIRT_meanKLD MSIRT_ASIRT_varKLD] = calculateKullbackLeiblerDistance(MSIRT_mean_map,MSIRT_variance_map,ASIRT_mean_map,ASIRT_variance_map);
[MSIRT_MLEM_meanKLD MSIRT_MLEM_varKLD] = calculateKullbackLeiblerDistance(MSIRT_mean_map,MSIRT_variance_map,MLEM_mean_map,MLEM_variance_map);

[MSIRT_RAGT_cone_meanKLD MSIRT_RAGT_cone_varKLD] = calculateKullbackLeiblerDistance(MSIRT_mean_map,MSIRT_variance_map,RAGT_cone_mean_map,RAGT_cone_variance_map);
[MSIRT_RAGT_line_meanKLD MSIRT_RAGT_line_varKLD] = calculateKullbackLeiblerDistance(MSIRT_mean_map,MSIRT_variance_map,RAGT_line_mean_map,RAGT_line_variance_map);


%MLEM
[MLEM_ART_meanKLD MLEM_ART_varKLD] = calculateKullbackLeiblerDistance(MLEM_mean_map,MLEM_variance_map,ART_mean_map,ART_variance_map);
[MLEM_MART_meanKLD MLEM_MART_varKLD] = calculateKullbackLeiblerDistance(MLEM_mean_map,MLEM_variance_map,MART_mean_map,MART_variance_map);
[MLEM_ASIRT_meanKLD MLEM_ASIRT_varKLD] = calculateKullbackLeiblerDistance(MLEM_mean_map,MLEM_variance_map,ASIRT_mean_map,ASIRT_variance_map);
[MLEM_MSIRT_meanKLD MLEM_MSIRT_varKLD] = calculateKullbackLeiblerDistance(MLEM_mean_map,MLEM_variance_map,MSIRT_mean_map,MSIRT_variance_map);

[MLEM_RAGT_cone_meanKLD MLEM_RAGT_cone_varKLD] = calculateKullbackLeiblerDistance(MLEM_mean_map,MLEM_variance_map,RAGT_cone_mean_map,RAGT_cone_variance_map);
[MLEM_RAGT_line_meanKLD MLEM_RAGT_line_varKLD] = calculateKullbackLeiblerDistance(MLEM_mean_map,MLEM_variance_map,RAGT_line_mean_map,RAGT_line_variance_map);


fprintf('\n\nResidual projection errors (RMSE):');
fprintf('\n%d ppm x m (ART)',min(ART_residual_projection_error));
fprintf('\n%d ppm x m (MART)',min(MART_residual_projection_error));
fprintf('\n%d ppm x m (ASIRT)',min(ASIRT_residual_projection_error));
fprintf('\n%d ppm x m (MSIRT)',min(MSIRT_residual_projection_error));
fprintf('\n%d ppm x m (MLEM)',min(MLEM_residual_projection_error));


%% Step 5: draw maps
fprintf('\n\nStep 5: show maps\n');

[X, Y] = meshgrid(cell_coords_x,cell_coords_y);

drawMap(X,Y,RAGT_cone_mean_map,RAGT_cone_variance_map,'RAGT_{cone}',min_x,max_x,min_y,max_y);
drawMap(X,Y,RAGT_line_mean_map,RAGT_line_variance_map,'RAGT_{line}',min_x,max_x,min_y,max_y);

drawMap(X,Y,ART_mean_map,ART_variance_map,'ART',min_x,max_x,min_y,max_y);
drawMap(X,Y,MART_mean_map,MART_variance_map,'MART',min_x,max_x,min_y,max_y);
drawMap(X,Y,ASIRT_mean_map,ASIRT_variance_map,'ASIRT',min_x,max_x,min_y,max_y);
drawMap(X,Y,MSIRT_mean_map,MSIRT_variance_map,'MSIRT',min_x,max_x,min_y,max_y);
drawMap(X,Y,MLEM_mean_map,MLEM_variance_map,'MLEM',min_x,max_x,min_y,max_y);
