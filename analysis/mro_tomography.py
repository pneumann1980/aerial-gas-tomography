import numpy as np
try:
    # Gurobi was the solver used for the published results (commercial licence required)
    import gurobipy as gp
    from gurobipy import GRB
except ImportError:
    gp = None

from shapely.geometry import Point, Polygon
from shapely.ops import polygonize
from scipy.sparse import lil_matrix
from scipy.sparse import csr_matrix
from scipy.optimize import lsq_linear

from scipy.sparse import issparse
from scipy.sparse import eye

# temporary imports
import matplotlib.pyplot as plt
from scipy import special
from scipy.stats import norm
import scipy.stats as stats
import math


def getMeasurementPath(start_x, end_x, start_y, end_y, cell_coords_x, cell_coords_y):
    cell_size = cell_coords_x[1] - cell_coords_x[0]

    # calculate start and end (cell-)index for x-coordinate
    cell_start_x = np.floor((start_x - cell_coords_x[0]) / cell_size).astype(int)
    cell_end_x = np.floor((end_x - cell_coords_x[0]) / cell_size).astype(int)

    # calculate start and end (cell-)index for y-coordinate
    cell_start_y = np.floor((start_y - cell_coords_y[0]) / cell_size).astype(int)
    cell_end_y = np.floor((end_y - cell_coords_y[0]) / cell_size).astype(int)

    if cell_start_x <= cell_end_x:
        x_intersections = np.arange(cell_start_x + 1, cell_end_x + 1)
    else:
        x_intersections = np.arange(cell_start_x, cell_end_x, -1)

    if cell_start_y <= cell_end_y:
        y_intersections = np.arange(cell_start_y + 1, cell_end_y + 1)
    else:
        y_intersections = np.arange(cell_start_y, cell_end_y, -1)
        
    #print(f'x_intersections:\n{x_intersections}')
    #print(f'y_intersections:\n{y_intersections}')
    
    # intersection with cells on x axis
    intersection_points_x = np.zeros((len(x_intersections), 3))
    if len(x_intersections) > 0:
        intersection_points_x[:, 0] = cell_coords_x[x_intersections]
        intersection_points_x[:, 2] = (intersection_points_x[:, 0] - start_x) / (end_x - start_x)
        intersection_points_x[:, 1] = start_y + (end_y - start_y) * intersection_points_x[:, 2]

    # intersection with cells on y axis
    intersection_points_y = np.zeros((len(y_intersections), 3))
    if len(y_intersections) > 0:
        intersection_points_y[:, 1] = cell_coords_y[y_intersections]
        intersection_points_y[:, 2] = (intersection_points_y[:, 1] - start_y) / (end_y - start_y)
        intersection_points_y[:, 0] = start_x + (end_x - start_x) * intersection_points_y[:, 2]

    intersection_points = np.vstack((intersection_points_x, intersection_points_y))
    #intersection_points = np.concatenate((intersection_points_x, intersection_points_y), axis=0)
    
    # add start and end point
    intersection_points = np.vstack(([start_x, start_y, 0], intersection_points, np.array([end_x, end_y, 1])))
    intersection_points = intersection_points[intersection_points[:, 2].argsort()]

    # the distance from the start of the beam to the intersection of each cell is the 4th column (t) multiplied by the length of the beam
    dist = np.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
    distances = intersection_points[:, 2] * dist
    distances = np.diff(distances)

    cells = np.zeros((len(distances), 2))
    
    for i in range(len(intersection_points) - 1):
        mid_x = (intersection_points[i, 0] + intersection_points[i + 1, 0]) / 2
        mid_y = (intersection_points[i, 1] + intersection_points[i + 1, 1]) / 2
        cells[i, 0] = np.floor((mid_x - cell_coords_x[0]) / cell_size).astype(int)
        cells[i, 1] = np.floor((mid_y - cell_coords_y[0]) / cell_size).astype(int)

    indexes = len(cell_coords_y) * cells[:, 0] + cells[:, 1]
    measurement_path = np.zeros((len(cell_coords_x) * len(cell_coords_y)))
    measurement_path[indexes.astype(int)] = distances

    #print(measurement_path[indexes.astype(int)])
    #input("Press any key to continue...")
    return measurement_path


