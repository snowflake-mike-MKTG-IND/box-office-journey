"""Chapter 2 — The Wall."""
import streamlit as st
import plotly.graph_objects as go
import theme, dataio

theme.apply_page_config("The Wall")
theme.cortex_footer()
df = dataio.predictions(); s = dataio.stats()

st.title("The Wall")
st.caption("Why accuracy stopped climbing \u2014 and the math behind breakouts.")

theme.story_card(
    "Some movies open far bigger than anything about them predicts",
    "A $10M-budget horror film opens to $81M. A modest sequel triples its forecast. These "
    "<b>breakouts</b> are where every version of the model kept failing \u2014 not from a bug, but "
    "because the information simply isn't there beforehand.",
    kind="warn",
)

# predicted vs actual scatter ($M), colored by hit/miss
d = df.copy()
d["ACT_M"] = d["ACTUAL_OW"] / 1e6; d["PRED_M"] = d["PRED_OW"] / 1e6
d["status"] = ["On target" if h else "Missed the tier" for h in d["TIER_HIT"]]
fig = go.Figure()
for stt, col in [("On target", theme.SF_BLUE), ("Missed the tier", theme.ORANGE)]:
    sub = d[d["status"] == stt]
    fig.add_trace(go.Scatter(x=sub["ACT_M"], y=sub["PRED_M"], mode="markers", name=stt,
                             marker=dict(size=7, color=col, opacity=0.65),
                             text=sub["MOVIE_TITLE"],
                             hovertemplate="%{text}<br>actual $%{x:.0f}M<br>predicted $%{y:.0f}M<extra></extra>"))
lim = max(d["ACT_M"].max(), d["PRED_M"].max()) * 1.05
fig.add_trace(go.Scatter(x=[0, lim], y=[0, lim], mode="lines", name="perfect prediction",
                         line=dict(color=theme.MUTED, dash="dash", width=1)))
# annotate the famous breakouts if present
for title in ["Project Hail Mary", "Backrooms", "Scary Movie 6"]:
    r = d[d["MOVIE_TITLE"].str.contains(title, case=False, na=False)]
    if len(r):
        r = r.iloc[0]
        fig.add_annotation(x=r["ACT_M"], y=r["PRED_M"], text=title, showarrow=True,
                           arrowhead=2, ax=40, ay=-30, font=dict(size=11, color=theme.DK1))
fig.update_layout(height=520, plot_bgcolor="white", legend=dict(orientation="h", y=1.1, x=0),
                  xaxis=dict(title="What it ACTUALLY opened to ($M)", gridcolor="#EEF2F5", range=[0, lim]),
                  yaxis=dict(title="What we PREDICTED ($M)", gridcolor="#EEF2F5", range=[0, lim]),
                  margin=dict(l=10, r=10, t=30, b=10))
st.plotly_chart(fig, use_container_width=True)
st.caption("Points below the dashed line opened bigger than we predicted. The far-right strays are the breakouts.")

theme.section("The honest math: a 'noise floor'")
theme.story_card(
    "Two identical-looking films can open $50M apart",
    "We measured how much films that look <i>the same</i> on every pre-release signal differ in "
    "their actual openings. For the biggest films, that unavoidable spread is as large as the "
    "model's entire error. Translation: <b>the model is already as good as the information allows</b> "
    "\u2014 a better algorithm can't fix what the data doesn't contain.",
)
theme.story_card(
    "So we stopped trying to be more accurate \u2014 and asked a better question",
    "If we can't say exactly how big a breakout will be, can we at least say <b>how likely</b> one "
    "is? That turned out to be very answerable.",
    kind="win",
)
st.page_link("pages/3_The_Reframe.py", label="Next: The Reframe \u2192")
