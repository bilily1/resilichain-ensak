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
st.set_page_config(page_title="Décision IA · ResiliChain", page_icon="🧠", layout="wide")

from utils import inject_theme, page_header, sidebar_logo, sidebar_user, PLOTLY_LAYOUT, COLORS, PALETTE
from auth import require_login, logout
from db import load

# Initialisation UI
require_login()
inject_theme()

# --- SIDEBAR & CHARGEMENT ---
with st.sidebar:
    sidebar_logo()
    sidebar_user()
    st.markdown("---")

    try:
        df_raw = load("journal_autohealing")
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
        st.stop()

    st.markdown("#### 🔍 Paramètres IA")
    modes = ["Tous"] + sorted(df_raw["mode"].unique().tolist())
    selected_mode = st.selectbox("Mode de résolution", modes)

    categories = ["Toutes"] + sorted(df_raw["categorie"].unique().tolist())
    selected_cat = st.selectbox("Domaine d'application", categories)

    st.markdown("---")
    if st.button("🚪 Se déconnecter", use_container_width=True):
        logout()

# --- FILTRAGE ---
df = df_raw.copy()
if selected_mode != "Tous":
    df = df[df["mode"] == selected_mode]
if selected_cat != "Toutes":
    df = df[df["categorie"] == selected_cat]
df = df.sort_values("date_heure", ascending=False)

# --- HEADER ---
page_header("🧠 Décisions IA & Auto-Healing", f"Analyse des 180 dernières interventions autonomes")

# --- KPIS PRINCIPAUX ---
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Actions Totales", len(df))
with c2:
    auto_count = (df["mode"] == "Automatique").sum()
    st.metric("🤖 Automatique", auto_count, f"{auto_count / len(df) * 100:.1f}%")
with c3:
    hil_count = (df["mode"] == "Human-in-loop").sum()
    st.metric("👤 Supervisé", hil_count, "HIL")
with c4:
    st.metric("💰 Économies", f"${df['economie_usd'].sum():,.0f}")
with c5:
    st.metric("🌿 CO₂ Évité", f"{df['co2_evite_kg'].sum():,.0f} kg")

st.markdown("---")

# --- BANDEAU TEMPS DE RÉACTION ---
if "temps_reaction_min" in df.columns:
    moy = df["temps_reaction_min"].mean()
    # Vert si sous la cible de 3 min, sinon orange/rouge
    color = COLORS["secondary"] if moy <= 3 else COLORS["danger"]
    status_text = "CONFORME" if moy <= 3 else "HORS CIBLE"

    st.markdown(f"""
    <div style='background:white; border:1px solid #E5E7EB; border-radius:12px;
                padding:1.2rem 1.5rem; margin-bottom:1.5rem; display:flex; 
                align-items:center; justify-content:space-between;
                box-shadow: 0 2px 4px rgba(0,0,0,0.02)'>
        <div>
            <span style='color:#6B7280; font-size:0.9rem; font-weight:500'>⚡ TEMPS DE RÉACTION MOYEN DU SYSTÈME</span><br>
            <span style='color:{color}; font-weight:800; font-size:1.8rem'>{moy:.2f} min</span>
        </div>
        <div style='background:{color}15; color:{color}; padding:6px 15px; 
                    border-radius:20px; font-weight:bold; font-size:0.8rem; border:1px solid {color}33'>
            {status_text} (Objectif ≤ 3.00)
        </div>
    </div>""", unsafe_allow_html=True)

# --- VISUALISATIONS ---
col1, col2 = st.columns(2)

with col1:
    # Top économies par action
    grp = df.groupby("type_action")["economie_usd"].sum().reset_index().sort_values("economie_usd")
    fig = px.bar(grp, x="economie_usd", y="type_action", orientation="h",
                 title="Impact Financier par Type d'Action",
                 color_discrete_sequence=[COLORS["primary"]])
    fig.update_layout(**PLOTLY_LAYOUT, height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Répartition Auto vs Human
    grp2 = df.groupby("mode")["action_id"].count().reset_index(name="nb")
    fig2 = px.pie(grp2, values="nb", names="mode", hole=0.6,
                  color="mode",
                  color_discrete_map={"Automatique": COLORS["secondary"], "Human-in-loop": COLORS["accent"]},
                  title="Niveau d'Autonomie IA")
    fig2.update_layout(**PLOTLY_LAYOUT, height=350)
    st.plotly_chart(fig2, use_container_width=True)

# --- COURBE D'EFFICIENCE ---
st.markdown("#### 📈 Évolution des Économies Cumulées (USD)")
df_s = df.sort_values("date_heure")
df_s["economie_cumul"] = df_s["economie_usd"].cumsum()
fig3 = px.area(df_s, x="date_heure", y="economie_cumul",
               color_discrete_sequence=[COLORS["secondary"]])
fig3.update_traces(fillcolor="rgba(0,196,159,0.1)")
fig3.update_layout(**PLOTLY_LAYOUT, height=250)
st.plotly_chart(fig3, use_container_width=True)

# --- JOURNAL DÉTAILLÉ ---
st.markdown("#### 📋 Journal des Décisions Logistiques")


def style_mode(val):
    return 'background-color: #EAF7F0; color: #00875A; font-weight: bold' if val == "Automatique" else 'background-color: #FFF4E5; color: #B45309'


cols_view = ["action_id", "date_heure", "type_action", "categorie",
             "scenario_selectionne", "economie_usd", "co2_evite_kg",
             "temps_reaction_min", "mode", "norme_iso"]

st.dataframe(
    df[cols_view].style.format({
        "date_heure": lambda t: t.strftime('%d/%m/%Y %H:%M'),
        "economie_usd": "${:,.0f}",
        "co2_evite_kg": "{:,.1f} kg",
        "temps_reaction_min": "{:.2f} m"
    }).map(style_mode, subset=["mode"]),
    use_container_width=True,
    height=400
)