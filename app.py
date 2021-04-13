
from flask import Flask, render_template, Response, request
from smartbell import SmartBell
from message import telegram_init, send_door_message, send_door_photo, set_smart_bell
import paho.mqtt.client as mqtt #import the client1


app = Flask(__name__)
update = None
smart_bell = None
client = None
@app.route('/')
def move():
    return render_template('index.html')


def gen(smart_bell: SmartBell):
    while True:
        frame, face_names = smart_bell.get_frame()
        if update and face_names and client:
            msg = ""
            for name in face_names:
                msg += " , "  + name
            # send mqtt message
            client.publish("doorbell", msg)

            #send_door_message(update=update, face_names=face_names)
            send_door_photo(update, face_names, frame)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(smart_bell),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
#---------------------mqtt shit



@app.route("/init")
def init():
    global  update, smart_bell, client


    # for telegram
    update = telegram_init()

    # for camera
    smart_bell = SmartBell()

    set_smart_bell(smart_bell)


    # mqtt

    client = mqtt.Client()

    client.connect("localhost", 1883, 60)

    return "Init done"

#if __name__ == '__main__':
#    app.run(threaded=True)
