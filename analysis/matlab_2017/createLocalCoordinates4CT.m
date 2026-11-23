clear;
clc;
%close all;


%% Step 0: load file and variable initialization
fprintf('\nStep 0: load file and variable initialization\n');

R1 = 1;
C1 = 3;

NUM_SAT = 5;
MIN_ALT = 2;
MIN_PITCH = -125;
MAX_PITCH = -55;
MAX_DISTANCE = 12;

bVisualizeLine = true;
bVisualizeCone = false;

CONE_NUM_FACES = 6;
CONE_CLOSED = 0;
CONE_DRAW_EDGES = 0;
CONE_ALPHA = 0.3;

INPUT_FILE_NAME = 'data_pn\input\13.mat';
OUTPUT_FILE_NAME = 'data_pn\output\13_out.CSV';

INPUT_SETUP_FILE_NAME = 'data_pn\input\setup.CSV';
OUTPUT_SETUP_FILE_NAME = 'data_pn\output\setup_out.CSV';

setup = dlmread(INPUT_SETUP_FILE_NAME);
fprintf('\nLoading: %s', INPUT_SETUP_FILE_NAME);

lon_setup = setup(:,1);
lat_setup = setup(:,2);      
alt_setup = setup(:,3); 

tot_num_setup = size(lon_setup,1);

data = load(INPUT_FILE_NAME);                                              %dlmread(INPUT_FILE_NAME,';',R1,C1);
fprintf('\nLoading: %s\n', INPUT_FILE_NAME);


%Calculate heading from FlightDataCore quaternion
heading_FDC = [];

qz_FDC = data.structs.FlightDataCore.qz;
qy_FDC = data.structs.FlightDataCore.qy;
qw_FDC = data.structs.FlightDataCore.qw;
qx_FDC = data.structs.FlightDataCore.qx;

numTot_FDC = size(qx_FDC,2);
for i=1:numTot_FDC
    [yaw] = toEulerAngle(qw_FDC(1,i),qx_FDC(1,i),qy_FDC(1,i),qz_FDC(1,i));
    heading_FDC = [heading_FDC;rad2deg(yaw)];
end

