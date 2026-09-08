# Product Roadmap

Three releases. Each one is shippable and leaves the product more useful than the last. Scope is deliberately thin per release so feedback lands before the next build.

## MVP &mdash; "See the trial" (shipped in this repo)

The single-trial health view that a clinical operations lead and a data manager can use in a weekly review.

- Executive overview: Trial Health Score with drivers, headline KPIs, recruitment vs plan, enrolment by country.
- Site performance league table with a site risk score, drivers and recommended action.
- Patient journey (EDC): visit schedule vs capture and open data items for one subject.
- Data-quality engine: five checks, findings tied to subject and location, Data Quality Score.
- Synthetic Phase II dataset and a deterministic build pipeline.

**Exit criteria:** a user can open the app cold and, within two minutes, name the trial status, the three sites most at risk and the biggest data-quality issue.

## Release 2 &mdash; "Explain and standardise"

Turn the view into something that supports compliance conversations and downstream analysis.

- Protocol Deviation Engine: rules-based detection beyond visit windows (consent timing, eligibility, dosing), categorised, with CAPA status.
- Adverse Event dashboard: severity, system organ class, arm, serious-event tracking.
- Simplified CDISC SDTM mapping (DM, AE, VS, SV) and the EDC &rarr; SDTM &rarr; analytics pipeline view.
- Data-quality trend over time and query-ageing view.

**Exit criteria:** a data manager can show the deviation and query position by site in a sponsor meeting without exporting to spreadsheets.

## Release 3 &mdash; "Act earlier"

Move from reporting the present to prioritising the next action.

- Risk scoring v2: configurable weights, thresholds and bands per study.
- Automated alerts when a site crosses a threshold, with the drivers attached.
- Predictive recruitment: projected enrolment date per site and for the trial, with confidence.
- Risk Copilot: natural-language questions answered from the computed metrics (deterministic, no medical advice).
- Intervention tracking: log an action against a site and measure the trend afterwards.

**Exit criteria:** the weekly site review is driven by the alert queue rather than by someone manually scanning the table.

## Later / not now

- Multi-study portfolio view.
- Write-back of queries to an EDC via API.
- Role-based access and site-facing login for coordinators.
- Integration with a real CTMS for milestone data.

## Sequencing rationale

MVP proves the core idea (one health view that ends in an action) with the least build. Release 2 adds the artefacts that make it credible in a regulated setting. Release 3 is where the product earns its keep by changing how the team works, and it is deliberately last because it depends on the risk model and the data being trusted first.
