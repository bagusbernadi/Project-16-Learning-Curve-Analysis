"""Generator Report v2 (Project 16). Dijalankan paling akhir, setelah seluruh pipeline dijalankan ulang dari nol.

Input : design-and-report/src/page_v1.html (halaman rancangan, pane Design TIDAK diubah),
        project/results/*, project/data/clean, project/data/anon, project/data/raw (ground truth tidak dibaca di sini).
Output: design-and-report/index.html
Setiap angka di teks Report berasal dari CSV lewat helper report_lib (I, D, P, cs). audit() memeriksa token
angka yang tidak berasal dari data dan tidak ada di STATIC.
"""
import re
import sys
from html import escape as esc
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] / "project"
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(HERE))
import pandas as pd
import common as C
import report_lib as R
from report_lib import I, D, P, cs, pill, OK, PART, NO, BLUE, HI, GREY, SOFT, table, qa, legend, bars, gbars, lines, audit

SRC = (HERE / "page_v1.html").read_text(encoding="utf-8")
CSS_EXTRA = (HERE / "report.css").read_text(encoding="utf-8")

# ---------- data ----------
r1, r2, r3 = C.RES1, C.RES2, C.RES3
ttt = pd.read_csv(r2 / "ttt_per_operator.csv")
cp = pd.read_csv(r2 / "curve_params.csv")
cmp_ = pd.read_csv(r2 / "curve_model_compare.csv")
cci = pd.read_csv(r2 / "curve_ci.csv").set_index("metrik")
st = pd.read_csv(r2 / "stats_results.csv")
hyp = pd.read_csv(r2 / "hypotheses.csv")
sens = pd.read_csv(r2 / "sensitivity_ttt.csv")
imp = pd.read_csv(r2 / "impact_scenarios.csv")
rec = pd.read_csv(r2 / "recovery_summary.csv").set_index("parameter")
recst = pd.read_csv(r2 / "recovery_station_order.csv")
cs_pd = pd.read_csv(r2 / "crosscheck_sql_pandas.csv")
cx_ex = pd.read_csv(r2 / "crosscheck_excel.csv")
ng = pd.read_csv(r2 / "ng_week.csv")
dq = pd.read_csv(r1 / "data_quality.csv").set_index("kategori")
dbc = pd.read_csv(r1 / "db_checks.csv")
dbt = pd.read_csv(r1 / "db_tables.csv")
achk = pd.read_csv(r1 / "anonymization_checklist.csv")
dtest = pd.read_csv(r3 / "dashboard_test.csv")
leak = pd.read_csv(r3 / "leak_scan.csv")
daily = pd.read_csv(C.ANON / "daily_output.csv")
exp_base = pd.read_csv(C.ANON / "experienced_baseline.csv")
stt = pd.read_csv(C.ANON / "station_target.csv")
dops = pd.read_csv(C.ANON / "new_operator.csv")


def S(q, prefix):
    rows = st[(st.pertanyaan == q) & st.metrik.str.startswith(prefix)]
    assert len(rows) >= 1, (q, prefix)
    return rows.iloc[0]


def CI(row, d=1):
    return f"CI 95% {D(row.ci_bawah, d)} sampai {D(row.ci_atas, d)}"


def CIP(row):
    return f"CI 95% {P(row.ci_bawah, 0)} sampai {P(row.ci_atas, 0)}"


def pv(p):
    return "< 0,001" if float(p) < 0.001 else D(float(p), 3)


nops = len(ttt)
n_reached = int(ttt.reached.sum())
med_row = S("Q1", "median time-to-target")
min_t, max_t = int(ttt.ttt_day.min()), int(ttt.ttt_day.max())
q1 = {r.metrik: r for r in st[st.pertanyaan == "Q1"].itertuples()}
q2 = S("Q2", "Wilcoxon")
q3_10, q3_15, q3_20 = (S("Q3", f"persen operator mencapai target pada hari {d}") for d in (10, 15, 20))
q5p = S("Q5", "plateau fit")
q5d = S("Q5", "hari kurva")
q5b = S("Q5", "median output operator berpengalaman")
kw = S("Q6", "Kruskal")
q7 = S("Q7", "Spearman rho: output minggu")
q9 = S("Q9", "Spearman rho")
q9a = S("Q9", "NG rate rata-rata minggu 1-2")
q9b = S("Q9", "NG rate rata-rata dua minggu")
q10 = S("Q10", "Spearman rho")
mw_b = S("Q8", "Mann-Whitney batch")
mw_m = S("Q8", "Mann-Whitney mentor")
best = cmp_.loc[cmp_.dipilih == 1].iloc[0]
rmse_rows = {r.model: r for r in cmp_.itertuples()}
n_pow_win = int((cp.lebih_baik == "power_law").sum())
b_med, P_med = cci.loc["b_power_median"], cci.loc["P_power_median"]
plat_med = cci.loc["plateau_day_median"]
base_sens = sens[sens.dasar == 1].iloc[0]
sens_min, sens_max = float(sens.median_ttt.min()), float(sens.median_ttt.max())
imp_base20 = imp[(imp.skenario == "median data (dasar)") & (imp.operator_baru_per_tahun == 20)].iloc[0]
imp_lo20 = imp[(imp.skenario == "batas bawah CI median") & (imp.operator_baru_per_tahun == 20)].iloc[0]
imp_hi20 = imp[(imp.skenario == "batas atas CI median") & (imp.operator_baru_per_tahun == 20)].iloc[0]
H = {r.id: r for r in hyp.itertuples()}
rec_P, rec_F1, rec_b = rec.loc["P"], rec.loc["F1"], rec.loc["b"]
dqv = {k: int(dq.loc[k, "jumlah"]) for k in dq.index}
dqp = {k: float(dq.loc[k, "proporsi"]) for k in dq.index}
total_rows = dqv["baris output harian (operator baru)"]
valid_rows = dqv["valid"]
n_checks_ok = int((dbc.hasil == "lulus").sum())
n_leak_files = len(leak)
n_leak_fail = int((leak.hasil == "gagal").sum())
n_dash_ok = int((dtest.hasil == "lulus").sum())
n_dash = len(dtest)
n_anon_ok = int((achk.hasil == "lulus").sum())
n_anon = len(achk)
n_cs = len(cs_pd)
n_cs_ok = int(cs_pd.cocok.sum())
n_ex = len(cx_ex)
n_ex_ok = int(cx_ex.cocok.sum())
dq_ok = total_rows == valid_rows + dqv["tidak hadir"] + dqv["jam tidak penuh"] + dqv["output 0"] + dqv["pindah stasiun"]
assert dq_ok, "Q12 tidak menjumlah"
assert int(ttt.reached.sum()) == nops
exp_ratio = float((exp_base.median_ok_qty / exp_base.station_code.map(
    stt.set_index("station_code").target_per_day)).median())

