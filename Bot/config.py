import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")
    WEBHOOK_URL = os.getenv("RAILWAY_STATIC_URL", "https://your-app.up.railway.app")
    PORT = int(os.getenv("PORT", 8080))
    
    # إعدادات المنصة
    COIN_NAME = "جوهرة"  # اسم العملة الافتراضية
    MIN_WITHDRAW = 100   # الحد الأدنى للسحب
    REFERRAL_BONUS = 10  # مكافأة الإحالة
