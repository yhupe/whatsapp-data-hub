import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from database.database import get_session_local

# Import of services
from services.message_processing_service import MessageProcessingService
from services.message_log_service import MessageLogService
from services.employee_service import EmployeeService

# Import of utils
from utils.jwt_utils import create_magic_link_token

# load environmental variables
load_dotenv()

# Load telegram_bot api token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise Exception("Environment variable 'TELEGRAM_BOT_TOKEN' not set.")

# Load FastAPI base URL
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL")
if not FASTAPI_BASE_URL:
    raise ValueError("FASTAPI_BASE_URL environment variable not set. Please add it to your .env file.")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a message when the command /start is issued.
    """

    user = update.effective_user

    keyboard = [[KeyboardButton("Share my telephone number", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_html(
        f"Hi {user.mention_html()}! I am your database bot.\n"
        f"Please share your phone number so I can identify you!",
        reply_markup=reply_markup
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Processes inbound messages and answers the chat automatically.
    """

    user_message_text = update.message.text
    telegram_user_telegram_id = update.effective_user.id

    employee_uuid = None
    user_identifier_for_log = f"telegram:{telegram_user_telegram_id}"

    session_local_instance = get_session_local()
    db = session_local_instance()

    try:
        employee_service_instance = EmployeeService(db=db)
        message_log_service_instance = MessageLogService(db=db)

        # new instance of MessageProcessingService
        message_processing_service_instance = MessageProcessingService(
            db=db,
            message_log_service=message_log_service_instance,
            employee_service=employee_service_instance
        )

        # Retrieve the phone number from employee based on telegram ID
        employee_instance = employee_service_instance.get_employee_by_telegram_id(telegram_user_telegram_id)

        response_text = ""

        if employee_instance:
            employee_uuid = employee_instance.id  # actual employee id of the user
            if employee_instance.phone_number:
                user_identifier_for_log = employee_instance.phone_number

            print(
                f"Employee {employee_instance.name} (ID: {employee_instance.id}, Authenticated: {employee_instance.is_authenticated}) found for Telegram ID {telegram_user_telegram_id}.")


            # authentication check
            if not employee_instance.is_authenticated:
                # Employee is not authenticated:
                print(f"Employee {employee_instance.name} is not authenticated. Generating magic link.")

                # create magic link
                token = create_magic_link_token(
                    employee_id=employee_instance.id,
                    email=employee_instance.email
                )

                # refactor the magic link url
                magic_link = f"{FASTAPI_BASE_URL}/auth/verify?token={token}"

                response_text = (
                    f"Hello {employee_instance.name}, your account is not authenticated, yet."
                    f"Please click the link to verify your identity:\n"
                    f"\n{magic_link}\n\n"
                    f"After that I can process your messages."
                )

                await update.message.reply_text(response_text)
                return

            else:
                print(f"Employee {employee_instance.name} is authenticated. Processing message normally.")

                db_message_log = await message_processing_service_instance.process_inbound_message(
                    employee_id=employee_uuid,
                    phone_number=user_identifier_for_log,
                    raw_message_content=user_message_text
                )

                response_text = db_message_log.system_response_content or "Message processed."

        else:
        # Employee not found: request to share the own contact
            print(f"No employee found for Telegram ID {telegram_user_telegram_id}. Requesting phone number share.")
            response_text = (
                "Hello! Your telegram ID is not known in the system.\n"
                "Please share your number by clicking the 'Share contact details' button "
                "so that I can authenticate and identify you."
            )
            await update.message.reply_text(response_text)
            return

        if response_text:  # Only if response_text is not empty
            await update.message.reply_text(response_text)

    except Exception as e:
        print(f"Error processing message: {e}")

        await update.message.reply_text(f"An internal error occurred while processing your message. [handle_message]")
    finally:
        db.close()


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Processes shared contact data and shows phone number.
    """

    user = update.effective_user

    if not update.message.contact:
        await update.message.reply_text("No contact details shared. Please click the button to share your phone number.")
        return

    # Telegram gives the phone number without '+', so I need to add it
    phone_number = update.message.contact.phone_number
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number

    telegram_user_id = user.id

    session_local_instance = get_session_local()
    db = session_local_instance()

    employee = None
    try:
        employee_service_instance = EmployeeService(db=db)

        # Try to find employee by telegram user id
        employee = employee_service_instance.get_employee_by_telegram_id(telegram_user_id)

        # if not found, try to find by phone number
        if not employee:
            employee = employee_service_instance.get_employee_by_phone_number(phone_number)

            if employee:
                # If employee found by phone number, telegram ID is being updated in db
                print(
                    f"Employee {employee.name} found by phone number. Updating with telegram ID {telegram_user_id}.")
                # updating the telegram ID
                employee = employee_service_instance.update_employee_telegram_details(
                    employee_id=employee.id,
                    telegram_id=telegram_user_id,
                )

                if not employee:
                    await update.message.reply_text(
                        f"There was an error while updating the employee account {employee.name}. Please try again.")
                    return

        # Either a found/updated employee or still None
        if employee:
            print(
                f"Employee {employee.name} (ID: {employee.id}, Telegram ID: {employee.telegram_id}) found/ linked.")

            # Checking the authentication status
            if employee.is_authenticated:
                response_text = (
                    f"Welcome back, {employee.name}! You are already authenticated "
                    f"and linked with your number {employee.phone_number}.\n"
                    f"You can fully use the chat bot! "
                )
            else:
                # Magic link
                print(
                    f"Employee {employee.name} is not authenticated after contact share. Generating magic link.")
                token = create_magic_link_token(
                    employee_id=employee.id,
                    email=employee.email
                )
                magic_link = f"{FASTAPI_BASE_URL}/auth/verify?token={token}"

                response_text = (
                    f"Thank you, {employee.name}! Your phone number ({employee.phone_number}) "
                    f"has been collected, but you are not authenticated, yet.\n"
                    f"Please click the link below to confirm your identity:\n"
                    f"\n{magic_link}\n\n"
                    f"After that I can process your messages."
                )

        else:
            # Not found by telegram ID or phone number
            response_text = (
                f"Hello {user.first_name}! Your phone number ({phone_number}) and telegram ID ({telegram_user_id}) "
                f"are not known in the system. Please create a new account via the "
                f"respective FastAPI-Endpoint.\n"
                f"After you did this, come back here, share your number again and we can continue your authentication."
                f"\n Follow the link (local and live) to POST a new EMPLOYEE: http://127.0.0.1:8000/docs or https://whatsapp-data-hub.fly.dev/docs"
            )

        await update.message.reply_text(response_text)

    except Exception as e:
        print(f"ERROR: Error in handle_contact: {e}")
        await update.message.reply_text(f"There has an internal error occurred while processing your data. [handle_contact]")
    finally:
        db.close()


def run_telegram_bot():
    """Starts the Telegram telegram_bot."""

    print("Starting Telegram telegram_bot...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    #  Initializes the start_command when the bot is started
    application.add_handler(CommandHandler("start", start_command))

    # Handler reacts to all text messages that are not assigned commands, after start
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # New handler for contact messages
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    # Start the bot
    print("Bot is polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    print("Telegram telegram_bot stopped.")

# To run the file: PYTHONPATH=. python -m telegram_bot.bot

if __name__ == "__main__":
    run_telegram_bot()