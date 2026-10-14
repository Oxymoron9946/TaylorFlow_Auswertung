# 6 Methodik

Dieses Kapitel beschreibt die Modellkette so, wie sie im Code umgesetzt ist.
Die ausführliche Herleitung mit allen Sensitivitätsanalysen steht im
Archiv-Repository (`docs/METHODIK.md`, `docs/FEHLERANALYSE_ECKIG_VS_RUND.md`).

Bezeichnungen: z Position ab Einlass, L_B Blasenlänge, L_S Sluglänge,
U Blasengeschwindigkeit, d Kanaldurchmesser bzw. Seitenlänge, δ Filmdicke,
T Temperatur, p Druck, C_L Konzentration in der Flüssigkeit,
C* Gleichgewichtskonzentration.

## 6.1 Annahmen

- **Isotherm:** Je Betriebspunkt werden T (Mittel der Messung) und p am
  Auslass gemittelt. Stoffdaten (ρ, μ, σ, H, D, p_v) gelten bei diesen
  Werten für den ganzen Kanal.
- **Gasphase:** Ideales Gas. Das Gas ist sofort mit Wasserdampf gesättigt;
  der trockene Gasdruck ist $p_{tr} = p - p_v$.
- **Absorption:** Nur CO2 wird absorbiert, der Inertanteil (N2) bleibt in
  der Blase.
- **Flüssigkeitsvolumen:** Das Flüssigkeitsvolumen einer Einheitszelle wird
  am Einlass bestimmt und bleibt konstant.
- **Durchmischung:** Der Slug ist ideal durchmischt (eine Konzentration C_L
  je Position).

## 6.2 Blasenlängen-Fit

Gemessene Blasenlängen aller Kameras werden mit dem Modell

$$L_B(z) = L_0 - A\left(1 - e^{-z/\lambda}\right) + B\,z \;+\; o_j$$

angepasst:
- A: absorptionsbedingte Verkürzung
- λ: Absorptionslänge
- B: Expansion durch den Druckabfall
- o_j: konstanter Versatz der Kamera j gegenüber Kamera 1 (o_1 = 0), der
  Kalibrierunterschiede zwischen den Kamerapositionen auffängt

Weitergerechnet wird mit der Kurve **ohne** Offsets.

**Gewichtung:**

$$\sigma = \sqrt{\sigma_{SEM}^2 + \sigma_{sys}^2}, \qquad
\sigma_{SEM} = s/\sqrt{n} + 1\,\mu\mathrm{m}, \quad \sigma_{sys} = 2\,\mu\mathrm{m}.$$

**Ablauf:**
1. Gewichteter Fit.
2. Robuster Fit (soft-L1) mit einer Skalierung aus der MAD der Residuen des
   ersten Durchgangs.

**Grenzen:**
- L_0 ∈ [0,1; 5] · max(L)
- A ≤ 2 · Spannweite(L)
- λ zwischen kleinstem Messpunktabstand und 10 L_Reaktor
- 0 ≤ B ≤ 2 max(L)/L_Reaktor
- |o_j| ≤ 0,2 · mittlere Blasenlänge

**Fallbacks:** Ohne Offsets → Modell v1 ($a e^{-bz} + c + dz$) → linear. Der
verwendete Modellname steht in `fit_model`.

Sluglänge $L_S = L_{UC} - L_B$ und Geschwindigkeit U werden linear über z
angepasst. Gefittete Geschwindigkeiten über $1{,}5 \cdot U_{ref}$ werden
verworfen und interpoliert; $U_{ref} = \max(\text{Median gemessen}, u_G + u_L)$.

## 6.3 Filmdicke und Blasengeometrie

Kapillarzahl $Ca = \mu U/\sigma$.

| Kanal | Gültigkeit | Filmdicke |
|---|---|---|
| rund | Ca ≤ 0,005 | Bretherton: $\delta = \tfrac{d}{2}\, 1{,}34\, Ca^{2/3}$ |
| rund | 0,005 < Ca ≤ 1,5 | Aussillous/Quéré: $\delta = \tfrac{d}{2}\, \dfrac{1{,}34\, Ca^{2/3}}{1 + 3{,}35\, Ca^{2/3}}$ |
| quadratisch | – | Kreutzer/Thulasidas: $\delta/d = 0{,}357 - 0{,}25\, e^{-2{,}25\, Ca^{0{,}445}}$ |

**Blase:** Durchmesser bzw. Seitenlänge $d_B = d - 2\delta$. Sie besteht aus
einem Zylinder (rund) bzw. Quader (quadratisch) der Länge $L_B - d_B$ und
zwei Kappen mit zusammen $V_{caps} = \tfrac{\pi}{6} d_B^3$:

$$V_B = V_{caps} + A_B\,\max(0,\, L_B - d_B), \qquad
A_B = \tfrac{\pi}{4} d_B^2 \;\text{(rund)}, \quad A_B = d_B^2 \;\text{(quadratisch)}.$$

**Flüssigkeit je Einheitszelle** (am Einlass):

