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
import tomllib
from pathlib import Path

def _load_citation() -> str:
    """
    Load CITATION.cff as a string for climate_error.__citation__.
    If running from an installed wheel (without source files), fall back to a short message.
    """
    root = Path(__file__).resolve().parents[1]
    cff = root / "CITATION.cff"
    if not cff.exists():
        return (
            "Veiga Rodrigues & Odderskov (2025), Applied Energy 398, 126392."
             + "\nDOI: 10.1016/j.apenergy.2025.126392"
        )
    try:
        data = tomllib.loads(cff.read_text(encoding="utf-8"))
        authors = ", ".join(a["family-names"] for a in data.get("authors", []))
        year = data.get("date-released", "")[:4]
        title = data.get("title", "")
        doi = data.get("identifiers", [{}])[0].get("value", "")
        return f"{authors} ({year}). {title}. DOI: {doi}"
    except Exception:
        return cff.read_text(encoding="utf-8")

__citation__ = _load_citation()


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

