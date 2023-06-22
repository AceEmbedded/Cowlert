import cv2
import numpy as np
import socket

# Server configuration
SERVER_IP = '192.168.1.179'  # Replace with Raspberry Pi IP address
SERVER_PORT = 9000

# Create a socket and connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# Create an OpenCV window to display the live stream
cv2.namedWindow('Live Stream', cv2.WINDOW_NORMAL)

try:
    while True:
        # Receive the data size from the server
        size_data = client_socket.recv(8)
        size = int.from_bytes(size_data, 'big')

        # Receive the data from the server
        data = b''
        while len(data) < size:
            packet = client_socket.recv(size - len(data))
            if not packet:
                break
            data += packet

        # Convert the received data to an image
        image = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)

        # Display the image in the OpenCV window
        cv2.imshow('Live Stream', image)

        # Check for 'q' key to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass

# Close the OpenCV window and the client socket
cv2.destroyAllWindows()
client_socket.close()
