"""12: Menyiapkan data untuk dashboard (Streamlit). Semua angka berasal dari results/2-analysis.

Aturan "operator tertinggal" (ditetapkan sebelum dashboard dibuat): time-to-target di atas
persentil ke-75 seluruh operator baru.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
import pandas as pd
import common as C

ttt = pd.read_csv(C.RES2 / "ttt_per_operator.csv")
cp = pd.read_csv(C.RES2 / "curve_params.csv")
days = pd.read_csv(C.RES2 / "valid_days_sql.csv")
wk = pd.read_csv(C.RES2 / "ng_week.csv")
hyp = pd.read_csv(C.RES2 / "hypotheses.csv")

p75 = float(np.percentile(ttt.ttt_day, 75))
op = ttt.merge(cp[["operator_code", "P_power", "F1_power", "b_power", "plateau_day_power"]], on="operator_code")
op["tertinggal"] = (op.ttt_day > p75).astype(int)
op[["operator_code", "station_code", "batch_code", "mentor_code", "ttt_day", "reached", "tertinggal",
    "week1_avg_pct", "ng_rate_all", "P_power", "F1_power", "b_power", "plateau_day_power",
    "last_valid_day"]].sort_values("operator_code").round(6).to_csv(C.RES3 / "dashboard_operator.csv", index=False)

# Kurva per operator: data harian dan kurva power law hasil fit (untuk grafik)
def f_power(d, P, F1, b):
    return P - (P - F1) * d ** (-b)

fit_rows = []
for r in cp.itertuples(index=False):
    g = days[days.operator_code == r.operator_code]
    for row in g.itertuples(index=False):
        fit_rows.append(dict(operator_code=r.operator_code, valid_day=int(row.valid_day), kind="harian",
                             pct_target=round(float(row.pct_target), 6), fitted=np.nan))
    for d in range(1, 61):
        fit_rows.append(dict(operator_code=r.operator_code, valid_day=d, kind="kurva",
                             pct_target=np.nan, fitted=round(float(f_power(d, r.P_power, r.F1_power, r.b_power)), 6)))
pd.DataFrame(fit_rows).sort_values(["operator_code", "kind", "valid_day"]).to_csv(
    C.RES3 / "dashboard_kurva.csv", index=False)

# Perbandingan stasiun
st = (op.groupby("station_code")
        .agg(operator=("operator_code", "size"), median_ttt=("ttt_day", "median"),
             min_ttt=("ttt_day", "min"), max_ttt=("ttt_day", "max"), tertinggal=("tertinggal", "sum"))
        .reset_index())
b_st = cp.merge(op[["operator_code", "station_code"]], on="operator_code").groupby("station_code").b_power.median()
st["median_b"] = st.station_code.map(b_st).round(6)
st.to_csv(C.RES3 / "dashboard_stasiun.csv", index=False)

# KPI ringkasan
kpi = pd.DataFrame([
    dict(kpi="median time-to-target (hari kerja valid)", nilai=float(ttt.ttt_day.median())),
    dict(kpi="persen operator mencapai target pada hari 15", nilai=float((ttt.ttt_day <= 15).mean())),
    dict(kpi="persen operator mencapai target pada hari 20", nilai=float((ttt.ttt_day <= 20).mean())),
    dict(kpi="standar perusahaan (hari)", nilai=float(C.STANDARD_DAYS)),
    dict(kpi="batas tertinggal (persentil 75)", nilai=p75),
    dict(kpi="jumlah operator tertinggal", nilai=float(op.tertinggal.sum())),
    dict(kpi="jumlah operator", nilai=float(len(op))),
])
kpi.round(6).to_csv(C.RES3 / "dashboard_kpi.csv", index=False)
hyp.to_csv(C.RES3 / "dashboard_hipotesis.csv", index=False)
print(kpi.to_string(index=False))
print(st.to_string(index=False))
