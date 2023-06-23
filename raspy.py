import cv2
import numpy as np
import socket
import threading
from RPi import GPIO

# Server configuration
SERVER_IP = ''  # Raspberry Pi IP address
SERVER_PORT = 8000
BUZZER_PIN = 18  # GPIO pin for the buzzer

# Initialize the camera
camera = cv2.VideoCapture(0)  # Use 0 for the first USB camera

# Set the video width and height (reduce resolution)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# Set the frame rate (reduce frame rate)
camera.set(cv2.CAP_PROP_FPS, 10)

# Initialize GPIO for buzzer
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Global buzzer state
buzzer_state = False

def toggle_buzzer(state):
    global buzzer_state
    buzzer_state = state
    GPIO.output(BUZZER_PIN, buzzer_state)

def handle_client_commands(client):
    while True:
        try:
            # Listen for commands from the client
            command = client.recv(1024)
            if command == b'start buzzer':
                toggle_buzzer(True)
            elif command == b'stop buzzer':
                toggle_buzzer(False)
        except OSError:
            print("Client disconnected.")
            break


def server_function():
    global camera
    while True:
        print('Waiting for client connection...')
        client_socket, client_address = server_socket.accept()
        print('Client connected:', client_address)

        # Initialize the camera when a client connects
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        camera.set(cv2.CAP_PROP_FPS, 10)
        
        # Start a new thread to handle client commands
        threading.Thread(target=handle_client_commands, args=(client_socket,)).start()

        try:
            while True:
                # Read a frame from the camera
                ret, frame = camera.read()

                # Check if frame was read correctly
                if ret:
                    # Convert the frame to JPEG format
                    ret, buffer = cv2.imencode('.jpg', frame)

                    # If frame was not encoded correctly, skip this iteration
                    if not ret:
                        continue

                    # Convert the image buffer to a byte array
                    data = buffer.tobytes()

                    # Send the data size to the client
                    size = len(data)
                    client_socket.sendall(size.to_bytes(8, 'big'))

                    # Send the data to the client
                    client_socket.sendall(data)
                else:
                    print("Failed to capture frame")

        except (BrokenPipeError, KeyboardInterrupt):
            # Release the camera and close the server socket
            camera.release()
            client_socket.close()
            print("Client disconnected, restarting server...")

# Initialize the camera
camera = None

# Create a socket and bind to the server address
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(1)

server_function()

# Close the server socket when done
server_socket.close()
