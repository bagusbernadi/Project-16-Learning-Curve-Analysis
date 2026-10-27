# Data

**Data project ini adalah simulasi.** Tidak ada data kerja operator yang dipakai. Angka menggambarkan kurva belajar
yang ditanam di simulator, bukan lini produksi.

| Folder / file | Isi | Di Git |
|---|---|---|
| `raw/` | Hasil simulator (nama dan produk karangan, ground truth) | Tidak (dibuat ulang dengan seed 16) |
| `mapping_key.csv` | Pemetaan nama karangan ke kode | Tidak |
| `clean/` | Data setelah cleaning dengan alasan tiap hari | Tidak (dibuat ulang) |
| `anon/` | Data yang sudah dianonimkan (kode operator, stasiun, work_day) | Ya |

Sumber: `project/code/1-data-preparation/python/00_simulate_raw.py`, parameter di `project/code/common.py`,
spesifikasi di `project/docs/simulation_spec.md`. Lisensi: tidak berlaku (data buatan).
