#!/usr/bin/env python3
"""Table 1 of Neumann et al., European Journal of Remote Sensing 2019 (earth-wall experiments, 2016-07-07).

Input : data/raw/cofi-abv/2016-07-07_earth-wall/111649.CSV.gz   (logger file of the UAV payload)
        data/metadata/cofi-abv/2016-07-07_earth-wall_selection.csv    (ID range of every trial, from comp_surface.xlsx)
        data/metadata/cofi-abv/2016-07-07_earth-wall_excluded_ids.csv (values removed in comp_surface.xlsx)
Output: results/ejrs2019/table1_reproduced.csv, results/ejrs2019/table1_comparison.csv

Two variants are computed:
  'published'  : the data selection of the original evaluation workbook comp_surface.xlsx (ID ranges and manually
                 removed values) and its confidence interval 1.96 * SD / sqrt(n_ci), with n_ci = 201 except for the two
                 cells where the workbook uses the reduced number of values (vegetation, 20 m, trials 1 and 2)
  'error_codes': all measurements with an error code other than 1 removed (gas: LMm-G, distance: LDS30-M),
                 confidence interval 1.96 * SD / sqrt(n) with the actual number n of remaining values
"""
import gzip
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'results' / 'ejrs2019'
COLS = {'distance': 'dist[m]', 'concentration': 'conc[ppm x m]', 'intensity': 'int[%]'}
DECIMALS = {'distance_mean_m': 2, 'concentration_mean_ppmm': 1, 'intensity_mean_pct': 1}


def load_raw():
    with gzip.open(ROOT / 'data/raw/cofi-abv/2016-07-07_earth-wall/111649.CSV.gz', 'rt', encoding='latin-1') as fh:
        raw = pd.read_csv(fh, sep=';', index_col=False, decimal=',')
    raw.columns = [c.strip() for c in raw.columns]
    return raw.set_index('id', drop=False)


def stats(values, n_ci):
    values = np.asarray(values, float)
    return values.mean(), 1.96 * values.std(ddof=1) / np.sqrt(n_ci)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    raw = load_raw()
    sel = pd.read_csv(ROOT / 'data/metadata/cofi-abv/2016-07-07_earth-wall_selection.csv')
    exc = pd.read_csv(ROOT / 'data/metadata/cofi-abv/2016-07-07_earth-wall_excluded_ids.csv')
    removed = {q: set(exc.loc[exc.quantity == q, 'id']) for q in ('gas', 'distance')}
    rows = []
    for s in sel.itertuples():
        block = raw.loc[s.id_first:s.id_last]
        assert len(block) == s.id_last - s.id_first + 1
        for variant in ('published', 'error_codes'):
            if variant == 'published':
                # as in comp_surface.xlsx: removed values only in the concentration and distance columns,
                # the intensity column was left complete; n of the CI formula as written in the workbook
                gas = block[~block.id.isin(removed['gas'])]
                dist = block[~block.id.isin(removed['distance'])]
                inten = block
                n_c, n_i, n_d = s.n_ci_concentration, s.n_ci_intensity, s.n_ci_distance
            else:
                gas = block[block['err_code[LMm-G]'] == 1]
                dist = block[block['err_code[LDS30-M]'] == 1]
                inten = gas
                n_c = n_i = len(gas)
                n_d = len(dist)
            dm, dc = stats(dist[COLS['distance']], n_d)
            cm, cc = stats(gas[COLS['concentration']], n_c)
            im, ic = stats(inten[COLS['intensity']], n_i)
            rows.append({'variant': variant, 'surface': s.surface, 'distance_m': s.distance_m, 'trial': s.trial,
                         'distance_mean_m': dm, 'distance_ci95_m': dc,
                         'concentration_mean_ppmm': cm, 'concentration_ci95_ppmm': cc,
                         'intensity_mean_pct': im, 'intensity_ci95_pct': ic,
                         'n_gas_values': len(gas), 'n_distance_values': len(dist), 'n_block': len(block),
                         'gas_invalid_share_pct': 100 * (block['err_code[LMm-G]'] != 1).mean(),
                         'distance_invalid_share_pct': 100 * (block['err_code[LDS30-M]'] != 1).mean()})
    table = pd.DataFrame(rows)
    table.to_csv(OUT / 'table1_reproduced.csv', index=False, float_format='%.6g', lineterminator='\n')

    # published Table 1 (as printed) and the values of the original workbook comp_surface.xlsx (cached cell values)
    pub = pd.read_csv(ROOT / 'data/original_results/ejrs2019/table1_published.csv', dtype=str)
    xls = pd.read_csv(ROOT / 'data/original_results/ejrs2019/table1_excel_values.csv')
    keys = ['surface', 'distance_m', 'trial']
    pub[['distance_m', 'trial']] = pub[['distance_m', 'trial']].astype(int)
    rep = table[table.variant == 'published'].merge(pub, on=keys, suffixes=('', '_pub')).merge(xls, on=keys, suffixes=('', '_xls'))
    cmp = []
    for r in rep.itertuples():
        for col in ['distance_mean_m', 'distance_ci95_m', 'concentration_mean_ppmm', 'concentration_ci95_ppmm',
                    'intensity_mean_pct', 'intensity_ci95_pct']:
            p_str = getattr(r, col + '_pub')
            p, q, x = float(p_str), getattr(r, col), getattr(r, col + '_xls')
            dec = len(p_str.split('.')[1]) if '.' in p_str else 0   # decimals as printed in Table 1
            unit = 10.0 ** -dec
            d = round(q, dec) - p
            status = 'match' if abs(d) < unit / 2 else ('last-digit' if abs(d) <= unit * 1.0001 else 'DEVIATION')
            cmp.append({'surface': r.surface, 'distance_m': r.distance_m, 'trial': r.trial, 'quantity': col,
                        'published': p, 'workbook': x, 'reproduced': q, 'difference_to_published': q - p,
                        'difference_to_workbook': q - x, 'status': status})
    cmp = pd.DataFrame(cmp)
    cmp.to_csv(OUT / 'table1_comparison.csv', index=False, float_format='%.6g', lineterminator='\n')
    print(f'EJRS 2019 Table 1: {len(cmp)} values, {int((cmp.status == "match").sum())} match, '
          f'{int((cmp.status == "last-digit").sum())} last digit, {int((cmp.status == "DEVIATION").sum())} deviate; '
          f'max. |reproduced - workbook| = {cmp.difference_to_workbook.abs().max():.2g}')
    return cmp


if __name__ == '__main__':
    main()
