"""04: Menjalankan views SQL (code/2-analysis/sql/views.sql) dan mengekspor hasilnya ke CSV.

Hasil ini adalah sumber angka analisis hilir (05-11). Setiap ekspor dibulatkan agar rerun
menghasilkan byte yang sama.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import duckdb
import common as C

con = duckdb.connect(str(C.DB_PATH))
con.execute((C.SQL_DIR / "views.sql").read_text(encoding="utf-8"))

exports = {
    "ttt_per_operator.csv": """
        SELECT t.operator_code, t.station_code, t.batch_code, t.mentor_code, t.reached, t.ttt_day,
               t.time_or_censor_day, t.last_valid_day, t.last_work_day,
               ROUND(w.week1_avg_pct, 6) AS week1_avg_pct, w.week1_ok_qty,
               ROUND(g.ng_rate_all, 6) AS ng_rate_all
        FROM v_ttt t
        LEFT JOIN v_week1 w USING (operator_code)
        LEFT JOIN v_ng_operator g USING (operator_code)
        ORDER BY t.operator_code""",
    "valid_days_sql.csv": """
        SELECT operator_code, valid_day, work_day, station_code, ok_qty, ng_qty, target,
               ROUND(pct_target, 6) AS pct_target, meets
        FROM v_valid_day ORDER BY operator_code, valid_day, work_day""",
    "ng_week.csv": """
        SELECT operator_code, tenure_week, ROUND(ng_rate, 6) AS ng_rate, hari
        FROM v_ng_week ORDER BY operator_code, tenure_week""",
    "streak_starts.csv": """
        SELECT operator_code, valid_day FROM v_streak WHERE streak_start = 1
        ORDER BY operator_code, valid_day""",
}
for name, q in exports.items():
    df = con.execute(q).df()
    df.to_csv(C.RES2 / name, index=False)
    print(f"{name}: {len(df)} baris")
con.close()
