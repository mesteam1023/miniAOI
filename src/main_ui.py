import tkinter as tk
from tkinter import ttk, messagebox
import sys
import requests, os, threading
import asyncio

# Add the src directory to the path to import load_img
sys.path.insert(0, '/home/pi/miniAOI/src')
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ['DISPLAY'] = ':0.0'
class MainUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Main Application")
        self.root.geometry("500x400")
        
        # Title
        title_label = tk.Label(root, text="Main Control Panel", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Button to open GRBL UI
        open_sample_btn = tk.Button(root, text="Open GRBL UI", command=self.open_grbl_ui, 
                                     width=20, height=2, bg="#4CAF50", fg="white")
        open_sample_btn.pack(pady=10)
        
        # Combobox for API data
        combobox_frame = tk.Frame(root)
        combobox_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(combobox_frame, text="Select Data:").pack(side="left", padx=5)
        self.data_combobox = ttk.Combobox(combobox_frame, width=30, state="readonly")
        self.data_combobox.pack(side="left", padx=5)
        
        load_btn = tk.Button(combobox_frame, text="Load from API", command=self.load_api_data)
        load_btn.pack(side="left", padx=5)
        
        # OrderNo textbox
        order_frame = tk.Frame(root)
        order_frame.pack(pady=5, padx=20, fill="x")
        tk.Label(order_frame, text="Order No:", width=10, anchor="w").pack(side="left")
        self.order_entry = tk.Entry(order_frame, width=30)
        self.order_entry.pack(side="left", padx=5)
        
        # PartNo textbox
        part_frame = tk.Frame(root)
        part_frame.pack(pady=5, padx=20, fill="x")
        tk.Label(part_frame, text="Part No:", width=10, anchor="w").pack(side="left")
        self.part_entry = tk.Entry(part_frame, width=30)
        self.part_entry.pack(side="left", padx=5)
        
        # Barcode textbox
        barcode_frame = tk.Frame(root)
        barcode_frame.pack(pady=5, padx=20, fill="x")
        tk.Label(barcode_frame, text="Barcode:", width=10, anchor="w").pack(side="left")
        self.barcode_entry = tk.Entry(barcode_frame, width=30)
        self.barcode_entry.pack(side="left", padx=5)
        
        # Submit button
        submit_btn = tk.Button(root, text="Submit", command=self.on_submit, 
                              width=15, height=2, bg="#2196F3", fg="white")
        submit_btn.pack(pady=20)
        
    def open_grbl_ui(self):
        """Open GRBL UI using the GRBLApp from load_img"""
        try:
            from load_img import GRBLApp
            
            # Create a new Tkinter window for GRBL UI
            grbl_window = tk.Toplevel(self.root)
            grbl_app = GRBLApp(grbl_window)
            grbl_app.setup_sync()  # Use synchronous setup
            
            messagebox.showinfo("Info", "GRBL UI opened successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open GRBL UI: {str(e)}")
    
    def load_api_data(self):
        """Load data from API and populate combobox"""
        try:
            # TODO: Replace with actual API call
            # Example: response = requests.get("your_api_url")
            # data = response.json()
            
            # Mock data for demonstration
            mock_data = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
            
            self.data_combobox['values'] = mock_data
            if mock_data:
                self.data_combobox.current(0)
            messagebox.showinfo("Success", "Data loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def on_submit(self):
        """Handle submit button click"""
        order_no = self.order_entry.get()
        part_no = self.part_entry.get()
        barcode = self.barcode_entry.get()
        selected_data = self.data_combobox.get()
        
        if not order_no or not part_no or not barcode:
            messagebox.showwarning("Warning", "Please fill in all fields")
            return
        
        # TODO: Process the data as needed
        message = f"Data submitted:\nOrder No: {order_no}\nPart No: {part_no}\nBarcode: {barcode}\nSelected: {selected_data}"
        messagebox.showinfo("Submitted", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainUI(root)
    root.mainloop()
