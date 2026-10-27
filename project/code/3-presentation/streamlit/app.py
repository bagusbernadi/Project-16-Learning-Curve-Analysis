"""Dashboard kurva belajar operator baru (Streamlit + Plotly). 3 halaman: Ringkasan, Kurva per Operator,
Perbandingan Stasiun. Semua data dibaca dari results/3-presentation (dibuat oleh 12_dashboard_data.py).
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

RES = Path(__file__).resolve().parents[3] / "results" / "3-presentation"
STANDARD = 30

kpi = pd.read_csv(RES / "dashboard_kpi.csv").set_index("kpi").nilai
ops = pd.read_csv(RES / "dashboard_operator.csv")
kurva = pd.read_csv(RES / "dashboard_kurva.csv")
stn = pd.read_csv(RES / "dashboard_stasiun.csv")
hyp = pd.read_csv(RES / "dashboard_hipotesis.csv")

st.set_page_config(page_title="Learning Curve Analysis", layout="wide")
st.title("Learning Curve Analysis: operator baru")
st.caption("Data anonim simulasi. Angka contoh, bukan lini produksi nyata.")
page = st.sidebar.radio("Halaman", ["Ringkasan", "Kurva per Operator", "Perbandingan Stasiun"])

if page == "Ringkasan":
    med = float(kpi["median time-to-target (hari kerja valid)"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Median time-to-target", f"{med:g} hari kerja", f"standar {STANDARD} hari")
    c2.metric("Operator mencapai target pada hari 15",
              f"{kpi['persen operator mencapai target pada hari 15'] * 100:.0f}%")
    c3.metric("Operator tertinggal", f"{int(kpi['jumlah operator tertinggal'])} dari {int(kpi['jumlah operator'])}",
              f"di atas hari ke-{kpi['batas tertinggal (persentil 75)']:g}", delta_color="inverse")
    st.subheader("Hipotesis")
    st.dataframe(hyp[["id", "verdict", "bukti"]], hide_index=True, width="stretch")

elif page == "Kurva per Operator":
    op_sel = st.selectbox("Operator", ops.operator_code.tolist())
    info = ops.set_index("operator_code").loc[op_sel]
    st.write(f"Stasiun {info.station_code}, time-to-target {int(info.ttt_day)} hari kerja valid"
             + (" (**tertinggal**)" if info.tertinggal == 1 else ""))
    k = kurva[kurva.operator_code == op_sel]
    h = k[k.kind == "harian"]
    f = k[k.kind == "kurva"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=h.valid_day, y=h.pct_target * 100, mode="markers", name="harian"))
    fig.add_trace(go.Scatter(x=f.valid_day, y=f.fitted * 100, mode="lines", name="kurva power law"))
    fig.add_hline(y=100, line_dash="dash", annotation_text="target 100%")
    fig.update_layout(xaxis_title="hari kerja valid ke-n", yaxis_title="% target", height=420)
    st.plotly_chart(fig, width="stretch")
    st.dataframe(ops[ops.operator_code == op_sel], hide_index=True, width="stretch")

else:
    fig = go.Figure(go.Bar(x=stn.station_code, y=stn.median_ttt, name="median time-to-target"))
    fig.add_hline(y=STANDARD, line_dash="dash", annotation_text="standar 30 hari")
    fig.update_layout(yaxis_title="hari kerja valid", height=380)
    st.plotly_chart(fig, width="stretch")
    st.dataframe(stn, hide_index=True, width="stretch")
    st.caption("Stasiun dengan 3 sampai 4 operator. Perbedaan antar stasiun belum signifikan (lihat hipotesis H3).")
