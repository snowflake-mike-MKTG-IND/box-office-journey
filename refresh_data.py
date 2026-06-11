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


SIGNAL_COLS = [
    "BUDGET", "TMDB_POPULARITY", "YT_COMMENTS", "KNOWN_IP_TIER",
    "ROLLING_7D", "ROLLING_3D", "ROLLING_14D", "VELOCITY_7D", "TRENDS_PEAK_SO_FAR",
    "MAX_STAR_POWER", "TOP2_STAR_POWER", "AVG_STAR_POWER",
    "PREDECESSOR_OW_LOG", "THEATRICAL_INTENT_PCT",
]

WIKI_COLS = [
    "WIKI_ROLLING_7D", "WIKI_ROLLING_14D", "WIKI_PEAK", "WIKI_CUMULATIVE",
    "WIKI_VELOCITY_7D",
]


def export_upcoming_features(conn, upcoming_ids):
    """Export feature data for upcoming movies + percentile ranks vs training set."""
    if not len(upcoming_ids):
        return pd.DataFrame()

    # Get model_version -> days_out mapping for each upcoming movie
    up_meta = pd.read_sql(
        "SELECT MOVIE_ID, MODEL_VERSION FROM SPARK_PAR_DEMO.PRODUCTION.OW_PREDICTION_V28_HISTORICAL "
        "WHERE PREDICTION_TYPE = 'UPCOMING'", conn)
    up_meta.columns = [c.upper() for c in up_meta.columns]
    # Parse days_out from MODEL_VERSION (e.g. V28-A@D7 -> -7)
    def parse_horizon(mv):
        if pd.isna(mv): return -7
        if '@D3' in str(mv): return -3
        if '@D7' in str(mv): return -7
        if '@D14' in str(mv): return -14
        return -7
    up_meta['DAYS_OUT'] = up_meta['MODEL_VERSION'].apply(parse_horizon)

    # Build per-movie queries
    conditions = " OR ".join(
        f"(f.MOVIE_ID={int(row.MOVIE_ID)} AND f.DAYS_OUT={int(row.DAYS_OUT)})"
        for _, row in up_meta.iterrows()
    )
    feat_cols = ", ".join(["f.MOVIE_ID", "f.MOVIE_TITLE", "f.DAYS_OUT"] + [f"f.{c}" for c in SIGNAL_COLS])
    wiki_cols = ", ".join([f"COALESCE(w.{c}, 0) AS {c}" for c in WIKI_COLS])

    sql = f"""
        SELECT {feat_cols}, {wiki_cols}
        FROM SPARK_PAR_DEMO.PRODUCTION.OW_PREDICTION_FEATURES_V f
        LEFT JOIN SPARK_PAR_DEMO.PRODUCTION.WIKIPEDIA_FEATURES_V w
            ON f.MOVIE_ID = w.MOVIE_ID AND f.DAYS_OUT = w.DAYS_OUT
        WHERE {conditions}
    """
    uf = pd.read_sql(sql, conn)
    uf.columns = [c.upper() for c in uf.columns]

    # Get training set features at D-7 for percentile context
    all_cols = SIGNAL_COLS + WIKI_COLS
    train_cols = ", ".join([f"f.{c}" for c in SIGNAL_COLS] + [f"COALESCE(w.{c}, 0) AS {c}" for c in WIKI_COLS])
    train_sql = f"""
        SELECT {train_cols}
        FROM SPARK_PAR_DEMO.PRODUCTION.OW_PREDICTION_FEATURES_V f
        LEFT JOIN SPARK_PAR_DEMO.PRODUCTION.WIKIPEDIA_FEATURES_V w
            ON f.MOVIE_ID = w.MOVIE_ID AND f.DAYS_OUT = w.DAYS_OUT
        WHERE f.DAYS_OUT = -7 AND f.OPENING_WEEKEND IS NOT NULL
    """
    train = pd.read_sql(train_sql, conn)
    train.columns = [c.upper() for c in train.columns]

    # Compute percentile ranks for each signal
    for col in all_cols:
        if col in uf.columns and col in train.columns:
            vals = train[col].dropna().values
            if len(vals) > 0:
                uf[f"{col}_PCTL"] = uf[col].apply(
                    lambda x: int(np.searchsorted(np.sort(vals), x) / len(vals) * 100) if pd.notna(x) else 0
                )
            else:
                uf[f"{col}_PCTL"] = 0

    return uf


