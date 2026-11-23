#!/usr/bin/env python3
"""Numbers of Neumann et al., IEEE ISOEN 2022 (remote drone-to-drone gas sensing, 2020-07-14, flight 7).

Input : data/raw/copter/2020-07-14/7/tdlas.tsv.gz                 TDLAS records of the measuring drone (DJI S1000+)
        data/raw/anemometer/2020-07-14/0/anemometer{0,1}.tsv.gz    ultrasonic anemometers (10 Hz)
Output: results/isoen2022/comparison.csv

The evaluation window is taken from the original workbook data/original_results/isoen2022/evaluation.xlsx:
rows 207 ('copter reaches WP') to 1448 (last row before 'copter landing'), i.e. 1242 TDLAS records.
Workbook row r holds TDLAS record r-1 (0-based); the first record of the window is therefore record 206.
Wind statistics as in visualize_anemometer_data.m (CircStat): direction atan2(v_x, v_y), circular mean and circular
variance weighted with the squared 3D wind speed, arithmetic mean of the 3D wind speed.
"""
import gzip
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'results' / 'isoen2022'
FIRST_RECORD, N_RECORDS = 206, 1242
MIN_INTENSITY = 10  # %, workbook formula IF(AND(error code = 1, intensity > 9), ...)


def load_tdlas():
    with gzip.open(ROOT / 'data/raw/copter/2020-07-14/7/tdlas.tsv.gz', 'rt') as fh:
        return pd.read_table(fh, names=['t_us', 'error_code', 'concentration_ppmm', 'intensity_pct'])


def wind_stats(df):
    vx, vy, vz = df.v_x / 100, df.v_y / 100, df.v_z / 100        # cm/s -> m/s
    speed = np.sqrt(vx ** 2 + vy ** 2 + vz ** 2)
    direction = np.mod(np.degrees(np.arctan2(vx, vy)), 360)
    w = speed ** 2
    s = np.sum(w * np.exp(1j * np.radians(direction)))
    return {'direction_deg': float(np.mod(np.degrees(np.angle(s)), 360)),
            'circular_variance': float(1 - abs(s) / w.sum()), 'speed_mps': float(speed.mean())}


def load_anemometer(i):
    cols = ['t', 'heater', 'v_x', 'v_y', 'v_z', 'temp', 'v_vavg', 'v_savg', 'd', 'dh', 'q']
    with gzip.open(ROOT / f'data/raw/anemometer/2020-07-14/0/anemometer{i}.tsv.gz', 'rt') as fh:
        df = pd.read_table(fh, header=None, usecols=range(11), names=cols)
    df['t'] = pd.to_datetime(df.t)
    return df


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t = load_tdlas()
    w = t.iloc[FIRST_RECORD:FIRST_RECORD + N_RECORDS]
    valid = w[w.error_code == 1]
    strong = valid[valid.intensity_pct >= MIN_INTENSITY]
    peak = strong.loc[strong.concentration_ppmm.idxmax()]
    ok = ((w.error_code == 1) & (w.intensity_pct >= MIN_INTENSITY)).to_numpy()
    tt = w.t_us.to_numpy() / 1e6
    longest, start = 0.0, None
    for k, flag in enumerate(ok):                # longest run of consecutive successful (>= 10 %) records
        if flag and start is None:
            start = k
        if start is not None and (not flag or k == len(ok) - 1):
            end = k if flag else k - 1
            longest = max(longest, tt[end] - tt[start])
            start = None
    t0, t1 = pd.to_datetime(w.t_us.iloc[0], unit='us', utc=True), pd.to_datetime(w.t_us.iloc[-1], unit='us', utc=True)

    rep = {'tdlas_measurements_total': len(w), 'tdlas_measurements_successful': len(valid),
           'tdlas_successful_share': 100 * len(valid) / len(w), 'tdlas_intensity_ge10_count': len(strong),
           'tdlas_intensity_ge10_share_of_successful': 100 * len(strong) / len(valid),
           'max_concentration_intensity_ge10': peak.concentration_ppmm, 'intensity_at_max_concentration': peak.intensity_pct,
           'longest_consecutive_period': longest}
    notes = {'longest_consecutive_period': 'duration from first to last of consecutive records with error code 1 and intensity >= 10 %'}
    wind_full, wind_win = [], []
    for i in (0, 1):
        a = load_anemometer(i)
        wind_full.append(wind_stats(a))
        wind_win.append(wind_stats(a[(a.t >= t0) & (a.t <= t1)]))
    rep['wind_speed_mean'] = np.mean([x['speed_mps'] for x in wind_full])
    rep['wind_direction_mean_min'] = wind_full[0]['direction_deg']
    rep['wind_direction_mean_max'] = wind_full[1]['direction_deg']
    rep['circular_variance'] = np.mean([x['circular_variance'] for x in wind_full])
    whole = (f'entire anemometer recording ({a.t.min():%H:%M}-{a.t.max():%H:%M} UTC); anemometer 0: '
             f"{wind_full[0]['direction_deg']:.1f} deg, S0 {wind_full[0]['circular_variance']:.3f}, {wind_full[0]['speed_mps']:.2f} m/s; "
             f"anemometer 1: {wind_full[1]['direction_deg']:.1f} deg, S0 {wind_full[1]['circular_variance']:.3f}, {wind_full[1]['speed_mps']:.2f} m/s. "
             f'During the experiment window ({t0:%H:%M:%S}-{t1:%H:%M:%S} UTC): '
             f"{wind_win[0]['direction_deg']:.1f} / {wind_win[1]['direction_deg']:.1f} deg, S0 {wind_win[0]['circular_variance']:.3f} / "
             f"{wind_win[1]['circular_variance']:.3f}, {wind_win[0]['speed_mps']:.2f} / {wind_win[1]['speed_mps']:.2f} m/s")
    for k in ('wind_speed_mean', 'wind_direction_mean_min', 'wind_direction_mean_max', 'circular_variance'):
        notes[k] = whole

    pub = pd.read_csv(ROOT / 'data/original_results/published_values.csv', dtype={'value': str}).query("publication == 'isoen2022'")
    rows = []
    for p in pub.itertuples():
        q = rep[p.quantity]
        dec = len(p.value.split('.')[1]) if '.' in p.value else 0   # decimals as printed in the paper
        rows.append({'quantity': p.quantity, 'unit': p.unit, 'published': float(p.value), 'reproduced': q,
                     'reproduced_rounded_as_published': round(q, dec), 'note': notes.get(p.quantity, '')})
    cmp = pd.DataFrame(rows)
    cmp['status'] = np.where(cmp.reproduced_rounded_as_published == cmp.published, 'match', 'DEVIATION')
    cmp.to_csv(OUT / 'comparison.csv', index=False, float_format='%.6g', lineterminator='\n')
    print(f'ISOEN 2022: {len(cmp)} values, {int((cmp.status == "match").sum())} match, '
          f'{int((cmp.status != "match").sum())} deviate ({", ".join(cmp.loc[cmp.status != "match", "quantity"])})')
    return cmp


if __name__ == '__main__':
    main()
