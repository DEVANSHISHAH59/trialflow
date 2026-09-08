"""Analytics rollups for the TrialFlow dashboard.

Turns the raw tables plus the risk and quality outputs into the compact JSON
the web app renders: executive KPIs, chart series, an example patient journey
and the pre-computed Risk Copilot answers.
"""

from __future__ import annotations

import pandas as pd

from config import STUDY, VISIT_SCHEDULE


def executive_kpis(tables, health, dq, sites_scored) -> dict:
    subjects = tables["subjects"]
    visits = tables["visits"]
    queries = tables["queries"]
    devs = tables["deviations"]
    aes = tables["adverse_events"]

    enrolled = len(subjects)
    active_sites = int((tables["sites"]["status"] == "Active").sum())
    open_q = int(queries["status"].isin(["Open", "Answered"]).sum())
    realised = visits[visits["status"].isin(["Done", "Missed"])]
    completeness = round(float(tables["forms"]["completed"].mean()) * 100, 1)
    sae = int((aes["aeser"] == "Y").sum())

    return {
        "study": STUDY,
        "trial_status": health["status"],
        "trial_health": health["score"],
        "health_components": health["components"],
        "kpis": [
            {"label": "Patients enrolled", "value": f"{enrolled} / {STUDY['target_enrollment']}",
             "sub": f"{round(enrolled / STUDY['target_enrollment'] * 100, 1)}% of target"},
            {"label": "Recruitment rate", "value": f"{round(enrolled / STUDY['target_enrollment'] * 100, 1)}%",
             "sub": "cumulative vs plan"},
            {"label": "Active sites", "value": active_sites, "sub": f"{len(tables['sites'])} planned"},
            {"label": "Data completeness", "value": f"{completeness}%", "sub": "required CRFs entered"},
            {"label": "Open queries", "value": open_q, "sub": f"{int((queries['age_days'] > 45).sum())} aged >45d"},
            {"label": "Protocol deviations", "value": len(devs),
             "sub": f"{int((devs['dvcat'] == 'Major').sum())} major"},
            {"label": "AE reports", "value": len(aes), "sub": f"{sae} serious"},
            {"label": "Sites at risk", "value": int(sites_scored["risk_band"].isin(["red", "amber"]).sum()),
             "sub": f"{int((sites_scored['risk_band'] == 'red').sum())} high risk"},
        ],
        "data_quality_score": dq["score"],
        "records_to_review": dq["records_to_review"],
    }


def recruitment_series(tables) -> dict:
    subjects = tables["subjects"].copy()
    subjects["enrollment_date"] = pd.to_datetime(subjects["enrollment_date"])
    by_month = (subjects.set_index("enrollment_date").resample("MS").size().cumsum())
    months = [d.strftime("%Y-%m") for d in by_month.index]
    actual = [int(v) for v in by_month.values]
    # simple linear plan to target over the same horizon
    n = len(months)
    plan = [round(STUDY["target_enrollment"] * (i + 1) / n) for i in range(n)]
    return {"months": months, "actual": actual, "plan": plan}


def enrollment_by_country(tables) -> list[dict]:
    s = tables["subjects"]
    return (s.groupby("country").size().rename("enrolled").reset_index()
            .sort_values("enrolled", ascending=False).to_dict("records"))


def ae_breakdowns(tables) -> dict:
    aes = tables["adverse_events"]
    by_sev = aes.groupby("aesev").size().reindex(["Mild", "Moderate", "Severe"]).fillna(0).astype(int)
    by_soc = (aes.groupby("aebodsys").size().sort_values(ascending=False).head(8))
    by_arm = aes.groupby(["arm", "aesev"]).size().unstack(fill_value=0)
    serious = aes[aes["aeser"] == "Y"][["usubjid", "site_id", "aeterm", "aesev", "aerel", "aestdtc", "aeout", "arm"]]
    return {
        "by_severity": [{"severity": k, "count": int(v)} for k, v in by_sev.items()],
        "by_soc": [{"soc": k, "count": int(v)} for k, v in by_soc.items()],
        "by_arm": [{"arm": a, **{s: int(by_arm.loc[a, s]) for s in by_arm.columns}} for a in by_arm.index],
        "serious": serious.to_dict("records"),
    }


def deviation_breakdowns(tables) -> dict:
    d = tables["deviations"]
    by_cat = d.groupby("dvcat").size().reindex(["Minor", "Moderate", "Major"]).fillna(0).astype(int)
    by_type = d.groupby("dvterm").size().sort_values(ascending=False)
    by_site = d.groupby("site_id").size().sort_values(ascending=False).head(10)
    return {
        "total": int(len(d)),
        "by_category": [{"category": k, "count": int(v)} for k, v in by_cat.items()],
        "by_type": [{"type": k, "count": int(v)} for k, v in by_type.items()],
        "by_site": [{"site_id": int(k), "count": int(v)} for k, v in by_site.items()],
        "records": d.sort_values(["dvcat", "site_id"]).to_dict("records"),
    }


