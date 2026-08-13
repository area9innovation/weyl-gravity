#!/usr/bin/env python3
"""Independent exact checker for the finite-corner Born interface."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1.json"
STATE_SOURCE = ROOT / "foundations/results/FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1.json"
BORN_SOURCE = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_BT_SEMIFINITE_RELATIVE_BORN_WEIGHT_V1.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def transpose(value):
    return tuple(zip(*value))


def product(left, right):
    return tuple(tuple(sum((a * b for a, b in zip(row, column)), Fraction()) for column in transpose(right)) for row in left)


def add(values):
    size = len(values[0])
    return tuple(tuple(sum((value[row][column] for value in values), Fraction()) for column in range(size)) for row in range(size))


def trace(value):
    return sum((value[index][index] for index in range(len(value))), Fraction())


def sharp(value, j):
    return product(product(j, transpose(value)), j)


def canonical_digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if value is None else value
    state = load(STATE_SOURCE)
    born = load(BORN_SOURCE)
    errors: list[str] = []
    checks: list[str] = []
    if result.get("canonical_digest") != canonical_digest(result):
        errors.append("canonical digest")
    inputs = {item.get("path"): item for item in result.get("provenance", {}).get("inputs", [])}
    for relative, item in inputs.items():
        path = ROOT / relative
        if not path.is_file() or item.get("sha256") != sha(path):
            errors.append("input hash " + relative)
    if set(inputs) != {str(STATE_SOURCE.relative_to(ROOT)), str(BORN_SOURCE.relative_to(ROOT)), "notes/bateman-turok-embedding.md"}:
        errors.append("interface provenance closure")
    if state.get("explicit_state_witness", {}).get("corner_state") != "omega_0(T)=<e_0,T e_0>" or state.get("five_link_chain", [None, None])[1].get("status") != "PROVED_BY_EXPLICIT_FORMULA":
        errors.append("state source")
    theorem = born.get("conditional_Born_theorem", {})
    if theorem.get("conditional_weights") != "p_i=Tr_fin(A_i^dagger A_i)/r" or len(theorem.get("hypotheses", [])) != 5:
        errors.append("Born source")
    checks.append("pinned source identities, formulas, and hashes")

    source_audit = result.get("predecessor_source_audit", {})
    independently_audited = []
    for item in born.get("provenance", {}).get("inputs", []):
        actual = sha(ROOT / item["path"])
        independently_audited.append({"path": item["path"], "recorded_sha256": item["sha256"], "actual_sha256": actual, "status": "MATCH" if actual == item["sha256"] else "DRIFT"})
    drift = [item["path"] for item in independently_audited if item["status"] == "DRIFT"]
    if source_audit.get("verifier_status") != "PROVENANCE_DRIFT" or source_audit.get("input_audit") != independently_audited or drift != ["notes/bateman-turok-embedding.md"]:
        errors.append("predecessor drift audit")
    if result.get("proof_authority", {}).get("status") != "INDEPENDENT_REDERIVATION" or len(result.get("proof_authority", {}).get("general_argument", [])) != 3:
        errors.append("independent proof authority")
    checks.append("fail-closed predecessor provenance drift and independent authority")

    interface = result.get("interface", {})
    source = interface.get("source_coordinates", [])
    target = interface.get("target_coordinates", [])
    if interface.get("id") != "STATE_TO_PROBABILITY" or interface.get("status") != "CERTIFIED" or interface.get("relation") != "CONDITIONAL_BRIDGE":
        errors.append("interface identity")
    if source != [{"foundation": "CLASSICAL_STANDARD", "carrier": "ALGEBRAIC_CSTAR", "obligation": "STATE_REPRESENTATION"}]:
        errors.append("source coordinate")
    if target != [{"foundation": "CLASSICAL_STANDARD", "carrier": "KREIN_INDEFINITE", "obligation": "PROBABILITY_RULE"}]:
        errors.append("target coordinate")
    if {item.get("id") for item in result.get("shared_object_ledger", [])} != {"H0", "TAU", "P_IN", "OMEGA_P"} or any(item.get("identity_status") != "IDENTICAL_OBJECT" for item in result.get("shared_object_ledger", [])):
        errors.append("shared object ledger")
    checks.append("typed coordinates and four shared-object identities")

    zero, one = Fraction(), Fraction(1)
    identity = ((one, zero, zero), (zero, one, zero), (zero, zero, one))
    j = ((one, zero, zero), (zero, one, zero), (zero, zero, -one))
    s = ((Fraction(3, 5), Fraction(-4, 5), zero), (Fraction(4, 5), Fraction(3, 5), zero), (zero, zero, one))
    incoming = ((one, zero, zero), (zero, zero, zero), (zero, zero, zero))
    outputs = [
        ((one, zero, zero), (zero, zero, zero), (zero, zero, zero)),
        ((zero, zero, zero), (zero, one, zero), (zero, zero, zero)),
        ((zero, zero, zero), (zero, zero, zero), (zero, zero, one)),
    ]
    if sharp(s, j) != transpose(s) or product(sharp(s, j), s) != identity or add(outputs) != identity:
        errors.append("cross-Krein isometry or output partition")
    processes = [product(product(output, s), incoming) for output in outputs]
    process_effects = [product(sharp(process, j), process) for process in processes]
    event_effects = [product(product(incoming, product(sharp(s, j), product(output, s))), incoming) for output in outputs]
    if process_effects != event_effects:
        errors.append("process/event effect identity")
    r = trace(incoming)
    probabilities = [trace(effect) / r for effect in event_effects]
    recorded = [fraction(item) for item in result.get("exact_witness", {}).get("probabilities", [])]
    if probabilities != [Fraction(9, 25), Fraction(16, 25), Fraction()] or recorded != probabilities:
        errors.append("same-state probability evaluation")
    if any(item < 0 for item in probabilities) or sum(probabilities, Fraction()) != 1 or fraction(result.get("exact_witness", {}).get("probability_sum", {})) != 1:
        errors.append("positivity or normalization")
    checks.append("independent exact effect identity and normalized probabilities")

    j_null = ((zero, one), (one, zero))
    b = ((Fraction(3, 5), zero), (zero, Fraction(3, 5)))
    c = ((zero, Fraction(4, 5)), (zero, zero))
    a = add([b, c])
    weak_traces = {
        "Tr(C^sharp C)": trace(product(sharp(c, j_null), c)),
        "Tr(B^sharp C)": trace(product(sharp(b, j_null), c)),
        "Tr(C^sharp B)": trace(product(sharp(c, j_null), b)),
        "Tr(B^sharp B)": trace(product(sharp(b, j_null), b)),
        "Tr(A^sharp A)": trace(product(sharp(a, j_null), a)),
    }
    recorded_weak = result.get("exact_witness", {}).get("nonzero_weak_null_remainder", {}).get("traces", {})
    if c == ((zero, zero), (zero, zero)) or sharp(c, j_null) != c or list(weak_traces.values()) != [zero, zero, zero, Fraction(18, 25), Fraction(18, 25)] or {key: fraction(value) for key, value in recorded_weak.items()} != weak_traces:
        errors.append("nonzero weak-null remainder")
    checks.append("independent nonzero weak-null exact fixture")

    obligations = {item.get("id"): item.get("status") for item in result.get("proof_obligations", [])}
    if obligations != {
        "SOURCE_STATE_NORMALIZED": "PASS",
        "SHARED_OBJECT_IDENTITY": "PASS",
        "EVENT_MAP_TYPED": "PASS",
        "POSITIVITY": "PASS",
        "NORMALIZATION": "PASS",
        "EXACT_NONTRIVIAL_WITNESS": "PASS",
        "NONZERO_WEAK_NULL_REMAINDER": "PASS",
    }:
        errors.append("proof obligation closure")
    flags = result.get("claim_flags", {})
    for name in ("cross_cell_interface_certified", "same_corner_state_used_on_both_sides", "event_effect_map_constructed", "conditional_probabilities_nonnegative", "conditional_probabilities_normalized", "interface_independent_rederivation_passed", "predecessor_note_only_provenance_drift_recorded"):
        if flags.get(name) is not True:
            errors.append("positive flag " + name)
    for name in ("legacy_semifinite_source_verifier_passed", "arbitrary_krein_process_probability_rule", "physical_thermodynamic_state_selected", "all_order_bt_probability_constructed", "lorentzian_claim"):
        if flags.get(name) is not False:
            errors.append("boundary flag " + name)
    checks.append("seven proof obligations and fail-closed claim flags")
    return errors, {"checks": checks, "probabilities": [str(item) for item in probabilities], "sum": str(sum(probabilities, Fraction())), "digest": canonical_digest(result)}


def main() -> int:
    errors, summary = check()
    print("FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1: " + ("PASS" if not errors else "FAIL"))
    for item in summary["checks"] if not errors else errors:
        print("  - " + item)
    if not errors:
        print("  - exact probabilities: " + ", ".join(summary["probabilities"]) + "; sum=" + summary["sum"])
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
