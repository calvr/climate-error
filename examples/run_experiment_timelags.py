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
df = pd.read_csv(DATA_DIR / "wind_data_ventosa_32m.csv.gz", index_col=0, header=0, parse_dates=True)
tzoomi = pd.to_datetime('2003-01-21')
tzoome = tzoomi + pd.timedelta_range('4d', '5d')[-1]
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
## Generate series with timelags
##
print("""
## EXPERIMENT: WSp is copy of WSo with time lags
""")
wsp = pd.Series(wso.values, index=wso.index, name='prediction')
#wsp = apply_random_lags(wsp)
wsp = apply_coherent_lags(wsp)
assert (wso.dropna().index == wsp.dropna().index).all(), "Observed and Predicted lengths do not match?"

bins, bin_edges = climerr.estimate_bins(wso, wsp)

## HISTOGRAMS
#wso.hist(grid=False, density=True, bins=bins, histtype='step', label=wso.name)
#wsp.hist(grid=False, density=True, bins=bins, histtype='step', label=wsp.name)
#plt.legend()
#plt.show()

## TIMESERIES AND HISTOGRAMS
#kwargs = dict(show=False, histtype='step', marker=',', ls='None')
kwargs = dict(show=False, histtype='step', marker='None', ls='-')
fig = plot_timeseries_w_hist(x=fill_time_gaps(wso).index, y=fill_time_gaps(wso), bins=bins, label=wso.name, color='C0', **kwargs)
fig = plot_timeseries_w_hist(x=fill_time_gaps(wsp).index, y=fill_time_gaps(wsp), bins=bins, label=wsp.name, color='C1', fig=fig, **kwargs)
fig.axes[0].set_xlim(fill_time_gaps(wso).index.min(), fill_time_gaps(wso).index.max())
fig.axes[0].set_ylim(0, 40)
fig.axes[0].set_xlabel('Time')
fig.axes[0].set_ylabel(r'Windspeed (m s$^{-1}$)')
fig.axes[0].legend(fontsize='large', frameon=False)
#fig.axes[1].set_xlabel(r'EDF (m$^{-1}$ s)')
fig.axes[1].set_xlabel(r'PDH (m$^{-1}$ s)')
fig.tight_layout()
fig.savefig(EXAMPLES_DIR / 'experiment_timelags.png')
#fig.savefig(EXAMPLES_DIR / 'experiment_timelags.pdf')

fig.axes[0].legend(fontsize='large', frameon=False, borderpad=0)
fig.axes[0].set_xlim(xmin=tzoomi, xmax=tzoome)
fig.axes[0].set_ylim(0, 30)
bbox0 = fig.axes[0].get_position()
bbox1 = fig.axes[1].get_position()
fig.delaxes(fig.axes[1])
fig.axes[0].set_position([bbox0.x0, bbox0.y0, bbox1.x1-bbox0.x0, bbox0.height])
fig.savefig(EXAMPLES_DIR / 'experiment_timelags_2.png')
#fig.savefig(EXAMPLES_DIR / 'experiment_timelags_2.pdf')
fig.show()

plt.show()
plt.close('all')




##
## Compute error metrics
##
Ao, Ko = climerr.ewa_weibull_fit_sample(wso)
Ap, Kp = climerr.ewa_weibull_fit_sample(wsp)
wBIAS, wSTDE, wRMSE = climerr.error_metrics_wasserstein_weibull(Ap, Kp, Ao, Ko)
eBIAS, eSTDE, eRMSE = climerr.error_metrics_wasserstein_2sample(wsp, wso, N=3000)
tBIAS, tSTDE, tRMSE = climerr.error_metrics_timeseries(wsp, wso)
wBIASn, wSTDEn, wRMSEn = climerr.normalise_error_metrics(wBIAS, wSTDE, wRMSE, climerr.weibull_moment(Ao, Ko, 1))
eBIASn, eSTDEn, eRMSEn = climerr.normalise_error_metrics(eBIAS, eSTDE, eRMSE, wso.mean())
tBIASn, tSTDEn, tRMSEn = climerr.normalise_error_metrics(tBIAS, tSTDE, tRMSE, wso.mean())

ofitBIAS, ofitSTDE, ofitRMSE = climerr.error_metrics_wasserstein_weibull_vs_sample(Ao, Ko, wso, N=3000)
ofitBIASn, ofitSTDEn, ofitRMSEn = climerr.normalise_error_metrics(ofitBIAS, ofitSTDE, ofitRMSE, wso.mean())
pfitBIAS, pfitSTDE, pfitRMSE = climerr.error_metrics_wasserstein_weibull_vs_sample(Ap, Kp, wsp, N=3000)
pfitBIASn, pfitSTDEn, pfitRMSEn = climerr.normalise_error_metrics(pfitBIAS, pfitSTDE, pfitRMSE, wsp.mean())


tMAE = (wsp - wso).abs().mean()
tMAEn = tMAE / wso.mean() * 100
eAREA = climerr.numerical_wasserstein(wsp, wso, N=3000, m=1, absolute=True)
eAREAn = eAREA / wso.mean() * 100


