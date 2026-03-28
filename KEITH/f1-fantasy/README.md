# F1 Fantasy — Suzuka 2026

Keith's F1 Fantasy lineup optimizer for the Suzuka GP (March 28-29, 2026).

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run src/app.py --server.port 8501
```

Then open http://localhost:8501

## Stack

- **OpenF1 API** — live race data (no auth)
- **OR-tools** — mixed integer programming optimizer
- **Streamlit** — dark-theme F1 dashboard
- **19 tests** — `py -m pytest tests/ -v`

## Architecture

```
OpenF1 API → data_fetcher.py → prediction_model.py → optimizer.py → app.py
```

## Deployment (Streamlit Community Cloud)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub → Deploy `KEITH/f1-fantasy/src/app.py`
4. URL is live in ~2 minutes

## Suzuka Timing (ET)

| Session | Day | Time |
|---------|-----|------|
| Qualifying | Sat Mar 28 | 02:00 |
| Race | Sun Mar 29 | 02:00 |

## Projected Lineup (pre-qualifying)

```
Drivers: Gasly, Antonelli, Bearman, Ocon, Perez
Constructors: Ferrari, Haas
Total: $99.9M / 157 projected points
```

Based on: 50% Australia + 30% China 2026 results + 20% Suzuka historical factors.
