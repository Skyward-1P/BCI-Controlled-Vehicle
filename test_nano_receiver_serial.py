import unittest
from unittest.mock import MagicMock, patch

class MockRF24:
    def __init__(self, data_to_receive):
        self.data_to_receive = data_to_receive
        self.read_called = False
    def available(self):
        return not self.read_called
    def read(self, buf, size):
        for i in range(size):
            buf[i] = self.data_to_receive[i]
        self.read_called = True

class TestNanoReceiverSerial(unittest.TestCase):
    def test_receive_and_send(self):
        NUM_ELECTRODES = 12
        # Simulate received data
        received_data = [i for i in range(NUM_ELECTRODES)]
        mock_radio = MockRF24(received_data)
        output_lines = []
        
        # Simulate the Arduino loop logic
        receivedValues = [0]*NUM_ELECTRODES
        if mock_radio.available():
            mock_radio.read(receivedValues, NUM_ELECTRODES)
            # Instead of Serial.print, append to output_lines
            line = ','.join(str(v) for v in receivedValues)
            output_lines.append(line)
        
        # Check output
        self.assertEqual(len(output_lines), 1)
        self.assertEqual(output_lines[0], ','.join(str(i) for i in range(NUM_ELECTRODES)))

if __name__ == '__main__':
    unittest.main() 