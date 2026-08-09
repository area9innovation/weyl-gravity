#!/usr/bin/env python3
"""Exact charge-algebra preflight for BT inclusive radical closure.

Bateman--Turok Eq. (20) uses the off-diagonal one-particle completeness
kernel W^{Omega Upsilon}=W^{Upsilon Omega}, with diagonal entries zero.  This
producer asks the finite algebraic question that can be answered before any
collinear integral exists: do tensor powers and finite sums of that kernel
preserve the strictly-negative relative trace radical inside BT's one-sided
nonpositive image?

The carrier is the finite Laurent group algebra Q[t,t^-1].  Charge is the
power of t, the BT/Krein adjoint preserves charge, multiplication adds charge,
and the invariant trace extracts charge zero.  This is a charge carrier, not a
Fock-space, loop-amplitude, phase-space, or Lorentzian construction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_INCLUSIVE_RADICAL_CLOSURE_V1.json",
)
REPORT_PATH = "reverse_physics/reports/bt-inclusive-radical-closure.md"
SCHEMA_PATH = (
    "reverse_physics/schema/"
    "reverse-physics-bt-inclusive-radical-closure-v1.schema.json"
)
SOURCE_COMMIT = "f60ac01be1f92b8c3c45c2eaafeff91b34b05e52"


class Series:
    """Finite exact Laurent series with rational coefficients."""

    def __init__(self, terms=None):
        clean = {}
        for charge, coefficient in (terms or {}).items():
            coefficient = Fraction(coefficient)
            charge = int(charge)
            if coefficient:
                clean[charge] = clean.get(charge, Fraction(0)) + coefficient
        self.terms = {q: c for q, c in clean.items() if c}

    @classmethod
    def monomial(cls, charge, coefficient=1):
        return cls({int(charge): Fraction(coefficient)})

    def __add__(self, other):
        if not isinstance(other, Series):
            other = Series.monomial(0, other)
        out = dict(self.terms)
        for charge, coefficient in other.terms.items():
            out[charge] = out.get(charge, Fraction(0)) + coefficient
        return Series(out)

    __radd__ = __add__

    def __neg__(self):
        return Series({q: -c for q, c in self.terms.items()})

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        if not isinstance(other, Series):
            other = Series.monomial(0, other)
        out = {}
        for q1, c1 in self.terms.items():
            for q2, c2 in other.terms.items():
                out[q1 + q2] = out.get(q1 + q2, Fraction(0)) + c1 * c2
        return Series(out)

    __rmul__ = __mul__

    def dagger(self, preserves_charge=True):
        if preserves_charge:
            return Series(self.terms)
        return Series({-q: c for q, c in self.terms.items()})

    def trace(self):
        return self.terms.get(0, Fraction(0))

    def support(self):
        return sorted(self.terms)

    def strictly_negative(self):
        # The negative-charge direct sum is a vector subspace and contains 0.
        # Non-vacuity is checked separately where a populated witness matters.
        return all(q < 0 for q in self.terms)

    def serialized(self):
        return [
            {
                "charge": charge,
                "coefficient": {
                    "numerator": coefficient.numerator,
                    "denominator": coefficient.denominator,
                },
            }
            for charge, coefficient in sorted(self.terms.items())
        ]

    def __eq__(self, other):
        return isinstance(other, Series) and self.terms == other.terms


def kernel_term(left_charge, right_charge, coefficient=1):
    return {
        "left_charge": int(left_charge),
        "right_charge": int(right_charge),
        "coefficient": Fraction(coefficient),
    }


def sandwich(value, left_charge, right_charge, preserves_charge=True):
    left = Series.monomial(left_charge).dagger(preserves_charge)
    right = Series.monomial(right_charge)
    return left * value * right


def apply_kernel(value, terms, preserves_charge=True):
    out = Series()
    for term in terms:
        out += term["coefficient"] * sandwich(
            value,
            term["left_charge"],
            term["right_charge"],
            preserves_charge,
        )
    return out


def tensor_power_kernel(base_terms, power):
    """Expand a tensor-power completeness kernel into effective charge pairs."""
    terms = [kernel_term(0, 0)]
    for _ in range(int(power)):
        next_terms = []
        for old in terms:
            for new in base_terms:
                next_terms.append(kernel_term(
                    old["left_charge"] + new["left_charge"],
                    old["right_charge"] + new["right_charge"],
                    old["coefficient"] * new["coefficient"],
                ))
        terms = next_terms
    return terms


def inclusive_sum(value, base_terms, weights, preserves_charge=True):
    out = Series()
    for multiplicity, weight in enumerate(weights):
        out += Fraction(weight) * apply_kernel(
            value, tensor_power_kernel(base_terms, multiplicity),
            preserves_charge,
        )
    return out


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def serialize_kernel(terms):
    return [
        {
            "left_charge": term["left_charge"],
            "right_charge": term["right_charge"],
            "total_shift": term["left_charge"] + term["right_charge"],
            "coefficient": {
                "numerator": term["coefficient"].numerator,
                "denominator": term["coefficient"].denominator,
            },
        }
        for term in terms
    ]


def build():
    # BT Eq. (20): only Omega-Upsilon and Upsilon-Omega entries survive.
    offdiagonal = [kernel_term(+1, -1), kernel_term(-1, +1)]
    positive_diagonal = [kernel_term(+1, +1)]
    negative_diagonal = [kernel_term(-1, -1)]

    b = Series.monomial(0, Fraction(3, 5))
    c = Series({-1: Fraction(2, 7), -2: Fraction(-5, 11),
                -3: Fraction(7, 13)})
    a = b + c

    bt_product = a.dagger(preserves_charge=True) * a
    hilbert_product = a.dagger(preserves_charge=False) * a
    bc = b.dagger() * c
    cb = c.dagger() * b
    cc = c.dagger() * c

    multiplicity_rows = []
    tensor_powers_preserve = True
    for multiplicity in range(6):
        terms = tensor_power_kernel(offdiagonal, multiplicity)
        image = apply_kernel(c, terms)
        expected = Fraction(2**multiplicity) * c
        shifts = sorted({
            term["left_charge"] + term["right_charge"] for term in terms
        })
        ok = image == expected and image.strictly_negative() and shifts == [0]
        tensor_powers_preserve = tensor_powers_preserve and ok
        multiplicity_rows.append({
            "unresolved_multiplicity": multiplicity,
            "expanded_kernel_terms": len(terms),
            "total_shifts": shifts,
            "image_support": image.support(),
            "image_scale": 2**multiplicity,
            "closure": ok,
        })

    # Arbitrary nonzero rational weights are a non-vacuity fixture only.  The
    # theorem is coefficient-independent because it is a support statement.
    weights = [Fraction(1), Fraction(-2, 3), Fraction(5, 7),
               Fraction(-11, 13), Fraction(17, 19), Fraction(-23, 29)]
    inclusive_image = inclusive_sum(c, offdiagonal, weights)
    inclusive_scale = sum(weight * 2**n for n, weight in enumerate(weights))

    positive_witness_input = Series.monomial(-2)
    positive_witness_output = apply_kernel(
        positive_witness_input, positive_diagonal)
    negative_control_output = apply_kernel(
        Series.monomial(-1), negative_diagonal)

    # Exhaust the bounded mutation carrier.  For every input charge -1..-6,
    # a sandwich shift <=0 preserves negativity.  Every positive shift has an
    # explicit input t^{-shift} that reaches trace-visible charge zero.
    criterion_rows = []
    criterion_exact = True
    for left_charge in range(-3, 4):
        for right_charge in range(-3, 4):
            shift = left_charge + right_charge
            closes_all = all(
                sandwich(Series.monomial(q), left_charge, right_charge)
                .strictly_negative()
                for q in range(-6, 0)
            )
            expected = shift <= 0
            witness_charge = -shift if shift > 0 else None
            if shift > 0:
                witness_trace = sandwich(
                    Series.monomial(witness_charge), left_charge, right_charge
                ).trace()
            else:
                witness_trace = Fraction(0)
            row_ok = closes_all == expected and (
                shift <= 0 or witness_trace != 0
            )
            criterion_exact = criterion_exact and row_ok
            criterion_rows.append({
                "left_charge": left_charge,
                "right_charge": right_charge,
                "total_shift": shift,
                "closes_negative_carrier": closes_all,
                "counterexample_input_charge": witness_charge,
                "counterexample_trace": {
                    "numerator": witness_trace.numerator,
                    "denominator": witness_trace.denominator,
                },
            })

    kernel_classification = [
        {
            "entry": "W^{Omega Upsilon}", "charges": [+1, -1],
            "total_shift": 0, "radical_closure": True,
            "physical_status": "present in BT Eq. (20)",
        },
        {
            "entry": "W^{Upsilon Omega}", "charges": [-1, +1],
            "total_shift": 0, "radical_closure": True,
            "physical_status": "present in BT Eq. (20)",
        },
        {
            "entry": "W^{Omega Omega}", "charges": [+1, +1],
            "total_shift": 2, "radical_closure": False,
            "physical_status": "zero in BT Eq. (20); decisive mutation",
        },
        {
            "entry": "W^{Upsilon Upsilon}", "charges": [-1, -1],
            "total_shift": -2, "radical_closure": True,
            "physical_status": "zero in BT Eq. (20); closure alone does not exclude it",
        },
    ]

    checks = {
        "BT_adjoint_preserves_negative_charge": c.dagger().support() == c.support(),
        "strictly_negative_terms_are_trace_null": c.trace() == 0,
        "negative_sector_is_not_a_global_radical": (
            (Series.monomial(-1).dagger() * Series.monomial(+1)).trace() == 1
        ),
        "weak_ghost_cross_terms_are_trace_null": (
            bc.trace() == 0 and cb.trace() == 0 and cc.trace() == 0
        ),
        "BT_Born_trace_discards_C_exactly": bt_product.trace() == b.terms[0] ** 2,
        "Hilbert_adjoint_control_makes_C_visible": (
            hilbert_product.trace() != bt_product.trace()
        ),
        "Eq20_offdiagonal_terms_have_zero_total_shift": all(
            term["left_charge"] + term["right_charge"] == 0
            for term in offdiagonal
        ),
        "tensor_powers_through_five_unresolved_states_close":
            tensor_powers_preserve,
        "finite_weighted_inclusive_sum_closes": (
            inclusive_image == inclusive_scale * c
            and inclusive_image.strictly_negative()
        ),
        "positive_diagonal_mutation_reaches_trace": (
            positive_witness_output.trace() == 1
        ),
        "negative_diagonal_independence_control_still_closes":
            negative_control_output.strictly_negative(),
        "bounded_kernel_criterion_is_shift_nonpositive_iff_closure":
            criterion_exact,
        "closure_test_is_nonvacuous": inclusive_scale != 0 and bool(c.terms),
    }
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "certificate": "REVERSE_PHYSICS_BT_INCLUSIVE_RADICAL_CLOSURE_V1",
        "schema_version": "reverse-physics-bt-inclusive-radical-closure-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "finite charge-completeness radical-closure theorem",
        "question": "Do finite unresolved-state sums generated by the Bateman-Turok Eq. (20) off-diagonal completeness kernel preserve the strictly-negative relative trace radical inside the one-sided nonpositive image?",
        "answer": "Yes, conditionally on that inclusive map being defined and remaining one-sided. The BT/Krein adjoint preserves charge, multiplication adds charge, and each nonzero Eq. (20) completeness entry has total charge shift zero. Every tensor power and finite weighted sum therefore maps strictly negative charge back to strictly negative charge, so B^dag C, C^dag B, and C^dag C remain trace-null within the nonpositive image. The negative sector is not a radical globally: t^-1 pairs with t^+1 to give trace one. The exact closure criterion is that every contributing total charge shift be nonpositive. A positive diagonal Omega-Omega mutation supplies the sharp counterexample t^-2 -> 1 with nonzero trace.",
        "candidate_theorem": {
            "statement": "In the one-sided nonpositive part of a charge-graded algebra whose BT/Krein adjoint preserves charge and whose invariant trace vanishes off charge zero, every finite coarse-graining generated by kernel sandwiches of nonpositive total charge shift preserves the strictly-negative relative trace radical. For the BT Eq. (20) off-diagonal kernel all shifts are zero, including every tensor power.",
            "carrier": "finite Laurent group algebra Q[t,t^-1], populated B and C fixtures in charges {0} and {-1,-2,-3}, Eq. (20) kernel charges, unresolved multiplicities 0..5, and exhaustive kernel mutations (q_L,q_R) in [-3,3]^2",
            "proof_obligations": [
                "verify that the BT/Krein adjoint preserves rather than reverses boost charge",
                "derive the charge shift q -> q+q_L+q_R of every kernel sandwich",
                "prove all tensor powers of the off-diagonal Eq. (20) kernel have zero total shift",
                "prove B^dag C, C^dag B, and C^dag C stay away from charge zero",
                "supply a trace-visible counterexample for every positive total shift",
            ],
            "counterexample_strategy": "Turn on W^{Omega Omega}, reverse charge under the adjoint as in a Hilbert/U(1) convention, or insert any positive-total-shift kernel and require a populated trace-visible witness.",
            "finite_machine_boundary": "exact Fraction arithmetic on finite Laurent supports and exhaustive integer charge pairs; no momentum, phase-space, regulator, loop, or resummation integral",
        },
        "carrier": {
            "algebra": "Q[t,t^-1] with finite support",
            "charge": "q(t^n)=n; multiplication adds charge",
            "BT_adjoint": "(t^n)^dagger=t^n; charge is preserved",
            "trace": "coefficient of t^0; every nonzero charge is trace-null",
            "negative_radical": "direct sum of charges q<0, a relative trace radical inside the nonpositive image but not a radical of the full Laurent algebra",
            "populated_B_fixture": b.serialized(),
            "populated_C_fixture": c.serialized(),
        },
        "eq20_completeness_kernel": {
            "source_equation": "Bateman-Turok Eq. (20)",
            "nonzero_terms": serialize_kernel(offdiagonal),
            "classification": kernel_classification,
            "tensor_power_rows": multiplicity_rows,
            "finite_weight_fixture": [
                {"numerator": value.numerator, "denominator": value.denominator}
                for value in weights
            ],
            "finite_weight_scale": {
                "numerator": inclusive_scale.numerator,
                "denominator": inclusive_scale.denominator,
            },
            "finite_weight_image": inclusive_image.serialized(),
        },
        "born_trace_identity": {
            "A": a.serialized(),
            "BT_A_dagger_A": bt_product.serialized(),
            "BT_trace": {
                "numerator": bt_product.trace().numerator,
                "denominator": bt_product.trace().denominator,
            },
            "B_dagger_B_trace": {
                "numerator": (b.terms[0] ** 2).numerator,
                "denominator": (b.terms[0] ** 2).denominator,
            },
            "Hilbert_mutation_trace": {
                "numerator": hilbert_product.trace().numerator,
                "denominator": hilbert_product.trace().denominator,
            },
            "negative_supports": {
                "B_dagger_C": bc.support(),
                "C_dagger_B": cb.support(),
                "C_dagger_C": cc.support(),
            },
        },
        "sharp_counterexamples": [
            {
                "mutation": "turn on W^{Omega Omega}",
                "input": "t^-2",
                "output": positive_witness_output.serialized(),
                "trace": 1,
            },
            {
                "mutation": "replace the BT charge-preserving adjoint by charge reversal",
                "input": "A=B+C from the populated carrier",
                "BT_trace": str(bt_product.trace()),
                "mutated_trace": str(hilbert_product.trace()),
            },
        ],
        "criterion_exhaustion": {
            "declared_pair_range": [-3, 3],
            "declared_negative_input_range": [-6, -1],
            "rows": criterion_rows,
            "result": "closure for the full negative carrier iff total shift <= 0; every positive shift r has counterexample t^-r -> 1",
        },
        "disposition": {
            "radical_closure": "PROVED_FOR_FINITE_EQ20_COMPLETENESS_KERNEL",
            "physical_inclusive_map": "NOT_CONSTRUCTED",
            "real_virtual_cancellation": "NOT_COMPUTED",
            "collinear_regulator": "NOT_SELECTED",
            "resummed_asymptotic_states": "NOT_CONSTRUCTED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "the first nontrivial real and virtual process amplitudes on one common collinear regulator",
            "a phase-space or distributional prescription proving cancellation of the regulator dependence",
            "the higher-order R_t map and the deferred proof that its image has no positive charges",
            "existence and trace-class control of the asymptotic/inclusive process operator",
            "a measure calculation excluding an SO+(1,1) anomaly",
        ],
        "next_gate": "Construct the first regulated real-plus-virtual process map. Radical closure no longer needs to be recomputed if its completeness and process kernels have nonpositive total charge shifts; the remaining work is analytic existence, regulator cancellation, and positivity of the neutral quotient component.",
        "does_not_establish": [
            "a KLN theorem, collinear cancellation, finite cross section, or any loop amplitude",
            "that Bateman-Turok Eq. (19) or the no-positive-charge property holds beyond the order supplied in their Letter",
            "that an inclusive process map exists, is trace class, or has the formal sandwich representation used by this charge carrier",
            "positivity of the neutral B component after loops or resummation",
            "absence of an SO+(1,1) measure anomaly",
            "that the negative sector is a radical of the full graded algebra; it pairs nontrivially with positive charge and is radical only relative to the one-sided nonpositive image",
            "anything about the tensor or BRST gravitational lift",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "external_source": "S. Bateman and N. Turok, arXiv:2607.00096v1, Eqs. (6), (19)-(21), especially the off-diagonal Wightman/completeness kernel in Eq. (20)",
            "inputs": [
                {"path": "notes/bateman-turok-embedding.md",
                 "sha256": sha256("notes/bateman-turok-embedding.md")},
                {"path": "reverse_physics/certificates/REVERSE_PHYSICS_CHARGE_GRADING_LOOP_STABILITY_V1.json",
                 "sha256": sha256("reverse_physics/certificates/REVERSE_PHYSICS_CHARGE_GRADING_LOOP_STABILITY_V1.json")},
                {"path": "reverse_physics/certificates/REVERSE_PHYSICS_BT_BORN_TRACE_V1.json",
                 "sha256": sha256("reverse_physics/certificates/REVERSE_PHYSICS_BT_BORN_TRACE_V1.json")},
                {"path": "reverse_physics/certificates/REVERSE_PHYSICS_BT_IR_REGULATOR_TRILEMMA_V1.json",
                 "sha256": sha256("reverse_physics/certificates/REVERSE_PHYSICS_BT_IR_REGULATOR_TRILEMMA_V1.json")},
            ],
            "exact_arithmetic": "fractions.Fraction on generated finite Laurent supports; no floating point",
        },
        "verification_commands": [
            "python3 reverse_physics/bt_inclusive_radical_closure.py --check",
            "python3 reverse_physics/verify_bt_inclusive_radical_closure.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_inclusive_radical_closure",
        ],
        "checks": {
            "detail": checks,
            "total": len(checks),
            "passed": sum(1 for passed in checks.values() if passed),
            "failures": failures,
            "ok": not failures,
        },
        "report": REPORT_PATH,
        "schema": SCHEMA_PATH,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="BT inclusive radical closure")
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not (args.emit or args.check):
        args.check = True

    certificate = build()
    print("BT finite inclusive radical-closure preflight")
    for name, passed in certificate["checks"]["detail"].items():
        print(("[OK ] " if passed else "[FAIL] ") + name)
    print("checks %d/%d" % (
        certificate["checks"]["passed"], certificate["checks"]["total"]
    ))

    if args.emit:
        if not certificate["checks"]["ok"]:
            print("refusing to emit a failing certificate")
            return 1
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(certificate, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print("wrote %s" % os.path.relpath(CERT_PATH, REPO_ROOT))

    if args.check:
        if not os.path.exists(CERT_PATH):
            print("FAIL missing certificate %s" % os.path.relpath(
                CERT_PATH, REPO_ROOT))
            return 1
        with open(CERT_PATH, encoding="utf-8") as handle:
            recorded = json.load(handle)
        if recorded != certificate:
            print("FAIL recorded certificate differs from exact recomputation")
            return 1
        print("recorded certificate agrees with exact recomputation")

    print("RESULT: %s" % ("PASS" if certificate["checks"]["ok"] else "FAIL"))
    return 0 if certificate["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
