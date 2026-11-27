import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class TestRogueGuardAppSmoke(unittest.TestCase):
    def test_streamlit_dashboard_starts_without_exception(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path), default_timeout=30)
        app.run()
        self.assertFalse(app.exception, msg=str(app.exception))


if __name__ == "__main__":
    unittest.main()
