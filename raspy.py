import cv2
import numpy as np
import socket

# Server configuration
SERVER_IP = '192.168.1.179'  # Raspberry Pi IP address
SERVER_PORT = 8000

# Initialize the camera
camera = cv2.VideoCapture(0)  # Use 0 for the first USB camera

# Set the video width and height (reduce resolution)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# Set the frame rate (reduce frame rate)
camera.set(cv2.CAP_PROP_FPS, 10)

# Create a socket and bind to the server address
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(1)

print('Waiting for client connection...')
client_socket, client_address = server_socket.accept()
print('Client connected:', client_address)

try:
    while True:
        # Read a frame from the camera
        ret, frame = camera.read()

        # Convert the frame to JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)

        # Convert the image buffer to a byte array
        data = buffer.tobytes()

        # Send the data size to the client
        size = len(data)
        client_socket.sendall(size.to_bytes(8, 'big'))

        # Send the data to the client
        client_socket.sendall(data)

except KeyboardInterrupt:
    # Release the camera and close the server socket
    camera.release()
    server_socket.close()
