# Release notes

## v1.0.0

First public version: data and analysis of the aerial gas tomography field study published in
IEEE ISOEN 2024 (doi: 10.1109/ISOEN61239.2024.10556071), prepared as documentation of preliminary work
for the proposal CACTUS (DFG SPP 2433). The data were recorded at BAM in June 2020, before and independently of CACTUS.

**Contents**

* Raw logger data of all 8 trials (2020-06-18 and 2020-06-29), losslessly compressed, with SHA-256 checksums of the originals.
* Inventory of all 79 flights of the campaign with exclusion reasons and the original field notes.
* Original processing and reconstruction code (BAM-internal repository `gastomo`, commit 26f7cf1) with minimal,
  documented adaptations; `reproduce.py` regenerates Table I and Fig. 2 with one command.
* Reproduced results in `results/`, comparison with the published values, sensitivity analysis.

**Verification**

* Table I of ISOEN 2024 reproduced from the raw data; see README, section 6.
* Ray files of all trials agree with the files produced for the paper in 2023.

**Known issues** (details and quantified effects in README, section 7)

* K1: regularisation λ = 1e-5 was used for the published results; the paper states λ = 0.1.
* K2: colour assignment of the rays in Fig. 2d of the paper was wrong (plotting bug, fixed; numbers unaffected).
* K3: cell lower-edge coordinates are used as cell centres when evaluating the reconstruction.
* K4–K6: filter 7 differs from its description in the paper; filter 8.1 compares ppm·m with ppm; JSD uses the natural
  logarithm (range 0 to ln 2).

The published values are not changed in this release; the issues are documented and their effect is quantified separately.
