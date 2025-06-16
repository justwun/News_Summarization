from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

Base = declarative_base()

class SummaryHistory(Base):
    __tablename__ = 'summary_history'

    id = Column(Integer, primary_key=True)
    original_text = Column(Text)
    summary = Column(Text)
    source_lang = Column(String(5))
    target_lang = Column(String(5))
    summary_length = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))  # Thêm dòng này

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Thay đổi thông tin kết nối cho phù hợp
DATABASE_URL = "mysql+pymysql://root:quan21042004@localhost:3306/news_summary_db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
