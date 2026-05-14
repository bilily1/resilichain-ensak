import pandas as pd
from config import ALPHA, BETA, GAMMA


def calculate_decision_score(row):
    """
    Applique la formule de score multicritères ResiliChain :
    Score = (Alpha * Performance) + (Beta * (1 - Impact_CO2)) + (Gamma * Economie_Cout)
    """
    # Note : Dans le dataset, ces colonnes sont déjà normalisées entre 0 et 1
    perf = row.get('score_performance', 0)
    co2 = row.get('score_eco_co2', 0)
    cost = row.get('score_economie_cout', 0)

    score = (ALPHA * perf) + (BETA * co2) + (GAMMA * cost)
    return round(score, 3)


def get_best_scenario(df_simulations, evenement_id):
    """
    Pour un événement donné, compare S1, S2 et S3 et retourne le gagnant.
    """
    sub = df_simulations[df_simulations['evenement_id'] == evenement_id].copy()

    if sub.empty:
        return None

    # Recalcul du score pour sécurité (ou lecture du score_global existant)
    if 'score_global' not in sub.columns:
        sub['score_global'] = sub.apply(calculate_decision_score, axis=1)

    # Le meilleur scénario est celui avec le score le plus élevé
    best_row = sub.loc[sub['score_global'].idxmax()]

    return best_row


def get_autohealing_stats(df_journal):
    """
    Analyse l'efficacité de l'auto-guérison (Auto-healing).
    Objectif OCP : Temps de réaction < 3 minutes.
    """
    if df_journal.empty:
        return {"reaction_moyenne": 0, "economie_totale": 0, "statut_alerte": "Normal"}

    avg_time = df_journal['temps_reaction_min'].mean()
    total_savings = df_journal['economie_usd'].sum()

    # Détermination de l'état du système
    statut = "Excellent" if avg_time <= 3 else "À optimiser"

    return {
        "reaction_moyenne": round(avg_time, 2),
        "economie_totale": int(total_savings),
        "statut_alerte": statut
    }