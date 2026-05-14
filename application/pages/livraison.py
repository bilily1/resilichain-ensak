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
st.set_page_config(page_title="Livraisons · ResiliChain", page_icon="🚛", layout="wide")

from utils import inject_theme, page_header, sidebar_logo, sidebar_user, PLOTLY_LAYOUT, PALETTE, COLORS, STATUS_COLORS
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
        df_raw = load("livraisons")
    except Exception as e:
        st.error(f"Erreur : {e}")
        st.stop()

    st.markdown("#### 🔍 Paramètres de transport")
    modes = ["Tous"] + sorted(df_raw["mode_transport"].unique().tolist())
    selected_mode = st.selectbox("Mode de transport", modes)

    statuts = ["Tous"] + sorted(df_raw["statut"].unique().tolist())
    selected_statut = st.selectbox("Statut actuel", statuts)

    carriers = ["Tous"] + sorted(df_raw["transporteur_nom"].unique().tolist())
    selected_carrier = st.selectbox("Transporteur", carriers)

    st.markdown("---")
    if st.button("🚪 Se déconnecter", use_container_width=True):
        logout()

# --- FILTRAGE ---
df = df_raw.copy()
if selected_mode != "Tous":
    df = df[df["mode_transport"] == selected_mode]
if selected_statut != "Tous":
    df = df[df["statut"] == selected_statut]
if selected_carrier != "Tous":
    df = df[df["transporteur_nom"] == selected_carrier]

# --- HEADER ---
page_header("🚛 Livraisons & Transport", f"Suivi opérationnel et impact carbone ({len(df)} trajets)")

# --- KPIS TOP ---
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Total Trajets", len(df))
with c2:
    otif_rate = df['otif'].mean() * 100
    st.metric("Taux OTIF", f"{otif_rate:.1f} %", delta=f"{otif_rate - 95:.1f}% vs cible")
with c3:
    avg_h = df['retard_heures'].mean()
    st.metric("Retard Moyen", f"{avg_h:.1f} h", delta=f"{avg_h:.1f}", delta_color="inverse")
with c4:
    st.metric("Empreinte CO₂", f"{df['co2_kg'].sum():,.0f} kg", "Total période")
with c5:
    st.metric("Coût Transport", f"${df['cout_transport_usd'].sum():,.0f}")

st.markdown("---")

# --- VISUALISATIONS ---
col1, col2 = st.columns(2)

with col1:
    # Graphique à double axe Y : CO2 vs Coût
    grp = df.groupby("mode_transport").agg(
        co2=("co2_kg", "sum"), cout=("cout_transport_usd", "sum")).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=grp["mode_transport"], y=grp["co2"],
                         name="CO₂ (kg)", marker_color=COLORS["secondary"], yaxis="y1"))
    fig.add_trace(go.Bar(x=grp["mode_transport"], y=grp["cout"],
                         name="Coût ($)", marker_color=COLORS["primary"], yaxis="y2"))

    # Correction Ligne 93 : On fusionne manuellement pour éviter le conflit "yaxis"
    fig.update_layout(
        paper_bgcolor=PLOTLY_LAYOUT["paper_bgcolor"],
        plot_bgcolor=PLOTLY_LAYOUT["plot_bgcolor"],
        font=PLOTLY_LAYOUT["font"],
        margin=PLOTLY_LAYOUT["margin"],
        title="Impact Carbone vs Coût par Mode",

        # Axe Y principal (Gauche - CO2)
        yaxis=dict(
            title=dict(text="CO₂ (kg)", font=dict(color=COLORS["secondary"])),
            gridcolor="#E6F4F9"
        ),
        # Axe Y secondaire (Droite - Coût)
        yaxis2=dict(
            title=dict(text="Coût ($)", font=dict(color=COLORS["primary"])),
            overlaying="y",
            side="right",
            showgrid=False
        ),
        barmode="group",
        height=350,
        showlegend=True,
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center")
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    grp2 = df.groupby("statut")["livraison_id"].count().reset_index(name="nb")
    fig2 = px.pie(grp2, values="nb", names="statut", hole=0.5,
                  color="statut", color_discrete_map=STATUS_COLORS,
                  title="État de la Flotte en Temps Réel")
    fig2.update_layout(**PLOTLY_LAYOUT, height=350)
    fig2.update_traces(textinfo='percent+label')
    st.plotly_chart(fig2, use_container_width=True)

# --- ANALYSE DE LA PONCTUALITÉ ---
if "date_depart" in df.columns:
    st.markdown("#### ⏱ Analyse de la Ponctualité (Retards cumulés)")
    df["mois"] = df["date_depart"].dt.strftime('%Y-%m')
    grp3 = df.groupby("mois")["retard_heures"].mean().reset_index()

    fig3 = px.line(grp3, x="mois", y="retard_heures",
                   markers=True, color_discrete_sequence=[COLORS["accent"]],
                   title="Évolution du retard moyen (Heures)")
    fig3.add_hline(y=12, line_dash="dash", line_color=COLORS["danger"], annotation_text="Seuil critique")
    fig3.update_layout(**PLOTLY_LAYOUT, height=250)
    st.plotly_chart(fig3, use_container_width=True)

# --- TABLEAU DÉTAILLÉ ---
st.markdown("#### 📋 Registre des Expéditions")


def style_otif(val):
    return 'background-color: #EAF7F0' if val == "✅ OK" else 'background-color: #FDE8E8'


cols_view = ["livraison_id", "origine", "destination", "mode_transport",
             "transporteur_nom", "produit", "statut", "masse_t",
             "retard_heures", "co2_kg", "cout_transport_usd", "otif"]

# Transformation de OTIF en texte avant le rendu pour le style
df_styled = df[cols_view].copy()
df_styled["otif"] = df_styled["otif"].map(lambda x: "✅ OK" if x == 1 else "❌ Échec")

st.dataframe(
    df_styled.style.format({
        "masse_t": "{:.1f} t",
        "co2_kg": "{:,.0f} kg",
        "cout_transport_usd": "${:,.0f}"
    }).map(style_otif, subset=["otif"]),
    use_container_width=True,
    height=400
)
