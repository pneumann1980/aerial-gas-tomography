function drawBeamsAndPaths()
    CELL_SIZE = 1.0;
    
    %load beams and robot trajectory
    INPUT_FILE_NAME = 'data_pn\output\13_out.csv';
    %FILE_NAME = ['data_pn' filesep 'test.CSV'];
    data = dlmread(INPUT_FILE_NAME, ';');
    
    x_pos = data(:,1);
    y_pos = data(:,2);
    
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
    
    cell_coords_x = min_x + CELL_SIZE*(0:num_cells_x-1);
    cell_coords_y = min_y + CELL_SIZE*(0:num_cells_y-1);
    
    tot_num_cells = num_cells_x * num_cells_y;
    tot_num_measurements = size(ppmm,1);
    
    fprintf('\n ---> Min, Max X coordinates (%f,%f)',min_x,max_x);
    fprintf('\n ---> Min, Max Y coordinates (%f,%f)',min_y,max_y);
    fprintf('\n ---> Total cells %d',num_cells_x*num_cells_y);

    h = figure();%'visible','on','units','normalized','outerposition',[0 0 1 1]);
    hold on
    grid on
   
    xlabel('y (m)');
    ylabel('z (m)');
    
    %plot trajectory
    %plot(x_pos,y_pos,'r','LineWidth',0.8);    
    
    %build the design matrix
    for m = 1:tot_num_measurements        
        if (ppmm(m) < 50)
%            continue;
        end
        
%PN        curr_meas = GetMeasurementCone(start_x(m),end_x(m),start_y(m),end_y(m),cell_coords_x,cell_coords_y);
%          curr_meas = 100*logical(curr_meas > 0);
%PN        curr_meas = reshape(curr_meas,num_cells_y,num_cells_x);
        
%PN        [X, Y] = meshgrid(cell_coords_x,cell_coords_y);
%PN        pcolor(X, Y,curr_meas);
%PN        colormap(flipud(hot));
        
%PN        plot([start_x(m) ; end_x(m)],[start_y(m) ; end_y(m)]);
        fBeamLength = sqrt((start_x(m) - end_x(m))^2 + (start_y(m) - end_y(m))^2);
        fFinalDeviation = fBeamLength * 0.17/20; 	

        %conical beam, width 0.17 m at 20 m LMm-G
        %conical beam, width 0.56 m at 30 m LMm-G

        end_x_plus = end_x(m) - fFinalDeviation * (-(start_y(m) - end_y(m)))/fBeamLength;
        end_y_plus = end_y(m) - fFinalDeviation * (start_x(m) - end_x(m))/fBeamLength;

        end_x_minus = end_x(m) + fFinalDeviation * (-(start_y(m) - end_y(m)))/fBeamLength;
        end_y_minus = end_y(m) + fFinalDeviation * (start_x(m) - end_x(m))/fBeamLength;

        % define the triangle polygon
        fConeX = [start_x(m) end_x_plus end_x_minus start_x(m)];
        fConeY = [start_y(m) end_y_plus end_y_minus start_y(m)];
        fill(fConeX,fConeY,'r','EdgeColor','none','LineWidth',0.5)
        
%         if (mod(m,50) == 0)
%             cd('Temp');
%             file_name = sprintf('measurement_%05d.jpg',m);
%             saveas(h,file_name);
%             %print(h,'-djpeg','-r300',file_name);
%             cd('..');
%         end

        if (mod(m,100) == 0)
            fprintf('\n%d measurements processed!',m);
        end        
    end 
       
    daspect([1 1 1]);  
    xlim([min_x max_x]);
    ylim([min_y max_y]);
    axis equal
    
    saveas(h, [INPUT_FILE_NAME '_BEAMS.png']);
    
    fprintf('\n');
end