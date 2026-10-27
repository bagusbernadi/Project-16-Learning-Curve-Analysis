"""11: Uji pemulihan (validasi). Membandingkan parameter kurva yang DITANAM (data/raw/ground_truth_operator.csv)
dengan hasil fit power law dari data (results/2-analysis/curve_params.csv).

Toleransi ditetapkan sebelum melihat hasil: P +-0,05; F1 +-0,10; b +-0,25.
Skrip ini satu-satunya yang membaca ground truth; analisis (04-10) tidak membacanya.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
import pandas as pd
import common as C

TOL = {"P": 0.05, "F1": 0.10, "b": 0.25}
gt = pd.read_csv(C.RAW / "ground_truth_operator.csv")
fit = pd.read_csv(C.RES2 / "curve_params.csv")
m = gt.merge(fit, on="operator_code")
rows = []
for r in m.itertuples(index=False):
    for name, t, f in (("P", r.P_true, r.P_power), ("F1", r.F1_true, r.F1_power), ("b", r.b_true, r.b_power)):
        err = f - t
        rows.append(dict(operator_code=r.operator_code, station_code=r.station_code, parameter=name,
                         nilai_ditanam=round(t, 6), nilai_fit=round(f, 6), selisih=round(err, 6),
                         toleransi=TOL[name], dalam_toleransi=int(abs(err) <= TOL[name])))
rec = pd.DataFrame(rows)

# Ringkasan per parameter
summ = (rec.groupby("parameter")
          .agg(n=("selisih", "size"), mae=("selisih", lambda s: float(np.mean(np.abs(s)))),
               bias=("selisih", "mean"), dalam_toleransi=("dalam_toleransi", "sum"))
          .reset_index())
summ["mae"] = summ.mae.round(6)
summ["bias"] = summ.bias.round(6)
summ.to_csv(C.RES2 / "recovery_summary.csv", index=False)
rec.to_csv(C.RES2 / "recovery_check.csv", index=False)

# Pemulihan efek stasiun: urutan b yang ditanam vs median b hasil fit per stasiun
planted_st = gt.groupby("station_code").b_true.median()
fit_st = m.groupby("station_code").b_power.median()
st = pd.DataFrame({"station_code": planted_st.index, "b_ditanam_median": planted_st.round(6).values,
                   "b_fit_median": fit_st.reindex(planted_st.index).round(6).values})
st["urutan_ditanam"] = st.b_ditanam_median.rank().astype(int)
st["urutan_fit"] = st.b_fit_median.rank().astype(int)
st["urutan_sama"] = (st.urutan_ditanam == st.urutan_fit).astype(int)
st.to_csv(C.RES2 / "recovery_station_order.csv", index=False)

print(summ.to_string(index=False))
print(st.to_string(index=False))
