# F1 Fantasy — Session Handoff

**Project:** f1-fantasy
**Date:** 2026-03-28
**Status:** ACTIVE — Suzuka race weekend approaching

---

## Current State

### What Was Built

5-tab Streamlit dashboard with TDD approach (43/43 tests passing):

| Component | File | Tests |
|-----------|------|-------|
| OpenF1 Client | `src/data_fetcher.py` | 6 |
| Prediction Model | `src/prediction_model.py` | 6 |
| OR-tools Optimizer | `src/optimizer.py` | 7 |
| Telemetry Tab | `src/telemetry_tab.py` | 6 |
| Strategy Tab | `src/strategy_tab.py` | 7 |
| Weather Tab | `src/weather_tab.py` | 7 |
| Monte Carlo Tab | `src/monte_carlo_tab.py` | 5 |
| Dashboard (tabbed) | `src/app.py` + `src/styles.py` | — |

**Live at:** `f1-fantasy-keithcostello.streamlit.app` (Streamlit Community Cloud)

**Repos:**
- `keithcostello/GPT_verses_CLAUDE` (main) — deployment target
- `keithcostello/GENERIC_CODEX` (codex_laptop) — development

### What Needs Fixing (TODOs)

1. **Telemetry tab**: Currently hardcoded to Suzuka. Needs year/country/session selector that updates ALL telemetry data. User can select any past race (Australia 2026, China 2026, etc.) and see that race's telemetry. In progress.

2. **Professional redesign**: Dashboard uses emojis for icons. User wants professional sports analytics look — text headers, monospace numbers, team color bars, bar charts. No emoji. In progress.

3. **Live data connection**: Suzuka FP1 starts Fri Mar 27 21:30 ET. When data drops, the dashboard will auto-populate with real telemetry.

---

## How to Run

```bash
# Local development
cd projects/f1-fantasy
pip install -r requirements.txt
streamlit run src/app.py --server.port 8501

# Run tests
py -m pytest tests/ -v
```

---

## Suzuka Timing (ET)

| Session | Day | Time (ET) |
|---------|-----|-----------|
| FP1 | Fri Mar 27 | 21:30 |
| FP2 | Sat Mar 28 | 01:00 |
| FP3 | Sat Mar 28 | 22:30 |
| Qualifying | Sat Mar 28 | 02:00 |
| Race | Sun Mar 29 | 02:00 |

---

## Contest Context

Keith vs Amy (wife) — F1 Fantasy Head-to-Head. Same data sources, different AI assistants. Amy's AI produced research documentation. Keith's AI (this build) produced working code with optimization + interactive dashboards.

---

## Next Steps (Priority Order)

1. **Verify telemetry fix** — test that selecting a different race weekend changes the lap/position/stint data
2. **Verify professional redesign** — remove all emoji, use bar charts, clean typography
3. **Push fixes to GitHub** — triggers Streamlit Cloud auto-redeploy
4. **Test with Suzuka FP1 data** — when data drops Friday night, verify live telemetry populates

---

## Key Files

- `src/app.py` — main Streamlit app with 5 tabs
- `src/telemetry_tab.py` — race selector + telemetry display (needs fixing)
- `src/styles.py` — F1 dark theme (needs professional redesign)
- `src/optimizer.py` — OR-tools budget optimizer (works correctly)
- `src/prediction_model.py` — weighted composite scoring (works correctly)
- `tests/` — 43 tests, all passing

## Evidence Commands

```bash
# Run all tests
py -m pytest projects/f1-fantasy/tests/ -v

# Verify Streamlit runs locally
streamlit run projects/f1-fantasy/src/app.py --server.port 8501

# Check OpenF1 API (from bash)
curl "https://api.openf1.org/v1/sessions?limit=5"
```

---

**Then provide a concise current-state dashboard and WAIT FOR INSTRUCTION.**