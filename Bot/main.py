
import logging
import os
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler
from bot.config import Config
from bot.database.models import init_db
from bot.handlers.start import start_command, help_command
from bot.handlers.balance import balance_command, balance_callback
from bot.handlers.referral import referral_command, referral_callback
from bot.handlers.withdraw import withdraw_command, withdraw_callback, process_withdraw_request

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# إنشاء تطبيق Flask
app = Flask(__name__)

# تهيئة قاعدة البيانات
database_url = os.getenv("DATABASE_URL", "sqlite:///bot.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
init_db(database_url)

# إنشاء تطبيق Telegram
telegram_app = Application.builder().token(Config.BOT_TOKEN).build()

# إضافة المعالجات
telegram_app.add_handler(CommandHandler("start", start_command))
telegram_app.add_handler(CommandHandler("help", help_command))
telegram_app.add_handler(CommandHandler("balance", balance_command))
telegram_app.add_handler(CommandHandler("referral", referral_command))
telegram_app.add_handler(CommandHandler("withdraw", withdraw_command))

# معالجات الأزرار
telegram_app.add_handler(CallbackQueryHandler(balance_callback, pattern='^balance$'))
telegram_app.add_handler(CallbackQueryHandler(referral_callback, pattern='^referral$'))
telegram_app.add_handler(CallbackQueryHandler(withdraw_callback, pattern='^withdraw'))

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    """استقبال التحديثات من Telegram"""
    try:
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        telegram_app.process_update(update)
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/')
def home():
    """صفحة التحقق من الصحة"""
    return "Bot is running! ✅", 200

@app.route('/health')
def health():
    """فحص الصحة"""
    return jsonify({
        'status': 'healthy',
        'bot': telegram_app.bot.username if telegram_app.bot else 'unknown'
    }), 200

def setup_webhook():
    """إعداد Webhook"""
    webhook_url = f"{Config.WEBHOOK_URL}/webhook"
    try:
        telegram_app.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")

if __name__ == '__main__':
    # إعداد Webhook
    setup_webhook()
    
    # تشغيل Flask
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=False
    )
else:
    # للإنتاج (Gunicorn)
    setup_webhook()
