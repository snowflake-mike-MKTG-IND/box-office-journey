"""Chapter 1 — The Climb."""
import streamlit as st
import plotly.graph_objects as go
import theme, dataio

theme.apply_page_config("The Climb")
theme.cortex_footer()
j = dataio.journey(); climb = j["climb"]

st.title("The Climb")
st.caption("From a coin flip to the high 70s \u2014 better signals, smarter structure.")

theme.story_card(
    "Starting point: barely better than guessing",
    "Version 2 got the size class right 58% of the time and missed the dollar figure by about "
    "$17M on average. The job from here: add signals that actually carry pre-release demand, and "
    "give the model a sensible structure.",
)

versions = [c["version"] for c in climb]
acc = [c["accuracy"] for c in climb]
mae = [c["mae"] for c in climb]

fig = go.Figure()
fig.add_trace(go.Scatter(x=versions, y=acc, name="Tier accuracy (%)", mode="lines+markers",
                         line=dict(color=theme.SF_BLUE, width=3), marker=dict(size=9), yaxis="y1"))
fig.add_trace(go.Scatter(x=versions, y=mae, name="Typical miss ($M)", mode="lines+markers",
                         line=dict(color=theme.ORANGE, width=3, dash="dot"), marker=dict(size=9), yaxis="y2"))
fig.update_layout(
    height=440, plot_bgcolor="white", hovermode="x unified",
    legend=dict(orientation="h", y=1.12, x=0),
    yaxis=dict(title="Tier accuracy (%)", range=[50, 85], gridcolor="#EEF2F5"),
    yaxis2=dict(title="Typical miss ($M)", overlaying="y", side="right", range=[6, 18], showgrid=False),
    xaxis=dict(title=None),
    margin=dict(l=10, r=10, t=30, b=10),
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("##### What changed at each step")
for c in climb:
    st.markdown(f"**{c['version']} \u00b7 {c['label']}** \u2014 {c['note']}  \n"
                f"<span style='color:{theme.MUTED}'>{c['accuracy']:.0f}% accuracy \u00b7 "
                f"~${c['mae']:.1f}M typical miss</span>", unsafe_allow_html=True)

theme.story_card(
    "Notice where the line flattens",
    "Accuracy raced from 58% into the high 70s \u2014 then stalled. Hand-tuned rules squeezed the "
    "error a little lower, but the size-class accuracy wouldn't break past the high 70s / ~80%. "
    "That plateau is the next chapter.",
    kind="warn",
)
st.page_link("pages/2_The_Wall.py", label="Next: The Wall \u2192")
