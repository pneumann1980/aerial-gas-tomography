#!/usr/bin/env python3
"""Reproduce the published results from the raw data in data/raw.

Part 1 - IEEE ISOEN 2024 (Table I, Fig. 2):

For every trial (data/metadata/trials.csv) and both methods of the paper
    (a) 'max': maximum concentration per measuring pose (pipeline filters 1-8)
    (b) 'all': all valid measurements (pipeline without filter 8.2)
the original processing chain in analysis/ is executed:
    extract_tdlas.py -> pkl2csv.py -> plot2d.py -> ct_ragt.py
Intermediate files are written to work/ (not versioned); the result tables, the comparison
with the published values and the figures of trial 5 are written to results/.

Part 2 - earlier publications (each < 1 min), see analysis/ejrs2019_*.py and analysis/isoen2022_*.py:
    European Journal of Remote Sensing 2019 / IEEE SENSORS 2018: Table 1 (earth wall), wind statistics,
    reference gas sensor array, 2D plume reconstructions;  IEEE ISOEN 2022: drone-to-drone measurement.

Usage:  python reproduce.py                 # everything (approx. 30 min)
        python reproduce.py --trials 5      # ISOEN 2024 trial 5 only (part 2 is skipped)
        python reproduce.py --only-earlier  # part 2 only
        python reproduce.py --solver gurobi # original QP solver for ISOEN 2024 (Gurobi licence required)
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
ANALYSIS = ROOT / 'analysis'
CELL_SIZE = 0.5            # m, as in the paper
MEASUREMENT_OPTION = 'path'
BAG_DIAMETER = 0.6         # m, used for the simple concentration estimate (peak / diameter)
SUCCESS_BEAM_HIT_RATIO = 0.8  # trials with beam-hit ratio >= 80 % are 'successful' (paper, Sec. IV)
METHODS = {'max': 'a', 'all': 'b'}


def run(script, args, log):
    env = dict(os.environ, MPLBACKEND='Agg', PYTHONIOENCODING='utf-8', PYTHONWARNINGS='ignore')
    cmd = [sys.executable, str(ANALYSIS / script)] + [str(a) for a in args]
    log.write(f'\n$ {" ".join(cmd)}\n')
    log.flush()
    subprocess.run(cmd, check=True, env=env, stdout=log, stderr=subprocess.STDOUT, cwd=ROOT)


def process(trial, method, work, solver, lam, force):
    out = work / f'trial{trial.trial}_{method}'
    if (out / 'ct_slice_0.json').exists() and not force:
        return out
    out.mkdir(parents=True, exist_ok=True)
    raw = ROOT / trial.raw_data_dir
    conc = trial.expected_concentration_ppm
    with open(out / 'log.txt', 'w', encoding='utf-8') as log:
        run('extract_tdlas.py', ['--file', raw, '--concentration', conc, '--out', out, '--method', method], log)
        run('pkl2csv.py', ['--file', raw, '--out', out], log)
        run('plot2d.py', ['--file', out], log)
        run('ct_ragt.py', ['--file', out, '--cell_size', CELL_SIZE, '--measurement_option', MEASUREMENT_OPTION,
                           '--concentration', conc, '--lambda_value', lam, '--solver', solver], log)
    return out


def collect(trials, work):
    rows, filters, intermediate = [], [], []
    for t in trials.itertuples():
        rays_a = json.load(open(work / f'trial{t.trial}_max' / 'rays_slice_0.json'))
        simple = rays_a['max_concentration_hitting_bag_ppmm'] / BAG_DIAMETER
        for method, label in METHODS.items():
            d = work / f'trial{t.trial}_{method}'
            ct = json.load(open(d / 'ct_slice_0.json'))
            r = {row['radius_m']: row for row in ct['radius_rows']}
            c = t.expected_concentration_ppm
            rows.append({
                'trial': t.trial, 'method': label,
                'beam_hit_ratio_pct': 100 * rays_a['beam_hit_ratio'] if label == 'a' else np.nan,
                'simple_concentration_ppm': simple,
                'simple_relative_error_pct': abs(simple - c) / c * 100,
                'estimated_concentration_r05_ppm': r[0.5]['bag_sum_ppm'],
                'estimated_concentration_r10_ppm': r[1.0]['bag_sum_ppm'],
                'relative_error_r05_pct': r[0.5]['relative_error_pct'],
                'relative_error_r10_pct': r[1.0]['relative_error_pct'],
                'expected_concentration_ppm': c,
                'peak_to_bag_distance_m': ct['peak_to_bag_distance_m'],
                'jensen_shannon_divergence': ct['jensen_shannon_divergence'],
                'num_measurements': ct['num_measurements'],
                'hot_spot_y_m': ct['hot_spot_x'], 'hot_spot_z_m': ct['hot_spot_y'],
                'solver': ct['solver'], 'lambda': ct['lambda'],
            })
            fl = json.load(open(d / 'filter_log.json'))
            filters.append({'trial': t.trial, 'method': label, **fl})
            # comparison of the ray file with the one produced in 2023 (data/original_results)
            ref = ROOT / 'data' / 'original_results' / 'copter' / t.date / str(t.flight) / method / 'out_slice_0.csv'
            new = np.loadtxt(d / 'out_slice_0.csv', delimiter=';')
            old = np.loadtxt(ref, delimiter=';')
            same_shape = new.shape == old.shape
            intermediate.append({
                'trial': t.trial, 'method': label, 'rays_reproduced': len(new), 'rays_original_2023': len(old),
                'max_abs_diff_geometry_m': float(np.abs(new[:, :4] - old[:, :4]).max()) if same_shape else np.nan,
                'max_abs_diff_concentration_ppmm': float(np.abs(new[:, 4] - old[:, 4]).max()) if same_shape else np.nan,
            })
    return pd.DataFrame(rows), pd.DataFrame(filters), pd.DataFrame(intermediate)


# number of decimals printed in Tab. I of the paper (used to compare at published precision)
DECIMALS = {'beam_hit_ratio_pct': 0, 'simple_concentration_ppm': 0, 'simple_relative_error_pct': 2,
            'estimated_concentration_r05_ppm': 0, 'estimated_concentration_r10_ppm': 0,
            'relative_error_r05_pct': 2, 'relative_error_r10_pct': 2, 'expected_concentration_ppm': 0,
            'peak_to_bag_distance_m': 2, 'jensen_shannon_divergence': 2}


def compare(reproduced, published):
    out = []
    for p in published.itertuples(index=False):
        q = reproduced[(reproduced.trial == p.trial) & (reproduced.method == p.method)]
        if q.empty:
            continue
        q = q.iloc[0]
        for col, dec in DECIMALS.items():
            pub = getattr(p, col)
            if pd.isna(pub):
                continue
            dec_ = 2 if (col.endswith('_ppm') and pub != round(pub)) else dec  # e.g. 3.79 ppm (trial 7b)
            unit = 10.0 ** -dec_
            diff = round(q[col], dec_) - pub
            status = 'match' if abs(diff) < unit / 2 else ('last-digit' if abs(diff) <= unit * 1.0001 else 'DEVIATION')
            out.append({'trial': p.trial, 'method': p.method, 'quantity': col, 'published': pub,
                        'reproduced': q[col], 'difference': q[col] - pub, 'status': status})
    return pd.DataFrame(out)


def summary(table):
    """Mean +/- SD over the 'successful' trials (beam-hit ratio >= 80 %), as in Sec. IV of the paper."""
    hit = table[table.method == 'a'].set_index('trial').beam_hit_ratio_pct
    ok = hit[hit >= 100 * SUCCESS_BEAM_HIT_RATIO].index
    rows = []
    for label in METHODS.values():
        sub = table[(table.method == label) & table.trial.isin(ok)]
        for col in ['relative_error_r10_pct', 'peak_to_bag_distance_m', 'jensen_shannon_divergence']:
            rows.append({'method': label, 'quantity': col, 'trials': ' '.join(map(str, ok)), 'mean': sub[col].mean(),
                         'sd_population': sub[col].std(ddof=0), 'sd_sample': sub[col].std(ddof=1)})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--trials', type=int, nargs='*', help='trial numbers (default: all)')
    ap.add_argument('--solver', choices=['scipy', 'gurobi'], default='scipy')
    ap.add_argument('--lambda_value', type=float, default=1e-5,
                    help='regularisation parameter (1e-5 = value used for the published results, see docs/verification.md, note K1)')
    ap.add_argument('--work', default=str(ROOT / 'work'), help='directory for intermediate files')
    ap.add_argument('--results', default=str(ROOT / 'results'), help='output directory for tables and figures')
    ap.add_argument('--force', action='store_true', help='recompute even if intermediate results exist')
    ap.add_argument('--only-earlier', action='store_true', help='only part 2 (publications 2018-2022)')
    args = ap.parse_args()

    if args.only_earlier:
        return run_earlier()

    trials = pd.read_csv(ROOT / 'data' / 'metadata' / 'trials.csv')
    if args.trials:
        trials = trials[trials.trial.isin(args.trials)]
    work, res = Path(args.work), Path(args.results)
    res.mkdir(parents=True, exist_ok=True)

    for t in trials.itertuples():
        for method in METHODS:
            t0 = time.time()
            process(t, method, work, args.solver, args.lambda_value, args.force)
            print(f'trial {t.trial} ({t.date} flight {t.flight}), method {METHODS[method]}: done ({time.time() - t0:.0f} s)', flush=True)

    table, filters, intermediate = collect(trials, work)
    table.to_csv(res / 'table1_reproduced.csv', index=False, float_format='%.10g', lineterminator='\n')
    filters.to_csv(res / 'filter_statistics.csv', index=False, lineterminator='\n')
    intermediate.to_csv(res / 'intermediate_comparison.csv', index=False, float_format='%.3g', lineterminator='\n')

    # solver check: values printed by the original Gurobi runs (2 decimals) for method (a)
    gurobi = pd.read_csv(ROOT / 'data' / 'original_results' / 'gurobi_output_2023_method_a.csv')
    a = table[table.method == 'a'].set_index('trial')
    solver_cmp = pd.DataFrame({
        'trial': gurobi.trial,
        'bag_sum_r05_gurobi_2023': gurobi.bag_sum_r05_ppm.values,
        'bag_sum_r05_reproduced': a.reindex(gurobi.trial).estimated_concentration_r05_ppm.values,
        'bag_sum_r10_gurobi_2023': gurobi.bag_sum_r10_ppm.values,
        'bag_sum_r10_reproduced': a.reindex(gurobi.trial).estimated_concentration_r10_ppm.values,
        'hot_spot_identical': ((a.reindex(gurobi.trial).hot_spot_y_m.values == gurobi.hot_spot_y_m.values)
                               & (a.reindex(gurobi.trial).hot_spot_z_m.values == gurobi.hot_spot_z_m.values)),
    }).dropna(subset=['bag_sum_r05_reproduced'])
    solver_cmp['max_abs_diff_ppm'] = np.maximum(
        (solver_cmp.bag_sum_r05_reproduced - solver_cmp.bag_sum_r05_gurobi_2023).abs(),
        (solver_cmp.bag_sum_r10_reproduced - solver_cmp.bag_sum_r10_gurobi_2023).abs())
    solver_cmp.to_csv(res / 'solver_comparison_gurobi_2023.csv', index=False, lineterminator='\n')

    published = pd.read_csv(ROOT / 'data' / 'original_results' / 'isoen2024_table1.csv')
    cmp = compare(table, published)
    cmp.to_csv(res / 'table1_comparison.csv', index=False, float_format='%.10g', lineterminator='\n')
    if set(trials.trial) == set(published.trial):
        summary(table).to_csv(res / 'summary_successful_trials.csv', index=False, float_format='%.4f', lineterminator='\n')

    # figures of the example trial (Fig. 2 of the paper)
    if 5 in set(trials.trial):
        fig = res / 'figures'
        fig.mkdir(exist_ok=True)
        for src, dst in [('trial5_max/CT_sliceID=0_c=0.50m_CT', 'fig2a_trial5_reconstruction'),
                         ('trial5_max/GT_sliceID=0_c=0.50m_CT', 'fig2b_trial5_ground_truth'),
                         ('trial5_max/out_slice_0.csvTDLAS_rays_slice_0_all', 'fig2c_trial5_rays_all'),
                         ('trial5_max/out_slice_0.csvTDLAS_rays_slice_0_filtered', 'fig2d_trial5_rays_hitting_bag')]:
            for ext in ('png', 'pdf'):
                shutil.copyfile(work / f'{src}.{ext}', fig / f'{dst}.{ext}')

    n_dev = int((cmp.status == 'DEVIATION').sum()) if len(cmp) else 0
    print(f'\nCompared {len(cmp)} published values: {int((cmp.status == "match").sum())} match, '
          f'{int((cmp.status == "last-digit").sum())} differ in the last printed digit, {n_dev} deviate.')
    print(f'Results written to {res}')
    if not args.trials:
        run_earlier()
    return 0


def run_earlier():
    """Part 2: results of the publications 2018-2022 (written to results/ejrs2019 and results/isoen2022)."""
    sys.path.insert(0, str(ANALYSIS))
    import ejrs2019_aiming
    import ejrs2019_earth_wall
    import ejrs2019_plume
    import isoen2022_drone_to_drone
    for module in (ejrs2019_earth_wall, ejrs2019_aiming, ejrs2019_plume, isoen2022_drone_to_drone):
        module.main()
    return 0


if __name__ == '__main__':
    sys.exit(main())
