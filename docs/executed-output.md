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

## 6. Investment Decision

**PILOT, not immediate adoption.**

The constrained portfolio meets the mandate under the historical assumptions and has lower estimated volatility than both baselines. However, its sensitivity to estimation windows and QQQ's expected-return assumption prevents unconditional adoption.

The pilot is conditional on source validation, continued mandate compliance, an agreed allocation-change tolerance, and ongoing monitoring.

**Reversal condition:** Suspend or reject the proposed allocation if no feasible portfolio meets the mandate or if allocation instability exceeds the client's approved tolerance.

## 7. Reproducibility

Run the application from the repository root:

`python -m streamlit run project2_app.py`

The reported values were observed in the locally executed Streamlit application using the bundled `prices.csv`. The historical signal requires an ALFRED connection.

Supporting documents:

- `docs/decision-memo.md`
- `docs/validation-and-ai-use.md`
- `docs/locked-changed-input.md`
