-- Site performance league table: recruitment, data completeness, query load and
-- protocol deviations per activated site. Feeds the CTMS-style site view.

WITH enrolled AS (
    SELECT site_id, COUNT(*) AS enrolled
    FROM subjects GROUP BY site_id
),
completeness AS (
    SELECT site_id, ROUND(100.0 * AVG(completed), 1) AS form_completeness_pct
    FROM forms GROUP BY site_id
),
open_q AS (
    SELECT site_id, COUNT(*) AS open_queries
    FROM queries WHERE status IN ('Open', 'Answered')
    GROUP BY site_id
),
dev AS (
    SELECT site_id, COUNT(*) AS deviations
    FROM deviations GROUP BY site_id
)
SELECT
    s.site_id,
    s.country,
    s.monitor,
    s.target_enrollment,
    COALESCE(e.enrolled, 0) AS enrolled,
    ROUND(100.0 * COALESCE(e.enrolled, 0) / s.target_enrollment, 1) AS recruitment_pct,
    COALESCE(c.form_completeness_pct, 100.0) AS form_completeness_pct,
    COALESCE(q.open_queries, 0) AS open_queries,
    ROUND(1.0 * COALESCE(q.open_queries, 0) / MAX(COALESCE(e.enrolled, 0), 1), 2) AS queries_per_subject,
    COALESCE(d.deviations, 0) AS deviations
FROM sites s
LEFT JOIN enrolled e ON e.site_id = s.site_id
LEFT JOIN completeness c ON c.site_id = s.site_id
LEFT JOIN open_q q ON q.site_id = s.site_id
LEFT JOIN dev d ON d.site_id = s.site_id
WHERE s.status = 'Active'
ORDER BY recruitment_pct ASC, open_queries DESC;
