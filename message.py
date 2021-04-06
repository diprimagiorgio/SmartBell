
"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from datetime import datetime
from typing import List

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

last_visit = []
user = None

# Define a few command handlers. These usually take the two arguments update and
# context.
#------------------------------------------------- COMMANDS
def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    global user
    user = update.effective_user
    update.message.reply_markdown_v2(
        f'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')



#------------------------------------------------- SEND UPDATE

#the function check if time delta is passed form last visit and update the last visit
def rw_last_visit(now, delta : int, person_index: int) -> bool:
    time_delta = now - last_visit[person_index]
    if time_delta.total_seconds() > delta:
        last_visit[person_index] = now
        return True
    else:
        return False
def send_door_message(updater: Updater, face_names: List) -> None:
    if not user:
        return
    """Write how is at the door, only if is not already happened too soon"""
    for name in face_names:
        if name != "Unknown":
            if rw_last_visit(datetime.now(), 20, 0):
                updater.bot.send_message(chat_id=user.id, text=f'Hey there is {name} at the door!')
def send_door_photo(updater: Updater, face_names:List, photo) -> None:
    if not user:
        return
    #get names
    names = ""
    for name in face_names:
        names += name +", "
    #update last visit
    if rw_last_visit(datetime.now(), 20, 0) and names != "" :
        updater.bot.send_photo(chat_id=user.id, photo=photo, caption=f'Hey there is {names} at the door!')
# maybe i should use a var last picture, it's posssible that  just one of the person is recognise and the others in another call of the function

#------------------------------------------------- INITIALIZER

def settingUp() -> Update:
    """Start the bot."""
    global last_visit
    #TODO  I have to assign a slot for each person
    last_visit.append(datetime.now())

    # Create the Updater and pass it your bot's token.
    updater = Updater("1762984493:AAHHm6S4qCJjqWLi4aNz5Qq8SIIlOJM798A")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    # Start the Bot
    updater.start_polling()

    return updater

