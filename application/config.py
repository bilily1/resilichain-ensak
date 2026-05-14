import os




# application/ → remonte une fois → racine du projet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

CSV = {
    "commandes":           os.path.join(DATA_DIR, "commandes.csv"),
    "stocks":              os.path.join(DATA_DIR, "stocks.csv"),
    "livraisons":          os.path.join(DATA_DIR, "livraisons.csv"),
    "anomalies":           os.path.join(DATA_DIR, "anomalies.csv"),
    "simulations":         os.path.join(DATA_DIR, "simulations.csv"),
    "co2_monitoring":      os.path.join(DATA_DIR, "co2_monitoring.csv"),
    "journal_autohealing": os.path.join(DATA_DIR, "journal_autohealing.csv"),
    "maintenance":         os.path.join(DATA_DIR, "maintenance.csv"),
    "utilisateurs":        os.path.join(DATA_DIR, "utilisateurs.csv"),
}

ALPHA = 0.40
BETA  = 0.35
GAMMA = 0.25

KPI_TARGETS = {
    "otif_pct":              90,
    "retard_pct":            10,
    "co2_reduction_pct":     30,
    "temps_reaction_min":     3,
    "anomalies_resolues_pct":75,
    "sante_equipements":     0.85,
    "rupture_stock_pct":     15,
    "score_s3_moyen":        0.80,
}

COLORS = {
    "primary":   "#0A7EA4",
    "secondary": "#00C49F",
    "accent":    "#F0A500",
    "danger":    "#E63946",
    "dark":      "#0D1B2A",
    "surface":   "#132337",
    "surface2":  "#1A2E45",
    "text":      "#E8F4FD",
    "muted":     "#7B9BB5",
}