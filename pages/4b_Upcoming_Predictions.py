"""Chapter 4b — Upcoming Predictions: detailed per-film cards with 'why' explanations."""
import streamlit as st
import pandas as pd
import numpy as np
import theme, dataio

theme.apply_page_config("Upcoming Predictions")
theme.cortex_footer()

st.title("Upcoming Predictions")
st.caption("Every film gets a base case, breakout odds, and the key signals behind the call.")

preds = dataio.predictions()
feats = dataio.upcoming_features()

preds["IS_UPCOMING"] = preds["ACTUAL_OW"].isna() | (preds.get("PREDICTION_TYPE", "") == "UPCOMING")
upcoming = preds[preds["IS_UPCOMING"]].sort_values("RELEASE_DATE").reset_index(drop=True)

if not len(upcoming):
    theme.story_card("No upcoming predictions right now",
                     "New films appear here automatically once scored and data is refreshed.")
    st.stop()

# Signal display config: (column, label, format, description)
SIGNALS = [
    ("ROLLING_7D", "Google Trends (7-day avg)", ".0f", "Search interest momentum — how much people are Googling this film"),
    ("ROLLING_3D", "Google Trends (3-day avg)", ".0f", "Very recent search surge"),
    ("TRENDS_PEAK_SO_FAR", "Peak search interest", ".0f", "Highest single-day search interest seen so far"),
    ("VELOCITY_7D", "Trend velocity", ".2f", "Rate of change in search interest (>1 = accelerating)"),
    ("YT_COMMENTS", "YouTube trailer comments", ",d", "Volume of trailer engagement on YouTube"),
    ("BUDGET", "Production budget", "$,.0f", "Studio investment — higher budgets get wider releases"),
    ("TMDB_POPULARITY", "TMDB popularity", ".1f", "Community awareness on The Movie Database"),
    ("MAX_STAR_POWER", "Star power (lead)", ".0f", "Lead actor's box office track record (0-10 scale)"),
    ("TOP2_STAR_POWER", "Star power (top 2)", ".0f", "Combined top-2 actors"),
    ("WIKI_ROLLING_7D", "Wikipedia views (7-day avg)", ".0f", "Daily Wikipedia page views in the past week"),
    ("WIKI_PEAK", "Wikipedia peak day", ".0f", "Highest single-day Wikipedia views"),
    ("KNOWN_IP_TIER", "IP strength", ".0f", "Intellectual property tier (0=original, 1=niche, 2=moderate, 3=high)"),
    ("PREDECESSOR_OW_LOG", "Franchise predecessor", ".1f", "Log of prior installment's OW (0 = no predecessor)"),
]

IP_LABELS = {0: "Original", 1: "Niche IP", 2: "Moderate IP", 3: "High-Profile IP"}
TIER_EMOJI = {"SMALL": "\U0001F539", "MID": "\U0001F536", "LARGE+": "\U0001F525"}


