# Project 2 — Validation and AI Use

**FIN43900 | Investment Management Application**

**AI-use disclosure:** AI tools assisted with coding, debugging, testing, and drafting documentation. Financial outputs were calculated by Python and reviewed against the application's displayed results. The final investment recommendation reflects my interpretation of the evidence.

**This project is an educational demonstration, not investment advice.**

## 1. Model Purpose and Scope

The application evaluates portfolios containing VT, BIL, QQQ, and IEF.

It searches for the lowest-volatility allocation on a 5% weight grid while requiring:

- Estimated annual return of at least 7%.
- At least 10% allocated specifically to BIL.
- Long-only positions.
- Portfolio weights totaling 100%.

The model is a historical estimation and sensitivity-analysis tool, not a system for forecasting future returns or executing trades.

## 2. Data Integrity and Provenance

The bundled `prices.csv` contains 60 monthly price observations from October 2021 through September 2026.

The dataset has four ETF columns and no missing values. The application uses monthly percentage returns to calculate annualized historical return and volatility estimates and the correlation matrix.

### ETF Price Data Provenance

The ETF price dataset was created using `get_prices.py`, which retrieves historical daily adjusted closing prices for VT, BIL, QQQ, and IEF through the `yfinance` Python library using Yahoo Finance data. The script selects the last available daily observation for each month and saves the resulting monthly panel to `prices.csv`.

Local file timestamps and development records establish that the CSV existed on October 22, 2026, supporting that date as the likely download date. The exact original retrieval time could not be independently confirmed.

The dataset contains 60 monthly observations covering October 2021 through September 2026. Dates are labeled using calendar month-ends, which may differ from actual trading dates when a month ends on a weekend or holiday.

The original data-provider response was not preserved, so individual price observations have not been independently reconciled against an archived Yahoo Finance download. However, the available generation script and development records support the documented source, and no evidence of simulated or estimated price observations was identified.

This provenance limitation is disclosed rather than treating the historical data as independently authenticated.

The application also monitors DGS10 using FRED and ALFRED.

For the historical decision date of September 30, 2026, the latest available observation was dated September 29, 2026, with a value of 5.26% per annum.

The DGS10 module excludes observations measured after the selected decision date. However, this does not certify that all ETF closing prices were available at the same historical decision time.

## 3. Baseline Validation

The application compares two fixed baselines against the constrained optimizer.

### Full Historical Window

| Portfolio             | Estimated return | Volatility | Mandate |
| --------------------- | ---------------: | ---------: | ------- |
| Equal weight          |            7.25% |      9.91% | PASS    |
| Custom 60/40          |            7.48% |     11.35% | PASS    |
| Constrained optimizer |            7.12% |      5.97% | PASS    |

### Last 36 Months

| Portfolio             | Estimated return | Volatility | Mandate |
| --------------------- | ---------------: | ---------: | ------- |
| Equal weight          |           13.52% |      7.76% | PASS    |
| Custom 60/40          |           14.73% |      8.88% | PASS    |
| Constrained optimizer |            7.06% |      1.99% | PASS    |

The optimized portfolios displayed lower historical volatility than both baselines in each window.

The results are conditional on the historical estimates and the available 5% allocation combinations.

## 4. Mandate and Optimization Tests

The application validates portfolio constraints and input data, including weights, reserve allocation, prices, and correlations.

Automated tests cover:

- Mandate compliance and violations.
- Valid and invalid CSV inputs.
- Correlation-matrix validation.
- Feasible and infeasible optimization cases.
- Fixed-weight stress evaluation and reoptimization.
- Point-in-time filtering and unavailable DGS10 observations.

The initial application passed 15 automated tests during development. Following the addition of cost and liquidity constraint stress testing, the expanded test suite contained 21 tests. On November 23, 2026, I independently executed `python -m unittest discover -v` from a fresh clone of the GitHub repository. All 21 tests passed in 1.264 seconds. I also launched the application and verified that its portfolio comparisons and updated stress-testing controls were available. The baseline portfolio outputs were also observed in the running Streamlit application.

