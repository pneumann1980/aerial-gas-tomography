import collections
import json
import os
import pandas as pd

def loadTabularData(filepath, column_names, sep='\t'):
    if not os.path.isfile(filepath):
        print('File does not exist:', filepath)
        return None
    
    data = pd.read_table(filepath, names=column_names, sep=sep)
    
    if data.empty:
        print('No measurements in', filepath)
        return None
    
    # parse Unix timestamp
    data.index = pd.to_datetime(data.index, unit='us', utc=True)
    
    return data

def loadCopterDataDjiGps5Hz(path):
    filepath = os.path.join(path, 'dji_gps_5hz.csv')
    column_names = ['t_dji_ms', 't_dji_ns', 'date', 'time',
                    'latitude', 'longitude', 'altitude',
                    'velocity_x', 'velocity_y', 'velocity_z',
                    'hdop', 'pdop', 'fix', 'gnss_status', 'hacc', 'sacc',
                    'used_gps', 'used_gln', 'nsv', 'gps_counter']
    return loadTabularData(filepath, column_names)

def loadCopterDataDjiGps50Hz(path):
    filepath = os.path.join(path, 'dji_gps_50hz.csv')
    column_names = ['t_dji_ms', 't_dji_ns',
                    'longitude', 'latitude', 'altitude',
                    'visible_satellite_number',
                    'signal_level', 'control_level']
    return loadTabularData(filepath, column_names)

def loadCopterDataDjiImuRaw(path):
    filepath = os.path.join(path, 'dji_imu_raw.csv')
    column_names = ['t', 't_dji_ms', 't_dji_ns',
                    'ax', 'ay', 'az',
                    'wx', 'wy', 'wz']
    return loadTabularData(filepath, column_names)

def loadCopterDataDjiPoseFused(path):
    filepath = os.path.join(path, 'dji_pose_fused.csv')
    column_names = ['t_dji_ms', 't_dji_ns', 'qw', 'qx', 'qy', 'qz',
                    'ax_ground', 'ay_ground', 'az_ground', # NEU frame?
                    'ax_body', 'ay_body', 'az_body', # FRU frame?
                    'vx', 'vy', 'vz', 'velocity_info', # NEU frame?
                    'wx', 'wy', 'wz', # NED frame?
                    'altitude', 'altitude_barometer']
    return loadTabularData(filepath, column_names)

def loadCopterDataDjiRtk(path):
    filepath = os.path.join(path, 'dji_rtk.csv')
    column_names = ['t_dji_ms', 't_dji_ns',
                    'longitude', 'latitude', 'hfsl', # hfsl = height from sea level
                    'vx', 'vy', 'vz', # NED
                    'yaw', 'position_info', 'yaw_info']
    return loadTabularData(filepath, column_names)

def loadCopterDataDjiStatus(path):
    filepath = os.path.join(path, 'dji_status.csv')
    column_names = ['t_dji_ms', 't_dji_ns',
                    'flight', 'display_mode', 'landing_gear', 'motor',
                    'battery_capacity', 'battery_voltage',
                    'battery_current', 'battery_percentage',
                    'control_mode',
                    'device_status', 'flight_status', 'vrc_status',
                    'rtk_connected', 'flight_anomaly']
    return loadTabularData(filepath, column_names)

