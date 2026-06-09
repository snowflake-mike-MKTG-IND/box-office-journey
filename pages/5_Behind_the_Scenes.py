"""Chapter 5 — Behind the Scenes (light, broad-audience)."""
import streamlit as st
import theme

theme.apply_page_config("Behind the Scenes")
theme.cortex_footer()

st.title("Behind the Scenes")
st.caption("How it works \u2014 in plain language.")

theme.section("The signals we use")
c1, c2, c3 = st.columns(3)
with c1: theme.story_card("Search interest", "Google Trends \u2014 how much the public is searching for a film as release nears.")
with c2: theme.story_card("Trailer reaction", "YouTube trailer comments and engagement \u2014 genuine audience pull, not ad spend.")
with c3: theme.story_card("Wikipedia attention", "Page views \u2014 a third independent read on pre-release curiosity.")
st.caption("Plus the basics: budget, cast, genre, studio, and release timing.")

theme.section("The signals we deliberately refuse")
theme.story_card(
    "No ticket pre-sales. No paid industry tracking.",
    "The industry's standard projections lean on pre-sales and expensive survey tracking. We left "
    "those out on purpose. The goal was to see how far <b>freely available, pre-release signals</b> "
    "can get you \u2014 which makes the result both cheaper to run and a fairer test of what's "
    "actually knowable.",
    kind="warn",
)

theme.section("Why we trust the numbers")
theme.story_card("Out-of-fold testing",
                 "Every film in the track record was predicted by a model that had <b>never seen it</b>. "
                 "No grading our own homework.")
theme.story_card("Calibrated odds",
                 "The breakout probabilities are checked against reality \u2014 '1 in 3' really happens "
                 "about a third of the time.")
theme.story_card("Honest about limits",
                 "We can't pin a breakout to an exact number \u2014 nobody can, beforehand \u2014 so we "
                 "report the odds and a range instead of a false-precision guess.", kind="win")

theme.section("Built on Snowflake")
st.markdown(
    "The data pipeline, models, and this app were built on **Snowflake** with the help of "
    "**Cortex Code** \u2014 from raw box-office and demand data through to the calibrated predictions "
    "you see here. The model is versioned in the Snowflake Model Registry; predictions live in "
    "Snowflake tables and refresh into this app.")
st.page_link("app.py", label="\u2190 Back to the start")
