#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix ts=8 et sw=4 sts=4 sta :
# -*- coding: utf-8 -*-

# ruff: noqa: E731

import logging
import warnings
import numpy as np
import scipy as sp
import scipy.optimize
import scipy.special
import scipy.stats
from scipy.optimize import brentq
#from scipy.special import gamma, polygamma
from scipy.special import gammaln
from typing import Iterable

_logger = logging.getLogger(__name__)


def weibull_cdf(x, A, K):
    """
    Return probability of P(X <= x) for given `x` value(s),
    for a Weibull distribution with parameters `A` and `K`.
    """
    return 1 - np.exp(-(x/A)**K)


def weibull_ppf(F, A, K):
    """
    Return the `x` value associated with a probability P(X <= x), for a
    Weibull distribution with parameters `A` and `K`.
    """
    return A*(-np.log(1 - F))**(1./K)


def weibull_moment(A, K, n=1):
    """
    Return the `n` non-centred statistical moment associated to
    a Weibull distribution with parameters `A` and `K`.
    """
    #return A**n * gamma(1 + n/K)
    return np.exp(n*np.log(A) + gammaln(1 + n/K))


def weibull_pdf(x, A, K):
    """
    Return the probability density for given `x` value(s),
    for a Weibull distribution with parameters `A` and `K`.
    """
    return K/A * (x/A)**(K-1) * np.exp(-(x/A)**K)


def mle_weibull_fit(x:Iterable):
    """
    Fit Weibull parameters to `x` sample using the Maximum Likelihood Estimator
    method in SciPy.
    """
    try:
        x = np.asarray(x).ravel()
        i = np.isfinite(x)
        assert i.sum() > 0, "Given `x` sample has no finite records?"
        xmu = np.mean(x[i])
        assert not np.allclose(xmu, x[i]), "Given `x` sample is filled with constant values?"
        K, _, A = sp.stats.weibull_min.fit(x[i], 2, floc=0, scale=xmu)
        assert np.isfinite(K) and K > 0, f"K solution value invalid {K=:g}."
        assert np.isfinite(A) and A > 0, f"A solution value invalid {A=:g}."
    except Exception as ex:
        _logger.warning("MLE fit of Weibull parameters failed", exc_info=True)
        warnings.warn(f"MLE fit of Weibull parameters failed: {ex}", RuntimeWarning, stacklevel=2)
        return np.nan, np.nan
    return A, K

        
