"""Home — The Question. Entry point for the Box Office Journey narrative app."""
import streamlit as st
import theme, dataio

theme.apply_page_config("Box Office Journey")
theme.cortex_footer()
s = dataio.stats()

theme.hero(
    "Can you call a movie's opening weekend before it opens?",
    "A six-month journey building an honest box-office prediction model on Snowflake \u2014 "
    "and what we learned when accuracy hit a wall.",
)

c1, c2, c3, c4 = st.columns(4)
with c1: theme.big_stat(f"{s['n_films']}", "films tracked")
with c2: theme.big_stat(f"{s['start_accuracy']:.0f}% \u2192 {s['tier_accuracy']:.0f}%", "tier accuracy, then \u2192 now")
with c3: theme.big_stat(f"${s['start_mae']:.0f}M \u2192 ${s['mae_millions']:.0f}M", "typical miss, then \u2192 now")
with c4: theme.big_stat(f"{s['flag_recall_pct']:.0f}%", "of breakouts now flagged early")

st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)

theme.story_card(
    "The rules we set ourselves",
    "Predict using <b>only public, pre-release signals</b> \u2014 search interest, trailer reaction, "
    "Wikipedia attention, budget, cast and genre. <b>No ticket pre-sales. No paid industry survey "
    "tracking.</b> The whole point was to see how far you can get <i>without</i> the expensive data "
    "the industry already relies on.",
)
theme.story_card(
    "Where it ends up",
    "Not a single magic number \u2014 something more useful and more honest: a most-likely opening, "
    "<b>plus the odds of a breakout</b>, plus a bear / base / bull range you can plan around.",
    kind="win",
)

theme.section("Follow the story", "Six short chapters \u2014 read in order, or jump around.")
cols = st.columns(3)
nav = [
    ("1 \u00b7 The Climb", "From a coin flip to the high 70s, version by version.", "pages/1_The_Climb.py"),
    ("2 \u00b7 The Wall", "Why accuracy stopped \u2014 and the math behind breakouts.", "pages/2_The_Wall.py"),
    ("3 \u00b7 The Reframe", "Stop guessing the number. Tell the odds.", "pages/3_The_Reframe.py"),
    ("4 \u00b7 The Track Record", "How it actually did \u2014 plus upcoming films.", "pages/4_Track_Record.py"),
    ("5 \u00b7 Behind the Scenes", "The signals we use \u2014 and the ones we refuse to.", "pages/5_Behind_the_Scenes.py"),
]
for i, (t, d, p) in enumerate(nav):
    with cols[i % 3]:
        with st.container(border=True):
            st.markdown(f"**{t}**")
            st.caption(d)
            st.page_link(p, label="Open \u2192")

st.caption(f"Track record is out-of-fold (leak-safe): every prediction was made by a model that had "
           f"never seen that film. Films released {s['date_min']} to {s['date_max']}.")
