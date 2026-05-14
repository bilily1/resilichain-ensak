import streamlit as st
import pandas as pd
import sys
import os

# --- CONFIGURATION DU CHEMIN ---
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Administration · ResiliChain", page_icon="⚙️", layout="wide")

from utils import inject_theme, page_header, sidebar_logo, sidebar_user, COLORS
from auth import require_login, logout, is_admin
from db import load

# Initialisation UI et Sécurité
require_login()
inject_theme()

# --- SIDEBAR ---
with st.sidebar:
    sidebar_logo()
    sidebar_user()
    st.markdown("---")
    if st.sidebar.button("🚪 Se déconnecter", use_container_width=True):
        logout()

# --- HEADER ---
page_header("⚙️ Administration Système", "Gestion des accès et paramètres du moteur IA")

# --- VÉRIFICATION DES DROITS ADMIN ---
if not is_admin():
    st.markdown(f"""
    <div style='background:#FEE2E2; border:1px solid {COLORS["danger"]}; border-radius:12px;
                padding:2rem; text-align:center; margin-top:2rem'>
        <div style='font-size:3rem'>🔒</div>
        <h3 style='color:{COLORS["danger"]}; margin-top:1rem'>Accès Restreint</h3>
        <p style='color:#6B7280;'>Vous n'avez pas les privilèges nécessaires pour accéder à la gestion des utilisateurs.<br>
        Veuillez contacter l'administrateur système OCP.</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

# --- CHARGEMENT DES DONNÉES ---
try:
    df = load("utilisateurs")
except Exception as e:
    st.error(f"Erreur lors du chargement de la base utilisateurs : {e}")
    st.stop()

# --- DASHBOARD STATS ADMIN ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Utilisateurs", len(df))
with c2:
    actifs = df["actif"].sum() if "actif" in df else 0
    st.metric("Comptes Actifs", actifs, delta=f"{len(df) - actifs} inactifs", delta_color="inverse")
with c3:
    st.metric("Rôles OCP", df["role"].nunique())
with c4:
    st.metric("Sites Couverts", df["site"].nunique())

st.markdown("---")

# --- LISTE DES UTILISATEURS (STYLE CARD) ---
st.markdown("#### 👥 Gestion des accès")

ROLE_COLORS = {
    "admin": COLORS["danger"],
    "responsable_logistique": COLORS["primary"],
    "analyste_data": COLORS["secondary"],
}

for _, row in df.iterrows():
    role = str(row.get("role", "utilisateur"))
    is_active = row.get("actif", True)
    base_color = ROLE_COLORS.get(role, "#6B7280")

    status_icon = "🟢" if is_active else "🔴"
    status_label = "Actif" if is_active else "Inactif"

    st.markdown(f"""
    <div style='background:white; border:1px solid #E5E7EB; border-radius:12px;
                padding:1rem 1.5rem; margin-bottom:0.6rem;
                display:flex; align-items:center; justify-content:space-between;
                box-shadow: 0 2px 4px rgba(0,0,0,0.02)'>
        <div style='display:flex; align-items:center; gap:1.5rem'>
            <div style='width:42px; height:42px; border-radius:50%; background:{base_color}22;
                        border:2px solid {base_color}55; display:flex; align-items:center;
                        justify-content:center; font-weight:bold; color:{base_color}'>
                {str(row.get("nom", "?"))[:2].upper()}
            </div>
            <div>
                <div style='font-weight:700; color:#1F2937'>{row.get("nom", "—")}</div>
                <div style='font-size:0.8rem; color:#6B7280'>{row.get("email", "—")}</div>
            </div>
        </div>
        <div style='display:flex; align-items:center; gap:2rem'>
            <span style='background:{base_color}15; color:{base_color}; border:1px solid {base_color}33;
                         border-radius:6px; font-size:0.7rem; font-weight:700; padding:4px 12px;
                         text-transform:uppercase; letter-spacing:0.5px'>
                {role.replace('_', ' ')}
            </span>
            <div style='min-width:100px; font-size:0.85rem; color:#4B5563'>📍 {row.get("site", "—")}</div>
            <div style='min-width:80px; font-size:0.85rem; font-weight:600'>
                {status_icon} <span style='color:#374151'>{status_label}</span>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

# --- CONFIGURATION IA & KPI ---
st.markdown("<br>", unsafe_allow_html=True)
col_cfg1, col_cfg2 = st.columns(2)

with col_cfg1:
    st.markdown(f"""
    <div style='background:#F9FAFB; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem'>
        <h5 style='color:{COLORS["primary"]}; margin-bottom:1rem'>⚙️ Paramètres du Modèle IA</h5>
        <p style='font-size:0.9rem; color:#4B5563'>Pondération de l'algorithme Decision-S3 :</p>
        <div style='display:grid; grid-template-columns: 1fr 1fr; gap:10px'>
            <div style='background:white; padding:10px; border-radius:8px; border:1px solid #EEF2F6'>
                <span style='font-size:0.7rem; color:#94A3B8'>α PERFORMANCE</span><br>
                <b style='color:{COLORS["primary"]}'>40%</b>
            </div>
            <div style='background:white; padding:10px; border-radius:8px; border:1px solid #EEF2F6'>
                <span style='font-size:0.7rem; color:#94A3B8'>β ENVIRONNEMENT</span><br>
                <b style='color:{COLORS["secondary"]}'>35%</b>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

with col_cfg2:
    st.markdown(f"""
    <div style='background:#F9FAFB; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem'>
        <h5 style='color:{COLORS["primary"]}; margin-bottom:1rem'>📊 Seuils de Performance (KPIs)</h5>
        <div style='font-size:0.85rem; color:#4B5563; line-height:1.8'>
            🎯 <b>OTIF cible :</b> <span style='color:{COLORS["secondary"]}'>95%</span><br>
            🌿 <b>Réduction CO₂ :</b> <span style='color:{COLORS["secondary"]}'>-30%</span><br>
            ⚡ <b>Temps de réaction :</b> <span style='color:{COLORS["secondary"]}'>&lt; 3.0 min</span>
        </div>
    </div>""", unsafe_allow_html=True)

# --- TABLEAU BRUT POUR EXPORT ---
with st.expander("📥 Voir les données brutes et exporter"):
    st.dataframe(df, use_container_width=True)