# Data

[← README](../README.md) · [Experiments](experiments.md) · **Data** · [Analysis](analysis.md) · [Verification](verification.md)

## Structure

```
data/
  raw/                                 original logger files, gzip-compressed (lossless)
    copter/<date>/<flight>/            S1000+ logs 2020 (I24, I22, unpublished July 2020 flights)
    anemometer/<date>/0/               anemometers July 2020
    cofi-abv/2016-07-07_earth-wall/    payload log of the earth-wall experiment
    cofi-abv/2016-07-20_scanning-aiming/
    cofi-abv/2017-08_plume/            anemometers, gas sensor array, UAV logs (flights 13, 87, 90)
    SHA256SUMS_uncompressed.txt        SHA-256 of the original, uncompressed files (243 files)
    SHA256SUMS_gz.txt                  SHA-256 of the compressed files
  metadata/                            trial assignment, campaign inventories, field notes (verbatim), missions, selections
  original_results/                    results produced for the publications (tables, workbooks, ray files, Gurobi output)
```

**Raw data are unchanged.** Every original file was compressed with gzip (`-9 -n`); decompressing yields the
byte-identical original (checked by `pytest`). The scripts read the `.gz` files directly. Only the channels used by an
analysis are included; the BAM archive holds the complete recordings.

## Files and units

| File | Content and units |
|------|-------------------|
| `copter/.../tdlas.tsv` | TDLAS: Unix time (µs), error code (1 = valid), concentration (ppm·m), intensity (%) |
| `copter/.../dji_rtk.csv` | D-RTK: Unix time (µs), …, longitude, latitude (deg), height (m), velocities (m/s), yaw (deg) |
| `copter/.../dji_pose_fused.csv` | A3 fused pose: quaternion, accelerations, velocities `vx, vy, vz` (m/s) |
| `copter/.../GimbalRealtimeData4.tsv` | gimbal controller; schema with units in `GimbalRealtimeData4.tsv-metadata.yaml` (angles in deg) |
| `copter/.../copter_activity.log` | mission log (JSON lines): waypoints, yaw set-points, "reached" events |
| `anemometer/.../anemometer*.tsv` | ISO time, heater, `v_x, v_y, v_z` (cm/s), temperature (0.01 °C), …; schema in `*-metadata.yaml` |
| `cofi-abv/2016-*/*.CSV` | payload logger (`;`, decimal comma): IMU, GPS, TDLAS (`int[%]`, `conc[ppm x m]`, `err_code[LMm-G]`), rangefinder (`dist[m]`, `err_code[LDS30-M]`) |
| `cofi-abv/2017-08_plume/anemometer/*/USA-0*.txt` | Metek uSonic-3, 1 Hz, header with units (m/s, deg, °C) |
| `cofi-abv/2017-08_plume/gas_sensor_array/*.csv` | Agilent U2355A, 10 channels, 1 Hz, logged unit "Vol%" (× 10⁴ = ppm), decimal comma |
| `cofi-abv/2017-08_plume/s1000/*/*.dmf` | UAV payload logs, binary DMF format (schema `struct_def.xml`); reader: `analysis/matlab_2017/load_dmf.m` (Matlab/GNU Octave) |

Column names of the 2020 logs are defined in `analysis/copter_data_loader.py`.

## Metadata

| Path | Content |
|------|---------|
| `metadata/trials.csv` | I24 trial ↔ flight, expected concentration |
| `metadata/campaign_2020-06_inventory.csv`, `campaign_2020-07_inventory.csv` | all flight folders of the 2020 campaigns with status and field notes |
| `metadata/field_notes/` | field notes 2020 (German, verbatim), coordinates, set-up sketch |
| `metadata/missions/` | waypoint missions 2020 (QGroundControl WPL) |
| `metadata/cofi-abv/` | descriptions, data selections and trial list of the 2016–2017 experiments |
