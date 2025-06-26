import os
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# You may need to install mne and requests: pip install mne requests
import mne
import requests

# Mapping: 0=Left, 1=Right, 2=Forward, 3=Reverse
COMMANDS = ['Left', 'Right', 'Forward', 'Reverse']
CLASS_MAP = {"left_hand": 0, "right_hand": 1, "feet": 2, "tongue": 3}
NUM_ELECTRODES = 12

# Download BCI Competition IV IIa data for one subject as a demo (full dataset is large)
DATA_URL = "https://www.bbci.de/competition/iv/desc_IIa.html"
GDF_URL = "https://www.bbci.de/competition/iv/BCI_Comp_IV_mat/subject_A01T.mat"
DATA_PATH = "A01T.mat"

# Download the file if not present
if not os.path.exists(DATA_PATH):
    print("Downloading sample subject data (A01T.mat)...")
    r = requests.get(GDF_URL)
    with open(DATA_PATH, 'wb') as f:
        f.write(r.content)

# Load the .mat file using mne
try:
    import scipy.io
    mat = scipy.io.loadmat(DATA_PATH)
    eeg = mat['data']  # This may need adjustment depending on the file structure
    # For demo, we will simulate data
    print("Loaded .mat file. (For full dataset, use all subjects)")
    # Simulate: 1000 samples, 12 channels, 4 classes
    X = np.random.randn(1000, NUM_ELECTRODES)
    y = np.random.choice([0, 1, 2, 3], size=1000)
except Exception as e:
    print(f"Error loading .mat file: {e}")
    print("Simulating data for demo...")
    X = np.random.randn(1000, NUM_ELECTRODES)
    y = np.random.choice([0, 1, 2, 3], size=1000)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred, target_names=COMMANDS))

# Save model
os.makedirs('model', exist_ok=True)
with open('model/model.pkl', 'wb') as f:
    pickle.dump(clf, f)
print("Model saved as model/model.pkl")

# Instructions:
# - For real use, replace the simulated data loading with actual EEG feature extraction from the .mat files.
# - Use the same feature order (12 channels) as your hardware.
# - Retrain as needed for best results. 