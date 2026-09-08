-- Data-quality summary by check type and by site.
-- Mirrors the Python data-quality engine so results can be reconciled.

WITH missing_forms AS (
    SELECT site_id, 'Missing required data' AS rule, COUNT(*) AS findings
    FROM forms WHERE completed = 0 GROUP BY site_id
),
out_of_range AS (
    SELECT site_id, 'Out-of-range value' AS rule, COUNT(*) AS findings
    FROM labs WHERE result > ref_hi OR result < ref_lo GROUP BY site_id
),
duplicates AS (
    SELECT site_id, 'Duplicate record' AS rule, COUNT(*) AS findings
    FROM (
        SELECT site_id, usubjid, visitnum, testcd, result_date, COUNT(*) AS n
        FROM labs
        GROUP BY site_id, usubjid, visitnum, testcd, result_date
        HAVING COUNT(*) > 1
    ) d
    GROUP BY site_id
),
inconsistency AS (
    SELECT site_id, 'Cross-form inconsistency' AS rule, COUNT(*) AS findings
    FROM subjects
    WHERE sex = 'F' AND pregnancy_status = 'Not applicable'
    GROUP BY site_id
),
all_findings AS (
    SELECT * FROM missing_forms
    UNION ALL SELECT * FROM out_of_range
    UNION ALL SELECT * FROM duplicates
    UNION ALL SELECT * FROM inconsistency
)
SELECT rule,
       SUM(findings) AS total_findings,
       COUNT(DISTINCT site_id) AS sites_affected
FROM all_findings
GROUP BY rule
ORDER BY total_findings DESC;
