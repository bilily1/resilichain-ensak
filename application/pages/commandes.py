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
st.set_page_config(page_title="Commandes · ResiliChain", page_icon="📦", layout="wide")

from utils import inject_theme, page_header, sidebar_logo, sidebar_user, PLOTLY_LAYOUT, PALETTE, COLORS, STATUS_COLORS
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
        df_raw = load("commandes")
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
        st.stop()

    st.markdown("#### 🔍 Filtres de recherche")

    # Filtres multi-critères
    sites = ["Tous"] + sorted(df_raw["site_origine"].unique().tolist())
    selected_site = st.selectbox("Site d'expédition", sites)

    statuts = ["Tous"] + sorted(df_raw["statut"].unique().tolist())
    selected_statut = st.selectbox("État commande", statuts)

    produits = ["Tous"] + sorted(df_raw["produit"].unique().tolist())
    selected_produit = st.selectbox("Produit OCP", produits)

    st.markdown("---")
    if st.button("🚪 Se déconnecter", use_container_width=True):
        logout()

# --- LOGIQUE DE FILTRAGE ---
df = df_raw.copy()
if selected_site != "Tous":
    df = df[df["site_origine"] == selected_site]
if selected_statut != "Tous":
    df = df[df["statut"] == selected_statut]
if selected_produit != "Tous":
    df = df[df["produit"] == selected_produit]

# --- HEADER ---
page_header("📦 Gestion des Commandes", f"Suivi des flux clients ({len(df)} commandes affichées)")

# --- KPIS PRINCIPAUX ---
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Total Commandes", len(df))
with c2:
    st.metric("Chiffre d'Affaires", f"${df['montant_total_usd'].sum():,.0f}")
with c3:
    avg_delay = df['retard_jours'].mean()
    st.metric("Retard Moyen", f"{avg_delay:.1f} j", delta=f"{avg_delay:.1f}", delta_color="inverse")
with c4:
    late_pct = (df['retard_jours'] > 0).mean() * 100
    st.metric("% Retard", f"{late_pct:.1f} %", delta_color="inverse")
with c5:
    clients = df["client_nom"].nunique() if "client_nom" in df else 0
    st.metric("Portefeuille Clients", clients)

st.markdown("---")

# --- VISUALISATIONS ---
col1, col2 = st.columns(2)

with col1:
    # Répartition par statut avec les couleurs définies dans utils.py
    grp = df.groupby("statut")["commande_id"].count().reset_index(name="nb")
    fig = px.bar(grp, x="statut", y="nb", color="statut",
                 color_discrete_map=STATUS_COLORS,
                 title="Répartition par Statut Logistique")
    fig.update_layout(**PLOTLY_LAYOUT, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Part des revenus par produit
    grp2 = df.groupby("produit")["montant_total_usd"].sum().reset_index()
    fig2 = px.pie(grp2, values="montant_total_usd", names="produit",
                  color_discrete_sequence=PALETTE, hole=0.5,
                  title="Analyse des Revenus par Produit")
    fig2.update_traces(textinfo='percent+label')
    fig2.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig2, use_container_width=True)

# --- ANALYSE TEMPORELLE ---
if "date_commande" in df.columns:
    st.markdown("#### 📈 Évolution du Chiffre d'Affaires Mensuel")
    df["mois"] = df["date_commande"].dt.strftime('%Y-%m')
    grp3 = df.groupby("mois")["montant_total_usd"].sum().reset_index()

    fig3 = px.area(grp3, x="mois", y="montant_total_usd",
                   title="CA Mensuel (USD)",
                   labels={"montant_total_usd": "Montant ($)", "mois": "Période"})
    fig3.update_traces(line_color=COLORS["primary"], fillcolor="rgba(0,122,158,0.1)")
    fig3.update_layout(**PLOTLY_LAYOUT, height=250)
    st.plotly_chart(fig3, use_container_width=True)

# --- TABLEAU DE DÉTAILS ---
st.markdown("#### 📋 Registre des Commandes")

# Colonnes métier essentielles
cols_view = ["commande_id", "date_commande", "produit", "client_nom",
             "pays_client", "quantite_t", "montant_total_usd", "statut",
             "retard_jours", "priorite_client"]


# Fonction de style pour la priorité
def color_priority(val):
    if val == "Haute": return 'color: #E63946; font-weight: bold'
    if val == "Moyenne": return 'color: #F0A500'
    return 'color: #00A86B'


st.dataframe(
    df[cols_view].style.format({
        "date_commande": lambda t: t.strftime('%d/%m/%Y'),
        "montant_total_usd": "${:,.0f}",
        "quantite_t": "{:,.1f} t"
    }).map(color_priority, subset=["priorite_client"]),
    use_container_width=True,
    height=400
)