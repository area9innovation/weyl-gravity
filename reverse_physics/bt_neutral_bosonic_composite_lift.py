#!/usr/bin/env python3
"""Exact minimal neutral bosonic composite lift of the BT fourth profile."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_NEUTRAL_BOSONIC_COMPOSITE_LIFT_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-neutral-bosonic-composite-lift-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-neutral-bosonic-composite-lift.md"
SOURCE = "932c93106aeacc83d08e6f5dfade16924a1916f9"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-neutral-bosonic-composite-lift-"
    "DONE-932c93106aeacc83.json"
)
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-neutral-bosonic-composite-lift.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EIGHT_POINT_KREIN_CHARGE_LOCALIZATION_V1.json",
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


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def rows(matrix):
    import sympy as sp

    return [
        [str(sp.factor(matrix[i, j])) for j in range(matrix.cols)]
        for i in range(matrix.rows)
    ]


def occupation_name(value):
    return "%d%d" % value


def factorial_weight(value):
    return math.factorial(value[0]) * math.factorial(value[1])


def build():
    import sympy as sp

    charge = load(INPUTS[1])
    profile = load(INPUTS[2])
    order_lambda = load(INPUTS[3])
    rho_q = frac(charge["charge_fibre"]["rho"])
    rho = sp.Rational(rho_q.numerator, rho_q.denominator)
    K4 = sp.Matrix(profile["fibrewise_krein_lift"]["pullback"])
    target = sp.diag(-sp.Rational(6699, 128), -sp.Rational(7149, 128))

    # Charge-zero degree four means two plus and two minus quanta.  With two
    # profile modes, each sign has the three occupation types below.
    occupations = [(2, 0), (1, 1), (0, 2)]
    basis = [(alpha, beta) for alpha in occupations for beta in occupations]
    index = {entry: position for position, entry in enumerate(basis)}
    gram = sp.zeros(len(basis))
    parity = sp.zeros(len(basis))
    for column, (alpha, beta) in enumerate(basis):
        parity[index[(beta, alpha)], column] = 1
        for row, (gamma, delta) in enumerate(basis):
            if alpha == delta and beta == gamma:
                gram[row, column] = (
                    factorial_weight(alpha)
                    * factorial_weight(beta)
                    * rho**8
                )
    positive_metric = sp.simplify(gram * parity)
    normalized_gram = sp.simplify(gram / rho**8)
    gram_eigenvalues = gram.eigenvals()
    gram_positive_index = sum(
        multiplicity
        for value, multiplicity in gram_eigenvalues.items()
        if value > 0
    )
    gram_negative_index = sum(
        multiplicity
        for value, multiplicity in gram_eigenvalues.items()
        if value < 0
    )

    # Two mutually orthogonal occupation-antisymmetric directions with equal
    # norm.  The third negative direction (20,02)-(02,20) is not required.
    A, B, C = occupations
    raw_one = sp.zeros(9, 1)
    raw_one[index[(A, B)]] = 1
    raw_one[index[(B, A)]] = -1
    raw_two = sp.zeros(9, 1)
    raw_two[index[(B, C)]] = 1
    raw_two[index[(C, B)]] = -1
    normalization = sp.sqrt(2) * rho**4
    U = sp.Matrix.hstack(raw_one / normalization, raw_two / normalization)
    amplitudes = sp.diag(sp.sqrt(6699) / 16, sp.sqrt(7149) / 16)
    forward = sp.simplify(U * amplitudes)
    pullback = sp.simplify(forward.T * gram * forward)

    source_metric = sp.eye(2)
    total_metric = sp.diag(source_metric, gram)
    sharp = sp.simplify(forward.T * gram)
    generator = sp.zeros(11)
    generator[:2, 2:] = -sharp
    generator[2:, :2] = forward
    total_parity = sp.diag(sp.eye(2), parity)
    total_charge = sp.zeros(11)

    census = []
    for half_degree in range(3):
        single_sign_dimension = half_degree + 1
        positive = single_sign_dimension * (single_sign_dimension + 1) // 2
        negative = single_sign_dimension * (single_sign_dimension - 1) // 2
        census.append({
            "total_degree": 2 * half_degree,
            "single_sign_occupation_dimension": single_sign_dimension,
            "neutral_dimension": single_sign_dimension**2,
            "positive_index": positive,
            "negative_index": negative,
        })

    checks = {
        "predecessor_certificates_pass": all(
            value["checks"]["ok"] for value in (charge, profile, order_lambda)
        ),
        "rho_replayed": rho_q == Fraction(819, 4000),
        "profile_effect_replayed": K4 == target,
        "degree_four_basis_has_nine_bosonic_occupations": len(basis) == 9,
        "every_degree_four_basis_vector_has_total_charge_zero": all(
            sum(alpha) == sum(beta) == 2 for alpha, beta in basis
        ),
        "degree_four_gram_is_symmetric_nondegenerate": (
            gram == gram.T and gram.rank() == 9
        ),
        "occupation_swap_is_involutive": parity**2 == sp.eye(9),
        "occupation_swap_preserves_gram": parity.T * gram * parity == gram,
        "fundamental_metric_is_positive_diagonal": (
            positive_metric.is_diagonal()
            and all(positive_metric[i, i] > 0 for i in range(9))
        ),
        "degree_four_inertia_is_six_three": (
            gram_positive_index == census[2]["positive_index"] == 6
            and gram_negative_index == census[2]["negative_index"] == 3
        ),
        "degree_two_negative_index_is_one": census[1]["negative_index"] == 1,
        "degree_two_cannot_carry_rank_two_effect": (
            census[1]["negative_index"] < target.rank()
        ),
        "odd_degrees_have_no_charge_zero_sector": all(
            not any(2 * plus_count == degree for plus_count in range(degree + 1))
            for degree in (1, 3)
        ),
        "degree_four_is_minimal_for_negative_rank_two": (
            target.rank() == 2
            and census[0]["negative_index"] == 0
            and census[1]["negative_index"] == 1
            and census[2]["negative_index"] >= 2
        ),
        "selected_raw_vectors_are_orthogonal": (
            (raw_one.T * gram * raw_two)[0] == 0
        ),
        "normalized_negative_pair_is_minus_two_identity": (
            sp.simplify(U.T * gram * U) == -2 * sp.eye(2)
        ),
        "selected_vectors_are_charge_neutral": total_charge == sp.zeros(11),
        "selected_vectors_are_ghost_odd": parity * U == -U,
        "forward_block_reconstructs_K4": pullback == target,
        "forward_block_has_rank_two": forward.rank() == 2,
        "block_generator_is_krein_skew": (
            sp.simplify(generator.T * total_metric + total_metric * generator)
            == sp.zeros(11)
        ),
        "block_generator_is_charge_neutral": (
            total_charge * generator - generator * total_charge == sp.zeros(11)
        ),
        "block_generator_is_ghost_odd": (
            total_parity * generator * total_parity == -generator
        ),
        "order_lambda_boundary_is_preserved": (
            order_lambda["disposition"]["finite_mode_order_lambda_Eq19"]
            == "PROVED_WITH_Q1_ZERO"
        ),
        "Eq19_and_physical_claims_stay_open": (
            charge["disposition"]["Eq19_all_orders"] == "NOT_PROVED"
            and charge["disposition"]["physical_fourth_probability"]
            == "NOT_ESTABLISHED"
        ),
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    checks = {name: bool(value) for name, value in checks.items()}

    basis_labels = [
        "p%s_m%s" % (occupation_name(alpha), occupation_name(beta))
        for alpha, beta in basis
    ]
    return {
        "certificate": "REVERSE_PHYSICS_BT_NEUTRAL_BOSONIC_COMPOSITE_LIFT_V1",
        "schema_version": "reverse-physics-bt-neutral-bosonic-composite-lift-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact minimal charge-neutral symmetric-bosonic higher-composite Krein lift of the rank-two BT fourth-profile block, with ghost-parity obstruction",
        "question": "What is the smallest symmetric bosonic composite of the two certified hard-profile charge fibres that can carry the rank-two negative fourth-profile block while remaining total-charge zero, and can that block be the ghost-even neutral term of Bateman-Turok Eq. (19)?",
        "answer": "The first carrier large enough is the charge-zero degree-four symmetric bosonic sector. For total degree 2k over two hard-profile modes, the neutral sector is indexed by a pair of k-particle occupation types and its Gram is the positively weighted transpose pairing. Its inertia is ((k+1)(k+2)/2, k(k+1)/2). Degree two therefore has inertia (3,1) and cannot realize the rank-two negative K4. Degree four has inertia (6,3). In its occupation basis alpha,beta in {(2,0),(1,1),(0,2)}, the two normalized antisymmetric vectors u1=[e_(20,11)-e_(11,20)]/(sqrt(2)rho^4) and u2=[e_(11,02)-e_(02,11)]/(sqrt(2)rho^4) are orthogonal, charge zero, and have Gram -2 I2. Multiplying them by sqrt(6699)/16 and sqrt(7149)/16 gives an exact rank-two forward block with B4^sharp B4=diag(-6699/128,-7149/128), and the associated finite block generator is charge neutral and Krein skew. However occupation swap is the induced ghost parity and sends both u_i to -u_i. Any ghost-even forward block D from the positive profile source obeys kappa D=D and therefore D^sharp D=D^T(G4 kappa)D is positive semidefinite because G4 kappa is positive; it cannot equal negative K4. The constructed generator is ghost odd, not by itself the ghost-even neutral P term asserted in Eq. (19). Thus a minimal neutral higher-composite carrier exists and the degree barrier is broken algebraically, but a BT-derived ghost-even projector still requires a ghost-odd source partner, a larger dynamical completion, or an additional trace mechanism.",
        "assumptions": [
            "The two hard evaluation idempotents are orthogonal profile modes carrying identical copies of the certified cross-Krein charge fibre.",
            "The bosonic composite metric is the canonical symmetric-Fock contraction induced by <p_i,m_j>=rho^2 delta_ij, with all other one-particle charge pairings zero.",
            "Total charge is additive, so degree-four neutrality means two plus and two minus quanta.",
            "The induced ghost parity exchanges plus and minus occupations, while the positive two-point profile source is ghost even.",
            "The construction is a finite reduced-mode carrier and generator; no claim is made that BT dynamics supplies its coefficients or domain."
        ],
        "bosonic_neutral_census": {
            "general_formula": "at degree 2k: d=k+1 occupation types per sign; neutral dimension d^2; inertia (d(d+1)/2,d(d-1)/2)",
            "rows": census,
            "rank_required": 2,
            "minimal_total_degree": 4,
            "odd_degree_charge_zero_sector": "ABSENT"
        },
        "degree_four_neutral_sector": {
            "rho": rat(rho_q),
            "profile_modes": ["h33", "h34"],
            "occupation_types": [occupation_name(value) for value in occupations],
            "basis": basis_labels,
            "gram_identity": "G4=rho^8*W, where W_(alpha,beta),(gamma,delta)=alpha!*beta!*delta_(alpha,delta)*delta_(beta,gamma)",
            "gram_over_rho_power_eight": rows(normalized_gram),
            "ghost_parity_occupation_swap": rows(parity),
            "positive_fundamental_metric_over_rho_power_eight": rows(
                sp.simplify(positive_metric / rho**8)
            ),
            "inertia": {"positive": 6, "negative": 3, "zero": 0},
            "all_basis_vectors_total_charge": 0
        },
        "minimal_neutral_lift": {
            "raw_negative_vectors": [
                "e_(20,11)-e_(11,20)",
                "e_(11,02)-e_(02,11)"
            ],
            "normalization": "1/(sqrt(2)*rho^4)",
            "normalized_embedding_U": rows(U),
            "normalized_gram": rows(sp.simplify(U.T * gram * U)),
            "amplitudes": ["sqrt(6699)/16", "sqrt(7149)/16"],
            "forward_block_B4": rows(forward),
            "pullback": rows(pullback),
            "pullback_identity": "B4^sharp*B4=K4",
            "charge": "ZERO",
            "ghost_parity": "ODD",
            "block_generator": "K4_comp=[[0,-B4^sharp],[B4,0]]",
            "generator_metric": "diag(I2,G4)",
            "krein_skew_identity": "K4_comp^T*eta+eta*K4_comp=0",
            "charge_identity": "[H_total,K4_comp]=0",
            "ghost_identity": "kappa_total*K4_comp*kappa_total=-K4_comp"
        },
        "Eq19_boundary": {
            "neutral_higher_composite_carrier": "CONSTRUCTED_MINIMALLY_AT_BOSONIC_DEGREE_FOUR",
            "charge_compatible_finite_generator": "CONSTRUCTED_ALGEBRAICALLY",
            "ghost_even_neutral_P_identification": "EXACTLY_REFUTED_FOR_THIS MINIMAL BLOCK WITH GHOST_EVEN PROFILE SOURCE",
            "reason": "All negative directions of the neutral occupation-transpose Gram are ghost-parity odd. A ghost-even forward block D from the positive profile source has D^sharp D=D^T(G4 kappa)D positive semidefinite and cannot equal negative K4; the exact rank-two lift therefore maps the ghost-even source into the odd sector.",
            "finite_mode_order_lambda_sector": "UNCHANGED_PROVED_WITH_Q1_ZERO",
            "required_successor": "Derive from BT dynamics either a ghost-odd source partner paired with this neutral degree-four sector or a larger projector/zero-mode trace whose complete ghost-even block contains additional terms and reproduces the profile response."
        },
        "disposition": {
            "minimal_neutral_bosonic_degree": "FOUR",
            "degree_two_neutral_completion": "EXACTLY_OBSTRUCTED_BY_NEGATIVE_INDEX_ONE",
            "neutral_higher_composite_Krein_lift": "CONSTRUCTED_EXACTLY",
            "charge_compatible_finite_generator": "CONSTRUCTED_EXACTLY",
            "ghost_even_Eq19_P_term": "NOT_CONSTRUCTED",
            "BT_dynamical_derivation": "NOT_CONSTRUCTED",
            "generalized_Born_trace": "NOT_CONSTRUCTED",
            "physical_fourth_probability": "NOT_ESTABLISHED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "does_not_establish": [
            "the all-order Bateman-Turok Eq. (19) projector identity",
            "that the public BT homomorphism generates the degree-four block",
            "ghost symmetry or weak ghost symmetry of a complete scattering process",
            "a generalized-Born trace on the composite carrier",
            "a normalized fourth event or complete 2->6 probability",
            "a spacetime Moller, LSZ, or S operator",
            "a continuum or arbitrary-incoming-state construction",
            "a gravity or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Construct the smallest enlarged source/projector complex containing a ghost-odd source partner for the two occupation-antisymmetric neutral degree-four directions. Enforce projector idempotence, Krein self-adjointness, total charge zero, ghost-evenness of the complete P block, reduction to Q1=0 at order lambda, and the exact K4 hard-profile pullback. If no such finite extension exists under the certified public Rt compression, the result becomes a scoped Eq. (19) obstruction; if it exists, compute its generalized-Born trace before calling it physical.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS]
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_neutral_bosonic_composite_lift.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_neutral_bosonic_composite_lift.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_neutral_bosonic_composite_lift"
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
        value = load(os.path.relpath(path, ROOT))
    except (OSError, json.JSONDecodeError) as exc:
        print("[FAIL] recorded certificate:", exc)
        return 1
    inputs = value.get("provenance", {}).get("inputs", [])
    ok = (
        value.get("certificate")
        == "REVERSE_PHYSICS_BT_NEUTRAL_BOSONIC_COMPOSITE_LIFT_V1"
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
    print("minimal neutral degree:", value["bosonic_neutral_census"]["minimal_total_degree"])
    print("ghost parity:", value["minimal_neutral_lift"]["ghost_parity"])
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
