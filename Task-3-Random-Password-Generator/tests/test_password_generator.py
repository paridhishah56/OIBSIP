"""Tests for secure password generation and session history."""

import random
import string
import unittest
from unittest.mock import patch

from password_generator import (
    AMBIGUOUS_CHARACTERS,
    MAX_LENGTH,
    MIN_LENGTH,
    PasswordOptions,
    SessionHistory,
    estimate_strength,
    generate_password,
)


class GeneratePasswordTests(unittest.TestCase):
    def test_length_boundaries(self) -> None:
        for length in (MIN_LENGTH, MAX_LENGTH):
            with self.subTest(length=length):
                password = generate_password(PasswordOptions(length=length))
                self.assertEqual(len(password), length)

    def test_each_supported_category_is_represented(self) -> None:
        options = PasswordOptions(length=8)
        password = generate_password(options)
        self.assertTrue(any(character in string.ascii_uppercase for character in password))
        self.assertTrue(any(character in string.ascii_lowercase for character in password))
        self.assertTrue(any(character in string.digits for character in password))
        self.assertTrue(any(character in string.punctuation for character in password))

    def test_selected_categories_are_represented(self) -> None:
        password = generate_password(
            PasswordOptions(length=8, uppercase=False, lowercase=False, digits=True, special_characters=True)
        )
        self.assertTrue(any(character in string.digits for character in password))
        self.assertTrue(any(character in string.punctuation for character in password))
        self.assertFalse(any(character in string.ascii_letters for character in password))

    def test_ambiguous_characters_are_excluded_from_every_category(self) -> None:
        password = generate_password(PasswordOptions(length=128, exclude_ambiguous=True))
        self.assertTrue(AMBIGUOUS_CHARACTERS.isdisjoint(password))

    def test_invalid_lengths_and_empty_selection(self) -> None:
        for length in (MIN_LENGTH - 1, MAX_LENGTH + 1, 10.5, True):
            with self.subTest(length=length), self.assertRaises(ValueError):
                generate_password(PasswordOptions(length=length))
        with self.assertRaisesRegex(ValueError, "Select at least one"):
            generate_password(
                PasswordOptions(uppercase=False, lowercase=False, digits=False, special_characters=False)
            )

    def test_secure_random_sources_are_used(self) -> None:
        with patch("password_generator.secrets.choice", wraps=__import__("secrets").choice) as secure_choice:
            with patch.object(random, "choice", side_effect=AssertionError("random.choice must not be used")):
                generate_password(PasswordOptions(length=8))
        self.assertGreater(secure_choice.call_count, 0)

    def test_strength_estimate_uses_length_and_diversity(self) -> None:
        self.assertEqual(estimate_strength("abc"), ("Weak", 30))
        self.assertEqual(estimate_strength("ab12cdefghij"), ("Medium", 65))
        self.assertEqual(estimate_strength("Abcdefgh123456!"), ("Medium", 65))
        self.assertEqual(estimate_strength("Abcdefgh123456!x"), ("Strong", 100))


class SessionHistoryTests(unittest.TestCase):
    def test_history_retains_only_five_most_recent_values(self) -> None:
        history = SessionHistory()
        for index in range(7):
            history.add(f"test-value-{index}")
        self.assertEqual(
            history.passwords,
            ("test-value-6", "test-value-5", "test-value-4", "test-value-3", "test-value-2"),
        )

    def test_clear_removes_all_values(self) -> None:
        history = SessionHistory()
        history.add("test-value")
        history.clear()
        self.assertEqual(history.passwords, ())


if __name__ == "__main__":
    unittest.main()
