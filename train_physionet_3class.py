import os
import mne
import numpy as np
from glob import glob
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle

# Map event keys to class labels
EVENT_TO_LABEL = {
    'T1': 0,  # Left
    'T2': 1,  # Right
    'T0': 2,  # Forward
}

DATA_DIR = '/home/skyward/university_ projects/brain_car/python_pc/data'
edf_files = glob(os.path.join(DATA_DIR, 'S*R*.edf'))

# 12 standard EEG channels in PhysioNet
EEG_CHANNELS = [
    'Fcz.', 'Fz..', 'C1..', 'Cz..', 'C2..', 'C3..', 'C4..', 'Cp1.', 'Cpz.', 'Cp2.', 'Pz..', 'T7..'
]

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
    print(f"Events in {edf_file}: {event_id}")
    for event_key, label in EVENT_TO_LABEL.items():
        if event_key not in event_id:
            continue
        epochs = mne.Epochs(raw, events, event_id={event_key: event_id[event_key]}, tmin=0, tmax=1, baseline=None, preload=True, verbose=False)
        data = epochs.get_data()  # shape: (n_trials, n_channels, n_times)
        for trial in data:
            features = np.concatenate([trial.mean(axis=1), trial.std(axis=1)])
            X.append(features)
            y.append(label)

X = np.array(X)
y = np.array(y)

print('Feature matrix shape:', X.shape)
print('Labels shape:', y.shape)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Train classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred, target_names=['Left', 'Right', 'Forward']))

# Save model
os.makedirs('model', exist_ok=True)
with open('model/model_physionet_3class.pkl', 'wb') as f:
    pickle.dump(clf, f)
print("Model saved as model/model_physionet_3class.pkl")
