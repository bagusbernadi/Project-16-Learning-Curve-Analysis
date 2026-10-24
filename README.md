[← Back to portfolio](https://bagusbernadi.github.io/)

# Project 16: Learning Curve Analysis

**Status: Design (rancangan).** Halaman rancangan ada di [`index.html`](index.html). Analisis, dashboard, dan angka hasil belum dikerjakan, sehingga bagian Analysis, Recommendation, dan Impact di bawah masih kosong.

**Tujuan:** membangun analisis kurva belajar dari data output harian operator baru yang dianonimkan, untuk mengukur berapa hari operator mencapai target output dibanding standar 30 hari dan faktor apa yang membedakan kecepatannya.

| | |
|---|---|
| Kategori | Manufaktur (data anonim) |
| Tingkat | Mudah sampai sedang |
| Data | Data kerja yang dianonimkan (nama operator, stasiun, dan produk diganti kode; angka diskala) |
| Tools | DuckDB + SQL, Python (pandas, NumPy, SciPy), Excel, Streamlit + Plotly |

## 1. Problem

**Pertanyaan utama:** Seberapa cepat operator baru mencapai target output harian dibanding standar 30 hari, dan apa yang membedakan operator yang cepat dan lambat?

Rancangan memecahnya menjadi 13 pertanyaan (8 Utama, 4 Pendukung, 1 Tambahan) dalam tema kecepatan, bentuk kurva, perbedaan antar operator dan stasiun, kualitas, dampak, dan validitas. Daftar lengkap ada di bagian 2 halaman rancangan.

## 2. Data

- Data kerja output harian operator baru yang dianonimkan: kode operator OP-01 sampai OP-10, stasiun ST-A sampai ST-C, angka output dan target dikalikan faktor rahasia, tanggal diubah menjadi hari ke-n. Data asli dan tabel pemetaan kode tidak masuk repositori.
- Ukuran (perkiraan): 10 operator, 3 stasiun, ±60 hari kerja per operator, ±600 baris.
- Rencana tabel: `new_operator`, `daily_output`, `station_target`, `experienced_baseline`.

## 3. Analysis

Belum dikerjakan. Rencana langkah (12 langkah, tahap A sampai D) ada di bagian 6 halaman rancangan: time-to-target dengan SQL window function, curve fitting (power law vs eksponensial), uji Wilcoxon terhadap 30 hari, dan perbandingan antar stasiun.

Hipotesis yang akan diuji (belum terbukti):
1. Median time-to-target jauh di bawah 30 hari (catatan awal: 10–20 hari).
2. Kurva cepat di awal lalu melambat.
3. Stasiun dengan langkah kerja lebih banyak butuh waktu lebih lama.
4. Output minggu pertama berkorelasi dengan time-to-target.
5. NG rate turun seiring output naik.

## 4. Recommendation

Belum dikerjakan. Output yang direncanakan: usulan standar dan program pendampingan berdasarkan data.

## 5. Impact

Belum dikerjakan. Rumus yang akan dipakai (semua hasil diberi label `estimated`):

```
Hari onboarding dihemat per tahun = (30 − median time-to-target) × jumlah operator baru per tahun
```

## Batasan yang sudah diketahui

- 10 operator adalah sampel kecil.
- Operator yang keluar sebelum mencapai target tetap dicatat.
- Belum ada data defect operator lama sebagai pembanding.
- Pola belum tentu penyebab.

## Struktur repository

```
index.html   Halaman rancangan project (bisa dibuka di browser atau lewat GitHub Pages)
README.md    Dokumen ini
```

Folder `docs/`, `data/anon/`, `scripts/`, `sql/`, `notebooks/`, `dashboard/`, dan `outputs/` ditambahkan saat pengerjaan dimulai. Folder `data/private/` tidak pernah di-commit.
