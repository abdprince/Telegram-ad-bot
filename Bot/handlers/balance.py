
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.models import get_session, User
from bot.utils.helpers import format_balance
from bot.config import Config

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /balance"""
    user = update.effective_user
    session = get_session()
    
    db_user = session.query(User).filter_by(telegram_id=user.id).first()
    
    if not db_user:
        await update.message.reply_text("❌ لم يتم العثور على حسابك. اضغط /start")
        session.close()
        return
    
    balance_text = f"""
💰 *رصيدك الحالي:*

{format_balance(db_user.balance)}

📊 *إحصائياتك:*
• الإعلانات المشاهدة: {db_user.total_ads_watched}
• الحد الأدنى للسحب: {Config.MIN_WITHDRAW} {Config.COIN_NAME}

💡 اضغط على "شاهد الإعلانات" لزيادة رصيدك!
    """
    
    await update.message.reply_text(balance_text, parse_mode='Markdown')
    session.close()

async def balance_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الضغط على زر الرصيد"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    session = get_session()
    db_user = session.query(User).filter_by(telegram_id=user.id).first()
    
    if db_user:
        await query.edit_message_text(
            f"💰 رصيدك: {format_balance(db_user.balance)}\n\n"
            f"📊 إعلانات مشاهدة: {db_user.total_ads_watched}",
            reply_markup=query.message.reply_markup
        )
    
    session.close()
