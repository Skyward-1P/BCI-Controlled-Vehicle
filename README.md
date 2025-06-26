# Brain Car Project

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)  
[![Arduino](https://img.shields.io/badge/Arduino-Mega%20%7C%20Nano-green.svg)](https://www.arduino.cc/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

This project enables brain-signal-based control of an RC car using Arduino and Python. It features:

- **Arduino Mega**: Reads 12 analog EEG signals via three ADS1115 ADCs, transmits data wirelessly using RF24L01 (2.4GHz, SPI).
- **Arduino Nano**: Receives wireless data, relays it to a PC via USB Serial.
- **Python PC App**: Receives, logs, classifies signals, and provides a real-time GUI. Sends commands to the RC car via Bluetooth.

## Features

- Real-time wireless EEG data acquisition (12 channels)
- End-to-end pipeline: EEG → Mega (ADS1115) → RF24L01 → Nano → Serial → Python
- Machine learning-based command prediction (Left, Right, Forward)
- Live GUI with data visualization, command history, and session export
- Signal quality checks and safety (Idle state)

## Directory Structure

- `arduino_mega_adc/mega_adc_i2c.ino` — Arduino Mega code (ADS1115, RF24L01)
- `arduino_nano_receiver/nano_receiver_serial.ino` — Arduino Nano code (RF24L01, Serial)
- `python_pc/` — Python code, model, and data

## Hardware Setup

1. **EEG Headset**: Connect 12 electrodes to three ADS1115 ADCs (I2C addresses: 0x48, 0x49, 0x4A), wired to Arduino Mega.
2. **Wireless Link**: Connect RF24L01 modules to both Mega and Nano (SPI wiring).
3. **Nano to PC**: Connect Nano to PC via USB. Connect Bluetooth module (HC-05) to Nano for RC car control.

## Software Setup

1. **Python Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r python_pc/requirements.txt
   ```
2. **Model**: Place your pre-trained model in `python_pc/model/model.pkl` (or use the provided training scripts).
3. **Arduino Libraries**: Install `Adafruit_ADS1X15` and `RF24` libraries via Arduino Library Manager.

## Usage

1. Upload Arduino sketches to Mega and Nano:
   - Mega: `arduino_mega_adc/mega_adc_i2c.ino`
   - Nano: `arduino_nano_receiver/nano_receiver_serial.ino`
2. Run the Python GUI:
   ```bash
   python python_pc/main.py
   ```
3. View live EEG data, logs, and command predictions in the GUI.

## Notes

- Set the correct serial port for your Nano in `main.py` (`NANO_PORT`).
- The `.csx` file is a CSV-like log of all received signals.
- Ensure good electrode contact for best results.

## Real-Time Prediction Test

To simulate real-time EEG control and test the ML pipeline:

```bash
cd python_pc
python test_realtime_sim.py
```

- Prints 100 simulated EEG samples, predicted command, and confidence.
- Some samples will trigger the 'Idle' state to demonstrate signal quality checks.

## GUI Features

- Live EEG data plot (12 channels)
- Predicted command and confidence
- Command history and session export (CSV)
- Signal quality status (Idle state if poor)

## Signal Quality and Safety

- Flatline or bad signals trigger 'Idle' to prevent unintended commands.
- Always ensure good electrode contact.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
