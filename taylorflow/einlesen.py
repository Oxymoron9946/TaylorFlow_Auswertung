# -*- coding: utf-8 -*-
"""
Einlesen der Messdateien und Anwenden der Ausschlussregeln.

Dateinamen (eine Datei je Kanal und Messart):

    Auswertung_<Messart>_<Material>_<Form>_<D>um_<L>cm_<X>mol<Gas>_<Nadel>um.csv

    Messart   Masse (Stoffübergang) oder Druck (Druckkalibrierung)
    Material  frei wählbar, z. B. Glas, PVC, PTFE
    Form      R oder Rund = runder Kanal; Q oder Eckig = quadratischer Kanal
    D         Kanaldurchmesser bzw. Seitenlänge [µm]
    L         Reaktorlänge [cm]
    X         CO2-Anteil im Eingangsgas [mol-%]
    Gas       Gasname für thermo (z. B. CO2)
    Nadel     Innendurchmesser der Gaseinlass-Nadel [µm]

Ausschlussregeln stehen in ``config/ausschluesse.yaml`` (siehe dort).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from . import stoffdaten
from .parameter import AuswerteParameter

DATEINAME_MUSTER = re.compile(
    r"^Auswertung_(Masse|Druck)_([A-Za-z0-9]+)_([A-Za-z]+)_(\d+)um_(\d+)cm_(\d+)mol([A-Za-z0-9]+)_(\d+)um\.csv$"
)
_FORM = {"r": "circular", "rund": "circular", "q": "rectangular", "eckig": "rectangular"}

PFLICHTSPALTEN = ["CameraPosition", "mean_BubbleLength_mm", "mean_UnitCellLength_mm",
                  "GasVelocity", "LiquidVelocity", "Temperatur_C", "Druck_Pa_Auslass",
                  "mean_Speed_m_s", "BinCenter_mm"]
_ZAHLSPALTEN = ["GasVelocity", "LiquidVelocity", "CameraPosition", "BinCenter_mm",
                "mean_BubbleLength_mm", "mean_UnitCellLength_mm", "mean_Speed_m_s",
                "std_BubbleLength_mm", "Druck_Pa_Auslass", "Temperatur_C"]


@dataclass(frozen=True)
class Messreihe:
    """Aus dem Dateinamen abgeleitete Beschreibung einer Messreihe."""
    datei: Path
    messart: str          # "Masse" oder "Druck"
    material: str
    geometrie: str        # "circular" oder "rectangular"
    d_kanal_um: int
    laenge_cm: int
    co2_mol_prozent: int
    gas: str
    nadel_um: int

    @property
    def form(self) -> str:
        return "Rund" if self.geometrie == "circular" else "Eckig"

    @property
    def kanal(self) -> str:
        """Eindeutiger Kanalname, z. B. ``Glas_Eckig_1000um_72cm_20molCO2_600um``."""
        return (f"{self.material}_{self.form}_{self.d_kanal_um}um_{self.laenge_cm}cm_"
                f"{self.co2_mol_prozent}mol{self.gas}_{self.nadel_um}um")

    @property
    def kalibrier_key(self) -> str:
        """Schlüssel in der Kalibrier-Datenbank (unabhängig von Länge und CO2-Anteil)."""
        return f"{self.material}_{self.geometrie}_{self.d_kanal_um}um_{self.nadel_um}um"

    @property
    def d_kanal_m(self) -> float:
        return float(self.d_kanal_um) * 1e-6

    @property
    def laenge_m(self) -> float:
        return float(self.laenge_cm) / 100.0

    @property
    def y_co2(self) -> float:
        return float(self.co2_mol_prozent) / 100.0

    @property
    def bezeichnung(self) -> str:
        return f"{self.material} | {self.form} | {self.d_kanal_um} µm | {self.nadel_um} µm"


def messreihe_aus_dateiname(datei: Path) -> Messreihe:
    """Zerlegt den Dateinamen; bricht mit einer verständlichen Meldung ab, wenn er nicht passt."""
    datei = Path(datei)
    m = DATEINAME_MUSTER.match(datei.name)
    if not m:
        raise ValueError(
            f"Dateiname '{datei.name}' passt nicht zum Schema "
            "Auswertung_<Masse|Druck>_<Material>_<R|Q>_<D>um_<L>cm_<X>mol<Gas>_<Nadel>um.csv "
            "(Beispiel: Auswertung_Masse_Glas_Q_1000um_72cm_20molCO2_600um.csv)."
        )
    messart, material, form, d, L, x, gas, nadel = m.groups()
    geometrie = _FORM.get(form.lower())
    if geometrie is None:
        raise ValueError(f"Unbekannte Kanalform '{form}' in '{datei.name}'. "
                         "Erlaubt: R oder Rund (rund), Q oder Eckig (quadratisch).")
    return Messreihe(datei, messart, material, geometrie, int(d), int(L), int(x), gas, int(nadel))


def finde_messreihen(ordner: Path, messart: str = "Masse") -> list[Messreihe]:
    """Alle gültig benannten Messdateien einer Messart, nach Dateiname sortiert."""
    return [messreihe_aus_dateiname(p) for p in sorted(Path(ordner).glob(f"Auswertung_{messart}_*.csv"))]


def _dateidialog(messart: str, startordner: Path) -> list[Path]:
    """Fenster zur Auswahl einer oder mehrerer Messdateien (Abbruch: leere Liste)."""
    import tkinter as tk
    from tkinter import filedialog

    fenster = tk.Tk()
    fenster.withdraw()
    fenster.attributes("-topmost", True)
    try:
        dateien = filedialog.askopenfilenames(
            parent=fenster,
            title=f"Messdateien auswählen (Auswertung_{messart}_….csv, mehrere mit Strg)",
            initialdir=str(startordner) if Path(startordner).is_dir() else None,
            filetypes=[(f"Messdateien {messart}", f"Auswertung_{messart}_*.csv"), ("CSV-Dateien", "*.csv")],
        )
    finally:
        fenster.destroy()
    return [Path(d) for d in dateien]


def waehle_messreihen(einstellung, messart: str, rohdaten_ordner: Path,
                      dialog_ordner: Path | None = None) -> list[Messreihe]:
    """
    Messreihen nach der Einstellung ``MESSDATEIEN`` in ``config.py``.

    Parameter
    ---------
    einstellung : "dialog" (Auswahlfenster), "alle" (alle Dateien der Messart im
        Rohdatenordner) oder eine Liste von Dateipfaden
    messart : "Masse" oder "Druck"
    dialog_ordner : Ordner, in dem das Auswahlfenster startet

    Rückgabe
    --------
    Liste der Messreihen; leer, wenn im Auswahlfenster abgebrochen wurde.
    """
    if isinstance(einstellung, str) and einstellung.lower() == "alle":
        reihen = finde_messreihen(rohdaten_ordner, messart)
        if not reihen:
            raise FileNotFoundError(f"Keine Dateien Auswertung_{messart}_*.csv in {rohdaten_ordner}.")
        return reihen
    if isinstance(einstellung, str) and einstellung.lower() == "dialog":
        dateien = _dateidialog(messart, Path(dialog_ordner or rohdaten_ordner))
    elif isinstance(einstellung, (str, Path)):
        dateien = [Path(einstellung)]
    else:
        dateien = [Path(d) for d in einstellung]

    fehlend = [str(d) for d in dateien if not d.is_file()]
    if fehlend:
        raise FileNotFoundError(f"Messdatei nicht gefunden: {fehlend}")
    reihen = [messreihe_aus_dateiname(d) for d in dateien]
    falsch = [r.datei.name for r in reihen if r.messart != messart]
    if falsch:
        raise ValueError(f"Hier werden Dateien Auswertung_{messart}_….csv erwartet, gewählt: {falsch}")
    namen = [r.kanal for r in reihen]
    doppelt = sorted({n for n in namen if namen.count(n) > 1})
    if doppelt:
        raise ValueError(f"Mehrere Dateien mit demselben Kanalnamen gewählt: {doppelt}")
    return sorted(reihen, key=lambda r: r.datei.name)


# =============================================================================
# Ausschlussregeln
# =============================================================================

def lade_ausschluesse(datei: Path) -> dict:
    """Liest ``config/ausschluesse.yaml``; fehlt die Datei, gibt es keine Ausschlüsse."""
    datei = Path(datei)
    if not datei.exists():
        return {}
    with open(datei, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _passt(df: pd.DataFrame, regel: dict) -> pd.Series:
    """Maske der Zeilen, auf die eine Regel zutrifft (alle angegebenen Felder müssen passen)."""
    maske = pd.Series(True, index=df.index)
    if "GasVelocity" in regel:
        maske &= np.isclose(df["GasVelocity"], regel["GasVelocity"])
    if "LiquidVelocity" in regel:
        maske &= np.isclose(df["LiquidVelocity"], regel["LiquidVelocity"])
    if "CameraPosition" in regel:
        maske &= (df["CameraPosition"] == regel["CameraPosition"])
    if "BinCenter_mm" in regel:
        maske &= np.isclose(df["BinCenter_mm"], regel["BinCenter_mm"], atol=0.1)
    return maske


def betriebspunkt_ueberspringen(regeln: list[dict], gas: float, liq: float) -> str | None:
    """Grund, falls der Betriebspunkt laut Regel komplett übersprungen wird, sonst None."""
    for r in regeln or []:
        if "GasVelocity" in r and not np.isclose(gas, r["GasVelocity"]):
            continue
        if "LiquidVelocity" in r and not np.isclose(liq, r["LiquidVelocity"]):
            continue
        return str(r.get("grund", "ohne Angabe"))
    return None


# =============================================================================
# Einlesen
# =============================================================================

def lade_messdaten(reihe: Messreihe, ausschluesse: dict, p: AuswerteParameter,
                   ausgabe=print) -> pd.DataFrame:
    """
    Liest eine Messdatei, entfernt ausgeschlossene Messpunkte und wendet den
    automatischen Kamerafilter an (nur Messart „Masse“).

    Kamerafilter (METHODIK §1): Ein Bin ist gültig bei rel. Standardfehler <=
    ``kamerafilter_rel_se_max_prozent``, mindestens ``kamerafilter_n_min``
    Blasen und Variationskoeffizient <= ``kamerafilter_cv_max_prozent``. Eine
    Kamera eines Betriebspunkts bleibt nur, wenn mindestens
    ``kamerafilter_anteil_min`` ihrer Bins und mindestens
    ``kamerafilter_bins_min`` Bins gültig sind. Betriebspunkte mit nur noch
    einer Kamera werden entfernt.
    """
    stoffdaten.pruefe_gas(reihe.gas)
    try:
        df = pd.read_csv(reihe.datei, sep=";", decimal=",", quotechar='"', encoding="utf-8-sig")
    except Exception as e:
        raise RuntimeError(f"Fehler beim Lesen von '{reihe.datei.name}': {e}") from e

    fehlend = [c for c in PFLICHTSPALTEN if c not in df.columns]
    if fehlend:
        raise ValueError(f"In '{reihe.datei.name}' fehlen die Spalten {fehlend}.")
    for c in _ZAHLSPALTEN:
        if c in df.columns:
            if df[c].dtype == object:
                df[c] = df[c].astype(str).str.replace(",", ".")
            df[c] = pd.to_numeric(df[c], errors="coerce")
    # Die Videoauswertung schreibt die Anzahl je Bin nur als GroupCount (gleicher Wert wie numel_*)
    if "numel_BubbleLength_mm" not in df.columns and "GroupCount" in df.columns:
        df["numel_BubbleLength_mm"] = pd.to_numeric(df["GroupCount"], errors="coerce")

    # --- Manuell ausgeschlossene Messpunkte -----------------------------------
    regeln = (ausschluesse.get(reihe.kanal) or {}).get("messpunkte_entfernen") or []
    if regeln:
        behalten = pd.Series(True, index=df.index)
        for r in regeln:
            behalten &= ~_passt(df, r)
        n_vorher = len(df)
        df = df[behalten]
        if n_vorher - len(df) > 0:
            ausgabe(f"  {n_vorher - len(df)} Messpunkte laut ausschluesse.yaml entfernt.")

    if reihe.messart != "Masse" or "numel_BubbleLength_mm" not in df.columns:
        return df

    # --- Automatischer Kamerafilter ---------------------------------------------
    df = df.copy()
    se = df["std_BubbleLength_mm"] / np.sqrt(df["numel_BubbleLength_mm"])
    rel_se = (se / df["mean_BubbleLength_mm"]) * 100
    cv = (df["std_BubbleLength_mm"] / df["mean_BubbleLength_mm"]) * 100
    ok = ((rel_se <= p.kamerafilter_rel_se_max_prozent)
          & (df["numel_BubbleLength_mm"] >= p.kamerafilter_n_min)
          & (cv <= p.kamerafilter_cv_max_prozent))

    gruppen = ["GasVelocity", "LiquidVelocity", "CameraPosition"]
    n_bins = len(df)
    n_kameras = df.groupby(gruppen).ngroups
    vorher = df.groupby(gruppen).size().rename("vorher")
    nachher = df[ok].groupby(gruppen).size().rename("nachher")
    stat = pd.merge(vorher, nachher, left_index=True, right_index=True, how="left")
    stat["nachher"] = stat["nachher"].fillna(0)
    stat["anteil"] = stat["nachher"] / stat["vorher"]
    gueltig = stat[(stat["anteil"] >= p.kamerafilter_anteil_min)
                   & (stat["nachher"] >= p.kamerafilter_bins_min)].index
    verworfen = stat[~stat.index.isin(gueltig)]
    df = df[df.set_index(gruppen).index.isin(gueltig)].copy()

    bp = ["GasVelocity", "LiquidVelocity"]
    kameras_je_bp = df.groupby(bp)["CameraPosition"].nunique()
    nur_eine = kameras_je_bp[kameras_je_bp <= 1].index
    if not nur_eine.empty:
        df = df[~df.set_index(bp).index.isin(nur_eine)].copy()

    entfernt = n_bins - len(df)
    ausgabe(f"  Kamerafilter: {entfernt} von {n_bins} Bins entfernt "
            f"({entfernt / n_bins * 100 if n_bins else 0:.1f} %), "
            f"{n_kameras - df.groupby(gruppen).ngroups} von {n_kameras} Kamerapositionen.")
    for idx in verworfen.index:
        ausgabe(f"    Kamera verworfen: Gas {float(idx[0]):.3f}, Liq {float(idx[1]):.3f}, Kamera {idx[2]}")
    for idx in nur_eine:
        ausgabe(f"    Betriebspunkt entfernt (<= 1 Kamera übrig): Gas {float(idx[0]):.3f}, Liq {float(idx[1]):.3f}")
    return df
