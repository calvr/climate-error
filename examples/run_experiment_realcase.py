#!/usr/bin/env python3
# vim: set fileencoding=utf-8 fileformat=unix ts=8 et sw=4 sts=4 sta :
# -*- coding: utf-8 -*-

import tabulate
import numpy as np
import pandas as pd
import xarray as xr
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

obs_fn = DATA_DIR / "wind_data_capel_m1_50m.csv.gz"
prd_fn = DATA_DIR / "newa_mesots_capel_cynon.nc"
outlabel = "realcase"

df = pd.read_csv(obs_fn, index_col=0, header=0, parse_dates=True)
tzoomi = pd.to_datetime('1992-02-26')
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


## Read WSp data
ds = xr.open_dataset(prd_fn)
wsp = ds['WS'].sel(height=50).compute().to_pandas()
wsp.name = "prediction"
ds.close()

wsp = fill_time_gaps(wsp)
dt = pd.Series(wsp.index, dtype=wsp.index.dtype).diff().dropna().mode()[0]
dt = f"{int(np.round(dt.total_seconds()/60))}min"
wso = wso.resample(dt, offset=0, label='right').mean()
wsp, wso = climerr.get_concurrent_records(wsp, wso, to_list=True)


## Get a Z-Scaled corrected WSc
wsc = (wsp - wsp.mean())/wsp.std(ddof=0) * wso.std(ddof=0) + wso.mean()
wsc.name = "Z-scaled prediction"
wsp.name = "original prediction"




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
kwargs = dict(show=False, histtype='step', marker='None', ls='--', lw=1)
fig = plot_timeseries_w_hist(x=fill_time_gaps(wsc).index, y=fill_time_gaps(wsc), bins=bins, label=wsc.name, color='C3', fig=fig, **kwargs)
fig.axes[0].set_xlim(fill_time_gaps(wso).index.min(), fill_time_gaps(wso).index.max())
fig.axes[0].set_ylim(0, 35)
fig.axes[0].set_xlabel('Time')
fig.axes[0].set_ylabel('Windspeed (m s$^{-1}$)')
fig.axes[0].legend(fontsize='large', frameon=False, borderpad=0)
#fig.axes[1].set_xlabel('EDF (m$^{-1}$ s)')
fig.axes[1].set_xlabel('PDH (m$^{-1}$ s)')
fig.tight_layout()
fig.savefig(EXAMPLES_DIR / f'experiment_{outlabel}.png', dpi=100)
#fig.savefig(EXAMPLES_DIR / f'experiment_{outlabel}.pdf')

#fig.axes[0].plot(fill_time_gaps(wsc).index, fill_time_gaps(wsc), color='C3', ls='--', lw=0.8, marker='None', label=wsc.name)
fig.axes[0].legend(fontsize='large', frameon=False)
fig.axes[0].set_xlim(xmin=tzoomi, xmax=tzoome)
fig.axes[0].set_ylim(0, 25)
bbox0 = fig.axes[0].get_position()
bbox1 = fig.axes[1].get_position()
fig.delaxes(fig.axes[1])
fig.axes[0].set_position([bbox0.x0, bbox0.y0, bbox1.x1-bbox0.x0, bbox0.height])
fig.savefig(EXAMPLES_DIR / f'experiment_{outlabel}_2.png', dpi=100)
#fig.savefig(EXAMPLES_DIR / f'experiment_{outlabel}_2.pdf')
fig.show()

plt.show()
plt.close('all')


#Ao, Ko = climerr.ewa_weibull_fit_sample(wso)
#Ap, Kp = climerr.ewa_weibull_fit_sample(wsp)
#Ac, Kc = climerr.ewa_weibull_fit_sample(wsc)
#wBIAS, wSTDE, wRMSE = climerr.error_metrics_wasserstein_weibull(Ap, Kp, Ao, Ko)
eBIAS, eSTDE, eRMSE = climerr.error_metrics_wasserstein_2sample(wsp, wso, N=3000)
tBIAS, tSTDE, tRMSE = climerr.error_metrics_timeseries(wsp, wso)
#wBIASn, wSTDEn, wRMSEn = climerr.normalise_error_metrics(wBIAS, wSTDE, wRMSE, weibullMoment(Ao, Ko, 1))
eBIASn, eSTDEn, eRMSEn = climerr.normalise_error_metrics(eBIAS, eSTDE, eRMSE, wso.mean())
tBIASn, tSTDEn, tRMSEn = climerr.normalise_error_metrics(tBIAS, tSTDE, tRMSE, wso.mean())

