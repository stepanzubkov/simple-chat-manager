from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from config import SQLALCHEMY_DATABASE_URI


Base = declarative_base()
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True, future=True)
