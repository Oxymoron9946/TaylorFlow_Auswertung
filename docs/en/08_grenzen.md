# 8 Limitations

## 8.1 Validity ranges of the models

| Model | Range | Behaviour outside |
|---|---|---|
| Bretherton pressure drop (circular) | Ca ≤ 0.005 | warning in the log, calculation continues |
| Kurimoto pressure drop (square) | 0.00159 ≤ Ca ≤ 0.0989; 0.0817 ≤ We ≤ 25.4; 8.33 ≤ Re ≤ 791; L_B/d ≥ approx. 2.3 | warning, calculation continues |
| film thickness circular | Ca ≤ 1.5 | approximation δ = 0.05 d with warning |
| slip Liu (2005) | 0.008–0.7 m/s (gas), 0.008–0.5 m/s (liquid), d 0.9–3 mm | warning (note only, not used in the calculation) |
| Henry constant | CO2, O2, N2, air in water | stop with message |
| CO2 diffusion | water | – |
| literature models | see chapter 9.2; the supplied channels lie outside the original range of almost all models | – |

In the supplied glass channel, some operating points at low u_G fall
slightly below the Kurimoto criterion L_B/d.

## 8.2 Known limitations

1. **Isothermal, property data at the outlet:**
   - T and p at the outlet apply to the whole channel.
   - For temperature changes of more than approx. 5 K along the channel, a
     section-wise evaluation would be needed.
2. **Constant liquid volume:**
   - V_L is determined at the inlet.
   - Changes of the slug length along z do not enter C_L.
3. **Caps and corners in the square channel:**
   - The liquid in the corners is added to the liquid volume (as half the
     cap volume) only in the circular channel.
   - The caps are approximated as half-ellipsoids in both geometries.
   - A cube instead of an ellipsoid approximation of the caps changes
     single kLa values in the glass channel by up to 26 % (median 1.8 %).
4. **Pressure model of the circular channels:**
   - No published pressure model (Bretherton, Kreutzer 2005, Warnier 2010)
     reproduces all three supplied circular channels with less than 70 %
     mean deviation without channel-specific adjustment.
   - Calibrated c values are therefore stored for PVC (chapter 10).
   - Channel PVC 1500/1150 is marked as unusable (c between −7.6 and +16);
     c = 0.465 applies there.
5. **Square and circular channels compared:**
   - In the glass channel (square), the measured values follow the trend of
     the literature models, especially Yue 2007; the absolute values differ
     in part by a multiple.
   - The circular channels show hardly any trend. Likely causes are the
     pressure model and material effects.
6. **Active zone as one range:**
   - kLa_log_mean uses the first and the last active point.
   - If the active zone were interrupted, the sections in between would be
     counted in the residence time. This does not occur in the supplied
     series.
7. **Literature models at 25 °C:**
   - Ca, Re and Sc of the literature models are calculated with fixed
     property data for about 25 °C.
   - The rest of the evaluation uses the measured temperature.
   - At 20–25 °C the difference is a few per cent.
8. **Cache of the property data:**
   - Property data are cached with the temperature rounded to 0.1 K.
   - Operating points with almost the same temperature receive identical
     values. The result of an operating point therefore depends slightly on
     which points were calculated before in the same run: if an operating
     point is added or excluded, other kLa_log_mean values change by at
     most about 0.002 %.
   - The reference results apply to evaluating all supplied channels in
     alphabetical order.
9. **3D surfaces:**
   - The cubic interpolation can over- or undershoot with few, irregularly
     spaced points.
   - For quantitative statements, the data points count.
10. **Several recordings per bin:** if a file contains several rows for the
    same camera and bin, the smallest bubble length is used (chapter 2.3).

## 8.3 Sensitivity to the settings

All fixed thresholds were varied with the supplied series (5 channels, 55
operating points). Effect on kLa_log_mean:

| Quantity | Variation | Effect |
|---|---|---|
| start value λ_0 of the fit | 0.01–0.2 m | none (identical results) |
| step size dz | 0.25–2 mm | a few per cent, below the measurement uncertainty |
| saturation limit | 0.99–0.999 | none |
| limit of the active zone u_rel(ΔC) | 0.3–0.7 | none |
| cap on U_fit | – | never active |
| offset limit | – | never reached |
| fallback model of the calibration | linear instead of polynomial | ≤ 3.6 % in one operating point |
| film thickness model | δ/d 0.03–0.10, Aussillous instead of Bretherton | none (approximation never active) |

The results therefore depend practically not on the numerical settings.
What matters are the measurement data, the pressure model and the exclusion
rules.

## 8.4 Open points

- **Pressure model of circular channels:** a physically founded
  alternative to the calibration is missing (8.2 no. 4).
- **Calibration:** the fallback models are fitted with only 5–8 points
  (chapter 10.5).
- **Rectangular, non-square channels:** geometry, pressure and film models
  would have to be extended.
- **Other liquids:** Henry constant and diffusion coefficient would have to
  be added (chapter 12.3).
