from flask_socketio import SocketIO
import socketio
import cv2
import base64
from time import sleep

# Initialize SocketIO Client
sio = socketio.Client()
cap = cv2.VideoCapture(0)  # Open webcam

@sio.event
def connect():
    print("[INFO] Connected to server")
    send_data()  # Start sending frames once connected

@sio.event
def disconnect():
    print("[INFO] Disconnected from server")

def send_data():
    while cap.isOpened():
        ret, img = cap.read()
        if ret:
            img = cv2.resize(img, (640, 480))  # Resize for performance
            _, buffer = cv2.imencode('.jpg', img)
            frame = base64.b64encode(buffer).decode("utf-8")  # Proper base64 encoding
            sio.emit('send', frame)  # Send frame to server
            sleep(0.03)  # Adjust for real-time streaming
        else:
            break

if __name__ == '__main__':
    try:
        sio.connect('http://localhost:5000')  # Update with actual server IP if needed
        sio.wait()
    except Exception as e:
        print(f"[ERROR] {e}")
