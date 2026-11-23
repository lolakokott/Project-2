"""Point-in-time DGS10 monitoring for FIN43900 Project 2."""

from datetime import date
import math

import pandas as pd
import requests

from asof_app import download_asof, last_observation

DEFAULT_DECISION_DATE = date(2026, 9, 30)


def load_dgs10(decision_date: date) -> tuple[date | None, float | None, str | None]:
    """Return observation date, yield in percent, and any unavailability reason."""
    try:
        vintage = download_asof("DGS10", decision_date, date.today())
    except requests.RequestException:
        return None, None, "The ALFRED vintage download failed."
    except ValueError:
        return None, None, "ALFRED returned unreadable vintage data."

    eligible = vintage.loc[vintage.index <= pd.Timestamp(decision_date)]
    observation_date, value = last_observation(eligible)
    if value is None:
        return None, None, "The ALFRED vintage has no measured values through the decision date."
    if not math.isfinite(value):
        return None, None, "The latest eligible ALFRED value is invalid."
    return observation_date, value, None
