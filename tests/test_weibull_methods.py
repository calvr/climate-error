#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix ts=8 et sw=4 sts=4 sta :
# -*- coding: utf-8 -*-

import pytest
import numpy as np
import pandas as pd
from scipy.special import gamma

from climate_error.weibull_methods import (
    weibull_cdf, weibull_ppf, weibull_pdf, weibull_moment, mle_weibull_fit,
    ewa_weibull_fit, ewa_weibull_fit_sample, ewa_weibull_fit_hist,
)


def test_weibull_moments():
    """
    Given multiple Weibull distributions, (A, K), and their respective
    probability of occurrence, P, compute the equivalent 1st, 2nd and 3rd
    statistical moments equivalent to the aggregation their random variables.
    """
    K = np.array([.5, 1., 2., 3., 5., 10.])
    A = np.array([1., 2., 5., 10., 15.])
    np.testing.assert_allclose(
        A[None,:] * gamma(1 + 1./K[:,None]),
        weibull_moment(A[None,:], K[:,None])
    )
    np.testing.assert_allclose(
        A[None,:]**2 * gamma(1 + 2./K[:,None]),
        weibull_moment(A[None,:], K[:,None], 2),
    )
    np.testing.assert_allclose(
        A[None,:]**3 * gamma(1 + 3./K[:,None]),
        weibull_moment(A[None,:], K[:,None], n=3),
    )


def test_weibull_cdf_ppf_pdf():
    """
    Given the values for the parameters of Weibull distributions,
    check if the CDF is consistend with the PPF and if differences
    between CDF values match the expected PDF.
    """
    for A in [1., 2., 5., 10., 15.]:
        for K in [.5, 1., 2., 3., 5., 10.]:
            u = (np.arange(10) + .5)/10
            x = weibull_ppf(u, A, K)
            np.testing.assert_allclose(
                u, weibull_cdf(x, A, K),
                atol=1e-5, rtol=1e-5,
                err_msg=f'FAILED FOR {A=} {K=}',
            )
            dx = 1e-5
            np.testing.assert_allclose(
                (weibull_cdf(x + dx, A, K) - weibull_cdf(x - dx, A, K)) / (2*dx),
                weibull_pdf(x, A, K),
                atol=1e-5, rtol=1e-5,
                err_msg=f'FAILED FOR {A=} {K=}',
            )


def test_weibull_fitting_methods():
    """
    Given a sample generated from a Weibull distribution with known parameters,
    check if the fitting methods return the same parameters when applied to
    the sample. Note that for the EWA method, there are known discrepancies
    due to the particular conditions which the method is based upon.
    """
    for A in [1., 2., 5., 10., 15.]:
        for K in [.5, 1., 2., 3., 5., 10.]:
            N = 5000
            p_bin_edges = np.linspace(0, 1, N + 1)  # exact
            p = .5*(p_bin_edges[1:] + p_bin_edges[:-1])  # mid point
            ws = weibull_ppf(p, A, K)  # generate X sample based on p-space
            ws = np.concatenate([ws, [np.nan]*10])
            np.random.shuffle(ws)
            Amle, Kmle = mle_weibull_fit(ws)
            np.testing.assert_allclose(
                [Amle, Kmle], [A, K], rtol=1e-3, err_msg=f'MLE FAILED FOR {A=} {K=}',
            )
            Amle_df, Kmle_df = mle_weibull_fit(pd.DataFrame(ws))
            np.testing.assert_allclose(
                [Amle, Kmle], [Amle_df, Kmle_df],
                err_msg=f'MLE FAILED FOR DataFrame, {A=} {K=}',
            )
            Aewa, Kewa = ewa_weibull_fit_sample(ws)
            np.testing.assert_allclose(
                [Aewa, Kewa], [A, K], rtol=5e-2, err_msg=f'EWA FAILED FOR {A=} {K=}',
            )
            Aewa_df, Kewa_df = ewa_weibull_fit_sample(pd.DataFrame(ws))
            np.testing.assert_allclose(
                [Aewa, Kewa], [Aewa_df, Kewa_df],
                err_msg=f'EWA FAILED FOR DataFrame, {A=} {K=}',
            )


