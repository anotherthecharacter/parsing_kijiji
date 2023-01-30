from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from decouple import config


engine = create_engine(f'postgresql://{config("DB_USER")}:{config("DB_PASSWORD")}@127.0.0.1:5432/kijiji', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()
