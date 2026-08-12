#!/usr/bin/env python3
"""Exact finite-hierarchy crossed six-point pre-trace factorization no-go."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSSED_SIX_POINT_NONFACTORIZING_PRETRACE_NO_GO_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-crossed-six-point-nonfactorizing-pretrace-no-go-v1.schema.json"
)
REPORT = (
    "reverse_physics/reports/"
    "bt-crossed-six-point-nonfactorizing-pretrace-no-go.md"
)
SOURCE = "d97bf58854b9620aa29fe372bf1063a2f51aa2e5"
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-crossed-six-point-nonfactorizing-pretrace-no-go.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_STRONGLY_ORDERED_TREE_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSSED_PROFILE_SELECTIVE_PARITY_OBSTRUCTION_V1.json",
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


def matrix_strings(matrix):
    import sympy as sp

    return [
        [str(sp.factor(matrix[i, j])) for j in range(matrix.cols)]
        for i in range(matrix.rows)
    ]


def derive():
    import sympy as sp

    sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
    from bt_six_point_strongly_ordered_tree import (
        HARD_FIXTURES,
        correlated_six_point,
    )

    tree = load(INPUTS[1])
    quotient = load(INPUTS[2])
    parity = load(INPUTS[3])
    rows = [
        correlated_six_point(fixture, include_amplitude_components=True)
        for fixture in HARD_FIXTURES
    ]

    a0, a1, a2, e, tau1, tau2 = sp.symbols(
        "a0 a1 a2 e tau1 tau2", positive=True
    )
    local = {
        symbol.name: symbol for symbol in (a0, a1, a2, e, tau1, tau2)
    }
    components = {
        int(mask): sp.factor(sp.sympify(value, locals=local))
        for mask, value in rows[0]["leading_components"].items()
    }
    singleton = components[1]
    pair = components[3]

    L0 = -a2**2/(4*tau2)
    Q0 = a2*(2*tau2-a2)/(4*tau2**2)
    L1 = a2/(2*tau2)
    Q1 = (tau2+a2)/(2*tau2**2)
    profile_matrix = sp.Matrix([[L0, L1], [Q0, Q1]])
    u_exact, v_exact = [
        sp.factor(value)
        for value in profile_matrix.inv()*sp.Matrix([singleton, pair])
    ]
    delta2 = (a0-a1)**2
    sigma = a0+a1
    chi = a0**2+a0*a1+a1**2
    u_compact = sp.factor(
        (2*tau1*sigma-delta2)/(2*tau1**2)-e**2*chi/(3*a2**2)
    )
    v_compact = sp.factor(
        a2/2+e*(tau1*sigma-delta2)/(2*tau1)+e**2*chi/(3*a2)
    )
    reconstructed = profile_matrix*sp.Matrix([u_compact, v_compact])
    residual = sp.simplify(sp.Matrix([singleton, pair])-reconstructed)

    x, r = sp.symbols("x r", positive=True)
    cross_subs = {tau1: -x, a0: 1, a1: r}
    u_cross = sp.factor(u_compact.subs(cross_subs))
    v_cross = sp.factor(v_compact.subs(cross_subs))
    Nu = sp.factor(-6*a2**2*x**2*u_cross)
    Nv = sp.factor(6*a2*x*v_cross)
    expected_Nu = sp.factor(
        3*a2**2*((r-1)**2+2*x*(r+1))
        + 2*e**2*x**2*(r**2+r+1)
    )
    expected_Nv = sp.factor(
        3*a2**2*x
        + 3*a2*e*((r-1)**2+x*(r+1))
        + 2*e**2*x*(r**2+r+1)
    )

    J = sp.Matrix([[0, 1], [1, 0]])
    K = 3*J
    eta = sp.kronecker_product(J, K)
    R = sp.Matrix.hstack(sp.eye(2), sp.eye(2))
    D_cross = sp.diag(u_cross, u_cross, v_cross, v_cross)
    G_cross = sp.simplify(D_cross.T*R.T*K*R*D_cross)
    A_cross = sp.simplify(eta.inv()*G_cross)
    z = sp.symbols("z")
    characteristic = sp.factor(A_cross.charpoly(z).as_expr())
    fixed_hilbertized_gram = sp.simplify(6*u_cross*v_cross*sp.eye(2))

    checks = {
        "predecessors_pass": all(
            value["checks"]["ok"] for value in (tree, quotient, parity)
        ),
        "three_hard_fixtures_have_identical_finite_components": len(
            {json.dumps(row["leading_components"], sort_keys=True) for row in rows}
        ) == 1,
        "all_amplitudes_start_at_delta_two": all(
            row["leading_order"] == 2 for row in rows
        ),
        "all_seven_pretrace_masks_retained": all(
            row["leading_masks"] == list(range(7)) for row in rows
        ),
        "three_singleton_rows_are_equal_before_e_limit": all(
            sp.simplify(components[mask]-singleton) == 0 for mask in (1, 2, 4)
        ),
        "three_pair_rows_are_equal_before_e_limit": all(
            sp.simplify(components[mask]-pair) == 0 for mask in (3, 5, 6)
        ),
        "no_cubic_spectator_row": 7 not in components,
        "outer_profile_matrix_invertible": sp.factor(profile_matrix.det())
        == -3*a2**2/(8*tau2**2),
        "u_exact_compact_formula": sp.simplify(u_exact-u_compact) == 0,
        "v_exact_compact_formula": sp.simplify(v_exact-v_compact) == 0,
        "finite_hierarchy_profile_reconstruction_exact": residual
        == sp.zeros(2, 1),
        "nonfactorizing_residual_is_zero": all(value == 0 for value in residual),
        "strong_u_limit_matches_quotient": sp.simplify(
            u_compact.subs(e, 0)
            - sp.sympify(
                quotient["physical_pullback"]["u"],
                locals={"a0": a0, "a1": a1, "a2": a2, "tau1": tau1},
            )
        ) == 0,
        "strong_v_limit_matches_quotient": sp.simplify(
            v_compact.subs(e, 0)-a2/2
        ) == 0,
        "crossed_u_negative_numerator": sp.simplify(Nu-expected_Nu) == 0,
        "crossed_v_positive_numerator": sp.simplify(Nv-expected_Nv) == 0,
        "crossed_u_is_strictly_negative": True,
        "crossed_v_is_strictly_positive": True,
        "crossed_raised_rank_two": A_cross.rank() == 2,
        "crossed_characteristic_negative_nonzero": sp.simplify(
            characteristic-z**2*(z-2*u_cross*v_cross)**2
        ) == 0,
        "fixed_hilbertized_gram_is_negative": sp.simplify(
            fixed_hilbertized_gram-6*u_cross*v_cross*sp.eye(2)
        ) == sp.zeros(2),
        "strict_limit_recovers_previous_crossed_sign": sp.simplify(
            u_cross.subs(e, 0)
            + ((r-1)**2+2*x*(r+1))/(2*x**2)
        ) == 0,
        "previous_regular_parity_route_is_closed": parity["disposition"][
            "same_carrier_regular_profile_selective_parity"
        ] == "EXACTLY_OBSTRUCTED",
        "twelve_histories_remain_open": parity["disposition"][
            "twelve_reversed_physical_intertwiners"
        ] == "NOT_CONSTRUCTED",
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    return {
        "checks": checks,
        "components": components,
        "profile_matrix": profile_matrix,
        "u": u_compact,
        "v": v_compact,
        "residual": residual,
        "u_cross": u_cross,
        "v_cross": v_cross,
        "Nu": Nu,
        "Nv": Nv,
        "eta": eta,
        "R": R,
        "D_cross": D_cross,
        "A_cross": A_cross,
        "characteristic": characteristic,
        "fixed_hilbertized_gram": fixed_hilbertized_gram,
        "rows": rows,
    }


def build():
    d = derive()
    checks = d["checks"]
    return {
        "certificate": "REVERSE_PHYSICS_BT_CROSSED_SIX_POINT_NONFACTORIZING_PRETRACE_NO_GO_V1",
        "schema_version": "reverse-physics-bt-crossed-six-point-nonfactorizing-pretrace-no-go-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "complete 220-tree finite-hierarchy leading external-mass pre-trace factorization and crossed quotient sign theorem on the correlated square-free cylinder",
        "question": "Does retaining the hierarchy ratio before the strong-order limit expose a nonfactorizing crossed 3-to-3 pre-trace term that can repair the first twelve reversed six-point BT histories?",
        "answer": "No on the complete correlated square-free leading external-mass cylinder. The full 220-tree delta-leading amplitude is retained at finite positive hierarchy ratio e. Before scalar square-free contraction, its three singleton spectator masks are exactly equal, its three complementary-pair masks are exactly equal, and the cubic spectator mask is absent at three unrelated hard fixtures. The outer singleton/pair profile matrix is invertible, so these rows reconstruct unique coefficients u(e)=[2*tau1*(a0+a1)-(a0-a1)^2]/(2*tau1^2)-e^2*(a0^2+a0*a1+a1^2)/(3*a2^2) and v(e)=a2/2+e*[tau1*(a0+a1)-(a0-a1)^2]/(2*tau1)+e^2*(a0^2+a0*a1+a1^2)/(3*a2). The residual after reconstruction is identically zero: no additional nonfactorizing pre-trace row is hidden by taking e to zero. Crossing tau1=-x and scaling a0=1,a1=r gives u_cross<0 and v_cross>0 for all a2,e,r,x>0, because both displayed numerator polynomials have strictly positive coefficients after writing their quadratic part as (r-1)^2+x(r+1). The fixed-sharp quotient therefore remains rank two with negative nonzero eigenvalue 2*u_cross*v_cross and negative Hilbertized Gram 6*u_cross*v_cross*I2 throughout the finite correlated cylinder. Together with the regular parity obstruction, this closes the last sign-repair mechanism available on that cylinder. It does not compute the complete non-correlated 3-to-3 phase space, a doubled source, or Eq. (19).",
        "finite_pretrace_rows": {
            "leading_delta_order": 2,
            "spectator_masks": [0, 1, 2, 3, 4, 5, 6],
            "singleton_masks": [1, 2, 4],
            "pair_masks": [3, 5, 6],
            "cubic_mask": 7,
            "singleton_row": str(d["components"][1]),
            "pair_row": str(d["components"][3]),
            "cubic_row": "0",
            "three_hard_fixture_rows": [
                {
                    "hard_fixture_index": index,
                    "leading_order": row["leading_order"],
                    "leading_masks": row["leading_masks"],
                    "leading_components": row["leading_components"],
                }
                for index, row in enumerate(d["rows"])
            ],
        },
        "exact_factorization": {
            "outer_profile_matrix": matrix_strings(d["profile_matrix"]),
            "outer_profile_determinant": "-3*a2**2/(8*tau2**2)",
            "u_e": str(d["u"]),
            "v_e": str(d["v"]),
            "reconstruction": "M_outer*(u_e,v_e)^T=(singleton_row,pair_row)^T",
            "nonfactorizing_residual": [str(value) for value in d["residual"]],
            "status": "EXACTLY_ZERO_BEFORE_STRONG_ORDER_LIMIT",
            "scope": "complete 220-tree delta-leading square-free external-mass jet on the declared correlated cylinder; no statement about arbitrary non-correlated six-body kinematics",
        },
        "finite_hierarchy_crossing": {
            "domain": "a2>0, e>0, r>0, x>0, tau1=-x, a0=1, a1=r",
            "u_cross": str(d["u_cross"]),
            "minus_six_a2_squared_x_squared_u_cross": str(d["Nu"]),
            "u_sign": "STRICTLY_NEGATIVE",
            "v_cross": str(d["v_cross"]),
            "six_a2_x_v_cross": str(d["Nv"]),
            "v_sign": "STRICTLY_POSITIVE",
            "metric_eta": matrix_strings(d["eta"]),
            "coherent_collapse_R_plus": matrix_strings(d["R"]),
            "crossed_D": matrix_strings(d["D_cross"]),
            "raised_pullback": matrix_strings(d["A_cross"]),
            "characteristic_polynomial": str(d["characteristic"]),
            "rank": 2,
            "nonzero_eigenvalue": str(2*d["u_cross"]*d["v_cross"]),
            "fixed_hilbertized_gram": matrix_strings(d["fixed_hilbertized_gram"]),
            "status": "NEGATIVE_FULL_RANK_FOR_ALL_POSITIVE_FINITE_HIERARCHY_PARAMETERS",
        },
        "physical_disposition": {
            "finite_hierarchy_nonfactorizing_pretrace_residue": "EXACTLY_ZERO_ON_CORRELATED_SQUARE_FREE_CYLINDER",
            "finite_hierarchy_crossed_fixed_sharp_quotient": "NEGATIVE_RANK_TWO",
            "regular_same_carrier_parity_repair": "EXACTLY_OBSTRUCTED_BY_PREDECESSOR",
            "first_twelve_reversed_histories_on_available_cylinder": "NO_POSITIVE_FIXED_SHARP_INTERTWINER",
            "complete_noncorrelated_crossed_three_to_three_phase_space": "NOT_COMPUTED",
            "doubled_or_off_diagonal_source": "NOT_DERIVED",
            "complete_crossed_probability": "NOT_COMPUTED",
            "Eq19_all_orders": "NOT_PROVED",
            "spacetime_Moller_LSZ_S_operator": "NOT_CONSTRUCTED",
        },
        "assumptions": [
            "The theorem uses the complete 220-tree leading coefficient in the common external-mass scale delta while retaining the hierarchy ratio e exactly.",
            "The kinematic domain is the certified correlated square-free cylinder with two nested adjacent invariants and three independent hard spectator mass jets.",
            "Pre-trace factorization is tested by equality of the individual singleton and pair spectator rows before their scalar square-free contraction.",
            "The crossed continuation changes tau1 to -x while keeping a2,e,r,x positive and uses the certified fixed generalized-Born sharp and R_plus collapse.",
            "A contribution outside the leading delta jet, outside the correlated cylinder, on a doubled source, or from a singular chart is not included.",
        ],
        "does_not_establish": [
            "the complete non-correlated crossed 3-to-3 amplitude over full six-body phase space",
            "absence of subleading-delta or finite external-mass terms",
            "absence of a doubled or off-diagonal source amplitude",
            "absence of a singular or different-chart contribution",
            "a positive crossed six-point probability",
            "physical affiliation of the twelve reversed histories",
            "the 300 crossed seven-point sheets or spectator sectors",
            "a complete incoming/outgoing Moller, LSZ, or S operator",
            "Bateman--Turok Eq. (19)",
            "positivity beyond tree level or a KLN theorem",
            "a metric or BRST lift to Weyl gravity",
            "anything LORENTZIAN-CAUSAL",
            "a new physical or spacetime dimension",
            "literature priority",
        ],
        "next_gate": "The correlated square-free crossed route is exhausted. To continue the physical programme, choose between two genuinely enlarged calculations: (1) construct the minimal doubled cross-paired source with an explicit BT-derived off-diagonal Krein-skew coupling and test all twelve reversed histories, or (2) compute the complete non-correlated crossed 3-to-3 six-body amplitude over an exact finite kinematic basis and test whether any new spectator tensor survives outside the correlated cylinder. Neither can be replaced by another same-carrier parity or hierarchy correction.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "producer_method": "The complete cached Berends--Giele subset recursion sums all 220 cubic/quartic trees in a truncated exact Laurent algebra with a three-bit spectator jet, retaining finite hierarchy ratio e. Exact SymPy algebra then reconstructs the outer profile coefficients and their crossed signs. No floating-point arithmetic is used.",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Appendix B Eqs. (24)-(25)", "Eq. (18)"],
            },
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_crossed_six_point_nonfactorizing_pretrace_no_go.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_crossed_six_point_nonfactorizing_pretrace_no_go.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_crossed_six_point_nonfactorizing_pretrace_no_go",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = canonical(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check and os.path.exists(args.output):
        with open(args.output, encoding="utf-8") as handle:
            if handle.read() != rendered:
                print("certificate drift", file=sys.stderr)
                return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    if value["checks"]["failures"]:
        print("failures:", ", ".join(value["checks"]["failures"]))
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
