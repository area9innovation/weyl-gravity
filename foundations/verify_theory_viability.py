#!/usr/bin/env python3
"""Independent fail-closed verifier for theory-viability assessment v1."""
from __future__ import annotations

from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "foundations/site/data.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_THEORY_VIABILITY_ASSESSMENT_V1.json"
SCHEMA = ROOT / "foundations/schema/foundational-theory-viability-assessment-v1.schema.json"
REPORT = ROOT / "foundations/reports/theory-viability-assessment-v1.md"
SITE_JSON = ROOT / "foundations/site/viability.json"
SITE_JS = ROOT / "foundations/site/viability.js"
DIRECT = {"LOCAL_RESULT", "LITERATURE_RESULT"}
RANK = {"NOT_MAPPED": 0, "REVIEWED_GAP": 1, "PRIORITY_GAP": 1, "PIECES_ONLY": 2, "LOCAL_RESULT": 3, "LITERATURE_RESULT": 3}
DEFAULT_GATE = [
    "KINEMATICS_OBSERVABLES",
    "STATE_EXISTENCE",
    "STATE_REPRESENTATION",
    "PROBABILITY_RULE",
    "PHYSICAL_STATE_SELECTION",
    "GENERATOR_SPECTRAL_DYNAMICS",
    "EVOLUTION_WELLPOSEDNESS",
    "CAUSAL_PROPAGATION_GREEN",
    "INTERACTION_CONSTRUCTION",
    "RECONSTRUCTION_LIMITS",
]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def metrics(profile: dict[str, Any]) -> tuple[int, int, int, int]:
    return (
        profile["default_gate"]["direct"],
        profile["default_gate"]["assessed"],
        profile["direct"],
        RANK[profile["reconstruction_status"]],
    )


def dominates(left: dict[str, Any], right: dict[str, Any]) -> bool:
    a, b = metrics(left), metrics(right)
    return all(x >= y for x, y in zip(a, b)) and any(x > y for x, y in zip(a, b))


