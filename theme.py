"""Shared theme + layout helpers for the Box Office Journey narrative app.
Snowflake-branded, tuned for a broad (non-technical) audience: big hero text, story cards,
plain-language helpers. Ported from the technical dashboard's theme.py."""
from __future__ import annotations
import streamlit as st

# Snowflake brand palette
SF_BLUE = "#29B5E8"
DK1 = "#1A2A33"
DK2 = "#11567F"
TEAL = "#71D3DC"
ORANGE = "#FF9F36"
VIOLET = "#7D44CF"
GREEN = "#2E9E83"
MUTED = "#6B7280"

TIER_COLORS = {"SMALL": SF_BLUE, "MID": ORANGE, "LARGE+": VIOLET}

APP_CSS = f"""
<style>
  .block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 1150px; }}
  h1, h2, h3 {{ color: {DK1}; letter-spacing: -0.01em; }}
  h1 {{ font-weight: 800; }}
  h2 {{ font-weight: 700; margin-top: 1.4rem; }}
  h3 {{ font-weight: 600; color: {DK2}; }}
  div[data-testid="stMetricValue"] {{ font-weight: 800; }}
  .section-spacer {{ height: 1.5rem; }}
  /* Hero band */
  .hero {{
      background: linear-gradient(135deg, {DK2} 0%, {SF_BLUE} 100%);
      color: white; border-radius: 16px; padding: 2.2rem 2rem; margin-bottom: 1.5rem;
  }}
  .hero h1 {{ color: white; font-size: 2.4rem; margin: 0 0 0.5rem 0; }}
  .hero p {{ color: #EAF7FD; font-size: 1.15rem; margin: 0; line-height: 1.5; }}
  /* Story callout card */
  .story-card {{
      border-left: 4px solid {SF_BLUE}; background: #F7FBFE; border-radius: 8px;
      padding: 1rem 1.25rem; margin: 0.75rem 0;
  }}
  .story-card.warn {{ border-left-color: {ORANGE}; background: #FFF8F0; }}
  .story-card.win  {{ border-left-color: {GREEN};  background: #F2FBF8; }}
  .story-card h4 {{ margin: 0 0 0.3rem 0; color: {DK2}; }}
  .story-card p {{ margin: 0; color: {DK1}; line-height: 1.5; }}
  /* Prediction "card" for a single film */
  .film-card {{ border: 1px solid #E5E7EB; border-radius: 12px; padding: 1rem 1.2rem; background: white; }}
  .breakout-flag {{ color: {VIOLET}; font-weight: 700; }}
  .big-stat {{ font-size: 2.6rem; font-weight: 800; color: {DK2}; line-height: 1; }}
  .big-stat-label {{ color: {MUTED}; font-size: 0.9rem; }}
</style>
"""


def apply_page_config(title: str, icon: str = "\U0001F3AC") -> None:
    st.set_page_config(page_title=title, page_icon=icon, layout="wide", initial_sidebar_state="expanded")
    st.markdown(APP_CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str) -> None:
    st.markdown(f"<div class='hero'><h1>{title}</h1><p>{subtitle}</p></div>", unsafe_allow_html=True)


def story_card(heading: str, body: str, kind: str = "") -> None:
    cls = "story-card" + (f" {kind}" if kind else "")
    st.markdown(f"<div class='{cls}'><h4>{heading}</h4><p>{body}</p></div>", unsafe_allow_html=True)


def big_stat(value: str, label: str) -> None:
    st.markdown(f"<div class='big-stat'>{value}</div><div class='big-stat-label'>{label}</div>", unsafe_allow_html=True)


def section(title: str, caption: str | None = None) -> None:
    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    st.subheader(title)
    if caption:
        st.caption(caption)


def cortex_footer() -> None:
    with st.sidebar:
        st.divider()
        st.caption("Built on Snowflake with")
        st.markdown(
            f"<a href='https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code' target='_blank' "
            f"style='color:{SF_BLUE}; text-decoration:none; font-weight:600;'>\u2744\uFE0F Cortex Code</a>",
            unsafe_allow_html=True)
