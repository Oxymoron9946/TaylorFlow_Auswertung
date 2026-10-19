# 6 Results

## 6.1 Course of the evaluation

For each selected measurement file, `auswertung.py` performs these steps
(code: `taylorflow/pipeline.py`, equations: chapter 7):

```
measurement file ──► reading, exclusions, camera filter            (einlesen.py)
   │
   └─► per operating point (u_G, u_L):
         1  data points: one value per camera and bin
         2  property data at T and p at the outlet (thermo, Henry, vapour pressure)
         3  fits over z: bubble length (with camera offsets), slug length, velocity
         4  pressure profile: backward integration from the outlet (Bretherton or Kurimoto)
         5  mass balance: bubble volume → absorbed amount → C_L, C*, saturation
         6  active zone and kLa_log_mean
         7  bubble length converted to inlet pressure
         8  literature models
   │
   └─► saving: profiles, operating point table, metadata           (ergebnisse.py)
Then: plots according to config.PLOTS                              (taylorflow/plots/)
```

## 6.2 Result files

For each channel, `ergebnisse/<channel>/` is created with:

| File | Content |
|---|---|
| `<channel>_betriebspunkte.csv` | one row per operating point: key figures, fit quality, literature models |
| `<channel>_profile.csv` | one row per grid point (1 mm) and operating point |
| `<channel>_meta.json` | program version, time, source file |
| `plots/` | plots according to `config.PLOTS` (chapter 4) |

Format: semicolon, decimal comma, UTF-8; the files can be opened directly
in Excel. In Python they are read with
`taylorflow.ergebnisse.lade_betriebspunkte(folder, channel)` or
`lade_profile(folder, channel)`; these functions read numbers without
rounding errors. An existing file of the same name is overwritten.

**Operating point table** (`…_betriebspunkte.csv`)

| Column | Unit | Meaning |
|---|---|---|
| `Config` | – | name of the operating point, e.g. `Gas_0_134_Liq_0_056` |
| `GasVelocity_m_s`, `LiquidVelocity_m_s` | m/s | superficial velocities u_G, u_L |
| **`kLa_log_mean_1_s`** | 1/s | **main result:** log-mean volumetric mass transfer coefficient over the active zone (chapter 7.6); 0 if the active zone is too short, empty for `kla_ungueltig` |
| `BubbleLength_mean_m`, `BubbleLength_start_m` | m | fitted bubble length, mean over the channel and at the inlet |
| `BubbleLength_meas_mean_m` | m | mean of the measured bubble lengths |
| `SlugLength_mean_m` | m | fitted slug length, mean over the channel |
| `Velocity_mean_m_s` | m/s | fitted bubble velocity, mean; input of the literature models |
| `Velocity_meas_mean_m_s` | m/s | mean of the measured velocities |
| `slip_meas_over_theo` | – | median measured velocity / (u_G + u_L); usually 1.05–1.30 |
| `n_spez_mol_s_m3` | mol/(s·m³) | volume-specific molar flux of CO2 over the whole channel (chapter 7.7) |
| `fit_model` | – | bubble model used; normally `Exp+Expansion v2+Offsets …` |
| `fit_r2`, `fit_chi2_red` | – | quality of the bubble fit; χ²_red ≈ 1 ideal, > 3 conspicuous, > 10 critical |
| `fit_corr_max` | – | largest correlation of two fit parameters; > 0.95 = poorly determined |
| `fit_n_bound_hits`, `fit_bound_hits` | – | parameters at a fit limit (number, description) |
| `fit_n_series`, `fit_n_offsets` | – | number of cameras and of fitted offsets |
| `fit_offset_o2_mm`, `fit_offset_o3_mm` | mm | camera offsets relative to camera 1 |
| `kLa_lit_*_1_s` | 1/s | predictions of the literature models (chapter 9) |
| `d_h_m`, `Geometrie` | m, – | channel diameter or side length; `rund` (circular) or `eckig` (square) |
| `D_CO2_m2_s` | m²/s | diffusion coefficient of CO2 in water at T |
| `T_sys_K`, `P_aus_Pa` | K, Pa | temperature and outlet pressure (mean of the operating point) |
| `manual_exclude`, `manual_exclude_reason` | – | `True` and reason for an entry under `kla_ungueltig` |

**Profile table** (`…_profile.csv`)

| Column | Unit | Meaning |
|---|---|---|
| `Config_Name` | – | operating point |
| `Position_z_m` | m | position in the channel (grid with `dz_m`) |
| `L_bubble_fit_m` | m | fitted bubble length (without camera offsets) |
| `L_bubble_corrected_m` | m | bubble length converted to the inlet pressure; shows only the absorption |
| `L_slug_fit_m`, `U_fit_m_s` | m, m/s | fitted slug length and bubble velocity |
| `Pressure_Pa` | Pa | calculated absolute pressure |
| `Diffused_Gas_mol` | mol | amount of CO2 absorbed per bubble up to z (monotonic) |
| `C_L_bulk_mol_m3` | mol/m³ | CO2 concentration in the liquid |
| `C_star_lokal_mol_m3` | mol/m³ | equilibrium concentration C* = H · p_CO2 |
| `Saturation_percent` | % | saturation C_L / C* |
| `C_star_lokal_raw_mol_m3`, `Saturation_percent_raw` | mol/m³, % | the same quantities before the monotonicity and saturation limits |
| `aktive_zone` | – | 1 = grid point in the active zone (chapter 7.6), 0 = not |
| `fit_offset_o1_m` … `o3_m` | m | camera offsets (constant per operating point) |
| `cam1_z_min_m` … `cam3_z_max_m` | m | range of the data points per camera |
| `z_meas_m`, `L_b_meas_m` | m | data points (only in the first rows, empty otherwise) |

## 6.3 Console output

For each operating point the console reports:

- the bubble model with R² and χ²_red
- the camera offsets
- for circular channels, the Bretherton factor c used
- inlet and outlet pressure
- kLa_log_mean and the number of grid points in the active zone

## 6.4 Warning log

`ergebnisse/Modell_Gueltigkeitswarnungen.txt` is rewritten in every run. It
collects, separated by channel and operating point:

| Message | Meaning | Action |
|---|---|---|
| `Liu (2005): … außerhalb` | operating point outside the range of the slip correlation | usually none, note only |
| `Bretherton (1961): Ca_L … > 0.005` | capillary number above the validity range of the Bretherton pressure model | treat the pressure profile with caution |
| `Kurimoto: …` | Ca, We, Re or L_B/d outside the Kurimoto range | treat the pressure profile with caution |
| `Filmdicke Modell: …` | film thickness outside the model range, approximation used | check the operating point |
| `Blasen-Fit: chi2_red = … -> ERHEBLICH` or `KRITISCH` | the fit describes the measurement poorly | look at the bubble length fit (chapter 4.2) |
| `Blasen-Fit: Parameter hoch korreliert` | A and λ (or B) cannot be determined independently | check the kLa of the point critically |
| `Serien-Offset … nahe/am Bound` | cameras strongly offset against each other | check the camera calibration |
| `Serien-Offset … > 50% des Absorptionssignals` | the offset may take up part of the absorption | check the plot, exclude the camera if necessary |
| `Slip U_meas/U_TP > 1.5` | measured velocity implausibly high | check the set points of the flow controllers |
| `kla_ungueltig aktiv: …` | entry from `ausschluesse.yaml` applied | – |
| `kla_ungueltig: Betriebspunkt '…' nicht gefunden` | name in `ausschluesse.yaml` matches no operating point | check the spelling (column `Config`) |