table = pd.DataFrame(
    {
        "Time-dependent error": {
            "BIAS": f"{tBIAS:.2f} m/s   ({tBIASn:4.1f}%)",
            "STDE": f"{tSTDE:.2f} m/s   ({tSTDEn:4.1f}%)",
            "RMSE": f"{tRMSE:.2f} m/s   ({tRMSEn:4.1f}%)",
            "MAE" : f"{ tMAE:.2f} m/s   ({ tMAEn:4.1f}%)",
        },
        "Climate error (empirical)": {
            "BIAS": f"{eBIAS:.2f} m/s   ({eBIASn:4.1f}%)",
            "STDE": f"{eSTDE:.2f} m/s   ({eSTDEn:4.1f}%)",
            "RMSE": f"{eRMSE:.2f} m/s   ({eRMSEn:4.1f}%)",
            "Area": f"{eAREA:.2f} m/s   ({eAREAn:4.1f}%)",
        },
        "Climate error (Weibull)": {
            "BIAS": f"{wBIAS:.2f} m/s   ({wBIASn:4.1f}%)",
            "STDE": f"{wSTDE:.2f} m/s   ({wSTDEn:4.1f}%)",
            "RMSE": f"{wRMSE:.2f} m/s   ({wRMSEn:4.1f}%)",
        },
        "Weibull wso fit error": {
            "BIAS": f"{ofitBIAS:.2f} m/s   ({ofitBIASn:4.1f}%)",
            "STDE": f"{ofitSTDE:.2f} m/s   ({ofitSTDEn:4.1f}%)",
            "RMSE": f"{ofitRMSE:.2f} m/s   ({ofitRMSEn:4.1f}%)",
        },
        "Weibull wsp fit error": {
            "BIAS": f"{pfitBIAS:.2f} m/s   ({pfitBIASn:4.1f}%)",
            "STDE": f"{pfitSTDE:.2f} m/s   ({pfitSTDEn:4.1f}%)",
            "RMSE": f"{pfitRMSE:.2f} m/s   ({pfitRMSEn:4.1f}%)",
        },
    }
)
table_txt = tabulate.tabulate(table, headers='keys', tablefmt='plain', colalign=(table.columns.size+1)*["right"])
print(table_txt)
with open(EXAMPLES_DIR / 'experiment_timelags_table.txt', mode='w') as fid:
    fid.write(table_txt + '\n')


plt.close('all')

co = plt.rcParams['axes.prop_cycle'].by_key()['color'][0]
cp = plt.rcParams['axes.prop_cycle'].by_key()['color'][1]
new_co = 'skyblue'    # darken_color(co)
new_cp = 'rosybrown'  # darken_color(cp)
wso.hist(grid=False, density=True, bins=bins, histtype='step', color=co, label='$ws_o$ density from histogram')
wsp.hist(grid=False, density=True, bins=bins, histtype='step', color=cp, label='$ws_p$ density from histogram')
x = np.linspace(0, bins.max(), 101)
plt.plot(x, climerr.weibull_pdf(x, Ao, Ko), lw=1.2, ls=(0, (6, 2)), color=new_co, label=f'$ws_o$ Weibull fit $A$={Ao:.1f} m/s, $K$={Ko:.2f}')
plt.plot(x, climerr.weibull_pdf(x, Ap, Kp), lw=1.2, ls=(0, (5, 4)), color=new_cp, label=f'$ws_p$ Weibull fit $A$={Ap:.1f} m/s, $K$={Kp:.2f}')
plt.legend(loc='center right', frameon=False, fontsize=10, bbox_to_anchor=(1, .667), borderpad=0, labelspacing=0)
#plt.title(
#      r'$K_{\mathregular{error}}$ = %.1f%%' % ((Kp/Ko-1)*100)
#    + r',  $A_{\mathregular{error}}$ = %.1f%%' % ((Ap/Ao-1)*100)
#)
plt.text(.99, .99,
         rf'Climate error (Weibull): BIAS={wBIASn:4.1f}%  STDE={wSTDEn:4.1f}%  RMSE={wRMSEn:4.1f}%'
    + f'\n$ws_o$ Weibull fit error: BIAS={ofitBIASn:4.1f}%  STDE={ofitSTDEn:4.1f}%  RMSE={ofitRMSEn:4.1f}%'
    + f'\n$ws_p$ Weibull fit error: BIAS={pfitBIASn:4.1f}%  STDE={pfitSTDEn:4.1f}%  RMSE={pfitRMSEn:4.1f}%'
    ,
    ha='right', va='top', transform=plt.gca().transAxes, fontsize='large',
)
plt.ylim([0, 0.14])
plt.xlim([0, 30])
plt.xlabel(r'Wind speed $(\text{m}\,\text{s}^{-1})$', labelpad=0)
plt.ylabel(r'Probability Density $(\text{m}^{-1}\,\text{s})$', labelpad=0)
plt.gcf().tight_layout()
#plt.savefig(EXAMPLES_DIR / 'experiment_timelags_hist.pdf')
plt.savefig(EXAMPLES_DIR / 'experiment_timelags_hist.png', dpi=100)
#plt.show()

plt.close('all')
  
