"""Chapter 3 — The Reframe (breakout odds)."""
import streamlit as st
import plotly.graph_objects as go
import theme, dataio

theme.apply_page_config("The Reframe")
theme.cortex_footer()
df = dataio.predictions(); calib = dataio.calibration()

st.title("The Reframe")
st.caption("Stop guessing the number. Tell the odds.")

theme.story_card(
    "The model already knew which films were risky",
    "On the breakouts it 'missed,' it wasn't clueless \u2014 it was giving them a real chance of going "
    "big. The single best-guess number simply <b>hid</b> that signal by averaging it away. So we "
    "surfaced it.",
    kind="win",
)

theme.section("What a prediction looks like now")
# pull a real flagged breakout card (Project Hail Mary if present, else highest-prob flagged)
flagged = df[df["BREAKOUT_FLAG"].astype(str).str.upper().isin(["TRUE", "1"])].copy()
phm = df[df["MOVIE_TITLE"].str.contains("Hail Mary", case=False, na=False)]
pick = phm.iloc[0] if len(phm) else (flagged.sort_values("P_LARGE", ascending=False).iloc[0] if len(flagged) else df.iloc[0])
c1, c2 = st.columns([3, 2])
with c1:
    st.markdown(f"<div class='film-card'><h4 style='margin-top:0'>{pick['MOVIE_TITLE']}</h4>"
                f"<p style='font-size:1.05rem'>{pick['SUMMARY_TEXT']}</p>"
                f"<p style='color:{theme.MUTED};margin-top:0.5rem'>Actual opening: "
                f"<b>${pick['ACTUAL_OW']/1e6:.0f}M</b></p></div>", unsafe_allow_html=True)
with c2:
    theme.story_card("How to read it",
                     "A <b>base case</b> (most likely), a <b>breakout watch</b> when the odds of a big "
                     "open are real, and a <b>bear / base / bull</b> range \u2014 in plain English, no "
                     "statistics degree required.")

theme.section("Are the odds trustworthy? Yes \u2014 they're calibrated",
              "When the model says a film has a given breakout chance, that's roughly how often it happens.")
labels = [c["bucket"] for c in calib]
rates = [c["actual_breakout_rate"] for c in calib]
ns = [c["n"] for c in calib]
fig = go.Figure(go.Bar(x=labels, y=rates, marker_color=theme.SF_BLUE,
                       text=[f"{r}%<br><span style='font-size:0.8em'>n={n}</span>" for r, n in zip(rates, ns)],
                       textposition="outside"))
fig.update_layout(height=380, plot_bgcolor="white",
                  yaxis=dict(title="Actually broke out (%)", range=[0, 100], gridcolor="#EEF2F5"),
                  xaxis=dict(title="What the model said the breakout chance was"),
                  margin=dict(l=10, r=10, t=20, b=10))
st.plotly_chart(fig, use_container_width=True)
theme.story_card(
    "Read it left to right",
    "Films the model put under 15% almost never broke out (~1%). Films it flagged at '1 in 3' broke "
    "out about a third of the time. Films over 50% broke out ~87% of the time. <b>The odds mean what "
    "they say.</b>",
)
st.page_link("pages/4_Track_Record.py", label="Next: The Track Record \u2192")
