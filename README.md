# FIN43900 Project 2

**AI use disclosure.** This project was developed with AI assistance.

**Educational use only.** This course application is a learning demonstration and does not provide investment advice.

## Portfolio mandate

The app searches for the lowest annualized volatility among long-only portfolios with weights totaling 100%, an estimated annual return of at least 7%, and a BIL reserve of at least 10%.

| Ticker | Exposure | Equal-weight baseline | Custom 60/40 policy baseline |
| --- | --- | ---: | ---: |
| VT | Global stocks | 25% | 40% |
| BIL | Short-term U.S. Treasury bills and the mandate reserve | 25% | 10% |
| QQQ | Nasdaq-100 stocks | 25% | 20% |
| IEF | Intermediate-term U.S. Treasury bonds | 25% | 30% |

The policy baseline holds 60% in stocks and 40% in Treasury bills and bonds. The app checks both baselines against the same mandate and searches allocations in 5-percentage-point increments. It reports the feasible grid allocation with the lowest estimated volatility or shows that no grid allocation meets the mandate. A finer grid or continuous optimizer could find different weights or lower volatility.

The app compares the full available return history with the last 36 monthly returns when enough prices are available. For each window, it estimates annual returns as 12 times the arithmetic mean monthly return and derives annualized covariance from monthly sample volatilities and correlations. Portfolio volatility is the square root of the weighted covariance calculation. These estimates depend on the chosen historical window. Future returns, volatilities, and correlations may differ, and the 7% threshold is a model constraint.

## Run from a fresh clone

Open a terminal in the cloned repository root. Use Python 3.13, the version family used to verify the dependency pins. Keep `prices.csv` alongside `project2_app.py` and the imported modules.

Create and activate a virtual environment on macOS or Linux.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, use these commands instead.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the pinned dependencies and launch the app from the repository root.

```bash
python -m pip install -r requirements.txt
python -m streamlit run project2_app.py
```

## ETF prices and the DGS10 vintage

The app uses the bundled `prices.csv` by default. It contains 60 monthly adjusted-price rows from October 2021 through September 2026, producing 59 monthly returns. The sidebar also accepts a CSV with a `Date` column in `YYYY-MM-DD` format and columns for `VT`, `BIL`, `QQQ`, and `IEF`. Use finite, positive prices and one row per consecutive month in chronological order. The app requires at least three price rows to estimate risk and 37 rows for the 36-month comparison.

ETF estimates use the dates present in the bundled or uploaded CSV. The row dates identify price observations, and the CSV provides no record of when those prices first became available. Changing the DGS10 decision date leaves the ETF estimation windows unchanged.

The DGS10 panel requests the ALFRED vintage for the selected decision date, which defaults to September 30, 2026. It displays the latest measured yield on or before that date within the requested vintage, along with the observation date. The data card identifies the Federal Reserve Board's H.15 series, its units of percent per annum without seasonal adjustment, and its business-day frequency. Observations are generally published the following business day. The archive has daily resolution, release timing can vary, and later vintages may incorporate revisions.

The DGS10 panel requires internet access to ALFRED and uses a public CSV endpoint without an API key. The app reports an unavailable vintage or failed download and continues to show ETF results when valid prices are available. DGS10 provides interest-rate context for a hypothetical IEF scenario. ETF estimates and weights are calculated independently of the yield. [FRED DGS10 series](https://fred.stlouisfed.org/series/DGS10) · [ALFRED DGS10 archive](https://alfred.stlouisfed.org/series?seid=DGS10)

## Return-only stress scenarios

Enter hypothetical annual return assumptions in percent for any ETF. Overrides apply to both windows, and blank fields use each window's historical estimate. The app evaluates the scenario at the original optimized weights when available and reruns the same constrained 5% grid under the new return assumptions. Each window retains its historical covariance, so fixed-weight volatility stays the same and reoptimized volatility can change through the new weights. DGS10 can inform an IEF assumption you enter yourself. The scenario is a sensitivity analysis of expected returns.

## Tests

Run the existing tests from the repository root with the virtual environment active.

```bash
python -m unittest discover -p "test_project2_*.py"
```

The portfolio tests cover CSV validation, correlations, mandate checks, and grid optimization. The stress tests cover fixed weights, reoptimization, infeasibility, and the Streamlit form. The DGS10 tests cover vintage selection, date filtering, missing observations, and the app's response to a failed download. They mock the ALFRED request.

## Investment Decision and Supporting Evidence

**Committee recommendation: PILOT, not immediate adoption.**

The optimized portfolio meets the mandate under historical estimates, but allocation changes across estimation windows and return assumptions support a monitored pilot rather than unconditional adoption.

- [Executed application output](docs/executed-output.md)
- [Investment committee decision memo](docs/decision-memo.md)
- [Validation and AI-use documentation](docs/validation-and-ai-use.md)
- [Locked Changed-Input Record](docs/locked-changed-input.md)

The decision is conditional on continued mandate compliance, reliable data, and an agreed tolerance for allocation changes. The project is an educational demonstration, not investment advice.
