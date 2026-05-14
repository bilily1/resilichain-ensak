import pandas as pd
from sklearn.ensemble import IsolationForest
from db import load


def detect_anomalies_ia(df_livraisons):
    """
    Utilise l'algorithme Isolation Forest pour détecter des anomalies
    multivariées dans les livraisons (Distance, Masse, Retard, CO2).
    """
    if df_livraisons.empty:
        return df_livraisons

    # Sélection des caractéristiques numériques pour l'IA
    features = ['distance_km', 'masse_t', 'retard_heures', 'co2_kg']
    X = df_livraisons[features].fillna(0)

    # Entraînement du modèle (Contamination à 10% pour identifier les 10% les plus suspects)
    model = IsolationForest(contamination=0.1, random_state=42)

    # Génération du score (plus il est bas/négatif, plus c'est une anomalie)
    df_livraisons['score_ia'] = model.fit_predict(X)
    df_livraisons['anomalie_detectee'] = df_livraisons['score_ia'].apply(lambda x: True if x == -1 else False)

    return df_livraisons


def get_anomaly_summary(df_anomalies):
    """
    Calcule les KPIs pour la page Anomalies.
    """
    if df_anomalies.empty:
        return {"taux_resolution": 0, "impact_total": 0, "nb_actives": 0}

    # Taux de résolution (Objectif OCP : >= 75%)
    total = len(df_anomalies)
    resolues = len(df_anomalies[df_anomalies['statut'].str.strip() == "Résolu"])
    taux_res = (resolues / total) * 100 if total > 0 else 0

    # Impact financier total des anomalies en cours
    impact_total = df_anomalies[df_anomalies['statut'] != "Résolu"]['impact_usd'].sum()

    # Nombre d'alertes critiques (Gravité 'Haute' ou 'Critique')
    nb_critiques = len(df_anomalies[df_anomalies['gravite'].isin(['Critique', 'Haute'])])

    return {
        "taux_resolution": round(taux_res, 1),
        "impact_total": int(impact_total),
        "nb_critiques": nb_critiques,
        "nb_actives": total - resolues
    }


def filter_by_severity(df_anomalies, severity_level):
    """Filtre les anomalies par niveau : Faible, Modéré, Critique."""
    return df_anomalies[df_anomalies['gravite'].str.lower() == severity_level.lower()]