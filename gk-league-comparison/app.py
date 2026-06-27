from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from mplsoccer import PyPizza


st.set_page_config(page_title="Goalkeeper League Comparison", page_icon="🧤", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

LEAGUES = {
    "Scottish Premiership 2025/26": "SCO1_2526.xlsx",
    "Scottish Championship 2025/26": "SCO2_2526.xlsx",
}

GK_METRICS = [
    "Conceded goals per 90",
    "Clean sheets",
    "Shots against per 90",
    "Save rate, %",
    "Prevented goals per 90",
    "Exits per 90",
]

POSSESSION_METRICS = [
    "Back passes received as GK per 90",
    "Passes per 90",
    "Average pass length, m",
    "Lateral Pass Share %",
    "Short/Medium Pass Share %",
    "Accurate lateral passes, %",
    "Accurate short / medium passes, %",
    "Accurate progressive passes, %",
]

INVERTED_METRICS = {
    "Conceded goals per 90",
    "Shots against per 90",
    "Average pass length, m",
}

PERCENT_METRICS = {
    "Save rate, %",
    "Lateral Pass Share %",
    "Short/Medium Pass Share %",
    "Accurate lateral passes, %",
    "Accurate short / medium passes, %",
    "Accurate progressive passes, %",
}

PLAYER_A_COLOR = "#9E9E9E"
PLAYER_B_COLOR = "#E53935"


@st.cache_data(show_spinner=False)
def load_league(filename: str) -> pd.DataFrame:
    frame = pd.read_excel(DATA_DIR / filename)
    required = {
        "Player",
        "Team",
        "Passes per 90",
        "Lateral passes per 90",
        "Short / medium passes per 90",
        *GK_METRICS,
        *(metric for metric in POSSESSION_METRICS if "Share" not in metric),
    }
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    numeric_columns = set(GK_METRICS + POSSESSION_METRICS).difference(
        {"Lateral Pass Share %", "Short/Medium Pass Share %"}
    ) | {"Lateral passes per 90", "Short / medium passes per 90"}
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    passes = frame["Passes per 90"].replace(0, np.nan)
    frame["Lateral Pass Share %"] = (frame["Lateral passes per 90"] / passes * 100).round(2)
    frame["Short/Medium Pass Share %"] = (
        frame["Short / medium passes per 90"] / passes * 100
    ).round(2)
    return frame


def player_label(row: pd.Series) -> str:
    team = row.get("Team")
    return f"{row['Player']} — {team}" if pd.notna(team) and str(team).strip() else str(row["Player"])


def selected_row(frame: pd.DataFrame, label: str) -> pd.Series:
    labels = frame.apply(player_label, axis=1)
    return frame.loc[labels.eq(label)].iloc[0]


def format_value(metric: str, value: float) -> str:
    if pd.isna(value):
        return "—"
    if metric in PERCENT_METRICS:
        return f"{value:.2f}%"
    if metric == "Clean sheets":
        return f"{value:.0f}"
    return f"{value:.2f}"


def is_better(metric: str, first: float, second: float) -> tuple[bool, bool]:
    if pd.isna(first) or pd.isna(second):
        return False, False
    if np.isclose(first, second, equal_nan=False):
        return True, True
    if metric in INVERTED_METRICS:
        return first < second, second < first
    return first > second, second > first


def comparison_table(
    title: str,
    metrics: list[str],
    row_a: pd.Series,
    row_b: pd.Series,
    name_a: str,
    name_b: str,
) -> None:
    rows = []
    for metric in metrics:
        value_a, value_b = row_a[metric], row_b[metric]
        best_a, best_b = is_better(metric, value_a, value_b)
        metric_class = " inverted" if metric in INVERTED_METRICS else ""
        rows.append(
            f"<tr><td class='metric{metric_class}'>{metric}</td>"
            f"<td class='value{' best' if best_a else ''}'>{format_value(metric, value_a)}</td>"
            f"<td class='value{' best' if best_b else ''}'>{format_value(metric, value_b)}</td></tr>"
        )
    st.markdown(
        f"""
        <div class="table-card">
          <h3>{title}</h3>
          <table class="comparison-table">
            <thead><tr><th>Metric</th><th>{name_a}</th><th>{name_b}</th></tr></thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def percentile_values(frame: pd.DataFrame, row: pd.Series, metrics: list[str]) -> list[int]:
    values: list[int] = []
    for metric in metrics:
        series = pd.to_numeric(frame[metric], errors="coerce")
        ranks = series.rank(method="average", pct=True, ascending=metric not in INVERTED_METRICS) * 100
        rank = ranks.loc[row.name]
        values.append(0 if pd.isna(rank) else int(round(rank)))
    return values


def wrap_label(label: str) -> str:
    replacements = {
        "Conceded goals per 90": "Conceded Goals\nper 90",
        "Shots against per 90": "Shots Against\nper 90",
        "Prevented goals per 90": "Prevented Goals\nper 90",
        "Back passes received as GK per 90": "Back Passes Received\nas GK per 90",
        "Average pass length, m": "Average Pass\nLength",
        "Lateral Pass Share %": "Lateral Pass\nShare %",
        "Short/Medium Pass Share %": "Short/Medium Pass\nShare %",
        "Accurate lateral passes, %": "Accurate Lateral\nPasses %",
        "Accurate short / medium passes, %": "Accurate Short/Medium\nPasses %",
        "Accurate progressive passes, %": "Accurate Progressive\nPasses %",
    }
    return replacements.get(label, label.replace(", %", " %").title())


def comparison_pizza(
    title: str,
    metrics: list[str],
    values_a: list[int],
    values_b: list[int],
    name_a: str,
    name_b: str,
    league_a: str,
    league_b: str,
    sample_a: int,
    sample_b: int,
):
    baker = PyPizza(
        params=[wrap_label(metric) for metric in metrics],
        background_color="#F2F2F2",
        straight_line_color="#D9D9D9",
        straight_line_lw=1,
        last_circle_lw=0,
        other_circle_lw=0,
        inner_circle_size=20,
    )
    fig, _ = baker.make_pizza(
        values_a,
        compare_values=values_b,
        figsize=(9, 9.5),
        color_blank_space="same",
        slice_colors=[PLAYER_A_COLOR] * len(metrics),
        compare_colors=[PLAYER_B_COLOR] * len(metrics),
        value_colors=["#000000"] * len(metrics),
        compare_value_colors=["#FFFFFF"] * len(metrics),
        value_bck_colors=["#D6D6D6"] * len(metrics),
        compare_value_bck_colors=[PLAYER_B_COLOR] * len(metrics),
        blank_alpha=0.28,
        kwargs_slices=dict(edgecolor="#F2F2F2", linewidth=1, alpha=0.48, zorder=2),
        kwargs_compare=dict(edgecolor="#F2F2F2", linewidth=1, alpha=0.72, zorder=3),
        kwargs_params=dict(color="#000000", fontsize=10.5, va="center"),
        kwargs_values=dict(fontsize=9.5, bbox=dict(edgecolor="#555555", boxstyle="round,pad=0.2", lw=0.8)),
        kwargs_compare_values=dict(fontsize=9.5, bbox=dict(edgecolor="#7A0000", boxstyle="round,pad=0.2", lw=0.8)),
        param_location=112.5,
    )
    fig.text(0.5, 0.99, title, ha="center", va="top", size=15, weight="bold")
    fig.text(0.455, 0.94, name_a, ha="right", size=12, color="#333333", weight="bold")
    fig.text(0.5, 0.94, "vs", ha="center", size=11, color="#555555")
    fig.text(0.545, 0.94, name_b, ha="left", size=12, color=PLAYER_B_COLOR, weight="bold")
    fig.text(0.5, 0.025, f"Percentile rank within selected league | Samples: {sample_a} and {sample_b} goalkeepers", ha="center", size=8.5)
    fig.text(0.5, 0.008, f"{league_a}  •  {league_b}", ha="center", size=8, color="#555555")
    fig.subplots_adjust(top=0.87, bottom=0.08, left=0.08, right=0.92)
    fig.set_facecolor("#F2F2F2")
    return fig


st.markdown(
    """
    <style>
      .stApp { background: #f7f8fb; }
      .block-container { max-width: 1450px; padding-top: 2rem; }
      h1, h2, h3 { color: #172033 !important; }
      .subtitle { color: #667085; margin-top: -0.75rem; margin-bottom: 1.5rem; }
      .selection-card, .table-card { background: white; border: 1px solid #e4e7ec; border-radius: 14px; padding: 1rem 1.2rem; box-shadow: 0 2px 8px rgba(16,24,40,.05); }
      .table-card h3 { margin: .15rem 0 .9rem; }
      .comparison-table { width: 100%; border-collapse: collapse; font-size: .95rem; }
      .comparison-table th { background: #172033; color: white; padding: .72rem; text-align: center; }
      .comparison-table th:first-child { text-align: left; }
      .comparison-table td { border-bottom: 1px solid #eaecf0; padding: .68rem .72rem; }
      .comparison-table tr:last-child td { border-bottom: none; }
      .comparison-table .metric { color: #344054; }
      .comparison-table .metric.inverted { color: #d92d20; }
      .comparison-table .value { text-align: center; color: #344054; }
      .comparison-table .value.best { font-weight: 800; color: #101828; background: #ecfdf3; }
      .key { color: #667085; font-size: .88rem; margin: .5rem 0 1rem; }
      [data-testid="stTabs"] button { font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Goalkeeper League Comparison")
st.markdown('<p class="subtitle">Compare raw performance and league-relative percentile profiles across Scotland’s top two divisions.</p>', unsafe_allow_html=True)

league_names = list(LEAGUES)
selector_cols = st.columns(4)
with selector_cols[0]:
    league_a = st.selectbox("Player 1 league", league_names, index=0)
with selector_cols[2]:
    league_b = st.selectbox("Player 2 league", league_names, index=1)

frame_a = load_league(LEAGUES[league_a])
frame_b = load_league(LEAGUES[league_b])
labels_a = frame_a.apply(player_label, axis=1).tolist()
labels_b = frame_b.apply(player_label, axis=1).tolist()

with selector_cols[1]:
    selection_a = st.selectbox("Player 1", labels_a, index=0)
with selector_cols[3]:
    selection_b = st.selectbox("Player 2", labels_b, index=0)

row_a = selected_row(frame_a, selection_a)
row_b = selected_row(frame_b, selection_b)
name_a, name_b = str(row_a["Player"]), str(row_b["Player"])

raw_tab, radar_tab = st.tabs(["Raw Comparison", "Percentile Radars"])

with raw_tab:
    st.markdown('<p class="key"><span style="color:#d92d20">Red metrics</span> are inverted (lower is better). The better value in each row is bold and shaded.</p>', unsafe_allow_html=True)
    left, right = st.columns(2, gap="large")
    with left:
        comparison_table("GK", GK_METRICS, row_a, row_b, name_a, name_b)
    with right:
        comparison_table("Possession", POSSESSION_METRICS, row_a, row_b, name_a, name_b)

with radar_tab:
    st.caption("Each goalkeeper is ranked from 0–100 against all goalkeepers in their selected league. Inverted metrics are reversed before ranking.")
    chart_left, chart_right = st.columns(2, gap="large")
    for container, title, metrics in (
        (chart_left, "GK Percentiles", GK_METRICS),
        (chart_right, "Possession Percentiles", POSSESSION_METRICS),
    ):
        with container:
            fig = comparison_pizza(
                title,
                metrics,
                percentile_values(frame_a, row_a, metrics),
                percentile_values(frame_b, row_b, metrics),
                name_a,
                name_b,
                league_a,
                league_b,
                len(frame_a),
                len(frame_b),
            )
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
