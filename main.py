import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("7717678907:aahidouqsn1tfueth-rrows5hgznpni8y50")  # Debes tener BOT_TOKEN=... en tu archivo .env

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ ¡Hola! Tu bot está funcionando correctamente en Render.")

if __name__ == "__main__":
    app = ApplicationBuilder().token("7717678907:aahidouqsn1tfueth-rrows5hgznpni8y50").build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()