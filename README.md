# Aerial Gas Tomography — Data and Analysis

[![Code licence: MIT](https://img.shields.io/badge/code_licence-MIT-blue.svg)](LICENSE)
[![Data licence: CC BY 4.0](https://img.shields.io/badge/data_licence-CC_BY_4.0-lightgrey.svg)](LICENSES/CC-BY-4.0.txt)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](requirements.txt)

Field data and analysis code for **aerial gas tomography**: the reconstruction of two-dimensional methane (CH4)
distributions from remote TDLAS measurements taken by a drone with a gimballed laser sensor. The repository contains the
raw data of the experiments carried out at the Bundesanstalt für Materialforschung und -prüfung (BAM) in 2016–2020, the
original analysis code and a reproduction of the central results of four publications.

> This repository documents **preliminary work** for the proposal *CACTUS* (DFG Priority Programme SPP 2433). The data
> and results were produced before and independently of CACTUS and are not results of the CACTUS project.

## Publications

| ID | Publication | Experiments | Full text |
|----|-------------|-------------|-----------|
| S18 | P. P. Neumann et al., "Gas Tomography Up In The Air!", *IEEE SENSORS*, 2018. [doi:10.1109/ICSENS.2018.8630293](https://doi.org/10.1109/ICSENS.2018.8630293) | 2D plume, Aug 2017 | [DOI](https://doi.org/10.1109/ICSENS.2018.8630293) |
| R19 | P. P. Neumann et al., "Aerial-based gas tomography – from single beams to complex gas distributions", *European Journal of Remote Sensing* 52(sup3), 2019. [doi:10.1080/22797254.2019.1640078](https://doi.org/10.1080/22797254.2019.1640078) | earth wall and aiming, Jul 2016; 2D plume, Aug 2017 | [PDF](publications/R19_Neumann_et_al_2019_EJRS.pdf) |
| I22 | P. P. Neumann et al., "Remote Drone-to-Drone Gas Sensing: A Feasibility Study", *IEEE ISOEN*, 2022. [doi:10.1109/ISOEN54820.2022.9789627](https://doi.org/10.1109/ISOEN54820.2022.9789627) | drone-to-drone, Jul 2020 | [DOI](https://doi.org/10.1109/ISOEN54820.2022.9789627) |
| I24 | P. P. Neumann et al., "Outdoor Gas Plume Reconstructions: A Field Study with Aerial Tomography", *IEEE ISOEN*, 2024. [doi:10.1109/ISOEN61239.2024.10556071](https://doi.org/10.1109/ISOEN61239.2024.10556071) | static CH4 bag, Jun 2020 | [DOI](https://doi.org/10.1109/ISOEN61239.2024.10556071) |

Accepted manuscripts of the IEEE papers: [publications/](publications/README.md). In addition, the repository holds the raw data of unpublished free-plume and two-slice experiments of July 2020, which
have not been evaluated ([details](docs/experiments.md#unpublished-experiments-july-2020)).

## Quick start

Requires Python 3.12. Open [reproduce.ipynb](reproduce.ipynb) in Jupyter or VS Code and choose **Run All** — the
notebook creates a virtual environment, installs the dependencies, reproduces all results and shows a summary. Or on
the command line:

```bash
python -m venv .venv
.venv/Scripts/activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python reproduce.py               # all results, approx. 10-30 min
python analysis/sensitivity.py    # optional sensitivity analysis
pytest -q                         # checks
```

## Reproduction results

| Publication | Reproduced from the raw data | Result |
|-------------|------------------------------|--------|
| I24 | Table I (152 values), Fig. 2, summary statistics | 141 identical, 7 differ in the last digit, 4 rounding differences in the paper |
| I22 | all 12 numbers of Sec. IV | 10 identical |
| R19 | Table 1 (162 values) | identical to the original evaluation workbook |
| R19 | experiment #3, wind statistics, reference sensors (18 values) | 17 identical |
| S18, R19 | reconstructions of the three published trials | visually identical to the published maps |

The published values are not changed. All checks and the differences found are documented in
[docs/verification.md](docs/verification.md).

## Repository structure

```
data/raw/               original logger files (gzip, lossless; SHA-256 of the originals)
data/metadata/          trial assignment, campaign inventories, field notes, missions
data/original_results/  results produced for the publications (tables, workbooks, ray files)
analysis/               original analysis code (Python 2020-2024, Matlab 2016-2017) and reproduction scripts
results/                reproduced tables and figures
publications/           full text of R19 (open access), links to the other publications
docs/                   documentation
reproduce.py            runs the complete reproduction
reproduce.ipynb         the same in a notebook, including set-up of the environment
tests/                  automated checks
```

## Documentation

* [Experiments](docs/experiments.md) — set-ups, campaigns, assignment of raw data to trials, unused flights
* [Data](docs/data.md) — file formats, units, metadata
* [Analysis](docs/analysis.md) — processing chain, filters, solver, provenance and changes of the code
* [Verification](docs/verification.md) — checks, results, notes on the published results, limitations

## Licence and citation

Code: [MIT](LICENSE). Data, results and documentation: [CC BY 4.0](LICENSES/CC-BY-4.0.txt). © Bundesanstalt für
Materialforschung und -prüfung (BAM). The publication in `publications/` is subject to its own terms
([details](publications/README.md)).

If you use the data, please cite the corresponding publication(s) and this repository (citation metadata:
[CITATION.cff](CITATION.cff); GitHub: "Cite this repository")
[TO BE PROVIDED: DOI of the archived release, e.g. Zenodo, if planned].

<details>
<summary>BibTeX</summary>

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

</details>

Release history: [RELEASE_NOTES.md](RELEASE_NOTES.md).