$$V_L = L_S A_K + L_B (A_K - A_B) \; (+\, V_{caps}/2 \text{ im runden Kanal}),$$

mit dem Kanalquerschnitt $A_K$.

## 6.4 Druckprofil

Rückwärtsintegration vom gemessenen Auslassdruck mit Schritt dz = 1 mm:
$p(z_i) = p(z_{i+1}) + (\mathrm{d}p/\mathrm{d}z)_i\,\Delta z$.

In beiden Modellen wird als Geschwindigkeit $u_{TP}$ die gefittete
Blasengeschwindigkeit $U(z)$ eingesetzt. METHODIK.md im Archiv spricht hier
von u_TP; der Code verwendet U.

**Runder Kanal** (Bretherton 1961, nach Fries 2008):

$$f_{app} = \frac{16}{Re}\left[1 + c\,\frac{d}{L_S}\,Ca^{-1/3}\right], \qquad
\Delta p_{UC} = 2 f_{app}\,\rho_L u_{TP}^2 \frac{L_S}{d}, \qquad
\frac{\mathrm{d}p}{\mathrm{d}z} = \frac{\Delta p_{UC}}{L_S + L_B}.$$

c stammt aus der Kalibrier-Datenbank:
- lineare Interpolation zwischen den kalibrierten Betriebspunkten
- außerhalb davon das gespeicherte Ersatzmodell
- ohne verwendbaren Eintrag der Theoriewert c = 0,465

**Quadratischer Kanal** (Kurimoto et al. 2020, Gl. 27/28):

$$\Delta p_B = \frac{\sigma}{d}\,\frac{7{,}106\,Ca^{2/3}}{N}, \qquad
\frac{\mathrm{d}p}{\mathrm{d}z} = \frac{L_S}{L_{UC}}\,\frac{\rho_L u^2}{2d}\,\frac{56{,}9}{Re}
\left[1 + \frac{d}{L_S}\,\frac{0{,}250\,Ca^{-1/3}}{N}\right],$$

mit $N = 1 + 0{,}744\,Ca^{2/3} - 0{,}623\,We^{0{,}120}$. Es gibt keinen freien
Faktor. Ca, Re und We werden mit der Blasengeschwindigkeit gebildet, wie bei
Kurimoto vorgesehen.

## 6.5 Stoffbilanz

Gasmenge in der Blase an der Stelle z und am Einlass:

$$n(z) = \frac{p_{tr}(z)\,V_B(z)}{R\,T}, \qquad n_0 = n(0).$$

Davon sind $n_{CO_2,0} = y_{CO_2}\, n_0$ und $n_{inert} = (1-y_{CO_2})\, n_0$.
Absorbiert bis z (begrenzt auf $[0,\, n_{CO_2,0}]$, danach monoton gemacht):

$$\Delta n(z) = n_0 - n(z), \qquad C_L(z) = \Delta n(z)/V_L.$$

Gleichgewicht mit dem lokalen CO2-Anteil im trockenen Gas:

$$y(z) = \frac{n_{CO_2,0} - \Delta n}{n_{inert} + n_{CO_2,0} - \Delta n}, \qquad
C^*(z) = H(T)\, p_{tr}(z)\, y(z),$$

$$H(T) = H_{298}\,\exp\!\left[\frac{\Delta_{sol}H}{R}\left(\frac1T - \frac1{298{,}15}\right)\right]
\quad\text{(Sander 2015; CO2: } H_{298} = 3{,}36\cdot10^{-4}\,\mathrm{mol/(m^3\,Pa)},\ 2400\,\mathrm{K}).$$

C_L wird höchstens auf $0{,}999\,C^*$ gesetzt. Die Sättigung ist $C_L/C^*$.

**Ableitung dn/dz:** analytisch aus dem Blasenfit statt numerisch aus dem
verrauschten Δn:

$$\frac{\mathrm{d}\Delta n}{\mathrm{d}z} = -\frac{1}{RT}\left[\frac{\mathrm{d}p_{tr}}{\mathrm{d}z}V_B
+ p_{tr}\,A_B\,\frac{\mathrm{d}L_B}{\mathrm{d}z}\right], \qquad
\frac{\mathrm{d}L_B}{\mathrm{d}z} = -\frac{A}{\lambda}e^{-z/\lambda} + B.$$

Negative Werte werden auf 0 gesetzt, Einbrüche interpoliert.

## 6.6 Lokales kLa und aktive Zone

$$k_La(z) = \frac{(\mathrm{d}\Delta n/\mathrm{d}z)\, U}{V_L\,\Delta C}, \qquad \Delta C = C^* - C_L
\qquad\text{(Yue 2007)}.$$

**Aktive Zone:**
- Ein Punkt gehört dazu, wenn $\Delta C > 0$ und die relative Unsicherheit von
  ΔC aus dem C*-Anteil höchstens 0,5 ist:
  $u_{rel}(C^*) \cdot C^* / \Delta C \le 0{,}5$, mit
  $u_{rel}(C^*) = \sqrt{0{,}03^2 + 0{,}02^2} \approx 3{,}6\,\%$.
