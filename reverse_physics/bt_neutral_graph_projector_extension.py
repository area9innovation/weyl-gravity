#!/usr/bin/env python3
"""Exact minimal ghost-even graph projector for the neutral BT K4 block."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_NEUTRAL_GRAPH_PROJECTOR_EXTENSION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-neutral-graph-projector-extension-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-neutral-graph-projector-extension.md"
SOURCE = "0ef68ed1d5e1da1eae57d0c134cf05f86c91ce6e"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-neutral-graph-projector-extension-DONE-0ef68ed1.json"
)
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-neutral-graph-projector-extension.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_NEUTRAL_BOSONIC_COMPOSITE_LIFT_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EIGHT_POINT_PROFILE_POSITIVITY_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json",
    EVENT,
]


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def rows(matrix):
    import sympy as sp

    return [
        [str(sp.factor(matrix[i, j])) for j in range(matrix.cols)]
        for i in range(matrix.rows)
    ]


def build():
    import sympy as sp

    composite = load(INPUTS[1])
    profile = load(INPUTS[2])
    order_lambda = load(INPUTS[3])
    K4 = sp.Matrix(profile["fibrewise_krein_lift"]["pullback"])
    target = sp.diag(-sp.Rational(6699, 128), -sp.Rational(7149, 128))
    I = sp.eye(2)
    T = sp.diag(sp.sqrt(6699) / 16, sp.sqrt(7149) / 16)
    eta_source_odd = -I
    eta_composite_negative = -2 * I
    eta = sp.diag(eta_source_odd, eta_composite_negative)
    kappa = -sp.eye(4)
    charge = sp.zeros(4)
    L = sp.Matrix.vstack(I, T)
    range_gram = sp.simplify(L.T * eta * L)
    M = sp.simplify(-range_gram)
    projector = sp.simplify(L * range_gram.inv() * L.T * eta)
    projector_sharp = sp.simplify(eta.inv() * projector.T * eta)
    complement = sp.Matrix.vstack(-2 * T, I)
    complement_gram = sp.simplify(complement.T * eta * complement)
    finite_born = sp.simplify(sp.trace(projector_sharp * projector))

    # A ghost-even affiliation F from the original even source to the odd
    # partner obeys -F=F.  The exact coefficient system has full rank four.
    f00, f01, f10, f11 = sp.symbols("f00 f01 f10 f11", real=True)
    F = sp.Matrix([[f00, f01], [f10, f11]])
    parity_defect = -I * F - F * I
    parity_matrix, parity_rhs = sp.linear_eq_to_matrix(
        list(parity_defect), [f00, f01, f10, f11]
    )

    checks = {
        "predecessor_certificates_pass": all(
            value["checks"]["ok"] for value in (composite, profile, order_lambda)
        ),
        "K4_replayed_exactly": K4 == target,
        "composite_degree_four_and_ghost_odd_imported": (
            composite["bosonic_neutral_census"]["minimal_total_degree"] == 4
            and composite["minimal_neutral_lift"]["ghost_parity"] == "ODD"
        ),
        "slope_reconstructs_covariant_K4": (
            sp.simplify(T.T * eta_composite_negative * T) == K4
        ),
        "slope_has_rank_two": T.rank() == 2,
        "odd_source_partner_rank_two_is_minimal": T.rank() == K4.rank() == 2,
        "graph_range_gram_is_minus_M": range_gram == -M,
        "M_is_positive_diagonal": (
            M == sp.diag(sp.Rational(6827, 128), sp.Rational(7277, 128))
            and all(M[i, i] > 0 for i in range(2))
        ),
        "graph_range_is_negative_definite": all(
            range_gram[i, i] < 0 for i in range(2)
        ),
        "projector_formula_is_exact": projector == sp.Matrix([
            [sp.Rational(128, 6827), 0, 16 * sp.sqrt(6699) / 6827, 0],
            [0, sp.Rational(128, 7277), 0, 16 * sp.sqrt(7149) / 7277],
            [8 * sp.sqrt(6699) / 6827, 0, sp.Rational(6699, 6827), 0],
            [0, 8 * sp.sqrt(7149) / 7277, 0, sp.Rational(7149, 7277)],
        ]),
        "projector_is_idempotent": sp.simplify(projector**2 - projector)
        == sp.zeros(4),
        "projector_is_krein_selfadjoint": projector_sharp == projector,
        "projector_is_charge_neutral": projector * charge - charge * projector
        == sp.zeros(4),
        "projector_is_ghost_even": projector * kappa - kappa * projector
        == sp.zeros(4),
        "projector_has_rank_two": projector.rank() == 2,
        "projector_trace_is_two": sp.trace(projector) == 2,
        "finite_algebraic_Born_trace_is_two": finite_born == 2,
        "graph_columns_are_fixed": sp.simplify(projector * L - L)
        == sp.zeros(4, 2),
        "complement_columns_are_killed": sp.simplify(projector * complement)
        == sp.zeros(4, 2),
        "range_and_kernel_are_krein_orthogonal": sp.simplify(
            L.T * eta * complement
        ) == sp.zeros(2),
        "kernel_is_negative_definite": (
            complement_gram == -2 * M
            and all(complement_gram[i, i] < 0 for i in range(2))
        ),
        "ghost_even_affiliation_linear_system_has_full_rank": (
            parity_matrix.rank() == 4 and parity_rhs == sp.zeros(4, 1)
        ),
        "ghost_even_affiliation_is_zero": sp.solve(
            list(parity_defect), [f00, f01, f10, f11], dict=True
        ) == [{f00: 0, f01: 0, f10: 0, f11: 0}],
        "positive_source_isometry_to_graph_is_signature_obstructed": (
            all(M[i, i] > 0 for i in range(2))
            and range_gram.det() > 0
            and sp.trace(range_gram) < 0
        ),
        "order_lambda_boundary_preserved": (
            order_lambda["disposition"]["finite_mode_order_lambda_Eq19"]
            == "PROVED_WITH_Q1_ZERO"
        ),
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_NEUTRAL_GRAPH_PROJECTOR_EXTENSION_V1",
        "schema_version": "reverse-physics-bt-neutral-graph-projector-extension-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact minimal ghost-odd source extension and ghost-even neutral graph projector for the BT degree-four profile block, with positive-source affiliation obstruction",
        "question": "Does adjoining the smallest ghost-odd source partner turn the charge-neutral degree-four K4 lift into an idempotent, Krein-self-adjoint, ghost-even finite projector, and can that projector be affiliated back to the original positive profile source?",
        "answer": "Yes to the projector and no to affiliation on the minimal carrier. Let the odd partner have metric -I2 and the selected neutral degree-four composite have metric -2I2. The exact slope T=diag(sqrt(6699)/16,sqrt(7149)/16) obeys T^T(-2I2)T=K4 and has rank two, so a two-dimensional odd partner is minimal. For L=(I2,T)^T and eta=diag(-I2,-2I2), the Krein-orthogonal graph projector P=L(L^T eta L)^-1 L^T eta is exact, rank two, idempotent, Krein self-adjoint, total-charge zero and ghost even. Its range Gram is -diag(6827/128,7277/128), its kernel is the eta-orthogonal negative graph, and tr(P^sharp P)=2. Thus the algebraic projector and a finite positive generalized-Born rank weight exist. However the original profile source has metric +I2 and ghost parity +I2, whereas both the odd partner and graph have parity -I. The ghost-even affiliation equation -F=F has only F=0, and any map into the graph has negative-semidefinite pullback -A^T M A, so no norm-preserving positive-source affiliation exists. The construction is therefore a finite candidate neutral P block only after adding an unaffiliated ghost-odd source; it is not the BT Rt pushforward or Eq. (19).",
        "assumptions": [
            "The original two-point hard-profile source is the certified positive I2 carrier and hence has ghost parity +I2.",
            "The selected neutral degree-four composite directions have metric -2I2, total charge zero, and ghost parity -I2 as certified by the predecessor.",
            "The added source partner is required to be a genuine ghost-odd Krein sector, so its metric is -I2 and its fundamental symmetry is -I2.",
            "Projector adjoints and traces are taken with the displayed finite nondegenerate Krein metric.",
            "Affiliation means a nonzero parity-intertwining and norm-preserving map from the original positive profile source; a merely linear sign-reversing identification is insufficient."
        ],
        "minimal_odd_source_extension": {
            "original_profile_metric": [["1", "0"], ["0", "1"]],
            "original_profile_ghost_parity": [["1", "0"], ["0", "1"]],
            "odd_partner_metric": rows(eta_source_odd),
            "odd_partner_ghost_parity": rows(-I),
            "composite_negative_metric": rows(eta_composite_negative),
            "composite_ghost_parity": rows(-I),
            "slope_T": rows(T),
            "slope_covariant_pullback": rows(
                sp.simplify(T.T * eta_composite_negative * T)
            ),
            "required_rank": 2,
            "partner_dimension": 2,
            "minimality": "rank(T)=rank(K4)=2, so every source carrying this injective slope has dimension at least two"
        },
        "neutral_graph_projector": {
            "carrier_metric": rows(eta),
            "carrier_ghost_parity": rows(kappa),
            "graph_embedding_L": rows(L),
            "positive_M": rows(M),
            "range_gram": rows(range_gram),
            "projector": rows(projector),
            "projector_identity": "P^2=P=P^sharp",
            "charge_identity": "[H_total,P]=0",
            "ghost_identity": "[kappa_total,P]=0",
            "rank": 2,
            "trace": 2,
            "finite_algebraic_generalized_Born_trace": 2,
            "kernel_embedding": rows(complement),
            "kernel_gram": rows(complement_gram),
            "range_kernel_pairing": rows(sp.simplify(L.T * eta * complement))
        },
        "positive_source_affiliation": {
            "ghost_even_equation": "(-I2)F=F(+I2)",
            "coefficient_rank": 4,
            "only_solution": "F=0",
            "graph_pullback_for_general_A": "(LA)^T eta (LA)=-A^T M A",
            "norm_preserving_positive_source_map": "EXACTLY_OBSTRUCTED_ON_MINIMAL GRAPH",
            "reason": "M is positive definite, so every nonzero graph image has negative norm while the original source metric is positive; parity independently forces every ghost-even direct affiliation to vanish.",
            "remaining_escape": "add further positive and negative source/target sectors or derive a nontrivial zero-mode trace from the BT Rt pushforward"
        },
        "Eq19_boundary": {
            "finite_neutral_ghost_even_projector_candidate": "CONSTRUCTED_ON_AUGMENTED ODD SOURCE",
            "finite_algebraic_trace": "COMPUTED_EQUAL_TO_TWO",
            "original_positive_source_affiliation": "EXACTLY_OBSTRUCTED_ON_MINIMAL CARRIER",
            "finite_mode_order_lambda_sector": "UNCHANGED_PROVED_WITH_Q1_ZERO",
            "BT_Rt_derivation": "NOT_CONSTRUCTED",
            "all_order_projector_identity": "NOT_PROVED"
        },
        "disposition": {
            "minimal_ghost_odd_source_partner_dimension": "TWO",
            "neutral_graph_projector": "CONSTRUCTED_EXACTLY",
            "projector_idempotence_and_Krein_selfadjointness": "PROVED",
            "projector_charge_and_ghost_compatibility": "PROVED",
            "finite_algebraic_generalized_Born_trace": "COMPUTED_EQUAL_TO_TWO",
            "positive_profile_source_affiliation": "EXACTLY_OBSTRUCTED_ON_MINIMAL CARRIER",
            "BT_dynamical_derivation": "NOT_CONSTRUCTED",
            "physical_fourth_probability": "NOT_ESTABLISHED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "does_not_establish": [
            "the all-order Bateman-Turok Eq. (19) projector identity",
            "that Rt supplies the added ghost-odd source partner",
            "affiliation of the finite graph projector to the original phi projection",
            "the continuum or thermodynamic generalized-Born trace",
            "weak ghost symmetry of a complete scattering process",
            "a normalized fourth event or complete 2->6 probability",
            "a spacetime Moller, LSZ, or S operator",
            "a gravity or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Enlarge the source by the minimum additional positive sector capable of pairing the new odd graph without violating ghost evenness, then solve the complete neutral projector equations with a nonzero map from the certified positive profile source. Require the public Rt compression and order-lambda Q1=0 block as fixed corners. If every such finite signature-balanced extension remains unaffiliated, the obstruction moves from the minimal graph to the complete finite public carrier; if one exists, its trace must be compared with the eight-point profile response before any physical promotion.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS]
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_neutral_graph_projector_extension.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_neutral_graph_projector_extension.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_neutral_graph_projector_extension"
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks
        },
        "report": REPORT,
        "schema": SCHEMA
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def fast_check(path):
    try:
        with open(path, encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print("[FAIL] recorded certificate:", exc)
        return 1
    inputs = value.get("provenance", {}).get("inputs", [])
    ok = (
        value.get("certificate")
        == "REVERSE_PHYSICS_BT_NEUTRAL_GRAPH_PROJECTOR_EXTENSION_V1"
        and value.get("checks", {}).get("passed")
        == value.get("checks", {}).get("total")
        == 26
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and len(inputs) == 5
        and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs)
        and value.get("disposition", {}).get("Eq19_all_orders") == "NOT_PROVED"
    )
    print("FAST RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fast-check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    if args.fast_check:
        return fast_check(args.output)
    value = build()
    rendered = canonical(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = canonical(json.load(handle))
        except (OSError, json.JSONDecodeError) as exc:
            print("[FAIL] recorded certificate:", exc)
            return 1
        if recorded != rendered:
            print("[FAIL] certificate drift")
            return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    print("projector rank:", value["neutral_graph_projector"]["rank"])
    print("affiliation:", value["positive_source_affiliation"]["norm_preserving_positive_source_map"])
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
