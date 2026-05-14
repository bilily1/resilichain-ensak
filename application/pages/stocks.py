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
st.set_page_config(page_title="Stocks · ResiliChain", page_icon="🏭", layout="wide")

from utils import inject_theme, page_header, sidebar_logo, sidebar_user, PLOTLY_LAYOUT, PALETTE, COLORS
from auth import require_login, logout
from db import load

# Initialisation UI
require_login()
inject_theme()

# --- SIDEBAR ---
with st.sidebar:
    sidebar_logo()
    sidebar_user()
    st.markdown("---")

    # CHARGEMENT DATA
    try:
        df_raw = load("stocks")
        if df_raw.empty:
            st.error("Table de stocks vide.")
            st.stop()
    except Exception as e:
        st.error(f"Erreur : {e}")
        st.stop()

    st.markdown("#### 🔍 Filtrage Avancé")
    sites = ["Tous les sites"] + sorted(df_raw["site"].unique().tolist())
    selected_site = st.selectbox("Site industriel", sites)

    statuts = ["Tous les statuts"] + sorted(df_raw["statut_stock"].unique().tolist())
    selected_statut = st.selectbox("État du stock", statuts)

    st.markdown("---")
    if st.button("🚪 Se déconnecter", use_container_width=True):
        logout()

# --- FILTRAGE ---
df = df_raw.copy()
if selected_site != "Tous les sites":
    df = df[df["site"] == selected_site]
if selected_statut != "Tous les statuts":
    df = df[df["statut_stock"] == selected_statut]

# --- HEADER ---
page_header("🏭 Gestion des Stocks", f"Analyse des inventaires ({len(df)} références actives)")

# --- KPIS TOP ---
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Total SKU", len(df))
with c2:
    st.metric("Valeur Stock", f"${df['valeur_usd'].sum():,.0f}")
with c3:
    st.metric("Remplissage Moyen", f"{df['taux_remplissage'].mean() * 100:.1f} %")
with c4:
    ruptures = (df["statut_stock"].str.strip() == "Rupture imminente").sum()
    st.metric("Alertes Rupture", ruptures, delta="- Critique" if ruptures > 0 else None, delta_color="inverse")
with c5:
    surstocks = (df["statut_stock"].str.strip() == "Surstock").sum()
    st.metric("Surstocks", surstocks)

st.markdown("---")

# --- VISUALISATIONS ---
col1, col2 = st.columns([1.2, 0.8])

STOCK_COLORS = {
    "Normal": COLORS["secondary"],
    "Stock bas": COLORS["accent"],
    "Rupture imminente": COLORS["danger"],
    "Surstock": "#6366F1"
}

with col1:
    df_plot = df.sort_values("taux_remplissage", ascending=False).head(20)
    fig = px.bar(df_plot,
                 x="taux_remplissage", y="produit", orientation="h",
                 color="statut_stock",
                 color_discrete_map=STOCK_COLORS,
                 title="Taux de remplissage (%) par Produit (Top 20)",
                 labels={"taux_remplissage": "Remplissage", "produit": ""})

    fig.update_layout(**PLOTLY_LAYOUT, height=450, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    grp = df.groupby("site")["valeur_usd"].sum().reset_index()
    fig2 = px.pie(grp, values="valeur_usd", names="site", hole=0.6,
                  color_discrete_sequence=PALETTE,
                  title="Distribution de la Valeur ($)")
    fig2.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
    fig2.update_layout(**PLOTLY_LAYOUT, height=450)
    st.plotly_chart(fig2, use_container_width=True)

# --- CARTE & TABLEAU ---
st.markdown("---")

# Correction pour les colonnes lat/lon
df_map = df.rename(columns={'lat': 'latitude', 'lon': 'longitude'})

if "latitude" in df_map.columns and "longitude" in df_map.columns:
    st.markdown("#### 🗺️ Cartographie des Entrepôts OCP")
    map_data = df_map.dropna(subset=["latitude", "longitude"])
    st.map(map_data, zoom=5, use_container_width=True)
else:
    st.info("💡 Coordonnées GPS indisponibles pour la carte.")

st.markdown("#### 📋 Registre détaillé des inventaires")

def color_status(val):
    color = "transparent"
    if val == "Rupture imminente":
        color = "#FDE8E8"
    elif val == "Stock bas":
        color = "#FFF4E5"
    elif val == "Normal":
        color = "#EAF7F0"
    return f'background-color: {color}'

cols = ["stock_id", "site", "produit", "categorie", "stock_actuel_t",
        "stock_min_t", "stock_max_t", "taux_remplissage", "statut_stock", "valeur_usd"]

st.dataframe(
    df[cols].style.format({
        "taux_remplissage": "{:.1%}",
        "valeur_usd": "${:,.0f}",
        "stock_actuel_t": "{:,.1f} t"
    }).map(color_status, subset=["statut_stock"]),
    use_container_width=True,
    height=400
)