import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
import cv2

# Function to update the frame
def update_frame():
    ret, frame = cap.read()
    if ret:
        # Flip the frame horizontally and vertically
        frame = cv2.flip(frame, -1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
    else:
        print("Failed to capture image")
    video_label.after(10, update_frame)

# Create the main window
root = tk.Tk()
root.title("Camera Feed")

# Create a Label to display the video
video_label = Label(root)
video_label.grid(row=0, column=0, padx=10, pady=10)

# Start capturing video from the camera
cap = cv2.VideoCapture(0)  # Use the first camera device

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open video device")
else:
    # Set camera parameters if needed
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1000)
    cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.2)
    cap.set(cv2.CAP_PROP_CONTRAST, 0.5)
    cap.set(cv2.CAP_PROP_SATURATION, 0.5)
    cap.set(cv2.CAP_PROP_GAIN, 0.1)

    # Start the frame update
    update_frame()

    # Start the Tkinter main loop
    root.mainloop()

# Release the video capture object
cap.release()
