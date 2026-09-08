# Acceptance Criteria and Traceability

## Definition of Done (every story)

- [ ] Acceptance criteria in the story pass against the generated dataset.
- [ ] The figure or behaviour is reproducible: `python engine/build.py` twice gives the same result.
- [ ] Every displayed number decomposes to visible components, counts or findings.
- [ ] Synthetic-data notice present on any view showing subject, site or AE data.
- [ ] No medical, safety or causality judgement is made or implied.
- [ ] Works with keyboard navigation; risk/severity never signalled by colour alone.
- [ ] Engine change covered by a spot-check in `docs/demo-script.md`.

## Traceability matrix

Problem &rarr; Requirement &rarr; Story &rarr; Acceptance &rarr; Feature &rarr; KPI it moves.

| Problem | Req | Story | Key acceptance | Feature | KPI |
|---|---|---|---|---|---|
| Underperforming sites found too late | 3.2, 3.4 | US-001, US-005 | Site &lt;70% target flagged with driver + action | Site risk score + detail panel | Days from threshold breach to flag |
| Query backlog threatens database lock | 5.1&ndash;5.4 | US-002 | Five checks produce located, severity-tagged findings | Data-quality engine + score | Open-query age; % &gt;45 days |
| Protocol compliance drift invisible until audit | 6.1&ndash;6.3 | US-003 | Out-of-window visits auto-detected, trended by site | Protocol Deviation Engine | Out-of-window visit rate per site |
| No single defensible trial status | 1.1&ndash;1.4, 2.1 | US-004 | 0&ndash;100 score from 5 weighted, banded drivers | Trial Health Score | Governance review prep time |
| Picture of a site is spread across systems | 3.1, 3.3, 3.5 | US-005 | One row per site; click for drivers + action | Site league table | % site reviews citing the score |
| Visits monitored without knowing what is open | 4.1&ndash;4.4 | US-006 | Per-visit capture + missing forms + completeness | Patient Journey (EDC) | Data completeness at monitoring visit |
| Hard to see safety data is flowing | 7.1&ndash;7.3 | US-007 | AE by severity/SOC/arm + serious list + notice | Adverse Event dashboard | Serious AE follow-up completeness |
| Data not in a standard shape for analysis | 8.1&ndash;8.3 | US-008 | DM/AE/VS/SV with SDTMIG names, labelled demo | Simplified SDTM mapping | Time to first analysis-ready extract |
| Weekly review is manual scanning | 9.1&ndash;9.3 | US-009 | Deterministic answers from computed metrics | Risk Copilot | Weekly review prep time |
| Numbers not trusted in regulated setting | 10.1&ndash;10.6 | US-010 | Every figure traceable; reproducible build | Cross-cutting | Adoption; challenge rate in reviews |

## Non-functional acceptance

| Area | Criterion |
|---|---|
| Reproducibility | Fixed seed; identical `trialflow.json` across runs on the same code |
| Performance | Full build completes in under 15 seconds on a laptop; app first paint under 2 seconds |
| Portability | UI is static; opens from `python -m http.server` or any static host with no config |
| Data safety | No real identifiers anywhere in the repo, data files or UI |
| Clarity of scope | "Simplified demonstration model" on SDTM; "not a safety assessment" on AE; "no LLM, no medical advice" on Copilot |
