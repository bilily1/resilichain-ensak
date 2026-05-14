import streamlit as st
import sys
import os

# --- CONFIGURATION DU CHEMIN ---
# On s'assure que le dossier 'application' est bien dans le path pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# --- IMPORT DES MODULES CORE ---
from auth import require_login, logout
from utils import inject_theme, sidebar_logo, sidebar_user, COLORS

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="ResiliChain · OCP Group",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- LOGIQUE DE CONNEXION ---
# require_login() redirigera vers pages/login.py si st.session_state['logged_in'] est False
require_login()

# Si on arrive ici, c'est que l'utilisateur est connecté
inject_theme()

# --- SIDEBAR COMMUNE ---
with st.sidebar:
    sidebar_logo()
    sidebar_user()
    st.markdown("---")
    if st.button("🚪 Se déconnecter", use_container_width=True):
        logout()

# --- CONTENU DE LA PAGE D'ACCUEIL ---
st.markdown(f"""
    <div style='text-align: center; padding: 2rem 0rem;'>
        <h1 style='color: {COLORS["primary"]}; font-size: 2.8rem;'>ResiliChain AI</h1>
        <p style='color: #64748B; font-size: 1.2rem; max-width: 800px; margin: 0 auto;'>
            Plateforme d'Intelligence Artificielle dédiée à la résilience et à la décarbonation 
            de la Supply Chain du groupe <b>OCP</b>.
        </p>
    </div>
""", unsafe_allow_html=True)

# --- ACCÈS RAPIDES (CARTES) ---
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style='background: white; padding: 1.5rem; border-radius: 15px; border: 1px solid #E2E8F0; height: 200px;'>
        <h3 style='color: {COLORS["primary"]};'>📊 Pilotage</h3>
        <p style='font-size: 0.9rem; color: #64748B;'>Visualisez les KPIs critiques, le taux OTIF et les performances globales en temps réel.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ouvrir le Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")

with col2:
    st.markdown(f"""
    <div style='background: white; padding: 1.5rem; border-radius: 15px; border: 1px solid #E2E8F0; height: 200px;'>
        <h3 style='color: {COLORS["secondary"]};'>🧠 Intelligence</h3>
        <p style='font-size: 0.9rem; color: #64748B;'>Consultez les décisions d'Auto-Healing prises par l'IA pour corriger les anomalies.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Décisions IA", use_container_width=True):
        st.switch_page("pages/decision.py")

with col3:
    st.markdown(f"""
    <div style='background: white; padding: 1.5rem; border-radius: 15px; border: 1px solid #E2E8F0; height: 200px;'>
        <h3 style='color: {COLORS["accent"]};'>🚛 Logistique</h3>
        <p style='font-size: 0.9rem; color: #64748B;'>Suivez l'état des livraisons, les stocks et l'empreinte carbone des trajets.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Gestion Livraisons", use_container_width=True):
        st.switch_page("pages/livraison.py")

# --- FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.caption("© 2026 ResiliChain - OCP Supply Chain AI Department | Confidentialité : Haute")