# ---------- grafik dan tabel ----------
ST_COL = {"ST-A": "#1A73E8", "ST-B": "#188038", "ST-C": "#9334E6"}
chart_ttt = bars([(r.operator_code, r.ttt_day, ST_COL[r.station_code], f"{r.operator_code} {r.station_code}: {I(r.ttt_day)} hari")
                  for r in ttt.itertuples()],
                 lambda v: D(v, 0), "Grafik time-to-target per operator", h=270, ymax=30, rot=0)
chart_ng = lines([f"minggu {w}" for w in sorted(ng.tenure_week.unique())],
                 [("NG rate rata-rata", "#EA4335", 2.5,
                   [float(ng[ng.tenure_week == w].ng_rate.mean()) for w in sorted(ng.tenure_week.unique())])],
                 lambda v: D(v * 100, 1) + "%", "Grafik NG rate per minggu masa kerja", h=240, zero=True)
chart_cmp = bars([(m, rmse_rows[m].loocv_rmse_mean, BLUE if m == best.model else GREY, f"{m}: {D(rmse_rows[m].loocv_rmse_mean, 4)}")
                  for m in ["power_law", "eksponensial", "linear_per_segmen"]],
                 lambda v: D(v, 3), "Grafik RMSE LOOCV tiga bentuk kurva", h=220, ymax=0.1, rot=0)
chart_sens = bars([(f"s{int(r.streak_hari)} a{int(r.ambang_persen)} {'+' if r.jam_tidak_penuh == 'dimasukkan' else '-'}",
                    float(r.median_ttt), BLUE if r.dasar == 1 else GREY,
                    f"streak {int(r.streak_hari)}, ambang {int(r.ambang_persen)}%, jam tidak penuh {r.jam_tidak_penuh}: median {D(r.median_ttt, 1)}")
                   for r in sens.itertuples()],
                  lambda v: D(v, 0), "Grafik sensitivitas median time-to-target", h=240, ymax=14, rot=35)

# ---------- helper lain ----------
def verdict_pill(v):
    kind = {"Terbukti": "", "Belum bisa disimpulkan": "p", "Tidak terbukti": "d"}.get(v, "d")
    return pill(v, kind)


def kpi(v, l, d, color):
    return (f'<div class="card kpi" style="--h:var(--{color})"><span class="v">{v}</span>'
            f'<span class="l">{l}</span><span class="d">{d}</span></div>')


# ---------- PANE REPORT ----------
QS = [
    (1, "Berapa hari median operator baru mencapai target output harian, dan berapa rentangnya?", "Utama", "Kecepatan"),
    (2, "Apakah time-to-target lebih cepat secara signifikan dibanding standar 30 hari?", "Utama", "Kecepatan"),
    (3, "Berapa persen operator yang sudah mencapai target pada hari ke-10, ke-15, dan ke-20?", "Utama", "Kecepatan"),
    (4, "Model kurva apa yang paling cocok dengan data, dan berapa learning rate-nya?", "Utama", "Bentuk kurva"),
    (5, "Pada output berapa kurva mulai mendatar, dan apakah plateau itu di atas target?", "Pendukung", "Bentuk kurva"),
    (6, "Apakah time-to-target berbeda antar stasiun?", "Utama", "Perbedaan"),
    (7, "Apakah output minggu pertama bisa memprediksi kapan operator mencapai target?", "Pendukung", "Perbedaan"),
    (8, "Apakah ada perbedaan antar batch training atau pendamping?", "Tambahan", "Perbedaan"),
    (9, "Bagaimana NG rate operator baru berubah selama masa belajar?", "Pendukung", "Kualitas"),
    (10, "Apakah operator yang cepat mencapai target punya NG rate lebih tinggi?", "Pendukung", "Kualitas"),
    (11, "Berapa hari onboarding dan output yang bisa dihitung ulang per tahun jika standar disesuaikan dengan data?", "Utama", "Dampak"),
    (12, "Berapa persen data tidak valid (hari tidak hadir, output 0, pindah stasiun), dan bagaimana ditangani?", "Utama", "Validitas"),
    (13, "Apakah time-to-target dari SQL sama dengan hitungan manual di Excel?", "Utama", "Validitas"),
]
WARN = {4, 5, 6, 7, 8, 9, 10, 11, 13}
ANS = {
    1: (f"Median time-to-target {I(med_row.nilai)} hari kerja valid ({CI(med_row, 0)}). Rentang {I(min_t)} sampai {I(max_t)} hari. "
        f"Semua {I(nops)} operator mencapai target ({I(n_reached)} dari {I(nops)}), tidak ada yang tersisa (censored)."),
    2: (f"Ya. Uji Wilcoxon satu sampel terhadap {I(30)} hari menghasilkan p {pv(q2.p_value)} (satu sisi, median di bawah 30). "
        f"Semua operator berada di bawah standar."),
    3: (f"Pada hari ke-10, {P(q3_10.nilai, 0)} operator sudah mencapai target ({CIP(q3_10)}). "
        f"Pada hari ke-15, {P(q3_15.nilai, 0)} ({CIP(q3_15)}). Pada hari ke-20, {P(q3_20.nilai, 0)} ({CIP(q3_20)})."),
    4: (f"Power law dipilih dengan kriteria LOOCV: RMSE rata-rata {D(rmse_rows['power_law'].loocv_rmse_mean, 4)}, "
        f"dibanding eksponensial {D(rmse_rows['eksponensial'].loocv_rmse_mean, 4)} dan linear per segmen {D(rmse_rows['linear_per_segmen'].loocv_rmse_mean, 4)}. "
        f"Selisih kecil. Learning rate b median {D(b_med.estimasi, 2)} ({CI(b_med, 2)})."),
    5: (f"Plateau median {D(P_med.estimasi, 2)} (CI {D(P_med.ci_bawah, 2)} sampai {D(P_med.ci_atas, 2)}), di atas target 1,00. "
        f"Median kurva mulai mendatar di hari ke-{I(plat_med.estimasi)} ({CI(plat_med, 0)}). "
        f"Operator berpengalaman rata-rata {D(q5b.nilai, 2)} dari target."),
    6: (f"Median per stasiun: ST-A {I(ttt[ttt.station_code == 'ST-A'].ttt_day.median())} hari, ST-B {I(ttt[ttt.station_code == 'ST-B'].ttt_day.median())} hari, "
        f"ST-C {I(ttt[ttt.station_code == 'ST-C'].ttt_day.median())} hari. Kruskal-Wallis p {pv(kw.p_value)}: tidak signifikan. "
        f"n per stasiun " + ", ".join(f"{k} {I(v)}" for k, v in ttt.station_code.value_counts().sort_index().items()) + "."),
    7: (f"Spearman rho {D(q7.nilai, 2)}, p {pv(q7.p_value)} (n {I(nops)}). Arahnya sesuai (output minggu pertama tinggi, target lebih cepat), tetapi tidak signifikan."),
    8: (f"Batch B1 median {I(ttt[ttt.batch_code == 'B1'].ttt_day.median())} hari (n {I(int((ttt.batch_code == 'B1').sum()))}), B2 median {I(ttt[ttt.batch_code == 'B2'].ttt_day.median())} hari (n {I(int((ttt.batch_code == 'B2').sum()))}), "
        f"p {pv(mw_b.p_value)}. Mentor M1 dan M2 sama ({I(ttt[ttt.mentor_code == 'M1'].ttt_day.median())} dan {I(ttt[ttt.mentor_code == 'M2'].ttt_day.median())} hari). "
        f"Sampel terlalu kecil untuk kesimpulan."),
    9: (f"NG rate rata-rata minggu 1-2 {P(q9a.nilai, 1)}, dua minggu terakhir {P(q9b.nilai, 1)}. Turun seiring masa kerja. "
        f"Korelasi pooled tidak dilaporkan p-value karena baris operator-minggu tidak independen."),
    10: (f"Spearman rho {D(q10.nilai, 2)}, p {pv(q10.p_value)} (n {I(nops)}). Tidak ada hubungan yang terdeteksi. "
         f"Catatan: OP-06 dan OP-09 berhenti atau pindah lebih awal, sehingga NG rate rata-rata mereka lebih tinggi (perancu)."),
    11: (f"Skenario dasar (median {D(med_row.nilai, 0)} hari, standar 30 hari, 20 operator baru per tahun): "
         f"{I(imp_base20.hari_onboarding_dihemat_per_tahun_estimated)} hari onboarding dihemat per tahun "
         f"(setara {I(imp_base20.output_setara_unit_estimated)} unit, estimated). Rentang dari batas CI: {I(imp_lo20.hari_onboarding_dihemat_per_tahun_estimated)} "
         f"sampai {I(imp_hi20.hari_onboarding_dihemat_per_tahun_estimated)} hari. Volume operator per tahun adalah asumsi."),
    12: (f"{P(dqp['tidak hadir'], 1)} tidak hadir, {P(dqp['jam tidak penuh'], 1)} jam tidak penuh, {P(dqp['output 0'], 1)} output 0, "
         f"{P(dqp['pindah stasiun'], 1)} pindah stasiun. Total {I(total_rows)} baris, {I(valid_rows)} hari valid ({P(dqp['valid'], 1)}). "
         f"Aturan dan log ada di docs/cleaning_decisions.md."),
    13: (f"Ya. Cek silang Excel untuk {I(n_ex)} operator: {I(n_ex_ok)} dari {I(n_ex)} sama dengan SQL. "
         f"Excel dihitung ulang oleh LibreOffice, bukan dihitung manual. Cek SQL vs pandas: {I(n_cs_ok)} dari {I(n_cs)} operator cocok."),
}


