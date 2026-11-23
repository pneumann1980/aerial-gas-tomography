#!/usr/bin/env python3

import argparse
import os
import numpy as np
import pandas as pd
import scipy.sparse as sp
import matplotlib.pyplot as plt

from mro_tomography import *
from scipy.sparse import lil_matrix
from tabulate import tabulate


# parse the command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='Specify the copter data path')
parser.add_argument('-cs', '--cell_size', type=float, default=0.5, help='Specify the cell size')
parser.add_argument('-l', '--lambda_value', type=float, default=1e-5, help='Specify lambda')
parser.add_argument('-mo', '--measurement_option', choices=['path', 'cone', 'cone2'], default='path', help='Specify the measurement option')
parser.add_argument('-c', '--concentration', type=float, default=0, help='Specify the expected TDLAS concentration')
args = parser.parse_args()

# check if the copter data path is provided as an argument
if args.file:
    copter_data_path = args.file
else:
    print("Please provide the copter data path using --file argument.")
    sys.exit(1)
    
# set the parameters based on command-line arguments
_lambda = args.lambda_value
_cell_size = args.cell_size
_measurement_option = args.measurement_option
_expected_tdlas_concentration = args.concentration

_epsilon = 0.0001;
Q = 2000;

# file path
#data_path = os.path.join(copter_data_path, 'out.csv')

