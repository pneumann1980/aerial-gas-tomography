#!/usr/bin/env python3
"""Experiment #3 of European Journal of Remote Sensing 2019 (aiming at a CH4-filled glass cube, 2016-07-20, Fig. 9c):
share of time with a detection (> 200 ppm*m) between 25 s and 351 s.

Input : data/raw/cofi-abv/2016-07-20_scanning-aiming/095915.CSV.gz (from id 2983) and 101021.CSV.gz (whole file; the
        payload logger was reset in between, see data/metadata/cofi-abv/2016-07-20_scanning-aiming_description.txt)
Output: results/ejrs2019/aiming_comparison.csv, aiming_variants.csv

Selection as in the original workbook data/original_results/ejrs2019/glass_cube_aiming.xlsx: time from the logger
milliseconds, continued across the reset; evaluated rows 127-1729 of sheet Tabelle1 (t = 25.16-351.06 s, 1,603 samples);
column AY ("all detections", published) counts every sample with > 200 ppm*m regardless of the error code, column AW
("filtered") only those with error code 0 or 1.
"""
import gzip
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'data/raw/cofi-abv/2016-07-20_scanning-aiming'
OUT = ROOT / 'results/ejrs2019'
THRESHOLD = 200      # ppm*m
FIRST, LAST = 125, 1727      # 0-based sample indices = workbook rows 127 and 1729


def load(name):
    with gzip.open(RAW / f'{name}.gz', 'rt', encoding='latin-1') as fh:
        return pd.read_csv(fh, sep=';', decimal=',')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    a = load('095915.CSV')
    a = a[a.iloc[:, 0] >= 2983]
    b = load('101021.CSV')
    m0, m_last = a['millis[N/A]'].iloc[0], a['millis[N/A]'].iloc[-1]
    t = np.concatenate([a['millis[N/A]'] - m0, b['millis[N/A]'] + m_last - m0]) / 1000
    conc = np.concatenate([a['conc[ppm x m]'], b['conc[ppm x m]']])[FIRST:LAST + 1]
    err = np.concatenate([a['err_code[LMm-G]'], b['err_code[LMm-G]']])[FIRST:LAST + 1]
    det = conc > THRESHOLD
    variants = pd.DataFrame([
        {'variant': 'all error codes (published, workbook column AY)', 'detections': int(det.sum())},
        {'variant': 'error codes 0 and 1 (workbook column AW "filtered")', 'detections': int((det & np.isin(err, [0, 1])).sum())},
        {'variant': 'error code 1 only (valid measurements)', 'detections': int((det & (err == 1)).sum())}])
    variants['samples'] = len(conc)
    variants['share_pct'] = 100 * variants.detections / len(conc)
    codes = pd.Series(err[det]).value_counts().sort_index()
    variants['note'] = ''
    variants.loc[0, 'note'] = (f't = {t[FIRST]:.3f}-{t[LAST]:.3f} s; error codes of the detections: '
                               + ', '.join(f'{k}: {v}' for k, v in codes.items()))
    variants.to_csv(OUT / 'aiming_variants.csv', index=False, float_format='%.6g', lineterminator='\n')

    pub = pd.read_csv(ROOT / 'data/original_results/published_values.csv', dtype={'value': str})
    p = pub.set_index('quantity').loc['leakage_detection_time_share']
    val = variants.share_pct.iloc[0]
    rr = round(val, 1)
    cmp = pd.DataFrame([{'quantity': 'leakage_detection_time_share', 'unit': p.unit, 'published': float(p.value),
                         'reproduced': val, 'reproduced_rounded_as_published': rr,
                         'status': 'match' if rr == float(p.value) else 'DEVIATION',
                         'note': variants.note.iloc[0]}])
    cmp.to_csv(OUT / 'aiming_comparison.csv', index=False, float_format='%.6g', lineterminator='\n')
    print(f'EJRS 2019 aiming: detection share {val:.2f} % (published {p.value} %); '
          f'error codes 0/1: {variants.share_pct.iloc[1]:.1f} %, error code 1: {variants.share_pct.iloc[2]:.1f} %')
    return cmp


if __name__ == '__main__':
    main()