def loadGimbalData(path):
    filepath = os.path.join(path, 'GimbalRealtimeData4.tsv')
    column_names = ['ax', 'ay', 'az', 'wx', 'wy', 'wz',
                    'serial_error_count', 'system_error', 'system_sub_error',
                    'rc_roll', 'rc_pitch', 'rc_yaw', 'rc_cmd',
                    'ext_fc_roll', 'ext_fc_pitch',
                    'angle_x', 'angle_y', 'angle_z',
                    'frame_angle_x', 'frame_angle_y', 'frame_angle_z',
                    'target_angle_x', 'target_angle_y', 'target_angle_z',
                    'cycle_time', 'i2c_error_count', 'battery_voltage',
                    'rt_data_flags', 'current_imu', 'current_profile',
                    'motor_power0', 'motor_power1', 'motor_power2',
                    'stator_rotor_angle0', 'stator_rotor_angle1', 'stator_rotor_angle2',
                    'balance_error0', 'balance_error1', 'balance_error2',
                    'current',
                    'mag0', 'mag1', 'mag2',
                    'imu_temperature', 'frame_imu_temperature',
                    'imu_g_error', 'imu_h_error',
                    'motor_out0', 'motor_out1', 'motor_out2',
                    'calib_mode', 'can_imu_ext_sens_error']
    #return loadTabularData(filepath, column_names, sep='\s+') # ignore tab at end of line
    gimbal_data = loadTabularData(filepath, column_names, sep='\s+') # ignore tab at end of line
    if gimbal_data is None:
        return None
    gimbal_data.sort_index(inplace=True)
    mask = gimbal_data.index.to_series().diff() > pd.Timedelta(value=1000, unit='microseconds')
    mask[0] = True # first element of diff() is NaN, so we manually need to keep it
    return gimbal_data[mask]

def loadLidarData(path):
    filepath = os.path.join(path, 'lidar.tsv')
    column_names = ['distance', 'signal_quality']
    return loadTabularData(filepath, column_names)

def loadTdlasData(path):
    filepath = os.path.join(path, 'tdlas.tsv')
    column_names = ['error_code', 'concentration', 'intensity']
    return loadTabularData(filepath, column_names)

def loadCopterActivity(path):
    filepath_activity_log = os.path.join(path, 'copter_activity.log')
    
    if not os.path.isfile(filepath_activity_log):
        print('File does not exist:', filepath_activity_log)
        return None
    
    with open(filepath_activity_log) as f:
        waypoint_list = []
        for line in f:
            json_line = json.loads(line)
            timestamp = pd.to_datetime(json_line['t'])
            if json_line['class'] == 'PilotWaypoint':
                position = json_line['position']
                properties = json_line['props']
                yaw_deg = float([kv['value'] for kv in properties if kv['key'] == 'yaw_deg'][0])
                waypoint_list.append([timestamp, position['latitude'],
                                      position['longitude'],
                                      position['altitude'], yaw_deg, 0])
            elif json_line['class'] == 'ReachedWaypoint':
                wp_copy = waypoint_list[-1][:]
                wp_copy[0] = timestamp
                wp_copy[-1] = 1
                waypoint_list.append(wp_copy)
        
        waypoints = pd.DataFrame(waypoint_list,
                                 columns=['t',
                                          'latitude', 'longitude', 'altitude',
                                          'yaw', 'reached']).set_index('t')
    
    return waypoints

def readCopterData(path, load_imu = False, load_pose = False):
    CopterData = collections.namedtuple('CopterData',
                                        ['gps5', 'gps50', 'imu', 'pose',
                                         'rtk', 'status', 'gimbal', 'lidar',
                                         'tdlas', 'waypoints'])
    
    gps5 = loadCopterDataDjiGps5Hz(path)
    gps50 = loadCopterDataDjiGps50Hz(path)
    imu = loadCopterDataDjiImuRaw(path) if load_imu else None
    pose = loadCopterDataDjiPoseFused(path) if load_pose else None
    rtk = loadCopterDataDjiRtk(path)
    status = loadCopterDataDjiStatus(path)
    
    gimbal = loadGimbalData(path)
    lidar = loadLidarData(path)
    tdlas = loadTdlasData(path)
    
    waypoints = loadCopterActivity(path)
    
    data = CopterData(gps5 = gps5,
                      gps50 = gps50,
                      imu = imu,
                      pose = pose,
                      rtk = rtk,
                      status = status,
                      gimbal = gimbal,
                      lidar = lidar,
                      tdlas = tdlas,
                      waypoints = waypoints)
    return data