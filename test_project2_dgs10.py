import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch

import requests
from streamlit.testing.v1 import AppTest

from asof_app import download_asof
from project2_dgs10 import DEFAULT_DECISION_DATE, load_dgs10


class Dgs10Tests(unittest.TestCase):
    def setUp(self):
        download_asof.clear()
        self.addCleanup(download_asof.clear)
        request = patch("asof_app.requests.get")
        self.get = request.start()
        self.addCleanup(request.stop)

    def set_vintage(self, rows):
        self.get.return_value = Mock(text="observation_date,DGS10_20260930\n" + rows)

    def test_excludes_observations_measured_after_decision_date(self):
        self.set_vintage("2026-10-01,9.99\n2026-09-30,5.25\n2026-09-29,5.26\n")
        self.assertEqual(load_dgs10(DEFAULT_DECISION_DATE), (date(2026, 9, 30), 5.25, None))

    def test_empty_vintages(self):
        for rows in ("", "2026-09-29,.\n", "2026-10-01,9.99\n"):
            with self.subTest(rows=rows):
                download_asof.clear()
                self.set_vintage(rows)
                observed, value, reason = load_dgs10(DEFAULT_DECISION_DATE)
                self.assertIsNone(observed)
                self.assertIsNone(value)
                self.assertIn("no measured values", reason)

    def test_selects_only_from_requested_alfred_vintage(self):
        self.set_vintage("2026-09-29,5.26\n2026-09-28,5.30\n2026-09-30,.\n")
        self.assertEqual(load_dgs10(DEFAULT_DECISION_DATE), (date(2026, 9, 29), 5.26, None))
        self.get.assert_called_once_with(
            "https://alfred.stlouisfed.org/graph/alfredgraph.csv",
            params={"id": "DGS10", "vintage_date": "2026-09-30"},
            timeout=30,
        )

    def test_network_failure_shows_reason_and_preserves_portfolio_display(self):
        self.get.side_effect = requests.ConnectionError("offline")
        self.assertEqual(
            load_dgs10(DEFAULT_DECISION_DATE), (None, None, "The ALFRED vintage download failed.")
        )
        self.get.reset_mock()
        app = AppTest.from_file(str(Path(__file__).with_name("project2_app.py"))).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.date_input[0].value, DEFAULT_DECISION_DATE)
        self.assertFalse(app.metric)
        self.assertTrue(any("DGS10 not available" in warning.value for warning in app.warning))
        self.assertIn("Full window", [heading.value for heading in app.subheader])
        self.get.assert_called_once()


if __name__ == "__main__":
    unittest.main()
