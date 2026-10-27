"""09: Uji sensitivitas definisi "mencapai target" (docs/definitions.md, bagian sensitivitas).

Variasi: streak 1, 2, 3 hari berturut-turut; ambang 90% dan 100% target; hari jam tidak penuh
dilewati (dasar) atau dimasukkan. Untuk tiap kombinasi: median TTT, jumlah operator yang
mencapai target, dan p-value Wilcoxon terhadap 30 hari. Konfigurasi dasar tidak diubah
berdasarkan hasil ini.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
import pandas as pd
from scipy import stats
import common as C

clean = pd.read_csv(C.CLEAN / "daily_output_clean.csv")
tgt = pd.read_csv(C.ANON / "station_target.csv").set_index("station_code").target_per_day
clean["target"] = clean.station_code.map(tgt)
newop = clean.sort_values(["operator_code", "work_day"])


def ttt_for(streak, thr, include_partial):
    out = {}
    for op, g in newop.groupby("operator_code", sort=True):
        g = g.sort_values("work_day")
        ok_base = (g.present == 1) & (g.alasan.isin(["valid", "jam tidak penuh"]))
        mask = ok_base if include_partial else (ok_base & (g.alasan == "valid"))
        h = g[mask]
        m = (h.ok_qty >= thr * h.target).to_numpy()
        found = None
        for i in range(len(m) - streak + 1):
            if m[i:i + streak].all():
                found = i + 1                      # hari kerja ke-n pada hari pertama streak
                break
        out[op] = found
    return out


rows = []
for streak in (1, 2, 3):
    for thr in (0.9, 1.0):
        for inc in (False, True):
            r = ttt_for(streak, thr, inc)
            vals = np.array([v for v in r.values() if v is not None], dtype=float)
            reached = len(vals)
            n = len(r)
            if reached >= 2:
                p = float(stats.wilcoxon(vals - 30, alternative="less").pvalue)
            else:
                p = np.nan
            rows.append(dict(streak_hari=streak, ambang_persen=int(thr * 100),
                             jam_tidak_penuh="dimasukkan" if inc else "dilewati",
                             operator_mencapai=reached, operator_total=n,
                             median_ttt=float(np.median(vals)) if reached else np.nan,
                             min_ttt=float(vals.min()) if reached else np.nan,
                             max_ttt=float(vals.max()) if reached else np.nan,
                             p_wilcoxon_vs30=p,
                             dasar=int(streak == 3 and thr == 1.0 and not inc)))
sens = pd.DataFrame(rows)
base = sens.loc[sens.dasar == 1].median_ttt.iloc[0]
sens["selisih_median_vs_dasar"] = sens.median_ttt - base
for c in ("median_ttt", "min_ttt", "max_ttt", "p_wilcoxon_vs30", "selisih_median_vs_dasar"):
    sens[c] = sens[c].round(6)
sens.to_csv(C.RES2 / "sensitivity_ttt.csv", index=False)
print(sens.to_string(index=False))
