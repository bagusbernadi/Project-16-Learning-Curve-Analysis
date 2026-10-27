# Definisi dan asumsi

Dokumen ini memuat definisi yang tidak ada di rancangan. Setiap butir diberi label:
**[Rancangan]** = sesuai bunyi rancangan; **[Asumsi]** = ditetapkan di sini, diuji sensitivitasnya.

## 1. Mencapai target

**[Rancangan]** Target tercapai dicatat pada hari pertama dari tiga hari berturut-turut yang mencapai target.

**[Asumsi] Target harian per stasiun.** Target = `target_per_day` di `station_target` (skala anonim):
ST-A 120, ST-B 100, ST-C 80. Target 100% pada ambang dasar.

**[Asumsi] Hari valid.** Hanya hari valid yang masuk kurva dan streak. Hari lain dilewati (bukan dihitung nol):
- tidak hadir (`present = 0`);
- jam kerja tidak penuh (`work_hours < 7`), dilewati dari kurva dan streak (lihat sensitivitas);
- output 0 pada hari hadir, dicurigai data hilang atau mesin berhenti;
- pindah stasiun (`station_code` berbeda dari stasiun utama operator). Waktu hanya dihitung dari hari sebelum pindah.

**[Asumsi] Nomor hari.** `valid_day` = nomor hari kerja valid per operator (1, 2, 3, ...). Time-to-target
dinyatakan dalam `valid_day` ("hari kerja valid"), bukan hari kalender. Hari tidak hadir tidak menambah nomor.
Catatan: nomor ini membuat time-to-target sedikit lebih kecil daripada hitungan kalender kerja.

**[Asumsi] Time-to-target.** `ttt_day` = `valid_day` pada hari pertama dari tiga hari valid berturut-turut dengan
`ok_qty >= target`. Jika belum tercapai, operator dicatat *censored* dengan `last_valid_day` sebagai batas bawah.

## 2. Output dan NG

**[Rancangan]** Unit NG tidak dihitung sebagai output. `ok_qty` adalah output.

**[Asumsi] Persen target** = `ok_qty / target_per_day`. Dipakai sebagai skala bersama antar stasiun.

**[Asumsi] NG rate** = `ng_qty / (ok_qty + ng_qty)` per hari; rata-rata operator = jumlah NG / jumlah total pada hari valid.

**[Asumsi] Minggu pertama** = hari valid 1 sampai 5. **Minggu masa kerja** = `(valid_day - 1) // 5 + 1`.

## 3. Operator censored dan operator yang berhenti

**[Rancangan]** Operator yang keluar sebelum mencapai target tetap dicatat.
Hasil: satu operator (OP-09) berhenti setelah hari hadir ke-28 dan sudah mencapai target sebelum itu.
Jumlah operator censored = 0. Metode dibuat untuk kasus censored (ttt kosong, `reached = 0`),
tetapi tidak ada kasus yang muncul pada data ini.

## 4. Kurva belajar

**[Asumsi] Bentuk kurva** (dibandingkan dengan kriteria yang sama, lihat `results/2-analysis/curve_model_compare.csv`):
- power law: `f(d) = P - (P - F1) * d^(-b)`;
- eksponensial: `f(d) = P - (P - F1) * exp(-k (d - 1))`;
- linear per segmen (satu titik patah): `f(d) = F1 + s1 * min(d-1, c-1) + s2 * max(d-c, 0)`.

**[Asumsi] Pemilihan model** = leave-one-operator-out: kurva gabungan dilatih pada 9 operator dan
memprediksi operator ke-10 yang tidak ikut dilatih. Model dengan RMSE rata-rata terkecil dipilih.
Konfigurasi tidak dipilih ulang setelah melihat hasil.

**[Asumsi] Learning rate** = `b` pada power law (per operator). **Plateau** = `P`. **Hari mulai mendatar** =
hari pertama `f(d) >= 0.95 P`; NaN bila tidak tercapai dalam 500 hari.

## 5. Perbandingan dan uji

- Q1 median dan rentang: median time-to-target dari operator yang mencapai target; CI 95% bootstrap per operator (B = 2000, seed 16).
- Q2 Wilcoxon satu sampel, alternatif satu sisi `median < 30`.
- Q3 persen operator dengan Wilson CI 95%.
- Q6 Kruskal-Wallis antar stasiun; daya uji rendah (n 3 sampai 4 per stasiun).
- Q7 Spearman output minggu pertama vs time-to-target.
- Q8 Mann-Whitney per batch dan per mentor (sampel 5 vs 5; hanya tambahan).
- Q9 tren NG rate per minggu masa kerja. Baris operator-minggu tidak independen, sehingga **p-value tidak dilaporkan**.
- Q10 Spearman time-to-target vs NG rate rata-rata per operator.

**[Asumsi] Kriteria keputusan hipotesis** (ditetapkan sebelum hasil dilihat, ada di `08_stats.py`):
- H1 Terbukti bila median < 20 dan p (Wilcoxon) < 0,05.
- H2 Terbukti bila power law menang (RMSE lebih kecil) pada ≥ 50% operator in-sample. Pemilihan model LOOCV dilaporkan terpisah.
- H3 Terbukti bila arah sesuai (langkah lebih banyak = lebih lama) dan Kruskal-Wallis p < 0,05; "Belum bisa disimpulkan" bila arah sesuai tanpa signifikansi.
- H4 Terbukti bila rho < 0 dan p < 0,05; "Belum bisa disimpulkan" bila rho < 0 tanpa signifikansi.
- H5 Terbukti bila median Spearman per operator < 0 dan batas atas CI < 0.

## 6. Dampak (Q11)

**[Rancangan]** Hari onboarding dihemat per tahun = (30 − median time-to-target) × jumlah operator baru per tahun.
**[Asumsi] Volume operator baru per tahun tidak ada di data.** Skenario 10, 20, 40 per tahun dihitung dan semua
diberi label `estimated`. Output setara = hari dihemat × rata-rata target harian (skala anonim), juga estimasi.
Angka tidak dikonversi ke rupiah.

## 7. Sensitivitas definisi "mencapai target" (`09_sensitivity.py`)

Variasi: streak 1, 2, 3 hari; ambang 90% dan 100%; hari jam tidak penuh dilewati atau dimasukkan.

Hasil ringkas (`results/2-analysis/sensitivity_ttt.csv`):

| Streak | Ambang | Jam tidak penuh | Median (hari valid) | Rentang | p Wilcoxon vs 30 |
|---|---|---|---|---|---|
| 1 | 90% | dilewati | 5 | 4 sampai 7 | < 0,001 |
| 1 | 100% | dilewati | 7 | 5 sampai 11 | < 0,001 |
| 2 | 90% | dilewati | 6,5 | 4 sampai 8 | < 0,001 |
| 2 | 100% | dilewati | 9,5 | 6 sampai 23 | < 0,001 |
| 3 | 90% | dilewati | 7 | 4 sampai 9 | < 0,001 |
| **3** | **100%** | **dilewati (dasar)** | **11** | **6 sampai 23** | **< 0,001** |
| 3 | 100% | dimasukkan | 12 | 6 sampai 23 | < 0,001 |

Kesimpulan sensitivitas: median berada di 5 sampai 12 hari pada semua variasi. Semua 10 operator mencapai target
di setiap variasi. Keputusan H1 tidak berubah. Konfigurasi dasar tidak diganti.

## 8. Uji pemulihan

Lihat `docs/simulation_spec.md` dan `results/2-analysis/recovery_summary.csv`. Toleransi (P ±0,05, F1 ±0,10,
b ±0,25) ditetapkan sebelum hasil dilihat.
