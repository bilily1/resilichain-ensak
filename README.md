# ResiliChain - ENSAK

> **Intelligent Self-Healing Supply Chain System**
> *Predict · Simulate · Heal*

Projet réalisé dans le cadre de l'**EMI Industrial Challenge 2026 - 13ème édition**,
en partenariat avec **OCP Maintenance Solutions**.

**Auteurs :** Moulaye Abdoule Hady HAIDARA et coéquipiers
**Institution :** École Nationale des Sciences Appliquées de Kénitra (ENSAK)
**Année universitaire :** 2025/2026

---

## Description

ResiliChain est un système IA auto-réparateur qui détecte les anomalies logistiques en temps réel, simule des scénarios multi-objectifs et exécute les décisions correctives de façon autonome, en intégrant le **CO₂ comme contrainte d'optimisation primaire**,  une première dans l'industrie.

Conçu pour les opérations logistiques d'**OCP Group** sur 5 sites industriels marocains : Khouribga, Jorf Lasfar, Safi, Benguerir, Casablanca Port.

---

## Fonctionnalités clés

- **Détection d'anomalies** en temps réel par algorithme Isolation Forest
- **Simulation Monte-Carlo** multi-scénarios (S1/S2/S3) évaluant coût, délai et CO₂
- **CO₂ comme contrainte primaire** d'optimisation (GHG Protocol)
- **Auto-Healing autonome** : détection → décision → action en < 3 minutes
- **Dashboard exécutif** avec KPIs temps réel
- **Cartographie interactive** des sites OCP (Folium)
- **Conformité native** ISO 9001 / 14001 / 45001 / 42001

---

## Résultats KPI

| KPI | Baseline | Avec ResiliChain | Gain |
|-----|----------|-----------------|------|
| Taux de retards livraison | 24% | 8% | **−67%** |
| Émissions CO₂ | 100% | 65% | **−35%** |
| Coûts logistiques | 100% | 78% | **−22%** |
| Temps de réaction | 4h | 2.7 min | **×120** |
| Taux OTIF | 76% | ≥91% | **+15pt** |
| Score décision S3 moyen | N/A | 0.91 | **≥0.80 ✔** |

---

## Architecture

    resilichain_app/
    │
    ├── app.py                      # Point d'entrée Streamlit
    ├── config.py                   # Configuration globale
    ├── db.py                       # Gestion base de données
    ├── auth.py                     # Authentification
    ├── utils.py                    # Fonctions utilitaires
    ├── simulation.py               # Moteur Monte-Carlo
    ├── decision.py                 # Decision Engine (α·Perf + β·CO₂ + γ·Coût)
    ├── anomalies.py                # Détection Isolation Forest
    ├── co2.py                      # Calcul empreinte carbone (GHG Protocol)
    ├── dashboard_logic.py          # Logique dashboard exécutif
    │
    ├── pages/
    │   ├── 1_Login.py
    │   ├── 2_Dashboard.py
    │   ├── 3_Commandes.py
    │   ├── 4_Stocks.py
    │   ├── 5_Livraisons.py
    │   ├── 6_Anomalies.py
    │   ├── 7_Simulation.py
    │   ├── 8_Decision.py
    │   ├── 9_CO2_Durabilite.py
    │   ├── 10_Historique.py
    │   └── 11_Administration.py
    │
    ├── data/
    │   ├── commandes.csv           # 600 entrées
    │   ├── stocks.csv              # 56 entrées
    │   ├── livraisons.csv          # 450 entrées
    │   ├── anomalies.csv           # 200 entrées
    │   ├── simulations.csv         # 360 entrées
    │   ├── co2_monitoring.csv      # 900 entrées
    │   ├── journal_autohealing.csv # 180 entrées
    │   ├── maintenance.csv         # 240 entrées
    │   └── utilisateurs.csv        # 7 entrées
    │
    ├── assets/
    │   └── logo.png
    │
    └── requirements.txt

---

## Formule de décision

    Score(S) = α * Performance(S) + β * (1 − CO₂_normalisé(S)) + γ * Coût⁻¹(S)
    α = 0.40 (performance)  |  β = 0.35 (CO₂)  |  γ = 0.25 (coût)

Le scénario S3 (redistribution optimale) obtient systématiquement un score ≥ 0.80.

---

## Technologies

| Composant | Technologie |
|-----------|-------------|
| Interface | Streamlit |
| Détection anomalies | Isolation Forest (scikit-learn) |
| Simulation | Monte-Carlo (numpy / scipy) |
| Calcul CO₂ | GHG Protocol |
| Visualisation | Plotly |
| Cartographie | Folium |
| Données | CSV synthétique - 2 993 entrées |
| Langage | Python 3.11 |

---

## Installation

    git clone https://github.com/bilily1/resilichain-ensak.git
    cd resilichain-ensak
    pip install -r requirements.txt
    streamlit run app.py

---

## Conformité normative

| Norme | Domaine | Niveau |
|-------|---------|--------|
| ISO 9001:2015 | Qualité | Natif |
| ISO 14001:2015 | Environnement | Natif |
| ISO 45001:2018 | Sécurité & Santé au Travail | Avancé |
| ISO/IEC 42001:2023 | IA Responsable | Natif |

---

## Documentation

Le rapport complet du projet est disponible : [`RAPPORT.pdf`](./RAPPORT.pdf)

---

## Contexte

- **Compétition :** EMI Industrial Challenge 2026 - 13ème Journée Industrielle de l'EMI
- **Partenaire industriel :** OCP Maintenance Solutions
- **Thématique :** Supply Chain & AI + Green Industry & Carbon Intelligence

---

*© 2026 ResiliChain ENSAK - Moulaye Abdoule Hady HAIDARA et coéquipiers*
