#!/usr/bin/env python3
"""Independent exact verifier for the positive-mixed Phi2 component-jet export."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import generate_berger_global_detector_rods as rods


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_POSITIVE_MIXED_PHI2_LOCAL_COMPONENT_JET_EXPORT.json"
PAYLOAD = P / "certificates/BERGER_POSITIVE_MIXED_PHI2_LOCAL_COMPONENT_JET_EXPORT_PAYLOAD.json"
SCHEMA = P / "schema/berger-positive-mixed-phi2-local-component-jet-export-v1.schema.json"
PAIRS = ((0, 0), (0, 1), (0, 2), (0, 3), (1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3))
X0, X1, X2, X3 = sp.symbols("x0 x1 x2 x3", real=True)
BASIS = (
    sp.S.One,
    X0**2 - X3**2,
    X1**2 - X3**2,
    X2**2 - X3**2,
    X0 * X1,
    X0 * X2,
    X0 * X3,
    X1 * X2,
    X1 * X3,
    X2 * X3,
)
U = sp.Rational(3, 20) * sp.sqrt(10)
V = sp.Rational(2, 3) * sp.sqrt(10)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def coefficient(record: dict[str, Any]) -> sp.Expr:
    q, s = record["rational"], record["sqrt10"]
    return sp.Rational(q["numerator"], q["denominator"]) + sp.sqrt(10) * sp.Rational(s["numerator"], s["denominator"])


def component_functions(replacement: dict[str, Any]) -> dict[str, sp.Expr]:
    sparse = {int(index): sp.sympify(value) for index, value in replacement["background_equation"]["Phi2_sparse"]}
    matrix = sp.zeros(10, 10)
    for component in range(10):
        for harmonic in range(10):
            matrix[component, harmonic] = sparse.get(10 * component + harmonic, 0)
    return {
        f"Phi2_{left}{right}": sp.expand(sum(matrix[row, col] * BASIS[col] for col in range(10)))
        for row, (left, right) in enumerate(PAIRS)
    }


def pbw_derivative(value: sp.Expr, multiindex: tuple[int, int, int, int]) -> sp.Expr:
    if multiindex[0]:
        return sp.S.Zero
    result = value
    for axis, count in enumerate(multiindex[1:]):
        for _ in range(count):
            result = rods._frame_derivative(result, axis)
    return sp.expand(result)


def connection() -> dict[tuple[int, int, int], sp.Expr]:
    structure: dict[tuple[int, int, int], sp.Expr] = defaultdict(lambda: sp.S.Zero)
    for left, right, out, value in ((1, 2, 3, U), (2, 3, 1, V), (3, 1, 2, V)):
        structure[left, right, out] = value
        structure[right, left, out] = -value
    answer = {}
    for direction in range(4):
        for index in range(4):
            for out in range(4):
                value = sp.factor(
                    (structure[direction, index, out] - structure[index, out, direction] + structure[out, direction, index]) / 2
                )
                if value:
                    answer[direction, index, out] = value
    return answer


def covariant_jets(components: dict[str, sp.Expr], maximum_order: int) -> list[dict[str, Any]]:
    gamma = connection()
    current = {
        (left, right): components[f"Phi2_{min(left, right)}{max(left, right)}"]
        for left in range(4) for right in range(4)
    }
    records = [
        {"indices": list(indices), "value": sp.sstr(value)}
        for indices, value in sorted(current.items()) if value != 0
    ]
    for _ in range(maximum_order):
        following: dict[tuple[int, ...], sp.Expr] = {}
        for direction in range(4):
            derivative_multiindex = tuple(int(axis == direction) for axis in range(4))
            for indices, value in current.items():
                total = pbw_derivative(value, derivative_multiindex)
                for slot, index in enumerate(indices):
                    for out in range(4):
                        changed = indices[:slot] + (out,) + indices[slot + 1:]
                        total -= gamma.get((direction, index, out), 0) * current.get(changed, sp.S.Zero)
                total = sp.factor(total)
                if total:
                    following[(direction,) + indices] = total
        current = following
        records.extend(
            {"indices": list(indices), "value": sp.sstr(value)}
            for indices, value in sorted(current.items())
        )
    return records


def evaluate_universal_terms(old: dict[str, Any], components: dict[str, sp.Expr]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    blocks = []
    dependent = 0
    vanished = 0
    unaffected = []
    for source_block in old["blocks"]:
        entries = []
        for source_entry in source_block["entries"]:
            totals: dict[tuple[str, tuple[int, ...]], sp.Expr] = defaultdict(lambda: sp.S.Zero)
            origins: dict[tuple[str, tuple[int, ...]], list[dict[str, Any]]] = defaultdict(list)
            for term in source_entry["terms"]:
                phi_factors = [factor for factor in term["coefficient_factors"] if factor["name"].startswith("Phi2_")]
                if not phi_factors:
                    unaffected.append(term)
                    continue
                assert len(phi_factors) == 1
                dependent += 1
                phi = phi_factors[0]
                value = pbw_derivative(components[phi["name"]], tuple(phi["spacetime_multiindex"]))
                if value == 0:
                    vanished += 1
                    continue
                remaining = [factor for factor in term["coefficient_factors"] if factor is not phi]
                key = (json.dumps(remaining, sort_keys=True, separators=(",", ":")), tuple(term["input_pbw_multiindex"]))
                totals[key] += coefficient(term["coefficient"]) * value
                origins[key].append({"name": phi["name"], "multiindex": phi["spacetime_multiindex"], "value": sp.sstr(value)})
            normalized = []
            for key in sorted(totals):
                value = sp.factor(totals[key])
                if value == 0:
                    continue
                factors, input_pbw = key
                normalized.append({
                    "coefficient": sp.sstr(value),
                    "coefficient_factors": json.loads(factors),
                    "input_pbw_multiindex": list(input_pbw),
                    "source_phi2_jets": origins[key],
                })
            if normalized:
                entries.append({"input_row": source_entry["input_row"], "output_row": source_entry["output_row"], "terms": normalized})
        if entries:
            blocks.append({"id": source_block["id"], "entries": entries})
    audit = {
        "dependent_source_term_count": dependent,
        "vanishing_after_evaluation_count": vanished,
        "surviving_normalized_term_count": sum(len(entry["terms"]) for block in blocks for entry in block["entries"]),
        "unaffected_source_term_count": len(unaffected),
        "unaffected_terms_canonical_sha256": canonical_sha256(unaffected),
    }
    return blocks, audit


def main() -> int:
    certificate = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    assert sha256(PAYLOAD) == certificate["payload_ref"]["sha256"]
    for ref in certificate["dependency_refs"].values():
        assert sha256(ROOT / ref["path"]) == ref["sha256"]

    refs = certificate["dependency_refs"]
    replacement = json.loads((ROOT / refs["replacement_payload"]["path"]).read_text())
    old = json.loads((ROOT / refs["old_108_payload"]["path"]).read_text())
    profile = json.loads((ROOT / refs["profile_variation"]["path"]).read_text())
    components = component_functions(replacement)
    expected = {
        "Phi2_00": sp.Rational(428, 567),
        "Phi2_11": -sp.Rational(29, 21),
        "Phi2_22": -sp.Rational(29, 21),
        "Phi2_33": -sp.Rational(6, 7),
    }
    assert {name: value for name, value in components.items() if value != 0} == expected
    assert payload["retained_to_local_map"]["reconstructed_nonzero_components"] == {name: sp.sstr(value) for name, value in expected.items()}

    consumed = sorted({
        (factor["name"], tuple(factor["spacetime_multiindex"]))
        for block in old["blocks"] for entry in block["entries"]
        for term in entry["terms"] for factor in term["coefficient_factors"]
        if factor["name"].startswith("Phi2_")
    })
    exported_jets = {(item["name"], tuple(item["spacetime_multiindex"])): sp.sympify(item["value"]) for item in payload["retained_to_local_map"]["consumed_component_jets"]}
    assert set(exported_jets) == set(consumed)
    assert all(exported_jets[key] == pbw_derivative(components[key[0]], key[1]) for key in consumed)

    maximum_order = max(sum(index) for _, index in consumed)
    direct_covariant = covariant_jets(components, maximum_order)
    assert canonical_sha256(direct_covariant) == payload["connection_and_covariant_jets"]["canonical_sha256"]
    direct_connection = [
        {"direction": a, "input": b, "output": c, "value": sp.sstr(value)}
        for (a, b, c), value in sorted(connection().items())
    ]
    assert direct_connection == payload["connection_and_covariant_jets"]["nonzero_connection_coefficients"]

    blocks, audit = evaluate_universal_terms(old, components)
    assert canonical_sha256(blocks) == payload["evaluated_nonrod_D3S"]["blocks_canonical_sha256"]
    assert audit == {key: payload["evaluated_nonrod_D3S"][key] for key in audit}

    # Method-distinct decisive rail: vary the normalized transverse detector
    # density directly, rather than replaying the universal D3S differentiator.
    assert profile["normalization_rule"]["event_specialization"]["d1_plus_sigma_a"] == "-Phi2_00/2"
    direct_density_variation = -expected["Phi2_00"] / 2
    assert direct_density_variation == sp.Rational(-214, 567)
    assert sp.sympify(payload["independent_tensor_variation_anchor"]["direct_value"]) == direct_density_variation
    assert payload["independent_tensor_variation_anchor"]["agreement_defect_count"] == 0
    assert payload["disposition"]["replacement_112_complete_executable_q1"] == "NO_CERTIFIED_MAP"
    print("BERGER_POSITIVE_MIXED_PHI2_LOCAL_COMPONENT_JET_EXPORT independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
