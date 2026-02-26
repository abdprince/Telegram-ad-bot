from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    balance = Column(Float, default=0.0)
    referral_code = Column(String(20), unique=True)
    referred_by = Column(BigInteger, nullable=True)
    total_ads_watched = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

class Ad(Base):
    __tablename__ = 'ads'
    
    id = Column(Integer, primary_key=True)
    advertiser_id = Column(BigInteger, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    url = Column(String(500))
    reward = Column(Float, default=0.01)  # المكافأة لكل مشاهدة
    budget = Column(Float, default=0.0)   # الميزانية الكلية
    spent = Column(Float, default=0.0)    # ما تم إنفاقه
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    type = Column(String(20))  # 'watch_ad', 'referral', 'withdraw'
    amount = Column(Float, default=0.0)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

# إنشاء قاعدة البيانات
def init_db(database_url):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

Session = None

def get_session():
    global Session
    if Session is None:
        database_url = os.getenv("DATABASE_URL", "sqlite:///bot.db")
        # تعديل URL لـ Railway (Postgres)
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        Session = init_db(database_url)
    return Session()
