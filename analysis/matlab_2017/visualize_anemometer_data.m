clear;
clc;
%close all;

INPUT_FILE_NAME_USA1 = 'data_pn\input\2017-08-03_reduxUSA-01.txt.mat';
INPUT_FILE_NAME_USA2 = 'data_pn\input\2017-08-03_reduxUSA-02.txt.mat';


data_USA1 = load(INPUT_FILE_NAME_USA1);
fprintf('\nLoading: %s', INPUT_FILE_NAME_USA1);

data_USA2 = load(INPUT_FILE_NAME_USA2);
fprintf('\nLoading: %s', INPUT_FILE_NAME_USA2);

t_USA1 = data_USA1.wind.t;
vel_USA1 = data_USA1.wind.vel;
dir_USA1 = data_USA1.wind.dir;

alpha_rad_USA1 = circ_ang2rad(dir_USA1); 
alpha_bar_USA1 = mod(360+rad2deg(circ_mean(alpha_rad_USA1,vel_USA1.*vel_USA1)),360)
R_alpha_USA1 = circ_r(alpha_rad_USA1)
[s_alpha_USA1 s0_alpha_USA1] = circ_std(alpha_rad_USA1)
[S s] = circ_var(alpha_rad_USA1,vel_USA1.*vel_USA1)
vel_bar_USA1 = mean(vel_USA1)

t_USA2 = data_USA2.wind.t;
vel_USA2 = data_USA2.wind.vel;
dir_USA2 = data_USA2.wind.dir;

alpha_rad_USA2 = circ_ang2rad(dir_USA2); 
alpha_bar_USA2 = mod(360+rad2deg(circ_mean(alpha_rad_USA2,vel_USA2.*vel_USA2)),360)
R_alpha_USA2 = circ_r(alpha_rad_USA2)
[s_alpha_USA2 s0_alpha_USA2] = circ_std(alpha_rad_USA2)
[S s] = circ_var(alpha_rad_USA2,vel_USA2.*vel_USA2)
vel_bar_USA2 = mean(vel_USA2)

%% 2D plot
fprintf('\n2D plot wind direction\n');

h1 = figure('visible','on','units','normalized','outerposition',[0 0 1 1]);
hold on
grid on

xlabel('t [s]');
ylabel('Wind Direction [°]');
  
plot(t_USA1,dir_USA1);
plot(t_USA2,dir_USA2);

saveas(h1, [INPUT_FILE_NAME_USA1 '_anemometer_wind_dir.png']);

%% 2D plot
fprintf('\n2D plot wind speed\n');

h2 = figure('visible','on','units','normalized','outerposition',[0 0 1 1]);
hold on
grid on

xlabel('t [s]');
ylabel('Wind Speed [m/s]');

plot(t_USA1,vel_USA1);   
plot(t_USA2,vel_USA2);

saveas(h2, [INPUT_FILE_NAME_USA1 '_anemometer_wind_speed.png']);