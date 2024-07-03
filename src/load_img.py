import tkinter as tk
import time
from tkinter import ttk, messagebox, Scrollbar
from PIL import Image, ImageTk
import threading
import asyncio
from grbl_controller import GRBLController  # Importing the GRBLController class from grbl_controller.py
import json
import requests
from Object.Coordinates import Coordinates
from Object.Coordinates import serialize_coordinates
import subprocess
from Image_Processing import encode_image_to_base64

input_file_path = 'input.txt'
output_file_path = 'output.txt'
file_path = 'coordinate.txt'
part_No=''
class GRBLApp:
    def __init__(self, root):
        self.root = root
        
    async def setup(self):
        # Your async initialization code here
        await self.setup_ui()

    def close_app(self):
        self.root.destroy()

    async def setup_ui(self):
        self.root.title("GRBL Controller")
        # self.root.geometry("1600x900")
        self.root.attributes('-fullscreen', True)
        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.image_frame = tk.Frame(self.root)
        self.image_frame.grid(row=0, column=0, rowspan=20, sticky="nsew")

        self.control_frame = tk.Frame(self.root)
        self.control_frame.grid(row=0, column=1, rowspan=20, sticky="nsew")

        self.canvas = tk.Canvas(self.image_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        h_scroll = Scrollbar(self.image_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll = Scrollbar(self.image_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.config(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        self.canvas.bind("<Button-1>", self.display_coordinates)

        await self.create_controls()

    async def create_controls(self):
        tk.Label(self.control_frame, text="Port:").grid(row=0, column=0)
        self.port_entry = tk.Entry(self.control_frame)
        self.port_entry.grid(row=0, column=1)
        self.port_entry.insert(0, 'COM14')

        tk.Label(self.control_frame, text="Baudrate:").grid(row=1, column=0)
        self.baudrate_entry = tk.Entry(self.control_frame)
        self.baudrate_entry.grid(row=1, column=1)
        self.baudrate_entry.insert(0, '115200')

        self.connect_button = tk.Button(self.control_frame, text="Connect", command=self.on_connect)
        self.connect_button.grid(row=2, column=0, columnspan=2)

        self.create_jog_controls()

        self.status_button = tk.Button(self.control_frame, text="Get Status", command=self.on_status)
        self.status_button.grid(row=7, column=0, columnspan=2)

        self.reset_button = tk.Button(self.control_frame, text="Reset Zero", command=self.on_reset_zero)
        self.reset_button.grid(row=8, column=0, columnspan=2)

        self.load_button =tk.Button(self.control_frame, text="Load Image", command=self.load_image_async)
        self.load_button.grid(row=9, column=0, columnspan=2)

        self.create_text_controls()

        self.coords_label = tk.Label(self.control_frame, text="Coordinates: (0, 0)")
        self.coords_label.grid(row=30, column=0, columnspan=2)
        self.progress = ttk.Progressbar(self.control_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.grid(row=32, column=0, columnspan=2)

    def create_jog_controls(self):
        tk.Label(self.control_frame, text="Jog Controls:").grid(row=3, column=0, columnspan=2)
        jog_buttons = [
            ("X+", lambda: self.start_jogging(1, 0, 0)),
            ("X-", lambda: self.start_jogging(-1, 0, 0)),
            ("Y+", lambda: self.start_jogging(0, 1, 0)),
            ("Y-", lambda: self.start_jogging(0, -1, 0)),
            ("Z+", lambda: self.start_jogging(0, 0, 1)),
            ("Z-", lambda: self.start_jogging(0, 0, -1))
        ]

        for i, (text, command) in enumerate(jog_buttons):
            btn = tk.Button(self.control_frame, text=text)
            btn.grid(row=4 + i // 2, column=i % 2)
            btn.bind('<ButtonPress-1>', lambda event, cmd=command: cmd())
            btn.bind('<ButtonRelease-1>', lambda event: self.stop_jogging())

    def create_text_controls(self):
        tk.Label(self.control_frame, text="Part No:").grid(row=10, column=0)
        self.part_no = tk.Entry(self.control_frame, width=20)
        self.part_no.grid(row=10, column=1, columnspan=2)
        tk.Label(self.control_frame, text="Type:").grid(row=12, column=0)
        self.entry1 = tk.Entry(self.control_frame, width=20)
        self.entry1.grid(row=12, column=1, columnspan=2)

        tk.Label(self.control_frame, text="Top , Left:").grid(row=14, column=0)
        self.entry2 = tk.Entry(self.control_frame, width=20)
        self.entry2.grid(row=14, column=1, columnspan=2)

        tk.Label(self.control_frame, text="Bottom , Right:").grid(row=16, column=0)
        self.entry3 = tk.Entry(self.control_frame, width=20)
        self.entry3.grid(row=16, column=1, columnspan=2)

        tk.Label(self.control_frame, text="Rotate:").grid(row=18, column=0)
        self.entry4 = tk.Entry(self.control_frame, width=20)
        self.entry4.grid(row=18, column=1, columnspan=2)
        self.entry4.insert(0, '0')

        tk.Label(self.control_frame, text="Threshold:").grid(row=20, column=0)
        self.entry5 = tk.Entry(self.control_frame, width=20)
        self.entry5.grid(row=20, column=1, columnspan=2)
        self.entry5.insert(0, '110')
        self.submit_button = tk.Button(self.control_frame, text="Submit", command=self.on_submit_click)
        self.submit_button.grid(row=22, column=1)
        self.rich_text = tk.Text(self.control_frame, height=10, width=40)
        self.rich_text.grid(row=24, column=0, columnspan=2)

        self.save_button = tk.Button(self.control_frame, text="Save to File", command=self.on_save_click)
        self.save_button.grid(row=28, column=1)
        self.save_button = tk.Button(self.control_frame, text="Close App", command=self.close_app)
        self.save_button.grid(row=36, column=1)
        # Bind the Enter key to the entry widgets
        self.part_no.bind("<Return>", lambda event: self.entry1.focus_set())
        self.entry1.bind("<Return>", lambda event: self.entry2.focus_set())
        self.entry2.bind("<Return>", lambda event: self.entry3.focus_set())
        self.entry3.bind("<Return>", lambda event: self.entry4.focus_set())
        self.entry4.bind("<Return>", lambda event: self.entry5.focus_set())
        self.entry5.bind("<Return>", lambda event: self.on_submit_click())

    def on_connect(self):
        port = self.port_entry.get()
        baudrate = int(self.baudrate_entry.get())
        self.grbl = GRBLController(port, baudrate)
        if self.grbl.connect():
            try:
                response_120 = self.grbl.send_command('$120=100')
                response_121 = self.grbl.send_command('$121=100')
                response_122 = self.grbl.send_command('$122=100')
                messagebox.showinfo("Connection", "Connected to GRBL!\n$120 Response: {}\n$121 Response: {}\n$122 Response: {}".format(response_120, response_121, response_122))
                self.connect_button.config(text="Connected", state=tk.DISABLED)
                self.port_entry.config(state=tk.DISABLED)
                self.baudrate_entry.config(state=tk.DISABLED)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send commands: {e}")
        else:
            messagebox.showerror("Connection", "Failed to connect to GRBL.")

    def start_jogging(self, x, y, z):
        self.is_jogging = True
        threading.Thread(target=self.on_jog, args=(x, y, z)).start()

    def stop_jogging(self):
        self.is_jogging = False

    def on_jog(self, x, y, z):
        if self.grbl:
            feedrate = 2500
            while self.is_jogging:
                response = self.grbl.jog(x, y, z, feedrate)
                print("Jog Response:", response)
                time.sleep(0.1)
        else:
            messagebox.showerror("Error", "Not connected to GRBL.")

    def on_status(self):
        if self.grbl:
            status = self.grbl.get_status()
            messagebox.showinfo("Status", status)
        else:
            messagebox.showerror("Error", "Not connected to GRBL.")

    def on_reset_zero(self):
        if self.grbl:
            response = self.grbl.reset_zero()
            messagebox.showinfo("Reset Zero", response)
        else:
            messagebox.showerror("Error", "Not connected to GRBL.")
    
    
    # def on_button_click(self):
    #     asyncio.ensure_future(self.load_image_async())


    def load_image_async(self):
        self.capture_frame(True)
        file_path = 'Sources/source_image.jpg'
        if file_path:
            # await self.update_progress(20)
            
            img = Image.open(file_path)
            # await self.update_progress(30)
            self.photo_img = ImageTk.PhotoImage(img)
            # await self.update_progress(70)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_img)
            # await self.update_progress(90)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
            # await self.update_progress(100)  # Set progress to 100% after finishing

    async def update_progress(self, value):
        self.progress["value"] = value
        await self.update_ui()

    async def update_ui(self):
        # Update the UI after a short delay to allow Tkinter to process events
        await asyncio.sleep(0.1)
        # self.root.update_idletasks()

    def display_coordinates(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        img_x = int(canvas_x)
        img_y = int(canvas_y)
        # Update label and entry with coordinates
        self.coords_label.config(text=f"Coordinates: ({img_x}, {img_y})")

        focused_widget = self.root.focus_get()
        if isinstance(focused_widget, tk.Entry):
            focused_widget.delete(0, tk.END)
            focused_widget.insert(tk.END, f"{img_x},{img_y}")

    def on_submit_click(self):
        global part_No
        part_No = self.part_no.get()
        input_text1 = self.entry1.get()
        input_text2 = self.entry2.get()
        input_text3 = self.entry3.get()
        input_text4 = self.entry4.get()
        input_text5 = self.entry5.get()
        combined_text = f"{input_text1},{input_text2},{input_text3},{input_text4},{input_text5}"
        self.rich_text.insert(tk.END, combined_text + "\n")
        self.entry1.delete(0, tk.END)
        self.entry2.delete(0, tk.END)
        self.entry3.delete(0, tk.END)
        self.entry1.focus_set()

    
        

    def remove_blank_lines(self):
        with open(input_file_path, 'r') as input_file:
            lines = input_file.readlines()
        non_blank_lines = [line for line in lines if line.strip()]
        with open(output_file_path, 'w') as output_file:
            output_file.writelines(non_blank_lines)

    def TakeCoordinates(self,datas):        
        checkType = "s"
        partNo=datas
        with open('SampleId.txt', 'r') as file:
            for line in file:
                id = int(line.strip())
        # url = f"http://10.100.10.83:5000/api/VisualIspection/PD/GetSamplePicture?id={id}"
        # response = requests.get(url)
              
        # result_list = json.loads(response.content)
        # json_item = result_list[0]           

        # base64str = json_item['picture']
        with open('output.txt', 'r') as file:
            for line in file:
                try:
                    line_data = line.split(",")     
                    type=line_data[0]
                    top_left = f'{line_data[1]},{line_data[2]}'      
                    bottom_right = f'{line_data[3]},{line_data[4]}'
                    rotate = line_data[5]
                    threshold = line_data[6]     
                    coordinates = Coordinates(0,partNo,type,str(id),top_left,bottom_right,rotate,threshold.replace('\n',''))            
                    url = "http://10.100.10.83:5000/api/VisualIspection/QD/InsertCoordinates"
                            

                    data = json.dumps(coordinates, default=serialize_coordinates)
                    headers = {'Content-Type': 'application/json'}
                    response = requests.post(url, data=data, headers=headers)

                    if response.status_code == 200 or response.status_code == 201:
                        print("Data successfully sent.")               
                    else:
                        print("Failed to send data:", response.status_code)
                        print("Failed to send data:", response.request.body)  
                except Exception as e:
                    print(f"An error occurred: {e}")
                    break
        url1 = f"http://10.100.10.83:5000/api/VisualIspection/PD/getCoordinates?partNo={partNo}"
        response1 = requests.get(url1)
        # Convert Base64 bytes to string (optional, depending on your use case)

        # print(
        #     response.content
        # )
        count = 0
        result_list1 = json.loads(response1.content)
        with open(file_path, 'w') as file:
            for item in result_list1:
                if count > 0:
                    file.write('\n')
                type=item['typeID']
                top_left = item['topLeft']    
                bottom_right = item['bottomRight']
                rotate = item['rotate']
                threshold = item['threshold']                         
                file.write(f'{type},{top_left},{bottom_right},{rotate},{threshold}')
                count = count + 1


    def on_save_click(self):
        with open(input_file_path, "w") as file:
            file.write(self.rich_text.get("1.0", tk.END))
        self.remove_blank_lines()
        self.rich_text.delete('1.0', tk.END)
        self.TakeCoordinates(part_No)
        self.part_no.delete(0, tk.END)
        self.part_no.focus_set()
        messagebox.showinfo("Information", "Update Sample done!")
    
    def capture_frame(self,source):
        # raspi_io.__init__()
        # raspi_io.flash_on()
        if source:
            file_name = "Sources/source_image.jpg"        
        else:
            file_name = "captured_image.jpg"
        ffmpeg_cmd = [
            "libcamera-still",
            "--timeout",
            "750",
            "--width",
            "4056",
            "--height",
            "3040",
            # "--autofocus-mode",
            # "auto",
            # "--autofocus-range",
            # "full",
            # "--autofocus-speed",
            # "fast",
            # "--autofocus-window","0.2,0.2,0.8,0.8",
            # "--shutter",
            # "3000",
            "--sharp",
            "5",
            # "--contrast",
            # "1",
            "--bright",
            "0.2",
            "--vflip",
            "1",
            "--hflip",
            "1",
            # "--hdr","sensor",
            # "--autofocus-on-capture",
            # "1",
            "-f",
            "1",        
            "--denoise",
            "cdn_hq",
            "-o",
            file_name
        ]
        subprocess.run(ffmpeg_cmd)
        url = "http://10.100.10.83:5000/api/VisualIspection/QD/InputSample"
            # url = "https://my-json-server.typicode.com/JasonNguyen1205/GitRepo/sample"
        source_path = 'Sources/source_image.jpg'
        picture = encode_image_to_base64(source_path)

        data = json.dumps({
            "id": 0,
            "picture": picture,
            "remark": "Test"
        })
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=data, headers=headers)

        if response.status_code == 200 or response.status_code == 201:
            print("Data successfully sent.")
            lines_to_write = int(response.content)
            with open('SampleId.txt', 'w') as file:
                file.writelines(str(lines_to_write))
        else:
            print("Failed to send data:", response.status_code)
            print("Failed to send data:", response.request.body)    
        # raspi_io.flash_off()
        # raspi_io.cleanup()