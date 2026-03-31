#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix ts=8 et sw=4 sts=4 sta :
# -*- coding: utf-8 -*-

# ruff: noqa: E731

import logging
import numpy as np
from typing import Iterable

from .weibull_methods import weibull_ppf, weibull_moment


_logger = logging.getLogger(__name__)


## Methods to compute the Empirical Quantile Function and the Comulative Distribution Function

# empiricalQ = lambda p, X: np.where(
#     np.isnan(np.atleast_1d(p)), np.nan,
#     np.sort(X[~np.isnan(X)])[
#         #np.maximum(0, np.ceil(np.atleast_1d(p)*(sum(~np.isnan(X)) - 1)).astype(int))  # same as np.quantile(X, p, method='higher')
#         np.maximum(0, np.round(np.atleast_1d(p)*(sum(~np.isnan(X)) - 1)).astype(int))  # same as np.quantile(X, p, method='nearest')
#     ],
# )
# empiricalCDF = lambda x, X: (
#     np.nan if np.isnan(x) else .5*(  # compute midpoint
#         np.sum(np.sort(X[~np.isnan(X)]) <= x)  # same as np.searchsorted(X, x, side='right')
#       + np.sum(np.sort(X[~np.isnan(X)]) <  x)  # same as np.searchsorted(Xsorted, v, side='left')
#     )/np.sum(~np.isnan(X))
# )

## Equivalent functions based on numpy methods
def empiricalQ(p, X:Iterable, method='nearest'):
    r"""
    Quantile function for the empirical distribution that governs sample `X`.
    Given a probability `p`, return the value `x` matching the inverse CDF such
    that $p = P(X<=x) = F(x)$. Works for a single value of `p` or an array.
    Equivalent to np.sort(X)[np.round(p*(len(X) - 1)).astype(int)] if 'nearest'
    or to np.sort(X)[np.ceil(p*(len(X) - 1)).astype(int)] if 'higher'.
    """
    Xsorted = np.sort(np.atleast_1d(X)[~np.isnan(X)])
    U = np.atleast_1d(p)
    b = np.isnan(U) | (U > 1) | (U < 0)
    U[b] = 0
    out = np.quantile(Xsorted, U, method=method)
    out = np.where(b, np.nan, out)
    return out if np.ndim(p) else out.item()


def empiricalCDF(x, X:Iterable):
    """
    Cumulative distribution function for the empirical distribution that
    governs sample `X`. Given a value `x` return the probability `p` such
    that $p = P(X<=x)$. Works for a single value of `x` or an array.
    Equivalent to finding the bin midpoints:
        >>> .5*(sum(sort(X) <= x) + sum(sort(X) < x)) / len(X)
    """
    Xsorted = np.sort(np.atleast_1d(X)[~np.isnan(X)])
    Z = np.atleast_1d(x)
    out = .5 * (
          np.searchsorted(Xsorted, Z, side='left')
        + np.searchsorted(Xsorted, Z, side='right')
    ) / Xsorted.size
    out = np.where(np.isnan(Z), np.nan, out)
    return out if np.ndim(x) else out.item()


## Quantile metrics based on Wasserstein distances

def numerical_wasserstein(p, o, N=1000, m=1, absolute=False):
    r"""
    Given two quantile functions characterizing the statistical distributions
    for predictions and observations, `p` and `o`, compute the agreement between
    their quantiles as given by the `m`-degree Wasserstein metric. The agreement
    is computed via numerical integration with a trapezoid method, where the
    quantile functions are discretized in `N` steps.
    
    Albeit samples can be given for either `p` or `o` to represent the
    empirical distribution, a callable function describing an analytical quantile
    function may be given instead (i.e. to either `p` or `o`).

    NOTE: When numerical_wassertein is called with `m=1` and `absolute=False`,
    the value returned shall be representative of the BIAS between the
    distribution averages evaluated from the quantile functions, i.e.:
        $\tilde{W}_1 (P,O) = \int_0^1 (Q_p(u) - Q_o(u)) du$.
    This is an alternative formulation for a Wasserstein distance and different
    from the earth-mover's distance (a.k.a. area metric) defined as:
        $W_1 (P, O) = \int_0^1 |Q_p(u) - Q_o(u)| du$
    To compute the latter, call instead:
        >>> emd = numerical_wasserstein(..., m=1, absolute=True)
    """
    #Qo = lambda u: empiricalQ(u, np.sort(o[~np.isnan(o)]))
    #Qp = lambda u: empiricalQ(u, np.sort(p[~np.isnan(p)]))
    Qo = o if callable(o) else lambda u: empiricalQ(u, np.sort(o[~np.isnan(o)]))
    Qp = p if callable(p) else lambda u: empiricalQ(u, np.sort(p[~np.isnan(p)]))
    du = 1./(N-1)  # probability bin width
    u = np.arange(N) * du  # np.linspace(0, 1, N)  # probability array
    #u[0], u[-1] = 0 + 2*np.finfo(float).eps, 1 - 2*np.finfo(float).eps
    u[0], u[-1] = .01*du, 1 - .01*du  # avoid infinites
    absfun = (lambda x: np.abs(x)) if absolute else (lambda x: x)
    return np.power(
        .5*du*sum(
            absfun(Qp(u[1:]) - Qo(u[1:]))**m + absfun(Qp(u[:-1]) - Qo(u[:-1]))**m
        ),
        1/m,
    )


