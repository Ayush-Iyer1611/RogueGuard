import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import auth


class TestLocalAuthentication(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "auth-test.db"
        self.db_patch = patch.object(auth, "DB", self.db_path)
        self.db_patch.start()
        auth.initialize_auth()

    def tearDown(self):
        self.db_patch.stop()
        self.temp_dir.cleanup()

    def create_operator(self):
        return auth.create_first_user("operator", "CorrectHorseBattery12", "CorrectHorseBattery12")

    def test_initial_setup_creates_one_admin(self):
        self.assertEqual(auth.user_count(), 0)
        self.assertEqual(self.create_operator(), "operator")
        self.assertEqual(auth.user_count(), 1)

    def test_password_is_hashed_not_stored_as_plaintext(self):
        self.create_operator()
        with sqlite3.connect(self.db_path) as con:
            stored = con.execute(
                "SELECT password_salt, password_hash FROM rg_local_users WHERE username = ?",
                ("operator",),
            ).fetchone()
        self.assertNotEqual(stored[1], "CorrectHorseBattery12")
        self.assertEqual(len(stored[0]), 32)
        self.assertEqual(len(stored[1]), 64)

    def test_valid_login_returns_user_record(self):
        self.create_operator()
        result = auth.authenticate("operator", "CorrectHorseBattery12")
        self.assertEqual(result, {"username": "operator", "role": "ADMIN"})

    def test_username_and_password_are_treated_as_values(self):
        self.create_operator()
        result = auth.authenticate("operator' OR 1=1 --", "' OR '1'='1")
        self.assertIsNone(result)
        self.assertEqual(auth.user_count(), 1)

    def test_invalid_password_is_rejected(self):
        self.create_operator()
        self.assertIsNone(auth.authenticate("operator", "WrongPassword123"))

    def test_five_failed_logins_trigger_temporary_lockout(self):
        self.create_operator()
        for _ in range(auth.MAX_LOGIN_FAILURES):
            self.assertIsNone(auth.authenticate("operator", "IncorrectPassword123"))
        self.assertIsNone(auth.authenticate("operator", "CorrectHorseBattery12"))

    def test_open_registration_is_not_available_after_first_account(self):
        self.create_operator()
        with self.assertRaises(ValueError):
            auth.create_first_user("seconduser", "AnotherCorrectPassword12", "AnotherCorrectPassword12")

    def test_password_minimum_length_is_enforced(self):
        with self.assertRaises(ValueError):
            auth.create_first_user("operator", "short", "short")


if __name__ == "__main__":
    unittest.main()
