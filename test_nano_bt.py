import serial
import time

# Fill in your Nano's serial port here:
NANO_PORT = '/dev/ttyUSB0'  # <-- Change this if needed!
NANO_BAUD = 115200
BT_PORT = '/dev/rfcomm0'
BT_BAUD = 9600

def mock_predict_command(eeg_data):
    # Replace this with your real ML model prediction
    # For now, just return 'Forward' for demonstration
    return 'Forward'

def main():
    with serial.Serial(NANO_PORT, NANO_BAUD, timeout=2) as nano_ser, \
         serial.Serial(BT_PORT, BT_BAUD, timeout=2) as bt_ser:
        print("Listening for EEG data from Nano...")
        while True:
            line = nano_ser.readline().decode().strip()
            if not line:
                continue
            print(f"Received EEG data: {line}")
            # Parse EEG data (comma-separated values)
            eeg_values = [int(x) for x in line.split(',') if x.isdigit()]
            # Predict command
            command = mock_predict_command(eeg_values)
            print(f"Predicted command: {command}")
            # Send command to RC car via Bluetooth
            bt_ser.write((command + '\n').encode())
            print(f"Sent command to RC car: {command}")

if __name__ == '__main__':
    main()
