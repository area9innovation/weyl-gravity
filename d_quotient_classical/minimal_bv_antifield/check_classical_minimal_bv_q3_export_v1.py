#!/usr/bin/env python3
"""Independent structural checker for the classical minimal-BV q3 export."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/minimal_bv_antifield"
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1.json"
PARENT = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
ACTION = HERE / "foundation/action_normalization.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def recorded_digest(value: Mapping[str, Any]) -> str:
    return digest({key: item for key, item in value.items() if key != "sha256"})


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    parent = json.loads(PARENT.read_text())
    action = json.loads(ACTION.read_text())
    if value.get("result_id") != "CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1" or value.get("result_kind") != "AUTHORITATIVE_ACTION_DERIVED_MINIMAL_BV_ARITY_THREE_EXPORT":
        errors.append("result identity or kind drift")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"] or value.get("lifecycle") != "CLASSIFIED":
        errors.append("dependency tag or lifecycle drift")
    if value.get("scope", {}).get("carrier_dimension") != 6 or value.get("scope", {}).get("coefficient_field") != "Q":
        errors.append("minimal carrier or exact coefficient field drift")
    if value.get("scope", {}).get("action_normalization") != action.get("Euler_coordinate"):
        errors.append("action normalization drift")

    ast = value.get("natural_operator_ast", {})
    nodes = ast.get("nodes", [])
    operations = [item.get("operation") for item in nodes]
    expected_operations = [
        "metric_three_parameter_family", "inverse_metric", "levi_civita_geometry",
        "schouten_and_weyl_4d", "cotton_4d", "bach_4d",
        "raise_symmetric_two_tensor", "absolute_metric_volume_density",
        "densitize_and_scale", "mixed_third_frechet_coefficient",
    ]
    if operations != expected_operations or ast.get("root_node") != "q3_hstar_hhh":
        errors.append("natural q3 AST coverage or root drift")
    if nodes and (nodes[-1].get("parameters", {}).get("coefficient") != "[a*b*c]" or nodes[-1].get("parameters", {}).get("hidden_factorial") is not False):
        errors.append("third Frechet convention drift")
    if ast.get("canonical_node_sha256") != digest(nodes):
        errors.append("natural q3 AST node hash drift")
    seen: set[str] = set()
    for node in nodes:
        if node.get("node_id") in seen or any(item not in seen for item in node.get("inputs", [])):
            errors.append("natural q3 AST is not a topological DAG")
            break
        seen.add(node.get("node_id"))

    ledger = value.get("master_action_degree_ledger", [])
    master_terms = action.get("minimal_master_terms", [])
    if len(ledger) != 4 or [item.get("master_action_summand") for item in ledger[1:]] != master_terms:
        errors.append("master-action degree ledger does not exhaust the pinned summands")
    if not ledger or ledger[0].get("q3_contribution") != "D^3 E_g(h1,h2,h3)" or any(item.get("maximum_Q_taylor_arity") != 2 for item in ledger[1:]):
        errors.append("q3 degree derivation drift")

    support = value.get("minimal_q3_support", {})
    rows = support.get("rows", [])
    symbols = [item.get("symbol") for item in parent.get("generators", [])]
    if [item.get("output_generator") for item in rows] != symbols:
        errors.append("six-row q3 support carrier drift")
    nonzero = [item for item in rows if item.get("q3_status") == "NONZERO_NATURAL_OPERATOR"]
    if len(nonzero) != 1 or nonzero[0].get("output_generator") != "g_star" or nonzero[0].get("accepted_input_generators") != ["g", "g", "g"]:
        errors.append("unique metric-Euler q3 row drift")
    zero = [item for item in rows if item.get("q3_status") == "IDENTICALLY_ZERO_BY_MASTER_ACTION_DEGREE"]
    if len(zero) != 5 or support.get("nonzero_row_count") != 1 or support.get("nonzero_ordered_component_count") != 1:
        errors.append("zero-row classification drift")
    if "intersect" not in support.get("support_rule", "") or support.get("maximum_metric_jet_order") != 4:
        errors.append("q3 locality or differential-order boundary drift")
    if support.get("sha256") != recorded_digest(support):
        errors.append("q3 support digest drift")

    authority = value.get("authority_chain", {})
    if authority.get("source_action") != action.get("result_id") or authority.get("source_minimal_bv_export") != parent.get("result_id"):
        errors.append("classical authority chain drift")
    if authority.get("source_Q_squared_zero_status") != "VERIFIED" or authority.get("not_a_competing_BV_complex") is not True or len(authority.get("derivation", [])) != 4:
        errors.append("nilpotency or no-competing-complex boundary drift")

    flags = value.get("claim_flags", {})
    for name in ("AUTHORITATIVE_MINIMAL_BV_Q3_EXPORTED", "ARBITRARY_THREE_METRIC_INPUTS_DECLARED", "ALL_SIX_MINIMAL_OUTPUT_ROWS_CLASSIFIED", "SUPPORT_LOCALITY_DECLARED"):
        if flags.get(name) is not True:
            errors.append(f"required q3 export flag false: {name}")
    for name in ("EXACT_COMPONENT_RECEIVER_REPLAYED", "ARITY_THREE_Q_SQUARED_IDENTITY_REPLAYED", "CYCLIC_QUARTIC_VERTEX_REPLAYED", "STRICT_386_NONMINIMAL_Q3_STABILIZED", "LORENTZIAN_CAUSAL_CERTIFIED", "QME_RESTORED"):
        if flags.get(name) is not False:
            errors.append(f"premature promotion: {name}")

    expected_hashes = {
        "natural_operator_ast_sha256": digest(ast),
        "master_action_degree_ledger_sha256": digest(ledger),
        "minimal_q3_support_sha256": digest(support),
        "authority_chain_sha256": digest(authority),
    }
    if value.get("canonical_hashes") != expected_hashes:
        errors.append("canonical hashes do not reproduce")
    inputs = value.get("provenance", {}).get("inputs", [])
    for item in inputs:
        path = ROOT / item.get("path", "")
        if not path.is_file() or item.get("sha256") != sha(path):
            errors.append(f"input provenance drift: {item.get('path')}")
    if len(value.get("does_not_establish", [])) < 6:
        errors.append("fail-closed boundary ledger shortened")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1_CHECK: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - all six minimal rows classified from the pinned master action")
        print("  - component replay, arity-three identity, cyclicity and 386 stabilization remain open")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
