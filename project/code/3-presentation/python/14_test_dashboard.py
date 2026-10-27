"""14: Uji dashboard dengan Streamlit AppTest. Setiap halaman harus berjalan tanpa exception, dan
angka median time-to-target yang tampil harus sama dengan results/2-analysis/ttt_per_operator.csv.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pandas as pd
from streamlit.testing.v1 import AppTest
import common as C

APP = C.ROOT / "code" / "3-presentation" / "streamlit" / "app.py"
at = AppTest.from_file(str(APP), default_timeout=60).run()
results = {}
results["halaman Ringkasan dijalankan tanpa error"] = not at.exception
med_shown = [m.value for m in at.metric]
med_csv = float(pd.read_csv(C.RES2 / "ttt_per_operator.csv").ttt_day.median())
results["median pada metrik sama dengan CSV"] = any(f"{med_csv:g}" in str(v) for v in med_shown)
results["tiga metrik di Ringkasan"] = len(at.metric) == 3

for page in ["Kurva per Operator", "Perbandingan Stasiun"]:
    at.sidebar.radio[0].set_value(page).run()
    results[f"halaman {page} tanpa error"] = not at.exception
    results[f"halaman {page} punya grafik"] = len(at.get("plotly_chart")) >= 1

at.sidebar.radio[0].set_value("Kurva per Operator").run()
at.selectbox[0].set_value("OP-05").run()
results["pilih operator OP-05 tanpa error"] = not at.exception

ok = all(results.values())
out = pd.DataFrame(list(results.items()), columns=["pemeriksaan", "hasil"])
out["hasil"] = out.hasil.map({True: "lulus", False: "gagal"})
out.to_csv(C.RES3 / "dashboard_test.csv", index=False)
print(out.to_string(index=False))
assert ok, "uji dashboard gagal"
