import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# load environmental variables
load_dotenv()

# load database url from environmental variables
DATABASE_URL = os.getenv("DATABASE_URL")

# raise error if database url does not exist
if DATABASE_URL is None:
    raise Exception("DATABASE_URL environment variable not set.")

# set up SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# set up declarative base
Base = declarative_base()

# set up SessionLocal class
# autocommit=False : database transactions need to be committed explicitly
# autoflush=False : changes won't be sent to the database automatically unless commit or flush is called
# bind=engine : session is linked to engine as created above
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# set up the dependency to open one DB session per request.
# After the request was successful or even failed, the session will be closed
# (seems to be standard using FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()