# 2 Measurement data

## 2.1 Origin

The input data are the result files of the video analysis (see its manual,
chapter 4). There is one file per channel and type of measurement; each row
is one position bin of one camera position at one operating point:

```
Videoauswertung\output\
  Output_MassTransfer\
    Auswertung_Masse_PVC_R_1000um_72cm_20molCO2_600um.csv     →  auswertung.py
  Output_PressureCalibration\
    Auswertung_Druck_PVC_R_1000um_72cm_0molCO2_600um.csv      →  kalibrierung.py
```

The video analysis already writes file names and columns in the required
format. The files are used unchanged and selected in the file selection
window at start-up (chapter 3).

## 2.2 File names

All information on the experimental set-up is taken **only from the file
name**; columns of the same name inside the file (Material, Kanal_um, …)
are not used.

```
Auswertung_<Messart>_<Material>_<Form>_<D>um_<L>cm_<X>mol<Gas>_<Nadel>um.csv
```

| Field | Meaning | Example |
|---|---|---|
| Messart | `Masse` = mass transfer measurement, `Druck` = measurement without CO2 for the pressure calibration | `Masse` |
| Material | channel material, free text (letters and digits) | `PVC`, `Glas`, `PTFE` |
| Form | `R` or `Rund` = circular channel; `Q` or `Eckig` = square channel | `R` |
| D | channel diameter or side length [µm] | `1000` |
| L | reactor length [cm]; sets the length of the calculation grid | `72` |
| X | CO2 fraction in the inlet gas [mol-%] | `20` |
| Gas | gas name; Henry constants are available for CO2, O2, N2 and air | `CO2` |
| Nadel | inner diameter of the gas inlet needle [µm] | `600` |

The file name defines the **channel name**. Results, plots and exclusion
rules are stored under this name:

```
File:          Auswertung_Masse_PVC_R_1000um_72cm_20molCO2_600um.csv
Channel name:  PVC_Rund_1000um_72cm_20molCO2_600um
```

Two series with the same channel name overwrite each other. A repeated
measurement on the same set-up therefore gets its own material code, e.g.
`PVC2`.

The pressure calibration uses a shorter **calibration key** without length
and CO2 fraction, e.g. `PVC_circular_1000um_600um`. A pressure measurement
thus applies to all mass transfer measurements on the same channel with the
same needle.

## 2.3 File content

Format: semicolon as separator, decimal point or decimal comma, UTF-8
encoding.

**Required columns**

| Column | Unit | Meaning |
|---|---|---|
| `GasVelocity` | m/s | superficial gas velocity u_G (set point) |
| `LiquidVelocity` | m/s | superficial liquid velocity u_L |
| `CameraPosition` | – | number of the camera position (1 = at the inlet) |
| `BinCenter_mm` | mm | position of the bin in the channel, measured from the inlet |
| `mean_BubbleLength_mm` | mm | mean bubble length in the bin |
| `mean_UnitCellLength_mm` | mm | mean length of the unit cell (bubble + slug) |
| `mean_Speed_m_s` | m/s | mean bubble velocity |
| `Temperatur_C` | °C | temperature (averaged per operating point) |
| `Druck_Pa_Auslass` | Pa | absolute pressure at the outlet |

**Also used, if present**

| Column | Use |
|---|---|
| `std_BubbleLength_mm` | measurement uncertainty in the bubble length fit and in the camera filter |
| `GroupCount` or `numel_BubbleLength_mm` | number of data points in the bin; for the standard error and the camera filter |

Without the number per bin, the camera filter (2.5) is skipped and the fit
weights with the standard deviation instead of the standard error.

**Several recordings or sensitivities.** If a file contains several rows
for the same camera and the same bin, e.g. from several recordings or a
sensitivity sweep of the video analysis, the row with the **smallest bubble
length** is used per camera and bin. For a traceable evaluation, a file
should contain only one sensitivity per operating point.

## 2.4 Exclusion rules

Data points or whole operating points that are not to be evaluated are
listed in `config/ausschluesse.yaml`, grouped by channel name. Each rule
states its reason (`grund`). There are three kinds:

```yaml
PVC_Rund_1000um_72cm_20molCO2_800um:
  messpunkte_entfernen:          # remove rows of the file before the evaluation
    - GasVelocity: 0.134
      LiquidVelocity: 0.25
      grund: Absorption vor dem ersten Messpunkt abgeschlossen
    - GasVelocity: 0.07
      LiquidVelocity: 0.111
      CameraPosition: 3          # only camera 3 of this operating point
      grund: Kamera 3 unscharf
  betriebspunkte_ueberspringen:  # operating point does not appear in any result file
    - LiquidVelocity: 0.056      # all operating points with u_L = 0.056 m/s
      grund: Pumpe instabil
  kla_ungueltig:                 # evaluated, but kLa_log_mean stays empty
    Gas_0_07_Liq_0_111: "Absorption kaum auswertbar"
```

| Kind | Fields | Effect |
|---|---|---|
| `messpunkte_entfernen` (remove data points) | `GasVelocity`, `LiquidVelocity`, `CameraPosition`, `BinCenter_mm` (tolerance 0.1 mm); all given fields must match | rows are removed before the evaluation |
| `betriebspunkte_ueberspringen` (skip operating points) | `GasVelocity` and/or `LiquidVelocity`; a missing field means “all values” | operating point is not evaluated |
| `kla_ungueltig` (kLa invalid) | name of the operating point as in column `Config` | kLa_log_mean empty, `manual_exclude = True` with reason; profiles and bubble length fit remain available, 3D surfaces and model comparisons omit the point |

The supplied file contains the exclusions of the supplied series with their
reasons. After a change, run `auswertung.py` again.

## 2.5 Automatic camera filter

Before the evaluation, unreliable camera positions are removed (only for
`Masse` files). A bin is valid if all three conditions are met:

- relative standard error of the bubble length ≤ 5 %
- at least 50 data points in the bin
- coefficient of variation ≤ 50 %

A camera of an operating point is kept if at least 75 % of its bins and at
least 3 bins are valid. Operating points with only one remaining camera are
dropped. The console reports how many bins and cameras were rejected. The
limits are in `config.PARAMETER` (`kamerafilter_*`, chapter 5).

## 2.6 Evaluating a new series

1. Run the batch for the measurement folder in the video analysis. The file
   `Auswertung_Masse_….csv` is written to `output/Output_MassTransfer/`.
2. Start `python auswertung.py` and select the file in the selection window.
3. Check the results (chapter 3.4): warning log, bubble length fits,
   overview of key figures.
4. Enter unusable data points or operating points in
   `config/ausschluesse.yaml` (2.4) and evaluate again.
5. **Circular channel:** without an entry in the calibration database, the
   pressure model uses the theoretical value c = 0.465; the console then
   reports “nicht kalibriert” (not calibrated). The channel can be
   calibrated with a pressure measurement (chapter 10). **Square channel:**
   no calibration needed.

**Other dimensions** (diameter, length, CO2 fraction): nothing else needs to
be adjusted; everything comes from the file name.

**Liquids other than water** and **rectangular, non-square channels** are
not supported (chapters 8 and 12).
