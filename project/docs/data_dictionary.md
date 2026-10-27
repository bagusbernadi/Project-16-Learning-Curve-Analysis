# Kamus data

Data dianonimkan (`project/data/anon/`). Sumber: simulasi (lihat `simulation_spec.md`).

## new_operator (satu baris per operator baru)
| Kolom | Tipe | Arti |
|---|---|---|
| operator_code | text | kode operator, OP-01 sampai OP-10 |
| station_code | text | stasiun utama: ST-A (Assembly), ST-B (Bonding), ST-C (Finishing) |
| batch_code | text | kelompok training (B1, B2) |
| mentor_code | text | kode pendamping (M1, M2) |
| start_week | int | minggu mulai masa kerja (selalu 1 pada data ini) |

## daily_output (satu baris per operator per hari kalender kerja)
| Kolom | Tipe | Arti |
|---|---|---|
| operator_code | text | kode operator |
| work_day | int | hari ke-n masa kerja (hari kalender kerja, termasuk hari tidak hadir) |
| station_code | text | stasiun pada hari itu |
| ok_qty | int | output OK (skala anonim, sudah dikali faktor 0,8) |
| ng_qty | int | unit NG (tidak dihitung sebagai output) |
| work_hours | real | jam kerja (0 jika tidak hadir) |
| present | int | 1 = hadir, 0 = tidak hadir |

Kolom tambahan di `project/data/clean/daily_output_clean.csv` (dibuat `02_clean.py`):
`alasan` (valid, tidak hadir, jam tidak penuh, output 0, pindah stasiun), `valid` (0/1), `valid_day` (nomor hari valid),
`target`, `pct_target`, `ng_rate`.

## station_target (referensi)
| Kolom | Tipe | Arti |
|---|---|---|
| station_code | text | kode stasiun |
| station_alias | text | nama umum: Assembly, Bonding, Finishing |
| target_per_day | int | target output harian (skala anonim): 120, 100, 80 |
| valid_from | int | berlaku mulai hari ke-n masa kerja (1) |

## experienced_baseline (pembanding operator berpengalaman)
| Kolom | Tipe | Arti |
|---|---|---|
| station_code | text | stasiun |
| week | int | minggu masa kerja (1 sampai 9) |
| median_ok_qty | real | median output OK operator berpengalaman pada minggu itu |
| median_ng_rate | real | median NG rate |
| n_operator | int | jumlah operator berpengalaman |
| n_rows | int | jumlah baris |

## Aturan anonimisasi
1. Nama operator diganti kode (OP-xx untuk operator baru, EXP-xx untuk berpengalaman). Tabel pemetaan di `project/data/mapping_key.csv`, tidak dikomit.
2. Nama stasiun diganti kode ST-A, ST-B, ST-C dengan nama umum.
3. Nama produk dan kolom keterangan bebas dihapus.
4. Tanggal kalender diganti `work_day`.
5. Output dan target dikalikan faktor yang sama (0,8). Rasio target tetap.

Pemeriksaan otomatis: `project/results/1-data-preparation/anonymization_checklist.csv`.
Pemindaian kebocoran terhadap seluruh file yang dikomit: `project/results/3-presentation/leak_scan.csv`.
