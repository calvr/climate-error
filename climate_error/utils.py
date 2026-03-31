#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix ts=8 et sw=4 sts=4 sta :
# -*- coding: utf-8 -*-

import logging
import numpy as np
import pandas as pd


_logger = logging.getLogger(__name__)


def get_concurrent_records(*args, to_list:bool=True):
    """
    Given multiple Pandas Series or DataFrames as *args, sharing a common index,
    return these but only with the concurrent records, i.e. the indices that are
    shared by all of the series objects and whose associated data is valid.
    """
    df = pd.concat(args, axis=1)
    df = df.dropna(axis=0, how='any')  # remove rows that contain NaNs
    if to_list:
        return tuple(df.iloc[:,i] for i in range(len(df.columns)))
    return df


def estimate_bins(wso, wsp=None, minbinw=.5):
    """
    Estimate bins suitable to compute histograms given a sample of wind-speed
    data values.
    """
    bin_edges = np.histogram_bin_edges(wso, bins='auto')
    #nbins = bin_edges.size - 1
    binw = pd.Series(np.round(np.diff(bin_edges), 8)).mode()[0]
    binw = minbinw if binw <= minbinw else 1
    wsp = wso if None is wsp else wsp
    wsmax = int(np.ceil(max(wsp.max(), wso.max())))
    bins = np.arange(0, wsmax + binw, binw)
    return bins, bin_edges

