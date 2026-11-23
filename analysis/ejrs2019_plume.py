#!/usr/bin/env python3
"""2D plume experiments of August 2017 (IEEE SENSORS 2018, Fig. 4; European Journal of Remote Sensing 2019, Sec. 6).

Input : data/raw/cofi-abv/2017-08_plume/anemometer/<day>/USA-0{1,2}.txt.gz    ultrasonic anemometers (1 Hz)
        data/raw/cofi-abv/2017-08_plume/gas_sensor_array/*.csv.gz             reference array of 10 PIR7000 (1 Hz)
        data/original_results/ejrs2019/rays_matlab_2017/<flight>_out.CSV      rays computed in 2017 by the Matlab ray
                                                                             tracer createLocalCoordinates4CT.m
Output: results/ejrs2019/plume_comparison.csv, plume_reconstructions.csv, figures/plume_*.png|pdf

Reconstruction as in analysis/matlab_2017/RAGT.m (path model, cell size 0.5 m, lower bound 0, lambda = 1e-5 as in the
code; lambda = 0.1 as stated in the papers is computed for comparison) with the bounded least-squares solver of
analysis/mro_tomography.py. Variance map as in calculateGDM.m (published) and with the usual least-squares formula.
Day #1 = 2017-08-03, day #2 = 2017-08-07; day #1 trial #4 = flight 13, day #2 trials #10 / #13 = flights 87 / 90.
"""
import gzip
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mro_tomography import getMeasurementPath, solveQP  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'data/raw/cofi-abv/2017-08_plume'
OUT = ROOT / 'results/ejrs2019'
CELL = 0.5
PUBLISHED_FLIGHTS = {13: 'day #1, trial #4', 87: 'day #2, trial #10', 90: 'day #2, trial #13'}
DAYS = {'day1': '2017-08-03', 'day2': '2017-08-07'}


def wind(day, unit):
    with gzip.open(RAW / f'anemometer/{day}/USA-0{unit}.txt.gz', 'rt', encoding='latin-1') as fh:
        df = pd.read_csv(fh, skiprows=[1])
    w = df.vel.to_numpy(float) ** 2
    s = np.sum(w * np.exp(1j * np.radians(df.dir.to_numpy(float))))
    return {'speed': df.vel.mean(), 'direction': np.mod(np.degrees(np.angle(s)), 360), 'S0': 1 - abs(s) / w.sum()}


def gas_array(name):
    with gzip.open(RAW / 'gas_sensor_array' / f'{name}.gz', 'rt', encoding='latin-1') as fh:
        df = pd.read_csv(fh, sep=';', skiprows=32, header=None, decimal=',')
    return df.iloc[:, 1:11].to_numpy(float) * 1e4      # logged in Vol% -> ppm


def reconstruct(flight, lam):
    d = pd.read_csv(ROOT / f'data/original_results/ejrs2019/rays_matlab_2017/{flight}_out.CSV', sep=';', header=None)
    sx, sy, ex, ey, y = (d.iloc[:, i].to_numpy(float) for i in range(5))
    min_x, max_x = min(sx.min(), ex.min()) - 0.5, max(sx.max(), ex.max()) + 0.5
    min_y, max_y = min(sy.min(), ey.min()) - 0.5, max(sy.max(), ey.max()) + 0.5
    nx, ny = int(np.ceil((max_x - min_x) / CELL)), int(np.ceil((max_y - min_y) / CELL))
    cx, cy = min_x + CELL * np.arange(nx), min_y + CELL * np.arange(ny)
    A = np.vstack([getMeasurementPath(sx[m], ex[m], sy[m], ey[m], cx, cy) for m in range(len(y))])
    x, _ = solveQP(A, y, lam, 0.0, solver='scipy')
    res = y - A @ x
    var_noise = res @ res / abs(len(y) - A.shape[1])
    diag_inv = np.diag(np.linalg.inv(A.T @ A + lam * np.eye(A.shape[1])))
    shape = lambda v: np.reshape(v, (ny, nx), order='F')
    return {'mean': shape(x), 'var_published': shape(var_noise / diag_inv), 'var_ls': shape(var_noise * diag_inv),
            'cx': cx, 'cy': cy, 'n_rays': len(y)}


def plot(r, flight, filename):
    ex = np.append(r['cx'], r['cx'][-1] + CELL)
    ey = np.append(r['cy'], r['cy'][-1] + CELL)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for ax, key, label in [(axes[0], 'mean', 'Concentration (ppm)'), (axes[1], 'var_published', 'Variance (ppm$^2$)')]:
        m = ax.pcolormesh(ex, ey, r[key], shading='flat', cmap='hot_r')
        ax.set_aspect('equal')
        ax.set_xlabel('y (m)')
        ax.set_ylabel('z (m)')
        fig.colorbar(m, ax=ax, shrink=0.8).set_label(label)
    axes[0].set_title(f'Flight {flight} ({PUBLISHED_FLIGHTS[flight]}): mean map')
    axes[1].set_title('variance map (formula of calculateGDM.m)')
    fig.tight_layout()
    for ext in ('png', 'pdf'):
        fig.savefig(filename.with_suffix('.' + ext), bbox_inches='tight')
    plt.close(fig)


