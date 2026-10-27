"""08: Uji statistik dan perbandingan (Q1-Q3, Q6-Q10) serta keputusan lima hipotesis.

Hipotesis diuji persis seperti bunyi di rancangan (bagian 4). Angka tidak dipilih ulang dari
hasil; uji yang tidak signifikan dilaporkan apa adanya. CI bootstrap per operator (B=2000, seed tetap).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
import pandas as pd
from scipy import stats
import common as C

rng = np.random.default_rng(C.SEED)
B = 2000
ttt = pd.read_csv(C.RES2 / "ttt_per_operator.csv")
ng = pd.read_csv(C.RES2 / "ng_week.csv")
dv = pd.read_csv(C.RES2 / "valid_days_sql.csv")
curve = pd.read_csv(C.RES2 / "curve_params.csv")
x = ttt.ttt_day.dropna().to_numpy(dtype=float)
n_ops = len(ttt)
rows = []


def boot_ci(vals, fn=np.median):
    vals = np.asarray(vals, dtype=float)
    est = float(fn(vals))
    bs = [fn(rng.choice(vals, size=len(vals), replace=True)) for _ in range(B)]
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return est, float(lo), float(hi)


def wilson(k, n, z=1.959964):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, c - h, c + h


def add(q, metric, value, lo=np.nan, hi=np.nan, p=np.nan, n=np.nan, catatan=""):
    rows.append(dict(pertanyaan=q, metrik=metric, nilai=value, ci_bawah=lo, ci_atas=hi, p_value=p,
                     n=n, catatan=catatan))


# Q1: median time-to-target dan rentang (operator yang mencapai target; semua 10 mencapai)
med, lo, hi = boot_ci(x)
add("Q1", "median time-to-target (hari kerja valid)", med, lo, hi, n=len(x))
add("Q1", "minimum time-to-target", float(x.min()), n=len(x))
add("Q1", "maksimum time-to-target", float(x.max()), n=len(x))
add("Q1", "IQR (Q3-Q1)", float(np.percentile(x, 75) - np.percentile(x, 25)), n=len(x))
add("Q1", "operator belum mencapai target (censored)", float(n_ops - len(x)), n=n_ops,
    catatan="semua operator mencapai target sebelum berhenti atau akhir periode")

# Q2: Wilcoxon satu sampel terhadap 30 hari (alternatif: median < 30)
w = stats.wilcoxon(x - 30, alternative="less")
add("Q2", "Wilcoxon satu sampel vs 30 hari (median < 30)", float(w.statistic), p=float(w.pvalue), n=len(x),
    catatan="uji satu sisi; statistik W")

# Q3: persen operator yang sudah mencapai target pada hari 10, 15, 20 (Wilson CI)
for day in (10, 15, 20):
    k = int(((ttt.ttt_day.notna()) & (ttt.ttt_day <= day)).sum())
    p, lo, hi = wilson(k, n_ops)
    add("Q3", f"persen operator mencapai target pada hari {day}", p, lo, hi, n=n_ops,
        catatan=f"{k} dari {n_ops} operator")

# Q6: time-to-target per stasiun (Kruskal-Wallis) dan median per stasiun
groups = [g.ttt_day.to_numpy(dtype=float) for _, g in ttt.groupby("station_code")]
kw = stats.kruskal(*groups)
add("Q6", "Kruskal-Wallis time-to-target antar stasiun", float(kw.statistic), p=float(kw.pvalue), n=n_ops,
    catatan="n per stasiun 4, 3, 3: daya uji sangat rendah")
for stn, g in ttt.groupby("station_code"):
    est, lo, hi = boot_ci(g.ttt_day.to_numpy(dtype=float))
    add("Q6", f"median time-to-target {stn}", est, lo, hi, n=len(g))

# Q7: minggu pertama (rata-rata persen target hari 1-5) vs time-to-target (Spearman)
rho, p = stats.spearmanr(ttt.week1_avg_pct, ttt.ttt_day, nan_policy="omit")
add("Q7", "Spearman rho: output minggu pertama vs time-to-target", float(rho), p=float(p), n=n_ops,
    catatan="n kecil; rho negatif berarti output minggu pertama tinggi, target lebih cepat")

# Q8: batch dan mentor (sampel kecil, tambahan)
for col, a, b in (("batch_code", "B1", "B2"), ("mentor_code", "M1", "M2")):
    xa = ttt[ttt[col] == a].ttt_day.to_numpy(dtype=float)
    xb = ttt[ttt[col] == b].ttt_day.to_numpy(dtype=float)
    mw = stats.mannwhitneyu(xa, xb, alternative="two-sided")
    add("Q8", f"median time-to-target {col} {a} (n={len(xa)})", float(np.median(xa)), n=len(xa))
    add("Q8", f"median time-to-target {col} {b} (n={len(xb)})", float(np.median(xb)), n=len(xb))
    add("Q8", f"Mann-Whitney {col} {a} vs {b}", float(mw.statistic), p=float(mw.pvalue), n=len(xa) + len(xb),
        catatan="sampel sangat kecil; tidak bisa dibedakan dari kebetulan")

# Q9: NG rate per minggu masa kerja (tren, Spearman pooled; operator diulang, catat keterbatasan)
rho9, p9 = stats.spearmanr(ng.tenure_week, ng.ng_rate, nan_policy="omit")
add("Q9", "Spearman rho: minggu masa kerja vs NG rate (pooled operator-minggu)", float(rho9),
    n=len(ng), catatan="p tidak dilaporkan: baris operator-minggu tidak independen; dibaca sebagai arah saja")
first = ng[ng.tenure_week <= 2].ng_rate.mean()
last = ng[ng.tenure_week >= ng.tenure_week.max() - 1].ng_rate.mean()
add("Q9", "NG rate rata-rata minggu 1-2", float(first), n=int((ng.tenure_week <= 2).sum()))
add("Q9", "NG rate rata-rata dua minggu terakhir", float(last), n=int((ng.tenure_week >= ng.tenure_week.max() - 1).sum()))

# Q10: time-to-target vs NG rate rata-rata (per operator)
rho10, p10 = stats.spearmanr(ttt.ttt_day, ttt.ng_rate_all, nan_policy="omit")
add("Q10", "Spearman rho: time-to-target vs NG rate rata-rata", float(rho10), p=float(p10), n=n_ops,
    catatan="NG rate dihitung dari hari valid; OP-06 dan OP-09 berhenti lebih awal sehingga NG rate-nya lebih tinggi (perancu)")

# H4 juga dari Q7; H5 dari korelasi per operator antara persen target dan NG rate harian
per_op_rho = []
for op, g in dv.groupby("operator_code"):
    g = g.copy()
    g["ng_rate"] = g.ng_qty / (g.ok_qty + g.ng_qty)
    r, _ = stats.spearmanr(g.pct_target, g.ng_rate, nan_policy="omit")
    per_op_rho.append(r)
per_op_rho = np.array(per_op_rho)
est5, lo5, hi5 = boot_ci(per_op_rho)
add("H5", "median Spearman per operator: persen target vs NG rate harian", est5, lo5, hi5, n=n_ops,
    catatan=f"{int((per_op_rho < 0).sum())} dari {n_ops} operator bernilai negatif")

# H3: stasiun dengan langkah lebih banyak lebih lama (urutan langkah A 6, B 4, C 3)
mdn = ttt.groupby("station_code").ttt_day.median().reindex(["ST-A", "ST-B", "ST-C"])
trend, _ = stats.spearmanr([6, 4, 3], mdn.to_numpy(), nan_policy="omit")
add("H3", "Spearman: jumlah langkah vs median time-to-target per stasiun", float(trend), n=3,
    catatan="hanya 3 stasiun; tidak bisa diuji signifikan")

# Q5: plateau kurva (fit power law) dibandingkan target (100%) dan operator berpengalaman
cv = pd.read_csv(C.RES2 / "curve_params.csv")
ci_plateau = pd.read_csv(C.RES2 / "curve_ci.csv").set_index("metrik")
pm = ci_plateau.loc["P_power_median"]
add("Q5", "plateau fit power law (median operator), relatif terhadap target", float(pm.estimasi),
    float(pm.ci_bawah), float(pm.ci_atas), n=n_ops, catatan="1,00 = 100% target")
pdm = ci_plateau.loc["plateau_day_median"]
add("Q5", "hari kurva mulai mendatar (95% plateau), median operator", float(pdm.estimasi),
    float(pdm.ci_bawah), float(pdm.ci_atas), n=int(cv.plateau_day_power.notna().sum()),
    catatan=f"{int(cv.plateau_day_power.isna().sum())} operator belum mendatar dalam 500 hari")
eb = pd.read_csv(C.ANON / "experienced_baseline.csv")
base_ratio = float((eb.median_ok_qty / eb.station_code.map(
    pd.read_csv(C.ANON / "station_target.csv").set_index("station_code").target_per_day)).median())
add("Q5", "median output operator berpengalaman, relatif terhadap target", base_ratio, n=int(eb.n_operator.sum()),
    catatan="median dari semua minggu dan stasiun, operator berpengalaman sebagai pembanding")

res = pd.DataFrame(rows)
for c in ("nilai", "ci_bawah", "ci_atas"):
    res[c] = res[c].round(6)
res["p_value"] = res.p_value.map(lambda v: "" if pd.isna(v) else f"{v:.6g}")
res.to_csv(C.RES2 / "stats_results.csv", index=False)

# Keputusan hipotesis (kriteria ditetapkan sebelum melihat hasil; lihat docs/definitions.md)
med_ttt = float(np.median(x))
p_wil = float(w.pvalue)
p_fit = float(curve.lebih_baik.eq("power_law").mean())
st_order_ok = bool(mdn.loc["ST-C"] < mdn.loc["ST-A"] and mdn.loc["ST-B"] <= mdn.loc["ST-A"])
h = [
    ("H1", "Median time-to-target jauh di bawah standar 30 hari (catatan awal: 10-20 hari).",
     f"median {med_ttt:g} hari; Wilcoxon p = {p_wil:.3g}",
     "Terbukti" if (med_ttt < 20 and p_wil < 0.05) else "Sebagian",
     "kriteria: median di bawah 20 dan p < 0,05"),
    ("H2", "Kurva belajar mengikuti pola cepat di awal lalu melambat (power law atau eksponensial).",
     f"power law terpilih LOOCV; {p_fit * 100:.0f}% operator power law lebih baik dari eksponensial (in-sample); b median dibaca di curve_ci.csv",
     "Terbukti" if p_fit >= 0.5 else "Tidak terbukti",
     "selisih LOOCV kecil (lihat curve_model_compare.csv)"),
    ("H3", "Stasiun dengan langkah kerja lebih banyak membutuhkan waktu lebih lama untuk mencapai target.",
     f"median per stasiun A {mdn['ST-A']:g}, B {mdn['ST-B']:g}, C {mdn['ST-C']:g} hari; tren Spearman {trend:.2f}",
     ("Terbukti" if (st_order_ok and kw.pvalue < 0.05) else ("Belum bisa disimpulkan" if st_order_ok else "Tidak terbukti")),
     "arah sesuai (ST-C tercepat), tetapi uji Kruskal-Wallis tidak signifikan dan n per stasiun 3 sampai 4"),
    ("H4", "Output minggu pertama berkorelasi dengan time-to-target, sehingga operator yang butuh bantuan bisa dikenali lebih awal.",
     f"Spearman rho = {rho:.2f}, p = {p:.3g} (n = {n_ops})",
     "Terbukti" if (rho < 0 and p < 0.05) else ("Belum bisa disimpulkan" if rho < 0 else "Tidak terbukti"),
     "n = 10; kekuatan korelasi tidak stabil"),
    ("H5", "NG rate operator baru turun seiring output naik.",
     f"median Spearman per operator = {est5:.2f} (CI {lo5:.2f} sampai {hi5:.2f}); {int((per_op_rho < 0).sum())} dari {n_ops} operator negatif",
     "Terbukti" if (est5 < 0 and hi5 < 0) else ("Belum bisa disimpulkan" if est5 < 0 else "Tidak terbukti"),
     "arah konsisten; NG rate juga turun seiring masa kerja (waktu dan output bergerak bersama)"),
]
hyp = pd.DataFrame(h, columns=["id", "hipotesis_rancangan", "bukti", "verdict", "catatan_keputusan"])
hyp.to_csv(C.RES2 / "hypotheses.csv", index=False)
print(res[["pertanyaan", "metrik", "nilai", "ci_bawah", "ci_atas", "p_value", "n"]].to_string(index=False))
print(hyp[["id", "verdict", "bukti"]].to_string(index=False))
