
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

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from datetime import datetime
from typing import List


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
ADD_NAME, ADD_PHOTO = range(2)

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

    # Add conversation handler to add a new face to the know person of the bell
    add_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_cmd)],
        states={
            ADD_NAME:[MessageHandler(Filters.text & ~Filters.command, add_name_handler )],
            ADD_PHOTO: [MessageHandler(Filters.photo, add_image_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # List all the know person of the bell
    """conv_handler = ConversationHandler(
        entry_points=[CommandHandler('list', add_cmd)],
        states={
    },
    fallbacks = [CommandHandler('cancel', cancel)],
    )"""

    # Remove one person from the know one of the database
    """remove_handler = ConversationHandler(
        entry_points=[CommandHandler('remove', rm_cmd)],
        states={
            SELECT : 
            SURE:
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )"""

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(add_handler)
    #I'd like to simulate a conversation after the command
    #dispatcher.add_handler(CommandHandler("newFace", new_face_command))

    #dispatcher.add_handler(MessageHandler(Filters.photo, image_handler))

    # Start the Bot
    updater.start_polling()

    return updater

# Define a few command handlers. These usually take the two arguments update and
# context.
#------------------------------------------------- GENERAL COMMANDS
cmd_keyboard = [['/add', '/list', '/remove', '/help']]

def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    global user
    user = update.effective_user
    update.message.reply_markdown_v2(
        f'Hi {user.mention_markdown_v2()}\!'
    )
    logger.info(f'{user} si è loggato ')
    update.message.reply_text(
        'Hi! My name is The Smart Bell Bot. I will help you to see who is at your door, without needing to move from your sofa. '
        'You need to send me the img of the person that i want to recognise with the command \ add .\n\n'
        'to have more info you can always ask me with \ help command',
        reply_markup=ReplyKeyboardMarkup(cmd_keyboard),
    )

def cancel(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def new_face_command(update: Update, _: CallbackContext) -> None:
    #file = bot.getFile(update.message.photo[-1].file_id)
    print(update.message.photo.file_id)
#------------------------------------------------- ADD COMMAND
def add_cmd(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s is adding a new picture ", user.first_name)
    update.message.reply_text(
        'Introduce me a friend of you! Please send me her/his name, '
        'so I know how to call her/him.',
        reply_markup=ReplyKeyboardRemove(),
    )

    return ADD_NAME
add_name = None
def add_image_handler(update: Update, _: CallbackContext) -> int:
    global smart_bell
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download(f'profiles/{add_name}.jpg')
    logger.info("Photo of %s: %s", user.first_name, f'{add_name}.jpg')
    # now someone have to add to the list of people
    if smart_bell.add_person(f'{add_name}.jpg'):
        update.message.reply_text(
            f'Gorgeous! Image of {add_name} uploaded',
            reply_markup=ReplyKeyboardRemove(),

        )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            'Error I\'m not able to find the face in the image, can you send a new one?'
        )
        return ADD_PHOTO

def add_name_handler(update: Update, _: CallbackContext) -> int:
    global add_name
    user = update.message.from_user
    add_name = update.message.text
    logger.info("Name of the friend of of %s: %s", user.first_name, add_name)
    update.message.reply_text(f'Thank you! Now I need also a picture to know how does {add_name} look like.')
    return ADD_PHOTO


smart_bell = None

#TODO  fix this is orrible, maybe i should do a class
def set_smart_bell(sm_bell):
    global smart_bell
    smart_bell = sm_bell
#def image_handler(update: Update, _: CallbackContext) -> None:


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