ceBIAS, ceSTDE, ceRMSE = climerr.error_metrics_wasserstein_2sample(wsc, wso, N=3000)
ctBIAS, ctSTDE, ctRMSE = climerr.error_metrics_timeseries(wsc, wso)
ceBIASn, ceSTDEn, ceRMSEn = climerr.normalise_error_metrics(ceBIAS, ceSTDE, ceRMSE, wso.mean())
ctBIASn, ctSTDEn, ctRMSEn = climerr.normalise_error_metrics(ctBIAS, ctSTDE, ctRMSE, wso.mean())


tMAE = (wsp - wso).abs().mean()
tMAEn = tMAE / wso.mean() * 100
ctMAE = (wsc - wso).abs().mean()
ctMAEn = ctMAE / wso.mean() * 100
eAREA = climerr.numerical_wasserstein(wsp, wso, N=3000, m=1, absolute=True)
eAREAn = eAREA / wso.mean() * 100
ceAREA = climerr.numerical_wasserstein(wsc, wso, N=3000, m=1, absolute=True)
ceAREAn = ceAREA / wso.mean() * 100




#ofitBIAS, ofitSTDE, ofitRMSE = climerr.error_metrics_wasserstein_weibull_vs_sample(Ao, Ko, wso, N=3000)
#ofitBIASn, ofitSTDEn, ofitRMSEn = climerr.normalise_error_metrics(ofitBIAS, ofitSTDE, ofitRMSE, wso.mean())
#pfitBIAS, pfitSTDE, pfitRMSE = climerr.error_metrics_wasserstein_weibull_vs_sample(Ap, Kp, wsp, N=3000)
#pfitBIASn, pfitSTDEn, pfitRMSEn = climerr.normalise_error_metrics(pfitBIAS, pfitSTDE, pfitRMSE, wsp.mean())

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
        "Time-dependent error for Z-scaled TS": {
            "BIAS": f"{ctBIAS:.2f} m/s   ({ctBIASn:4.1f}%)",
            "STDE": f"{ctSTDE:.2f} m/s   ({ctSTDEn:4.1f}%)",
            "RMSE": f"{ctRMSE:.2f} m/s   ({ctRMSEn:4.1f}%)",
            "MAE" : f"{ ctMAE:.2f} m/s   ({ ctMAEn:4.1f}%)",
        },
        "Climate error for Z-scaled TS (empirical)": {
            "BIAS": f"{ceBIAS:.2f} m/s   ({ceBIASn:4.1f}%)",
            "STDE": f"{ceSTDE:.2f} m/s   ({ceSTDEn:4.1f}%)",
            "RMSE": f"{ceRMSE:.2f} m/s   ({ceRMSEn:4.1f}%)",
            "Area": f"{ceAREA:.2f} m/s   ({ceAREAn:4.1f}%)",
        },
        #"Climate error (Weibull)": {
        #    "BIAS": f"{wBIAS:.2f} m/s   ({wBIASn:4.1f}%)",
        #    "STDE": f"{wSTDE:.2f} m/s   ({wSTDEn:4.1f}%)",
        #    "RMSE": f"{wRMSE:.2f} m/s   ({wRMSEn:4.1f}%)",
        #},
        #"Weibull wso fit error": {
        #    "BIAS": f"{ofitBIAS:.2f} m/s   ({ofitBIASn:4.1f}%)",
        #    "STDE": f"{ofitSTDE:.2f} m/s   ({ofitSTDEn:4.1f}%)",
        #    "RMSE": f"{ofitRMSE:.2f} m/s   ({ofitRMSEn:4.1f}%)",
        #},
        #"Weibull wsp fit error": {
        #    "BIAS": f"{pfitBIAS:.2f} m/s   ({pfitBIASn:4.1f}%)",
        #    "STDE": f"{pfitSTDE:.2f} m/s   ({pfitSTDEn:4.1f}%)",
        #    "RMSE": f"{pfitRMSE:.2f} m/s   ({pfitRMSEn:4.1f}%)",
        #},
    }
)
table_txt = tabulate.tabulate(table, headers='keys', tablefmt='plain', colalign=(table.columns.size+1)*["right"])
print(table_txt)
with open(EXAMPLES_DIR / f'experiment_{outlabel}_table.txt', mode='w') as fid:
    fid.write(table_txt + '\n')


plt.close('all')


