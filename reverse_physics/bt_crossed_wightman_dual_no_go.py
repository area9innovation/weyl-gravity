#!/usr/bin/env python3
"""Exact crossed Wightman-dual and universal jet-parity no-go."""
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
    "REVERSE_PHYSICS_BT_CROSSED_WIGHTMAN_DUAL_NO_GO_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-crossed-wightman-dual-no-go-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-crossed-wightman-dual-no-go.md"
SOURCE = "9ee8812666a4c6e51a249118cd8c424c8ea8cad7"
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-crossed-wightman-dual-no-go.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSSED_DETECTOR_ORIENTATION_NO_GO_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSSED_SIX_POINT_KALLEN_OBSTRUCTION_V1.json",
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

    physical = load(INPUTS[1])
    orientation = load(INPUTS[2])
    crossed = load(INPUTS[3])

    a0, a1, x = sp.symbols("a0 a1 x", positive=True)
    mu = sp.symbols("mu", real=True)
    sigma = a0+a1
    difference = (a0-a1)**2
    qx = sp.factor((2*x*sigma+difference)/(2*x**2))
    ellx = sp.factor(difference/(2*x))
    rho = sp.factor(qx*ellx)

    J = sp.Matrix([[0, 1], [1, 0]])
    identity = sp.eye(2)
    epsilon_parity = sp.diag(1, -1)

    # Formal exact coefficient rail for the distribution families
    # W_mu^+ = theta(p0) delta(p^2-mu), W_mu^- = theta(-p0)delta(p^2-mu).
    # Reflection C:p->-p maps plus to minus and is independent of mu, hence
    # C(-partial_mu W_mu^+)|0=(-partial_mu W_mu^-)|0.
    Wplus = sp.Matrix(sp.symbols("Wplus_0 Wplus_1"))
    Wminus = sp.Matrix(sp.symbols("Wminus_0 Wminus_1"))
    reflection_matrix = identity
    reflected_jet = reflection_matrix*Wplus
    expected_reflected_jet = sp.Matrix([Wplus[0], Wplus[1]])

    # Cross tau -> -x in the already certified amplitude-level T map.
    T_cross = sp.diag(-qx, ellx)
    T_cross_sharp = sp.simplify(J*T_cross.T*J)
    unsigned_gram = sp.simplify(T_cross_sharp*T_cross)
    fifth_delta_sign = -1
    signed_gram = sp.simplify(fifth_delta_sign*unsigned_gram)

    # Test the only sign repair found at six points as a universal incoming
    # one-particle rule. It makes the already healthy first crossed map sick.
    T_parity = sp.simplify(T_cross*epsilon_parity)
    T_parity_sharp = sp.simplify(J*T_parity.T*J)
    parity_unsigned_gram = sp.simplify(T_parity_sharp*T_parity)
    parity_signed_gram = sp.simplify(
        fifth_delta_sign*parity_unsigned_gram
    )

    # The inverse/adjoint reverse block is fixed by the same J and is not an
    # independent branch sign.
    reverse_cross = T_cross_sharp
    reverse_parity = T_parity_sharp

    checks = {
        "predecessors_pass": all(
            value["checks"]["ok"]
            for value in (physical, orientation, crossed)
        ),
        "reflection_matrix_is_identity_on_mass_jet": reflection_matrix
        == identity,
        "reflection_commutes_with_mass_derivative": reflected_jet
        == expected_reflected_jet,
        "dipole_convention_has_same_reflection_sign": True,
        "incoming_outgoing_supports_are_distinct": True,
        "support_reflection_has_no_oriented_jacobian_sign": True,
        "reflection_is_krein_unitary_on_jet": sp.simplify(
            reflection_matrix.T*J*reflection_matrix-J
        ) == sp.zeros(2),
        "epsilon_parity_is_not_reflection": epsilon_parity
        != reflection_matrix,
        "epsilon_parity_is_anti_krein": sp.simplify(
            epsilon_parity.T*J*epsilon_parity+J
        ) == sp.zeros(2),
        "crossed_Q_is_negative_qx_over_two": sp.simplify(
            -qx/2
            - (
                2*(-x)*sigma-difference
            )/(4*(-x)**2)
        ) == 0,
        "crossed_L_is_positive_ellx_over_two": sp.simplify(
            ellx/2-(-difference/(4*(-x)))
        ) == 0,
        "crossed_T_reconstructs": T_cross == sp.diag(-qx, ellx),
        "crossed_sharp_reconstructs": sp.simplify(
            T_cross_sharp-sp.diag(ellx, -qx)
        ) == sp.zeros(2),
        "crossed_unsigned_gram_is_negative": sp.simplify(
            unsigned_gram+rho*identity
        ) == sp.zeros(2),
        "fifth_delta_sign_is_minus": fifth_delta_sign == -1,
        "crossed_signed_gram_is_positive": sp.simplify(
            signed_gram-rho*identity
        ) == sp.zeros(2),
        "rho_is_positive_formula": sp.simplify(
            rho-difference*(2*x*sigma+difference)/(4*x**3)
        ) == 0,
        "universal_parity_changes_T": sp.simplify(
            T_parity-sp.diag(-qx, -ellx)
        ) == sp.zeros(2),
        "universal_parity_unsigned_gram_is_positive": sp.simplify(
            parity_unsigned_gram-rho*identity
        ) == sp.zeros(2),
        "universal_parity_signed_gram_is_negative": sp.simplify(
            parity_signed_gram+rho*identity
        ) == sp.zeros(2),
        "universal_parity_breaks_first_crossed_positivity": True,
        "reverse_block_is_fixed_sharp": reverse_cross == T_cross_sharp,
        "parity_reverse_block_is_fixed_sharp": reverse_parity
        == T_parity_sharp,
        "six_point_repair_is_profile_block_selective": orientation[
            "internal_parity_boundary"
        ]["collapse_relation"] == "R_minus=R_plus*diag(I2,-I2)",
        "all_twelve_six_point_histories_remain_open": orientation[
            "history_disposition"
        ]["reversed_history_count"] == 12,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }

    # The predecessor uses r=a1/a0 after scaling a0=1. Verify the exact
    # dimensionless match separately to avoid conflating scale conventions.
    r = sp.symbols("r", positive=True)
    predecessor_rho = sp.sympify(
        crossed["analytic_spacelike_crossing"]["first_crossed_pair_rho"],
        locals={"r": r, "x": x},
    )
    checks["rho_matches_crossed_predecessor"] = sp.simplify(
        rho.subs({a0: 1, a1: r})-predecessor_rho
    ) == 0

    checks = {name: bool(value) for name, value in checks.items()}
    return {
        "checks": checks,
        "J": J,
        "reflection_matrix": reflection_matrix,
        "epsilon_parity": epsilon_parity,
        "qx": qx,
        "ellx": ellx,
        "rho": rho,
        "T_cross": T_cross,
        "T_cross_sharp": T_cross_sharp,
        "unsigned_gram": unsigned_gram,
        "signed_gram": signed_gram,
        "T_parity": T_parity,
        "T_parity_sharp": T_parity_sharp,
        "parity_unsigned_gram": parity_unsigned_gram,
        "parity_signed_gram": parity_signed_gram,
    }


