"""Simplified CDISC SDTM-aligned mapping.

This is a demonstration model, not a validated SDTM implementation. It maps the
raw EDC tables into four SDTM-style domains (DM, AE, VS, SV) using the variable
names and structure from the SDTM Implementation Guide, so downstream analysis
and any submission-style tooling can read a familiar shape.
"""

from __future__ import annotations

import pandas as pd

from config import STUDY

COUNTRY_ISO = {
    "Ireland": "IRL", "Germany": "DEU", "United Kingdom": "GBR", "Spain": "ESP",
    "Poland": "POL", "France": "FRA", "Italy": "ITA", "Netherlands": "NLD",
}
VS_TESTS = {"SYSBP": "Systolic Blood Pressure", "DIABP": "Diastolic Blood Pressure", "PULSE": "Pulse Rate"}
ARMCD = {"TF-Compound 150mg": "A", "Placebo": "P"}


def dm(subjects: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame({
        "STUDYID": STUDY["studyid"],
        "DOMAIN": "DM",
        "USUBJID": subjects["usubjid"],
        "SUBJID": subjects["usubjid"].str.split("-").str[-1],
        "SITEID": subjects["site_id"].astype(str),
        "RFSTDTC": subjects["enrollment_date"],
        "AGE": subjects["age"],
        "AGEU": "YEARS",
        "SEX": subjects["sex"],
        "COUNTRY": subjects["country"].map(COUNTRY_ISO),
        "ARM": subjects["arm"],
        "ARMCD": subjects["arm"].map(ARMCD),
        "ACTARM": subjects["arm"],
        "DSDECOD": subjects["disposition"],
    })
    return df


def ae(adverse_events: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame({
        "STUDYID": STUDY["studyid"],
        "DOMAIN": "AE",
        "USUBJID": adverse_events["usubjid"],
        "AESEQ": adverse_events["aeseq"],
        "AETERM": adverse_events["aeterm"],
        "AEBODSYS": adverse_events["aebodsys"],
        "AESEV": adverse_events["aesev"].str.upper(),
        "AESER": adverse_events["aeser"],
        "AEREL": adverse_events["aerel"],
        "AESTDTC": adverse_events["aestdtc"],
        "AEENDTC": adverse_events["aeendtc"],
        "AEOUT": adverse_events["aeout"],
    })
    return df


def vs(labs: pd.DataFrame) -> pd.DataFrame:
    v = labs[labs["testcd"].isin(VS_TESTS)].copy()
    df = pd.DataFrame({
        "STUDYID": STUDY["studyid"],
        "DOMAIN": "VS",
        "USUBJID": v["usubjid"],
        "VSTESTCD": v["testcd"],
        "VSTEST": v["testcd"].map(VS_TESTS),
        "VISITNUM": v["visitnum"],
        "VISIT": v["visit"].str.upper(),
        "VSORRES": v["result"],
        "VSORRESU": v["unit"],
        "VSDTC": v["result_date"],
    })
    return df.reset_index(drop=True)


def sv(visits: pd.DataFrame) -> pd.DataFrame:
    s = visits[visits["actual_date"].notna()].copy()
    df = pd.DataFrame({
        "STUDYID": STUDY["studyid"],
        "DOMAIN": "SV",
        "USUBJID": s["usubjid"],
        "VISITNUM": s["visitnum"],
        "VISIT": s["visit"].str.upper(),
        "SVSTDTC": s["actual_date"],
        "SVENDTC": s["actual_date"],
    })
    return df.reset_index(drop=True)


def build_all(tables: dict) -> dict:
    return {
        "DM": dm(tables["subjects"]),
        "AE": ae(tables["adverse_events"]),
        "VS": vs(tables["labs"]),
        "SV": sv(tables["visits"]),
    }
