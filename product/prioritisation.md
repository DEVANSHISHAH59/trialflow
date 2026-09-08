# Prioritisation

## Method

Each candidate item is scored on **value** (impact on the primary users' weekly decisions), **confidence** (how sure we are it will land), **effort** (build cost) and **risk reduction** (does it de-risk a regulated conversation). Priority is `(value x confidence x risk_reduction) / effort`, then adjusted for dependencies.

Bands: **P0** must be in the MVP or the product does not stand up; **P1** makes it credible in a regulated setting; **P2** changes how the team works and depends on P0/P1 being trusted.

## Scored backlog

| ID | Item | Value | Conf | Effort | RiskRed | Priority | Notes |
|---|---|---|---|---|---|---|---|
| TF-001 | Executive overview + Trial Health Score | 5 | 5 | 3 | 4 | **P0** | The reason to open the product |
| TF-002 | Site performance table + site risk score | 5 | 5 | 3 | 4 | **P0** | Primary weekly decision for the ops lead |
| TF-003 | Patient journey / EDC completeness | 4 | 4 | 3 | 3 | **P0** | Primary weekly decision for the data manager |
| TF-004 | Data-quality engine + score | 5 | 5 | 3 | 5 | **P0** | Without it the DQ score is not defensible |
| TF-005 | Protocol Deviation Engine | 4 | 4 | 3 | 5 | **P1** | Needed for the compliance conversation |
| TF-006 | Adverse Event dashboard | 3 | 4 | 2 | 3 | **P1** | High value to the medical monitor, low build |
| TF-007 | Simplified SDTM mapping (DM/AE/VS/SV) | 4 | 3 | 4 | 4 | **P1** | Unlocks standard analysis; scoped to 4 domains |
| TF-008 | Risk scoring v2 (configurable weights/bands) | 3 | 3 | 4 | 2 | **P2** | Only worth it once v1 is trusted |
| TF-009 | Predictive recruitment | 4 | 2 | 5 | 2 | **P2** | High value, low confidence, high effort |
| TF-010 | Automated threshold alerts | 4 | 3 | 3 | 3 | **P2** | Depends on TF-002 and TF-008 |
| TF-011 | Intervention tracking + trend after action | 4 | 3 | 3 | 3 | **P2** | Proves the product changes outcomes |

## Why the MVP is these four

TF-001 to TF-004 are the smallest set where a clinical operations lead and a data manager can each make their main weekly decision from the product alone. Everything else is an enhancement to a working loop, not part of the loop.

## Deliberate cuts from the MVP

| Cut | Why | When it comes back |
|---|---|---|
| Multi-study portfolio view | Doubles data-model and UI cost; no primary persona needs it weekly yet | After single-study adoption is proven |
| Query write-back to an EDC | Needs a validated integration and vendor-specific work | Release 3+, once the query workflow is trusted read-only |
| Site-facing login for coordinators | Access control and support cost; CRAs can relay in the MVP | Release 3 |
| LLM-generated narrative | Determinism first; the rules answer the questions that matter | Copilot v2, clearly bounded, never over medical content |
| Configurable risk weights | Fixed weights are easier to validate and explain first | TF-008 in Release 3 |

## Sequencing constraints

- TF-007 (SDTM) depends on the raw EDC schema from TF-003/TF-004 being stable.
- TF-010 (alerts) depends on TF-002 and TF-008.
- TF-011 (intervention tracking) depends on TF-002 and a place to store actions.
