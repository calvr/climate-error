#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix ts=8 et sw=4 sts=4 sta :
# -*- coding: utf-8 -*-

import pytest
import numpy as np
import pandas as pd

from climate_error.quantile_error_metrics import (
    weibull_moment,
    empiricalQ,
    empiricalCDF,
    numerical_wasserstein,
    error_metrics_wasserstein_weibull,
    error_metrics_wasserstein_2sample,
    error_metrics_wasserstein_weibull_vs_sample,
    error_metrics_timeseries,
    normalise_error_metrics,
)


def test_empirical_cdf_quantile_consistency():
    rng = np.random.default_rng(123)
    X = rng.normal(loc=5.0, scale=2.0, size=500)
    X[::50] = np.nan  # inject NaNs
    p = np.linspace(0.05, 0.95, 20)
    q = empiricalQ(p, X)
    # CDF(Q(p)) ≈ p
    p_back = empiricalCDF(q, X)
    assert q.shape == p.shape
    np.testing.assert_allclose(p_back, p, atol=0.05)
    # scalar version
    q0 = empiricalQ(0.5, X)
    p0 = empiricalCDF(q0, X)
    assert np.isclose(p0, 0.5, atol=0.05)


def test_numerical_wasserstein_zero_for_identical_samples():
    rng = np.random.default_rng(0)
    x = rng.weibull(2.0, size=1000)
    bias = numerical_wasserstein(x, x, m=1, N=500, absolute=False)
    w1 = numerical_wasserstein(x, x, m=1, N=500, absolute=True)
    w2 = numerical_wasserstein(x, x, m=2, N=500)
    assert np.isclose(bias, 0.0, atol=1e-6)
    assert np.isclose(w1, 0.0, atol=1e-6)
    assert np.isclose(w2, 0.0, atol=1e-6)


def test_weibull_vs_sample_error_metrics_reasonable():
    rng = np.random.default_rng(42)
    A, K = 8.0, 2.0
    # generate sample from "observed" Weibull
    u = rng.random(2000)
    o = A * (-np.log(1 - u)) ** (1 / K)
    BIAS_num, STDE_num, RMSE_num = error_metrics_wasserstein_weibull_vs_sample(A, K, o, N=3000)
    BIAS_an, STDE_an, RMSE_an = error_metrics_wasserstein_weibull(A, K, A, K)
    # analytical: same distribution => zero
    assert np.isclose(BIAS_an, 0.0, atol=1e-12)
    assert np.isclose(STDE_an, 0.0, atol=1e-12)
    assert np.isclose(RMSE_an, 0.0, atol=1e-12)
    # numerical vs sample: should be close to zero
    assert np.isclose(abs(BIAS_num), abs(weibull_moment(A, K) - np.nanmean(o)), atol=1e-1)
    assert STDE_num <= RMSE_num
    BIASn, STDEn, RMSEn = normalise_error_metrics(BIAS_num, STDE_num, RMSE_num, weibull_moment(A, K), pct=False)
    assert STDEn <= RMSEn
    assert RMSEn < 0.05


def test_timeseries_and_wasserstein_agree_on_bias_sign():
    rng = np.random.default_rng(1)
    o = rng.normal(10.0, 2.0, size=1000)
    p = o + 1.5  # known positive bias
    B_ts, S_ts, R_ts = error_metrics_timeseries(p, o)
    B_w, S_w, R_w = error_metrics_wasserstein_2sample(p, o)
    assert B_ts > 0
    assert B_w > 0
    assert R_ts >= abs(B_ts)
    assert R_w >= abs(B_w)


def test_normalise_error_metrics_scaling():
    BIAS, STDE, RMSE = 2.0, 3.0, 4.0
    ref = 10.0
    Bn, Sn, Rn = normalise_error_metrics(BIAS, STDE, RMSE, ref, pct=False)
    assert np.isclose(Bn, 0.2)
    assert np.isclose(Sn, 0.3)
    assert np.isclose(Rn, 0.4)
    Bp, Sp, Rp = normalise_error_metrics(BIAS, STDE, RMSE, ref, pct=True)
    assert np.isclose(Bp, 20.0)
    assert np.isclose(Sp, 30.0)
    assert np.isclose(Rp, 40.0)

