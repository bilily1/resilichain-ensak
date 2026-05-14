import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

# --- CONFIGURATION DU CHEMIN ---
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Anomalies · ResiliChain", page_icon="🚨", layout="wide")

from utils import inject_theme, page_header, sidebar_logo, sidebar_user, PLOTLY_LAYOUT, PALETTE, COLORS
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
        df_raw = load("anomalies")
    except Exception as e:
        st.error(f"Erreur : {e}")
        st.stop()

    st.markdown("#### 🔍 Paramètres de détection")
    sites = ["Tous"] + sorted(df_raw["site"].unique().tolist())
    selected_site = st.selectbox("Site industriel", sites)

    severities = ["Toutes"] + sorted(df_raw["severite"].unique().tolist())
    selected_sev = st.selectbox("Degré de sévérité", severities)

    statuts = ["Tous"] + sorted(df_raw["statut"].unique().tolist())
    selected_stat = st.selectbox("Statut de résolution", statuts)

    st.markdown("---")
    if st.button("🚪 Se déconnecter", use_container_width=True):
        logout()

# --- FILTRAGE ---
df = df_raw.copy()
if selected_site != "Tous":
    df = df[df["site"] == selected_site]
if selected_sev != "Toutes":
    df = df[df["severite"] == selected_sev]
if selected_stat != "Tous":
    df = df[df["statut"] == selected_stat]

df = df.sort_values("date_detection", ascending=False)

# --- HEADER ---
page_header("🚨 Détection des Anomalies", "Surveillance IA par Isolation Forest (Modèle OCP-S3)")

# --- KPIS TOP ---
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Total Détecté", len(df))
with c2:
    critiques = (df["severite"].str.lower() == "critique").sum()
    st.metric("🔴 Critiques", critiques, delta=f"{critiques} alertes", delta_color="inverse")
with c3:
    moderees = (df["severite"].str.lower() == "modéré").sum()
    st.metric("🟡 Modérées", moderees)
with c4:
    resolues = (df["statut"].str.lower() == "résolu").sum()
    st.metric("✅ Résolues", resolues, f"{resolues / len(df):.0%}")
with c5:
    impact = df['impact_usd'].sum() if "impact_usd" in df else 0
    st.metric("💸 Perte Évitée", f"${impact:,.0f}")

st.markdown("---")

# Alerte visuelle pour les urgences
actives_crit = df[(df["severite"].str.lower() == "critique") & (df["statut"].str.lower() == "actif")]
if not actives_crit.empty:
    st.error(f"🚨 **ALERTE :** {len(actives_crit)} anomalie(s) critique(s) nécessite(nt) une intervention immédiate.")

# --- VISUALISATIONS ---
col1, col2 = st.columns(2)

SEV_MAP = {"critique": COLORS["danger"], "modéré": COLORS["accent"], "faible": COLORS["secondary"]}

with col1:
    grp = df.groupby(["type_anomalie", "severite"])["anomalie_id"].count().reset_index(name="nb")
    fig = px.bar(grp, x="nb", y="type_anomalie", color="severite", orientation="h",
                 color_discrete_map=SEV_MAP,
                 title="Profil des Anomalies détectées")
    fig.update_layout(**PLOTLY_LAYOUT, height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    impact_col = "impact_usd" if "impact_usd" in df.columns else "anomalie_id"
    grp2 = df.groupby("categorie")[impact_col].sum().reset_index()
    fig2 = px.pie(grp2, values=impact_col, names="categorie", hole=0.5,
                  color_discrete_sequence=PALETTE,
                  title="Analyse de l'Impact Financier")
    fig2.update_layout(**PLOTLY_LAYOUT, height=350)
    st.plotly_chart(fig2, use_container_width=True)

# --- SCORE IA ---
if "score_isolation_forest" in df.columns:
    st.markdown("#### 🧠 Score de Confiance IA (Isolation Forest)")
    fig3 = px.histogram(df, x="score_isolation_forest", color="severite",
                        nbins=40, color_discrete_map=SEV_MAP,
                        title="Distribution des scores (Anomalies extrêmes < -0.6)")
    fig3.update_layout(**PLOTLY_LAYOUT, height=250)
    st.plotly_chart(fig3, use_container_width=True)

# --- TABLEAU D'AUDIT ---
st.markdown("#### 📋 Registre des Incidents")


def style_severite(val):
    if val.lower() == "critique": return 'background-color: #FDE8E8; color: #E63946; font-weight: bold'
    if val.lower() == "modéré": return 'background-color: #FFF4E5; color: #B45309'
    return 'background-color: #EAF7F0; color: #00875A'


cols_view = ["anomalie_id", "date_detection", "type_anomalie", "severite",
             "site", "statut", "impact_usd", "score_isolation_forest", "action_declenchee"]

st.dataframe(
    df[cols_view].style.format({
        "impact_usd": "${:,.0f}",
        "score_isolation_forest": "{:.4f}"
    }).map(style_severite, subset=["severite"]),
    use_container_width=True,
    height=400
)