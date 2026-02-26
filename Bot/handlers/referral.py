
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database.models import get_session, User
from bot.config import Config

async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /referral"""
    user = update.effective_user
    session = get_session()
    
    db_user = session.query(User).filter_by(telegram_id=user.id).first()
    
    if not db_user:
        await update.message.reply_text("❌ اضغط /start أولاً")
        session.close()
        return
    
    bot_username = context.bot.username
    referral_link = f"https://t.me/{bot_username}?start={db_user.telegram_id}"
    
    referral_text = f"""
🔗 *رابط الإحالة الخاص بك:*

`{referral_link}`

انسخ الرابط وشاركه مع أصدقائك!

🎁 *المكافأة:* {Config.REFERRAL_BONUS} {Config.COIN_NAME} لكل صديق

📈 *إحصائياتك:*
• عدد الإحالات: {db_user.total_ads_watched // 10}  # مثال تقديري
    """
    
    keyboard = [
        [InlineKeyboardButton("📤 مشاركة الرابط", url=f"https://t.me/share/url?url={referral_link}&text=انضم%20واكسب%20جواهر!")]
    ]
    
    await update.message.reply_text(
        referral_text, 
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    session.close()

async def referral_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الضغط على زر الإحالة"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    session = get_session()
    db_user = session.query(User).filter_by(telegram_id=user.id).first()
    
    if db_user:
        bot_username = context.bot.username
        referral_link = f"https://t.me/{bot_username}?start={db_user.telegram_id}"
        
        await query.edit_message_text(
            f"🔗 رابطك:\n`{referral_link}`\n\n"
            f"🎁 مكافأة: {Config.REFERRAL_BONUS} {Config.COIN_NAME}/صديق",
            parse_mode='Markdown'
        )
    
    session.close()
