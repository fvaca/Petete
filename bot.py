import os
import logging
import random
from html import escape
from uuid import uuid4
import telegram
import telegram.ext
import telegram.constants
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

# Create an instance of the petete.Soul class to interact with the OpenAI API
AIBOT = petete.Soul(OPENAI_ORG_ID, OPENAI_PROJECT_ID, OPENAI_PROJECT_SECRET_KEY)

# Define a function to check if the password is valid
def is_password_valid(password, is_admin=False):
    if is_admin:
        return password == ADMIN_PASS
    else:
        return password == ALLOW_USER_PASS

# Define the echo handler - it will be called when the bot receives a message
async def echo(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE) -> None:
    """
    This function would be added to the dispatcher as a handler for messages coming from the Bot API
    """

    # Print to console the message sent by the user
    print(f'({update.message.from_user.id}) {update.message.from_user.first_name} wrote {update.message.text}')
    
    is_group = update.message.chat.type == 'group' or update.message.chat.type == 'supergroup'
    
    # if is_group:
    #     AIBOT.add_message_to_group(update.message.text, update.message.chat_id, update.message.from_user.username)
    
    if (is_group and 'petete' in update.message.text.lower()):        
        response = AIBOT.chat(update.message.text, update.message.from_user.id, is_group=True, group_id=update.message.chat_id)
        response = f"@{update.message.from_user.username} {response}"
        await update.message.reply_text(response)

    elif not is_group:
        response = AIBOT.chat(update.message.text, update.message.from_user.id, is_group=False, group_id=update.message.chat_id)
        await update.message.reply_text(response)
    else:
        AIBOT.record_message(update.message.from_user.id, update.message.text, is_group, update.message.chat_id)
        
    nr = random.randint(0, 100) 
    if nr== 0 or nr == 11 or nr == 22 or nr == 33 or nr == 44 or nr == 55 or nr == 66 or nr == 77 or nr == 88 or nr == 99:
        await update.message.reply_text("El libro gordo te enseña, el libro gordo entretiene, y yo te digo contenta, hasta el mensaje que viene.")
        if is_group:
            await update.message.reply_text(f"@{update.message.from_user.username} recuerda si quieres hablar conmigo, mencioname y escribe 'petete'")

