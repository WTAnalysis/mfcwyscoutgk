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
TEAM_COLUMN = "Team within selected timeframe"

LEAGUES = {
    "Scottish Premiership 2025/26": "SCO1_2526.xlsx",
    "Scottish Championship 2025/26": "SCO2_2526.xlsx",
    "Scottish Championship 2024/25": "SCO2_2425.xlsx",
    "Ligue 2 2022/23": "FRA2_2223.xlsx",
    "Premier League 2 2025/26": "PL2_2526.xlsx",
    "English U18 Premier League 2025/26": "EU18_2526.xlsx",
    "English National League 2025/26": "ENG5_2526.xlsx",
    "English National League N/S 2025/26": "ENG6_2526.xlsx",
    "English Professional Development League 2025/26": "PDL_2526.xlsx",
    "Scottish League One 2025/26": "SCO3_2526.xlsx",
    "Scottish League Two 2025/26": "SCO4_2526.xlsx",
    "Austrian 2. Liga 2025/26": "AUT2_2526.xlsx",
    "Belgian Challenger Pro League 2025/26": "BEL2_2526.xlsx",
    "Bosnian Primera Liga 2025/26": "BOS1_2526.xlsx",
    "Bulgarian First League 2025/26": "BUL1_2526.xlsx",
    "Canadian Premier League 2025": "CAN1_2025.xlsx",
    "Canadian Premier League 2026": "CAN1_2026.xlsx",
    "Croatian Superleague 2025/26": "CRO1_2526.xlsx",
    "Cyprus 1. Division 2025/26": "CYP1_2526.xlsx",
    "Czech Chance Liga 2025/26": "CZE1_2526.xlsx",
    "Czech Chance National Liga 2025/26": "CZE2_2526.xlsx",
    "Danish 1. Division 2024/25": "DEN2_2425.xlsx",
    "Danish 1. Division 2025/26": "DEN2_2526.xlsx",
    "Danish 2. Division 2024/25": "DEN3_2425.xlsx",
    "Danish 2. Division 2025/26": "DEN3_2526.xlsx",
    "Estonian Premium Liga 2025/26": "EST1_2526.xlsx",
    "Finnish Ykkosliiga 2025": "FIN2_2025.xlsx",
    "Finnish Ykkosliiga 2026": "FIN2_2026.xlsx",
    "French National 2025/26": "FRA3_2526.xlsx",
    "Georgian Erovnuli Liga 2025": "GEO1_2025.xlsx",
    "Georgian Erovnuli Liga 2026": "GEO1_2026.xlsx",
    "German 3. Liga 2025/26": "GER3_2526.xlsx",
    "German U19 Bundesliga 2025/26": "GERU19_2526.xlsx",
    "Hungarian NB1 2025/26": "HUN1_2526.xlsx",
    "Hungarian NB2 2025/26": "HUN2_2526.xlsx",
    "Italian Serie C 2025/26": "ITA3_2526.xlsx",
    "Korean K League 2025": "KOR1_2025.xlsx",
    "Korean K League 2026": "KOR1_2026.xlsx",
    "Latvian Virsliga 2025": "LAT1_2025.xlsx",
    "Latvian Virsliga 2026": "LAT1_2026.xlsx",
    "Dutch Eerste Divisie 2025/26": "NED2_2526.xlsx",
    "Northern Irish Premiership 2025/26": "NIR1_2526.xlsx",
    "Norwegian Obos Ligaen 2025": "NOR2_2025.xlsx",
    "Norwegian Obos Ligaen 2026": "NOR2_2026.xlsx",
    "Portuguese Segunda Liga 2025/26": "POR2_2526.xlsx",
    "Romanian Superliga 2025/26": "ROM1_2526.xlsx",
    "Serbian Super Liga 2025/26": "SER1_2526.xlsx",
    "Slovakian Nike Liga 2025/26": "SLK1_2526.xlsx",
    "Slovenian 1. SNL 2025/26": "SLV1_2526.xlsx",
    "Spanish Primera Division 2025/26": "SPA3_2526.xlsx",
    "Swedish Superettan 2025": "SWE2_2025.xlsx",
    "Swedish Superettan 2026": "SWE2_2026.xlsx",
    "Swedish Ettan 2025": "SWE3_2025.xlsx",
    "Swedish Ettan 2026": "SWE3_2026.xlsx",
    "Swedish Allsvenskan Academy 2025": "SWEA_2025.xlsx",
    "Swedish Allsvenskan Academy 2026": "SWEA_2026.xlsx",
    "Swiss Challenger League 2025/26": "SWI2_2526.xlsx",
    "USA USL League 1 2025": "USA3_2025.xlsx",
    "USA USL League 1 2026": "USA3_2026.xlsx",
    "USA USL Championship 2025": "USA2_2025.xlsx",
    "USA USL Championship 2026": "USA2_2026.xlsx",
    "USA MLS Next Pro 2025": "MLSA_2025.xlsx",
    "USA MLS Next Pro 2026": "MLSA_2026.xlsx",
    "Welsh Premier League 2025/26": "WAL1_2526.xlsx",
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
        TEAM_COLUMN,
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
    team = row.get(TEAM_COLUMN)
    return f"{row['Player']} — {team}" if pd.notna(team) and str(team).strip() else str(row["Player"])


def player_chart_label(row: pd.Series) -> str:
    """Return Player - Team - Age while gracefully handling missing values."""
    parts = [str(row["Player"])]
    team = row.get(TEAM_COLUMN)
    if pd.notna(team) and str(team).strip():
        parts.append(str(team).strip())
    age = row.get("Age")
    if pd.notna(age) and str(age).strip():
        try:
            age = str(int(float(age)))
        except (TypeError, ValueError):
            age = str(age).strip()
        parts.append(age)
    return " - ".join(parts)


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


def league_percentile_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Build the pizza-chart percentile ranks for every player in a league."""
    result = pd.DataFrame(index=frame.index)
    for column in ("Player", TEAM_COLUMN, "Age"):
        result[column] = frame[column] if column in frame.columns else "—"
    for metric in GK_METRICS + POSSESSION_METRICS:
        series = pd.to_numeric(frame[metric], errors="coerce")
        result[metric] = (
            series.rank(method="average", pct=True, ascending=metric not in INVERTED_METRICS)
            .mul(100)
            .round()
            .astype("Int64")
        )
    return result


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
      html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: #000000 !important; }
      [data-testid="stHeader"] { background: #000000 !important; }
      .block-container { max-width: 1450px; padding-top: 2rem; }
      h1, h2, h3 { color: #ffffff !important; }
      p, label, .stCaption { color: #ffffff !important; }
      .subtitle { color: #d0d5dd !important; margin-top: -0.75rem; margin-bottom: 1.5rem; }
      .selection-card, .table-card { background: #000000; border: 1px solid #ffffff; border-radius: 14px; padding: 1rem 1.2rem; box-shadow: none; }
      .table-card h3 { margin: .15rem 0 .9rem; }
      .comparison-table { width: 100%; border-collapse: collapse; font-size: .95rem; }
      .comparison-table th { background: #ffffff; color: #000000; padding: .72rem; text-align: center; border-right: 1px solid #000000; }
      .comparison-table th:first-child { text-align: left; }
      .comparison-table td { background: #000000; color: #ffffff; border-bottom: 1px solid #ffffff; padding: .68rem .72rem; }
      .comparison-table tr:last-child td { border-bottom: none; }
      .comparison-table .metric { color: #ffffff; }
      .comparison-table .metric.inverted { color: #ff6b6b; }
      .comparison-table .value { text-align: center; color: #ffffff; }
      .comparison-table .value.best { font-weight: 800; color: #ffffff; background: #123d2a; }
      .key { color: #ffffff; font-size: .88rem; margin: .5rem 0 1rem; }
      [data-testid="stWidgetLabel"] p { color: #ffffff !important; font-weight: 600; }
      [data-baseweb="select"] > div { background-color: #111111 !important; border: 1px solid #ffffff !important; }
      [data-baseweb="select"] span, [data-baseweb="select"] svg { color: #ffffff !important; fill: #ffffff !important; }
      [data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] { background-color: #111111 !important; color: #ffffff !important; }
      [data-testid="stTabs"] button { font-weight: 700; }
      [data-testid="stTabs"] button p { color: #ffffff !important; }
      [data-testid="stTabs"] button[aria-selected="true"] p { color: #ff6b6b !important; }
      [data-testid="stTabs"] button:hover p { color: #ff9b9b !important; }
      [data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: #ff6b6b !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Goalkeeper League Comparison")
st.markdown('<p class="subtitle">Compare raw performance and league-relative percentile profiles across selected competitions.</p>', unsafe_allow_html=True)

league_names = list(LEAGUES)
selector_cols = st.columns(4)
with selector_cols[0]:
    league_a = st.selectbox("Competition & Player to compare", league_names, index=0)
with selector_cols[2]:
    league_b = st.selectbox("Goalkeeper Search competition & player", league_names, index=1)

frame_a = load_league(LEAGUES[league_a])
frame_b = load_league(LEAGUES[league_b])
labels_a = frame_a.apply(player_label, axis=1).tolist()
labels_b = frame_b.apply(player_label, axis=1).tolist()

with selector_cols[1]:
    selection_a = st.selectbox("Player to compare", labels_a, index=0)
with selector_cols[3]:
    selection_b = st.selectbox("Goalkeeper Search player", labels_b, index=0)

row_a = selected_row(frame_a, selection_a)
row_b = selected_row(frame_b, selection_b)
name_a, name_b = str(row_a["Player"]), str(row_b["Player"])
chart_name_a, chart_name_b = player_chart_label(row_a), player_chart_label(row_b)

raw_tab, radar_tab, league_data_tab = st.tabs(["Raw Comparison", "Percentile Radars", "League Data"])

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
                chart_name_a,
                chart_name_b,
                league_a,
                league_b,
                len(frame_a),
                len(frame_b),
            )
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

with league_data_tab:
    st.caption(
        f"Percentile ranks for all goalkeepers in {league_b}. "
        f"Click any metric header to sort; Player, {TEAM_COLUMN} and Age remain pinned while scrolling."
    )
    percentile_table = league_percentile_table(frame_b)
    metric_options = GK_METRICS + POSSESSION_METRICS
    filter_columns = st.columns(3, gap="medium")
    active_filters: list[tuple[str, int, int]] = []
    for filter_number, filter_column in enumerate(filter_columns, start=1):
        with filter_column:
            selected_metric = st.selectbox(
                f"Filter {filter_number} metric",
                ["No filter", *metric_options],
                key=f"league_data_filter_metric_{filter_number}",
            )
            minimum, maximum = st.slider(
                f"Filter {filter_number} percentile range",
                min_value=0,
                max_value=100,
                value=(0, 100),
                disabled=selected_metric == "No filter",
                key=f"league_data_filter_range_{filter_number}",
            )
            if selected_metric != "No filter":
                active_filters.append((selected_metric, minimum, maximum))

    filtered_table = percentile_table
    for metric, minimum, maximum in active_filters:
        filtered_table = filtered_table[
            filtered_table[metric].between(minimum, maximum, inclusive="both").fillna(False)
        ]

    st.caption(f"Showing {len(filtered_table)} of {len(percentile_table)} goalkeepers.")
    pinned_columns = {
        column: st.column_config.TextColumn(column, pinned=True)
        for column in ("Player", TEAM_COLUMN, "Age")
    }
    metric_columns = {
        metric: st.column_config.NumberColumn(metric, min_value=0, max_value=100, format="%d")
        for metric in GK_METRICS + POSSESSION_METRICS
    }
    st.dataframe(
        filtered_table,
        hide_index=True,
        use_container_width=True,
        height=700,
        column_config={**pinned_columns, **metric_columns},
    )
