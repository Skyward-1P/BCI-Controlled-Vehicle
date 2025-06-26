import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk

import numpy as np
import gui
import queue

class TestGUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.data_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.app = gui.BrainCarGUI(self.root, self.data_queue, self.command_queue)

    def tearDown(self):
        self.root.destroy()

    def test_gui_instantiation(self):
        self.assertIsInstance(self.app, gui.BrainCarGUI)
        self.assertEqual(self.app.latest_data, [0]*12)
        self.assertEqual(self.app.last_command, "None")

    def test_update_gui_with_data(self):
        self.data_queue.put(np.ones((12, 321)))
        self.command_queue.put("Forward")
        self.app.update_gui()
        self.assertEqual(self.app.latest_data, [1]*12)
        self.assertEqual(self.app.last_command, "Forward")
        self.assertIn("Forward", self.app.command_history)
        self.assertIn([1]*12, self.app.data_history)

    @patch('tkinter.filedialog.asksaveasfilename', return_value='test_export.csv')
    @patch('builtins.open')
    def test_export_session(self, mock_open, mock_dialog):
        self.app.data_history = [[1]*12, [0]*12]
        self.app.command_history = ["Forward", "Left"]
        self.app.export_session()
        mock_open.assert_called_with('test_export.csv', 'w', newline='')

if __name__ == '__main__':
    unittest.main() 