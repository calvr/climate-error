<!-- vim: set fileencoding=utf-8 fileformat=unix : -->
<!-- vim: set spell spelllang=en,pt : -->
<!-- -*- coding: utf-8 -*- -->
<!-- vim: set ts=8 et sw=4 sts=4 sta : -->

# ATTRIBUTION

This repository contains **derived datasets** produced from publicly available sources.
Unless otherwise noted below:


- **Data** are provided under **Creative Commons Attribution 4.0 International (CC BY 4.0)**
  as required by each original source; **attribution and indication of changes** are provided
  in the sections below. CC BY 4.0 allows sharing and adapting the material for any purpose,
  provided you give appropriate credit, link to the license, and indicate changes; you may not
  add legal terms or technological measures that legally restrict others from doing anything
  the license permits. [2](https://help.emd.dk/mediawiki/index.php/GASP_Global)

- **Code** in this repository is licensed separately (see `LICENSE`) and **does not change the
  licenses of the data**.

- **DTU Data** requests that citations **display the item DOI as a full URL**; we follow this
  practice below. [1](https://wasp.dtu.dk/wind-atlases/global-wind-atlas)

---


## 1) La Ventosa (DTU Data)

**Title**: *Resource data from the Ventosa mast*  
**Authors**: Kurt Schaldemose Hansen; Nikola Vasiljevic; Steen Arne Sørensen  
**Source (DOI)**: https://doi.org/10.11583/DTU.14135609  
**License**: **CC BY 4.0** — https://creativecommons.org/licenses/by/4.0/
(license indicated on the dataset page) [3](https://figshare.com/articles/dataset/Resource_wind_data_and_turbulence_array_measurements_from_4_ECN_mast/18319037/1)

**Files derived in this repository**  
- `wind_data_ventosa_32m.csv.gz`

**Changes made (for attribution)**  
- Converted original **NetCDF** to **CSV (gzip)**.  
- Selected variables: `ws32`, `TI_ws32`, `wd32`; applied **QC filter** (kept rows where `ws32_qc <= 1` and `wd32_qc <= 1`).  
- Applied **physical sanity filters**: wind speed `(0, 99) m/s`, wind direction `[0, 360) deg`, turbulence intensity `> 0`.  
- Dropped invalid rows and **sorted by time index**.  
- No endorsement by DTU or the authors is implied.  
  (CC BY 4.0 allows redistribution/adaptation with attribution and indication of changes.) [2](https://help.emd.dk/mediawiki/index.php/GASP_Global)

---


## 2) Capel Cynon (DTU Data)

**Title**: *Resource data from the Capel Cynon masts*  
**Authors**: Kurt Schaldemose Hansen; Nikola Vasiljevic; Steen Arne Sørensen  
**Source (DOI)**: https://doi.org/10.11583/DTU.14135627  
**License**: **CC BY 4.0** — (as indicated for this item; verify on the dataset landing page when downloading).
Public mirrors list this dataset under CC BY 4.0. [4](https://crosslinkstudies.com/hesk/knowledgebase.php?article=45)

**Files derived in this repository**  
- `wind_data_capel_m1_50m.csv.gz`

**Changes made (for attribution)**
- Converted original **NetCDF** to **CSV (gzip)**.  
- Selected variables: `ws50_m1`, `wd40_m1` *(if a `wd50_m1` channel is present in the NetCDF, use that instead—variable names may vary per version)*; applied **QC filter** (kept rows where `*_qc <= 1`).  
- Applied **physical sanity filters**: wind speed `(0, 99) m/s`, wind direction `[0, 360) deg`, turbulence intensity `> 0` (if present).  
- Dropped invalid rows and **sorted by time index**.  
- No endorsement by DTU or the authors is implied.  
  (CC BY 4.0 allows redistribution/adaptation with attribution and indication of changes.) [2](https://help.emd.dk/mediawiki/index.php/GASP_Global)

---


## 3) NEWA — Mesoscale Time Series (API)

**Title**: New European Wind Atlas (NEWA) — Mesoscale time series via API  
**About / Terms of Use**: https://map.neweuropeanwindatlas.eu/about  
**API landing**: https://map.neweuropeanwindatlas.eu/api/  
**License**: The Works are licensed under **CC BY 4.0**, except where otherwise stated. The Terms include a **required attribution string** and prohibit implying endorsement. [5](https://library.osu.edu/sites/default/files/2021-12/how_to_attribute_a_creative_commons_licensed_work-2017.pdf)  

**Required attribution string (from NEWA Terms)**  
> “Data obtained from the **New European Wind Atlas**, a free, web‑based application developed, owned and operated by the NEWA Consortium. For additional information see **www.neweuropeanwindatlas.eu**.” [5](https://library.osu.edu/sites/default/files/2021-12/how_to_attribute_a_creative_commons_licensed_work-2017.pdf)

**Files derived in this repository**  
- `newa_mesots_capel_cynon.nc`

**Changes made (for attribution)**  
- Programmatically requested a **single‑point** mesoscale time series from the NEWA API (Capel Cynon area).  
- Location: **lon = −4.354217, lat = 52.138872**; **heights** requested: `[50, 100]`.  
- Time period: **1990‑01‑01T00:00:00** to **1996‑01‑01T00:00:00** (within the NEWA mesoscale coverage window).  
- Variables requested included: `HGT, WS10, WD10, T2, Q2, RHO, PSFC, ZNT, UST, RMOL, PBLH, WS, WD, TKE, T, QVAPOR`.  
- Saved the result as **NetCDF** (`newa_mesots_capel_cynon.nc`).  
- No endorsement by the NEWA Consortium is implied.  
  (NEWA About/Terms describe coverage and CC BY 4.0 licensing with an explicit attribution requirement.) [5](https://library.osu.edu/sites/default/files/2021-12/how_to_attribute_a_creative_commons_licensed_work-2017.pdf)

---


## How to cite these sources

When reusing the data in publications or derivative works, please cite the **original sources**
in addition to this repository:

- **La Ventosa**: Hansen, K.S.; Vasiljevic, N.; Sørensen, S.A. (2021).
  *Resource data from the Ventosa mast*. **DTU Data**. https://doi.org/10.11583/DTU.14135609 (**CC BY 4.0**, as indicated).
  [3](https://figshare.com/articles/dataset/Resource_wind_data_and_turbulence_array_measurements_from_4_ECN_mast/18319037/1)

- **Capel Cynon**: Hansen, K.S.; Vasiljevic, N.; Sørensen, S.A. (2021).
  *Resource data from the Capel Cynon masts*. **DTU Data**. https://doi.org/10.11583/DTU.14135627 (**CC BY 4.0**, as indicated).
  [4](https://crosslinkstudies.com/hesk/knowledgebase.php?article=45)

- **NEWA**: *New European Wind Atlas* (NEWA). About/Terms: https://map.neweuropeanwindatlas.eu/about (**CC BY 4.0** and **required attribution string** shown above).
  [5](https://library.osu.edu/sites/default/files/2021-12/how_to_attribute_a_creative_commons_licensed_work-2017.pdf)

> DTU Data Terms of Use remind users to give proper credit and show the DOI as a complete URL in citations. [1](https://wasp.dtu.dk/wind-atlases/global-wind-atlas)

---


## Notes on licensing and reuse

- **CC BY 4.0** permits redistribution/adaptation in any medium or format (e.g., NetCDF → CSV),
  with **attribution**, **link to the license**, and an **indication of changes**, and forbids
  adding legal/technical restrictions that would limit the rights granted by the license.
  [2](https://help.emd.dk/mediawiki/index.php/GASP_Global)

- If you further modify these derived files, please retain the **original attributions** above,
  add your **own attribution** and **description of changes**, and avoid implying endorsement by
  the original data providers. (NEWA Terms explicitly forbid implying endorsement.)
  [5](https://library.osu.edu/sites/default/files/2021-12/how_to_attribute_a_creative_commons_licensed_work-2017.pdf)

