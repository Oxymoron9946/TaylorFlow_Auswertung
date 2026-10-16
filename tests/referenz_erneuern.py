# -*- coding: utf-8 -*-
"""
Vergleicht eine Neuauswertung der mitgelieferten Messdaten mit tests/referenz/
und schreibt die Referenz auf Wunsch neu.

    python tests/referenz_erneuern.py              nur vergleichen
    python tests/referenz_erneuern.py --schreiben  Referenz überschreiben

Gerechnet wird mit den Standardwerten aus taylorflow/parameter.py (nicht mit
config.py), wie im Regressionstest.
"""

import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

WURZEL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WURZEL))

from taylorflow import protokoll  # noqa: E402
from taylorflow.einlesen import finde_messreihen, lade_ausschluesse  # noqa: E402
from taylorflow.ergebnisse import CSV_FORMAT, LESEN, lade_betriebspunkte, lade_profile, speichere  # noqa: E402
from taylorflow.parameter import AuswerteParameter  # noqa: E402
from taylorflow.pipeline import werte_kanal_aus  # noqa: E402

REFERENZ = WURZEL / "tests" / "referenz"
AUSZUG_Z = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.72]


def main(schreiben: bool) -> int:
    ordner = Path(tempfile.mkdtemp())
    aus = lade_ausschluesse(WURZEL / "config" / "ausschluesse.yaml")
    protokoll.starte(ordner / "protokoll.txt")
    for r in finde_messreihen(WURZEL / "data" / "raw"):
        e = werte_kanal_aus(r, AuswerteParameter(), aus, WURZEL / "data" / "calibrated_c_database.json",
                            ausgabe=lambda *a: None)
        speichere(e, ordner, aus, ausgabe=lambda *a: None)

    unterschiede = 0
    for kanal in sorted(p.name for p in ordner.iterdir() if p.is_dir()):
        prof = lade_profile(ordner, kanal)
        prof = prof[prof["Position_z_m"].round(6).isin(AUSZUG_Z)].reset_index(drop=True)
        for neu, datei in [(lade_betriebspunkte(ordner, kanal), f"{kanal}_betriebspunkte.csv"),
                           (prof, f"{kanal}_profile_auszug.csv")]:
            alt_pfad = REFERENZ / datei
            if alt_pfad.exists():
                alt = pd.read_csv(alt_pfad, low_memory=False, **LESEN)
                for c in sorted(set(alt.columns) | set(neu.columns)):
                    if c not in neu.columns or c not in alt.columns or len(alt) != len(neu):
                        print(f"{datei}: Spalte {c} nur in {'Referenz' if c in alt.columns else 'Neuauswertung'}")
                        unterschiede += 1
                    elif pd.api.types.is_numeric_dtype(alt[c]):
                        a, b = alt[c].to_numpy(float), neu[c].to_numpy(float)
                        if not np.array_equal(a, b, equal_nan=True):
                            with np.errstate(divide="ignore", invalid="ignore"):
                                rel = np.nanmax(np.abs(b - a) / np.abs(a)) * 100
                            print(f"{datei}: {c} weicht ab, max. {rel:.3g} %")
                            unterschiede += 1
                    elif not (alt[c].fillna("").astype(str) == neu[c].fillna("").astype(str)).all():
                        print(f"{datei}: {c} (Text) weicht ab")
                        unterschiede += 1
            else:
                print(f"{datei}: neu")
            if schreiben:
                neu.to_csv(alt_pfad, index=False, **CSV_FORMAT)

    print(f"\n{unterschiede} Unterschiede." + (" Referenz neu geschrieben." if schreiben else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main("--schreiben" in sys.argv))
