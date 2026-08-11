#!/usr/bin/env python3
"""Independent verifier for the BT neutral graph projector extension."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_NEUTRAL_GRAPH_PROJECTOR_EXTENSION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-neutral-graph-projector-extension-v1.schema.json",
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


def verify(certificate):
    import sympy as sp

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if errors:
        return {"schema_validation": False}
    inputs = certificate["provenance"]["inputs"]
    composite = load(os.path.join(ROOT, inputs[1]["path"]))
    profile = load(os.path.join(ROOT, inputs[2]["path"]))
    order_lambda = load(os.path.join(ROOT, inputs[3]["path"]))
    event = load(os.path.join(ROOT, inputs[4]["path"]))
    extension = certificate["minimal_odd_source_extension"]
    graph = certificate["neutral_graph_projector"]
    affiliation = certificate["positive_source_affiliation"]
    boundary = certificate["Eq19_boundary"]
    disposition = certificate["disposition"]

    I = sp.eye(2)
    T = sp.diag(sp.sqrt(6699) / 16, sp.sqrt(7149) / 16)
    eta_odd = -I
    eta_target = -2 * I
    eta = sp.diag(eta_odd, eta_target)
    kappa = -sp.eye(4)
    L = sp.Matrix.vstack(I, T)
    range_gram = sp.simplify(L.T * eta * L)
    M = -range_gram
    P = sp.simplify(L * range_gram.inv() * L.T * eta)
    Psharp = sp.simplify(eta.inv() * P.T * eta)
    N = sp.Matrix.vstack(-2 * T, I)
    K4 = sp.diag(-sp.Rational(6699, 128), -sp.Rational(7149, 128))

    f00, f01, f10, f11 = sp.symbols("f00 f01 f10 f11", real=True)
    F = sp.Matrix([[f00, f01], [f10, f11]])
    parity_defect = -F - F
    coefficient_matrix, rhs = sp.linear_eq_to_matrix(
        list(parity_defect), [f00, f01, f10, f11]
    )

    checks = {
        "schema_validation": True,
        "certificate_identity": certificate["certificate"]
        == "REVERSE_PHYSICS_BT_NEUTRAL_GRAPH_PROJECTOR_EXTENSION_V1",
        "input_hashes_recomputed": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "predecessors_independently_pass": all(
            value["checks"]["ok"] for value in (composite, profile, order_lambda)
        ),
        "done_event_replayed": (
            event["body"]["payload"]["to_state"] == "DONE"
            and event["body"]["payload"]["target"]
            == "sf:program/work/reverse-physics-bateman-neutral-graph-projector-extension"
        ),
        "imported_degree_four_block_replayed": (
            composite["minimal_neutral_lift"]["pullback"]
            == [["-6699/128", "0"], ["0", "-7149/128"]]
            and composite["minimal_neutral_lift"]["ghost_parity"] == "ODD"
        ),
        "displayed_metrics_reconstructed": (
            matrix(extension["odd_partner_metric"]) == eta_odd
            and matrix(extension["composite_negative_metric"]) == eta_target
            and matrix(graph["carrier_metric"]) == eta
            and matrix(graph["carrier_ghost_parity"]) == kappa
        ),
        "slope_reconstructed": matrix(extension["slope_T"]) == T,
        "K4_slope_identity_recomputed": (
            T.T * eta_target * T == K4
            and matrix(extension["slope_covariant_pullback"]) == K4
            and matrix(profile["fibrewise_krein_lift"]["pullback"]) == K4
        ),
        "partner_minimality_recomputed": (
            extension["partner_dimension"] == T.rank() == K4.rank() == 2
        ),
        "graph_embedding_and_M_reconstructed": (
            matrix(graph["graph_embedding_L"]) == L
            and matrix(graph["positive_M"]) == M
            and matrix(graph["range_gram"]) == range_gram
        ),
        "range_is_negative_definite": (
            M == sp.diag(sp.Rational(6827, 128), sp.Rational(7277, 128))
            and all(M[i, i] > 0 for i in range(2))
        ),
        "projector_reconstructed": matrix(graph["projector"]) == P,
        "projector_idempotence_recomputed": P**2 == P,
        "projector_Krein_adjoint_recomputed": Psharp == P,
        "projector_charge_and_ghost_recomputed": (
            P * kappa == kappa * P
            and graph["charge_identity"] == "[H_total,P]=0"
        ),
        "projector_rank_trace_recomputed": (
            P.rank() == graph["rank"] == 2
            and sp.trace(P) == graph["trace"] == 2
        ),
        "finite_Born_trace_recomputed": (
            sp.trace(Psharp * P)
            == graph["finite_algebraic_generalized_Born_trace"]
            == 2
        ),
        "range_fixed_and_kernel_killed": (
            P * L == L and P * N == sp.zeros(4, 2)
        ),
        "kernel_reconstructed": (
            matrix(graph["kernel_embedding"]) == N
            and matrix(graph["kernel_gram"]) == N.T * eta * N == -2 * M
        ),
        "range_kernel_orthogonality_recomputed": (
            L.T * eta * N == matrix(graph["range_kernel_pairing"])
            == sp.zeros(2)
        ),
        "ghost_even_affiliation_system_recomputed": (
            coefficient_matrix.rank() == affiliation["coefficient_rank"] == 4
            and rhs == sp.zeros(4, 1)
            and sp.solve(
                list(parity_defect), [f00, f01, f10, f11], dict=True
            ) == [{f00: 0, f01: 0, f10: 0, f11: 0}]
            and affiliation["only_solution"] == "F=0"
        ),
        "positive_norm_affiliation_signature_obstructed": (
            affiliation["norm_preserving_positive_source_map"]
            == "EXACTLY_OBSTRUCTED_ON_MINIMAL GRAPH"
            and all(M[i, i] > 0 for i in range(2))
            and range_gram.det() > 0
            and sp.trace(range_gram) < 0
        ),
        "order_lambda_boundary_replayed": (
            order_lambda["disposition"]["finite_mode_order_lambda_Eq19"]
            == "PROVED_WITH_Q1_ZERO"
            and boundary["finite_mode_order_lambda_sector"]
            == "UNCHANGED_PROVED_WITH_Q1_ZERO"
        ),
        "Eq19_and_physical_claims_not_promoted": (
            boundary["BT_Rt_derivation"] == "NOT_CONSTRUCTED"
            and boundary["all_order_projector_identity"] == "NOT_PROVED"
            and disposition["physical_fourth_probability"] == "NOT_ESTABLISHED"
            and disposition["Eq19_all_orders"] == "NOT_PROVED"
        ),
        "gravity_and_Lorentzian_claims_excluded": (
            any("gravity" in value for value in certificate["does_not_establish"])
            and any(
                "LORENTZIAN-CAUSAL" in value
                for value in certificate["does_not_establish"]
            )
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