co = plt.rcParams['axes.prop_cycle'].by_key()['color'][0]
cp = plt.rcParams['axes.prop_cycle'].by_key()['color'][1]
new_co = 'skyblue'    # darken_color(co)
new_cp = 'rosybrown'  # darken_color(cp)
wso.hist(grid=False, density=True, bins=bins, histtype='step', color=co, label=r'$ws_o$ density from histogram')
wsp.hist(grid=False, density=True, bins=bins, histtype='step', color=cp, label=r'$ws_p$ density from histogram')
x = np.linspace(0, bins.max(), 101)
#plt.plot(x, climerr.weibull_pdf(x, Ao, Ko), lw=1.2, ls=(0, (6, 2)), color=new_co, label=f'$ws_o$ Weibull fit $A$={Ao:.1f} m/s, $K$={Ko:.2f}')
#plt.plot(x, climerr.weibull_pdf(x, Ap, Kp), lw=1.2, ls=(0, (5, 4)), color=new_cp, label=f'$ws_p$ Weibull fit $A$={Ap:.1f} m/s, $K$={Kp:.2f}')
plt.legend(loc='center right', frameon=False, fontsize=10, bbox_to_anchor=(1, .667), borderpad=0, labelspacing=0)
#plt.title(
#      r'$K_{\mathregular{error}}$ = %.1f%%' % ((Kp/Ko-1)*100)
#    + r',  $A_{\mathregular{error}}$ = %.1f%%' % ((Ap/Ao-1)*100)
#)
plt.text(.99, .99,
               rf'Time-based error: BIAS={tBIASn:4.1f}%  STDE={tSTDEn:4.1f}%  RMSE={tRMSEn:4.1f}%'
    + '\n\n'
    + rf'Climate error (empirical): BIAS={eBIASn:4.1f}%  STDE={eSTDEn:4.1f}%  RMSE={eRMSEn:4.1f}%',
    ha='right', va='top', transform=plt.gca().transAxes, fontsize='large',
)
plt.ylim([0, 0.10])
plt.xlim([0, 30])
plt.xlabel(r'Wind speed $(\text{m}\,\text{s}^{-1})$', labelpad=0)
plt.ylabel(r'Probability Density $(\text{m}^{-1}\,\text{s})$', labelpad=0)
plt.gcf().tight_layout()
#plt.savefig(EXAMPLES_DIR / 'experiment_timelags_hist2.pdf')
plt.savefig(EXAMPLES_DIR / 'experiment_timelags_hist2.png', dpi=100)
plt.show()


plt.close('all')

fig, ax = plt.subplots(figsize=(4,4))
ax.set_aspect('equal', 'box')
data = [
    [tBIAS, tSTDE, 'Time-dependent error', dict(marker='D', markersize=8, markerfacecolor="None", markeredgecolor="k", markeredgewidth=2)],
    [eBIAS, eSTDE, 'Climate error (empirical)', dict(marker='x', markerfacecolor="C7", markeredgecolor="C7", markersize=12, markeredgewidth=3)],
    [wBIAS, wSTDE, 'Climate error (Weibull)', dict(marker='+', markerfacecolor="C6", markeredgecolor="C6", markersize=15, markeredgewidth=3)],
    [ofitBIAS, ofitSTDE, 'Weibull $ws_o$ fit error', dict(marker='3', markerfacecolor="None", markeredgecolor="C0", markersize=12, markeredgewidth=1.5)],
    [pfitBIAS, pfitSTDE, 'Weibull $ws_p$ fit error', dict(marker='4', markerfacecolor="None", markeredgecolor="C1", markersize=12, markeredgewidth=1.5)],
]
_ = [ax.plot(abs(x), abs(y), ls='None', label=label, clip_on=False, **kwargs) for x, y, label, kwargs in data]
ax.legend(loc='lower right', frameon=True, fontsize=10, handleheight=0.3, handletextpad=0.3, labelspacing=0.8, borderpad=0.6)
max_radius = 1.05*max([*ax.get_xlim(), *ax.get_ylim()])
max_radius = 2.5
ax.set_xlim(xmin=0, xmax=max_radius)
ax.set_ylim(ymin=0, ymax=max_radius)
ax.set_xlabel(r'|BIAS| $(\text{m}\,\text{s}^{-1})$', labelpad=0)
ax.set_ylabel(r'STDE $(\text{m}\,\text{s}^{-1})$', labelpad=0)
plt.gcf().tight_layout()
ax.plot([0, max_radius], [0, max_radius], c='grey', linestyle=':', linewidth=.5)
radii = ax.get_xticks()
radii = np.append(radii, np.arange(radii[-1], max_radius*np.sqrt(2), radii[-1] - radii[-2])[1:])
_ = [
    ax.add_artist(plt.Circle((0, 0), radius, color='grey', linestyle=':', fill=False, linewidth=.5))
    for radius in radii if radius > 0
]
#plt.gcf().subplots_adjust(left=.14, bottom=.10)
#plt.savefig(EXAMPLES_DIR / 'experiment_timelags_taylor.pdf')
plt.savefig(EXAMPLES_DIR / 'experiment_timelags_taylor.png')
plt.show()