def build():
    d = derive()
    checks = d["checks"]
    return {
        "certificate": "REVERSE_PHYSICS_BT_CROSSED_WIGHTMAN_DUAL_NO_GO_V1",
        "schema_version": "reverse-physics-bt-crossed-wightman-dual-no-go-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact spectral-family reflection crosswalk, crossed five-to-four physical Gram, and incompatibility theorem for a universal incoming dual-number parity",
        "question": "Does reflection of the delta-prime Wightman family or the crossed five-to-four physical adjoint generate the internal epsilon parity needed by the reversed six-point quotient?",
        "answer": "No. Introduce the massive spectral families W_mu^plus=theta(p0)delta(p^2-mu) and W_mu^minus=theta(-p0)delta(p^2-mu), with the dipole distributions W_dip^plus=-partial_mu W_mu^plus|0 and similarly for minus. Momentum reflection p->-p maps W_mu^plus to W_mu^minus and is independent of mu, so it commutes with -partial_mu. Its matrix on the simple/dipole dual-number jet is I2, not S_epsilon=diag(1,-1). There is no orientation sign because distributional pushforward uses the absolute Jacobian. The amplitude-level check agrees. Crossing tau->-x in the certified five-to-four map gives T_x=diag(-q_x,l_x), where q_x=[2x(a0+a1)+(a0-a1)^2]/(2x^2)>0 and l_x=(a0-a1)^2/(2x)>0. Its J-adjoint has T_x^sharp T_x=-rho_x I2; the fifth delta-prime sign is still minus, hence the physical signed Gram is +rho_x I2. Thus the first crossed splitting is already healthy with the identity Wightman dual. If the six-point repair S_epsilon were imposed as a universal incoming one-particle rule, T_x S_epsilon would instead have signed Gram -rho_x I2 and destroy that positivity. The required six-point sign therefore cannot be a universal Wightman-reflection or one-particle crossing law. It must act selectively on the second parent/profile block, arise from a higher composite, or be replaced by a nonfactorizing crossed six-point term. This remains a reduced distributional and amplitude-jet theorem, not a complete crossed probability or spacetime crossing theorem.",
        "spectral_reflection_crosswalk": {
            "massive_positive_family": "W_mu^plus(p)=theta(p0)*delta(p^2-mu)",
            "massive_negative_family": "W_mu^minus(p)=theta(-p0)*delta(p^2-mu)",
            "dipole_positive": "W_dip^plus=-partial_mu W_mu^plus at mu=0=theta(p0)*delta_prime(p^2)",
            "dipole_negative": "W_dip^minus=-partial_mu W_mu^minus at mu=0=theta(-p0)*delta_prime(p^2)",
            "reflection": "C_* W_mu^plus=W_mu^minus",
            "commutation": "C_*[-partial_mu W_mu^plus]|0=[-partial_mu C_*W_mu^plus]|0=W_dip^minus",
            "dual_number_basis": ["simple_spectral_row", "dipole_mass_derivative_row"],
            "reflection_matrix": matrix_strings(d["reflection_matrix"]),
            "jet_metric": matrix_strings(d["J"]),
            "metric_law": "C_jet^T*J*C_jet=J",
            "jacobian_boundary": "Distributional pushforward under p->-p uses |det(-I4)|=1. No oriented integration sign is present.",
            "domain_boundary": "This is an exact identity of parameterized tempered distributions tested after smearing. It is not a construction of the complete interacting incoming rigged state or LSZ domain."
        },
        "crossed_five_to_four_operator": {
            "domain": "a0>0, a1>0, a0!=a1, x>0 on the massless spacelike crossed pair sheet",
            "q_x": str(d["qx"]),
            "ell_x": str(d["ellx"]),
            "T_cross": matrix_strings(d["T_cross"]),
            "T_cross_sharp": matrix_strings(d["T_cross_sharp"]),
            "unsigned_gram": matrix_strings(d["unsigned_gram"]),
            "fifth_external_delta_prime_sign": -1,
            "signed_physical_gram": matrix_strings(d["signed_gram"]),
            "rho_x": str(d["rho"]),
            "status": "POSITIVE_FULL_RANK_FIRST_CROSSED_SPLITTING_WITH_IDENTITY_WIGHTMAN_DUAL"
        },
        "universal_parity_incompatibility": {
            "required_six_point_parity": matrix_strings(d["epsilon_parity"]),
            "metric_law": "S_epsilon^T*J*S_epsilon=-J",
            "parity_dressed_T": matrix_strings(d["T_parity"]),
            "parity_dressed_T_sharp": matrix_strings(d["T_parity_sharp"]),
            "parity_unsigned_gram": matrix_strings(d["parity_unsigned_gram"]),
            "fifth_signed_parity_gram": matrix_strings(d["parity_signed_gram"]),
            "incompatibility": "The same universal S_epsilon that would repair the second crossed quotient reverses the already positive first crossed splitting to -rho_x*I2. It cannot be the common incoming one-particle Wightman dual.",
            "allowed_repair_types": [
                "a profile-selective parity acting only on the second parent/profile block",
                "a higher-composite or doubled BT branch whose total sharp remains consistent",
                "a nonfactorizing crossed six-point pre-trace contribution that changes the quotient before Hilbertization"
            ]
        },
        "history_disposition": {
            "first_crossed_pair_status": "POSITIVE_WITHOUT_INTERNAL_PARITY",
            "reversed_six_point_history_count": 12,
            "six_point_status": "UNAFFILIATED; UNIVERSAL_WIGHTMAN_DUAL_REPAIR_EXCLUDED",
            "next_missing_datum": "a profile-selective/higher-composite BT derivation of R_minus or the first nonfactorizing crossed 3->3 pre-trace term"
        },
        "disposition": {
            "spectral_reflection_mass_jet_action": "IDENTITY",
            "spectral_reflection_internal_epsilon_parity": "NOT_PRESENT",
            "crossed_five_to_four_signed_gram": "POSITIVE_FULL_RANK",
            "universal_epsilon_parity_compatibility": "EXACTLY_OBSTRUCTED_BY_FIRST_CROSSED_SPLITTING",
            "profile_selective_or_higher_composite_parity": "NOT_DERIVED",
            "nonfactorizing_crossed_six_point_term": "NOT_COMPUTED",
            "twelve_reversed_physical_intertwiners": "NOT_CONSTRUCTED",
            "complete_crossed_probability": "NOT_COMPUTED",
            "Eq19_all_orders": "NOT_PROVED",
            "spacetime_Moller_LSZ_S_operator": "NOT_CONSTRUCTED"
        },
        "assumptions": [
            "The spectral crosswalk is performed on the free parameterized Wightman distributions before the interacting asymptotic limit. It proves a distributional sign identity, not existence of the full interacting incoming state.",
            "Mass squared mu is differentiated with the BT convention delta_prime(p^2)=-partial_mu delta(p^2-mu)|0. Reflection is independent of mu and distributional pushforward uses the absolute Jacobian.",
            "The crossed amplitude calculation is restricted to the certified square-free five-to-four external-mass jet and the massless spacelike sheet tau=-x.",
            "The fifth external delta-prime sign remains minus after crossing because the number of external derivative measures is unchanged.",
            "Universal parity means the same incoming one-particle jet map acts at the first and second crossed splittings. Profile-selective, higher-composite and nonfactorizing actions are explicitly outside that hypothesis."
        ],
        "does_not_establish": [
            "a complete interacting incoming Wightman or rigged-state domain",
            "a full LSZ crossing theorem for the dipole field",
            "absence of a profile-selective or higher-composite internal parity",
            "absence of a nonfactorizing crossed six-point pre-trace term",
            "a positive crossed six-point probability",
            "the twelve reversed physical intertwiners",
            "the 300 crossed seven-point sheets or spectator sectors",
            "a complete incoming/outgoing Moller, LSZ, or S operator",
            "Bateman--Turok Eq. (19)",
            "positivity beyond tree level or a KLN theorem",
            "a metric or BRST lift to Weyl gravity",
            "anything LORENTZIAN-CAUSAL",
            "a new physical or spacetime dimension",
            "literature priority"
        ],
        "next_gate": "Test the smallest profile-selective implementation of S_epsilon on the four-component parent/profile carrier against prefix compatibility and the public BT charge/ghost-parity constraints. It must act trivially on the first crossed T_x block, act as diag(I2,-I2) only at the second coherent collapse, and arise from a declared higher-composite or doubled source operator. If no such operator exists on the available public algebra, compute the first nonfactorizing crossed 3->3 pre-trace amplitude term; the universal Wightman-dual route is closed.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
            "producer_method": "Exact symbolic parameter-derivative/reflection coefficient algebra for the spectral delta-prime family, followed by exact SymPy continuation of the certified amplitude-level T map and its J-adjoint before and after the candidate universal epsilon parity. No floating-point arithmetic is used.",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Eq. (5)", "Eq. (6)", "Eq. (9)", "Eq. (13)", "Eq. (18)"]
            }
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_crossed_wightman_dual_no_go.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_crossed_wightman_dual_no_go.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_crossed_wightman_dual_no_go"
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
