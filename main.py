
from flask import Flask, render_template, Response, request
from camera import VideoCamera
import telepot
from telepot.loop import MessageLoop
import time
import os

app = Flask(__name__)
#app = Flask(__name__, template_folder='/var/www/html/templates')

#background process happening without any refreshing

telegramID = 0
bot = telepot.Bot('1762984493:AAHHm6S4qCJjqWLi4aNz5Qq8SIIlOJM798A')


@app.route('/')
def move():
    return render_template('index.html')


def gen(camera):
    while True:
        #frame = camera.get_frame()
        frame = camera.get_frame_and_message(telegramID, bot)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'text' and msg['text'] == '/start':
            bot.sendMessage(chat_id, 'Hello')
            global telegramID
            telegramID = chat_id

@app.route("/telegram")
def telegram():
    MessageLoop(bot, handle).run_as_thread()
    return "Send a message to the bot with written /start\n{tID}".format(tID = telegramID)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
