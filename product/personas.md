# Personas

Five roles use TrialFlow. The first two are the primary users; the platform is designed around their weekly decisions.

## 1. Sponsor Clinical Operations Lead (primary)

**Goal:** keep the trial on timeline and know where the risk is before the monthly governance meeting.
**Context:** accountable for delivery across all sites and vendors. Works from summaries, drills in only when something looks wrong.
**Needs from TrialFlow:**
- One trial-health number they can defend, with its drivers.
- A ranked list of sites that need intervention this week, with the reason.
- Evidence that a past intervention worked (trend after action).

**Frustrations:** status decks that are a week stale; each vendor reporting a different number; no clear "so what".

## 2. Clinical Data Manager (primary)

**Goal:** keep the database clean and the query backlog under control so database lock is not at risk.
**Context:** owns data-quality checks, query generation and reconciliation across forms.
**Needs from TrialFlow:**
- Automated detection of missing data, impossible dates, out-of-range values, duplicates and cross-form inconsistencies.
- Each finding tied to a subject, a location and a severity so it can be routed as a query.
- A data-quality score trended over time and by site.

**Frustrations:** manual listings review; the same error class recurring at a site with no feedback loop; not knowing which site to escalate.

## 3. CRA / Site Monitor

**Goal:** focus monitoring visits on the sites and subjects that need it.
**Context:** covers a portfolio of sites; limited visit days; risk-based monitoring expectations.
**Needs from TrialFlow:**
- Per-site recruitment, data completeness, query load and deviation count in one row.
- A subject-level view of open data items before a visit.

**Frustrations:** preparing for a visit by opening five systems; discovering a consent or window issue on site instead of before.

## 4. Medical Monitor

**Goal:** oversee safety data flow and see that serious events are captured and followed up.
**Context:** reviews adverse events and safety trends; owns clinical judgement, not operational tracking.
**Needs from TrialFlow:**
- AE counts by severity, system organ class and arm, and a list of serious events with status.
- Clear labelling that this is a summary of recorded data, not a safety assessment.

**Frustrations:** operational tools that blur the line into clinical interpretation.

## 5. Site Coordinator (indirect)

**Goal:** know what the sponsor is asking the site to fix, and why.
**Context:** enters data, schedules visits, answers queries. Does not log into TrialFlow directly in the MVP.
**Needs (served through the CRA):**
- A clear, specific list of open data items rather than a vague "please clean up".
- The protocol window for an upcoming visit so it is not missed.

**Frustrations:** bulk query dumps with no priority; deviations raised for issues they were never told about.