## Quantile error metrics

def error_metrics_wasserstein_weibull(Ap:float, Kp:float, Ao:float, Ko:float):
    """
    Compute the error metrics between two Weibull distributions describing
    predictions and observations, 'p' and 'o', given the respective parameters
    `Ap`, `Kp` and `Ao`, `Ko`. The error metrics are the analytical equivalents
    of the agreement between their quantile functions. The output metrics are
    the equivalent BIAS, STDE and RMSE.
    """
    BIAS = weibull_moment(Ap, Kp, 1) - weibull_moment(Ao, Ko, 1)
    RMSE = np.sqrt(
        weibull_moment(Ap, Kp, 2) + weibull_moment(Ao, Ko, 2)
        - 2 * weibull_moment(Ap*Ao, 1./(1./Kp + 1./Ko), 1)
    )
    RMSE = abs(BIAS) if np.isclose(RMSE**2, BIAS**2) else RMSE  # avoid sqrt(-|x|)
    STDE = np.sqrt(RMSE**2 - BIAS**2)
    return BIAS, STDE, RMSE


def error_metrics_wasserstein_2sample(p:Iterable, o:Iterable, N=3000):
    """
    Compute the error metrics between the empirical distributions governing
    two samples characterizing predictions and observations, 'p' and 'o'.
    The error metrics are the numerical agreement between the empirical
    quantile functions, equivalent to Wasserstein distances. The output
    metrics are the equivalent BIAS, STDE and RMSE. The discretisation
    of the numerical integration is controled by integer `N`.
    """
    BIAS = numerical_wasserstein(p, o, m=1, N=N, absolute=False)
    RMSE = numerical_wasserstein(p, o, m=2, N=N)
    RMSE = abs(BIAS) if np.isclose(RMSE**2, BIAS**2) else RMSE  # avoid sqrt(-|x|)
    STDE = np.sqrt(RMSE**2 - BIAS**2)
    return BIAS, STDE, RMSE


def error_metrics_wasserstein_weibull_vs_sample(
    Ap:float, Kp:float, o:Iterable, N=3000,
):
    """
    Compute the error metrics between an analytical Weibull distribution with
    parameters `Ap`, `Kp` and the empirical distribution that governs a sample
    of observations, 'o'. The error metrics are the numerical agreement between
    the quantile functions of both distributions, equivalent to Wasserstein
    distances. The output metrics are the equivalent BIAS, STDE and RMSE. The
    discretisation of the numerical integration is controled by integer `N`.
    """
    Qp = lambda u: weibull_ppf(np.atleast_1d(u), Ap, Kp)
    BIAS = numerical_wasserstein(Qp, o, m=1, N=N, absolute=False)
    RMSE = numerical_wasserstein(Qp, o, m=2, N=N)
    RMSE = abs(BIAS) if np.isclose(RMSE**2, BIAS**2) else RMSE  # avoid sqrt(-|x|)
    STDE = np.sqrt(RMSE**2 - BIAS**2)
    return BIAS, STDE, RMSE


def error_metrics_timeseries(p, o):
    """
    Compute the time-dependent error metrics between two time series datasets
    with predictions and observations, `p` and `o` respectively. The output
    metrics are the BIAS, STDE and RMSE.
    """
    BIAS = np.nanmean(p - o)
    RMSE = np.sqrt(np.nanmean((p - o)**2))
    RMSE = abs(BIAS) if np.isclose(RMSE**2, BIAS**2) else RMSE  # avoid sqrt(-|x|)
    STDE = np.sqrt(RMSE**2 - BIAS**2)
    return BIAS, STDE, RMSE


def normalise_error_metrics(BIAS, STDE, RMSE, nvalue, pct=True):
    """
    Given dimensional BIAS, STDE and RMSE values, make these dimensionless by
    normalising with the reference value given in `nvalue`. By default the
    output values are percentages (otherwise set `pct=False`).
    """
    factor = 100 if pct else 1
    BIASn = BIAS / nvalue * factor
    RMSEn = RMSE / nvalue * factor
    STDEn = STDE / nvalue * factor
    return BIASn, STDEn, RMSEn

