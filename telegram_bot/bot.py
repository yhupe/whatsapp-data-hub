import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# load environmental variables
load_dotenv()

# Fetch telegram telegram_bot api token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise Exception("Environment variable 'TELEGRAM_BOT_TOKEN' not set.")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! I am your chat telegram_bot to interact with your database.\n How can I help you?",
    )

async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message."""
    # Dies ist ein Platzhalter. Hier würdest du die Nachricht verarbeiten
    # und z.B. an deine FastAPI-Anwendung oder KI weiterleiten.
    await update.message.reply_text(f"Du hast gesagt: '{update.message.text}'")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log the error and send a telegram message to notify the developer."""
    print(f"Update {update} caused error {context.error}")
    # Hier könntest du eine Benachrichtigung an einen Admin senden
    # await context.telegram_bot.send_message(chat_id=YOUR_ADMIN_CHAT_ID, text=f"Error: {context.error}")


def run_telegram_bot():
    """Starts the Telegram telegram_bot."""
    print("Starting Telegram telegram_bot...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # --- Registriere Handler ---
    application.add_handler(CommandHandler("start", start_command))

    # Reagiert auf alle Textnachrichten, die keine Befehle sind
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))

    # Füge einen Fehler-Handler hinzu
    #application.add_handler(application.error_handler)


    # Starte den Bot
    print("Bot is polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    print("Telegram telegram_bot stopped.")

# Dieser Block stellt sicher, dass der Bot nur läuft, wenn das Skript direkt ausgeführt wird
if __name__ == "__main__":
    run_telegram_bot()