#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix ts=8 et sw=4 sts=4 sta :
# -*- coding: utf-8 -*-
"""
Create a filtered CSV subset from the "Capel Cynon" data in the NetCDF that is
available from DTU via DOI: https://doi.org/10.11583/DTU.14135627
License: CC BY 4.0 (verify on dataset landing page when downloading).
         URL: https://creativecommons.org/licenses/by/4.0/

Usage:
    1. Download file 'capel_all.nc' from the URL page referenced by the given DOI.
    2. Run this script to write the relevant data to a CSV file.
"""

import xarray as xr
import pandas as pd

url = "https://doi.org/10.11583/DTU.14135627"
ncfn = "capel_all.nc"
ocsv = "wind_data_capel_m1_50m.csv.gz"

if not os.path.isfile(ncfn):
    raise FileNotFoundError(f"'{ncfn}' not found... please download it from '{url}'")

ds = xr.open_dataset(ncfn)
signals, quality = ['ws50_m1', 'wd40_m1'], ['ws50_m1_qc', 'wd40_m1_qc']  # signals to process
df = ds[[*signals, *quality]].to_dataframe()
df = df.mask(df[quality].max(axis=1) > 1).dropna(axis=0).drop(columns=quality)  # drop rows that fail quality check
wsmu = list(df.columns[df.columns.str.fullmatch(r'ws.*', case=False)])  # wind speed magnitude
wsti = list(df.columns[df.columns.str.fullmatch(r'ti.*', case=False)])  # turbulence intensity
wdmu = list(df.columns[df.columns.str.fullmatch(r'wd.*', case=False)])  # wind direction azimuth
b = (
      ((df[wsmu] <= 0) | (df[wsmu] >= 99)).any(axis=1)
    | ((df[wdmu] < 0) | (df[wdmu] >= 360)).any(axis=1)
    | (df[wsti] <= 0).any(axis=1)
)
print(f"availability {(1-b.sum()/b.size)*100:.0f}%")
df = df.mask(b).dropna(axis=0)
print(f"years of records: {df.index.size/(6*24*365.25):.2f} yr")
df.to_csv(
    ocsv,
    mode='w',
    sep=',',
    na_rep='',
    lineterminator='\n',
    index=True,
    header=True,
    compression='gzip',
)

