#!/usr/bin/env python3
"""Independently check the strict residual-SDR type/locality audit."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.json"
GRAPH = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
DFINITE = HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
ZERO_MODES = HERE / "certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"
CENTERED = HERE / "certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json"
PRIOR_OBSTRUCTION = ROOT / "d_quotient_classical/certificates/CANDIDATE13_REDUCED_SOURCE_SUPPORT_LOCAL_UPGRADE_OBSTRUCTION_V1.json"
GREEN_TRANSFER = ROOT / "d_quotient_classical/certificates/GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1.json"


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def decode(raw: str) -> Fraction:
    return Fraction(raw)


def multiply(first: list[list[Fraction]], second: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum(first[r][k] * second[k][c] for k in range(len(second))) for c in range(len(second[0]))] for r in range(len(first))]


def apply(matrix: list[list[Fraction]], vector: list[Fraction]) -> list[Fraction]:
    return [sum(entry * item for entry, item in zip(row, vector)) for row in matrix]


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    dependencies = (GRAPH, PAIRING, DFINITE, ZERO_MODES, CENTERED, PRIOR_OBSTRUCTION, GREEN_TRANSFER)
    pins = {item.get("path"): item.get("sha256") for item in value.get("provenance", {}).get("inputs", [])}
    for path in dependencies:
        if pins.get(str(path.relative_to(ROOT))) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append("dependency hash " + path.name)

    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    pairing = json.loads(PAIRING.read_text(encoding="utf-8"))
    dfinite = json.loads(DFINITE.read_text(encoding="utf-8"))
    zero_modes = json.loads(ZERO_MODES.read_text(encoding="utf-8"))
    centered = json.loads(CENTERED.read_text(encoding="utf-8"))
    maps = graph.get("graph_sdr_component_maps", {})
    expected_shapes = {
        "i_end_graph": [386, 30], "p_end_graph": [30, 386],
        "H_alg_graph": [386, 386], "P_end_graph": [386, 386], "P_alg_graph": [386, 386],
    }
    for name, shape in expected_shapes.items():
        if maps.get(name, {}).get("shape") != shape:
            errors.append("graph map shape " + name)
    replay = graph.get("exact_replay", {})
    for key in ("qH_plus_Hq_equals_P_alg_graph", "p_graph_i_graph_identity_defects", "i_graph_p_graph_equals_P_end_defects", "H_squared_defects", "H_i_graph_defects", "p_graph_H_defects", "H_alg_graph_cyclicity_defects"):
        expected = True if key == "qH_plus_Hq_equals_P_alg_graph" else 0
        if replay.get(key) != expected:
            errors.append("graph replay " + key)

    endpoint = [row.get("row_id") for row in pairing.get("component_basis", {}).get("rows", [])[:30]]
    residual = [label for block in dfinite.get("blocks", []) for label in block.get("residual_basis", [])]
    symmetry = [*zero_modes.get("zero_mode_basis", {}).get("canonical_generator_order", []), *zero_modes.get("zero_mode_basis", {}).get("canonical_dual_order", [])]
    census = value.get("type_census", {})
    if len(endpoint) != 30 or len(set(endpoint)) != 30 or census.get("endpoint_row_ids") != endpoint:
        errors.append("endpoint species dictionary")
    if [block.get("full_dimension") for block in dfinite.get("blocks", [])] != [230, 440, 758, 1216, 1846]:
        errors.append("D-finite full dimensions")
    if [block.get("residual_dimension") for block in dfinite.get("blocks", [])] != [10, 40, 82, 136, 202] or len(residual) != 470:
        errors.append("D-finite residual dimensions")
    if not all(":W_PLUS:" in label or ":W_MINUS:" in label for label in residual):
        errors.append("D-finite residual labels")
    if len(symmetry) != 30 or set(endpoint).intersection(symmetry):
        errors.append("endpoint/zero-mode type collision")
    if census.get("centered_dimensions_C3_C4_C5") != centered.get("scope", {}).get("centered_cochain_dimensions_C3_C4_C5") or census.get("sha256") != digest({key: item for key, item in census.items() if key != "sha256"}):
        errors.append("type census")

    fixture = value.get("support_locality_obstruction", {}).get("finite_exact_fixture", {})
    constant = [[decode(item) for item in row] for row in fixture.get("constant_projector", [])]
    harmonic = [[decode(item) for item in row] for row in fixture.get("harmonic_projector", [])]
    localized = [decode(item) for item in fixture.get("localized_input", [])]
    if len(constant) != 3 or len(harmonic) != 3 or len(localized) != 3:
        errors.append("support fixture shape")
    else:
        constant_output = apply(constant, localized)
        harmonic_output = apply(harmonic, localized)
        checks = {
            "zero_projector_idempotent": multiply(constant, constant) == constant,
            "mode_projector_idempotent": multiply(harmonic, harmonic) == harmonic,
            "localized_input_support": [i for i, item in enumerate(localized) if item] == [0],
            "zero_projector_expands_support": [i for i, item in enumerate(constant_output) if item] == [0, 1, 2],
            "mode_projector_expands_support": [i for i, item in enumerate(harmonic_output) if item] == [0, 1, 2],
        }
        if fixture.get("checks") != checks or not all(checks.values()):
            errors.append("support fixture replay")

    ledger = {item.get("id"): item for item in value.get("carrier_ledger", [])}
    expected_kinds = {
        "GRAPH_ENDPOINT_FIELDS": (30, "SECTION_SHEAF_COMPONENT_CARRIER", "FINITE_ORDER_SUPPORT_LOCAL"),
        "DFINITE_WEYL_RESIDUAL": (470, "FINITE_HARMONIC_COEFFICIENT_CARRIER", "REDUCED_MODE_NOT_ARBITRARY_SUPPORT"),
        "CONFORMAL_KILLING_COTANGENT": (30, "FINITE_LIE_COTANGENT_CARRIER", "GLOBAL_ZERO_MODE_COEFFICIENTS"),
        "CENTERED_CE_COCHAINS": (12343, "FINITE_CENTERED_CE_COCHAIN_CARRIER", "LOCAL_ALGEBRAIC_AND_REDUCED_MODE_ONLY"),
    }
    for key, expected in expected_kinds.items():
        item = ledger.get(key, {})
        if (item.get("coordinates"), item.get("kind"), item.get("locality")) != expected:
            errors.append("carrier ledger " + key)

    decision = value.get("architecture_decision", {})
    if decision.get("original_M3_disposition") != "REJECT_AS_SINGLE_UNTYPED_SUPPORT_LOCAL_RESIDUAL_SDR_REQUIREMENT":
        errors.append("M3 disposition")
    if decision.get("M3L_COMMON_ENDPOINT_SDR_BINDING", {}).get("status") != "EXACT_OBJECT_EXISTS_COMMON_HASH_BINDING_OPEN" or decision.get("M3R_TYPED_RESIDUAL_COMPARISON", {}).get("status") != "NOT_CONSTRUCTED":
        errors.append("M3 typed split")
    if decision.get("sha256") != digest({key: item for key, item in decision.items() if key != "sha256"}):
        errors.append("architecture digest")

    flags = value.get("claim_flags", {})
    for key in ("STRICT_386_GRAPH_ENDPOINT_SDR_SUPPORT_LOCAL", "M3_TYPED_SPLIT_REQUIRED"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "GRAPH_ENDPOINT_30_IS_FINITE_RESIDUAL_30", "DFINITE_RESIDUAL_PROJECTOR_SUPPORT_LOCAL",
        "ZERO_MODE_PROJECTOR_SUPPORT_LOCAL", "ORIGINAL_M3_SINGLE_OBJECT_TYPE_CORRECT",
        "M3L_COMMON_ENDPOINT_SDR_BOUND", "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED",
        "CLASSICAL_IMPORT_GATE_PASSED", "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        if flags.get(key) is not False:
            errors.append("fail-closed flag " + key)
    expected_digest = digest({key: value.get(key) for key in ("carrier_ledger", "type_census", "support_locality_obstruction", "architecture_decision", "claim_flags")})
    if value.get("independent_checker", {}).get("expected_digest") != expected_digest:
        errors.append("independent digest")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    errors = check(value)
    print("STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
