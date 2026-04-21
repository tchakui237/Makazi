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
from sqlalchemy.pool import NullPool

# ──────────────────────────────────────────────────────────────
# Configuration de l'URL de la base de données
# ──────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")

is_sqlite = False

if DATABASE_URL:
    # SQLAlchemy requiert le préfixe 'postgresql://' et non 'postgres://'
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    # Fallback local : Base SQLite
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'makazi.db')}"
    is_sqlite = True

# ──────────────────────────────────────────────────────────────
# Création de l'Engine
# ──────────────────────────────────────────────────────────────
# CORRECTION CRITIQUE : NullPool pour compatibilité PgBouncer (Supabase port 6543).
# Le Transaction Pooler de Supabase fonctionne en "transaction mode" :
# il réattribue les connexions entre chaque transaction.
# Sans NullPool, SQLAlchemy maintient son propre pool par-dessus PgBouncer,
# ce qui provoque des commits sur des connexions orphelines → données invisibles.
# NullPool force SQLAlchemy à ouvrir/fermer une connexion propre par transaction.

if is_sqlite:
    connect_args = {"check_same_thread": False}
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
else:
    engine = create_engine(DATABASE_URL, poolclass=NullPool)

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