def example_patient_journey(tables) -> dict:
    """Pick one mid-treatment subject with a visible data gap for the drill-down."""
    subjects = tables["subjects"]
    visits = tables["visits"]
    forms = tables["forms"]
    labs = tables["labs"]

    missing_by_sub = forms[forms["completed"] == 0].groupby("usubjid").size()
    oor = labs[(labs["result"] > labs["ref_hi"]) | (labs["result"] < labs["ref_lo"])]
    oor_by_sub = oor.groupby("usubjid").size()
    missed_by_sub = visits[visits["status"] == "Missed"].groupby("usubjid").size()
    mid = subjects[subjects["status"].isin(["Active", "Withdrawn"])]["usubjid"]
    score = (missing_by_sub.reindex(mid).fillna(0)
             + oor_by_sub.reindex(mid).fillna(0)
             + missed_by_sub.reindex(mid).fillna(0))
    score = score[(missing_by_sub.reindex(mid).fillna(0) > 0) & (oor_by_sub.reindex(mid).fillna(0) > 0)]
    usubjid = score.sort_values(ascending=False).index[0] if len(score) else subjects["usubjid"].iloc[0]
    sub = subjects[subjects["usubjid"] == usubjid].iloc[0]
    v = visits[visits["usubjid"] == usubjid].sort_values("visitnum")
    f = forms[forms["usubjid"] == usubjid]
    completeness = round(float(f["completed"].mean()) * 100, 1) if len(f) else 0.0

    rows = []
    for _, r in v.iterrows():
        vv_forms = f[f["visit"] == r["visit"]]
        missing = vv_forms[vv_forms["completed"] == 0]["form_name"].tolist()
        rows.append({
            "visit": r["visit"], "scheduled_date": r["scheduled_date"],
            "actual_date": r["actual_date"], "status": r["status"],
            "missing_forms": missing,
        })
    open_issues = []
    for _, r in v.iterrows():
        vv_forms = f[f["visit"] == r["visit"]]
        for name in vv_forms[vv_forms["completed"] == 0]["form_name"]:
            open_issues.append(f'Missing {name} at {r["visit"]}')
    lb = labs[labs["usubjid"] == usubjid]
    for _, r in lb[(lb["result"] > lb["ref_hi"]) | (lb["result"] < lb["ref_lo"])].iterrows():
        open_issues.append(f'{r["testcd"]} {r["result"]}{r["unit"]} out of range at {r["visit"]}')

    return {
        "usubjid": usubjid,
        "site_id": int(sub["site_id"]),
        "country": sub["country"],
        "arm": sub["arm"],
        "sex": sub["sex"],
        "age": int(sub["age"]),
        "status": sub["status"],
        "data_completeness": completeness,
        "visits": rows,
        "open_issues": open_issues[:8],
    }


def risk_copilot(tables, health, dq, sites_scored) -> list[dict]:
    """Deterministic answers over the computed metrics. No LLM, no medical advice."""
    red = sites_scored[sites_scored["risk_band"] == "red"]
    amber = sites_scored[sites_scored["risk_band"] == "amber"]
    qa = []

    lines = []
    for _, s in pd.concat([red, amber]).head(6).iterrows():
        lines.append({
            "site": f'Site {int(s["site_id"])} ({s["country"]})',
            "band": s["risk_band"],
            "score": s["risk_score"],
            "reasons": s["risk_reasons"],
            "action": s["recommended_action"],
        })
    qa.append({
        "q": "Which sites require intervention this week and why?",
        "summary": f'{len(red)} sites are high risk and {len(amber)} need attention. '
                   f'Highest is Site {int(sites_scored.iloc[0]["site_id"])} '
                   f'({sites_scored.iloc[0]["country"]}) at risk score {sites_scored.iloc[0]["risk_score"]:.0f}.',
        "detail": lines,
    })

    low = [c for c in health["components"] if c["rag"] != "green"]
    qa.append({
        "q": "Why is the trial health score where it is?",
        "summary": f'Trial health is {health["score"]}/100 ({health["status"]}). '
                   f'{len(low)} of 5 components are below target.',
        "detail": [{"component": c["name"].replace("_", " ").title(), "value": c["value"], "rag": c["rag"]}
                   for c in health["components"]],
    })

    qa.append({
        "q": "What are the biggest data-quality issues right now?",
        "summary": f'Data quality score {dq["score"]}%, {dq["records_to_review"]} records to review.',
        "detail": [{"rule": r["rule"], "count": r["count"]} for r in dq["by_rule"]],
    })

    aes = tables["adverse_events"]
    sae = aes[aes["aeser"] == "Y"]
    top_soc = aes.groupby("aebodsys").size().sort_values(ascending=False).head(3)
    qa.append({
        "q": "Are there any emerging safety signals?",
        "summary": f'{len(aes)} AEs reported, {len(sae)} serious. This is a summary of recorded data, '
                   f'not a medical assessment.',
        "detail": [{"system_organ_class": k, "events": int(v)} for k, v in top_soc.items()]
                  + [{"system_organ_class": "Serious AEs (all arms)", "events": int(len(sae))}],
    })
    return qa