# Define the start handler - it will be called when the bot receives the /start command
async def start(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    """
    This function handles the /start command
    """

    print(f'({update.message.from_user.id}) {update.message.from_user.first_name} started the bot')
    await update.message.reply_text(AIBOT.chat("hola, Como puedes ayudarme?", update.message.from_user.id))
    # context.bot.send_message(
    #     update.message.chat_id,
    #     AIBOT.chat("hola, Como puedes ayudarme?", update.message.from_user.id)
    # )

# Define the clave handler - it will be called when the bot receives the /hablame command       
async def add_bot_user(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    """
    This function handles the /hablame command
    """
    
    user= { 'id': update.message.from_user.id, 'username': update.message.from_user.username, 'first_name': update.message.from_user.first_name }
    is_valid = False
    if not context.args:
        context.bot.send_message(
            update.message.chat_id,
            "Por favor, ingresa la clave para poder interactuar con el bot."
        )
        return
    elif len(context.args) > 1 and is_password_valid(context.args[0], is_admin=True):
        username = context.args[1]
        #user = get_telegram_user(username)
        is_valid = True       
        return
    elif is_password_valid(context.args[0]):
        is_valid = True
        
    if is_valid:
        if AIBOT.allow_user(user['id'], user['username'], user['first_name']):
            await update.message.reply_text(f"{update.message.from_user.first_name}, puedes interactuar con el bot.")
            # context.bot.send_message(
            #     update.message.chat_id,
            #     f"{update.message.from_user.first_name}, puedes interactuar con el bot."
            # )
    else:
        await update.message.reply_text("Clave incorrecta, no tienes permisos para interactuar con el bot.")
        # context.bot.send_message(
        #     update.message.chat_id,
        #     "Clave incorrecta, no tienes permisos para interactuar con el bot."
        # )

async def add_bot_group(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    """
    This function handles the /admin_hablanos command
    """
    
    password = context.args[0] if context.args else None
    if password and is_password_valid(password, is_admin=True):
        AIBOT.allow_group(update.message.chat_id)
        await update.message.reply_text("Grupo registrado.")
        # context.bot.send_message(
        #     update.message.chat_id,
        #     "Grupo registrado."
        # )
    else:
        await update.message.reply_text("Clave incorrecta, no tienes permisos para interactuar con el bot.")
        # context.bot.send_message(
        #     update.message.chat_id,
        #     "Clave incorrecta, no tienes permisos para interactuar con el bot."
        # )

# Define the show_all_bot_users handler - it will be called when the bot receives the /admin_bot_users command
async def show_all_bot_users(update: telegram.Update, context: telegram.ext.CallbackContext) -> None: 
    """
    This function handles the /admin_bot_users command
    """
    
    password = context.args[0] if context.args else None
    if password and is_password_valid(password, is_admin=True):
        await update.message.reply_text("Estos son los usuarios que pueden interactuar con el bot.")

        # context.bot.send_message(
        #     update.message.chat_id,
        #     "Estos son los usuarios que pueden interactuar con el bot."
        # )
        
        users = AIBOT.list_users()        
        for user in users:
            await update.message.reply_text(user)
            # context.bot.send_message(
            #     update.message.chat_id,
            #     user
            # )

# Define the show_all_bot_settings handler - it will be called when the bot receives the /admin_bot_settings command
async def show_all_bot_settings(update: telegram.Update, context: telegram.ext.CallbackContext) -> None: 
    """
    This function handles the /admin_bot_settings command
    """
    
    password = context.args[0]
    if is_password_valid(password, is_admin=True):
        await update.message.reply_text("Estos son los ajustes del bot.")
        # context.bot.send_message(
        #     update.message.chat_id,
        #     "Estos son los ajustes del bot."
        # )
        
        settings = AIBOT.list_settings()        
        for setting in settings:
            await update.message.reply_text(setting)

            # context.bot.send_message(
            #     update.message.chat_id,
            #     setting
            # )

async def show_bot_behavior(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:  
    """
    This function handles the /cual_es_la_personalidad command
    """
    is_group = update.message.chat.type == 'group' or update.message.chat.type == 'supergroup'
    if is_group:
        behavior = AIBOT.get_group_behavior(update.message.chat_id)
    else:
        behavior = AIBOT.get_user_behavior(update.message.from_user.id)
        
    await update.message.reply_text(behavior)

async def show_bot_model(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:  
    """
    This function handles the /cual_es_el_modelo command
    """
    is_group = update.message.chat.type == 'group' or update.message.chat.type == 'supergroup'
    if is_group:
        model = AIBOT.get_group_model(update.message.chat_id)
    else:
        model = AIBOT.get_user_model(update.message.from_user.id)
        
    await update.message.reply_text(model)

async def change_bot_behavior(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:    
    """
    This function handles the /cambia_personalidad command
    """
    
    behavior = context.args[0]
    AIBOT.update_user_behavior(update.message.from_user.id, behavior)
    await update.message.reply_text("Personalidad actualizada.")
    # context.bot.send_message(
    #     update.message.chat_id,
    #     "Personalidad actualizada."
    # )

async def change_bot_group_behavior(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:    
    """
    This function handles the /admin_cambia_personalidad command
    """
    
    password = context.args[0] if context.args else None
    if password and is_password_valid(password, is_admin=True):
        behavior = context.args[1]
        AIBOT.update_group_behavior(update.message.chat_id, behavior)
        await update.message.reply_text("Personalidad actualizada.")
        # context.bot.send_message(
        #     update.message.chat_id,
        #     "Personalidad actualizada."
        # )
    else:
        await update.message.reply_text("Clave incorrecta, no tienes permisos para interactuar con el bot.")
        # context.bot.send_message(
        #     update.message.chat_id,
        #     "Clave incorrecta, no tienes permisos para interactuar con el bot."
        # )

async def change_bot_model(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:    
    """
    This function handles the /cambia_modelo command
    """
    
    model = context.args[0]
    AIBOT.update_user_model(update.message.from_user.id, model)
    await update.message.reply_text("Modelo actualizado.")
    # context.bot.send_message(
    #     update.message.chat_id,
    #     "Modelo actualizado."
    # )  

async def change_bot_group__model(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:    
    """
    This function handles the /admin_cambia_modelo command
    """
    
    password = context.args[0] if context.args else None
    if password and is_password_valid(password, is_admin=True):
        model = context.args[1]
        AIBOT.update_group_model(update.message.chat_id, model)
        await update.message.reply_text("Modelo actualizado.")
        # context.bot.send_message(
        #     update.message.chat_id,
        #     "Modelo actualizado."
        # )
    else:
        await update.message.reply_text("Clave incorrecta, no tienes permisos para interactuar con el bot.")
        # context.bot.send_message(
        #     update.message.chat_id,
        #     "Clave incorrecta, no tienes permisos para interactuar con el bot."
        # )

async def get_messages(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE) -> None:    
    """
    This function handles the /mi_mensajes command
    """
    password = context.args[0] if context.args else None
    if password and is_password_valid(password, is_admin=True):
        messages = AIBOT.get_messages()
        
        for message in messages:
            await update.message.reply_text(message)
    else:        
        messages = AIBOT.get_messages(update.message.from_user.id)    
        for message in messages:
            await update.message.reply_text(message)


async def help_command(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")
    await update.message.reply_text("I need somebody!")
    messages = AIBOT.get_messages(update.message.from_user.id)    
    # for message in messages:
    #     await update.message.reply_text(message)
    # await update.message.reply_text(context.args[0])


# Define the main function to run the bot
def main() -> None:
    # Create the Application and pass it your bot's token.
    application = telegram.ext.Application.builder().token(BOT_TOKEN).build()
    
    # on different commands - answer in Telegram
    application.add_handler(telegram.ext.CommandHandler("admin_settings", show_all_bot_settings, has_args=True)) #hidden command
    application.add_handler(telegram.ext.CommandHandler("admin_bot_users", show_all_bot_users, has_args=True)) #hidden command
    application.add_handler(telegram.ext.CommandHandler('admin_hablanos', add_bot_group, has_args=True))
    application.add_handler(telegram.ext.CommandHandler('admin_cambia_personalidad', change_bot_group_behavior, has_args=True))
    application.add_handler(telegram.ext.CommandHandler('admin_cambia_modelo', change_bot_group__model, has_args=True))

    application.add_handler(telegram.ext.CommandHandler('hablame', add_bot_user, has_args=True))
    application.add_handler(telegram.ext.CommandHandler('cual_es_la_personalidad', show_bot_behavior))
    application.add_handler(telegram.ext.CommandHandler('cual_es_el_modelo', show_bot_model))
    
    # application.add_handler(telegram.ext.CommandHandler('cual_es_la_personalidad', show_bot_behavior))
    # application.add_handler(telegram.ext.CommandHandler('cambia_personalidad', change_bot_behavior))
    # application.add_handler(telegram.ext.CommandHandler('cambia_modelo', change_bot_model))
    # application.add_handler(telegram.ext.CommandHandler('mi_mensajes', get_messages, has_args=True))
    
    # Echo any message that is not a command
    application.add_handler(telegram.ext.MessageHandler(~telegram.ext.filters.COMMAND, echo))
    
    
    application.add_handler(telegram.ext.CommandHandler("help", help_command))
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)


if __name__ == '__main__':
    main()