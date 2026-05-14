import pandas as pd
from db import load
from config import KPI_TARGETS


def kpis() -> dict:
    try:
        # Chargement groupé des tables
        liv = load("livraisons")
        cmd = load("commandes")
        co2 = load("co2_monitoring")
        jah = load("journal_autohealing")
        ano = load("anomalies")
        mnt = load("maintenance")
        stk = load("stocks")
        sim = load("simulations")
    except Exception:
        return {}

    def safe(fn, default=0):
        try:
            return fn()
        except:
            return default

    # --- Calculs alignés sur le Dataset OCP ---

    # OTIF : On time In Full (Livraisons)
    otif = safe(lambda: round(liv["otif"].mean() * 100, 1))

    # Retard : Basé sur retard_heures > 0 dans livraisons (selon doc p.12)
    retard = safe(lambda: round((liv["retard_heures"] > 0).mean() * 100, 1))

    # CO2 : Moyenne de réduction (Objectif 30%)
    co2_red = safe(lambda: round(co2["reduction_pct"].mean(), 1))

    # Auto-healing : Temps de réaction IA
    t_react = safe(lambda: round(jah["temps_reaction_min"].mean(), 2))
    eco = safe(lambda: int(jah["economie_usd"].sum()))

    # Anomalies : Taux de résolution
    ano_res = safe(lambda: round((ano["statut"].str.strip() == "Résolu").mean() * 100, 1))

    # Maintenance : Santé moyenne des équipements
    sante = safe(lambda: round(mnt["score_sante_apres"].mean(), 2))

    # Stocks : % de produits en rupture critique
    rupture = safe(lambda: round((stk["statut_stock"].str.strip() == "Rupture").mean() * 100, 1))

    # Décision : Score moyen du scénario S3 sélectionné
    if "selectionne" in sim.columns:
        sel = sim[sim["selectionne"] == True]
        score_s3 = safe(lambda: round(sel["score_global"].mean(), 3))
    else:
        score_s3 = 0

    return {
        "otif_pct": (otif, KPI_TARGETS["otif_pct"], False),  # lower_is_better = False
        "retard_pct": (retard, KPI_TARGETS["retard_pct"], True),  # lower_is_better = True
        "co2_reduction_pct": (co2_red, KPI_TARGETS["co2_reduction_pct"], False),
        "temps_reaction_min": (t_react, KPI_TARGETS["temps_reaction_min"], True),
        "economie_usd": (eco, None, False),
        "anomalies_resolues_pct": (ano_res, KPI_TARGETS["anomalies_resolues_pct"], False),
        "sante_equipements": (sante, KPI_TARGETS["sante_equipements"], False),
        "rupture_stock_pct": (rupture, KPI_TARGETS["rupture_stock_pct"], True),
        "score_s3_moyen": (score_s3, KPI_TARGETS["score_s3_moyen"], False),
    }


def get_delta_metadata(val, target, lower_is_better=False):
    """
    Retourne la couleur pour st.metric (normal, inverse, off)
    """
    if target is None:
        return "off"

    if lower_is_better:
        is_good = val <= target
    else:
        is_good = val >= target

    return "normal" if is_good else "inverse"