def getMeasurementCone(start_x, end_x, start_y, end_y, cell_coords_x, cell_coords_y):
    # step 1: compute the new end vertices of the cone by approximating it by a triangle   
    fBeamLength = np.sqrt((start_x - end_x)**2 + (start_y - end_y)**2)
    fFinalDeviation = fBeamLength * 0.17 / 20  
    # conical beam, width 0.17 m at 20 m LMm-G
    # conical beam, width 0.56 m at 30 m RMLD
    
    end_x_plus = end_x - fFinalDeviation * (-(start_y - end_y)) / fBeamLength
    end_y_plus = end_y - fFinalDeviation * (start_x - end_x) / fBeamLength

    end_x_minus = end_x + fFinalDeviation * (-(start_y - end_y)) / fBeamLength
    end_y_minus = end_y + fFinalDeviation * (start_x - end_x) / fBeamLength

    # define the triangle polygon
    fConeX = [start_x, end_x_plus, end_x_minus, start_x]
    fConeY = [start_y, end_y_plus, end_y_minus, start_y]
    
    # step 2: Intersect cone polygon with grid cell polygon and compute the area of the intersection
    cellsize = cell_coords_x[1] - cell_coords_x[0]
    measurement_path = np.zeros((len(cell_coords_x) * len(cell_coords_y),))
    
    for i in range(len(cell_coords_x) - 1):
        x_pos = cell_coords_x[i]
        areas = np.zeros((len(cell_coords_y),))
        
        for j in range(len(cell_coords_y) - 1):
            y_pos = cell_coords_y[j]
            
            # define the cell polygon
            fCellX = [x_pos, x_pos, x_pos + cellsize, x_pos + cellsize, x_pos]
            fCellY = [y_pos, y_pos + cellsize, y_pos + cellsize, y_pos, y_pos]
            
            # compute intersection and area
            cone_polygon = Polygon(zip(fConeX, fConeY))
            cell_polygon = Polygon(zip(fCellX, fCellY))
            intersection = cone_polygon.intersection(cell_polygon)
            
            if intersection.is_empty:
                areas[j] = 0
            else:
                if isinstance(intersection, Polygon):
                    areas[j] = intersection.area
                else:
                    areas[j] = sum(p.area for p in polygonize(intersection))
        
        measurement_path[i * len(cell_coords_y): (i + 1) * len(cell_coords_y)] = areas
    
    measurement_path = lil_matrix(measurement_path)
    return measurement_path


def rotate_vector(vector, rad_angle):
    rotation_matrix = np.array([[np.cos(rad_angle), np.sin(rad_angle)],
                                [-np.sin(rad_angle), np.cos(rad_angle)]])
    rotated_vector = np.dot(rotation_matrix, vector)
    return rotated_vector

def reconstruct_individual_concentrations(concentration, opening_angle, num_points):
    # Calculate the mean and standard deviation of the Gaussian distribution
    mean = concentration / 2.0  # Assuming symmetric distribution
    std_dev = opening_angle / (2.0 * stats.norm.ppf(0.95))  # Assuming 95% confidence interval
    
    # Generate equally spaced values along the x-axis
    x_values = np.linspace(mean - 4 * std_dev, mean + 4 * std_dev, num_points)
    
    # Calculate the corresponding individual concentrations using the inverse CDF
    individual_concentrations = stats.norm.pdf(x_values, mean, std_dev) / np.sum(stats.norm.pdf(x_values, mean, std_dev))
    individual_concentrations *= concentration  # Scale the concentrations to match the given concentration
    
    return individual_concentrations

