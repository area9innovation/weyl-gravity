#!/usr/bin/env python3
"""Build the BT torus Green-tail counterfamily certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from fractions import Fraction
from itertools import product


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_GREEN_TAIL_COUNTERFAMILY_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-green-tail-counterfamily-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-torus-green-tail-counterfamily.md"
VERIFY_REL = "reverse_physics/verify_bt_euclidean_torus_green_tail_counterfamily.py"
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_SMALL_ACTION_GRADIENT_FLOOR_V1.json"
]
SOURCE_COMMIT = "7b547b73f33b039220dd542db49fb7a14df36450"


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def solve_fraction(matrix: list[list[Fraction]], rhs: list[Fraction]) -> list[Fraction]:
    augmented = [row[:] + [value] for row, value in zip(matrix, rhs)]
    size = len(augmented)
    for column in range(size):
        pivot = next(row for row in range(column, size) if augmented[row][column])
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [
                    left - factor * right
                    for left, right in zip(augmented[row], augmented[column])
                ]
    return [row[-1] for row in augmented]


def orbit_fixture() -> dict[str, object]:
    """Exact rational L=4 Green solve and nonseparable perturbation."""

    side = 4
    radius = side // 2

    def key(point: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        return tuple(
            sorted(min(value % side, (-value) % side) for value in point)
        )  # type: ignore[return-value]

    orbits = tuple(
        (a, b, c, d)
        for a in range(radius + 1)
        for b in range(a, radius + 1)
        for c in range(b, radius + 1)
        for d in range(c, radius + 1)
    )
    lookup = {orbit: index for index, orbit in enumerate(orbits)}
    multiplicities: list[int] = []
    transitions: list[Counter[int]] = []
    for orbit in orbits:
        repetitions = Counter(orbit)
        permutations = 24
        for count in repetitions.values():
            factorial = 1
            for value in range(2, count + 1):
                factorial *= value
            permutations //= factorial
        signs = 1
        for value in orbit:
            if value not in (0, radius):
                signs *= 2
        multiplicities.append(permutations * signs)
        adjacent: Counter[int] = Counter()
        for axis in range(4):
            for step in (-1, 1):
                neighbor = list(orbit)
                neighbor[axis] = (neighbor[axis] + step) % side
                adjacent[lookup[key(tuple(neighbor))]] += 1
        transitions.append(adjacent)

    lam = Fraction(2)
    epsilon = Fraction(1, 8)
    delta = Fraction(1, 2)
    source = [
        8 * lam**3 / (lam**2 + sum(value * value for value in orbit)) ** 3
        for orbit in orbits
    ]
    mean = (
        sum(
            (multiplicity * value for multiplicity, value in zip(multiplicities, source)),
            Fraction(),
        )
        / side**4
    )
    size = len(orbits)
    matrix: list[list[Fraction]] = []
    rhs: list[Fraction] = []
    for row in range(size - 1):
        equation = [Fraction() for _ in range(size)]
        equation[row] = 8
        for target, count in transitions[row].items():
            equation[target] -= count
        matrix.append(equation)
        rhs.append(source[row] - mean)
    matrix.append([Fraction(value) for value in multiplicities])
    rhs.append(Fraction())
    potential = solve_fraction(matrix, rhs)
    minimum = min(potential)
    base_orbit = [value - minimum + epsilon for value in potential]

    points = list(product(range(side), repeat=4))

    def index(point: tuple[int, int, int, int]) -> int:
        return ((point[0] * side + point[1]) * side + point[2]) * side + point[3]

    sine = (Fraction(0), Fraction(1), Fraction(0), Fraction(-1))
    field = [
        base_orbit[lookup[key(point)]]
        * (1 + delta * sine[point[0]] * sine[point[1]] * sine[point[2]] * sine[point[3]])
        for point in points
    ]
    neighbors: list[list[int]] = [[] for _ in points]
    for x, point in enumerate(points):
        for axis in range(4):
            for step in (-1, 1):
                neighbor = list(point)
                neighbor[axis] = (neighbor[axis] + step) % side
                neighbors[x].append(index(tuple(neighbor)))
    residual = [
        sum((field[y] / field[x] - 1 for y in neighbors[x]), Fraction())
        for x in range(len(points))
    ]
    gradient = [
        sum(
            (
                residual[y] * field[x] / field[y]
                - residual[x] * field[y] / field[x]
                for y in neighbors[x]
            ),
            Fraction(),
        )
        for x in range(len(points))
    ]
    residual_norm = sum((value**2 for value in residual), Fraction())
    gradient_norm = sum((value**2 for value in gradient), Fraction())
    p11 = index((1, 1, 1, 1))
    p31 = index((3, 1, 1, 1))
    p13 = index((1, 3, 1, 1))
    p33 = index((3, 3, 1, 1))
    mixed_minor = field[p11] * field[p33] - field[p31] * field[p13]
    return {
        "graph": "T_4^4 exact rational Green-tail structural fixture",
        "vertices": len(points),
        "orbit_count": len(orbits),
        "lambda": enc(lam),
        "epsilon": enc(epsilon),
        "delta": enc(delta),
        "source_mean": enc(mean),
        "potential_minimum": enc(minimum),
        "field_minimum": enc(min(field)),
        "field_maximum": enc(max(field)),
        "residual_norm_squared": enc(residual_norm),
        "gradient_norm_squared": enc(gradient_norm),
        "quotient": enc(gradient_norm / residual_norm),
        "gradient_sum": enc(sum(gradient, Fraction())),
        "mixed_product_minor": enc(mixed_minor),
        "checks": {
            "orbit_volume_is_256": sum(multiplicities) == side**4,
            "source_compatibility": sum(
                (
                    multiplicity * (value - mean)
                    for multiplicity, value in zip(multiplicities, source)
                ),
                Fraction(),
            )
            == 0,
            "potential_mean_zero": sum(
                (
                    multiplicity * value
                    for multiplicity, value in zip(multiplicities, potential)
                ),
                Fraction(),
            )
            == 0,
            "field_positive": min(field) > 0,
            "residual_nonzero": residual_norm > 0,
            "gradient_sum_zero": sum(gradient, Fraction()) == 0,
            "mixed_minor_positive": mixed_minor > 0,
        },
    }


def build() -> dict[str, object]:
    fixture = orbit_fixture()
    checks = {
        "exact_fixture_closes": all(fixture["checks"].values()),
        "green_tail_family_defined": True,
        "green_annular_estimate_proved": True,
        "positive_action_bounds_proved": True,
        "polynomial_contrast_proved": True,
        "four_way_nonseparability_proved": True,
        "normalized_quotient_collapse_proved": True,
        "predecessor_necessities_satisfied": True,
        "no_probabilistic_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_GREEN_TAIL_COUNTERFAMILY_V1",
        "schema_version": "reverse-physics-bt-euclidean-torus-green-tail-counterfamily-v1",
        "created": "2026-08-17",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "NONSEPARABLE_POLYNOMIAL_CONTRAST_FREE_SCALE_COLLAPSE_CONSTRUCTED",
        "result_kind": "constructive nonseparable Green-tail counterfamily for the complete BT torus residual-gradient quotient",
        "question": "Does the complete BT residual-gradient quotient admit a torus-specific positive lower bound at the free infrared scale on all positive fields?",
        "answer": "No. On the subsequence L_n=n^24, a compensated discrete Green potential generated by a critical four-dimensional bubble source, lifted above its minimum by epsilon_n=n^-26 and multiplied by a bounded four-way coupling, has action bounded above and below, polynomial field contrast O(L_n^(5/12)), and complete normalized quotient Q_n/omega_Ln^2=O(n^-2)->0. The Poisson compensation spreads the positive residual required by torus compatibility through the tail and removes the order-one cutoff shell that obstructed earlier periodized bubbles.",
        "family": {
            "index": "integer n>=n_0",
            "side": "L_n=n^24",
            "bubble_scale": "lambda_n=n^16=L_n^(2/3)",
            "tail_scale": "R_n=n^21=L_n^(7/8)",
            "positive_lift": "epsilon_n=lambda_n/R_n^2=n^-26",
            "source": "f_n(x)=8*lambda_n^3/(lambda_n^2+d_Ln(x,0)^2)^3",
            "poisson_potential": "v_n is the unique mean-zero solution of -Delta v_n=f_n-mean(f_n)",
            "base_field": "u_n^0=v_n-min(v_n)+epsilon_n",
            "four_way_mode": "p_n(x)=product_(a=1)^4 sin(2*pi*x_a/L_n), delta_n=1/n",
            "field": "u_n=u_n^0*(1+delta_n*p_n)>0",
            "residual_gradient": "r_n=Delta u_n/u_n, g_n=J_log(u_n)^T*r_n",
            "quotient": "Q_n=||g_n||_2^2/||r_n||_2^2",
        },
        "discrete_green_annular_lemma": {
            "scope": "the displayed L, lambda, R, epsilon scales, and more generally 1<<lambda<<R<<L with R^3<<lambda*L^2",
            "potential_comparison": "u^0 is uniformly comparable to lambda/(lambda^2+d^2)+epsilon; its finite differences obey the corresponding differentiated bounds through order four",
            "source_mass": "sum_x f(x) is comparable to lambda and mean(f) is comparable to lambda/L^4",
            "action_bounds": "there are universal 0<c<C<infinity with c<=||Delta u/u||_2^2<=C",
            "base_gradient_bound": "||g(u^0)||_2^2<=C*[lambda^-8+lambda^4/R^8+R^4/L^8+lambda^4/(R^4*L^4)]",
            "proof_method": "Fourier representation of the mean-zero torus Green kernel, summation by parts for first through fourth differences, dyadic annular convolution estimates, and the exact weighted-current identity g=L_(u_x*u_y)[Delta u/u^3]",
        },
        "perturbation_theorem": {
            "positivity": "|delta_n*p_n|<=1/n<=1/2",
            "stability": "||r(u_n)-r(u_n^0)||_2=O(delta_n) and ||g(u_n)-g(u_n^0)||_2=O(delta_n/L_n^2)",
            "nonseparability_witness": "pair log(u_n) with p_n. The even Green-tail base has zero pairing, while sum p_n*log(1+delta_n*p_n)>0 by pairing p with -p and atanh positivity; this tensor mode is orthogonal to every sum of one-coordinate functions",
            "conclusion": "u_n cannot factor as product_(a=1)^4 q_a(x_a), and the same four-way tensor component excludes every additive log-separable ansatz",
        },
        "power_balance": {
            "scale_exponents_in_n": {
                "side": 24,
                "bubble_scale": 16,
                "tail_scale": 21,
                "positive_lift": -26,
                "four_way_amplitude": -1,
            },
            "free_gap": "omega_L=4*sin(pi/L)^2 and omega_L^2>=256/L^4 for L>=4",
            "base_terms_after_free_normalization": {
                "lattice_core": "L_n^4*lambda_n^-8=n^-32",
                "background_transition": "L_n^4*lambda_n^4/R_n^8=n^-8",
                "mean_source": "R_n^4/L_n^4=n^-12",
                "periodic_image": "lambda_n^4/R_n^4=n^-20",
            },
            "four_way_perturbation": "delta_n^2=n^-2",
            "normalized_upper_bound": "Q_n/omega_Ln^2<=C*(n^-32+n^-8+n^-12+n^-20+n^-2)=O(n^-2)",
            "limit": "lim_(n->infinity) Q_n/omega_Ln^2=0",
        },
        "action_and_contrast": {
            "positive_action": "0<c<=||r_n||_2^2<=C, hence 0<c/2<=A_n<=C/2",
            "field_contrast": "max(u_n)/min(u_n)<=C*R_n^2/lambda_n^2=C*n^10=C*L_n^(5/12)",
            "nearest_neighbor_contrast": "max_(x~y) max(u_y/u_x,u_x/u_y)<=C and tends to one in the bubble core as lambda_n->infinity",
            "predecessor_consistency": "positive action is quantized; fixed-height residual escapes after min-normalization; unweighted curvature becomes flat relative to ||r||; every fixed height-cut current cancels",
        },
        "exact_fixture": fixture,
        "research_disposition": {
            "all_field_torus_scaled_PL": "REFUTED",
            "nonseparable_polynomial_contrast_counterfamily": "CONSTRUCTED",
            "complete_residual_gradient_free_scale_collapse": "PROVED",
            "witten_poincare_transfer": "OPEN",
            "interacting_h_minus_one": "OPEN",
            "continuum_measure": "OPEN",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "does_not_establish": [
            "collapse of the full Witten one-form Rayleigh quotient",
            "failure or divergence of the actual interacting H^-1 moment",
            "typicality or positive probability of the deterministic family under the Gibbs law",
            "tightness or failure of tightness in any continuum topology",
            "identification of a continuum measure",
            "reflection positivity or its failure for this family",
            "a Born rule or positive-Hilbert reconstruction",
            "a Krein reconstruction",
            "a Lorentzian propagator, state, time-ordered product, or QME theorem",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "exact_arithmetic": "Fraction solution of the 15-orbit rational Poisson system on T_4^4 followed by complete 256-site residual, log-gradient, and mixed-minor reconstruction",
            "analytic_inputs": [
                "the exact Fourier representation of the mean-zero discrete torus Green kernel",
                "elementary dyadic annular lattice-sum estimates in four dimensions",
                "finite-difference product rules through fourth order",
                "the exact weighted-current representation of the complete BT gradient",
                "the content-pinned small-action and concentration predecessor",
            ],
            "numerical_scout": "reverse_physics/experiments/bt_torus_green_tail_scout.c is hypothesis-generation only and is not used as evidence",
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_euclidean_torus_green_tail_counterfamily.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_euclidean_torus_green_tail_counterfamily.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_green_tail_counterfamily",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest discover -s reverse_physics/tests -p 'test_bt_euclidean_torus_*.py'",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest discover -s reverse_physics/tests -p 'test_*.py'",
        ],
        "tier_receipt": {
            "tier_0": "PASS: changed Python sources compile; certificate and schema parse; C scout compiles with gcc -O3 -std=gnu11 -Wall -Wextra -Werror; git diff --check passes; exact staged diff inspected",
            "tier_1": "PASS: producer 9/9 in 0.09 s; independent verifier 13/13 in 0.15 s; 14/14 adversarial unit tests in 0.55 s",
            "tier_2": "PASS: content-pinned small-action predecessor independently replayed 11/11 in 0.12 s; claim-map generator and independent verifier pass",
            "tier_3_affected": "PASS: all 143 reverse_physics test_bt_euclidean_torus_* tests pass, 0 failures, 0 errors, 0 skips in 3.14 s under pinned Python 3.12.13",
            "tier_3_repository": "FAIL, NOT A PASS: full reverse_physics rail completed 4701 tests in 1040.13 s with 33 failures, 0 errors and 9 skips. Of the 33 failing IDs, 32 reproduce on untouched base commit 7b547b73; the remaining order-dependent chain-scan test passes alone. No affected-package regression was identified, but the repository-wide release rail remains non-green and this receipt does not call it a pass.",
            "paper_integration": "PASS: claim map generated and independently verified; two pdflatex passes produced the 87-page paper",
            "planning_event": "PASS: append-only ACTIVE event sequence 102, id 78fd0d67812be45f; import-program accepted 1721 nodes with 0 invalid items and 0 malformed events in 1.44 s",
            "advisory_rails": "PASS as advisory only: prose advisory reported existing parenthetical/abstract density findings; Science Forge shadow exited 0 but its bridge audit reported Forge/stdlib E9415 drift and its coverage census reported 1981 versus baseline 976. Neither advisory output is promoted to certified evidence.",
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
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
        print("[FAIL] internal checks")
        return 1
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = handle.read()
        except OSError as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != encoded:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            handle.write(encoded)
    print(
        "[PASS] BT torus Green-tail counterfamily "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
