# Goalkeeper League Comparison

A Streamlit app for comparing goalkeeper performance across the Scottish Premiership and Scottish Championship (2025/26).

## Features

- Four linked selectors for two leagues and two goalkeepers.
- Raw GK and possession tables with inverted metrics marked in red and the better value highlighted.
- Derived `Lateral Pass Share %` and `Short/Medium Pass Share %` metrics, calculated to two decimal places when data loads.
- Two overlaid pizza charts showing league-relative percentile ranks for the selected players.
- Inverted percentile treatment for conceded goals per 90, shots against per 90, and average pass length.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a new GitHub repository.
2. Upload every file and folder from this directory, preserving the `data/` folder.
3. In Streamlit Community Cloud, create an app from the repository and set the entrypoint to `app.py`.

The included source spreadsheets are loaded from paths relative to `app.py`, so no local-machine paths or secrets are required.
