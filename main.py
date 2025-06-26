import serial
import time
import threading
import queue
import numpy as np
import pickle
import os
from predictor import predict_command

# Serial port settings (update as needed)
NANO_PORT = '/dev/ttyUSB0'  # Arduino Nano
BT_PORT = '/dev/rfcomm0'    # Bluetooth HC-05
BAUDRATE = 115200
BT_BAUDRATE = 9600

DATA_FILE = os.path.join('data', 'signals.csx')
N_CHANNELS = 12
N_TIMEPOINTS = 321

# Command labels
COMMANDS = ['Left', 'Right', 'Forward']

data_queue = queue.Queue()  # For data to GUI
command_queue = queue.Queue()  # For command to GUI

def serial_reader():
    """Read from Nano, log to file, and put (12, 321) arrays in queue."""
    try:
        ser = serial.Serial(NANO_PORT, BAUDRATE, timeout=1)
    except Exception as e:
        print(f"Error opening Nano serial: {e}")
        return
    os.makedirs('data', exist_ok=True)
    with open(DATA_FILE, 'a') as f:
        while True:
            buffer = np.zeros((N_CHANNELS, N_TIMEPOINTS), dtype=np.int16)
            t = 0
            while t < N_TIMEPOINTS:
                line = ser.readline().decode(errors='ignore').strip()
                if not line:
                    continue
                f.write(line + '\n')
                f.flush()
                try:
                    values = [int(x) for x in line.split(',')]
                    if len(values) == N_CHANNELS:
                        buffer[:, t] = values
                        t += 1
                except Exception:
                    continue
            data_queue.put(buffer)


def bluetooth_sender(cmd):
    """Send command to RC car via Bluetooth."""
    try:
        bt = serial.Serial(BT_PORT, BT_BAUDRATE, timeout=1)
        bt.write((cmd + '\n').encode())
        bt.close()
    except Exception as e:
        print(f"Bluetooth send error: {e}")


def classify_and_send():
    """Classify (12, 321) data and send command via Bluetooth. Each command is sent for 3 seconds, then a stop command ('S') is sent."""
    while True:
        trial = data_queue.get()
        command, confidence = predict_command(trial)
        print(f"Predicted: {command} | Confidence: {confidence:.2f}")
        bluetooth_sender(command)
        command_queue.put(command)  # Pass to GUI
        # Wait 3 seconds, then send stop command
        time.sleep(3)
        bluetooth_sender('S')
        command_queue.put('S')


def main():
    # Start serial reader thread
    t1 = threading.Thread(target=serial_reader, daemon=True)
    t1.start()
    # Start classifier thread
    t2 = threading.Thread(target=classify_and_send, daemon=True)
    t2.start()
    # Start GUI (imported from gui.py)
    import gui
    gui.run_gui(data_queue, command_queue)

if __name__ == '__main__':
    main() 