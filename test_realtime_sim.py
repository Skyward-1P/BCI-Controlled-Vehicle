import numpy as np
from predictor import predict_command

sf = 160  # Sampling frequency
n_channels = 12
n_timepoints = 321

print("Simulating real-time EEG data...")
for i in range(100):
    if i % 20 == 0:
        # Simulate bad signal (flatline)
        trial = np.zeros((n_channels, n_timepoints))
    else:
        # Simulate normal EEG (random noise)
        trial = np.random.randn(n_channels, n_timepoints) * 10
    command, confidence = predict_command(trial, sf)
    print(f"Sample {i+1:03d}: Command={command}, Confidence={confidence:.2f}") 