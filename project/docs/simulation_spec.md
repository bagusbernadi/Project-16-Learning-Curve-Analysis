# Spesifikasi simulasi (data simulasi, bukan lini produksi)

**Data project ini adalah simulasi.** Angka menggambarkan simulasi dengan kurva belajar yang ditanam,
bukan catatan output nyata. Pemilihan simulasi dibuat oleh user karena data kerja tidak dilampirkan.

Pipeline: `00_simulate_raw.py` (nama dan produk karangan) -> `01_anonymize.py` (kode, skala faktor 0,8) -> analisis.
Seed: 16. Semua parameter ada di `project/code/common.py` (blok `TRUE`).

## Ground truth yang ditanam

Kurva belajar (power law), `f(d) = output / target`, d = hari hadir ke-n:

`f(d) = P_i - (P_i - F1_i) * d^(-b_i)`

| Parameter | Nilai | Keterangan |
|---|---|---|
| P (plateau) | rata-rata 1,10, sd 0,04 per operator | plateau di atas target |
| F1 (hari pertama) | rata-rata 0,25, sd 0,05 per operator | dibatasi 0,05 sampai 0,6 |
| b (learning rate) | 0,70 ST-A; 0,85 ST-B; 1,00 ST-C, dikali exp(N(0; 0,12)) per operator | makin banyak langkah, makin lambat |
| Noise harian | lognormal, sd 0,07 | |
| NG rate | 0,02 + 0,08 exp(-0,05 d) | NG turun seiring masa kerja |

Data kotor yang ditanam: hari tidak hadir (4%), output 0 (1% hari hadir), jam kerja tidak penuh (6% hari hadir, 4 sampai 6 jam),
operator pindah stasiun (OP-06 ke ST-C pada hari hadir ke-25), operator berhenti (OP-09 setelah hari hadir ke-28).

Operator berpengalaman (pembanding): 4 per stasiun, output plateau 1,05, noise sd 0,05, NG 2%.

## Hal yang sengaja tidak dijanjikan

- Efek perbedaan batch dan mentor tidak ditanam (Q8 hanya deskriptif).
- Efek stasiun ditanam sebagai gradien nominal, tetapi per operator berbeda karena noise. Urutan stasiun hasil fit
  bisa berbeda dari gradien nominal (lihat `recovery_station_order.csv`).
- Daya uji per stasiun rendah (3 sampai 4 operator).

## Uji pemulihan (`11_recovery.py`)

Hanya skrip ini yang membaca `data/raw/ground_truth_operator.csv`. Toleransi (ditetapkan sebelum melihat hasil):
P ±0,05; F1 ±0,10; b ±0,25.

Hasil (`results/2-analysis/recovery_summary.csv`): P 9 dari 10 dalam toleransi; F1 8 dari 10; b 9 dari 10.
Bias F1 positif (+0,07). Penyebab yang diduga: hari valid membuang hari jam pendek dan output 0 (seleksi pada outcome),
sehingga kurva awal terangkat. Ini dilaporkan sebagai keterbatasan dan tidak diperbaiki setelah melihat hasil.

## Yang di-commit dan yang tidak

- Dikomit: `project/data/anon/` (data sudah dianonimkan), kode, dan hasil.
- Tidak dikomit: `project/data/raw/` (berisi nama karangan dan ground truth), `project/data/mapping_key.csv`,
  dan `learning.duckdb`. Ketiganya dibuat ulang oleh skrip dengan seed yang sama.
