import sys
from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")
WURZEL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WURZEL))


@pytest.fixture(scope="session")
def ergebnisordner(tmp_path_factory):
    """Vollständige Auswertung der mitgelieferten Messdaten (einmal je Testlauf)."""
    from taylorflow import protokoll
    from taylorflow.einlesen import finde_messreihen, lade_ausschluesse
    from taylorflow.ergebnisse import speichere
    from taylorflow.parameter import AuswerteParameter
    from taylorflow.pipeline import werte_kanal_aus

    ordner = tmp_path_factory.mktemp("ergebnisse")
    aus = lade_ausschluesse(WURZEL / "config" / "ausschluesse.yaml")
    protokoll.starte(ordner / "protokoll.txt")
    for r in finde_messreihen(WURZEL / "data" / "raw"):
        e = werte_kanal_aus(r, AuswerteParameter(), aus, WURZEL / "data" / "calibrated_c_database.json",
                            ausgabe=lambda *a: None)
        speichere(e, ordner, aus, ausgabe=lambda *a: None)
    return ordner
