#!/usr/bin/env python3
"""Independent structural checker for the normally-hyperbolic factor atlas."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1.json"
LEDGER = ROOT / "foundations/literature-causal-green-atlas-v1.json"
CUBE = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V2.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def digest(result: dict[str, Any]) -> str:
    payload = {key: result[key] for key in ("dependency_chain", "framework_findings", "cell_actions", "evidence_overlays", "bounded_search")}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check(result: dict[str, Any] | None = None, ledger: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if result is None else result
    ledger = load(LEDGER) if ledger is None else ledger
    cube = load(CUBE)
    errors: list[str] = []
    sources = {x.get("id"): x for x in ledger.get("entries", [])}
    expected_sources = {"baer-2015", "muehlhoff-2010", "selivanova-selivanov-2013", "selivanova-selivanov-2018", "kostrykin-potthoff-schrader-2011", "nachtergaele-raz-schlein-sims-2007"}
    if set(sources) != expected_sources:
        errors.append("source ID closure")
    if any(x.get("source_kind") != "PRIMARY_RESEARCH" or x.get("artifact", {}).get("status") != "CONTENT_PINNED" or len(x.get("artifact", {}).get("sha256", "")) != 64 for x in sources.values()):
        errors.append("content-pin closure")
    expected_stages = {"CODED_GEOMETRY", "OPERATOR_DATA", "ENERGY_ESTIMATE", "CAUCHY_EXISTENCE", "UNIQUENESS", "CONTINUITY", "FINITE_PROPAGATION", "GREEN_MAPS", "DISTRIBUTIONAL_EXTENSION"}
    if {x.get("id") for x in result.get("dependency_chain", [])} != expected_stages:
        errors.append("dependency-stage closure")
    frameworks = {x.get("framework"): x for x in result.get("framework_findings", [])}
    expected_frameworks = {"CLASSICAL_STANDARD", "COMPUTABLE_TTE", "BISHOP_CONSTRUCTIVE", "REVERSE_MATHEMATICS", "ZF_WITHOUT_COUNTABLE_CHOICE", "FINITE_OR_DISCRETE"}
    if set(frameworks) != expected_frameworks or any(not x.get("does_not_establish") for x in frameworks.values()):
        errors.append("framework boundary closure")
    known_evidence = expected_sources | {"weihrauch-zhong-2002", "brown-simpson-1986", "humphreys-simpson-1996", "humphreys-simpson-1999", "brattka-2008", "blackadar-farah-karagila-2026", "FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1", "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1"}
    used = {e for section in (result.get("framework_findings", []), result.get("cell_actions", []), result.get("evidence_overlays", [])) for item in section for e in item.get("evidence", [])}
    if not used <= known_evidence:
        errors.append("evidence reference closure")
    cube_by = {"|".join(x[k] for k in ("foundation", "carrier", "obligation")): x for x in cube["cells"]}
    actions = result.get("cell_actions", [])
    if len(actions) != 9 or len({x.get("coordinate") for x in actions}) != 9:
        errors.append("nine status-changing actions")
    for action in actions:
        source = cube_by.get(action.get("coordinate"), {})
        if source.get("status") != action.get("old") or action.get("new") not in {"LITERATURE_RESULT", "LOCAL_RESULT", "PIECES_ONLY", "PRIORITY_GAP", "NOT_MAPPED"}:
            errors.append("cell action " + str(action.get("coordinate")))
    overlays = result.get("evidence_overlays", [])
    if len(overlays) != 5 or len({x.get("coordinate") for x in overlays}) != 5 or any(x.get("coordinate") not in cube_by for x in overlays):
        errors.append("five evidence overlays")
    calculated = digest(result)
    if calculated != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    search = result.get("bounded_search", {})
    if search.get("included_new_records") != 6 or search.get("screened_primary_records") != 13 or "never" not in search.get("negative_finding_rule", ""):
        errors.append("bounded-search boundary")
    return errors, {"digest": calculated, "sources": len(sources), "dependency_stages": len(result.get("dependency_chain", [])), "frameworks": len(frameworks), "cell_actions": len(actions), "evidence_overlays": len(overlays)}


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
