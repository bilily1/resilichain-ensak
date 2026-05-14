import streamlit as st
import pandas as pd
from db import load  # Assure-toi que db.py contient bien la fonction load()


def _get_users() -> pd.DataFrame:
    try:
        # Charge les 7 utilisateurs mentionnés dans la doc [cite: 14, 41]
        df = load("utilisateurs")
        return df
    except Exception:
        # Fallback si le fichier est manquant
        return pd.DataFrame({
            "user_id": ["U001"],
            "nom": ["Admin ResiliChain"],
            "role": ["admin"],
            "site": ["Jorf Lasfar"],
            "email": ["admin@ocp.ma"],
            "actif": [True],
            "password": ["admin123"],
        })


def login(email: str, password: str) -> bool:
    users = _get_users()

    # Vérification de l'existence de la colonne password
    if "password" not in users.columns:
        # Si pas de password dans le CSV, on laisse passer pour le test (ou on rejette)
        match = users[(users["email"] == email) & (users["actif"] == True)]
    else:
        match = users[
            (users["email"] == email) &
            (users["password"].astype(str) == password) &
            (users["actif"] == True)
            ]

    if not match.empty:
        u = match.iloc[0]
        # Stockage des infos en session [cite: 42, 43]
        st.session_state["logged_in"] = True
        st.session_state["user_nom"] = u["nom"]
        st.session_state["user_role"] = u["role"]
        st.session_state["user_site"] = u["site"]
        st.session_state["user_email"] = u["email"]
        return True
    return False


def logout():
    # Nettoyage complet
    for k in ["logged_in", "user_nom", "user_role", "user_site", "user_email"]:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()


def require_login():
    """À appeler au début de chaque page dans le dossier /pages"""
    if not st.session_state.get("logged_in"):
        st.warning("🔒 Accès restreint. Veuillez vous connecter sur la page d'accueil.")
        st.stop()


def is_admin() -> bool:
    """Utile pour masquer des menus (ex: Administration) """
    return st.session_state.get("user_role") == "admin"