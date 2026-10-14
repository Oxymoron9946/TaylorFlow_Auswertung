# -*- coding: utf-8 -*-
"""
Speichern und Laden der Ergebnisdateien.

Je Kanal entsteht ein Ordner ``<Ergebnisordner>/<Kanal>/`` mit

    <Kanal>_profile.csv         Profile entlang z, eine Zeile je z und Betriebspunkt
    <Kanal>_betriebspunkte.csv  Kennwerte, eine Zeile je Betriebspunkt
    <Kanal>_meta.json           Programmversion, Zeitpunkt, Quelldatei

Format: Semikolon als Trennzeichen, Dezimalkomma, UTF-8 mit BOM (Excel-tauglich).
Bedeutung aller Spalten: docs/04_auswertung.md.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from . import __version__, protokoll
from .pipeline import KanalErgebnis

CSV_FORMAT = dict(sep=";", decimal=",", encoding="utf-8-sig")
LESEN = dict(CSV_FORMAT, float_precision="round_trip")  # exakt, ohne Rundung beim Einlesen


def kanal_ordner(ergebnis_ordner: Path, kanal: str) -> Path:
    return Path(ergebnis_ordner) / kanal


def speichere(ergebnis: KanalErgebnis, ergebnis_ordner: Path, ausschluesse: dict,
              ausgabe=print) -> Path:
    """Schreibt Profile, Betriebspunkt-Tabelle und Metadaten eines Kanals."""
    kanal = ergebnis.reihe.kanal
    ordner = kanal_ordner(ergebnis_ordner, kanal)
    ordner.mkdir(parents=True, exist_ok=True)
    if not ergebnis.profile:
        raise ValueError(f"Kanal {kanal}: kein Betriebspunkt auswertbar.")

    teile = []
    for name, df in ergebnis.profile.items():
        df = df.copy()
        df.insert(0, "Config_Name", name)
        teile.append(df)
    pd.concat(teile, ignore_index=True).to_csv(ordner / f"{kanal}_profile.csv", index=False, **CSV_FORMAT)

    bp = _kla_ungueltig_markieren(pd.DataFrame(ergebnis.betriebspunkte), kanal,
                                  (ausschluesse.get(kanal) or {}).get("kla_ungueltig") or {})
    bp.to_csv(ordner / f"{kanal}_betriebspunkte.csv", index=False, **CSV_FORMAT)

    meta = {"version": __version__, "zeitpunkt": datetime.now(timezone.utc).isoformat(),
            "kanal": kanal, "quelldatei": ergebnis.reihe.datei.name}
    with open(ordner / f"{kanal}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    ausgabe(f"  Ergebnisse gespeichert in {ordner}")
    return ordner


def _kla_ungueltig_markieren(bp: pd.DataFrame, kanal: str, liste: dict) -> pd.DataFrame:
    """Setzt kLa_log_mean für gelistete Betriebspunkte auf NaN und ergänzt die Begründung."""
    bp = bp.copy()
    bp["manual_exclude"] = False
    bp["manual_exclude_reason"] = ""
    for name, grund in liste.items():
        maske = bp["Config"] == name
        if not maske.any():
            protokoll.warnung(kanal, f"kla_ungueltig: Betriebspunkt '{name}' nicht gefunden")
            continue
        bp.loc[maske, "kLa_log_mean_1_s"] = np.nan
        bp.loc[maske, "manual_exclude"] = True
        bp.loc[maske, "manual_exclude_reason"] = str(grund)
        protokoll.warnung(f"{kanal} | {name}", f"kla_ungueltig aktiv: {grund}")
    return bp


# =============================================================================
# Laden
# =============================================================================

def vorhandene_kanaele(ergebnis_ordner: Path) -> list[str]:
    """Alle Kanäle mit gespeicherten Ergebnissen."""
    ordner = Path(ergebnis_ordner)
    if not ordner.exists():
        return []
    return sorted(p.name for p in ordner.iterdir()
                  if p.is_dir() and (p / f"{p.name}_betriebspunkte.csv").exists())


def lade_betriebspunkte(ergebnis_ordner: Path, kanal: str) -> pd.DataFrame:
    """Kennwerte je Betriebspunkt eines Kanals."""
    return pd.read_csv(kanal_ordner(ergebnis_ordner, kanal) / f"{kanal}_betriebspunkte.csv", **LESEN)


def lade_profile(ergebnis_ordner: Path, kanal: str) -> pd.DataFrame:
    """Profile entlang z aller Betriebspunkte eines Kanals."""
    return pd.read_csv(kanal_ordner(ergebnis_ordner, kanal) / f"{kanal}_profile.csv",
                       low_memory=False, **LESEN)


def profil_eines_betriebspunkts(profile: pd.DataFrame, betriebspunkt: str) -> pd.DataFrame:
    """Teil der Profiltabelle für einen Betriebspunkt (Name wie in Spalte ``Config``)."""
    teil = profile[profile["Config_Name"] == betriebspunkt]
    if teil.empty:
        raise KeyError(f"Betriebspunkt '{betriebspunkt}' nicht gefunden. "
                       f"Vorhanden: {sorted(profile['Config_Name'].unique())}")
    return teil