The optimizer performs an exhaustive search over 5-percentage-point weight combinations, not continuous portfolio optimization. It cannot establish the globally optimal allocation across all possible real-valued weights.

## 5. Estimation-Window Stability

The constrained optimizer produced the following allocations:

| ETF | Full window | Last 36 months |
| --- | ----------: | -------------: |
| VT  |          5% |            10% |
| BIL |         70% |            85% |
| QQQ |         25% |             5% |
| IEF |          0% |             0% |

The largest individual allocation change was 20 percentage points in QQQ.

Both portfolios passed the mandate, but the change in portfolio weights demonstrates sensitivity to the historical estimation window.

## 6. Locked Changed-Input Validation

Before running the changed-input experiment, I recorded and committed my prediction to GitHub.

The experiment reduced QQQ's full-window estimated annual return from 16.0396% to 14.0396%.

| Metric           | Baseline | Fixed-weight stress | Reoptimized stress |
| ---------------- | -------: | ------------------: | -----------------: |
| Estimated return |    7.12% |               6.62% |              7.06% |
| Volatility       |    5.97% |               5.97% |              6.71% |
| BIL reserve      |      70% |                 70% |                60% |
| Mandate          |     PASS |                FAIL |               PASS |

The original allocation failed the return objective under the new assumption. Reoptimization restored compliance, but required a larger VT allocation and higher estimated volatility.

This demonstrated that a portfolio passing the mandate under historical assumptions may not remain feasible when estimates change.

The original prediction, observed results, and comparison are documented in `docs/locked-changed-input.md`. GitHub commit history preserves the sequence.

## 7. Stress Testing and Model Limitations

The stress-testing module allows expected-return assumptions to change while maintaining each estimation window's historical covariance matrix.

Consequently, fixed-weight portfolio volatility remains unchanged in a return-only scenario. Reoptimized volatility may change when portfolio weights change.

The model does not currently establish:

- Forecast accuracy or out-of-sample performance.
- Transaction costs, slippage, or market impact.
- A continuous globally optimal portfolio.
- Stable return correlations in future market conditions.
- A fully point-in-time-correct historical ETF backtest.
- An enforceable client tolerance for allocation changes.

The application must identify infeasible scenarios instead of presenting a compliant allocation that does not exist.

### Additional Cost and Liquidity Stress Validation

I expanded the application to test changes in hypothetical annual portfolio costs and minimum BIL reserve requirements, in addition to expected-return assumptions and estimation windows. The optimizer applies costs to net expected returns and enforces the stressed liquidity constraint when searching for feasible allocations.

**Cost stress:** I applied a hypothetical annual portfolio cost of 25 basis points while retaining the original 10% BIL minimum. In the full historical window, the original allocation's estimated net annual return decreased from 7.1226% to 6.8726%, causing the mandate to fail. Reoptimization produced an allocation of VT 0%, BIL 70%, QQQ 30%, and IEF 0%, with a net expected return of 7.1221% and annualized volatility of 6.35%. The reoptimized portfolio passed the mandate.

In the last-36-month window, the original allocation's estimated net return decreased to 6.8054%, also failing the mandate. Reoptimization restored compliance with a 7.1126% net return and 2.27% annualized volatility.

**Liquidity constraint stress:** I increased the minimum required BIL allocation from 10% to 80%, with no additional portfolio cost. In the full historical window, the application correctly identified the problem as infeasible: the highest achievable estimated return with at least 80% BIL was 6.1339%, below the 7% objective. The application did not present an infeasible portfolio as compliant.

In the last-36-month window, the original allocation of VT 10%, BIL 85%, QQQ 5%, and IEF 0% remained feasible, with a 7.0554% estimated annual return and 1.99% volatility.

