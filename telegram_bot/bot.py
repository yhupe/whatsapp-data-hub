import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from database.database import get_session_local

# Import of services
from services.message_processing_service import MessageProcessingService
from services.message_log_service import MessageLogService
from services.employee_service import EmployeeService

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


## NEW

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verarbeitet eingehende Textnachrichten, speichert sie und antwortet."""

    user_message_text = update.message.text
    telegram_user_id = update.effective_user.id

    # Hier solltest du die tatsächliche Employee-UUID des Mitarbeiters hinterlegen,
    # der diesen Bot nutzt, oder eine Logik entwickeln, die den Employee ermittelt.
    # Fürs Erste nehmen wir eine Dummy-UUID oder None.
    employee_uuid = None  # Oder UUID("DEINE_FESTE_EMPLOYEE_UUID_HIER")

    session_local_instance = get_session_local()
    db = session_local_instance()  # Manuelle Datenbank-Session im Bot-Kontext

    try:
        # Hier instanziieren wir die Services direkt, da wir keine FastAPI-Depends haben
        # im Bot-Kontext. Für komplexere Bots könnte man hier auch eine Dependency Injection
        # Bibliothek wie 'fastapi-utils' oder 'simple-di' verwenden, aber manuell ist ok für jetzt.

        # Wichtig: Die Services benötigen die Session 'db'
        employee_service_instance = EmployeeService(db=db)
        message_log_service_instance = MessageLogService(db=db)

        # NEU: MessageProcessingService instanziieren
        message_processing_service_instance = MessageProcessingService(
            db=db,
            message_log_service=message_log_service_instance,
            employee_service=employee_service_instance
        )

        # Verwende den neuen MessageProcessingService
        db_message_log = await message_processing_service_instance.process_inbound_message(
            employee_id=employee_uuid,
            whatsapp_customer_phone_number=f"telegram:{telegram_user_id}",
            # Identifiziert den Telegram-Nutzer als "Kunden"
            raw_message_content=user_message_text
        )

        # Die Antwort vom System (simulierte KI)
        response_text = db_message_log.system_response_content or "Message processed."
        await update.message.reply_text(response_text)

    except Exception as e:
        print(f"Error processing message: {e}")
        await update.message.reply_text(f"There's an internal error while processing your message.")
    finally:
        db.close()


## NEW


def run_telegram_bot():
    """Starts the Telegram telegram_bot."""
    print("Starting Telegram telegram_bot...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # --- Registriere Handler ---
    application.add_handler(CommandHandler("start", start_command))

    # Reagiert auf alle Textnachrichten, die keine Befehle sind
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Füge einen Fehler-Handler hinzu
    #application.add_handler(application.error_handler)


    # Starte den Bot
    print("Bot is polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    print("Telegram telegram_bot stopped.")


if __name__ == "__main__":
    run_telegram_bot()