def main():
    (OUT / 'figures').mkdir(parents=True, exist_ok=True)
    pub = pd.read_csv(ROOT / 'data/original_results/published_values.csv', dtype={'value': str}).query("publication == 'ejrs2019'")
    pub = pub.set_index('quantity')
    rep, notes = {}, {}
    for dkey, day in DAYS.items():
        for u in (1, 2):
            w = wind(day, u)
            rep[f'wind_speed_mean_{dkey}_usa{u}'] = w['speed']
            rep[f'wind_direction_mean_{dkey}_usa{u}'] = w['direction']
            rep[f'circular_variance_{dkey}_usa{u}'] = w['S0']
    for k in [k for k in rep if k.startswith(('wind', 'circular'))]:
        notes[k] = 'entire recording of the day (as in visualize_anemometer_data.m)'
    v = gas_array('U2355A_PIR7000_Array_Messung6_201783_12051593.csv')
    ch = int(np.unravel_index(v.argmax(), v.shape)[1]) + 1
    rep['reference_array_max_concentration_day1_trial4'] = v.max()
    notes['reference_array_max_concentration_day1_trial4'] = (
        f'file U2355A_PIR7000_Array_Messung6_201783_12051593.csv (trial list: day 1 trial 4 = gas measurement 6), '
        f'channel {ch}, raw value x 10^4 without offset correction')
    per_channel = '; '.join(f'ch{k + 1} {v[:, k].mean():.0f}+/-{v[:, k].std(ddof=1):.0f}' for k in range(10))
    for k in ('reference_array_sensor1_mean_day1_trial4', 'reference_array_sensor1_sd_day1_trial4',
              'reference_array_sensor3_mean_day1_trial4', 'reference_array_sensor3_sd_day1_trial4'):
        rep[k] = np.nan
        notes[k] = ('not reproducible: averaging window, zero-offset correction and sensor-to-channel assignment are not '
                    f'documented; mean+/-SD over the whole file (ppm): {per_channel}')
    rows = []
    for q, val in rep.items():
        p = pub.loc[q]
        dec = len(p.value.split('.')[1]) if '.' in p.value else 0
        rr = round(val, dec) if not np.isnan(val) else np.nan
        rows.append({'quantity': q, 'unit': p.unit, 'published': float(p.value), 'reproduced': val,
                     'reproduced_rounded_as_published': rr,
                     'status': 'match' if rr == float(p.value) else ('NOT REPRODUCIBLE' if np.isnan(val) else 'DEVIATION'),
                     'note': notes.get(q, '')})
    cmp = pd.DataFrame(rows)
    cmp.to_csv(OUT / 'plume_comparison.csv', index=False, float_format='%.6g', lineterminator='\n')

    recs = []
    for flight in sorted(int(f.name.split('_')[0]) for f in (ROOT / 'data/original_results/ejrs2019/rays_matlab_2017').glob('*_out.CSV')):
        for lam in (1e-5, 0.1):
            r = reconstruct(flight, lam)
            i, j = np.unravel_index(np.argmax(r['mean']), r['mean'].shape)
            recs.append({'flight': flight, 'published_as': PUBLISHED_FLIGHTS.get(flight, ''), 'lambda': lam, 'n_rays': r['n_rays'],
                         'n_cells': r['mean'].size, 'max_concentration_ppm': r['mean'].max(),
                         'max_cell_y_centre_m': r['cx'][j] + CELL / 2, 'max_cell_z_centre_m': r['cy'][i] + CELL / 2,
                         'cells_above_1500ppm': int((r['mean'] > 1500).sum())})
            if lam == 1e-5 and flight in PUBLISHED_FLIGHTS:
                plot(r, flight, OUT / 'figures' / f'plume_flight{flight}_mean_variance')
    pd.DataFrame(recs).to_csv(OUT / 'plume_reconstructions.csv', index=False, float_format='%.6g', lineterminator='\n')
    print(f'EJRS 2019 plume: {len(cmp)} values, {int((cmp.status == "match").sum())} match, '
          f'{int((cmp.status == "DEVIATION").sum())} deviate, {int((cmp.status == "NOT REPRODUCIBLE").sum())} not reproducible; '
          f'{len(recs)} reconstructions')
    return cmp


if __name__ == '__main__':
    main()
