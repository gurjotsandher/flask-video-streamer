from flask import Flask, render_template
import eventlet
import eventlet.wsgi
import socketio
import cv2  # OpenCV for video capture
import base64

# Flask & SocketIO Setup
sio = socketio.Server(cors_allowed_origins="*")
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

clients = {}

@app.route('/')
def index():
    return render_template('video-stream.html')

@sio.event
def connect(sid, environ):
    print(f"[INFO] Client {sid} connected")
    clients[sid] = True  # Mark client as active
    sio.emit('message', {'data': 'Connected'}, room=sid)

@sio.event
def check(sid, data):
    print(f"[INFO] Received 'check' event from {sid}: {data}")

@sio.event
def disconnect(sid):
    print(f"[INFO] Client {sid} disconnected")
    if sid in clients:
        del clients[sid]

# Video Streaming Function
def send_video():
    cap = cv2.VideoCapture(0)  # 0 for webcam, or use video file path

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to capture frame")
            break

        _, buffer = cv2.imencode('.jpg', frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        # Send frame to all connected clients
        for sid in list(clients.keys()):
            sio.emit('image', img_base64, room=sid)

        eventlet.sleep(0.05)  # Adjust frame rate (Lower is faster)

    cap.release()

# Start Video Stream in Background
eventlet.spawn(send_video)

if __name__ == '__main__':
    print("[INFO] Flask-SocketIO Server Running on Port 5000...")
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
