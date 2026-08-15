#!/usr/bin/env python3
"""Independent exact checker for the five-row strict q2 diagonal AST."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_Q2_KINEMATIC_COTANGENT_AST_V1.json"
SOURCE = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
IMPORTED = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json"
MINIMAL = ROOT / "field_bv_identification/certificates/minimal_bv_chain.json"
SYMBOLS = ("h", "c", "omega", "h_star", "c_star", "omega_star")
FORMULAS = {
    "odd_vector_half_bracket": ("c", ("c", "c"), 1, "c^rho partial_rho c^mu = (1/2)[c,c]^mu", ("bracket_xi",)),
    "scalar_lie_transport": ("omega", ("c", "omega"), 1, "c^rho partial_rho omega", ("Lie_omega",)),
    "metric_lie_transport": ("h", ("c", "h"), 1, "c^rho partial_rho h_mu_nu + h_rho_nu partial_mu c^rho + h_mu_rho partial_nu c^rho", ("Lie_g",)),
    "weyl_metric_product": ("h", ("omega", "h"), 2, "omega * h_mu_nu", ("g", "omega")),
    "metric_antifield_diff_noether": ("c_star", ("h", "h_star"), 1, "h_star^mu_nu partial_lambda h_mu_nu - 2 partial_mu(h_star^mu_nu h_lambda_nu)", ("N_xi",)),
    "covector_density_lie_transport": ("c_star", ("c", "c_star"), 1, "c^rho partial_rho c_star_lambda + c_star_rho partial_lambda c^rho + (partial_rho c^rho)c_star_lambda", ("Lie_xi_star",)),
    "weyl_antifield_gradient": ("c_star", ("omega", "omega_star"), 1, "omega_star partial_lambda omega", ("N_xi",)),
    "metric_antifield_trace_pair": ("omega_star", ("h", "h_star"), 2, "h_mu_nu h_star^mu_nu", ("N_omega",)),
    "scalar_density_lie_transport": ("omega_star", ("c", "omega_star"), 1, "partial_rho(c^rho omega_star)", ("Lie_omega_star",)),
}
ORIGINS = {
    "odd_vector_half_bracket": ("A_DIFF_GHOST", "c_star"),
    "scalar_lie_transport": ("A_DIFF_WEYL_GHOST", "omega_star"),
    "metric_lie_transport": ("A_DIFF_METRIC", "h_star"),
    "weyl_metric_product": ("A_WEYL_METRIC", "h_star"),
    "metric_antifield_diff_noether": ("A_DIFF_METRIC", "c"),
    "covector_density_lie_transport": ("A_DIFF_GHOST", "c"),
    "weyl_antifield_gradient": ("A_DIFF_WEYL_GHOST", "c"),
    "metric_antifield_trace_pair": ("A_WEYL_METRIC", "omega"),
    "scalar_density_lie_transport": ("A_DIFF_WEYL_GHOST", "omega"),
}
MASTER_TERMS = {
    "A_DIFF_METRIC": "h_star^mu_nu (c^rho partial_rho h_mu_nu + h_rho_nu partial_mu c^rho + h_mu_rho partial_nu c^rho)",
    "A_WEYL_METRIC": "2 h_star^mu_nu omega h_mu_nu",
    "A_DIFF_GHOST": "c_star_mu c^rho partial_rho c^mu",
    "A_DIFF_WEYL_GHOST": "omega_star c^rho partial_rho omega",
}
GRADING = {"h": (0, 0), "c": (-1, 1), "omega": (-1, 1), "h_star": (1, 1), "c_star": (2, 0), "omega_star": (2, 0)}
FALSE_FLAGS = {"SIXTH_METRIC_ANTIFIELD_ROW_PORTABLE", "SUSPENDED_GRADED_POLARIZATION_REPLAYED", "STRICT_SUPPORT_LOCAL_Q2_COMPLETE", "STRICT_FULL_LOCAL_D_ACTION_CERTIFIED", "CLASSICAL_IMPORT_GATE_PASSED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"}


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source = json.loads(SOURCE.read_text())
    imported = json.loads(IMPORTED.read_text())
    minimal = json.loads(MINIMAL.read_text())
    rows = {row["source_atom"]: [(term["coefficient"], tuple(term["factors"])) for term in row["image"]["terms"]] for row in source["differential"]["Q"]["rows"]}
    expected_source = {"g": [(2, ("g", "omega")), (1, ("Lie_g",))], "xi": [(1, ("bracket_xi",))], "omega": [(1, ("Lie_omega",))], "xi_star": [(1, ("N_xi",)), (1, ("Lie_xi_star",))], "omega_star": [(1, ("N_omega",)), (1, ("Lie_omega_star",))]}
    if any(rows.get(key) != item for key, item in expected_source.items()):
        errors.append("source Q sign/term crosswalk drift")
    crosswalk = value.get("source_crosswalk", {})
    if digest(crosswalk.get("source_Q_rows")) != digest(expected_source):
        errors.append("serialized source Q crosswalk drift")
    if crosswalk.get("source_canonical_hashes") != source.get("canonical_hashes") or crosswalk.get("receiver_canonical_hashes") != imported.get("independent_replay", {}).get("canonical_hashes"):
        errors.append("source/receiver canonical hash crosswalk drift")
    if crosswalk.get("master_action") != minimal.get("master_action", {}).get("minimal_master_action"):
        errors.append("displayed master-action crosswalk drift")
    if crosswalk.get("master_term_dictionary") != MASTER_TERMS:
        errors.append("quadratic master-term dictionary drift")
    definitions = value.get("operator_definitions", [])
    by_id = {item.get("operator_id"): item for item in definitions if isinstance(item, dict)}
    if set(by_id) != set(FORMULAS) or len(definitions) != len(by_id):
        errors.append("operator inventory is not exactly nine unique primitives")
    components = value.get("components", [])
    by_component = {item.get("operator_id"): item for item in components if isinstance(item, dict)}
    if set(by_component) != set(FORMULAS) or len(components) != len(by_component):
        errors.append("component/operator bijection failed")
    generator_ledger = value.get("generator_ledger", [])
    ledger_grading = {item.get("symbol"): (item.get("local_tangent_degree"), item.get("Grassmann_parity")) for item in generator_ledger if isinstance(item, dict)}
    if ledger_grading != GRADING or any(item.get("local_tangent_degree") != -item.get("BV_ghost_number") for item in generator_ledger):
        errors.append("local tangent/BV ghost grading ledger drift")
    for operator_id, (output, inputs, coefficient, formula, source_atoms) in FORMULAS.items():
        definition = by_id.get(operator_id, {})
        item = by_component.get(operator_id, {})
        if definition.get("coordinate_formula") != formula:
            errors.append(f"{operator_id}: coordinate formula drift")
        if tuple(definition.get("source_atoms", [])) != source_atoms:
            errors.append(f"{operator_id}: source atom crosswalk drift")
        origin = definition.get("variational_origin", {})
        if (origin.get("master_term_id"), origin.get("Euler_variable")) != ORIGINS[operator_id] or origin.get("BV_coordinate_sign") != "fixed by the receiver-replayed source Q row":
            errors.append(f"{operator_id}: variational origin drift")
        if tuple(definition.get("inputs", [])) != inputs or tuple(item.get("inputs", [])) != inputs:
            errors.append(f"{operator_id}: input roles drift")
        if item.get("output") != output or item.get("coefficient") != coefficient:
            errors.append(f"{operator_id}: output/coefficient drift")
        jets = definition.get("maximum_input_jet_orders", [])
        if len(jets) != 2 or any(type(order) is not int or not 0 <= order <= 1 for order in jets) or sum(jets) > 2:
            errors.append(f"{operator_id}: jet bound failure")
        if item:
            degree = GRADING[item["output"]][0] - sum(GRADING[symbol][0] for symbol in item["inputs"])
            parity = (GRADING[item["output"]][1] - sum(GRADING[symbol][1] for symbol in item["inputs"]) - 1) % 2
            if degree != 1 or parity:
                errors.append(f"{operator_id}: degree/parity failure")
    ledger = value.get("row_ledger", [])
    if [row.get("output") for row in ledger] != list(SYMBOLS):
        errors.append("row ledger order/coverage drift")
    for row in ledger:
        ids = [item.get("component_id") for item in components if item.get("output") == row.get("output")]
        expected_status = "OPEN_HARD_BACH_AND_COTANGENT_ROW" if row.get("output") == "h_star" else "DIAGONAL_POLYNOMIAL_SERIALIZED"
        if row.get("status") != expected_status or row.get("component_ids") != ids or (row.get("output") == "h_star") != (ids == []):
            errors.append(f"row ledger mismatch: {row.get('output')}")
    hashes = value.get("canonical_hashes", {})
    expected_hashes = {"generator_ledger_sha256": digest(generator_ledger), "operator_definitions_sha256": digest(definitions), "components_sha256": digest(components), "row_ledger_sha256": digest(ledger), "proof_gates_sha256": digest(value.get("proof_gates")), "source_crosswalk_sha256": digest(value.get("source_crosswalk"))}
    if hashes != expected_hashes:
        errors.append("canonical hashes do not reproduce")
    flags = value.get("claim_flags", {})
    if flags.get("FIVE_DIAGONAL_Q2_ROWS_PORTABLE") is not True or any(flags.get(flag) is not False for flag in FALSE_FLAGS):
        errors.append("claim boundary flags promoted")
    gates = {row.get("check_id"): row.get("status") for row in value.get("proof_gates", [])}
    expected_gates = {
        "source_sign_and_coefficient_crosswalk": "RECEIVER_REPLAYED",
        "operator_inventory_and_tensor_types": "RECEIVER_REPLAYED",
        "exact_coefficients_and_jet_bounds": "RECEIVER_REPLAYED",
        "five_row_diagonal_completeness": "RECEIVER_REPLAYED",
        "q2_koszul_symmetry": "NOT_REPLAYED",
        "q1_q2_arity_two_nilpotency": "NOT_REPLAYED",
        "D_q2_derivation": "NOT_REPLAYED",
        "BV_cyclicity_q2": "NOT_REPLAYED",
    }
    if gates != expected_gates or len(value.get("proof_gates", [])) != len(gates):
        errors.append("proof gate inventory/status drift")
    for gate in ("q2_koszul_symmetry", "q1_q2_arity_two_nilpotency", "D_q2_derivation", "BV_cyclicity_q2"):
        if gates.get(gate) != "NOT_REPLAYED":
            errors.append(f"{gate}: premature promotion")
    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append(f"provenance drift: {item.get('path')}")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_Q2_KINEMATIC_COTANGENT_AST_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - 9 exact tensor-natural primitives across 5 diagonal q2 rows")
        print("  - h_star, polarization and all interaction identities remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