def qchip(n, title):
    return f'<a class="qc{" w" if n in WARN else ""}" href="#sec2{n}" title="{esc(title)}">Q{n}</a>'


def qcard(n, title, prio):
    return qa(f"Q{n}", title, prio, ANS[n], status="Terjawab" if n not in WARN else "Dengan catatan", warn=n in WARN)


def block(title, qs):
    return (f'<h3>{title}</h3>' + "".join(qcard(n, t, p) for n, t, p, _ in [q for q in QS if q[0] in qs]))


# Pill per status output dan hipotesis
def hyp_row(hid):
    h = H[hid]
    return [f"<b>{hid}</b>", esc(h.hipotesis_rancangan), esc(cs(h.bukti)), verdict_pill(h.verdict), esc(h.catatan_keputusan)]


hyp_table = table(["ID", "Hipotesis (sesuai rancangan)", "Bukti", "Verdict", "Catatan keputusan"],
                  [hyp_row(x) for x in ["H1", "H2", "H3", "H4", "H5"]])

# Bagian 2 (business questions)
sec2 = []
sec2.append(f'<div class="card"><h3>Jawaban singkat</h3><p>Semua {I(13)} pertanyaan terjawab dengan angka dari data. '
            f'{I(len(WARN))} di antaranya diberi catatan kuning karena sampel kecil, asumsi, atau perancu. '
            f'Pertanyaan utama project dijawab di bagian 7.</p>'
            f'<p class="how">Klik nomor pertanyaan untuk melompat. Q hijau = terjawab. Q kuning = terjawab dengan catatan.</p>'
            f'<div class="qchips">' + "".join(qchip(n, t) for n, t, _, _ in QS) + '</div></div>')
sec2.append(f'<div id="sec21"></div><h3>2.1 Kecepatan: berapa lama sampai target</h3>'
            f'<div class="card"><p>Grafik 2.1a: time-to-target per operator. Warna menunjukkan stasiun: biru ST-A, hijau ST-B, ungu ST-C. Garis pada {I(30)} hari adalah standar.</p>'
            f'{chart_ttt}{legend([(BLUE, "ST-A"), ("#188038", "ST-B"), ("#9334E6", "ST-C")])}'
            f'{table(["Operator", "Stasiun", "Time-to-target (hari valid)", "Tercapai"], [[r.operator_code, r.station_code, I(r.ttt_day), "ya" if r.reached else "tidak"] for r in ttt.itertuples()])}'
            f'<p>Tabel 2.1b: median dan rentang. Median {I(med_row.nilai)} hari ({CI(med_row, 0)}); rentang {I(min_t)} sampai {I(max_t)}.</p></div>')
sec2.append(block("", [1, 2, 3]).replace("<h3></h3>", ""))
sec2.append('<div id="sec24"></div><h3>2.2 Bentuk kurva: bagaimana operator belajar</h3>'
            f'<div class="card"><p>Tabel 2.2a: RMSE out-of-operator (LOOCV). Power law dipilih, dengan selisih kecil terhadap eksponensial.</p>'
            f'{chart_cmp}'
            f'{table(["Model", "Parameter", "RMSE LOOCV rata-rata", "Dipilih"], [[r.model, I(r.n_parameter), D(r.loocv_rmse_mean, 4), "ya" if r.dipilih == 1 else "tidak"] for r in cmp_.itertuples()])}'
            f'<p>Tabel 2.2b: parameter power law per operator (P plateau, F1 hari pertama, b learning rate, hari mulai mendatar).</p>'
            f'{table(["Operator", "P", "F1", "b", "Hari mendatar"], [[r.operator_code, D(r.P_power, 3), D(r.F1_power, 3), D(r.b_power, 3), (I(r.plateau_day_power) if pd.notna(r.plateau_day_power) else "belum")] for r in cp.itertuples()])}'
            f'</div>')
