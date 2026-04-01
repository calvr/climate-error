#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix ts=8 et sw=4 sts=4 sta :
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import climate_error as climerr

from helpers import *


np.random.seed(0)

custom_mpl_style()

DATA_DIR, EXAMPLES_DIR = get_paths()


# Define the periodic function
ofun = lambda t: np.sin(t) + 0.5 * np.sin(2 * t) + 2

# Generate time values
t = np.linspace(0, 3*2*np.pi, 1000)

# Compute the original signal
o = ofun(t)


# Plotting function
def plot_signals_and_rmse(t, o, dt, ax=None, plot=False, row=True, col=True):
    mup = .2
    p = ofun(t + dt) + mup # Apply the lag to the signal p(t)
    mean_o = np.mean(o)
    t_bias, t_stde, t_rmse = climerr.error_metrics_timeseries(p, o)
    t_bias_n, t_stde_n, t_rmse_n = climerr.normalise_error_metrics(t_bias, t_stde, t_rmse, mean_o)
    q_bias, q_stde, q_rmse = climerr.error_metrics_wasserstein_2sample(p, o)
    q_bias_n, q_stde_n, q_rmse_n = climerr.normalise_error_metrics(q_bias, q_stde, q_rmse, mean_o)
    print(
          f"lag = {dt:.3f} s\n"
        + f"Time-based error:     \t{t_bias_n=:.0f}% \t{t_stde_n=:.0f}% \t{t_rmse_n=:.0f}%\n"
        + f"Quantile-based error: \t{q_bias_n=:.0f}% \t{q_stde_n=:.0f}% \t{q_rmse_n=:.0f}%\n"
    )
    if None is ax:
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
    # Plot the original and lagged signals
    ax.plot(t, o, c='k', label=r'obs(t)')
    ax.plot(t, p, c='teal', label=fr'prediction(t + {dt:.2g})')
    # Highlighting the RMSE
    ax.fill_between(t, o, p, color='teal', alpha=0.1,
        label=(
                f'tBIAS = {t_bias_n:.0f}%   tRMSE = {t_rmse_n:.0f}%'
            + f'\nqBIAS = {q_bias_n:.0f}%   qRMSE = {q_rmse_n:.0f}%'
        ),
    )
    if row:
        ax.set_xlabel('Time')
    if col:
        ax.set_ylabel('Signal')
    ax.legend(loc='lower left', bbox_to_anchor=(0, 1), ncol=3, fontsize='small', frameon=False, borderaxespad=0)
    ax.grid(False)
    ax.set_xlim(xmin=min(t), xmax=max(t))
    if plot:
        plt.show()


# Compute and plot signals with different lags

lags = [0, .1*2*np.pi, .2*2*np.pi, .5*2*np.pi]

fig, axes = plt.subplots(2, 2, figsize=(10, 3))  # create subplots

for idx, (ax, dt,) in enumerate(zip(axes.flatten(), lags)):
    row, col = divmod(idx, 2)
    row = (np.shape(axes)[1] - 1) == row
    col = 0 == col
    plot_signals_and_rmse(t, o, dt, ax=ax, row=row, col=col)

fig.tight_layout(h_pad=1, w_pad=1)
fig.subplots_adjust(left=.04, bottom=.14, right=.98, top=.9, wspace=.1, hspace=.8)
plt.savefig(EXAMPLES_DIR / 'periodic_lag_error.png', dpi=100)
plt.show()



