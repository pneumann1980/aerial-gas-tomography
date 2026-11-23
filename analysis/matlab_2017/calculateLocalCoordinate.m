function [x,y] = calculateLocalCoordinate(lon1,lat1,lon_ref,lat_ref,angle)
%     d = calculateDistance(lon1,lat1,lon_ref,lat_ref);
%     alpha = mod(calculateInitialBearing(lon1,lat1,lon_ref,lat_ref)-angle+450,360)-180;    
% 	
%     if(abs(alpha)==180.0 || abs(alpha)==90.0 || alpha==0.0)                    
%         if(abs(alpha)==90.0)
%          	x = sign(alpha)*d;
%            	y = 0;
%         else
%             x = 0;
%             y = d;
%             
%             if(alpha~=0)
%                y = -y; 
%             end
%         end
%     else
%         beta = 90-abs(alpha);
%      	alpha_rad = degtorad(alpha);
%         beta_rad = degtorad(beta);
% 
%      	x = d*sin(alpha_rad)/sin(pi/2);
%      	y = d*sin(beta_rad)/sin(pi/2);
%     end

    %Decimaldegree to UTM coordinates
    [N_ref,E_ref] = ell2utm(deg2rad(lon_ref),deg2rad(lat_ref));
    [N,E] = ell2utm(deg2rad(lon1),deg2rad(lat1));
    
    %Set reference point as coordinate origin
    x = E-E_ref;
    y = N-N_ref;
    
    %Rotation around the z-axis
    alpha = deg2rad(angle);
    x = cos(alpha)*x-sin(alpha)*y;
    y = sin(alpha)*x+cos(alpha)*y;
end