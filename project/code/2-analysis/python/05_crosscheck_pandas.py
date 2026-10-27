"""05: Cek silang SQL vs pandas. Hitung ulang TTT, minggu pertama, dan NG rate dengan pandas
dari data bersih, lalu bandingkan dengan hasil views SQL (04). Harus identik.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
import pandas as pd
import common as C

clean = pd.read_csv(C.CLEAN / "daily_output_clean.csv")
tgt = pd.read_csv(C.ANON / "station_target.csv").set_index("station_code").target_per_day
v = clean[clean.valid == 1].copy()
v["target"] = v.station_code.map(tgt)
v["meets"] = (v.ok_qty >= v.target).astype(int)
v = v.sort_values(["operator_code", "work_day"]).reset_index(drop=True)
v["valid_day_py"] = v.groupby("operator_code").cumcount() + 1

rows = []
for op, g in v.groupby("operator_code"):
    m = g.meets.to_numpy()
    ttt = None
    for i in range(len(m) - 2):                       # hari pertama dari 3 hari berturut-turut
        if m[i] and m[i + 1] and m[i + 2]:
            ttt = int(g.valid_day_py.iloc[i])
            break
    w1 = g[g.valid_day_py <= 5]
    week1 = (w1.ok_qty / w1.target).mean()
    ng_all = g.ng_qty.sum() / (g.ok_qty + g.ng_qty).sum()
    rows.append(dict(operator_code=op, ttt_pandas=ttt, week1_pandas=week1, ng_pandas=ng_all))
py = pd.DataFrame(rows)

sql = pd.read_csv(C.RES2 / "ttt_per_operator.csv")
m = sql.merge(py, on="operator_code")
out = pd.DataFrame({
    "operator_code": m.operator_code,
    "ttt_sql": m.ttt_day.astype("Int64"),
    "ttt_pandas": m.ttt_pandas.astype("Int64"),
    "week1_sql": m.week1_avg_pct.round(6),
    "week1_pandas": m.week1_pandas.round(6),
    "ng_sql": m.ng_rate_all.round(6),
    "ng_pandas": m.ng_pandas.round(6),
})
out["ttt_cocok"] = (out.ttt_sql == out.ttt_pandas).astype(int)
out["week1_selisih"] = (out.week1_sql - out.week1_pandas).abs().round(9)
out["ng_selisih"] = (out.ng_sql - out.ng_pandas).abs().round(9)
out["cocok"] = ((out.ttt_cocok == 1) & (out.week1_selisih < 1e-6) & (out.ng_selisih < 1e-6)).astype(int)
out.to_csv(C.RES2 / "crosscheck_sql_pandas.csv", index=False)
print(out.to_string(index=False))
print(f"cocok: {out.cocok.sum()}/{len(out)} operator")
assert out.cocok.sum() == len(out), "SQL dan pandas tidak cocok"
