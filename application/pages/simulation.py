import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os

# --- CONFIGURATION DU CHEMIN ---
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Simulations · ResiliChain", page_icon="🧪", layout="wide")

from utils import inject_theme, page_header, sidebar_logo, sidebar_user, PLOTLY_LAYOUT, COLORS, PALETTE
from auth import require_login, logout
from db import load

# Initialisation UI
require_login()
inject_theme()

# --- SIDEBAR & DATA ---
with st.sidebar:
    sidebar_logo()
    sidebar_user()
    st.markdown("---")

    try:
        df_raw = load("simulations")
    except Exception as e:
        st.error(f"Erreur : {e}")
        st.stop()

    st.markdown("#### ⚙️ Paramètres Monte-Carlo")
    st.info("Les scores S3 sont calculés via l'algorithme Decision-S3 (Pondération 40/35/25).")

    st.markdown("---")
    if st.button("🚪 Se déconnecter", use_container_width=True):
        logout()

# Filtrage des données sélectionnées (optimales)
df = df_raw.copy()
sel = df[df["selectionne"].astype(str).str.lower() == "true"] if "selectionne" in df.columns else df

# --- HEADER ---
page_header("🧪 Simulation & Analyse de Scénarios", "Comparaison multi-critères S1 (Baseline) vs S3 (IA)")

# --- KPIS TOP ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Événements Simulés", df["evenement_id"].nunique())
with c2:
    st.metric("Score S3 Moyen", f"{sel['score_global'].mean():.3f}")
with c3:
    co2_red = abs(sel['delta_co2_pct'].mean())
    st.metric("Réduction CO₂ Moy.", f"-{co2_red:.1f}%", delta="Impact Vert", delta_color="normal")
with c4:
    cost_sav = abs(sel['delta_cout_pct'].mean())
    st.metric("Économie Coût Moy.", f"-{cost_sav:.1f}%", delta="Efficience")

st.markdown("---")

# --- GRAPHIQUES DE COMPARAISON ---
st.markdown("#### ⚖️ Performance Comparative des Scénarios")
avg = df.groupby("scenario")[["delta_delai_h", "delta_cout_pct", "delta_co2_pct", "score_global"]].mean().reset_index()

col1, col2 = st.columns(2)

with col1:
    fig = go.Figure()
    metrics_plot = [
        ("delta_cout_pct", COLORS["primary"], "Δ Coût (%)"),
        ("delta_co2_pct", COLORS["secondary"], "Δ CO₂ (%)")
    ]
    for metric, color, label in metrics_plot:
        fig.add_trace(go.Bar(name=label, x=avg["scenario"], y=avg[metric], marker_color=color))

    fig.update_layout(**PLOTLY_LAYOUT, barmode="group", title="Deltas de performance (Moyenne)", height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Coloration spéciale pour S3
    bar_colors = [COLORS["primary"] if s != "S3" else COLORS["secondary"] for s in avg["scenario"]]
    fig2 = px.bar(avg, x="scenario", y="score_global",
                  title="Score Global de Résilience (Cible: 1.000)",
                  text_auto='.3f', color_discrete_sequence=[COLORS["secondary"]])
    fig2.update_traces(marker_color=bar_colors)
    fig2.update_layout(**PLOTLY_LAYOUT, height=350)
    fig2.update_yaxes(range=[0, 1.1])
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# --- FOCUS ÉVÉNEMENT ---
st.markdown("#### 🔍 Analyse détaillée par Événement")
if "evenement_id" in df.columns:
    events = sorted(df["evenement_id"].unique().tolist())
    evt = st.selectbox("Choisir un incident simulé :", events)
    sub = df[df["evenement_id"] == evt].sort_values("scenario")

    if not sub.empty:
        best_score = sub["score_global"].max()
        cols = st.columns(len(sub))

        for i, (_, row) in enumerate(sub.iterrows()):
            is_best = row["score_global"] == best_score
            border_color = COLORS["secondary"] if is_best else "#E5E7EB"
            bg_color = "white"

            with cols[i]:
                badge = f"<div style='background:{COLORS['secondary']}22; color:{COLORS['secondary']}; border-radius:12px; font-size:0.7rem; padding:4px; font-weight:700; margin-bottom:10px'>RECOMMANDÉ IA</div>" if is_best else "<div style='height:31px'></div>"

                st.markdown(f"""
                <div style='background:{bg_color}; border:2px solid {border_color}; border-radius:15px; padding:1.5rem; text-align:center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1)'>
                    {badge}
                    <h3 style='margin:0; color:{COLORS["primary"]}'>{row.get("scenario", "—")}</h3>
                    <div style='font-size:2rem; font-weight:800; color:{COLORS["primary"] if not is_best else COLORS["secondary"]}; margin:10px 0'>
                        {row.get("score_global", 0):.3f}
                    </div>
                    <p style='font-size:0.8rem; color:#6B7280; margin-bottom:15px'>Score de résilience</p>
                    <div style='text-align:left; font-size:0.85rem; border-top:1px solid #F3F4F6; padding-top:15px'>
                        ⏱️ Retard : <b style='float:right; color:{COLORS["accent"]}'>{row.get("delta_delai_h", 0):+.1f} h</b><br>
                        💰 Coût : <b style='float:right; color:{COLORS["primary"]}'>{row.get("delta_cout_pct", 0):+.1f} %</b><br>
                        🌿 CO₂ : <b style='float:right; color:{COLORS["secondary"]}'>{row.get("delta_co2_pct", 0):+.1f} %</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- TABLEAU BRUT ---
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📥 Consulter la matrice complète des simulations"):
    st.dataframe(df.sort_values(["evenement_id", "scenario"]), use_container_width=True)