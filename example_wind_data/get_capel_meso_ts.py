#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix ts=8 et sw=4 sts=4 sta :
# -*- coding: utf-8 -*-

"""
Download a NEWA mesoscale time series (single grid point) and save as NetCDF.
About/Terms (incl. license & attribution string): https://map.neweuropeanwindatlas.eu/about
License: CC BY 4.0 (verify on dataset landing page when downloading).
         URL: https://creativecommons.org/licenses/by/4.0/

API root (public docs landing): https://map.neweuropeanwindatlas.eu/api/
Coverage (meso): 1989-01-01 to 2018-12-31 (per NEWA About).

Usage:
    1. Simply run `python get_capel_meso_ts.py`

"""

import os
import logging
import requests
import email
import xarray as xr

apiurl = "https://wps.neweuropeanwindatlas.eu/api"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3 Edg/16.16299"  

def get_newa_timeseries(
    lon, lat,
    endpoint="mesoscale-ts/v1/get-data-point",
    heights=[50, 75, 100, 150, 200, 250, 500],
    variables=[
        "HGT", "WS10", "WD10", "T2", "Q2", "RHO", "PSFC",
        "ZNT", "UST", "RMOL", "PBLH",
        "WS", "WD", "TKE", "T", "QVAPOR", 
    ],
    start="1989-01-01T00:00:00",
    stop="2022-12-31T23:30:00",
    output_fn=None,
):
    logger = logging.getLogger()
    response = requests.get(
        f"{apiurl}/{endpoint}",
        headers={
            "User-Agent": user_agent,
        },
        params={
            "longitude": lon,
            "latitude": lat,
            "dt_start": start,
            "dt_stop": stop,
            "height": heights,
            "variable": variables,
        },
        stream=True,
    )
    try:
        response.raise_for_status()
    except Exception as ex:
        logger.error(f"str(ex)... request URL was {response.url}")
        raise
    content_type = response.headers.get('Content-Type', None)
    if 200 != response.status_code:
        logger.warning(f"Status Code was {response.status_code}...")
    if 'json' in content_type.lower():
        return response.json()
    if 'netcdf' in content_type.lower():
        if None is output_fn:
            msg = email.message.Message()
            #msg['Content-Disposition'] = response.headers.get('Content-Disposition', None)
            msg.add_header('Content-Disposition', response.headers.get('Content-Disposition', None))
            output_fn = msg.get_filename()
        with open(output_fn, mode='wb') as fid:
            for chunk in response.iter_content(chunk_size=8192):
                _ = fid.write(chunk)
        logger.warning(f"... downloaded NetCDF to {output_fn}")
        return xr.open_dataset(output_fn)
    if 'text/' in content_type.lower():
        try:
            data = response.content.decode('utf-8')
        except:
            data = response.text
        return data
    logger.warning(f"Unknown Content-Type: {content_type}")
    return response


if __name__ == '__main__':
    ds = get_newa_timeseries(
        lon = -4.354217,
        lat = 52.138872,
        heights = [50, 100],
        start = "1990-01-01T00:00:00",
        stop = "1996-01-01T00:00:00",
        variables=[
            "HGT", "WS10", "WD10", "T2", "Q2", "RHO", "PSFC",
            "ZNT", "UST", "RMOL", "PBLH",
            "WS", "WD", "TKE", "T", "QVAPOR",
        ],
        output_fn = 'newa_mesots_capel_cynon.nc',
    )
    ds.compute()
    ds.close()
    print(ds)
    print(sorted(list(ds.attrs)))

