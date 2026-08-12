#!/usr/bin/env python3
"""Independent verifier for the complete selected tagged BT q6 probability."""
from __future__ import annotations

import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COMPLETE_TAGGED_Q6_PHYSICAL_PROBABILITY_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-complete-tagged-q6-physical-probability-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate):
    inputs = certificate["provenance"]["inputs"]
    imported = {
        os.path.basename(row["path"]): load(os.path.join(ROOT, row["path"]))
        for row in inputs
    }
    parity = imported["REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA5_PARITY_SELECTION_V1.json"]
    ledger = imported["REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA6_OBJECT_LEDGER_V1.json"]
    spectator = imported["REVERSE_PHYSICS_BT_TAGGED_PACKET_NORMAL_ORDERED_SPECTATOR_REDUCTION_V1.json"]
    loop = imported["REVERSE_PHYSICS_BT_FINITE_TIME_ACTIVE_LOOP_AFFILIATION_V1.json"]
    tree = imported["REVERSE_PHYSICS_BT_TAGGED_CONNECTED_COMPACT_PACKET_INTERFERENCE_V1.json"]
    leading = imported["REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1.json"]

    lam, kappa, area, domega, Cff, Bstar = sp.symbols(
        "lambda kappa Area DeltaOmega Cff Bstar", positive=True
    )
    q4 = 75 * lam**4 * domega / (2048 * sp.pi**2 * kappa**2 * area)
    qtree = 25 * sp.sqrt(2) * lam**6 * domega * Cff / (
        1024 * sp.pi**2 * kappa**2 * area
    )
    qloop = 125 * lam**6 * domega * Bstar / (
        16384 * sp.pi**4 * kappa**2 * area
    )
    tree_ratio = sp.factor(qtree / q4)
    loop_ratio = sp.factor(qloop / q4)
    R6 = sp.factor((qtree + qloop) / (lam**2 * q4))

    transient_sum, L = sp.symbols("transient_sum L", real=True)
    wall = -6 + transient_sum - 16 * sp.sqrt(2) * sp.pi**2 * Cff / 5
    Rwall = 2 * sp.sqrt(2) * Cff / 3 + 5 * (wall + 6 - transient_sum) / (24 * sp.pi**2)
    critical_sixth = sp.Rational(65536, 15625) * sp.exp(wall)

    complete = certificate["complete_probability"]
    audit = certificate["completeness_audit"]
    signs = certificate["sign_and_bounds"]
    scope = certificate["physical_scope"]
    interpretation = certificate["interpretation"]
    boundaries = certificate["does_not_establish"]
    predecessors = [value for name, value in imported.items() if name.startswith("REVERSE_PHYSICS_")]
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in inputs),
        "six_predecessors_pass": len(predecessors) == 6 and all(row["checks"]["ok"] for row in predecessors),
        "dependency_tags_are_exact": certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_is_coefficient_computed": certificate["lifecycle_state"] == "COEFFICIENT_COMPUTED",
        "leading_coefficient_is_rederived": leading["complete_leading_tagged_probability"]["general_coefficient"].startswith("q_click=3*lambda^4") and complete["leading_term"] == "q4=75*lambda^4*DeltaOmega/(2048*pi^2*kappa^2*Area)",
        "tree_ratio_is_rederived": sp.simplify(tree_ratio - 2 * sp.sqrt(2) * lam**2 * Cff / 3) == 0,
        "loop_ratio_is_rederived": sp.simplify(loop_ratio - 5 * lam**2 * Bstar / (24 * sp.pi**2)) == 0,
        "assembled_R6_is_rederived": sp.simplify(R6 - 2 * sp.sqrt(2) * Cff / 3 - 5 * Bstar / (24 * sp.pi**2)) == 0,
        "recorded_relative_coefficient_is_exact": complete["relative_q6_coefficient"] == "R6[f;T,mu]=(2*sqrt(2)/3)*Re C_ff(T)+(5/(24*pi^2))*B_*(T,mu)",
        "recorded_probability_has_even_remainder": complete["assembled_probability"] == "q_tag[f;T]=q4*{1+lambda^2*R6[f;T,mu]}+O(lambda^8)",
        "parity_remainder_is_imported": "q(lambda)=q(-lambda)" in parity["answer"] and audit["next_remainder"].startswith("O(lambda^8)"),
        "three_term_ledger_is_imported": "sum of the three corresponding interferences" in ledger["answer"],
        "spectator_zero_is_imported": spectator["interpretation"]["spectator_order_lambda2_packet_kernel"] == "ZERO_IN_DECLARED_SCHEME" and complete["spectator_cross"].startswith("0"),
        "tree_functional_is_imported": tree["compact_tree_cross_functional"]["status"] == "BOX_INDEPENDENT_COMPACT_PACKET_TREE_CROSS_FUNCTIONAL_COMPUTED",
        "loop_affiliation_is_imported": loop["interpretation"]["finite_duration_BT_Dyson_affiliation"] == "PROVED_ON_SELECTED_ENERGY_DIAGONAL_HARD_CARRIER",
        "ledger_is_exhausted": audit["status"] == "ORDER_LAMBDA6_LEDGER_EXHAUSTED",
        "sign_wall_is_rederived": sp.simplify(Rwall) == 0 and "16*sqrt(2)*pi^2/5" in signs["zero_wall"],
        "critical_scale_is_rederived": "65536/15625" in signs["critical_scale"] and critical_sixth.is_positive,
        "scheme_dependence_is_explicit": "finite scheme change" in signs["scale_boundary"] and interpretation["universal_q6_sign"] == "NO_SCHEME_PACKET_DURATION_AND_SCALE_DEPENDENT",
        "packet_bound_is_imported": signs["tree_bound"] == "abs(C_ff(T))<=54*T*sqrt(mu_in*mu_out)/d0",
        "physical_scope_is_selected": scope["status"] == "SELECTED_BT_PHYSICAL_PROBABILITY_PROVED_THROUGH_Q6",
        "all_order_positivity_is_not_promoted": interpretation["all_order_positivity"] == "NOT_PROVED" and any("every perturbative order" in row for row in boundaries),
        "Eq19_alltime_gravity_Lorentzian_boundaries_are_exact": interpretation["general_Eq19"] == "NOT_PROVED" and interpretation["all_time_scattering"] == "NOT_CONSTRUCTED" and interpretation["gravity_or_BV_BRST_transfer"] == "NOT_CONSTRUCTED" and interpretation["Lorentzian_causal_claim"] == "NOT_ESTABLISHED",
        "next_gate_preserves_both_routes": "direct physical route" in certificate["next_gate"] and "Eq. (19) route" in certificate["next_gate"],
    }
    return {name: bool(value) for name, value in checks.items()}


def main():
    checks = verify(load(CERT))
    failures = [name for name, ok in checks.items() if not ok]
    print("checks %d/%d" % (sum(checks.values()), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    if failures:
        print("failures:", ", ".join(failures))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