def ewa_weibull_fit(xmu, x3mu, prob_exceed_mu, tol=1e-6, maxiter=1000):
    """
    Fit Weibull parameters following the European Wind Atlas method.
    This approach considers the following contraints:
    - Total wind energy of the fitted Weibull distribution must be equal
      to that of the sample.
    - The probability to have wind speeds higher than the average value is the
      same for both the fitted distribution and the sample.

    Args:
        xmu (float): The mean of the sample or distribution, mean(X).
        x3mu (float): The 3rd non-centred statistical moment of the sample or
            distribution, mean(X**3). Note that mean(X**3) > mean(X)**3 for
            the input data to be valid.
        prob_exceed_mu (float): The probability for the random variable X to
            exceed the mean value, `xmu`. Value must be between ]0, 1[.
        tol (float, optional): The numerical tolerance for the root-finding
            algorithm.
        maxiter (int, optional): The maximum number of iterations that the
            root-finding algorithm will be allowed to converge to a solution.
    Returns:
        A, K (float): Scale and shape parameters of the Weibull distribution.

    Note:
    Although the original formulation of the EWA method allows for a point-based
    initial guess root-finding algorithm such as the Newton-Rhapson or secant
    methods, the Brent method is used instead as it was found to be more fast
    and numerically robust.

    References:
    - Troen & Petersen (1989). European Wind Atlas. Risø.
      URL: https://orbit.dtu.dk/en/publications/european-wind-atlas/
    - EMD WindPro 2.9 Manual, Section 3.1.3, Eq. (9).
      URL: https://help.emd.dk/knowledgebase/content/WindPRO2.9/03-UK_WindPRO2.9_ENERGY.pdf
      URL: https://help.emd.dk/mediawiki/index.php/File:Description_of_Weibull_fitting.pdf
    """
    ## »»» ROOT-FINDING FORMULATION TO COMPUTE K
    ## Eq. (9) in https://help.emd.dk/knowledgebase/content/WindPRO2.9/03-UK_WindPRO2.9_ENERGY.pdf
    # root_fun = lambda K, mu, mu3, p_ws_gt_mu: np.exp(-(mu/(mu3/gamma(1 + 3./K)**(1/3.)))**K) - p_ws_gt_mu
    ## Manipulation of Eq. (9) and conversion to log space
    # root_fun = lambda K, mu, mu3, p_ws_gt_mu: K/3.*np.log(gamma(1 + 3./K)*(mu**3)/mu3) - np.log(-np.log(p_ws_gt_mu))
    # root_dfun = lambda K, mu, mu3, p_ws_gt_mu: np.log(gamma(1 + 3./K)*(mu**3)/mu3)/3. - polygamma(0, 1 + 3./K)/K
    ## Highest robustness if gammaln is used instead of gamma
    root_fun = lambda K, ln_xmu3_x3mu, lnmln_p_ws_gt_mu: K/3.*(gammaln(1+3./K) + ln_xmu3_x3mu) - lnmln_p_ws_gt_mu
    #root_dfun = lambda K, ln_xmu3_x3mu, lnmln_p_ws_gt_mu: (gammaln(1+3./K) + ln_xmu3_x3mu)/3. - polygamma(0, 1+3./K)/K
    ## «««
    assert xmu > 0, f"Given {xmu=} value, for the mean(x), must be greater than 0."
    assert x3mu > (xmu**3), (
        f"Expecting mean(x**3) > mean(x)**3 but insted got {x3mu=} and {xmu**3=}."
    )
    assert (prob_exceed_mu >= 0) and (prob_exceed_mu <= 1), (
        f"Expecting P(X>mu) in [0, 1], got {prob_exceed_mu=} instead."
    )
    prob_exceed_mu = min(max(prob_exceed_mu, np.finfo(float).tiny), 1 - np.finfo(float).eps)
    ## Define arguments to root-finding function
    ln_xmu3_x3mu = 3*np.log(xmu) - np.log(x3mu)  # np.log(xmu**3/x3mu)
    lnmln_p_ws_gt_mu = np.log(-np.log(prob_exceed_mu))
    args = (ln_xmu3_x3mu, lnmln_p_ws_gt_mu,)
    ## Brent method superior to Newton-Rhapson/secant (faster & robust)... define bracket
    n = 0
    a, b = np.exp(np.log(2) - .2), np.exp(np.log(2) + .2)  # initial guess of x0 = 2
    while root_fun(a, *args) * root_fun(b, *args) > 0:
        assert min(a, b) > tol and n < maxiter, f"Failed to bracket root in log(K)! {a=} {b=}"
        a, b = np.exp(np.log(a) - .2), np.exp(np.log(b) + .2)
        n += 1
    K, info = brentq(
        f=root_fun, a=a, b=b, args=args,
        xtol=tol, maxiter=maxiter, full_output=True, disp=False,
    )
    assert info.converged, (
        f"Method did not converge after {info.iterations} iterations."
    )
    #assert abs(root_fun(K, *args)) <= tol, (
    #    f"root-function value above tolerance, {abs(root_fun(K, *args)):g} > {tol:g}."
    #)
    assert np.isfinite(K) and K > 0, f"K solution value invalid {K=:g}."
    A = np.exp((np.log(x3mu) - gammaln(1 + 3./K)) / 3.)  # A = (x3mu / gamma(1 + 3./K))**(1./3.)
    assert np.isfinite(A) and A > 0, f"A solution value invalid {A=:g}."
    return A, K


