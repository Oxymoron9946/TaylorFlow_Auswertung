# -*- coding: utf-8 -*-
"""
Messwerte mit Modellen vergleichen und eigene Modelle anpassen.

Modelle
    Literaturmodelle   fest im Code (``taylorflow.literatur.LITERATURMODELLE``)
    eigene Modelle     Potenzansätze, gespeichert in ``config/eigene_modelle.yaml``

Eigenes Modell (Potenzansatz):

    y = a · x_1^b_1 · x_2^b_2 · ...

Zielgröße y und Einflussgrößen x_k sind beliebige Zahlenspalten der
Betriebspunkt-Tabelle (z. B. kLa_log_mean_1_s über GasVelocity_m_s und
LiquidVelocity_m_s). Angepasst wird mit der Methode der kleinsten Quadrate
im logarithmischen Raum, d. h. es werden relative Abweichungen minimiert.
Ein angepasstes Modell lässt sich speichern und danach wie ein
Literaturmodell in Vergleichen und 3D-Flächen verwenden.

Typischer Ablauf (siehe ``literaturvergleich.py``):

    daten = lade_betriebspunkte_mehrerer_kanaele(ordner, ["PVC_Rund_..."])
    modell = fit_potenzansatz(daten, "kLa_log_mean_1_s",
                              ["GasVelocity_m_s", "LiquidVelocity_m_s"], name="pvc_kla")
    speichere_modell(modell, "config/eigene_modelle.yaml")
    tabelle = vergleichstabelle(daten, "kLa_log_mean_1_s", ["vandu", "pvc_kla"])
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from .literatur import LITERATURMODELLE, modelleingaben
from .parameter import AuswerteParameter

STANDARD_MODELLDATEI = Path(__file__).resolve().parents[1] / "config" / "eigene_modelle.yaml"


@dataclass
class EigenesModell:
    """Angepasster Potenzansatz y = koeffizient · Π variablen_k ^ exponenten_k."""
    name: str
    titel: str
    zielgroesse: str
    variablen: list[str]
    koeffizient: float
    exponenten: list[float]
    form: str = "potenz"
    datengrundlage: list[str] = field(default_factory=list)
    n_punkte: int = 0
    mape_prozent: float = float("nan")
    r2_log: float = float("nan")
    erstellt: str = ""

    def berechne(self, daten: pd.DataFrame) -> np.ndarray:
        y = np.full(len(daten), float(self.koeffizient))
        for v, b in zip(self.variablen, self.exponenten):
            if v not in daten.columns:
                raise KeyError(f"Modell '{self.name}' braucht die Spalte '{v}'.")
            y = y * np.asarray(daten[v], dtype=float) ** float(b)
        return y

    def formel(self) -> str:
        teile = [f"{self.koeffizient:.4g}"] + [f"{v}^{b:.3f}" for v, b in zip(self.variablen, self.exponenten)]
        return f"{self.zielgroesse} = " + " · ".join(teile)


# =============================================================================
# Modelle verwalten
# =============================================================================

def lade_eigene_modelle(datei: Path | None = None) -> dict[str, EigenesModell]:
    datei = Path(datei or STANDARD_MODELLDATEI)
    if not datei.exists():
        return {}
    with open(datei, "r", encoding="utf-8") as f:
        roh = yaml.safe_load(f) or {}
    return {name: EigenesModell(name=name, **werte) for name, werte in roh.items()}


def speichere_modell(modell: EigenesModell, datei: Path | None = None) -> Path:
    """Fügt das Modell der YAML-Datei hinzu (gleichnamige Einträge werden ersetzt)."""
    datei = Path(datei or STANDARD_MODELLDATEI)
    if modell.name in LITERATURMODELLE:
        raise ValueError(f"Der Name '{modell.name}' ist bereits ein Literaturmodell.")
    vorhanden = {}
    if datei.exists():
        with open(datei, "r", encoding="utf-8") as f:
            vorhanden = yaml.safe_load(f) or {}
    eintrag = asdict(modell)
    eintrag.pop("name")
    eintrag["koeffizient"] = float(eintrag["koeffizient"])
    eintrag["exponenten"] = [float(b) for b in eintrag["exponenten"]]
    vorhanden[modell.name] = eintrag
    datei.parent.mkdir(parents=True, exist_ok=True)
    with open(datei, "w", encoding="utf-8") as f:
        f.write("# Eigene Modelle (Potenzansätze), angelegt mit modellvergleich.fit_potenzansatz.\n")
        yaml.safe_dump(vorhanden, f, allow_unicode=True, sort_keys=False)
    return datei


def verfuegbare_modelle(datei: Path | None = None) -> dict[str, str]:
    """{Name: Anzeigename} aller Literatur- und eigenen Modelle."""
    namen = {n: m.titel for n, m in LITERATURMODELLE.items()}
    namen.update({n: m.titel for n, m in lade_eigene_modelle(datei).items()})
    return namen


def modell_titel(name: str, datei: Path | None = None) -> str:
    alle = verfuegbare_modelle(datei)
    if name not in alle:
        raise KeyError(f"Unbekanntes Modell '{name}'. Verfügbar: {sorted(alle)}")
    return alle[name]


def vorhersage(daten: pd.DataFrame, name: str, datei: Path | None = None,
               p: AuswerteParameter | None = None) -> np.ndarray:
    """Modellvorhersage für jede Zeile einer Betriebspunkt-Tabelle."""
    if name in LITERATURMODELLE:
        p = p or AuswerteParameter()
        m = LITERATURMODELLE[name]
        werte = []
        for _, r in daten.iterrows():
            x = modelleingaben(r["Velocity_mean_m_s"], r["BubbleLength_mean_m"], r["SlugLength_mean_m"],
                               r["d_h_m"], r["D_CO2_m2_s"], r["Geometrie"],
                               r["GasVelocity_m_s"], r["LiquidVelocity_m_s"], p)
            werte.append(float(m.funktion(x)))
        return np.array(werte, dtype=float)
    eigene = lade_eigene_modelle(datei)
    if name not in eigene:
        raise KeyError(f"Unbekanntes Modell '{name}'. Verfügbar: {sorted(verfuegbare_modelle(datei))}")
    return eigene[name].berechne(daten)


# =============================================================================
# Anpassen und Bewerten
# =============================================================================

def fit_potenzansatz(daten: pd.DataFrame, zielgroesse: str, variablen: list[str], name: str,
                     titel: str = "", ohne_ausgeschlossene: bool = True) -> EigenesModell:
    """
    Passt y = a · Π x_k^b_k an (kleinste Quadrate auf log y).

    Verwendet nur Zeilen mit positiven, endlichen Werten aller beteiligten
    Spalten; mit ``ohne_ausgeschlossene`` außerdem nur Betriebspunkte ohne
    ``manual_exclude``.
    """
    d = daten
    if ohne_ausgeschlossene and "manual_exclude" in d.columns:
        d = d[~d["manual_exclude"].astype(bool)]
    spalten = [zielgroesse] + list(variablen)
    werte = d[spalten].apply(pd.to_numeric, errors="coerce")
    ok = (werte > 0).all(axis=1) & np.isfinite(werte).all(axis=1)
    werte = werte[ok]
    if len(werte) < len(variablen) + 2:
        raise ValueError(f"Zu wenige gültige Punkte ({len(werte)}) für {len(variablen) + 1} Parameter.")
    X = np.column_stack([np.ones(len(werte))] + [np.log(werte[v].values) for v in variablen])
    y = np.log(werte[zielgroesse].values)
    koeff, *_ = np.linalg.lstsq(X, y, rcond=None)
    y_fit = X @ koeff
    r2_log = 1 - np.sum((y - y_fit) ** 2) / np.sum((y - y.mean()) ** 2)
    modell = EigenesModell(
        name=name, titel=titel or name, zielgroesse=zielgroesse, variablen=list(variablen),
        koeffizient=float(np.exp(koeff[0])), exponenten=[float(b) for b in koeff[1:]],
        datengrundlage=sorted(d.loc[werte.index, "Kanal"].unique()) if "Kanal" in d.columns else [],
        n_punkte=int(len(werte)), r2_log=float(r2_log), erstellt=date.today().isoformat())
    modell.mape_prozent = statistik(werte[zielgroesse].values, modell.berechne(werte))["MAPE_%"]
    return modell


def statistik(gemessen, berechnet, band_prozent: float = 15.0) -> dict:
    """
    Abweichung berechnet gegen gemessen (nur Paare mit positiven, endlichen Werten).

    MAPE_%      mittlere absolute relative Abweichung
    Bias_%      Median der relativen Abweichung (positiv = Modell zu hoch)
    RMSE        Wurzel der mittleren quadratischen Abweichung (Einheit der Zielgröße)
    im_Band_%   Anteil der Punkte innerhalb ±band_prozent
    """
    g = np.asarray(gemessen, dtype=float)
    b = np.asarray(berechnet, dtype=float)
    ok = np.isfinite(g) & np.isfinite(b) & (g > 0) & (b > 0)
    if ok.sum() == 0:
        return {"n": 0, "MAPE_%": np.nan, "Bias_%": np.nan, "RMSE": np.nan, "im_Band_%": np.nan}
    rel = (b[ok] - g[ok]) / g[ok]
    return {"n": int(ok.sum()), "MAPE_%": float(np.mean(np.abs(rel)) * 100),
            "Bias_%": float(np.median(rel) * 100), "RMSE": float(np.sqrt(np.mean((b[ok] - g[ok]) ** 2))),
            "im_Band_%": float(np.mean(np.abs(rel) <= band_prozent / 100) * 100)}


def vergleichstabelle(daten: pd.DataFrame, zielgroesse: str, modelle: list[str],
                      datei: Path | None = None, band_prozent: float = 15.0,
                      ohne_ausgeschlossene: bool = True) -> pd.DataFrame:
    """Statistik je Modell gegenüber der Zielgröße, sortiert nach MAPE."""
    d = daten
    if ohne_ausgeschlossene and "manual_exclude" in d.columns:
        d = d[~d["manual_exclude"].astype(bool)]
    zeilen = []
    for m in modelle:
        s = statistik(d[zielgroesse], vorhersage(d, m, datei), band_prozent)
        zeilen.append({"Modell": m, "Titel": modell_titel(m, datei), **s})
    return pd.DataFrame(zeilen).sort_values("MAPE_%", na_position="last").reset_index(drop=True)


def lade_betriebspunkte_mehrerer_kanaele(ergebnis_ordner: Path, kanaele: list[str] | None = None) -> pd.DataFrame:
    """Betriebspunkt-Tabellen mehrerer Kanäle untereinander, mit Spalte ``Kanal``."""
    from .ergebnisse import lade_betriebspunkte, vorhandene_kanaele
    kanaele = kanaele or vorhandene_kanaele(ergebnis_ordner)
    teile = []
    for k in kanaele:
        bp = lade_betriebspunkte(ergebnis_ordner, k)
        bp.insert(0, "Kanal", k)
        teile.append(bp)
    if not teile:
        raise FileNotFoundError(f"Keine Ergebnisse in {ergebnis_ordner}. Erst auswertung.py ausführen.")
    return pd.concat(teile, ignore_index=True)
