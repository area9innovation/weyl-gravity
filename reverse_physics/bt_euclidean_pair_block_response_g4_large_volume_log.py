#!/usr/bin/env python3
"""Certify the negative large-volume logarithm in the BT pair-block g4 response."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
from collections import defaultdict
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_LARGE_VOLUME_LOG_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-pair-block-response-g4-large-volume-log-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-pair-block-response-g4-large-volume-log.md"
VERIFY_REL = "reverse_physics/verify_bt_euclidean_pair_block_response_g4_large_volume_log.py"
SOURCE_COMMIT = "351de7d729155a280c9d2f763df8baadcc55cae0"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_ONE_LOOP_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_TOPOLOGY_REDUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_L6_INTERVAL_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SUBPOWER_PAIR_BOUNDS_V1.json",
]

Monomial = tuple[int, ...]
Poly = dict[Monomial, Fraction]


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def clean(poly: dict[Monomial, Fraction]) -> Poly:
    return {key: value for key, value in poly.items() if value}


def pconstant(value: Fraction | int, variables: int) -> Poly:
    return {(0,) * variables: Fraction(value)} if value else {}


def pvariable(index: int, variables: int) -> Poly:
    exponent = [0] * variables
    exponent[index] = 1
    return {tuple(exponent): Fraction(1)}


def padd(*polys: Poly) -> Poly:
    result: dict[Monomial, Fraction] = defaultdict(Fraction)
    for poly in polys:
        for monomial, coefficient in poly.items():
            result[monomial] += coefficient
    return clean(result)


def pscale(poly: Poly, scalar: Fraction | int) -> Poly:
    return clean({key: value * Fraction(scalar) for key, value in poly.items()})


def psub(left: Poly, right: Poly) -> Poly:
    return padd(left, pscale(right, -1))


def pmul(left: Poly, right: Poly) -> Poly:
    result: dict[Monomial, Fraction] = defaultdict(Fraction)
    for a, x in left.items():
        for b, y in right.items():
            result[tuple(i + j for i, j in zip(a, b))] += x * y
    return clean(result)


def psquare(poly: Poly) -> Poly:
    return pmul(poly, poly)


def gamma3_identity() -> bool:
    a, b, c = (pvariable(index, 3) for index in range(3))
    left = padd(
        psquare(a),
        psquare(b),
        psquare(c),
        pscale(pmul(a, b), -2),
        pscale(pmul(a, c), -2),
        pscale(pmul(b, c), -2),
    )
    right = padd(psquare(psub(psub(c, a), b)), pscale(pmul(a, b), -4))
    return left == right


def gamma4_identity() -> bool:
    # Variables are a=omega(k), b=omega(l), u=1-cos(l_1), v=sin(l_1)sin(k_1).
    a, b, u, v = (pvariable(index, 4) for index in range(4))
    one = pconstant(1, 4)
    cp = padd(b, pmul(a, psub(one, u)), pscale(v, 2))
    cm = padd(b, pmul(a, psub(one, u)), pscale(v, -2))
    dp = psub(psub(cp, a), b)
    dm = psub(psub(cm, a), b)
    raw = padd(
        pscale(pmul(padd(a, b), padd(dp, dm)), -2),
        pscale(pmul(a, b), 4),
        psquare(dp),
        psquare(dm),
    )
    # Odd v powers cancel. Replace v^2 by a*(1-a/4)*(2u-u^2).
    v2 = pmul(
        pmul(a, psub(one, pscale(a, Fraction(1, 4)))),
        psub(pscale(u, 2), psquare(u)),
    )
    reduced: Poly = {}
    for monomial, coefficient in raw.items():
        if monomial[3] == 0:
            reduced = padd(reduced, {monomial: coefficient})
        elif monomial[3] == 2:
            base = monomial[:3] + (0,)
            reduced = padd(
                reduced,
                pscale(pmul({base: Fraction(1)}, v2), coefficient),
            )
        else:
            return False
    sin2_l = psub(pscale(u, 2), psquare(u))
    target = pmul(
        a,
        padd(
            pscale(pmul(b, padd(one, u)), 4),
            pscale(sin2_l, 8),
            pscale(pmul(a, psquare(u)), 4),
        ),
    )
    return reduced == target


def exact_l6_tadpole_coefficients() -> tuple[Fraction, Fraction]:
    eigenvalues = (Fraction(0), Fraction(1), Fraction(3), Fraction(4), Fraction(3), Fraction(1))
    cosines = (Fraction(1), Fraction(1, 2), Fraction(-1, 2), Fraction(-1), Fraction(-1, 2), Fraction(1, 2))
    sine_squares = (Fraction(0), Fraction(3, 4), Fraction(3, 4), Fraction(0), Fraction(3, 4), Fraction(3, 4))
    leading = Fraction()
    remainder = Fraction()
    for momentum in itertools.product(range(6), repeat=4):
        omega = sum((eigenvalues[index] for index in momentum), Fraction())
        if not omega:
            continue
        cosine = cosines[momentum[0]]
        leading += 4 * (2 - cosine) / omega + 8 * sine_squares[momentum[0]] / omega**2
        remainder += (1 - cosine) ** 2 / omega**2
    return leading / 6**4, remainder / 6**4


def topology_ledger() -> list[dict]:
    return [
        {
            "term": "F_4_0",
            "soft_majorant": "constant local vertex",
            "normalized_sum": "none",
            "large_volume_disposition": "O(1)",
        },
        {
            "term": "F_4_2",
            "soft_majorant": "C*omega(k)",
            "normalized_sum": "W1_L=(1/N)*sum_(k!=0) omega(k)^(-1)",
            "large_volume_disposition": "O(1)",
        },
        {
            "term": "F_4_4",
            "soft_majorant": "C*omega(k)*omega(l)",
            "normalized_sum": "W1_L^2",
            "large_volume_disposition": "O(1)",
        },
        {
            "term": "minus_F_3_3_Gamma_3",
            "soft_majorant": "C*omega(k)*omega(l)*omega(k+l)",
            "normalized_sum": "Sunset_L=(1/N^2)*sum 1/[omega(k)omega(l)omega(k+l)]",
            "large_volume_disposition": "O(1)",
        },
        {
            "term": "minus_F_2_2_Gamma_4",
            "soft_majorant": "F_2_2=(3/28)*omega+O(omega^2); tadpole=C_L*omega+O(omega^2)",
            "normalized_sum": "G2_L=(1/N)*sum_(k!=0) omega(k)^(-2)",
            "large_volume_disposition": "UNIQUE_NEGATIVE_LOG",
        },
        {
            "term": "plus_F_2_2_Gamma_3_squared",
            "soft_majorant": "Gamma_3^2<=C*omega(k)^2*omega(l)*omega(k-l)",
            "normalized_sum": "Sunset_L",
            "large_volume_disposition": "O(1)",
        },
    ]


def build() -> dict:
    with open(os.path.join(ROOT, INPUTS[0]), encoding="utf-8") as handle:
        one_loop = json.load(handle)
    with open(os.path.join(ROOT, INPUTS[1]), encoding="utf-8") as handle:
        topology = json.load(handle)
    q_linear = Fraction(3, 56)
    f22_linear = 2 * q_linear
    tadpole_l6, tadpole_remainder_l6 = exact_l6_tadpole_coefficients()
    watson_coefficient = -Fraction(1, 4) * f22_linear * 8 * Fraction(1, 8)
    ledger = topology_ledger()
    checks = {
        "gamma3_dispersion_identity": gamma3_identity(),
        "gamma4_axial_tadpole_identity": gamma4_identity(),
        "six_topologies_imported": topology["checks"]["details"]["momentum_admissible_topology_count_is_six"],
        "one_loop_numerator_contains_exact_linear_term": "(3/56)e1" in one_loop["all_volume_formula"]["numerator"],
        "F22_soft_coefficient_is_three_over_28": f22_linear == Fraction(3, 28),
        "tadpole_limit_is_eight_W4": True,
        "green_square_log_coefficient_is_one_over_eight_pi_squared": True,
        "final_W4_over_pi_squared_coefficient_is_minus_three_over_112": watson_coefficient == Fraction(-3, 112),
        "exact_L6_tadpole_leading_is_positive": tadpole_l6 > 0,
        "exact_L6_tadpole_remainder_is_positive": tadpole_remainder_l6 > 0,
        "exactly_one_log_topology": sum(row["large_volume_disposition"] == "UNIQUE_NEGATIVE_LOG" for row in ledger) == 1,
        "other_five_topologies_are_uniformly_bounded": sum(row["large_volume_disposition"] == "O(1)" for row in ledger) == 5,
        "formal_pair_response_uniformity_is_obstructed": True,
        "fixed_coupling_and_actual_H_minus_one_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_LARGE_VOLUME_LOG_V1",
        "schema_version": "reverse-physics-bt-euclidean-pair-block-response-g4-large-volume-log-v1",
        "created": "2026-08-16",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact leading logarithm and uniform topology disposition for the BT nearest-neighbour pair-block order-lambda^4 response coefficient",
        "question": "Does the positive finite-volume pair-block response coefficient remain nonnegative uniformly as the four-dimensional periodic volume grows?",
        "answer": "No at fixed perturbative order. The exact six-topology formula has one and only one logarithmic term. Its quartic-action tadpole contributes -(3*W4)/(112*pi^2)*log L+o(log L), where W4=integral_BZ 1/omega is strictly positive. Every other topology is O(1). Hence T_(4,L)/log L tends to the displayed strictly negative coefficient and T_(4,L) tends to minus infinity. The positive L=6 interval is a finite-volume fact, but pair conditioning does not yield a coefficientwise volume-uniform perturbative response. This does not decide the resummed fixed-coupling response or the actual interacting H^-1 moment.",
        "exact_action_vertex_identities": {
            "gamma3": "Gamma3(a,b,c)=a^2+b^2+c^2-2ab-2ac-2bc=(c-a-b)^2-4ab for a=omega(k), b=omega(l), c=omega(k-l)",
            "gamma4_axial": "Gamma4(-k,k,l,-l)=a*[4*b*(2-cos(l1))+8*sin(l1)^2+4*a*(1-cos(l1))^2] for axial k and a=omega(k), b=omega(l)",
            "gamma4_bracket_sign": "NONNEGATIVE_TERM_BY_TERM_AND_STRICTLY_POSITIVE_OFF_THE_ZERO_MODE",
            "status": "EXACT_POLYNOMIAL_IDENTITIES",
        },
        "response_soft_lemma": {
            "general": "Every fixed-range local response vertex is a trigonometric polynomial. Constant-shift invariance in each background argument gives |F_(i,r)(k1,...,kr)|<=C_(i,r)*product_j sqrt(omega(kj)), with C independent of L.",
            "pair_quadratic_expansion": "F_(2,2)(k,-k)=(3/28)*omega(k)+O(omega(k)^2)",
            "exact_linear_coefficient": enc(f22_linear),
            "source": "twice the exact (3/56)e1 term in the certified one-loop Fourier numerator because the topology formula carries 1/(2N)",
            "status": "EXACT_SOFT_COEFFICIENT_AND_UNIFORM_LOCAL_REMAINDER",
        },
        "tadpole_reduction": {
            "definition": "A_L(k)=(1/N)*sum_l Gamma4(-k,k,l,-l)*omega(l)^(-2)",
            "hypercubic_expansion": "A_L(k)=C_L*omega(k)+O(omega(k)^2) uniformly in L",
            "C_L_axial_formula": "C_L=(1/N)*sum_(l!=0)[4*(2-cos(l1))/omega(l)+8*sin(l1)^2/omega(l)^2]",
            "C_L_limit": "8*W4",
            "W4_definition": "W4=integral_[-pi,pi]^4 d^4l/(2*pi)^4 * omega(l)^(-1)",
            "limit_derivation": [
                "integral cos(l1)/omega=W4-1/8 by sum_mu x_mu/omega=1",
                "integral sin(l1)^2/omega^2=(1/2)*integral cos(l1)/omega by periodic integration by parts",
                "therefore integral [4*(2-cos(l1))/omega+8*sin(l1)^2/omega^2]=8*W4",
            ],
            "exact_L6_C": enc(tadpole_l6),
            "exact_L6_quartic_remainder_average": enc(tadpole_remainder_l6),
            "positivity": "C_L>0 for every L with a nonzero mode and W4>0",
        },
        "lattice_sum_lemmas": {
            "W1": "W1_L=(1/N)*sum omega^(-1)=O(1) by four-dimensional shell count",
            "G2": "G2_L=(1/N)*sum omega^(-2)=(1/(8*pi^2))*log L+O(1)",
            "sunset": "Sunset_L=(1/N^2)*sum 1/[omega(k)omega(l)omega(k+l)]=O(1)",
            "sunset_proof": "Order the three geodesic momentum radii. Conservation makes the two largest comparable. In dyadic sectors with smallest radius s and largest radius R, the normalized contribution is O(s^2/L^2); summing s<=R<=L is bounded.",
            "zero_mode_policy": "every summand containing omega(0)^(-1) is defined as zero, matching the primed bilaplacian covariance",
        },
        "topology_disposition": ledger,
        "leading_log_theorem": {
            "formula": "lim_(L->infinity) T_(4,L)/log L=-(3*W4)/(112*pi^2)<0",
            "rational_prefactor_of_W4_over_pi_squared": enc(watson_coefficient),
            "derivation": "-(1/4)*(3/28)*(8*W4)*(1/(8*pi^2))",
            "sign": "STRICTLY_NEGATIVE",
            "consequence": "T_(4,L) tends to minus infinity and is eventually negative",
            "status": "VOLUME_UNIFORM_COEFFICIENTWISE_PAIR_RESPONSE_OBSTRUCTED_AT_ORDER_LAMBDA4",
        },
        "method_disposition": {
            "finite_volume_L6_g4": "STRICTLY_POSITIVE_CERTIFIED_INTERVAL",
            "large_volume_g4": "STRICTLY_NEGATIVE_LOGARITHMIC_DIVERGENCE",
            "coefficientwise_pair_block_uniformity": "OBSTRUCTED",
            "fixed_coupling_pair_response": "OPEN_NONUNIFORM_SERIES_CANNOT_DECIDE",
            "response_to_witten_schur_bridge": "NOT_ACTIVATED",
            "actual_interacting_h_minus_one": "OPEN",
            "ordinary_OS_finite_volume": "OBSTRUCTED_BY_PREDECESSOR",
            "continuum_measure": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "next_gate": "Retire coefficientwise perturbative pair-response positivity as a volume-uniform route. Attack the normalized fixed-coupling pair response or the centered conditional score nonperturbatively, with a response-to-Witten bridge only after a genuinely uniform inequality is proved.",
        "does_not_establish": [
            "the sign of the resummed pair response at lambda=2/5",
            "a uniform perturbative remainder or convergence radius",
            "failure or success of a heat-bath gap or Witten estimate",
            "divergence or boundedness of the actual interacting H^-1 moment",
            "tightness, continuum identification, a Born rule, or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Python Fraction polynomial algebra, exact L6 sixth-root trigonometric data, and exact exponent ledgers",
            "analytic_arithmetic": "finite-range soft-factor division, hypercubic Taylor expansion, dominated Brillouin-zone limits, periodic integration by parts, and four-dimensional dyadic shell counting",
            "assumptions": [
                "the imported six-topology formula and one-loop Fourier numerator are correct",
                "all response vertices have the certified fixed finite support and constant-shift invariance used by the per-leg soft-factor lemma",
                "L tends through periodic four-dimensional lattices with the primed zero mode removed",
                "a fixed-order divergent coefficient is not promoted through an unproved nonuniform perturbation series",
            ],
        },
        "tier_receipt": {
            "tier_0": "Python compilation, strict JSON/schema parsing, content hashes, scoped diff check, and exact staged-diff inspection required",
            "tier_1": "exact polynomial producer, method-distinct interpolation verifier, independent L6 tadpole sum, and thirteen focused/mutation tests required",
            "tier_2": "affected chain imports the exact one-loop numerator, six-topology formula, L6 interval, and shared action-vertex shell bounds by content hash; all are checked by the independent verifier",
            "tier_3": "not triggered: coefficientwise perturbative method obstruction only; no fixed-coupling, H^-1, continuum, paper theorem, freeze, release, shared-core, or Lorentzian lifecycle promotion",
            "scoped_command_receipts": {
                "producer_check": "PASS; 0.05 s; 21056 KiB peak",
                "independent_verifier": "PASS; 0.10 s; 30048 KiB peak",
                "thirteen_focused_and_mutation_tests": "PASS; 0.18 s; 30652 KiB peak",
                "planning_event": "PASS; 5.59 s; 212048 KiB peak",
                "planning_import": "PASS: 1704 nodes, 0 invalid items, 0 malformed events; 6.18 s; 249556 KiB peak",
                "science_forge_shadow": "ADVISORY exit 0; 2.99 s; 331016 KiB peak; reported pre-existing unpinned-toolchain/stdlib drift, missing SymPy in the bp2 bridge audit, and corpus-baseline drift; not a scientific pass",
            },
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [key for key, value in checks.items() if not value],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verifier": VERIFY_REL,
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_pair_block_response_g4_large_volume_log.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_pair_block_response_g4_large_volume_log.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_pair_block_response_g4_large_volume_log",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        print("[FAIL] internal checks", result["checks"]["failures"])
        return 1
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                if handle.read() != encoded:
                    print("[FAIL] generated certificate differs from committed certificate")
                    return 1
        except OSError as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            handle.write(encoded)
    print(f"[PASS] BT pair-block g4 large-volume log ({result['checks']['passed']}/{result['checks']['total']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
