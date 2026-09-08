"""Study-level constants for the TrialFlow synthetic Phase II trial.

Everything the generator and the engines need to agree on lives here so the
numbers stay consistent across data generation, the risk engine and the docs.
"""

SEED = 42

STUDY = {
    "studyid": "TF-201",
    "title": "A Phase II, Randomised, Double-Blind Study of TF-Compound vs Placebo",
    "phase": "Phase II",
    "indication": "Moderate plaque psoriasis",
    "target_enrollment": 900,
    "planned_sites": 40,
    "arms": ["TF-Compound 150mg", "Placebo"],
    "first_patient_in": "2025-02-03",
    "data_cut": "2026-09-05",
}

# Visit schedule. day is the protocol target day from randomisation; the window
# is the allowed range. A visit dated outside [day+lo, day+hi] is a deviation.
VISIT_SCHEDULE = [
    {"visitnum": 1, "visit": "Screening",  "day": -14, "win_lo": -28, "win_hi": -1},
    {"visitnum": 2, "visit": "Baseline",   "day": 0,   "win_lo": 0,   "win_hi": 0},
    {"visitnum": 3, "visit": "Week 4",     "day": 28,  "win_lo": -3,  "win_hi": 3},
    {"visitnum": 4, "visit": "Week 8",     "day": 56,  "win_lo": -3,  "win_hi": 3},
    {"visitnum": 5, "visit": "Week 12",    "day": 84,  "win_lo": -5,  "win_hi": 5},
    {"visitnum": 6, "visit": "Week 16 EOT", "day": 112, "win_lo": -5,  "win_hi": 7},
]

# Required forms per visit, used by the data-quality completeness check.
REQUIRED_FORMS = {
    "Screening": ["Demographics", "Inclusion/Exclusion", "Medical History", "Informed Consent", "Laboratory"],
    "Baseline": ["Vital Signs", "PASI Score", "Laboratory", "Randomisation"],
    "Week 4": ["Vital Signs", "PASI Score", "Adverse Events"],
    "Week 8": ["Vital Signs", "PASI Score", "Laboratory", "Adverse Events"],
    "Week 12": ["Vital Signs", "PASI Score", "Adverse Events"],
    "Week 16 EOT": ["Vital Signs", "PASI Score", "Laboratory", "Adverse Events", "End of Treatment"],
}

COUNTRIES = [
    ("Ireland", 6), ("Germany", 7), ("United Kingdom", 6), ("Spain", 5),
    ("Poland", 5), ("France", 4), ("Italy", 4), ("Netherlands", 3),
]

# Reference ranges for the lab / vitals out-of-range data-quality rule.
REFERENCE_RANGES = {
    "SYSBP": (90, 160, "mmHg"),
    "DIABP": (50, 100, "mmHg"),
    "PULSE": (45, 110, "beats/min"),
    "ALT":   (7, 56, "U/L"),
    "HGB":   (11.0, 17.5, "g/dL"),
}

# Risk-engine weights. Site risk is a 0-100 score; higher is worse.
SITE_RISK_WEIGHTS = {
    "recruitment_gap": 0.30,     # how far below enrolment target
    "query_rate": 0.25,          # open queries per enrolled subject
    "deviation_rate": 0.25,      # protocol deviations per enrolled subject
    "data_incompleteness": 0.20, # 1 - form completeness
}
SITE_RISK_BANDS = {"green": 30, "amber": 56}  # < green = ok, < amber = watch, else act

# Trial-health score (0-100, higher is better) component weights.
TRIAL_HEALTH_WEIGHTS = {
    "recruitment": 0.25,
    "data_completeness": 0.25,
    "query_backlog": 0.15,
    "site_performance": 0.20,
    "protocol_deviations": 0.15,
}