**Validation outcome:** The original QQQ changed-input experiment remained consistent after the application changes. Codex reported 21 passing automated tests, and I separately observed the cost and liquidity stress results in the running Streamlit application.

These tests strengthen my PILOT recommendation. They demonstrate that modest costs can cause the original portfolio to fail its return requirement and that a stricter liquidity constraint can prevent the optimizer from finding any feasible allocation.

## 8. Reproducibility and Independent Challenge

The repository includes application modules, historical data, dependency requirements, automated tests, and launch instructions.

A self-conducted fresh-clone simulation reproduced the expected baseline portfolio results. A separate independent partner cold run has not yet been verified.

An independent reviewer could reasonably challenge the model if the historical data source cannot be reconciled, estimation sensitivity becomes unacceptable, the mandate cannot be satisfied under relevant stress scenarios, or the results are presented as forward-looking predictions.

These conditions could justify restricting use even when the application executes successfully.

## 9. AI Use and Human Judgment

AI assisted in developing and debugging the Streamlit application, calculation modules, point-in-time monitor, stress-testing interface, and automated tests.

I reviewed the displayed financial outputs against my earlier lab results and checked the model's behavior under a changed-input scenario.

My Locked Changed-Input prediction was written before the experiment and committed to GitHub. I received AI feedback on my reasoning, and interpreted the results afterward.

AI-generated outputs were not treated as sufficient evidence of model accuracy on their own. I distinguished tests reported by Codex from behavior I observed in the running application.

### Material AI Uses and Verification

I used AI as a development and analytical support tool, rather than as a substitute for my investment judgment.

| AI tool | Material use | Verification and disposition |
|---|---|---|
| OpenAI ChatGPT | Interpreting and organizing assignment requirements, discussing portfolio methodology, and reviewing financial reasoning | I compared recommendations with the assignment requirements and my observed application results. I retained the PILOT recommendation because the tested allocations showed sensitivity to assumptions. |
| OpenAI Codex | Assisting with Python implementation, debugging, Streamlit functionality, automated tests, and drafting documentation | Codex assisted with developing the automated tests. I subsequently ran the complete 21-test suite myself from a fresh GitHub clone and confirmed that all tests passed. I also launched Streamlit and reviewed the portfolio results and stress-testing functionality. |
| AI-assisted documentation | Organizing the investment memo and validation explanations | I reviewed the descriptions against the financial results and made the final decisions regarding the recommendation, limitations, and monitoring conditions. |

**Model/version and interaction dates:**  I used OpenAI ChatGPT version GPT-6 and Codex version GPT-6.2-Sol throughout Project 2 development in November 2026 only. 

**Material output check:** AI-assisted code and explanations were evaluated using the portfolio's baseline results and the QQQ changed-input experiment. The full-window original allocation returned an estimated 7.12% with 5.97% volatility. Reducing QQQ's expected return by 2 percentage points reduced the fixed-weight portfolio's estimated return to 6.62%, causing a mandate failure. Reoptimization restored feasibility with a 7.06% estimated return and 6.71% volatility.

These observed results supported my decision to recommend a monitored PILOT rather than immediate adoption.

**Independent judgment:** I was responsible for defining the mandate, reviewing the portfolio results, assessing the model's limitations,  determining the investment recommendation, and reviewing documentation. AI assistance informed the development and review process but did not replace my responsibility for those decisions.

## 10. Investment Judgment and Monitoring

**Recommendation: PILOT, not immediate adoption.**

The application provides a transparent method for identifying feasible portfolios, but the sensitivity to estimated returns and estimation windows limits confidence in implementing one allocation without further review.

Before broader adoption, I would require agreement on acceptable allocation instability, continued mandate compliance, reliable data, and additional testing of model assumptions.

The committee should reassess or suspend the pilot if the model cannot identify a feasible allocation or if the resulting changes exceed the client's approved risk tolerance.
