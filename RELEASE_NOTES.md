# Release notes

## v1.0.0

First public version. Data and analysis of aerial gas tomography experiments carried out at BAM in 2016–2020 and
published in IEEE SENSORS 2018, European Journal of Remote Sensing 2019, IEEE ISOEN 2022 and IEEE ISOEN 2024, prepared
as documentation of preliminary work for the proposal CACTUS (DFG SPP 2433). The data are not results of CACTUS.

**Contents**

* Raw data (243 files, losslessly compressed, SHA-256 of the originals): all 8 trials of ISOEN 2024, the drone-to-drone
  flight of ISOEN 2022 with anemometer data, the 2016 earth-wall and scanning/aiming logs and the 2017 plume data.
* Unpublished, unevaluated raw data of the July 2020 free-plume and two-slice experiments (19 flights).
* Metadata: trial assignments, flight inventories of the 2020 campaigns with exclusion reasons, field notes, mission
  files, trial list of the 2017 campaign.
* Original analysis code (Python 2020–2024 with minimal documented adaptations; Matlab 2016–2017 for reference),
  original evaluation workbooks and intermediate results.
* `reproduce.py` and `reproduce.ipynb`: one command (or one click) for all reproduced results; `pytest` checks.
* Licences: code MIT; data, results and documentation CC BY 4.0.

**Verification** (see `docs/verification.md`)

* ISOEN 2024: Table I and summary statistics reproduced from the raw data (141 of 152 values identical, 7 last-digit
  differences, 4 rounding differences in the paper).
* EJRS 2019: Table 1 identical to the original evaluation workbook; experiment #3, wind statistics and reference-array
  values reproduced (17 of 18 at published precision); reconstructions visually identical to the published maps.
* ISOEN 2022: 10 of 12 numbers reproduced.

**Notes on the published results** (published values are not changed; details in `docs/verification.md`)

* Regularisation λ = 1e-5 used instead of the stated λ = 0.1 (ISOEN 2024, SENSORS 2018).
* Lower cell edges used as cell centres (ISOEN 2024); effect quantified.
* Published variance maps (SENSORS 2018, EJRS 2019) divide instead of multiply by diag((AᵀA+λI)⁻¹).
* EJRS 2019 Table 1 differs in 16 values from its own workbook; exclusion of invalid values is inconsistent.
* EJRS 2019 experiment #3 includes measurements with invalid error codes (12.9 % with valid measurements only).
* ISOEN 2022 wind statistics refer to the whole 3.7 h recording, not to the experiment.
