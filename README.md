<div align="center">
  <img src="assets/logo.png" width="72" alt="ShareChat logo"/>

  <h1>ShareChat Analytics Intelligence Platform</h1>

  <p><strong>An end-to-end product analytics system for a regional-language social platform — built to demonstrate the SQL depth, metric design, and analytical storytelling expected of a Product Analyst.</strong></p>

  <p>
    <img src="https://img.shields.io/badge/SQL-Redshift--compatible-blue" alt="SQL"/>
    <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python"/>
    <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white" alt="React"/>
    <img src="https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white" alt="FastAPI"/>
    <img src="https://img.shields.io/badge/Rows-2.97M-success" alt="Rows"/>
    <img src="https://img.shields.io/badge/SQL%20Queries-15-orange" alt="Queries"/>
  </p>
</div>

---

## Why This Project

Most "product analyst" portfolios are a Kaggle dataset, three charts in a notebook, and a short writeup. That doesn't mirror the actual job.

This project does. It generates a 3M-row synthetic event warehouse modeled on a real social platform's data shape, lands it in a star schema, runs 15 Redshift-compatible SQL queries against it, evaluates an A/B test with proper statistical rigor, and surfaces the findings through a production-grade React dashboard with a FastAPI backend.

> **Scoping note.** This is deliberately a **product analytics** project, not a data science one. No ML models, no predictions. The questions a PM actually needs answered — *who's churning, where's the funnel drop-off, does this feature work* — are better answered with well-written SQL and clear metric definitions than with a black-box model.

---

## Headline Findings

Every number below comes from running the actual SQL queries against the generated warehouse — they're reproducible end-to-end.

| # | Finding | Evidence |
|---|---------|----------|
| 1 | **Tier-3/4 users out-engage Tier-1 on time spent** | 26.1 min avg session vs 21.6 min for Tier-1 → **+20%** |
| 2 | **But monetisation is 5× behind** | Tier-1 ARPU ₹13.92 vs Tier-3 ARPU ₹2.66 → **5.2× gap** |
| 3 | **Android-Low has a crash-proxy problem** | 7.92% of sessions terminate < 10s vs ~0% on every other tier |
| 4 | **A/B variant ships** | +6.2% session duration, p < 0.001, holds across all major segments |
| 5 | **Ad CTR collapses down the tiers** | Tier-1 4.91% → Tier-2 3.51% → Tier-3 2.13% → Tier-4 1.80% |

The full reasoning, segment breakdowns, and recommended product actions live in [`reports/product_memo.md`](reports/product_memo.md).

---

## Architecture

```
pipeline/                         # Data generation & warehouse build
  01_generate_data.py    ──►  data/raw/*.csv          (2.97M rows, ~20s)
  02_simulate_api_fetch.py ──► paginated fetch, retry, dedupe
  03_build_warehouse.py  ──►  data/warehouse/sharechat.db   (star schema)
  04_data_quality_checks.py ──► 8 DQ categories, written report

sql/                              # 15 Redshift-compatible analytical queries
notebooks/                        # EDA, A/B deep-dive, creator ecosystem

backend/                          # FastAPI — serves the warehouse over REST
  app/api/routes/                 # overview, users, content, monetisation,
                                  # language, retention, ab_test, query
  app/core/cache.py               # permanent process-level cache (no TTL)
  app/core/database.py            # SQLite + WAL + 256MB mmap pragmas

frontend/                         # React 18 + Vite + TypeScript + Tailwind
  src/pages/                      # 8 dashboard pages
  src/components/                 # KPICard, charts, layout, UI primitives
  src/services/api.ts             # typed fetch layer
  src/hooks/useAPI.ts             # loading/error state hook
```

**Star schema.** Fact tables (`fact_events`, `fact_sessions`, `fact_ad_impressions`) join to dimensions (`dim_users`, `dim_creators`, `dim_posts`). Every SQL query in `/sql` runs unchanged on Redshift; SQLite is used for portability.

---

## Run It

### Prerequisites

- Python 3.10+
- Node.js 18+

### 1 — Build the warehouse

```bash
cd pipeline
pip install -r requirements.txt

python 01_generate_data.py        # ~20s  → data/raw/
python 02_simulate_api_fetch.py   # ~70s  → paginate, dedupe, refresh
python 03_build_warehouse.py      # ~35s  → data/warehouse/sharechat.db
python 04_data_quality_checks.py  # ~10s  → DQ report
```

### 2 — Start the backend

```bash
start_backend.bat
# or manually: cd backend && uvicorn app.main:app --reload
# API available at http://localhost:8000
```

### 3 — Start the frontend

```bash
start_frontend.bat
# or manually: cd frontend && npm install && npm run dev
# Dashboard at http://localhost:5173
```

### Optional — Notebooks

```bash
cd pipeline
jupyter lab ../notebooks/
```

---

## Project Structure

