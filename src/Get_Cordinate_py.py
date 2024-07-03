import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageCoordinatePicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Coordinate Picker")

        self.canvas = tk.Canvas(root)
        self.canvas.pack()

        self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack()

        self.coordinates_label = tk.Label(root, text="Coordinates: ")
        self.coordinates_label.pack()

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        self.image = Image.open(file_path)
        self.photo_image = ImageTk.PhotoImage(self.image)
        self.canvas.config(width=self.photo_image.width(), height=self.photo_image.height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)

        self.canvas.bind("<Button-1>", self.get_coordinates)

    def get_coordinates(self, event):
        x, y = event.x, event.y
        self.coordinates_label.config(text=f"Coordinates: ({x}, {y})")
        print(f"Coordinates: ({x}, {y})")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCoordinatePicker(root)
    root.mainloop()