- Gegen Ende des Kanals, wenn ΔC klein wird, endet die aktive Zone.

**Einlauf:**
- Vor dem ersten Messpunkt wird das lokale kLa auf 0 gesetzt, denn dort
  existieren nur extrapolierte Fitwerte.

**Ausreißer:**
- Lokale Werte über $\max(\tilde k + 3{,}5 \cdot 1{,}4826\,\mathrm{MAD},\ 20\,\mathrm{s^{-1}})$
  werden verworfen (Iglewicz/Hoaglin 1993); $\tilde k$ ist der Median der
  positiven Werte.

**Unsicherheit des lokalen kLa** (Spalte `u_rel_kLa`):

$$u_{rel}(k_La) = \sqrt{u_{rel}(\dot n)^2 + u_{rel}(V_L)^2 + u_{rel}(\Delta C)^2},$$

- $u_{rel}(\dot n) = 7{,}29\,\%$
- $u_{rel}(V_L) = 1{,}41\,\mathrm{px} / L_B[\mathrm{px}]$
- $u(\Delta C)$ aus $u(C^*)$ und dem entlang z quadratisch aufsummierten
  Fehler von C_L

## 6.7 kLa_log_mean

Für eine Pfropfenströmung mit konstantem kLa gilt
$\mathrm{d}C_L/\mathrm{d}t = k_La\,(C^* - C_L)$. Integriert über die aktive
Zone (vom ersten bis zum letzten aktiven Punkt):

$$k_La_{log} = \frac{1}{t_{res}}\ln\frac{\Delta C_{ein}}{\Delta C_{aus}}, \qquad
t_{res} = \int_{z_{ein}}^{z_{aus}} \frac{\mathrm{d}z}{U(z)}$$

(Kashid 2011).

Eigenschaften:
- kLa_log_mean nutzt nur ΔC an den Rändern der aktiven Zone und die
  Verweilzeit, nicht die lokalen Werte. Damit ist es unempfindlich gegen
  Rauschen in dn/dz.
- Es wird 0 bei weniger als 10 aktiven Gitterpunkten.
- Es bleibt leer, wenn nach dem Ausreißerfilter weniger als 10 valide
  lokale Werte übrig sind oder der Betriebspunkt unter `kla_ungueltig`
  steht.

## 6.8 Weitere Kenngrößen

**Volumenspezifischer Molenstrom über den ganzen Kanal** (Bezug wie beim
Monolithen):

$$\dot n_{spez} = \frac{\Delta n(z_{Ende})\, f_B}{A_K\, z_{Ende}}, \qquad f_B = \frac{U(0)}{L_B(0) + L_S(0)}$$

(f_B ist die Blasenfrequenz).

**Druckkorrigierte Blasenlänge:** Das Blasenvolumen wird auf den
Einlassdruck umgerechnet, $V_B\, p_{tr}(z)/p_{tr}(0)$, und zurück in eine
Länge. Ohne Absorption wäre die Kurve konstant.

**Schlupf:** Median der gemessenen Blasengeschwindigkeit / (u_G + u_L).

## 6.9 Literatur

- Aussillous, P., Quéré, D. (2000). Quick deposition of a fluid on the wall of a tube. *Phys. Fluids* 12, 2367–2371.
- Bretherton, F. P. (1961). The motion of long bubbles in tubes. *J. Fluid Mech.* 10, 166–188.
- Fries, D. M. et al. (2008). Gas–liquid two-phase flow in meandering microchannels. *Chem. Eng. J.* 135S, S37–S45.
- Iglewicz, B., Hoaglin, D. (1993). *How to Detect and Handle Outliers.* ASQC.
- Kashid, M. N. et al. (2011). Gas–liquid and liquid–liquid mass transfer in microstructured reactors. *Chem. Eng. Sci.* 66, 3876–3897.
- Kreutzer, M. T. (2003). *Hydrodynamics of Taylor flow in capillaries and monolith reactors.* Diss., TU Delft.
- Kurimoto, R. et al. (2020). Pressure drop of Taylor flow in square microchannels. *Chem. Eng. Sci.*
- Liu, H. et al. (2005). Hydrodynamics of Taylor flow in vertical capillaries. *Ind. Eng. Chem. Res.* 44, 4884–4897.
- Sander, R. (2015). Compilation of Henry's law constants for water as solvent. *Atmos. Chem. Phys.* 15, 4399–4981.
- Versteeg, G. F., van Swaaij, W. P. M. (1988). Solubility and diffusivity of acid gases in aqueous alkanolamine solutions. *J. Chem. Eng. Data* 33, 29–34.
- Yue, J. et al. (2007). Hydrodynamics and mass transfer characteristics in gas–liquid flow through a rectangular microchannel. *Chem. Eng. Sci.* 62, 2096–2108.

Quellen der Literaturmodelle: [Kapitel 8](08_literaturvergleich.md).
