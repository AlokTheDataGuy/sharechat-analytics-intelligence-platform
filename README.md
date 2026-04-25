# ShareChat Creator & Content Engagement Analytics

**Product Analyst Portfolio Project**

A complete, end-to-end product analytics system built to demonstrate the skills required for the Product Analyst Intern role — SQL depth, metric design, cohort thinking, A/B test evaluation, and analytical storytelling.

> **Scoping note:** This is a deliberate **product analytics** project, not a data science project. No ML models. The questions a PM needs answered — who's churning, where's the funnel drop-off, does this feature work — are better answered by well-written SQL and clear metric definitions than by a black-box model. That scoping decision is itself a talking point.

---

## What's Built

| Component | Description |
|-----------|-------------|
| `src/01_generate_data.py` | Generates 2.97M rows across 7 tables (50K users, 5K creators, 100K posts, 2M events, 500K sessions, 300K ad impressions) with realistic behavioral signals |
| `src/02_simulate_api_fetch.py` | Simulates paginated API fetch with retry/backoff/dedup — directly demonstrates the JD's "scripting to fetch from endpoints" requirement |
| `src/03_build_warehouse.py` | Loads all CSVs into a SQLite star schema with 18 indexes; documented Redshift equivalents (DISTKEY, SORTKEY, DISTSTYLE ALL) |
| `src/04_data_quality_checks.py` | 8-category DQ checks: row counts, nulls, referential integrity, date validity, duplicates, TEST_ users, enum validation, distributions |
| `sql/01–15_*.sql` | 15 Redshift-compatible SQL queries; all execute against the SQLite warehouse |
| `sql/README.md` | Business question, interpretation, and PM action for each query |
| `notebooks/01_exploratory_analysis.ipynb` | EDA: user distributions, session behaviour, festival effects, A/B preview |
| `notebooks/02_ab_test_deep_dive.ipynb` | Full statistical A/B test writeup: power check, t-test, CI, segment cuts, Simpson's paradox check, recommendation |
| `notebooks/03_creator_ecosystem.ipynb` | Creator power-law, Lorenz curve, streak analysis, category health |
| `dashboard/app.py` | Streamlit dashboard — 8 pages: Overview, User Analytics, Content, Monetisation, Retention, Language, A/B Test, SQL Workbench |
| `reports/product_memo.md` | PM-style memo with real numbers: Tier-3/4 monetisation gap, Android-Low crash rates, A/B test recommendation |
| `reports/metrics_definitions.md` | Precise definitions (formula + SQL + pitfalls) for every metric |
| `docs/PROJECT_REPORT.md` | 2,500-word technical writeup |
| `docs/DATA_DICTIONARY.md` | Every field in every table |
| `docs/SCHEMA_DIAGRAM.md` | Star schema diagram (ASCII + Mermaid) with design rationale |
| `docs/DASHBOARD_GUIDE.md` | 5-minute interview demo script |
| `docs/INTERVIEW_PREP.md` | STAR answers, SQL prep, ShareChat context, numbers to memorise |

---

## Key Findings (From Real Generated Data)

| Finding | Numbers |
|---------|---------|
| **Tier-3/4 session premium** | 26.1 min avg vs 21.6 min for Tier-1 (+20%) |
| **Tier-1 vs Tier-3 ARPU** | ₹13.92 vs ₹2.66 — 5.2× monetisation gap |
| **Android-Low crash proxy** | 7.92% of sessions < 10s vs 0% on all other tiers |
| **A/B test lift** | +6.2% session duration (p < 0.001), variant = 25.1 min, control = 23.6 min |
| **Ad CTR by tier** | Tier-1: 4.91%, Tier-2: 3.51%, Tier-3: 2.13%, Tier-4: 1.80% |

---

## Setup & Run

### Prerequisites
```bash
pip install -r requirements.txt
```

### Run the data pipeline
```bash
python src/01_generate_data.py       # ~20s — generates 2.97M rows to data/raw/
python src/02_simulate_api_fetch.py  # ~70s — paginates, deduplicates, refreshes events CSV
python src/03_build_warehouse.py     # ~35s — builds SQLite warehouse (547 MB)
python src/04_data_quality_checks.py # ~10s — validates and reports
```

### Launch the dashboard
```bash
streamlit run dashboard/app.py
```
Opens at `http://localhost:8501`

### Run the notebooks
```bash
jupyter lab notebooks/
```

---

## Project Structure

```
sharechat-analytics/
├── README.md
├── requirements.txt
├── .gitignore
├── app.py                    ← original standalone dashboard (root)
├── assets/
│   └── logo.png
├── data/
│   ├── raw/                  ← generated CSVs (gitignored)
│   └── warehouse/            ← SQLite DB + DQ report (gitignored)
├── src/
│   ├── 01_generate_data.py
│   ├── 02_simulate_api_fetch.py
│   ├── 03_build_warehouse.py
│   ├── 04_data_quality_checks.py
│   └── build_notebooks.py
├── sql/
│   ├── 01_engagement_metrics.sql
│   ├── 02_retention_cohorts.sql
│   ├── 03_content_performance.sql
│   ├── 04_creator_analytics.sql
│   ├── 05_funnel_analysis.sql
│   ├── 06_ab_test_analysis.sql
│   ├── 07_monetization_analysis.sql
│   ├── 08_anomaly_detection.sql
│   ├── 09_power_users.sql
│   ├── 10_creator_retention.sql
│   ├── 11_language_cross_analysis.sql
│   ├── 12_session_patterns.sql
│   ├── 13_festival_impact.sql
│   ├── 14_device_segmentation.sql
│   ├── 15_cohort_ltv.sql
│   └── README.md
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb
│   ├── 02_ab_test_deep_dive.ipynb
│   └── 03_creator_ecosystem.ipynb
├── dashboard/
│   └── app.py                ← 8-page dashboard connected to SQLite warehouse
├── reports/
│   ├── product_memo.md       ← keystone deliverable
│   └── metrics_definitions.md
└── docs/
    ├── PROJECT_REPORT.md
    ├── DATA_DICTIONARY.md
    ├── SCHEMA_DIAGRAM.md
    ├── DASHBOARD_GUIDE.md
    └── INTERVIEW_PREP.md
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Data generation | Python, NumPy (vectorised — no Faker for performance) |
| API simulation | Python, requests-style pattern |
| Warehouse | SQLite (Redshift-compatible SQL throughout) |
| SQL analysis | 15 queries — window functions, CTEs, statistical tests |
| Notebooks | Jupyter, pandas, matplotlib, seaborn, scipy |
| Dashboard | Streamlit, Plotly |
| Statistics | scipy.stats (t-test, chi-square, power analysis) |

---

## Author

Built as a portfolio project for the **ShareChat Product Analyst Internship** application.  
All data is synthetic. Behavioral signals modelled after publicly documented ShareChat platform dynamics.