def resampleMeasurements(start_x, end_x, start_y, end_y, cell_coords_x, cell_coords_y, ppmm):
    # parameters
    beam_extension_angle = 8.5e-3
    wavelength = 1653e-9
    num_rays = 5
    
    # restore cell size from cell coordinates
    cell_size = cell_coords_x[1] - cell_coords_x[0]
    
    # calculate the direction vector of the TDLAS measurement 
    start_point = np.array([start_x, start_y])
    end_point = np.array([end_x, end_y])
    v = end_point - start_point
    norm_v = v / np.linalg.norm(v)
    
    #print(start_x)
    #print(start_y)
    #print(norm_v)
    
    # calculate the mean and standard deviation
    concentrations = []
    concentrations = reconstruct_individual_concentrations(ppmm, beam_extension_angle, num_rays)
    #print(concentrations)

    # rotation parameters
    rotation_angles = np.linspace(1.0, -1.0, num_rays) * beam_extension_angle
    #print(rotation_angles)
    
    # array to store new end points
    intersection_points = []
    
    res_start_x = [] 
    res_end_x = [] 
    res_start_y = [] 
    res_end_y = [] 
    res_ppmm = [] 
    
    # perform rotation for each angle
    for angle in rotation_angles:
        rotated_vector = rotate_vector(norm_v, angle)
        #print(rotated_vector)
        
        if rotated_vector[1] != 0:
            # calculate intersection point with x-axis
            intersection_x = -rotated_vector[0] / rotated_vector[1] * start_point[1] + start_point[0]
            intersection_points.append([intersection_x, 0])
        else:
            # handle the case when rotated_vector[1] is zero
            print('Measurement path could not be resampled!')
            return res_start_x, res_end_x, res_start_y, res_end_y, res_ppmm
            
    for point, conc in zip(intersection_points, concentrations):
        res_start_x.append(start_x)
        res_end_x.append(point[0])
        res_start_y.append(start_y)
        res_end_y.append(point[1])
        res_ppmm.append(conc)
            
    # creating the figure and axes
    #fig, ax = plt.subplots()
    # plotting the line
    #for point in intersection_points:
    #    ax.plot([start_x, point[0]], [start_y, point[1]], color='magenta', alpha=0.5, linewidth=1)
        
    #ax.set_xlabel('x [m]')  # Set the x-axis label
    #ax.set_ylabel('y [m]')  # Set the y-axis label
    #ax.set_title('TDLAS Rays')  # Set the plot title
    #plt.plot(range(len(res_ppmm)), res_ppmm)
    #plt.show()
    
    #input("Waiting for your command!")
    
    return res_start_x, res_end_x, res_start_y, res_end_y, res_ppmm


def addPhantomMeasurements(min_x, max_x, min_y, max_y, pos_x, pos_y, radius, num_rays):
    # parameters
    res_start_x = [] 
    res_end_x = [] 
    res_start_y = [] 
    res_end_y = [] 
    res_ppmm = [] 

    # build result set
    res_start_y = np.linspace(min_y, max_y, num_rays)
    mask = np.logical_or(res_start_y <= pos_y - radius, res_start_y >= pos_y + radius)
    
    res_start_y = res_start_y[mask]
    res_end_y = res_start_y
    
    # re-calculate the number of rays
    num_rays = len(res_start_y)
    
    res_start_x = np.full(num_rays, min_x)
    res_end_x = np.full(num_rays, max_x)  
    res_ppmm = np.zeros(num_rays) 
    
    # creating the figure and axes
    #fig, ax = plt.subplots()
    # plotting the line
    #for m in range(num_rays):
    #    ax.plot([res_start_x[m], res_end_x[m]], [res_start_y[m], res_end_y[m]], color='magenta', alpha=0.5, linewidth=1)
        
    #ax.set_xlabel('x [m]')  # Set the x-axis label
    #ax.set_ylabel('y [m]')  # Set the y-axis label
    #ax.set_title('TDLAS Rays')  # Set the plot title
    #plt.plot(range(len(res_ppmm)), res_ppmm)
    #plt.show()
    
    #input("Waiting for your command!")
    
    return res_start_x, res_end_x, res_start_y, res_end_y, res_ppmm

def solveQP(A, ppmm, lam, lower_bound=0, solver='scipy'):
    # Solves  min_x  x^T (A^T A + lam I) x - 2 ppmm^T A x   s.t.  x >= lower_bound,
    # i.e.  min_x ||A x - ppmm||^2 + lam ||x||^2  (strictly convex for lam > 0, unique minimiser).
    # solver='gurobi': original implementation (Gurobi QP, used for the published results)
    # solver='scipy' : the same problem written as bound-constrained linear least squares
    #                  [A; sqrt(lam) I] x ~ [ppmm; 0] and solved with scipy.optimize.lsq_linear (BVLS)
    if solver == 'scipy':
        return solveQP_scipy(A, ppmm, lam, lower_bound)
    if gp is None:
        raise ImportError("solver='gurobi' requires gurobipy and a Gurobi licence")

    # build the quadratic term
    H = A.T @ A + lam * np.eye(A.shape[1])
    
    # build the linear term
    q = -2 * ppmm.T @ A

    model = gp.Model()

    # add variables
    x = model.addVars(A.shape[1])

    # set objective
    obj = gp.QuadExpr()
    for i in range(A.shape[1]):
        for j in range(A.shape[1]):
            obj.addTerms(H[i, j], x[i], x[j])
            
    model.setObjective(obj + gp.quicksum(q[i] * x[i] for i in range(A.shape[1])), GRB.MINIMIZE)

    # add constraints
    for i in range(A.shape[1]):
        model.addConstr(x[i] >= lower_bound)

    # set Gurobi parameters
    model.setParam('OutputFlag', False)

    # optimize model
    model.optimize()

    # get solution
    solution = np.array([x[i].X for i in range(A.shape[1])])
    lagrange_multipliers = np.array([model.pi[i] for i in range(A.shape[1])])

    return solution, lagrange_multipliers