def main():
    conn = snowflake.connector.connect(connection_name=os.getenv("SNOWFLAKE_CONNECTION_NAME") or "demo_mktadv_kp")
    # Only pure model OOF predictions + live upcoming. Manual-override / excluded rows are dropped.
    df = pd.read_sql("SELECT * FROM SPARK_PAR_DEMO.PRODUCTION.OW_PREDICTION_V28_HISTORICAL "
                     "WHERE PREDICTION_TYPE IN ('OOF_BACKTEST', 'UPCOMING')", conn)
    df.columns = [c.upper() for c in df.columns]
    df.to_csv(os.path.join(DATA, "predictions_v28.csv"), index=False)

    # Export upcoming features with percentile context
    upcoming_ids = df[df["PREDICTION_TYPE"] == "UPCOMING"]["MOVIE_ID"].tolist()
    uf = export_upcoming_features(conn, upcoming_ids)
    if len(uf):
        uf.to_csv(os.path.join(DATA, "upcoming_features.csv"), index=False)
        print(f"  upcoming_features.csv: {len(uf)} rows, {len(uf.columns)} cols")

    conn.close()

    # headline stats + calibration are computed over the leak-safe BACKTEST only.
    # Upcoming rows (null actuals) are in the CSV for the live tracker but excluded from scoring metrics.
    bt = df[df["PREDICTION_TYPE"] == "OOF_BACKTEST"].copy()
    n = len(bt); acc = bt["TIER_HIT"].mean() * 100; mae = bt["ABS_ERROR"].mean() / 1e6
    large = bt["ACTUAL_TIER"] == "LARGE+"
    missed = large & (bt["PRED_TIER"] != "LARGE+")
    flag = bt["BREAKOUT_FLAG"].astype(bool)
    caught = (missed & flag).sum()
    stats = {
        "n_films": int(n), "tier_accuracy": round(acc, 1), "mae_millions": round(mae, 2),
        "n_breakouts": int(large.sum()), "breakout_flags": int(flag.sum()),
        "missed_breakouts": int(missed.sum()), "flag_catches_missed": int(caught),
        "flag_recall_pct": round(caught / max(1, missed.sum()) * 100),
        "date_min": str(bt["RELEASE_DATE"].min())[:10], "date_max": str(bt["RELEASE_DATE"].max())[:10],
        "start_accuracy": 58.1, "start_mae": 16.8,
        "n_upcoming": int((df["PREDICTION_TYPE"] == "UPCOMING").sum()),
    }
    json.dump(stats, open(os.path.join(DATA, "headline_stats.json"), "w"), indent=2)

    # calibration: bucket -> predicted label vs actual LARGE+ rate
    buckets = [(0, .15, "Under 15%"), (.15, .30, "15-30% (~1 in 5)"),
               (.30, .50, "30-50% (~1 in 3)"), (.50, 1.01, "Over 50%")]
    calib = []
    for lo, hi, lab in buckets:
        m = (bt["P_LARGE"] >= lo) & (bt["P_LARGE"] < hi)
        if m.sum():
            calib.append({"bucket": lab, "n": int(m.sum()),
                          "actual_breakout_rate": round((bt.loc[m, "ACTUAL_TIER"] == "LARGE+").mean() * 100)})
    json.dump(calib, open(os.path.join(DATA, "calibration.json"), "w"), indent=2)

    json.dump({"climb": CLIMB, "milestones": MILESTONES},
              open(os.path.join(DATA, "journey.json"), "w"), indent=2)

    print(f"wrote data/: predictions_v28.csv ({len(df)} rows; {n} backtest + {int((df['PREDICTION_TYPE']=='UPCOMING').sum())} upcoming), "
          f"headline_stats.json, calibration.json, journey.json")
    print(f"  headline: {acc:.1f}% tier acc, ${mae:.2f}M MAE, {flag.sum()} breakout flags, "
          f"catches {caught}/{missed.sum()} missed breakouts")


if __name__ == "__main__":
    main()
