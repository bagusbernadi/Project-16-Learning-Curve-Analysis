-- Views Project 16. Dijalankan oleh 04_run_queries.py terhadap learning.duckdb.
-- Definisi (docs/definitions.md): hari valid = hari kerja yang lolos cleaning (valid = 1).
-- Target tercapai = 3 hari valid berturut-turut dengan ok_qty >= target_per_day.
-- Time-to-target = nomor hari kerja valid (valid_day) pada hari pertama dari streak itu.

CREATE OR REPLACE VIEW v_valid_day AS
SELECT d.operator_code,
       d.valid_day,
       d.work_day,
       d.station_code,
       d.ok_qty,
       d.ng_qty,
       t.target_per_day AS target,
       d.ok_qty * 1.0 / t.target_per_day AS pct_target,
       CASE WHEN d.ok_qty >= t.target_per_day THEN 1 ELSE 0 END AS meets
FROM daily_output d
JOIN station_target t USING (station_code)
WHERE d.valid = 1;

-- Hari awal streak: hari ini dan dua hari valid berikutnya semuanya memenuhi target.
CREATE OR REPLACE VIEW v_streak AS
SELECT operator_code,
       valid_day,
       meets,
       LEAD(meets, 1) OVER w AS meets_next1,
       LEAD(meets, 2) OVER w AS meets_next2,
       CASE WHEN meets = 1
             AND LEAD(meets, 1) OVER w = 1
             AND LEAD(meets, 2) OVER w = 1 THEN 1 ELSE 0 END AS streak_start
FROM v_valid_day
WINDOW w AS (PARTITION BY operator_code ORDER BY valid_day, work_day);

-- Ringkasan per operator: time-to-target, status censored, dan hari terakhir yang diamati.
CREATE OR REPLACE VIEW v_ttt AS
WITH first_hit AS (
    SELECT operator_code, MIN(valid_day) AS ttt_day
    FROM v_streak
    WHERE streak_start = 1
    GROUP BY operator_code
),
last_obs AS (
    SELECT operator_code, MAX(valid_day) AS last_valid_day, MAX(work_day) AS last_work_day
    FROM v_valid_day
    GROUP BY operator_code
)
SELECT n.operator_code,
       n.station_code,
       n.batch_code,
       n.mentor_code,
       f.ttt_day,
       CASE WHEN f.ttt_day IS NULL THEN 0 ELSE 1 END AS reached,
       COALESCE(f.ttt_day, l.last_valid_day) AS time_or_censor_day,
       l.last_valid_day,
       l.last_work_day
FROM new_operator n
LEFT JOIN first_hit f USING (operator_code)
LEFT JOIN last_obs l USING (operator_code)
ORDER BY n.operator_code;

-- Minggu pertama = hari valid 1 sampai 5: rata-rata persen target (untuk Q7).
CREATE OR REPLACE VIEW v_week1 AS
SELECT operator_code,
       AVG(pct_target) AS week1_avg_pct,
       SUM(ok_qty) AS week1_ok_qty
FROM v_valid_day
WHERE valid_day <= 5
GROUP BY operator_code
ORDER BY operator_code;

-- NG rate per minggu masa kerja (valid_day) (untuk Q9-Q10).
CREATE OR REPLACE VIEW v_ng_week AS
SELECT operator_code,
       (CAST(valid_day AS INTEGER) - 1) // 5 + 1 AS tenure_week,
       SUM(ng_qty) * 1.0 / NULLIF(SUM(ok_qty + ng_qty), 0) AS ng_rate,
       COUNT(*) AS hari
FROM v_valid_day
GROUP BY operator_code, tenure_week
ORDER BY operator_code, tenure_week;

-- Rata-rata NG rate operator sepanjang masa kerja (untuk Q10).
CREATE OR REPLACE VIEW v_ng_operator AS
SELECT operator_code,
       SUM(ng_qty) * 1.0 / NULLIF(SUM(ok_qty + ng_qty), 0) AS ng_rate_all
FROM v_valid_day
GROUP BY operator_code
ORDER BY operator_code;
