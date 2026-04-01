#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix ts=8 et sw=4 sts=4 sta :
# -*- coding: utf-8 -*-

import pytest
import numpy as np
import pandas as pd

from climate_error.utils import get_concurrent_records, estimate_bins


def test_get_concurrent_records_series():
    t = pd.date_range("2020-01-01", periods=10)
    s1 = pd.Series([0, 1, 2, 3, np.nan, 5, np.nan, 7, 8, 9], index=t, name='a')
    s2 = pd.Series([10, 30, 40, np.nan, np.nan, 70], index=t[[1,3,4,5,6,7]], name='b')
    r1, r2 = get_concurrent_records(s1, s2)
    assert isinstance(r1, pd.Series)
    assert isinstance(r2, pd.Series)
    assert r1.index.equals(r2.index)
    assert r1.index.isin(t).all()
    pd.testing.assert_series_equal(s1.loc[r1.index], r1)
    pd.testing.assert_series_equal(s2.loc[r1.index], r2)
    #
    r = get_concurrent_records(s1, s2, to_list=False)
    assert isinstance(r, pd.DataFrame)
    assert r.index.equals(r1.index)
    pd.testing.assert_series_equal(r['a'], r1)
    pd.testing.assert_series_equal(r['b'], r2)


def test_estimate_bins():
    wso = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    bins, edges = estimate_bins(wso)
    assert isinstance(bins, np.ndarray)
    assert isinstance(edges, np.ndarray)
    assert bins.ndim == 1
    assert edges.ndim == 1
    #
    wso = np.linspace(0, 10, 1000)
    bins, _ = estimate_bins(wso, minbinw=1.0)
    bin_widths = np.unique(np.diff(bins))
    assert np.all(bin_widths >= 1.0)
    #
    wso = np.array([2.1, 5.3, 7.9])
    bins, _ = estimate_bins(wso)
    assert bins[-1] >= np.ceil(wso.max())
    #
    wso = np.array([1.0, 2.0, 3.0])
    wsp = np.array([10.0])
    bins, _ = estimate_bins(wso, wsp=wsp)
    assert bins[-1] >= 10.0

