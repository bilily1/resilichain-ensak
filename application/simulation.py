import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os

# --- CONFIGURATION DU CHEMIN D'IMPORT ---
# Permet d'accéder aux modules racines (db, auth, config, utils) depuis le dossier /pages
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)

# --- IMPORTS RESILICHAIN ---
from utils import inject_theme, page_header, sidebar_logo, sidebar_user, PLOTLY_LAYOUT
from auth import require_login, logout
from db import load
from config import ALPHA, BETA, GAMMA, COLORS

# --- INITIALISATION PAGE ---
st.set_page_config(
    page_title="Simulation Monte-Carlo · ResiliChain",
    page_icon="🧪",
    layout="wide"
)

# Sécurisation de l'accès
require_login()
inject_theme()

# --- SIDEBAR ---
with st.sidebar:
    sidebar_logo()
    st.markdown(f"<h3 style='text-align:center; color:{COLORS['text']}'>Navigation</h3>", unsafe_allow_html=True)
    sidebar_user()
    st.markdown("---")
    if st.button("🚪 Se déconnecter", use_container_width=True, type="secondary"):
        logout()

# --- HEADER ---
page_header(
    "🧪 Simulation Monte-Carlo",
    "Analyse comparative S1/S2/S3 · Optimisation de la résilience face aux perturbations logistiques OCP"
)


# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def get_sim_data():
    df = load("simulations")
    if df.empty:
        return pd.DataFrame()
    # Nettoyage et typage
    if "selectionne" in df.columns:
        df["selectionne"] = df["selectionne"].astype(str).str.lower().str.strip() == "true"
    return df


df = get_sim_data()

if df.empty:
    st.error("❌ Impossible de charger les données de simulation. Vérifiez le fichier 'simulations.csv'.")
    st.stop()

# --- SECTION 1 : MÉTRIQUES GLOBALES ---
sel = df[df["selectionne"] == True] if "selectionne" in df.columns else df

m1, m2, m3, m4 = st.columns(4)

with m1:
    count = df["evenement_id"].nunique() if "evenement_id" in df.columns else len(df)
    st.metric("Événements simulés", f"{count}", help="Nombre total de perturbations analysées")

with m2:
    score = sel["score_global"].mean() if "score_global" in sel.columns else 0
    st.metric("Score S3 moyen", f"{score:.3f}", delta=f"{(score - 0.8):.3f}", help="Objectif OCP : > 0.800")

with m3:
    co2 = sel["delta_co2_pct"].mean() if "delta_co2_pct" in sel.columns else 0
    st.metric("Réduction CO₂ moy.", f"{co2:.1f} %", help="Impact environnemental du scénario optimal")

with m4:
    cost = sel["delta_cout_pct"].mean() if "delta_cout_pct" in sel.columns else 0
    st.metric("Économie coût moy.", f"{abs(cost):.1f} %", help="Optimisation financière moyenne")

st.markdown("---")

# --- SECTION 2 : ANALYSE GRAPHIQUE ---
col_left, col_right = st.columns([1, 1.5])

with col_left:
    st.markdown("#### ⚖️ Performance par Scénario")
    st.info("S1: Statu Quo | S2: Réactivité Rapide | S3: Optimisation ResiliChain (IA)")

    req_cols = ["scenario", "delta_delai_h", "delta_cout_pct", "delta_co2_pct"]
    if all(c in df.columns for c in req_cols):
        avg = df.groupby("scenario")[req_cols[1:]].mean().reset_index()

        fig = go.Figure()
        metrics = {
            "delta_cout_pct": ("Δ Coût (%)", COLORS["primary"]),
            "delta_co2_pct": ("Δ CO₂ (%)", COLORS["secondary"]),
            "delta_delai_h": ("Δ Délai (h)", COLORS["accent"])
        }

        for m_key, (m_label, m_color) in metrics.items():
            fig.add_trace(go.Bar(name=m_label, x=avg["scenario"], y=avg[m_key], marker_color=m_color))

        fig.update_layout(**PLOTLY_LAYOUT, barmode="group", height=350, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("#### 🎯 Distribution des Scores Globaux")
    if "score_global" in df.columns:
        fig_dist = px.box(df, x="scenario", y="score_global", color="scenario",
                          color_discrete_map={"S1": COLORS["danger"], "S2": COLORS["accent"],
                                              "S3": COLORS["secondary"]})
        fig_dist.update_layout(**PLOTLY_LAYOUT, height=350, showlegend=False)
        st.plotly_chart(fig_dist, use_container_width=True)

st.markdown("---")

# --- SECTION 3 : FOCUS ÉVÉNEMENT (DRILL-DOWN) ---
st.markdown("#### 🔍 Comparaison détaillée par Événement")

if "evenement_id" in df.columns:
    events = sorted(df["evenement_id"].unique().tolist())
    evt_selected = st.selectbox("Sélectionner un ID d'événement pour analyse comparative :", events)

    sub = df[df["evenement_id"] == evt_selected].sort_values("scenario")

    if not sub.empty:
        max_score = sub["score_global"].max()
        cards = st.columns(len(sub))

        for i, (_, row) in enumerate(sub.iterrows()):
            is_best = row["score_global"] == max_score
            border_color = COLORS["secondary"] if is_best else "rgba(123, 155, 181, 0.2)"

            card_html = f"""
            <div style="background:{COLORS['surface']}; border:2px solid {border_color}; border-radius:15px; padding:20px; position:relative;">
                {f'<span style="position:absolute; top:-12px; left:20px; background:{COLORS["secondary"]}; color:white; padding:2px 12px; border-radius:10px; font-size:0.7rem; font-weight:bold;">OPTIMAL</span>' if is_best else ''}
                <div style="text-align:center; margin-bottom:15px;">
                    <h2 style="margin:0; color:{COLORS['text']}; font-family:Syne;">{row['scenario']}</h2>
                    <small style="color:{COLORS['muted']}">Score d'efficacité</small>
                    <div style="font-size:2rem; font-weight:900; color:{COLORS['secondary'] if is_best else COLORS['text']}">{row['score_global']:.3f}</div>
                </div>
                <div style="border-top:1px solid rgba(255,255,255,0.05); padding-top:10px; font-size:0.85rem;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                        <span style="color:{COLORS['muted']}">🕒 Délai</span>
                        <b style="color:{COLORS['accent']}">{row['delta_delai_h']:+.1f} h</b>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                        <span style="color:{COLORS['muted']}">💰 Coût</span>
                        <b style="color:{COLORS['primary']}">{row['delta_cout_pct']:+.1f} %</b>
                    </div>
                    <div style="display:flex; justify-content:space-between;">
                        <span style="color:{COLORS['muted']}">🌱 CO₂</span>
                        <b style="color:{COLORS['secondary']}">{row['delta_co2_pct']:+.1f} %</b>
                    </div>
                </div>
            </div>
            """
            cards[i].markdown(card_html, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📊 Voir le registre brut des simulations"):
    st.dataframe(df, use_container_width=True, height=250)