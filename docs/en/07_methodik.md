# 7 Methodology

This chapter describes the chain of models as implemented in the code.

Symbols: z position from the inlet, L_B bubble length, L_S slug length,
U bubble velocity, d channel diameter or side length, δ film thickness,
T temperature, p pressure, C_L concentration in the liquid,
C* equilibrium concentration.

## 7.1 Assumptions

- **Isothermal:** T and p at the outlet are averaged per operating point.
  Property data (ρ, μ, σ, H, D, p_v) at these values apply to the whole
  channel.
- **Gas phase:** ideal gas. The gas is immediately saturated with water
  vapour; the dry gas pressure is $p_{tr} = p - p_v$.
- **Absorption:** only CO2 is absorbed; the inert part (N2) stays in the
  bubble.
- **Liquid volume:** the liquid volume of a unit cell is determined at the
  inlet and remains constant.
- **Mixing:** the slug is ideally mixed (one concentration C_L per position).

## 7.2 Bubble length fit

The measured bubble lengths of all cameras are fitted with the model

$$L_B(z) = L_0 - A\left(1 - e^{-z/\lambda}\right) + B\,z \;+\; o_j$$

- A: shortening due to absorption
- λ: absorption length
- B: expansion due to the pressure drop
- o_j: constant offset of camera j relative to camera 1 (o_1 = 0), which
  absorbs calibration differences between the camera positions

The calculation continues with the curve **without** offsets.

**Weighting:**

$$\sigma = \sqrt{\sigma_{SEM}^2 + \sigma_{sys}^2}, \qquad
\sigma_{SEM} = s/\sqrt{n} + 1\,\mu\mathrm{m}, \quad \sigma_{sys} = 2\,\mu\mathrm{m}.$$

**Procedure:**

1. Weighted fit.
2. Robust fit (soft-L1) with a scale from the MAD of the residuals of the
   first pass.

**Parameter limits:**

- L_0 ∈ [0.1; 5] · max(L)
- A ≤ 2 · range(L)
- λ between the smallest spacing of data points and 10 L_reactor
- 0 ≤ B ≤ 2 max(L)/L_reactor
- |o_j| ≤ 0.2 · mean bubble length

**Fallback models:** if the fit fails, a model without offsets follows, then
$a e^{-bz} + c + dz$, finally a straight line. The name of the model used is
in the column `fit_model`.

Slug length $L_S = L_{UC} - L_B$ and velocity U are fitted linearly over z.
Fitted velocities above $1.5 \cdot U_{ref}$ are discarded and interpolated;
$U_{ref} = \max(\text{measured median}, u_G + u_L)$.

## 7.3 Film thickness and bubble geometry

Capillary number $Ca = \mu U/\sigma$.

| Channel | Validity | Film thickness |
|---|---|---|
| circular | Ca ≤ 0.005 | Bretherton: $\delta = \tfrac{d}{2}\, 1.34\, Ca^{2/3}$ |
| circular | 0.005 < Ca ≤ 1.5 | Aussillous/Quéré: $\delta = \tfrac{d}{2}\, \dfrac{1.34\, Ca^{2/3}}{1 + 3.35\, Ca^{2/3}}$ |
| square | – | Kreutzer/Thulasidas: $\delta/d = 0.357 - 0.25\, e^{-2.25\, Ca^{0.445}}$ |

**Bubble:** diameter or side length $d_B = d - 2\delta$. It consists of a
cylinder (circular) or cuboid (square) of length $L_B - d_B$ and two caps
with a combined volume $V_{caps} = \tfrac{\pi}{6} d_B^3$:

$$V_B = V_{caps} + A_B\,\max(0,\, L_B - d_B), \qquad
A_B = \tfrac{\pi}{4} d_B^2 \;\text{(circular)}, \quad A_B = d_B^2 \;\text{(square)}.$$

**Liquid per unit cell** (at the inlet), with the channel cross-section
$A_K$:

$$V_L = L_S A_K + L_B (A_K - A_B) \; (+\, V_{caps}/2 \text{ in the circular channel}).$$

## 7.4 Pressure profile

Backward integration from the measured outlet pressure with step dz = 1 mm:
$p(z_i) = p(z_{i+1}) + (\mathrm{d}p/\mathrm{d}z)_i\,\Delta z$. In both models
the fitted bubble velocity $U(z)$ is used as the velocity $u_{TP}$.

**Circular channel** (Bretherton 1961, after Fries 2008):

$$f_{app} = \frac{16}{Re}\left[1 + c\,\frac{d}{L_S}\,Ca^{-1/3}\right], \qquad
\Delta p_{UC} = 2 f_{app}\,\rho_L u_{TP}^2 \frac{L_S}{d}, \qquad
\frac{\mathrm{d}p}{\mathrm{d}z} = \frac{\Delta p_{UC}}{L_S + L_B}.$$

c comes from the calibration database (chapter 10):

- linear interpolation between the calibrated operating points
- outside them, the stored fallback model
- without a usable entry, the theoretical value c = 0.465

**Square channel** (Kurimoto et al. 2020, eq. 27/28):

$$\Delta p_B = \frac{\sigma}{d}\,\frac{7.106\,Ca^{2/3}}{N}, \qquad
\frac{\mathrm{d}p}{\mathrm{d}z} = \frac{L_S}{L_{UC}}\,\frac{\rho_L u^2}{2d}\,\frac{56.9}{Re}
\left[1 + \frac{d}{L_S}\,\frac{0.250\,Ca^{-1/3}}{N}\right],$$

