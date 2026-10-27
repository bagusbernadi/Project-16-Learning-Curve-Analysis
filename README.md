[← Back to portfolio](https://bagusbernadi.github.io/)

# Project 16: Learning Curve Analysis

| | |
|---|---|
| Kategori | Manufaktur PLC Splitter, learning curve |
| Tingkat | Menengah |
| Data | **Simulasi** (tidak ada data kerja; lihat `project/docs/simulation_spec.md`) |
| Tools | Python (pandas, NumPy, SciPy), DuckDB + SQL, Excel (cek silang), Streamlit + Plotly, Matplotlib |

Status: **Selesai di branch `project-16-build`** (belum di-merge ke `main`). Dashboard belum di-deploy.

Pertanyaan utama: seberapa cepat operator baru mencapai target output harian dibanding standar 30 hari, dan apa yang
membedakan operator yang cepat dan lambat?

## 1. Problem
Standar 30 hari untuk operator baru belum pernah diuji dengan data. Jika operator biasanya mencapai target lebih cepat,
standar itu terlalu panjang. Jika lebih lambat, operator perlu bantuan lebih awal.

## 2. Data
Data simulasi 10 operator baru dan 3 stasiun (ST-A, ST-B, ST-C), dibuat dengan seed tetap. Data dianonimkan
(kode OP-xx, ST-x; tanggal menjadi `work_day`). Cleaning menyisakan hari valid dan mencatat alasan tiap hari yang dilewati.
Detail: `project/docs/cleaning_decisions.md`, `project/docs/data_dictionary.md`.

## 3. Analysis
- Time-to-target: hari valid pertama dari tiga hari berturut-turut dengan output ≥ target.
- Bentuk kurva: power law dipilih dengan leave-one-operator-out (RMSE 0,0832; eksponensial 0,0878; linear per segmen 0,0920).
- Uji: Wilcoxon satu sampel terhadap 30 hari, Kruskal-Wallis antar stasiun, Spearman, Mann-Whitney.
- Sensitivitas definisi (12 kombinasi) dan uji pemulihan parameter yang ditanam.
- Cek silang: SQL vs pandas 10 dari 10 operator, SQL vs Excel (dihitung ulang LibreOffice) 3 dari 3.

## 4. Recommendation
- Pantau operator baru pada hari ke-10 dan ke-15. Pada hari ke-15, 90% operator sudah mencapai target (CI 60% sampai 98%).
- Tinjau standar 30 hari, tetapi uji dulu dengan data kerja nyata sebelum diubah.
- Perhatikan NG rate pada minggu pertama; NG turun dari sekitar 7,9% (minggu 1 sampai 2) ke 2,3% (dua minggu terakhir).

## 5. Impact
Median time-to-target 11 hari (CI 7 sampai 15). Dengan asumsi 20 operator baru per tahun, selisih 30 − 11 hari setara
380 hari onboarding per tahun (**estimated**; volume operator per tahun adalah asumsi, bukan data).

## Hipotesis
| ID | Verdict |
|---|---|
| H1 | Terbukti |
| H2 | Terbukti |
| H3 | Belum bisa disimpulkan (arah sesuai, tidak signifikan) |
| H4 | Belum bisa disimpulkan (rho −0,35, p = 0,323) |
| H5 | Terbukti |

## Batasan
- **Data adalah simulasi.** Angka tidak boleh dikutip sebagai fakta lini produksi. Lisensi tidak berlaku.
- Sampel kecil: 10 operator, 3 stasiun dengan 3 sampai 4 operator per stasiun. Perbedaan batch dan mentor tidak bisa dibedakan dari kebetulan.
- Uji pemulihan menunjukkan bias F1 positif (+0,07) akibat seleksi hari valid. Tidak diperbaiki setelah melihat hasil.
- Tidak ada operator censored pada data ini; penanganan censored belum teruji pada data nyata.
- Dashboard Streamlit diuji dengan AppTest, **belum di-deploy** (item terbuka).
- Notebook `analysis.ipynb` tidak dibuat. Output opsional (template Excel, slide) tidak dibuat.
- Branch `project-16-build` perlu dihapus setelah review, jika sudah di-merge atau tidak dipakai.

## Menjalankan
Dari folder `project/`, jalankan skrip secara berurutan sesuai nomor (`code/*/python/00_...` sampai `15_...`),
lalu dari root repo: `python3 design-and-report/src/build_report.py`. Paket: `project/requirements.txt`.

## Struktur repository
```
README.md
index.html                 pengalihan ke design-and-report/
.gitignore
design-and-report/         index.html (tab Design + Report), src/
project/
  code/                    program (common.py, 1-data-preparation, 2-analysis, 3-presentation)
  results/                 hasil analisis per tahap
  data/                    raw/ dan clean/ (tidak di-commit), anon/, README.md
  docs/                    definitions.md, data_dictionary.md, cleaning_decisions.md, simulation_spec.md
  outputs/                 crosscheck.xlsx, infografik (PNG dan PDF)
  requirements.txt
```
