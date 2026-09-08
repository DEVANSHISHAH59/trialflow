# Sprint Backlog

Two-week sprints, one Product Owner, notional team of two engineers. Status reflects this repository: Sprints 1&ndash;3 are built, Sprint 4 is planned.

| ID | Story / task | Stories | Priority | Sprint | Status |
|---|---|---|---|---|---|
| TF-001 | Executive overview + Trial Health Score | US-004 | P0 | 1 | Done |
| TF-002 | Site performance league table | US-001, US-005 | P0 | 1 | Done |
| TF-003 | Patient journey / EDC completeness view | US-006 | P0 | 1 | Done |
| TF-014 | Synthetic Phase II dataset generator | US-010 | P0 | 1 | Done |
| TF-004 | Data-quality engine + Data Quality Score | US-002 | P0 | 2 | Done |
| TF-015 | SQLite warehouse + SQL views | US-010 | P0 | 2 | Done |
| TF-016 | Site risk model (4 components, bands, actions) | US-005 | P0 | 2 | Done |
| TF-005 | Protocol Deviation Engine | US-003 | P1 | 2 | Done |
| TF-006 | Adverse Event dashboard | US-007 | P1 | 3 | Done |
| TF-007 | Simplified SDTM mapping (DM, AE, VS, SV) | US-008 | P1 | 3 | Done |
| TF-017 | EDC &rarr; SDTM &rarr; analytics pipeline view | US-008 | P1 | 3 | Done |
| TF-018 | Risk Copilot (deterministic, 4 intents) | US-009 | P1 | 3 | Done |
| TF-019 | Deploy to static hosting; synthetic-data notices | US-010 | P0 | 3 | Done |
| TF-008 | Risk scoring v2: configurable weights and bands | US-004, US-005 | P2 | 4 | Planned |
| TF-010 | Automated threshold alerts with drivers attached | US-001, US-005 | P2 | 4 | Planned |
| TF-020 | Data-quality trend over time and query-ageing view | US-002 | P1 | 4 | Planned |
| TF-011 | Intervention log + trend after action | US-005 | P2 | 5 | Backlog |
| TF-009 | Predictive recruitment per site and trial | US-001 | P2 | 5 | Backlog |
| TF-021 | Screen-reader pass and axe-core audit | US-010 | P1 | 5 | Backlog |

## Sprint goals

- **Sprint 1 &mdash; "See the trial":** a user can open the app and read trial status, site standings and one subject's data position.
- **Sprint 2 &mdash; "Trust the data":** the data-quality and site-risk numbers are computed by an engine over a warehouse, not hand-set.
- **Sprint 3 &mdash; "Explain it in a meeting":** deviations, AEs and a standard data shape are all in the product; it is deployed.
- **Sprint 4 &mdash; "Act earlier":** the weekly review starts from an alert queue, and risk weights can be tuned per study.

## Working agreements

- No story is Done until its acceptance criteria pass and the build is still reproducible.
- Every sprint ends with the demo script in `docs/demo-script.md` updated and run start to finish.
- Scope is cut before quality: a thinner slice that ends in an action beats a wider slice that just reports.
