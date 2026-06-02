"""Data loading utilities."""

from pathlib import Path
from typing import List, Tuple
import json

import pandas as pd
import streamlit as st

from config import BUSINESS_OUTCOMES, DATA_FILES, HARD_FAILURE_OUTCOMES


def resolve_file(possible_names: List[str]) -> str:
    """Return the first available local filename from accepted candidates."""
    for name in possible_names:
        if Path(name).exists():
            return name
    raise FileNotFoundError(f"Could not find any of these files: {possible_names}")


@st.cache_data
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load all four datasets and add operational helper fields.

    Returns:
        ingestion, agent, api, alerts DataFrames.
    """
    ingestion = pd.read_csv(resolve_file(DATA_FILES["ingestion"]))
    agent = pd.read_csv(resolve_file(DATA_FILES["agent"]))
    api = pd.read_csv(resolve_file(DATA_FILES["api"]))

    with open(resolve_file(DATA_FILES["alerts"]), "r") as f:
        alerts = pd.DataFrame(json.load(f))

    for df in [ingestion, agent, api, alerts]:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["date"] = df["timestamp"].dt.date

    ingestion["is_failure"] = ingestion["status"] != "SUCCESS"

    # True platform failures only. Business outcomes are tracked separately.
    agent["is_hard_failure"] = agent["outcome"].isin(HARD_FAILURE_OUTCOMES)
    agent["is_business_outcome"] = agent["outcome"].isin(BUSINESS_OUTCOMES)

    api["is_breaker_open"] = api["circuit_breaker_status"].eq("OPEN")

    return ingestion, agent, api, alerts
