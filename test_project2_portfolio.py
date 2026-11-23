import unittest

import numpy as np

from project2_portfolio import (
    find_lowest_risk_mix,
    load_monthly_returns,
    mandate_failures,
    validate_correlations,
)

VALID_CSV = """Date,VT,BIL,QQQ,IEF
2024-01-31,100,100,100,100
2024-02-29,105,101,107,99
2024-03-31,103,103,108,102
"""


class PortfolioTests(unittest.TestCase):
    def test_mandate_boundaries_and_failures(self):
        self.assertEqual(mandate_failures((0.4, 0.1, 0.2, 0.3), 0.07), [])
        failures = mandate_failures((-0.10, 0.05, 1.10, 0.25), 0.0699)
        for phrase in ("between 0%", "sum to 100%", "BIL allocation", "7% objective"):
            self.assertTrue(any(phrase in reason for reason in failures), failures)
        self.assertTrue(mandate_failures((0.4, 0.1, 0.2, 0.3), float("nan")))

    def test_valid_csv_returns(self):
        returns = load_monthly_returns(VALID_CSV)
        self.assertEqual(returns.shape, (2, 4))
        self.assertAlmostEqual(returns.iloc[0]["VT"], 0.05)

    def test_invalid_csv(self):
        invalid_cases = {
            "wrong ticker": VALID_CSV.replace("QQQ", "SPY"),
            "duplicate ticker": VALID_CSV.replace("QQQ", "VT"),
            "invalid date": VALID_CSV.replace("2024-02-29", "2024-02-30"),
            "duplicate date": VALID_CSV.replace("2024-02-29", "2024-01-31"),
            "duplicate month": VALID_CSV.replace("2024-02-29", "2024-01-30"),
            "gap": VALID_CSV.replace("2024-03-31", "2024-04-30"),
            "out of order": VALID_CSV.replace("2024-01-31", "2024-04-30"),
            "missing": VALID_CSV.replace(",105,", ",,"),
            "nonnumeric": VALID_CSV.replace(",105,", ",oops,"),
            "zero": VALID_CSV.replace(",105,", ",0,"),
            "negative": VALID_CSV.replace(",105,", ",-1,"),
            "infinite": VALID_CSV.replace(",105,", ",inf,"),
            "extra field": VALID_CSV.replace(",107,99", ",107,99,12"),
        }
        for label, csv_text in invalid_cases.items():
            with self.subTest(label=label), self.assertRaises(ValueError):
                load_monthly_returns(csv_text)

    def test_invalid_correlations(self):
        indefinite = np.full((4, 4), -0.5)
        np.fill_diagonal(indefinite, 1)
        asymmetric = np.eye(4)
        asymmetric[0, 1] = 0.5
        outside_range = np.eye(4)
        outside_range[0, 1] = outside_range[1, 0] = 1.01
        for matrix in (indefinite, asymmetric, outside_range, np.eye(4) * 0.5):
            with self.assertRaises(ValueError):
                validate_correlations(matrix)
        validate_correlations(np.ones((4, 4)))

    def test_optimizer_finds_minimum_volatility_feasible_grid_mix(self):
        # Only VT earns enough to reach the target with a 70% VT allocation.
        # BIL has zero risk, so additional VT increases volatility.
        result = find_lowest_risk_mix(
            [0.101, 0.0, 0.0, 0.0], np.diag([0.04, 0.0, 0.01, 0.01])
        )
        self.assertEqual(result["weights"], (0.7, 0.3, 0.0, 0.0))
        self.assertEqual(result["failures"], [])
        self.assertAlmostEqual(result["volatility"], 0.14)

    def test_optimizer_returns_none_when_bil_floor_makes_target_infeasible(self):
        self.assertIsNone(find_lowest_risk_mix([0.075, 0.0, 0.0, 0.0], np.eye(4)))


if __name__ == "__main__":
    unittest.main()
