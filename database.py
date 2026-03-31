from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = "sqlite:///./lotto.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class LotteryResult(Base):
    __tablename__ = "lottery_results"

    id = Column(Integer, primary_key=True, index=True)
    sanook_id = Column(String, unique=True, index=True)
    type = Column(String, index=True) # ไทย, ลาวพัฒนา, ฮานอย, ฮานอยพิเศษ
    draw_date = Column(Date, index=True)
    draw_title = Column(String)
    prizes = Column(JSON)
    url = Column(String)
    scraped_at = Column(DateTime, default=datetime.now)

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
