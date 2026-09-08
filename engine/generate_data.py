"""Synthetic Phase II clinical-trial data generator for TrialFlow.

Produces raw, EDC-style tables with deliberately seeded quality problems
(missing forms, out-of-window visits, impossible dates, duplicates, cross-form
inconsistencies) so the data-quality and risk engines have something to find.

All data is synthetic. No real patients, sites or products are represented.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from config import COUNTRIES, REFERENCE_RANGES, SEED, STUDY, VISIT_SCHEDULE, REQUIRED_FORMS

FIRST_NAMES = ["Dr A. Byrne", "Dr K. Novak", "Dr M. Rossi", "Dr S. Kaur", "Dr L. Meyer",
               "Dr P. Dubois", "Dr J. Kowalski", "Dr R. Santos", "Dr H. Andersen", "Dr T. Nguyen"]
MONITORS = ["CRA-01", "CRA-02", "CRA-03", "CRA-04", "CRA-05"]

AE_TERMS = [
    ("Headache", "Nervous system disorders", ["Mild", "Mild", "Moderate"]),
    ("Nausea", "Gastrointestinal disorders", ["Mild", "Moderate"]),
    ("Nasopharyngitis", "Infections and infestations", ["Mild", "Mild"]),
    ("Injection site erythema", "General disorders", ["Mild", "Moderate"]),
    ("Fatigue", "General disorders", ["Mild", "Moderate"]),
    ("Upper respiratory tract infection", "Infections and infestations", ["Mild", "Moderate"]),
    ("Alanine aminotransferase increased", "Investigations", ["Moderate", "Severe"]),
    ("Diarrhoea", "Gastrointestinal disorders", ["Mild", "Moderate"]),
    ("Dizziness", "Nervous system disorders", ["Mild", "Moderate"]),
    ("Hypertension", "Vascular disorders", ["Moderate", "Severe"]),
]

DEVIATION_TYPES = [
    ("Visit conducted outside protocol window", "Minor"),
    ("Required assessment not performed", "Moderate"),
    ("Informed consent not on file at time of procedure", "Major"),
    ("Inclusion/exclusion criterion not met", "Major"),
    ("Study drug dosing error", "Moderate"),
    ("Prohibited concomitant medication", "Moderate"),
    ("Sample not processed within required time", "Minor"),
]

QUERY_REASONS = [
    ("missing value", "Required field left blank"),
    ("out of range", "Value outside expected clinical range, please confirm"),
    ("inconsistent date", "Assessment date is before the visit date"),
    ("implausible value", "Value is biologically implausible, please verify source"),
    ("missing page", "Expected CRF page not entered for this visit"),
    ("coding clarification", "Verbatim term needs clarification for medical coding"),
]


def _rng():
    return np.random.default_rng(SEED)


def build_sites(rng) -> pd.DataFrame:
    rows = []
    site_id = 101
    country_pool = []
    for name, n in COUNTRIES:
        country_pool += [name] * n
    rng.shuffle(country_pool)
    activation_start = pd.Timestamp(STUDY["first_patient_in"]) - pd.Timedelta(days=25)
    for i, country in enumerate(country_pool):
        activated = i < 38  # 2 planned sites never activated
        target = int(rng.integers(18, 30))
        act_date = activation_start + pd.Timedelta(days=int(rng.integers(0, 210)))
        rows.append({
            "site_id": site_id,
            "country": country,
            "pi_name": FIRST_NAMES[i % len(FIRST_NAMES)],
            "monitor": MONITORS[i % len(MONITORS)],
            "target_enrollment": target,
            "activation_date": act_date.date().isoformat() if activated else None,
            "status": "Active" if activated else "Planned",
        })
        site_id += 1
    return pd.DataFrame(rows)


SLOW_SITES = {102, 108, 119, 126, 131}
MEDIUM_SITES = {103, 107, 114, 121, 128, 135}
FAST_SITES = {101, 104, 112}


def build_subjects(rng, sites: pd.DataFrame) -> pd.DataFrame:
    active = sites[sites["status"] == "Active"].copy()
    # High-risk sites recruit far below target; a couple of stars over-recruit.
    slow_sites = SLOW_SITES
    fast_sites = FAST_SITES
    rows = []
    seq = {}
    data_cut = pd.Timestamp(STUDY["data_cut"])
    for _, s in active.iterrows():
        sid = int(s["site_id"])
        target = int(s["target_enrollment"])
        if sid in slow_sites:
            n = int(round(target * rng.uniform(0.30, 0.50)))
        elif sid in MEDIUM_SITES:
            n = int(round(target * rng.uniform(0.55, 0.70)))
        elif sid in fast_sites:
            n = int(round(target * rng.uniform(1.02, 1.15)))
        else:
            n = int(round(target * rng.uniform(0.78, 0.98)))
        act = pd.Timestamp(s["activation_date"])
        for _ in range(n):
            seq[sid] = seq.get(sid, 0) + 1
            usubjid = f"{STUDY['studyid']}-{sid}-{seq[sid]:03d}"
            enroll = act + pd.Timedelta(days=int(rng.integers(5, 480)))
            if enroll > data_cut:
                enroll = data_cut - pd.Timedelta(days=int(rng.integers(1, 30)))
            days_on_study = (data_cut - enroll).days
            arm = STUDY["arms"][int(rng.integers(0, 2))]
            sex = "F" if rng.random() < 0.54 else "M"
            age = int(np.clip(rng.normal(45, 13), 18, 78))
            # disposition
            r = rng.random()
            if days_on_study >= 112 and r < 0.72:
                status, disp = "Completed", "Completed"
            elif r < 0.08:
                status, disp = "Withdrawn", rng.choice(
                    ["Adverse event", "Withdrawal by subject", "Lost to follow-up", "Protocol deviation"])
            elif r < 0.13:
                status, disp = "Screen Failure", "Screen failure"
            else:
                status, disp = "Active", "On treatment"
            preg = "Not applicable" if sex == "M" else rng.choice(
                ["Negative", "Not applicable"], p=[0.94, 0.06])  # a few mis-recorded on purpose
            rows.append({
                "usubjid": usubjid, "site_id": sid, "country": s["country"], "arm": arm,
                "sex": sex, "age": age, "enrollment_date": enroll.date().isoformat(),
                "status": status, "disposition": disp, "pregnancy_status": preg,
            })
    return pd.DataFrame(rows)


def build_visits_forms_labs(rng, subjects: pd.DataFrame):
    data_cut = pd.Timestamp(STUDY["data_cut"])
    v_rows, f_rows, l_rows = [], [], []
    for _, sub in subjects.iterrows():
        struggling = int(sub["site_id"]) in SLOW_SITES
        miss_form_p = 0.045 if struggling else 0.02
        drift_p = 0.09 if struggling else 0.055
        if sub["status"] == "Screen Failure":
            expected_visits = VISIT_SCHEDULE[:1]
        else:
            expected_visits = VISIT_SCHEDULE
        rand_date = pd.Timestamp(sub["enrollment_date"])
        screening_actual = None
        for v in expected_visits:
            target = rand_date + pd.Timedelta(days=v["day"])
            due = target
            # visit realised only if its due date has passed
            realised = due <= data_cut
            status = "Pending"
            actual = None
            if realised:
                # most visits land in window; ~9% drift out; ~4% missed
                roll = rng.random()
                if roll < 0.02 and v["visitnum"] > 2:
                    status = "Missed"
                else:
                    if roll < drift_p and v["visitnum"] > 2:
                        offset = int(rng.choice([v["win_hi"] + rng.integers(2, 9),
                                                 v["win_lo"] - rng.integers(2, 7)]))
                    else:
                        offset = int(rng.integers(v["win_lo"], v["win_hi"] + 1))
                    actual = (due + pd.Timedelta(days=offset))
                    status = "Done"
            if sub["status"] == "Withdrawn" and v["visitnum"] >= 4 and rng.random() < 0.7:
                status, actual = "Pending", None
            if v["visit"] == "Screening" and actual is not None:
                screening_actual = actual
            v_rows.append({
                "usubjid": sub["usubjid"], "site_id": sub["site_id"], "visitnum": v["visitnum"],
                "visit": v["visit"], "scheduled_date": due.date().isoformat(),
                "actual_date": actual.date().isoformat() if actual is not None else None,
                "status": status,
                "win_lo": v["win_lo"], "win_hi": v["win_hi"], "target_day": v["day"],
            })
            # forms: an EDC only holds CRF pages for visits that occurred
            if status == "Done":
                for form in REQUIRED_FORMS[v["visit"]]:
                    completed = rng.random() > miss_form_p
                    entered = None
                    if completed and actual is not None:
                        entered = (actual + pd.Timedelta(days=int(rng.integers(0, 12)))).date().isoformat()
                    f_rows.append({
                        "usubjid": sub["usubjid"], "site_id": sub["site_id"], "visitnum": v["visitnum"],
                        "visit": v["visit"], "form_name": form, "completed": int(completed),
                        "entered_date": entered,
                    })
            # labs / vitals on visits that have a Laboratory or Vital Signs form
            if status == "Done" and actual is not None and (
                    "Laboratory" in REQUIRED_FORMS[v["visit"]] or "Vital Signs" in REQUIRED_FORMS[v["visit"]]):
                for testcd, (lo, hi, unit) in REFERENCE_RANGES.items():
                    if rng.random() < 0.05:
                        continue  # missing result -> feeds completeness + query
                    span = hi - lo
                    val = rng.normal((lo + hi) / 2, span / 6.5)
                    if rng.random() < 0.012:  # genuine out-of-range
                        val = hi + rng.uniform(1, span * 0.4) if rng.random() < 0.5 else lo - rng.uniform(1, span * 0.3)
                    result_date = actual + pd.Timedelta(days=int(rng.integers(0, 4)))
                    # ~1% impossible: result dated before screening
                    if rng.random() < 0.0015 and screening_actual is not None:
                        result_date = screening_actual - pd.Timedelta(days=int(rng.integers(1, 20)))
                    l_rows.append({
                        "usubjid": sub["usubjid"], "site_id": sub["site_id"], "visitnum": v["visitnum"],
                        "visit": v["visit"], "testcd": testcd, "result": round(float(val), 1),
                        "unit": unit, "result_date": result_date.date().isoformat(),
                        "ref_lo": lo, "ref_hi": hi,
                    })
    visits = pd.DataFrame(v_rows)
    forms = pd.DataFrame(f_rows)
    labs = pd.DataFrame(l_rows)
    # seed a handful of exact duplicate lab rows
    if len(labs):
        dup = labs.sample(n=max(3, len(labs) // 400), random_state=SEED)
        labs = pd.concat([labs, dup], ignore_index=True)
    return visits, forms, labs


def build_adverse_events(rng, subjects: pd.DataFrame) -> pd.DataFrame:
    rows = []
    seq = 0
    for _, sub in subjects.iterrows():
        if sub["status"] == "Screen Failure":
            continue
        n_ae = rng.poisson(0.8)
        start = pd.Timestamp(sub["enrollment_date"])
        for _ in range(int(n_ae)):
            seq += 1
            term, soc, sev_pool = AE_TERMS[int(rng.integers(0, len(AE_TERMS)))]
            sev = sev_pool[int(rng.integers(0, len(sev_pool)))]
            serious = "Y" if (sev == "Severe" and rng.random() < 0.6) else "N"
            rel = rng.choice(["Not related", "Unlikely", "Possible", "Probable"],
                             p=[0.35, 0.2, 0.3, 0.15])
            st = start + pd.Timedelta(days=int(rng.integers(3, 150)))
            ongoing = rng.random() < 0.3
            en = None if ongoing else (st + pd.Timedelta(days=int(rng.integers(2, 45)))).date().isoformat()
            rows.append({
                "usubjid": sub["usubjid"], "site_id": sub["site_id"], "aeseq": seq,
                "aeterm": term, "aebodsys": soc, "aesev": sev, "aeser": serious,
                "aerel": rel, "aestdtc": st.date().isoformat(), "aeendtc": en,
                "aeout": "Recovered/Resolved" if en else "Not recovered/Not resolved",
                "arm": sub["arm"],
            })
    return pd.DataFrame(rows)


def build_deviations(rng, subjects: pd.DataFrame, visits: pd.DataFrame) -> pd.DataFrame:
    rows = []
    # derive out-of-window visit deviations directly from the visit data
    done = visits[visits["actual_date"].notna()].copy()
    done["actual"] = pd.to_datetime(done["actual_date"])
    done["sched"] = pd.to_datetime(done["scheduled_date"])
    done["delta"] = (done["actual"] - done["sched"]).dt.days
    oow = done[(done["delta"] > done["win_hi"]) | (done["delta"] < done["win_lo"])]
    for _, r in oow.iterrows():
        rows.append({
            "usubjid": r["usubjid"], "site_id": r["site_id"], "visitnum": r["visitnum"],
            "visit": r["visit"], "dvterm": "Visit conducted outside protocol window",
            "dvcat": "Minor", "dvdtc": r["actual_date"],
            "dvstatus": rng.choice(["Open", "Closed"], p=[0.4, 0.6]),
            "corrective_action": "Site retrained on visit scheduling; window recalculated.",
        })
    # concentrate extra deviations on the struggling sites, plus a few elsewhere
    struggling_subj = subjects[subjects["site_id"].isin(SLOW_SITES)]
    extra = pd.concat([
        struggling_subj.sample(n=min(16, len(struggling_subj)), random_state=SEED),
        subjects.sample(n=10, random_state=SEED),
    ])
    for _, sub in extra.iterrows():
        term, cat = DEVIATION_TYPES[int(rng.integers(1, len(DEVIATION_TYPES)))]
        vi = int(rng.integers(0, 6))
        rows.append({
            "usubjid": sub["usubjid"], "site_id": sub["site_id"], "visitnum": VISIT_SCHEDULE[vi]["visitnum"],
            "visit": VISIT_SCHEDULE[vi]["visit"], "dvterm": term, "dvcat": cat,
            "dvdtc": (pd.Timestamp(sub["enrollment_date"]) + pd.Timedelta(days=int(rng.integers(10, 120)))).date().isoformat(),
            "dvstatus": rng.choice(["Open", "Closed"], p=[0.5, 0.5]),
            "corrective_action": "CAPA logged; monitored at next visit.",
        })
    return pd.DataFrame(rows)


def build_queries(rng, forms: pd.DataFrame, labs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    data_cut = pd.Timestamp(STUDY["data_cut"])
    qid = 1000
    missing = forms[forms["completed"] == 0]
    for _, r in missing.sample(frac=0.72, random_state=SEED).iterrows():
        qid += 1
        reason_cd, reason_tx = QUERY_REASONS[0]
        opened = data_cut - pd.Timedelta(days=int(rng.integers(1, 90)))
        rows.append(_query_row(qid, r["usubjid"], r["site_id"], r["visit"], r["form_name"],
                               reason_cd, reason_tx, opened, data_cut, rng))
    oor = labs[(labs["result"] > labs["ref_hi"]) | (labs["result"] < labs["ref_lo"])]
    for _, r in oor.iterrows():
        qid += 1
        reason_cd, reason_tx = QUERY_REASONS[1]
        opened = data_cut - pd.Timedelta(days=int(rng.integers(1, 70)))
        rows.append(_query_row(qid, r["usubjid"], r["site_id"], r["visit"], "Laboratory",
                               reason_cd, reason_tx, opened, data_cut, rng, field=r["testcd"]))
    return pd.DataFrame(rows)


def _query_row(qid, usubjid, site_id, visit, form, reason_cd, reason_tx, opened, data_cut, rng, field=""):
    age = (data_cut - opened).days
    if age > 45:
        status = rng.choice(["Open", "Answered"], p=[0.6, 0.4])
    else:
        status = rng.choice(["Open", "Answered", "Closed"], p=[0.4, 0.3, 0.3])
    sev = "Major" if reason_cd in ("out of range", "implausible value") else rng.choice(["Minor", "Moderate"])
    return {
        "query_id": f"Q-{qid}", "usubjid": usubjid, "site_id": int(site_id), "form": form,
        "field": field, "reason_code": reason_cd, "reason_text": reason_tx, "severity": sev,
        "status": status, "opened_date": opened.date().isoformat(), "age_days": int(age),
    }


def generate_all(outdir: str = "data/raw") -> dict:
    import os
    os.makedirs(outdir, exist_ok=True)
    rng = _rng()
    sites = build_sites(rng)
    subjects = build_subjects(rng, sites)
    visits, forms, labs = build_visits_forms_labs(rng, subjects)
    aes = build_adverse_events(rng, subjects)
    devs = build_deviations(rng, subjects, visits)
    queries = build_queries(rng, forms, labs)
    tables = {
        "sites": sites, "subjects": subjects, "visits": visits, "forms": forms,
        "labs": labs, "adverse_events": aes, "deviations": devs, "queries": queries,
    }
    for name, df in tables.items():
        df.to_csv(f"{outdir}/{name}.csv", index=False)
    return tables


if __name__ == "__main__":
    t = generate_all()
    for k, v in t.items():
        print(f"{k:16s} {len(v):6d} rows")
