# Analysis

[← README](../README.md) · [Experiments](experiments.md) · [Data](data.md) · **Analysis** · [Verification](verification.md)

## I24 processing chain

`reproduce.py` runs, for every trial and for methods (a) and (b) of the paper, the original scripts:

| Step | Script | Function |
|------|--------|----------|
| 1 | `analysis/extract_tdlas.py` | loads the logs, converts RTK to local coordinates, assigns slice/waypoint/pose, applies the filters below |
| 2 | `analysis/pkl2csv.py` | laser ray per measurement (sensor pose → intersection with z = 0), projected into the slice plane |
| 3 | `analysis/plot2d.py` | ray plots (Fig. 2c, 2d), beam-hit ratio, maximum ray concentration through the bag |
| 4 | `analysis/ct_ragt.py` | reconstruction (λ = 1·10⁻⁵, lower bound 1.8957 ppm, cell size 0.5 m, path model), evaluation, Fig. 2a/2b |

| Filter (paper) | Criterion in the code |
|----------------|-----------------------|
| 1 (1) | error code 1 and intensity ≥ 3 % |
| 2 (2) | RTK, gimbal and pose data available for the measurement interval (300 ms) |
| 3.1/3.2 (3) | within 0.5 m of a slice plane and of a waypoint |
| 4 (4) | SD of altitude < 0.03 m |
| 5 (5) | \|yaw − set-point\| < 2° |
| 6 (6) | SD of gimbal pitch < 0.05° |
| 7 (7) | squared norm of the mean velocity < 0.05 m²/s² (note K4) |
| 8.1 (–) | values > 1.2 × expected concentration divided by round(value/expected) (note K5) |
| 8.2 (8) | maximum per waypoint and pose — method (a); disabled for method (b) |

Quantities of Table I: *beam-hit ratio* = rays of method (a) intersecting a circle of r = 0.3 m around the bag centre
with ≥ 100 ppm·m, divided by 13; *simple estimate* = maximum of these rays / 0.6 m; *estimated concentration* = sum of
cell values within r = 0.5 m or 1.0 m of the bag centre; *peak-to-bag distance* = distance of the maximum cell;
*JSD* = Jensen-Shannon divergence against a ground-truth map that distributes the expected concentration over the cells
by their overlap with a 0.6 m × 0.6 m square.

## S18 / R19 / I22 scripts

| Script | Reproduces |
|--------|-----------|
| `analysis/ejrs2019_earth_wall.py` | R19 Table 1 from the raw log, with the data selection of the original workbook (`data/metadata/cofi-abv/2016-07-07_earth-wall_*.csv`) and, as a variant, with all error codes ≠ 1 removed |
| `analysis/ejrs2019_aiming.py` | R19 experiment #3 (share of time with detection) with the selection of the original workbook, and variants restricted to valid error codes |
| `analysis/ejrs2019_plume.py` | R19 wind statistics, reference array (day #1 trial #4), reconstructions of all 10 ray files from 2017 (method of `RAGT.m`, λ = 1·10⁻⁵ and, for comparison, 0.1), mean and variance maps of the three published trials |
| `analysis/isoen2022_drone_to_drone.py` | I22 measurement counts, maximum concentration, longest period, wind statistics (CircStat logic of `visualize_anemometer_data.m`) |
| `analysis/sensitivity.py` | I24 with λ = 0.1 and with true cell centres (notes K1, K3) |

The Matlab code of 2016–2017 (ray tracing `createLocalCoordinates4CT.m`, `RAGT.m` and helpers, and the reader
`load_dmf.m` for the DMF logs of 2017) is included unchanged in `analysis/matlab_2017/` for reference (selected files of the BAM-internal repository `gas_tomography`, commit 4f43c4f;
third-party toolboxes not included). It requires Matlab and Gurobi and was not re-executed; the reconstructions start
from the ray files it wrote in 2017. The numbers of R19 experiment #2 were computed in an Excel workbook (included) and
were located there, not recomputed.

## Solver

The published reconstructions were computed with the commercial QP solver Gurobi. The objective ‖Ax − b‖² + λ‖x‖²
with a lower bound is strictly convex and has a unique minimiser; the scripts solve the same problem by default as
bounded linear least squares with SciPy (`lsq_linear`, BVLS), which reproduces the stored Gurobi output to 0.01 ppm.
The Gurobi formulation is kept (`--solver gurobi`, requires `gurobipy` and a licence).

## Provenance and changes of the code

* **Python (2020–2024):** Dino Hüllmann and Patrick P. Neumann; imported unchanged from the BAM-internal repository
  `gastomo`, commit `26f7cf1` (state of the final I24 figures), as the first commit of this repository's analysis code.
* **Matlab (2016–2017):** Patrick P. Neumann; DMF reader `load_dmf.m`: Dino Hüllmann and Patrick P. Neumann.
* **Changes since the import** (`git diff c2c8733 -- analysis`): reading of `.gz` files and separate output directory;
  `extract_tdlas.py --method {max,all}`; `ct_ragt.py --solver`; key numbers written as JSON/CSV; unused variance map no
  longer computed; `plt.get_cmap` instead of the removed `cm.get_cmap`; **bug fix** of the ray colours in `plot2d.py`
  (note K2); new scripts `sensitivity.py`, `ejrs2019_*.py`, `isoen2022_*.py`.
* `analysis/ct_mlem.py` (MLEM) is included unchanged; it was not used for any published result, was marked "still not
  working" by its authors and contains an indexing error (all contributions are accumulated in cell 0).
