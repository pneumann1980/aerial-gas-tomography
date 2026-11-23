#!/usr/bin/env python3
# create *csv from data

import argparse
import os
import pickle
import sys
import time

import numpy as np
import pandas as pd
#import scipy.spatial

from copter_data_loader import readCopterData
import mro_geometry
import mro_kinematics

# parse the command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='Specify the copter data path')
parser.add_argument('-o', '--out', help='Directory with the pickles of extract_tdlas.py; CSV output is written there (default: copter data path)')
args = parser.parse_args()

# check if the copter data path is provided as an argument
if args.file:
    copter_data_path = args.file
else:
    print("Please provide the copter data path using --file argument.")
    sys.exit(1)

out_path = args.out if args.out else copter_data_path
    
def convertArrayToGeometryMsgsPoint(array):
    return geometry_msgs.msg.Point(x=array[0], y=array[1], z=array[2])

def convertArrayToGeometryMsgsQuaternion(array):
    return geometry_msgs.msg.Quaternion(x=array[0], y=array[1], z=array[2], w=array[3])

# read experiment data and preprocess pickles
x = readCopterData(copter_data_path)

tdlas_pickle_path = os.path.join(out_path, 'tdlas.pkl')
tdlas = pd.read_pickle(tdlas_pickle_path)

rtk_pickle_path = os.path.join(out_path, 'rtk.pkl')
rtk = pd.read_pickle(rtk_pickle_path)

planes_pickle_path = os.path.join(out_path, 'planes.pkl')
with open(planes_pickle_path, 'rb') as handle:
    planes = pickle.load(handle)

# create short hands for frequently used DataFrames
gimbal = x.gimbal

# get rotation matrices for each plane
v_base = np.array([1,0,0])
plane_rotations = [mro_kinematics.getRotationMatrixFrom2Vectors(v_base, plane.n0)
                   for plane in planes]
#print(plane_rotations)

iter_index = rtk.index.union(tdlas.index)
iter_index = iter_index.union(gimbal.index)

# extract unique slice IDs
slice_ids = np.unique(rtk['slice_id']).astype(int)

# filter slice IDs greater than or equal to 0
filtered_slice_ids = slice_ids[slice_ids >= 0]
print(f'Current filtered_slice_ids: {filtered_slice_ids} (dtype: {filtered_slice_ids.dtype})')

gimbal_angle_y = gimbal.angle_y.iloc[0]
gimbal_angle_z_delta = 0 # TODO

#data_out = np.zeros((len(tdlas), 5)) # TODO adjust for slices
#data_out_row = 0

# ToDo: make it more robust?
# assuming that the slice ids are in ascending order without gaps
data_out = []
data_out_row = []

for _ in filtered_slice_ids:
    data_out.append(np.zeros((len(tdlas), 5))) 
    data_out_row.append(0)

for idx in iter_index:
    if idx in rtk.index:
        current_rtk = rtk.loc[idx]
        #rotation = scipy.spatial.transform.Rotation.from_euler('ZY', [current_rtk.yaw, gimbal_angle_y], degrees=True)
        rot_z = mro_kinematics.getRotationMatrixZ(current_rtk.yaw, degrees=True)
        rot_y = mro_kinematics.getRotationMatrixY(gimbal_angle_y, degrees=True)
        #rotation = rot_z.dot(rot_y)
        rotation = rot_y.dot(rot_z)
        
    if idx in gimbal.index:
        current_gimbal = gimbal.loc[idx]
        gimbal_angle_y = current_gimbal.angle_y
        gimbal_angle_z_delta = current_gimbal.frame_angle_y - current_gimbal.angle_y
        
    if idx in tdlas.index:
        current_tdlas = tdlas.loc[idx]
        current_yaw = current_tdlas.pose_yaw
        #rotation = scipy.spatial.transform.Rotation.from_euler('ZY', [current_yaw, current_tdlas.gimbal_angle_y], degrees=True)
        #rotation = scipy.spatial.transform.Rotation.from_euler('yz', [current_tdlas.gimbal_angle_y, current_yaw], degrees=True)
        #direction = rotation.apply([1,0,0])
        rot_z = mro_kinematics.getRotationMatrixZ(current_yaw, degrees=True)
        rot_y = mro_kinematics.getRotationMatrixY(180.0-current_tdlas.gimbal_angle_y, degrees=True)
        #rot_y = mro_kinematics.getRotationMatrixY(current_tdlas.gimbal_angle_y, degrees=True)
        rotation = rot_z.dot(rot_y)
        direction = rotation.dot([-1,0,0])
        
        slice_id = int(current_tdlas['slice_id'])
        #print(f'Current TDLAS slice ID: {slice_id} (dtype: {slice_id.dtype})')
        
        # create for each slice a seperate file
        if slice_id >= 0 and abs(direction[2]) > 1e-6:
            #tdlas_pos = current_tdlas.pos
            tdlas_pos = mro_geometry.Point3d(current_tdlas.pos_x, current_tdlas.pos_y, current_tdlas.pos_z)
            
            ray_length = -tdlas_pos[2]/direction[2]
            if ray_length < 30 and ray_length > 1:
                in_plane_start_point = planes[slice_id].getProjectionPointOf(tdlas_pos)
                rotated_in_plane_start_point = plane_rotations[slice_id].T.dot(in_plane_start_point)
                
                end_point = tdlas_pos + ray_length * direction
                
                in_plane_end_point = planes[slice_id].getProjectionPointOf(end_point)
                rotated_in_plane_end_point = plane_rotations[slice_id].T.dot(in_plane_end_point)
                
                # replace with your desired threshold value
                x_threshold = float('inf') #10, if relevant
                if abs(rotated_in_plane_end_point[1]) <= x_threshold:
                    #data_out[data_out_row, :]
                    data_out[slice_id][data_out_row[slice_id], :] =  np.array([rotated_in_plane_start_point[1],
                                                                               rotated_in_plane_start_point[2],
                                                                               rotated_in_plane_end_point[1],
                                                                               rotated_in_plane_end_point[2],
                                                                               current_tdlas.concentration])
                    #data_out_row += 1
                    data_out_row[slice_id] += 1
                    
                #print(tdlas_pos)
                #print(end_point)
    
#data_out = data_out[0:data_out_row, :]
#data_out_path = os.path.join(copter_data_path, 'out.csv')
#np.savetxt(data_out_path, data_out, delimiter=';')
#print('Results written to', data_out_path)

for i in range(len(filtered_slice_ids)):
    slice_id = filtered_slice_ids[i]
    current_data_out = data_out[i][:data_out_row[i], :]
    data_out_path = os.path.join(out_path, f'out_slice_{slice_id}.csv')
    np.savetxt(data_out_path, current_data_out, delimiter=';')
    print('Results for slice', slice_id, 'written to', data_out_path)