```
sharechat-analytics/
├── assets/                       # Logo and brand assets
├── backend/                      # FastAPI application
│   ├── app/
│   │   ├── api/routes/           # REST endpoints (8 modules)
│   │   ├── core/
│   │   │   ├── cache.py          # Permanent in-process cache
│   │   │   └── database.py       # SQLite connection + pragmas
│   │   └── main.py
│   └── requirements.txt
├── data/
│   ├── raw/                      # Generated CSVs (gitignored)
│   └── warehouse/                # SQLite DB (gitignored)
├── docs/                         # Schema, data dictionary, interview prep
├── frontend/                     # React + Vite + TypeScript dashboard
│   ├── public/logo.png
│   ├── src/
│   │   ├── components/           # KPICard, Sidebar, LoadingState, UI
│   │   ├── hooks/useAPI.ts
│   │   ├── pages/                # Overview, UserAnalytics, Content,
│   │   │                         # Monetisation, Retention, Language,
│   │   │                         # ABTest, SQLWorkbench
│   │   └── services/api.ts
│   ├── index.html
│   └── package.json
├── notebooks/                    # EDA, A/B deep-dive, creator ecosystem
├── pipeline/                     # Data generation scripts
│   ├── 01_generate_data.py
│   ├── 02_simulate_api_fetch.py
│   ├── 03_build_warehouse.py
│   ├── 04_data_quality_checks.py
│   └── requirements.txt
├── reports/                      # Product memo, metrics definitions
├── sql/                          # 15 analytical queries + README
├── start_backend.bat
├── start_frontend.bat
└── README.md
```

---

## What's Inside

### Pipeline (`pipeline/`)

| Script | Purpose |
|--------|---------|
| `01_generate_data.py` | Vectorised generation of 2.97M rows across 7 tables — 50K users, 5K creators, 100K posts, 2M events, 500K sessions, 300K ad impressions. |
| `02_simulate_api_fetch.py` | Simulates paginated API fetch with retry/backoff/deduplication. |
| `03_build_warehouse.py` | Loads CSVs into a SQLite star schema with 18 indexes; Redshift equivalents documented inline. |
| `04_data_quality_checks.py` | 8-category DQ suite: nulls, referential integrity, date validity, duplicates, enum validation, distribution sanity. |

### SQL (`sql/`)

15 Redshift-compatible queries, each paired with a business question and PM action in `sql/README.md`:

```
01_engagement_metrics.sql        09_power_users.sql
02_retention_cohorts.sql         10_creator_retention.sql
03_content_performance.sql       11_language_cross_analysis.sql
04_creator_analytics.sql         12_session_patterns.sql
05_funnel_analysis.sql           13_festival_impact.sql
06_ab_test_analysis.sql          14_device_segmentation.sql
07_monetization_analysis.sql     15_cohort_ltv.sql
08_anomaly_detection.sql
```

### Notebooks (`notebooks/`)

| Notebook | Coverage |
|----------|---------|
| `01_exploratory_analysis.ipynb` | User distributions, session shape, festival effect |
| `02_ab_test_deep_dive.ipynb` | Power check → t-test → CI → segment cuts → ship recommendation |
| `03_creator_ecosystem.ipynb` | Power-law fit, Lorenz curve & Gini, streak analysis |

### Dashboard Pages

`Overview` · `User Analytics` · `Content Performance` · `Monetisation` · `Retention` · `Language Analysis` · `A/B Test` · `SQL Workbench`

The SQL Workbench page lets a reviewer run any of the 15 queries live against the warehouse.

---

## Tech Stack

| Layer | Choice |
|-------|--------|
| Data generation | Python + NumPy (vectorised) — ~20s for 3M rows |
| Warehouse | SQLite with WAL mode, 256MB mmap, permanent in-process cache |
| SQL | 15 queries — window functions, CTEs, statistical computation |
| Backend | FastAPI + uvicorn |
| Frontend | React 18 + Vite + TypeScript + Tailwind CSS + Recharts |
| Notebooks | pandas, matplotlib, seaborn, scipy |
| Statistics | `scipy.stats` (t-test, chi-square, power analysis) |

---

## How This Maps to the JD

| JD requirement | Where it shows up |
|----------------|-------------------|
| SQL on a Redshift analytical engine | `sql/01–15_*.sql` — all Redshift-compatible |
| Scripting to fetch from API endpoints | `pipeline/02_simulate_api_fetch.py` |
| Working with large user-behaviour data | 2M+ event rows across a star schema |
| Trend & pattern recognition | `sql/08_anomaly_detection.sql`, `sql/13_festival_impact.sql` |
| Segmentation | City tier, language, device class, RFM-style creator tiers |
| Statistics | `notebooks/02_ab_test_deep_dive.ipynb` |
| Reporting & presenting findings | `reports/product_memo.md`, dashboard, `docs/DASHBOARD_GUIDE.md` |

---

## Author

Built as a portfolio project for the **ShareChat Product Analyst Internship**.
All data is synthetic; behavioural signals are modelled on publicly documented platform dynamics.

[LinkedIn](https://www.linkedin.com/in/alokthedataguy/) · [Email](mailto:iamadsmart@gmail.com)
