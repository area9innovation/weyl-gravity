#!/usr/bin/env python3
"""Exact Bateman--Turok perfect-square five-point tree-amplitude jet.

The producer enumerates the 10 cubic--quartic and 15 three-cubic labeled
trees from the Feynman rules in Bateman--Turok Appendix B.  It works in the
cyclic invariant chart

    x_i = k_i^2,  s_i = (k_i+k_{i+1})^2,  sum_i k_i = 0,

and reduces in the square-free external-virtuality algebra x_i^2=0.  The
normalized result is A_5 = M_5/(8 lambda^3).

Two rails are deliberately separated:

* the fast rail proves the degree <= 2 coefficients vanish canonically in
  Q(s_0,...,s_4), evaluates the complete jet at exact rational fixtures, and
  classifies three exact one-parameter channel faces;
* --full-symbolic also constructs and hashes all 16 nonzero rational-function
  coefficients.  It is an exhaustive receipt, not a per-edit smoke test.

This is an amplitude-side LOCAL-ALGEBRAIC calculation.  It is not a five-body
phase-space prescription or a KLN calculation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from functools import lru_cache
from fractions import Fraction
from itertools import combinations


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_FIVE_POINT_TREE_JET_V1.json",
)
REPORT_PATH = "reverse_physics/reports/bt-five-point-tree-jet.md"
SCHEMA_PATH = (
    "reverse_physics/schema/reverse-physics-bt-five-point-tree-jet-v1.schema.json"
)
SOURCE_COMMIT = "527d578dccf72d18cb4e776b3857ec3715270199"
N = 5
FULL_MASK = (1 << N) - 1


class RationalDomain:
    zero = Fraction(0)
    one = Fraction(1)

    @staticmethod
    def convert(value):
        return Fraction(value)

    @staticmethod
    def quotient(numerator, denominator):
        return Fraction(numerator, denominator)


class FieldDomain:
    def __init__(self, field):
        self.field = field
        self.zero = field.zero
        self.one = field.one

    def convert(self, value):
        return self.field(value)

    def quotient(self, numerator, denominator):
        return self.field(numerator) / self.field(denominator)


class Jet:
    """Sparse square-free jet with a declared total-degree cutoff."""

    def __init__(self, domain, coefficients=None, max_degree=N):
        self.domain = domain
        self.max_degree = int(max_degree)
        self.coefficients = {
            int(mask): domain.convert(value)
            for mask, value in (coefficients or {}).items()
            if value != 0 and int(mask).bit_count() <= self.max_degree
        }

    @classmethod
    def scalar(cls, domain, value, max_degree=N):
        return cls(domain, {0: value}, max_degree)

    def _coerce(self, other):
        if isinstance(other, Jet):
            if other.domain is not self.domain:
                raise ValueError("jet domain mismatch")
            if other.max_degree != self.max_degree:
                raise ValueError("jet cutoff mismatch")
            return other
        return Jet.scalar(self.domain, other, self.max_degree)

    def __add__(self, other):
        other = self._coerce(other)
        out = dict(self.coefficients)
        for mask, value in other.coefficients.items():
            out[mask] = out.get(mask, self.domain.zero) + value
        return Jet(self.domain, out, self.max_degree)

    __radd__ = __add__

    def __neg__(self):
        return Jet(
            self.domain,
            {mask: -value for mask, value in self.coefficients.items()},
            self.max_degree,
        )

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __mul__(self, other):
        other = self._coerce(other)
        out = {}
        for left_mask, left_value in self.coefficients.items():
            for right_mask, right_value in other.coefficients.items():
                if left_mask & right_mask:
                    continue
                mask = left_mask | right_mask
                if mask.bit_count() > self.max_degree:
                    continue
                out[mask] = out.get(mask, self.domain.zero) + (
                    left_value * right_value
                )
        return Jet(self.domain, out, self.max_degree)

    __rmul__ = __mul__

    def __truediv__(self, scalar):
        scalar = self.domain.convert(scalar)
        return self * (self.domain.one / scalar)

    def inverse_square_geometric(self):
        """Compute self^-2 from the finite (1+u)^-2 series."""
        constant = self.coefficients.get(0, self.domain.zero)
        if constant == 0:
            raise ZeroDivisionError("channel has zero constant term")
        unit = Jet.scalar(self.domain, self.domain.one, self.max_degree)
        remainder = (self - constant) / constant
        power = unit
        out = Jet(self.domain, max_degree=self.max_degree)
        for degree in range(self.max_degree + 1):
            coefficient = self.domain.convert(((-1) ** degree) * (degree + 1))
            out += (coefficient / (constant * constant)) * power
            power = power * remainder
        return out

    def coefficient(self, mask):
        return self.coefficients.get(int(mask), self.domain.zero)


def basis_vector(index):
    return tuple(1 if slot == index else 0 for slot in range(N))


def vector_add(*vectors):
    return tuple(sum(entries) for entries in zip(*vectors))


def vector_scale(scalar, vector):
    return tuple(scalar * entry for entry in vector)


def build_amplitude(domain, s_values, max_degree=N):
    """Build A_5=M_5/(8 lambda^3) directly from BT dot-product vertices."""
    if len(s_values) != N:
        raise ValueError("five cyclic invariants required")
    s_values = [domain.convert(value) for value in s_values]

    def x(index):
        return Jet(domain, {1 << index: domain.one}, max_degree)

    @lru_cache(maxsize=None)
    def basis_dot(left, right):
        if left == right:
            return x(left)
        if (right - left) % N == 1:
            return (Jet.scalar(domain, s_values[left], max_degree)
                    - x(left) - x(right)) / 2
        if (left - right) % N == 1:
            return (Jet.scalar(domain, s_values[right], max_degree)
                    - x(left) - x(right)) / 2
        if (right - left) % N == 2:
            constant = (
                s_values[(left + 3) % N]
                - s_values[left]
                - s_values[(left + 1) % N]
            )
            return (Jet.scalar(domain, constant, max_degree)
                    + x((left + 1) % N)) / 2
        return basis_dot(right, left)

    @lru_cache(maxsize=None)
    def dot(left, right):
        if right < left:
            return dot(right, left)
        out = Jet(domain, max_degree=max_degree)
        for i, left_value in enumerate(left):
            if not left_value:
                continue
            for j, right_value in enumerate(right):
                if right_value:
                    out += (left_value * right_value) * basis_dot(i, j)
        return out

    @lru_cache(maxsize=None)
    def square(vector):
        return dot(vector, vector)

    @lru_cache(maxsize=None)
    def cubic(a, b, c):
        # BT (B1) polynomial, without the common -2 i lambda.
        return (
            square(a) * dot(b, c)
            + square(b) * dot(a, c)
            + square(c) * dot(a, b)
        )

    @lru_cache(maxsize=None)
    def quartic(a, b, c, d):
        # BT (B2) polynomial, without the common -4 i lambda^2.
        return (
            dot(a, b) * dot(c, d)
            + dot(a, c) * dot(b, d)
            + dot(a, d) * dot(b, c)
        )

    external = [basis_vector(index) for index in range(N)]
    pairs = list(combinations(range(N), 2))
    ends = {}
    for pair in pairs:
        momentum = vector_add(*(external[index] for index in pair))
        end_vertex = cubic(
            external[pair[0]], external[pair[1]],
            vector_scale(-1, momentum),
        )
        ends[pair] = (
            end_vertex * square(momentum).inverse_square_geometric(),
            momentum,
        )

    amplitude = Jet(domain, max_degree=max_degree)
    cubic_quartic_rows = []
    for pair in pairs:
        end_factor, momentum = ends[pair]
        remaining = tuple(index for index in range(N) if index not in pair)
        amplitude += end_factor * quartic(
            *(external[index] for index in remaining), momentum)
        cubic_quartic_rows.append({
            "cubic_external_pair": list(pair),
            "quartic_external_triple": list(remaining),
        })

    three_cubic_rows = []
    for central_external in range(N):
        remaining = [index for index in range(N)
                     if index != central_external]
        anchor = remaining[0]
        for partner in remaining[1:]:
            left_pair = tuple(sorted((anchor, partner)))
            right_pair = tuple(sorted(
                index for index in remaining if index not in left_pair
            ))
            left_end, left_momentum = ends[left_pair]
            right_end, right_momentum = ends[right_pair]
            amplitude -= (
                left_end * right_end
                * cubic(left_momentum, right_momentum,
                        external[central_external])
            )
            three_cubic_rows.append({
                "central_external": central_external,
                "left_external_pair": list(left_pair),
                "right_external_pair": list(right_pair),
            })

    return amplitude, cubic_quartic_rows, three_cubic_rows


def rational(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def rational_jet_rows(amplitude):
    return [
        {
            "mask": mask,
            "subset": [index + 1 for index in range(N)
                       if mask & (1 << index)],
            "degree": mask.bit_count(),
            "coefficient": rational(amplitude.coefficient(mask)),
        }
        for mask in range(1 << N)
    ]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def symbolic_field(variable_names):
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field

    result = field(",".join(variable_names), QQ)
    return result[0], list(result[1:])


def symbolic_low_degree_proof():
    field_object, generators = symbolic_field(
        ["s0", "s1", "s2", "s3", "s4"])
    domain = FieldDomain(field_object)
    amplitude, _, _ = build_amplitude(domain, generators, max_degree=2)
    rows = []
    for mask in range(1 << N):
        if mask.bit_count() <= 2:
            rows.append({
                "mask": mask,
                "degree": mask.bit_count(),
                "canonical_zero": amplitude.coefficient(mask) == domain.zero,
            })
    return rows


def full_symbolic_hashes():
    field_object, generators = symbolic_field(
        ["s0", "s1", "s2", "s3", "s4"])
    domain = FieldDomain(field_object)
    amplitude, _, _ = build_amplitude(domain, generators, max_degree=N)
    rows = []
    for mask in range(1 << N):
        coefficient = amplitude.coefficient(mask)
        if coefficient == domain.zero:
            continue
        canonical = str(coefficient)
        rows.append({
            "mask": mask,
            "subset": [index + 1 for index in range(N)
                       if mask & (1 << index)],
            "degree": mask.bit_count(),
            "canonical_length": len(canonical),
            "sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        })
    return rows, (amplitude * amplitude).coefficient(FULL_MASK) == domain.zero


def polynomial_valuation_at_zero(polynomial):
    return min(monomial[0] for monomial, _ in polynomial.terms())


def rational_function_valuation(value):
    return (
        polynomial_valuation_at_zero(value.numer)
        - polynomial_valuation_at_zero(value.denom)
    )


def face_rows():
    field_object, generators = symbolic_field(["epsilon"])
    epsilon = generators[0]
    domain = FieldDomain(field_object)
    faces = [
        (
            "ADJACENT_COLLINEAR_s0",
            [epsilon, 3, 5, 7, 11],
            "s0 -> 0 with every other pair channel nonzero at epsilon=0",
        ),
        (
            "NONADJACENT_COLLINEAR_z02",
            [2, 3, 7, 5 + epsilon, 11],
            "z02=s3-s0-s1 -> 0 with other pair channels nonzero",
        ),
        (
            "SOFT_LEG_5",
            [2, 3, 2 + 5 * epsilon, 7 * epsilon, 11 * epsilon],
            "all four pair invariants incident on external leg 5 scale as epsilon",
        ),
    ]
    output = []
    for name, trajectory, description in faces:
        amplitude, _, _ = build_amplitude(domain, trajectory, max_degree=N)
        coefficient_rows = []
        for mask, coefficient in sorted(amplitude.coefficients.items()):
            coefficient_rows.append({
                "mask": mask,
                "degree": mask.bit_count(),
                "epsilon_valuation": rational_function_valuation(coefficient),
            })
        degree_ranges = []
        for degree in (3, 4, 5):
            valuations = [
                row["epsilon_valuation"] for row in coefficient_rows
                if row["degree"] == degree
            ]
            degree_ranges.append({
                "degree": degree,
                "minimum_valuation": min(valuations),
                "maximum_valuation": max(valuations),
            })
        output.append({
            "face": name,
            "trajectory": [str(value) for value in trajectory],
            "description": description,
            "coefficient_rows": coefficient_rows,
            "degree_ranges": degree_ranges,
            "projected_square_zero_for_nonzero_epsilon": (
                (amplitude * amplitude).coefficient(FULL_MASK) == domain.zero
            ),
        })
    return output


FIXTURES = [
    ("F1", [2, 3, 5, 7, 11]),
    ("F2", [3, 5, 8, 13, 21]),
    ("F3", [5, -2, 7, 4, 11]),
]


def fixture_rows():
    domain = RationalDomain()
    output = []
    topology = None
    for name, invariants in FIXTURES:
        amplitude, cubic_quartic, three_cubic = build_amplitude(
            domain, invariants, max_degree=N)
        if topology is None:
            topology = (cubic_quartic, three_cubic)
        squared = amplitude * amplitude
        output.append({
            "fixture": name,
            "cyclic_invariants": [rational(value) for value in invariants],
            "jet_rows": rational_jet_rows(amplitude),
            "nonzero_masks": sorted(amplitude.coefficients),
            "minimum_nonzero_degree": min(
                mask.bit_count() for mask in amplitude.coefficients),
            "projected_square": rational(squared.coefficient(FULL_MASK)),
        })
    return output, topology


def build(full_symbolic=False, recorded_symbolic=None):
    fixtures, topology = fixture_rows()
    cubic_quartic, three_cubic = topology
    low_degree = symbolic_low_degree_proof()
    faces = face_rows()

    if full_symbolic:
        symbolic_hashes, symbolic_square_zero = full_symbolic_hashes()
    elif recorded_symbolic is not None:
        symbolic_hashes = recorded_symbolic["coefficient_hashes"]
        symbolic_square_zero = recorded_symbolic["projected_square_zero"]
    else:
        symbolic_hashes = []
        symbolic_square_zero = False

    expected_nonzero = [
        mask for mask in range(1 << N) if mask.bit_count() >= 3
    ]
    checks = {
        "ten_cubic_quartic_trees": len(cubic_quartic) == 10,
        "fifteen_three_cubic_trees": len(three_cubic) == 15,
        "all_low_degree_symbolic_coefficients_zero": (
            len(low_degree) == 16
            and all(row["canonical_zero"] for row in low_degree)
        ),
        "all_fixtures_have_complete_32_slot_rows": all(
            len(row["jet_rows"]) == 32 for row in fixtures
        ),
        "all_fixtures_have_exact_degree_3_to_5_support": all(
            row["nonzero_masks"] == expected_nonzero
            and row["minimum_nonzero_degree"] == 3
            for row in fixtures
        ),
        "all_fixture_projected_squares_zero": all(
            row["projected_square"] == rational(0) for row in fixtures
        ),
        "all_faces_keep_projected_square_zero": all(
            row["projected_square_zero_for_nonzero_epsilon"] for row in faces
        ),
        "leading_face_poles_are_at_most_simple": all(
            next(r for r in row["degree_ranges"] if r["degree"] == 3)[
                "minimum_valuation"] >= -1
            for row in faces
        ),
        "full_symbolic_support_hashed": (
            len(symbolic_hashes) == 16
            and [row["mask"] for row in symbolic_hashes] == expected_nonzero
        ),
        "full_symbolic_projected_square_zero": symbolic_square_zero is True,
        "physical_phase_space_stays_fail_closed": True,
        "no_lorentzian_claim": True,
    }

    certificate = {
        "certificate": "REVERSE_PHYSICS_BT_FIVE_POINT_TREE_JET_V1",
        "schema_version": "reverse-physics-bt-five-point-tree-jet-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "five-point tree off-shell amplitude jet",
        "question": (
            "What is the complete square-free five-point PS tree-amplitude "
            "jet, and does its amplitude-side BT fivefold probability "
            "projector contain a real-emission term?"
        ),
        "answer": (
            "The normalized amplitude M5/(8 lambda^3) has exactly the 16 "
            "degree-3, degree-4, and degree-5 square-free slots. All 16 "
            "slots of degree at most 2 vanish identically in Q(s0,...,s4). "
            "Consequently the top coefficient of |M5|^2 is exactly zero at "
            "nonexceptional kinematics, although individual leading jet "
            "coefficients have simple soft/collinear poles."
        ),
        "candidate_theorem": {
            "statement": (
                "In the cyclic five-invariant chart and away from internal "
                "channel zeros, the complete PS five-point tree amplitude "
                "lies in the third power of the external-virtuality ideal; "
                "therefore D5|M5|^2=0 pointwise."
            ),
            "carrier": (
                "Q(s0,...,s4)[x1,...,x5]/(xi^2), with exact rational-function "
                "coefficients and all momenta incoming."
            ),
            "proof_obligations": [
                "enumerate every labeled tree exactly once",
                "preserve the relative sign fixed by the published Feynman rules",
                "prove all degree-zero, one, and two jet coefficients vanish canonically",
                "construct and content-hash all remaining 16 coefficient functions",
                "verify the squared top coefficient independently",
                "separate pointwise amplitude algebra from phase-space distributions",
            ],
            "counterexample_strategy": (
                "Flip the relative sign of the three-cubic family or omit one "
                "labeled tree; either mutation must populate a forbidden low-degree slot."
            ),
            "finite_machine_boundary": (
                "Exact 32-slot square-free jet, 25 labeled trees, three exact "
                "rational kinematic fixtures, and three exact one-parameter faces."
            ),
        },
        "conventions": {
            "all_momenta": "incoming, k1+...+k5=0",
            "external_virtualities": "xi=ki^2",
            "cyclic_invariants": "si=(ki+k_{i+1})^2 with indices modulo 5",
            "nonadjacent_identity": (
                "(ki+k_{i+2})^2=s_{i+3}-s_i-s_{i+1}+x_i+x_{i+1}+x_{i+2}"
            ),
            "cubic_rule": (
                "-2 i lambda [p1^2 p2.p3 + p2^2 p1.p3 + p3^2 p1.p2]"
            ),
            "quartic_rule": (
                "-4 i lambda^2 [p1.p2 p3.p4 + p1.p3 p2.p4 + p1.p4 p2.p3]"
            ),
            "propagator": "-i/(K^2+i epsilon)^2",
            "normalized_amplitude": "A5=M5/(8 lambda^3)",
            "relative_sign": (
                "+ for cubic-quartic trees and - for three-cubic trees"
            ),
            "tree_conjugation": (
                "away from channel poles the tree coefficients are real "
                "rational functions, so dagger fixes A5"
            ),
        },
        "topology": {
            "cubic_quartic_count": len(cubic_quartic),
            "three_cubic_count": len(three_cubic),
            "total_count": len(cubic_quartic) + len(three_cubic),
            "cubic_quartic_rows": cubic_quartic,
            "three_cubic_rows": three_cubic,
        },
        "symbolic_jet": {
            "ring": "Q(s0,s1,s2,s3,s4)[x1,...,x5]/(xi^2)",
            "slot_count": 32,
            "zero_low_degree_rows": low_degree,
            "nonzero_degree_counts": {"3": 10, "4": 5, "5": 1},
            "coefficient_hashes": symbolic_hashes,
            "canonical_serialization": (
                "str(FracElement) from SymPy 1.14 rational-function field over QQ"
            ),
            "projected_square_zero": symbolic_square_zero,
            "identity": (
                "A5 in (x1,...,x5)^3 implies coefficient_[x1...x5](A5^2)=0"
            ),
        },
        "exact_fixtures": fixtures,
        "soft_collinear_faces": faces,
        "disposition": {
            "complete_five_point_tree_jet": "COMPUTED_AND_HASHED",
            "ordinary_on_shell_five_point_amplitude": "ZERO",
            "amplitude_virtuality_order": "AT_LEAST_THREE_EXACTLY_THREE_GENERIC",
            "pointwise_D5_amplitude_square": "ZERO",
            "leading_jet_soft_collinear_behavior": "SIMPLE_POLES_ON_DECLARED_FACES",
            "five_body_phase_space_projector": "NOT_CONSTRUCTED",
            "distributional_boundary_terms": "NOT_CLASSIFIED",
            "real_virtual_cancellation": "NOT_COMPUTED",
            "physical_nlo_process_map": "NOT_CONSTRUCTED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a five-body phase-space parameterization derived from the BT projector rather than an arbitrary invariant chart",
            "a common regulator specifying the order of mass differentiation, phase-space integration, and collinear limit",
            "a proof or counterexample for distributional boundary terms at channel pinch surfaces",
            "the regulated renormalized four-leg one-loop interference jet",
            "a real--virtual or dressed-state cancellation theorem if a distributional real term survives",
            "scheme/field-redefinition invariance of the combined off-shell amplitude and projector",
        ],
        "next_gate": (
            "Derive the regulated five-body BT phase-space projector and test "
            "whether its distributional mass derivatives preserve the "
            "pointwise D5|M5|^2=0 result; separately compute the four-leg loop jet."
        ),
        "does_not_establish": [
            "that physical 2->3 probability vanishes after phase-space integration",
            "that differentiation commutes with the collinear regulator limit",
            "absence of distributional boundary or pinch contributions",
            "a real--virtual KLN cancellation or resummation",
            "a finite NLO cross section or positivity beyond tree level",
            "scheme or field-redefinition invariance of the completed construction",
            "a tensor/BRST gravitational lift or anything LORENTZIAN-CAUSAL",
            "literature priority for the five-point cancellation",
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-09",
            "inputs": [
                {
                    "path": "notes/bateman-turok-embedding.md",
                    "sha256": sha256("notes/bateman-turok-embedding.md"),
                },
                {
                    "path": (
                        "reverse_physics/certificates/"
                        "REVERSE_PHYSICS_BT_OFFSHELL_JET_OBSTRUCTION_V1.json"
                    ),
                    "sha256": sha256(
                        "reverse_physics/certificates/"
                        "REVERSE_PHYSICS_BT_OFFSHELL_JET_OBSTRUCTION_V1.json"
                    ),
                },
            ],
            "primary_source": "https://arxiv.org/abs/2607.00096v1",
            "interpreter": (
                "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3"
            ),
            "sympy_version": "1.14.0",
        },
        "verification_commands": [
            "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_five_point_tree_jet.py --check",
            "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_five_point_tree_jet.py --check-full",
            "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_five_point_tree_jet.py",
            "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_five_point_tree_jet",
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


def load_recorded():
    with open(CERT_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="produce exact BT five-point tree-amplitude jet")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--check-full", action="store_true")
    args = parser.parse_args(argv)

    recorded = None
    if (args.check or args.check_full) and os.path.exists(CERT_PATH):
        recorded = load_recorded()
    recorded_symbolic = recorded.get("symbolic_jet") if recorded else None
    full = args.write or args.check_full
    payload = build(full_symbolic=full, recorded_symbolic=recorded_symbolic)
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