# find all 'out_slice_X.csv' files in the folder
for file in os.listdir(copter_data_path):
    if file.startswith('out_slice_') and file.endswith('.csv'):
        data_path = os.path.join(copter_data_path, file)
        
        # extract the slice number from the file name
        slice_id = int(file.split('_')[2].split('.')[0])
        
        # print the file path and slice number
        print("File:", data_path)
        print("Slice ID:", slice_id)
        
        # load data from CSV
        data = pd.read_csv(data_path, delimiter=';', header=None)
        start_x = data.iloc[:, 0]
        start_y = data.iloc[:, 1]
        end_x = data.iloc[:, 2]
        end_y = data.iloc[:, 3]
        ppmm = data.iloc[:, 4]

        # calculate boundaries
        min_x = min(start_x.min(), end_x.min()) - 0.5
        max_x = max(start_x.max(), end_x.max()) + 0.5
        min_y = min(start_y.min(), end_y.min()) - 0.5
        max_y = max(start_y.max(), end_y.max()) + 0.5

        num_cells_x = int(np.ceil((max_x - min_x) / _cell_size))
        num_cells_y = int(np.ceil((max_y - min_y) / _cell_size))

        cell_coords_x = min_x + _cell_size * np.arange(num_cells_x)
        cell_coords_y = min_y + _cell_size * np.arange(num_cells_y)
        #print(cell_coords_x)
        #print(cell_coords_y)

        tot_num_cells = num_cells_x * num_cells_y
        tot_num_measurements = ppmm.shape[0]
        A = lil_matrix((tot_num_measurements, tot_num_cells))

        print(f'Min, Max X coordinates: ({min_x}, {max_x})')
        print(f'Min, Max Y coordinates: ({min_y}, {max_y})')
        print(f'Total cells: {num_cells_x * num_cells_y}')
        print(f'Total measurements: {tot_num_measurements}')
        
        # resample the integral measurements based on the novel cone model
        if _measurement_option == "cone2":
            # initialize variables
            res_start_x = []
            res_end_x = []
            res_start_y = []
            res_end_y = []
            res_ppmm = []
        
            for m in range(tot_num_measurements):
                tmp_start_x, tmp_end_x, tmp_start_y, tmp_end_y, tmp_ppmm = resampleMeasurements(start_x[m], end_x[m], start_y[m], end_y[m], cell_coords_x, cell_coords_y, ppmm[m])
                res_start_x.extend(tmp_start_x)
                res_end_x.extend(tmp_end_x)
                res_start_y.extend(tmp_start_y)
                res_end_y.extend(tmp_end_y)
                res_ppmm.extend(tmp_ppmm)
            
            # add phantom measurements to improve temporary the map
            #tmp_start_x, tmp_end_x, tmp_start_y, tmp_end_y, tmp_ppmm = addPhantomMeasurements(min_x, max_x, min_y, max_y, 0, 1.85, 0.6, 1000)
            #res_start_x.extend(tmp_start_x)
            #res_end_x.extend(tmp_end_x)
            #res_start_y.extend(tmp_start_y)
            #res_end_y.extend(tmp_end_y)
            #res_ppmm.extend(tmp_ppmm)
                
            # overwrite with resampled measurements
            tot_num_measurements = len(res_ppmm)
            print(f'Total measurements after resampling: {tot_num_measurements}')
            
            # create a dictionary with the column names and lists
            data = {
                'start_x': res_start_x,
                'end_x': res_end_x,
                'start_y': res_start_y,
                'end_y': res_end_y,
                'ppmm': res_ppmm
            }

            # create a DataFrame from the dictionary
            df = pd.DataFrame(data)
            
            # filter the DataFrame based on the boundaries
            df = df[
                (df['start_x'] >= min_x) &
                (df['start_x'] <= max_x) &
                (df['end_x'] >= min_x) &
                (df['end_x'] <= max_x) &
                (df['start_y'] >= min_y) &
                (df['start_y'] <= max_y) &
                (df['end_y'] >= min_y) &
                (df['end_y'] <= max_y)
            ]
            
            # reset the index
            df = df.reset_index(drop=True)
            
            # assign the filtered values to the respective variables
            start_x = df['start_x']
            start_y = df['start_y']
            end_x = df['end_x']
            end_y = df['end_y']
            ppmm = df['ppmm']
            
            # overwrite with resampled measurements
            tot_num_measurements = len(ppmm)
            A = lil_matrix((tot_num_measurements, tot_num_cells))
            print(f'Filtered measurements after resampling: {tot_num_measurements}')
            
            # creating the figure and axes
            fig, ax = plt.subplots()

            # plotting the line
            ax.plot([start_x, end_x], [start_y, end_y], color='magenta', alpha=0.5, linewidth=1)
            plt.show()
             
        # step 1: compute initial concentrations "smart guesses"
        print('Step 1: compute initial concentrations "smart guesses"')

        sum_A_ij = np.zeros(tot_num_cells)   # sum of intersection areas of all beams intersecting cell i
        sum_p_j = np.zeros(tot_num_cells)    # sum of the average concentrations for each cell c_i
        k = np.zeros(tot_num_cells)          # number of times cell c_i is hit by a beam

        c_init = np.zeros(tot_num_cells)     # initial concentration values

        for j in range(tot_num_measurements):
            if _measurement_option == "path" or _measurement_option == "cone2":
                A[j, :] = getMeasurementPath(start_x[j], end_x[j], start_y[j], end_y[j], cell_coords_x, cell_coords_y)
            elif _measurement_option == "cone":
                # A[m, :] containing intersecting areas of each cell
                A[j, :] = getMeasurementCone(start_x[j], end_x[j], start_y[j], end_y[j], cell_coords_x, cell_coords_y)       
            else:
                raise ValueError("Invalid measurement_option value. Please choose either 'path', 'cone', or 'cone2'.")

            y, x = np.nonzero(A[j, :])
            s = A[j, :].toarray()[y, x].flatten()

            for i in range(len(y)):
                sum_p_j[y[i]] += ppmm[j] / np.sqrt((end_x[j] - start_x[j]) ** 2 + (end_y[j] - start_y[j]) ** 2)
                sum_A_ij[y[i]] += s[i]
                k[y[i]] += 1

            if j % 100 == 0:
                print(f'[Step 1] {j} measurements processed!')

        for i in range(tot_num_cells):
            if k[i] > 0:
                c_init[i] = sum_p_j[i] / k[i]

        # step 2: update
        print('Step 2: update')

        c_q_old = c_init
        c_q_new = c_q_old

        converge = []
        residual_projection_error = []

        for q in range(Q):
            print(f'Iteration: {q} of {Q}')

            p_q = np.zeros(tot_num_measurements)  # reprojection values: calculated beam sum
            tmp_c = np.zeros(tot_num_cells)
            sum_s = np.zeros(tot_num_measurements)

            # step 2.1: for each iteration q calculate the reprojection values
            for j in range(tot_num_measurements):
                y, x = np.nonzero(A[j, :])
                s = A[j, :].toarray()[y, x].flatten()

                for i in range(len(y)):
                    p_q[j] += s[i] * c_q_old[y[i]]
                    sum_s[j] += s[i]

                if j % 100 == 0:
                    print(f'[Step 2.1] {j} measurements processed!')

            # step 2.1.1: correct values using Eq. 2b from IEEE Sensors paper
            for j in range(tot_num_measurements):
                p_q[j] = np.sqrt((end_x[j] - start_x[j]) ** 2 + (end_y[j] - start_y[j]) ** 2) * p_q[j] / sum_s[j]

            # step 2.2: calculate second sum of the equation
            for j in range(tot_num_measurements):
                for i in range(tot_num_cells):
                    tmp_c[i] += (A[j, i] * ppmm[j]) / p_q[j]

                if j % 100 == 0:
                    print(f'[Step 2.2] {j} measurements processed!')

            # step 2.3: calculate final cell concentration
            for i in range(tot_num_cells):
                if sum_A_ij[i] > 0:
                    c_q_new[i] = (c_q_old[i] / sum_A_ij[i]) * tmp_c[i]

            stop = np.max(np.abs(c_q_new - c_q_old))
            print(f'Stop: {stop} vs. {_epsilon}')
            
            if stop < _epsilon:                
                break
            else:
                converge.append(stop)
                residual_projection_error.append(np.sqrt(np.mean((ppmm - p_q) ** 2)))

            print(f'Residual projection error (RMSE): {np.min(residual_projection_error)} ppm x m')
            c_q_old = c_q_new
        
        # mean map
        mean_map_vector = c_q_new

        # variance map
        variance_map_vector, var_process_noise = getVarMap(mean_map_vector, A, ppmm.values, _lambda)
        
        print('Mean and variance created!\n')

        # create the meshgrid and reshape the result vectors
        # by setting order='F', the reshaping will be performed in column-major order, which matches the behavior of MATLAB's reshape() function..
        X, Y = np.meshgrid(cell_coords_x, cell_coords_y, indexing='xy')
        mean_map = np.reshape(mean_map_vector, (num_cells_y, num_cells_x), order='F')
        variance_map = np.reshape(variance_map_vector, (num_cells_y, num_cells_x), order='F')

        # print the hot spot coordinates and the total concentration
        hot_spot_coords = getHotSpotLocation(mean_map, cell_coords_x, cell_coords_y)
        x, y = hot_spot_coords
        
        distance = np.sqrt((0 - x)**2 + (1.85 - y)**2)

        print(f'Hot spot coordinates: {hot_spot_coords[0]:.2f}, {hot_spot_coords[1]:.2f} m')
        print(f'Distance from bag to hot spot: {distance:.2f} m')

        # Prepare data for the table
        radius = [0.25, 0.5, 0.6, 1.0, 1.5]
        data = []
        for i in zip(radius):   
            total_concentration = getConcentrationSum(mean_map, cell_coords_x, cell_coords_y, hot_spot_coords, i)
            total_conc_bag_area = getConcentrationSum(mean_map, cell_coords_x, cell_coords_y, (0, 1.85), i)
            data.append([i[0], total_concentration, total_conc_bag_area, _expected_tdlas_concentration * 0.6, _expected_tdlas_concentration  *0.6 -total_conc_bag_area])
    
        # Create the table
        headers = ["Radius (m)", "Hot Spot Concentration (ppm)", "Bag Concentration (ppm)", "Expected Concentration (ppm)", "Difference (ppm)"]
        table = tabulate(data, headers=headers, floatfmt=".2f", tablefmt="fancy_grid")
        print(table)
        
        sum_mean_map = np.sum(mean_map)
        print(f'Total map concentration: {sum_mean_map:.2f} ppm')
        print(f'Difference: {_expected_tdlas_concentration * 0.6 - sum_mean_map:.2f} ppm')
        print('\n')
        
        fig = plt.figure(figsize=(10, 8))

        plt.colormaps()
        plt.set_cmap('hot')
        plt.set_cmap(plt.get_cmap().reversed())
        
        # mean map
        ax1 = fig.add_subplot(2, 1, 1)
        mean_map_plot = ax1.pcolor(X, Y, mean_map, shading='auto')
        ax1.set_aspect('equal')
        ax1.set_xlabel('y (m)')
        ax1.set_ylabel('z (m)')
        str_mean = f'Mean Map of Slice {slice_id} (c = {_cell_size:.2f} m)'
        ax1.set_title(str_mean)
        cbar = fig.colorbar(mean_map_plot, ax=ax1)
        cbar.set_label('Concentration (ppm)')  

        # plot the red "x" at the hot spot coordinates
        ax1.plot(x, y, 'rx', markersize=10, linewidth=5)
        ax1.plot(0, 1.85, 'gx', markersize=10, linewidth=5)
        
        circle1 = plt.Circle((0, 1.85), 0.6, color='green', fill=False)
        circle2 = plt.Circle((0, 1.85), 1.0, color='red', fill=False)
        ax1.add_artist(circle1)
        ax1.add_artist(circle2)
    
        # variance map
        ax2 = fig.add_subplot(2, 1, 2)
        variance_map_plot = ax2.pcolor(X, Y, variance_map, shading='auto')
        ax2.set_aspect('equal')
        ax2.set_xlabel('y (m)')
        ax2.set_ylabel('z (m)')
        str_var = f'Variance Map of Slice {slice_id} (c = {_cell_size:.2f} m)'
        ax2.set_title(str_var)
        fig.colorbar(variance_map_plot, ax=ax2)

        plt.tight_layout()
        plt.show()

        fig.savefig(f'{copter_data_path}/CT_sliceID={slice_id}_c={_cell_size:.2f}m_CT.png')
        print(f'Figures of Slice {slice_id} created!')