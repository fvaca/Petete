import os
import logging
import random
# import urllib3 - not sure if this is needed...
import telegram
import telegram.ext
import petete

from dotenv import load_dotenv
# from telegram import Update, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler



logger = logging.getLogger(__name__)

# Load environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')
OPENAI_PROJECT_ID = os.environ.get('OPENAI_PROJECT_ID')
OPENAI_PROJECT_SECRET_KEY = os.environ.get('OPENAI_PROJECT_SECRET_KEY')
ALLOW_USER_PASS= os.environ.get('ALLOW_USER_PASS')
ADMIN_PASS= os.environ.get('ADMIN_PASS')

# Store bot screaming status
screaming = False

# Pre-assign menu text
FIRST_MENU = "<b>Menu 1</b>\n\nA beautiful menu with a shiny inline button."
SECOND_MENU = "<b>Menu 2</b>\n\nA better menu with even more shiny inline buttons."

# Pre-assign button text
NEXT_BUTTON = "Next"
BACK_BUTTON = "Back"
TUTORIAL_BUTTON = "Tutorial"

# Build keyboards
FIRST_MENU_MARKUP = telegram.InlineKeyboardMarkup([[
    telegram.InlineKeyboardButton(NEXT_BUTTON, callback_data=NEXT_BUTTON)
]])
SECOND_MENU_MARKUP = telegram.InlineKeyboardMarkup([
    [telegram.InlineKeyboardButton(BACK_BUTTON, callback_data=BACK_BUTTON)],
    [telegram.InlineKeyboardButton(TUTORIAL_BUTTON, url="https://core.telegram.org/bots/api")]
])

AIBOT = petete.Soul(OPENAI_ORG_ID, OPENAI_PROJECT_ID, OPENAI_PROJECT_SECRET_KEY)

# Define a function to check if the password is valid
def is_password_valid(password, is_admin=False):
    if is_admin:
        return password == ADMIN_PASS
    else:
        return password == ALLOW_USER_PASS

