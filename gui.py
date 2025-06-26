import tkinter as tk
from tkinter import ttk, filedialog
import threading
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import csv
from predictor import predict_command

class BrainCarGUI:
    def __init__(self, root, data_queue, command_queue):
        self.root = root
        self.data_queue = data_queue
        self.command_queue = command_queue
        self.latest_data = [0]*12
        self.last_command = "None"
        self.data_history = []  # Store all data samples
        self.command_history = []  # Store all commands
        self.last_confidence = 0.0
        self.status_var = tk.StringVar()

        root.title("Brain Car Control Panel")
        self.data_label = ttk.Label(root, text="Latest Data:")
        self.data_label.pack()
        self.data_values = ttk.Label(root, text=str(self.latest_data))
        self.data_values.pack()

        self.command_label = ttk.Label(root, text="Last Command:")
        self.command_label.pack()
        self.command_value = ttk.Label(root, text=self.last_command)
        self.command_value.pack()

        self.status_label = ttk.Label(root, textvariable=self.status_var)
        self.status_label.pack()

        # Command history
        self.history_label = ttk.Label(root, text="Command History:")
        self.history_label.pack()
        self.command_listbox = tk.Listbox(root, height=6, width=30)
        self.command_listbox.pack()

        # Real-time plot
        self.fig, self.ax = plt.subplots(figsize=(6,2))
        self.line, = self.ax.plot(range(12), self.latest_data, marker='o')
        self.ax.set_ylim(-0.5, 1.5)
        self.ax.set_title('12-Channel Data')
        self.ax.set_xlabel('Channel')
        self.ax.set_ylabel('Value')
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        # Log window
        self.log_text = tk.Text(root, height=8, width=60)
        self.log_text.pack()

        # Export button
        self.export_button = ttk.Button(root, text="Export Session", command=self.export_session)
        self.export_button.pack(pady=5)

        self.update_gui()

    def update_gui(self):
        # Only use real EEG data from the data_queue
        if self.data_queue.empty():
            return  # No data to process, skip update
        trial = self.data_queue.get()
        command, confidence = predict_command(trial)
        self.latest_data = trial.mean(axis=1).tolist()
        self.last_command = command
        self.last_confidence = confidence
        self.command_history.append(command)
        self.data_history.append(self.latest_data)
        # Update plot
        self.line.set_ydata(self.latest_data)
        self.ax.set_title(f'12-Channel Data | Command: {command} | Confidence: {confidence:.2f}')
        self.canvas.draw()
        # Update status
        self.status_var.set(f"Command: {command} | Confidence: {confidence:.2f}")
        # Signal quality check
        if command == 'Idle':
            self.status_var.set("Signal quality poor: Idle state")
        while not self.command_queue.empty():
            cmd = self.command_queue.get_nowait()
            self.last_command = cmd
            self.command_value.config(text=self.last_command)
            self.command_history.append(cmd)
            self.command_listbox.insert(tk.END, cmd)
            self.log_text.insert(tk.END, f"Command: {cmd}\n")
            self.log_text.see(tk.END)
        self.root.after(100, self.update_gui)

    def export_session(self):
        file_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')])
        if not file_path:
            return
        try:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Sample'] + [f'Ch{i+1}' for i in range(12)] + ['Command'])
                for i, data in enumerate(self.data_history):
                    cmd = self.command_history[i] if i < len(self.command_history) else ''
                    writer.writerow([i+1] + data + [cmd])
            self.log_text.insert(tk.END, f"Session exported to {file_path}\n")
        except Exception as e:
            self.log_text.insert(tk.END, f"Export error: {e}\n")

def run_gui(data_queue, command_queue):
    root = tk.Tk()
    app = BrainCarGUI(root, data_queue, command_queue)
    root.mainloop() 