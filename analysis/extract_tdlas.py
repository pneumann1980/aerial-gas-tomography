#!/usr/bin/env python3

import argparse
import collections
import os
import pickle
import sys
import pytz

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.spatial

import ast
import json
import mro_geodesy
import mro_geometry
from copter_data_loader import readCopterData

# parameter set
b_filter_1   = True #TDLAS filter 1: error code must be 1 and intensity above threshold
b_filter_2   = True #TDLAS filter 2: remove measurements for which we don't have RTK, gimbal and pose data
b_filter_3_1 = True #TDLAS filter 3.1: remove measurements that don't belong to a slice
b_filter_3_2 = True #TDLAS filter 3.2: remove positions that don't belong to a waypoint
b_filter_4   = True #TDLAS filter 4: altitude stability
b_filter_5   = True #TDLAS filter 5: yaw angle
b_filter_6   = True #TDLAS filter 6: the gimbal must be still during the whole measurement
b_filter_7   = True #TDLAS filter 7: the copter must be still during the whole measurement
b_filter_8_1 = True #TDLAS filter 8.1: filter potential interreflections
b_filter_8_2 = True #TDLAS filter 8.2: all, max, or median concentration
b_filter_8_3 = False #TDLAS filter 8.3: filter concentrations below the threshold

# parse the command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='Specify the copter data path')
parser.add_argument('-c', '--concentration', type=float, help='Specify the expected TDLAS concentration')
parser.add_argument('-o', '--out', help='Output directory for the pickles (default: copter data path)')
parser.add_argument('-m', '--method', choices=['max', 'all'], default='max',
                    help="'max': maximum concentration per measuring pose (filter 8.2, method (a)); "
                         "'all': all valid measurements (filter 8.2 disabled, method (b))")
args = parser.parse_args()

# method (b) of the ISOEN 2024 paper ('all valid data') = pipeline without filter 8.2
b_filter_8_2 = (args.method == 'max')

# check if the copter data path is provided as an argument
if args.file:
    copter_data_path = args.file
else:
    print("Please provide the copter data path using --file argument.")
    sys.exit(1)

# check if the expected TDLAS concentration is provided as an argument
if args.concentration is not None:
    expected_tdlas_concentration = args.concentration
else:
    print("Please provide the expected TDLAS concentration using --concentration argument.")
    sys.exit(1)

out_path = args.out if args.out else copter_data_path
os.makedirs(out_path, exist_ok=True)
filter_log = {'tdlas_raw': None}


IndexRange = collections.namedtuple('IndexRange', ['begin', 'end'])

def getLineSegments(data_series, max_delta, min_length=1):
    line_segments = []
    i = 0
    while i < len(data_series)-1:
        delta_next = data_series[i+1] - data_series[i]
        for j in range(i, len(data_series)-1):
            current_delta = data_series[j+1] - data_series[j]
            diff = abs(current_delta - delta_next)
            if diff > max_delta:
                j -= 1
                break
        j += 1
        if j-i >= min_length:
            line_segments.append(IndexRange(i, j))
        i = j
    
    return line_segments

def mergeLineSegments(segment1, segment2):
    merged_segments = []
    for r1 in segment1:
        for r2 in segment2:
            begin_candidate = max(r1.begin, r2.begin)
            end_candidate = min(r1.end, r2.end)
            if begin_candidate < end_candidate:
                merged_segments.append(IndexRange(begin_candidate, end_candidate))
    
    return merged_segments

def toPoint3D(item):
    return mro_geometry.Point3d(item.x, item.y, item.z)

#def getDataBetweenTimes(data_frame, t1, t2):
#    data_slice = data_frame.iloc[
#        data_frame.index.get_indexer([t1], method='pad')[0]:
#        data_frame.index.get_indexer([t2], method='backfill')[0] + 1
#    ]
#    return data_slice


x = readCopterData(copter_data_path, load_pose=True)

# create short hands for frequently used DataFrames
rtk = x.rtk
gimbal = x.gimbal
lidar = x.lidar

gimbal['angle_z_delta'] = gimbal.frame_angle_z - gimbal.angle_z

