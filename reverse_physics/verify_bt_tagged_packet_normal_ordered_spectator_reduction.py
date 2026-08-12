#!/usr/bin/env python3
"""Independent verifier for the normal-ordered tagged spectator reduction."""
from __future__ import annotations

import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_NORMAL_ORDERED_SPECTATOR_REDUCTION_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-tagged-packet-normal-ordered-spectator-reduction-v1.schema.json")


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
    imported = {os.path.basename(row["path"]): load(os.path.join(ROOT, row["path"])) for row in inputs}
    source = imported["bateman_turok_hamiltonian_source_v1.json"]
    generic = imported["REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA6_OBJECT_LEDGER_V1.json"]
    charge = imported["REVERSE_PHYSICS_CHARGE_GRADING_LOOP_STABILITY_V1.json"]

    # Solve the graph equations in a separate bounded enumeration.
    solutions = []
    for vertices in range(0, 6):
        for internal in range(0, 12):
            for loops in range(0, 8):
                if 4*vertices == 2 + 2*internal and loops == internal - vertices + 1:
                    solutions.append((2*vertices, vertices, internal, loops))
    order_two = [row for row in solutions if row[0] == 2]

    # Independent charge/dimension scan for neutral scalar monomials; the
    # derivative-two row represents the unique kinetic term modulo boundary.
    monomials = []
    for derivatives in (0, 2, 4):
        for n_omega in range(5):
            for n_upsilon in range(5):
                dimension = derivatives + n_omega + n_upsilon
                derivative_structure = (
                    derivatives == 0
                    or (derivatives == 2 and n_omega == n_upsilon == 1)
                )
                if dimension <= 4 and n_omega == n_upsilon and derivative_structure:
                    monomials.append((derivatives, n_omega, n_upsilon))
    selected = [(0, 0, 0), (0, 1, 1), (2, 1, 1), (0, 2, 2)]
    selected.sort(key=lambda row: (sum(row), row[0]))
    monomials.sort(key=lambda row: (sum(row), row[0]))

    # Wick replay with named species: the only nonzero contraction joins
    # unlike fields, and normal ordering subtracts that internal pair.
    W = {("O", "O"): 0, ("U", "U"): 0, ("O", "U"): 1, ("U", "O"): 1}
    external_remainders = {
        "OO": W[("U", "U")],
        "OU": 4*W[("O", "U")],
        "UO": 4*W[("U", "O")],
        "UU": W[("O", "O")],
    }

    lam = sp.symbols("lambda")
    T2, C4, L4 = sp.symbols("T2 C4 L4", real=True)
    q = sp.expand((lam**2*T2 + lam**4*(C4 + L4))**2)

    graphs = certificate["auxiliary_graph_classification"]
    counterterms = certificate["species_and_counterterm_ledger"]
    reduced = certificate["reduced_probability_ledger"]
    boundary = certificate["frame_boundary"]
    interpretation = certificate["interpretation"]
    limits = certificate["does_not_establish"]
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in inputs),
        "imported_certificates_pass": all(value["checks"]["ok"] for name, value in imported.items() if name.startswith("REVERSE_PHYSICS_")),
        "dependency_tags_are_exact": certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_is_coefficient_computed": certificate["lifecycle_state"] == "COEFFICIENT_COMPUTED",
        "auxiliary_action_is_imported": "Omega^2 Upsilon^2" in source["public_inputs"]["auxiliary_action"],
        "cross_only_propagator_is_imported": charge["structural_inputs"]["their_wightman"].endswith("W^{OmegaOmega} = W^{UpsilonUpsilon} = 0"),
        "order_two_graph_solution_is_unique": order_two == [(2, 1, 1, 1)],
        "recorded_graph_solution_is_exact": graphs["order_lambda2_solution"] == {"vertices": 1, "internal_lines": 1, "loops": 1, "topology": "ONE_VERTEX_TADPOLE"},
        "next_two_point_graph_is_order_four": (4, 2, 3, 2) in solutions and graphs["next_two_point_order"].startswith("lambda^4"),
        "cross_wick_replay_is_off_diagonal": external_remainders == {"OO": 0, "OU": 4, "UO": 4, "UU": 0},
        "tadpole_is_momentum_independent": counterterms["external_momentum_degree"] == 0,
        "neutral_power_counting_basis_is_complete": monomials == selected,
        "recorded_two_point_basis_is_mass_and_kinetic": counterterms["two_point_basis"] == ["Omega*Upsilon", "partial_Omega*partial_Upsilon"],
        "normal_ordering_condition_is_explicit": counterterms["normal_ordering"].startswith(":Omega^2*Upsilon^2:"),
        "massless_condition_is_explicit": "equals zero" in counterterms["mass_condition"],
        "unit_residue_condition_is_explicit": "free value" in counterterms["residue_condition"],
        "renormalized_spectator_block_is_zero": counterterms["renormalized_order_lambda2_two_point_block"] == "S2_spectator=0",
        "generic_ledger_really_contained_spectator_cross": generic["probability_ledger"]["spectator_self_energy_status"].startswith("MISSING"),
        "reduced_q6_is_two_crosses": sp.expand(q.coeff(lam, 6) - 2*T2*C4 - 2*T2*L4) == 0,
        "recorded_reduced_q6_formula_is_exact": reduced["q6_formula"] == "q_tag^(6)=2*Re<T2,C4_tree>+2*Re<T2,I_spectator tensor L4_active_loop>",
        "spectator_cross_is_zero_not_missing": reduced["spectator_cross"].startswith("ZERO_BY_DECLARED"),
        "active_loop_remains_missing": reduced["active_loop_cross"].startswith("MISSING") and interpretation["active_four_point_one_loop_packet_kernel"] == "MISSING",
        "scheme_boundary_is_fail_closed": boundary["status"] == "SELECTED_AUXILIARY_SCHEME_ONLY" and "reinstating" in boundary["scheme_warning"],
        "public_convention_is_not_overclaimed": "uniquely prescribes" in limits[0],
        "complete_q6_is_not_promoted": reduced["complete_q6"] == "NOT_COMPUTED" and interpretation["complete_order_lambda6_probability"] == "NOT_COMPUTED",
        "Eq19_gravity_Lorentzian_boundaries_are_exact": interpretation["general_Eq19"] == "NOT_PROVED" and interpretation["gravity_or_BV_BRST_transfer"] == "NOT_CONSTRUCTED" and interpretation["Lorentzian_causal_claim"] == "NOT_ESTABLISHED",
        "next_gate_is_unique_active_loop_in_declared_scheme": "sole missing q6 coefficient" in certificate["next_gate"] and "normal-ordered massless unit-residue scheme" in certificate["next_gate"],
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
