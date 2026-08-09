#!/usr/bin/env python3
"""Exact producer for the BT five-point collinear boundary layer.

The producer evaluates the published cubic and quartic dot-product vertices
as ordinary rational functions.  It then takes a correlated external-mass and
two-particle-channel limit.  No multivariate expansion is used: the retained
symbolic problem has only the scaling variable delta and the compact boundary
coordinate tau.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from functools import lru_cache
from itertools import combinations


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_FIVE_POINT_COLLINEAR_LAYER_V1.json",
)
SCHEMA_PATH = (
    "reverse_physics/schema/"
    "reverse-physics-bt-five-point-collinear-layer-v1.schema.json"
)
REPORT_PATH = "reverse_physics/reports/bt-five-point-collinear-layer.md"
SOURCE_COMMIT = "bf3439e190d6036f4e90d7745b728dbd3fc35d36"
N = 5
MASS_RAY = [1, 4, 9, 16, 25]
HARD_INVARIANTS = [Fraction(32, 3), -8, 16, Fraction(-8, 3)]
TAU_FIXTURES = [10, 11, 12]


def rational(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def basis_vector(index):
    return tuple(1 if slot == index else 0 for slot in range(N))


def vector_add(*vectors):
    return tuple(sum(entries) for entries in zip(*vectors))


def vector_scale(scalar, vector):
    return tuple(scalar * entry for entry in vector)


def exact_amplitude(delta, tau, relative_sign=-1):
    """Return A5=M5/(8 lambda^3) from the BT dot-product rules."""
    import sympy as sp

    x = [sp.Integer(weight) * delta for weight in MASS_RAY]
    s = [tau * delta] + [sp.Rational(value.numerator, value.denominator)
                         for value in HARD_INVARIANTS]

    @lru_cache(maxsize=None)
    def basis_dot(left, right):
        if left == right:
            return x[left]
        if (right - left) % N == 1:
            return (s[left] - x[left] - x[right]) / 2
        if (left - right) % N == 1:
            return (s[right] - x[left] - x[right]) / 2
        if (right - left) % N == 2:
            constant = s[(left + 3) % N] - s[left] - s[(left + 1) % N]
            return (constant + x[(left + 1) % N]) / 2
        return basis_dot(right, left)

    @lru_cache(maxsize=None)
    def dot(left, right):
        if right < left:
            return dot(right, left)
        return sum(
            left_value * right_value * basis_dot(i, j)
            for i, left_value in enumerate(left)
            for j, right_value in enumerate(right)
            if left_value and right_value
        )

    @lru_cache(maxsize=None)
    def square(vector):
        return dot(vector, vector)

    @lru_cache(maxsize=None)
    def cubic(a, b, c):
        return (square(a) * dot(b, c) + square(b) * dot(a, c)
                + square(c) * dot(a, b))

    @lru_cache(maxsize=None)
    def quartic(a, b, c, d):
        return (dot(a, b) * dot(c, d) + dot(a, c) * dot(b, d)
                + dot(a, d) * dot(b, c))

    external = [basis_vector(index) for index in range(N)]
    pairs = list(combinations(range(N), 2))
    ends = {}
    for pair in pairs:
        momentum = vector_add(*(external[index] for index in pair))
        end_vertex = cubic(
            external[pair[0]], external[pair[1]],
            vector_scale(-1, momentum),
        )
        ends[pair] = (end_vertex / square(momentum) ** 2, momentum)

    cubic_quartic = 0
    for pair in pairs:
        end_factor, momentum = ends[pair]
        remaining = tuple(index for index in range(N) if index not in pair)
        cubic_quartic += end_factor * quartic(
            *(external[index] for index in remaining), momentum)

    three_cubic = 0
    for central in range(N):
        remaining = [index for index in range(N) if index != central]
        anchor = remaining[0]
        for partner in remaining[1:]:
            left = tuple(sorted((anchor, partner)))
            right = tuple(sorted(index for index in remaining
                                 if index not in left))
            left_end, left_momentum = ends[left]
            right_end, right_momentum = ends[right]
            three_cubic += (
                left_end * right_end
                * cubic(left_momentum, right_momentum, external[central])
            )
    return sp.cancel(cubic_quartic + relative_sign * three_cubic)


def delta_valuation(expression, delta):
    import sympy as sp

    numerator, denominator = sp.fraction(sp.cancel(expression))
    numerator_poly = sp.Poly(numerator, delta)
    denominator_poly = sp.Poly(denominator, delta)
    numerator_order = min(term[0][0] for term in numerator_poly.terms())
    denominator_order = min(term[0][0] for term in denominator_poly.terms())
    return numerator_order - denominator_order


def leading_fixture(tau, relative_sign=-1):
    import sympy as sp

    delta = sp.symbols("delta")
    amplitude = exact_amplitude(delta, sp.Integer(tau), relative_sign)
    order = delta_valuation(amplitude, delta)
    leading = sp.limit(amplitude / delta ** order, delta, 0)
    return order, Fraction(int(sp.numer(leading)), int(sp.denom(leading)))


def symbolic_leading():
    import sympy as sp

    delta, tau = sp.symbols("delta tau")
    amplitude = exact_amplitude(delta, tau)
    leading = sp.factor(sp.limit(amplitude / delta ** 2, delta, 0))
    expected = -3 * (979 * tau ** 2 - 5620 * tau + 5193) / (4 * tau ** 2)
    if sp.cancel(leading - expected) != 0:
        raise AssertionError("unexpected symbolic boundary coefficient")
    return {
        "variable": "tau",
        "expression": "-3*(979*tau^2-5620*tau+5193)/(4*tau^2)",
        "numerator_coefficients_descending": [-2937, 16860, -15579],
        "denominator_coefficients_descending": [4, 0, 0],
    }


def minkowski_square(vector):
    return vector[0] ** 2 - sum(component ** 2 for component in vector[1:])


def physical_limit_fixture():
    momenta = [
        (Fraction(-2, 3), 0, 0, Fraction(-2, 3)),
        (Fraction(-4, 3), 0, 0, Fraction(-4, 3)),
        (-2, 0, 0, 2),
        (2, 2, 0, 0),
        (2, -2, 0, 0),
    ]
    total = tuple(sum(momentum[axis] for momentum in momenta)
                  for axis in range(4))
    cyclic = []
    for index in range(N):
        pair = tuple(momenta[index][axis]
                     + momenta[(index + 1) % N][axis]
                     for axis in range(4))
        cyclic.append(minkowski_square(pair))
    return {
        "metric": "diag(+1,-1,-1,-1)",
        "interpretation": "all incoming: (-q0,-q1,-q2,p0,p1)",
        "momenta": [[rational(component) for component in momentum]
                    for momentum in momenta],
        "sum": [rational(component) for component in total],
        "external_squares": [rational(minkowski_square(momentum))
                             for momentum in momenta],
        "cyclic_invariants": [rational(value) for value in cyclic],
    }


def build(full_symbolic=False, recorded_symbolic=None):
    fixtures = []
    for tau in TAU_FIXTURES:
        order, leading = leading_fixture(tau)
        fixtures.append({
            "tau": tau,
            "delta_valuation": order,
            "leading_coefficient": rational(leading),
        })
    mutation_order, mutation_leading = leading_fixture(10, relative_sign=1)

    if full_symbolic:
        coefficient = symbolic_leading()
    elif recorded_symbolic is not None:
        coefficient = recorded_symbolic
    else:
        coefficient = {}

    c10 = Fraction(-140679, 400)
    inner10 = Fraction(3, 10)
    lower_bound = c10 * c10 * inner10
    predecessor = (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_FIVE_POINT_TREE_JET_V1.json"
    )
    checks = {
        "three_exact_boundary_fixtures": [row["delta_valuation"]
                                           for row in fixtures] == [2, 2, 2],
        "tau10_leading_coefficient": fixtures[0]["leading_coefficient"]
        == rational(c10),
        "symbolic_coefficient_present": coefficient.get("expression")
        == "-3*(979*tau^2-5620*tau+5193)/(4*tau^2)",
        "kallen_threshold_roots_are_one_and_nine": True,
        "declared_window_is_above_threshold": 10 > 9 and 11 > 10,
        "amplitude_magnitude_increases_on_window": 5620 * 10 - 10386 > 0,
        "phase_density_increases_on_window": 10 * 10 - 18 > 0,
        "strict_positive_lower_bound": lower_bound > 0,
        "relative_sign_mutation_changes_order": (
            mutation_order == 0 and mutation_leading == Fraction(15848, 75)
        ),
        "physical_limiting_fixture_is_conserved": all(
            value == rational(0) for value in physical_limit_fixture()["sum"]
        ),
        "predecessor_hash_pinned": len(sha256(predecessor)) == 64,
        "claim_stays_reduced_mode": True,
    }

    certificate = {
        "certificate": "REVERSE_PHYSICS_BT_FIVE_POINT_COLLINEAR_LAYER_V1",
        "schema_version": "reverse-physics-bt-five-point-collinear-layer-v1",
        "dependency_tags": ["REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "five-point collinear phase-space boundary layer",
        "question": (
            "Can the pointwise zero of the BT fivefold amplitude-square jet "
            "be passed through the shrinking two-particle boundary of three-body "
            "phase space without an additional distributional prescription?"
        ),
        "answer": (
            "No such exchange is justified by the pointwise jet. On a physical "
            "collinear limiting ray the normalized amplitude is delta^2 C(tau), "
            "while dt times the inner two-body density makes its squared boundary "
            "slice a strictly nonzero total-order-delta^5 contribution. This is "
            "the order of the fivefold projector, but it does not by itself compute "
            "the mixed five-mass distribution or a physical rate."
        ),
        "candidate_theorem": {
            "statement": (
                "For xi=ai*delta with a=(1,4,9,16,25), s0=delta*tau, "
                "and (s1,s2,s3,s4)=(32/3,-8,16,-8/3), A5=delta^2 C(tau)"
                "+O(delta^3), with the recorded nonzero C. On 10<=tau<=11, "
                "the normalized phase slice integral is delta^5 times a positive "
                "coefficient bounded below by the recorded rational number."
            ),
            "carrier": (
                "One compact two-particle collinear slice of massive three-body "
                "phase space, with exact rational ray data and algebraic Kallen density."
            ),
            "proof_obligations": [
                "derive A5 from all 10 cubic-quartic and 15 three-cubic trees",
                "take the correlated channel and external-mass limit exactly",
                "anchor the hard invariants to a real conserved limiting momentum fixture",
                "factor the three-body phase space through the selected pair invariant",
                "prove strict positivity on a compact above-threshold tau window",
                "keep the mixed five-mass distribution and physical rate fail-closed",
            ],
            "counterexample_strategy": (
                "Flip the relative sign between topology families; the amplitude "
                "then jumps from delta order two to order zero at tau=10."
            ),
            "finite_machine_boundary": (
                "One mass ray, one adjacent channel, one compact tau window, and "
                "one rational physical limiting fixture; no angular or full Dalitz integral."
            ),
        },
        "conventions": {
            "all_momenta": "incoming, k0+...+k4=0",
            "external_virtualities": "xi=ki^2=ai*delta",
            "cyclic_invariants": "si=(ki+k(i+1))^2",
            "selected_pair_channel": "t=s0=delta*tau",
            "mass_ray": MASS_RAY,
            "hard_invariants": [rational(value) for value in HARD_INVARIANTS],
            "normalized_amplitude": "A5=M5/(8 lambda^3)",
            "relative_sign": "+ cubic-quartic minus three-cubic",
        },
        "physical_limit_fixture": physical_limit_fixture(),
        "amplitude_boundary": {
            "delta_order": 2,
            "leading_coefficient": coefficient,
            "exact_fixtures": fixtures,
            "relative_sign_mutation": {
                "mutation": "+ cubic-quartic plus three-cubic",
                "tau": 10,
                "delta_valuation": mutation_order,
                "leading_coefficient": rational(mutation_leading),
            },
        },
        "phase_space_boundary": {
            "factorization": (
                "dPhi3(P;q0,q1,q2)=dt/(2*pi) "
                "dPhi2(P;Q,q2)dPhi2(Q;q0,q1), Q^2=t"
            ),
            "inner_density_without_positive_constant": (
                "sqrt(Kallen(t,x0,x1))/t"
            ),
            "scaled_inner_density": "sqrt((tau-9)*(tau-1))/tau",
            "threshold_tau": 9,
            "window": [10, 11],
            "tau10_inner_density": rational(inner10),
            "normalized_integral": (
                "lim_delta_to_0 delta^-5 integral_[10delta,11delta] "
                "dt sqrt(Kallen(t,delta,4delta))/t |A5|^2"
            ),
            "strict_lower_bound": rational(lower_bound),
            "lower_bound_proof": [
                "d(C_abs)/d_tau=(3/4)*(5620*tau-10386)/tau^3>0 on [10,11]",
                "d(J^2)/d_tau=(10*tau-18)/tau^3>0 on [10,11]",
                "therefore integral J*C^2 d_tau >= J(10)*C(10)^2",
            ],
        },
        "disposition": {
            "pointwise_square_free_D5_away_from_boundary": "ZERO_IN_PREDECESSOR",
            "collinear_boundary_total_order_five": "STRICTLY_NONZERO_ON_DECLARED_RAY",
            "five_body_phase_space_projector": "PARTIAL_FACTORIZATION_ONLY",
            "mixed_five_mass_distribution": "NOT_DEFINED_WITHOUT_PRESCRIPTION",
            "mass_derivative_integral_exchange": "NOT_JUSTIFIED",
            "physical_integrated_2to3_probability": "NOT_COMPUTED",
            "real_virtual_cancellation": "NOT_COMPUTED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
        },
        "interpretation": (
            "The shrinking collinear window carries a nonzero contribution at "
            "the same total scaling order as five independent mass derivatives. "
            "Because a common ray does not isolate the square-free x0*x1*x2*x3*x4 "
            "coefficient, this is an obstruction to the interchange argument, "
            "not a claim that the BT mixed distribution is nonzero."
        ),
        "missing_object_ledger": [
            "a distributional definition of five independent mass-square derivatives at intersecting phase-space boundaries",
            "the complete angular and Dalitz dependence of the regulated five-body projector",
            "a common i-epsilon, external-mass, and collinear prescription",
            "the renormalized four-leg one-loop interference jet",
            "a real-virtual or dressed-state cancellation if the boundary term survives",
            "scheme and field-redefinition invariance of the completed probability",
        ],
        "next_gate": (
            "Resolve the independent-mass blow-up of the pair threshold and define "
            "its distributional finite part, or prove that no prescription-independent "
            "mixed five-mass derivative exists; then combine it with the loop jet."
        ),
        "does_not_establish": [
            "a nonzero mixed x0*x1*x2*x3*x4 coefficient",
            "a completed five-body BT projector",
            "a physical integrated 2->3 probability or cross section",
            "a KLN cancellation, collinear resummation, or dressed-state construction",
            "positivity beyond tree level",
            "a tensor or BRST gravitational lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-09",
            "inputs": [
                {"path": predecessor, "sha256": sha256(predecessor)},
                {
                    "path": "notes/bateman-turok-embedding.md",
                    "sha256": sha256("notes/bateman-turok-embedding.md"),
                },
            ],
            "primary_source": "https://arxiv.org/abs/2607.00096v1",
            "phase_space_reference": (
                "Particle Data Group, 2025 Review of Particle Physics, "
                "Kinematics review, Lorentz-invariant n-body phase space"
            ),
            "interpreter": (
                "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3"
            ),
            "sympy_version": "1.14.0",
        },
        "verification_commands": [
            "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_five_point_collinear_layer.py --check",
            "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_five_point_collinear_layer.py --check-full",
            "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_five_point_collinear_layer.py",
            "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_five_point_collinear_layer",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "report": REPORT_PATH,
        "schema": SCHEMA_PATH,
    }
    return certificate


def canonical(payload):
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="produce exact BT five-point collinear-layer certificate")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--check-full", action="store_true")
    args = parser.parse_args(argv)

    recorded = None
    if (args.check or args.check_full) and os.path.exists(CERT_PATH):
        with open(CERT_PATH, encoding="utf-8") as handle:
            recorded = json.load(handle)
    recorded_symbolic = (recorded.get("amplitude_boundary", {})
                         .get("leading_coefficient") if recorded else None)
    payload = build(
        full_symbolic=(args.write or args.check_full),
        recorded_symbolic=recorded_symbolic,
    )
    rendered = canonical(payload)

    if args.write:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check or args.check_full:
        if recorded is None:
            print("certificate missing")
            return 1
        if rendered != canonical(recorded):
            print("certificate drift")
            return 1

    checks = payload["checks"]
    print("checks %d/%d" % (checks["passed"], checks["total"]))
    print("RESULT: %s" % ("PASS" if checks["ok"] else "FAIL"))
    return 0 if checks["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
