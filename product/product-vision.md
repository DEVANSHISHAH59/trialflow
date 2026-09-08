# Product Vision

## Vision statement

**TrialFlow enables clinical operations and data-management teams to see trial execution and data-quality risks early, in one place, and prioritise the corrective actions that protect the timeline and the data.**

## The problem

Running a clinical trial means watching several systems at once: a CTMS for sites and milestones, an EDC for patient data, separate trackers for protocol deviations, adverse events and data queries, and a recruitment plan in a spreadsheet. The signal that a site is in trouble is usually spread across all of them. By the time it is obvious in one system, the trial has already lost weeks.

The people accountable for the trial (the sponsor, the clinical operations lead, the data manager) do not need another report. They need a single view that says what is at risk now and what to do about it.

## The product

TrialFlow consolidates operational and clinical data into a unified trial-health platform:

- A **Trial Health Score** and its drivers, so the status of the whole trial is legible at a glance.
- A **site risk model** that combines recruitment, data quality, query load and protocol deviations into one score, with the drivers and a recommended action for every site.
- An **EDC data-quality engine** that runs deterministic checks and turns each finding into a query with an owner.
- A **simplified CDISC SDTM mapping** so the data can be read in a standard structure for analysis.
- A **Risk Copilot** that answers execution questions from the computed metrics, without an LLM and without touching medical judgement.

## What TrialFlow is not

- Not an EDC or a CTMS of record. It reads operational data; it is not the system of record.
- Not a validated SDTM implementation. The mapping is a demonstration of the structure and the workflow.
- Not a clinical or safety decision tool. It summarises recorded data and predefined rules. It does not diagnose patients, assess causality or recommend treatment.

## Success measures

| Outcome | Measure |
|---|---|
| Risks surfaced earlier | Median days between a site crossing a risk threshold and it being flagged |
| Faster query resolution | Median age of open queries; share of queries older than 45 days |
| Fewer avoidable deviations | Out-of-window visit rate, trended by site after intervention |
| Adoption | Weekly active operations and data-management users; share of site reviews that cite the risk score |

## Guiding principles

1. **Every number is traceable.** A score always decomposes into the data points behind it.
2. **Decisions, not dashboards.** Each view ends in a recommended action or a queue of work.
3. **Deterministic first.** Rules and analytics are reproducible from a fixed input before any model is added.
4. **Stay out of the clinic.** Operational oversight only; medical and safety assessment stays with the qualified people who own it.
