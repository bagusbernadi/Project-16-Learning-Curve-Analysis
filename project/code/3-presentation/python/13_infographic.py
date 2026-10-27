"""13: One-sheet infografik (PNG dan PDF). Semua angka dibaca dari results/2-analysis dan results/3-presentation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import common as C

st_ = pd.read_csv(C.RES2 / "stats_results.csv")
ttt = pd.read_csv(C.RES2 / "ttt_per_operator.csv")
imp = pd.read_csv(C.RES2 / "impact_scenarios.csv")
kpi = pd.read_csv(C.RES3 / "dashboard_kpi.csv").set_index("kpi").nilai


def val(q, metric_start):
    r = st_[(st_.pertanyaan == q) & st_.metrik.str.startswith(metric_start)].iloc[0]
    return r


med = float(kpi["median time-to-target (hari kerja valid)"])
med_row = val("Q1", "median time-to-target")
p10 = val("Q3", "persen operator mencapai target pada hari 10")
p15 = val("Q3", "persen operator mencapai target pada hari 15")
ng_awal = float(val("Q9", "NG rate rata-rata minggu 1-2").nilai)
ng_akhir = float(val("Q9", "NG rate rata-rata dua minggu").nilai)
imp20 = imp[(imp.skenario == "median data (dasar)") & (imp.operator_baru_per_tahun == 20)].iloc[0]

fig = plt.figure(figsize=(8.27, 11.69))  # A4
fig.patch.set_facecolor("white")
fig.text(0.5, 0.95, "Seberapa cepat operator baru mencapai target?", ha="center", fontsize=20, weight="bold", color="#174EA6")
fig.text(0.5, 0.92, "Project 16: Learning Curve Analysis (data simulasi, anonim)", ha="center", fontsize=12, color="#5F6368")

cards = [
    (f"{med:g} hari", f"median time-to-target\n(CI {med_row.ci_bawah:g} sampai {med_row.ci_atas:g} hari)", "#1A73E8"),
    ("30 hari", "standar perusahaan\n(tidak pernah diuji dengan data)", "#5F6368"),
    (f"{p15.nilai * 100:.0f}%", "operator sudah mencapai target\npada hari ke-15", "#188038"),
]
for i, (big, small, col) in enumerate(cards):
    x = 0.08 + i * 0.30
    fig.patches.append(plt.Rectangle((x, 0.66), 0.26, 0.20, transform=fig.transFigure, facecolor="#F8F9FA",
                                     edgecolor="#DADCE0", lw=1.2))
    fig.text(x + 0.13, 0.80, big, ha="center", fontsize=24, weight="bold", color=col)
    fig.text(x + 0.13, 0.70, small, ha="center", fontsize=10, color="#202124")

ax = fig.add_axes([0.12, 0.46, 0.78, 0.17])
ax.bar(ttt.operator_code, ttt.ttt_day, color=["#1A73E8" if d <= 30 else "#EA4335" for d in ttt.ttt_day])
ax.axhline(30, ls="--", color="#5F6368")
ax.text(len(ttt) - 0.5, 31, "standar 30 hari", ha="right", fontsize=9, color="#5F6368")
ax.set_ylabel("hari kerja valid")
ax.set_title("Time-to-target per operator", loc="left", fontsize=12, color="#174EA6")
ax.tick_params(axis="x", labelsize=8, rotation=45)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

bullets = [
    f"{int(ttt.reached.sum())} dari {len(ttt)} operator mencapai target. Tidak ada operator yang berhenti tanpa mencapai target.",
    f"Pada hari ke-10, {p10.nilai * 100:.0f}% operator sudah mencapai target (CI {p10.ci_bawah * 100:.0f}% sampai {p10.ci_atas * 100:.0f}%).",
    "Kurva belajar mengikuti pola cepat di awal lalu melambat (power law dipilih LOOCV).",
    f"Estimasi (asumsi 20 operator baru per tahun): {imp20.hari_onboarding_dihemat_per_tahun_estimated:g} hari onboarding dihemat per tahun.",
    f"NG rate turun dari {ng_awal * 100:.1f}% (minggu 1-2) menjadi {ng_akhir * 100:.1f}% (dua minggu terakhir).",
    "Batasan: 10 operator, data simulasi. Perbedaan antar stasiun belum terbukti.",
]
fig.text(0.10, 0.31, "Temuan utama", fontsize=13, weight="bold", color="#174EA6")
for i, b in enumerate(bullets):
    fig.text(0.10, 0.28 - i * 0.034, f"• {b}", fontsize=10, color="#202124", wrap=True)

fig.text(0.5, 0.03, "Angka: results/2-analysis dan results/3-presentation. Estimasi berlabel estimated.",
         ha="center", fontsize=8, color="#5F6368")
out = C.OUT_XLSX
fig.savefig(out / "infographic.png", dpi=150)
fig.savefig(out / "infographic.pdf")
print("infographic written:", out / "infographic.png")
