#!/usr/bin/env python3
"""Independent receiver for strict q2/q3 typed Green compatibility."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1.json"
REPORT = HERE / "REPORT_STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1.md"
SCHEMA = HERE / "schema/strict-m2-q2-q3-typed-green-compatibility-v1.schema.json"
INPUTS = {
    "m1c": HERE / "certificates/STRICT_M1C_COMMON_SNAPSHOT_V1.json",
    "gate": HERE / "certificates/CLASSICAL_IMPORT_GATE_V30_RECONCILIATION.json",
    "green": HERE / "certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json",
    "field_inverse": HERE / "certificates/STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1.json",
    "q2": HERE / "certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json",
    "q3": HERE / "certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json",
    "cyclic": HERE / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json",
    "literature": ROOT / "foundations/literature-causal-green-atlas-v1.json",
}
EXPECTED_IDS = {
    "m1c": "STRICT_M1C_COMMON_SNAPSHOT_V1",
    "gate": "CLASSICAL_IMPORT_GATE_V30_RECONCILIATION",
    "green": "STRICT_386_GRAPH_GREEN_ACTION_NAME_V1",
    "field_inverse": "STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1",
    "q2": "STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1",
    "q3": "STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1",
    "cyclic": "STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1",
    "literature": "FOUNDATIONAL_CAUSAL_GREEN_LITERATURE_V1",
}
CHECKERS = (
    "check_strict_m1c_common_snapshot.py",
    "check_classical_import_gate_v30_reconciliation.py",
    "check_strict_386_graph_green_action_name.py",
    "check_strict_386_field_equation_green_quotient_inverse.py",
    "check_strict_386_source_q2_common_assembly.py",
    "check_strict_386_source_q3_common_assembly.py",
    "check_strict_386_local_cyclic_pairing_closure.py",
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def source_id(value: dict[str, Any]) -> str | None:
    return value.get("result_id") or value.get("ledger_id") or value.get("schema")


def verify_embedded_hash(value: dict[str, Any], label: str, errors: list[str]) -> None:
    if value.get("sha256") != digest({key: item for key, item in value.items() if key != "sha256"}):
        errors.append(f"{label} digest")


def check(value: dict[str, Any], run_receivers: bool = False) -> list[str]:
    errors: list[str] = []
    try:
        schema = load(SCHEMA)
        Draft202012Validator.check_schema(schema)
        if list(Draft202012Validator(schema).iter_errors(value)):
            errors.append("schema validation")
    except Exception:
        errors.append("schema validation")

    source = {name: load(path) for name, path in INPUTS.items()}
    provenance = value.get("provenance", {}).get("inputs", [])
    by_id = {item.get("input_id"): item for item in provenance}
    if len(provenance) != 8 or len(by_id) != 8:
        errors.append("provenance census")
    for name, path in INPUTS.items():
        item = by_id.get(name, {})
        if (
            item.get("path") != str(path.relative_to(ROOT))
            or item.get("sha256") != file_hash(path)
            or item.get("result_or_artifact_id") != EXPECTED_IDS[name]
            or source_id(source[name]) != EXPECTED_IDS[name]
        ):
            errors.append("provenance binding")

    m1c, gate, green, inverse, q2, q3, cyclic, literature = (
        source[name] for name in ("m1c", "gate", "green", "field_inverse", "q2", "q3", "cyclic", "literature")
    )
    binding = value.get("snapshot_binding", {})
    resolution = gate.get("m1c_common_snapshot_resolution", {})
    if (
        gate.get("gate_disposition", {}).get("gate_a_status") != "VERIFIED"
        or gate.get("claim_flags", {}).get("CLASSICAL_IMPORT_GATE_PASSED") is not True
        or resolution.get("snapshot_sha256") != m1c.get("snapshot_sha256")
        or resolution.get("certificate_sha256") != file_hash(INPUTS["m1c"])
        or binding.get("snapshot_id") != m1c.get("snapshot_id")
        or binding.get("snapshot_sha256") != m1c.get("snapshot_sha256")
    ):
        errors.append("Gate-A snapshot binding")
    pins = {item.get("pin_id"): item for item in m1c.get("artifact_pins", [])}
    for pin_id, input_id in (("source_q2", "q2"), ("source_q3", "q3"), ("local_cyclic", "cyclic")):
        if pins.get(pin_id, {}).get("sha256") != file_hash(INPUTS[input_id]):
            errors.append("snapshot operation pins")

    ledger = value.get("type_ledger", {})
    verify_embedded_hash(ledger, "type ledger", errors)
    if (
        ledger.get("plus") != "Lambda_plus:X_C^k -> X_PC^(k-1), continuously extended X_PC^k -> X_PC^(k-1)"
        or ledger.get("minus") != "Lambda_minus:X_C^k -> X_FC^(k-1), continuously extended X_FC^k -> X_FC^(k-1)"
        or ledger.get("homotopy") != "q1 Lambda_sigma + Lambda_sigma q1 = identity on the matching support class"
        or ledger.get("field_component") != inverse.get("green_field_equation_component", {}).get("definition")
    ):
        errors.append("typed operator ledger")

    support = value.get("support_and_continuity", {})
    verify_embedded_hash(support, "support and continuity", errors)
    baer = next((item for item in literature.get("entries", []) if item.get("id") == "baer-2015"), {})
    if (
        support.get("q2_locality", {}).get("source_families") != q2.get("family_census", {}).get("total_shifted_source_q2_families")
        or support.get("q3_locality", {}).get("source_families") != q3.get("family_census", {}).get("total_source_q3_families")
        or support.get("q2_locality", {}).get("graph_compositional_DAG") is not True
        or support.get("q3_locality", {}).get("graph_compositional_DAG") is not True
        or support.get("analytic_extension", {}).get("source_pdf_sha256") != baer.get("artifact", {}).get("sha256")
        or support.get("global_unindexed_joint_LF_continuity_claimed") is not False
    ):
        errors.append("support-space theorem")

    responses = value.get("causal_response_names", {})
    verify_embedded_hash(responses, "causal responses", errors)
    expected_operation_hashes = {
        "B2": q2.get("source_q2_snapshot", {}).get("sha256"),
        "B3": q3.get("source_q3_snapshot", {}).get("sha256"),
    }
    for sign, support_class in (("plus", "PC"), ("minus", "FC")):
        for response_id, arity in (("B2", 2), ("B3", 3)):
            response = responses.get(sign, {}).get("responses", {}).get(response_id, {})
            name = response.get("operator_name", {})
            if (
                name.get("arity") != arity
                or name.get("operation", {}).get("sha256") != expected_operation_hashes[response_id]
                or name.get("green", {}).get("sha256") != green.get("operator_names", {}).get(sign, {}).get("canonical_name_sha256")
                or response.get("compact_input_type") != f"X_C^{arity} -> X_{support_class}"
                or response.get("canonical_name_sha256") != digest(name)
                or response.get("continuous_on_fixed_support_steps") is not True
            ):
                errors.append("causal response construction")

    replay = value.get("compatibility_replay", {})
    verify_embedded_hash(replay, "compatibility replay", errors)
    expected_defects = {
        "q1_q2_identity": q2.get("q1_q2_replay", {}).get("graph_386_q1_q2_defects"),
        "q1_q3_plus_q2_q2_identity": q3.get("arity_three_replay", {}).get("graph_386_arity_three_defects"),
        "q2_cyclicity": cyclic.get("local_cyclicity_replay", {}).get("graph_q2_cyclicity_defects"),
        "q3_cyclicity_mod_horizontal_boundary": cyclic.get("local_cyclicity_replay", {}).get("graph_q3_cyclicity_defects_mod_d"),
    }
    for key, expected in expected_defects.items():
        if replay.get(key) != expected or expected != 0:
            errors.append("nonlinear identity replay")
    if (
        green.get("analytic_and_exact_replay", {}).get("full_graph_homotopy_identity_exact") is not True
        or green.get("analytic_and_exact_replay", {}).get("advanced_retarded_adjoint_exact") is not True
        or replay.get("green_homotopy_defects") != 0
        or replay.get("advanced_retarded_adjoint_defects") != 0
        or replay.get("total_exact_or_structural_defects") != 0
        or "compact test leg" not in replay.get("cyclic_chain", "")
    ):
        errors.append("Green chain/cyclic replay")

    trees = value.get("polarized_finite_tree_theorem", {})
    verify_embedded_hash(trees, "finite tree theorem", errors)
    if (
        trees.get("q2_and_q3_vertices_included") is not True
        or trees.get("all_finite_same_orientation_trees") is not True
        or trees.get("infinite_tree_sum_or_convergence") is not False
        or trees.get("arbitrary_mixed_orientation_trees") is not False
    ):
        errors.append("finite tree boundary")

    source2 = value.get("lambda2_general_source_cocycle", {})
    verify_embedded_hash(source2, "second source", errors)
    coefficients = source2.get("coefficients", {})
    try:
        exact_total = Fraction(coefficients["q2_Jacobiator"]) + Fraction(coefficients["q3_image"]) * Fraction(coefficients["arity_three_factor"])
    except Exception:
        exact_total = Fraction(1)
    if (
        exact_total != 0
        or coefficients.get("total") != "0"
        or source2.get("orientations_checked") != 2
        or source2.get("structural_defects") != 0
        or "compact" not in source2.get("support", "")
        or inverse.get("claim_flags", {}).get("STRICT_386_FIELD_EQUATION_CONSTRAINED_RIGHT_INVERSE_CERTIFIED") is not True
    ):
        errors.append("general second-source closure")

    envelope = value.get("causal_envelope", {})
    verify_embedded_hash(envelope, "causal envelope", errors)
    expected_envelope = {
        "snapshot_id": m1c.get("snapshot_id"),
        "snapshot_sha256": m1c.get("snapshot_sha256"),
        "gate_certificate_sha256": file_hash(INPUTS["gate"]),
        "green_plus_sha256": green.get("canonical_hashes", {}).get("plus_action_name_sha256"),
        "green_minus_sha256": green.get("canonical_hashes", {}).get("minus_action_name_sha256"),
        "q2_snapshot_sha256": q2.get("source_q2_snapshot", {}).get("sha256"),
        "q3_snapshot_sha256": q3.get("source_q3_snapshot", {}).get("sha256"),
        "pairing_sha256": cyclic.get("pairing_replay", {}).get("pairing_sha256"),
        "field_inverse_sha256": inverse.get("typed_inverse_snapshot", {}).get("sha256"),
        "type_ledger_sha256": ledger.get("sha256"),
        "support_and_continuity_sha256": support.get("sha256"),
        "responses_sha256": responses.get("sha256"),
        "compatibility_replay_sha256": replay.get("sha256"),
        "tree_theorem_sha256": trees.get("sha256"),
        "second_source_sha256": source2.get("sha256"),
    }
    for key, expected in expected_envelope.items():
        if envelope.get(key) != expected:
            errors.append("causal envelope binding")
    if envelope.get("immutable_snapshot_modified") is not False:
        errors.append("immutable snapshot mutation")

    flags = value.get("claim_flags", {})
    required_true = (
        "CLASSICAL_IMPORT_GATE_PASSED", "STRICT_386_TYPED_LORENTZIAN_GREEN_HOMOTOPY_CERTIFIED",
        "STRICT_386_AUTHORITATIVE_Q2_GREEN_COMPATIBILITY_CERTIFIED",
        "STRICT_386_AUTHORITATIVE_Q3_GREEN_COMPATIBILITY_CERTIFIED",
        "STRICT_386_Q2_Q3_CYCLIC_GREEN_CHAIN_CERTIFIED",
        "STRICT_386_POLARIZED_FINITE_Q2_Q3_TREES_CERTIFIED",
        "STRICT_386_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE_CERTIFIED",
        "NONLINEAR_GREEN_COMPATIBILITY_CERTIFIED",
    )
    required_false = (
        "STRICT_386_ARBITRARY_MIXED_SIGN_TREES_CERTIFIED",
        "STRICT_386_INFINITE_TREE_SERIES_CONVERGENCE_CERTIFIED",
        "STRICT_386_ALL_ORDER_MOLLER_MAP_CERTIFIED",
        "STRICT_386_DISTRIBUTION_KERNEL_BYTES_SERIALIZED",
        "COMPLETE_LORENTZIAN_OFFSHELL_BV_PROPAGATOR_CONSTRUCTED",
        "FULL_COMPLEX_BRST_HADAMARD_TWO_POINT_FUNCTION_CONSTRUCTED",
        "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED", "QME_RESTORED",
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED", "PHYSICAL_POSITIVITY_CERTIFIED",
        "LORENTZIAN_QUANTUM_THEORY",
    )
    for flag in required_true:
        if flags.get(flag) is not True:
            errors.append(f"positive flag {flag}")
    for flag in required_false:
        if flags.get(flag) is not False:
            errors.append(f"fail-closed flag {flag}")
    expected_content = digest({
        "causal_envelope": envelope,
        "claim_flags": flags,
        "does_not_establish": value.get("does_not_establish"),
    })
    if value.get("content_sha256") != expected_content:
        errors.append("content digest")

    report = REPORT.read_text(encoding="utf-8") if REPORT.is_file() else ""
    if "post-freeze causal envelope" not in report or "not a Hadamard two-point function" not in report:
        errors.append("human report boundary")

    if run_receivers:
        for checker in CHECKERS:
            completed = subprocess.run([sys.executable, str(HERE / checker)], cwd=ROOT, text=True, capture_output=True)
            if completed.returncode:
                errors.append(f"predecessor receiver failed {checker}")
    return sorted(set(errors))


def main() -> int:
    errors = check(load(RESULT), run_receivers=True)
    if errors:
        print("STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1: PASS")
    print("  - Gate-A q2/q3 bound to both typed Green orientations")
    print("  - chain, cyclic, causal-support and finite-tree obligations verified")
    print("  - general second nonlinear source cocycle closes; Hadamard remains open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