time_FDC = double(data.structs.FlightDataCore.t');                         %*10^-6;
lat_FDC = double(data.structs.FlightDataCore.gps_info_lat')*10^-7;      
lon_FDC = double(data.structs.FlightDataCore.gps_info_lon')*10^-7;
alt_FDC = data.structs.FlightDataCore.gps_height';
sat_FDC = double(data.structs.FlightDataCore.gps_info_detail_usedGPS');

%Gimbal
time_FQO = data.structs.FilterQuatOutput.t;
pitch_FQO = data.structs.FilterQuatOutput.pitch';
roll_FQO = data.structs.FilterQuatOutput.roll';
yaw_FQO = data.structs.FilterQuatOutput.yaw';

numTot_FQO = size(data.structs.FilterQuatOutput.t,2);                      %retrieve timestamp of filter (forgotten in the fw_copter code)
for i=numTot_FQO:-1:1
   time_FQO(1,i) = data.structs.Adafruit_Acc_Measurement.t(1,i); 
end
time_FQO = double(time_FQO');

%LDS30
time_LDS30 = double(data.structs.LDS30_Measurement.t');
distance_LDS30 = data.structs.LDS30_Measurement.distance';
LDS30M_err = data.structs.LDS30_Measurement.error_code';

%LMmG
time_LMmG = double(data.structs.LMm_Measurement.t');
intensity_LMmG = data.structs.LMm_Measurement.intensity_percent';
ppmm_LMmG = data.structs.LMm_Measurement.concentration';
LMmG_err = data.structs.LMm_Measurement.error_code';

%time = data(:,4-C1);
%roll = data(:,19-C1);     
%pitch = data(:,20-C1);
%lat = data(:,24-C1);      
%lon = data(:,25-C1);
%alt = data(:,26-C1); 
%sat = data(:,28-C1);
%heading = data(:,29-C1);
%intensity = data(:,42-C1);
%ppmm = data(:,43-C1);
%LMmG_err = data(:,44-C1);
%distance = data(:,45-C1);
%LDS30M_err = data(:,48-C1);

time = time_LMmG;   
lat = interp1(time_FDC,lat_FDC,time_LMmG,'linear');      
lon = interp1(time_FDC,lon_FDC,time_LMmG,'linear'); 
alt = interp1(time_FDC,alt_FDC,time_LMmG,'linear');  
sat = interp1(time_FDC,sat_FDC,time_LMmG,'linear'); 
heading = mod(360+interp1(time_FDC,heading_FDC,time_LMmG,'linear'),360);
intensity = intensity_LMmG;
ppmm = ppmm_LMmG;
distance = interp1(time_LDS30,distance_LDS30,time_LMmG,'linear');

pitch = interp1(time_FQO,pitch_FQO,time_LMmG,'linear');
pitch = rad2deg(pitch)-180;                                                %correcting pitch angle

%Adafruit_Gyro
time_gyro = double(data.structs.Adafruit_Gyro_Measurement.t');             %remove data from gimbal up movement after sweep
gyro_y_tmp = data.structs.Adafruit_Gyro_Measurement.y';

GYRO_BIAS = 0.15;
idx = find(gyro_y_tmp>GYRO_BIAS);

idx_gyro_moving =[];
for j=1:size(ppmm,1)
    for i=1:size(idx,1)
        if(time_gyro(idx(i)) > time(j)-500 && time_gyro(idx(i)) < time(j)+500)
           idx_gyro_moving = [idx_gyro_moving;j]; 
        end
    end
end

tot_num_measurements = size(ppmm,1);

lat_start = [];      
lon_start = [];
alt_start = []; 

lat_end = [];      
lon_end = [];
alt_end = []; 

start_x = [];
start_y = [];
end_x = [];
end_y = [];
ppmm_res = [];

%% Step 1: calculate endpoints of the beams (GPS coordinates) 
fprintf('\nStep 1: calculate endpoints of the beams (GPS coordinates)\n');

for i = 10:tot_num_measurements     
   gyro_not_moving = size(find(idx_gyro_moving==i),1) == 0;
   
       if(pitch(i) > MIN_PITCH && pitch(i) < MAX_PITCH && LMmG_err(i) == 1 && gyro_not_moving)          
            angle = heading(i);
            if(pitch(i) < -90)
                angle = mod(heading(i)+180,360);                           %if pitch smaller than -90 (e.g., -120) than bearing +180 to calculate endpoint correctly!!!!
            end
            
            [a,b,c] = calculateTriangleProjection(pitch(i),distance(i),alt(i));                                   
         	[lon1,lat1,alt1] = calculateBeamEndpoint(lon(i),lat(i),alt(i)-b,a,angle);                            
            
            lat_start = [lat_start;lon(i)];      
            lon_start = [lon_start;lat(i)];
            alt_start = [alt_start;alt(i)]; 

            lat_end = [lat_end;lon1];      
            lon_end = [lon_end;lat1];
            %alt_end = [alt_end;alt1];
            alt_end = [alt_end;0];                                         %TODO: remove dirty hack!!!!!

            ppmm_res = [ppmm_res; ppmm(i)];
       end
   %end
end


%% Step 2: coordinate transformation (global --> local) 
fprintf('\nStep 2: coordinate transformation (global --> local)\n');

tot_num_valid_measurements = size(ppmm_res,1);

lat_tmp = [lat_end;lat_setup];
lon_tmp = [lon_end;lon_setup];

lat_ref = lat_setup(1);                                                    %Set source as coordinate origin
lon_ref = lon_setup(1);

[lat_max, idx] = max(lat_tmp);
lon_max = lon_tmp(idx);

b = -12;                                                                   %Setup declination              
fprintf('\ncalculated bearing: %f°\n',b);

for i = 1:tot_num_valid_measurements
    [x_s,y_s] = calculateLocalCoordinate(lon_start(i),lat_start(i),lon_ref,lat_ref,b);
    [x_e,y_e] = calculateLocalCoordinate(lon_end(i),lat_end(i),lon_ref,lat_ref,b);
                                                
    start_x = [start_x;x_s];
    start_y = [start_y;y_s];
    end_x = [end_x;x_e];
    end_y = [end_y;y_e];
end

x = [];
y = [];
z = [];

for i = 1:tot_num_setup
    [x_tmp,y_tmp] = calculateLocalCoordinate(lon_setup(i),lat_setup(i),lon_ref,lat_ref,b);
    
    x = [x;x_tmp];
    y = [y;y_tmp];
    z = [z;alt_setup(i)];
end

min_x = min(vertcat(min(start_x),min(end_x)));
max_x = max(vertcat(max(start_x),max(end_x)));
min_y = min(vertcat(min(start_y),min(end_y)));
max_y = max(vertcat(max(start_y),max(end_y)));
min_z = min(vertcat(min(alt_start),min(alt_end)));
max_z = max(vertcat(max(alt_start),max(alt_end)));

%idx = find(end_x);                                                        %plot and write only data to csv that is within the specified range
idx = find(end_x > 0.0 & end_x < 100.0);                                   %plot all

%dlmwrite(OUTPUT_FILE_NAME,horzcat(start_x,start_y,end_x,end_y,ppmm_res),'delimiter',';','precision','%.2f');
%dlmwrite(OUTPUT_FILE_NAME,horzcat(start_x,alt_start,end_x,alt_end,ppmm_res),'delimiter',';','precision','%.2f');  
dlmwrite(OUTPUT_FILE_NAME,horzcat(start_y(idx),alt_start(idx),end_y(idx),alt_end(idx),ppmm_res(idx)),'delimiter',';','precision','%.2f');   
dlmwrite(OUTPUT_SETUP_FILE_NAME,horzcat(x,y,z),'delimiter',';','precision','%.2f'); 


%% Step 3a: 2D plot
fprintf('\nStep 3a: 2D plot\n');

h1 = figure('visible','on','units','normalized','outerposition',[0 0 1 1]);
hold on
grid on

xlabel('y (m)');
ylabel('x (m)');

%plot trajectory
plot(start_y(idx),start_x(idx),'r','LineWidth',0.8); 

%beam end points
plot(end_y(idx),end_x(idx),'+');   

%Measuerement positions
for i = 12:tot_num_setup
    plot(y(i),x(i),'o','MarkerEdgeColor','k','MarkerFaceColor','y','MarkerSize',10);
end

%Measuerement positions
for i = 17:tot_num_setup
    plot(y(i),x(i),'o','MarkerEdgeColor','k','MarkerFaceColor','g','MarkerSize',10);
end

axis equal    
daspect([1 1 1]);
%xlim([min_x max_x]);
%ylim([min_y max_y]);

xlim([min_y max_y]);
ylim([min_x max_x]);

saveas(h1, [OUTPUT_FILE_NAME '_2D.png']);
 
%% Step 3b: 3D plot
fprintf('\nStep 3b: 3D plot\n'); 

h2 = figure('visible','on','units','normalized','outerposition',[0 0 1 1]);
hold on
grid on

view([-37.5 30]);
%xlim([min_x max_x]);
%ylim([min_y max_y]);
%zlim([min_z max_z]);
xlabel('x (m)');
ylabel('y (m)');
zlabel('z (m)');

plot3(start_x,start_y,alt_start,'r','LineWidth',3);

%build the design matrix
for i = 1:tot_num_valid_measurements
    if (ppmm_res(i) < 200)
        %continue;
    end
    
    if(bVisualizeLine)
        plot3([start_x(i);end_x(i)],[start_y(i);end_y(i)],[alt_start(i);alt_end(i)],'g','LineWidth',1);
    end
    
    if(bVisualizeCone)
        fBeamLength = sqrt((start_x(i)-end_x(i))^2 + (start_y(i)-end_y(i))^2 + (alt_start(i)-alt_end(i))^2);
        fFinalDeviation = fBeamLength * 0.17/20; 
        
        drawCone([start_x(i),start_y(i),alt_start(i)],[end_x(i),end_y(i),alt_end(i)],[0,fFinalDeviation],CONE_NUM_FACES,'g',CONE_CLOSED,CONE_DRAW_EDGES);
        alpha(CONE_ALPHA);
    end
    
    if (mod(i,100) == 0)
        fprintf('\n[Step 1] %d measurements processed!',i);
    end
end 

plot3(x(1),y(1),z(1),'o','MarkerEdgeColor','k','MarkerFaceColor','r','MarkerSize',10);

%Reference gassensor array
for i = 2:9 
    plot3(x(i),y(i),z(i),'o','MarkerEdgeColor','k','MarkerFaceColor','b','MarkerSize',10);
end

%Anemometer
for i = 10:11
    plot3(x(i),y(i),z(i),'o','MarkerEdgeColor','k','MarkerFaceColor','m','MarkerSize',10);
end

%Measuerement positions
for i = 12:tot_num_setup
    plot3(x(i),y(i),z(i),'o','MarkerEdgeColor','k','MarkerFaceColor','y','MarkerSize',10);
end

%axis equal
daspect([1 1 1]);
pbaspect([1 1 1]);

saveas(h2, [OUTPUT_FILE_NAME '_3D.png']);
fprintf('\nDone!\n');