co = plt.rcParams['axes.prop_cycle'].by_key()['color'][0]
cp = plt.rcParams['axes.prop_cycle'].by_key()['color'][1]
cc = plt.rcParams['axes.prop_cycle'].by_key()['color'][3]
new_co = 'skyblue'    # darken_color(co)
new_cp = 'rosybrown'  # darken_color(cp)
new_cc = 'darkred'  # darken_color(cp)
wso.hist(grid=False, density=True, bins=bins, histtype='step', color=co, label=f'$ws_o$ density from histogram')
wsp.hist(grid=False, density=True, bins=bins, histtype='step', color=cp, label=f'original $ws_p$ density from histogram')
wsc.hist(grid=False, density=True, bins=bins, histtype='step', color=cc, ls='--', label=f'Z-scaled $ws_p$ density from histogram')
x = np.linspace(0, bins.max(), 101)
#plt.plot(x, climerr.weibull_pdf(x, Ao, Ko), lw=1.2, ls=(0, (6, 2)), color=new_co, label=f'$ws_o$ Weibull fit $A$={Ao:.1f} m/s, $K$={Ko:.2f}')
#plt.plot(x, climerr.weibull_pdf(x, Ap, Kp), lw=1.2, ls=(0, (5, 4)), color=new_cp, label=f'$ws_p$ Weibull fit $A$={Ap:.1f} m/s, $K$={Kp:.2f}')
plt.legend(loc='center right', frameon=False, fontsize=10, bbox_to_anchor=(1, .4), borderpad=0, labelspacing=0)
#plt.title(
#      r'$K_{\mathregular{error}}$ = %.1f%%' % ((Kp/Ko-1)*100)
#    + r',  $A_{\mathregular{error}}$ = %.1f%%' % ((Ap/Ao-1)*100)
#)
plt.text(.99, .99,
      f'Time-based error                                            \n'
    + f'   for original $ws_p$: BIAS={ tBIASn:4.1f}%  STDE={ tSTDEn:4.1f}%  RMSE={ tRMSEn:4.1f}%\n'
    + f'   for Z-scaled $ws_p$: BIAS={ctBIASn:4.1f}%  STDE={ctSTDEn:4.1f}%  RMSE={ctRMSEn:4.1f}%\n'
    + f'Climate error (empirical)                                   \n'
    + f'   for original $ws_p$: BIAS={ eBIASn:4.1f}%  STDE={ eSTDEn:4.1f}%  RMSE={ eRMSEn:4.1f}%\n'
    + f'   for Z-scaled $ws_p$: BIAS={ceBIASn:4.1f}%  STDE={ceSTDEn:4.1f}%  RMSE={ceRMSEn:4.1f}%\n',
    ha='right', va='top', transform=plt.gca().transAxes, fontsize='large',
)
plt.ylim([0, 0.18])
plt.xlim([0, 30])
plt.xlabel(r'Wind speed $(\text{m}\,\text{s}^{-1})$', labelpad=0)
plt.ylabel(r'Probability Density $(\text{m}^{-1}\,\text{s})$', labelpad=0)
plt.gcf().tight_layout()
plt.savefig(EXAMPLES_DIR / f'experiment_{outlabel}_hist2.png', dpi=100)
#plt.savefig(EXAMPLES_DIR / f'experiment_{outlabel}_hist2.pdf')
plt.show()



plt.close('all')

fig, ax = plt.subplots(figsize=(4,4))
ax.set_aspect('equal', 'box')
data = [
    [tBIAS, tSTDE, 'Time-dependent error original $ws_p$', dict(marker='D', markersize=8, markerfacecolor="None", markeredgecolor="k", markeredgewidth=2)],
    [ctBIAS, ctSTDE, 'Time-dependent error Z-scaled $ws_p$', dict(marker='s', markersize=9, markerfacecolor="None", markeredgecolor="C3", markeredgewidth=2)],
    [eBIAS, eSTDE, 'Climate error original $ws_p$', dict(marker='x', markerfacecolor="k", markeredgecolor="k", markersize=11, markeredgewidth=3)],
    [ceBIAS, ceSTDE, 'Climate error Z-scaled $ws_p$', dict(marker='+', markerfacecolor="C3", markeredgecolor="C3", markersize=14, markeredgewidth=3)],
]
_ = [ax.plot(abs(x), abs(y), ls='None', label=label, clip_on=False, **kwargs) for x, y, label, kwargs in data]
ax.legend(loc='center', frameon=True, fontsize=10, handleheight=0.3, handletextpad=0.3, labelspacing=0.8, borderpad=0.6)
max_radius = 1.05*max([*ax.get_xlim(), *ax.get_ylim()])
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
plt.savefig(EXAMPLES_DIR / f'experiment_{outlabel}_taylor.png', dpi=100)
#plt.savefig(EXAMPLES_DIR / f'experiment_{outlabel}_taylor.pdf')
plt.show()




