-- Trial-level execution metrics, one row per study.
-- Reads the raw EDC tables loaded into the TrialFlow SQLite warehouse.

WITH enrolment AS (
    SELECT COUNT(*) AS enrolled,
           SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed,
           SUM(CASE WHEN status = 'Withdrawn' THEN 1 ELSE 0 END) AS withdrawn,
           SUM(CASE WHEN status = 'Screen Failure' THEN 1 ELSE 0 END) AS screen_failures
    FROM subjects
),
sites_active AS (
    SELECT COUNT(*) AS active_sites,
           SUM(target_enrollment) AS planned_capacity
    FROM sites WHERE status = 'Active'
),
forms_done AS (
    SELECT ROUND(100.0 * AVG(completed), 1) AS data_completeness_pct FROM forms
),
queries_open AS (
    SELECT COUNT(*) AS open_queries,
           SUM(CASE WHEN age_days > 45 THEN 1 ELSE 0 END) AS aged_queries
    FROM queries WHERE status IN ('Open', 'Answered')
),
devs AS (
    SELECT COUNT(*) AS deviations,
           SUM(CASE WHEN dvcat = 'Major' THEN 1 ELSE 0 END) AS major_deviations
    FROM deviations
),
ae AS (
    SELECT COUNT(*) AS ae_reports,
           SUM(CASE WHEN aeser = 'Y' THEN 1 ELSE 0 END) AS serious_ae
    FROM adverse_events
)
SELECT
    e.enrolled,
    e.completed,
    e.withdrawn,
    e.screen_failures,
    ROUND(100.0 * e.enrolled / 900.0, 1) AS recruitment_pct_of_target,
    s.active_sites,
    s.planned_capacity,
    f.data_completeness_pct,
    q.open_queries,
    q.aged_queries,
    d.deviations,
    d.major_deviations,
    a.ae_reports,
    a.serious_ae
FROM enrolment e, sites_active s, forms_done f, queries_open q, devs d, ae a;
