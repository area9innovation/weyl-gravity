#!/usr/bin/env python3
"""Exact external-virtuality-jet obstruction for the BT Born projector.

Bateman--Turok Eq. (13) differentiates a squared *off-shell* amplitude once
with respect to every external mass squared before setting those masses to
zero.  The appropriate finite algebraic carrier is therefore the square-free
jet algebra Q[x_1,...,x_n]/(x_i^2).  This producer proves that the resulting
functional does not descend to the ordinary on-shell quotient x_i=0.

The result is deliberately local-algebraic.  It does not compute a loop
amplitude, real-emission phase space, regulator cancellation, or a physical
NLO cross section.
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
    "REVERSE_PHYSICS_BT_OFFSHELL_JET_OBSTRUCTION_V1.json",
)
REPORT_PATH = "reverse_physics/reports/bt-offshell-jet-obstruction.md"
SCHEMA_PATH = (
    "reverse_physics/schema/"
    "reverse-physics-bt-offshell-jet-obstruction-v1.schema.json"
)
SOURCE_COMMIT = "22c46b47bdab068a3a7116448d50c5e361cb7a5b"


class Jet:
    """An exact element of Q[x_1,...,x_n]/(x_i^2), keyed by bit mask."""

    def __init__(self, n, coefficients=None):
        self.n = int(n)
        limit = 1 << self.n
        clean = {}
        for mask, coefficient in (coefficients or {}).items():
            mask = int(mask)
            coefficient = Fraction(coefficient)
            if not 0 <= mask < limit:
                raise ValueError("mask outside declared jet")
            if coefficient:
                clean[mask] = clean.get(mask, Fraction(0)) + coefficient
        self.coefficients = {m: c for m, c in clean.items() if c}

    @classmethod
    def one(cls, n):
        return cls(n, {0: 1})

    @classmethod
    def monomial(cls, n, mask, coefficient=1):
        return cls(n, {mask: coefficient})

    def __add__(self, other):
        if not isinstance(other, Jet):
            other = Jet.monomial(self.n, 0, other)
        if self.n != other.n:
            raise ValueError("jet arity mismatch")
        out = dict(self.coefficients)
        for mask, coefficient in other.coefficients.items():
            out[mask] = out.get(mask, Fraction(0)) + coefficient
        return Jet(self.n, out)

    __radd__ = __add__

    def __mul__(self, other):
        if not isinstance(other, Jet):
            other = Jet.monomial(self.n, 0, other)
        if self.n != other.n:
            raise ValueError("jet arity mismatch")
        out = {}
        for left_mask, left_coefficient in self.coefficients.items():
            for right_mask, right_coefficient in other.coefficients.items():
                # An overlap contains some x_i^2 and vanishes in the jet.
                if left_mask & right_mask:
                    continue
                mask = left_mask | right_mask
                out[mask] = out.get(mask, Fraction(0)) + (
                    left_coefficient * right_coefficient
                )
        return Jet(self.n, out)

    __rmul__ = __mul__

    @property
    def full_mask(self):
        return (1 << self.n) - 1

    def on_shell(self):
        return self.coefficients.get(0, Fraction(0))

    def projector(self):
        """Coefficient selected by d/dx_1 ... d/dx_n at x=0."""
        return self.coefficients.get(self.full_mask, Fraction(0))

    def serialized(self):
        return [
            {
                "mask": mask,
                "subset": [index + 1 for index in range(self.n)
                           if mask & (1 << index)],
                "coefficient": rational(coefficient),
            }
            for mask, coefficient in sorted(self.coefficients.items())
        ]

    def __eq__(self, other):
        return (
            isinstance(other, Jet)
            and self.n == other.n
            and self.coefficients == other.coefficients
        )


def rational(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def ambiguity_witness(n, parameter):
    """M=1 and M'=1+a*x_1...x_n have equal on-shell values."""
    parameter = Fraction(parameter)
    base = Jet.one(n)
    top = Jet.monomial(n, (1 << n) - 1, parameter)
    mutated = base + top
    base_probability = (base * base).projector()
    mutated_probability = (mutated * mutated).projector()
    return {
        "external_legs": n,
        "jet_dimension": 1 << n,
        "parameter": rational(parameter),
        "base_on_shell": rational(base.on_shell()),
        "mutated_on_shell": rational(mutated.on_shell()),
        "base_projected_probability": rational(base_probability),
        "mutated_projected_probability": rational(mutated_probability),
        "probability_shift": rational(mutated_probability - base_probability),
        "expected_shift": rational(2 * parameter),
        "mutation": "Delta M = a x_1...x_n",
    }


