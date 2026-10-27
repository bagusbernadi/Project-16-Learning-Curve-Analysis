"""15: Pindai kebocoran identitas. Mencari nama asli (dari tabel pemetaan), nama stasiun asli, nama produk,
dan teks keterangan mentah di seluruh file yang akan di-commit.

Aturan: target 0 kecocokan di data, hasil, dokumen, README, dan halaman. Kode simulator (00) dan
anonimisasi (01) boleh memuat nilai karangan karena keduanya mendefinisikan pemetaan; kecocokan di sana
dicatat dan diberi label, bukan dihitung sebagai kebocoran.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pandas as pd
import common as C

REPO = C.ROOT.parent
key = pd.read_csv(C.MAPPING_KEY)
names = key[key.jenis.isin(["operator", "operator_pembanding"])].asli.tolist()
stations = key[key.jenis == "stasiun"].asli.tolist()
notes = ["PLC-1x8-Kode-K", "PLC-1x8-Kode-L", "Lini Assembly 1", "Lini Bonding 2", "Lini Finishing 3",
         "jam pulang awal", "mesin berhenti (catatan)"]
# Kebocoran parsial: kata nama (min. 5 huruf) dari nama orang saja; istilah keterangan tidak dipecah
name_parts = {w for n in names for w in n.split() if len(w) >= 5}
TERMS = {"nama operator": names, "nama stasiun": stations + ["Lini Assembly 1", "Lini Bonding 2", "Lini Finishing 3"],
         "produk dan keterangan": [t for t in notes if not t.startswith("Lini")],
         "bagian nama operator": sorted(name_parts)}

ALLOW_DEFINING = {
    "project/code/1-data-preparation/python/00_simulate_raw.py",
    "project/code/1-data-preparation/python/01_anonymize.py",
    "project/code/3-presentation/python/15_scan_leak.py",
}
SKIP_DIRS = {"__pycache__", ".git"}
SKIP_FILES = {"leak_scan.csv", "mapping_key.csv", "raw_output.csv", "raw_station_target.csv", "ground_truth_operator.csv",
              "learning.duckdb", "learning.duckdb.wal"}
TEXT = {".csv", ".md", ".py", ".html", ".sql", ".txt", ".css", ".js", ".yaml", ".yml", ".toml", ".txt"}
roots = [REPO / "README.md", REPO / "index.html", REPO / "design-and-report", REPO / "project", REPO / ".gitignore"]
files = []
for r in roots:
    if r.is_file():
        files.append(r)
    elif r.exists():
        for p in r.rglob("*"):
            if p.is_file() and not (set(p.parts) & SKIP_DIRS) and p.name not in SKIP_FILES \
                    and (p.suffix in TEXT or p.name == ".gitignore") \
                    and "data/raw" not in p.as_posix() and not p.as_posix().startswith(str(C.RAW)):
                files.append(p)

rows = []
for p in sorted(files):
    rel = p.relative_to(REPO).as_posix()
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    hits = {k: sum(1 for t in v if t in text) for k, v in TERMS.items()}
    n_hit = sum(hits.values())
    label = "kode pemetaan (diizinkan)" if rel in ALLOW_DEFINING else "data/hasil/dokumen"
    rows.append(dict(file=rel, jenis=label, kecocokan=n_hit,
                     kategori=";".join(f"{k}={v}" for k, v in hits.items() if v)))
scan = pd.DataFrame(rows)
scan["hasil"] = scan.apply(lambda r: "lulus" if r.kecocokan == 0 else (
    "diizinkan (kode pemetaan)" if r.jenis.startswith("kode") else "gagal"), axis=1)
scan.to_csv(C.RES3 / "leak_scan.csv", index=False)  # hanya jumlah dan kategori, tidak menulis istilah asli
print(f"file dipindai: {len(scan)}; file gagal: {int((scan.hasil == 'gagal').sum())}")
print(scan[scan.kecocokan > 0][["file", "jenis", "kecocokan", "hasil"]].to_string(index=False))
assert int((scan.hasil == "gagal").sum()) == 0, "ada kebocoran identitas di file yang akan di-commit"
