import pandas as pd
import streamlit as st
import os
from config import CSV


@st.cache_data(ttl=300, show_spinner="Chargement des données ResiliChain...")
def load(table: str) -> pd.DataFrame:
    path = CSV.get(table)

    if path is None:
        st.error(f"Erreur de configuration : La table '{table}' n'existe pas dans config.py")
        return pd.DataFrame()

    if not os.path.exists(path):
        st.warning(f"Fichier source introuvable : {path}")
        return pd.DataFrame()

    try:
        # engine="python" est lent mais robuste pour les formats mixtes
        df = pd.read_csv(path, sep=None, engine="python")

        # 1. Nettoyage crucial des noms de colonnes (supprime les espaces)
        df.columns = df.columns.str.strip()

        # 2. Conversion automatique des dates
        for col in df.columns:
            if "date" in col.lower():
                df[col] = pd.to_datetime(df[col], errors="coerce")

        # 3. Conversion intelligente des booléens (pour les colonnes 'actif', 'conforme', etc.)
        for col in df.select_dtypes("object").columns:
            # On vérifie seulement les 10 premières lignes pour la performance
            sample = df[col].dropna().astype(str).str.lower().unique()[:10]
            if set(sample).issubset({"true", "false", "1", "0", "oui", "non", "nan"}):
                mapping = {
                    "true": True, "false": False,
                    "1": True, "0": False,
                    "oui": True, "non": False
                }
                df[col] = df[col].astype(str).str.lower().map(mapping)

        return df

    except Exception as e:
        st.error(f"Erreur lors de la lecture de {table} : {e}")
        return pd.DataFrame()


def get_last_sync(table: str):
    """Optionnel : Retourne la date de dernière modification du fichier"""
    path = CSV.get(table)
    if path and os.path.exists(path):
        import datetime
        mtime = os.path.getmtime(path)
        return datetime.datetime.fromtimestamp(mtime).strftime('%d/%m/%Y %H:%M')
    return "Inconnue"