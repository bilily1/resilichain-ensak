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

# --- IMPORTS ---
from utils import inject_theme, page_header, sidebar_logo, sidebar_user, PLOTLY_LAYOUT, PALETTE, COLORS
from auth import require_login, logout
from db import load
from dashboard_logic import kpis, get_delta_metadata

# --- INITIALISATION ---
st.set_page_config(page_title="Dashboard · ResiliChain", page_icon="📊", layout="wide")
require_login()
inject_theme()

# --- SIDEBAR ---
with st.sidebar:
    sidebar_logo()
    sidebar_user()
    st.markdown("---")
    if st.button("🚪 Se déconnecter", use_container_width=True):
        logout()

# --- HEADER ---
page_header("📊 Dashboard Exécutif", "Intelligence Opérationnelle · OCP Supply Chain AI")

# --- RÉCUPÉRATION DES KPIS ---
data = kpis()

if not data:
    st.error("Impossible de charger les indicateurs de performance.")
    st.stop()

# --- LIGNE 1 : KPIS LOGISTIQUES & ENVIRONNEMENT ---
c1, c2, c3, c4 = st.columns(4)

with c1:
    val, tgt, lower_better = data["otif_pct"]
    st.metric("🎯 Taux OTIF", f"{val} %", f"Cible {tgt}%",
              delta_color=get_delta_metadata(val, tgt, lower_better))

with c2:
    val, tgt, lower_better = data["retard_pct"]
    st.metric("⏱ Taux retard", f"{val} %", f"Cible {tgt}%",
              delta_color=get_delta_metadata(val, tgt, lower_better))

with c3:
    val, tgt, lower_better = data["co2_reduction_pct"]
    st.metric("🌿 Réduction CO₂", f"{val} %", f"Cible {tgt}%",
              delta_color=get_delta_metadata(val, tgt, lower_better))

with c4:
    val, tgt, lower_better = data["temps_reaction_min"]
    st.metric("⚡ Réaction IA", f"{val} min", f"Cible {tgt} min",
              delta_color=get_delta_metadata(val, tgt, lower_better))

st.markdown("<br>", unsafe_allow_html=True)

# --- LIGNE 2 : KPIS FINANCIERS & IA ---
c5, c6, c7, c8 = st.columns(4)

with c5:
    val, _, _ = data["economie_usd"]
    st.metric("💰 Économies IA", f"${val:,.0f}", "Cumul période")

with c6:
    val, tgt, lower_better = data["anomalies_resolues_pct"]
    st.metric("🛡 Résolution", f"{val} %", f"Cible {tgt}%",
              delta_color=get_delta_metadata(val, tgt, lower_better))

with c7:
    val, tgt, lower_better = data["sante_equipements"]
    st.metric("🔧 Santé Équip.", f"{val}", f"Cible {tgt}",
              delta_color=get_delta_metadata(val, tgt, lower_better))

with c8:
    val, tgt, lower_better = data["score_s3_moyen"]
    st.metric("🧠 Efficacité S3", f"{val}", f"Cible {tgt}",
              delta_color=get_delta_metadata(val, tgt, lower_better))

st.markdown("---")

# --- SECTION GRAPHIQUES ---
col_l, col_r = st.columns([3, 2])

with col_l:
    st.markdown("#### 📦 Flux des Commandes OCP")
    try:
        cmd = load("commandes")
        cmd["mois"] = cmd["date_commande"].dt.strftime('%Y-%m')
        grp = cmd.groupby("mois").agg(
            montant=("montant_total_usd", "sum"),
            nb=("commande_id", "count")
        ).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Bar(x=grp["mois"], y=grp["montant"],
                             marker_color=COLORS["primary"], name="Chiffre d'Affaires ($)"))
        fig.add_trace(go.Scatter(x=grp["mois"], y=grp["nb"],
                                 mode="lines+markers", name="Volume Commandes",
                                 yaxis="y2", line=dict(color=COLORS["secondary"], width=3)))

        # Utilisation de la configuration sécurisée (pas de **PLOTLY_LAYOUT direct avec yaxis)
        fig.update_layout(
            paper_bgcolor=PLOTLY_LAYOUT["paper_bgcolor"],
            plot_bgcolor=PLOTLY_LAYOUT["plot_bgcolor"],
            font=PLOTLY_LAYOUT["font"],
            margin=PLOTLY_LAYOUT["margin"],
            height=300,
            yaxis2=dict(overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", y=1.1, x=0),
            barmode="group"
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info("Données flux indisponibles")

with col_r:
    st.markdown("#### 🚛 Émissions CO₂ par Mode")
    try:
        liv = load("livraisons")
        grp2 = liv.groupby("mode_transport")["co2_kg"].sum().reset_index()
        fig2 = px.pie(grp2, values="co2_kg", names="mode_transport",
                      color_discrete_sequence=PALETTE, hole=0.6)
        fig2.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=True)
        st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.info("Données transport indisponibles")

st.markdown("---")

# --- SECTION BASSE : CARTE & ALERTES ---
col_m, col_a = st.columns([2, 1])

with col_m:
    st.markdown("#### 🗺️ Cartographie des Stocks (Sites OCP)")
    try:
        stk = load("stocks")
        # --- SOLUTION POUR LAT/LON ---
        # On renomme lat/lon en latitude/longitude pour Streamlit
        stk_map = stk.rename(columns={'lat': 'latitude', 'lon': 'longitude'})

        if "latitude" in stk_map.columns and "longitude" in stk_map.columns:
            map_data = stk_map.dropna(subset=['latitude', 'longitude'])
            st.map(map_data, zoom=5)
        else:
            st.warning("Coordonnées GPS (lat/lon) introuvables dans stocks.csv")
    except Exception as e:
        st.info(f"Carte indisponible")

with col_a:
    st.markdown("#### 🚨 Alertes IA Actives")
    try:
        ano = load("anomalies")
        actives = ano[ano["statut"].str.strip() != "Résolu"].head(5)
        severity_map = {"Critique": COLORS["danger"], "Haute": COLORS["accent"], "Moyenne": "#5B8FA8"}

        for _, r in actives.iterrows():
            sev = r.get("gravite", "Moyenne")
            site_name = r.get("site", r.get("origine", "Site OCP"))  # Sécurité si 'site' manque
            color = severity_map.get(sev, COLORS["muted"])
            st.markdown(f"""
            <div style='background:white; border-left:4px solid {color}; 
                        padding:10px; border-radius:8px; margin-bottom:8px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>
                <div style='font-weight:bold; font-size:0.85rem; color:{COLORS["text"]}'>{r['type_anomalie']}</div>
                <div style='font-size:0.75rem; color:{COLORS["muted"]}'>{site_name} • 
                    <span style='color:{color}; font-weight:bold;'>{sev}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except Exception:
        st.write("Aucune alerte en cours.")