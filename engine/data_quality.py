"""Clinical data-quality rules engine.

Runs a fixed set of deterministic checks over the raw EDC tables and returns a
findings table plus a Data Quality Score. Each finding names the rule, the
subject, the location and a severity so it can be routed to a data query.
"""

from __future__ import annotations

import pandas as pd


def _finding(rule, severity, usubjid, site_id, location, detail):
    return {
        "rule": rule, "severity": severity, "usubjid": usubjid, "site_id": int(site_id),
        "location": location, "detail": detail,
    }


def rule_missing_required_form(forms: pd.DataFrame) -> list[dict]:
    out = []
    miss = forms[forms["completed"] == 0]
    for _, r in miss.iterrows():
        out.append(_finding("Missing required data", "Moderate", r["usubjid"], r["site_id"],
                            f'{r["visit"]} / {r["form_name"]}',
                            "Visit performed but required CRF not entered"))
    return out


def rule_impossible_date(labs: pd.DataFrame, visits: pd.DataFrame) -> list[dict]:
    out = []
    screening = visits[(visits["visit"] == "Screening") & visits["actual_date"].notna()][["usubjid", "actual_date"]]
    screening = screening.rename(columns={"actual_date": "screening_date"})
    m = labs.merge(screening, on="usubjid", how="left")
    m["result_date"] = pd.to_datetime(m["result_date"])
    m["screening_date"] = pd.to_datetime(m["screening_date"])
    bad = m[m["result_date"] < m["screening_date"]]
    for _, r in bad.iterrows():
        out.append(_finding("Impossible date", "Major", r["usubjid"], r["site_id"],
                            f'Laboratory / {r["testcd"]}',
                            f'Result dated {r["result_date"].date()} is before screening {r["screening_date"].date()}'))
    return out


def rule_out_of_range(labs: pd.DataFrame) -> list[dict]:
    out = []
    bad = labs[(labs["result"] > labs["ref_hi"]) | (labs["result"] < labs["ref_lo"])]
    for _, r in bad.iterrows():
        out.append(_finding("Out-of-range value", "Major", r["usubjid"], r["site_id"],
                            f'{r["visit"]} / {r["testcd"]}',
                            f'{r["result"]} {r["unit"]} outside reference {r["ref_lo"]}-{r["ref_hi"]}'))
    return out


def rule_duplicate_record(labs: pd.DataFrame) -> list[dict]:
    out = []
    keys = ["usubjid", "visitnum", "testcd", "result_date"]
    dups = labs[labs.duplicated(subset=keys, keep="first")]
    for _, r in dups.iterrows():
        out.append(_finding("Duplicate record", "Moderate", r["usubjid"], r["site_id"],
                            f'{r["visit"]} / {r["testcd"]}',
                            "Identical subject + visit + test + date entered more than once"))
    return out


def rule_cross_form_inconsistency(subjects: pd.DataFrame) -> list[dict]:
    out = []
    bad = subjects[(subjects["sex"] == "F") & (subjects["pregnancy_status"] == "Not applicable")]
    for _, r in bad.iterrows():
        out.append(_finding("Cross-form inconsistency", "Moderate", r["usubjid"], r["site_id"],
                            "Demographics vs Pregnancy Test",
                            "Sex is Female but pregnancy status recorded as Not applicable"))
    return out


def run(tables: dict) -> dict:
    forms, labs, visits, subjects = (tables["forms"], tables["labs"], tables["visits"], tables["subjects"])
    findings = (
        rule_missing_required_form(forms)
        + rule_impossible_date(labs, visits)
        + rule_out_of_range(labs)
        + rule_duplicate_record(labs)
        + rule_cross_form_inconsistency(subjects)
    )
    fdf = pd.DataFrame(findings)

    # Score: share of evaluable data points that passed all checks.
    evaluable = len(forms) + len(labs) + len(subjects)
    flagged = len(fdf)
    score = round(100 * (1 - flagged / evaluable), 1)

    by_rule = (fdf.groupby("rule").size().sort_values(ascending=False)
               .rename("count").reset_index().to_dict("records")) if len(fdf) else []
    by_site = (fdf.groupby("site_id").size().rename("findings").reset_index()
               .to_dict("records")) if len(fdf) else []

    return {
        "score": score,
        "evaluable_points": int(evaluable),
        "flagged": int(flagged),
        "records_to_review": int(flagged),
        "by_rule": by_rule,
        "by_site": by_site,
        "findings": fdf,
    }
