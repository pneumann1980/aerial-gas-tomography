"""Checks that secure the reproducibility of the published results.

    pytest -q                 # all checks (approx. 3 min)
    pytest -q -m "not slow"   # without the end-to-end run of trial 5
"""
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'data' / 'raw'


def _sha256_gz(path):
    h = hashlib.sha256()
    with gzip.open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def test_raw_data_unchanged():
    """The decompressed raw files are byte-identical to the original logger files (SHA-256)."""
    lines = (RAW / 'SHA256SUMS_uncompressed.txt').read_text().splitlines()
    assert len(lines) == 48
    for line in lines:
        digest, rel = line.split('  ', 1)
        assert _sha256_gz(RAW / (rel + '.gz')) == digest, rel


def test_committed_results_match_paper():
    """results/table1_reproduced.csv reproduces every value of Tab. I (ISOEN 2024) at published precision,
    apart from documented last-digit rounding differences."""
    cmp = pd.read_csv(ROOT / 'results' / 'table1_comparison.csv')
    assert len(cmp) == 8 * 10 + 8 * 9  # 10 values for method (a), 9 for method (b) (no beam-hit ratio)
    # the only deviations are the documented rounding errors of the paper (README, K7):
    # simple relative error of trials 5 and 6 is printed as 23.80 / 50.00 instead of 23.78 / 50.04
    dev = cmp[cmp.status == 'DEVIATION']
    assert set(zip(dev.trial, dev.method, dev.quantity)) == {
        (5, 'a', 'simple_relative_error_pct'), (5, 'b', 'simple_relative_error_pct'),
        (6, 'a', 'simple_relative_error_pct'), (6, 'b', 'simple_relative_error_pct')}, dev.to_string()
    assert (dev.difference.abs() < 0.05).all()


def test_solver_reproduces_gurobi_2023():
    """The SciPy solver reproduces the bag sums printed by the original Gurobi runs to 0.01 ppm."""
    df = pd.read_csv(ROOT / 'results' / 'solver_comparison_gurobi_2023.csv')
    assert len(df) == 8
    assert (df.max_abs_diff_ppm <= 0.005 + 1e-9).all() and df.hot_spot_identical.all()


def test_committed_intermediate_results_match_2023():
    """The ray files of all trials agree with the files produced in 2023 (same rays, same concentrations)."""
    df = pd.read_csv(ROOT / 'results' / 'intermediate_comparison.csv')
    assert len(df) == 16
    assert (df.rays_reproduced == df.rays_original_2023).all()
    assert (df.max_abs_diff_geometry_m < 1e-6).all()
    assert (df.max_abs_diff_concentration_ppmm == 0).all()


@pytest.mark.slow
def test_end_to_end_trial5(tmp_path):
    """Full processing chain for trial 5, method (a), from the raw data (Fig. 2 of the paper)."""
    subprocess.run([sys.executable, str(ROOT / 'reproduce.py'), '--trials', '5',
                    '--work', str(tmp_path / 'work'), '--results', str(tmp_path / 'results')], check=True, cwd=ROOT)
    ref = np.loadtxt(ROOT / 'data' / 'original_results' / 'copter' / '2020-06-29' / '6' / 'max' / 'out_slice_0.csv', delimiter=';')
    new = np.loadtxt(tmp_path / 'work' / 'trial5_max' / 'out_slice_0.csv', delimiter=';')
    assert new.shape == ref.shape and np.abs(new - ref).max() < 1e-6
    ct = json.load(open(tmp_path / 'work' / 'trial5_max' / 'ct_slice_0.json'))
    rows = {r['radius_m']: r for r in ct['radius_rows']}
    assert round(rows[0.5]['bag_sum_ppm']) == 11579      # Tab. I, trial 5 (a)
    assert round(rows[1.0]['bag_sum_ppm']) == 25137
    assert round(ct['peak_to_bag_distance_m'], 2) == 0.93
    assert round(ct['jensen_shannon_divergence'], 2) == 0.35
    rays = json.load(open(tmp_path / 'work' / 'trial5_max' / 'rays_slice_0.json'))
    assert rays['max_concentration_hitting_bag_ppmm'] == 11891  # Sec. IV: 11,891 ppm m
