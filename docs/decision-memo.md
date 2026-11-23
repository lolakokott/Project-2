# Project 2 — Investment Committee Decision Memo

**FIN43900 | Investment Management Application**

**Educational demonstration only — not investment advice.**

## 1. Executive Recommendation

**Recommendation: PILOT, not immediate adoption.**

I recommend using the constrained portfolio as a monitored pilot rather than immediately implementing it as a long-term investment allocation.

The optimizer identifies portfolios that meet the 7% estimated annual return objective and 10% minimum BIL reserve requirement while minimizing historical annualized volatility on a 5% allocation grid. However, the recommended weights change considerably when the estimation period or expected-return assumptions change.

The model demonstrates that feasible portfolios exist under the tested assumptions, but it does not establish that those allocations will remain suitable under future market conditions.

## 2. Investment Mandate

The portfolio consists of four ETFs:

| ETF | Investment role |
|---|---|
| VT | Global equity diversification |
| BIL | Treasury-bill reserve |
| QQQ | Growth-oriented equity exposure |
| IEF | Intermediate-term Treasury exposure |

The portfolio must meet the following conditions:

- Estimated annual return of at least 7%.
- Minimum allocation of 10% to BIL.
- Long-only positions.
- Portfolio weights totaling 100%.

The optimization objective is to identify the lowest-volatility feasible allocation using 5-percentage-point weight increments.

The central client question is how much allocation instability is acceptable when estimates change.

## 3. Portfolio Results and Baseline Comparison

Using monthly adjusted-price observations from October 2021 through September 2026, the application generated the following results.

### Full Historical Window

| Portfolio | Estimated return | Annualized volatility | BIL reserve | Mandate |
|---|---:|---:|---:|---|
| Equal weight | 7.25% | 9.91% | 25% | PASS |
| Custom 60/40 benchmark | 7.48% | 11.35% | 10% | PASS |
| Constrained optimizer | **7.12%** | **5.97%** | **70%** | **PASS** |

The constrained portfolio produced the lowest estimated volatility of the three approaches while meeting the return and reserve requirements.

Its allocation was:

| ETF | Weight |
|---|---:|
| VT | 5% |
| BIL | 70% |
| QQQ | 25% |
| IEF | 0% |

The custom 60/40 benchmark is a chosen policy benchmark consisting of 60% equities and 40% Treasury ETFs, not an official market index.

### Last 36 Months

| Portfolio | Estimated return | Annualized volatility | BIL reserve | Mandate |
|---|---:|---:|---:|---|
| Equal weight | 13.52% | 7.76% | 25% | PASS |
| Custom 60/40 benchmark | 14.73% | 8.88% | 10% | PASS |
| Constrained optimizer | **7.06%** | **1.99%** | **85%** | **PASS** |

The shorter-window optimized allocation was VT 10%, BIL 85%, QQQ 5%, and IEF 0%.

Although both optimized portfolios passed the mandate, QQQ's allocation decreased by 20 percentage points between the two windows.

This creates an important concern: the model's recommended allocation depends heavily on the historical data used to estimate returns and risk.

## 4. Changed-Input Stress Test

To challenge the original allocation, I reduced QQQ's full-window expected annual return from 16.0396% to 14.0396%, a decrease of 2 percentage points.

I recorded and committed my prediction before running the scenario. The original prediction and observed results are documented separately in `docs/locked-changed-input.md`.

| Metric | Original allocation | Original weights under stress | Reoptimized under stress |
|---|---:|---:|---:|
| VT | 5% | 5% | 25% |
| BIL | 70% | 70% | 60% |
| QQQ | 25% | 25% | 15% |
| IEF | 0% | 0% | 0% |
| Estimated return | 7.12% | 6.62% | 7.06% |
| Annualized volatility | 5.97% | 5.97% | 6.71% |
| Mandate | PASS | **FAIL** | PASS |

At the original weights, the portfolio failed the 7% return objective.

Reoptimization restored feasibility, but the resulting portfolio had higher volatility and required a 20-percentage-point increase in VT exposure.

This supports the PILOT recommendation. The optimizer can respond to changed assumptions, but the original allocation is not sufficiently stable to justify unconditional adoption.

The stress exercise changes expected returns while holding the historical covariance matrix fixed. It does not simulate transaction costs or simultaneous changes in correlations and volatility.

## 5. Point-in-Time Data and Model Limitations

The application includes DGS10, the 10-year Treasury constant maturity yield, as a monitoring signal.

For the September 30, 2026 historical decision date, the ALFRED vintage showed a latest available observation of September 29, 2026, with a yield of 5.26% per annum.

DGS10 is relevant when considering interest-rate exposure, particularly through IEF. However, the application does not use the Treasury yield as a direct forecast of ETF returns.

The portfolio estimates are calculated from historical ETF prices. The DGS10 point-in-time check does not independently establish that every ETF price was available at the specified historical decision time.

Other limitations include reliance on backward-looking return estimates, a 5% allocation grid rather than continuous optimization, and sensitivity to the selected estimation window.

## 6. Proposed Pilot Allocation and Conditions

I recommend treating the tested allocations as **scenario-based evidence, not guaranteed future portfolio weights**.

Across the historical-window and QQQ-stress results, the optimizer produced the following observed weight ranges:

| ETF | Observed range |
|---|---:|
| VT | 5–25% |
| BIL | 60–85% |
| QQQ | 0–25% |
| IEF | 0% |

These ranges describe tested outputs. They are not independent allocation limits, and arbitrary combinations within them may fail the mandate.

For a pilot, I would begin with the full-window allocation as a reference portfolio rather than authorizing immediate execution. Before implementing
