"""Path dan parameter bersama Project 16 (Learning Curve Analysis).

Semua parameter ground truth simulasi ada di sini (lihat docs/simulation_spec.md).
Parameter ini hanya dipakai simulator (00) dan skrip uji pemulihan (11). Skrip analisis
tidak boleh membaca nilai ini.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # project/
RAW = ROOT / "data" / "raw"
ANON = ROOT / "data" / "anon"
CLEAN = ROOT / "data" / "clean"
MAPPING_KEY = ROOT / "data" / "mapping_key.csv"     # tidak di-commit
DB_PATH = ROOT / "learning.duckdb"                  # tidak di-commit
RES1 = ROOT / "results" / "1-data-preparation"
RES2 = ROOT / "results" / "2-analysis"
RES3 = ROOT / "results" / "3-presentation"
SQL_DIR = ROOT / "code" / "2-analysis" / "sql"
OUT_XLSX = ROOT / "outputs"
DOCS = ROOT / "docs"
for _d in (RAW, ANON, CLEAN, RES1, RES2, RES3, OUT_XLSX, DOCS):
    _d.mkdir(parents=True, exist_ok=True)


def result(name: str) -> Path:
    """Cari CSV hasil di folder tahap yang sesuai."""
    for folder in (RES1, RES2, RES3):
        p = folder / name
        if p.exists():
            return p
    raise FileNotFoundError(name)


SEED = 16
STANDARD_DAYS = 30            # standar perusahaan (hari)
STREAK = 3                    # target dicapai: 3 hari kerja berturut-turut
TARGET_THRESHOLD = 1.00       # ambang: ok_qty >= 100% target harian (sensitivitas di 09)
OBS_SLOTS = 60                # slot hari kalender kerja per operator (termasuk hari tidak hadir)

# Stasiun: target output harian (skala anonim) dan jumlah langkah kerja
STATIONS = {
    "ST-A": {"alias": "Assembly", "target": 120, "steps": 6},
    "ST-B": {"alias": "Bonding", "target": 100, "steps": 4},
    "ST-C": {"alias": "Finishing", "target": 80, "steps": 3},
}

# Operator baru (10 orang) dan stasiunnya; batch dan mentor untuk analisis Q8
NEW_OPERATORS = {
    "OP-01": ("ST-A", "B1", "M1"), "OP-02": ("ST-A", "B1", "M1"),
    "OP-03": ("ST-A", "B2", "M2"), "OP-04": ("ST-A", "B2", "M2"),
    "OP-05": ("ST-B", "B1", "M1"), "OP-06": ("ST-B", "B2", "M2"),
    "OP-07": ("ST-B", "B2", "M1"),
    "OP-08": ("ST-C", "B1", "M2"), "OP-09": ("ST-C", "B2", "M2"),
    "OP-10": ("ST-C", "B1", "M1"),
}
# Operator yang pindah stasiun (ST-B -> ST-C) dan yang berhenti sebelum target
MOVER = {"OP-06": ("ST-C", 25)}          # (stasiun tujuan, hari kerja ke-n pindah)
LEAVER = {"OP-09": 28}                    # berhenti setelah hari hadir ke-28
EXPERIENCED_PER_STATION = 4               # operator berpengalaman sebagai pembanding

# Ground truth kurva belajar (power law): f(d) = P - (P - F1) * d^(-b), f = output / target
TRUE = {
    "PLATEAU_MEAN": 1.10, "PLATEAU_SD": 0.04,
    "F1_MEAN": 0.25, "F1_SD": 0.05,
    "B_STATION": {"ST-A": 0.70, "ST-B": 0.85, "ST-C": 1.00},   # makin banyak langkah, makin lambat
    "B_OP_SD_LOG": 0.12,
    "NOISE_SD_LOG": 0.07,                                       # noise harian (lognormal)
    "NG_BASE": 0.02, "NG_START": 0.08, "NG_DECAY": 0.05,        # NG rate = base + start*exp(-decay*d)
    "ABSENT_P": 0.04, "ZERO_P": 0.01, "PARTIAL_P": 0.06,        # data kotor (2 sampai 11 persen)
    "PARTIAL_HOURS": (4.0, 6.0),
    "EXP_PLATEAU": 1.05, "EXP_NOISE_SD_LOG": 0.05,
}

# Faktor anonimisasi: output dan target dikalikan faktor yang sama (rasio tetap)
ANON_FACTOR = 0.8
