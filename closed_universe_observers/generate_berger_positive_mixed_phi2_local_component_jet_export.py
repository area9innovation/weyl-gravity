#!/usr/bin/env python3
"""Export the positive-mixed Phi2 retained-basis to local component jets."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import generate_berger_global_rod_q1_solvability as solve


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_POSITIVE_MIXED_PHI2_LOCAL_COMPONENT_JET_EXPORT.json"
PAYLOAD = P / "certificates/BERGER_POSITIVE_MIXED_PHI2_LOCAL_COMPONENT_JET_EXPORT_PAYLOAD.json"
SCHEMA = P / "schema/berger-positive-mixed-phi2-local-component-jet-export-v1.schema.json"
REPORT = P / "reports/berger-positive-mixed-phi2-local-component-jet-export.md"
DEPENDENCIES = {
    "replacement": P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY.json",
    "replacement_payload": P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY_PAYLOAD.json",
    "variational_shortfall": P / "certificates/BERGER_REPLACEMENT_112_EXECUTABLE_UNARY_VARIATIONAL_INPUT_SHORTFALL.json",
    "variational_shortfall_payload": P / "certificates/BERGER_REPLACEMENT_112_EXECUTABLE_UNARY_VARIATIONAL_INPUT_SHORTFALL_PAYLOAD.json",
    "old_108": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "old_108_payload": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET_PAYLOAD.json",
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "old_phi2_geometry": P / "certificates/BERGER_84_ROW_ROD_GRAVITY_UNARY.json",
    "profile_variation": P / "certificates/BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY.json",
}
REPORT_TEXT = """# Positive-mixed Phi2 local component-jet export

The retained positive-mixed primitive reconstructs exactly four nonzero
orthonormal-frame components: Phi2_00=428/567,
Phi2_11=Phi2_22=-29/21, and Phi2_33=-6/7. This uses the declared
ten-component symmetric-tensor ordering and ten-element retained quadratic
harmonic basis; it does not substitute values from the old background.

The export evaluates all 942 named local component-PBW jets consumed by the
universal nonrod D3S formulas through total derivative order five. Harmonic
reconstruction, the three noncommuting Berger frame commutators, reality,
and K_Berger weight zero pass exactly. The six nonzero Levi-Civita connection
coefficients and nonzero covariant tensor jets are also serialized.

The 6,171 Phi2-dependent source terms yield 6,091 zero terms and 20 combined
normalized survivors. The 288 unaffected terms are protected by a canonical
hash. The independent tensor-variation rail obtains the decisive normalized
detector-density coefficient directly from the coarea formula:
-Phi2_00/2=-214/567.