def test_weibull_ewa_failures():
    A, K = ewa_weibull_fit_sample(np.array([np.nan]*20))
    assert np.isnan(A) and np.isnan(K), f"Got {A=} {K=} for X without valid records?"
    A, K = ewa_weibull_fit_sample(np.array([8.]*20))
    assert np.isnan(A) and np.isnan(K), f"Got {A=} {K=} for X full of constant values?"
    with pytest.raises(Exception):
        A, K = ewa_weibull_fit(-8., 10**3, 0.5)
        #assert np.isnan(A) and np.isnan(K), f"Got {A=} {K=} for negative mean(X)?"
    with pytest.raises(Exception):
        A, K = ewa_weibull_fit(8., 5**3, 0.5)
        #assert np.isnan(A) and np.isnan(K), f"Got {A=} {K=} for mean(X)**3 > mean(X**3)?"
    with pytest.raises(Exception):
        A, K = ewa_weibull_fit(8., 10**3, -0.5)
        #assert np.isnan(A) and np.isnan(K), f"Got {A=} {K=} for negative P(X>xmu)?"
    with pytest.raises(Exception):
        A, K = ewa_weibull_fit(8., 10**3, 50.)
        #assert np.isnan(A) and np.isnan(K), f"Got {A=} {K=} for P(X>xmu) > 1?"


def test_weibull_mle_failures():
    A, K = mle_weibull_fit(np.array([np.nan]*20))
    assert np.isnan(A) and np.isnan(K), f"Got {A=} {K=} for X without valid records?"
    A, K = mle_weibull_fit(np.array([8.]*20))
    assert np.isnan(A) and np.isnan(K), f"Got {A=} {K=} for X full of constant values?"


def test_weibull_hist_fit():
    """
    Given a sample generated from a Weibull distribution with known parameters,
    check if the histogram based fitting method returns similar parameters.
    """
    for A in [1., 2., 5., 10., 15.]:
        for K in [1., 2., 3., 5.]:
            max_bin_edge = np.ceil(weibull_ppf(.999, A, K)) + 5
            ws_bin_edges = np.linspace(0, max_bin_edge, 51)
            f_bin_edges = weibull_cdf(ws_bin_edges, A, K)
            ws_bins = .5*(ws_bin_edges[1:] + ws_bin_edges[:-1])
            f_bins = f_bin_edges[1:] - f_bin_edges[:-1]
            Aewa, Kewa = ewa_weibull_fit_hist(ws_bins, f_bins)
            np.testing.assert_allclose(
                [Aewa, Kewa], [A, K], atol=1e-1, rtol=1e-1, err_msg=f'EWA FAILED FOR {A=} {K=}',
            )


def test_weibull_ewa_hist_failures():
    x = np.arange(1, 11)
    p = weibull_cdf(x+1, 5, 2) - weibull_cdf(x-1, 5, 2)
    A, K = ewa_weibull_fit_hist(x, x*np.nan)
    assert np.isnan(A) and np.isnan(K), f"Got {A=} {K=} for X|F bins without valid records?"
    A, K = ewa_weibull_fit_hist([np.nan] + list(x), [0] + list(p))
    assert np.isnan(A) and np.isnan(K), f"Got {A=} {K=} for X | F bins with NaN?"
    A, K = ewa_weibull_fit_hist(-x, p)
    assert np.isnan(A) and np.isnan(K), f"Got {A=} {K=} with negative X bins?"
    A, K = ewa_weibull_fit_hist(x, -p)
    assert np.isnan(A) and np.isnan(K), f"Got {A=} {K=} with negative F bins?"

