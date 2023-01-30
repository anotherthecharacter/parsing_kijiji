from sqlalchemy import Column, Integer, String

from alchemy import Base, engine


class Ad(Base):
    __tablename__ = 'ad'

    id = Column(Integer, primary_key=True)
    page = Column(Integer)
    image = Column(String)
    date = Column(String)
    currency = Column(String)
    price = Column(String)


Base.metadata.create_all(engine)
