# Project 2 — Executed Application Output

**FIN43900 | Investment Management Application**

**AI-use disclosure:** This application was developed with AI assistance. Portfolio calculations were performed in Python and the displayed results were reviewed by the student.

**Educational demonstration only — not investment advice.**

## 1. Mandate

- Estimated annual return ≥ 7%.
- BIL reserve ≥ 10%.
- Long-only portfolio.
- Weights total 100%.
- Minimize historical annualized volatility using a 5% allocation grid.

## 2. Full Historical Window

59 monthly returns, November 2021–September 2026.

| Portfolio | VT | BIL | QQQ | IEF | Return | Volatility | Mandate |
|---|---:|---:|---:|---:|---:|---:|---|
| Equal weight | 25% | 25% | 25% | 25% | 7.25% | 9.91% | PASS |
| Custom 60/40 | 40% | 10% | 20% | 30% | 7.48% | 11.35% | PASS |
| Constrained optimizer | 5% | 70% | 25% | 0% | 7.12% | 5.97% | PASS |

## 3. Last 36 Months

36 monthly returns, October 2023–September 2026.

| Portfolio | VT | BIL | QQQ | IEF | Return | Volatility | Mandate |
|---|---:|---:|---:|---:|---:|---:|---|
| Equal weight | 25% | 25% | 25% | 25% | 13.52% | 7.76% | PASS |
| Custom 60/40 | 40% | 10% | 20% | 30% | 14.73% | 8.88% | PASS |
| Constrained optimizer | 10% | 85% | 5% | 0% | 7.06% | 1.99% | PASS |

**Largest optimized allocation change:** 20 percentage points in QQQ.

## 4. Point-in-Time DGS10 Signal

| Field | Result |
|---|---|
| Historical decision date | September 30, 2026 |
| Latest measured date available | September 29, 2026 |
| DGS10 yield | 5.26% per annum |
| Source | Federal Reserve H.15 via FRED/ALFRED |

The DGS10 signal is used for monitoring, not as a direct return forecast. ETF data availability is not independently certified for the same historical decision time.

## 5. Locked Changed-Input Stress

**Scenario:** QQQ's full-window annual expected return reduced from 16.0396% to 14.0396%.

| Metric | Historical baseline | Original weights under stress | Reoptimized stress |
|---|---:|---:|---:|
| VT | 5% | 5% | 25% |
| BIL | 70% | 70% | 60% |
| QQQ | 25% | 25% | 15% |
| IEF | 0% | 0% | 0% |
| Est. annual return | 7.12% | 6.62% | 7.06% |
| Annualized volatility | 5.97% | 5.97% | 6.71% |
| BIL reserve | 70% | 70% | 60% |
| Mandate | PASS | FAIL | PASS |

**Largest reoptimized weight change:** 20 percentage points in VT.

This scenario changes expected returns only. The historical covariance matrix remains fixed.

## 6. Additional Stress Tests — Costs and Liquidity

### Annual Cost Stress: 25 Basis Points

This scenario applies a hypothetical annual cost of 25 basis points (0.25 percentage points) and retains the original 10% minimum BIL requirement. All ETF expected-return assumptions remain unchanged.

| Metric | Full-window original weights | Full-window reoptimized | 36-month original weights | 36-month reoptimized |
|---|---:|---:|---:|---:|
| VT | 5% | 0% | 10% | 5% |
| BIL | 70% | 70% | 85% | 85% |
| QQQ | 25% | 30% | 5% | 10% |
| IEF | 0% | 0% | 0% | 0% |
| Gross annual return | 7.1226% | 7.3721% | 7.0554% | 7.3626% |
| Net annual return | 6.8726% | 7.1221% | 6.8054% | 7.1126% |
| Annualized volatility | 5.97% | 6.35% | 1.99% | 2.27% |
| Mandate | FAIL | PASS | FAIL | PASS |

The original allocations failed the 7% net return objective after costs. Reoptimization found feasible portfolios in both historical windows, although estimated volatility increased.

### Minimum BIL Reserve Stress: 80%

This scenario increases the minimum BIL requirement from 10% to 80%, with no additional annual cost.

**Full historical window:** The original 70% BIL allocation failed the stressed reserve requirement. Reoptimization returned INFEASIBLE because the highest achievable estimated annual return with at least 80% BIL was 6.1339%, below the 7% objective.

**Last 36 months:** The original allocation of VT 10%, BIL 85%, QQQ 5%, and IEF 0% continued to meet the mandate. Estimated annual return was 7.0554%, with 1.99% annualized volatility.

These scenarios demonstrate that both cost assumptions and liquidity constraints can materially affect mandate feasibility.

**Process stopping condition:** Do not approve a proposed allocation when no feasible portfolio meets the stressed mandate. Reassess the assumptions or seek a revised mandate from the committee rather than presenting a noncompliant allocation as acceptable.

## 7. Investment Decision

**PILOT, not immediate adoption.**

The constrained portfolio meets the mandate under the historical assumptions and has lower estimated volatility than both baselines. However, its sensitivity to estimation windows and QQQ's expected-return assumption prevents unconditional adoption.

The pilot is conditional on source validation, continued mandate compliance, an agreed allocation-change tolerance, and ongoing monitoring.

**Reversal condition:** Suspend or reject the proposed allocation if no feasible portfolio meets the mandate or if allocation instability exceeds the client's approved tolerance.

## 8. Reproducibility

Run the application from the repository root:

`python -m streamlit run project2_app.py`

The reported values were observed in the locally executed Streamlit application using the bundled `prices.csv`. The historical signal requires an ALFRED connection.

Supporting documents:

- `docs/decision-memo.md`
- `docs/validation-and-ai-use.md`
- `docs/locked-changed-input.md`
