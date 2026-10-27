"""03: Memuat data bersih ke DuckDB (learning.duckdb, tidak di-commit) dan menjalankan pengecekan aturan.

Tabel: new_operator, daily_output, station_target, experienced_baseline.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import duckdb
import pandas as pd
import common as C

if C.DB_PATH.exists():
    C.DB_PATH.unlink()
con = duckdb.connect(str(C.DB_PATH))
con.execute(f"""
CREATE TABLE new_operator AS SELECT * FROM read_csv_auto('{C.ANON / 'new_operator.csv'}');
CREATE TABLE station_target AS SELECT * FROM read_csv_auto('{C.ANON / 'station_target.csv'}');
CREATE TABLE experienced_baseline AS SELECT * FROM read_csv_auto('{C.ANON / 'experienced_baseline.csv'}');
CREATE TABLE daily_output AS SELECT * FROM read_csv_auto('{C.CLEAN / 'daily_output_clean.csv'}');
""")
# Constraint aturan (output tidak boleh negatif, kategori alasan terdaftar)
checks = {
    "ok_qty tidak negatif": "SELECT count(*) FROM daily_output WHERE ok_qty < 0",
    "ng_qty tidak negatif": "SELECT count(*) FROM daily_output WHERE ng_qty < 0",
    "setiap operator ada di new_operator": "SELECT count(*) FROM daily_output d LEFT JOIN new_operator n USING (operator_code) WHERE n.operator_code IS NULL",
    "setiap stasiun ada di station_target": "SELECT count(*) FROM daily_output d LEFT JOIN station_target s USING (station_code) WHERE s.station_code IS NULL",
    "work_day unik per operator": "SELECT count(*) FROM (SELECT operator_code, work_day FROM daily_output GROUP BY 1,2 HAVING count(*)>1)",
    "alasan terdaftar": "SELECT count(*) FROM daily_output WHERE alasan NOT IN ('valid','tidak hadir','jam tidak penuh','output 0','pindah stasiun')",
}
rows = [(name, con.execute(q).fetchone()[0]) for name, q in checks.items()]
out = pd.DataFrame(rows, columns=["pengecekan", "pelanggaran"])
out["hasil"] = out.pelanggaran.map(lambda n: "lulus" if n == 0 else "gagal")
out.to_csv(C.RES1 / "db_checks.csv", index=False)
tables = con.execute("SELECT table_name, estimated_size FROM duckdb_tables() ORDER BY 1").df()
tables.to_csv(C.RES1 / "db_tables.csv", index=False)
con.close()
print(out.to_string(index=False))
assert (out.pelanggaran == 0).all(), "pengecekan database gagal"
