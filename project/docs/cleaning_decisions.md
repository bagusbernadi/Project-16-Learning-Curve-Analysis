# Keputusan cleaning (Q12)

Sumber: `project/results/1-data-preparation/data_quality.csv` dan `cleaning_log.csv`. Setiap baris hari yang dilewati
ada di log dengan alasannya.

| Kategori | Jumlah baris | Proporsi | Keputusan |
|---|---|---|---|
| baris output harian (operator baru) | 570 | 100% | dasar |
| tidak hadir | 18 | 3,2% | dilewati; bukan dihitung nol |
| jam tidak penuh (< 7 jam) | 23 | 4,0% | dilewati dari kurva dan streak (sensitivitas: dimasukkan) |
| output 0 pada hari hadir | 4 | 0,7% | dilewati; dicurigai data hilang atau mesin berhenti |
| pindah stasiun | 36 | 6,3% | dilewati; waktu hanya dari sebelum pindah |
| valid | 489 | 85,8% | dipakai |

Catatan:
- Persentase dihitung dari 570 baris, termasuk baris yang tidak hadir.
- "Pindah stasiun" mencakup seluruh hari setelah pindah (termasuk hari tidak hadir yang kebetulan setelah pindah).
  Hasil: operator yang pindah (OP-06) hanya punya 23 hari valid sebelum pindah.
- Operator dengan hari valid paling sedikit: OP-06 (23) dan OP-09 (26), keduanya karena berhenti atau pindah lebih awal.
  Ini membuat NG rate rata-rata mereka lebih tinggi (perancu, lihat Q10).

## Keterbatasan (dilaporkan, tidak diubah)

Menyaring hari jam pendek dan output 0 adalah seleksi berdasarkan outcome. Pada uji pemulihan (`recovery_summary.csv`)
ini menaikkan kurva awal: bias F1 +0,07. Sensitivitas dengan hari jam tidak penuh dimasukkan ada di `sensitivity_ttt.csv`
(median 12 dibanding 11, keputusan H1 tidak berubah).
