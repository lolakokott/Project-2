# Project 2 — Cold-Run Record

**Test type:** Self-conducted fresh-clone simulation with AI review.

**Repository:** https://github.com/lolakokott/Project-2

**Launch command:** `python -m streamlit run project2_app.py`

**Result location:** Streamlit application, under *ETF portfolio estimates*.

**First failure:** No application failure reported in the supplied output.

**Elapsed time:** Not recorded.

## Observed Results

The application displayed the two baseline portfolios and the constrained portfolio in both estimation windows.

For the full historical window, the constrained allocation was VT 5%, BIL 70%, QQQ 25%, and IEF 0%, with a 7.12% estimated annual return, 5.97% annualized volatility, and a PASS mandate verdict.

For the last 36 months, the constrained allocation was VT 10%, BIL 85%, QQQ 5%, and IEF 0%, with a 7.06% estimated annual return, 1.99% volatility, and a PASS mandate verdict.

The largest allocation difference was 20 percentage points in QQQ. The DGS10 monitoring card displayed 5.26% for the September 29, 2026 observation, using the September 30, 2026 historical decision date.

## Limitations

This was a self-conducted simulation, not a cold run independently conducted by a classmate. The output was reviewed with AI assistance. Independent reproducibility remains to be confirmed.
