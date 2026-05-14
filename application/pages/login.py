import streamlit as st
import sys
import os

# --- CONFIGURATION DU CHEMIN (Indispensable pour PyCharm) ---
# On remonte d'un niveau pour trouver les modules (auth, db, config)
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)

from auth import login

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="ResiliChain · Connexion",
    page_icon="⛓️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS PERSONNALISÉ (LOGIN DARK MODE) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@800&family=DM+Sans:wght@400;500;700&display=swap');

/* Cache la barre de navigation et le menu sur la page de login */
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }

/* Background sombre spécifique au Login */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top right, #132337, #0D1B2A) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Style de la carte centrale */
.login-card {
    background: #132337;
    border: 1px solid rgba(10,126,164,0.28);
    border-radius: 18px;
    padding: 2.5rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}

/* Style des labels et inputs */
label { color: #7B9BB5 !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.1em; }
input { 
    background-color: #1A2E45 !important; 
    color: white !important; 
    border-radius: 8px !important;
    border: 1px solid rgba(10,126,164,0.3) !important;
}

/* Bouton principal */
.stButton > button {
    background: linear-gradient(90deg, #0A7EA4, #00C49F) !important;
    color: white !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 0.75rem !important;
    transition: 0.3s ease;
}
.stButton > button:hover { transform: scale(1.02); opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

# --- CONTENU DE LA PAGE ---
st.markdown("""
<div style='text-align:center; margin-bottom: 2rem; margin-top: 2rem;'>
    <h1 style='font-family:Syne; font-size:3rem; font-weight:800; margin:0;
               background:linear-gradient(90deg,#0A7EA4,#00C49F);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
        ResiliChain
    </h1>
    <p style='color:#7B9BB5; font-size:0.8rem; letter-spacing:0.2em; text-transform:uppercase;'>
        OCP · Supply Chain AI · 2025–2026
    </p>
</div>
""", unsafe_allow_html=True)

# Utilisation d'un conteneur pour centrer la carte
_, central_col, _ = st.columns([1, 4, 1])

with central_col:
    with st.container():
        email = st.text_input("Identifiant OCP", placeholder="votre.nom@ocp.ma")
        password = st.text_input("Mot de passe", placeholder="••••••••", type="password")

        st.write("")  # Espacement

        if st.button("ACCÉDER AU SYSTÈME →", use_container_width=True):
            if login(email, password):
                st.success("Accès autorisé. Redirection...")
                st.switch_page("pages/dashboard.py")
            else:
                st.error("Identifiants incorrects. Veuillez réessayer.")

    # Footer de la carte
    st.markdown("""
    <div style='margin-top: 2rem; padding-top: 1rem; border-top: 1px solid rgba(10,126,164,0.15); text-align:center;'>
        <p style='color:#4A6A82; font-size:0.7rem;'>Accès réservé au personnel autorisé</p>
        <div style='display:flex; justify-content:center; gap:5px;'>
            <code style='color:#00C49F; font-size:0.6rem; background:rgba(0,196,159,0.1); padding:2px 6px;'>ADMIN</code>
            <code style='color:#00C49F; font-size:0.6rem; background:rgba(0,196,159,0.1); padding:2px 6px;'>LOGISTIQUE</code>
            <code style='color:#00C49F; font-size:0.6rem; background:rgba(0,196,159,0.1); padding:2px 6px;'>ANALYSTE</code>
        </div>
    </div>
    """, unsafe_allow_html=True)