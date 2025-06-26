import os
import mne
import numpy as np
from glob import glob
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report
import pickle

# Frequency bands (Hz)
BANDS = {
    'delta': (0.5, 4),
    'theta': (4, 8),
    'alpha': (8, 13),
    'beta': (13, 30),
    'gamma': (30, 45)
}

# Map event keys to class labels
EVENT_TO_LABEL = {
    'T1': 0,  # Left
    'T2': 1,  # Right
    'T0': 2,  # Forward
}

DATA_DIR = '/home/skyward/university_ projects/brain_car/python_pc/data'
edf_files = glob(os.path.join(DATA_DIR, 'S*R*.edf'))

# Use 12 common motor cortex channels (adjust as needed)
EEG_CHANNELS = [
    'Fcz.', 'Fz..', 'C1..', 'Cz..', 'C2..', 'C3..', 'C4..', 'Cp1.', 'Cpz.', 'Cp2.', 'Pz..', 'T7..'
]

def bandpower(data, sf, band):
    from scipy.signal import welch
    band = np.asarray(band)
    low, high = band
    bp = []
    for ch in data:
        freqs, psd = welch(ch, sf, nperseg=min(2*sf, len(ch)))
        idx_band = np.logical_and(freqs >= low, freqs <= high)
        bp.append(np.mean(psd[idx_band]))
    return np.array(bp)

X = []
y = []

for edf_file in edf_files:
    print(f"Processing {edf_file} ...")
    raw = mne.io.read_raw_edf(edf_file, preload=True, verbose=False)
    present_channels = [ch for ch in EEG_CHANNELS if ch in raw.ch_names]
    if len(present_channels) < 8:
        print(f"Warning: Only found {len(present_channels)} EEG channels in {edf_file}. Using available.")
    raw.pick_channels(present_channels)
    events, event_id = mne.events_from_annotations(raw)
    for event_key, label in EVENT_TO_LABEL.items():
        if event_key not in event_id:
            continue
        epochs = mne.Epochs(raw, events, event_id={event_key: event_id[event_key]}, tmin=0, tmax=1, baseline=None, preload=True, verbose=False)
        data = epochs.get_data()  # (n_trials, n_channels, n_times)
        sf = int(raw.info['sfreq'])
        for trial in data:
            # Time-domain features
            means = trial.mean(axis=1)
            stds = trial.std(axis=1)
            # Frequency band powers
            bandpowers = []
            for band in BANDS.values():
                bp = bandpower(trial, sf, band)
                bandpowers.append(bp)
            bandpowers = np.concatenate(bandpowers)
            features = np.concatenate([means, stds, bandpowers])
            X.append(features)
            y.append(label)

X = np.array(X)
y = np.array(y)

print('Feature matrix shape:', X.shape)
print('Labels shape:', y.shape)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Try Random Forest, SVM, and LDA
models = {
    'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
    'SVM': SVC(kernel='rbf', C=1, random_state=42),
    'LDA': LDA()
}

for name, model in models.items():
    print(f"\nTraining and evaluating {name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=['Left', 'Right', 'Forward']))
    # Cross-validation
    scores = cross_val_score(model, X, y, cv=5)
    print(f"{name} 5-fold CV accuracy: {scores.mean():.3f} ± {scores.std():.3f}")

# Save the best model (Random Forest here, or pick your favorite)
with open('model/model_physionet_3class_advanced.pkl', 'wb') as f:
    pickle.dump(models['RandomForest'], f)
print("Advanced model saved as model/model_physionet_3class_advanced.pkl")
