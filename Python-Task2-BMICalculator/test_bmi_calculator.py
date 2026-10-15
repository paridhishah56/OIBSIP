import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from bmi_calculator import calculate_bmi, classify_bmi, get_positive_number


class BMICalculatorTests(unittest.TestCase):
    def test_calculates_bmi(self):
        self.assertAlmostEqual(calculate_bmi(70, 1.75), 70 / (1.75 ** 2))

    def test_classifies_all_bmi_categories(self):
        examples = [
            (18.49, "Underweight"),
            (18.5, "Normal"),
            (24.99, "Normal"),
            (25, "Overweight"),
            (29.99, "Overweight"),
            (30, "Obese"),
        ]

        for bmi, expected_category in examples:
            with self.subTest(bmi=bmi):
                self.assertEqual(classify_bmi(bmi), expected_category)

    def test_rejects_non_numeric_weight_and_height(self):
        invalid_values = [
            ("not a number", 1.75),
            (70, "not a number"),
        ]

        for weight, height in invalid_values:
            with self.subTest(weight=weight, height=height):
                with self.assertRaises(ValueError):
                    calculate_bmi(weight, height)

    def test_rejects_zero_and_negative_weight_or_height(self):
        invalid_values = [
            (0, 1.75),
            (-70, 1.75),
            (70, 0),
            (70, -1.75),
        ]

        for weight, height in invalid_values:
            with self.subTest(weight=weight, height=height):
                with self.assertRaises(ValueError):
                    calculate_bmi(weight, height)

    def test_retries_invalid_input_until_a_positive_number_is_entered(self):
        output = io.StringIO()

        with patch("builtins.input", side_effect=["abc", "0", "-2", "65"]):
            with redirect_stdout(output):
                value = get_positive_number("Weight: ", "Weight")

        self.assertEqual(value, 65)
        self.assertIn("Weight must be a number", output.getvalue())
        self.assertIn("Weight must be greater than zero", output.getvalue())


if __name__ == "__main__":
    unittest.main()