#!/usr/bin/env python3
"""Exact C6 audit of the BT transverse centered-residual Jacobian."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TRANSVERSE_RESIDUAL_JACOBIAN_GATE_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-transverse-residual-jacobian-gate-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-transverse-residual-jacobian-gate.md"
)
VERIFY_REL = (
    "reverse_physics/"
    "verify_bt_euclidean_transverse_residual_jacobian_gate.py"
)
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_SPECTRAHEDRAL_PUSHFORWARD_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_WEIGHTED_CURRENT_GATE_V2.json",
]
SOURCE_COMMIT = "db21ef6a7422a76f9f5bd28060a2307e74666ca2"
N = 6
ZERO = (0,) * N
BASIS = (
    (-1, -2, -2),
    (2, 3, 2),
    (-2, -2, -1),
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
)

Poly = dict[tuple[int, ...], Fraction]


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def clean(poly: Poly) -> Poly:
    return {key: value for key, value in poly.items() if value}


def add(left: Poly, right: Poly) -> Poly:
    out = dict(left)
    for key, value in right.items():
        out[key] = out.get(key, Fraction()) + value
    return clean(out)


def scale(poly: Poly, scalar: Fraction | int) -> Poly:
    scalar = Fraction(scalar)
    return clean({key: scalar * value for key, value in poly.items()})


def multiply(left: Poly, right: Poly) -> Poly:
    out: Poly = {}
    for a, ca in left.items():
        for b, cb in right.items():
            exponent = tuple(a[i] + b[i] for i in range(N))
            out[exponent] = out.get(exponent, Fraction()) + ca * cb
    return clean(out)


def monomial(i: int, j: int, coefficient: Fraction | int = 1) -> Poly:
    exponent = [0] * N
    exponent[i] -= 1
    exponent[j] += 1
    return {tuple(exponent): Fraction(coefficient)}


def determinant3(matrix: list[list[Poly]]) -> Poly:
    out: Poly = {}
    for permutation in itertools.permutations(range(3)):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(3)
            for j in range(i + 1, 3)
        )
        term: Poly = {ZERO: Fraction((-1) ** inversions)}
        for row, column in enumerate(permutation):
            term = multiply(term, matrix[row][column])
        out = add(out, term)
    return out


def gram_determinant() -> Fraction:
    gram = [
        [Fraction(sum(BASIS[row][i] * BASIS[row][j] for row in range(N))) for j in range(3)]
        for i in range(3)
    ]
    return determinant_fraction(gram)


def determinant_fraction(matrix: list[list[Fraction]]) -> Fraction:
    work = [row[:] for row in matrix]
    determinant = Fraction(1)
    for column in range(len(work)):
        pivot = next((row for row in range(column, len(work)) if work[row][column]), None)
        if pivot is None:
            return Fraction()
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant *= -1
        value = work[column][column]
        determinant *= value
        for j in range(column, len(work)):
            work[column][j] /= value
        for row in range(column + 1, len(work)):
            value = work[row][column]
            if value:
                for j in range(column, len(work)):
                    work[row][j] -= value * work[column][j]
    return determinant


def residual_derivative() -> list[list[Poly]]:
    matrix = [[{} for _ in range(N)] for _ in range(N)]
    for i in range(N):
        for j in ((i - 1) % N, (i + 1) % N):
            edge = monomial(i, j)
            matrix[i][j] = add(matrix[i][j], edge)
            matrix[i][i] = add(matrix[i][i], scale(edge, -1))
    return matrix


def output_project(matrix: list[list[Poly]]) -> list[list[Poly]]:
    projected = [[{} for _ in range(N)] for _ in range(N)]
    for i in range(N):
        for j in range(N):
            column_mean: Poly = {}
            for row in range(N):
                column_mean = add(column_mean, scale(matrix[row][j], Fraction(1, N)))
            projected[i][j] = add(matrix[i][j], scale(column_mean, -1))
    return projected


def restrict(matrix: list[list[Poly]]) -> list[list[Poly]]:
    out = [[{} for _ in range(3)] for _ in range(N)]
    for i in range(N):
        for a in range(3):
            for j in range(N):
                out[i][a] = add(out[i][a], scale(matrix[i][j], BASIS[j][a]))
    return out


def jacobian_squared(projected: bool) -> Poly:
    matrix = residual_derivative()
    if projected:
        matrix = output_project(matrix)
    restricted = restrict(matrix)
    out: Poly = {}
    for rows in itertools.combinations(range(N), 3):
        minor = determinant3([[restricted[row][column] for column in range(3)] for row in rows])
        out = add(out, multiply(minor, minor))
    return scale(out, Fraction(1, gram_determinant()))


def canonical_hash(poly: Poly) -> str:
    rows = []
    for exponent in sorted(poly):
        coefficient = poly[exponent]
        rows.append(
            ",".join(str(value) for value in exponent)
            + f":{coefficient.numerator}/{coefficient.denominator}\n"
        )
    return hashlib.sha256("".join(rows).encode("ascii")).hexdigest()


def stats(poly: Poly) -> dict:
    positive = [value for value in poly.values() if value > 0]
    negative = [value for value in poly.values() if value < 0]
    barycenter = [
        sum((coefficient * exponent[i] for exponent, coefficient in poly.items()), Fraction())
        for i in range(N)
    ]
    return {
        "term_count": len(poly),
        "positive_term_count": len(positive),
        "negative_term_count": len(negative),
        "positive_coefficient_sum": enc(sum(positive, Fraction())),
        "negative_coefficient_sum": enc(sum(negative, Fraction())),
        "vacuum_value": enc(sum(poly.values(), Fraction())),
        "coefficient_weighted_exponent_sum": [enc(value) for value in barycenter],
        "canonical_polynomial_sha256": canonical_hash(poly),
    }


def logarithmic_hessian_at_vacuum(poly: Poly) -> list[list[Fraction]]:
    value = sum(poly.values(), Fraction())
    return [
        [
            sum(
                (coefficient * exponent[i] * exponent[j] for exponent, coefficient in poly.items()),
                Fraction(),
            )
            / (2 * value)
            for j in range(N)
        ]
        for i in range(N)
    ]


def fourier_eigenvalues(first_row: list[Fraction]) -> list[Fraction]:
    a, b, c, d, c2, b2 = first_row
    if b != b2 or c != c2:
        raise AssertionError("the Hessian is not cyclic-reflection invariant")
    return [
        a + 2 * b + 2 * c + d,
        a + b - c - d,
        a - b - c + d,
        a - 2 * b + 2 * c - d,
        a - b - c + d,
        a + b - c - d,
    ]


def logarithmic_hessian(poly: Poly, dyadic_exponents: tuple[int, ...]) -> list[list[Fraction]]:
    out = [[Fraction() for _ in range(N)] for _ in range(N)]
    for exponent, coefficient in poly.items():
        power = sum(exponent[i] * dyadic_exponents[i] for i in range(N))
        weight = coefficient * (Fraction(2**power) if power >= 0 else Fraction(1, 2 ** (-power)))
        for i in range(N):
            for j in range(N):
                out[i][j] += weight * exponent[i] * exponent[j]
    return out


def evaluate_dyadic(poly: Poly, point: tuple[int, ...]) -> Fraction:
    grouped: dict[int, Fraction] = {}
    for exponent, coefficient in poly.items():
        power = sum(exponent[i] * point[i] for i in range(N))
        grouped[power] = grouped.get(power, Fraction()) + coefficient
    return sum(
        (
            coefficient * (Fraction(2**power) if power >= 0 else Fraction(1, 2 ** (-power)))
            for power, coefficient in grouped.items()
        ),
        Fraction(),
    )


def dyadic_box_audit(poly: Poly, radius: int = 3) -> dict:
    minimum: Fraction | None = None
    minimizers: list[tuple[int, ...]] = []
    count = 0
    for first in itertools.product(range(-radius, radius + 1), repeat=N - 1):
        last = -sum(first)
        if not -radius <= last <= radius:
            continue
        point = first + (last,)
        value = evaluate_dyadic(poly, point)
        count += 1
        if minimum is None or value < minimum:
            minimum = value
            minimizers = [point]
        elif value == minimum:
            minimizers.append(point)
    assert minimum is not None
    return {
        "radius": radius,
        "point_count": count,
        "minimum": enc(minimum),
        "minimizers": [list(point) for point in minimizers],
        "status": "EXACT_FINITE_AUDIT_NOT_GLOBAL_PROOF",
    }


def build() -> dict:
    unprojected = jacobian_squared(projected=False)
    projected = jacobian_squared(projected=True)
    projected_stats = stats(projected)
    unprojected_stats = stats(unprojected)
    vacuum_hessian = logarithmic_hessian_at_vacuum(projected)
    vacuum_eigenvalues = fourier_eigenvalues(vacuum_hessian[0])
    nonconvex_point = (1, -1, 2, -2, -2, 2)
    nonconvex_hessian = logarithmic_hessian(projected, nonconvex_point)
    leading_minors = [
        determinant_fraction([row[:size] for row in nonconvex_hessian[:size]])
        for size in range(1, N + 1)
    ]
    box = dyadic_box_audit(projected)
    checks = {
        "basis_is_mean_and_complete_phase_orthogonal": all(
            sum(BASIS[row][column] for row in range(N)) == 0
            and sum((2, 1, -1, -2, -1, 1)[row] * BASIS[row][column] for row in range(N)) == 0
            and sum((0, 1, 1, 0, -1, -1)[row] * BASIS[row][column] for row in range(N)) == 0
            for column in range(3)
        ),
        "basis_gram_determinant_is_72": gram_determinant() == 72,
        "unprojected_polynomial_has_296_positive_terms": unprojected_stats["term_count"] == 296
        and unprojected_stats["negative_term_count"] == 0,
        "unprojected_vacuum_value_is_1296": unprojected_stats["vacuum_value"] == enc(1296),
        "projected_polynomial_has_1293_terms": projected_stats["term_count"] == 1293,
        "projected_sign_counts_are_951_and_342": projected_stats["positive_term_count"] == 951
        and projected_stats["negative_term_count"] == 342,
        "projected_coefficient_sums_are_1602_and_minus_306": projected_stats["positive_coefficient_sum"] == enc(1602)
        and projected_stats["negative_coefficient_sum"] == enc(-306),
        "projected_vacuum_value_is_1296": projected_stats["vacuum_value"] == enc(1296),
        "projected_exponent_barycenter_is_zero": all(
            value == enc(0) for value in projected_stats["coefficient_weighted_exponent_sum"]
        ),
        "vacuum_log_jacobian_hessian_first_row_is_exact": vacuum_hessian[0]
        == [Fraction(97, 72), Fraction(-35, 48), Fraction(23, 144), Fraction(-5, 24), Fraction(23, 144), Fraction(-35, 48)],
        "vacuum_log_jacobian_hessian_is_positive_mod_scale": vacuum_eigenvalues
        == [Fraction(0), Fraction(2, 3), Fraction(41, 24), Fraction(10, 3), Fraction(41, 24), Fraction(2, 3)],
        "projected_coefficientwise_amgm_route_fails": projected_stats["negative_term_count"] > 0,
        "squared_jacobian_log_field_convexity_fails_exactly": leading_minors[4] < 0,
        "dyadic_radius_three_audit_has_unique_vacuum_minimum": box["minimum"] == enc(1296)
        and box["minimizers"] == [[0, 0, 0, 0, 0, 0]],
        "global_projected_jacobian_minimum_remains_open": True,
        "interacting_h_minus_one_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_TRANSVERSE_RESIDUAL_JACOBIAN_GATE_V1",
        "schema_version": "reverse-physics-bt-euclidean-transverse-residual-jacobian-gate-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "TRANSVERSE_JACOBIAN_NATURAL_CONVEXITY_ROUTES_OBSTRUCTED",
        "result_kind": "exact centered-residual transverse-Jacobian proof-architecture audit on C6",
        "question": "Can the complete lowest-phase transverse residual Jacobian be bounded below by its vacuum value using coefficientwise AM-GM or translation averaging plus convexity?",
        "answer": "Not by either natural route. For the physical centered derivative P_H Dr on C6, the squared transverse Jacobian is an exact 1293-term Laurent polynomial with 951 positive and 342 negative coefficients, so the positive-coefficient AM-GM proof available before output projection does not survive centering. Its log-field Hessian is exactly indefinite at the dyadic profile (1,-1,2,-2,-2,2) log 2, so translation averaging plus convexity of the squared Jacobian also fails. The vacuum is nevertheless a strict local minimum modulo scale, and it is the unique minimum in the exact mean-zero dyadic box [-3,3]^6. A global lower bound or counterexample remains open.",
        "geometry": {
            "graph": "six-cycle C6",
            "mean_zero_space": "H={psi in R^6: sum psi_i=0}",
            "phase_plane": "span{(2,1,-1,-2,-1,1),(0,1,1,0,-1,-1)}",
            "transverse_basis_rows": [list(row) for row in BASIS],
            "basis_gram_determinant": enc(gram_determinant()),
            "residual": "r_i=Omega_(i-1)/Omega_i+Omega_(i+1)/Omega_i-2",
            "physical_derivative": "L_psi=P_H Dr(psi)",
            "squared_jacobian": "det(B^T L_psi^T L_psi B)/det(B^T B)",
            "vacuum_value": enc(1296),
        },
        "laurent_audit": {
            "unprojected_Dr": unprojected_stats,
            "centered_P_H_Dr": projected_stats,
            "unprojected_disposition": "ALL_COEFFICIENTS_POSITIVE_SO_WEIGHTED_AMGM_PROVES_ITS_VACUUM_MINIMUM",
            "centered_disposition": "NEGATIVE_COEFFICIENTS_OBSTRUCT_THAT_COEFFICIENTWISE_AMGM_PROOF",
        },
        "local_vacuum_result": {
            "log_jacobian_hessian_first_row": [enc(value) for value in vacuum_hessian[0]],
            "fourier_eigenvalues": [enc(value) for value in vacuum_eigenvalues],
            "status": "STRICT_LOCAL_MINIMUM_MODULO_CONSTANT_SCALE",
        },
        "exact_nonconvexity_witness": {
            "dyadic_log2_exponents": list(nonconvex_point),
            "squared_jacobian_log_field_hessian_leading_principal_minors": [enc(value) for value in leading_minors],
            "negative_order_five_minor": enc(leading_minors[4]),
            "conclusion": "the squared centered transverse Jacobian is not globally convex in log-field coordinates",
        },
        "finite_search": box,
        "method_disposition": {
            "unprojected_positive_laurent_amgm": "PROVED_BUT_NOT_THE_PHYSICAL_CENTERED_MAP",
            "centered_positive_laurent_amgm": "OBSTRUCTED",
            "centered_squared_jacobian_global_convexity": "OBSTRUCTED",
            "centered_vacuum_strict_local_minimum": "PROVED",
            "centered_dyadic_radius_three_vacuum_minimum": "EXACT_FINITE_AUDIT",
            "centered_global_vacuum_minimum": "OPEN",
            "normalized_lowest_mode_marginal": "OPEN_EVEN_IF_THE_JACOBIAN_MINIMUM_IS_LATER_PROVED",
            "interacting_uniform_h_minus_one": "OPEN",
        },
        "research_consequence": {
            "surviving_route": "derive a regrouped forest/effective-resistance inequality for the centered polynomial, or search for an exact positive-field counterexample outside the audited dyadic box",
            "normalization_boundary": "a pointwise transverse-Jacobian lower bound alone would control one coarea entropy factor, not the normalized level-set area or the annealed center moment",
            "why_complete_phase_matters": "the domain complement removes both members of the lowest translation-invariant real phase plane",
        },
        "missing_object_ledger": [
            "a proof or counterexample for the global centered transverse-Jacobian minimum on C6 and larger tori",
            "a theorem connecting any such Jacobian estimate to the normalized lowest-mode marginal",
            "the actual interacting volume-uniform H^-1 estimate or controlled divergence",
        ],
        "next_gate": "Use all-minors matrix-tree or effective-resistance identities to regroup the centered C6 polynomial into sign-definite forest blocks; fail that, conduct a rigorously bounded counterexample search. Do not treat the exact finite box as a global theorem.",
        "does_not_establish": [
            "a global centered transverse-Jacobian lower bound",
            "a normalized lowest-mode marginal bound",
            "an interacting H^-1 estimate or divergence",
            "a continuum Euclidean measure or continuum OS theorem",
            "Born probability, Krein reconstruction, or Lorentzian causal physics",
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "input_sha256": {relative: sha256(relative) for relative in INPUTS},
            "arithmetic": "exact fractions and integer Laurent exponents; the finite search evaluates powers of two exactly",
            "external_literature_context": "the all-minors matrix-tree theorem suggests a regrouping route but is not used as evidence for a theorem here",
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_transverse_residual_jacobian_gate.py --check",
            "ulimit -v 500000; mise x python@3.12 -- python3 reverse_physics/verify_bt_euclidean_transverse_residual_jacobian_gate.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_transverse_residual_jacobian_gate",
        ],
        "tier_receipt": {
            "tier_0": "Python compilation and certificate/schema JSON parsing passed under the 500 MB address-space cap; the planning import accepted 1,687 nodes with zero invalid items and zero malformed events in 6.58 s; the first Git status inherited the Python cap and failed on threaded lstat, then the Git-only scoped diff-check passed without that cap; exact staged-diff inspection is required immediately before commit",
            "tier_1": "producer drift check passed in 14.31 s at 21,600 KB peak RSS; independent SymPy verifier passed in 22.92 s at 81,308 KB after an initial 0.56 s non-import-guard self-match failure was corrected and not counted as a pass; seven unit/mutation tests passed in 15.17 s at 21,676 KB; the 2.98 s advisory Science Forge shadow wrapper exited zero but its bridge audit failed closed because the external bp2transformer Python lacks sympy, and its census reported drift at 1,844 versus 976 certificates",
            "tier_2": "not run because the imported content-addressed residual and full-phase certificates and their shared operators are unchanged; their hashes are checked independently",
            "tier_3": "not run because this is a proof-architecture checkpoint with no freeze, lifecycle promotion, release, or shared-core change",
        },
        "checks": {
            "ok": not failures,
            "passed": len(checks) - len(failures),
            "total": len(checks),
            "failures": failures,
            "details": checks,
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "verifier": VERIFY_REL,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.check:
        with open(CERT_PATH, encoding="utf-8") as handle:
            stored = json.load(handle)
        if result != stored:
            raise SystemExit("certificate drift")
        print(
            "[PASS] BT transverse residual-Jacobian producer "
            f"({result['checks']['passed']}/{result['checks']['total']})"
        )
        return 0
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
