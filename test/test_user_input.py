#!/usr/bin/python3
"""Tests for user_input key handling.

These tests verify that all digits, letters, and special characters
are correctly captured and converted to strings by the input system.
We simulate key events to test without a real keyboard.
"""

import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from smileymath.user_input import UserInput, IntUserInput, DoubleIntUserInput, Key


class TestGetInputString(unittest.TestCase):
    """Test that get_input_string correctly builds strings from key lists."""

    def setUp(self):
        """Create a UserInput instance without starting a listener."""
        with patch('smileymath.user_input.logging'):
            self.ui = UserInput(timeout=10)

    def test_single_digits(self):
        """All digits 0-9 should be captured."""
        for digit in '0123456789':
            self.ui.input_key_list = [digit]
            result = self.ui.get_input_string()
            self.assertEqual(result, digit, f"Digit '{digit}' was not captured")

    def test_multi_digit_number(self):
        """Multi-digit numbers should be assembled correctly."""
        self.ui.input_key_list = ['1', '2', '3']
        self.assertEqual(self.ui.get_input_string(), '123')

    def test_lowercase_letters(self):
        """All lowercase letters should be captured."""
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            self.ui.input_key_list = [letter]
            result = self.ui.get_input_string()
            self.assertEqual(result, letter, f"Letter '{letter}' was not captured")

    def test_uppercase_letters(self):
        """All uppercase letters should be captured."""
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            self.ui.input_key_list = [letter]
            result = self.ui.get_input_string()
            self.assertEqual(result, letter, f"Letter '{letter}' was not captured")

    def test_special_characters(self):
        """Common special characters used in time format etc."""
        for char in ':.-+/':
            self.ui.input_key_list = [char]
            result = self.ui.get_input_string()
            self.assertEqual(result, char, f"Character '{char}' was not captured")

    def test_space(self):
        """Space key should produce a space character."""
        self.ui.input_key_list = ['2', Key.SPACE, '1']
        self.assertEqual(self.ui.get_input_string(), '2 1')

    def test_enter_ignored_in_string(self):
        """Enter key in the list should not appear in the string."""
        self.ui.input_key_list = ['5', Key.ENTER]
        self.assertEqual(self.ui.get_input_string(), '5')

    def test_empty_input(self):
        """Empty key list should produce empty string."""
        self.ui.input_key_list = []
        self.assertEqual(self.ui.get_input_string(), '')

    def test_time_format(self):
        """Time format like 14:30 should be captured correctly."""
        self.ui.input_key_list = ['1', '4', ':', '3', '0']
        self.assertEqual(self.ui.get_input_string(), '14:30')

    def test_division_with_remainder_format(self):
        """Format '2 1' (quotient remainder) should work."""
        self.ui.input_key_list = ['2', Key.SPACE, '1']
        self.assertEqual(self.ui.get_input_string(), '2 1')


class TestHandleSpecialKey(unittest.TestCase):
    """Test that _handle_special_key correctly handles key events."""

    def setUp(self):
        with patch('smileymath.user_input.logging'):
            self.ui = UserInput(timeout=10)
        self.ui.input_key_list = []

    def test_char_key_appended(self):
        """Character keys should be stored directly in input_key_list."""
        # Simulate what _read_keys does for a regular character
        self.ui.input_key_list.append('7')
        self.assertEqual(len(self.ui.input_key_list), 1)
        self.assertEqual(self.ui.input_key_list[0], '7')

    def test_space_stored(self):
        """Space key should be stored."""
        self.ui._handle_special_key(Key.SPACE)
        self.assertEqual(len(self.ui.input_key_list), 1)
        self.assertEqual(self.ui.input_key_list[0], Key.SPACE)

    def test_backspace_removes_last(self):
        """Backspace should remove the last entry."""
        self.ui.input_key_list = ['1', '2']
        self.ui._handle_special_key(Key.BACKSPACE)
        self.assertEqual(len(self.ui.input_key_list), 1)
        self.assertEqual(self.ui.input_key_list[0], '1')

    def test_backspace_removes_first_char(self):
        """Backspace should be able to remove the only character."""
        self.ui.input_key_list = ['5']
        self.ui._handle_special_key(Key.BACKSPACE)
        self.assertEqual(len(self.ui.input_key_list), 0)

    def test_backspace_on_empty_does_nothing(self):
        """Backspace on empty list should not crash."""
        self.ui.input_key_list = []
        self.ui._handle_special_key(Key.BACKSPACE)
        self.assertEqual(len(self.ui.input_key_list), 0)

    def test_enter_with_valid_input_stops(self):
        """Enter with valid formatted input should return False (stop reading)."""
        self.ui.input_key_list = ['5']
        result = self.ui._handle_special_key(Key.ENTER)
        self.assertFalse(result)

    def test_enter_with_empty_input_resets(self):
        """Enter with empty/invalid input should reset the list."""
        # For IntUserInput, empty string is invalid
        with patch('smileymath.user_input.logging'):
            ui = IntUserInput(timeout=10)
        ui.input_key_list = []
        result = ui._handle_special_key(Key.ENTER)
        # Should return True (continue reading)
        self.assertTrue(result)

    def test_all_digits_stored(self):
        """All digits 0-9 should be storable."""
        for digit in '0123456789':
            self.ui.input_key_list.append(digit)
        self.assertEqual(len(self.ui.input_key_list), 10)
        result = self.ui.get_input_string()
        self.assertEqual(result, '0123456789')


class TestIntUserInputFormat(unittest.TestCase):
    """Test IntUserInput format validation."""

    def setUp(self):
        with patch('smileymath.user_input.logging'):
            self.ui = IntUserInput(timeout=10)

    def test_valid_int(self):
        """Valid integer string should parse."""
        result = self.ui.format_input('42')
        self.assertEqual(result, 42)

    def test_invalid_int(self):
        """Non-integer string should raise."""
        with self.assertRaises(ValueError):
            self.ui.format_input('abc')

    def test_check_format_valid(self):
        """check_format should return True for valid int."""
        self.assertTrue(self.ui.check_format('7'))

    def test_check_format_invalid(self):
        """check_format should return False for invalid input."""
        self.assertFalse(self.ui.check_format(''))
        self.assertFalse(self.ui.check_format('abc'))


class TestDoubleIntUserInputFormat(unittest.TestCase):
    """Test DoubleIntUserInput format validation."""

    def setUp(self):
        with patch('smileymath.user_input.logging'):
            self.ui = DoubleIntUserInput(timeout=10)

    def test_two_ints(self):
        """'2 1' should return (2, 1)."""
        result = self.ui.format_input('2 1')
        self.assertEqual(result, (2, 1))

    def test_single_int_assumes_zero_remainder(self):
        """'5' should return (5, 0)."""
        result = self.ui.format_input('5')
        self.assertEqual(result, (5, 0))

    def test_check_format_valid(self):
        """check_format should return True for valid input."""
        self.assertTrue(self.ui.check_format('3 2'))
        self.assertTrue(self.ui.check_format('7'))


if __name__ == '__main__':
    unittest.main()
