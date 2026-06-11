import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv()
from config import config
import unittest



class TestConfig(unittest.TestCase):

    
    def test_time_util_now(self):
        ts_set = {
        # Input -> Expected (matching %Y-%m-%dT%H:%M)
        "2024-06-01 12:00:00":          "2024-06-01T12:00",
        "2026-06-10T14:15:05-04:00":    "2026-06-10T14:15",
        "2025-06-15T18:30:00Z":         "2025-06-15T18:30"
    }

        for ts, expected in ts_set.items():
            result = config.time_util_now(ts)
            self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()