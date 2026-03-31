#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix ts=8 et sw=4 sts=4 sta :
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path


def get_paths():
    try:
        REPO_DIR = Path(__file__).resolve().parent
    except Exception:
        REPO_DIR = Path().resolve().parent
    #
    print(f"{REPO_DIR=}")
    DATA_DIR = REPO_DIR.parent / "example_wind_data"
    if not (DATA_DIR.exists() and DATA_DIR.is_dir()):
        DATA_DIR = REPO_DIR / "example_wind_data"
    assert (DATA_DIR.exists() and DATA_DIR.is_dir()), (
        "Cannot find DATA_DIR?"
        + f" Check if {REPO_DIR=} and {DATA_DIR=} are correct..."
    )
    print(f"{DATA_DIR=}")
    #
    EXAMPLES_DIR = DATA_DIR.parent / "examples"
    assert (EXAMPLES_DIR.exists() and EXAMPLES_DIR.is_dir()), (
        "Cannot find EXAMPLES_DIR?"
        + f" Check if {REPO_DIR=}, {DATA_DIR=} and {EXAMPLES_DIR=} are correct..."
    )
    return DATA_DIR, EXAMPLES_DIR


def custom_mpl_style(**kwargs):
    params = {
        "text.usetex": False,
        ## STIX fonts
        # "font.family": "STIXGeneral",
        # "mathtext.fontset": "stix",
        # "mathtext.fallback": "stix",
        ## Computer Modern Typewriter fonts
        "font.family": "cmtt10",
        "font.monospace": "cmtt10",
        "mathtext.fontset": "custom",
        "mathtext.fallback": "cm",
        "mathtext.rm": "cmtt10",
        "mathtext.sf": "cmtt10",
        "mathtext.tt": "cmtt10",
        "mathtext.it": "cmtt10:italic",
        "mathtext.bf": "cmtt10:bold",
        "mathtext.bfit": "cmtt10:italic:bold",
        "mathtext.cal": "cmtt10",
        ## Other
        "axes.titlesize": "x-large",
        "axes.labelsize": "x-large",
        "legend.fontsize": "large",
        "xtick.labelsize": "small",
        "ytick.labelsize": "small",
        "figure.figsize": (6.4, 4.0),
    }
    params.update(kwargs)
    mpl.rcParams.update(params)


def fill_time_gaps(df, verbose=False):
    difft = pd.Series(df.index, dtype=df.index.dtype).diff().dropna()
    dt = difft.mode()[0]
    print(f"Sampling interval determined from TimeStamps as {dt.total_seconds() / 60} min")
    if 1 == difft.unique().size:
        return df
    if verbose:
        print(
            "TimeStamps in Mast CSV have gaps...\n"
            + "Found following gaps: "
            + str([pd.Timedelta(d) for d in difft.unique() if pd.Timedelta(d) != dt])
            + "\nAdding TimeStamps to remove gaps in DataFrame"
        )
    return df.resample(dt).asfreq()


def apply_random_lags(ds:pd.Series, max_lag='6h'):
    dt = pd.Series(ds.index, dtype=ds.index.dtype).diff().dropna().mode()[0]
    max_lag = int(np.ceil(pd.Timedelta(max_lag)/dt))
    j = np.arange(ds.index.size) + np.random.randint(-max_lag, max_lag + 1, ds.index.size)
    j = np.minimum(np.maximum(j, 0), ds.index.size - 1)
    return pd.Series(ds.values[j], index=ds.index, name=ds.name)


def apply_coherent_lags(ds:pd.Series, max_lag='6h', dropna=True):
    x = fill_time_gaps(ds)
    #max_lag = 6*6  # 6 hours = 36 10min records
    dt = pd.Series(x.index, dtype=x.index.dtype).diff().dropna().mode()[0]
    rows_per_day = int(np.ceil(pd.Timedelta('24h')/dt))
    max_lag = int(np.ceil(pd.Timedelta(max_lag)/dt))
    boundary_rows = max(rows_per_day, 2*max_lag)
    #nblocks = int((x.index.size - 2*boundary_rows)/ max_lag)
    y = np.zeros_like(x)
    i = boundary_rows
    y[:i] = x.iloc[:i].values
    while i < (x.index.size - boundary_rows):
        ii = np.arange(max_lag) + i
        # Apply a random shift within a range (e.g., -6 to +6 hours)
        lag = np.random.randint(-max_lag, max_lag + 1)
        #if x.iloc[ii + lag].isna().any():
        #    print(i)
        #    break
        #y[ii] = x.iloc[ii + lag].values
        y[ii] = x.iloc[ii + lag].mask(x.iloc[ii + lag].isna().values, x.iloc[ii].values).values
        i += max_lag
    y[i:] = x.iloc[i:].values
    y = pd.Series(y, index=x.index, name=x.name)
    y.loc[x.isna()] = np.nan
    return y.dropna() if dropna else y


def darken_color(hex_color, factor=0.7):
    rgb = mcolors.hex2color(hex_color)
    dark_rgb = tuple([max(0, min(1, c * factor)) for c in rgb])
    return mcolors.rgb2hex(dark_rgb)


def plot_timeseries_w_hist(
    x=None, y=None, bins=None, show=True, fig=None,
    color='teal', ls='-', lw=.5, marker='None', label=None,
    histtype='stepfilled', alpha=.5, density=True,
):
    x = x if None is not x else np.linspace(0, 1*2*np.pi, 151)
    y = y if None is not y else np.sin(x) #+ np.random.normal(0, 0.1, x.size)
    if fig is None:
        fig = plt.figure()
        gs = mpl.gridspec.GridSpec(1, 2, width_ratios=[4, 1], wspace=None)
        ax_main = fig.add_subplot(gs[0])
        ax_hist = fig.add_subplot(gs[1], sharey=ax_main)  # hist on right y-axis line
    else:
        ax_main, ax_hist = fig.axes[0], fig.axes[1]
    #ax_main.set_xlabel('Time')
    #ax_main.set_ylabel('Signal')
    ax_main.plot(x, y, c=color, ls=ls, lw=lw, marker=marker, label=label)
    if None is bins:
        bin_edges = np.histogram_bin_edges(y.dropna(), bins='auto')
        bins = bin_edges.size - 1
    ax_hist.hist(y.dropna(), bins=bins,
        align='mid',
        density=density,
        orientation='horizontal',
        histtype=histtype,
        alpha=alpha,
        color=color,
    )
    plt.setp(ax_hist.get_yticklabels(), visible=False)  # hide y-axis label
    stats_text = (  
        rf"$\mu_x = {np.mean(y):.2f}$"
        rf"   $\sigma_x = {np.std(y, ddof=0):.2f}$"
        rf"   $\overline{{x^2}} = {np.mean(y**2):.2f}$"
    )
    ax_hist.text(1.03 + .16*len(ax_hist.texts), .5, stats_text, transform=ax_hist.transAxes,
        va='center', rotation=90, ha='left', fontsize='medium',
        color=color, fontweight='bold',
        bbox=dict(facecolor='white', alpha=0),
    )
    plt.tight_layout()
    if not show:
        return fig
    plt.show()

