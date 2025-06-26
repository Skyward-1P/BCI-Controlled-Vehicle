import mne
import numpy as np
import glob

# List of EDF files to process
edf_files = [
    'S001R04.edf',
    'S001R06.edf',
    'S001R08.edf',
    'S001R10.edf',
    'S001R12.edf',
    'S001R14.edf',
    'S002R04.edf',
    'S002R06.edf',
    'S002R10.edf',
    'S002R12.edf',
    'S002R14.edf',
]

# Number of channels to select (match your hardware)
N_CHANNELS = 12

# Store all data and labels
all_X = []
all_y = []

for edf_file in edf_files:
    print(f"Loading {edf_file} ...")
    raw = mne.io.read_raw_edf(edf_file, preload=True, verbose=False)
    
    # Extract events from annotations
    events, event_id = mne.events_from_annotations(raw)
    print(f"  Found events: {event_id}")
    
    # Define epoching parameters (0 to 2 seconds after event)
    tmin, tmax = 0, 2
    epochs = mne.Epochs(raw, events, event_id=event_id, tmin=tmin, tmax=tmax, baseline=None, preload=True, verbose=False)
    
    # Pick the first N_CHANNELS (or modify to select specific channels)
    epochs.pick_channels(raw.ch_names[:N_CHANNELS])
    
    # Get data and labels
    X = epochs.get_data()  # shape: (n_epochs, n_channels, n_times)
    y = epochs.events[:, 2]  # event codes (T0, T1, T2)
    
    print(f"  Data shape: {X.shape}, Labels shape: {y.shape}")
    
    all_X.append(X)
    all_y.append(y)

# Concatenate all data
X_all = np.concatenate(all_X, axis=0)
y_all = np.concatenate(all_y, axis=0)

print("\nFinal data shapes:")
print("X_all:", X_all.shape)  # (total_epochs, n_channels, n_times)
print("y_all:", y_all.shape)  # (total_epochs,)

# Save for later ML processing (optional)
# np.save('X_all.npy', X_all)
# np.save('y_all.npy', y_all)

# You can now proceed with feature extraction and ML training using X_all and y_all 