# only consider waypoints that were reached
waypoints = x.waypoints[x.waypoints.reached == 1].copy() # added copy() to suppress warning about copy vs. view

# use the middle waypoint as origin of the Cartesian coordinate system
# (here we probably want higher precision than at e.g. the take-off position)
cartesian_origin = waypoints.iloc[int(len(waypoints)/2)]
cartesian_origin_height = rtk.hfsl.min()
cartesian_converter = mro_geodesy.CartesianConverter(cartesian_origin.latitude,
                                                     cartesian_origin.longitude,
                                                     cartesian_origin_height)

# compute Cartesian coordinates for RTK and waypoints
rtk[['x', 'y', 'z']] = [cartesian_converter.toCartesian(lat, lon, height)
                        for (lat, lon, height)
                        in zip(rtk.latitude, rtk.longitude, rtk.hfsl)]
rtk['pos'] = [np.array([x, y, z])
              for (x, y, z) in zip(rtk.x, rtk.y, rtk.z)]
waypoints[['x', 'y', 'z']] = [cartesian_converter.toCartesian(lat, lon, height)
                              for (lat, lon, height)
                              in zip(waypoints.latitude, waypoints.longitude, waypoints.altitude)]

# extract waypoints forming slices
waypoint_x_segments = getLineSegments(waypoints.x, 0.05, 4) # 0.05 m tolerance, at least 4 waypoints for a slice
waypoint_y_segments = getLineSegments(waypoints.y, 0.05, 4)
waypoint_segments = mergeLineSegments(waypoint_x_segments, waypoint_y_segments)

# get slice planes
offset_3rd_point = mro_geometry.Point3d(0, 0, -10) # the z-axis should be in the planes
plane_points = [(toPoint3D(waypoints.iloc[segment.begin]),
                 toPoint3D(waypoints.iloc[segment.end]),
                 toPoint3D(waypoints.iloc[segment.begin]) + offset_3rd_point)
                for segment in waypoint_segments]

planes = [mro_geometry.Plane(*points) for points in plane_points]

# Assign the slice ID to each RTK position. The first slice ID is 0.
# If the RTK position does not belong to any slice, NO_SLICE is assigned.
plane_tolerance = 0.5 # [m]
NO_SLICE = -1
rtk['slice_id'] = [max([idx if abs(plane.distance(mro_geometry.Point3d(x, y, z))) < plane_tolerance else NO_SLICE
                        for idx, plane in enumerate(planes)])
                   for (x, y, z) in zip(rtk.x, rtk.y, rtk.z)]

# Assign the waypoint ID to each RTK position. The first waypoint ID is 0.
# If the RTK position does not belong to any waypoint, NO_WAYPOINT is assigned.
waypoint_tolerance = 0.5
NO_WAYPOINT = -1
waypoints['z'] = waypoints['z'] - (waypoints['z'].max() - rtk['z'].max())

rtk['waypoint_id'] = [min([(idx, np.linalg.norm(waypoint - (x, y, z))) for idx, waypoint in enumerate(waypoints[['x', 'y', 'z']].values) if np.linalg.norm(waypoint - (x, y, z)) <= waypoint_tolerance], key=lambda x: x[1], default=(NO_WAYPOINT, float('inf')))[0]
                      if slice_id != NO_SLICE else NO_WAYPOINT
                      for x, y, z, slice_id in zip(rtk['x'], rtk['y'], rtk['z'], rtk['slice_id'])]

tdlas = x.tdlas
filter_log['tdlas_raw'] = len(tdlas)

# TDLAS filter 1: error code must be 1 and intensity above threshold
if b_filter_1:
    old_len = len(tdlas)
    tdlas_min_intensity = 3 # [%]
    tdlas = tdlas[(tdlas.error_code == 1) & (tdlas.intensity >= tdlas_min_intensity)].copy()
    print(f'TDLAS filter 1: {old_len-len(tdlas)} measurements removed')
    filter_log['filter_1_removed'] = old_len-len(tdlas)

# compute times at which the measurements started
measurement_duration = pd.Timedelta(value=300, unit='milliseconds')
tdlas['t_measurement_start'] = tdlas.index - measurement_duration # tdlas.index = t_measurement_end

