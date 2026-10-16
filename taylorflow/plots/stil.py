# -*- coding: utf-8 -*-
"""
Gemeinsamer Stil aller Plots: Sprache, Größen, Schrift, Farben, Speichern.

Alle Plotfunktionen nehmen ein ``PlotStil``-Objekt entgegen und geben eine
matplotlib-Figure zurück. Gespeichert wird mit ``speichere``. Größen werden
in Zentimetern angegeben.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

# Farben (TU-Dresden-Hausfarben, abgedunkelt für Druck)
BLAU = "#002557"
BLAU_MITTEL = "#0F5FA3"
BLAU_HELL = "#7FBBE0"
GRUEN = "#3B8B3B"
ORANGE = "#E08600"
ROT = "#C8102E"
GRAU = "#58585A"
KAMERA_FARBEN = ["#0F5FA3", "#E08600", "#3B8B3B", "#8E44AD"]


@dataclass(frozen=True)
class PlotStil:
    """Darstellungsoptionen für alle Plots."""
    sprache: str = "de"                       # "de" oder "en"
    formate: tuple = ("png",)                 # z. B. ("png", "pdf")
    dpi: int = 300
    schriftart: tuple = ("DejaVu Sans", "Arial", "Helvetica")
    schriftgroesse: float = 10.0
    groesse_profil_cm: tuple = (16.0, 9.0)
    groesse_3d_cm: tuple = (14.0, 11.0)
    groesse_heatmaps_cm: tuple = (30.0, 17.0)
    groesse_paritaet_cm: tuple = (12.0, 11.0)
    titel_anzeigen: bool = True
    gitter: bool = True
    blickwinkel_3d: tuple = (25, 135)         # (Höhe, Azimut) in Grad

    def mit(self, **aenderungen) -> "PlotStil":
        """Kopie mit geänderten Werten, z. B. ``stil.mit(sprache="en")``."""
        return replace(self, **aenderungen)


TEXTE = {
    "z_cm": ("Reaktorposition $z$ [cm]", "Reactor position $z$ [cm]"),
    "L_b_mm": ("Blasenlänge $L_B$ [mm]", "Bubble length $L_B$ [mm]"),
    "kamera": ("Kamera", "Camera"),
    "messwerte_kamera": ("Messwerte Kamera {j}", "Measured, camera {j}"),
    "fit_ohne": ("Fit ohne Kamera-Offsets", "Fit without camera offsets"),
    "fit_mit": ("Fit mit Kamera-Offsets", "Fit with camera offsets"),
    "fit_mit_zwischen": ("Fit mit Offsets (zwischen Kameras)", "Fit with offsets (between cameras)"),
    "L_korr": ("Blasenlänge auf Einlassdruck korrigiert", "Bubble length corrected to inlet pressure"),
    "dn_umol": (r"Absorbierte Stoffmenge je Blase $\Delta n$ [µmol]", r"Absorbed amount per bubble $\Delta n$ [µmol]"),
    "p_pa": ("Druck $p$ [Pa]", "Pressure $p$ [Pa]"),
    "u_G": (r"$u_{G}$ [m/s]", r"$u_{G}$ [m/s]"),
    "u_L": (r"$u_{L}$ [m/s]", r"$u_{L}$ [m/s]"),
    "kla": (r"$k_La_{\mathrm{log}}$ [1/s]", r"$k_La_{\mathrm{log}}$ [1/s]"),
    "nspez": (r"$\dot n_{\mathrm{spez}}$ [mol/(s m³)]", r"$\dot n_{\mathrm{spec}}$ [mol/(s m³)]"),
    "messpunkte": ("Messpunkte", "Measured points"),
    "saettigung_aus": ("Sättigung am Austritt [%]", "Saturation at outlet [%]"),
    "z95": (r"Absorptionslänge $z_{95}/L$ [%]", r"Absorption length $z_{95}/L$ [%]"),
    "beta_ein": (r"Gasanteil am Einlass $\beta = L_B/(L_B+L_S)$ [-]", r"Gas fraction at inlet $\beta = L_B/(L_B+L_S)$ [-]"),
    "schlupf": (r"Schlupf $u_{B,\mathrm{gemessen}}/u_{TP}$ [-]", r"Slip $u_{B,\mathrm{meas}}/u_{TP}$ [-]"),
    "L_b_ein_mm": ("Blasenlänge am Einlass [mm]", "Bubble length at inlet [mm]"),
    "gemessen": ("gemessen", "measured"),
    "berechnet": ("berechnet", "predicted"),
    "band": ("±{p:g} %", "±{p:g} %"),
    "keine_daten": ("keine Daten", "no data"),
}


def t(schluessel: str, stil: PlotStil, **werte) -> str:
    """Beschriftung in der eingestellten Sprache."""
    de, en = TEXTE[schluessel]
    text = en if stil.sprache == "en" else de
    return text.format(**werte) if werte else text


def zahl(wert: float, stil: PlotStil, stellen: int = 3) -> str:
    """Zahl als Text mit Dezimalkomma (de) bzw. -punkt (en)."""
    s = f"{wert:.{stellen}g}"
    return s.replace(".", ",") if stil.sprache == "de" else s


@contextmanager
def rc(stil: PlotStil):
    """Setzt Schrift und Schriftgröße für die Dauer eines Plots."""
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": list(stil.schriftart),
                         "font.size": stil.schriftgroesse, "axes.unicode_minus": False}):
        yield


def neue_figur(stil: PlotStil, groesse_cm: tuple, projektion: str | None = None):
    """Neue Figure mit einer Achse (Größe in cm)."""
    fig = plt.figure(figsize=(groesse_cm[0] / 2.54, groesse_cm[1] / 2.54), layout="constrained")
    ax = fig.add_subplot(111, projection=projektion)
    return fig, ax


def formatiere_achsen(ax, stil: PlotStil, achsen: str = "xy") -> None:
    """Dezimalkomma für Deutsch, Gitter nach Einstellung."""
    if stil.sprache == "de":
        fmt = FuncFormatter(lambda v, _pos: f"{v:g}".replace(".", ","))
        for a in achsen:
            getattr(ax, f"{a}axis").set_major_formatter(fmt)
    if stil.gitter:
        ax.grid(True, linestyle=":", alpha=0.4)


def speichere(fig, ordner: Path, name: str, stil: PlotStil) -> list[Path]:
    """Speichert die Figure in allen Formaten aus ``stil.formate`` und schließt sie."""
    ordner = Path(ordner)
    ordner.mkdir(parents=True, exist_ok=True)
    pfade = []
    for fmt in stil.formate:
        pfad = ordner / f"{name}.{fmt}"
        fig.savefig(pfad, dpi=stil.dpi, bbox_inches="tight")
        pfade.append(pfad)
    plt.close(fig)
    return pfade


def achsgrenzen(werte, rand: float = 0.05, ab_null: bool = True) -> tuple[float, float]:
    """Achsbereich mit relativem Rand; beginnt bei 0, wenn ``ab_null``."""
    werte = np.asarray(werte, dtype=float)
    werte = werte[np.isfinite(werte)]
    if werte.size == 0:
        return 0.0, 1.0
    hi = float(werte.max()) * (1 + rand)
    lo = 0.0 if ab_null else float(werte.min()) - rand * abs(float(werte.min()))
    return lo, hi if hi > lo else lo + 1.0
