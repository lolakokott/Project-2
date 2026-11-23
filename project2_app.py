"""Streamlit entry point for the FIN43900 Project 2 application."""

from datetime import date
from pathlib import Path

import streamlit as st

from project2_dgs10 import DEFAULT_DECISION_DATE, load_dgs10
from project2_portfolio import (
    EQUAL_WEIGHTS,
    POLICY_WEIGHTS,
    TICKERS,
    estimate_inputs,
    evaluate_portfolio,
    find_lowest_risk_mix,
    load_monthly_returns,
)
from project2_stress import run_stress

LOCAL_PRICES = Path(__file__).resolve().with_name("prices.csv")


def display_portfolio(label, result):
    st.markdown(f"**{label}**")
    if result is None:
        st.warning("Mandate FAIL — no 5% grid allocation meets all mandate requirements.")
        return

    st.write(" · ".join(
        f"{ticker} {weight:.0%}" for ticker, weight in zip(TICKERS, result["weights"])
    ))
    st.write(
        f"Estimated annual return **{result['return']:.2%}** · "
        f"Annualized volatility **{result['volatility']:.2%}** · "
        f"BIL reserve **{result['reserve']:.0%}**"
    )
    if result["failures"]:
        st.warning("Mandate FAIL — " + " ".join(result["failures"]))
    else:
        st.success(
            "Mandate PASS — Estimated annual return is at least 7%, BIL is at least "
            "10%, and long-only weights total 100%."
        )


def display_window(label, monthly_returns):
    st.subheader(label)
    st.caption(
        f"{len(monthly_returns)} monthly returns, "
        f"{monthly_returns.index[0]:%b %Y} through {monthly_returns.index[-1]:%b %Y}"
    )
    try:
        returns, covariance = estimate_inputs(monthly_returns)
        equal = evaluate_portfolio(EQUAL_WEIGHTS, returns, covariance)
        policy = evaluate_portfolio(POLICY_WEIGHTS, returns, covariance)
        optimized = find_lowest_risk_mix(returns, covariance)
    except ValueError as error:
        st.error(f"Estimates unavailable. {error}")
        return None

    display_portfolio("Equal weight", equal)
    display_portfolio("Custom 60/40 benchmark (chosen policy benchmark)", policy)
    display_portfolio("Lowest-volatility feasible mix", optimized)
    return returns, covariance, optimized


def display_largest_change(baseline, comparison, unavailable_message):
    if baseline is None or comparison is None:
        st.info(unavailable_message)
        return

    changes = [
        round(abs(new - original) * 100)
        for original, new in zip(baseline["weights"], comparison["weights"])
    ]
    largest = max(changes)
    if largest == 0:
        st.write("0 percentage points across all tickers.")
    else:
        tickers = ", ".join(ticker for ticker, change in zip(TICKERS, changes) if change == largest)
        st.write(f"**{largest} percentage points** ({tickers})")


def display_stress_window(label, window, overrides):
    st.subheader(label)
    if window is None:
        st.info("Historical estimates are unavailable for this window.")
        return

    returns, covariance, baseline = window
    stressed_returns = [
        historical if override is None else override / 100
        for historical, override in zip(returns, overrides)
    ]
    st.write("Annual return assumptions used")
    st.write(" · ".join(
        f"{ticker} {historical:.4%} → {stressed:.4%}"
        for ticker, historical, stressed in zip(TICKERS, returns, stressed_returns)
    ))
    try:
        fixed, optimized, infeasible_reason = run_stress(baseline, stressed_returns, covariance)
    except ValueError as error:
        st.error(f"Scenario unavailable. {error}")
        return

    display_portfolio("Historical optimized baseline", baseline)
    if fixed is None:
        st.info("Fixed-weight scenario unavailable because there is no historical optimized mix.")
    else:
        display_portfolio("Scenario at original weights", fixed)

    if optimized is None:
        st.markdown("**Reoptimized scenario**")
        st.warning(f"INFEASIBLE — {infeasible_reason}")
    else:
        display_portfolio("Reoptimized scenario", optimized)

    st.markdown("**Largest weight change from baseline to reoptimized scenario**")
    display_largest_change(
        baseline, optimized, "Both optimizations need a feasible allocation to compare weights."
    )
    return optimized