def render_film_card(row, feat_row):
    """Render a single film's prediction card."""
    movie_id = int(row["MOVIE_ID"])
    title = row["MOVIE_TITLE"]
    release = str(row["RELEASE_DATE"])[:10]
    tier = row["PRED_TIER"]
    base_ow = row["BASE_OW"] / 1e6
    bear_ow = row["BEAR_OW"] / 1e6
    bull_ow = row["BULL_OW"] / 1e6
    p_large = row["P_LARGE"] * 100
    p_mid = row["P_MID"] * 100
    p_small = row["P_SMALL"] * 100
    breakout_prob = row.get("BREAKOUT_PROB", 0) or 0
    breakout_flag = str(row.get("BREAKOUT_FLAG", "")).upper() in ("TRUE", "1")
    model_ver = row.get("MODEL_VERSION", "")
    summary = row.get("SUMMARY_TEXT", "")

    # Determine status from model version
    is_final = "@D3" in str(model_ver) or "@D1" in str(model_ver)
    status_label = "FINAL" if is_final else "UPCOMING"
    status_color = theme.GREEN if is_final else theme.SF_BLUE

    # Header
    tier_color = theme.TIER_COLORS.get(tier, theme.MUTED)
    st.markdown(
        f"<div style='border: 2px solid {status_color}; border-radius: 12px; padding: 1.2rem; margin-bottom: 0.5rem;'>"
        f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
        f"<div><span style='font-size:1.5rem; font-weight:800; color:{theme.DK1};'>{title}</span>"
        f"<span style='margin-left:1rem; font-size:0.85rem; color:{theme.MUTED};'>Opens {release}</span></div>"
        f"<div><span style='background:{status_color}; color:white; padding:3px 10px; border-radius:12px; "
        f"font-size:0.75rem; font-weight:700;'>{status_label}</span>"
        f"<span style='margin-left:0.5rem; font-size:0.75rem; color:{theme.MUTED};'>{model_ver}</span></div>"
        f"</div></div>",
        unsafe_allow_html=True)

    # Prediction row
    c1, c2, c3, c4 = st.columns([2, 2, 2, 4])
    with c1:
        st.markdown(f"<div style='text-align:center;'>"
                    f"<div style='font-size:0.75rem; color:{theme.MUTED};'>Predicted tier</div>"
                    f"<div style='font-size:1.8rem; font-weight:800; color:{tier_color};'>"
                    f"{TIER_EMOJI.get(tier, '')} {tier}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div style='text-align:center;'>"
                    f"<div style='font-size:0.75rem; color:{theme.MUTED};'>Base case</div>"
                    f"<div style='font-size:1.8rem; font-weight:800; color:{theme.DK2};'>"
                    f"${base_ow:.0f}M</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div style='text-align:center;'>"
                    f"<div style='font-size:0.75rem; color:{theme.MUTED};'>Range</div>"
                    f"<div style='font-size:1.1rem; font-weight:600; color:{theme.DK1};'>"
                    f"${bear_ow:.0f}M &mdash; ${bull_ow:.0f}M</div></div>", unsafe_allow_html=True)
    with c4:
        if breakout_flag:
            st.markdown(f"<div style='text-align:center;'>"
                        f"<div style='font-size:0.75rem; color:{theme.MUTED};'>Breakout chance</div>"
                        f"<div style='font-size:1.3rem; font-weight:800; color:{theme.VIOLET};'>"
                        f"\U0001F680 {breakout_prob*100:.0f}% breakout watch</div></div>",
                        unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:center;'>"
                        f"<div style='font-size:0.75rem; color:{theme.MUTED};'>Tier probabilities</div>"
                        f"<div style='font-size:0.95rem; color:{theme.DK1};'>"
                        f"S: {p_small:.0f}% &nbsp; M: {p_mid:.0f}% &nbsp; L+: {p_large:.0f}%</div></div>",
                        unsafe_allow_html=True)

    # Why this call — signal breakdown
    if feat_row is not None and len(feat_row):
        with st.expander("Why this call — key signals", expanded=True):
            render_signals(feat_row)
    else:
        st.caption("Feature detail not available for this film.")

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)