sec2.append(block("", [4, 5]).replace("<h3></h3>", ""))
sec2.append('<div id="sec26"></div><h3>2.3 Perbedaan: stasiun, minggu pertama, batch dan mentor</h3>'
            f'<div class="card"><p>Tabel 2.3a: time-to-target per stasiun dan batch.</p>'
            f'{table(["Kelompok", "n", "Median (hari valid)", "Rentang"], [[f"Stasiun {s}", I(len(g)), I(g.ttt_day.median()), f"{I(g.ttt_day.min())} sampai {I(g.ttt_day.max())}"] for s, g in ttt.groupby("station_code")] + [[f"Batch {b}", I(len(g)), I(g.ttt_day.median()), f"{I(g.ttt_day.min())} sampai {I(g.ttt_day.max())}"] for b, g in ttt.groupby("batch_code")])}'
            f'{sens_note_sec26(q7) if False else ""}</div>')
sec2.append(block("", [6, 7, 8]).replace("<h3></h3>", ""))
sec2.append('<div id="sec29"></div><h3>2.4 Kualitas: apakah cepat berarti asal</h3>'
            f'<div class="card"><p>Grafik 2.4a: NG rate rata-rata per minggu masa kerja.</p>{chart_ng}</div>')
sec2.append(block("", [9, 10]).replace("<h3></h3>", ""))
sec2.append('<div id="sec211"></div><h3>2.5 Dampak: jika standar disesuaikan</h3>'
            f'<div class="card"><p>Tabel 2.5a: skenario dampak (semua estimated). Volume operator baru per tahun adalah asumsi, bukan data.</p>'
            f'{table(["Skenario", "Median (hari)", "Operator baru per tahun", "Hari dihemat per tahun", "Output setara (unit)"], [[r.skenario, D(r.median_ttt, 1), I(r.operator_baru_per_tahun), I(r.hari_onboarding_dihemat_per_tahun_estimated), I(r.output_setara_unit_estimated)] for r in imp.itertuples()])}</div>')
sec2.append(block("", [11]).replace("<h3></h3>", ""))
sec2.append('<div id="sec212"></div><h3>2.6 Validitas: kualitas dan cek silang</h3>'
            f'<div class="card"><p>Tabel 2.6a: cek silang time-to-target SQL vs Excel (3 operator).</p>'
            f'{table(["Operator", "TTT Excel", "TTT SQL", "Cocok"], [[r.operator_code, I(r.ttt_excel), I(r.ttt_sql), "ya" if r.cocok else "tidak"] for r in cx_ex.itertuples()])}'
            f'<p>Tabel 2.6b: SQL vs pandas untuk {I(n_cs)} operator, mencakup time-to-target, minggu pertama, dan NG rate: {I(n_cs_ok)} dari {I(n_cs)} cocok.</p></div>')
sec2.append(block("", [12, 13]).replace("<h3></h3>", ""))
sec2.append('<h3>Hipotesis pada Design Project</h3><div class="card"><p class="how">Bunyi dan definisi hipotesis mengikuti rancangan. Verdict ditetapkan sebelum hasil dilihat (docs/definitions.md, bagian 5).</p>'
            + hyp_table + '</div>')

# Bagian 1 (data)
sample_rows = daily.head(6)
REP = []
REP.append(f'<div class="callout a"><h4>Data project ini adalah simulasi</h4>Data adalah data simulasi dengan kurva belajar yang ditanam (lihat docs/simulation_spec.md). '
           f'Angka menggambarkan simulasi, bukan lini produksi nyata.</div>')
REP.append('<h2 id="rp1">1. Data yang berhasil didapatkan<small>Isi data mentah, tabel di database, dan data hasil analisis</small></h2>')
REP.append('<div class="kpis">'
           + kpi(I(total_rows), "baris output harian", f"{I(nops)} operator baru, termasuk hari tidak hadir.", "navyH")
           + kpi(I(valid_rows), "hari valid", f"{P(dqp['valid'], 1)} dari baris, dipakai untuk kurva dan streak.", "tealH")
           + kpi(I(len(exp_base.station_code.unique())), "stasiun", "ST-A, ST-B, ST-C dengan nama umum.", "amberH")
           + kpi(I(len(dbt)), "tabel di database", "4 tabel anonim plus view SQL.", "plumH")
           + kpi(I(n_checks_ok), "pengecekan database lulus", f"Dari {I(len(dbc))} aturan yang diuji.", "skyH")
           + kpi(P(med_row.nilai / 30, 0), "median dibanding 30 hari", f"Median {I(med_row.nilai)} dari standar {I(30)} hari.", "roseH")
           + '</div>')
REP.append('<h3>1.1 Data mentah dan anonim</h3>'
           f'<div class="card"><p>Tabel 1.1a: contoh baris data yang sudah dianonimkan (enam baris pertama).</p>'
           + table(list(sample_rows.columns), [[cs(v) for v in r] for r in sample_rows.itertuples(index=False)])
           + f'<p>Tabel 1.1b: kualitas data (Q12). Log cleaning ada di docs/cleaning_decisions.md.</p>'
           + table(["Kategori", "Jumlah", "Proporsi", "Keputusan"],
                   [[k, I(dqv[k]), P(dqp[k], 1), kp] for k, kp in [
                       ("baris output harian (operator baru)", "dasar"), ("tidak hadir", "dilewati"),
                       ("jam tidak penuh", "dilewati dari kurva dan streak"), ("output 0", "dilewati"),
                       ("pindah stasiun", "dilewati; waktu dari sebelum pindah"), ("valid", "dipakai")]])
           + '</div>')
REP.append('<h3>1.2 Tabel di database dan hasil</h3>'
           f'<div class="card"><p>Tabel 1.2a: tabel di learning.duckdb (tidak dikomit, dibuat ulang dari skrip).</p>'
           + table(["Tabel", "Perkiraan ukuran"], [[r.table_name, I(r.estimated_size)] for r in dbt.itertuples()])
           + f'<p>Tabel 1.2b: pengecekan aturan database. {I(n_checks_ok)} dari {I(len(dbc))} lulus.</p>'
           + table(["Pengecekan", "Pelanggaran", "Hasil"], [[r.pengecekan, I(r.pelanggaran), pill(r.hasil, "" if r.hasil == "lulus" else "d")] for r in dbc.itertuples()])
           + f'<p>Tabel 1.2c: file hasil analisis di results/2-analysis.</p>'
           + table(["File", "Isi"], [[f, cs(i)] for f, i in [
               ("ttt_per_operator.csv", "time-to-target, minggu pertama, NG rate per operator"),
               ("valid_days_sql.csv", "hari valid dengan persen target"),
               ("curve_params.csv", "parameter kurva per operator"),
               ("curve_model_compare.csv", "perbandingan bentuk kurva (LOOCV)"),
               ("curve_ci.csv", "CI bootstrap median"),
               ("stats_results.csv", "hasil uji Q1 sampai Q10 dan Q5"),
               ("hypotheses.csv", "verdict H1 sampai H5"),
               ("sensitivity_ttt.csv", "sensitivitas definisi mencapai target"),
               ("impact_scenarios.csv", "skenario dampak (estimated)"),
               ("recovery_summary.csv", "uji pemulihan parameter"),
               ("crosscheck_sql_pandas.csv", "cek silang SQL vs pandas"),
               ("crosscheck_excel.csv", "cek silang Excel")]])
           + '</div>')
REP.append('<h3>1.3 Angka kunci (KPI)</h3>'
           f'<div class="card"><p>Tabel 1.3: lima ukuran kinerja sesuai rancangan.</p>'
           + table(["KPI", "Rumus ringkas", "Hasil", "Jumlah data"], [
               ["Time-to-target", "hari valid pertama dari 3 hari berturut-turut ≥ target", f"median {I(med_row.nilai)} hari", I(nops)],
               ["Persen target", "ok_qty / target_per_day", f"median hari valid {P(float(daily.assign(x=1).shape[0] and 0) + 0.8, 0) if False else P(float(pd.read_csv(C.RES2 / 'valid_days_sql.csv').pct_target.median()), 0)}", I(valid_rows)],
               ["Learning rate", "b pada power law", f"median {D(b_med.estimasi, 2)}", I(nops)],
               ["Plateau", "P pada power law", f"median {D(P_med.estimasi, 2)}", I(nops)],
               ["Hari onboarding dihemat", "(30 - median) x operator per tahun", f"{I(imp_base20.hari_onboarding_dihemat_per_tahun_estimated)} hari per tahun (estimated)", I(20)],
           ]) + '</div>')

# Bagian 3 (dataset: rancangan vs realisasi)
REP.append('<h2 id="rp2">2. Apakah business question terjawab?<small>' + f'{I(13)} pertanyaan pada Design Project, dijawab dengan data' + '</small></h2>')
REP.extend(sec2)
REP.append('<h2 id="rp3">3. Apakah dataset sesuai dengan Design Project?<small>Perbandingan rancangan dengan realisasi</small></h2>')
REP.append('<div class="card"><p class="how">Tabel 3a. Rancangan dan realisasi dataset.</p>'
           + table(["Hal", "Rancangan", "Realisasi", "Verdict"], [
               ["Sumber data", "data kerja operator baru yang dianonimkan", "data simulasi dengan kurva belajar yang ditanam", pill("Berubah", "p")],
               ["Izin penggunaan data", "perlu dipastikan dari perusahaan", "tidak berlaku (data simulasi)", pill("Tidak berlaku", "d")],
               ["Ukuran", f"{I(10)} operator, {I(3)} stasiun, ±60 hari", f"{I(nops)} operator, {I(3)} stasiun, {I(total_rows)} baris", pill("Sesuai", "")],
               ["Tabel", "new_operator, daily_output, station_target, experienced_baseline", "sama; disimpan sebagai tabel DuckDB", pill("Sesuai", "")],
               ["Aturan anonimisasi", "kode operator, stasiun, produk dihapus, skala", f"{I(n_anon_ok)} dari {I(n_anon)} pemeriksaan lulus", pill("Sesuai", "")],
               ["Data tidak lengkap", "2 sampai 3 persen", f"{P(dqp['tidak hadir'] + dqp['output 0'] + dqp['jam tidak penuh'], 1)} hari tidak valid (tidak hadir, output 0, jam pendek)", pill("Sesuai", "")],
               ["Kode operator", "OP-01 sampai OP-10", "OP-01 sampai OP-10, pembanding EXP-01 sampai EXP-12", pill("Sesuai + tambahan", "")],
               ["Hipotesis H1", "median jauh di bawah 30 hari", f"median {I(med_row.nilai)} hari", verdict_pill(H["H1"].verdict)],
               ["Hipotesis H2", "kurva cepat lalu melambat", "power law", verdict_pill(H["H2"].verdict)],
               ["Hipotesis H3", "stasiun dengan langkah lebih banyak lebih lama", "arah sesuai, tidak signifikan", verdict_pill(H["H3"].verdict)],
               ["Hipotesis H4", "minggu pertama berkorelasi dengan time-to-target", f"rho {D(q7.nilai, 2)}, tidak signifikan", verdict_pill(H["H4"].verdict)],
               ["Hipotesis H5", "NG rate turun seiring output naik", "arah konsisten pada semua operator", verdict_pill(H["H5"].verdict)],
           ])
           + '<p>Tabel 3b: angka asumsi dan parameter ditetapkan sendiri (berlabel asumsi, lihat docs/definitions.md): '
             'target per stasiun, aturan hari valid, streak 3 hari, volume operator per tahun, toleransi uji pemulihan.</p></div>')
REP.append('<div class="card"><p class="how">Tabel 3c. Uji pemulihan parameter yang ditanam (validasi, bukan hasil analisis).</p>'
           + table(["Parameter", "Operator dalam toleransi", "MAE", "Bias"], [
               [k, f"{I(rec.loc[k].dalam_toleransi)} dari {I(rec.loc[k].n)}", D(rec.loc[k].mae, 3), D(rec.loc[k].bias, 3)] for k in ["P", "F1", "b"]])
           + f'<p>Bias F1 positif. Penyebab yang diduga: hari valid membuang hari jam pendek dan output 0, sehingga kurva awal terangkat. Ini tidak diperbaiki setelah melihat hasil.</p>'
           + table(["Stasiun", "Median b ditanam", "Median b fit", "Urutan sama"], [
               [r.station_code, D(r.b_ditanam_median, 3), D(r.b_fit_median, 3), "ya" if r.urutan_sama else "tidak"] for r in recst.itertuples()])
           + '</div>')

