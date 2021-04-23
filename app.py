#https://stackoverflow.com/questions/57748375/unable-to-install-dlib-from-dockerfile-on-raspberry-pi
# https://docs.docker.com/language/python/run-containers/
# https://github.com/Ellerbach/Raspberry-IoTEdge
from flask import Flask, render_template, Response, request
from smartbell import SmartBell
from smartBell_telegram_bot import telegram_init, send_door_message, send_door_photo
from mqtt_message import MyMQTT


app = Flask(__name__)
 #I can remove it if i'm able to put in main
smart_bell = None


@app.route('/')
def move():
    return render_template('index.html')

def gen(smart_bell: SmartBell):
    while True:
        frame, face_names = smart_bell.get_frame()
        
        if face_names:

            MyMQTT.send(topic="doorbell", message=face_names)

            #send_door_message(update=update, face_names=face_names)
            send_door_photo(face_names, frame)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(smart_bell),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/init")
def init():
    # for camera
    global smart_bell
    smart_bell = SmartBell()
    # for telegram
    telegram_init(smart_bell)
    return "init done"


"""if __name__ == '__main__':
    # for camera
    global smart_bell
    smart_bell = SmartBell()
    # for telegram
    telegram_init(smart_bell)
    app.run(debug=True)
"""