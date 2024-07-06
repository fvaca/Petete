import os
import logging
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

def echo(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    """
    This function would be added to the dispatcher as a handler for messages coming from the Bot API
    """

    # Print to console the message sent by the user
    print(f'({update.message.from_user.id}) {update.message.from_user.first_name} wrote {update.message.text}')
    
    # Send a message to the user from the bot
    if update.message.text:
        context.bot.send_message(
            update.message.chat_id,
            AIBOT.chat(update.message.text, update.message.from_user)
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

# Define the clave handler - it will be called when the bot receives the /clave command       
def clave(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    """
    This function handles the /clave command
    """
    
    clave = update.message.text.replace('/clave ', '')
    
    if update.message.text and clave == ALLOW_USER_PASS:
        if AIBOT.allow_user(update.message.from_user):
            context.bot.send_message(
                update.message.chat_id,
                "Bienvenido, puedes interactuar con el bot."
            )
    else:
        context.bot.send_message(
            update.message.chat_id,
            "Clave incorrecta, no tienes permisos para interactuar con el bot."
        )

# Define the menu handler
def menu(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    """
    This handler sends a menu with the inline buttons we pre-assigned above
    """

    context.bot.send_message(
        update.message.from_user.id,
        FIRST_MENU,
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=FIRST_MENU_MARKUP
    )


def button_tap(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    """
    This handler processes the inline buttons on the menu
    """

    data = update.callback_query.data
    text = ''
    markup = None

    if data == NEXT_BUTTON:
        text = SECOND_MENU
        markup = SECOND_MENU_MARKUP
    elif data == BACK_BUTTON:
        text = FIRST_MENU
        markup = FIRST_MENU_MARKUP

    # Close the query to end the client-side loading animation
    update.callback_query.answer()

    # Update message content with corresponding menu section
    update.callback_query.message.edit_text(
        text,
        telegram.ParseMode.HTML,
        reply_markup=markup
    )


def main() -> None:
    telegram_updater = telegram.ext.Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    # Then, we register each handler and the conditions the update must meet to trigger it
    dispatcher = telegram_updater.dispatcher

    # Register commands
    dispatcher.add_handler(telegram.ext.CommandHandler("scream", start))
    dispatcher.add_handler(telegram.ext.CommandHandler("menu", menu))
    dispatcher.add_handler(telegram.ext.CommandHandler("clave", clave))
    

    # Register handler for inline buttons
    dispatcher.add_handler(telegram.ext.CallbackQueryHandler(button_tap))

    # Echo any message that is not a command
    dispatcher.add_handler(telegram.ext.MessageHandler(~telegram.ext.Filters.command, echo))

    # Start the Bot
    telegram_updater.start_polling()

    # Run the bot until you press Ctrl-C
    telegram_updater.idle()


if __name__ == '__main__':
    main()