
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationTypes
from bot.database.models import get_session, User, Transaction
from bot.config import Config
from datetime import datetime

# حالات المحادثة
WAITING_FOR_AMOUNT = 1
WAITING_FOR_WALLET = 2

async def withdraw_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /withdraw"""
    user = update.effective_user
    session = get_session()
    
    db_user = session.query(User).filter_by(telegram_id=user.id).first()
    
    if not db_user:
        await update.message.reply_text("❌ اضغط /start أولاً")
        session.close()
        return
    
    if db_user.balance < Config.MIN_WITHDRAW:
        await update.message.reply_text(
            f"❌ رصيدك غير كافٍ!\n\n"
            f"💰 رصيدك: {db_user.balance:.2f} {Config.COIN_NAME}\n"
            f"📍 الحد الأدنى: {Config.MIN_WITHDRAW} {Config.COIN_NAME}\n\n"
            f"استمر في مشاهدة الإعلانات!"
        )
        session.close()
        return
    
    keyboard = [
        [InlineKeyboardButton("💳 PayPal", callback_data='withdraw_paypal')],
        [InlineKeyboardButton("💎 USDT (TRC20)", callback_data='withdraw_usdt')],
        [InlineKeyboardButton("❌ إلغاء", callback_data='cancel_withdraw')]
    ]
    
    await update.message.reply_text(
        f"💸 *طلب سحب*\n\n"
        f"رصيدك: {db_user.balance:.2f} {Config.COIN_NAME}\n"
        f"اختر طريقة السحب:",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    session.close()

async def withdraw_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الضغط على زر السحب"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'cancel_withdraw':
        await query.edit_message_text("❌ تم إلغاء طلب السحب")
        return
    
    user = update.effective_user
    session = get_session()
    db_user = session.query(User).filter_by(telegram_id=user.id).first()
    
    if data == 'withdraw_paypal':
        await query.edit_message_text(
            "📧 أرسل بريدك الإلكتروني لـ PayPal:\n\n"
            "⚠️ ملاحظة: الحد الأدنى للسحب هو 10$"
        )
        context.user_data['withdraw_method'] = 'paypal'
        return WAITING_FOR_WALLET
        
    elif data == 'withdraw_usdt':
        await query.edit_message_text(
            "📱 أرسل عنوان محفظة USDT (TRC20):\n\n"
            "⚠️ تأكد من صحة العنوان!"
        )
        context.user_data['withdraw_method'] = 'usdt'
        return WAITING_FOR_WALLET
    
    session.close()

async def process_withdraw_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة طلب السحب"""
    user = update.effective_user
    wallet = update.message.text
    method = context.user_data.get('withdraw_method', 'unknown')
    amount = context.user_data.get('withdraw_amount', 0)
    
    # هنا يمكنك إضافة منطق التحقق وإرسال الطلب للإدارة
    admin_message = f"""
🚨 *طلب سحب جديد*

👤 المستخدم: {user.id} (@{user.username})
💰 المبلغ: {amount} {Config.COIN_NAME}
💳 الطريقة: {method.upper()}
📍 المحفظة: `{wallet}`

للموافقة أرسل: /approve_{user.id}_{amount}
    """
    
    # إرسال للإدmin (ضع معرفك هنا)
    admin_id = 123456789  # ← غير هذا لمعرفك
    await context.bot.send_message(admin_id, admin_message, parse_mode='Markdown')
    
    await update.message.reply_text(
        "✅ تم استلام طلب السحب!\n"
        "⏳ سيتم المراجعة خلال 24-48 ساعة."
    )
    
    return ConversationHandler.END
