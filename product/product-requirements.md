# Product Requirements (MVP + Release 2)

Scope: single trial. Multi-study is out of scope. This document states what the product must do and the constraints it operates under; the how is in `/engine` and `/web`.

## 1. Trial health

1.1 The system computes a Trial Health Score from 0 to 100 from five weighted components: recruitment, data completeness, query backlog, site performance and protocol deviations.
1.2 Each component is shown with its own value and a red/amber/green band.
1.3 The overall score maps to a status: On Track (&ge;80), Needs Attention (65&ndash;79), At Risk (&lt;65).
1.4 The score is reproducible: the same input data always yields the same score.

## 2. Executive KPIs

2.1 The overview shows: patients enrolled vs target, recruitment rate, active vs planned sites, data completeness, open queries (with aged count), protocol deviations (with major count), AE reports (with serious count), sites at risk.
2.2 Recruitment is shown cumulatively against a plan line.
2.3 Enrolment is shown by country.

## 3. Site performance and risk

3.1 Every activated site appears in a league table with recruitment, data completeness, open queries and deviation count.
3.2 The system computes a site risk score from 0 to 100 (higher is worse) from four normalised components: recruitment gap, open-query rate, deviation rate and data incompleteness, with fixed weights.
3.3 Each site is banded green / amber (watch) / red (act).
3.4 Selecting a site shows the drivers that crossed threshold and a recommended action tied to the band.
3.5 The table is sortable by any column.

## 4. Patient journey (EDC data quality)

4.1 For a selected subject, the system shows every expected visit, its scheduled and actual date and its status (Done / Missed / Pending).
4.2 For each completed visit, the system lists required forms that are missing or incomplete.
4.3 The system shows a data-completeness percentage for the subject.
4.4 Open data items are listed and described in a way that can be sent to a site as a query.

## 5. Data-quality engine

5.1 The system runs at least these checks over the raw EDC tables:
  - missing required data (visit performed, required CRF not entered);
  - impossible date (e.g. result dated before screening);
  - out-of-range value (outside a predefined reference range);
  - duplicate record (same subject + visit + assessment + date);
  - cross-form inconsistency (e.g. sex vs pregnancy status).
5.2 Each finding names the rule, the subject, the site, the location and a severity.
5.3 The system computes a Data Quality Score as the share of evaluable data points with no finding.
5.4 Findings are summarised by rule and by site.

## 6. Protocol deviations (Release 2)

6.1 Visits dated outside the protocol window are detected automatically from the visit data.
6.2 Other deviation types are recorded with a category (Minor / Moderate / Major), a date, a status and a corrective action.
6.3 Deviations are summarised by category, by type and by site.

## 7. Adverse events (Release 2)

7.1 AEs are summarised by severity, by system organ class and by treatment arm.
7.2 Serious adverse events are listed with causality, outcome and status.
7.3 Every AE view carries a notice that it is a summary of recorded data, not a safety assessment.

## 8. SDTM mapping (Release 2)

8.1 The raw EDC tables are mapped to SDTM-style domains DM, AE, VS and SV using SDTM Implementation Guide variable names.
8.2 The mapping is labelled a simplified demonstration model, not a validated implementation.
8.3 The EDC &rarr; data quality &rarr; SDTM &rarr; warehouse &rarr; analytics &rarr; dashboard &rarr; action pipeline is shown.

## 9. Risk Copilot (Release 2 preview)

9.1 The user can select an execution question and get an answer generated only from the computed metrics.
9.2 Answers are deterministic. No LLM is required for the answer to be correct.
9.3 The copilot summarises predefined analytics and rules. It must not diagnose patients, assess causality or make treatment recommendations, and it must say so.

## 10. Constraints

10.1 **Synthetic data only.** No real patient, site, investigator or product data is used or displayed.
10.2 **Traceability.** Every displayed figure decomposes to the data behind it.
10.3 **No medical judgement.** Operational oversight only.
10.4 **Reproducible build.** `python engine/build.py` regenerates all outputs deterministically from a fixed seed.
10.5 **No server dependency for the UI.** The web app is static and reads one JSON file.
10.6 **Accessibility.** Standard headings, keyboard-reachable navigation, colour never the only signal (bands also carry text).
