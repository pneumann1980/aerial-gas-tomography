# Experiments and file assignment

[← README](../README.md) · **Experiments** · [Data](data.md) · [Analysis](analysis.md) · [Verification](verification.md)

Publication IDs: S18 (IEEE SENSORS 2018), R19 (European Journal of Remote Sensing 2019), I22 (IEEE ISOEN 2022),
I24 (IEEE ISOEN 2024); full citations in the [README](../README.md#publications).

## Origin of the data

* **2016–2017 (S18, R19):** BAM in-house interdisciplinary R&D project *Complex Fires – Consequences of accidental
  failure of gas tanks* (CoFi-ABV), in which the aerial platform UAV-REGAS was developed. The acknowledgements of
  S18/R19 also mention a related BMWi ZIM project (grant KF2201091HM4). Location: BAM Test Site for Technical Safety.
* **2020 (I22, I24):** research of the same group at BAM (I24 with a co-author at TUM); the publications state no
  third-party funding. Coordinates of the set-ups: `data/metadata/field_notes/Koordinaten.txt`.
* All measurements were taken with aerial robots and stationary reference instruments; there are no ground-robot
  measurements.

## Measurement set-up

* **Aerial robot:** DJI S1000+ octocopter (A3 Pro flight controller) with a 3-axis gimbal carrying a TDLAS CH4 sensor
  (TGE Laser Methane mini-G, ≈ 530 g: path-integrated concentration in ppm·m, backscatter intensity in %, error code;
  manufacturer accuracy ±10 %), a laser rangefinder (Astech LDS30M) and a camera. 2017: GPS and a modified DJI Zenmuse Z15 gimbal; 2016: DJI S900 (experiment
  descriptions and photos); 2020: D-RTK GNSS, custom gimbal and position controller. The ground (I22: a second drone)
  serves as reflector.
* **Reconstruction:** grid-based least squares with lower bound and Tikhonov regularisation (Trincavelli et al., IEEE
  SENSORS 2012); rays from the sensor pose to the reflecting surface; cell size 0.5 m.
* **Earth wall (R19, 2016-07-07):** UAV on the ground in front of a 30° earth wall (bright sand, dark sand, vegetation)
  at 10, 15 and 20 m; trial 1 = background, trial 2 = glass cube (0.2 m, 2.5 Vol% CH4) in the beam, trial 3 = reference
  against a white sheet; 2 Hz.
* **2D plume (S18, R19, Aug 2017):** natural gas released through tubes in front of a fan; reference: 10 Dräger PIR7000
  IR transmitters on a 2 m × 2 m × 2 m frame and two Metek uSonic-3 anemometers at 2 m (USA1) and 4 m (USA2), all 1 Hz;
  5 waypoints at ≈ 10 m, pitch scans from −60° to −120° in 5° steps.
* **Drone-to-drone (I22, 2020-07-14):** TDLAS aimed horizontally at a manually piloted DJI M100 carrying a cardboard
  reflector, ≈ 15 m apart at ≈ 3 m height, 3 m in front of a fan-driven CH4 source; two anemometers (10 Hz).
* **Static bag (I24, June 2020):** CH4-filled bag (≈ 1.3 m long, ≈ 0.6 m diameter, centre 1.85 m above ground);
  gate-shaped mission of 13 waypoints at 7, 8.5 and 10 m, pitch scans in 5° steps; bag concentration measured once per
  day with a Dräger X-am 5600 (16,500 ppm on 2020-06-18, 26,000 ppm on 2020-06-29).

## I24 — static bag, June 2020

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

The trial–flight assignment comes from the original analysis notebooks and agrees with the numbers of TDLAS records in
the LaTeX source of Table I. `data/metadata/campaign_2020-06_inventory.csv` lists all 79 flight folders of 2020-06-16
to 2020-06-30 with reached waypoints, duration, TDLAS records, status, exclusion reason and field note (German and
English). Flights not used:

1. 2020-06-16/17: set-up and commissioning; no reference concentration.
2. Flights without a complete 13-waypoint gate mission (tests, positioning, aborted flights).
3. Complete missions with a documented problem: 2020-06-18 #2 (RTK yaw not initialised), 2020-06-29 #0 (last
   waypoints incomplete), 2020-06-29 #12 (yaw twisted after take-off, "not usable for CT"); 2020-06-30 #0 (6 of 13
   waypoints).
4. 2020-06-18 #24 (complete mission): the reason is not documented.

