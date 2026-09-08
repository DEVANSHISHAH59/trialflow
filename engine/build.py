"""TrialFlow build pipeline.

    raw EDC tables  ->  SQLite warehouse  ->  SQL views  ->  quality + risk engines
                    ->  SDTM domains      ->  web/data/trialflow.json

Run from the project root:  python engine/build.py
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd  # noqa: E402

import analytics  # noqa: E402
import data_quality  # noqa: E402
import risk_engine  # noqa: E402
import sdtm_mapping  # noqa: E402
from config import STUDY  # noqa: E402
from generate_data import generate_all  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "warehouse", "trialflow.db")
SQL_DIR = os.path.join(ROOT, "sql")
SQL_OUT = os.path.join(ROOT, "docs", "sql-output")
SDTM_DIR = os.path.join(ROOT, "sdtm")
WEB_DATA = os.path.join(ROOT, "web", "data", "trialflow.json")


def load_warehouse(tables: dict) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    for name, df in tables.items():
        df.to_sql(name, conn, index=False, if_exists="replace")
    conn.commit()
    return conn


def run_sql_files(conn: sqlite3.Connection) -> dict:
    os.makedirs(SQL_OUT, exist_ok=True)
    results = {}
    for fname in sorted(os.listdir(SQL_DIR)):
        if not fname.endswith(".sql"):
            continue
        with open(os.path.join(SQL_DIR, fname), "r", encoding="utf-8") as fh:
            sql = fh.read()
        # execute the final SELECT for output; run any preceding statements too
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        cur = conn.cursor()
        for stmt in statements[:-1]:
            cur.execute(stmt)
        df = pd.read_sql_query(statements[-1], conn)
        out_path = os.path.join(SQL_OUT, fname.replace(".sql", ".csv"))
        df.to_csv(out_path, index=False)
        results[fname] = df
        print(f"  sql/{fname:24s} -> {len(df):4d} rows -> docs/sql-output/{fname.replace('.sql', '.csv')}")
    return results


def write_sdtm(domains: dict) -> None:
    os.makedirs(SDTM_DIR, exist_ok=True)
    for name, df in domains.items():
        df.to_csv(os.path.join(SDTM_DIR, f"{name}.csv"), index=False)
        print(f"  sdtm/{name}.csv{'':10s} {len(df):5d} rows")


def json_safe(obj):
    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [json_safe(v) for v in obj]
    if isinstance(obj, float):
        return round(obj, 3)
    if pd.isna(obj) if not isinstance(obj, (list, dict)) else False:
        return None
    return obj


def main():
    os.chdir(ROOT)
    print("1. generating synthetic EDC data ...")
    tables = generate_all(os.path.join(ROOT, "data", "raw"))
    for k, v in tables.items():
        print(f"  {k:16s} {len(v):6d} rows")

    print("2. loading SQLite warehouse ...")
    conn = load_warehouse(tables)

    print("3. running SQL views ...")
    sql_results = run_sql_files(conn)

    print("4. data-quality engine ...")
    dq = data_quality.run(tables)
    print(f"  score {dq['score']}%   findings {dq['flagged']}")

    print("5. risk engine ...")
    sites_scored = risk_engine.site_table(tables)
    health = risk_engine.trial_health(tables, sites_scored)
    print(f"  trial health {health['score']}/100 ({health['status']})   "
          f"red sites {(sites_scored['risk_band'] == 'red').sum()}   "
          f"amber {(sites_scored['risk_band'] == 'amber').sum()}")

    print("6. SDTM mapping ...")
    domains = sdtm_mapping.build_all(tables)
    write_sdtm(domains)

    print("7. assembling web/data/trialflow.json ...")
    payload = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "disclaimer": "All data is synthetic. No real patients, sites, investigators or "
                      "products are represented. SDTM mapping is a simplified demonstration model.",
        "overview": analytics.executive_kpis(tables, health, dq, sites_scored),
        "recruitment": analytics.recruitment_series(tables),
        "enrollment_by_country": analytics.enrollment_by_country(tables),
        "sites": json.loads(sites_scored.to_json(orient="records")),
        "data_quality": {
            "score": dq["score"], "records_to_review": dq["records_to_review"],
            "evaluable_points": dq["evaluable_points"],
            "by_rule": dq["by_rule"], "by_site": dq["by_site"],
            "sample_findings": json.loads(dq["findings"].head(40).to_json(orient="records")),
        },
        "deviations": analytics.deviation_breakdowns(tables),
        "adverse_events": analytics.ae_breakdowns(tables),
        "patient_journey": analytics.example_patient_journey(tables),
        "sdtm": {
            name: {
                "rows": int(len(df)),
                "columns": list(df.columns),
                "sample": json.loads(df.head(8).to_json(orient="records")),
            } for name, df in domains.items()
        },
        "copilot": analytics.risk_copilot(tables, health, dq, sites_scored),
        "sql_catalog": [
            {"file": f"sql/{k}", "rows": int(len(v)), "columns": list(v.columns)}
            for k, v in sql_results.items()
        ],
    }
    os.makedirs(os.path.dirname(WEB_DATA), exist_ok=True)
    with open(WEB_DATA, "w", encoding="utf-8") as fh:
        json.dump(json_safe(payload), fh, indent=2, default=str)
    size_kb = os.path.getsize(WEB_DATA) / 1024
    print(f"  wrote {WEB_DATA}  ({size_kb:.0f} KB)")

    conn.close()
    print("done.")


if __name__ == "__main__":
    main()
