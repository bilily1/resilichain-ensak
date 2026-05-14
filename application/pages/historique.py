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
st.set_page_config(page_title="Historique · ResiliChain", page_icon="📜", layout="wide")

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
        df_raw = load("maintenance")
    except Exception as e:
        st.error(f"Erreur de chargement maintenance : {e}")
        st.stop()

    st.markdown("#### 🔍 Filtres Opérationnels")
    sites = ["Tous"] + sorted(df_raw["site"].unique().tolist())
    selected_site = st.selectbox("Site minier/industriel", sites)

    interv_types = ["Tous"] + sorted(df_raw["type_intervention"].unique().tolist())
    selected_type = st.selectbox("Type d'intervention", interv_types)

    st.markdown("---")
    if st.button("🚪 Se déconnecter", use_container_width=True):
        logout()

# --- FILTRAGE ---
df = df_raw.copy()
if selected_site != "Tous":
    df = df[df["site"] == selected_site]
if selected_type != "Tous":
    df = df[df["type_intervention"] == selected_type]

# --- HEADER ---
page_header("📜 Historique Maintenance", "Suivi des interventions et intégrité des actifs OCP")

# --- KPIS TOP ---
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Interventions", len(df))
with c2:
    st.metric("Coût Total", f"${df['cout_usd'].sum():,.0f}")
with c3:
    gain_sante = df['score_sante_apres'].mean() - df['score_sante_avant'].mean()
    st.metric("Gain Santé Moy.", f"+{gain_sante:.2f}", "Impact Tech")
with c4:
    st.metric("Indisponibilité", f"{df['arret_production_h'].sum():,.0f} h", delta="Heures d'arrêt",
              delta_color="inverse")
with c5:
    sst_rate = df['iso_45001_ok'].mean() * 100 if "iso_45001_ok" in df else 0
    st.metric("Conformité SST", f"{sst_rate:.0f}%", "ISO 45001")

st.markdown("---")

# --- VISUALISATIONS ---
col1, col2 = st.columns(2)

with col1:
    # Analyse financière par type d'intervention
    grp = df.groupby("type_intervention")["cout_usd"].sum().reset_index()
    fig = px.bar(grp, x="type_intervention", y="cout_usd",
                 title="Budget Maintenance par Type",
                 color_discrete_sequence=[COLORS["primary"]])
    fig.update_layout(**PLOTLY_LAYOUT, height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Comparatif Santé Avant/Après
    avg = df.groupby("type_equipement").agg(
        avant=("score_sante_avant", "mean"),
        apres=("score_sante_apres", "mean")
    ).reset_index()

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name='Avant', x=avg["type_equipement"], y=avg["avant"], marker_color="#94A3B8"))
    fig2.add_trace(go.Bar(name='Après', x=avg["type_equipement"], y=avg["apres"], marker_color=COLORS["secondary"]))

    fig2.update_layout(**PLOTLY_LAYOUT, barmode='group', title="Efficacité Technique (Score Santé 0-10)", height=350)
    st.plotly_chart(fig2, use_container_width=True)

# --- TABLEAU DÉTAILLÉ ---
st.markdown("#### 📋 Registre des Interventions")


def style_sst(val):
    return 'color: #00875A; font-weight: bold' if val == 1 else 'color: #E63946; font-weight: bold'


cols_view = ["maintenance_id", "equipement_nom", "site", "type_intervention",
             "date_intervention", "cout_usd", "score_sante_avant",
             "score_sante_apres", "arret_production_h", "iso_45001_ok"]

st.dataframe(
    df[cols_view].style.format({
        "cout_usd": "${:,.0f}",
        "score_sante_avant": "{:.2f}",
        "score_sante_apres": "{:.2f}",
        "arret_production_h": "{:.1f} h",
        "iso_45001_ok": lambda x: "✅ CONFORME" if x == 1 else "❌ INCIDENT"
    }).map(style_sst, subset=["iso_45001_ok"]),
    use_container_width=True,
    height=450
)