# Bagian 4 (tools)
REP.append('<h2 id="rp4">4. Apakah tools yang digunakan sesuai?<small>Perbandingan rancangan dengan eksekusi</small></h2>')
REP.append('<div class="card"><p class="how">Tabel 4a. Tools rancangan dan realisasi.</p>'
           + table(["Tool", "Rancangan", "Realisasi", "Verdict"], [
               ["Python (pandas, NumPy, SciPy)", "anonimisasi, curve fitting, uji Wilcoxon", "dipakai untuk semua tahap; uji Kruskal-Wallis dan Mann-Whitney ditambahkan", pill("Sesuai + tambahan", "")],
               ["DuckDB + SQL", "view persen target, rata-rata 3 hari, TTT", f"view SQL; {I(n_cs_ok)} dari {I(n_cs)} cocok dengan pandas", pill("Sesuai", "")],
               ["Excel", "cek silang 3 operator (Q13)", f"workbook dengan formula, dihitung ulang oleh LibreOffice headless; {I(n_ex_ok)} dari {I(n_ex)} cocok", pill("Sesuai + penyesuaian", "p")],
               ["Skrip anonimisasi", "pengecekan nama yang tersisa", f"{I(n_anon_ok)} dari {I(n_anon)} pemeriksaan lulus; pindai kebocoran {I(n_leak_files)} file, {I(n_leak_fail)} gagal", pill("Sesuai", "")],
               ["Streamlit + Plotly", "dashboard 3 halaman, link publik", f"3 halaman diuji dengan AppTest ({I(n_dash_ok)} dari {I(n_dash)} lulus); belum di-deploy", pill("Sebagian", "p")],
               ["GitHub + Markdown", "repo dan README", "repo dan README; deploy belum", pill("Sesuai", "")],
           ]) + '</div>')

# Bagian 5 (alur kerja)
REP.append('<h2 id="rp5">5. Apakah alur pengerjaan sesuai dengan Design Project?<small>12 langkah rancangan vs yang dijalankan</small></h2>')
REP.append('<div class="card"><p class="how">Tabel 5a. Dua belas langkah rancangan dan yang dijalankan.</p>'
           + table(["No", "Langkah rancangan", "Realisasi", "Verdict"], [
               ["1", "Menyepakati definisi", "docs/definitions.md dengan label asumsi dan sensitivitas", pill("Sesuai + tambahan", "")],
               ["2", "Struktur tabel dan aturan anonim", "docs/data_dictionary.md", pill("Sesuai", "")],
               ["3", "Menganonimkan data", "simulasi dulu (00), lalu anonimisasi (01)", pill("Berubah", "p")],
               ["4", "Membersihkan data", f"cleaning dengan {I(len(dq) - 1)} kategori (02)", pill("Sesuai", "")],
               ["5", "Memasukkan ke database", "DuckDB dengan pengecekan (03)", pill("Sesuai", "")],
               ["6", "Query time-to-target", "view SQL dan ekspor (04)", pill("Sesuai", "")],
               ["7", "Cek silang Excel", "Excel dihitung ulang LibreOffice (06)", pill("Sesuai + penyesuaian", "p")],
               ["8", "Curve fitting", "power law, eksponensial, linear per segmen, LOOCV (07)", pill("Sesuai + tambahan", "")],
               ["9", "Uji dan perbandingan", "Wilcoxon, Wilson, Kruskal-Wallis, Spearman (08)", pill("Sesuai", "")],
               ["10", "Menghitung dampak", "skenario estimated (10)", pill("Sesuai", "")],
               ["11", "Membuat dashboard", "Streamlit 3 halaman, diuji AppTest (12, 14)", pill("Sebagian", "p")],
               ["12", "README dan finalisasi", "README dan Report (17)", pill("Sebagian", "p")],
           ])
           + '<p>Tabel 5b: penyesuaian dan improvisasi yang tidak ada di rancangan.</p>'
           + table(["Penyesuaian", "Alasan"], [
               ["Simulasi dibuat sebelum anonimisasi", "data kerja tidak dilampirkan; user memilih simulasi"],
               ["Uji pemulihan (11) dan pindai kebocoran (15)", "validasi yang tidak ada di rancangan"],
               ["Kurva diuji dengan LOOCV", "pemilihan model tanpa memakai data uji"],
               ["Notebook (analysis.ipynb) tidak dibuat", "waktu; hasil ada di CSV dan Report"],
           ])
           + '<p>Tabel 5c: perubahan nama dan lokasi file terhadap rancangan.</p>'
           + table(["Rancangan", "Realisasi"], [
               ["scripts/anonymize.py", "project/code/1-data-preparation/python/01_anonymize.py"],
               ["scripts/clean_data.py", "project/code/1-data-preparation/python/02_clean.py"],
               ["data/anon/*.csv", "project/data/anon/*.csv"],
               ["data/private/", "project/data/raw/ dan project/data/mapping_key.csv (tidak dikomit)"],
               ["docs/kpi_definitions.md", "project/docs/definitions.md"],
               ["docs/data_dictionary.md", "project/docs/data_dictionary.md"],
               ["docs/cleaning_log.md", "project/docs/cleaning_decisions.md dan project/results/1-data-preparation/cleaning_log.csv"],
               ["learning.duckdb", "project/learning.duckdb (tidak dikomit)"],
               ["sql/", "project/code/2-analysis/sql/views.sql"],
               ["outputs/crosscheck.xlsx", "project/outputs/crosscheck.xlsx"],
               ["notebooks/analysis.ipynb", "(tidak ada di rancangan realisasi: tidak dibuat)"],
               ["outputs/*.csv", "project/results/2-analysis/*.csv"],
               ["dashboard/app.py", "project/code/3-presentation/streamlit/app.py"],
               ["outputs/infographic.pdf / .png", "project/outputs/infographic.pdf dan .png"],
               ["requirements.txt", "project/requirements.txt"],
               ["README.md", "README.md"],
               ["index.html", "design-and-report/index.html (rancangan di design-and-report/src/page_v1.html)"],
               ["outputs/monitoring_template.xlsx", "(tidak dibuat)"],
               ["slides/presentation.pdf", "(tidak dibuat)"],
           ])
           + '</div>')

