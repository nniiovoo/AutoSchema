"""Reported-value notation and quote boundaries in the Task 3 selector."""
from decimal import Decimal
import unittest

from polymer_cards_lib.validation import _literal
from selection_lib.screening import _parse_raw_value, _unit_key


class RawValueNotationTests(unittest.TestCase):
    def parsed(self, raw):
        result = _parse_raw_value(raw)
        self.assertIsNotNone(result, raw)
        mean, deviation, unit = result
        return mean, deviation, _unit_key(unit)

    def test_multiplication_and_exponent_notation_is_exact(self):
        cases = {
            "2.4 × 10−4 S cm−1": (Decimal("0.00024"), "S/cm"),
            "6.5 × 10−5 S cm−1": (Decimal("0.000065"), "S/cm"),
            "2.56 × 10−3 S·cm−1": (Decimal("0.00256"), "S/cm"),
            "1.2 × 10⁻⁴ S cm⁻¹": (Decimal("0.00012"), "S/cm"),
            "3.4×10^-5 S/cm": (Decimal("0.000034"), "S/cm"),
            "3.4 x 10-5 S/cm": (Decimal("0.000034"), "S/cm"),
            "1.2e−4 S/cm": (Decimal("0.00012"), "S/cm"),
            "1.2E-4 S/cm": (Decimal("0.00012"), "S/cm"),
            "−5 °C": (Decimal("-5"), "°C"),
            "95%": (Decimal("95"), "%"),
        }
        for raw, (value, unit) in cases.items():
            with self.subTest(raw=raw):
                mean, deviation, parsed_unit = self.parsed(raw)
                self.assertEqual(value, mean)
                self.assertIsNone(deviation)
                self.assertEqual(unit, parsed_unit)

    def test_ambiguous_forms_are_not_scaled(self):
        # "× 10" without a caret or sign is not an exponent; it stays in the unit and fails review.
        mean, _dev, unit = self.parsed("2 × 10 mm")
        self.assertEqual(Decimal("2"), mean)
        self.assertNotEqual("mm", unit)
        # A bare power of ten is not read as 1e-4.
        mean, _dev, unit = self.parsed("10-4 S/cm")
        self.assertEqual(Decimal("10"), mean)
        self.assertNotEqual("S/cm", unit)
        # Scaled value with a deviation, and absurd exponents, need review.
        self.assertIsNone(_parse_raw_value("2.4 × 10−4 ± 0.3 S/cm"))
        self.assertIsNone(_parse_raw_value("1 × 10^150 S/cm"))

    def test_deviation_still_parsed(self):
        mean, deviation, unit = self.parsed("90 ± 3%")
        self.assertEqual((Decimal("90"), Decimal("3"), "%"), (mean, deviation, unit))

    def test_unit_aliases_are_explicit(self):
        self.assertEqual("S/cm", _unit_key("S cm−1"))
        self.assertEqual("mS/cm", _unit_key("mS cm⁻¹"))
        self.assertEqual("S/cm", _unit_key("S/cm"))
        self.assertNotEqual(_unit_key("S/cm"), _unit_key("mS/cm"))


class RawValueQuoteBoundaryTests(unittest.TestCase):
    def test_value_ending_a_sentence_is_found(self):
        self.assertTrue(_literal("95%", "The recovery of P-A was 95%."))
        self.assertTrue(_literal("0.40 MPa", "Strength was 0.40 MPa."))
        self.assertTrue(_literal("2.4 × 10−4 S cm−1", "σ was 2.4 × 10−4 S cm−1."))

    def test_fragments_of_a_larger_number_are_rejected(self):
        self.assertFalse(_literal("400 MPa", "The modulus was 1,400 MPa."))
        self.assertFalse(_literal("3%", "Recovery was 90 ± 3%."))
        self.assertFalse(_literal("95%", "Recovery was >95%."))
        self.assertFalse(_literal("4 S/cm", "It reached 2,4 S/cm."))


if __name__ == "__main__":
    unittest.main()
