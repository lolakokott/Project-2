"""Return-only portfolio scenarios for FIN43900 Project 2."""

from project2_portfolio import (
    BIL_INDEX,
    MINIMUM_BIL,
    TARGET_RETURN,
    TICKERS,
    evaluate_portfolio,
    find_lowest_risk_mix,
)


def run_stress(baseline, expected_returns, covariance):
    """Evaluate the original weights and independently search the mandate grid."""
    fixed = (
        evaluate_portfolio(baseline["weights"], expected_returns, covariance)
        if baseline is not None else None
    )
    optimized = find_lowest_risk_mix(expected_returns, covariance)
    if optimized is not None:
        return fixed, optimized, None

    # The highest-return mix puts all discretionary weight in the highest-return
    # ETF. The mandate's BIL floor is itself a point on the 5% grid.
    highest = max(range(len(TICKERS)), key=expected_returns.__getitem__)
    weights = [0.0] * len(TICKERS)
    weights[BIL_INDEX] = MINIMUM_BIL
    weights[highest] += 1 - MINIMUM_BIL
    ceiling = evaluate_portfolio(weights, expected_returns, covariance)["return"]
    return fixed, None, (
        f"The highest annual return possible on the 5% grid with at least "
        f"{MINIMUM_BIL:.0%} BIL is {ceiling:.4%}, below the {TARGET_RETURN:.0%} objective."
    )