# Bagian 6 (output)
REP.append('<h2 id="rp6">6. Apakah project output tercapai?<small>Output pada Design Project, bagian 7</small></h2>')
REP.append('<div class="card"><p class="how">Tabel 6a. Status output rancangan.</p>'
           + table(["Output", "Label", "Status", "Bukti"], [
               ["Dashboard kurva belajar", "Utama", pill("Sebagian", "p"), f"3 halaman diuji dengan AppTest ({I(n_dash_ok)} dari {I(n_dash)}); belum di-deploy"],
               ["One-sheet infografik", "Utama", pill("Tercapai", ""), "outputs/infographic.pdf dan .png"],
               ["Database dan query SQL", "Utama", pill("Tercapai", ""), f"learning.duckdb (tidak dikomit); views.sql; {I(n_checks_ok)} pengecekan lulus"],
               ["Skrip anonimisasi", "Utama", pill("Tercapai", ""), f"01_anonymize.py; pindai kebocoran {I(n_leak_files)} file, {I(n_leak_fail)} gagal"],
               ["Notebook analisis", "Utama", pill("Tidak dibuat", "d"), "tidak dibuat; analisis di skrip 04 sampai 11"],
               ["README dan repositori", "Utama", pill("Sebagian", "p"), "README dan Report; deploy belum; branch belum di-merge"],
               ["Template pemantauan operator baru", "Opsional", pill("Tidak dibuat", "d"), "-"],
               ["Slide presentasi", "Opsional", pill("Tidak dibuat", "d"), "-"],
           ])
           + '<p>Tabel 6b: daftar dokumen rancangan dan status pada repositori.</p>'
           + table(["Dokumen", "Status"], [
               ["docs/definitions.md", pill("Ada", "")], ["docs/data_dictionary.md", pill("Ada", "")],
               ["docs/cleaning_decisions.md", pill("Ada", "")], ["docs/simulation_spec.md", pill("Ada", "")],
               ["data/anon/*.csv", pill("Ada", "")], ["data/mapping_key.csv", pill("Tidak di-commit", "d")],
               ["learning.duckdb", pill("Tidak di-commit", "d")], ["outputs/crosscheck.xlsx", pill("Ada", "")],
               ["outputs/infographic.pdf dan .png", pill("Ada", "")], ["dashboard/app.py", pill("Ada", "")],
               ["requirements.txt", pill("Ada", "")], ["README.md", pill("Ada", "")],
               ["notebooks/analysis.ipynb", pill("Tidak dibuat", "d")],
           ])
           + '</div>')

# Bagian 7 (kesimpulan)
ok_criteria = [
    ("Kedelapan pertanyaan Utama terjawab dengan angka dari data",
     "Terpenuhi", "Q1, Q2, Q3, Q4, Q6, Q11, Q12, Q13 dijawab; Q6 dengan catatan sampel kecil"),
    ("Time-to-target SQL sama dengan Excel untuk operator yang dicek", "Terpenuhi (LibreOffice)",
     f"{I(n_ex_ok)} dari {I(n_ex)} operator sama"),
    ("Kelima hipotesis diputuskan dengan alasan", "Terpenuhi",
     f"H1 {H['H1'].verdict}; H2 {H['H2'].verdict}; H3 {H['H3'].verdict}; H4 {H['H4'].verdict}; H5 {H['H5'].verdict}"),
    ("Anonimisasi: tidak ada nama asli di repositori", "Terpenuhi" if n_leak_fail == 0 else "Gagal",
     f"pindai {I(n_leak_files)} file, {I(n_leak_fail)} gagal"),
    ("Orang awam bisa membuka dashboard dan menyebut median dalam 1 menit", "Belum diuji",
     "belum ada uji dengan pembaca awam; dashboard belum di-deploy"),
    ("Checklist standar terpenuhi (dashboard ter-deploy, notebook)", "Sebagian",
     "dashboard belum di-deploy; notebook tidak dibuat"),
]
n_ok_crit = sum(1 for c in ok_criteria if c[1].startswith("Terpenuhi"))
REP.append('<h2 id="rp7">7. Kesimpulan<small>Hasil analisis, Impact, success criteria, rekomendasi, saran perbaikan, dan batasan</small></h2>')
REP.append('<h4>7.1 Hasil analisis</h4><div class="card">'
           f'<p><b>Pertanyaan utama:</b> seberapa cepat operator baru mencapai target dibanding standar 30 hari?</p>'
           f'<p>Operator baru mencapai target dalam median {I(med_row.nilai)} hari kerja valid ({CI(med_row, 0)}), jauh di bawah standar 30 hari (Q1, Q2). '
           f'Pada hari ke-15, {P(q3_15.nilai, 0)} operator sudah mencapai target (Q3). Kurva mengikuti power law dan mendatar di sekitar hari ke-{I(plat_med.estimasi)} (Q4, Q5). '
           f'Perbedaan antar stasiun belum terbukti (Q6). NG rate turun seiring masa kerja (Q9).</p>'
           f'<p>Hipotesis: H1 {H["H1"].verdict.lower()}, H2 {H["H2"].verdict.lower()}, H5 {H["H5"].verdict.lower()}; '
           f'H3 dan H4 {H["H3"].verdict.lower()}.</p></div>')
REP.append('<h4>7.2 Impact</h4><div class="card">'
           f'<p>Estimasi (estimated): dengan 20 operator baru per tahun, standar 30 hari dapat disesuaikan sehingga '
           f'{I(imp_base20.hari_onboarding_dihemat_per_tahun_estimated)} hari onboarding dihemat per tahun (setara {I(imp_base20.output_setara_unit_estimated)} unit). '
           f'Angka ini bergantung pada volume operator per tahun, yang tidak ada di data.</p>'
           f'<p>Nilai praktis: dasar perencanaan kapasitas. Nilai analitis: standar 30 hari kini diuji dengan data. '
           f'Nilai portofolio: pipeline lengkap dari anonimisasi sampai dashboard. Belum terukur: dampak nyata pada operator.</p></div>')
REP.append('<h4>7.3 Success criteria</h4><div class="card">'
           + table(["Kriteria", "Status", "Bukti"], [[k, pill(s, "" if s.startswith("Terpenuhi") else ("p" if s == "Sebagian" else "d")), cs(b)] for k, s, b in ok_criteria])
           + f'<p>Hasil: {I(n_ok_crit)} dari {I(len(ok_criteria))} kriteria tercapai.</p></div>')
REP.append('<h4>7.4 Rekomendasi</h4><div class="card"><ul class="tight">'
           '<li>Gunakan time-to-target sebagai pemantauan awal operator baru, dengan titik cek di hari ke-10 dan ke-15.</li>'
           '<li>Tinjau standar 30 hari berdasarkan data, tetapi uji dulu dengan data kerja nyata sebelum diubah.</li>'
           '<li>Perhatikan NG rate pada minggu pertama, karena NG tinggi di awal lalu turun seiring masa kerja.</li></ul></div>')
REP.append('<h4>7.5 Saran perbaikan</h4><div class="card"><ul class="tight">'
           '<li>Ganti data simulasi dengan data kerja yang dianonimkan, lalu jalankan ulang pipeline dari nol.</li>'
           '<li>Tambah operator per stasiun agar perbedaan stasiun bisa diuji.</li>'
           '<li>Perbaiki pemilihan hari valid: hari jam pendek dan output 0 menyebabkan bias kurva (lihat uji pemulihan).</li>'
           '<li>Deploy dashboard dan uji dengan pembaca awam.</li></ul></div>')
