import pickle
import numpy as np
from scipy.signal import welch

# Frequency bands
BANDS = {
    'delta': (0.5, 4),
    'theta': (4, 8),
    'alpha': (8, 13),
    'beta': (13, 30),
    'gamma': (30, 45)
}

# Channel names (update as needed to match your data)
EEG_CHANNELS = [
    'Fc5.', 'Fc3.', 'Fc1.', 'Fcz.', 'Fc2.', 'Fc4.', 'Fc6.', 'C5..', 'C3..', 'C1..', 'Cz..', 'C2..'
]

MODEL_PATH = 'model/model_physionet_3class_advanced.pkl'
IDLE_THRESHOLD = 1e-6  # Threshold for flatline detection

# Load model
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

# Feature extraction (same as training)
def extract_features(trial, sf=160):
    features = []
    for ch in trial:
        features.append(np.mean(ch))
        features.append(np.std(ch))
        for band in BANDS.values():
            bp = bandpower(ch, sf, band)
            features.append(bp)
    return np.array(features)

def bandpower(data, sf, band):
    freqs, psd = welch(data, sf, nperseg=sf*2)
    idx_band = np.logical_and(freqs >= band[0], freqs <= band[1])
    return np.mean(psd[idx_band])

# Signal quality check
def is_signal_good(trial):
    # Flatline or all zeros/constant
    if np.all(np.abs(trial) < IDLE_THRESHOLD):
        return False
    # Add more checks as needed (e.g., out-of-range)
    return True

# Predict command
def predict_command(trial, sf=160):
    if not is_signal_good(trial):
        return 'Idle', 0.0
    features = extract_features(trial, sf)
    proba = model.predict_proba([features])[0]
    pred = np.argmax(proba)
    command = ['Left', 'Right', 'Forward'][pred]
    confidence = proba[pred]
    return command, confidence 