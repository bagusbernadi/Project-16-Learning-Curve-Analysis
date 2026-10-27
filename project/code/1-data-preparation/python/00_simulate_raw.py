"""00: Simulasi data mentah output harian (seeded). Nama operator dan produk adalah karangan.

Ground truth (common.TRUE) dipakai di sini untuk membangkitkan data. Analisis
hilir tidak membaca TRUE; hanya 11_recovery.py yang membandingkan hasil fit dengan TRUE.
Output: data/raw/raw_output.csv (tidak di-commit; dibuat ulang dari seed).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
import pandas as pd
import common as C
from common import ANON_FACTOR

START = pd.Timestamp("2026-09-01")   # tanggal kalender awal (karangan)

rng = np.random.default_rng(C.SEED)
T = C.TRUE
FAKE_NAMES = ["Rina Maharani", "Dimas Prakoso", "Sari Wulandari", "Yoga Pratama", "Ayu Lestari",
              "Fajar Nugroho", "Intan Permata", "Bayu Setiawan", "Nadia Kusuma", "Galih Ramadhan"]
FAKE_EXP = ["Wahyu Hidayat", "Dewi Anggraini", "Rudi Cahyono", "Tina Marlina", "Agus Salim",
            "Lia Safitri", "Hendra Gunawan", "Mira Oktaviani", "Eko Putranto", "Sinta Rahayu",
            "Andi Firmansyah", "Fitri Handayani"]
STATION_RAW = {"ST-A": "Lini Assembly 1", "ST-B": "Lini Bonding 2", "ST-C": "Lini Finishing 3"}
PRODUCT = ["PLC-1x8-Kode-K", "PLC-1x8-Kode-L"]
rows = []
truth = []   # ground truth per operator (hanya untuk 11_recovery.py)

# Operator baru
ops = list(C.NEW_OPERATORS.items())
for k, (op, (st0, batch, mentor)) in enumerate(ops):
    name = FAKE_NAMES[k]
    p_i = T["PLATEAU_MEAN"] + rng.normal(0, T["PLATEAU_SD"])
    f1_i = float(np.clip(T["F1_MEAN"] + rng.normal(0, T["F1_SD"]), 0.05, 0.6))
    b_i = T["B_STATION"][st0] * np.exp(rng.normal(0, T["B_OP_SD_LOG"]))
    truth.append(dict(operator_code=op, nama_operator=name, P_true=p_i, F1_true=f1_i, b_true=b_i,
                      station_code=st0))
    present_days, slot = 0, 0
    while slot < C.OBS_SLOTS:
        slot += 1
        if op in C.LEAVER and present_days >= C.LEAVER[op]:
            break
        absent = rng.random() < T["ABSENT_P"]
        st = st0
        if op in C.MOVER and present_days + 1 >= C.MOVER[op][1]:
            st = C.MOVER[op][0]
        if absent:
            rows.append(dict(tanggal=(START + pd.Timedelta(days=slot - 1)).strftime("%Y-%m-%d"), nama_operator=name, nama_stasiun=STATION_RAW[st],
                             produk=PRODUCT[k % 2], batch_nama=batch, mentor_nama=mentor,
                             jam_kerja=0.0, hadir=0, output_ok=0, output_ng=0, slot=slot, keterangan=""))
            continue
        present_days += 1
        d = present_days
        f = p_i - (p_i - f1_i) * d ** (-b_i)                  # power law, f = output / target
        noise = np.exp(rng.normal(0, T["NOISE_SD_LOG"]))
        ok_anon = C.STATIONS[st]["target"] * f * noise         # skala anonim
        ng_frac = T["NG_BASE"] + T["NG_START"] * np.exp(-T["NG_DECAY"] * d)
        ng_anon = ok_anon * ng_frac / (1 - ng_frac)
        hours = 8.0
        note = ""
        if rng.random() < T["PARTIAL_P"]:
            hours = round(rng.uniform(*T["PARTIAL_HOURS"]), 1)
            ok_anon *= hours / 8.0
            ng_anon *= hours / 8.0
            note = "jam pulang awal"
        if rng.random() < T["ZERO_P"]:
            ok_anon, ng_anon, note = 0.0, 0.0, "mesin berhenti (catatan)"
        raw_ok = round(ok_anon / ANON_FACTOR)
        raw_ng = round(ng_anon / ANON_FACTOR)
        rows.append(dict(tanggal=(START + pd.Timedelta(days=slot - 1)).strftime("%Y-%m-%d"), nama_operator=name, nama_stasiun=STATION_RAW[st],
                         produk=PRODUCT[k % 2], batch_nama=batch, mentor_nama=mentor,
                         jam_kerja=hours, hadir=1, output_ok=int(raw_ok), output_ng=int(raw_ng),
                         slot=slot, keterangan=note))

# Operator berpengalaman (pembanding, tidak dianalisis per hari kurva)
for k in range(3 * C.EXPERIENCED_PER_STATION):
    st = list(C.STATIONS)[k // C.EXPERIENCED_PER_STATION]
    name = FAKE_EXP[k]
    for slot in range(1, C.OBS_SLOTS + 1):
        noise = np.exp(rng.normal(0, T["EXP_NOISE_SD_LOG"]))
        ok_anon = C.STATIONS[st]["target"] * T["EXP_PLATEAU"] * noise
        ng_frac = T["NG_BASE"]
        raw_ok = round(ok_anon / ANON_FACTOR)
        raw_ng = round(ok_anon * ng_frac / (1 - ng_frac) / ANON_FACTOR)
        rows.append(dict(tanggal=(START + pd.Timedelta(days=slot - 1)).strftime("%Y-%m-%d"), nama_operator=name, nama_stasiun=STATION_RAW[st],
                         produk=PRODUCT[k % 2], batch_nama="Senior", mentor_nama="-",
                         jam_kerja=8.0, hadir=1, output_ok=int(raw_ok), output_ng=int(raw_ng),
                         slot=slot, keterangan=""))

raw = pd.DataFrame(rows)
pd.DataFrame(truth).to_csv(C.RAW / "ground_truth_operator.csv", index=False)
raw.to_csv(C.RAW / "raw_output.csv", index=False)
pd.DataFrame([dict(nama_stasiun=STATION_RAW[s], target_harian=round(v["target"] / ANON_FACTOR))
              for s, v in C.STATIONS.items()]).to_csv(C.RAW / "raw_station_target.csv", index=False)
print(f"raw rows: {len(raw)} -> {C.RAW / 'raw_output.csv'}")
