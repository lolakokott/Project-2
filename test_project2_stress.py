import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

from project2_portfolio import find_lowest_risk_mix
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
        self.assertIn("at least 10% BIL is 6.7500%, below the 7% objective", reason)

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


if __name__ == "__main__":
    unittest.main()
