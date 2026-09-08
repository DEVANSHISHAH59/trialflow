"""Site-level and trial-level risk scoring.

Site risk is a 0-100 score (higher is worse) built from four normalised
components. Trial health is a 0-100 score (higher is better) that rolls up
recruitment, data completeness, query backlog, site performance and protocol
deviations. Both are pure functions of the raw tables so the numbers are
reproducible and explainable.
"""

from __future__ import annotations

import pandas as pd

from config import SITE_RISK_BANDS, SITE_RISK_WEIGHTS, TRIAL_HEALTH_WEIGHTS


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def site_table(tables: dict) -> pd.DataFrame:
    sites = tables["sites"]
    subjects = tables["subjects"]
    forms = tables["forms"]
    queries = tables["queries"]
    devs = tables["deviations"]

    active = sites[sites["status"] == "Active"].copy()
    enrolled = subjects.groupby("site_id").size().rename("enrolled")
    completeness = (forms.groupby("site_id")["completed"].mean().rename("form_completeness"))
    open_q = (queries[queries["status"].isin(["Open", "Answered"])]
              .groupby("site_id").size().rename("open_queries"))
    dev_n = devs.groupby("site_id").size().rename("deviations")

    df = (active.set_index("site_id")
          .join(enrolled).join(completeness).join(open_q).join(dev_n)
          .reset_index())
    for c in ["enrolled", "open_queries", "deviations"]:
        df[c] = df[c].fillna(0).astype(int)
    df["form_completeness"] = (df["form_completeness"].fillna(1.0) * 100).round(1)
    df["recruitment_pct"] = (df["enrolled"] / df["target_enrollment"] * 100).round(1)

    # normalised risk components in [0, 1]
    df["c_recruitment_gap"] = df["recruitment_pct"].apply(lambda p: _clip01((85 - p) / 60))
    df["c_query_rate"] = (df["open_queries"] / df["enrolled"].clip(lower=1)).apply(lambda r: _clip01(r / 1.5))
    df["c_deviation_rate"] = (df["deviations"] / df["enrolled"].clip(lower=1)).apply(lambda r: _clip01(r / 0.5))
    df["c_data_incompleteness"] = ((100 - df["form_completeness"]) / 100).apply(lambda r: _clip01(r / 0.15))

    w = SITE_RISK_WEIGHTS
    df["risk_score"] = (
        w["recruitment_gap"] * df["c_recruitment_gap"]
        + w["query_rate"] * df["c_query_rate"]
        + w["deviation_rate"] * df["c_deviation_rate"]
        + w["data_incompleteness"] * df["c_data_incompleteness"]
    ) * 100
    df["risk_score"] = df["risk_score"].round(1)

    def band(s):
        if s < SITE_RISK_BANDS["green"]:
            return "green"
        if s < SITE_RISK_BANDS["amber"]:
            return "amber"
        return "red"

    df["risk_band"] = df["risk_score"].apply(band)

    def reasons(row):
        out = []
        if row["recruitment_pct"] < 70:
            out.append(f'Recruitment {row["recruitment_pct"]:.0f}% of target')
        if row["enrolled"] and row["open_queries"] / max(row["enrolled"], 1) > 0.6:
            out.append(f'{row["open_queries"]} open queries ({row["open_queries"]/max(row["enrolled"],1):.1f} per subject)')
        if row["enrolled"] and row["deviations"] / max(row["enrolled"], 1) > 0.25:
            out.append(f'{row["deviations"]} protocol deviations')
        if row["form_completeness"] < 92:
            out.append(f'Data completeness {row["form_completeness"]:.0f}%')
        return out

    df["risk_reasons"] = df.apply(reasons, axis=1)
    df["recommended_action"] = df.apply(
        lambda r: "Initiate site performance review; prioritise open data queries and CAPA follow-up."
        if r["risk_band"] == "red" else
        ("Increase monitoring frequency; agree recruitment and query-resolution plan with site."
         if r["risk_band"] == "amber" else "Routine monitoring."), axis=1)

    cols = ["site_id", "country", "pi_name", "monitor", "target_enrollment", "enrolled",
            "recruitment_pct", "form_completeness", "open_queries", "deviations",
            "risk_score", "risk_band", "risk_reasons", "recommended_action"]
    return df[cols].sort_values("risk_score", ascending=False).reset_index(drop=True)


def trial_health(tables: dict, sites_scored: pd.DataFrame) -> dict:
    subjects = tables["subjects"]
    forms = tables["forms"]
    queries = tables["queries"]
    devs = tables["deviations"]
    from config import STUDY

    enrolled = len(subjects)
    recruitment = _clip01(enrolled / STUDY["target_enrollment"])
    data_completeness = float(forms["completed"].mean())
    open_q = int((queries["status"].isin(["Open", "Answered"])).sum())
    query_backlog = _clip01(1 - (open_q / max(enrolled, 1)) / 1.2)
    site_perf = _clip01(1 - (sites_scored["risk_band"].isin(["red", "amber"]).mean()))
    major_dev = int((devs["dvcat"] == "Major").sum())
    dev_factor = _clip01(1 - (len(devs) / max(enrolled, 1)) / 0.4) * (0.85 if major_dev > 5 else 1.0)

    w = TRIAL_HEALTH_WEIGHTS
    components = {
        "recruitment": round(recruitment * 100, 1),
        "data_completeness": round(data_completeness * 100, 1),
        "query_backlog": round(query_backlog * 100, 1),
        "site_performance": round(site_perf * 100, 1),
        "protocol_deviations": round(dev_factor * 100, 1),
    }
    score = round(sum(w[k] * v for k, v in components.items()), 0)

    def rag(v):
        return "green" if v >= 80 else ("amber" if v >= 60 else "red")

    status = "On Track" if score >= 80 else ("Needs Attention" if score >= 65 else "At Risk")
    return {
        "score": int(score),
        "status": status,
        "components": [{"name": k, "value": v, "rag": rag(v)} for k, v in components.items()],
    }
