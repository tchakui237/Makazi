"""
Makazi — Moteur d'Intelligence Artificielle (Régression OLS avec interactions).

=== FONDEMENT MATHÉMATIQUE ===
La régression linéaire ordinaire (OLS) estime le vecteur des coefficients :
    beta_hat = (X^T X)^{-1} X^T Y

=== MODÈLE AVEC TERMES D'INTERACTION ===
Le modèle naïf Y = β₀ + β_chambres·X_ch + β_pop·D_pop + β_res·D_res + ...
suppose que l'impact d'une chambre supplémentaire est IDENTIQUE dans les
trois catégories. C'est faux sur le marché yaoundais :

    Populaire      : +1 chambre ≈ +18 000 FCFA
    Résidentiel    : +1 chambre ≈ +55 000 FCFA
    Administratif  : +1 chambre ≈ +160 000 FCFA

Solution : termes d'INTERACTION chambres × type_quartier :
    Y = β₀
      + β_ch·X_ch                          (pente Administratif — référence)
      + β_ch_pop·(X_ch × D_pop)            (correction pente Populaire)
      + β_ch_res·(X_ch × D_res)            (correction pente Résidentiel)
      + β_pop·D_pop + β_res·D_res          (niveaux de base)
      + β_autres·X_autres + ε

Avec cette spécification chaque catégorie dispose de sa propre pente
pour le nombre de chambres, sans perdre les degrés de liberté d'un
modèle totalement séparé.

=== CORRECTIONS APPORTÉES DANS CETTE VERSION ===
1. IQR appliqué PAR CATÉGORIE (pas globalement) — évite de couper
   les grandes villas Administratif (600k–900k FCFA).
2. Suppression des colonnes de variance nulle avant OLS — évite le
   crash shape-mismatch de statsmodels (ex. cuisines=1 partout).
3. Termes d'interaction chambres × type_quartier — β_chambres réaliste
   par catégorie au lieu d'une pente unique et biaisée.

Pipeline :
    1. Chargement SQLite → DataFrame
    2. Prétraitement (bool→float, interactions, One-Hot, IQR/catégorie)
    3. Suppression colonnes variance nulle
    4. Entraînement OLS (statsmodels)
    5. Prédiction avec IC 95%
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sqlalchemy.orm import Session
from .models import Apartment


class MakaziMLEngine:
    """Moteur ML singleton pour Makazi."""

    def __init__(self):
        self.model = None
        self.r_squared: float | None = None
        self.feature_cols: list[str] = []
        self._zero_var_cols: list[str] = []   # colonnes supprimées (variance=0)

    # ──────────────────────────────────────────────────────────────────────────
    # ENTRAÎNEMENT
    # ──────────────────────────────────────────────────────────────────────────

    def train(self, db: Session) -> None:
        """
        Entraîne le modèle OLS avec termes d'interaction sur toutes les données.
        """
        apartments = db.query(Apartment).all()
        if len(apartments) < 10:
            self.model      = None
            self.r_squared  = None
            return

        # ── Étape 1 : Construction du DataFrame ──────────────────────────────
        data = pd.DataFrame([{
            "type_quartier": a.type_quartier,
            "chambres":  a.chambres,
            "douches":   a.douches,
            "salons":    a.salons,
            "cuisines":  a.cuisines,
            "bureaux":   a.bureaux,
            "forage":    a.forage,
            "eneo":      a.eneo,
            "loyer":     a.loyer,
        } for a in apartments])

        # ── Étape 2a : Conversion booléens → float ───────────────────────────
        data["forage"] = data["forage"].astype(float)
        data["eneo"]   = data["eneo"].astype(float)

        # ── Étape 2b : Filtre IQR PAR CATÉGORIE ─────────────────────────────
        #
        # JUSTIFICATION :
        # Un IQR global fusionne trois distributions très différentes
        # (Populaire ~40k, Résidentiel ~150k, Administratif ~500k).
        # La fence haute globale tombe vers 540k FCFA, coupant TOUTES les
        # grandes villas Administratif (600k–900k FCFA). Le modèle apprenait
        # un plafond artificiel bas → sous-estimation systématique.
        #
        # Avec l'IQR par catégorie, seuls les vrais outliers INTRA-groupe
        # (erreurs de saisie, annonces frauduleuses) sont supprimés.
        # Seuil 2×IQR (au lieu de 1.5×) car les prix immobiliers au Cameroun
        # ont naturellement une queue de distribution étalée (négociation,
        # standing, vue...).
        #
        cleaned = []
        for _, group in data.groupby("type_quartier"):
            Q1  = group["loyer"].quantile(0.25)
            Q3  = group["loyer"].quantile(0.75)
            IQR = Q3 - Q1
            lo  = Q1 - 2.0 * IQR
            hi  = Q3 + 2.0 * IQR
            cleaned.append(group[(group["loyer"] >= lo) & (group["loyer"] <= hi)])

        data = pd.concat(cleaned, ignore_index=True)
        if len(data) < 10:
            self.model     = None
            self.r_squared = None
            return

        # ── Étape 2c : One-Hot Encoding de type_quartier ─────────────────────
        # drop_first=True : Administratif = référence implicite (les 2 = 0)
        data = pd.get_dummies(data, columns=["type_quartier"], drop_first=True)

        # ── Étape 2d : Termes d'INTERACTION chambres × type_quartier ─────────
        #
        # JUSTIFICATION :
        # Sans interaction, l'OLS contraint β_chambres à être identique dans
        # les trois catégories — ce qui est économétriquement faux.
        # Sur le marché yaoundais, +1 chambre vaut :
        #   ~18 000 FCFA en Populaire
        #   ~55 000 FCFA en Résidentiel
        #  ~160 000 FCFA en Administratif
        #
        # Les termes d'interaction (produit) permettent au modèle d'estimer
        # une pente distincte par catégorie avec un seul modèle unifié.
        #
        # Colonne Administratif non générée par drop_first → l'intercept et
        # β_chambres capturent la pente de référence Administratif directement.
        #
        for col in [c for c in data.columns if c.startswith("type_quartier_")]:
            data[f"chambres_x_{col}"] = data["chambres"] * data[col]

        # ── Étape 3 : Séparation X / Y ───────────────────────────────────────
        Y = data["loyer"].astype(float)
        X = data.drop(columns=["loyer"]).astype(float)

        # ── Étape 4 : Suppression colonnes de variance nulle ─────────────────
        #
        # JUSTIFICATION :
        # Si une feature est constante sur tous les appartements (ex. cuisines=1
        # dans 100% des données), elle est parfaitement colinéaire avec
        # l'intercept → (X^T X) devient singulière → statsmodels supprime un
        # paramètre → shape mismatch en prédiction → crash.
        # Ce guard est robuste à tout jeu de données partiel ou filtré.
        #
        variance_mask      = X.var(ddof=0) > 0
        self._zero_var_cols = X.columns[~variance_mask].tolist()
        X = X.loc[:, variance_mask]
        self.feature_cols  = X.columns.tolist()

        # ── Étape 5 : Ajout constante + entraînement OLS ─────────────────────
        X          = sm.add_constant(X)
        self.model = sm.OLS(Y, X).fit()
        self.r_squared = float(self.model.rsquared)

    # ──────────────────────────────────────────────────────────────────────────
    # PRÉDICTION
    # ──────────────────────────────────────────────────────────────────────────

    def predict(self, features: dict) -> dict:
        """
        Prédit le loyer Ŷ et l'intervalle de confiance à 95%.

        La reconstruction du vecteur x_new suit exactement le pipeline
        d'entraînement (One-Hot + interactions + suppression variance nulle).
        """
        if self.model is None:
            raise ValueError(
                "Modèle non entraîné. Ajoutez au moins 10 entrées."
            )

        type_q = features["type_quartier"]

        # ── Construction du vecteur brut ──────────────────────────────────────
        row: dict[str, float] = {
            "chambres": float(features["chambres"]),
            "douches":  float(features["douches"]),
            "salons":   float(features["salons"]),
            "cuisines": float(features["cuisines"]),
            "bureaux":  float(features["bureaux"]),
            "forage":   1.0 if features["forage"] else 0.0,
            "eneo":     1.0 if features["eneo"]   else 0.0,
        }

        # ── One-Hot manuel (Administratif → toutes les dummies = 0) ──────────
        for col in self.feature_cols:
            if col.startswith("type_quartier_"):
                modality = col.replace("type_quartier_", "")
                row[col] = 1.0 if type_q == modality else 0.0

        # ── Termes d'interaction identiques à l'entraînement ─────────────────
        for col in self.feature_cols:
            if col.startswith("chambres_x_type_quartier_"):
                dummy_col = col.replace("chambres_x_", "")
                row[col] = row["chambres"] * row.get(dummy_col, 0.0)

        # ── Alignement sur les features actives ───────────────────────────────
        # Les colonnes de variance nulle sont absentes de feature_cols ;
        # elles ne doivent donc pas apparaître dans x_new.
        x_new = pd.DataFrame([row])[self.feature_cols].astype(float)
        x_new = sm.add_constant(x_new, has_constant="add")

        # ── Prédiction Ŷ = X_new × beta_hat ──────────────────────────────────
        prediction = self.model.get_prediction(x_new)
        y_hat      = float(prediction.predicted_mean[0])

        # IC 95% : Ŷ ± t_{α/2, n-p} × SE(Ŷ)
        conf_int = prediction.conf_int(alpha=0.05)
        lower    = float(conf_int[0, 0])
        upper    = float(conf_int[0, 1])

        return {
            "predicted_price": round(max(0.0, y_hat), 0),
            "lower_bound":     round(max(0.0, lower), 0),
            "upper_bound":     round(max(0.0, upper), 0),
        }


# Instance singleton
ml_engine = MakaziMLEngine()