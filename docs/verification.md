# Verification

[← README](../README.md) · [Experiments](experiments.md) · [Data](data.md) · [Analysis](analysis.md) · **Verification**

## Running the reproduction

Python 3.12 (tested with 3.12.3 on Windows 11), packages in `requirements.txt`. Besides the quick start in the README:

```bash
python reproduce.py --only-earlier   # S18 / R19 / I22 only (< 1 min)
python reproduce.py --trials 5       # I24 trial 5 only
pytest -q -m "not slow"              # checks without the end-to-end run of trial 5
```

Intermediate files are written to `work/` (not versioned).

## Outputs (`results/`)

| Path | Content |
|------|---------|
| `table1_reproduced.csv`, `table1_comparison.csv` | I24 Table I (8 trials × methods a, b), value-by-value comparison (`match` / `last-digit` / `DEVIATION`) |
| `summary_successful_trials.csv` | I24 mean and SD over the successful trials 2, 3, 5, 8 |
| `solver_comparison_gurobi_2023.csv`, `intermediate_comparison.csv`, `filter_statistics.csv` | I24 solver check, ray files vs. 2023, filter counts |
| `figures/` | I24 Fig. 2 (trial 5) |
| `sensitivity/` | I24 with λ = 0.1 and true cell centres (notes K1, K3) |
| `ejrs2019/table1_*.csv` | R19 Table 1, comparison with the printed table and the original workbook |
| `ejrs2019/aiming_*.csv` | R19 experiment #3 |
| `ejrs2019/plume_*.csv`, `ejrs2019/figures/` | R19/S18 wind and reference-array values, 20 reconstructions, maps of flights 13, 87, 90 |
| `isoen2022/comparison.csv` | I22 numbers |

## Checks

(T) = automated in `pytest`.