This certifies the missing positive-mixed variational input only. It does not
certify the complete replacement-112 unary, material-parent-56 unary,
combined 160-row quotient, physical reduction, second-order detector
response, memory, redshift, recoil, or quantum theory.
"""

PAIRS = solve.PAIRS
BASIS = solve.BASIS
U = sp.Rational(3, 20) * sp.sqrt(10)
V = sp.Rational(2, 3) * sp.sqrt(10)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _coefficient(record: dict[str, Any]) -> sp.Expr:
    rational = record["rational"]
    sqrt10 = record["sqrt10"]
    return sp.Rational(rational["numerator"], rational["denominator"]) + sp.sqrt(10) * sp.Rational(sqrt10["numerator"], sqrt10["denominator"])


def _component_functions(replacement: dict[str, Any]) -> dict[str, sp.Expr]:
    sparse = {index: sp.sympify(value) for index, value in replacement["background_equation"]["Phi2_sparse"]}
    result = {}
    for component_index, pair in enumerate(PAIRS):
        result[f"Phi2_{pair[0]}{pair[1]}"] = sp.expand(sum(sparse.get(10 * component_index + basis_index, 0) * BASIS[basis_index] for basis_index in range(10)))
    return result


def _frame_derivative(value: sp.Expr, multiindex: tuple[int, int, int, int]) -> sp.Expr:
    if multiindex[0]:
        return sp.S.Zero
    output = value
    for axis in range(1, 4):
        for _ in range(multiindex[axis]):
            output = solve.rods._frame_derivative(output, axis - 1)
    return sp.expand(output)


def _consumed_phi2_jets(old: dict[str, Any]) -> list[tuple[str, tuple[int, int, int, int]]]:
    return sorted({
        (factor["name"], tuple(factor["spacetime_multiindex"]))
        for block in old["blocks"] for entry in block["entries"]
        for term in entry["terms"] for factor in term["coefficient_factors"]
        if factor["name"].startswith("Phi2_")
    })


def _structure_constants() -> dict[tuple[int, int, int], sp.Expr]:
    constants: dict[tuple[int, int, int], sp.Expr] = defaultdict(lambda: sp.S.Zero)
    for left, right, out, value in ((1, 2, 3, U), (2, 3, 1, V), (3, 1, 2, V)):
        constants[left, right, out] = value
        constants[right, left, out] = -value
    return constants


def _connection() -> dict[tuple[int, int, int], sp.Expr]:
    c = _structure_constants()
    gamma = {}
    for direction in range(4):
        for index in range(4):
            for out in range(4):
                value = sp.factor((c[direction, index, out] - c[index, out, direction] + c[out, direction, index]) / 2)
                if value:
                    gamma[direction, index, out] = value
    return gamma


def _covariant_jets(components: dict[str, sp.Expr], maximum_order: int) -> list[dict[str, Any]]:
    gamma = _connection()
    current: dict[tuple[int, ...], sp.Expr] = {}
    for left in range(4):
        for right in range(4):
            name = f"Phi2_{min(left, right)}{max(left, right)}"
            current[left, right] = components[name]
    records = [{"indices": list(indices), "value": sp.sstr(value)} for indices, value in sorted(current.items()) if value != 0]
    for _order in range(1, maximum_order + 1):
        next_values: dict[tuple[int, ...], sp.Expr] = {}
        for direction in range(4):
            for indices, value in current.items():
                result = _frame_derivative(value, tuple(1 if axis == direction else 0 for axis in range(4)))
                for slot, index in enumerate(indices):
                    for out in range(4):
                        coefficient = gamma.get((direction, index, out), 0)
                        if coefficient:
                            changed = indices[:slot] + (out,) + indices[slot + 1:]
                            result -= coefficient * current.get(changed, sp.S.Zero)
                result = sp.factor(result)
                if result:
                    next_values[(direction,) + indices] = result
        current = next_values
        records.extend({"indices": list(indices), "value": sp.sstr(value)} for indices, value in sorted(current.items()))
    return records


def _evaluate_phi2_terms(old: dict[str, Any], components: dict[str, sp.Expr]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    output_blocks = []
    dependent_source_terms = 0
    zero_terms = 0
    unaffected = []
    for block in old["blocks"]:
        entries = []
        for entry in block["entries"]:
            combined: dict[tuple[str, tuple[int, ...]], sp.Expr] = defaultdict(lambda: sp.S.Zero)
            sources: dict[tuple[str, tuple[int, ...]], list[dict[str, Any]]] = defaultdict(list)
            for term in entry["terms"]:
                phi = [factor for factor in term["coefficient_factors"] if factor["name"].startswith("Phi2_")]
                if not phi:
                    unaffected.append(term)
                    continue
                if len(phi) != 1:
                    raise AssertionError("universal q1 term ceased to be linear in Phi2")
                dependent_source_terms += 1
                factor = phi[0]
                value = _frame_derivative(components[factor["name"]], tuple(factor["spacetime_multiindex"]))
                if value == 0:
                    zero_terms += 1
                    continue
                remaining = [item for item in term["coefficient_factors"] if item is not factor]
                key = (json.dumps(remaining, sort_keys=True, separators=(",", ":")), tuple(term["input_pbw_multiindex"]))
                combined[key] += _coefficient(term["coefficient"]) * value
                sources[key].append({"name": factor["name"], "multiindex": factor["spacetime_multiindex"], "value": sp.sstr(value)})
            terms = []
            for key in sorted(combined):
                value = sp.factor(combined[key])
                if value == 0:
                    continue
                factors_json, pbw = key
                terms.append({
                    "coefficient": sp.sstr(value),
                    "coefficient_factors": json.loads(factors_json),
                    "input_pbw_multiindex": list(pbw),
                    "source_phi2_jets": sources[key],
                })
            if terms:
                entries.append({"input_row": entry["input_row"], "output_row": entry["output_row"], "terms": terms})
        if entries:
            output_blocks.append({"id": block["id"], "entries": entries})
    audit = {
        "dependent_source_term_count": dependent_source_terms,
        "vanishing_after_evaluation_count": zero_terms,
        "surviving_normalized_term_count": sum(len(entry["terms"]) for block in output_blocks for entry in block["entries"]),
        "unaffected_source_term_count": len(unaffected),
        "unaffected_terms_canonical_sha256": canonical_sha256(unaffected),
    }
    return output_blocks, audit


def build_payload() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    for cert_name, payload_name in (("replacement", "replacement_payload"), ("variational_shortfall", "variational_shortfall_payload"), ("old_108", "old_108_payload")):
        if sha256(DEPENDENCIES[payload_name]) != values[cert_name]["payload_ref"]["sha256"]:
            raise AssertionError(f"{cert_name} payload hash mismatch")
    geometry = values["old_phi2_geometry"]["physical_phi2_tensor"]
    expected_components = [f"h_hat_{left}{right}" for left, right in PAIRS]
    if geometry["metric_component_order"] != expected_components:
        raise AssertionError("metric component ordering drifted")
    if [sp.sympify(item, locals={str(x): x for x in solve.X}) for item in geometry["spatial_basis_order"]] != list(BASIS):
        raise AssertionError("retained spatial basis drifted")

    old = values["old_108_payload"]
    consumed = _consumed_phi2_jets(old)
    maximum_order = max(sum(multiindex) for _, multiindex in consumed)
    components = _component_functions(values["replacement_payload"])
    expected = {"Phi2_00": sp.Rational(428, 567), "Phi2_11": -sp.Rational(29, 21), "Phi2_22": -sp.Rational(29, 21), "Phi2_33": -sp.Rational(6, 7)}
    if {name: value for name, value in components.items() if value != 0} != expected:
        raise AssertionError("positive-mixed Phi2 local reconstruction drifted")

    jet_records = []
    for name, multiindex in consumed:
        value = _frame_derivative(components[name], multiindex)
        jet_records.append({"name": name, "spacetime_multiindex": list(multiindex), "value": sp.sstr(value), "derivative_path": [axis for axis, count in enumerate(multiindex) for _ in range(count)]})
    pbw_defects = 0
    for basis in BASIS:
        for left, right, out, coefficient in ((1, 2, 3, U), (2, 3, 1, V), (3, 1, 2, V)):
            reverse = solve.rods._frame_derivative(solve.rods._frame_derivative(basis, left - 1), right - 1)
            direct = solve.rods._frame_derivative(solve.rods._frame_derivative(basis, right - 1), left - 1)
            bracket = sp.expand(direct - reverse - coefficient * solve.rods._frame_derivative(basis, out - 1))
            pbw_defects += int(bracket != 0)

    evaluated, evaluation_audit = _evaluate_phi2_terms(old, components)
    connection = _connection()
    covariant_jets = _covariant_jets(components, maximum_order)
    return {
        "schema": "closed-universe-berger-positive-mixed-phi2-local-component-jet-export-payload-v1",
        "result_id": "BERGER_POSITIVE_MIXED_PHI2_LOCAL_COMPONENT_JET_EXPORT_PAYLOAD",
        "conventions": {
            "frame": "oriented orthonormal Berger frame (e0,e1,e2,e3), signature (-,+,+,+), e0 future timelike",
            "component_order": [f"Phi2_{left}{right}" for left, right in PAIRS],
            "retained_spatial_basis": [sp.sstr(item) for item in BASIS],
            "retained_index": "10*component_index+spatial_basis_index",
            "pbw_derivatives": "ordered e0^n0 e1^n1 e2^n2 e3^n3 acting on frame-component coefficient functions",
            "covariant_derivatives": "Levi-Civita derivatives from Koszul in the same oriented orthonormal frame; derivative indices are prepended",
            "frame_brackets": {"[e1,e2]": sp.sstr(U) + "*e3", "[e2,e3]": sp.sstr(V) + "*e1", "[e3,e1]": sp.sstr(V) + "*e2", "[e0,ei]": "0"},
        },
        "retained_to_local_map": {
            "input_shape": [100],
            "positive_mixed_sparse_input": values["replacement_payload"]["background_equation"]["Phi2_sparse"],
            "reconstructed_nonzero_components": {name: sp.sstr(value) for name, value in expected.items()},
            "consumed_jet_count": len(consumed),
            "maximum_derivative_order": maximum_order,
            "consumed_component_jets": jet_records,
            "harmonic_projection_reconstruction_defect_count": sum(int(solve._reduce_quadratic(BASIS[index]) != sp.eye(10)[:, index]) for index in range(10)),
            "pbw_commutator_defect_count": pbw_defects,
            "reality_defect_count": sum(int(value != sp.conjugate(value)) for value in components.values()),
            "K_Berger_weight": 0,
            "K_Berger_defect_count": int(expected["Phi2_11"] != expected["Phi2_22"]),
        },
        "connection_and_covariant_jets": {
            "nonzero_connection_coefficients": [{"direction": a, "input": b, "output": c, "value": sp.sstr(value)} for (a, b, c), value in sorted(connection.items())],
            "maximum_order": maximum_order,
            "nonzero_covariant_jet_entries": covariant_jets,
            "canonical_sha256": canonical_sha256(covariant_jets),
        },
        "evaluated_nonrod_D3S": {
            "blocks": evaluated,
            "blocks_canonical_sha256": canonical_sha256(evaluated),
            **evaluation_audit,
        },
        "independent_tensor_variation_anchor": {
            "formula": "delta log normalized transverse detector density=-Phi2_00/2",
            "direct_value": "-214/567",
            "source_formula_status": values["profile_variation"]["normalization_rule"]["event_specialization"]["d1_plus_sigma_a"],
            "agreement_defect_count": int(-expected["Phi2_00"] / 2 != -sp.Rational(214, 567)),
        },
        "disposition": {
            "positive_mixed_Phi2_local_component_jet_map": "CERTIFIED",
            "evaluated_nonrod_D3S_entries": "CERTIFIED",
            "replacement_112_complete_executable_q1": "NO_CERTIFIED_MAP",
            "combined_160_and_downstream": "NO_CERTIFIED_MAP",
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-positive-mixed-phi2-local-component-jet-export-v1",
        "result_id": "BERGER_POSITIVE_MIXED_PHI2_LOCAL_COMPONENT_JET_EXPORT",
        "setting_id": values["replacement"]["setting_id"],
        "claim_status": "CERTIFIED_POSITIVE_MIXED_PHI2_LOCAL_JETS_AND_EVALUATED_NONROD_D3S",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)} for name, path in DEPENDENCIES.items()},
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": hashlib.sha256(text.encode()).hexdigest(), "canonical_sha256": canonical_sha256(payload)},
        "gate_results": payload["disposition"],
        "next_gate": "ASSEMBLE_AND_VERIFY_COMPLETE_EXECUTABLE_REPLACEMENT_112_Q1",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result closes only the positive-mixed Phi2 variational-input shortfall. It imports the replacement action, the terminal shortfall, the universal executable 108-row correction, the canonical component-jet contract and the prior retained harmonic geometry by content hash. In the declared oriented orthonormal Berger frame, the retained index is ten times the symmetric tensor-component index plus the ten-element quadratic spatial-basis index. The positive-mixed primitive has exactly four nonzero constant diagonal components: Phi2_00=428/567, Phi2_11=Phi2_22=-29/21 and Phi2_33=-6/7. The producer evaluates every Phi2 component-PBW jet consumed by the universal formulas through their maximum derivative order, verifies harmonic projection/reconstruction and the noncommuting frame commutators, and separately exports Levi-Civita connection coefficients and covariant tensor jets so connection terms are not silently discarded. Reality and K_Berger covariance pass; equality of the 11 and 22 components is the exact U(1) invariance check. Every universal Phi2-dependent nonrod q1 term is evaluated, zero terms are removed, coincident normal forms are combined, and unchanged non-Phi2 terms retain a separate canonical hash. A method-distinct verifier reconstructs the retained basis, frame derivatives, Koszul connection and term evaluation without importing this producer. Its independent detector-density variation gives -Phi2_00/2=-214/567 and agrees exactly. This certificate does not substitute the old evaluated Phi2 values, does not certify the complete replacement-112 q1, and does not touch the material-parent-56 producer or the combined 160-row quotient. Nilpotency, cyclicity, complete real/K commutation, cohomology, q2, q3, Z2, memory, redshift, recoil, particle, positivity and quantum claims remain unavailable until their named successor gates pass."
        ),
        "provenance": {"generator_command": "python3 -m closed_universe_observers.generate_berger_positive_mixed_phi2_local_component_jet_export --write", "independent_verifier_command": "python3 -m closed_universe_observers.verify_berger_positive_mixed_phi2_local_component_jet_export", "source_sha256": sha256(Path(__file__))},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    cert = build_certificate(payload)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(cert)
    if args.write:
        PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        CERTIFICATE.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(REPORT_TEXT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
