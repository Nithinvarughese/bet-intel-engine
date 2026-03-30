# Pitch Metrics

A small **football analytics demo** that estimates **1X2 probabilities** (home win / draw / away win) from historical results using a **Poisson scoreline model**, with a **Streamlit** dashboard and **PostgreSQL** storage.

> **Disclaimer:** Educational and portfolio use only. This is not betting advice, and the model is intentionally simple (e.g. scorelines capped at 0–5 goals per side).

---

## Features

- **Match simulator** — Pick home and away teams; see implied probabilities and a stacked outcome bar.
- **League efficiency chart** — Interactive Plotly scatter: attack vs defense indices vs league average (100).
- **Data pipeline** — Optional ingest from [API-Football](https://www.api-football.com/) (Premier League–style fixtures; default league id `39`, season `2023`).
- **Dark UI** — Streamlit layout with sidebar controls, tabs (Overview, Simulation, League chart, Methodology), and theme via `.streamlit/config.toml`.

---

## Tech stack

| Layer | Choice |
|--------|--------|
| UI | [Streamlit](https://streamlit.io/) |
| Charts | [Plotly](https://plotly.com/python/) |
| Data | [pandas](https://pandas.pydata.org/) |
| Model | [SciPy](https://scipy.org/) `poisson` |
| Database | [PostgreSQL 15](https://www.postgresql.org/) (Docker) |
| ORM | [SQLAlchemy](https://www.sqlalchemy.org/) 2.x |
| Config | [python-dotenv](https://github.com/theskumar/python-dotenv) (`.env`) |

---

## Repository layout

```
bet-intel-engine/
├── app.py              # Streamlit entrypoint
├── analytics.py        # League aggregates + Poisson 1X2 logic
├── database.py         # Engine, session, table creation on import
├── models.py           # SQLAlchemy `matches` model
├── schemas.py          # Pydantic validation for ingest
├── ingest.py           # Fetch fixtures from API-Football → DB
├── docker-compose.yml  # Local Postgres
├── .streamlit/
│   └── config.toml     # Theme
├── .env.example        # Copy to `.env` (not committed)
└── requirements.txt
```

---

## Prerequisites

- **Python 3.11+** (3.12/3.14 work if dependencies install cleanly)
- **Docker Desktop** (or Docker Engine) for Postgres, *or* your own PostgreSQL instance
- **Git**

Optional:

- **API-Football** key ([RapidAPI / API-Sports](https://rapidapi.com/api-sports/api/api-football)) for `ingest.py`

---

## Quick start

### 1. Clone and virtual environment

```bash
git clone https://github.com/Nithinvarughese/bet-intel-engine.git
cd bet-intel-engine
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start PostgreSQL

```bash
docker compose up -d
```

Postgres listens on **localhost:5432**. Data is stored in `./postgres_data` (ignored by Git).

### 3. Environment variables

```bash
cp .env.example .env
```

Edit `.env` and set **`DATABASE_URL`** so it matches your database user, password, host, port, and database name. If you use the bundled `docker-compose.yml` without changes, align `DATABASE_URL` with the `POSTGRES_*` values defined there.

For ingestion and API tests, set **`FOOTBALL_API_KEY`** in `.env`.

### 4. Create tables

Running the database module initializes the schema (and prints a short confirmation):

```bash
python database.py
```

### 5. (Optional) Load match data

```bash
python ingest.py
```

Requires a valid `FOOTBALL_API_KEY`. The app expects rows in `matches` with **`status = 'FT'`** for finished games so averages and predictions can be computed.

### 6. Run the app

```bash
streamlit run app.py
```

Open the URL shown in the terminal (typically `http://localhost:8501`).

---

## How the model works (short)

1. From finished matches, compute league-average home and away goals.
2. Derive **attack / defense strength** multipliers per team (relative to those averages) for home and away performances.
3. For a selected fixture, build **expected goals** for each side from the relevant strengths.
4. Assume **independent Poisson** goals up to **5** each; sum scoreline probabilities into home win, draw, and away win.

Details and limitations are summarized in the app under **Methodology**.

---

## Configuration reference

| Variable | Required | Purpose |
|----------|----------|---------|
| `DATABASE_URL` | Yes | SQLAlchemy URL, e.g. `postgresql://USER:PASSWORD@localhost:5432/football_analytics` |
| `FOOTBALL_API_KEY` | No | API-Football key for `ingest.py` / `test_api.py` |

---

## Deploying (e.g. Streamlit Community Cloud)

1. Push this repo to GitHub.
2. Connect the repo in [Streamlit Cloud](https://streamlit.io/cloud) with **Main file** `app.py`.
3. Add **`DATABASE_URL`** (and any other secrets) in the app’s **Secrets** UI so the hosted app can reach a **publicly reachable** Postgres instance (managed DB or tunnel). Local `localhost` URLs will not work from the cloud.

---

## Portfolio tips

- Add a **screenshot** or **GIF** of the Simulation and League chart tabs (e.g. `docs/screenshot.png` in the repo).
- Link a **live demo** once the app is deployed (Streamlit Cloud or similar).

---

## License

No license file is included by default. Add one (e.g. MIT) if you want to clarify reuse terms.
