# Release notes

## v1.0.0

First public version. Data and analysis of aerial gas tomography experiments carried out at BAM in 2016–2020 and
published in IEEE SENSORS 2018, European Journal of Remote Sensing 2019, IEEE ISOEN 2022 and IEEE ISOEN 2024, prepared
as documentation of preliminary work for the proposal CACTUS (DFG SPP 2433). The data are not results of CACTUS.

**Contents**

* Raw data (131 files, losslessly compressed, SHA-256 of the originals): all 8 trials of ISOEN 2024, the drone-to-drone
  flight of ISOEN 2022 with anemometer data, the 2016 earth-wall and scanning/aiming logs and the 2017 plume data
  (anemometers, reference gas sensor array, UAV logs of the three published trials).
* Metadata: trial assignments, inventory of all 79 flights of the June 2020 campaign with exclusion reasons, field notes,
  trial list of the 2017 campaign, data selection of the 2016 evaluation.
* Original analysis code (Python 2020–2024 with minimal documented adaptations; Matlab 2016–2017 for reference) and
  original evaluation workbooks and intermediate results.
* `reproduce.py`: one command for all reproduced results; `pytest` checks.
* Full texts of the four publications (`publications/`; IEEE papers as accepted manuscripts).
* Licences: code MIT, data/results/documentation CC BY 4.0.

**Verification** (README, Sec. 6.3)

* ISOEN 2024 Table I and summary statistics reproduced from the raw data (141 of 152 values identical, 7 last-digit
  differences, 4 rounding errors of the paper); ray files identical to those of 2023.
* EJRS 2019 Table 1 reproduced from the raw log, identical to the original workbook; experiment #3 (30.2 %), wind
  statistics (12/12) and the reference-array values (4 of 5 at published precision) reproduced; reconstructions of
  SENSORS 2018 / EJRS 2019 identical to the published maps.
* ISOEN 2022: 10 of 12 numbers reproduced.

**Known issues** (README, Sec. 7; published values are not changed)

* Regularisation λ = 1e-5 used instead of the stated λ = 0.1 (ISOEN 2024, SENSORS 2018).
* Cell lower-edge coordinates used as cell centres (ISOEN 2024); quantified separately.
* Published variance maps (SENSORS 2018, EJRS 2019) divide instead of multiply by diag((AᵀA+λI)⁻¹).
* EJRS 2019 Table 1 deviates in 16 values from its own workbook; inconsistent exclusion of invalid values.
* ISOEN 2022 wind statistics refer to the whole 3.7 h recording, not to the experiment.
* EJRS 2019 experiment #3: the 30.2 % detection share includes measurements with invalid error codes (12.9 % with
  valid measurements only).
* Fig. 2d colours of ISOEN 2024 (plotting bug, fixed); further minor issues K4–K10, E5, D2.
