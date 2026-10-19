# 12 Program structure and extension

## 12.1 Structure

```
config.py              all settings
auswertung.py          evaluation and plots
abbildung.py           single figure
literaturvergleich.py  model comparison
kalibrierung.py        pressure calibration
monolith.py            monolith
taylorflow/
  parameter.py         numbers of the evaluation (dataclass AuswerteParameter)
  einlesen.py          file selection, file names, data, exclusions, camera filter
  pipeline.py          evaluation per channel and operating point (steps 1–8, chapter 6.1)
  fits.py              bubble model with camera offsets, linear fits
  druckverlust.py      Bretherton, Kurimoto, calibration database
  hydrodynamik.py      capillary number, film thickness
  geometrie.py         bubble volume and cross-section
  stoffdaten.py        thermo interface, Henry, vapour pressure, diffusion
  kla.py               active zone, kLa_log_mean
  unsicherheit.py      error propagation (not called by the evaluation)
  literatur.py         literature models and registry
  modellvergleich.py   predictions, power-law fit, statistics, own models
  ergebnisse.py        saving and loading the result files
  protokoll.py         warning log
  monolith.py          gas balance of the monolith
  kalibrierung.py      pressure calibration
  plots/
    stil.py            PlotStil, German/English texts, saving
    optionen.py        options per plot: defaults, checks, calls
    profile.py         plots per operating point
    flaechen.py        3D surfaces
    heatmaps.py        key figure overview
    paritaet.py        parity plots
tests/                 tests and reference results
docs/                  manual (Markdown), figures, PDF generation
```

**Dependencies:** the scripts in the project folder read `config.py` and
call the package `taylorflow`. The package itself does not know
`config.py`; all settings are passed as arguments. The functions can
therefore also be used individually.

## 12.2 Tests

```bat
python -m pytest
```

| File | Checks |
|---|---|
| `tests/test_regression.py` | evaluates all supplied measurement files and compares every number of the operating point tables and an extract of the profiles exactly with `tests/referenz/` |
| `tests/test_bausteine.py` | single parts with synthetic data: file names, fit, active zone, kLa_log_mean, uncertainty, model registry, power law |
| `tests/test_dateiauswahl.py` | selection of measurement files (list, “alle”, selection window), files of the video analysis |
| `tests/test_plots.py` | plot options in `config.py` and `abbildung.py` for every plot |

After every code change, the regression test shows whether results have
changed.

**If a change alters the results on purpose** (new model, correction):

1. Quantify the effect:

   ```bat
   python tests/referenz_erneuern.py
   ```

   lists every differing column with the largest relative deviation.
2. Rewrite the reference:

   ```bat
   python tests/referenz_erneuern.py --schreiben
   ```

3. Increase `__version__` in `taylorflow/__init__.py`; the version is
   stored in every `<channel>_meta.json`.

## 12.3 Typical extensions

### New literature model

In `taylorflow/literatur.py`:

```python
def mein_modell(u_B, L_B, L_S, d_h, D):
    """Author (year), journal. Valid for …"""
    return 2.0 * np.sqrt(D * u_B / (L_B + L_S)) / d_h

LITERATURMODELLE["mein_modell"] = Literaturmodell(
    "mein_modell", "Author 2027", "kLa_lit_mein_modell_1_s",
    lambda x: mein_modell(*_e(x, "u_B", "L_B", "L_S", "d_h", "D")))
```

The available inputs are listed in `modelleingaben()`. New quantities are
added there and in the calls in `pipeline.py` and
`modellvergleich.vorhersage`. The new column changes the operating point
table; rewrite the reference afterwards (12.2).

### New plot

1. Create a function in a module under `taylorflow/plots/`. It receives the
   data, a `PlotStil`, a title and its options as keyword arguments and
   returns a figure. Building blocks:
   - `neue_figur(stil, groesse_cm)`
   - `t(schluessel, stil)` for labels; enter new texts in `TEXTE`, in
     German and English
   - `formatiere_achsen(ax, stil)`
2. In `taylorflow/plots/optionen.py`:
   - an entry in `STANDARD` with all options and defaults
   - a branch in `erzeuge` that calls the function and sets the file name
3. Create a block with the same entries as in `STANDARD` in `config.PLOTS`.
   The test `test_config_zeigt_alle_optionen_mit_standardwerten` checks that
   both match.

The plot is then available in `auswertung.py` and `abbildung.py`.

### New option for an existing plot

Add a parameter with a default value to the plot function, and enter the
same name with the same default in `STANDARD` (`optionen.py`) and in the
block in `config.PLOTS`.

### Other liquid or gas

- **Liquid:** set `fluessigkeit` in `config.PARAMETER` (name for thermo,
  e.g. `"ethanol"`).
- **Henry constant:** for liquids other than water, extend
  `stoffdaten.henry`; currently an error message is raised.
- **Diffusion coefficient:** `stoffdaten.diffusion_co2_wasser` only applies
  to CO2/water. It is used only for the literature models and the column
  `D_CO2_m2_s`.
- **Gas:** enter new gases in `HENRY_DATEN`.

### New evaluation parameter

1. Add a field with a default value in `AuswerteParameter` (`parameter.py`).
2. Use it in the calculation via `p.<name>`.
3. List it in `config.PARAMETER` and document it in chapter 5.

## 12.4 Building the manual

The manual consists of the Markdown files in `docs/` (German) and
`docs/en/` (English). Figures and PDF are created with two scripts:

```bat
python docs/bilder_erzeugen.py          figures from the supplied data (German labels)
python docs/bilder_erzeugen.py en       the same with English labels
python docs/build_pdf.py                docs/Handbuch_TaylorFlow.pdf
python docs/build_pdf.py en             docs/Handbuch_TaylorFlow_en.pdf
```

The PDF additionally requires `pip install pypandoc_binary` and a LaTeX
installation with XeLaTeX (TeX Live or MiKTeX).
