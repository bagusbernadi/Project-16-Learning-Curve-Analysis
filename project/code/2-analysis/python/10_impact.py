"""10: Dampak (Q11). Rumus rancangan:
  hari onboarding dihemat per tahun = (standar - median time-to-target) x jumlah operator baru per tahun
Setara output = hari dihemat x rata-rata target harian per stasiun (skala anonim, estimasi).
Semua angka diberi label estimated. Volume operator baru per tahun TIDAK ada di data: skenario eksplisit.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pandas as pd
import common as C

ttt = pd.read_csv(C.RES2 / "ttt_per_operator.csv")
ci = pd.read_csv(C.RES2 / "curve_ci.csv")
stats_ = pd.read_csv(C.RES2 / "stats_results.csv")
med = float(ttt.ttt_day.median())
ci_med = stats_[(stats_.pertanyaan == "Q1") & stats_.metrik.str.startswith("median")].iloc[0]
lo, hi = float(ci_med.ci_bawah), float(ci_med.ci_atas)
target_avg = pd.read_csv(C.ANON / "station_target.csv").target_per_day.mean()
STANDARD = 30

rows = []
for label, m in (("median data (dasar)", med), ("batas bawah CI median", lo), ("batas atas CI median", hi)):
    for n_per_year in (10, 20, 40):
        hari = (STANDARD - m) * n_per_year
        rows.append(dict(skenario=label, median_ttt=round(m, 2), standar_hari=STANDARD,
                         operator_baru_per_tahun=n_per_year,
                         hari_onboarding_dihemat_per_tahun_estimated=round(hari, 1),
                         output_setara_unit_estimated=round(hari * target_avg, 0),
                         label="estimated; volume operator per tahun = asumsi"))
imp = pd.DataFrame(rows)
imp.to_csv(C.RES2 / "impact_scenarios.csv", index=False)
print(imp.to_string(index=False))