# Define the echo handler - it will be called when the bot receives a message
def echo(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    """
    This function would be added to the dispatcher as a handler for messages coming from the Bot API
    """

    # Print to console the message sent by the user
    print(f'({update.message.from_user.id}) {update.message.from_user.first_name} wrote {update.message.text}')
    
    is_group = update.message.chat.type == 'group' or update.message.chat.type == 'supergroup'
    if is_group and update.message.text and 'petete' in update.message.text.lower():
        response = AIBOT.chat(update.message.text, update.message.from_user.id)
        context.bot.send_message(
            update.message.chat_id,
            response
        )        
    else:
        response = AIBOT.chat(update.message.text, update.message.from_user.id)
        context.bot.send_message(
            update.message.chat_id,
            response
        )

    nr = random.randint(0, 100) 
    if nr== 42 or nr == 69 or nr == 100:
        context.bot.send_message(
                update.message.chat_id,
                "El libro gordo te enseña, el libro gordo entretiene, y yo te digo contenta, hasta el mensaje que viene."
            )
        
# Define the start handler - it will be called when the bot receives the /start command
def start(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    """
    This function handles the /start command
    """

    print(f'({update.message.from_user.id}) {update.message.from_user.first_name} started the bot')
    context.bot.send_message(
        update.message.chat_id,
        AIBOT.chat("hola, Como puedes ayudarme?", update.message.from_user.id)
    )

# Define the clave handler - it will be called when the bot receives the /admin_hablame command       
def add_bot_user(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    """
    This function handles the /admin_hablame command
    """
    if not context.args:
        context.bot.send_message(
            update.message.chat_id,
            "Por favor, ingresa la clave para poder interactuar con el bot."
        )
        return
    password = context.args[0]
    
    if update.message.text and is_password_valid(password):
        if AIBOT.allow_user(update.message.from_user.id, update.message.from_user.username, update.message.from_user.first_name):
            context.bot.send_message(
                update.message.chat_id,
                f"{update.message.from_user.first_name}, puedes interactuar con el bot."
            )
    else:
        context.bot.send_message(
            update.message.chat_id,
            "Clave incorrecta, no tienes permisos para interactuar con el bot."
        )

# Define the show_all_bot_users handler - it will be called when the bot receives the /admin_bot_users command
def show_all_bot_users(update: telegram.Update, context: telegram.ext.CallbackContext) -> None: 
    """
    This function handles the /admin_bot_users command
    """
    
    password = context.args[0]
    if is_password_valid(password, is_admin=True):
        context.bot.send_message(
            update.message.chat_id,
            "Estos son los usuarios que pueden interactuar con el bot."
        )
        
        users = AIBOT.list_users()        
        for user in users:
            context.bot.send_message(
                update.message.chat_id,
                user
            )

# Define the show_all_bot_settings handler - it will be called when the bot receives the /admin_bot_settings command
def show_all_bot_settings(update: telegram.Update, context: telegram.ext.CallbackContext) -> None: 
    """
    This function handles the /admin_bot_settings command
    """
    
    password = context.args[0]
    if is_password_valid(password, is_admin=True):
        context.bot.send_message(
            update.message.chat_id,
            "Estos son los ajustes del bot."
        )
        
        settings = AIBOT.list_settings()        
        for setting in settings:
            context.bot.send_message(
                update.message.chat_id,
                setting
            )

def show_bot_behavior(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:  
    """
    This function handles the /cual_es_la_personalidad command
    """
    
    context.bot.send_message(
        update.message.chat_id,
        AIBOT.get_user_behavior(update.message.from_user.id)
    )

def change_bot_behavior(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:    
    """
    This function handles the /cambia_personalidad command
    """
    
    behavior = context.args[0]
    AIBOT.update_user_behavior(update.message.from_user.id, behavior)
    
    context.bot.send_message(
        update.message.chat_id,
        "Personalidad actualizada."
    )

def change_bot_model(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:    
    """
    This function handles the /cambia_modelo command
    """
    
    model = context.args[0]
    AIBOT.update_user_model(update.message.from_user.id, model)
    
    context.bot.send_message(
        update.message.chat_id,
        "Modelo actualizado."
    )  

def get_messages(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:    
    """
    This function handles the /mi_mensajes command
    """
    password = context.args[0]
    if is_password_valid(password, is_admin=True):
        messages = AIBOT.get_messages()
        
        for message in messages:
            context.bot.send_message(
                update.message.chat_id,
                message
            )
    else:        
        messages = AIBOT.get_messages(update.message.from_user.id)    
        for message in messages:
            context.bot.send_message(
                update.message.chat_id,
                message
            )

# Define the main function to run the bot
def main() -> None:
    telegram_updater = telegram.ext.Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    # Then, we register each handler and the conditions the update must meet to trigger it
    dispatcher = telegram_updater.dispatcher

    # Echo any message that is not a command
    dispatcher.add_handler(telegram.ext.MessageHandler(~telegram.ext.Filters.command, echo))
    
    dispatcher.add_handler(telegram.ext.CommandHandler("admin_settings", show_all_bot_settings, pass_args=True)) #hidden command
    dispatcher.add_handler(telegram.ext.CommandHandler("admin_bot_users", show_all_bot_users, pass_args=True)) #hidden command
    
    dispatcher.add_handler(telegram.ext.CommandHandler('hablame', add_bot_user, pass_args=True))    
    dispatcher.add_handler(telegram.ext.CommandHandler('cual_es_la_personalidad', show_bot_behavior))
    dispatcher.add_handler(telegram.ext.CommandHandler('cambia_personalidad', change_bot_behavior))
    dispatcher.add_handler(telegram.ext.CommandHandler('cambia_modelo', change_bot_model))
    dispatcher.add_handler(telegram.ext.CommandHandler('mi_mensajes', get_messages, pass_args=True))

    # Start the Bot
    telegram_updater.start_polling()

    # Run the bot until you press Ctrl-C
    telegram_updater.idle()


if __name__ == '__main__':
    main()