# TDLAS filter 2: remove measurements for which we don't have RTK, gimbal and pose data
if b_filter_2:
    old_len = len(tdlas)
    t_min = max(rtk.index.min(), gimbal.index.min(), x.pose.index.min())
    t_max = min(rtk.index.max(), gimbal.index.max(), x.pose.index.max())
    tdlas = tdlas[(tdlas.t_measurement_start >= t_min) & (tdlas.index <= t_max)]
    print(f'TDLAS filter 2: {old_len-len(tdlas)} measurements removed')
    filter_log['filter_2_removed'] = old_len-len(tdlas)

# get RTK data for each TDLAS measurement
#getDataBetweenTimes = (lambda data_frame, t1, t2:
#                       data_frame.iloc[data_frame.index.get_loc(t1, method='pad'):
#                                       data_frame.index.get_loc(t2, method='backfill')+1])
getDataBetweenTimes = (lambda data_frame, t1, t2:
                       data_frame.iloc[data_frame.index.get_indexer([t1], method='pad')[0]:
                                       data_frame.index.get_indexer([t2], method='backfill')[0]+1])

tdlas['rtk_data'] = [getDataBetweenTimes(rtk[['yaw', 'x', 'y', 'z', 'slice_id', 'waypoint_id']], t1, t2)
                     for (t1, t2)
                     in zip(tdlas.t_measurement_start, tdlas.index)]

# TDLAS filter 3.1: remove measurements that don't belong to a slice
if b_filter_3_1:
    old_len = len(tdlas)
    reduceSliceId = lambda series: series.iat[0] if (series == series.iat[0]).all() else NO_SLICE
    tdlas['slice_id'] = [reduceSliceId(rtk_data.slice_id) for rtk_data in tdlas.rtk_data]
    tdlas = tdlas[tdlas.slice_id != NO_SLICE]
    print(f'TDLAS filter 3.1: {old_len-len(tdlas)} measurements removed')
    filter_log['filter_3.1_removed'] = old_len-len(tdlas)

# TDLAS filter 3.2: remove positions that don't belong to a waypoint
if b_filter_3_2:
    old_len = len(tdlas)
    reduceWaypointId = lambda series: series.iat[0] if (series == series.iat[0]).all() else NO_WAYPOINT
    tdlas['waypoint_id'] = [reduceWaypointId(rtk_data.waypoint_id) for rtk_data in tdlas.rtk_data]
    tdlas = tdlas[tdlas.waypoint_id != NO_WAYPOINT]
    print(f'TDLAS filter 3.2: {old_len-len(tdlas)} measurements removed')
    filter_log['filter_3.2_removed'] = old_len-len(tdlas)

# TDLAS filter 4: altitude stability
if b_filter_4:
    old_len = len(tdlas)
    tdlas['altitude_std'] = [rtk_data.z.std() for rtk_data in tdlas.rtk_data]
    tdlas = tdlas[tdlas.altitude_std < 0.03]
    print(f'TDLAS filter 4: {old_len-len(tdlas)} measurements removed')
    filter_log['filter_4_removed'] = old_len-len(tdlas)

# get yaw setpoints
#tdlas['yaw_setpoint'] = [waypoints.iloc[waypoints.index.get_loc(i, method='pad')].yaw
#                         for i in tdlas.index]
tdlas['yaw_setpoint'] = [waypoints.asof(i).yaw for i in tdlas.index]

# TDLAS filter 5: yaw angle
tdlas['pose_yaw'] = [rtk_data.yaw.mean() for rtk_data in tdlas.rtk_data]

if b_filter_5:
    old_len = len(tdlas)
    tdlas = tdlas[(tdlas.pose_yaw - tdlas.yaw_setpoint).abs() < 2]
    print(f'TDLAS filter 5: {old_len-len(tdlas)} measurements removed')
    filter_log['filter_5_removed'] = old_len-len(tdlas)

# get gimbal data for each TDLAS measurement
tdlas['gimbal_data'] = [getDataBetweenTimes(gimbal[['angle_x', 'angle_y', 'angle_z_delta']], t1, t2)
                        for (t1, t2) in zip(tdlas.t_measurement_start, tdlas.index)]

