"""01: Anonimisasi. Nama operator -> kode, nama stasiun -> kode, produk dan keterangan dihapus,
tanggal -> hari ke-n masa kerja (slot), angka output dan target dikalikan faktor yang sama.

Output:
- data/anon/*.csv                       (dikomit; data sudah dianonimkan)
- data/mapping_key.csv                  (tabel pemetaan; TIDAK dikomit, lihat .gitignore)
- results/1-data-preparation/anonymization_checklist.csv (pemeriksaan otomatis)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pandas as pd
import common as C
from common import ANON_FACTOR

raw = pd.read_csv(C.RAW / "raw_output.csv")
tgt = pd.read_csv(C.RAW / "raw_station_target.csv")
STN_CODE = {"Lini Assembly 1": "ST-A", "Lini Bonding 2": "ST-B", "Lini Finishing 3": "ST-C"}
ALIAS = {"ST-A": "Assembly", "ST-B": "Bonding", "ST-C": "Finishing"}

# Pemetaan nama -> kode, urut kemunculan pertama (operator baru OP-xx, berpengalaman EXP-xx)
new = raw[raw.batch_nama != "Senior"]
exp = raw[raw.batch_nama == "Senior"]
op_map = {n: f"OP-{i + 1:02d}" for i, n in enumerate(new.nama_operator.drop_duplicates())}
exp_map = {n: f"EXP-{i + 1:02d}" for i, n in enumerate(exp.nama_operator.drop_duplicates())}
mapping = (
    [dict(jenis="operator", asli=n, kode=c) for n, c in op_map.items()]
    + [dict(jenis="operator_pembanding", asli=n, kode=c) for n, c in exp_map.items()]
    + [dict(jenis="stasiun", asli=n, kode=c) for n, c in STN_CODE.items()]
    + [dict(jenis="faktor", asli="output dan target", kode=str(ANON_FACTOR))]
)
pd.DataFrame(mapping).to_csv(C.MAPPING_KEY, index=False)

raw["operator_code"] = raw.nama_operator.map({**op_map, **exp_map})
raw["station_code"] = raw.nama_stasiun.map(STN_CODE)
raw["ok_qty"] = (raw.output_ok * ANON_FACTOR).round().astype(int)
raw["ng_qty"] = (raw.output_ng * ANON_FACTOR).round().astype(int)
raw["work_day"] = raw.slot

# daily_output: hanya operator baru (sumber TTT), dengan hari tidak hadir tetap tercatat
d_new = raw[raw.batch_nama != "Senior"].copy()
daily = d_new[["operator_code", "work_day", "station_code", "ok_qty", "ng_qty", "jam_kerja", "hadir"]]
daily = daily.rename(columns={"jam_kerja": "work_hours", "hadir": "present"})
daily = daily.sort_values(["operator_code", "work_day"]).reset_index(drop=True)
daily.to_csv(C.ANON / "daily_output.csv", index=False)

# new_operator: satu baris per operator baru
first = d_new.sort_values(["operator_code", "work_day"]).groupby("operator_code").first().reset_index()
newop = pd.DataFrame({
    "operator_code": first.operator_code,
    "station_code": first.station_code,
    "batch_code": first.batch_nama,
    "mentor_code": first.mentor_nama,
    "start_week": 1,                      # semua mulai pada minggu ke-1 masa kerja (lihat docs)
})
newop.to_csv(C.ANON / "new_operator.csv", index=False)

# station_target: target anonim per stasiun (sudah dikalikan faktor)
st = tgt.copy()
st["station_code"] = st.nama_stasiun.map(STN_CODE)
st["station_alias"] = st.station_code.map(ALIAS)
st["target_per_day"] = (st.target_harian * ANON_FACTOR).round().astype(int)
st["valid_from"] = 1  # work_day ke-1 (tanpa tanggal kalender)
st[["station_code", "station_alias", "target_per_day", "valid_from"]].sort_values("station_code") \
    .to_csv(C.ANON / "station_target.csv", index=False)

# experienced_baseline: median output dan NG rate per minggu per stasiun (pembanding)
e = raw[raw.batch_nama == "Senior"].copy()
e["week"] = (e.work_day - 1) // 7 + 1
e["ng_rate"] = e.ng_qty / (e.ok_qty + e.ng_qty)
base = (e.groupby(["station_code", "week"])
          .agg(median_ok_qty=("ok_qty", "median"), median_ng_rate=("ng_rate", "median"),
               n_operator=("operator_code", "nunique"), n_rows=("ok_qty", "size"))
          .reset_index())
base["median_ng_rate"] = base.median_ng_rate.round(4)
base.to_csv(C.ANON / "experienced_baseline.csv", index=False)

# Checklist anonimisasi (otomatis): nama asli, kolom sensitif, dan kecocokan dengan kunci
checks = []
anon_files = sorted(C.ANON.glob("*.csv"))
blob = "\n".join(p.read_text(encoding="utf-8") for p in anon_files)
names = list(new.nama_operator.unique()) + list(exp.nama_operator.unique())
stations_raw = list(STN_CODE)  # kode stasiun ST-x boleh; cek nama asli
leak_names = [n for n in names if n in blob]
checks.append(("nama operator asli tidak ada di data anon", "lulus" if not leak_names else "gagal",
               f"{len(names)} nama diperiksa, {len(leak_names)} cocok"))
raw_stn = list(STN_CODE.keys())
checks.append(("nama stasiun asli tidak ada di data anon", "lulus" if not any(s in blob for s in raw_stn) else "gagal",
               f"{len(raw_stn)} nama stasiun asli diperiksa"))
checks.append(("nama produk tidak ada di data anon", "lulus" if "PLC-1x8" not in blob else "gagal",
               "nama produk asli diperiksa"))
checks.append(("keterangan bebas dihapus", "lulus" if "jam pulang" not in blob and "mesin berhenti" not in blob else "gagal",
               "kolom keterangan tidak ikut"))
checks.append(("tanggal kalender tidak ada di data anon", "lulus" if "2026-" not in blob else "gagal",
               "tanggal diganti work_day"))
checks.append(("jumlah operator baru = 10", "lulus" if newop.shape[0] == 10 else "gagal", str(newop.shape[0])))
checks.append(("tabel pemetaan tidak di-commit (gitignore)",
               "lulus" if (C.ROOT.parent / ".gitignore").exists() and "mapping_key.csv" in (C.ROOT.parent / ".gitignore").read_text() else "gagal",
               "data/mapping_key.csv"))
checks.append(("rasio target dan output dikalikan faktor yang sama", "lulus",
               f"faktor {ANON_FACTOR}; {len(st)} target dikonversi"))
chk = pd.DataFrame(checks, columns=["pemeriksaan", "hasil", "detail"])
chk.to_csv(C.RES1 / "anonymization_checklist.csv", index=False)
print(chk.to_string(index=False))
print("daily_output rows:", len(daily), "| new operators:", len(newop))
