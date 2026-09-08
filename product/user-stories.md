# User Stories

Format: role, goal, reason, then acceptance criteria as Given / When / Then. IDs are referenced by the backlog and the traceability matrix.

---

### US-001 &mdash; Site recruitment against target
**As a** Clinical Operations Lead **I want** to see site recruitment performance against target **so that** I can identify underperforming sites early.

- **Given** a site has an enrolment target
  **When** actual enrolment is below 70% of target
  **Then** the site is classified as at risk on the recruitment component
  **And** the site detail shows "Recruitment N% of target" as a driver
  **And** the site appears in the intervention list on the Risk Copilot answer.

---

### US-002 &mdash; Detect missing or inconsistent EDC data
**As a** Clinical Data Manager **I want** the system to identify missing or inconsistent EDC data **so that** I can prioritise data queries.

- **Given** a completed visit with a required CRF not entered
  **When** the data-quality engine runs
  **Then** a "Missing required data" finding is created with the subject, site, visit and form
  **And** it is counted in the Data Quality Score and the by-rule and by-site summaries.
- **Given** a lab result dated before the subject's screening date
  **Then** an "Impossible date" finding of severity Major is created.
- **Given** a value outside its predefined reference range
  **Then** an "Out-of-range value" finding of severity Major is created.
- **Given** the same subject + visit + test + date entered more than once
  **Then** a "Duplicate record" finding is created.
- **Given** sex is Female and pregnancy status is recorded as Not applicable
  **Then** a "Cross-form inconsistency" finding is created.

---

### US-003 &mdash; Protocol deviations by site
**As a** Clinical Operations Lead **I want** to identify protocol deviations by site **so that** I can prioritise corrective action.

- **Given** a visit with an actual date outside the protocol window for that visit
  **When** the deviation engine runs
  **Then** a "Visit conducted outside protocol window" deviation is created for that subject and site
  **And** it appears in the deviation log and the by-site and by-type summaries.
- **Given** the deviation log
  **When** I open the Protocol Deviations view
  **Then** I see totals by category (Minor / Moderate / Major) and the top sites by deviation count.

---

### US-004 &mdash; One trial-health number
**As a** Sponsor **I want** a single trial-health score with its drivers **so that** I can state the trial status in a governance meeting and defend it.

- **Given** the current trial data
  **When** the build runs
  **Then** a Trial Health Score from 0 to 100 is produced from five weighted components
  **And** each component shows its value and a red/amber/green band
  **And** the score maps to On Track, Needs Attention or At Risk
  **And** re-running the build on the same data produces the same score.

---

### US-005 &mdash; Site risk drivers and recommended action
**As a** Clinical Operations Lead **I want** each at-risk site to show why it is at risk and what to do **so that** I can act without assembling the picture myself.

- **Given** a site with a risk score
  **When** I select the site row
  **Then** I see the drivers that crossed threshold (recruitment, query rate, deviations, data completeness)
  **And** a recommended action that matches the site's band.

---

### US-006 &mdash; Subject data completeness before a visit
**As a** CRA **I want** to see a subject's open data items **so that** I can resolve them before or during the monitoring visit.

- **Given** a subject with completed visits
  **When** I open the Patient Journey view
  **Then** I see each visit's scheduled date, actual date and status
  **And** a list of missing or incomplete forms per visit
  **And** a data-completeness percentage for the subject
  **And** each open item phrased so it can be sent to the site as a query.

---

### US-007 &mdash; Adverse events for operational oversight
**As a** Medical Monitor **I want** AE counts by severity, system organ class and arm, and the serious events listed **so that** I can see that safety data is flowing and being followed up.

- **Given** recorded adverse events
  **When** I open the Adverse Events view
  **Then** I see counts by severity, by system organ class and by arm
  **And** a list of serious adverse events with causality, outcome and status
  **And** a notice that this is a summary of recorded data, not a safety assessment.

---

### US-008 &mdash; Read the data in a standard structure
**As a** Statistical Programmer **I want** the EDC data mapped to SDTM-style domains **so that** analysis and submission-style tooling can read a familiar structure.

- **Given** the raw EDC tables
  **When** the SDTM mapping runs
  **Then** DM, AE, VS and SV domains are produced with SDTM Implementation Guide variable names
  **And** the output is labelled a simplified demonstration model, not a validated implementation
  **And** row counts and a sample of each domain are visible in the app.

---

### US-009 &mdash; Ask an execution question
**As a** Clinical Operations Lead **I want** to ask which sites need intervention and why **so that** I can prepare the weekly review quickly.

- **Given** the computed metrics
  **When** I select a question in the Risk Copilot
  **Then** I get a summary and a breakdown generated only from those metrics
  **And** the answer is the same every time for the same data
  **And** the view states that there is no LLM and no medical advice.

---

### US-010 &mdash; Trust the numbers
**As any** user **I want** every figure to trace back to its data **so that** I can rely on it in a regulated setting.

- **Given** any score or KPI in the app
  **When** I look for its basis
  **Then** the component values, counts or findings behind it are visible in the same or a linked view
  **And** the build is reproducible from a fixed seed.
