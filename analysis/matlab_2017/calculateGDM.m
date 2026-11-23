function [mean_map_vector, variance_map_vector, var_process_noise] = calculateGDM(mean_map_vector,A,ppmm,lambda)
    %MEAN MAP
    
    %PROCESS NOISE
    [num_measurements, num_cells] = size(A);
    res = ppmm - A*mean_map_vector;
    %k = rank(full(A));
    var_process_noise = res'*res/abs(num_measurements-num_cells);
    
    %VARIANCE MAP
    inv_des = inv(A'*A + lambda*eye(num_cells));
    variance_map_vector = var_process_noise./diag(inv_des);
end