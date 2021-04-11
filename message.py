
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
last_visit = {} # last time that we have sent a message for that person
user = None
#------------------------------------------------- INITIALIZER

def telegram_init() -> Update:
    """Start the bot."""

    # Create the Updater and pass it your bot's token.
    updater = Updater("1762984493:AAHHm6S4qCJjqWLi4aNz5Qq8SIIlOJM798A")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    #I'd like to simulate a conversation after the command
    #dispatcher.add_handler(CommandHandler("newFace", new_face_command))

    dispatcher.add_handler(MessageHandler(Filters.photo, image_handler))

    # Start the Bot
    updater.start_polling()

    return updater

# Define a few command handlers. These usually take the two arguments update and
# context.
#------------------------------------------------- COMMANDS
def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    global user
    user = update.effective_user
    update.message.reply_markdown_v2(
        f'Hi {user.mention_markdown_v2()}\!'
    )
    logger.info(f'{user} si è loggato ')



def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def new_face_command(update: Update, _: CallbackContext) -> None:
    #file = bot.getFile(update.message.photo[-1].file_id)
    print(update.message.photo.file_id)
#------------------------------------------------- RECEIVE PHOTO
smart_bell = None

#TODO  fix this is orrible, maybe i should do a class
def set_smart_bell(sm_bell):
    global smart_bell
    smart_bell = sm_bell
def image_handler(update: Update, _: CallbackContext) -> None:
    global smart_bell
    photo_file = update.message.photo[-1].get_file()
    photo_file.download(f'profiles/{update.message.caption}.jpg')
    logger.info("Photo of %s: %s", user.first_name, f'{update.message.caption}.jpg')
    #now someone have to add to the list of people
    if smart_bell.add_person(f'{update.message.caption}.jpg') :
        update.message.reply_text(
            'Gorgeous! Image uploaded'
        )
    else:
        update.message.reply_text(
            'Error I\'m not able to find the face in the image, can you send a new one?'
        )


#------------------------------------------------- SEND UPDATE

#the function checks if time delta is passed form last visit and update the last visit
def rw_last_visit(now, delta : int, person: str) -> bool:
    # if never sent or sent more than delta seconds ago
    if last_visit.get(person) is None or (now - last_visit.get(person)).total_seconds() > delta:
        last_visit.update({person: now})
        return True
    else:
        return False
def send_door_message(updater: Updater, face_names: List) -> None:
    if not user:
        return
    """Write who is at the door, only if is some time has passed from the last message"""
    time_delta = 20
    for name in face_names:
        if name != "Unknown":
            if rw_last_visit(datetime.now(), time_delta, name):
                updater.bot.send_message(chat_id=user.id, text=f'Hey there is {name} at the door!')

def send_door_photo(updater: Updater, face_names:List, photo) -> None:
    if not user:
        return
    names = ""
    #get names
    #for name in face_names:
    #    names += name +", "
    ##update last visit, if one of the person was not present i should send a message
    #if rw_last_visit(datetime.now(), 20, 0) and names != "" :
    #    updater.bot.send_photo(chat_id=user.id, photo=photo, caption=f'Hey there is {names} at the door!')
    ## maybe i should use a var last picture, it's posssible that  just one of the person is recognise and the others in another call of the function
    time_delta = 20
    for name in face_names:
        if name != "Unknown":
            if rw_last_visit(datetime.now(), time_delta, name):
                updater.bot.send_photo(chat_id=user.id, photo=photo, caption=f'Hey there is {name} at the door!')


