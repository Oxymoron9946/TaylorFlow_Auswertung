# 5 Configuration

All settings are in `config.py` in the project folder. The file is divided
into numbered sections. Plots and appearance (sections 4 and 5 of the file)
are described in chapter 4; this chapter describes the remaining entries.

Values that affect the calculation result are in `PARAMETER`. With their
default values, the reference results in `tests/referenz/` are obtained.
The column **Effect** states how strongly a change affects kLa_log_mean. It
is based on variation runs with the supplied series (5 channels, 55
operating points); “–” means not investigated separately.

## 5.1 Folders and files

| Entry | Default | Meaning |
|---|---|---|
| `ROHDATEN_ORDNER` (raw data folder) | `data/raw` | supplied measurement files; source for `MESSDATEIEN = "alle"` |
| `DIALOG_ORDNER` (dialog folder) | same as `ROHDATEN_ORDNER` | folder in which the selection window starts, e.g. the output folder of the video analysis |
| `ERGEBNIS_ORDNER` (results folder) | `ergebnisse` | outputs; one subfolder per channel |
| `AUSSCHLUSS_DATEI` (exclusion file) | `config/ausschluesse.yaml` | exclusion rules (chapter 2.4) |
| `KALIBRIER_DATENBANK` (calibration database) | `data/calibrated_c_database.json` | Bretherton factors of the circular channels (chapter 10) |
| `MODELL_DATEI` (model file) | `config/eigene_modelle.yaml` | saved own models (chapter 9) |

Paths outside the project folder are given as `Path(r"…")`, e.g.

```python
DIALOG_ORDNER = Path(r"D:\Videoauswertung\output\Output_MassTransfer")
```

## 5.2 Scope of the evaluation

| Entry | Default | Meaning |
|---|---|---|
| `MESSDATEIEN` (measurement files) | `"dialog"` | `"dialog"` = selection window; `"alle"` = all `Auswertung_Masse_*.csv` in `ROHDATEN_ORDNER`; or a list of file paths |
| `NEU_RECHNEN` (recalculate) | `True` | `False`: only redraw the plots from existing results |
| `BETRIEBSPUNKTE` (operating points) | `None` | operating points for the plots per operating point; `None` = all |

## 5.3 Evaluation parameters (`PARAMETER`)

### Camera filter

| Entry | Default | Unit | Meaning |
|---|---|---|---|
| `kamerafilter_rel_se_max_prozent` | 5.0 | % | max. relative standard error of the bubble length per bin |
| `kamerafilter_n_min` | 50 | – | min. number of data points per bin |
| `kamerafilter_cv_max_prozent` | 50.0 | % | max. coefficient of variation per bin |
| `kamerafilter_anteil_min` | 0.75 | – | min. fraction of valid bins for a camera to be kept |
| `kamerafilter_bins_min` | 3 | – | min. number of valid bins per camera |

### Bubble length fit

| Entry | Default | Unit | Meaning | Effect |
|---|---|---|---|---|
| `fit_serien_offsets` | `True` | – | fit camera offsets o_j (camera 1 is the reference) | – |
| `fit_loss` | `"soft_l1"` | – | robust loss function; `"linear"` = classical least squares | – |
| `sigma_sys_m` | 2e-6 | m | systematic measurement error, added in quadrature to the standard error | – |
| `sigma_sem_floor_m` | 1e-6 | m | lower limit of the standard error per bin | – |
| `fit_lambda0_m` | 0.05 | m | start value of the absorption length λ | none (0.01–0.2 m) |
| `offset_bound_anteil` | 0.2 | – | limit \|o_j\| ≤ fraction · mean bubble length | none (limit never reached) |

The camera resolves about 55 µm/px. The two error limits of 1 and 2 µm are
far below this; they only prevent bins with very many bubbles from
dominating the fit.

### Integration

| Entry | Default | Unit | Meaning | Effect |
|---|---|---|---|---|
| `dz_m` | 1e-3 | m | step size for pressure profile and mass balance | small (0.25–2 mm: a few per cent) |
| `u_fit_cap_faktor` | 1.5 | – | fitted velocities above factor · U_ref are discarded and interpolated; U_ref = max(median of the measurement, u_G + u_L) | none (never active) |
| `saettigung_clip` | 0.999 | – | C_L is limited to this fraction of C* | none (0.99–0.999) |

### Measurement uncertainties

| Entry | Default | Meaning |
|---|---|---|
| `u_rel_h_cp` | 0.03 | relative uncertainty of the Henry constant |
| `u_rel_p_co2` | 0.02 | relative uncertainty of the CO2 partial pressure |

Both values determine where the active zone ends (chapter 7.6). The other
three entries of this section (`k_opt_mm_pro_px`, `u_rel_dn_dt`,
`pixel_unsicherheit_px`) belong to the error propagation in
`taylorflow/unsicherheit.py`. This function is available for own
uncertainty analyses and is not called by the evaluation.

### kLa evaluation

| Entry | Default | Meaning | Effect |
|---|---|---|---|
| `max_urel_delta_c` | 0.5 | a grid point belongs to the active zone if ΔC > 0 and the uncertainty of C* is at most this fraction of ΔC | none (0.3–0.7) |
| `logmean_min_aktive_punkte` | 10 | fewer active grid points: kLa_log_mean = 0 | – |

### Pressure drop and property data

| Entry | Default | Meaning |
|---|---|---|
| `c_bretherton_theorie` | 0.465 | Bretherton factor for circular channels without a usable calibration |
| `fluessigkeit` (liquid) | `"Water"` | liquid name for the library `thermo` |

The literature models use fixed property data for water/CO2 at about 25 °C
(chapter 9.2). They are defined in `taylorflow/parameter.py` (`lit_*`) and
can also be set in `PARAMETER` if required.

An unknown name in `PARAMETER` produces a message listing all permitted
names.

## 5.4 Further sections

| Section | Script | Chapter |
|---|---|---|
| `VERGLEICH` (comparison) | `literaturvergleich.py` | 9 |
| `KALIBRIERUNG` (calibration) | `kalibrierung.py` | 10 |
| `MONOLITH` | `monolith.py` | 11 |
