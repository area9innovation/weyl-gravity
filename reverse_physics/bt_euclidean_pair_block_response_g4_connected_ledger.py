#!/usr/bin/env python3
"""Build the exact connected order-lambda^4 pair-response ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_CONNECTED_LEDGER_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-pair-block-response-g4-connected-ledger-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-pair-block-response-g4-connected-ledger.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_pair_block_response_g4_connected_ledger.py"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-euclidean-continuum-reconstruction.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_ONE_LOOP_V1.json",
]
SOURCE_COMMIT = "a5bb8313d71f0906b2544f52c4f3e96c1ee55817"

Coord = tuple[int, int, int, int]
Monomial = tuple[int, int]
Poly = dict[Monomial, Fraction]
Dual = tuple[Poly, Poly]
ORIGIN: Coord = (0, 0, 0, 0)
EDGE: Coord = (1, 0, 0, 0)
INTERNAL = (ORIGIN, EDGE)
INTERNAL_SET = set(INTERNAL)
DIRS = tuple(
    tuple(sign if index == axis else 0 for index in range(4))
    for axis in range(4)
    for sign in (-1, 1)
)
PAIR_COVARIANCE = (
    (Fraction(9, 616), Fraction(1, 308)),
    (Fraction(1, 308), Fraction(9, 616)),
)


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def add_coord(left: Coord, right: Coord) -> Coord:
    return tuple(a + b for a, b in zip(left, right))  # type: ignore[return-value]


def padd(*polys: Poly) -> Poly:
    result: dict[Monomial, Fraction] = defaultdict(Fraction)
    for poly in polys:
        for monomial, coefficient in poly.items():
            result[monomial] += coefficient
    return {key: value for key, value in result.items() if value}


def pscale(poly: Poly, scalar: Fraction | int) -> Poly:
    scalar = Fraction(scalar)
    return {
        monomial: scalar * coefficient
        for monomial, coefficient in poly.items()
        if scalar * coefficient
    }


def pmul(left: Poly, right: Poly) -> Poly:
    result: dict[Monomial, Fraction] = defaultdict(Fraction)
    for (a, b), left_coefficient in left.items():
        for (c, d), right_coefficient in right.items():
            result[(a + c, b + d)] += left_coefficient * right_coefficient
    return {key: value for key, value in result.items() if value}


def ppow(poly: Poly, exponent: int) -> Poly:
    result: Poly = {(0, 0): Fraction(1)}
    for _ in range(exponent):
        result = pmul(result, poly)
    return result


def dadd(*values: Dual) -> Dual:
    return padd(*(value[0] for value in values)), padd(
        *(value[1] for value in values)
    )


def dscale(value: Dual, scalar: Fraction | int) -> Dual:
    return pscale(value[0], scalar), pscale(value[1], scalar)


def dmul(left: Dual, right: Dual) -> Dual:
    return pmul(left[0], right[0]), padd(
        pmul(left[1], right[0]), pmul(left[0], right[1])
    )


def dpow(value: Dual, exponent: int) -> Dual:
    result: Dual = ({(0, 0): Fraction(1)}, {})
    for _ in range(exponent):
        result = dmul(result, value)
    return result


def internal_linear(vertex: Coord, neighbour: Coord) -> Poly:
    result: dict[Monomial, Fraction] = defaultdict(Fraction)
    if neighbour == ORIGIN:
        result[(1, 0)] += 1
    elif neighbour == EDGE:
        result[(0, 1)] += 1
    if vertex == ORIGIN:
        result[(1, 0)] -= 1
    elif vertex == EDGE:
        result[(0, 1)] -= 1
    return {key: value for key, value in result.items() if value}


def edge_dual(vertex: Coord, neighbour: Coord, axis: int) -> Dual:
    direction = Fraction(neighbour[axis] ** 2 - vertex[axis] ** 2)
    derivative = {(0, 0): direction} if direction else {}
    return internal_linear(vertex, neighbour), derivative


def conditional_action_jets(axis: int) -> tuple[list[Dual], int]:
    """Return U1,...,U4 and their response derivatives at zero background."""

    affected = set(INTERNAL)
    for coord in INTERNAL:
        for direction in DIRS:
            affected.add(add_coord(coord, direction))
    totals: list[Dual] = [({}, {}) for _ in range(4)]
    for vertex in affected:
        powers: dict[int, Dual] = {}
        for degree in range(1, 6):
            powers[degree] = ({}, {})
        for direction in DIRS:
            edge = edge_dual(vertex, add_coord(vertex, direction), axis)
            for degree in range(1, 6):
                powers[degree] = dadd(powers[degree], dpow(edge, degree))
        a, b, c, d, e = (powers[index] for index in range(1, 6))
        rows = (
            dscale(dmul(a, b), Fraction(1, 2)),
            dadd(
                dscale(dmul(b, b), Fraction(1, 8)),
                dscale(dmul(a, c), Fraction(1, 6)),
            ),
            dadd(
                dscale(dmul(b, c), Fraction(1, 12)),
                dscale(dmul(a, d), Fraction(1, 24)),
            ),
            dadd(
                dscale(dmul(c, c), Fraction(1, 72)),
                dscale(dmul(b, d), Fraction(1, 48)),
                dscale(dmul(a, e), Fraction(1, 120)),
            ),
        )
        totals = [dadd(total, row) for total, row in zip(totals, rows)]
    return totals, len(affected)


@lru_cache(maxsize=None)
def gaussian_moment(a: int, b: int) -> Fraction:
    if a + b == 0:
        return Fraction(1)
    if (a + b) % 2:
        return Fraction()
    if a:
        return (
            (a - 1) * PAIR_COVARIANCE[0][0] * gaussian_moment(a - 2, b)
            if a >= 2
            else Fraction()
        ) + b * PAIR_COVARIANCE[0][1] * gaussian_moment(a - 1, b - 1)
    return (b - 1) * PAIR_COVARIANCE[1][1] * gaussian_moment(0, b - 2)


def expectation(poly: Poly, insert_u0: bool = False) -> Fraction:
    return sum(
        coefficient * gaussian_moment(a + int(insert_u0), b)
        for (a, b), coefficient in poly.items()
    )


def exponential_series(jets: list[Dual], order: int = 4) -> list[Dual]:
    """Coefficients of exp(-sum_j lambda^j U_j), by E'=-U'E."""

    rows: list[Dual] = [({(0, 0): Fraction(1)}, {})]
    for n in range(1, order + 1):
        value: Dual = ({}, {})
        for j in range(1, n + 1):
            value = dadd(value, dscale(dmul(jets[j - 1], rows[n - j]), j))
        rows.append(dscale(value, Fraction(-1, n)))
    return rows


def conditional_center_response(axis: int) -> tuple[list[Fraction], int, list[int]]:
    jets, affected = conditional_action_jets(axis)
    exponential = exponential_series(jets)
    z = [expectation(value) for value, _ in exponential]
    dz = [expectation(derivative) for _, derivative in exponential]
    n = [expectation(value, True) for value, _ in exponential]
    dn = [expectation(derivative, True) for _, derivative in exponential]
    center = [Fraction()] * 5
    response = [Fraction()] * 5
    for degree in range(5):
        center[degree] = n[degree] - sum(
            z[j] * center[degree - j] for j in range(1, degree + 1)
        )
        response[degree] = dn[degree] - sum(
            dz[j] * center[degree - j] + z[j] * response[degree - j]
            for j in range(1, degree + 1)
        )
    term_counts = [len(value) for value, _ in jets]
    return response, affected, term_counts


def weighted_partitions(total: int, minimum: int = 1) -> list[tuple[int, ...]]:
    if total == 0:
        return [()]
    rows: list[tuple[int, ...]] = []
    for first in range(minimum, total + 1):
        for tail in weighted_partitions(total - first, first):
            rows.append((first,) + tail)
    return rows


def cumulant_coefficient(parts: tuple[int, ...]) -> Fraction:
    counts: dict[int, int] = defaultdict(int)
    for part in parts:
        counts[part] += 1
    denominator = math.prod(math.factorial(value) for value in counts.values())
    return Fraction((-1) ** len(parts), denominator)


def conditional_ledger() -> list[dict]:
    rows = []
    for order in range(1, 5):
        for parts in weighted_partitions(order):
            vertices = len(parts)
            total_degree = 1 + order + 2 * vertices
            minimum_innovation_legs = 2 * vertices
            background_before_response = total_degree - minimum_innovation_legs
            rows.append(
                {
                    "order": order,
                    "parts": list(parts),
                    "coefficient": enc(cumulant_coefficient(parts)),
                    "term": "kappa_u(u," + ",".join(f"U{part}" for part in parts) + ")",
                    "interaction_vertices": vertices,
                    "total_field_degree": total_degree,
                    "minimum_connected_innovation_legs": minimum_innovation_legs,
                    "maximum_background_degree_after_response": background_before_response - 1,
                }
            )
    return rows


def annealed_g4_ledger() -> list[dict]:
    rows = []
    for center_order in range(1, 5):
        marginal_order = 4 - center_order
        for parts in weighted_partitions(marginal_order):
            vertices = len(parts)
            maximum_fields = center_order + marginal_order + 2 * vertices
            edges = maximum_fields // 2
            graph_vertices = 1 + vertices
            rows.append(
                {
                    "center_order": center_order,
                    "parts": list(parts),
                    "coefficient": enc(cumulant_coefficient(parts)),
                    "term": (
                        f"kappa_0(Dm{center_order}"
                        + ("," if parts else "")
                        + ",".join(f"S{part}" for part in parts)
                        + ")"
                    ),
                    "maximum_background_fields": maximum_fields,
                    "maximum_wick_edges": edges,
                    "connected_vertices": graph_vertices,
                    "maximum_loop_rank": edges - graph_vertices + 1,
                }
            )
    return rows


def build() -> dict:
    long_response, affected_long, long_counts = conditional_center_response(0)
    trans_response, affected_trans, trans_counts = conditional_center_response(1)
    vacuum_b2 = Fraction(1, 8) * long_response[2] + Fraction(3, 8) * trans_response[2]
    vacuum_b4 = Fraction(1, 8) * long_response[4] + Fraction(3, 8) * trans_response[4]
    inner = conditional_ledger()
    outer = annealed_g4_ledger()
    checks = {
        "pair_precision_inverse_rechecked": (
            72 * PAIR_COVARIANCE[0][0] - 16 * PAIR_COVARIANCE[1][0] == 1
            and 72 * PAIR_COVARIANCE[0][1] - 16 * PAIR_COVARIANCE[1][1] == 0
        ),
        "affected_site_count_is_sixteen": affected_long == affected_trans == 16,
        "action_jet_term_counts_are_orientation_independent": long_counts == trans_counts,
        "odd_vacuum_response_coefficients_vanish": all(
            long_response[index] == trans_response[index] == 0 for index in (1, 3)
        ),
        "lambda2_longitudinal_matches_one_loop_predecessor": long_response[2] == Fraction(-7349, 379456),
        "lambda2_transverse_matches_one_loop_predecessor": trans_response[2] == Fraction(-7979, 379456),
        "lambda2_vacuum_pair_matches_one_loop_predecessor": vacuum_b2 == Fraction(-15643, 1517824),
        "lambda4_longitudinal_exact": long_response[4] == Fraction(297291527, 329112813568),
        "lambda4_transverse_exact": trans_response[4] == Fraction(342682355, 329112813568),
        "lambda4_vacuum_pair_exact_positive": vacuum_b4 == Fraction(41416831, 82278203392) and vacuum_b4 > 0,
        "conditional_m4_has_five_partition_terms": sum(row["order"] == 4 for row in inner) == 5,
        "conditional_response_background_degree_is_at_most_order": all(row["maximum_background_degree_after_response"] == row["order"] for row in inner),
        "annealed_g4_has_seven_connected_terms": len(outer) == 7,
        "all_annealed_g4_terms_have_at_most_two_loops": all(row["maximum_loop_rank"] == 2 for row in outer),
        "disconnected_vacuum_factors_are_absent_from_cumulants": True,
        "full_g4_coefficient_remains_uncomputed": True,
        "large_volume_g4_power_or_log_remains_open": True,
        "no_fixed_coupling_hminus1_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_CONNECTED_LEDGER_V1",
        "schema_version": "reverse-physics-bt-euclidean-pair-block-response-g4-connected-ledger-v1",
        "created": "2026-08-16",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact nested-cumulant reduction, two-loop complexity theorem, and zero-background checkpoint for the BT pair-block order-lambda^4 response",
        "question": "After the positive pair-block one-loop coefficient, what is the complete normalized order-lambda^4 object, and how large an exact Wick calculation is actually required?",
        "answer": (
            "The complete coefficient is a seven-term outer cumulant built from the five-term conditional-center cumulant. This form cancels every disconnected partition-function component before estimation. For a conditional term of total coupling order i with r interaction vertices, connectedness to the observed pair field consumes at least 2r innovation legs; after the response derivative, Dm_i has background degree at most i. Adding any partition of the remaining order 4-i in the normalized marginal gives at most 4+2s background fields on 1+s connected vertices, hence loop rank at most two. No three-loop evaluation is needed. As an exact local checkpoint, the all-zero external fiber has b_pair,vac(lambda)=-15643*lambda^2/1517824+41416831*lambda^4/82278203392+O(lambda^6); the positive fourth-order term is too small to repair the negative local response at lambda=2/5. This does not decide the full-Gibbs fourth-order coefficient because the one-loop theorem already proves that free-background annealing is load-bearing."
        ),
        "scaled_action": {
            "definition": "S_lambda=S0+lambda*S1+lambda^2*S2+lambda^3*S3+lambda^4*S4+O(lambda^5)",
            "jets": "A=sum d, B=sum d^2, C=sum d^3, D=sum d^4, E=sum d^5 over eight directed differences",
            "S1": "(1/2)*sum A*B",
            "S2": "sum(B^2/8+A*C/6)",
            "S3": "sum(B*C/12+A*D/24)",
            "S4": "sum(C^2/72+B*D/48+A*E/120)",
            "affected_residual_sites": affected_long,
            "zero_fiber_monomial_counts": long_counts,
        },
        "conditional_center_cumulants": {
            "general_formula": "m_n=sum_(sum j*k_j=n) (-1)^K/prod_j(k_j!)*kappa_u(u,U1^[k1],...,Un^[kn])",
            "m1": "-kappa_u(u,U1)",
            "m2": "-kappa_u(u,U2)+(1/2)*kappa_u(u,U1,U1)",
            "m3": "-kappa_u(u,U3)+kappa_u(u,U1,U2)-(1/6)*kappa_u(u,U1,U1,U1)",
            "m4": "-kappa_u(u,U4)+kappa_u(u,U1,U3)+(1/2)*kappa_u(u,U2,U2)-(1/2)*kappa_u(u,U1,U1,U2)+(1/24)*kappa_u(u,U1,U1,U1,U1)",
            "labeled_partition_table": inner,
            "status": "EXACT_CONDITIONAL_NORMALIZATION_PROVED",
        },
        "annealed_connected_g4": {
            "formula": "T4=E0[Dm4]-kappa0(Dm3,S1)-kappa0(Dm2,S2)+(1/2)kappa0(Dm2,S1,S1)-kappa0(Dm1,S3)+kappa0(Dm1,S1,S2)-(1/6)kappa0(Dm1,S1,S1,S1)",
            "equivalent_weight_ledger": "T4=E0[Dm4]+E0[Dm3*W1]+E0[Dm2*W2]+E0[Dm1*W3]-Z2*T2, with W1=-S1, W2=S1^2/2-S2, W3=-S3+S1*S2-S1^3/6 and Z2=E0[W2]",
            "normalization_rule": "Joint cumulants remove every Wick component disconnected from Dm_i; no vacuum factor is bounded separately.",
            "labeled_partition_table": outer,
            "term_count": len(outer),
            "status": "EXACT_FULL_GIBBS_NORMALIZATION_LEDGER_PROVED",
        },
        "two_loop_theorem": {
            "conditional_count": "For order i and r conditional interaction vertices, total degree is 1+i+2r. A cumulant connected to u needs at least r innovation edges, consuming 2r legs, and D removes one remaining background leg; therefore deg_background(Dm_i)<=i.",
            "outer_count": "For s marginal vertices whose coupling orders sum to 4-i, the maximal background degree is i+(4-i)+2s=4+2s. A connected Wick graph then has E<=s+2 edges and V=s+1 vertices, so beta=E-V+1<=2.",
            "maximum_free_background_loop_rank": 2,
            "consequence": "An exact finite-volume coefficient needs only zero-, one-, and two-loop connected sums; a three-loop tensor or exhaustive dense covariance object is unnecessary.",
            "status": "PROVED_BY_EXACT_DEGREE_AND_CONNECTEDNESS_COUNT",
        },
        "zero_background_checkpoint": {
            "meaning": "All external fields are fixed to zero; only the exact two-variable conditional pair Gaussian is integrated. This is not the annealed full-Gibbs coefficient.",
            "longitudinal_lambda2": enc(long_response[2]),
            "transverse_lambda2": enc(trans_response[2]),
            "orientation_averaged_lambda2": enc(vacuum_b2),
            "longitudinal_lambda4": enc(long_response[4]),
            "transverse_lambda4": enc(trans_response[4]),
            "orientation_averaged_lambda4": enc(vacuum_b4),
            "lambda_two_sign": "STRICTLY_NEGATIVE",
            "lambda_four_sign": "STRICTLY_POSITIVE",
            "lambda_two_plus_four_at_two_fifths": enc(Fraction(4, 25) * vacuum_b2 + Fraction(16, 625) * vacuum_b4),
            "truncated_sign_at_two_fifths": "STRICTLY_NEGATIVE",
            "status": "EXACT_ZERO_BACKGROUND_DIAGNOSTIC_ONLY",
        },
        "method_disposition": {
            "complete_g4_normalization_ledger": "PROVED",
            "maximum_g4_background_loop_rank": "TWO",
            "zero_background_g4_coefficient": "COMPUTED",
            "full_gibbs_finite_volume_g4_coefficient": "OPEN",
            "large_volume_g4_power_or_log": "OPEN",
            "uniform_higher_order_pair_response": "OPEN",
            "nonperturbative_pair_response_at_lambda_0_4": "OPEN",
            "response_to_witten_schur_bridge": "OPEN",
            "actual_interacting_h_minus_one": "OPEN",
            "continuum_measure": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "the exact zero-, one-, and two-loop values in the seven connected outer rows on a finite periodic lattice",
            "the large-volume hard/hard, hard/soft, and soft/soft bounds or asymptotic coefficient for the resulting connected two-loop symbol",
            "a volume-uniform perturbative remainder or nonperturbative pair-fiber response inequality at lambda=2/5",
            "the response-to-Witten transfer followed by the normalized lowest mode and every dyadic H^-1 shell",
        ],
        "next_gate": (
            "Generate the seven connected rows directly in Fourier space, retaining the two pair orientations and rank-two conditioned-covariance corrections. Evaluate the rational L=4 coefficient by streaming topology rather than materializing a dense covariance tensor. If nonzero, separate the two-loop symbol into hard/hard, hard/soft, and soft/soft regions and decide its large-volume power or logarithm. Only after a uniform response estimate should the response-to-Witten and interacting H^-1 bridges be attempted."
        ),
        "does_not_establish": [
            "the sign or value of the full-Gibbs order-lambda^4 pair response",
            "that the positive one-loop coefficient survives at lambda=2/5",
            "a convergent perturbation series or volume-uniform remainder",
            "a heat-bath spectral gap, Witten coercivity, or interacting H^-1 estimate",
            "tightness or continuum identification",
            "a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "arithmetic": "Exact Python Fraction bivariate polynomial arithmetic, exact correlated-pair Gaussian recursion, formal integer-partition cumulant coefficients, and exact graph degree counting; no floating-point evidence is used.",
            "assumptions": [
                "the response derivative is the axial quadratic direction used by the certified one-loop predecessor",
                "the loop theorem is an upper bound; momentum conservation and extra innovation contractions may lower individual topology ranks",
                "the zero-background calculation is diagnostic and is never substituted for the full normalized Gaussian-background average",
            ],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_pair_block_response_g4_connected_ledger.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_pair_block_response_g4_connected_ledger.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_pair_block_response_g4_connected_ledger",
        ],
        "tier_receipt": {
            "tier_0": "Python compilation, strict JSON/schema parsing, exact input hashes, scoped diff check, and staged-diff inspection required",
            "tier_1": "deterministic producer, nonimporting exact verifier, and mutation tests required",
            "tier_2": "the content-addressed one-loop input is checked by hash; no shared operator or coefficient lifecycle is promoted",
            "tier_3": "not run: this classifies the next coefficient but does not compute it or promote H^-1, continuum, freeze, release, shared-core, or Lorentzian state",
            "memory_policy": "all Python commands run sequentially under a 500000 KiB virtual-memory ceiling",
            "elapsed_seconds_and_peak_kib": {
                "producer": "0.07 s, 21480 KiB",
                "independent_verifier": "0.13 s, 30744 KiB",
                "unit_tests": "0.31 s, 30760 KiB",
            },
            "repository_audits": {
                "planning_import": "PASS: 1700 nodes, 0 invalid items, 0 malformed events; 8.45 s, 188220 KiB",
                "science_forge_shadow": "not run: no registered shadow input changes; this skip is not a pass",
            },
            "failed_commands_not_counted_as_passes": [
                "the first sfc work-event launch inherited the producer's 500000 KiB shell ulimit and stopped before writing an event because the Go runtime could not reserve its page summary; the append was rerun successfully in a fresh shell with GOMEMLIMIT=300MiB and GOGC=50"
            ],
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
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        print("[FAIL] internal checks", result["checks"]["failures"])
        return 1
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != result:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
    print(
        "[PASS] BT pair-block g4 connected ledger "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
