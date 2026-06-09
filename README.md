# Predicting Opening Weekend: The Journey

An interactive story of how we built a movie opening-weekend prediction model on Snowflake —
from a rule-based first guess in January to a calibrated, honest prediction that tells you the
**odds of a breakout**, not just a single number.

**Live app:** _(Streamlit Community Cloud URL — added after deploy)_

## What this is
A narrative dashboard for a broad audience (not just data scientists). It walks through:
1. **The Question** — can you predict a film's opening before it opens, using only public signals?
2. **The Climb** — version by version, from 58% to ~78% tier accuracy.
3. **The Wall** — the honest twist: some films (breakouts) are near-impossible to pin to one number.
4. **The Reframe** — stop guessing the number; tell the odds. Calibrated breakout probability.
5. **The Track Record** — how the model actually did, plus a live tracker for upcoming films.
6. **Behind the Scenes** — built on Snowflake + Cortex Code; the signals we use and the ones we
   deliberately refuse to use (ticket presales, industry tracking) — which is what makes it honest.

## Ground rules (why the predictions are honest)
- **Only public, pre-release signals**: Google Trends, YouTube trailer reaction, Wikipedia interest,
  budget/cast/genre. **No ticket presales. No industry survey tracking.** The point is to beat
  industry projections *without* the data they rely on.
- **Track record is out-of-fold (leak-safe)**: every film's prediction was made by a model that had
  never seen that film. No hindsight inflation.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
The app reads only the bundled snapshot in `data/` — no database connection required.

## Deploy to Streamlit Community Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with the GitHub account that
   owns this repo (`snowflake-mike-MKTG-IND`).
2. **New app** \u2192 **Deploy from existing repo**:
   - Repository: `snowflake-mike-MKTG-IND/box-office-journey`
   - Branch: `main`
   - Main file path: `app.py`
3. Click **Deploy**. No secrets are needed \u2014 the app reads only the bundled `data/` snapshot.
4. Copy the resulting URL into the **Live app** link at the top of this README.

Because the repo is private, authorize Streamlit's GitHub access when prompted. Every push to `main`
(including refreshed `data/`) auto-redeploys.

## Refresh the data (maintainers)
`refresh_data.py` regenerates the bundled snapshot from Snowflake (run locally, with a configured
`demo_mktadv_kp` connection), then commit the updated `data/` files — Streamlit Cloud auto-deploys.
```bash
SNOWFLAKE_CONNECTION_NAME=demo_mktadv_kp python refresh_data.py
git add data/ && git commit -m "Refresh predictions" && git push
```

## Adding new predictions
Score upcoming films with the V28-A model, append them to
`SPARK_PAR_DEMO.PRODUCTION.OW_PREDICTION_V28_HISTORICAL`, then run `refresh_data.py` and commit.
The **Track Record** page surfaces them automatically.

---
Built on Snowflake with [Cortex Code](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code).
