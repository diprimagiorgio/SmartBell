
"""
Bot to menage the smart bell.
The bot is able to
    insert a person in the smart bell, i this way the smart bell is able to recognize her/him
    remove person from the smart bell
    see a list of all the person present in the db
    recive a message every time that someone is at the door
"""
#TODO I'd like to have the possibility of setting th etime delta for the message and a variable that says if we are interestin reciving the messages
import logging

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler
from datetime import datetime
from typing import List
from smartbell import SmartBell

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
ADD_NAME, ADD_PHOTO = range(2)

logger = logging.getLogger(__name__)
last_message = {} # last time that we have sent a message for that person
user = None

updater: Updater = None
smart_bell : SmartBell = None

#------------------------------------------------- INITIALIZER

def telegram_init(sm_bell: SmartBell):
    global updater, smart_bell
    """Start the bot."""
    if smart_bell or updater :
        return
    smart_bell = sm_bell

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

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(add_handler)

    dispatcher.add_handler(CommandHandler("list", list_cmd))
    dispatcher.add_handler(CallbackQueryHandler(remove_callback))


    # Start the Bot
    updater.start_polling()


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
    #TODO message of functionality
    update.message.reply_text('I have this this and this functionality')

#------------------------------------------------- ADD COMMAND

add_name = None # name of the person to add

# explain the process to the user
def add_cmd(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s is adding a new picture ", user.first_name)
    update.message.reply_text(
        'Introduce me a friend of you! Please send me her/his name, '
        'so I know how to call her/him.',
        reply_markup=ReplyKeyboardRemove(),
    )
    return ADD_NAME

# save the mane of the person to add_name
def add_name_handler(update: Update, _: CallbackContext) -> int:
    global add_name
    user = update.message.from_user
    add_name = update.message.text
    logger.info("Name of the friend of of %s: %s", user.first_name, add_name)
    update.message.reply_text(f'Thank you! Now I need also a picture to know how does {add_name} look like.')
    return ADD_PHOTO

# Save the picture in the profiles dir and call the function of the Smart bell to adding to the known person
def add_image_handler(update: Update, _: CallbackContext) -> int:
    global smart_bell
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download(f'profiles/{add_name}.jpg')
    logger.info("Photo of %s: %s", user.first_name, f'{add_name}.jpg')
    # check if the image is ok and in case the person is  added to the known person
    if smart_bell.add_person(f'{add_name}.jpg'):
        update.message.reply_text(
            f'Gorgeous! Image of {add_name} uploaded. Now next time that {add_name} is a the door I will recognise her/him'
        )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            'Error I\'m not able to find the face in the image, can you send a new one?'
        )
        return ADD_PHOTO
#------------------------------------------------- LIST COMMAND
#TODO i'd like to have two different handler one to show the picture and one to remove the person

# list all the known people and provide the possibility to remove by pressing on the name or the cross symbol
def list_cmd(update: Update, _: CallbackContext) -> int:
    global smart_bell
    buttons = []

    for name in smart_bell.get_known_person:
        buttons.append( [ InlineKeyboardButton(text=name,
                                callback_data=f"{name}"),
                          InlineKeyboardButton(text= u"\u274C",
                                callback_data=f"{name}")
                          ])

    user = update.message.from_user
    logger.info("User %s has asked to receive the list ", user.first_name)
    update.message.reply_text( "Choose the user to remove or press the name to show the picture saved", reply_markup = InlineKeyboardMarkup(buttons) )
    return 1

# remove the user in the query from the files and from the list of the known person
def remove_callback(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    if smart_bell.remove_person(query.data):
        query.edit_message_text(text=f"Removed with success : {query.data}")
    else:
        query.edit_message_text(text=f"Error I was not able to remove the person : {query.data}")


#------------------------------------------------- SEND UPDATE

#the function checks if time delta is passed form last visit and update the last visit
# Ture if I should send the message and, in that case I have uploaded the last visit
# false no needed to send the message and I have not uploaded the last messag/visit
def rw_last_visit(now, delta : int, person: str) -> bool:
    # if never sent or sent more than delta seconds ago
    if last_message.get(person) is None or (now - last_message.get(person)).total_seconds() > delta:
        last_message.update({person: now})
        return True
    else:
        return False
# check if in the list there is a person that was not at the door in the last time delta I can send a  message otherwise I have already
#        send the message to the user and I can skip it
def check_message_needed(now: datetime, time_delta: int, list_names: List[str] ) -> bool:
    for name in list_names:
        if name != "Unknown" and rw_last_visit(now, time_delta, name):
            return True
    return False

# send to the user a message with the names of the people at the door
def send_door_message( face_names: List) -> None:
    if not user:
        return
    global updater
    # Write who is at the door, only if is some time has passed from the last message
    if check_message_needed(datetime.now(), time_delta=20, list_names=face_names):
        str_msg = SmartBell.get_names_list(list_names=face_names)
        updater.bot.send_message(chat_id=user.id, text=f'Hey there is {str_msg} at the door!')

def send_door_photo( face_names:List, photo) -> None:

    if not user:
        return
    global updater
    if check_message_needed(datetime.now(), time_delta=20, list_names=face_names):
        str_msg = SmartBell.get_names_list(list_names=face_names)
        updater.bot.send_photo(chat_id=user.id, photo=photo, caption=f'Hey there is {str_msg} at the door!')


