"""Dashboard styling utilities."""

import streamlit as st


def apply_theme() -> None:
    """Apply high-contrast dark operations-console theme."""
    st.markdown(
        """
<style>
:root {
    --page: #07111f;
    --panel: #0f172a;
    --panel2: #111827;
    --border: rgba(96, 165, 250, 0.55);
    --text: #f8fafc;
    --muted: #cbd5e1;
    --blue: #2563eb;
    --cyan: #38bdf8;
    --red: #ef4444;
    --amber: #f59e0b;
    --green: #22c55e;
}

.stApp {
    background: linear-gradient(180deg, #06101d 0%, #0b1220 45%, #0f172a 100%);
    color: var(--text);
}

.block-container {
    max-width: 1500px;
    padding-top: 1.4rem;
    padding-left: 2.4rem;
    padding-right: 2.4rem;
    padding-bottom: 2.4rem;
}

[data-testid="stSidebar"] {
    background: #07111f;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: var(--text) !important;
}

[data-baseweb="select"] > div {
    background-color: #111827 !important;
    color: var(--text) !important;
    border: 1px solid rgba(125, 211, 252, 0.75) !important;
    border-radius: 12px !important;
    box-shadow: none !important;
}

[data-baseweb="select"] span,
[data-baseweb="select"] svg {
    color: var(--text) !important;
    fill: var(--text) !important;
}

div[data-baseweb="popover"],
ul[role="listbox"] {
    background-color: #111827 !important;
    border: 1px solid rgba(125, 211, 252, 0.75) !important;
    border-radius: 12px !important;
}

li[role="option"] {
    background-color: #111827 !important;
    color: var(--text) !important;
}

li[role="option"]:hover,
li[aria-selected="true"] {
    background-color: #1d4ed8 !important;
    color: #ffffff !important;
}

h1, h2, h3, h4, h5, h6 {
    color: var(--text) !important;
    font-weight: 800 !important;
}

p, li, label {
    color: var(--muted) !important;
}

.hero {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 52%, #38bdf8 100%);
    border: 1px solid rgba(125, 211, 252, 0.75);
    padding: 26px 28px;
    border-radius: 20px;
    margin: 0 0 18px 0;
    box-shadow: 0 18px 40px rgba(37, 99, 235, 0.28);
}

.hero h1 {
    color: #ffffff !important;
    margin: 0 0 8px 0;
}

.hero p {
    color: #eff6ff !important;
    margin: 0;
    font-size: 16px;
}

.glass-card,
.summary-box {
    background: rgba(15, 23, 42, 0.97);
    border: 1px solid var(--border);
    border-left: 6px solid var(--cyan);
    border-radius: 16px;
    padding: 18px 20px;
    margin: 0 0 18px 0;
    box-shadow: 0 12px 28px rgba(0,0,0,0.26);
}

.signal-card,
.signal-card-critical,
.signal-card-warning {
    border-radius: 16px;
    padding: 17px 20px;
    margin-bottom: 14px;
    box-shadow: 0 12px 28px rgba(0,0,0,0.22);
}

.signal-card {
    background: rgba(12, 74, 110, 0.58);
    border: 1px solid rgba(56,189,248,0.60);
    border-left: 7px solid var(--cyan);
}

.signal-card-critical {
    background: rgba(127, 29, 29, 0.55);
    border: 1px solid rgba(248,113,113,0.68);
    border-left: 7px solid var(--red);
}

.signal-card-warning {
    background: rgba(113, 63, 18, 0.56);
    border: 1px solid rgba(251,191,36,0.68);
    border-left: 7px solid var(--amber);
}

[data-testid="metric-container"] {
    background: linear-gradient(135deg, #10244a, #1d4ed8);
    border: 1px solid rgba(125, 211, 252, 0.78);
    border-radius: 16px;
    padding: 17px;
    box-shadow: 0 12px 28px rgba(29, 78, 216, 0.25);
}

[data-testid="metric-container"] label,
[data-testid="metric-container"] div {
    color: #ffffff !important;
}

button[data-baseweb="tab"] {
    background-color: #111827;
    color: #e5e7eb;
    border-radius: 11px;
    margin-right: 7px;
    padding: 10px 16px;
    border: 1px solid #334155;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #0369a1, #2563eb);
    color: #ffffff;
    border: 1px solid #7dd3fc;
}

[data-testid="stPlotlyChart"] {
    background-color: rgba(15, 23, 42, 0.98);
    border: 1px solid rgba(96,165,250,0.55);
    border-radius: 16px;
    padding: 12px;
    box-shadow: 0 12px 28px rgba(0,0,0,0.26);
    margin-bottom: 18px;
}

.ops-table {
    width: 100%;
    border-collapse: collapse;
    background: rgba(15, 23, 42, 0.98);
    border: 1px solid rgba(96,165,250,0.60);
    border-radius: 16px;
    overflow: hidden;
    margin-top: 10px;
    margin-bottom: 22px;
    box-shadow: 0 12px 28px rgba(0,0,0,0.25);
}

.ops-table th {
    background: #1e3a8a;
    color: #ffffff;
    padding: 11px 12px;
    text-align: left;
    font-weight: 800;
    border-bottom: 1px solid #60a5fa;
}

.ops-table td {
    color: #e5e7eb;
    padding: 10px 12px;
    border-bottom: 1px solid #1e293b;
}

.ops-table tr:nth-child(even) {
    background-color: rgba(30,41,59,0.76);
}

.ops-table tr:hover {
    background-color: rgba(30,64,175,0.50);
}

.badge {
    display: inline-block;
    padding: 4px 9px;
    border-radius: 999px;
    background: rgba(14,165,233,0.20);
    border: 1px solid rgba(56,189,248,0.45);
    color: #e0f2fe !important;
    font-size: 12px;
    font-weight: 700;
}

.stAlert {
    background-color: rgba(15, 23, 42, 0.98) !important;
    border: 1px solid rgba(96,165,250,0.55) !important;
    border-radius: 14px;
}

@media (max-width: 900px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )
