# TrialFlow

**Clinical Trial Product & Data Operations Platform**

TrialFlow is a demonstration product that combines the operational view of a **CTMS**, an **EDC data-quality layer** and a **clinical-trial analytics platform** into one place, so a sponsor or clinical operations lead can answer a single question: **is this trial healthy?**

It is built and documented as a product, not a dashboard. The repository holds the product vision, personas, roadmap, user stories with acceptance criteria and a prioritised sprint backlog alongside a working Python data engine and a deployed web app.

> **All data is synthetic.** No real patients, sites, investigators or study drugs are represented. The CDISC SDTM mapping is a simplified demonstration model, not a validated implementation. Nothing here is medical, safety or regulatory advice.

**Live app:** https://trialflow.vercel.app
**Product docs:** [`/product`](product/) &nbsp;|&nbsp; **Case study:** [`docs/CASE-STUDY.md`](docs/CASE-STUDY.md)

---

## What it does

A simulated Phase II trial (`TF-201`, ~740 subjects across 38 activated sites in 8 countries). The platform monitors the chain **patients → sites → visits → EDC data → adverse events → protocol deviations → data queries → recruitment → milestones** and turns it into product decisions.

| Section | What it shows |
|---|---|
| **Executive Overview** | Trial Health Score (0&ndash;100) with its five drivers, eight headline KPIs, recruitment vs plan, enrolment by country |
| **Site Performance** | CTMS-style league table with a 0&ndash;100 **site risk score**; click a site for the risk drivers and the recommended action |
| **Patient Journey (EDC)** | A simulated EDC completeness layer for one subject: expected vs captured visits, missing assessments, open data items |
| **Data Quality** | Five deterministic checks (missing data, impossible dates, out-of-range values, duplicates, cross-form inconsistency) with a **Data Quality Score** |
| **Protocol Deviations** | Out-of-window visits detected from the schedule, plus a categorised deviation log trended by site |
| **Adverse Events** | AEs by severity, system organ class and treatment arm, with the serious events listed |
| **SDTM Mapping** | Raw EDC mapped to SDTM-style **DM, AE, VS, SV** domains; the EDC &rarr; SDTM &rarr; analytics pipeline; the SQL views in the warehouse |
| **Risk Copilot** | Ask a question about trial execution; answers are generated deterministically from the computed metrics. No LLM. No medical advice. |

## Architecture

```
synthetic EDC tables  ->  SQLite warehouse  ->  SQL views
                      ->  data-quality engine + risk engine + SDTM mapping
                      ->  web/data/trialflow.json  ->  static web app (Vercel)
```

The Python engine in [`/engine`](engine/) is the source of every number on the site. The web app in [`/web`](web/) only presents `trialflow.json`; it has no build step and no server.

## Run it locally

```bash
pip install -r requirements.txt
python engine/build.py          # regenerates data, runs SQL, writes web/data/trialflow.json
cd web && python -m http.server 8000
# open http://localhost:8000
```

`engine/build.py` is deterministic (fixed seed), so the same command always produces the same trial.

## Repository layout

```
trialflow/
├── product/       product vision, personas, roadmap, PRD, user stories,
│                  acceptance criteria, prioritisation, sprint backlog
├── engine/        Python: generate_data, data_quality, risk_engine,
│                  sdtm_mapping, analytics, build (pipeline)
├── sql/           trial_metrics.sql, site_performance.sql, data_quality.sql
├── sdtm/          generated SDTM-style domains (DM, AE, VS, SV)
├── warehouse/     generated SQLite database
├── data/raw/      generated raw EDC tables
├── web/           static single-page app (index.html, styles.css, app.js, data/)
└── docs/          case study, data dictionary, demo script, architecture
```

## Tech

Python (pandas, numpy, sqlite3), SQL, vanilla JavaScript, Plotly.js, Vercel static hosting. Built with Claude Code agentic workflows.
