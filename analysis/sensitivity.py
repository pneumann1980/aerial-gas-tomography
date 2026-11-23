#!/usr/bin/env python3
"""Sensitivity of the ISOEN 2024 Table I values to two issues found during the v1.0.0 review.

This script does NOT change the reproduced paper values (results/table1_reproduced.csv). It re-evaluates
the ray files produced by reproduce.py (work/trial<N>_<method>/out_slice_0.csv) with the same
reconstruction (ct_ragt.py: path model, c = 0.5 m, lower bound 1.8957 ppm, same solver) in three variants:

  published   : lambda = 1e-5 and the original evaluation, i.e. cell_coords = lower cell edges are used as
                if they were cell centres for the hot-spot position, the radius sums, the ground-truth map
                and the plot (identical to ct_ragt.py, serves as a consistency check)
  lambda_0.1  : as 'published', but with lambda = 0.1 as stated in the paper (Sec. II)
  cell_centres: lambda = 1e-5, but hot spot, radius sums and ground-truth map evaluated at the true
                cell centres (lower edge + c/2) of the grid used to build the design matrix

Usage: python analysis/sensitivity.py [--work work] [--results results/sensitivity]
"""
import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mro_tomography import getMeasurementPath, solveQP, getHotSpotLocation, getConcentrationSum  # noqa: E402
from mro_geometry import intersecting_area  # noqa: E402
from mro_metrics import calculateJensenShannonDivergence  # noqa: E402

CELL = 0.5
BAG = (0.0, 1.85)
BAG_SIZE = 0.6
BACKGROUND = 1.8957
ROOT = Path(__file__).resolve().parent.parent


def reconstruct(path, lam, solver):
    data = pd.read_csv(path, delimiter=';', header=None)
    sx, sy, ex, ey, ppmm = (data.iloc[:, i] for i in range(5))
    min_x = min(sx.min(), ex.min()) - 0.5
    max_x = max(sx.max(), ex.max()) + 0.5
    min_y = min(sy.min(), ey.min()) - 0.5
    max_y = max(sy.max(), ey.max()) + 0.5
    nx = int(np.ceil((max_x - min_x) / CELL))
    ny = int(np.ceil((max_y - min_y) / CELL))
    cx = min_x + CELL * np.arange(nx)
    cy = min_y + CELL * np.arange(ny)
    A = np.vstack([getMeasurementPath(sx[m], ex[m], sy[m], ey[m], cx, cy) for m in range(len(ppmm))])
    x, _ = solveQP(A, ppmm.values, lam, BACKGROUND, solver=solver)
    return np.reshape(x, (ny, nx), order='F'), cx, cy


def evaluate(mean_map, cx, cy, expected):
    """Hot spot, radius sums, ground truth and JSD exactly as in ct_ragt.py for the given coordinates."""
    hx, hy = getHotSpotLocation(mean_map, cx, cy)
    X, Y = np.meshgrid(cx, cy, indexing='xy')
    gt = np.zeros_like(mean_map)
    for i in range(mean_map.shape[0]):
        for j in range(mean_map.shape[1]):
            gt[i, j] = expected * intersecting_area((X[i, j], Y[i, j]), CELL, BAG, BAG_SIZE) / BAG_SIZE ** 2
    gt[gt == 0] = BACKGROUND
    r05 = getConcentrationSum(mean_map, cx, cy, BAG, 0.5)
    r10 = getConcentrationSum(mean_map, cx, cy, BAG, 1.0)
    return {'estimated_concentration_r05_ppm': r05, 'estimated_concentration_r10_ppm': r10,
            'relative_error_r05_pct': abs(r05 - expected) / expected * 100,
            'relative_error_r10_pct': abs(r10 - expected) / expected * 100,
            'peak_to_bag_distance_m': float(np.hypot(hx - BAG[0], hy - BAG[1])),
            'jensen_shannon_divergence': float(calculateJensenShannonDivergence(mean_map, gt))}


def plot_corrected(mean_map, cx, cy, filename):
    """Reconstruction drawn with the true cell edges (the original plot centres each cell on its lower edge)."""
    edges_x = np.append(cx, cx[-1] + CELL)
    edges_y = np.append(cy, cy[-1] + CELL)
    fig, ax = plt.subplots(figsize=(10, 3))
    m = ax.pcolormesh(edges_x, edges_y, mean_map, shading='flat', cmap='hot_r')
    ax.set_aspect('equal')
    ax.set_xlim(-5, 5)
    ax.set_xlabel('y (m)')
    ax.set_ylabel('z (m)')
    for r, style, col in [(0.3, 'solid', 'green'), (0.5, 'dashed', 'red'), (1.0, 'dashed', 'red')]:
        ax.add_artist(plt.Circle(BAG, r, linewidth=1, color=col, linestyle=style, fill=False))
    fig.colorbar(m, ax=ax).set_label('Concentration (ppm)')
    fig.savefig(filename.with_suffix('.png'), bbox_inches='tight')
    fig.savefig(filename.with_suffix('.pdf'), bbox_inches='tight')
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--work', default=str(ROOT / 'work'))
    ap.add_argument('--results', default=str(ROOT / 'results' / 'sensitivity'))
    ap.add_argument('--solver', choices=['scipy', 'gurobi'], default='scipy')
    args = ap.parse_args()
    work, res = Path(args.work), Path(args.results)
    res.mkdir(parents=True, exist_ok=True)
    trials = pd.read_csv(ROOT / 'data' / 'metadata' / 'trials.csv')
    hit = pd.read_csv(ROOT / 'results' / 'table1_reproduced.csv').query("method == 'a'").set_index('trial').beam_hit_ratio_pct

    rows = []
    for t in trials.itertuples():
        for method, label in (('max', 'a'), ('all', 'b')):
            ray_file = work / f'trial{t.trial}_{method}' / 'out_slice_0.csv'
            c = t.expected_concentration_ppm
            mm, cx, cy = reconstruct(ray_file, 1e-5, args.solver)
            rows.append({'trial': t.trial, 'method': label, 'variant': 'published', **evaluate(mm, cx, cy, c)})
            rows.append({'trial': t.trial, 'method': label, 'variant': 'cell_centres',
                         **evaluate(mm, cx + CELL / 2, cy + CELL / 2, c)})
            if t.trial == 5 and method == 'max':
                plot_corrected(mm, cx, cy, res / 'trial5_reconstruction_true_cell_positions')
            mm01, cx01, cy01 = reconstruct(ray_file, 0.1, args.solver)
            rows.append({'trial': t.trial, 'method': label, 'variant': 'lambda_0.1', **evaluate(mm01, cx01, cy01, c)})
            print(f'trial {t.trial} method {label} done', flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(res / 'sensitivity_table.csv', index=False, float_format='%.10g')

    ok = hit[hit >= 80].index
    summ = (df[df.trial.isin(ok)]
            .groupby(['variant', 'method'])[['relative_error_r10_pct', 'peak_to_bag_distance_m', 'jensen_shannon_divergence']]
            .agg(['mean', lambda s: s.std(ddof=0)]))
    summ.columns = [f'{a}_{"mean" if b == "mean" else "sd_population"}' for a, b in summ.columns]
    summ.reset_index().to_csv(res / 'sensitivity_summary_successful_trials.csv', index=False, float_format='%.4f')
    print(summ.round(3).to_string())


if __name__ == '__main__':
    main()
