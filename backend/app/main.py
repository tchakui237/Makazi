import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud, database
from .database import engine, get_db

# CRITIQUE : Cette ligne crée les tables sur Supabase au démarrage si elles n'existent pas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Makazi API", description="API de prédiction des prix de loyer à Yaoundé")

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Makazi - Système de collecte et prédiction"}

# --- Routes de Collecte ---
@app.post("/collect/", response_model=schemas.House)
def create_house(house: schemas.HouseCreate, db: Session = Depends(get_db)):
    return crud.create_house(db=db, house=house)

@app.get("/houses/", response_model=list[schemas.House])
def read_houses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_houses(db, skip=skip, limit=limit)

# --- Routes de Prédiction ---
@app.post("/predict/")
def predict_price(features: schemas.PredictionInput, db: Session = Depends(get_db)):
    # On récupère les données pour "entraîner" ou calibrer le calcul
    houses = crud.get_houses(db, limit=1000)
    if len(houses) < 2:
        raise HTTPException(status_code=400, detail="Pas assez de données pour prédire")
    
    # Logique simple de prix moyen par quartier/chambre (Simulation OLS)
    avg_price = sum([h.price for h in houses]) / len(houses)
    prediction = avg_price * (features.rooms / 2) # Exemple de calcul
    
    return {"predicted_price": round(prediction, 2)}

# --- Route de Statistique (pour le Dashboard) ---
@app.get("/stats/")
def get_stats(db: Session = Depends(get_db)):
    houses = crud.get_houses(db, limit=1000)
    return {
        "total_houses": len(houses),
        "avg_price": sum([h.price for h in houses]) / len(houses) if houses else 0
    }

if __name__ == "__main__":
    import uvicorn
    # Railway utilise la variable d'environnement PORT
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
