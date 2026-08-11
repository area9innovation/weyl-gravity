#!/usr/bin/env python3
"""Independent verifier for the BT public-Fock odd-source affiliation."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PUBLIC_FOCK_ODD_SOURCE_AFFILIATION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-public-fock-odd-source-affiliation-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def matrix(value):
    import sympy as sp

    return sp.Matrix([[sp.sympify(entry) for entry in row] for row in value])


def independent_occupation_matrices():
    import sympy as sp

    occ = ((2, 0), (1, 1), (0, 2))
    labels = tuple(itertools.product(occ, repeat=2))
    index = {label: i for i, label in enumerate(labels)}
    gram = sp.zeros(len(labels))
    swap = sp.zeros(len(labels))
    for col, (alpha, beta) in enumerate(labels):
        swap[index[(beta, alpha)], col] = 1
        partner = (beta, alpha)
        row = index[partner]
        gram[row, col] = math.prod(
            math.factorial(value) for value in alpha + beta
        )
    raw = sp.zeros(9, 2)
    raw[index[(occ[0], occ[1])], 0] = 1
    raw[index[(occ[1], occ[0])], 0] = -1
    raw[index[(occ[1], occ[2])], 1] = 1
    raw[index[(occ[2], occ[1])], 1] = -1
    return gram, swap, raw


def verify(certificate):
    import sympy as sp

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if errors:
        return {"schema_validation": False}
    inputs = certificate["provenance"]["inputs"]
    moller = load(os.path.join(ROOT, inputs[1]["path"]))
    charge = load(os.path.join(ROOT, inputs[2]["path"]))
    composite = load(os.path.join(ROOT, inputs[3]["path"]))
    graph = load(os.path.join(ROOT, inputs[4]["path"]))
    order_lambda = load(os.path.join(ROOT, inputs[5]["path"]))
    event = load(os.path.join(ROOT, inputs[6]["path"]))
    public = certificate["public_neutral_degree_four_sector"]
    transport = certificate["complement_to_public_symmetric_power"]
    realization = certificate["graph_source_realization"]
    boundary = certificate["Eq19_boundary"]
    disposition = certificate["disposition"]

    rho = sp.Rational(819, 4000)
    J = sp.Matrix([[0, 1], [1, 0]])
    C = sp.Matrix([[-rho, -1], [0, 1]])
    S = sp.Matrix([[1, 1], [0, -rho]])
    W, kappa, raw = independent_occupation_matrices()
    Wsel = raw / 2
    G = rho**8 * W
    Usel = raw / (sp.sqrt(2) * rho**4)
    phi4 = rho**4 * sp.eye(9)
    selected_forward = sp.sqrt(2) * sp.eye(2)
    selected_inverse = sp.eye(2) / sp.sqrt(2)
    public_gram = Wsel.T * W * Wsel
    complement_gram = Usel.T * G * Usel

    checks = {
        "schema_validation": True,
        "certificate_identity": certificate["certificate"]
        == "REVERSE_PHYSICS_BT_PUBLIC_FOCK_ODD_SOURCE_AFFILIATION_V1",
        "input_hashes_recomputed": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "predecessors_independently_pass": all(
            value["checks"]["ok"]
            for value in (moller, charge, composite, graph, order_lambda)
        ),
        "done_event_replayed": (
            event["body"]["payload"]["to_state"] == "DONE"
            and event["body"]["payload"]["target"]
            == "sf:program/work/reverse-physics-bateman-public-fock-odd-source-affiliation"
        ),
        "public_metric_and_charge_transport_replayed": (
            matrix(public["one_particle_metric_J"]) == J
            and matrix(transport["missing_leg_C"]) == C
            and matrix(transport["complement_charge_basis_S"]) == S
            and C * S == -rho * sp.eye(2)
        ),
        "public_degree_four_gram_reconstructed": (
            matrix(public["gram"]) == W
            and W.T == W
            and W.det() != 0
        ),
        "public_ghost_parity_reconstructed": (
            matrix(public["ghost_parity"]) == kappa
            and kappa**2 == sp.eye(9)
            and kappa.T * W * kappa == W
        ),
        "positive_fundamental_metric_reconstructed": (
            matrix(public["positive_fundamental_metric"]) == W * kappa
            and W * kappa == sp.diag(4, 2, 4, 2, 1, 2, 4, 2, 4)
        ),
        "inertia_recomputed_from_parity_eigenspaces": (
            (sp.eye(9) + kappa).rank() == public["inertia"][0] == 6
            and (sp.eye(9) - kappa).rank() == public["inertia"][1] == 3
        ),
        "public_selected_columns_reconstructed": (
            matrix(public["selected_raw_columns"]) == raw
            and matrix(public["selected_normalized_columns"]) == Wsel
        ),
        "public_selected_gram_recomputed": (
            public_gram == -sp.eye(2)
            and matrix(public["selected_gram"]) == public_gram
        ),
        "public_selected_charge_and_parity_recomputed": (
            kappa * Wsel == -Wsel
            and public["selected_total_charge"] == [0, 0]
            and matrix(public["selected_ghost_parity"]) == -sp.eye(2)
        ),
        "complement_gram_reconstructed": (
            matrix(transport["complement_degree_four_gram"]) == G
            and matrix(transport["complement_selected_normalized_columns"])
            == Usel
            and matrix(transport["complement_selected_gram"])
            == complement_gram
            == -2 * sp.eye(2)
        ),
        "full_Sym4_map_reconstructed": (
            matrix(transport["Sym4_C_in_charge_basis"]) == phi4
            and phi4.T * W * phi4 == G
            and phi4 * kappa == kappa * phi4
        ),
        "selected_forward_map_recomputed": (
            phi4 * Usel == Wsel * selected_forward
            and matrix(transport["selected_forward_matrix_U_to_W"])
            == selected_forward
            and selected_forward.T * public_gram * selected_forward
            == complement_gram
        ),
        "selected_inverse_map_recomputed": (
            matrix(transport["selected_inverse_matrix_W_to_U"])
            == selected_inverse
            and selected_inverse * selected_forward == sp.eye(2)
            and selected_inverse.T * complement_gram * selected_inverse
            == public_gram
        ),
        "selected_map_charge_and_parity_recomputed": (
            transport["selected_map_total_charge"] == 0
            and transport["selected_map_ghost_parity"] == "EVEN"
            and selected_inverse * (-sp.eye(2))
            == (-sp.eye(2)) * selected_inverse
        ),
        "graph_source_metric_matches_public_sector": (
            matrix(realization["abstract_graph_odd_source_metric"])
            == matrix(realization["public_selected_metric"])
            == public_gram
            and graph["minimal_odd_source_extension"]["odd_partner_metric"]
            == realization["public_selected_metric"]
        ),
        "graph_slope_not_conflated_with_carrier_map": (
            matrix(realization["graph_slope_T"])
            != matrix(transport["selected_inverse_matrix_W_to_U"])
            and realization["graph_slope_status"] == "NOT_DERIVED_BY_SYM4_C"
        ),
        "positive_scalar_source_obstruction_preserved": (
            realization["original_scalar_positive_source_status"]
            == "DIRECT_AFFILIATION_REMAINS_EXACTLY_OBSTRUCTED"
            and graph["positive_source_affiliation"][
                "norm_preserving_positive_source_map"
            ]
            == "EXACTLY_OBSTRUCTED_ON_MINIMAL GRAPH"
        ),
        "order_lambda_boundary_replayed": (
            order_lambda["disposition"]["finite_mode_order_lambda_Eq19"]
            == "PROVED_WITH_Q1_ZERO"
            and boundary["finite_mode_order_lambda_sector"]
            == "UNCHANGED_PROVED_WITH_Q1_ZERO"
        ),
        "Rt_and_Eq19_claims_not_promoted": (
            boundary["graph_slope_from_public_Rt"] == "NOT_DERIVED"
            and boundary["nonlinear_Rt_excitation_of_degree_four_sector"]
            == "NOT_COMPUTED"
            and boundary["all_order_projector_identity"] == "NOT_PROVED"
            and disposition["Eq19_all_orders"] == "NOT_PROVED"
        ),
        "physical_claims_not_promoted": (
            disposition["physical_fourth_probability"] == "NOT_ESTABLISHED"
            and any("LORENTZIAN-CAUSAL" in row for row in certificate["does_not_establish"])
            and any("gravity" in row for row in certificate["does_not_establish"])
        ),
    }
    return {name: bool(value) for name, value in checks.items()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print(("PASS" if ok else "FAIL") + ": " + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