def render_signals(feat_row):
    """Render the signal breakdown with percentile bars."""
    cols_left, cols_right = st.columns(2)

    # Group signals into categories
    demand_signals = [s for s in SIGNALS if s[0] in ("ROLLING_7D", "ROLLING_3D", "TRENDS_PEAK_SO_FAR", "VELOCITY_7D")]
    audience_signals = [s for s in SIGNALS if s[0] in ("YT_COMMENTS", "WIKI_ROLLING_7D", "WIKI_PEAK")]
    profile_signals = [s for s in SIGNALS if s[0] in ("BUDGET", "MAX_STAR_POWER", "KNOWN_IP_TIER", "TMDB_POPULARITY")]

    with cols_left:
        st.markdown(f"**Demand momentum**")
        for col, label, fmt, desc in demand_signals:
            render_signal_bar(feat_row, col, label, fmt, desc)

        st.markdown(f"**Audience buzz**")
        for col, label, fmt, desc in audience_signals:
            render_signal_bar(feat_row, col, label, fmt, desc)

    with cols_right:
        st.markdown(f"**Film profile**")
        for col, label, fmt, desc in profile_signals:
            if col == "KNOWN_IP_TIER":
                val = feat_row.get(col, 0) or 0
                ip_label = IP_LABELS.get(int(val), f"Tier {int(val)}")
                st.markdown(f"<div style='margin-bottom:0.6rem;'>"
                            f"<div style='font-size:0.8rem; color:{theme.MUTED};'>{label}</div>"
                            f"<div style='font-size:1rem; font-weight:600;'>{ip_label}</div>"
                            f"</div>", unsafe_allow_html=True)
            elif col == "BUDGET":
                val = feat_row.get(col, 0) or 0
                pctl = feat_row.get(f"{col}_PCTL", 0) or 0
                st.markdown(f"<div style='margin-bottom:0.6rem;'>"
                            f"<div style='font-size:0.8rem; color:{theme.MUTED};'>{label}</div>"
                            f"<div style='font-size:1rem; font-weight:600;'>${val/1e6:.0f}M "
                            f"<span style='font-size:0.8rem; color:{theme.MUTED};'>(top {100-int(pctl)}%)</span></div>"
                            f"</div>", unsafe_allow_html=True)
            else:
                render_signal_bar(feat_row, col, label, fmt, desc)

        # Predecessor / franchise info
        pred_log = feat_row.get("PREDECESSOR_OW_LOG", 0) or 0
        if pred_log > 0:
            pred_ow = np.exp(pred_log) / 1e6
            st.markdown(f"<div style='margin-bottom:0.6rem;'>"
                        f"<div style='font-size:0.8rem; color:{theme.MUTED};'>Franchise predecessor OW</div>"
                        f"<div style='font-size:1rem; font-weight:600;'>~${pred_ow:.0f}M</div>"
                        f"</div>", unsafe_allow_html=True)


def render_signal_bar(feat_row, col, label, fmt, desc):
    """Render a single signal as value + percentile bar."""
    val = feat_row.get(col, 0)
    pctl = feat_row.get(f"{col}_PCTL", 0)
    if pd.isna(val): val = 0
    if pd.isna(pctl): pctl = 0
    val = float(val)
    pctl = int(pctl)

    # Format value
    if fmt == ",d":
        val_str = f"{int(val):,}"
    elif fmt.startswith("$"):
        val_str = f"${val:,.0f}"
    else:
        val_str = f"{val:{fmt}}"

    # Color the percentile bar
    if pctl >= 80:
        bar_color = theme.GREEN
    elif pctl >= 50:
        bar_color = theme.SF_BLUE
    elif pctl >= 20:
        bar_color = theme.ORANGE
    else:
        bar_color = theme.MUTED

    pctl_label = f"top {100-pctl}%" if pctl >= 50 else f"bottom {pctl}%"

    st.markdown(
        f"<div style='margin-bottom:0.6rem;'>"
        f"<div style='display:flex; justify-content:space-between; align-items:baseline;'>"
        f"<span style='font-size:0.8rem; color:{theme.MUTED};'>{label}</span>"
        f"<span style='font-size:0.9rem; font-weight:600;'>{val_str}</span></div>"
        f"<div style='background:#E5E7EB; border-radius:4px; height:6px; width:100%; margin-top:2px;'>"
        f"<div style='background:{bar_color}; border-radius:4px; height:6px; width:{pctl}%;'></div></div>"
        f"<div style='font-size:0.7rem; color:{theme.MUTED};'>{pctl_label} of films at this stage</div>"
        f"</div>",
        unsafe_allow_html=True)


# --- Main render loop ---
theme.section(f"{len(upcoming)} films in the prediction window")

for _, row in upcoming.iterrows():
    movie_id = int(row["MOVIE_ID"])
    # Match features by movie_id
    feat_match = feats[feats["MOVIE_ID"] == movie_id] if len(feats) else pd.DataFrame()
    feat_row = feat_match.iloc[0].to_dict() if len(feat_match) else None
    render_film_card(row, feat_row)

st.divider()
st.page_link("pages/5_Behind_the_Scenes.py", label="Next: Behind the Scenes \u2192")
