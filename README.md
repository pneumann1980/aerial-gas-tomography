# aerial-gas-tomography

Experimental data and analysis code supporting the development of aerial gas tomography:
reconstruction of 2D cross-sections of a methane (CH4) distribution from remote TDLAS
measurements taken by an aerial robot (drone) with a gimballed sensor.

This repository documents **preliminary work** for the proposal *CACTUS* (DFG Priority Programme SPP 2433).
All data and results in this repository originate from **BAM in-house research carried out before CACTUS**
(field campaign June 2020, published 2024); they are not results of the CACTUS project.
The reproduced study is

> P. P. Neumann, D. Hüllmann, N. P. Winkler, H. Lohrke, A. J. Lilienthal,
> "Outdoor Gas Plume Reconstructions: A Field Study with Aerial Tomography,"
> *2024 IEEE International Symposium on Olfaction and Electronic Nose (ISOEN)*, Grapevine, TX, USA, 2024, pp. 1–3.
> doi: [10.1109/ISOEN61239.2024.10556071](https://doi.org/10.1109/ISOEN61239.2024.10556071)

(hereafter *ISOEN 2024*). The repository contains the raw sensor data of all eight trials of that paper,
the original processing code, a one-command reproduction of Table I and Fig. 2, and a documented check
of the published numbers including the issues found during this check.

**Quick start**

```bash
python -m venv .venv
.venv/Scripts/activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python reproduce.py               # all 8 trials x 2 methods, approx. 30 min
python analysis/sensitivity.py    # optional: effect of the issues listed in "Known issues"
pytest -q                         # checks, approx. 3 min
```

---

## 1. Related work and data provenance

| Year | Publication | Measurements | In this repository |
|------|-------------|--------------|--------------------|
| 2018 | P. P. Neumann et al., "Gas Tomography Up In The Air!", *IEEE SENSORS 2018*, pp. 1–4, doi: [10.1109/ICSENS.2018.8630293](https://doi.org/10.1109/ICSENS.2018.8630293) | first aerial gas tomography experiments with the UAV-REGAS platform (DJI S1000+, TDLAS on gimbal) and a stationary reference gas-sensor array | no |
| 2019 | P. P. Neumann, H. Kohlhoff, D. Hüllmann, D. Krentel, M. Kluge, M. Dzierliński, A. J. Lilienthal, M. Bartholmai, "Aerial-based gas tomography – from single beams to complex gas distributions", *European Journal of Remote Sensing* 52(sup3), 2–16, 2019, doi: [10.1080/22797254.2019.1640078](https://doi.org/10.1080/22797254.2019.1640078) | platform validation and 2D plume reconstruction with reference array of 10 IR gas transmitters and 2 ultrasonic anemometers; platform developed in the BAM in-house project CoFi-ABV | no |
| 2022 | P. P. Neumann, D. Hüllmann, N. P. Winkler, J. Schugardt, "Remote Drone-to-Drone Gas Sensing: A Feasibility Study", *IEEE ISOEN 2022*, pp. 1–3, doi: [10.1109/ISOEN54820.2022.9789627](https://doi.org/10.1109/ISOEN54820.2022.9789627) | open-path TDLAS measurement between two drones (field test 2020-07-14) | no |
| 2024 | ISOEN 2024 (see above) | **8 tomography trials over a static CH4 bag, 2020-06-18 and 2020-06-29** | **yes, complete** |

All measurements were taken with aerial robots or stationary/laboratory set-ups at BAM;
the material provided for this repository contains **no ground-robot measurements**.
Funding of the 2020 field campaign: [TO BE PROVIDED: project/funding source of the June 2020 campaign].

---

## 2. Measurement set-up (ISOEN 2024, Sec. II)

* **Aerial robot:** DJI Spreading Wings S1000+ octocopter, A3 Pro flight controller, D-RTK GNSS,
  custom PID position controller; custom 3-axis gimbal carrying the gas sensor, a laser rangefinder and a camera
  (details: European Journal of Remote Sensing 2019).
* **Gas sensor:** TDLAS CH4 sensor TGE Laser Methane mini-G (LMm-G); output = path-integrated concentration in ppm·m,
  backscatter intensity in %, error code; recorded at approx. 4 Hz. The sensor needs a reflecting surface (here the ground).
* **Static "plume" (ground truth):** CH4-filled bag, length approx. 1.3 m, diameter approx. 0.6 m, fixed between two
  tripods with its centre at a height of 1.85 m. In the slice coordinate system the bag centre is at (y, z) = (0, 1.85) m.
* **Reference concentration:** bag concentration measured after the experiments of each day with a Dräger X-am 5600
  (IR methane sensor). Values used: 16,500 ppm (2020-06-18) and 26,000 ppm (2020-06-29), see `data/metadata/trials.csv`.
* **Flight pattern:** gate-shaped mission of 13 waypoints at 7, 8.5 and 10 m altitude, 1 m/s; at each waypoint
  a gimbal pitch scan in 5° steps; 180° yaw rotation at the last three waypoints; one trial ≈ 12 min.
* **Location:** BAM test site (coordinates of the set-up: `data/metadata/field_notes/Koordinaten.txt`).

---

## 3. Campaign overview and file assignment

### 3.1 Trials used in ISOEN 2024

| Trial | Date | Flight | Raw data | Expected conc. (ppm) | TDLAS records | Remark |
|------:|------|-------:|----------|---------------------:|--------------:|--------|
| 1 | 2020-06-18 | 5  | `data/raw/copter/2020-06-18/5`  | 16,500 | 2971 | mission errors (paper); gimbal yaw drift |
| 2 | 2020-06-18 | 19 | `data/raw/copter/2020-06-18/19` | 16,500 | 2789 | |
| 3 | 2020-06-18 | 20 | `data/raw/copter/2020-06-18/20` | 16,500 | 2492 | |
| 4 | 2020-06-29 | 3  | `data/raw/copter/2020-06-29/3`  | 26,000 | 2594 | gimbal yaw drift; 14 waypoints logged |
| 5 | 2020-06-29 | 6  | `data/raw/copter/2020-06-29/6`  | 26,000 | 2581 | example trial of Fig. 2 |
| 6 | 2020-06-29 | 8  | `data/raw/copter/2020-06-29/8`  | 26,000 | 2474 | gimbal yaw drift |
| 7 | 2020-06-29 | 9  | `data/raw/copter/2020-06-29/9`  | 26,000 | 2249 | gimbal yaw drift; field note: bag slack |
| 8 | 2020-06-29 | 10 | `data/raw/copter/2020-06-29/10` | 26,000 | 2571 | |

The assignment trial ↔ flight is taken from the original analysis notebooks; it is independently confirmed by the
number of TDLAS records per trial noted in the LaTeX source of Table I (2971, 2789, 2492, 2594, 2581, 2474, 2249, 2571).

### 3.2 Complete measurement series and exclusion rules

`data/metadata/campaign_2020-06_inventory.csv` lists **all 79 flight folders** of the campaign (2020-06-16 to
2020-06-30) with number of reached waypoints, mission duration, number of TDLAS records, status, exclusion reason
and the original field note (German, with English translation). Exclusion rules applied there:

1. 2020-06-16 and 2020-06-17: set-up and commissioning days (positioning, controller tuning, yaw alignment
   according to the field notes); no reference concentration recorded; not evaluated.
2. Flights without a complete 13-waypoint gate mission (tests, positioning, aborted flights) are excluded.
3. Complete missions excluded because of a documented problem: 2020-06-18 #2 (RTK yaw not initialised),
   2020-06-29 #0 (last waypoint(s) incomplete), 2020-06-29 #12 (yaw twisted after take-off, "not usable for CT").
4. 2020-06-30 #0: only 6 of 13 waypoints (no complete mission).
5. **Not documented:** 2020-06-18 #24 is a complete 13-waypoint mission with TDLAS data but was not used
   in ISOEN 2024: [TO BE PROVIDED: reason for excluding 2020-06-18 flight 24].

Within a trial, individual measurements are excluded by the filters of the processing pipeline (Sec. 5);
the number of measurements removed by every filter is listed per trial in `results/filter_statistics.csv`.

### 3.3 Other campaigns (not part of this repository)

The BAM MRO data archive additionally contains: 2016 flight tests (DJI S900, laser tracking, earth wall, scanning vs. aiming),
2017 experiments #5 "2D plume" (with gas-sensor array) and #6 "wind" (presumably the basis of the 2018/2019
publications; this assignment was not verified in detail), 2019 laboratory measurements of the TDLAS spot size,
and 2020-07 experiments with a fan-driven free CH4 plume and two anemometers, including the drone-to-drone
measurement of 2020-07-14 (ISOEN 2022). They are not needed to reproduce ISOEN 2024 and are not included.

---

## 4. Data

```
data/
  raw/copter/<date>/<flight>/       original logger files of the 8 trials (gzip, lossless)
  raw/SHA256SUMS_uncompressed.txt   SHA-256 of the original, uncompressed files
  raw/SHA256SUMS_gz.txt             SHA-256 of the compressed files in this repository
  metadata/trials.csv               trial <-> flight, reference concentration, remarks
  metadata/campaign_2020-06_inventory.csv   all flights of the campaign with status/exclusion reason
  metadata/field_notes/             original field notes (German, verbatim) and surveyed coordinates
  original_results/isoen2024_table1.csv     Table I of ISOEN 2024 (transcribed from the LaTeX source)
  original_results/copter/<date>/<flight>/{max,all}/out_slice_0.csv   ray files produced in 2023 for the paper
```

**Raw data are unchanged.** Each original file was compressed with gzip (`gzip -9 -n`); decompressing yields the
byte-identical original (checked by `pytest`, test `test_raw_data_unchanged`). The analysis reads the `.gz` files
directly. Only the logger files read by the analysis are included (per flight: RTK, fused pose, gimbal,
TDLAS, mission log). Further channels recorded in the archive (raw IMU, ESC, compass, GPS, remote control, lidar,
camera) are not used by the analysis and are not included.

All logger files are tab-separated text without header; the first column is the Unix time stamp in µs.
Column names are defined in `analysis/copter_data_loader.py`.

| File | Content | Columns used by the analysis (units) |
|------|---------|--------------------------------------|
| `tdlas.tsv` | TDLAS gas sensor | `error_code` (1 = valid), `concentration` (ppm·m, path-integrated), `intensity` (backscatter, %) |
| `dji_rtk.csv` | D-RTK position | `longitude`, `latitude` (deg, WGS84), `hfsl` (height, m), `yaw` (deg) |
| `dji_pose_fused.csv` | fused attitude/velocity of the A3 controller | `vx`, `vy`, `vz` (m/s) |
| `GimbalRealtimeData4.tsv` | SimpleBGC32 gimbal controller; schema in `GimbalRealtimeData4.tsv-metadata.yaml` | `angle_y` (pitch, deg), `angle_z`, `frame_angle_z` (deg) |
| `copter_activity.log` | mission log (JSON lines) | waypoints (lat, lon, altitude, yaw setpoint), "reached" events |

Derived quantities: rays in the slice plane `(y_start, z_start, y_end, z_end)` in m with the path-integrated
concentration in ppm·m (`out_slice_0.csv`); reconstructed cell concentrations in ppm (cell size 0.5 m).

---

## 5. Analysis

### 5.1 Processing chain

`reproduce.py` runs, for every trial and for both methods of the paper, the original scripts in `analysis/`:

| Step | Script | Function |
|------|--------|----------|
| 1 | `extract_tdlas.py` | loads the logger files, converts RTK positions to local Cartesian coordinates, assigns slice/waypoint/pose and applies the filters below |
| 2 | `pkl2csv.py` | computes for each valid measurement the laser ray (start = sensor pose, end = intersection with z = 0) projected into the slice plane |
| 3 | `plot2d.py` | ray plots (Fig. 2c, 2d), beam-hit ratio and maximum ray concentration through the bag |
| 4 | `ct_ragt.py` | tomographic reconstruction (least squares with Tikhonov regularisation and lower bound, Trincavelli et al., IEEE SENSORS 2012), evaluation against the bag, figures (Fig. 2a, 2b) |

Filters in `extract_tdlas.py` (numbering as in the code; paper numbering in brackets):

| Filter | Criterion (code) |
|--------|------------------|
| 1 (1) | `error_code == 1` and intensity ≥ 3 % |
| 2 (2) | RTK, gimbal and pose data available for the measurement interval (300 ms) |
| 3.1/3.2 (3) | RTK position within 0.5 m of a slice plane and within 0.5 m of a waypoint |
| 4 (4) | SD of RTK altitude during the measurement < 0.03 m |
| 5 (5) | \|yaw − yaw setpoint\| < 2° |
| 6 (6) | SD of gimbal pitch during the measurement < 0.05° |
| 7 (7) | squared norm of the mean velocity (vx, vy, vz) < 0.05 m²/s² (see Known issues, K4) |
| 8.1 (–) | values > 1.2 × expected value divided by round(value / expected) ("inter-reflections"; see K5) |
| 8.2 (8) | maximum concentration per waypoint and gimbal pose — **method (a)**; disabled for **method (b)** |

Parameters of the reconstruction (as used for the published results): cell size c = 0.5 m, ray model `path`,
regularisation λ = 1·10⁻⁵ (see K1), lower bound 1.8957 ppm (hard-coded "average background methane concentration in 2020").

Quantities of Table I:

* *Beam-hit ratio*: number of rays of method (a) that intersect a circle of radius 0.3 m around the bag centre
  and carry ≥ 100 ppm·m, divided by 13 (number of waypoints).
* *Simple concentration estimation*: maximum ppm·m of these rays divided by the bag diameter 0.6 m.
* *Estimated concentration*: sum of the reconstructed cell concentrations within r = 0.5 m and r = 1.0 m of the bag centre.
* *Relative error*: |estimate − expected| / expected.
* *Peak-to-bag distance*: distance between the cell with maximum concentration and the bag centre.
* *Jensen-Shannon divergence*: between the normalised reconstruction and a ground-truth map in which the expected
  concentration is distributed over the cells in proportion to their overlap with a 0.6 m × 0.6 m square around the bag centre.

### 5.2 Solver

The published results were computed with the commercial QP solver Gurobi (licence required; the licence
available for this check had expired). The objective, ‖Ax − b‖² + λ‖x‖² with x ≥ lower bound, is strictly convex and has
a unique minimiser. `reproduce.py` therefore solves the same problem by default as a bound-constrained linear
least-squares problem with SciPy (`scipy.optimize.lsq_linear`, BVLS). The original Gurobi formulation is kept and can be
selected with `--solver gurobi`.

### 5.3 Changes to the original code

The code in `analysis/` was imported unchanged from the BAM-internal repository `gastomo`, commit `26f7cf1`
(2024-06-06, state used for the final paper figures); see the first commit on this branch. Changes since then
(`git diff c2c8733 -- analysis`):

* input/output: raw files are read from `.gz`; results are written to a separate output directory instead of the raw-data folder;
  unused logger channels are not loaded; key numbers are additionally written as JSON/CSV;
* `extract_tdlas.py --method {max,all}` selects method (a)/(b) (previously done by editing the filter flags);
* `ct_ragt.py --solver {scipy,gurobi}`; the variance map, which is not used for any result, is no longer computed;
* compatibility: `matplotlib.cm.get_cmap` → `plt.get_cmap`, raw-string regular expressions;
* **bug fix** in `plot2d.py` (colour assignment of the rays in Fig. 2d, see K2);
* `analysis/sensitivity.py` (new) quantifies the effect of the issues K1 and K3.

`analysis/ct_mlem.py` (MLEM reconstruction) is included unchanged for completeness. It was **not used** for any
published result, was marked "still not working" by its authors and contains an indexing error
(`np.nonzero` of a 1×N row returns the row index 0, so all contributions are accumulated in cell 0).

---

## 6. Reproduction

### 6.1 Installation and execution

Requirements: Python 3.12 (tested with 3.12.3, Windows 11) and the packages in `requirements.txt`
(numpy, pandas, scipy, matplotlib, PyGeodesy, sympy, shapely, tabulate, pytz; pytest for the checks).
Gurobi (`gurobipy`) is optional and only needed for `--solver gurobi`.

```bash
python -m venv .venv
.venv/Scripts/activate                 # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python reproduce.py                    # Table I + Fig. 2, all trials and both methods
python analysis/sensitivity.py         # optional, effect of K1 and K3 (requires reproduce.py first)
pytest -q                              # checks
```

Run time of `reproduce.py` on a standard office PC: approx. 20–30 min (most of it in `extract_tdlas.py`).
Single trials: `python reproduce.py --trials 5`. Intermediate files go to `work/` (not versioned).

### 6.2 Outputs (`results/`)

| File | Content |
|------|---------|
| `table1_reproduced.csv` | all quantities of Table I for 8 trials × methods (a), (b), full precision |
| `table1_comparison.csv` | value-by-value comparison with the published Table I (`match` / `last-digit` / `DEVIATION`) |
| `summary_successful_trials.csv` | mean and SD over the successful trials (beam-hit ratio ≥ 80 %: trials 2, 3, 5, 8) |
| `solver_comparison_gurobi_2023.csv` | SciPy solver vs. values printed by the original Gurobi runs (2023) |
| `intermediate_comparison.csv` | ray files vs. the ray files produced for the paper in 2023 |
| `filter_statistics.csv` | number of measurements removed by each filter, per trial and method |
| `figures/fig2{a,b,c,d}_trial5_*` | Fig. 2 of the paper (trial 5), PNG and PDF |
| `sensitivity/` | output of `analysis/sensitivity.py` (Sec. 7) |

### 6.3 Verification performed for v1.0.0

All checks below were executed; the automated ones are part of `pytest`.

| Check | Result |
|-------|--------|
| Raw data: decompressed files vs. SHA-256 of the original logger files (48 files) | identical |
| Ray files of all 16 runs vs. files produced in 2023 (`data/original_results`) | same rays and same concentrations; geometry differs by ≤ 2·10⁻⁹ m (floating point) |
| SciPy solver vs. printed Gurobi output (bag sums r = 0.5 m and 1.0 m, method (a), 8 trials) | identical to 0.01 ppm; identical hot-spot cells |
| Table I: 152 published values | 141 identical at published precision; 7 differ by one unit in the last printed digit; 4 deviate (K7) |
| Summary statistics in Sec. IV of the paper | reproduced, see below |
| Fig. 2a–c (trial 5) | visually identical to the published figure |
| Fig. 2d (trial 5) | ray colours corrected (K2); otherwise identical |
| `reproduce.py` from a fresh clone in a fresh virtual environment created from `requirements.txt` | see 6.4 |

The 7 last-digit differences: trial 4 simple estimate 28,861.7 ppm printed as 28,861 (truncated) and its relative error
11.006 % printed as 11.00 (both listed for methods a and b); trial 4 (b) r = 1.0 m: 17,857.50 ppm printed as 17,858;
trial 8 JSD 0.3547 (a) and 0.5147 (b) printed as 0.36 and 0.52 (cause not determinable; the Gurobi run of trial 8 did not
print the JSD).

Summary over the successful trials 2, 3, 5, 8 (population SD, n = 4, as in the paper):

| Quantity | Paper, method (a) | Reproduced (a) | Paper, method (b) | Reproduced (b) |
|----------|------------------|----------------|-------------------|----------------|
| relative error, r = 1.0 m | 4.2 % ± 0.6 % | 4.21 % ± 0.60 % | 35.8 % ± 10.6 % | 35.84 % ± 10.54 % |
| peak-to-bag distance | 0.52 m ± 0.28 m | 0.51 m ± 0.27 m | 0.75 m ± 0.18 m | 0.75 m ± 0.17 m |
| Jensen-Shannon divergence | 0.34 ± 0.04 | 0.34 ± 0.04 | 0.38 ± 0.11 | 0.38 ± 0.11 |

The small differences in the SDs result from computing them with the rounded table values in the paper.

### 6.4 Fresh-clone check

FRESH-CLONE-PENDING

---

## 7. Known issues found during the review

The published values are **not** changed by this release. `results/` reproduces the published analysis;
`analysis/sensitivity.py` quantifies the effect of the issues K1 and K3 separately (`results/sensitivity/`).

| | Issue | Effect |
|---|-------|--------|
| K1 | **Regularisation parameter.** The paper states λ = 0.1. The published Table I was computed with λ = 1·10⁻⁵ (default of `ct_ragt.py`; the analysis notebooks never set it). Table I is reproduced only with λ = 1·10⁻⁵. | With λ = 0.1, successful trials (a): relative error 4.5 % ± 1.6 %, peak-to-bag distance 0.56 m ± 0.22 m, JSD 0.34 ± 0.04. Individual values change, e.g. trial 4 (a) relative error (r = 1 m) 25.7 % → 17.9 %. |
| K2 | **Fig. 2d colours.** `plot2d.py` built 2n−2 line segments for n rays, so most rays were drawn with the colour of another ray (e.g. the darkest ray in the published figure carries 6,196 ppm·m, the ray with the maximum 11,891 ppm·m was drawn in the colour of 8,513 ppm·m). | Display only; the numbers (11,891 ppm·m, 19,818 ppm) are correct. **Fixed** in this release. |
| K3 | **Cell coordinates.** `cell_coords_x/y` are the lower cell edges of the grid used for the design matrix, but are used as cell centres for the hot-spot position, the radius sums, the ground-truth map, and in the plot (`pcolor(..., shading='auto')` centres each cell on its lower edge, i.e. the reconstruction in Fig. 2a is drawn shifted by −0.25 m in y and z relative to the bag circle). | Evaluated at the true cell centres, successful trials (a): relative error 4.5 % ± 0.3 %, peak-to-bag distance 0.33 m ± 0.21 m, JSD 0.36 ± 0.04. The aggregate statements of the paper are essentially unchanged, but individual values change, e.g. trial 4 (a) relative error 25.7 % → 4.2 %, trial 2 (a) peak-to-bag distance 0.16 m → 0.44 m. Corrected plot: `results/sensitivity/trial5_reconstruction_true_cell_positions.png`. |
| K4 | **Filter 7** is described in the paper as "SD of the velocity > 0.05 m/s"; the code removes measurements whose squared mean velocity norm is ≥ 0.05 m²/s² (i.e. ≥ 0.22 m/s). | Description only; results correspond to the code. |
| K5 | **Filter 8.1** (not described in the paper) divides values above 1.2 × the expected bag concentration by round(value/expected) to correct inter-reflections. It uses the reference value inside the pre-processing and compares ppm·m with ppm. | No value was changed in any trial (`filter_statistics.csv`), so no effect on the results; latent issue. |
| K6 | **Jensen-Shannon divergence** uses the natural logarithm, so its range is 0 to ln 2 ≈ 0.69, not 0 to 1 as stated in the paper. | Interpretation only. |
| K7 | **Rounding in Table I.** Simple relative error of trial 5 printed as 23.80 % (correct 23.78 %) and of trial 6 as 50.00 % (correct 50.04 %). | ≤ 0.04 percentage points. |
| K8 | **Figure annotation.** In Fig. 2a the inner dashed circle is drawn with r = 0.6 m, while the evaluation (and the caption) uses r = 0.5 m. | Display only; not changed. |
| K9 | **Variance map.** `getVarMap` divides the noise variance by the diagonal of (AᵀA + λI)⁻¹ instead of multiplying it. | Not used for any result; computation disabled in `ct_ragt.py`. |
| K10 | **Field notes.** For 2020-06-18 the note "#19 full mission, lidar not measured" does not match the data (flight 19 contains lidar data, flight 24 does not); the numbering of the notes may be shifted. | Lidar is not used by the analysis; trial assignment is confirmed independently (Sec. 3.1). |

---

## 8. Limitations and missing metadata

* **Ground truth.** The bag concentration was measured once per day after the experiments (Dräger X-am 5600).
  For 2020-06-18 only a range (1.62–1.70 Vol%) is documented; 16,500 ppm was used. Changes of the bag during the day
  are not captured (field note for trial 7: bag slack). The ground-truth map assumes a 0.6 m × 0.6 m square
  cross-section with homogeneous concentration.
* **Uncertainties.** No uncertainty of the reference instrument, of the TDLAS sensor or of the reconstruction is
  reported in the available material; no uncertainty is stated here.
* **Geometry.** The slice z-origin is the lowest RTK antenna height of the flight; rays end at z = 0 (no lidar range is
  used). Offsets between RTK antenna, gimbal and laser and the ground level at the bag are not documented.
* **Small sample.** 8 trials, 4 of them "successful"; the success criterion (beam-hit ratio ≥ 80 %) and all filter
  thresholds were chosen heuristically.
* **Missing or not included metadata:**
  * [TO BE PROVIDED: calibration status and uncertainty of the Dräger X-am 5600 and time of the measurements]
  * [TO BE PROVIDED: calibration/uncertainty of the TDLAS sensor (TGE LMm-G) used in 2020]
  * [TO BE PROVIDED: bag dimensions on 2020-06-18 (2020-06-29: 130 × 61 × 57 cm³ according to the field note) and meaning of the note "ca. 2350 ppm*m" on 2020-06-29]
  * [TO BE PROVIDED: source of the background concentration 1.8957 ppm used as lower bound]
  * [TO BE PROVIDED: reason for excluding 2020-06-18 flight 24]
  * wind data: anemometer recordings of 2020-06-18 and 2020-06-29 exist in the BAM archive but were not used in
    ISOEN 2024 and are not included;
  * the drawing of the experimental set-up (Fig. 1 of the paper) is not included (copyright IEEE).

---

## 9. Authors, licence, citation

* **Data:** recorded at BAM in June 2020 (authors of ISOEN 2024: P. P. Neumann, D. Hüllmann, N. P. Winkler, H. Lohrke, A. J. Lilienthal).
  [TO BE PROVIDED: persons to be credited as creators of the data set, if different]
* **Code:** Dino Hüllmann (2020) and Patrick P. Neumann (2023–2024), according to the history of the BAM-internal
  repository `gastomo`; adaptations for this release are recorded in the git history of this repository.
* **Licence:** [TO BE PROVIDED: licence for code (e.g. MIT/BSD) and for data (e.g. CC BY 4.0) — no licence information
  exists in the source material].
* **Funding:** [TO BE PROVIDED].

If you use this repository, please cite ISOEN 2024 (see top) and this repository
[TO BE PROVIDED: DOI of the archived release, e.g. Zenodo, if planned].

```bibtex
@inproceedings{Neumann2024ISOEN,
  author    = {Neumann, Patrick P. and H{\"u}llmann, Dino and Winkler, Nicolas P. and Lohrke, Heiko and Lilienthal, Achim J.},
  title     = {Outdoor Gas Plume Reconstructions: A Field Study with Aerial Tomography},
  booktitle = {2024 IEEE International Symposium on Olfaction and Electronic Nose (ISOEN)},
  address   = {Grapevine, TX, USA},
  pages     = {1--3},
  year      = {2024},
  doi       = {10.1109/ISOEN61239.2024.10556071}
}
```

Release history: see [RELEASE_NOTES.md](RELEASE_NOTES.md).
