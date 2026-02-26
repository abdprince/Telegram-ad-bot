
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from bot.database.models import get_session, User
from bot.utils.helpers import generate_referral_code

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /start"""
    user = update.effective_user
    session = get_session()
    
    # التحقق من وجود المستخدم أو إنشاؤه
    db_user = session.query(User).filter_by(telegram_id=user.id).first()
    
    if not db_user:
        # التحقق من كود الإحالة
        referral_code = None
        if context.args and len(context.args) > 0:
            referral_code = context.args[0]
        
        # إنشاء مستخدم جديد
        db_user = User(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            referral_code=generate_referral_code(user.id),
            referred_by=int(referral_code) if referral_code and referral_code.isdigit() else None
        )
        session.add(db_user)
        session.commit()
        
        # مكافأة الإحالة إذا وجدت
        if db_user.referred_by:
            referrer = session.query(User).filter_by(telegram_id=db_user.referred_by).first()
            if referrer:
                from bot.config import Config
                referrer.balance += Config.REFERRAL_BONUS
                session.commit()
                await context.bot.send_message(
                    chat_id=referrer.telegram_id,
                    text=f"🎉 انضم صديق بإحالتك! ربحت {Config.REFERRAL_BONUS} جوهرة"
                )
    
    # تحديث آخر نشاط
    from datetime import datetime
    db_user.last_active = datetime.utcnow()
    session.commit()
    
    # إنشاء أزرار التفاعل
    keyboard = [
        [
            InlineKeyboardButton(
                "🚀 شاهد الإعلانات", 
                web_app=WebAppInfo(url="https://your-web-app-url.com")
            )
        ],
        [
            InlineKeyboardButton("💰 رصيدي", callback_data='balance'),
            InlineKeyboardButton("🔗 رابط الإحالة", callback_data='referral')
        ],
        [
            InlineKeyboardButton("📊 إحصائياتي", callback_data='stats'),
            InlineKeyboardButton("💸 طلب سحب", callback_data='withdraw')
        ]
    ]
    
    welcome_text = f"""
👋 أهلاً {user.first_name}!

🎯 مرحباً بك في منصة الإعلانات الافتراضية

💎 اجمع الجواهر بمشاهدة الإعلانات
🎁 اربح المزيد من خلال دعوة أصدقائك
💵 حوّل جواهرك إلى أموال حقيقية

📌 اضغط على الزر أدناه لبدء مشاهدة الإعلانات!
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    session.close()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /help"""
    help_text = """
📖 *أوامر البوت:*

/start - بدء البوت والقائمة الرئيسية
/balance - عرض رصيدك الحالي
/referral - الحصول على رابط الإحالة
/withdraw - طلب سحب الأرباح
/help - عرض هذه الرسالة

💡 *كيفية الربح:*
1. اضغط على "شاهد الإعلانات"
2. شاهد الإعلان لمدة 30 ثانية
3. اجمع جواهرك فوراً!

🎁 *مكافأة الإحالة:*
اربح 10 جواهر لكل صديق ينضم عبر رابطك!
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')