def solveQP_scipy(A, ppmm, lam, lower_bound=0):
    A = A.toarray() if issparse(A) else np.asarray(A)
    n_cells = A.shape[1]
    A_aug = np.vstack((A, np.sqrt(lam) * np.eye(n_cells)))
    b_aug = np.concatenate((np.asarray(ppmm, dtype=float), np.zeros(n_cells)))
    res = lsq_linear(A_aug, b_aug, bounds=(lower_bound, np.inf), method='bvls', tol=1e-12, max_iter=100 * n_cells)
    if not res.success:
        raise RuntimeError(f'lsq_linear did not converge: {res.message}')
    # Lagrange multipliers of the bounds (gradient of the objective at the solution, zero for inactive bounds)
    grad = 2 * (A.T @ (A @ res.x - ppmm) + lam * res.x)
    lagrange_multipliers = np.where(res.active_mask != 0, grad, 0.0)
    return res.x, lagrange_multipliers

#Some first thoughts....
# Function to convert coordinates to grid indices
def coordinates_to_indices(x, y):
    return int(x / grid_resolution), int(y / grid_resolution)

# Example known concentration values corresponding to measurement positions
#known_concentrations = {coordinates_to_indices(x, y): concentration for (x, y), concentration in zip(measurement_positions, [1.0, 0.5, 0.8])}

def solveQPwithConstraints(A, ppmm, lam, known_concentrations, lower_bound=0):
    n, m = A.shape
    H = A.T @ A + lam * np.eye(m)
    q = -2 * ppmm.T @ A
    
    model = gp.Model()
    x = model.addVars(m, lb=lower_bound, name='x')
    
    obj = gp.QuadExpr()
    for i in range(m):
        for j in range(m):
            obj += H[i, j] * x[i] * x[j]
    obj += gp.quicksum(q[i] * x[i] for i in range(m))
    
    model.setObjective(obj, GRB.MINIMIZE)
    
    # Add constraints for known concentrations if they are greater than zero and not NaN
    for i in range(m):
        if not np.isnan(known_concentrations[i]) and known_concentrations[i] > 0:
            model.addConstr(x[i] == known_concentrations[i], name=f"stationary_{i}")
    
    model.setParam('OutputFlag', 0)
    model.optimize()
    
    if model.status == GRB.OPTIMAL:
        solution = np.array([x[i].X for i in range(m)])
        lagrange_multipliers = np.array([constr.Pi for constr in model.getConstrs() if 'stationary' in constr.ConstrName])
        return solution, lagrange_multipliers
    else:
        raise Exception("Optimization was unsuccessful. Status Code: {}".format(model.status))
    
def getVarMap(mean_map_vector, A, ppmm, lam):
    # process noise
    num_measurements, num_cells = A.shape
    res = ppmm - A @ mean_map_vector
    var_process_noise = (res.T @ res) / abs(num_measurements - num_cells)

    # variance map
    inv_des = np.linalg.inv(A.T @ A + lam * np.eye(num_cells))
    variance_map_vector = var_process_noise / np.diag(inv_des)
    
    return variance_map_vector, var_process_noise


def getHotSpotLocation(mean_map, cell_coords_x, cell_coords_y):
    # step 1: initialize variables
    max_concentration = float('-inf')
    hot_spot_coords = None

    # step 2: find the hot spot
    num_cells_y, num_cells_x = mean_map.shape

    for i in range(num_cells_y):
        for j in range(num_cells_x):
            concentration = mean_map[i, j]
            if concentration > max_concentration:
                max_concentration = concentration
                hot_spot_coords = (round(cell_coords_x[j], 2), round(cell_coords_y[i], 2))
    
    return hot_spot_coords


def getConcentrationSum(mean_map, cell_coords_x, cell_coords_y, coords, radius):
    # step 1: initialize variables
    num_cells_y, num_cells_x = mean_map.shape

    # step 2: sum up concentrations within the given radius 
    total_concentration = 0.0
    x, y = coords

    for i in range(num_cells_y):
        for j in range(num_cells_x):
            distance = np.sqrt((cell_coords_x[j] - x)**2 +
                               (cell_coords_y[i] - y)**2)
            if distance <= radius:
                total_concentration += mean_map[i, j]

    total_concentration = round(total_concentration, 2)
    
    return total_concentration
