import streamlit as st

# --- 1. CONFIGURATION DES COULEURS & PALETTES ---

# Couleurs spécifiques pour les statuts logistiques (Page Livraison)
STATUS_COLORS = {
    "En route": "#007A9E",   # Bleu
    "Livré":    "#00A86B",   # Vert
    "Retard":   "#E63946",   # Rouge
    "Chargement": "#F0A500"  # Orange
}
COLORS = {
    "primary": "#007A9E",  # Bleu OCP
    "secondary": "#00A86B",  # Vert Durabilité
    "accent": "#F0A500",  # Orange Alerte/Énergie
    "danger": "#E63946",  # Rouge Critique
    "background": "#F0F4F8",
    "surface": "#FFFFFF",
    "text": "#1B3A4B",
    "muted": "#5B8FA8"
}

# La variable PALETTE qui manquait et causait l'ImportError
PALETTE = [COLORS["primary"], COLORS["secondary"], COLORS["accent"], "#6366F1", "#EC4899"]

# --- 2. STYLE CSS (THEME CLAIR PREMIUM) ---
THEME_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {{
    background-color: {COLORS['background']} !important;
    color: {COLORS['text']} !important;
    font-family: 'DM Sans', sans-serif !important;
}}

[data-testid="stSidebar"] {{
    background-color: {COLORS['surface']} !important;
    border-right: 2px solid #D0E8F0 !important;
}}

/* Cartes de métriques */
[data-testid="metric-container"] {{
    background-color: {COLORS['surface']} !important;
    border: 1px solid #D0E8F0 !important;
    border-top: 4px solid {COLORS['primary']} !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    box-shadow: 0 4px 12px rgba(0,122,158,0.05) !important;
}}

/* Titres */
h1, h2, h3, h4 {{ 
    font-family: 'Syne', sans-serif !important; 
    color: {COLORS['text']} !important; 
    font-weight: 800 !important;
}}

/* Boutons */
.stButton > button {{
    background: {COLORS['primary']} !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.3s ease !important;
    width: 100%;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(0,122,158,0.2) !important;
    border: none !important;
    color: white !important;
}}
</style>
"""


# --- 3. FONCTIONS D'INTERFACE ---

def inject_theme():
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div style='padding: 1rem 0; border-bottom: 2px solid #D0E8F0; margin-bottom: 2rem'>
        <h1 style='margin:0; background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['secondary']});
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size: 2.2rem;'>{title}</h1>
        <p style='color: {COLORS['muted']}; margin: 0.5rem 0 0; font-size: 1rem;'>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def sidebar_logo():
    st.sidebar.markdown(f"""
    <div style='text-align: center; padding: 1.5rem 0; border-bottom: 2px solid #D0E8F0; margin-bottom: 1rem'>
        <div style='font-family: Syne; font-size: 1.6rem; font-weight: 800; 
                    color: {COLORS['primary']}'>ResiliChain</div>
        <div style='font-size: 0.65rem; letter-spacing: 0.15em; color: {COLORS['muted']}'>OCP • SUPPLY CHAIN AI</div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_user():
    # Gestion sécurisée des données utilisateur pour éviter les erreurs de clé
    user = st.session_state.get("user", {})
    nom = user.get("nom", "Utilisateur")
    role = user.get("role", "Analyste").replace('_', ' ').title()
    site = user.get("site", "Siège OCP")

    st.sidebar.markdown(f"""
    <div style='background: #E6F4F9; padding: 1rem; border-radius: 12px; border: 1px solid #B8D8E8'>
        <div style='font-weight: 700; color: {COLORS['text']}; font-size: 0.9rem;'>👤 {nom}</div>
        <div style='color: {COLORS['muted']}; font-size: 0.75rem; margin-bottom: 4px;'>{role}</div>
        <div style='color: {COLORS['primary']}; font-size: 0.7rem; font-weight: 600;'>📍 {site}</div>
    </div>
    """, unsafe_allow_html=True)


# --- 4. CONFIGURATION PLOTLY ---
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLORS['text'], family="DM Sans"),
    margin=dict(l=10, r=10, t=40, b=10),
    hovermode="closest",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="#E6F4F9")
)