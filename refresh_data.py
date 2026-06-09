#!/usr/bin/env python3
"""Regenerate the bundled data snapshot for the Box Office Journey app from Snowflake.
Run locally by maintainers (needs the demo_mktadv_kp connection). The deployed public app reads
ONLY the files this writes into data/ -- no DB connection in production.

  SNOWFLAKE_CONNECTION_NAME=demo_mktadv_kp python refresh_data.py
"""
import os, json
import pandas as pd, numpy as np
import snowflake.connector

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
os.makedirs(DATA, exist_ok=True)

# ---- curated narrative climb (editorial: key beats, plain-language, honest) ----
# Accuracy = tier accuracy; MAE in $M. Early points from the project version log; later points are
# the validated CV numbers. The story is rise-then-plateau, then the reframe to odds.
CLIMB = [
    {"version": "V2",  "date": "2026-02-15", "accuracy": 58.1, "mae": 16.8, "label": "First real features", "note": "Rolling search-trend windows. A coin-flip-plus starting point."},
    {"version": "V5",  "date": "2026-02-15", "accuracy": 63.5, "mae": 15.1, "label": "Audience intent", "note": "YouTube trailer intent + star power added."},
    {"version": "V10", "date": "2026-02-15", "accuracy": 67.8, "mae": 14.0, "label": "Tiered structure", "note": "Predict the size class first, then the dollars."},
    {"version": "V14", "date": "2026-02-27", "accuracy": 71.5, "mae": 13.1, "label": "Production pipeline", "note": "Three clean tiers: Small / Mid / Large+."},
    {"version": "V15", "date": "2026-03-08", "accuracy": 77.3, "mae": 11.0, "label": "Data quality leap", "note": "Cleaner inputs; biggest single jump."},
    {"version": "V18", "date": "2026-04-21", "accuracy": 77.2, "mae": 10.96, "label": "Wikipedia interest", "note": "A third public demand signal joins search + social."},
    {"version": "V22c","date": "2026-05-12", "accuracy": 78.5, "mae": 9.21, "label": "Rule era peak", "note": "Hand-tuned rules squeezed error down -- but on hindsight knowledge."},
    {"version": "V27", "date": "2026-06-05", "accuracy": 79.5, "mae": 10.3, "label": "Modern ensemble", "note": "Tuned gradient boosting + a foundation model, no hand rules."},
    {"version": "V28-A","date": "2026-06-08", "accuracy": 77.0, "mae": 10.0, "label": "Honest & rule-free", "note": "Learns how to combine signals instead of hand-coded rules. The base for the odds reframe."},
]

MILESTONES = [
    {"act": "The Question", "title": "Can you call it before it opens?",
     "body": "Predict a movie's opening weekend using only signals available before release -- and without the ticket pre-sales or paid survey tracking the industry leans on."},
    {"act": "The Climb", "title": "From a coin flip to the high 70s",
     "body": "Better public signals (search, trailer reaction, Wikipedia) and a smarter structure pushed accuracy from 58% to the high-70s and cut the typical miss from ~$17M to ~$10M."},
    {"act": "The Wall", "title": "Accuracy stopped climbing -- and we learned why",
     "body": "A handful of films open far bigger than anything about them beforehand suggests. We proved mathematically that these breakouts sit at an irreducible 'noise floor': two films that look identical can open $50M apart."},
    {"act": "The Reframe", "title": "Stop guessing the number. Tell the odds.",
     "body": "The model already 'knew' these films were risky -- it gave them real breakout probability. We surfaced that: most-likely number, PLUS a calibrated chance of a breakout."},
    {"act": "Today", "title": "An honest prediction you can plan around",
     "body": "Every film gets a base case, a breakout probability, and a bear / base / bull range -- calibrated so '1 in 3' really happens about 1 in 3 times."},
]


def main():
    conn = snowflake.connector.connect(connection_name=os.getenv("SNOWFLAKE_CONNECTION_NAME") or "demo_mktadv_kp")
    df = pd.read_sql("SELECT * FROM SPARK_PAR_DEMO.PRODUCTION.OW_PREDICTION_V28_HISTORICAL", conn)
    conn.close()
    df.columns = [c.upper() for c in df.columns]
    df.to_csv(os.path.join(DATA, "predictions_v28.csv"), index=False)

    # headline stats
    n = len(df); acc = df["TIER_HIT"].mean() * 100; mae = df["ABS_ERROR"].mean() / 1e6
    large = df["ACTUAL_TIER"] == "LARGE+"
    missed = large & (df["PRED_TIER"] != "LARGE+")
    flag = df["BREAKOUT_FLAG"].astype(bool)
    caught = (missed & flag).sum()
    stats = {
        "n_films": int(n), "tier_accuracy": round(acc, 1), "mae_millions": round(mae, 2),
        "n_breakouts": int(large.sum()), "breakout_flags": int(flag.sum()),
        "missed_breakouts": int(missed.sum()), "flag_catches_missed": int(caught),
        "flag_recall_pct": round(caught / max(1, missed.sum()) * 100),
        "date_min": str(df["RELEASE_DATE"].min())[:10], "date_max": str(df["RELEASE_DATE"].max())[:10],
        "start_accuracy": 58.1, "start_mae": 16.8,
    }
    json.dump(stats, open(os.path.join(DATA, "headline_stats.json"), "w"), indent=2)

    # calibration: bucket -> predicted label vs actual LARGE+ rate
    buckets = [(0, .15, "Under 15%"), (.15, .30, "15-30% (~1 in 5)"),
               (.30, .50, "30-50% (~1 in 3)"), (.50, 1.01, "Over 50%")]
    calib = []
    for lo, hi, lab in buckets:
        m = (df["P_LARGE"] >= lo) & (df["P_LARGE"] < hi)
        if m.sum():
            calib.append({"bucket": lab, "n": int(m.sum()),
                          "actual_breakout_rate": round((df.loc[m, "ACTUAL_TIER"] == "LARGE+").mean() * 100)})
    json.dump(calib, open(os.path.join(DATA, "calibration.json"), "w"), indent=2)

    json.dump({"climb": CLIMB, "milestones": MILESTONES},
              open(os.path.join(DATA, "journey.json"), "w"), indent=2)

    print(f"wrote data/: predictions_v28.csv ({n} rows), headline_stats.json, calibration.json, journey.json")
    print(f"  headline: {acc:.1f}% tier acc, ${mae:.2f}M MAE, {flag.sum()} breakout flags, "
          f"catches {caught}/{missed.sum()} missed breakouts")


if __name__ == "__main__":
    main()