def display_stress(full, recent):
    st.header("Portfolio stress testing")
    st.caption(
        "Hypothetical scenarios, not forecasts. Each window uses its historical covariance "
        "for baseline and scenario volatility. Volatility changes only when the allocation changes."
    )
    with st.form("portfolio_stress"):
        st.write(
            "Enter annual expected returns in percent. Blank fields use each window’s historical "
            "estimate. Overrides apply to both windows."
        )
        overrides = [
            column.number_input(
                f"{ticker} annual return (%)",
                value=None,
                step=0.1,
                format="%.4f",
                help=(
                    "Optional interest-rate scenario motivated by DGS10. Enter your own IEF "
                    "return assumption. DGS10 does not supply an IEF forecast."
                    if ticker == "IEF" else None
                ),
            )
            for ticker, column in zip(TICKERS, st.columns(len(TICKERS)))
        ]
        submitted = st.form_submit_button("Run hypothetical scenario")

    if submitted:
        st.session_state["portfolio_stress_returns"] = overrides
    if "portfolio_stress_returns" not in st.session_state:
        return

    full_column, recent_column = st.columns(2)
    with full_column:
        full_optimized = display_stress_window(
            "Full window scenario", full, st.session_state["portfolio_stress_returns"]
        )
    with recent_column:
        recent_optimized = display_stress_window(
            "Last 36 months scenario", recent, st.session_state["portfolio_stress_returns"]
        )
    st.subheader("Largest reoptimized weight difference across windows")
    display_largest_change(
        full_optimized, recent_optimized,
        "Both windows need a feasible scenario allocation to compare weights.",
    )


def display_dgs10():
    st.subheader("DGS10 monitoring · 10-year Treasury yield")
    decision_date = st.date_input(
        "DGS10 historical decision date",
        value=DEFAULT_DECISION_DATE,
        min_value=date(1776, 1, 1),
        max_value=date.today(),
    )
    with st.spinner("Loading the ALFRED vintage…"):
        observation_date, value, reason = load_dgs10(decision_date)
    if reason:
        st.warning(f"DGS10 not available. {reason}")
    else:
        st.metric("Latest as-of yield", f"{value:.2f}%")
        st.write(f"Observation date · {observation_date:%B %d, %Y}")

    with st.container(border=True):
        st.markdown("**DGS10 data card**")
        st.markdown(
            "Source · Federal Reserve Board H.15 Selected Interest Rates via "
            "[FRED](https://fred.stlouisfed.org/series/DGS10) and "
            "[ALFRED](https://alfred.stlouisfed.org/series?seid=DGS10)."
        )
        st.write("Units · Percent per annum, unadjusted for seasonality.")
        st.write("Frequency · Business-day daily, generally published the following business day.")
        st.write(
            "Vintage limitations · ALFRED shows the archived values available for the "
            "selected date at daily resolution. Release timing can vary, and later vintages "
            "can incorporate revisions. Selection excludes observations measured after the decision date."
        )
        st.write(
            "DGS10 motivates a later interest-rate stress test for IEF and is not an IEF forecast. "
            "ETF return estimates and portfolio weights are calculated independently of this signal."
        )


def main():
    st.set_page_config(page_title="FIN43900 Project 2", layout="wide")
    st.title("Investment Management Application")
    st.caption("FIN43900 Project 2")
    st.write(
        "Minimize annualized volatility on a 5% grid while targeting at least "
        "7% estimated annual return and holding at least 10% in BIL. "
        "Long-only allocations must total 100%."
    )
    st.caption("Historical estimates are backward-looking and do not forecast future returns or volatility.")
    display_dgs10()
    st.header("ETF portfolio estimates")
    upload = st.sidebar.file_uploader("Upload an optional price CSV", type="csv")
    st.sidebar.caption("Use Date (YYYY-MM-DD), VT, BIL, QQQ, and IEF with one row per consecutive month.")
    try:
        csv_text = (
            upload.getvalue().decode("utf-8-sig") if upload is not None
            else LOCAL_PRICES.read_text(encoding="utf-8-sig")
        )
        monthly_returns = load_monthly_returns(csv_text)
    except (OSError, ValueError) as error:
        st.error(f"Unable to load prices. {error}")
        return

    st.caption(f"Price source · {upload.name if upload is not None else LOCAL_PRICES.name}")
    full_column, recent_column = st.columns(2)
    with full_column:
        full = display_window("Full window", monthly_returns)
    with recent_column:
        recent = None
        if len(monthly_returns) >= 36:
            recent = display_window("Last 36 months", monthly_returns.tail(36))
        else:
            st.subheader("Last 36 months")
            st.info("This comparison requires 36 monthly returns (37 monthly price rows).")

    st.subheader("Largest optimized allocation change")
    display_largest_change(
        full[2] if full is not None else None,
        recent[2] if recent is not None else None,
        "Both windows need a feasible optimized allocation to calculate the change.",
    )
    display_stress(full, recent)


if __name__ == "__main__":
    main()
