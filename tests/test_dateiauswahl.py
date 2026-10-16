# -*- coding: utf-8 -*-
"""Auswahl der Messdateien (config.MESSDATEIEN): Liste, "alle" und Auswahlfenster."""

from pathlib import Path

import pytest

from taylorflow import einlesen
from taylorflow.einlesen import waehle_messreihen

ROH = Path(__file__).resolve().parents[1] / "data" / "raw"
GLAS = ROH / "Auswertung_Masse_Glas_Q_1000um_72cm_20molCO2_600um.csv"
PVC = ROH / "Auswertung_Masse_PVC_R_1000um_72cm_20molCO2_600um.csv"


def test_alle_findet_jede_datei_der_messart():
    assert len(waehle_messreihen("alle", "Masse", ROH)) == 5
    assert len(waehle_messreihen("alle", "Druck", ROH)) == 4


def test_feste_liste():
    reihen = waehle_messreihen([PVC, GLAS], "Masse", ROH)
    assert [r.kanal for r in reihen] == ["Glas_Eckig_1000um_72cm_20molCO2_600um",
                                         "PVC_Rund_1000um_72cm_20molCO2_600um"]


def test_dialog_liefert_gewaehlte_dateien(monkeypatch):
    aufrufe = []

    def dialog(messart, startordner):
        aufrufe.append((messart, startordner))
        return [GLAS]

    monkeypatch.setattr(einlesen, "_dateidialog", dialog)
    reihen = waehle_messreihen("dialog", "Masse", ROH, dialog_ordner=ROH / "unterordner")
    assert [r.datei for r in reihen] == [GLAS]
    assert aufrufe == [("Masse", ROH / "unterordner")]


def test_abbruch_im_dialog_ergibt_leere_liste(monkeypatch):
    monkeypatch.setattr(einlesen, "_dateidialog", lambda messart, startordner: [])
    assert waehle_messreihen("dialog", "Masse", ROH) == []


def test_falsche_messart_wird_gemeldet():
    with pytest.raises(ValueError, match="Auswertung_Druck"):
        waehle_messreihen([GLAS], "Druck", ROH)


def test_datei_ohne_numel_spalten_wie_videoauswertung(tmp_path):
    """Dateien der Videoauswertung enthalten GroupCount statt numel_*; das Ergebnis ist dasselbe."""
    import pandas as pd

    from taylorflow.einlesen import lade_ausschluesse, lade_messdaten, messreihe_aus_dateiname
    from taylorflow.parameter import AuswerteParameter

    df = pd.read_csv(GLAS, sep=";")
    ohne = tmp_path / GLAS.name
    df.drop(columns=[c for c in df.columns if c.startswith("numel_")]).to_csv(ohne, sep=";", index=False)
    aus = lade_ausschluesse(ROH.parents[1] / "config" / "ausschluesse.yaml")
    a = lade_messdaten(messreihe_aus_dateiname(GLAS), aus, AuswerteParameter(), ausgabe=lambda *x: None)
    b = lade_messdaten(messreihe_aus_dateiname(ohne), aus, AuswerteParameter(), ausgabe=lambda *x: None)
    assert len(a) == len(b)
    assert (a["numel_BubbleLength_mm"].values == b["numel_BubbleLength_mm"].values).all()


def test_fehlende_datei_wird_gemeldet():
    with pytest.raises(FileNotFoundError):
        waehle_messreihen([ROH / "Auswertung_Masse_X_R_1um_1cm_1molCO2_1um.csv"], "Masse", ROH)
