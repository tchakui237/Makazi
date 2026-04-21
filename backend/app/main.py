"""
Makazi — Point d'entrée de l'API FastAPI.

Corrections appliquées :
- ml_engine.train() appelé au démarrage → R² calculé dès le lancement
- ml_engine.train() rappelé après chaque POST /collect/ → R² toujours à jour
- ml_engine.predict() utilisé dans /predict/ → prédictions OLS réelles
- get_stats() retourne ml_engine.r_squared au lieu de None
"""

import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import engine, get_db, SessionLocal
from .seed import seed_database
from .ml import ml_engine

# ── Création des tables ───────────────────────────────────────
models.Base.metadata.create_all(bind=engine)

# ── Seed + entraînement initial ───────────────────────────────
db = SessionLocal()
try:
    if db.query(models.Apartment).count() == 0:
        print("Base de données vide. Lancement du seed...")
        seed_database(db)
        print("Seed terminé avec succès !")

    # Entraînement du modèle OLS au démarrage
    print("Entraînement du modèle OLS...")
    ml_engine.train(db)
    if ml_engine.r_squared is not None:
        print(f"Modèle entraîné — R² = {ml_engine.r_squared:.4f}")
    else:
        print("Données insuffisantes pour entraîner le modèle (< 10 entrées).")
except Exception as e:
    print(f"Erreur au démarrage: {e}")
finally:
    db.close()

# ── Application FastAPI ───────────────────────────────────────
app = FastAPI(
    title="Makazi API",
    description="API de prédiction des prix de loyer à Yaoundé",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "online", "project": "Makazi"}


# ── Collecte ──────────────────────────────────────────────────

@app.post("/collect/", response_model=schemas.ApartmentOut)
def collect_apartment(apartment: schemas.ApartmentCreate, db: Session = Depends(get_db)):
    result = crud.create_apartment(db=db, apartment=apartment)
    # Ré-entraînement du modèle après chaque nouvelle entrée
    try:
        ml_engine.train(db)
    except Exception as e:
        print(f"Avertissement : ré-entraînement échoué après collecte — {e}")
    return result


# ── Prédiction (OLS réel via ml_engine) ──────────────────────

@app.post("/predict/", response_model=schemas.PredictionResponse)
def predict_price(features: schemas.PredictionRequest, db: Session = Depends(get_db)):
    # Si le modèle n'est pas entraîné, on tente un entraînement à la volée
    if ml_engine.model is None:
        ml_engine.train(db)

    if ml_engine.model is None:
        raise HTTPException(
            status_code=400,
            detail="Données insuffisantes pour prédire. Collectez au moins 10 entrées.",
        )

    try:
        result = ml_engine.predict(features.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction : {e}")

    return schemas.PredictionResponse(
        predicted_price=result["predicted_price"],
        lower_bound=result["lower_bound"],
        upper_bound=result["upper_bound"],
    )


# ── Statistiques ──────────────────────────────────────────────

@app.get("/stats/", response_model=schemas.StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    apartments = db.query(models.Apartment).all()
    total = len(apartments)

    if total == 0:
        return schemas.StatsResponse(
            total_entries=0,
            average_price=0.0,
            r_squared=None,
        )

    avg = sum(a.loyer for a in apartments) / total

    # R² réel calculé par le modèle OLS — plus jamais None si les données existent
    return schemas.StatsResponse(
        total_entries=total,
        average_price=round(avg, 2),
        r_squared=round(ml_engine.r_squared, 4) if ml_engine.r_squared is not None else None,
    )


# ── Distribution ──────────────────────────────────────────────

@app.get("/distribution/")
def get_distribution(db: Session = Depends(get_db)):
    apartments = db.query(models.Apartment).all()

    result: dict = {}
    for a in apartments:
        tq = a.type_quartier
        if tq not in result:
            result[tq] = {"type_quartier": tq, "count": 0, "loyers": []}
        result[tq]["count"] += 1
        result[tq]["loyers"].append(a.loyer)

    output = []
    for tq, d in result.items():
        loyers = d["loyers"]
        output.append({
            "type_quartier": tq,
            "count": d["count"],
            "min": min(loyers),
            "max": max(loyers),
            "average": round(sum(loyers) / len(loyers), 2),
            "loyers": loyers,
        })

    return output
