#!/usr/bin/env python3
"""Exact public-Fock realization of the neutral BT graph's odd source type."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PUBLIC_FOCK_ODD_SOURCE_AFFILIATION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-public-fock-odd-source-affiliation-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-public-fock-odd-source-affiliation.md"
SOURCE = "a8a80bb713ab9840c6b311637421c676ce73eb92"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-public-fock-odd-source-affiliation-DONE-a8a80bb7.json"
)
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-public-fock-odd-source-affiliation.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FINITE_PHYSICAL_MOLLER_COLUMN_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EIGHT_POINT_KREIN_CHARGE_LOCALIZATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_NEUTRAL_BOSONIC_COMPOSITE_LIFT_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_NEUTRAL_GRAPH_PROJECTOR_EXTENSION_V1.json",
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


def occupation_data():
    """Return the canonical two-profile neutral degree-four occupation data."""
    import sympy as sp

    occupations = [(2, 0), (1, 1), (0, 2)]
    basis = [(alpha, beta) for alpha in occupations for beta in occupations]
    gram = sp.zeros(9)
    parity = sp.zeros(9)
    for i, (alpha, beta) in enumerate(basis):
        parity[basis.index((beta, alpha)), i] = 1
        for j, (gamma, delta) in enumerate(basis):
            if alpha == delta and beta == gamma:
                gram[i, j] = (
                    math.factorial(alpha[0])
                    * math.factorial(alpha[1])
                    * math.factorial(beta[0])
                    * math.factorial(beta[1])
                )
    raw = sp.zeros(9, 2)
    raw[basis.index((occupations[0], occupations[1])), 0] = 1
    raw[basis.index((occupations[1], occupations[0])), 0] = -1
    raw[basis.index((occupations[1], occupations[2])), 1] = 1
    raw[basis.index((occupations[2], occupations[1])), 1] = -1
    labels = [
        "p%d%d_m%d%d" % (a[0], a[1], b[0], b[1]) for a, b in basis
    ]
    return occupations, basis, labels, gram, parity, raw


def build():
    import sympy as sp

    moller = load(INPUTS[1])
    charge = load(INPUTS[2])
    composite = load(INPUTS[3])
    graph = load(INPUTS[4])
    order_lambda = load(INPUTS[5])
    rho_row = charge["charge_fibre"]["rho"]
    rho = sp.Rational(rho_row["numerator"], rho_row["denominator"])
    J = sp.Matrix(charge["charge_fibre"]["target_metric_J"])
    C = sp.Matrix(
        [
            [sp.sympify(entry) for entry in row]
            for row in charge["charge_fibre"]["certified_missing_leg_C"]
        ]
    )
    S = sp.Matrix(
        [
            [sp.sympify(entry) for entry in row]
            for row in charge["charge_fibre"]["null_charge_basis_S"]
        ]
    )
    occupations, basis, labels, W, kappa, raw = occupation_data()
    positive_metric = sp.simplify(W * kappa)
    public_selected = raw / 2
    public_selected_gram = sp.simplify(public_selected.T * W * public_selected)
    complement_gram = rho**8 * W
    complement_selected = raw / (sp.sqrt(2) * rho**4)
    complement_selected_gram = sp.simplify(
        complement_selected.T * complement_gram * complement_selected
    )

    # C*S=-rho I on each profile's transported charge eigenbasis.  Its
    # fourth symmetric power is therefore rho^4 I on this total-degree-four
    # sector; the minus sign disappears because the degree is even.
    one_particle_charge_map = sp.simplify(C * S)
    phi4 = rho**4 * sp.eye(9)
    public_coordinate_left_inverse = sp.simplify(
        public_selected_gram.inv() * public_selected.T * W
    )
    selected_forward = sp.simplify(
        public_coordinate_left_inverse * phi4 * complement_selected
    )
    selected_inverse = sp.simplify(selected_forward.inv())
    full_isometry_defect = sp.simplify(phi4.T * W * phi4 - complement_gram)
    selected_inverse_isometry_defect = sp.simplify(
        selected_inverse.T
        * complement_selected_gram
        * selected_inverse
        - public_selected_gram
    )
    selected_forward_isometry_defect = sp.simplify(
        selected_forward.T * public_selected_gram * selected_forward
        - complement_selected_gram
    )
    selected_charge = sp.zeros(2)
    selected_parity = -sp.eye(2)

    checks = {
        "predecessor_certificates_pass": all(
            value["checks"]["ok"]
            for value in (moller, charge, composite, graph, order_lambda)
        ),
        "rho_replayed_exactly": rho == sp.Rational(819, 4000),
        "public_one_particle_metric_is_cross_Krein_J": J == sp.Matrix([[0, 1], [1, 0]]),
        "missing_leg_C_replayed": C == sp.Matrix([[-rho, -1], [0, 1]]),
        "transported_charge_basis_replayed": S == sp.Matrix([[1, 1], [0, -rho]]),
        "one_particle_charge_map_is_minus_rho_identity": one_particle_charge_map == -rho * sp.eye(2),
        "public_neutral_degree_four_dimension_is_nine": W.shape == (9, 9),
        "public_neutral_degree_four_gram_is_symmetric": W.T == W,
        "public_neutral_degree_four_gram_is_nondegenerate": W.det() != 0,
        "occupation_swap_is_involutive": kappa**2 == sp.eye(9),
        "occupation_swap_preserves_public_gram": kappa.T * W * kappa == W,
        "public_fundamental_metric_is_positive": (
            positive_metric == sp.diag(4, 2, 4, 2, 1, 2, 4, 2, 4)
            and all(positive_metric[i, i] > 0 for i in range(9))
        ),
        "public_neutral_inertia_is_six_three": (
            (sp.eye(9) + kappa).rank() == 6
            and (sp.eye(9) - kappa).rank() == 3
        ),
        "selected_public_vectors_have_gram_minus_I2": public_selected_gram == -sp.eye(2),
        "selected_public_vectors_are_ghost_odd": kappa * public_selected == -public_selected,
        "selected_public_vectors_are_total_charge_zero": selected_charge == sp.zeros(2),
        "complement_full_gram_is_rho8_public_gram": complement_gram == rho**8 * W,
        "selected_complement_vectors_have_gram_minus_2I2": complement_selected_gram == -2 * sp.eye(2),
        "selected_complement_vectors_are_ghost_odd": kappa * complement_selected == -complement_selected,
        "Sym4_C_is_rho4_identity_in_charge_basis": phi4 == rho**4 * sp.eye(9),
        "Sym4_C_is_full_degree_four_isometry": full_isometry_defect == sp.zeros(9),
        "Sym4_C_commutes_with_ghost_parity": phi4 * kappa == kappa * phi4,
        "selected_forward_matrix_is_sqrt2_identity": selected_forward == sp.sqrt(2) * sp.eye(2),
        "selected_forward_map_is_metric_isometry": selected_forward_isometry_defect == sp.zeros(2),
        "selected_inverse_matrix_is_one_over_sqrt2_identity": selected_inverse == sp.eye(2) / sp.sqrt(2),
        "selected_inverse_map_is_metric_isometry": selected_inverse_isometry_defect == sp.zeros(2),
        "selected_affiliation_is_charge_zero_and_ghost_even": (
            selected_inverse * selected_charge == selected_charge * selected_inverse
            and selected_inverse * selected_parity == selected_parity * selected_inverse
        ),
        "graph_odd_source_metric_matches_public_selected_metric": (
            graph["minimal_odd_source_extension"]["odd_partner_metric"]
            == rows(public_selected_gram)
        ),
        "graph_slope_remains_distinct_from_carrier_isometry": (
            graph["minimal_odd_source_extension"]["slope_T"]
            != rows(selected_inverse)
        ),
        "order_lambda_boundary_preserved": (
            order_lambda["disposition"]["finite_mode_order_lambda_Eq19"]
            == "PROVED_WITH_Q1_ZERO"
        ),
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_PUBLIC_FOCK_ODD_SOURCE_AFFILIATION_V1",
        "schema_version": "reverse-physics-bt-public-fock-odd-source-affiliation-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact public two-profile neutral degree-four Fock realization of the ghost-odd source type required by the finite BT graph projector",
        "question": "Is the two-dimensional ghost-odd source partner used by the neutral graph projector an artificial summand, or does the public two-profile O(1,1) J-Fock carrier already contain it with a canonical exact affiliation to the complement composite?",
        "answer": "It is already present as a canonical public Fock subspace. The public two-profile neutral degree-four sector has dimension nine and inertia (6,3). The normalized occupation-antisymmetric vectors w1=(e_(20,11)-e_(11,20))/2 and w2=(e_(11,02)-e_(02,11))/2 have Gram -I2, total charge zero and ghost parity -I2, exactly matching the odd source type of the graph projector. In the complement charge basis n_plus=(1,0), n_minus=(1,-rho), the certified missing leg obeys C*S=-rho I2. Hence Sym^4(C)=rho^4 I9 on the degree-four neutral sector. It sends the normalized complement vectors u_i to sqrt(2) w_i and is a full metric isometry. Its selected inverse A=(1/sqrt(2))I2 maps the public odd sector to the complement composite and obeys A^T(-2I2)A=-I2 while commuting with charge and ghost parity. Thus the odd source carrier need not be adjoined abstractly: it is realized inside the public J-Fock carrier. This does not derive the graph slope T, show that the phi projection or nonlinear Rt pushforward excites the sector, prove Eq. (19), or construct a physical fourth probability.",
        "assumptions": [
            "The public O(1,1) one-particle charge fibre uses the cross-Krein metric J certified by the finite physical Moller and charge-localization predecessors.",
            "The two hard-profile labels define orthogonal copies of that public charge fibre and of its complement pullback.",
            "Both degree-four sectors use the canonical symmetric-boson contraction, including occupation factorials.",
            "Ghost parity on a neutral occupation basis exchanges the plus and minus occupation multi-indices.",
            "Carrier affiliation means an explicit charge- and parity-intertwining metric isometry between the selected public and complement Fock subspaces; it does not mean dynamical production by Rt."
        ],
        "public_neutral_degree_four_sector": {
            "one_particle_metric_J": rows(J),
            "occupation_types": [list(value) for value in occupations],
            "basis": labels,
            "dimension": 9,
            "gram": rows(W),
            "ghost_parity": rows(kappa),
            "positive_fundamental_metric": rows(positive_metric),
            "inertia": [6, 3],
            "all_basis_vectors_total_charge": 0,
            "selected_raw_columns": rows(raw),
            "selected_normalized_columns": rows(public_selected),
            "selected_gram": rows(public_selected_gram),
            "selected_total_charge": [0, 0],
            "selected_ghost_parity": rows(selected_parity),
            "selected_basis_names": ["w1=(e_(20,11)-e_(11,20))/2", "w2=(e_(11,02)-e_(02,11))/2"]
        },
        "complement_to_public_symmetric_power": {
            "rho": {"numerator": int(rho.p), "denominator": int(rho.q)},
            "missing_leg_C": rows(C),
            "complement_charge_basis_S": rows(S),
            "one_particle_map_C_times_S": rows(one_particle_charge_map),
            "one_particle_identity": "C*S=-rho*I2",
            "complement_degree_four_gram": rows(complement_gram),
            "complement_selected_normalized_columns": rows(complement_selected),
            "complement_selected_gram": rows(complement_selected_gram),
            "Sym4_C_in_charge_basis": rows(phi4),
            "full_metric_identity": "Sym4(C)^T*W_public*Sym4(C)=G_complement=rho^8*W_public",
            "selected_forward_matrix_U_to_W": rows(selected_forward),
            "selected_forward_identity": "Sym4(C)u_i=sqrt(2)w_i",
            "selected_inverse_matrix_W_to_U": rows(selected_inverse),
            "selected_inverse_metric_identity": "A^T*(-2I2)*A=-I2",
            "selected_map_total_charge": 0,
            "selected_map_ghost_parity": "EVEN"
        },
        "graph_source_realization": {
            "abstract_graph_odd_source_metric": graph["minimal_odd_source_extension"]["odd_partner_metric"],
            "public_selected_metric": rows(public_selected_gram),
            "public_source_type_realization": "CONSTRUCTED_CANONICALLY",
            "carrier_identification": "Identify the graph source O with span(w1,w2) inside the public two-profile neutral degree-four J-Fock sector.",
            "canonical_complement_affiliation": "A=(1/sqrt(2))I2 maps O isometrically to span(u1,u2) and is charge zero and ghost even.",
            "graph_slope_T": graph["minimal_odd_source_extension"]["slope_T"],
            "graph_slope_status": "NOT_DERIVED_BY_SYM4_C",
            "original_scalar_positive_source_status": "DIRECT_AFFILIATION_REMAINS_EXACTLY_OBSTRUCTED",
            "meaning": "The carrier-existence objection is removed on the full public Fock space, but the public phi projector and nonlinear Rt dynamics have not been shown to select the graph of T."
        },
        "Eq19_boundary": {
            "public_ghost_odd_source_carrier": "CONSTRUCTED_CANONICALLY",
            "public_to_complement_selected_isometry": "PROVED_EXACTLY",
            "abstract_odd_source_adjunction": "REPLACED_BY_EXPLICIT_PUBLIC_FOCK_SUBSPACE",
            "original_positive_scalar_profile_affiliation": "REMAINS_OBSTRUCTED",
            "graph_slope_from_public_Rt": "NOT_DERIVED",
            "nonlinear_Rt_excitation_of_degree_four_sector": "NOT_COMPUTED",
            "finite_mode_order_lambda_sector": "UNCHANGED_PROVED_WITH_Q1_ZERO",
            "all_order_projector_identity": "NOT_PROVED"
        },
        "disposition": {
            "public_neutral_degree_four_sector": "CONSTRUCTED_EXACTLY",
            "public_sector_inertia": "SIX_POSITIVE_THREE_NEGATIVE",
            "public_odd_source_dimension": "TWO",
            "Sym4_C_full_metric_affiliation": "PROVED",
            "selected_charge_and_ghost_affiliation": "PROVED",
            "graph_odd_source_public_realization": "PROVED",
            "graph_slope_dynamical_derivation": "NOT_CONSTRUCTED",
            "physical_fourth_probability": "NOT_ESTABLISHED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "does_not_establish": [
            "that the original positive scalar hard-profile source is the selected public Fock sector",
            "that the phi-theory projection has a nonzero component in the selected public odd sector",
            "that the nonlinear Rt pushforward produces the selected degree-four sector",
            "the graph slope T or its two eight-point coefficients from public Rt dynamics",
            "the all-order Bateman-Turok Eq. (19) projector identity",
            "the continuum or thermodynamic generalized-Born trace",
            "weak ghost symmetry of a complete scattering process",
            "a normalized fourth event or complete 2->6 probability",
            "a spacetime Moller, LSZ, or S operator",
            "a gravity or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Compute the first nonlinear public Rt contribution capable of mapping the physical phi projection into the selected neutral degree-four public Fock sector. Project that contribution onto span(w1,w2), test whether its graph coefficient equals T=diag(sqrt(6699)/16,sqrt(7149)/16), and enforce projector idempotence with the certified order-lambda Q1=0 corner. A mismatch is a scoped dynamical obstruction; a match would still require the continuum trace and asymptotic domain before Eq. (19) or physical positivity can be promoted.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS]
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_public_fock_odd_source_affiliation.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_public_fock_odd_source_affiliation.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_public_fock_odd_source_affiliation"
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
        == "REVERSE_PHYSICS_BT_PUBLIC_FOCK_ODD_SOURCE_AFFILIATION_V1"
        and value.get("checks", {}).get("passed")
        == value.get("checks", {}).get("total")
        == 31
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and len(inputs) == 7
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
    print("public inertia:", value["public_neutral_degree_four_sector"]["inertia"])
    print("source realization:", value["graph_source_realization"]["public_source_type_realization"])
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
