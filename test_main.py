import unittest
from unittest.mock import patch, MagicMock, mock_open
import main
import os
import numpy as np

class DummySerial:
    def __init__(self, lines):
        self.lines = lines
        self.index = 0
    def readline(self):
        if self.index < len(self.lines):
            line = self.lines[self.index]
            self.index += 1
            return line.encode()
        return b''
    def close(self):
        pass

class TestMain(unittest.TestCase):
    @patch('serial.Serial')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_serial_reader(self, mock_file, mock_makedirs, mock_serial):
        # Simulate 321 lines of serial input, each with 12 comma-separated values
        lines = [','.join(['1']*12) for _ in range(321)]
        mock_serial.return_value = DummySerial(lines)
        q = main.queue.Queue()
        # Patch data_queue in main
        with patch('main.data_queue', q):
            # Run serial_reader in a thread and stop after one buffer
            import threading
            t = threading.Thread(target=main.serial_reader, daemon=True)
            t.start()
            import time
            time.sleep(0.2)  # Give thread time to fill buffer
            t.join(timeout=0.1)
            self.assertFalse(q.empty())
            arr = q.get()
            self.assertEqual(arr.shape, (12, 321))

    @patch('serial.Serial')
    def test_bluetooth_sender(self, mock_serial):
        # Test bluetooth_sender sends correct command
        mock_serial_instance = MagicMock()
        mock_serial.return_value = mock_serial_instance
        main.bluetooth_sender('Forward')
        mock_serial_instance.write.assert_called_with(b'Forward\n')
        mock_serial_instance.close.assert_called_once()

if __name__ == '__main__':
    unittest.main() 