Measurements within a trial are removed by the filters of the pipeline ([Analysis](analysis.md#i24-processing-chain));
counts per filter: `results/filter_statistics.csv`.

## I22 — drone-to-drone, 2020-07-14

Flight 7 (field note "Copter zu Copter"): `data/raw/copter/2020-07-14/7` (TDLAS records and mission log); anemometers
`data/raw/anemometer/2020-07-14/0` (0 = left, 1 = right). The evaluation window (1,242 TDLAS records from "copter reaches
WP" to "copter landing") is taken from the original workbook `data/original_results/isoen2022/evaluation.xlsx` (a local
file path was removed from its file metadata; cell contents unchanged).

## S18 / R19 — CoFi-ABV experiments 2016–2017

| Experiment | Raw data | Original evaluation |
|------------|----------|---------------------|
| Earth wall, 2016-07-07 (R19 Table 1, Fig. 8) | `data/raw/cofi-abv/2016-07-07_earth-wall/111649.CSV.gz` (ID ranges: `data/metadata/cofi-abv/2016-07-07_earth-wall_description.txt`) | `data/original_results/ejrs2019/comp_surface.xlsx` |
| Scanning and aiming, 2016-07-20 (R19 Fig. 9) | `data/raw/cofi-abv/2016-07-20_scanning-aiming/*.CSV` (description in `data/metadata/cofi-abv/`) | `comp_scanning.xlsx`, `glass_cube_aiming.xlsx` |
| 2D plume, 2017-08-03 (day #1) and 2017-08-07 (day #2) (S18 Fig. 4, R19 Figs. 10–12) | anemometers, reference gas sensor array (all files), UAV logs (`*.dmf`) of the three published trials | ray files of 10 trials computed in 2017: `data/original_results/ejrs2019/rays_matlab_2017/` |

Trial list of the plume campaign: `data/metadata/cofi-abv/2017-08_plume_Experimente (Plume).xlsx` (original, German;
first names of persons replaced by the name of the data stream they recorded, otherwise unchanged). Published trials:
day #1 trial #4 = UAV flight 13 = gas array "Messung 6"; day #2 trials #10 and #13 = flights 87 and 90. Further UAV
logs, videos and photos remain in the BAM archive.

### Number of trials (R19)

S18/R19 report 26 trials. The trial list contains 29 runs on the two days, 2 of them "wind measurement only", which
leaves 27 runs with gas release. One further run must have been left out; three candidates remain and the material does
not decide between them: day #1 run 8 ("not evaluable, yaw problems"), day #2 run 7 (no UAV log) and day #2 run 8
("aborted (WLAN)").

## Unpublished experiments, July 2020

The free-plume and two-slice experiments of July 2020 were **not published and have not been evaluated**; no reference
concentration was measured. Their raw data are included unchanged for completeness; the repository contains no results
for them.

* **Set-up:** CH4 release in front of a fan, two anemometers (left/right as in I22); set-up sketch (file created
  2020-06-12, German): `data/metadata/field_notes/2020_Versuchsübersicht.pdf`.
* **Missions** (`data/metadata/missions/`, QGroundControl WPL format; identified for each flight from the waypoint
  coordinates of its log): `stream1` — one line of 11 waypoints, 1.0 m apart, at 10 m height; `stream2` — two parallel
  lines ("slices") ≈ 1.5 m apart with 7 waypoints each, 1.65 m apart, at 10 m. At each waypoint the custom command 31010
  of the flight software runs with the parameters 60, 120, 5. The directory also holds the missions of the June bag
  campaign (`sack1`–`sack3`) and of the drone-to-drone flights (`copter2copter*`).
* **Flights with raw data** (same channels as I24; anemometers in `data/raw/anemometer/2020-07-08/0`, `2020-07-13/0`,
  `2020-07-14/0`):

  | Experiment (mission) | Flights (field note) |
  |----------------------|----------------------|
  | free plume (`stream1`) | 2020-07-08 #6, #7 (not noted), #12 ("gimbal yaw rotated by one notch"); 2020-07-13 #0 (5 bar), #1 (3.5 bar), #2, #4, #6, #8, #9, #10 (2.5 bar); 2020-07-14 #0, #1 (2.5 bar) |
  | two slices (`stream2`) | 2020-07-14 #2 (TDLAS battery empty at the 2nd slice), #8 (battery empty very early), #9 (not noted, 1 waypoint), #11 (16 waypoints) |
  | drone-to-drone (`copter2copter`) | 2020-07-14 #3 ("wrong height"; TDLAS and mission log only) |

* **Inventory:** `data/metadata/campaign_2020-07_inventory.csv` lists all 44 flight folders of 2020-07-07 to
  2020-07-14 (mission, reached waypoints, duration, TDLAS records, inclusion, field note). Not included: flights without
  TDLAS data or without a mission (positioning, take-off survey, anemometer ascent, 2020-07-14 #13–#18 with mission
  `sprengplatz2` at another location) and empty folders.
* **Not documented:** release rate, gas composition, fan setting, meaning of the pressure values (5 / 3.5 / 2.5 bar);
  field notes are missing for some flights (2020-07-08; 2020-07-14 #9, #10, #12–#18).

## Not included

2016 first flight tests and laser tracking, 2017-08 wind experiments, 2019 laboratory measurements of the TDLAS spot
size, all videos and photos.