# TDLAS filter 6: the gimbal must be still during the whole measurement
if b_filter_6:
    old_len = len(tdlas)
    max_gimbal_angle_std = 0.05
    tdlas['gimbal_angle_y_std'] = [gimbal_data.angle_y.std() for gimbal_data in tdlas.gimbal_data]
    tdlas = tdlas[tdlas.gimbal_angle_y_std < max_gimbal_angle_std]
    print(f'TDLAS filter 6: {old_len-len(tdlas)} measurements removed')
    filter_log['filter_6_removed'] = old_len-len(tdlas)

# get velocity data for each TDLAS measurement
tdlas['velocity_data'] = [getDataBetweenTimes(x.pose[['vx', 'vy', 'vz']], t1, t2)
                          for (t1, t2)
                          in zip(tdlas.t_measurement_start, tdlas.index)]

# TDLAS filter 7: the copter must be still during the whole measurement
if b_filter_7:
    old_len = len(tdlas)
    tdlas['velocity_mean_squared_sum'] = [np.square(df.mean().values).sum() for df in tdlas.velocity_data]
    tdlas = tdlas[tdlas.velocity_mean_squared_sum < 0.05]
    print(f'TDLAS filter 7: {old_len-len(tdlas)} measurements removed')
    filter_log['filter_7_removed'] = old_len-len(tdlas)

# compute measurement poses
tdlas['pos'] = [np.array([rtk_data.x.mean(),
                          rtk_data.y.mean(),
                          rtk_data.z.mean()])
                for rtk_data in tdlas.rtk_data]

tdlas['pos_x'] = [rtk_data.x.mean() for rtk_data in tdlas.rtk_data]
tdlas['pos_y'] = [rtk_data.y.mean() for rtk_data in tdlas.rtk_data]
tdlas['pos_z'] = [rtk_data.z.mean() for rtk_data in tdlas.rtk_data]

tdlas['gimbal_angle_y'] = [gimbal_data.angle_y.mean() for gimbal_data in tdlas.gimbal_data]
tdlas['gimbal_angle_z_delta'] = [gimbal_data.angle_z_delta.mean() for gimbal_data in tdlas.gimbal_data]

# Assign the measurement pose ID to each measurement pose. 
# If the measurement pose does not belong to any measurement, NO_MEASUREMENT_POSE is assigned.
NO_MEASUREMENT_POSE = -1
y_set_points = list(range(0, 181, 5))

# Iterate over each row and assign measurement_pose_id
tdlas['measurement_pose_id'] = [next((i for i, angle_y in enumerate(y_set_points) if abs(row['gimbal_angle_y'] - angle_y) <= 2), NO_MEASUREMENT_POSE) for _, row in tdlas.iterrows()]

# TDLAS filter 8.1: filter potential interreflections
if b_filter_8_1:
    old_len = len(tdlas)
    concentration_out_of_range = tdlas.loc[tdlas.concentration > 1.2*expected_tdlas_concentration, 'concentration'].copy()
    tdlas.loc[tdlas.concentration > 1.2*expected_tdlas_concentration, 'concentration'] = concentration_out_of_range / (concentration_out_of_range / expected_tdlas_concentration).round()
    print(f'TDLAS filter 8.1: {old_len-len(tdlas)} measurements removed')
    filter_log['filter_8.1_values_corrected'] = int(len(concentration_out_of_range))
    
