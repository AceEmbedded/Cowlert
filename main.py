from flask import Flask, render_template, request, Response
# import RPi.GPIO as GPIO
from flask_basicauth import BasicAuth
import cv2

app = Flask(__name__)

# Basic authentication
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'password'

basic_auth = BasicAuth(app)

# # Set the GPIO mode
# GPIO.setmode(GPIO.BCM)
# BUZZER_PIN = 18  # change to your actual pin
# GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Initialize the VideoCapture object
cap = cv2.VideoCapture(0)

@app.route('/')
@basic_auth.required
def index():
    return render_template('index.html')

# @app.route('/toggle-buzzer', methods=['POST'])
# @basic_auth.required
# def toggle_buzzer():
#     state = GPIO.input(BUZZER_PIN)
#     GPIO.output(BUZZER_PIN, not state)
#     return '', 204

@app.route('/toggle-cow-detection', methods=['POST'])
@basic_auth.required
def toggle_cow_detection():
    # You'll need to implement the logic here to start or stop the cow detection
    pass

@app.route('/toggle-camera', methods=['POST'])
@basic_auth.required
def toggle_camera():
    # You'll need to implement the logic here to start or stop the camera
    pass

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
