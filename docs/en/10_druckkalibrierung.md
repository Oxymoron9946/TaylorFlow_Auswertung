# 10 Pressure calibration

> **Status:** The procedure is fully included but not yet finally
> validated and is currently not used routinely. The evaluation only reads
> the existing database `data/calibrated_c_database.json`.
> `kalibrierung.py` only changes this file if explicitly set to do so.

## 10.1 Purpose

In the circular channel, the pressure drop is calculated with the
Bretherton model (chapter 7.4). It contains a factor c with the theoretical
value 0.465. With this value the calculated pressure profile does not fit
all channels, and no other published model fits better (chapter 8.2). c is
therefore determined per channel from measurements without CO2; there the
bubble length changes only because of the pressure.

Square channels (Kurimoto model) are not calibrated.

## 10.2 Procedure

For each operating point of a file `Auswertung_Druck_…_0molCO2_….csv`:

1. **Fits:** bubble length (weighted), slug length and velocity linearly
   over z.
2. **Real pressure drop** from the bubble expansion (ideal gas, volume
   proportional to length):

   $$p_{tr,in} = p_{tr,out}\,\frac{L_B(z_{end})}{L_B(0)}, \qquad \Delta p_{real} = p_{tr,in} + p_v - p_{out}$$

3. **Splitting the model:** the Bretherton model is linear in c:
   - $\mathrm{d}p/\mathrm{d}z = \text{base} + c \cdot \text{extra}$
   - base = model with c = 0
   - extra = model(c = 1) − model(c = 0)
   - Both parts are integrated over the channel.
4. **Result:**
   $c = (\Delta p_{real} - \Delta p_{base}) / \Delta p_{extra}$

Over all operating points, three **fallback models** for c(u_G, u_L) are
fitted:

| Model | Form |
|---|---|
| Linear | $a\,u_G + b\,u_L + c_0$ |
| Polynomial | $a\,u_G + b\,u_L + c_1\,u_G u_L + c_0$ |
| Power-Law | $a\,u_G^{b}\,u_L^{c_1}$ |

For each model, R² and AIC (smaller = better; penalises additional
parameters) are reported.

## 10.3 Use in the evaluation

For a circular channel, the entry with the calibration key is looked up,
e.g. `PVC_circular_1000um_600um` (chapter 2.2). Then:

| Situation | c used |
|---|---|
| within the calibrated operating points | linear interpolation |
| outside | stored fallback model (`fallback_model`) |
| no entry, `"USE": false` or fewer than 4 points | theoretical value 0.465 (message in the console) |

The result is at least 0.001.

**Content of the database:**

| Key | Points | c | Fallback model | used |
|---|---|---|---|---|
| `PVC_circular_1000um_600um` | 5 | 0.31–1.33 | Power-Law (R² 0.91) | yes |
| `PVC_circular_1000um_800um` | 8 | 0.05–0.70 | Polynomial (R² 0.58) | yes |
| `PVC_circular_1500um_1150um` | 8 | −7.6 to +16 | Polynomial | no (`USE: false`) |
| `Glas_rectangular_1000um_600um` | 8 | – | – | no; square, Kurimoto |
| PTFE | – | – | – | no entry, c = 0.465 |

An entry can be switched off by hand:

```json
"PVC_circular_1500um_1150um": {
    "USE": false,
    "NOTE": "c_calib zwischen -7.6 und +16, vermutlich Messfehler",
    ...
}
```

## 10.4 New calibration

1. Evaluate the pressure measurement with the video analysis; the file
   `Auswertung_Druck_….csv` is written to `output/Output_PressureCalibration/`.
   Material, shape, D and needle must match the mass transfer measurement.
2. In `config.py`, section `KALIBRIERUNG`:

   | Entry | Default | Meaning |
   |---|---|---|
   | `messdateien` (files) | `"dialog"` | `"dialog"` = selection window, `"alle"` = all `Auswertung_Druck_*.csv` in `ROHDATEN_ORDNER`, or a list of paths |
   | `dialog_ordner` | `ROHDATEN_ORDNER` | start folder of the selection window, e.g. `Output_PressureCalibration` of the video analysis |
   | `ersatzmodell` (fallback model) | `"auto"` | `"auto"` (largest R²) or `"Linear"`, `"Polynomial"`, `"Power-Law"` |
   | `datenbank_schreiben` (write database) | `False` | leave at `False` first |

3. Run `python kalibrierung.py` and select the file(s).
4. Check the results in `ergebnisse/kalibrierung/`:
   - `<key>_c_werte.csv`: c per operating point
   - `<key>_c_flaeche.png`: c over u_G and u_L

   Plausible values are of the order of the theoretical value (0.1–2).
   Negative or strongly scattering values indicate a problem in the
   pressure measurement or the fits.
5. Only then set `datenbank_schreiben = True` and run again. Existing fields
   `USE` and `NOTE` are kept. Then run `auswertung.py` again for the
   channel.

A new calibration of the supplied pressure data reproduces the stored c
values to about 10⁻⁴ and selects the same fallback models.

## 10.5 Open questions

- **Assumption volume proportional to length:** caps are neglected, the
  film thickness is taken as constant. For short bubbles the assumption is
  rough.
- **Fitting with few points:** five to eight points per channel are few for
  fitting three to four parameters. `auto` selects by R² and thus favours
  the polynomial; by AIC the linear model would be chosen for PVC 1000/800.
  For operating points within the calibrated points this does not matter
  (interpolation).
- **PVC 1500/1150:** the strongly scattering c values are not explained.
- **Measurement deviation of the bubble length:** it enters the calibration
  only via the standard deviation, not via the standard error and
  systematic part as in the bubble length fit of the mass transfer
  measurement.