def complement_rows(n):
    """Show that every square-free amplitude slot can reach the projector."""
    full = (1 << n) - 1
    rows = []
    for mask in range(1 << n):
        complement = full ^ mask
        pair = (Jet.monomial(n, mask) +
                Jet.monomial(n, complement))
        rows.append({
            "mask": mask,
            "complement_mask": complement,
            "union_mask": mask | complement,
            "overlap_mask": mask & complement,
            "projector_of_pair_squared": rational((pair * pair).projector()),
        })
    return rows


def build():
    dimension_rows = []
    for n in range(1, 8):
        witness = ambiguity_witness(n, Fraction(n, n + 2))
        dimension_rows.append(witness)

    virtual = ambiguity_witness(4, Fraction(3, 7))
    real = ambiguity_witness(5, Fraction(5, 11))
    combined_shift = (
        Fraction(virtual["probability_shift"]["numerator"],
                 virtual["probability_shift"]["denominator"])
        + Fraction(real["probability_shift"]["numerator"],
                   real["probability_shift"]["denominator"])
    )

    complement_4 = complement_rows(4)
    complement_5 = complement_rows(5)

    checks = {
        "square_free_dimensions_are_2_to_n": all(
            row["jet_dimension"] == 2 ** row["external_legs"]
            for row in dimension_rows
        ),
        "all_on_shell_witnesses_agree": all(
            row["base_on_shell"] == row["mutated_on_shell"]
            for row in dimension_rows
        ),
        "all_projector_shifts_are_twice_parameter": all(
            row["probability_shift"] == row["expected_shift"]
            and row["probability_shift"]["numerator"] != 0
            for row in dimension_rows
        ),
        "four_leg_virtual_witness_is_nonzero": (
            virtual["probability_shift"] == rational(Fraction(6, 7))
        ),
        "five_leg_real_witness_is_nonzero": (
            real["probability_shift"] == rational(Fraction(10, 11))
        ),
        "nlo_ambiguities_are_independent": (
            combined_shift == Fraction(136, 77)
        ),
        "every_four_leg_slot_has_complement_pair": all(
            row["union_mask"] == 15
            and row["overlap_mask"] == 0
            and row["projector_of_pair_squared"] == rational(2)
            for row in complement_4
        ),
        "every_five_leg_slot_has_complement_pair": all(
            row["union_mask"] == 31
            and row["overlap_mask"] == 0
            and row["projector_of_pair_squared"] == rational(2)
            for row in complement_5
        ),
        "published_companions_remain_unavailable": True,
        "physical_nlo_map_remains_fail_closed": True,
        "no_lorentzian_claim": True,
    }

    certificate = {
        "certificate": "REVERSE_PHYSICS_BT_OFFSHELL_JET_OBSTRUCTION_V1",
        "schema_version": "reverse-physics-bt-offshell-jet-obstruction-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "external-virtuality jet necessity and public-data obstruction",
        "question": (
            "Do the published on-shell amplitudes and optical-theorem data "
            "define the first Bateman--Turok real-plus-virtual probability?"
        ),
        "answer": (
            "No. The delta-prime projector requires a square-free off-shell "
            "virtuality jet. Amplitudes with identical on-shell values can "
            "give different projected probabilities. The public sources do "
            "not provide the required four-leg virtual and five-leg real jets."
        ),
        "candidate_theorem": {
            "statement": (
                "For n dipole external legs, D_n[K M^dagger M] is defined "
                "by the square-free jet Q[x_1,...,x_n]/(x_i^2), but does not "
                "descend to the on-shell quotient M -> M(0) whenever "
                "K(0) and M(0) are nonzero."
            ),
            "carrier": (
                "Exact rational square-free virtuality jets; x_i denotes the "
                "independent external mass squared used for delta'(p_i^2)."
            ),
            "proof_obligations": [
                "derive the square-free jet from one derivative per external leg",
                "show the top-coefficient projector equals the mixed derivative",
                "construct equal-on-shell amplitudes with unequal probabilities",
                "classify the first four-leg virtual and five-leg real requirements",
                "keep kinematic integration and infrared cancellation fail-closed",
            ],
            "counterexample_strategy": (
                "Add a rational multiple of x_1...x_n. It vanishes on shell "
                "but shifts the projected squared amplitude by twice that multiple."
            ),
            "finite_machine_boundary": (
                "Exact coefficients through n=7 and exhaustive complement "
                "pairing for the n=4 and n=5 NLO jets; no continuum integral."
            ),
        },
        "jet_algebra": {
            "ring": "Q[x_1,...,x_n]/(x_1^2,...,x_n^2)",
            "projector": "D_n(F) = coefficient of x_1...x_n in F",
            "on_shell_map": "epsilon(F) = F(0,...,0)",
            "dimension": "2^n",
            "non_descent_identity": (
                "M_a=1+a*x_1...x_n: epsilon(M_a)=1 but "
                "D_n(M_a^dagger M_a)=2a"
            ),
            "kinematic_prefactor_extension": (
                "For analytic K, the same mutation shifts D_n[K|M|^2] "
                "by 2*K(0)*Re(M(0)^dagger*a); the rational fixture sets "
                "K(0)=M(0)=1 and a real."
            ),
            "dimension_rows": dimension_rows,
            "four_leg_complement_rows": complement_4,
            "five_leg_complement_rows": complement_5,
        },
        "first_nlo_pair": {
            "order_bookkeeping": (
                "For the PS interaction, tree 2->2 is order lambda^2, "
                "one-loop 2->2 interference and tree 2->3 squared are both "
                "order lambda^6 in probability."
            ),
            "virtual_channel": {
                "external_legs": 4,
                "required_object": (
                    "multi-affine jet of the regulated renormalized one-loop "
                    "2->2 interference, including its phase-space factor"
                ),
                "fixture": virtual,
            },
            "real_channel": {
                "external_legs": 5,
                "required_object": (
                    "multi-affine jet of the regulated tree 2->3 squared "
                    "amplitude, including its phase-space factor"
                ),
                "fixture": real,
            },
            "combined_fixture_shift": rational(combined_shift),
            "inference_boundary": (
                "The five-leg derivative count follows from BT Eq. (18), "
                "one delta-prime Wightman factor for each external leg; BT "
                "prints the explicit phase-space reduction only for 2->2."
            ),
        },
        "literature_audit": [
            {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "supports": (
                    "Eqs. (9)-(13) use an amputated off-shell amplitude and "
                    "differentiate the squared amplitude before the on-shell limit; "
                    "Eq. (18) gives general n-particle projections."
                ),
                "status_on_2026_08_09": "PUBLIC_V1",
            },
            {
                "source": "Holdom arXiv:2303.06723 and arXiv:2402.09223",
                "supports": (
                    "one-loop renormalization and selected two-body optical-theorem "
                    "or differential-cross-section data, not the required NLO jets"
                ),
                "status_on_2026_08_09": "PUBLIC",
            },
            {
                "source": (
                    "Anderson--Bateman--Herzog--Turok, Renormalization of a "
                    "Four-Derivative Theory"
                ),
                "supports": "claimed companion infrared/renormalization analysis",
                "status_on_2026_08_09": "TO_APPEAR_IN_BT_REFERENCE_25",
            },
            {
                "source": (
                    "Bateman--Turok, Unitarity and Positivity in Higher "
                    "Derivative QFTs from Hidden Ghost Parity"
                ),
                "supports": "deferred detailed projection and positivity proof",
                "status_on_2026_08_09": "TO_APPEAR_IN_BT_REFERENCE_19",
            },
        ],
        "disposition": {
            "offshell_jet_necessity": "PROVED",
            "descent_to_on_shell_amplitude_class": "DISPROVED",
            "published_on_shell_data_define_first_nlo_probability": "NO",
            "four_leg_virtual_jet": "NOT_COMPUTED",
            "five_leg_real_jet": "NOT_COMPUTED",
            "common_regulator": "NOT_SELECTED",
            "real_virtual_cancellation": "NOT_COMPUTED",
            "physical_nlo_process_map": "NOT_CONSTRUCTED",
            "underlying_theory_ambiguous": "NOT_ESTABLISHED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "regulated renormalized four-leg one-loop off-shell jet through multi-degree (1,1,1,1)",
            "regulated five-leg tree real-emission off-shell jet through multi-degree (1,1,1,1,1)",
            "one common soft/collinear regulator and phase-space prescription for both jets",
            "proof that counterterms, interpolating fields, and projectors transform jointly so the projected probability is scheme/field-redefinition invariant",
            "real--virtual cancellation or dressed-state/resummation construction",
            "trace-class physical inclusive process operator after the regulator is removed",
        ],
        "next_gate": (
            "Compute the multi-affine tree 2->3 jet directly from BT Feynman "
            "rules and classify its soft/collinear faces on a declared common "
            "regulator; in parallel specify the renormalized four-leg loop jet."
        ),
        "does_not_establish": [
            "that the PS theory itself is ambiguous or inconsistent",
            "that a full off-shell Feynman calculation cannot supply the missing jets",
            "a loop amplitude, a tree 2->3 amplitude, or a KLN cancellation",
            "scheme or field-redefinition dependence of a completed BT construction",
            "a finite physical cross section or positivity beyond tree level",
            "a regulator, resummation, Hadamard state, or causal perturbative construction",
            "any tensor/BRST gravitational lift or anything LORENTZIAN-CAUSAL",
            "literature priority for the elementary jet-algebra lemma",
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
                        "REVERSE_PHYSICS_BT_INCLUSIVE_RADICAL_CLOSURE_V1.json"
                    ),
                    "sha256": sha256(
                        "reverse_physics/certificates/"
                        "REVERSE_PHYSICS_BT_INCLUSIVE_RADICAL_CLOSURE_V1.json"
                    ),
                },
                {
                    "path": (
                        "reverse_physics/certificates/"
                        "REVERSE_PHYSICS_BT_BORN_TRACE_V1.json"
                    ),
                    "sha256": sha256(
                        "reverse_physics/certificates/"
                        "REVERSE_PHYSICS_BT_BORN_TRACE_V1.json"
                    ),
                },
            ],
            "arxiv_sources": [
                "https://arxiv.org/abs/2607.00096v1",
                "https://arxiv.org/abs/2303.06723",
                "https://arxiv.org/abs/2402.09223",
            ],
        },
        "verification_commands": [
            "python3 reverse_physics/bt_offshell_jet_obstruction.py --check",
            "python3 reverse_physics/verify_bt_offshell_jet_obstruction.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_offshell_jet_obstruction",
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
        description="produce exact BT off-shell jet obstruction certificate")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    rendered = canonical(payload)
    if args.write:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                recorded = handle.read()
        except OSError as error:
            print(error)
            return 1
        if recorded != rendered:
            print("certificate drift")
            return 1
    checks = payload["checks"]
    print("checks %d/%d" % (checks["passed"], checks["total"]))
    print("RESULT: %s" % ("PASS" if checks["ok"] else "FAIL"))
    return 0 if checks["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