def verify(*, value: dict[str, Any] | None = None) -> tuple[list[str], list[str]]:
    atlas, result, schema = load(ATLAS), (load(RESULT) if value is None else value), load(SCHEMA)
    errors: list[str] = []
    checks: list[str] = []
    errors.extend("schema " + item.message for item in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(result))
    checks.append("Draft 2020-12 assessment schema")
    if digest(result) != result.get("canonical_digest"):
        errors.append("assessment canonical digest")
    if result.get("source_atlas_digest") != atlas.get("canonical_digest"):
        errors.append("source atlas digest")
    checks.append("content-addressed assessment and atlas source")

    axes = {axis["id"]: [item["id"] for item in axis["keys"]] for axis in atlas["axes"]}
    foundations, carriers, obligations = axes["FOUNDATION"], axes["CARRIER"], axes["REFINED_OBLIGATION"]
    cells = {(cell["foundation"], cell["carrier"], cell["obligation"]): cell for cell in atlas["cells"]}
    profiles = {(item["foundation"], item["carrier"]): item for item in result.get("profiles", [])}
    if len(profiles) != 36 or set(profiles) != set(itertools.product(foundations, carriers)):
        errors.append("36-profile Cartesian closure")
    for foundation, carrier in itertools.product(foundations, carriers):
        profile = profiles.get((foundation, carrier), {})
        profile_cells = [cells[(foundation, carrier, obligation)] for obligation in obligations]
        gate_cells = [cells[(foundation, carrier, obligation)] for obligation in DEFAULT_GATE]
        expected_counts = Counter(cell["status"] for cell in profile_cells)
        if any(profile.get("counts", {}).get(status) != expected_counts[status] for status in RANK):
            errors.append(f"profile status counts {foundation}/{carrier}")
        if profile.get("direct") != sum(cell["status"] in DIRECT for cell in profile_cells):
            errors.append(f"profile direct count {foundation}/{carrier}")
        if profile.get("assessed") != sum(cell["status"] != "NOT_MAPPED" for cell in profile_cells):
            errors.append(f"profile assessed count {foundation}/{carrier}")
        gate = profile.get("default_gate", {})
        if gate.get("direct") != sum(cell["status"] in DIRECT for cell in gate_cells) or gate.get("assessed") != sum(cell["status"] != "NOT_MAPPED" for cell in gate_cells):
            errors.append(f"default gate count {foundation}/{carrier}")
        expected_blockers = [
            {"obligation": cell["obligation"], "status": cell["status"]}
            for cell in gate_cells if cell["status"] not in DIRECT
        ]
        if gate.get("blockers") != expected_blockers or gate.get("complete_direct") != (not expected_blockers):
            errors.append(f"default gate blockers {foundation}/{carrier}")
    checks.append("independent 36-profile coverage and blocker recomputation")

    frontier = {
        key for key, profile in profiles.items()
        if not any(other_key != key and dominates(other, profile) for other_key, other in profiles.items())
    }
    expected_frontier = {
        ("CLASSICAL_STANDARD", "HILBERT_OPERATOR"),
        ("CLASSICAL_STANDARD", "ALGEBRAIC_CSTAR"),
        ("FINITE_DISCRETE", "FINITE_EXACT"),
        ("FINITE_DISCRETE", "HILBERT_OPERATOR"),
    }
    if frontier != expected_frontier or {key for key, profile in profiles.items() if profile.get("pareto_default")} != frontier:
        errors.append("default Pareto frontier")
    if any(profile.get("default_gate", {}).get("complete_direct") for profile in profiles.values()):
        errors.append("unexpected complete default-gate profile")
    checks.append("non-scalar default Pareto navigation and no-complete-profile result")

    envelopes = {item["foundation"]: item for item in result.get("carrier_envelopes", [])}
    if set(envelopes) != set(foundations):
        errors.append("six foundation envelopes")
    for foundation in foundations:
        subset_rows = []
        for size in range(1, len(carriers) + 1):
            for subset in itertools.combinations(carriers, size):
                direct = sum(
                    max(RANK[cells[(foundation, carrier, obligation)]["status"]] for carrier in subset) == 3
                    for obligation in obligations
                )
                subset_rows.append((direct, size, subset))
        maximum = max(item[0] for item in subset_rows)
        minimum_size = min(item[1] for item in subset_rows if item[0] == maximum)
        minimal = [list(item[2]) for item in subset_rows if item[0] == maximum and item[1] == minimum_size]
        envelope = envelopes.get(foundation, {})
        if envelope.get("maximum_direct_obligations") != maximum or envelope.get("minimum_carriers_for_that_maximum") != minimum_size or envelope.get("minimal_maximum_subsets") != minimal:
            errors.append(f"carrier envelope optimum {foundation}")
        if envelope.get("composition_status") != "NOT_ASSESSED":
            errors.append(f"carrier envelope composition promotion {foundation}")
    checks.append("independent exhaustive 378-portfolio envelope audit")

    rails = {item.get("id"): item.get("status") for item in result.get("global_rails", [])}
    if rails != {
        "OBLIGATION_COVERAGE": "COMPUTED_FROM_ATLAS",
        "CROSS_OBLIGATION_COMPOSITION": "PARTIALLY_ASSESSED",
        "EMPIRICAL_AGREEMENT": "NOT_IN_CURRENT_SCHEMA",
    }:
        errors.append("three-rail separation")
    flags = result.get("claim_flags", {})
    for key in ("all_36_single_carrier_profiles_computed", "carrier_portfolio_envelopes_computed", "coverage_and_empirical_agreement_separated"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("complete_observationally_valid_theory_identified", "cross_cell_composability_established", "empirical_agreement_assessed", "scalar_winner_score_defined"):
        if flags.get(key) is not False:
            errors.append("fail-closed flag " + key)
    checks.append("composition, observation, and scalar-score boundaries")

    if value is None and SITE_JSON.read_bytes() != RESULT.read_bytes():
        errors.append("site/result assessment parity")
    expected_js = b"window.THEORY_VIABILITY_DATA = " + SITE_JSON.read_bytes().rstrip() + b";\n"
    if SITE_JS.read_bytes() != expected_js:
        errors.append("offline assessment assignment")
    html = (ROOT / "foundations/site/index.html").read_text()
    app = (ROOT / "foundations/site/app.js").read_text()
    for token in ("Theory profiles", "viabilityView", "viability.js", "Coverage readiness map", "Coverage envelope, not a composed theory", "No complete observationally validated theory is certified", "EMPIRICAL_AGREEMENT", "paretoProfiles"):
        if token not in html + app + SITE_JS.read_text():
            errors.append("interface token " + token)
    checks.append("offline theory-profile interface and result parity")

    report = REPORT.read_text()
    for token in ("36", "six carrier-portfolio", "no single profile", "Pareto", "partially assessed", "not in the current schema", "not a composition theorem", "does not establish"):
        if token not in report:
            errors.append("report token " + token)
    checks.append("human-readable outcome and boundaries")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_THEORY_VIABILITY_ASSESSMENT_V1: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