with $N = 1 + 0.744\,Ca^{2/3} - 0.623\,We^{0.120}$. There is no free factor.
Ca, Re and We are formed with the bubble velocity, as intended by Kurimoto.

## 7.5 Mass balance

Amount of gas in the bubble at position z and at the inlet:

$$n(z) = \frac{p_{tr}(z)\,V_B(z)}{R\,T}, \qquad n_0 = n(0).$$

Of this, $n_{CO_2,0} = y_{CO_2}\, n_0$ and $n_{inert} = (1-y_{CO_2})\, n_0$.
Absorbed up to z (limited to $[0,\, n_{CO_2,0}]$, then made monotonic):

$$\Delta n(z) = n_0 - n(z), \qquad C_L(z) = \Delta n(z)/V_L.$$

Equilibrium with the local CO2 fraction in the dry gas:

$$y(z) = \frac{n_{CO_2,0} - \Delta n}{n_{inert} + n_{CO_2,0} - \Delta n}, \qquad
C^*(z) = H(T)\, p_{tr}(z)\, y(z),$$

$$H(T) = H_{298}\,\exp\!\left[\frac{\Delta_{sol}H}{R}\left(\frac1T - \frac1{298.15}\right)\right]$$

with $H_{298} = 3.36\cdot10^{-4}\,\mathrm{mol/(m^3\,Pa)}$ and
$\Delta_{sol}H/R = 2400\,\mathrm{K}$ for CO2 (Sander 2015).

C_L is limited to $0.999\,C^*$. The saturation is $C_L/C^*$.

## 7.6 Active zone and kLa_log_mean

**Active zone.** A grid point belongs to it if the driving concentration
difference $\Delta C = C^* - C_L$ is positive and larger than twice the
uncertainty of C*:

$$\Delta C > 0 \quad\text{and}\quad \frac{u_{rel}(C^*)\, C^*}{\Delta C} \le 0.5, \qquad
u_{rel}(C^*) = \sqrt{0.03^2 + 0.02^2} \approx 3.6\,\%.$$

When the liquid is nearly saturated, ΔC can no longer be determined
reliably; there the active zone ends. The condition is met as long as the
saturation stays below about 93 %; in the supplied series the active zone
therefore usually covers almost the whole channel.

**kLa_log_mean.** For plug flow with constant kLa,
$\mathrm{d}C_L/\mathrm{d}t = k_La\,(C^* - C_L)$ holds. Integrated over the
active zone, from the first up to and including the last active point:

$$k_La_{log} = \frac{1}{t_{res}}\ln\frac{\Delta C_{in}}{\Delta C_{out}}, \qquad
t_{res} = \int_{z_{in}}^{z_{out}} \frac{\mathrm{d}z}{U(z)}$$

(Kashid 2011).

- kLa_log_mean uses ΔC at the boundaries of the active zone and the
  residence time. It is therefore insensitive to noise in the values in
  between.
- It is 0 with fewer than 10 active grid points or if ΔC does not decrease
  in the active zone.
- It stays empty if the operating point is listed under `kla_ungueltig`.

## 7.7 Further key figures

**Volume-specific molar flux over the whole channel** (same reference as
for the monolith):

$$\dot n_{spec} = \frac{\Delta n(z_{end})\, f_B}{A_K\, z_{end}}, \qquad f_B = \frac{U(0)}{L_B(0) + L_S(0)}$$

(f_B is the bubble frequency).

**Pressure-corrected bubble length:** the bubble volume is converted to the
inlet pressure, $V_B\, p_{tr}(z)/p_{tr}(0)$, and back into a length. Without
absorption the curve would be constant.

**Absorption length z95** (key figure overview): position at which Δn
reaches 95 % of its value at the channel end, relative to the channel
length.

**Slip:** median of the measured bubble velocity / (u_G + u_L).

## 7.8 Measurement uncertainty

An error propagation for the mass transfer along z (uncertainties of molar
flux, liquid volume and ΔC) is included as the function
`relative_unsicherheit` in `taylorflow/unsicherheit.py`. The evaluation
does not use it; it is available for own analyses.

## 7.9 References

- Aussillous, P., Quéré, D. (2000). Quick deposition of a fluid on the wall of a tube. *Phys. Fluids* 12, 2367–2371.
- Bretherton, F. P. (1961). The motion of long bubbles in tubes. *J. Fluid Mech.* 10, 166–188.
- Fries, D. M. et al. (2008). Gas–liquid two-phase flow in meandering microchannels. *Chem. Eng. J.* 135S, S37–S45.
- Kashid, M. N. et al. (2011). Gas–liquid and liquid–liquid mass transfer in microstructured reactors. *Chem. Eng. Sci.* 66, 3876–3897.
- Kreutzer, M. T. (2003). *Hydrodynamics of Taylor flow in capillaries and monolith reactors.* PhD thesis, TU Delft.
- Kurimoto, R. et al. (2020). Pressure drop of Taylor flow in square microchannels. *Chem. Eng. Sci.*
- Liu, H. et al. (2005). Hydrodynamics of Taylor flow in vertical capillaries. *Ind. Eng. Chem. Res.* 44, 4884–4897.
- Sander, R. (2015). Compilation of Henry's law constants for water as solvent. *Atmos. Chem. Phys.* 15, 4399–4981.
- Versteeg, G. F., van Swaaij, W. P. M. (1988). Solubility and diffusivity of acid gases in aqueous alkanolamine solutions. *J. Chem. Eng. Data* 33, 29–34.

Sources of the literature models: chapter 9.
