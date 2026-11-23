#!/usr/bin/env python3

import argparse
import collections
import json
import os
import pickle
import sys

import matplotlib.pyplot as plt
import matplotlib.collections as mcoll
from matplotlib.collections import LineCollection
import matplotlib.cm as cm
import numpy as np
import pandas as pd
import scipy.spatial

from mro_geometry import *

# Parse the command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help="Directory containing the 'out_slice_X.csv' files (output of pkl2csv.py)")
args = parser.parse_args()

# Check if the copter data path is provided as an argument
if args.file:
    copter_data_path = args.file
else:
    print("Please provide the copter data path using --file argument.")
    sys.exit(1)

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
        
        column_names = ['sx', 'sy', 'ex', 'ey', 'concentration']

        data = pd.read_table(data_path, names=column_names, sep=';')

        # creating the figure and axes for all lines
        fig_all, ax_all = plt.subplots()
        
        # plotting all lines
        ax_all.plot([data.sx, data.ex], [data.sy, data.ey], color='magenta', alpha=0.5, linewidth=1)
        ax_all.set_aspect('equal')
        ax_all.set_xlim(-5, 5)        # Set x-axis limits to -5 and 5
        ax_all.set_xlabel('x (m)')
        ax_all.set_ylabel('y (m)')
        #ax_all.set_title(f'TDLAS Rays of Slice {slice_id}')

        print("Max. Concentration (all):", max(data.concentration))
        
        # creating the figure and axes for filtered lines
        fig_filtered, ax_filtered = plt.subplots()
        
        # bag position and radius  
        circle_center = (0, 1.85)
        circle_radius = 0.3

        # calculate intersecting line indices
        intersecting_indices = line_circle_intersection(data, circle_center, circle_radius)

        # Filter the original DataFrame to get the intersecting lines
        filtered_data = data.iloc[intersecting_indices]
        total_num_lines = 13 # the number of waypoints is 13 --> min. 13 rays should "touch" the bag; len(filtered_data)
        
        # filter lines below threshold
        threshold = 100  
        filtered_data = filtered_data[filtered_data.concentration >= threshold].reset_index(drop=True)
        cur_num_lines = len(filtered_data)

        print(f'Ratio: {cur_num_lines}/{total_num_lines} = {cur_num_lines/total_num_lines}')
        
        # Create a set of line segments
        points = np.array([filtered_data.sx, filtered_data.sy, filtered_data.ex, filtered_data.ey]).T.reshape(-1, 2, 2)
        # BUGFIX (v1.0.0): the original code used
        #   segments = np.vstack([points[:-1], points[1:]])
        # which creates 2n-2 segments for n concentration values, so that most rays were drawn
        # with the colour of another ray (ISOEN 2024, Fig. 2d). One segment per ray is correct.
        # Only the colouring of the figure is affected, no numerical result.
        segments = points

        # Define the colormap
        colormap = plt.get_cmap('hot_r')  # cm.get_cmap was removed in matplotlib 3.9

        # Create the LineCollection object
        lc = LineCollection(segments, cmap=colormap, linewidth=1, alpha=0.5)
        lc.set_array(filtered_data.concentration)
        print("Max. Concentration (filtered):",max(filtered_data.concentration))
        
        # Add the collection to the axes
        ax_filtered.add_collection(lc)

        # Adjust the plot limits
        ax_filtered.autoscale()

        # Add circle
        circle1 = plt.Circle(circle_center, circle_radius, color='green', fill=False)
        ax_filtered.add_artist(circle1)

        # Add colorbar
        norm = plt.Normalize(vmin=filtered_data.concentration.min(), vmax=filtered_data.concentration.max())
        sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
        sm.set_array(filtered_data.concentration)
        cbar = fig_filtered.colorbar(sm, ax=ax_filtered)
        cbar.set_label(r'Concentration (ppm $\cdot$ m)')  

        # Set aspect ratio and axis labels
        ax_filtered.set_aspect('equal')
        ax_filtered.set_xlim(-5, 5)
        ax_filtered.set_xlabel('x (m)')
        ax_filtered.set_ylabel('y (m)')

        # save figures
        fig_all.savefig(f'{data_path}TDLAS_rays_slice_{slice_id}_all.png', bbox_inches='tight')
        fig_all.savefig(f'{data_path}TDLAS_rays_slice_{slice_id}_all.pdf', bbox_inches='tight')
        fig_filtered.savefig(f'{data_path}TDLAS_rays_slice_{slice_id}_filtered.png', bbox_inches='tight')
        fig_filtered.savefig(f'{data_path}TDLAS_rays_slice_{slice_id}_filtered.pdf', bbox_inches='tight')

        # machine-readable summary (beam-hit ratio and simple concentration estimate of ISOEN 2024, Tab. I)
        with open(os.path.join(copter_data_path, f'rays_slice_{slice_id}.json'), 'w') as handle:
            json.dump({'num_rays': len(data),
                       'max_concentration_all_ppmm': float(max(data.concentration)),
                       'num_rays_hitting_bag': cur_num_lines,
                       'num_waypoints_expected': total_num_lines,
                       'beam_hit_ratio': cur_num_lines/total_num_lines,
                       'max_concentration_hitting_bag_ppmm': float(max(filtered_data.concentration))}, handle, indent=2)
        plt.close('all')