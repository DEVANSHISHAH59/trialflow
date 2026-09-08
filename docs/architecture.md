# Architecture

## Overview

```
 engine/generate_data.py        raw EDC tables (data/raw/*.csv)
            |
            v
 engine/build.py  ------------>  warehouse/trialflow.db  (SQLite)
            |                          |
            |                          v
            |                   sql/*.sql  ->  docs/sql-output/*.csv
            |
            +--> engine/data_quality.py    findings + Data Quality Score
            +--> engine/risk_engine.py     site risk table + Trial Health Score
            +--> engine/sdtm_mapping.py    sdtm/DM|AE|VS|SV.csv
            +--> engine/analytics.py       KPI rollups, chart series, copilot answers
            |
            v
 web/data/trialflow.json  ---->  web/ (index.html + styles.css + app.js)  ---->  Vercel (static)
```

## Principles

1. **One source of truth for numbers.** The Python engine computes everything. `trialflow.json` is a build artefact. The web app performs no calculations beyond formatting.
2. **Deterministic build.** `SEED` in `engine/config.py` fixes the dataset. The same commit always produces the same `trialflow.json`.
3. **No runtime backend.** The UI is static files plus one JSON document. It hosts anywhere and has nothing to operate.
4. **Separable engines.** Data generation, quality checks, risk scoring and SDTM mapping are independent modules the orchestrator calls in sequence.

## Components

| Component | Responsibility | Key files |
|---|---|---|
| Data generator | Synthetic Phase II EDC tables with seeded quality problems | `engine/generate_data.py`, `engine/config.py` |
| Warehouse loader | Load raw tables into SQLite; run SQL views | `engine/build.py`, `sql/*.sql` |
| Data-quality engine | Five deterministic checks; findings and score | `engine/data_quality.py` |
| Risk engine | Site risk components and score; trial-health composite | `engine/risk_engine.py` |
| SDTM mapping | Raw tables to DM/AE/VS/SV with SDTMIG names | `engine/sdtm_mapping.py` |
| Analytics | KPI rollups, chart series, patient journey, copilot answers | `engine/analytics.py` |
| Web app | Render `trialflow.json` across eight views | `web/index.html`, `web/app.js`, `web/styles.css` |

## Risk model

**Site risk score** (0&ndash;100, higher is worse) = weighted sum of four components, each normalised to [0, 1]:

| Component | Definition | Weight |
|---|---|---|
| Recruitment gap | how far enrolment is below 85% of target | 0.30 |
| Open-query rate | open queries per enrolled subject | 0.25 |
| Deviation rate | protocol deviations per enrolled subject | 0.25 |
| Data incompleteness | 1 &minus; form completeness | 0.20 |

Bands: green &lt; 30, amber 30&ndash;56, red &ge; 56.

**Trial Health Score** (0&ndash;100, higher is better) = weighted sum of recruitment (0.25), data completeness (0.25), query backlog (0.15), site performance (0.20) and protocol deviations (0.15), each expressed as a 0&ndash;100 sub-score. Status: On Track &ge; 80, Needs Attention 65&ndash;79, At Risk &lt; 65.

Weights and bands are in `engine/config.py`. Making them configurable per study is backlog item TF-008.

## Deployment

The `web/` directory is served as static output. `vercel.json` sets `outputDirectory` to `web` with no build step. Any static host works the same way.

## Not in scope

No authentication, no database server, no external API calls at runtime, no PHI. The web app does not call back to the engine; regenerating data is a build-time action.
