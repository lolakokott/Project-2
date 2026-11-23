"""Historical estimates and mandate checks for FIN43900 Project 2."""

import csv
from datetime import date
from itertools import product
import math

import numpy as np
import pandas as pd

TICKERS = ("VT", "BIL", "QQQ", "IEF")
TARGET_RETURN = 0.07
MINIMUM_BIL = 0.10
BIL_INDEX = TICKERS.index("BIL")
EQUAL_WEIGHTS = (0.25, 0.25, 0.25, 0.25)
POLICY_WEIGHTS = (0.40, 0.10, 0.20, 0.30)
GRID_UNITS = 20
TOLERANCE = 1e-10


def load_monthly_returns(csv_text):
    """Validate CSV text and calculate simple monthly price returns."""
    try:
        rows = list(csv.reader(csv_text.removeprefix("\ufeff").splitlines(), strict=True))
    except csv.Error as error:
        raise ValueError(f"Malformed CSV ({error}).") from error

    header = rows[0] if rows else []
    if len(header) != 5 or header[0] != "Date" or set(header[1:]) != set(TICKERS):
        raise ValueError("Use a Date column followed by exactly VT, BIL, QQQ, and IEF.")

    dates = []
    prices = []
    previous_month = None
    for row in rows[1:]:
        if len(row) != len(header):
            raise ValueError("Every row must contain a date and four prices.")
        try:
            day = date.fromisoformat(row[0])
            if day.isoformat() != row[0]:
                raise ValueError
        except ValueError as error:
            raise ValueError("Dates must be valid YYYY-MM-DD values.") from error
        month = day.year * 12 + day.month
        if previous_month is not None and month != previous_month + 1:
            raise ValueError("Provide one observation per consecutive month in chronological order.")
        previous_month = month

        try:
            values = [float(value) for value in row[1:]]
        except ValueError as error:
            raise ValueError("All prices must be present and numeric.") from error
        if any(not math.isfinite(value) or value <= 0 for value in values):
            raise ValueError("All prices must be finite and strictly positive.")
        dates.append(pd.Timestamp(day))
        prices.append(values)

    if len(prices) < 3:
        raise ValueError("Provide at least three monthly prices per ticker to estimate risk.")
    frame = pd.DataFrame(prices, index=dates, columns=header[1:])
    monthly_returns = frame[list(TICKERS)].pct_change(fill_method=None).iloc[1:]
    if not np.isfinite(monthly_returns.to_numpy()).all():
        raise ValueError("Monthly returns must be finite.")
    return monthly_returns


def validate_correlations(matrix):
    matrix = np.asarray(matrix, dtype=float)
    if matrix.shape != (len(TICKERS), len(TICKERS)):
        raise ValueError("Correlation matrix must be 4 by 4.")
    if not np.isfinite(matrix).all() or np.any(np.abs(matrix) > 1):
        raise ValueError("Correlations must be finite and within [-1, 1].")
    if not np.allclose(matrix, matrix.T, rtol=0, atol=TOLERANCE):
        raise ValueError("Correlation matrix must be symmetric.")
    if not np.allclose(matrix.diagonal(), 1, rtol=0, atol=TOLERANCE):
        raise ValueError("Correlation matrix diagonal must equal 1.")
    if np.linalg.eigvalsh((matrix + matrix.T) / 2).min() < -TOLERANCE:
        raise ValueError("Correlation matrix must be positive semidefinite.")
    return matrix


def mandate_failures(weights, estimated_return, *, minimum_bil=MINIMUM_BIL, annual_cost=0):
    if len(weights) != len(TICKERS):
        return ["Provide one weight for each of VT, BIL, QQQ, and IEF."]
    if any(not math.isfinite(weight) for weight in weights):
        return ["All weights must be finite."]
    failures = []
    if any(not 0 <= weight <= 1 for weight in weights):
        failures.append("Each weight must be between 0% and 100%.")
    if not math.isclose(math.fsum(weights), 1, rel_tol=0, abs_tol=TOLERANCE):
        failures.append("Weights must sum to 100%.")
    if weights[BIL_INDEX] < minimum_bil:
        failures.append(f"BIL allocation is below the {minimum_bil * 100:g}% minimum.")
    if not math.isfinite(estimated_return):
        failures.append("Estimated annual return must be finite.")
    elif estimated_return - annual_cost < TARGET_RETURN:
        return_label = "net annual return" if annual_cost else "annual return"
        failures.append(f"Estimated {return_label} is below the 7% objective.")
    return failures


def estimate_inputs(monthly_returns):
    """Use arithmetic annualization and sample monthly standard deviations."""
    returns = monthly_returns.mean().to_numpy() * 12
    volatilities = monthly_returns.std().to_numpy() * math.sqrt(12)
    if not np.isfinite(returns).all() or not np.isfinite(volatilities).all():
        raise ValueError("Annualized returns and volatilities must be finite.")
    # Estimation can put perfect correlations just outside the bounds by roundoff.
    correlations = validate_correlations(monthly_returns.corr().clip(-1, 1).to_numpy())
    with np.errstate(over="ignore", invalid="ignore"):
        covariance = correlations * np.outer(volatilities, volatilities)
    if not np.isfinite(covariance).all():
        raise ValueError("Annualized covariance must be finite.")
    return returns, covariance


def evaluate_portfolio(weights, returns, covariance, *, minimum_bil=MINIMUM_BIL, annual_cost=0):
    expected = math.fsum(weight * float(rate) for weight, rate in zip(weights, returns))
    failures = mandate_failures(
        weights, expected, minimum_bil=minimum_bil, annual_cost=annual_cost
    )
    if len(weights) != len(TICKERS) or any(
        not math.isfinite(weight) or not 0 <= weight <= 1 for weight in weights
    ):
        raise ValueError(failures[0])
    with np.errstate(over="ignore", invalid="ignore"):
        variance = float(np.asarray(weights) @ covariance @ np.asarray(weights))
    if not math.isfinite(variance) or not math.isfinite(expected):
        raise ValueError("Portfolio annualized return and volatility must be finite.")
    return {
        "weights": weights,
        "return": expected,  # Gross return, retained for historical callers.
        "net_return": expected - annual_cost,
        "volatility": math.sqrt(max(variance, 0.0)),
        "reserve": weights[BIL_INDEX],
        "failures": failures,
    }


def find_lowest_risk_mix(returns, covariance, *, minimum_bil=MINIMUM_BIL, annual_cost=0):
    best = None
    for units in product(range(GRID_UNITS + 1), repeat=len(TICKERS)):
        if sum(units) != GRID_UNITS or units[BIL_INDEX] / GRID_UNITS < minimum_bil:
            continue
        weights = tuple(unit / GRID_UNITS for unit in units)
        candidate = evaluate_portfolio(
            weights, returns, covariance, minimum_bil=minimum_bil, annual_cost=annual_cost
        )
        if not candidate["failures"] and (
            best is None or candidate["volatility"] < best["volatility"]
        ):
            best = candidate
    return best
