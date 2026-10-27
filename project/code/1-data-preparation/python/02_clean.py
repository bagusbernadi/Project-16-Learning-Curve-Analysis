"""02: Pembersihan data. Setiap hari kerja diberi status valid atau tidak valid beserta alasannya.

Aturan (lihat docs/definitions.md dan docs/cleaning_decisions.md):
- tidak hadir          : present = 0 -> dilewati (bukan dihitung nol)
- jam tidak penuh      : work_hours < 7 -> dilewati dari kurva dan streak
- output 0             : hadir tetapi ok_qty = 0 -> dilewati (dicurigai data hilang/mesin berhenti)
- pindah stasiun       : station_code berbeda dari stasiun utama operator -> dilewati,
                         time-to-target hanya dari hari sebelum pindah
Hari valid diberi nomor urut hari kerja ke-n (valid_day). Nomor ini dipakai kurva dan TTT.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pandas as pd
import common as C

MIN_HOURS = 7.0
d = pd.read_csv(C.ANON / "daily_output.csv")
newop = pd.read_csv(C.ANON / "new_operator.csv")
d = d.merge(newop[["operator_code", "station_code"]].rename(columns={"station_code": "station_utama"}),
            on="operator_code", how="left")
d = d.sort_values(["operator_code", "work_day"]).reset_index(drop=True)

reason = []
for r in d.itertuples(index=False):
    if r.present == 0:
        reason.append("tidak hadir")
    elif r.station_code != r.station_utama:
        reason.append("pindah stasiun")
    elif r.work_hours < MIN_HOURS:
        reason.append("jam tidak penuh")
    elif r.ok_qty == 0:
        reason.append("output 0")
    else:
        reason.append("valid")
d["alasan"] = reason
d["valid"] = (d.alasan == "valid").astype(int)
d["valid_day"] = d.groupby("operator_code").valid.cumsum().where(d.valid == 1)
d["target"] = d.station_code.map(pd.read_csv(C.ANON / "station_target.csv")
                                 .set_index("station_code").target_per_day)
d["pct_target"] = d.ok_qty / d.target
d["ng_rate"] = d.ng_qty / (d.ok_qty + d.ng_qty).where((d.ok_qty + d.ng_qty) > 0)

clean = d.drop(columns=["station_utama"])
clean.to_csv(C.CLEAN / "daily_output_clean.csv", index=False)

# Log cleaning: satu baris per hari yang dilewati (dan alasannya), untuk audit dan Q12
log = d[d.valid == 0][["operator_code", "work_day", "station_code", "alasan"]].copy()
log.to_csv(C.RES1 / "cleaning_log.csv", index=False)

# Q12: audit kualitas data (ringkasan)
total = len(d)
rows = [("baris output harian (operator baru)", total, 1.0)]
for a in ["tidak hadir", "jam tidak penuh", "output 0", "pindah stasiun", "valid"]:
    n = int((d.alasan == a).sum())
    rows.append((a, n, n / total))
dq = pd.DataFrame(rows, columns=["kategori", "jumlah", "proporsi"])
dq["proporsi"] = dq.proporsi.round(4)
dq.to_csv(C.RES1 / "data_quality.csv", index=False)

# Hari valid per operator (cek kecukupan data)
per_op = d.groupby("operator_code").agg(hari_valid=("valid", "sum"), baris=("valid", "size")).reset_index()
per_op.to_csv(C.RES1 / "valid_days_per_operator.csv", index=False)
print(dq.to_string(index=False))
print(per_op.to_string(index=False))