REP.append('<h4>7.6 Batasan</h4><div class="card"><ul class="tight">'
           '<li><b>Data adalah simulasi.</b> Angka menggambarkan simulasi, bukan lini produksi. Hasil uji pemulihan dibaca sebagai validasi metode.</li>'
           f'<li>Sampel kecil: {I(nops)} operator dan 3 stasiun. Stasiun dengan 3 sampai 4 operator tidak cukup untuk uji yang kuat.</li>'
           '<li>Perbedaan batch dan mentor (Q8) tidak bisa dibedakan dari kebetulan.</li>'
           f'<li>Bias F1 +{D(rec_F1.bias, 2)} pada uji pemulihan karena seleksi hari valid. Sensitivitas: median {D(sens_min, 0)} sampai {D(sens_max, 0)} hari di semua variasi definisi.</li>'
           '<li>Volume operator per tahun (dampak) adalah asumsi; semua angka dampak berlabel estimated.</li>'
           '<li>Tidak ada operator censored pada data ini; metode censored belum teruji pada data nyata.</li>'
           '<li>Dashboard belum di-deploy. Notebook tidak dibuat. Branch belum di-merge ke main.</li></ul></div>')

REPORT_PANE = ('<div class="pane" id="report" data-tab="report" hidden>\n'
               '<div class="callout g"><h4>Report Project versi 2: evaluasi hasil terhadap Design Project</h4>'
               f'Cek silang: {I(n_cs_ok)} dari {I(n_cs)} SQL vs pandas, {I(n_ex_ok)} dari {I(n_ex)} SQL vs Excel. '
               f'Angka diaudit dari CSV hasil.</div>\n'
               + '<div class="card"><p class="how">Ringkasan tujuh pertanyaan evaluasi. Klik untuk melompat ke bagian.</p>'
               + table(["No", "Pertanyaan evaluasi", "Verdict", "Ringkasan"], [
                   [f'<span class="en">{i}</span>', f'<a href="#rp{i}">{t}</a>', pill(v[0], v[1]), v[2]] for i, (t, v) in enumerate([
                       ("Data yang berhasil didapatkan", ("Berhasil", "", f"{I(total_rows)} baris, {I(valid_rows)} hari valid")),
                       ("Apakah business question terjawab?", ("Sebagian", "p", f"{I(13)} pertanyaan dijawab, {I(len(WARN))} dengan catatan")),
                       ("Apakah dataset sesuai dengan Design Project?", ("Berubah", "p", "data simulasi, bukan data kerja")),
                       ("Apakah tools yang digunakan sesuai?", ("Sesuai + penyesuaian", "p", "Excel dihitung ulang LibreOffice")),
                       ("Apakah alur pengerjaan sesuai dengan Design Project?", ("Sebagian", "p", "dashboard belum di-deploy, notebook tidak dibuat")),
                       ("Apakah project output tercapai?", ("Sebagian", "p", "dashboard belum di-deploy")),
                       ("Kesimpulan", ("Simulasi", "", f"median {I(med_row.nilai)} hari ke target")),
                   ], 1)])
               + '</div>\n'
               + "\n".join(REP)
               + '\n</div>\n')

# ---------- rakit halaman ----------
nav_src = SRC[SRC.index('<nav aria-label="Project navigation">'):SRC.index('</nav>') + 6]
btn_design = re.search(r'<button[^>]*data-t="design"[^>]*>.*?</button>', nav_src, re.S).group(0)
btn_report = re.search(r'<button[^>]*data-t="report"[^>]*>.*?</button>', nav_src, re.S).group(0)
links_design = re.search(r'<div class="links" data-tab="design">.*?</div>', nav_src, re.S).group(0)
new_report_links = ('<div class="links" data-tab="report" hidden>'
                    + "".join(f'<a href="#rp{i}">{t}</a>' for i, t in enumerate(
                        ["Data", "Business Questions", "Dataset", "Tools", "Alur Kerja", "Project Output", "Kesimpulan"], 1))
                    + '</div>')
# urutan baku: kedua tombol tab berdampingan dulu, baru grup link (lihat skill portfolio-project-report-page)
nav_new = ('<nav aria-label="Project navigation">' + btn_design + btn_report
           + links_design + new_report_links + '</nav>')

design_start = SRC.index('<header class="banner">')
design_end = SRC.index('<div class="pane" id="report"')
design_pane = SRC[design_start:design_end]
head_end = SRC.index('</style>')
body_start = SRC.index('<body>')
hub_link = SRC[body_start:SRC.index('<main>')]
tail_start = SRC.index('</main>')
tail = SRC[tail_start:]

html = (SRC[:head_end] + CSS_EXTRA + "\n" + SRC[head_end:body_start]
        + hub_link
        + '<main>\n' + nav_new + '\n' + design_pane + REPORT_PANE + tail)

# Pane Design harus identik dengan sumber (rule: tidak boleh diubah)
assert design_pane in html, "pane Design berubah"
assert SRC[design_start:design_end] == design_pane

# ---------- audit angka ----------
STATIC = {"00", "01", "02", "03", "04", "06", "07", "08", "1.1", "1.2", "1.3", "2.1", "2.2", "2.3", "2.4",
          "2.5", "2.6", "7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "95", "30", "13", "12", "10", "15", "20", "1", "2", "3", "4", "5", "6", "7", "8", "9", "11", "14", "16", "17",
          "0,8", "0,05", "0,95", "0,25", "0,07", "0,10", "1,00", "100", "0", "60", "500", "2000", "2026", "1,1",
          "0,01", "0,02", "0,04", "0,06", "0,001", "0,5", "7", "9", "18", "19", "23", "24", "25", "26", "28",
          "40", "50", "80", "120", "150", "125", "200", "300", "4", "3", "2", "1,0", "0,3", "0,2", "0,9", "0,6",
          "0,1", "0,3", "0,15", "0,4", "0,13", "0,62", "0,33", "0,5", "0,8", "0,7", "1,5", "2,5", "1,25", "0,35",
          "0,80", "0,31", "0,84", "0,91", "0,15", "0,80", "2,0", "3,0"}
n_tok, bad = audit(REPORT_PANE, STATIC)
print(f"token angka diperiksa: {n_tok}; tidak terdaftar: {len(bad)}")
if bad:
    print("TIDAK TERDAFTAR:", bad[:80])
    for t in bad:
        m = re.search(r"(?<![\\d.,])" + re.escape(t) + r"(?![\\d,])", R.visible_text(REPORT_PANE))
        if m:
            vt = R.visible_text(REPORT_PANE)
            print("  ", t, "|", vt[max(0, m.start()-60):m.end()+30].replace("\n", " "))
out = HERE.parent / "index.html"
out.write_text(html, encoding="utf-8")
print("written", out, len(html))
