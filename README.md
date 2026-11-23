# aerial-gas-tomography

Experimental data and analysis code supporting the development of aerial gas tomography:
reconstruction of 2D cross-sections of a methane (CH4) distribution from remote TDLAS
measurements taken by an aerial robot (drone) with a gimballed sensor.

This repository documents **preliminary work** for the proposal *CACTUS* (DFG Priority Programme SPP 2433).
All data and results originate from **BAM research carried out 2016–2020 and published 2018–2024**, i.e. before
and independently of CACTUS; they are **not** results of the CACTUS project. The repository contains the raw
data, the original analysis code and a reproduction of the central published results of four publications
(in addition, the unpublished and unevaluated raw data of the July 2020 free-plume and two-slice experiments, Sec. 3.4):

| ID | Publication | Field campaign | Reproduced here |
|----|-------------|----------------|-----------------|
| **S18** | P. P. Neumann, D. Hüllmann, D. Krentel, M. Kluge, H. Kohlhoff, A. J. Lilienthal, "Gas Tomography Up In The Air!", *2018 IEEE SENSORS*, New Delhi, India, 2018, pp. 1–4. doi: [10.1109/ICSENS.2018.8630293](https://doi.org/10.1109/ICSENS.2018.8630293) | 2D plume, Aug 2017 | Fig. 4 (mean and variance map, day #1 trial #4) |
| **R19** | P. P. Neumann, H. Kohlhoff, D. Hüllmann, D. Krentel, M. Kluge, M. Dzierliński, A. J. Lilienthal, M. Bartholmai, "Aerial-based gas tomography – from single beams to complex gas distributions", *European Journal of Remote Sensing* 52(sup3), 2–16, 2019. doi: [10.1080/22797254.2019.1640078](https://doi.org/10.1080/22797254.2019.1640078) | earth wall Jul 2016; scanning/aiming Jul 2016; 2D plume Aug 2017 | Table 1; experiment #3; wind statistics; reference array; Fig. 10 reconstructions |
| **I22** | P. P. Neumann, D. Hüllmann, N. P. Winkler, J. Schugardt, "Remote Drone-to-Drone Gas Sensing: A Feasibility Study", *2022 IEEE International Symposium on Olfaction and Electronic Nose (ISOEN)*, Aveiro, Portugal, 2022, pp. 1–3. doi: [10.1109/ISOEN54820.2022.9789627](https://doi.org/10.1109/ISOEN54820.2022.9789627) | drone-to-drone, 2020-07-14 | all numbers of Sec. IV |
| **I24** | P. P. Neumann, D. Hüllmann, N. P. Winkler, H. Lohrke, A. J. Lilienthal, "Outdoor Gas Plume Reconstructions: A Field Study with Aerial Tomography", *2024 IEEE International Symposium on Olfaction and Electronic Nose (ISOEN)*, Grapevine, TX, USA, 2024, pp. 1–3. doi: [10.1109/ISOEN61239.2024.10556071](https://doi.org/10.1109/ISOEN61239.2024.10556071) | static CH4 bag, June 2020 | Table I, Fig. 2, all summary statistics (complete raw data of all 8 trials) |

Full texts of the four publications: [publications/](publications/).

**Quick start**

```bash
python -m venv .venv
.venv/Scripts/activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python reproduce.py               # everything, approx. 10-30 min (I24 dominates; --only-earlier: S18/R19/I22, < 1 min)
python analysis/sensitivity.py    # optional: effect of the issues K1 and K3 on I24
pytest -q                         # checks, approx. 3-15 min
```

Alternatively, open [reproduce.ipynb](reproduce.ipynb) in Jupyter or VS Code and choose **Run All**: it creates `.venv`,
installs `requirements.txt`, runs the three steps above and shows a summary with the main figures.

---

## 1. Origin of the data

* **2016–2017 (S18, R19):** BAM in-house interdisciplinary R&D project *Complex Fires – Consequences of accidental
  failure of gas tanks* (CoFi-ABV, BAM focus area "infrastructure"), in which the aerial platform UAV-REGAS was developed
  (R19, Sec. 3). The acknowledgements of S18/R19 also mention a related BMWi ZIM project (grant KF2201091HM4).
* **2020 (I22, I24):** research of the same group at BAM (I24 with a co-author at TUM). I22 and I24 contain no
  acknowledgement of funding; no third-party funding is stated for the 2020 campaigns.
* The 2016–2017 experiments took place on the BAM Test Site for Technical Safety (BAM TTS, R19); coordinates of the
  2020 set-ups: `data/metadata/field_notes/Koordinaten.txt`. All measurements were taken with aerial robots and
  stationary reference instruments; the material provided contains **no ground-robot measurements**.

---

## 2. Measurement set-up

* **Aerial robot:** DJI Spreading Wings S1000+ octocopter with A3 Pro flight controller; 3-axis gimbal carrying a TDLAS
  CH4 sensor (TGE Laser Methane mini-G, LMm-G; output: path-integrated concentration in ppm·m, backscatter intensity in %,
  error code), a laser rangefinder (Astech LDS30M) and a camera. 2017: GPS and a modified DJI Zenmuse Z15 gimbal
  (S18, R19); the 2016 experiments used a DJI S900 according to the experiment descriptions and photos;
  2020: D-RTK GNSS, custom gimbal and custom PID position controller (I22, I24). The sensor uses the ground (or,
  in I22, a second drone) as reflector.
* **Reconstruction:** grid-based least squares with non-negativity/lower bound and Tikhonov regularisation
  (Trincavelli et al., IEEE SENSORS 2012); rays from the sensor pose to the reflecting surface; cell size 0.5 m.
* **Earth wall (R19, 2016-07-07):** UAV on the ground in front of a 30° earth wall (bright sand, dark sand, vegetation)
  at 10, 15 and 20 m; per case trial 1 = background, trial 2 = glass cube (0.2 m, 2.5 Vol% CH4) in the beam,
  trial 3 = reference against a white sheet; 2 Hz.
* **2D plume (S18, R19, Aug 2017):** natural gas released through tubes in front of a fan; reference: 10 Dräger PIR7000
  IR transmitters on a 2 m × 2 m × 2 m frame (1 Hz) and two Metek uSonic-3 anemometers at 2 m (USA1) and 4 m (USA2)
  (1 Hz); the UAV flew 5 waypoints at ≈ 10 m and scanned the pitch from −60° to −120° in 5° steps; 26 trials on two days.
* **Drone-to-drone (I22, 2020-07-14):** TDLAS on the S1000+ aimed horizontally at a manually piloted DJI M100 carrying
  a cardboard reflector, ≈ 15 m apart at ≈ 3 m height, 3 m in front of a fan-driven CH4 source; two anemometers (10 Hz).
* **Static bag (I24, June 2020):** CH4-filled bag (≈ 1.3 m long, ≈ 0.6 m diameter, centre 1.85 m above ground,
  at (y, z) = (0, 1.85) m in the slice); gate-shaped mission of 13 waypoints at 7, 8.5 and 10 m, pitch scans in 5° steps;
  reference: bag concentration measured once per day with a Dräger X-am 5600 (16,500 ppm on 2020-06-18,
  26,000 ppm on 2020-06-29).

---

## 3. Campaigns and file assignment

### 3.1 I24 — static bag, June 2020 (complete)

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

The assignment trial ↔ flight comes from the original analysis notebooks and is confirmed independently by the numbers
of TDLAS records noted in the LaTeX source of Table I. `data/metadata/campaign_2020-06_inventory.csv` lists **all 79
flight folders** of 2020-06-16 to 2020-06-30 with reached waypoints, duration, TDLAS records, status, exclusion reason
and the original field note (German, with English translation). Exclusion rules:

1. 2020-06-16/17: set-up and commissioning (positioning, controller tuning, yaw alignment); no reference concentration.
2. Flights without a complete 13-waypoint gate mission (tests, positioning, aborted flights).
3. Complete missions with a documented problem: 2020-06-18 #2 (RTK yaw not initialised), 2020-06-29 #0 (last
   waypoint(s) incomplete), 2020-06-29 #12 (yaw twisted after take-off, "not usable for CT").
4. 2020-06-30 #0: only 6 of 13 waypoints.
5. **Not documented:** 2020-06-18 #24 (complete mission with TDLAS data) was not used in I24; the reason is neither
   documented nor known any more.

Within a trial, measurements are removed by the filters of the pipeline (Sec. 5.1); counts per filter and trial:
`results/filter_statistics.csv`.

### 3.2 I22 — drone-to-drone, 2020-07-14

Flight 7 of 2020-07-14 (field note: "Copter zu Copter"): `data/raw/copter/2020-07-14/7` (TDLAS records and mission log);
anemometers: `data/raw/anemometer/2020-07-14/0` (anemometer 0 = left, anemometer 1 = right according to
`data/metadata/field_notes/Koordinaten.txt`). The evaluation window (1,242 TDLAS records from "copter reaches WP" to "copter
landing") is taken from the original workbook `data/original_results/isoen2022/evaluation.xlsx`.

### 3.3 R19 / S18 — CoFi-ABV experiments 2016–2017

| Experiment | Raw data in this repository | Original evaluation |
|------------|-----------------------------|---------------------|
| Earth wall, 2016-07-07 (R19 Table 1, Fig. 8) | `data/raw/cofi-abv/2016-07-07_earth-wall/111649.CSV` (all trials; ID ranges in `data/metadata/cofi-abv/2016-07-07_earth-wall_description.txt`) | `data/original_results/ejrs2019/comp_surface.xlsx` |
| Scanning while hovering and aiming at a leak, 2016-07-20 (R19 Fig. 9b/c) | `data/raw/cofi-abv/2016-07-20_scanning-aiming/*.CSV` (file description in `data/metadata/cofi-abv/2016-07-20_scanning-aiming_description.txt`) | `comp_scanning.xlsx`, `glass_cube_aiming.xlsx` |
| 2D plume, 2017-08-03 (day #1) and 2017-08-07 (day #2) (S18 Fig. 4, R19 Figs. 10–12) | anemometers (both days), reference gas sensor array (all files), UAV logs (`*.dmf`) of the three published trials | ray files of 10 trials computed in 2017: `data/original_results/ejrs2019/rays_matlab_2017/` |

Trial list of the plume campaign: `data/metadata/cofi-abv/2017-08_plume_Experimente (Plume).xlsx` (original, German;
the first names of the persons operating the data loggers were replaced by the name of the data stream, e.g.
"ROS (name)" → "ROS"; nothing else was changed). Published example trials: day #1 trial #4 = UAV flight 13 = gas array
"Messung 6"; day #2 trial #10 = flight 87; day #2 trial #13 = flight 90 (from the LaTeX sources of S18/R19 and the trial
list). Further UAV logs (other trials, rosbags), videos and photos remain in the BAM archive.

**Number of trials.** S18/R19 report 26 trials on the two days. The trial list contains 29 runs (day #1: 14, day #2: 15);
2 of them are "wind measurement only" (day #1 runs 13 and 14), which leaves 27 runs with gas release. Exactly one further
run must have been left out; the material allows three candidates and does not decide between them:
day #1 run 8 ("not evaluable (except reference data), yaw problems"), day #2 run 7 (no UAV log, "N/A??") and day #2
run 8 ("aborted (WLAN)").

### 3.4 Unpublished — free-plume and two-slice experiments, July 2020

These experiments were **not published and have not been evaluated**; no reference concentration was measured. Their
raw data are included unchanged for completeness of the 2020 campaigns; this repository contains no results for them.

* **Set-up** (field notes): CH4 release in front of a fan ("Versuchsaufbau mit Ventilator"), two anemometers (left and
  right as in Sec. 3.2); set-up sketch (file created 2020-06-12, German): `data/metadata/field_notes/2020_Versuchsübersicht.pdf`.
* **Missions** (`data/metadata/missions/`, QGroundControl WPL format; the mission of each flight was identified from the
  waypoint coordinates of its mission log): `stream1` — one line of 11 waypoints at 10 m height, 1.0 m apart;
  `stream2` — two parallel lines ("slices") ≈ 1.5 m apart with 7 waypoints each, 1.65 m apart, at 10 m height. At each
  waypoint the custom command 31010 of the flight software is executed with the parameters 60, 120, 5. The directory
  also contains the mission files of the June 2020 bag campaign (`sack1`–`sack3`) and of the drone-to-drone flights
  (`copter2copter*`).
* **Flights with raw data in this repository** (same channels as I24; anemometers: `data/raw/anemometer/2020-07-08/0`,
  `2020-07-13/0`, and `2020-07-14/0` of Sec. 3.2):

  | Experiment (mission) | Flights (field note) |
  |----------------------|----------------------|
  | free plume (`stream1`) | 2020-07-08 #6, #7 (not noted, 4 and 6 waypoints), #12 ("measurement, gimbal yaw rotated by one notch"); 2020-07-13 #0 (5 bar), #1 (3.5 bar), #2, #4, #6, #8, #9, #10 (2.5 bar); 2020-07-14 #0, #1 (2.5 bar) |
  | two slices (`stream2`) | 2020-07-14 #2 (TDLAS battery empty at the 2nd slice), #8 (TDLAS battery empty very early), #9 (not noted, 1 waypoint), #11 (16 waypoints) |
  | drone-to-drone (`copter2copter`) | 2020-07-14 #3 ("wrong height"; TDLAS and mission log only, as flight 7 of Sec. 3.2) |

* **Inventory:** `data/metadata/campaign_2020-07_inventory.csv` lists all 44 flight folders of 2020-07-07 to 2020-07-14
  with mission, reached waypoints, duration, TDLAS records, inclusion of the raw data and the field note (German and
  English). Not included are flights without TDLAS data or without a mission (positioning flights, survey of the
  take-off site, anemometer ascent 2020-07-13 #5, flights 2020-07-14 #13–#18 with the mission `sprengplatz2` at another
  location) and the empty folders.
* **Not documented:** release rate and gas composition, fan setting, meaning of the pressure values in the field notes
  (5 / 3.5 / 2.5 bar); 2020-07-08 and 2020-07-14 #9, #10, #12–#18 have no or only partial field notes.

### 3.5 Not included

2016 first flight tests and laser tracking, 2017-08 wind experiments, 2019 laboratory measurements of the TDLAS spot
size, all videos and photos.

---

## 4. Data

```
data/
  raw/                               original logger files, gzip-compressed (lossless)
    copter/<date>/<flight>/            S1000+ logs 2020 (I24: 8 trials; I22: 2020-07-14 flight 7; July 2020: Sec. 3.4)
    anemometer/<date>/0/               anemometers July 2020 (I22: 2020-07-14)
    cofi-abv/2016-07-07_earth-wall/    payload log earth-wall experiment
    cofi-abv/2016-07-20_scanning-aiming/
    cofi-abv/2017-08_plume/            anemometers, gas sensor array, UAV logs (flights 13, 87, 90)
    SHA256SUMS_uncompressed.txt        SHA-256 of the original, uncompressed files (243 files)
    SHA256SUMS_gz.txt                  SHA-256 of the compressed files
  metadata/                          trial assignment, campaign inventories, field notes (verbatim), missions, selections
  original_results/                  results produced for the papers (tables, workbooks, ray files, Gurobi output)
```

**Raw data are unchanged.** Every original file was compressed with gzip (`-9 -n`); decompressing yields the
byte-identical original (`pytest`: `test_raw_data_unchanged`). The scripts read the `.gz` files directly. Only
channels used by an analysis are included; the BAM archive holds the complete recordings.

| File | Content and units |
|------|-------------------|
| `copter/.../tdlas.tsv` | TDLAS: Unix time (µs), error code (1 = valid), concentration (ppm·m), intensity (%) |
| `copter/.../dji_rtk.csv` | D-RTK: Unix time (µs), …, longitude, latitude (deg), height (m), velocities (m/s), yaw (deg) |
| `copter/.../dji_pose_fused.csv` | A3 fused pose: quaternion, accelerations, velocities `vx, vy, vz` (m/s) |
| `copter/.../GimbalRealtimeData4.tsv` | gimbal controller, schema with units in `GimbalRealtimeData4.tsv-metadata.yaml` (angles in deg) |
| `copter/.../copter_activity.log` | mission log (JSON lines): waypoints, yaw set-points, "reached" events |
| `anemometer/.../anemometer*.tsv` | ISO time, heater, `v_x, v_y, v_z` (cm/s), temperature (0.01 °C), …; schema in `*-metadata.yaml` |
| `cofi-abv/2016-*/*.CSV` | payload logger (`;`, decimal comma): IMU, GPS, TDLAS (`int[%]`, `conc[ppm x m]`, `err_code[LMm-G]`), rangefinder (`dist[m]`, `err_code[LDS30-M]`) |
| `cofi-abv/2017-08_plume/anemometer/*/USA-0*.txt` | Metek uSonic-3, 1 Hz, header with units (m/s, deg, °C) |
| `cofi-abv/2017-08_plume/gas_sensor_array/*.csv` | Agilent U2355A, 10 channels, 1 Hz, logged unit "Vol%" (×10⁴ = ppm), decimal comma |
| `cofi-abv/2017-08_plume/s1000/*/*.dmf` | UAV payload logs in the binary DMF format (schema `struct_def.xml`); readable with the Matlab reader of the original project (not included) |

Column names of the 2020 logs are defined in `analysis/copter_data_loader.py`.

---

## 5. Analysis

### 5.1 I24 processing chain

`reproduce.py` runs, for every trial and for methods (a) and (b) of the paper, the original scripts:

| Step | Script | Function |
|------|--------|----------|
| 1 | `analysis/extract_tdlas.py` | loads the logs, converts RTK to local coordinates, assigns slice/waypoint/pose, applies the filters below |
| 2 | `analysis/pkl2csv.py` | laser ray per measurement (sensor pose → intersection with z = 0), projected into the slice plane |
| 3 | `analysis/plot2d.py` | ray plots (Fig. 2c, 2d), beam-hit ratio, maximum ray concentration through the bag |
| 4 | `analysis/ct_ragt.py` | reconstruction (λ = 1·10⁻⁵, lower bound 1.8957 ppm, c = 0.5 m, path model), evaluation, Fig. 2a/2b |

| Filter (paper) | Criterion in the code |
|----------------|-----------------------|
| 1 (1) | error code 1 and intensity ≥ 3 % |
| 2 (2) | RTK, gimbal and pose data available for the measurement interval (300 ms) |
| 3.1/3.2 (3) | within 0.5 m of a slice plane and of a waypoint |
| 4 (4) | SD of altitude < 0.03 m |
| 5 (5) | \|yaw − set-point\| < 2° |
| 6 (6) | SD of gimbal pitch < 0.05° |
| 7 (7) | squared norm of the mean velocity < 0.05 m²/s² (K4) |
| 8.1 (–) | values > 1.2 × expected concentration divided by round(value/expected) (K5) |
| 8.2 (8) | maximum per waypoint and pose — method (a); disabled for method (b) |

Quantities of Table I: *beam-hit ratio* = rays of method (a) intersecting a circle of r = 0.3 m around the bag centre
with ≥ 100 ppm·m, divided by 13; *simple estimate* = maximum of these rays / 0.6 m; *estimated concentration* = sum of
cell values within r = 0.5 m or 1.0 m of the bag centre; *peak-to-bag distance* = distance of the maximum cell;
*JSD* against a ground-truth map distributing the expected concentration over the cells by their overlap with a
0.6 m × 0.6 m square.

### 5.2 S18 / R19 / I22 scripts

| Script | Reproduces |
|--------|-----------|
| `analysis/ejrs2019_earth_wall.py` | R19 Table 1 from the raw log, with the data selection of the original workbook (ID ranges, removed values, n of the confidence intervals: `data/metadata/cofi-abv/2016-07-07_earth-wall_*.csv`) and, as a second variant, with all error codes ≠ 1 removed |
| `analysis/ejrs2019_aiming.py` | R19 experiment #3: share of time with detection from the raw logs, with the selection of the original workbook `glass_cube_aiming.xlsx`, and two variants restricted to valid error codes |
| `analysis/ejrs2019_plume.py` | R19 wind statistics (both days, both anemometers), reference array (day #1 trial #4: maximum, mean ± SD of sensors 1 and 3), reconstructions of all 10 ray files from 2017 (method of `analysis/matlab_2017/RAGT.m`: path model, c = 0.5 m, x ≥ 0, λ = 1·10⁻⁵ and, for comparison, 0.1), mean and variance maps of the three published trials |
| `analysis/isoen2022_drone_to_drone.py` | I22 measurement counts, maximum concentration, longest period, wind statistics (CircStat logic of `visualize_anemometer_data.m`) |

The 2017 ray tracing (`createLocalCoordinates4CT.m`, from the DMF logs) and all Matlab scripts of 2016–2018 are included
unchanged in `analysis/matlab_2017/` (selected files of the BAM-internal Matlab repository `gas_tomography`,
commit 4f43c4f, 2017-08-17; third-party toolboxes CircStat, geodetic and polygon_clip are not included). They require
Matlab and Gurobi and were **not re-executed**; the reconstructions start from the ray files written by them in 2017.
The numbers of R19 experiments #2 and #3 were computed by hand in Excel workbooks (included); those of experiment #3
were re-implemented, those of experiment #2 were located in the workbook but not re-implemented (Sec. 6.3).

### 5.3 Solver

The published reconstructions were computed with the commercial QP solver Gurobi (the licence available for this check
had expired). The objective ‖Ax − b‖² + λ‖x‖² with a lower bound is strictly convex and has a unique minimiser; the
scripts solve the same problem by default as bounded linear least squares with SciPy (`lsq_linear`, BVLS). The Gurobi
formulation is kept (`--solver gurobi`).

### 5.4 Changes to the original code

`analysis/*.py` was imported unchanged from the BAM-internal repository `gastomo`, commit `26f7cf1` (2024-06-06, state of
the final I24 figures; first commit of this branch). Changes since then (`git diff c2c8733 -- analysis`): reading of `.gz`
files and separate output directory; `extract_tdlas.py --method {max,all}`; `ct_ragt.py --solver`; key numbers written as
JSON/CSV; unused variance map no longer computed in `ct_ragt.py`; `plt.get_cmap` instead of the removed `cm.get_cmap`;
**bug fix** of the ray colours in `plot2d.py` (K2); new scripts `sensitivity.py`, `ejrs2019_*.py`, `isoen2022_*.py`.
`analysis/ct_mlem.py` (MLEM) is included unchanged; it was not used for any published result, was marked "still not
working" by its authors and contains an indexing error (`np.nonzero` of a 1×N row returns row index 0, so all
contributions are accumulated in cell 0).

---

## 6. Reproduction and verification

### 6.1 Execution

Python 3.12 (tested 3.12.3, Windows 11), packages in `requirements.txt`; `gurobipy` is optional.

```bash
pip install -r requirements.txt
python reproduce.py                  # I24 (approx. 10-30 min) and S18/R19/I22
python reproduce.py --only-earlier   # S18/R19/I22 only (< 1 min)
python reproduce.py --trials 5       # I24 trial 5 only
python analysis/sensitivity.py       # effect of K1/K3 on I24 (after reproduce.py)
pytest -q                            # all checks; pytest -q -m "not slow" skips the end-to-end run
```

Intermediate files go to `work/` (not versioned).

### 6.2 Outputs (`results/`)

| Path | Content |
|------|---------|
| `table1_reproduced.csv`, `table1_comparison.csv` | I24 Table I (8 trials × methods a, b) and value-by-value comparison (`match` / `last-digit` / `DEVIATION`) |
| `summary_successful_trials.csv` | I24 mean and SD over the successful trials 2, 3, 5, 8 |
| `solver_comparison_gurobi_2023.csv`, `intermediate_comparison.csv`, `filter_statistics.csv` | I24 solver check, ray files vs. 2023, filter counts |
| `figures/fig2*_trial5_*` | I24 Fig. 2 (trial 5) |
| `sensitivity/` | I24 effect of K1 and K3 |
| `ejrs2019/table1_reproduced.csv`, `ejrs2019/table1_comparison.csv` | R19 Table 1 (published selection and error-code variant), comparison with printed table and workbook |
| `ejrs2019/aiming_comparison.csv`, `ejrs2019/aiming_variants.csv` | R19 experiment #3 (detection share; variants by error code) |
| `ejrs2019/plume_comparison.csv`, `ejrs2019/plume_reconstructions.csv`, `ejrs2019/figures/` | R19/S18 wind and reference-array values; key numbers of 20 reconstructions; mean/variance maps of flights 13, 87, 90 |
| `isoen2022/comparison.csv` | I22 numbers |

### 6.3 Checks performed for v1.0.0

All checks were executed; those marked (T) are automated in `pytest`.

| Check | Result |
|-------|--------|
| (T) 243 raw files, decompressed, vs. SHA-256 of the originals | identical |
| **I24** (T) ray files of 16 runs vs. files produced in 2023 | same rays and concentrations; geometry ≤ 2·10⁻⁹ m |
| **I24** (T) SciPy vs. printed Gurobi output (bag sums, 8 trials) | identical to 0.01 ppm, identical hot-spot cells |
| **I24** (T) Table I, 152 values | 141 identical, 7 differ in the last printed digit, 4 deviate (K7) |
| **I24** summary statistics of Sec. IV | reproduced (table below) |
| **I24** Fig. 2a–c / 2d | visually identical / ray colours corrected (K2) |
| **R19** (T) Table 1, 162 values, from the raw log | identical to the original workbook (≤ 5·10⁻⁷); printed table: 146 identical, 8 last digit, 8 deviate (E1) |
| **R19** (T) wind statistics, 12 values | 12 identical |
| **R19** (T) reference array, day #1 trial #4: maximum, mean ± SD of sensors 1 and 3 | maximum 8,811 ppm reproduced; sensor 1 48.7 ± 213.2 ppm (paper 48 ± 213), sensor 3 1474.0 ± 2068.5 ppm (paper 1474 ± 2069) with the window identified in E5 |
| **R19** experiment #2 (6 values) | found as computed cells of `comp_scanning.xlsx`: RMSE 1.19° (`comp!BG927`), 1.92° (`BH927`), 1.49° (`BF927`); pitch −0.26° ± 1.86° (`Tabelle2!C927/C929`); altitude 0.10 ± 0.08 m (`Tabelle1!N927/N929`); orientation 0.27 ± 0.27 (`comp!Z927/Z929`); position 0.25 ± 0.12 m (`Tabelle1!J927/J929`) — not recomputed from the raw logs |
| **R19** (T) experiment #3, 30.2 % detection time | reproduced from the raw logs: 484 of 1,603 samples = 30.19 % (workbook `glass_cube_aiming.xlsx`, sheet Tabelle3); see E6 |
| **R19** number of trials (26) | trial list: 27 runs with gas release; see Sec. 3.3 |
| **S18/R19** reconstructions of flights 13, 87, 90 (λ = 1·10⁻⁵) | mean and variance maps visually identical to the published figures (E3) |
| **I22** (T) 12 values | 10 identical; longest period and circular variance deviate (D1, D2) |
| Fresh clone of this branch + fresh virtual environment from `requirements.txt` (Python 3.12.3, Windows 11): `reproduce.py`, `analysis/sensitivity.py`, `pytest` | all result tables identical in content to the committed ones; figures differ only at byte level (font rendering, ±1 pixel); 9 of 9 tests passed; run time 10 min including tests |
| Not checked | Linux/macOS; other Python/package versions; `--solver gurobi` (no valid licence) |

I24 summary over the successful trials 2, 3, 5, 8 (population SD, n = 4):

| Quantity | Paper (a) | Reproduced (a) | Paper (b) | Reproduced (b) |
|----------|-----------|----------------|-----------|----------------|
| relative error, r = 1.0 m | 4.2 % ± 0.6 % | 4.21 % ± 0.60 % | 35.8 % ± 10.6 % | 35.84 % ± 10.54 % |
| peak-to-bag distance | 0.52 m ± 0.28 m | 0.51 m ± 0.27 m | 0.75 m ± 0.18 m | 0.75 m ± 0.17 m |
| Jensen-Shannon divergence | 0.34 ± 0.04 | 0.34 ± 0.04 | 0.38 ± 0.11 | 0.38 ± 0.11 |

(The paper's SDs were computed from the rounded table values.) I24 last-digit differences: trial 4 simple estimate
28,861.7 ppm printed as 28,861 and 11.006 % as 11.00 (methods a and b); trial 4 (b) 17,857.50 ppm printed as 17,858;
trial 8 JSD 0.3547 (a) / 0.5147 (b) printed as 0.36 / 0.52.

---

## 7. Issues found during the review

Published values are **not** changed in this release; the issues are documented and, where possible, quantified.

**I24 (bag experiments 2020)** — effects of K1 and K3 in `results/sensitivity/`:

| | Issue | Effect |
|---|-------|--------|
| K1 | **Regularisation parameter.** The paper states λ = 0.1; Table I was computed with λ = 1·10⁻⁵ (default of `ct_ragt.py`, never set in the notebooks). | With λ = 0.1, successful trials (a): relative error 4.5 % ± 1.6 %, peak-to-bag 0.56 m ± 0.22 m, JSD 0.34 ± 0.04; individual values change (trial 4 (a): 25.7 % → 17.9 %). |
| K2 | **Fig. 2d colours.** 2n−2 line segments for n rays; most rays drawn in the colour of another ray. | Display only; fixed. |
| K3 | **Cell coordinates.** Lower cell edges are used as cell centres for hot spot, radius sums, ground-truth map and plot (Fig. 2a drawn shifted by −0.25 m in y and z). | At true cell centres, successful trials (a): 4.5 % ± 0.3 %, 0.33 m ± 0.21 m, JSD 0.36 ± 0.04; individual values change (trial 4 (a): 25.7 % → 4.2 %; trial 2 (a) peak-to-bag 0.16 m → 0.44 m). |
| K4 | **Filter 7** described as "SD of velocity > 0.05 m/s"; code: squared mean velocity ≥ 0.05 m²/s². | Description only. |
| K5 | **Filter 8.1** (not in the paper) uses the reference value and compares ppm·m with ppm. | Changed no value in any trial. |
| K6 | **JSD** uses the natural logarithm: range 0 to ln 2 ≈ 0.69, not 0 to 1. | Interpretation only. |
| K7 | **Rounding in Table I:** trial 5 simple relative error 23.80 % (correct 23.78 %), trial 6 50.00 % (50.04 %). | ≤ 0.04 percentage points. |
| K8 | Fig. 2a: inner dashed circle drawn with r = 0.6 m; evaluation and caption use 0.5 m. | Display only. |
| K9 | **Variance map formula** (`getVarMap`, and `calculateGDM.m` in 2017): noise variance **divided** by diag((AᵀA + λI)⁻¹); the least-squares variance is the product. | I24: not used. S18/R19: the published variance maps use this formula (see E4). |
| K10 | Field note 2020-06-18 "#19 … lidar not measured" contradicts the data (flight 19 has lidar data, flight 24 not). | None (lidar not used). |

**S18 / R19 (2016–2017)**

| | Issue | Effect |
|---|-------|--------|
| E1 | **Table 1 of R19 differs from its own workbook** in 16 of 162 values: e.g. dark sand 10 m trial 3 distance 0.41 m (workbook 0.43 m), dark sand 15 m trial 1 CI 2.6 (3.6) ppm·m, vegetation 15 m trial 3 3277.0 (3277.2) ppm·m; four distance CIs differ by 0.0002–0.0005 m and two concentration CIs by 0.02–0.04 ppm·m; several values are rounded in the wrong direction (e.g. 14.1847 m printed as 14.19 m). | Transcription/rounding; `results/ejrs2019/table1_comparison.csv` lists every value. |
| E2 | **Inconsistent exclusion in Table 1.** For vegetation 20 m invalid gas values were removed, for dark sand 20 m trials 1 and 2 not (error codes 0: 15 %, 5: 9 %), although the text states that non-valid data were excluded; the 95 % CI uses 1.96·SD/√201 also where fewer values remain (distances) and the z- instead of the t-quantile; 18 implausible distances (0.08–3.2 m at 20 m) with error code 1 were removed by hand. | Removing all error codes ≠ 1: dark sand 20 m trial 2 4,204 instead of 4,275 ppm·m (−1.7 %), trial 1 60.7 instead of 58.7 ppm·m (variant `error_codes` in `table1_reproduced.csv`). |
| E3 | **Regularisation parameter.** S18 states λ = 0.1; `RAGT.m` and the published maps use λ = 1·10⁻⁵ (as K1). | With λ = 0.1 the maps differ, e.g. flight 90: maximum 1,723 ppm at z = 6.25 m instead of 4,455 ppm at z = 1.25 m (`plume_reconstructions.csv`). |
| E4 | **Published variance maps** (S18 Fig. 4b, R19 Fig. 10) use the formula of K9; their values (≈ 6–43 "ppm²" for concentrations of thousands of ppm) scale inversely with the least-squares variance, i.e. they show high values where many rays cross. | The interpretation in S18/R19 (variance map as indicator of the source position, beams "indirectly visible") should be re-examined. |
| E5 | **Reference array statistics** (R19 Sec. 6): sensors are numbered 0–9 (R19 Fig. 11), i.e. sensor k = logger channel k+1; negative values are set to 0 (Fig. 11). The averaging window is not documented. The window of samples 8–264 (12:01:01–12:05:17, the period with gas signal) reproduces three of the four values; no window reproduces all four. | Sensor 1 mean 48.7 ppm is printed as 48 ppm (−0.7 ppm); the other values agree at the published precision. |
| E6 | **Experiment #3** (R19 Sec. 6): the 30.2 % counts all samples > 200 ppm·m regardless of the TDLAS error code; 200 of the 484 counted samples have error code 5 or 6. | With error codes 0 and 1 only (column "filtered" of the workbook): 17.7 %; with valid measurements only (error code 1): 12.9 % (`aiming_variants.csv`). |

**I22 (drone-to-drone 2020)**

| | Issue | Effect |
|---|-------|--------|
| D1 | **Wind conditions.** The reported values (349°–10°, S0 ≈ 0.6, 1.7 m/s) are the statistics of the **entire** anemometer recording (08:43–12:27 UTC, 3.7 h), not of the experiment (11:36–11:42 UTC). | During the experiment: mean direction 77° / 92°, S0 0.31 / 0.26, 1.71 / 1.84 m/s; the stated wind direction does not describe the experiment. S0 of the whole recording: 0.62 / 0.69 ("around 0.6"). |
| D2 | **Longest period** of consecutive successful measurements: paper ≈ 4 s, raw data 5.1 s (18 consecutive records). | Definition not documented (possibly from the video). |

---

## 8. Limitations and missing metadata

* **Ground truth I24:** bag concentration measured once per day after the experiments; for 2020-06-18 only a range
  (1.62–1.70 Vol%) is documented, 16,500 ppm was used; trial 7 field note: bag slack. Ground-truth map assumes a
  0.6 m × 0.6 m homogeneous cross-section.
* **Ground truth S18/R19:** point measurements of the reference array (2 m × 2 m frame) only; no quantitative comparison
  with the reconstructions was published.
* **Uncertainties:** no uncertainty of the reference instruments, the TDLAS sensor or the reconstructions is available
  in the material; none is stated here.
* **Geometry:** I24 slice z-origin = lowest RTK antenna height; rays end at z = 0; sensor/antenna offsets not
  documented. 2017: GPS positioning (no RTK), which S18/R19 identify as insufficient.
* **Small samples and heuristic thresholds** (filters, success criterion ≥ 80 % beam-hit ratio).
* **Missing information:**
  * Calibration: the Dräger X-am 5600, the PIR7000 array and the TDLAS sensor (TGE LMm-G) were calibrated in the
    laboratory; calibration records, dates and uncertainties are not part of the material. The PIR7000 signal is
    logged in "Vol%" and converted with the factor 10⁴ to ppm without further correction.
  * Not documented: source of the background concentration 1.8957 ppm used as lower bound in I24; bag dimensions on
    2020-06-18; meaning of the note "ca. 2350 ppm*m" on 2020-06-29; reason why 2020-06-18 flight 24 was not used;
    which run of August 2017 is not among the 26 trials (Sec. 3.3); averaging window of the reference array (E5);
    release conditions of the July 2020 experiments (Sec. 3.4).
  * Anemometer recordings of 2020-06-18/29 exist in the BAM archive but were not used in I24 and are not included.
  * Photos and videos of the experiments are not included.

---

## 9. Authors, licence, citation

* **Data:** recorded at BAM by the authors of the publications above (2016–2020).
* **Code:** Python (2020–2024): Dino Hüllmann and Patrick P. Neumann (history of the BAM-internal repository `gastomo`);
  Matlab (2016–2017): Patrick P. Neumann (history of the BAM-internal repository `gas_tomography`); adaptations for this
  release: git history of this repository.
* **Licence:** code (`analysis/`, `reproduce.py`, `tests/`): MIT ([LICENSE](LICENSE)); data, results and documentation
  (`data/`, `results/`, `*.md`): CC BY 4.0 ([LICENSES/CC-BY-4.0.txt](LICENSES/CC-BY-4.0.txt)); copyright holder:
  Bundesanstalt für Materialforschung und -prüfung (BAM). The files in `publications/` are excluded; their terms are
  given in [publications/README.md](publications/README.md).
* **Funding:** see Sec. 1.

Please cite the publication(s) above whose data you use and this repository
[TO BE PROVIDED: DOI of the archived release, e.g. Zenodo, if planned].

```bibtex
@inproceedings{Neumann2024ISOEN,
  author    = {Neumann, Patrick P. and H{\"u}llmann, Dino and Winkler, Nicolas P. and Lohrke, Heiko and Lilienthal, Achim J.},
  title     = {Outdoor Gas Plume Reconstructions: A Field Study with Aerial Tomography},
  booktitle = {2024 IEEE International Symposium on Olfaction and Electronic Nose (ISOEN)},
  pages     = {1--3}, year = {2024}, doi = {10.1109/ISOEN61239.2024.10556071}
}
@inproceedings{Neumann2022ISOEN,
  author    = {Neumann, Patrick P. and H{\"u}llmann, Dino and Winkler, Nicolas P. and Schugardt, Jan},
  title     = {Remote Drone-to-Drone Gas Sensing: A Feasibility Study},
  booktitle = {2022 IEEE International Symposium on Olfaction and Electronic Nose (ISOEN)},
  pages     = {1--3}, year = {2022}, doi = {10.1109/ISOEN54820.2022.9789627}
}
@article{Neumann2019EJRS,
  author  = {Neumann, Patrick P. and Kohlhoff, Harald and H{\"u}llmann, Dino and Krentel, Daniel and Kluge, Martin and Dzierli{\'n}ski, Marcin and Lilienthal, Achim J. and Bartholmai, Matthias},
  title   = {Aerial-based gas tomography -- from single beams to complex gas distributions},
  journal = {European Journal of Remote Sensing}, volume = {52}, number = {sup3}, pages = {2--16}, year = {2019},
  doi     = {10.1080/22797254.2019.1640078}
}
@inproceedings{Neumann2018SENSORS,
  author    = {Neumann, Patrick P. and H{\"u}llmann, Dino and Krentel, Daniel and Kluge, Martin and Kohlhoff, Harald and Lilienthal, Achim J.},
  title     = {Gas Tomography Up In The Air!},
  booktitle = {2018 IEEE SENSORS}, pages = {1--4}, year = {2018}, doi = {10.1109/ICSENS.2018.8630293}
}
```

Release history: [RELEASE_NOTES.md](RELEASE_NOTES.md).
