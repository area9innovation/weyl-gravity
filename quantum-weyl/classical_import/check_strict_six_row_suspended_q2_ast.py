#!/usr/bin/env python3
"""Independent checker for the portable six-row suspended q2 ledger."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json"
KINEMATIC = HERE / "certificates/STRICT_Q2_KINEMATIC_COTANGENT_AST_V1.json"
BACH = HERE / "certificates/STRICT_BACH_NATURAL_OPERATOR_AST_V1.json"
HSTAR = HERE / "certificates/STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1.json"
EXPORTED = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
CONTRACT = HERE / "certificates/SUPPORT_LOCAL_Q2_EXPORT_CONTRACT.json"
SYMBOLS = ("h", "c", "omega", "h_star", "c_star", "omega_star")
DEGREES = {"h": 0, "c": -1, "omega": -1, "h_star": 1, "c_star": 2, "omega_star": 2}
PARITIES = {symbol: degree % 2 for symbol, degree in DEGREES.items()}
PRIMARY = {
    "q2_c_cc": ("c", ("c", "c"), 1, "vector_ghost_lie_bracket", -1),
    "q2_omega_comega": ("omega", ("c", "omega"), 1, "scalar_lie_transport", None),
    "q2_h_ch": ("h", ("c", "h"), 1, "metric_lie_transport", None),
    "q2_h_omegah": ("h", ("omega", "h"), 2, "weyl_metric_product", None),
    "q2_hstar_hh": ("h_star", ("h", "h"), 1, "polarized_bach_natural_operator", 1),
    "q2_hstar_chstar": ("h_star", ("c", "h_star"), 1, "contravariant_density_lie_transport", None),
    "q2_hstar_omegahstar": ("h_star", ("omega", "h_star"), -2, "weyl_metric_antifield_product", None),
    "q2_cstar_hhstar": ("c_star", ("h", "h_star"), 1, "metric_antifield_diff_noether", None),
    "q2_cstar_ccstar": ("c_star", ("c", "c_star"), 1, "covector_density_lie_transport", None),
    "q2_cstar_omegaomegastar": ("c_star", ("omega", "omega_star"), 1, "weyl_antifield_gradient", None),
    "q2_omegastar_hhstar": ("omega_star", ("h", "h_star"), 2, "metric_antifield_trace_pair", None),
    "q2_omegastar_comegastar": ("omega_star", ("c", "omega_star"), 1, "scalar_density_lie_transport", None),
}
TRUE_FLAGS = {
    "PORTABLE_TENSOR_NATURAL_HSTAR_ROW",
    "SUSPENDED_GRADED_POLARIZATION_REPLAYED",
    "SIX_MINIMAL_Q2_ROW_LEDGERS_COMPLETE",
    "Q2_KOSZUL_SYMMETRY_REPLAYED",
}
FALSE_FLAGS = {
    "Q1_Q2_ARITY_TWO_NILPOTENCY_REPLAYED",
    "STRICT_FULL_LOCAL_D_ACTION_CERTIFIED",
    "D_Q2_DERIVATION_REPLAYED",
    "BV_CYCLICITY_Q2_REPLAYED",
    "STRICT_SUPPORT_LOCAL_Q2_COMPLETE",
    "CLASSICAL_IMPORT_GATE_PASSED",
    "LORENTZIAN_CAUSAL_CERTIFIED",
    "QME_RESTORED",
}


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    kinematic = json.loads(KINEMATIC.read_text())
    bach = json.loads(BACH.read_text())
    hstar = json.loads(HSTAR.read_text())
    exported = json.loads(EXPORTED.read_text())
    contract = json.loads(CONTRACT.read_text())

    if value.get("result_state") != "SIX_ROWS_PORTABLE_AND_KOSZUL_REPLAYED_Q1_D_PAIRING_IDENTITIES_OPEN" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("result state or lifecycle drift")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"] or value.get("convention") != "suspended-graded-symmetric-factorial-v1":
        errors.append("dependency tag or suspension convention drift")
    scope = value.get("scope", {})
    if scope.get("locality") != "SUPPORT_LOCAL_POLYDIFFERENTIAL" or scope.get("maximum_metric_input_jet_order") != 4 or "intersection" not in scope.get("support_rule", ""):
        errors.append("support-local scope or jet order drift")

    generator = value.get("generator_ledger", [])
    expected_generator = [{"symbol": symbol, "local_tangent_degree": DEGREES[symbol], "Grassmann_parity": PARITIES[symbol]} for symbol in SYMBOLS]
    if generator != expected_generator:
        errors.append("generator degree/parity ledger drift")
    source_names = {"g": "h", "xi": "c", "omega": "omega", "g_star": "h_star", "xi_star": "c_star", "omega_star": "omega_star"}
    exported_by_symbol = {item["symbol"]: item for item in exported["generators"]}
    if any(exported_by_symbol[source]["Grassmann_parity"] != PARITIES[target] or -exported_by_symbol[source]["ghost_number"] != DEGREES[target] for source, target in source_names.items()):
        errors.append("authoritative generator grading crosswalk failed")

    primary = value.get("primary_components", [])
    primary_by_id = {item.get("primary_id"): item for item in primary if isinstance(item, dict)}
    if len(primary) != 12 or set(primary_by_id) != set(PRIMARY):
        errors.append("primary component inventory is not exactly twelve unique terms")
    for primary_id, (output, inputs, coefficient, operator, intrinsic) in PRIMARY.items():
        item = primary_by_id.get(primary_id, {})
        if (item.get("output"), tuple(item.get("inputs", [])), item.get("coefficient"), item.get("operator_id")) != (output, inputs, coefficient, operator):
            errors.append(f"{primary_id}: output/input/coefficient/operator drift")
        if intrinsic is not None and item.get("intrinsic_swap_sign") != intrinsic:
            errors.append(f"{primary_id}: intrinsic swap sign drift")
        if item.get("maximum_total_derivative_order", 99) > 4 or item.get("maximum_input_jet_orders") is None or len(item.get("maximum_input_jet_orders", [])) != 2:
            errors.append(f"{primary_id}: jet bound drift")
        if primary_id == "q2_hstar_hh":
            semantics = item.get("portable_semantics", {})
            if semantics != {"result_id": bach["result_id"], "ast_sha256": bach["canonical_hashes"]["natural_operator_ast_sha256"], "root_node": bach["natural_operator_ast"]["root_node"]}:
                errors.append("portable Bach root binding drift")

    kinematic_components = {item["component_id"]: item for item in kinematic["components"]}
    for primary_id in set(PRIMARY) & set(kinematic_components):
        item, source = primary_by_id.get(primary_id, {}), kinematic_components[primary_id]
        if item.get("coefficient") != source["coefficient"] or item.get("inputs") != source["inputs"] or item.get("output") != source["output"]:
            errors.append(f"{primary_id}: diagonal kinematic crosswalk drift")
    hstar_source = {item["component_id"]: item for item in hstar["components"]}
    for primary_id in ("q2_hstar_chstar", "q2_hstar_omegahstar"):
        item, source = primary_by_id.get(primary_id, {}), hstar_source[primary_id]
        if item.get("inputs") != source["inputs"] or item.get("coordinate_formula") != source["coordinate_formula"]:
            errors.append(f"{primary_id}: h-star cotangent crosswalk drift")

    ordered = value.get("ordered_components", [])
    ordered_by_id = {item.get("component_id"): item for item in ordered if isinstance(item, dict)}
    if len(ordered) != 22 or len(ordered_by_id) != 22:
        errors.append("ordered component inventory is not exactly twenty-two unique terms")
    for item in ordered:
        component_id = item.get("component_id")
        primary_item = primary_by_id.get(item.get("primary_id"), {})
        output, inputs = item.get("output"), item.get("inputs", [])
        if output != primary_item.get("output") or len(inputs) != 2 or any(symbol not in DEGREES for symbol in inputs):
            errors.append(f"{component_id}: ordered component binding drift")
            continue
        left, right = inputs
        if DEGREES[output] - DEGREES[left] - DEGREES[right] != 1:
            errors.append(f"{component_id}: cohomological degree-one failure")
        expected_sign = -1 if PARITIES[left] * PARITIES[right] else 1
        if item.get("koszul_swap_sign") != expected_sign:
            errors.append(f"{component_id}: Koszul sign drift")
        partner = ordered_by_id.get(item.get("koszul_swap_partner"), {})
        if item.get("orientation") == "INTRINSIC_SELF_PAIR":
            if partner != item or left != right or primary_item.get("intrinsic_swap_sign") != expected_sign:
                errors.append(f"{component_id}: intrinsic self-pair failure")
        elif partner.get("inputs") != [right, left] or partner.get("koszul_swap_partner") != component_id or partner.get("coefficient_relative_to_primary") != expected_sign * item.get("coefficient_relative_to_primary", 0):
            errors.append(f"{component_id}: ordered Koszul partner failure")

    rows = value.get("row_completeness", [])
    if [row.get("output") for row in rows] != list(SYMBOLS) or any(row.get("status") != "COMPLETE" for row in rows):
        errors.append("row-completeness ledger order/status drift")
    for row in rows:
        output = row.get("output")
        expected_primary = [item["primary_id"] for item in primary if item.get("output") == output]
        expected_ordered = [item["component_id"] for item in ordered if item.get("output") == output]
        if not expected_primary or row.get("primary_component_ids") != expected_primary or row.get("ordered_component_ids") != expected_ordered:
            errors.append(f"{output}: row-completeness component references drift")

    diagonal = value.get("diagonal_crosswalk", {})
    if diagonal.get("source_diagonal_component_count") != 12 or diagonal.get("ordered_suspended_component_count") != 22 or "(1/2)" not in diagonal.get("Taylor_formula", ""):
        errors.append("diagonal Taylor count/convention drift")
    same = {item.get("primary_id"): item for item in diagonal.get("same_species_rows", [])}
    if same.get("q2_c_cc", {}).get("swap_sign") != -1 or same.get("q2_hstar_hh", {}).get("swap_sign") != 1:
        errors.append("same-species diagonal recovery drift")
    grassmann = diagonal.get("external_Grassmann_exact_replay", {})
    vector = grassmann.get("odd_vector_fixture", {})
    try:
        x = tuple(Fraction(item) for item in vector["X"])
        y = tuple(Fraction(item) for item in vector["Y"])
        dx = tuple(tuple(Fraction(item) for item in row) for row in vector["dX"])
        dy = tuple(tuple(Fraction(item) for item in row) for row in vector["dY"])
        bracket = tuple(sum(x[rho] * dy[mu][rho] - y[rho] * dx[mu][rho] for rho in range(4)) for mu in range(4))
        if vector.get("underlying_bracket_XY") != [str(item) for item in bracket] or vector.get("q2_c_c_theta1theta2_coefficient") != [str(2 * item) for item in bracket] or vector.get("half_q2_equals_c_partial_c_theta1theta2") is not True or vector.get("nonzero_component_count") != sum(item != 0 for item in bracket):
            errors.append("odd-vector external Grassmann factor-two replay failed")
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        errors.append("odd-vector external Grassmann fixture malformed")
    mixed_grassmann = grassmann.get("mixed_species", [])
    expected_mixed = []
    for item in primary:
        left, right = item.get("inputs", [None, None])
        if left == right:
            continue
        sign = -1 if PARITIES[left] * PARITIES[right] else 1
        expected_mixed.append({"primary_id": item["primary_id"], "kernel_swap_sign": sign, "external_coefficient_reordering_sign": sign, "half_sum_multiplier": "1"})
    if mixed_grassmann != expected_mixed or grassmann.get("all_ten_mixed_multipliers_equal_one") is not True or grassmann.get("even_metric_self_pair_half_multiplier") != "1/2":
        errors.append("mixed/even external Grassmann diagonal replay failed")

    statuses = {item.get("check_id"): item.get("status") for item in value.get("proof_checks", [])}
    if statuses != {
        "six_output_rows_complete": "VERIFIED",
        "cohomological_degree_one": "VERIFIED",
        "q2_koszul_symmetry": "VERIFIED",
        "diagonal_Taylor_recovery": "VERIFIED",
        "portable_hstar_row": "VERIFIED",
        "q1_q2_arity_two_nilpotency": "NOT_REPLAYED",
        "D_q2_derivation": "NOT_REPLAYED",
        "BV_cyclicity_q2": "NOT_REPLAYED",
    }:
        errors.append("proof-check status inventory drift or premature promotion")
    if contract.get("result_state") != "CONTRACT_READY_AWAITING_CLASSICAL_EXPORT" or contract.get("checks", {}).get("identities_independently_recomputed") != "NOT_COMPUTED":
        errors.append("complete downstream contract boundary drift")
    flags = value.get("claim_flags", {})
    if any(flags.get(flag) is not True for flag in TRUE_FLAGS) or any(flags.get(flag) is not False for flag in FALSE_FLAGS):
        errors.append("claim flags drift or premature promotion")
    if len(value.get("does_not_establish", [])) < 6:
        errors.append("does-not-establish ledger shortened")

    expected_hashes = {
        "generator_ledger_sha256": digest(generator),
        "primary_components_sha256": digest(primary),
        "ordered_components_sha256": digest(ordered),
        "row_completeness_sha256": digest(rows),
        "diagonal_crosswalk_sha256": digest(diagonal),
        "proof_checks_sha256": digest(value.get("proof_checks")),
    }
    if value.get("canonical_hashes") != expected_hashes:
        errors.append("canonical hashes do not reproduce")
    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or file_sha(path) != item.get("sha256"):
            errors.append(f"provenance drift: {item.get('path')}")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - 12 primary and 22 ordered components cover all six rows")
        print("  - degree one, Koszul symmetry and portable h-star integration replayed")
        print("  - q1q2, local D, cyclicity and Gate A remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
