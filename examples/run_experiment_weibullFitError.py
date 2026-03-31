#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix ts=8 et sw=4 sts=4 sta :
# -*- coding: utf-8 -*-

import tabulate
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

import climate_error as climerr

from helpers import *


np.random.seed(0)

custom_mpl_style()

DATA_DIR, EXAMPLES_DIR = get_paths()


##
## Read wind data
##
df = pd.read_csv(DATA_DIR / "wind_data_capel_m1_50m.csv.gz", index_col=0, header=0, parse_dates=True)
wso = df.iloc[:,0].dropna()
wso.name = 'observation'

availability = {
    yr: (
        ((wso.index >= f'{yr}-01-01') & (wso.index < f'{yr+1}-01-01')).sum()
        / pd.date_range(f'{yr}-01-01', f'{yr+1}-01-01', freq='10min', inclusive='left').size
    )
    for yr in wso.index.year.unique()
}
years = [k for k, v in availability.items() if v > .95]
assert len(years) > 0, f"Availability bad?  {availability}"
wso = wso.loc[(wso.index >= f'{min(years)}-01-01') & (wso.index < f'{max(years)+1}-01-01')]


##
## Compute error metrics
##
print("""
## EXPERIMENT: Estimate Weibull fit error
""")

bins, bin_edges = climerr.estimate_bins(wso)

Ao, Ko = climerr.ewa_weibull_fit_sample(wso)
fitBIAS, fitSTDE, fitRMSE = climerr.error_metrics_wasserstein_weibull_vs_sample(Ao, Ko, wso, N=3000)
fitBIASn, fitSTDEn, fitRMSEn = climerr.normalise_error_metrics(fitBIAS, fitSTDE, fitRMSE, wso.mean())


##
## Output table
##
table = pd.DataFrame(
    {
        "Weibull fit error through Wasserstein distances": {
            "BIAS": f"{fitBIAS:.2f} m/s   ({fitBIASn:4.1f}%)",
            "STDE": f"{fitSTDE:.2f} m/s   ({fitSTDEn:4.1f}%)",
            "RMSE": f"{fitRMSE:.2f} m/s   ({fitRMSEn:4.1f}%)",
        },
    }
)
table_txt = tabulate.tabulate(table, headers='keys', tablefmt='plain', colalign=(table.columns.size+1)*["right"])
print(table_txt)
with open(EXAMPLES_DIR / 'experiment_weibullFitError_table.txt', mode='w') as fid:
    fid.write(table_txt + '\n')


##
## Make plots
##

plt.close('all')

co = plt.rcParams['axes.prop_cycle'].by_key()['color'][0]
cp = plt.rcParams['axes.prop_cycle'].by_key()['color'][1]
new_co = 'skyblue'    # darken_color(co)
new_cp = 'rosybrown'  # darken_color(cp)
wso.hist(grid=False, density=True, bins=bins, histtype='step', color=co, label=f'$ws_o$ density from histogram')
x = np.linspace(0, bins.max(), 101)
plt.plot(x, climerr.weibull_pdf(x, Ao, Ko), lw=1.2, ls=(0, (6, 2)), color=new_co, label=f'$ws_o$ Weibull fit $A$={Ao:.1f} m/s, $K$={Ko:.2f}')
plt.legend(loc='center right', frameon=False, fontsize=10, bbox_to_anchor=(.99, .80), borderpad=0, labelspacing=0)
plt.text(.98, .98, 
    f'Climate error for Weibull fit vs. EDF\nBIAS={fitBIASn:4.1f}%, RMSE={fitRMSEn:4.1f}%, STDE={fitSTDEn:4.1f}%',
    ha='right', va='top', transform=plt.gca().transAxes, fontsize='large',
    bbox=dict(boxstyle='square', facecolor='white', edgecolor='None', alpha=1),
)
wso_mu = wso.mean()
fit_mu = climerr.weibull_moment(Ao, Ko, 1)
plt.axvline(wso_mu, color=co, lw=1, ls='-')
plt.axvline(fit_mu, color=new_co, lw=1, ls=(0, (6, 2)))
plt.text(wso_mu, 0, r'$\;\mu_o\;$',
    ha=('right' if wso_mu < fit_mu else 'left'), va='bottom', fontsize='large',
)
plt.text(fit_mu, 0, r'$\;\mu_{Weibull(A_o, K_o)}\;$',
    ha=('right' if wso_mu >= fit_mu else 'left'), va='bottom', fontsize='large',
)
plt.ylim([0, 0.12])
plt.xlim([0, 30])
plt.xlabel(r'Wind speed $(\text{m}\,\text{s}^{-1})$', labelpad=0)
plt.ylabel(r'Probability Density $(\text{m}^{-1}\,\text{s})$', labelpad=0)
plt.gcf().tight_layout()
#plt.savefig(EXAMPLES_DIR / 'experiment_weibullFitError.pdf')
plt.savefig(EXAMPLES_DIR / 'experiment_weibullFitError.png', dpi=100)
plt.show()