| Check | Result |
|-------|--------|
| (T) 243 raw files, decompressed, vs. SHA-256 of the originals | identical |
| **I24** (T) ray files of 16 runs vs. files produced in 2023 | same rays and concentrations; geometry ≤ 2·10⁻⁹ m |
| **I24** (T) SciPy vs. stored Gurobi output (bag sums, 8 trials) | identical to 0.01 ppm, identical hot-spot cells |
| **I24** (T) Table I, 152 values | 141 identical, 7 differ in the last printed digit, 4 deviate (K7) |
| **I24** summary statistics, Fig. 2 | reproduced (table below); Fig. 2a–c visually identical, Fig. 2d ray colours corrected (K2) |
| **R19** (T) Table 1, 162 values, from the raw log | identical to the original workbook (≤ 5·10⁻⁷); printed table: 146 identical, 8 last digit, 8 deviate (E1) |
| **R19** (T) wind statistics, 12 values | identical |
| **R19** (T) reference array, day #1 trial #4 | maximum 8,811 ppm identical; sensor 1 48.7 ± 213.2 ppm (paper 48 ± 213), sensor 3 1474.0 ± 2068.5 ppm (paper 1474 ± 2069) (E5) |
| **R19** (T) experiment #3, 30.2 % detection time | 484 of 1,603 samples = 30.19 % (E6) |
| **R19** experiment #2 (6 values) | located in `comp_scanning.xlsx` (e.g. RMSE 1.19° in `comp!BG927`); not recomputed from the raw logs |
| **R19** number of trials (26) | trial list: 27 runs with gas release ([Experiments](experiments.md#number-of-trials-r19)) |
| **S18/R19** reconstructions of flights 13, 87, 90 | mean and variance maps visually identical to the published figures (E3) |
| **I22** (T) 12 values | 10 identical; longest period and circular variance deviate (D1, D2) |
| Fresh clone + fresh virtual environment (Python 3.12.3, Windows 11) | all result tables identical in content; figures differ only at byte level; all tests passed |
| Not checked | Linux/macOS; other Python/package versions; `--solver gurobi` (no valid licence) |

I24 summary over the successful trials 2, 3, 5, 8 (population SD, n = 4):

| Quantity | Paper (a) | Reproduced (a) | Paper (b) | Reproduced (b) |
|----------|-----------|----------------|-----------|----------------|
| relative error, r = 1.0 m | 4.2 % ± 0.6 % | 4.21 % ± 0.60 % | 35.8 % ± 10.6 % | 35.84 % ± 10.54 % |
| peak-to-bag distance | 0.52 m ± 0.28 m | 0.51 m ± 0.27 m | 0.75 m ± 0.18 m | 0.75 m ± 0.17 m |
| Jensen-Shannon divergence | 0.34 ± 0.04 | 0.34 ± 0.04 | 0.38 ± 0.11 | 0.38 ± 0.11 |

The paper's SDs were computed from the rounded table values.

## Notes on the published results

The published values are not changed in this repository. The following differences were found during the reproduction
and are documented and, where possible, quantified.

### I24 (static bag, 2020)

Effects of K1 and K3: `results/sensitivity/`.

| | Note | Effect |
|---|------|--------|
| K1 | **Regularisation parameter:** the paper states λ = 0.1; Table I was computed with λ = 1·10⁻⁵ (default of `ct_ragt.py`). | With λ = 0.1, successful trials (a): relative error 4.5 % ± 1.6 %, peak-to-bag 0.56 m ± 0.22 m, JSD 0.34 ± 0.04; trial 4 (a): 25.7 % → 17.9 %. |
| K2 | **Fig. 2d colours:** most rays are drawn in the colour of another ray. | Display only; fixed. |
| K3 | **Cell coordinates:** lower cell edges are used as cell centres (hot spot, radius sums, ground truth, plot). | At true cell centres, successful trials (a): 4.5 % ± 0.3 %, 0.33 m ± 0.21 m, JSD 0.36 ± 0.04; trial 4 (a): 25.7 % → 4.2 %. |
| K4 | **Filter 7** is described as "SD of velocity > 0.05 m/s"; the code uses the squared mean velocity. | Description only. |
| K5 | **Filter 8.1** (not in the paper) compares ppm·m with ppm. | No value changed. |
| K6 | **JSD** uses the natural logarithm: range 0 to ln 2 ≈ 0.69. | Interpretation only. |
| K7 | **Rounding in Table I:** trial 5 simple relative error 23.80 % (23.78 %), trial 6 50.00 % (50.04 %). | ≤ 0.04 percentage points. |
| K8 | Fig. 2a: inner circle drawn with r = 0.6 m instead of 0.5 m. | Display only. |
| K9 | **Variance map formula** (`getVarMap`, `calculateGDM.m`): noise variance divided by, instead of multiplied with, diag((AᵀA + λI)⁻¹). | I24: not used; S18/R19: see E4. |
| K10 | Field note 2020-06-18 "#19 … lidar not measured" contradicts the data. | None (lidar not used). |

### S18 / R19 (2016–2017)

| | Note | Effect |
|---|------|--------|
| E1 | **R19 Table 1** differs from its own workbook in 16 of 162 values (transcription and rounding, e.g. dark sand 10 m trial 3: 0.41 m instead of 0.43 m). | Every value listed in `results/ejrs2019/table1_comparison.csv`. |
| E2 | **Exclusion of invalid values in Table 1** is inconsistent (removed for vegetation 20 m, not for dark sand 20 m trials 1 and 2); the 95 % CI uses n = 201 and the z-quantile throughout; 18 implausible distances were removed by hand. | Removing all error codes ≠ 1: dark sand 20 m trial 2 4,204 instead of 4,275 ppm·m (−1.7 %). |
| E3 | **Regularisation parameter:** S18 states λ = 0.1; the published maps use λ = 1·10⁻⁵ (as K1). | With λ = 0.1 the maps differ (`plume_reconstructions.csv`). |
| E4 | **Variance maps** (S18 Fig. 4b, R19 Fig. 10) use the formula of K9; they are high where many rays cross. | Their interpretation in S18/R19 should be re-examined. |
| E5 | **Reference array:** sensors are numbered 0–9 (R19 Fig. 11), negative values set to 0; the averaging window is not documented. Samples 8–264 (the period with gas signal) reproduce three of the four values. | Sensor 1 mean 48.7 ppm printed as 48 ppm. |
| E6 | **Experiment #3:** the 30.2 % counts samples > 200 ppm·m regardless of the TDLAS error code. | Valid measurements only (error code 1): 12.9 % (`aiming_variants.csv`). |

### I22 (drone-to-drone, 2020)

| | Note | Effect |
|---|------|--------|
| D1 | **Wind conditions** (349°–10°, S0 ≈ 0.6, 1.7 m/s) are statistics of the entire 3.7 h anemometer recording, not of the experiment (11:36–11:42 UTC). | During the experiment: mean direction 77° / 92°, S0 0.31 / 0.26, 1.71 / 1.84 m/s. |
| D2 | **Longest period** of consecutive successful measurements: paper ≈ 4 s, raw data 5.1 s. | Definition not documented. |

## Limitations and missing metadata

* **Ground truth I24:** bag concentration measured once per day after the experiments (2020-06-18: only the range
  1.62–1.70 Vol% documented, 16,500 ppm used); the ground-truth map assumes a homogeneous 0.6 m × 0.6 m cross-section.
* **Ground truth S18/R19:** point measurements of the reference array only; no quantitative comparison with the
  reconstructions was published.
* **Calibration and uncertainty:** the Dräger X-am 5600, the PIR7000 array and the TDLAS sensor were calibrated in the
  laboratory; calibration records and uncertainties are not part of the material, and none are stated here. The PIR7000
  signal is converted from "Vol%" to ppm with the factor 10⁴ only.
* **Geometry:** I24 slice origin at the lowest RTK antenna height, rays end at z = 0, sensor/antenna offsets not
  documented; 2017 GPS positioning without RTK.
* **Small samples and heuristic thresholds** (filters, success criterion ≥ 80 % beam-hit ratio).
* **Not documented:** source of the background value 1.8957 ppm (lower bound in I24); bag dimensions on 2020-06-18;
  meaning of the note "ca. 2350 ppm*m" (2020-06-29); reason why 2020-06-18 flight 24 was not used; the run of August
  2017 not among the 26 trials; averaging window of the reference array; release conditions of the July 2020
  experiments.
* Not included: anemometer recordings of 2020-06-18/29 (not used in I24), photos and videos.
