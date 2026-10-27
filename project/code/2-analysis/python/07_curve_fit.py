"""07: Curve fitting kurva belajar (Q4, Q5).

Tiga bentuk kurva, dibandingkan dengan kriteria yang sama:
  power law    : f(d) = P - (P - F1) * d^(-b)
  eksponensial : f(d) = P - (P - F1) * exp(-k * (d - 1))
  linear per segmen: f(d) = F1 + s1 * min(d-1, c-1) + s2 * max(d-c, 0)

Pemilihan model memakai leave-one-operator-out (LOOCV): kurva gabungan dilatih pada 9 operator,
lalu memprediksi operator ke-10 yang tidak ikut dilatih. Konfigurasi tidak dipilih ulang dari
data uji. Setelah model dipilih, kurva per operator dipasang dan CI diberi bootstrap per operator.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import common as C

rng = np.random.default_rng(C.SEED)
d_all = pd.read_csv(C.RES2 / "valid_days_sql.csv")
d_all["d"] = d_all.valid_day.astype(float)
ops = sorted(d_all.operator_code.unique())


def f_power(d, P, F1, b):
    return P - (P - F1) * d ** (-b)


def f_exp(d, P, F1, k):
    return P - (P - F1) * np.exp(-k * (d - 1))


def f_pw(d, F1, s1, s2, c):
    return F1 + s1 * np.minimum(d - 1, c - 1) + s2 * np.maximum(d - c, 0)


MODELS = {
    "power_law": (f_power, [1.1, 0.25, 0.6], ([0.5, 0.0, 0.01], [2.0, 1.0, 3.0])),
    "eksponensial": (f_exp, [1.1, 0.25, 0.2], ([0.5, 0.0, 0.001], [2.0, 1.0, 3.0])),
    "linear_per_segmen": (f_pw, [0.25, 0.1, 0.0, 10.0], ([0.0, -0.5, -0.5, 2.0], [1.0, 1.0, 1.0, 40.0])),
}


def fit(fn, p0, bounds, x, y):
    p, _ = curve_fit(fn, x, y, p0=p0, bounds=bounds, maxfev=20000)
    return p


rows = []
for name, (fn, p0, bd) in MODELS.items():
    errs = []
    for held in ops:
        tr = d_all[d_all.operator_code != held]
        te = d_all[d_all.operator_code == held]
        try:
            p = fit(fn, p0, bd, tr.d.to_numpy(), tr.pct_target.to_numpy())
            pred = fn(te.d.to_numpy(), *p)
            errs.append(float(np.sqrt(np.mean((pred - te.pct_target.to_numpy()) ** 2))))
        except RuntimeError:
            errs.append(np.nan)
    rows.append(dict(model=name, n_parameter=len(p0), loocv_rmse_mean=np.nanmean(errs),
                     loocv_rmse_median=np.nanmedian(errs), operator_gagal=int(np.isnan(errs).sum())))
cmp = pd.DataFrame(rows)
cmp["loocv_rmse_mean"] = cmp.loocv_rmse_mean.round(6)
cmp["loocv_rmse_median"] = cmp.loocv_rmse_median.round(6)
best = cmp.sort_values(["loocv_rmse_mean", "model"]).iloc[0]["model"]
cmp["dipilih"] = (cmp.model == best).astype(int)
cmp.to_csv(C.RES2 / "curve_model_compare.csv", index=False)

# Kurva per operator, dengan model yang dipilih untuk power law dan eksponensial (keduanya dilaporkan)
per = []
for op in ops:
    g = d_all[d_all.operator_code == op]
    x, y = g.d.to_numpy(), g.pct_target.to_numpy()
    pp = fit(f_power, MODELS["power_law"][1], MODELS["power_law"][2], x, y)
    pe = fit(f_exp, MODELS["eksponensial"][1], MODELS["eksponensial"][2], x, y)
    rmse_p = float(np.sqrt(np.mean((f_power(x, *pp) - y) ** 2)))
    rmse_e = float(np.sqrt(np.mean((f_exp(x, *pe) - y) ** 2)))
    # hari mulai mendatar: pertama kali f(d) >= 95% dari plateau P (power law)
    dd = np.arange(1, 501, dtype=float)
    fd = f_power(dd, *pp)
    hit = np.flatnonzero(fd >= 0.95 * pp[0])
    plateau_day = float(dd[hit[0]]) if hit.size else np.nan   # NaN = belum mendatar (di luar 500 hari)
    per.append(dict(operator_code=op, P_power=pp[0], F1_power=pp[1], b_power=pp[2], rmse_power=rmse_p,
                    P_exp=pe[0], F1_exp=pe[1], k_exp=pe[2], rmse_exp=rmse_e,
                    plateau_day_power=plateau_day, n_hari=len(g)))
per = pd.DataFrame(per)
per["lebih_baik"] = np.where(per.rmse_power <= per.rmse_exp, "power_law", "eksponensial")
per.round(6).to_csv(C.RES2 / "curve_params.csv", index=False)

# Bootstrap per operator untuk CI (median lintas operator)
B = 2000
metrics = {"b_power_median": per.b_power.to_numpy(), "P_power_median": per.P_power.to_numpy(),
           "plateau_day_median": per.plateau_day_power.to_numpy().astype(float)}
ci = []
for name, vals in metrics.items():
    est = float(np.nanmedian(vals))
    boots = [np.nanmedian(rng.choice(vals, size=len(vals), replace=True)) for _ in range(B)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    ci.append(dict(metrik=name, estimasi=round(est, 6), ci_bawah=round(float(lo), 6),
                   ci_atas=round(float(hi), 6), jumlah_operator=len(vals)))
pd.DataFrame(ci).to_csv(C.RES2 / "curve_ci.csv", index=False)
print(cmp.to_string(index=False))
print(per.round(3).to_string(index=False))
print(pd.DataFrame(ci).to_string(index=False))
print("model dipilih (LOOCV):", best)
