import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


# set up declarative base
Base = declarative_base()

# Placeholders
_engine = None
_SessionLocal = None

def get_engine():
    global _engine # Wir wollen die globale Variable _engine ändern
    if _engine is None: # Nur erstellen, wenn sie noch nicht existiert
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            # Dieser Fehler wird nur ausgelöst, wenn DATABASE_URL wirklich nicht gesetzt ist.
            # In den Tests sollte es durch .env.test gesetzt werden, in der Haupt-App durch main.py.
            raise Exception("DATABASE_URL environment variable not set.")

        # Hier wird die Engine erstellt (Passe dies an dein PostgreSQL an)
        _engine = create_engine(database_url)
    return _engine


def get_session_local():
    global _SessionLocal # Wir wollen die globale Variable _SessionLocal ändern
    if _SessionLocal is None: # Nur erstellen, wenn sie noch nicht existiert
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_db():
    # NEU: Ruft get_session_local() auf, um die SessionLocal-Klasse zu bekommen,
    # und dann () um eine Session-Instanz zu erstellen.
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()