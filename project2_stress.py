"""Portfolio stress scenarios for FIN43900 Project 2."""

import math

from project2_portfolio import (
    BIL_INDEX,
    GRID_UNITS,
    MINIMUM_BIL,
    TARGET_RETURN,
    TICKERS,
    evaluate_portfolio,
    find_lowest_risk_mix,
)


def run_stress(
    baseline, expected_returns, covariance, *,
    cost_bps=0, minimum_bil_pct=MINIMUM_BIL * 100,
):
    """Evaluate the original weights and independently search the mandate grid."""
    if not math.isfinite(cost_bps) or cost_bps < 0:
        raise ValueError("Annual portfolio cost must be finite and nonnegative.")
    if not 0 <= minimum_bil_pct <= 100:
        raise ValueError("The stressed BIL minimum must be between 0% and 100%.")
    if len(expected_returns) != len(TICKERS) or not all(map(math.isfinite, expected_returns)):
        raise ValueError("Provide one finite expected return per ETF.")

    annual_cost = cost_bps / 10_000
    minimum_bil = minimum_bil_pct / 100
    fixed = (
        evaluate_portfolio(
            baseline["weights"], expected_returns, covariance,
            minimum_bil=minimum_bil, annual_cost=annual_cost,
        )
        if baseline is not None else None
    )
    optimized = find_lowest_risk_mix(
        expected_returns, covariance, minimum_bil=minimum_bil, annual_cost=annual_cost
    )
    if optimized is not None:
        return fixed, optimized, None

    # Put all discretionary units into the highest-return ETF after meeting the
    # BIL floor at the first eligible grid weight.
    highest = max(range(len(TICKERS)), key=expected_returns.__getitem__)
    reserve_units = next(
        units for units in range(GRID_UNITS + 1) if units / GRID_UNITS >= minimum_bil
    )
    units = [0] * len(TICKERS)
    units[BIL_INDEX] = reserve_units
    units[highest] += GRID_UNITS - reserve_units
    weights = [weight_units / GRID_UNITS for weight_units in units]
    ceiling = evaluate_portfolio(
        weights, expected_returns, covariance, annual_cost=annual_cost
    )["net_return"]
    return fixed, None, (
        f"The highest estimated net annual return on the 5% grid with at least "
        f"{minimum_bil_pct:g}% BIL is {ceiling:.4%} after {cost_bps:g} bps of annual cost. "
        f"This falls below the {TARGET_RETURN:.0%} net return objective."
    )
