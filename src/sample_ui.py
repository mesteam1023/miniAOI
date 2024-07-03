import tkinter as tk
from tkinter import messagebox
count = 0
# Create the main application window
root = tk.Tk()
root.title("Simple GUI")
root.geometry("600x600")

# Create a label for the first text box
label1 = tk.Label(root, text="Enter text in Box 1:")
label1.pack(pady=5)

# Create the first entry widget
entry1 = tk.Entry(root, width=30)
entry1.pack(pady=5)

# Create a label for the second text box
label2 = tk.Label(root, text="Enter text in Box 2:")
label2.pack(pady=5)

# Create the second entry widget
entry2 = tk.Entry(root, width=30)
entry2.pack(pady=5)

# Create a Text widget for displaying combined input
rich_text = tk.Text(root, height=10, width=40)
rich_text.pack(pady=10)
# Replace 'input.txt' and 'output.txt' with your actual file paths
input_file_path = 'input.txt'
output_file_path = 'output.txt'

def remove_blank_lines(input_file_path, output_file_path):
    with open(input_file_path, 'r') as input_file:
        lines = input_file.readlines()

    non_blank_lines = [line for line in lines if line.strip()]
    # Remove the last line
    non_blank_lines = non_blank_lines[:-1]
    with open(output_file_path, 'w') as output_file:
        output_file.writelines(non_blank_lines)
# Define a function to be called when the Submit button is clicked
def on_submit_click():
    global count
    input_text1 = entry1.get()
    input_text2 = entry2.get()
    combined_text = f"{input_text1},{input_text2}"
    rich_text.insert(tk.END, combined_text + "\n")
    
# Define a function to be called when the Save to File button is clicked
def on_save_click():
    with open("input.txt", "w") as file:
        file.write(rich_text.get("1.0", tk.END))
    remove_blank_lines(input_file_path, output_file_path)
    messagebox.showinfo("Information", "Text has been saved to output.txt")

# Bind the Enter key to the first entry widget to move focus to the second entry widget
entry1.bind("<Return>", lambda event: entry2.focus_set())

# Bind the Enter key to the second entry widget to trigger the action and update the Text widget
entry2.bind("<Return>", lambda event: on_submit_click())

# Create a Submit button
submit_button = tk.Button(root, text="Submit", command=on_submit_click)
submit_button.pack(pady=5)

# Create a Save to File button
save_button = tk.Button(root, text="Save to File", command=on_save_click)
save_button.pack(pady=5)



# Run the application
root.mainloop()
