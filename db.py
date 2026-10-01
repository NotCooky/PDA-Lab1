from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Float)
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///steam.db", future=True)
SessionLocal = sessionmaker(bind=engine, future=True)
Base = declarative_base()


class Game(Base):
    __tablename__ = "games"

    app_id = Column(Integer, primary_key=True)

    title = Column(String, nullable=False)
  
    release_date = Column(String)

    price = Column(Float)         
    
    discount = Column(Integer)     
    
    rating = Column(Float)         

    platforms = Column(String)




def init_db():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
    print("БД инициализирована")