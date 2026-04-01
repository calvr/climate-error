#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix ts=8 et sw=4 sts=4 sta :
# -*- coding: utf-8 -*-

# ruff: noqa: E402

"""
climate_error
=============

Quantile Error Metrics and Weibull Methods for Wind Climate Analysis.

This package provides:
- quantile_error_metrics: functions to compute quantile-based error metrics
- weibull_methods: parameter estimation and validation tools for Weibull distributions
"""


# Package version
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("climate-error")
except PackageNotFoundError:  # Package is not installed (e.g., running from a development checkout)
    __version__ = "0.0.0"


# Citation info
__citation__ = (
    "Carlos Veiga Rodrigues & Io Odderskov (2025)."
    + " Climate error metrics based on Wasserstein distances."
    + " Applied Energy 398, 126392."
    + " DOI: 10.1016/j.apenergy.2025.126392"
)


# Public API imports
from .utils import get_concurrent_records, estimate_bins
from .weibull_methods import (
    weibull_moment,
    weibull_cdf,
    weibull_ppf,
    weibull_pdf,
    ewa_weibull_fit_sample,
    ewa_weibull_fit_hist,
)
from .quantile_error_metrics import (
    numerical_wasserstein,
    error_metrics_wasserstein_weibull,
    error_metrics_wasserstein_2sample,
    error_metrics_wasserstein_weibull_vs_sample,
    error_metrics_timeseries,
    normalise_error_metrics,
)


# Define the public API (`from climate_error import *`)
__all__ = [
    "__version__",
    "__citation__",
    # Utils
    "get_concurrent_records",
    "estimate_bins",
    # Weibull methods
    "weibull_moment",
    "weibull_cdf",
    "weibull_ppf",
    "weibull_pdf",
    "ewa_weibull_fit_sample",
    "ewa_weibull_fit_hist",
    # Quantile error metrics
    "numerical_wasserstein",
    "error_metrics_wasserstein_weibull",
    "error_metrics_wasserstein_2sample",
    "error_metrics_wasserstein_weibull_vs_sample",
    "error_metrics_timeseries",
    "normalise_error_metrics",
]

