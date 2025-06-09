from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class SummaryHistory(Base):
    __tablename__ = 'summary_history'

    id = Column(Integer, primary_key=True)
    original_text = Column(Text)
    summary = Column(Text)
    source_lang = Column(String(5))
    target_lang = Column(String(5))
    summary_length = Column(String(20))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# Thay đổi thông tin kết nối cho phù hợp
DATABASE_URL = "mysql+pymysql://root:quan21042004@localhost:3306/news_summary_db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
