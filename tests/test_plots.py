# -*- coding: utf-8 -*-
"""Plot-Optionen aus config.PLOTS und das Skript abbildung.py."""

import pytest

import config
from taylorflow.plots import optionen


def test_config_zeigt_alle_optionen_mit_standardwerten():
    """config.PLOTS soll jede Option sichtbar mit ihrem Standardwert enthalten."""
    assert set(config.PLOTS) == set(optionen.STANDARD)
    for name, block in config.PLOTS.items():
        assert optionen.mische(name, block) == optionen.STANDARD[name], name
        assert set(block) == set(optionen.STANDARD[name]), name


def test_tippfehler_in_option_wird_gemeldet():
    with pytest.raises(KeyError, match="farbskala"):
        optionen.mische("kla_flaeche", {"farbskale": "viridis"})


def test_unbekannter_plot_wird_gemeldet():
    with pytest.raises(KeyError, match="Möglich"):
        optionen.mische("kla_flaech", {})


def test_ein_aus_als_wahrheitswert():
    assert optionen.mische("heatmaps", False)["an"] is False


def test_abbildung_mit_anpassungen(ergebnisordner, tmp_path):
    import abbildung
    pfade = abbildung.erzeuge_abbildung(
        "Glas_Eckig_1000um_72cm_20molCO2_600um", "blasenlaengen_fit", "Gas_0_134_Liq_0_056",
        anpassungen=dict(x_bereich_cm=(0, 40), legende="innen", kennwertkasten=False),
        stil_anpassungen=dict(sprache="en", formate=("png", "pdf")),
        ziel_ordner=tmp_path, dateiname="test", ergebnis_ordner=ergebnisordner)
    assert sorted(p.name for p in pfade) == ["test.pdf", "test.png"]
    assert all(p.stat().st_size > 0 for p in pfade)


@pytest.mark.parametrize("plot", ["kla_flaeche", "nspez_flaeche", "heatmaps", "spalten_flaechen",
                                  "modell_flaechen", "stoffmenge", "druckprofil"])
def test_jeder_plot_laesst_sich_anpassen(ergebnisordner, tmp_path, plot):
    import abbildung
    anpassung = {
        "kla_flaeche": dict(farbskala="viridis", achsen=dict(z=(0, 2)), blickwinkel=(30, 200)),
        "nspez_flaeche": dict(hoehenlinien=False, messpunkte=False, groesse_cm=(10, 8)),
        "heatmaps": dict(felder=["kla", "z95", "n_spez_mol_s_m3"], farbskalen=dict(kla="viridis")),
        "spalten_flaechen": dict(spalten=[dict(spalte="Velocity_mean_m_s", beschriftung="u_B [m/s]")]),
        "modell_flaechen": dict(modelle=["vandu"], titel="Van Du"),
        "stoffmenge": dict(flaeche=False, farbe="tab:red", y_bereich_umol=(0, 1)),
        "druckprofil": dict(einheit="mbar", titel=""),
    }[plot]
    pfade = abbildung.erzeuge_abbildung("Glas_Eckig_1000um_72cm_20molCO2_600um", plot,
                                        "Gas_0_134_Liq_0_056", anpassungen=anpassung,
                                        ziel_ordner=tmp_path, ergebnis_ordner=ergebnisordner)
    assert pfade and all(p.exists() for p in pfade)
