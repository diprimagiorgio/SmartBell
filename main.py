
from flask import Flask, render_template, Response, request
from camera import VideoCamera
from message import settingUp, send_door_message, send_door_photo
import time
import os

app = Flask(__name__)
#app = Flask(__name__, template_folder='/var/www/html/templates')

#background process happening without any refreshing

update = None

@app.route('/')
def move():
    return render_template('index.html')


def gen(camera):
    while True:
        frame, face_names = camera.get_frame()
        if update:
            #send_door_message(update=update, face_names=face_names)
            send_door_photo(update, face_names, frame)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')




@app.route("/telegram")
def telegram():
    global update
    update = settingUp()
    return f"Send a message to the bot with written /start\n{update}"

if __name__ == '__main__':
    app.run(threaded=True)
