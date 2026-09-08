# TrialFlow &mdash; Product Case Study

*A two-page product case study. All data is synthetic.*

---

## Page 1 &mdash; The problem and the solution

### Problem

A sponsor running a Phase II trial monitors execution across a CTMS, an EDC, and separate trackers for deviations, adverse events, data queries and recruitment. The signal that a site is failing is spread across all of them. By the time it is obvious in any one system, weeks of timeline are already gone, and the weekly site review is someone manually scanning tables trying to work out where to focus.

Three people carry the consequences:

- the **Clinical Operations Lead**, who has to state a defensible trial status in governance and decide which sites to intervene on this week;
- the **Clinical Data Manager**, who has to keep the query backlog from putting database lock at risk;
- the **Medical Monitor**, who needs to see that safety data is flowing and being followed up.

### Solution

TrialFlow consolidates the operational and clinical data for one trial into a single trial-health platform, and every view ends in a decision rather than a chart.

- A **Trial Health Score** (0&ndash;100) built from five weighted drivers: recruitment, data completeness, query backlog, site performance, protocol deviations.
- A **site risk model** that turns recruitment gap, query rate, deviation rate and data incompleteness into one 0&ndash;100 score per site, with the drivers and a recommended action.
- A **data-quality engine**: five deterministic checks over the raw EDC tables, each finding tied to a subject, a location and a severity, rolled into a **Data Quality Score**.
- A **Protocol Deviation Engine** that detects out-of-window visits from the schedule and trends deviations by site.
- A **simplified CDISC SDTM mapping** (DM, AE, VS, SV) and the full EDC &rarr; data-quality &rarr; SDTM &rarr; warehouse &rarr; analytics &rarr; dashboard &rarr; action pipeline.
- A **Risk Copilot** that answers execution questions deterministically from the computed metrics, with no LLM and no medical judgement.

### Scope discipline

The MVP is four features (overview, site risk, patient journey, data-quality engine): the smallest set where the operations lead and the data manager can each make their main weekly decision from the product alone. Multi-study view, EDC query write-back, site-facing login and any LLM-generated narrative were cut from the MVP on purpose, with a documented reason and a point at which each returns.

---

## Page 2 &mdash; Product decisions

### From problem to KPI

| Problem | Requirement | User story | Acceptance criterion | Feature | KPI it moves |
|---|---|---|---|---|---|
| Underperforming sites found too late | Flag sites below target with the reason | US-001, US-005 | Site &lt;70% of target is flagged with a named driver and a recommended action | Site risk score + detail panel | Days from a site crossing a threshold to it being flagged |
| Query backlog threatens database lock | Detect missing and inconsistent data automatically | US-002 | Five checks each produce a located, severity-tagged finding that rolls into the DQ score | Data-quality engine | Median open-query age; share older than 45 days |
| Protocol drift invisible until audit | Detect out-of-window visits from the schedule | US-003 | Every visit dated outside its window becomes a deviation, trended by site | Protocol Deviation Engine | Out-of-window visit rate per site after intervention |
| No single defensible trial status | One score from weighted, banded drivers | US-004 | 0&ndash;100 score, five components each with a RAG band, reproducible | Trial Health Score | Governance review preparation time |
| Weekly review is manual scanning | Answer "which sites need intervention and why" | US-009 | Deterministic answer generated only from computed metrics | Risk Copilot | Weekly review preparation time |

### A worked example

Site 102 (Germany) recruits at 32% of target, carries an above-average open-query rate and four protocol deviations, and sits at 92.8% data completeness. Individually none of these would trigger a call. Combined, the site risk model scores it in the red band, the detail panel lists the three drivers that crossed threshold, and the recommended action is a site performance review with the open queries prioritised. The Risk Copilot surfaces the same site first when asked which sites need intervention this week. The operations lead walks into the review already knowing where to start.

### What this demonstrates

- **Owning a product, not building a dashboard:** vision, personas, roadmap, PRD, user stories with acceptance criteria and a prioritised sprint backlog, all in the repository.
- **Working in a regulated shape:** synthetic data only, every figure traceable to its source, a reproducible build, and a hard line kept between operational oversight and medical judgement.
- **Prioritisation with a rationale:** a scored backlog, an MVP defined by the users' weekly decisions, and documented cuts.

### Honest limitations

This is a demonstration on synthetic data. The SDTM mapping covers four domains and is not validated. The risk weights are fixed, not calibrated against real outcomes. Predictive recruitment and automated alerts are on the roadmap, not built. The value of the risk model would need to be tested against real trial history before anyone relied on it.
