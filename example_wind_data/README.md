# Example datasets with wind measurements and predictions

This folder contains curated datasets with wind measurements
and weather predictions, derived from publicly available sources.
The files containing the datasets are:

- [Measurements dataset at La Ventosa site][La Ventosa dataset (2021)]: [`wind_data_ventosa_32m.csv.gz`](./wind_data_ventosa_32m.csv.gz).
- [Measurements dataset at Capel-Cynon][Capel-Cynon dataset (2021)]: [`wind_data_capel_m1_50m.csv.gz`](./wind_data_capel_m1_50m.csv.gz).
- [NEWA weather predictions][NEWA Application]: [`newa_mesots_capel_cynon.nc`](./newa_mesots_capel_cynon.nc)

It also contains Python scripts (see [LICENSE](../LICENSE) for details) that were used to process the original datasets
and fetch the prediction data from the [NEWA Application]:

- [`get_data_ventosa.py`](./get_data_ventosa.py) was used to generate file [`wind_data_ventosa_32m.csv.gz`](./wind_data_ventosa_32m.csv.gz) from the original data.
- [`get_data_capel.py`](./get_data_capel.py) was used to generate file [`wind_data_capel_m1_50m.csv.gz`](./wind_data_capel_m1_50m.csv.gz) from the original data.
- [`get_capel_meso_ts.py`](./get_capel_meso_ts.py) was used to fetch the weather predictions in [`newa_mesots_capel_cynon.nc`](./newa_mesots_capel_cynon.nc) from the [NEWA API][NEWA Application].

For **Attribution & licensing** please refer to
[`ATTRIBUTION.md`](../ATTRIBUTION.md) for per-source details.


## References
<!-- Section anchor to link to this block as a whole -->
<a id="references"></a>

1. <a id="ref-ventosa"></a> Hansen KS, Vasiljevic N, Sørensen SA (2021). *Resource data from the La Ventosa mast*. DTU Data. [doi:10.11583/DTU.14135609][Ventosa DOI]
2. <a id="ref-capel"></a> Hansen KS, Vasiljevic N, Sørensen SA (2021). *Resource data from the Capel Cynon masts*. DTU Data. [doi:10.11583/DTU.14135627][Capel DOI]
3. <a id="ref-newa"></a> New European Wind Atlas (NEWA) — About/Terms & data access. [Link][NEWA About].


<!-- Reusable in-text shortcuts to the items above -->
[La Ventosa dataset (2021)]: #ref-ventosa
[Capel-Cynon dataset (2021)]: #ref-capel
[NEWA Application]: #ref-newa

<!-- Direct external links (DOIs / sites) -->
[Ventosa DOI]: https://doi.org/10.11583/DTU.14135609
[Capel DOI]: https://doi.org/10.11583/DTU.14135627
[NEWA About]: https://map.neweuropeanwindatlas.eu/about

