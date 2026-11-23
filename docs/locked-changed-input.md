# Lab 20 — Locked Changed-Input Record

## Pre-Run Prediction

**Input being changed:** QQQ's estimated annual return.

- Original value: 16.0396%
- New value: 14.0396%
- Change: −2 percentage points
- Estimation window: Full historical period, November 2021–September 2026

**My prediction:**

I predict that reducing QQQ's expected annual return will decrease its allocation in the optimized portfolio because it becomes less attractive relative to the other ETFs.

I expect the portfolio's estimated return to decrease. I expect volatility to remain unchanged if the original allocation is held constant, although reoptimization could change portfolio risk.

I am uncertain whether the portfolio will still satisfy its 7% expected-return requirement. The result will depend on whether the optimizer can find another feasible allocation.

**Decision expectation:** I will reassess the PILOT recommendation based on whether the stressed portfolio meets the mandate and how much the optimized weights change.

---

## Post-Run Results

**Scenario:** Reduced QQQ's annual expected return from 16.0396% to 14.0396% in the full historical window, holding the other expected returns and historical covariance estimates unchanged.

### Full Historical Window

| Metric | Historical baseline | Original weights under stress | Reoptimized under stress |
|---|---:|---:|---:|
| VT weight | 5% | 5% | 25% |
| BIL weight | 70% | 70% | 60% |
| QQQ weight | 25% | 25% | 15% |
| IEF weight | 0% | 0% | 0% |
| Estimated annual return | 7.12% | 6.62% | 7.06% |
| Annualized volatility | 5.97% | 5.97% | 6.71% |
| BIL reserve | 70% | 70% | 60% |
| Mandate | PASS | FAIL | PASS |

**Largest reoptimized allocation change:** 20 percentage points in VT.

### Comparison With My Prediction

My prediction was partially confirmed. As expected, QQQ's allocation decreased after its assumed return was reduced. At the original weights, the portfolio's estimated return fell below 7%, causing the mandate to fail, while volatility remained unchanged.

After reoptimization, the portfolio satisfied the mandate with a 7.06% estimated return. However, volatility increased to 6.71%, and VT's allocation increased from 5% to 25%. This demonstrated that maintaining the return objective required accepting a different risk profile.

### Additional 36-Month Results

The application also applied the 14.0396% QQQ override to the last-36-month window, reducing its historical QQQ estimate from 26.3915%.

The original allocation's estimated return decreased from 7.06% to 6.44%, failing the mandate. Reoptimization produced VT 20%, BIL 80%, QQQ 0%, and IEF 0%, with a 7.54% estimated return and 2.37% volatility. This portfolio passed the mandate.

Because the same absolute override was applied to both windows, the 36-month test represented a larger return shock and is not directly comparable to a two-percentage-point reduction.

## Investment Decision

**PILOT, not ADOPT.**

The stress test reinforces my original decision. Although the optimizer found feasible allocations in both windows, reducing one return assumption caused the existing allocations to fail the mandate and required significant reallocation.

I would limit use to a monitored pilot until the client confirms an acceptable allocation-change tolerance and further stress tests demonstrate sufficient stability.

I would reconsider broader adoption if the portfolio consistently meets the mandate under reasonable assumptions without requiring substantial weight changes. I would suspend the pilot or reject the proposed allocation if feasible portfolios cannot meet the return objective under an agreed stress scenario.

## Validation Limitations

The scenario changes expected returns but holds each window's historical covariance matrix fixed. It does not model transaction costs, market-impact costs, or simultaneous shocks to volatility and correlation.

The results are backward-looking sensitivity estimates, not forecasts.

**AI-use disclosure:** The prediction was formed by the student independently with AI feedback on the reasoning. The scenario was then run in the application, and the observed results were reviewed.
