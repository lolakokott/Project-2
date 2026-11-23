import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

from project2_portfolio import estimate_inputs, find_lowest_risk_mix, load_monthly_returns
from project2_stress import run_stress


class StressTests(unittest.TestCase):
    def setUp(self):
        self.covariance = np.diag([0.04, 0.0, 0.01, 0.01])
        self.historical = [0.101, 0.0, 0.0, 0.0]
        self.baseline = find_lowest_risk_mix(self.historical, self.covariance)

    def test_fixed_weight_stress_keeps_allocation_reserve_and_volatility(self):
        fixed, _, _ = run_stress(self.baseline, [0.0, 0.0, 0.101, 0.0], self.covariance)
        self.assertEqual(fixed["weights"], (0.70, 0.30, 0.0, 0.0))
        self.assertEqual(fixed["volatility"], self.baseline["volatility"])
        self.assertEqual(fixed["reserve"], self.baseline["reserve"])
        self.assertEqual(fixed["return"], 0.0)
        self.assertIn("Estimated annual return is below the 7% objective.", fixed["failures"])
        self.assertAlmostEqual(self.baseline["return"], 0.0707)

    def test_reoptimization_finds_lowest_risk_feasible_scenario_mix(self):
        _, optimized, reason = run_stress(
            self.baseline, [0.0, 0.0, 0.101, 0.0], self.covariance
        )
        self.assertEqual(optimized["weights"], (0.0, 0.30, 0.70, 0.0))
        self.assertAlmostEqual(optimized["return"], 0.0707)
        self.assertAlmostEqual(optimized["volatility"], 0.07)
        self.assertEqual(optimized["failures"], [])
        self.assertIsNone(reason)

    def test_infeasibility_explains_the_return_ceiling_with_bil_floor(self):
        fixed, optimized, reason = run_stress(
            self.baseline, [0.075, 0.0, 0.0, 0.0], self.covariance
        )
        self.assertIsNone(optimized)
        self.assertTrue(fixed["failures"])
        self.assertIn("at least 10% BIL is 6.7500%", reason)
        self.assertIn("below the 7% net return objective", reason)

    def test_real_price_windows_keep_baselines_and_qqq_only_results_at_defaults(self):
        monthly = load_monthly_returns(Path(__file__).with_name("prices.csv").read_text())
        # Pre-change outputs using the bundled prices and a 10% QQQ-only override.
        cases = [
            (monthly, (0.05, 0.70, 0.25, 0.0), 0.07122606249718694,
             (0.50, 0.50, 0.0, 0.0), 0.05612701294235587, 0.07353822067776516),
            (monthly.tail(36), (0.10, 0.85, 0.05, 0.0), 0.07055364129971729,
             (0.20, 0.80, 0.0, 0.0), 0.06235787008619084, 0.0754220374473485),
        ]
        for window, baseline_weights, baseline_return, weights, fixed_return, result_return in cases:
            with self.subTest(months=len(window)):
                returns, covariance = estimate_inputs(window)
                baseline = find_lowest_risk_mix(returns, covariance)
                self.assertEqual(baseline["weights"], baseline_weights)
                self.assertAlmostEqual(baseline["return"], baseline_return)
                self.assertEqual(run_stress(baseline, returns, covariance), (baseline, baseline, None))

                stressed = returns.copy()
                stressed[2] = 0.10
                fixed, optimized, reason = run_stress(
                    baseline, stressed, covariance, cost_bps=0, minimum_bil_pct=10
                )
                self.assertEqual(fixed["weights"], baseline_weights)
                self.assertAlmostEqual(fixed["return"], fixed_return)
                self.assertEqual(fixed["return"], fixed["net_return"])
                self.assertTrue(fixed["failures"])
                self.assertEqual(optimized["weights"], weights)
                self.assertAlmostEqual(optimized["return"], result_return)
                self.assertEqual(optimized["return"], optimized["net_return"])
                self.assertFalse(optimized["failures"])
                self.assertIsNone(reason)

    def test_cost_deducts_flat_amount_and_changes_optimizer_choice(self):
        fixed, optimized, reason = run_stress(
            self.baseline, self.historical, self.covariance, cost_bps=50
        )
        self.assertEqual(fixed["return"], self.baseline["return"])
        self.assertEqual(fixed["volatility"], self.baseline["volatility"])
        self.assertAlmostEqual(fixed["net_return"], fixed["return"] - 0.005)
        self.assertIn("Estimated net annual return is below the 7% objective.", fixed["failures"])
        self.assertEqual(optimized["weights"], (0.75, 0.25, 0.0, 0.0))
        self.assertGreaterEqual(optimized["net_return"], 0.07)
        self.assertFalse(optimized["failures"])
        self.assertIsNone(reason)

    def test_tighter_off_grid_reserve_changes_optimizer_choice(self):
        returns, covariance = [0.10, 0.06, 0.10, 0.10], np.eye(4)
        baseline = find_lowest_risk_mix(returns, covariance)
        fixed, optimized, reason = run_stress(
            baseline, returns, covariance, minimum_bil_pct=42
        )
        self.assertEqual(fixed["reserve"], 0.25)
        self.assertIn("BIL allocation is below the 42% minimum.", fixed["failures"])
        self.assertEqual(optimized["reserve"], 0.45)
        self.assertFalse(optimized["failures"])
        self.assertIsNone(reason)

    def test_infeasibility_accounts_for_cost_and_grid_reserve_together(self):
        returns = [0.09, 0, 0, 0]
        for cost, minimum in ((50, 10), (0, 16)):
            _, optimized, _ = run_stress(
                self.baseline, returns, self.covariance,
                cost_bps=cost, minimum_bil_pct=minimum,
            )
            self.assertIsNotNone(optimized)

        _, optimized, reason = run_stress(
            self.baseline, returns, self.covariance,
            cost_bps=50, minimum_bil_pct=16,
        )
        self.assertIsNone(optimized)
        self.assertIn("at least 16% BIL is 6.7000% after 50 bps", reason)

    def test_stress_input_validation(self):
        invalid = [
            {"cost_bps": -1}, {"cost_bps": float("inf")}, {"cost_bps": float("nan")},
            {"minimum_bil_pct": -1}, {"minimum_bil_pct": 101},
            {"minimum_bil_pct": float("nan")},
        ]
        for values in invalid:
            with self.subTest(values=values), self.assertRaises(ValueError):
                run_stress(self.baseline, self.historical, self.covariance, **values)

    def test_bil_minimum_accepts_both_endpoints(self):
        returns, covariance = [0.10, 0.10, 0.10, 0.10], np.eye(4)
        for minimum, expected_reserve in ((0, 0.25), (100, 1.0)):
            with self.subTest(minimum=minimum):
                _, optimized, reason = run_stress(
                    None, returns, covariance, minimum_bil_pct=minimum
                )
                self.assertEqual(optimized["reserve"], expected_reserve)
                self.assertIsNone(reason)

    def test_scenario_can_optimize_when_historical_baseline_is_infeasible(self):
        fixed, optimized, reason = run_stress(None, self.historical, self.covariance)
        self.assertIsNone(fixed)
        self.assertEqual(optimized, self.baseline)
        self.assertIsNone(reason)

    def test_streamlit_form_compares_both_windows_and_preserves_baseline(self):
        monthly = pd.DataFrame(index=pd.date_range("2020-01-01", periods=37, freq="MS"))

        def synthetic_inputs(window):
            returns = self.historical if len(window) == 37 else [0.081, 0.0, 0.0, 0.0]
            return returns, self.covariance

        app_path = Path(__file__).with_name("project2_app.py")
        with (
            patch("project2_portfolio.load_monthly_returns", return_value=monthly),
            patch("project2_portfolio.estimate_inputs", side_effect=synthetic_inputs),
            patch("project2_dgs10.load_dgs10", return_value=(None, None, "Offline test")),
        ):
            app = AppTest.from_file(str(app_path)).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.number_input[4].value, 0)
            self.assertEqual(app.number_input[5].value, 10)
            baseline = [item.value for item in app.markdown]
            self.assertNotIn("Full window scenario", [item.value for item in app.subheader])

            app.number_input[3].set_value(10.1)
            app.button[0].click().run()
            self.assertFalse(app.exception)
            headings = [item.value for item in app.subheader]
            self.assertIn("Full window scenario", headings)
            self.assertIn("Last 36 months scenario", headings)
            scenario = [item.value for item in app.markdown]
            self.assertEqual(scenario[:len(baseline)], baseline)
            self.assertTrue(any("IEF 0.0000% → 10.1000%" in value for value in scenario))

            app.number_input[0].set_value(7.5)
            app.number_input[3].set_value(None)
            app.button[0].click().run()
            self.assertFalse(app.exception)
            warnings = [item.value for item in app.warning if "INFEASIBLE" in item.value]
            self.assertEqual(len(warnings), 2)
            self.assertTrue(all("6.7500%" in warning for warning in warnings))

            app.number_input[4].set_value(100)
            app.number_input[5].set_value(12)
            app.button[0].click().run()
            self.assertFalse(app.exception)
            warnings = [item.value for item in app.warning if "INFEASIBLE" in item.value]
            self.assertEqual(len(warnings), 2)
            self.assertTrue(all("5.3750% after 100 bps" in warning for warning in warnings))
            self.assertFalse(any("net annual return" in item.value for item in app.success))
            scenario = [item.value for item in app.markdown]
            self.assertEqual(scenario[:len(baseline)], baseline)
            self.assertTrue(any(
                "Estimated gross annual return" in value and "Estimated net annual return" in value
                for value in scenario
            ))


if __name__ == "__main__":
    unittest.main()
