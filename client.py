import cv2
import numpy as np
import socket
from tkinter import *
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import torch
import CowDetection

# Server configuration
SERVER_IP = '192.168.1.179'  # Replace with Raspberry Pi IP address
SERVER_PORT = 8000

# Variables for toggling features
stream_flag = True
detection_flag = False
buzzer_flag = False
buzzer_activated = True


# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='person.pt')  # Replace with your model path



def toggle_stream():
    global stream_flag
    stream_flag = not stream_flag
    write2log(f"Stream {'started' if stream_flag else 'stopped'}")

def toggle_detection():
    global detection_flag
    detection_flag = not detection_flag
    client_socket.send(b'start detection' if detection_flag else b'stop detection')
    write2log(f"Detection {'started' if detection_flag else 'stopped'}")
    #updateDetectionandBuzzerStatus(buzzer_flag)

def toggle_buzzer():
    global buzzer_flag
    buzzer_flag = not buzzer_flag
    client_socket.send(b'start buzzer' if buzzer_flag else b'stop buzzer')
    write2log(f"Buzzer {'started' if buzzer_flag else 'stopped'}")
    updateDetectionandBuzzerStatus(buzzer=buzzer_flag)


def toggle_buzzer_button():
    global buzzer_activated
    buzzer_activated = not buzzer_activated
    write2log(f"Buzzer {'Activated' if buzzer_activated else 'Deactivated'}")





def write2log(log):
    log_terminal.insert(END, f"{log}\n")
    log_terminal.see(END)  # Scroll to the bottom

def updateDetectionandBuzzerStatus(detection=None, buzzer=None):
    if detection != None:
        detection_label['text'] = f"Total Cows Detected: {detection}"
    if buzzer != None:
        buzzer_label['text'] = f"Buzzer state: {'ON' if buzzer else 'OFF'}"

# Create a tkinter window
root = Tk()
root.title("INTRUSION DETECTION AND REPELLANT SYSTEM")
root.geometry("600x700")  # Adjust to the resolution of the video stream or the desired window size
root.configure(bg='black')
root.resizable(False, False)  # This will make the window size fixed

# Set theme
style = ttk.Style()
style.theme_use('clam')
style.configure('.', font=('Helvetica', 12))
style.configure('TFrame', background='black')
style.configure('TButton', background='blue', foreground='white')
style.configure('TLabel', background='black', foreground='white')

# Create a label for the title
title_label = ttk.Label(root, text="AYEGBUSI OSEYEMI PRECIOUS (160408049)", anchor=CENTER)
title_label.pack(side=TOP, padx=10, pady=10)

# Create a label for displaying the video stream
video_frame = ttk.Frame(root, width=640, height=480)
video_frame.pack(side=TOP, padx=10, pady=10)
video_label = Label(video_frame)
video_label.pack()

# Create log terminal
log_frame = ttk.Frame(root)
log_frame.pack(side=TOP, padx=10, pady=10)
log_label = ttk.Label(log_frame, text='Log Terminal:', anchor=W)
log_label.pack(fill=X)
log_terminal = scrolledtext.ScrolledText(log_frame, bg='black', fg='white', height=15)
log_terminal.pack(fill=X)


# Create detection and buzzer status labels
status_frame = ttk.Frame(root)
status_frame.pack(side=TOP, padx=10, pady=10)
ttk.Label(status_frame, text='Status:', anchor=W).pack(fill=X)
detection_label = ttk.Label(status_frame, text='Total Cows Detected: 0')
buzzer_label = ttk.Label(status_frame, text='Buzzer state: OFF')
detection_label.pack(fill=X)
buzzer_label.pack(fill=X)

# Create a default image when no data is received
default_img = ImageTk.PhotoImage(Image.new('RGB', (640, 480)))  # adjust the size to your needs




# Create buttons
button_frame = ttk.Frame(root)
button_frame.pack(side=TOP, fill=X)
ttk.Button(button_frame, text="Toggle Stream", command=toggle_stream).pack(side=LEFT, fill=X, expand=True)
ttk.Button(button_frame, text="Toggle Detection", command=toggle_detection).pack(side=LEFT, fill=X, expand=True)
ttk.Button(button_frame, text="Toggle Buzzer", command=toggle_buzzer_button).pack(side=LEFT, fill=X, expand=True)

# Create a socket and connect to the server
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
except socket.error:
    print("Failed to connect to the server.")
    client_socket = None

def update_image():
    # If the stream is not supposed to be active, don't update the image
    if not stream_flag:
        video_label.after(10, update_image)
        if buzzer_flag == True:
            toggle_buzzer()
        return

    if client_socket is not None:
        try:
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

            if detection_flag:
                results = CowDetection.cow(image)
                print(results)

                # Annotate the image with the detections and count the cows
                cow_count = len(results["bb"])
                image = CowDetection.plot_many_box(image, results["bb"])
                # Update the cow count
                updateDetectionandBuzzerStatus(detection=cow_count)
                if buzzer_activated:
                    if cow_count > 0 and buzzer_flag == False:
                        toggle_buzzer()
                    elif cow_count == 0 and buzzer_flag == True:
                        toggle_buzzer()
                elif buzzer_activated == False and buzzer_flag==True:
                    toggle_buzzer()

            elif detection_flag == False and buzzer_flag==True:
                toggle_buzzer()


                    


            # Convert the image color from BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Convert the Image object into a TkPhoto object
            im = Image.fromarray(image)
            imgtk = ImageTk.PhotoImage(image=im) 
        except Exception as e:
            print(f"Error receiving data: {e}")
            imgtk = default_img
    else:
        imgtk = default_img

    # Update the image in the label
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    # Refresh the image in the label every 10 milliseconds
    video_label.after(10, update_image)

update_image()

root.mainloop()

# Close the client socket
if client_socket is not None:
    client_socket.close()
