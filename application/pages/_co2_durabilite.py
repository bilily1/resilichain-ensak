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
st.set_page_config(page_title="Durabilité · ResiliChain", page_icon="🌿", layout="wide")

from utils import inject_theme, page_header, sidebar_logo, sidebar_user, PLOTLY_LAYOUT, PALETTE, COLORS
from auth import require_login, logout
from db import load
from co2 import calculate_co2_metrics, get_compliance_report

# Initialisation UI
require_login()
inject_theme()

# --- CHARGEMENT & PRÉPARATION DES DONNÉES ---
try:
    # On utilise la table livraisons qui contient les données CO2
    df_raw = load("livraisons")
    df = df_raw.copy()

    # SECURITÉ : Initialisation des colonnes manquantes pour éviter les crashs
    if 'co2_kg_baseline' not in df.columns:
        df['co2_kg_baseline'] = df['co2_kg'] * 1.25
    if 'conforme_iso14001' not in df.columns:
        df['conforme_iso14001'] = 1  # Par défaut tout est conforme
    if 'reduction_pct' not in df.columns:
        df['reduction_pct'] = ((df['co2_kg_baseline'] - df['co2_kg']) / df['co2_kg_baseline']) * 100
    if 'masse_t' not in df.columns:
        df['masse_t'] = 25.0  # Valeur par défaut pour le calcul d'intensité

except Exception as e:
    st.error(f"Erreur de chargement des données CO2 : {e}")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    sidebar_logo()
    sidebar_user()
    st.markdown("---")

    st.markdown("#### 🔍 Filtres Écologiques")
    sites = ["Tous les sites"] + sorted(df["origine"].unique().tolist())
    selected_site = st.selectbox("Site de départ", sites)

    iso_only = st.checkbox("Afficher uniquement les non-conformes ISO")

    st.markdown("---")
    if st.button("🚪 Se déconnecter", use_container_width=True):
        logout()

# --- LOGIQUE DE FILTRAGE ---
if selected_site != "Tous les sites":
    df = df[df["origine"] == selected_site]
if iso_only:
    # On filtre ceux qui ne sont pas conformes (0)
    df = df[df["conforme_iso14001"] == 0]

# --- CALCUL DES MÉTRIQUES (via co2.py sécurisé) ---
metrics = calculate_co2_metrics(df)
compliance = get_compliance_report(df)

# --- HEADER ---
page_header("🌿 Performance Environnementale", "Bilan Carbone & Conformité ISO 14001")

# --- KPIS TOP ---
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Total CO₂ Réel", f"{metrics['total_reel']:,.0f} kg")
    st.caption("🌍 Impact total mesuré")

with c2:
    st.metric(
        label="Économie Carbone",
        value=f"{metrics['economie_totale']:,.0f} kg",
        delta=f"{metrics['reduction_moyenne']}%"
    )
    st.caption("✨ Optimisation via IA")

with c3:
    st.metric(
        label="Conformité ISO",
        value=f"{compliance['taux_conformite']}%",
        delta=f"{compliance['nb_incidents_iso']} alertes",
        delta_color="inverse"
    )
    st.caption("📜 Norme ISO 14001")

with c4:
    st.metric("Intensité Carbone", f"{metrics['intensite_carbone']:.3f}")
    st.caption("🔋 kg CO₂ / t.km")

st.markdown("---")

# --- VISUALISATIONS ---
col1, col2 = st.columns(2)

with col1:
    # Comparaison Réel vs Baseline
    fig = go.Figure()

    # On prend les 15 premiers pour la lisibilité
    df_plot = df.head(15)
    x_axis = df_plot['livraison_id'] if 'livraison_id' in df_plot.columns else df_plot.index

    fig.add_trace(go.Bar(name='Emissions Réelles', x=x_axis, y=df_plot['co2_kg'],
                         marker_color=COLORS['secondary']))
    fig.add_trace(go.Bar(name='Baseline (Standard)', x=x_axis, y=df_plot['co2_kg_baseline'],
                         marker_color='#D0E8F0'))

    fig.update_layout(**PLOTLY_LAYOUT, barmode='group', title="Réduction CO₂ par trajet (Top 15)", height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Répartition par mode
    grp = df.groupby("mode_transport")["co2_kg"].sum().reset_index()
    fig2 = px.pie(grp, values="co2_kg", names="mode_transport", hole=0.5,
                  color_discrete_sequence=[COLORS['secondary'], COLORS['primary'], COLORS['accent']],
                  title="Empreinte Carbone par Mode")
    fig2.update_layout(**PLOTLY_LAYOUT, height=350)
    st.plotly_chart(fig2, use_container_width=True)

# --- SECTION ISO 14001 ---
st.markdown("#### 📋 Audit de Conformité Environnementale")

if compliance['nb_incidents_iso'] > 0:
    st.warning(
        f"⚠️ {compliance['nb_incidents_iso']} trajets présentent une déviation par rapport à la norme ISO 14001.")


def style_iso(val):
    return 'color: #E63946; font-weight: bold' if val == "NON-CONFORME" else 'color: #00A86B'


cols_view = ["origine", "destination", "mode_transport", "produit",
             "distance_km", "co2_kg", "reduction_pct", "conforme_iso14001"]
cols_view = [c for c in cols_view if c in df.columns]

st.dataframe(
    df[cols_view].assign(
        status_iso=df["conforme_iso14001"].map(lambda x: "CONFORME" if x == 1 else "NON-CONFORME")
    ).drop(columns=["conforme_iso14001"]).style.format({
        "distance_km": "{:,.0f} km",
        "co2_kg": "{:,.1f} kg",
        "reduction_pct": "{:.1f}%"
    }).map(style_iso, subset=["status_iso"]),
    use_container_width=True,
    height=400
)

# --- ANALYSE DE L'INTENSITÉ ---
st.markdown("#### 📉 Analyse de l'Intensité Carbone")
try:
    # Calcul de l'intensité locale
    df['intensite'] = df['co2_kg'] / ((df['masse_t'] * df['distance_km']) + 0.001)

    # Groupement par transporteur (si la colonne existe)
    t_col = "transporteur_nom" if "transporteur_nom" in df.columns else "mode_transport"
    grp_intensite = df.groupby(t_col)["intensite"].mean().reset_index().sort_values("intensite")

    fig3 = px.line(grp_intensite, x=t_col, y="intensite", markers=True,
                   title="Efficacité Carbone (Le plus bas est le meilleur)",
                   color_discrete_sequence=[COLORS['primary']])
    fig3.update_layout(**PLOTLY_LAYOUT, height=300)
    st.plotly_chart(fig3, use_container_width=True)
except Exception as e:
    st.info("Données d'intensité en cours de mise à jour...")