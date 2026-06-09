"""Chapter 4 — The Track Record + live/upcoming predictions."""
import streamlit as st
import pandas as pd
import theme, dataio

theme.apply_page_config("Track Record")
theme.cortex_footer()
df = dataio.predictions(); s = dataio.stats()

st.title("The Track Record")
st.caption(f"How V28 actually did across {s['n_films']} films \u2014 out-of-fold, so no hindsight. "
           f"Releases {s['date_min']} to {s['date_max']}.")

c1, c2, c3, c4 = st.columns(4)
with c1: theme.big_stat(f"{s['tier_accuracy']:.0f}%", "got the size class right")
with c2: theme.big_stat(f"${s['mae_millions']:.0f}M", "typical miss")
with c3: theme.big_stat(f"{s['flag_recall_pct']:.0f}%", "of breakouts flagged early")
with c4: theme.big_stat(f"{s['breakout_flags']}", "breakout watches raised")

# split upcoming (no actual yet) vs backtest
df["IS_UPCOMING"] = df["ACTUAL_OW"].isna() | (df.get("PREDICTION_TYPE", "") == "UPCOMING")
upcoming = df[df["IS_UPCOMING"]]
hist = df[~df["IS_UPCOMING"]].copy()

theme.section("Breakout watch \u2014 did the flags pay off?",
              "Films the model flagged for breakout potential, and what actually happened.")
fl = hist[hist["BREAKOUT_FLAG"].astype(str).str.upper().isin(["TRUE", "1"])].copy()
fl = fl.sort_values("P_LARGE", ascending=False)
fl["Breakout chance"] = (fl["P_LARGE"] * 100).round().astype(int).astype(str) + "%"
fl["Predicted"] = "$" + (fl["BASE_OW"] / 1e6).round().astype(int).astype(str) + "M"
fl["Actually opened"] = "$" + (fl["ACTUAL_OW"] / 1e6).round().astype(int).astype(str) + "M"
fl["Broke out?"] = ["Yes \u2014 LARGE+" if t == "LARGE+" else "No" for t in fl["ACTUAL_TIER"]]
st.dataframe(fl[["MOVIE_TITLE", "Breakout chance", "Predicted", "Actually opened", "Broke out?"]]
             .rename(columns={"MOVIE_TITLE": "Film"}), use_container_width=True, hide_index=True)

theme.section("Upcoming releases")
if len(upcoming):
    up = upcoming.sort_values("RELEASE_DATE")
    up["Breakout chance"] = (up["P_LARGE"] * 100).round().astype(int).astype(str) + "%"
    st.dataframe(up[["MOVIE_TITLE", "RELEASE_DATE", "PRED_TIER", "Breakout chance", "SUMMARY_TEXT"]]
                 .rename(columns={"MOVIE_TITLE": "Film", "RELEASE_DATE": "Releases",
                                  "PRED_TIER": "Most likely", "SUMMARY_TEXT": "The call"}),
                 use_container_width=True, hide_index=True)
else:
    theme.story_card("No films in the upcoming window right now",
                     "New films appear here automatically once they're scored and the data is "
                     "refreshed. Each gets the same base case + breakout odds + bear/base/bull range.")

st.page_link("pages/5_Behind_the_Scenes.py", label="Next: Behind the Scenes \u2192")
