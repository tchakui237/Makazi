"""
Makazi — Configuration de la base de données SQLAlchemy.

Ce module fournit :
- L'engine SQLAlchemy (PostgreSQL en production, SQLite en local)
- La factory de sessions `SessionLocal`
- La classe de base `Base` pour les modèles déclaratifs
- Le générateur `get_db()` pour l'injection de dépendances FastAPI
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ──────────────────────────────────────────────────────────────
# Configuration de l'URL de la base de données
# ──────────────────────────────────────────────────────────────
# 1. On cherche la variable d'environnement (ex: Supabase via Railway)
DATABASE_URL = os.getenv("DATABASE_URL")

is_sqlite = False

if DATABASE_URL:
    # SQLAlchemy requiert le préfixe 'postgresql://' et non 'postgres://'
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    # 2. Fallback local : Base SQLite sur ton Kali Linux
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'makazi.db')}"
    is_sqlite = True

# ──────────────────────────────────────────────────────────────
# Création de l'Engine
# ──────────────────────────────────────────────────────────────
# Le paramètre check_same_thread est obligatoire pour SQLite 
# mais provoque une erreur fatale sur PostgreSQL. On le rend conditionnel.
connect_args = {"check_same_thread": False} if is_sqlite else {}
from sqlalchemy.pool import NullPool

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    poolclass=NullPool if not is_sqlite else None,
)



SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Générateur de session pour l'injection de dépendances FastAPI.
    Assure la fermeture propre de la session après chaque requête.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
