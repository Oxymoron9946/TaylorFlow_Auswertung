# -*- coding: utf-8 -*-
"""
Regressionstest: Eine komplette Neuauswertung der mitgelieferten Rohdaten muss
die eingefrorenen Referenzwerte in tests/referenz/ exakt reproduzieren.

Schlägt der Test nach einer beabsichtigten Änderung der Rechnung fehl, wird
die Referenz neu erzeugt (siehe Handbuch, Kapitel „Erweitern“).
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from taylorflow import protokoll
from taylorflow.einlesen import finde_messreihen, lade_ausschluesse
from taylorflow.ergebnisse import lade_betriebspunkte, lade_profile, speichere
from taylorflow.parameter import AuswerteParameter
from taylorflow.pipeline import werte_kanal_aus

WURZEL = Path(__file__).resolve().parents[1]
REFERENZ = WURZEL / "tests" / "referenz"
F = dict(sep=";", decimal=",", encoding="utf-8-sig", float_precision="round_trip")


@pytest.fixture(scope="module")
def ergebnisordner(tmp_path_factory):
    ordner = tmp_path_factory.mktemp("ergebnisse")
    aus = lade_ausschluesse(WURZEL / "config" / "ausschluesse.yaml")
    protokoll.starte(ordner / "protokoll.txt")
    for r in finde_messreihen(WURZEL / "data" / "raw"):
        e = werte_kanal_aus(r, AuswerteParameter(), aus, WURZEL / "data" / "calibrated_c_database.json",
                            ausgabe=lambda *a: None)
        speichere(e, ordner, aus, ausgabe=lambda *a: None)
    return ordner


def _vergleiche(neu: pd.DataFrame, ref: pd.DataFrame):
    assert list(neu.columns) == list(ref.columns)
    assert len(neu) == len(ref)
    for c in ref.columns:
        if pd.api.types.is_numeric_dtype(ref[c]):
            np.testing.assert_array_equal(neu[c].to_numpy(float), ref[c].to_numpy(float), err_msg=c)
        else:
            assert (neu[c].fillna("").astype(str) == ref[c].fillna("").astype(str)).all(), c


KANAELE = sorted(p.name.replace("_betriebspunkte.csv", "") for p in REFERENZ.glob("*_betriebspunkte.csv"))


@pytest.mark.parametrize("kanal", KANAELE)
def test_betriebspunkte_unveraendert(ergebnisordner, kanal):
    _vergleiche(lade_betriebspunkte(ergebnisordner, kanal),
                pd.read_csv(REFERENZ / f"{kanal}_betriebspunkte.csv", **F))


@pytest.mark.parametrize("kanal", KANAELE)
def test_profile_unveraendert(ergebnisordner, kanal):
    neu = lade_profile(ergebnisordner, kanal)
    neu = neu[neu["Position_z_m"].round(6).isin([0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.72])].reset_index(drop=True)
    _vergleiche(neu, pd.read_csv(REFERENZ / f"{kanal}_profile_auszug.csv", low_memory=False, **F))
