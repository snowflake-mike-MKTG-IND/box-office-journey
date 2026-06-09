"""Cached loaders for the bundled snapshot in data/. The deployed app reads only these files."""
import json, os
import pandas as pd
import streamlit as st

_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@st.cache_data
def predictions() -> pd.DataFrame:
    df = pd.read_csv(os.path.join(_DATA, "predictions_v28.csv"))
    df.columns = [c.upper() for c in df.columns]
    return df


@st.cache_data
def journey() -> dict:
    return json.load(open(os.path.join(_DATA, "journey.json")))


@st.cache_data
def stats() -> dict:
    return json.load(open(os.path.join(_DATA, "headline_stats.json")))


@st.cache_data
def calibration() -> list:
    return json.load(open(os.path.join(_DATA, "calibration.json")))
