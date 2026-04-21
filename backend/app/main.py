"""
Makazi — Application FastAPI principale.

Points d'entree :
    POST /collect      : Ajouter un appartement + re-entrainer le modele
    GET  /stats        : Statistiques globales (total, moyenne, R2)
    POST /predict      : Prediction de loyer avec IC 95%
    GET  /distribution : Donnees de distribution des loyers pour graphique
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func

from .database import engine, get_db, Base
from .models import Apartment
from .schemas import (
    ApartmentCreate, ApartmentOut,
    PredictionRequest, PredictionResponse,
    StatsResponse,
)
from .ml import ml_engine
from .seed import seed_database


# ── Lifecycle : initialisation au demarrage ───────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Au demarrage :
    1. Creer les tables SQLite (ou PostgreSQL) si elles n'existent pas
    2. Inserer les donnees de test si la base est vide
    3. Entrainer le modele OLS initial
    """
    Base.metadata.create_all(bind=engine)

    from .database import SessionLocal
    db = SessionLocal()
    try:
        seed_database(db)
        ml_engine.train(db)
    finally:
        db.close()

    yield  # Application en fonctionnement


app = FastAPI(
    title="Makazi API",
    description="API d'analyse immobiliere pour Yaounde",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS : autoriser le frontend Next.js (Local + Vercel) ─────────
# On récupère l'URL du frontend si elle est définie dans les variables d'environnement de Railway
FRONTEND_URL = os.getenv("FRONTEND_URL")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://makazi-frontend.vercel.app", # <-- Remplace ceci par ton VRAI lien Vercel plus tard si tu n'utilises pas la variable d'environnement
]

if FRONTEND_URL:
    origins.append(FRONTEND_URL)

# On autorise aussi toutes les origines Vercel (utile si Vercel crée des URLs de preview)
origins.append("https://*.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════════════════════════
# ROUTE 1 : POST /collect
# ══════════════════════════════════════════════════════════════════
@app.post("/collect", response_model=ApartmentOut)
def collect(data: ApartmentCreate, db: Session = Depends(get_db)):
    """
    Ajoute un nouvel appartement a la base de donnees.
    La validation Pydantic bloque automatiquement les loyers incoherents.
    """
    apartment = Apartment(
        type_quartier=data.type_quartier,
        chambres=data.chambres,
        douches=data.douches,
        salons=data.salons,
        cuisines=data.cuisines,
        bureaux=data.bureaux,
        forage=data.forage,
        eneo=data.eneo,
        loyer=data.loyer,
    )
    db.add(apartment)
    db.commit()
    db.refresh(apartment)

    # Re-entrainement automatique apres chaque nouvel ajout sain
    ml_engine.train(db)

    return apartment


# ══════════════════════════════════════════════════════════════════
# ROUTE 2 : GET /stats
# ══════════════════════════════════════════════════════════════════
@app.get("/stats", response_model=StatsResponse)
def stats(db: Session = Depends(get_db)):
    """
    Retourne les statistiques globales.
    """
    total = db.query(sql_func.count(Apartment.id)).scalar() or 0
    avg = db.query(sql_func.avg(Apartment.loyer)).scalar() or 0.0

    return StatsResponse(
        total_entries=total,
        average_price=round(float(avg), 0),
        r_squared=round(ml_engine.r_squared, 4) if ml_engine.r_squared else None,
    )


# ══════════════════════════════════════════════════════════════════
# ROUTE 3 : POST /predict
# ══════════════════════════════════════════════════════════════════
@app.post("/predict", response_model=PredictionResponse)
def predict(data: PredictionRequest):
    """
    Predit le loyer Y_hat et l'intervalle de confiance a 95%.
    """
    try:
        result = ml_engine.predict({
            "type_quartier": data.type_quartier,
            "chambres": data.chambres,
            "douches": data.douches,
            "salons": data.salons,
            "cuisines": data.cuisines,
            "bureaux": data.bureaux,
            "forage": data.forage,
            "eneo": data.eneo,
        })
        return PredictionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ══════════════════════════════════════════════════════════════════
# ROUTE 4 : GET /distribution
# ══════════════════════════════════════════════════════════════════
@app.get("/distribution")
def distribution(db: Session = Depends(get_db)):
    """
    Retourne les donnees de distribution des loyers.
    """
    apartments = db.query(Apartment).all()
    
    groups: dict[str, list[float]] = {}
    for a in apartments:
        if a.type_quartier not in groups:
            groups[a.type_quartier] = []
        groups[a.type_quartier].append(a.loyer)

    result = []
    for tq, loyers in groups.items():
        result.append({
            "type_quartier": tq,
            "count": len(loyers),
            "min": min(loyers),
            "max": max(loyers),
            "average": round(sum(loyers) / len(loyers), 0),
            "loyers": sorted(loyers),
        })

    return result