def ewa_weibull_fit_sample(x:Iterable, tol=1e-6, maxiter=1000):
    """
    Fit Weibull parameters to `x` sample following the European Wind Atlas
    method. For references and implementation details check the documentation
    of function `ewa_weibull_fit`.

    Args:
        x (numpy.ndarray or list-like): Sample of data values to which the
            Weibull parameters will be fitted.
        tol (float, optional): The numerical tolerance for the root-finding
            algorithm.
        maxiter (int, optional): The maximum number of iterations that the
            root-finding algorithm will be allowed to converge to a solution.
    Returns:
        A, K (float): Scale and shape parameters of the Weibull distribution.
    """
    try:
        x = np.asarray(x).ravel()
        i = np.isfinite(x)
        assert i.sum() > 0, "Given `x` sample has no finite records?"
        xmu = np.mean(x[i])
        x3mu = np.mean(x[i]**3)  # 3rd order moment
        prob_exceed_mu = sum(x[i] > xmu) / float(i.sum())  # probability to exceed mean value
        A, K = ewa_weibull_fit(xmu, x3mu, prob_exceed_mu, tol=tol, maxiter=maxiter)
    except Exception as ex:
        _logger.warning("Sample-based EWA fit of Weibull parameters failed", exc_info=True)
        warnings.warn(f"Sample-based EWA fit of Weibull parameters failed: {ex}", RuntimeWarning, stacklevel=2)
        return np.nan, np.nan
    return A, K


def ewa_weibull_fit_hist(
    xbins:Iterable, bin_counts:Iterable, bin_edge_min=None, bin_edge_max=None,
    tol=1e-6, maxiter=1000,
):
    """
    Fit Weibull parameters to histogram following the European Wind Atlas
    method. For references and implementation details check the documentation
    of function `ewa_weibull_fit`.

    Args:
        xbins (numpy.ndarray or list-like): Bins of data values to which the
            Weibull parameters will be fitted.
        bin_counts (numpy.ndarray or list-like): Frequency of record counts
            associated to each bin in `xbins`.
        tol (float, optional): The numerical tolerance for the root-finding
            algorithm.
        maxiter (int, optional): The maximum number of iterations that the
            root-finding algorithm will be allowed to converge to a solution.
    Returns:
        A, K (float): Scale and shape parameters of the Weibull distribution.
    """
    try:
        x = np.asarray(xbins).ravel()
        p = np.asarray(bin_counts).ravel()
        i = ~(np.isfinite(x) & np.isfinite(p))
        assert 0 == i.sum(), (
            f"{i.sum()} invalid values found in either `xbins` or `bin_counts`, i.e. NaN | Inf."
        )
        assert np.all(x >= 0), f"Not all values in `xbins` are positive? {x}"
        assert np.all(p >= 0), f"Not all values in `bin_counts` are positive? {p}"
        p = p / p.sum()
        i = np.argsort(x)
        x, p = x[i], p[i]
        x_edges = .5*(x[1:] + x[:-1])
        bin_edge_min = (
            2*x[0] - x_edges[0] if None is bin_edge_min or bin_edge_min > x[0]
            else bin_edge_min
        )
        bin_edge_max = (
            2*x[-1] - x_edges[-1] if None is bin_edge_max or bin_edge_max < x[-1]
            else bin_edge_max
        )
        x_edges = np.concatenate([[bin_edge_min], x_edges, [bin_edge_max]])
        xmu = np.sum(x * p)
        x3mu = np.sum(x**3 * p)  # 3rd order moment
        i = np.flatnonzero(x_edges[:-1] > xmu)
        prob_exceed_mu = np.sum(p[i])
        i = i.min() if np.size(i) > 0 else np.size(x)
        prob_exceed_mu += p[i-1] * (x_edges[i] - xmu)/(x_edges[i] - x_edges[i-1])
        A, K = ewa_weibull_fit(xmu, x3mu, prob_exceed_mu, tol=tol, maxiter=maxiter)
    except Exception as ex:
        _logger.warning("Histogram-based EWA fit of Weibull parameters failed", exc_info=True)
        warnings.warn(f"Histogram-based EWA fit of Weibull parameters failed: {ex}", RuntimeWarning, stacklevel=2)
        return np.nan, np.nan
    return A, K