# TDLAS filter 8.2: all, max, or median concentration
if b_filter_8_2:  
    if False:
        min_waypoint_id = tdlas['waypoint_id'].min()
        max_waypoint_id = tdlas['waypoint_id'].max()

        min_measurement_pose_id = tdlas['measurement_pose_id'].min()
        max_measurement_pose_id = tdlas['measurement_pose_id'].max()

        for waypoint_id in range(min_waypoint_id, max_waypoint_id+1):
            for measurement_pose_id in range(min_measurement_pose_id, max_measurement_pose_id+1):
                selected_rows = tdlas.loc[tdlas['waypoint_id'].isin([waypoint_id]) & tdlas['measurement_pose_id'].isin([measurement_pose_id])]

                if not selected_rows.empty:
                    print("waypoint_id:", waypoint_id, "measurement_pose_id:", measurement_pose_id)
                    print(selected_rows['concentration'].values)

                    # Plotting the histogram
                    plt.hist(selected_rows['concentration'], bins=10)
                    plt.xlabel('Concentration')
                    plt.ylabel('Frequency')
                    plt.title('Histogram')
                    plt.show()
                else:
                    print("No rows found for waypoint_id:", waypoint_id, "measurement_pose_id:", measurement_pose_id)
    
    old_len = len(tdlas)
    # calculate the mean for all values (except the objects)
    #idx = tdlas.groupby(['waypoint_id', 'measurement_pose_id'])['concentration'].transform('median') == tdlas['concentration'] 
    idx = tdlas.groupby(['waypoint_id', 'measurement_pose_id'])['concentration'].idxmax()
    tdlas = tdlas.loc[idx]
    
    print(f'TDLAS filter 8.2: {old_len-len(tdlas)} measurements removed')
    filter_log['filter_8.2_removed'] = old_len-len(tdlas)

# TDLAS filter 8.3: filter concentrations below the threshold
if b_filter_8_3:
    print('Filtering values below the threshold...')
    thr_concentration = 500
    
    old_len = len(tdlas)
    tdlas = tdlas.loc[tdlas.concentration >= thr_concentration].copy()
    print(f'TDLAS filter 8.3: {old_len-len(tdlas)} measurements removed')
    filter_log['filter_8.3_removed'] = old_len-len(tdlas)
    
print(f'Number of valid measurements: {len(tdlas)}')
filter_log['valid_measurements'] = len(tdlas)
filter_log['method'] = args.method
with open(os.path.join(out_path, 'filter_log.json'), 'w') as handle:
    json.dump(filter_log, handle, indent=2)

tdlas_pickle_path = os.path.join(out_path, 'tdlas.pkl')
tdlas.to_pickle(tdlas_pickle_path)
print('Saved TDLAS pickle to', tdlas_pickle_path)

rtk_pickle_path = os.path.join(out_path, 'rtk.pkl')
rtk.to_pickle(rtk_pickle_path)
print('Saved RTK pickle to', rtk_pickle_path)

planes_pickle_path = os.path.join(out_path, 'planes.pkl')
with open(planes_pickle_path, 'wb') as handle:
    pickle.dump(planes, handle, protocol=pickle.HIGHEST_PROTOCOL)
print('Saved planes pickle to', planes_pickle_path)

print('Done')
sys.exit()

# calculate the direction vector of the TDLAS measurement
tdlas['rotation'] = [scipy.spatial.transform.Rotation.from_euler('zy', [pose_yaw, gimbal_angle_y], degrees=True)
              for (pose_yaw, gimbal_angle_y) in zip(tdlas.pose_yaw, tdlas.gimbal_angle_y)]
tdlas['direction'] = [r.apply([1,0,0]) for r in tdlas.rotation]
tdlas['dx'] = [v[0] for v in tdlas.direction]
tdlas['dy'] = [v[1] for v in tdlas.direction]
tdlas['dz'] = [v[2] for v in tdlas.direction]

# calculate the ray length based on pose and direction data (instead of the laser rangefinder)
tdlas = tdlas[tdlas.dz > 1e-3] 
tdlas['ray_length'] = [-pose[2]/direction[2]
                       for (pose, direction)
                       in zip(tdlas.pose, tdlas.direction)] 

filtered_gimbal_index = list(set([t for gimbal_data in tdlas.gimbal_data for t in gimbal_data.index]))
filtered_gimbal = gimbal.loc[filtered_gimbal_index]

filtered_rtk_index = list(set([t for rtk_data in tdlas.rtk_data for t in rtk_data.index]))
filtered_rtk = rtk.loc[filtered_rtk_index]
    
plt.figure()
rtk.y.plot()
filtered_rtk.y.plot(style='.')
tdlas.error_code.plot(style='.')
plt.show()

plt.figure()
gimbal.angle_y.plot()
filtered_gimbal.angle_y.plot(style='.')
plt.show()

#plt.figure()
#tdlas.concentration.plot(style='.')
#plt.show()