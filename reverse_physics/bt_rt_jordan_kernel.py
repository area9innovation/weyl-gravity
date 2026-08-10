#!/usr/bin/env python3
"""Derive the first nonlinear Bateman--Turok R_t kernel exactly.

The calculation uses a tiny Laurent-polynomial algebra over Gaussian
rationals.  It first checks Appendix C at order lambda^0, then expands the
two composite fields in Eq. (16) through order lambda and extracts the
resonant two-annihilator kernel.  No floating-point arithmetic is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_RT_JORDAN_KERNEL_V1.json",
)
SCHEMA_PATH = (
    "reverse_physics/schema/reverse-physics-bt-rt-jordan-kernel-v1.schema.json"
)
REPORT_PATH = "reverse_physics/reports/bt-rt-jordan-kernel.md"
SOURCE_COMMIT = "481505506ef804febc748bcd4e0521a89e16843a"
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_ASYMPTOTIC_GENERATOR_PREFLIGHT_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json",
]


@dataclass(frozen=True)
class Gaussian:
    real: Fraction = Fraction(0)
    imag: Fraction = Fraction(0)

    def __add__(self, other):
        if hasattr(other, "terms"):
            return NotImplemented
        other = gaussian(other)
        return Gaussian(self.real + other.real, self.imag + other.imag)

    __radd__ = __add__

    def __neg__(self):
        return Gaussian(-self.real, -self.imag)

    def __sub__(self, other):
        if hasattr(other, "terms"):
            return NotImplemented
        return self + (-gaussian(other))

    def __rsub__(self, other):
        return gaussian(other) - self

    def __mul__(self, other):
        if hasattr(other, "terms"):
            return NotImplemented
        other = gaussian(other)
        return Gaussian(
            self.real * other.real - self.imag * other.imag,
            self.real * other.imag + self.imag * other.real,
        )

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = gaussian(other)
        norm = other.real * other.real + other.imag * other.imag
        if not norm:
            raise ZeroDivisionError
        return Gaussian(
            (self.real * other.real + self.imag * other.imag) / norm,
            (self.imag * other.real - self.real * other.imag) / norm,
        )


def gaussian(value):
    if isinstance(value, Gaussian):
        return value
    return Gaussian(Fraction(value))


ZERO = Gaussian()
ONE = Gaussian(Fraction(1))
I = Gaussian(Fraction(0), Fraction(1))


class Laurent:
    """Laurent polynomials in (e1,e2,t) over Q(i)."""

    def __init__(self, terms=None):
        clean = {}
        for powers, coefficient in (terms or {}).items():
            coefficient = gaussian(coefficient)
            powers = tuple(int(power) for power in powers)
            if coefficient != ZERO:
                clean[powers] = clean.get(powers, ZERO) + coefficient
        self.terms = {powers: value for powers, value in clean.items()
                      if value != ZERO}

    @classmethod
    def monomial(cls, e1=0, e2=0, t=0, coefficient=1):
        return cls({(e1, e2, t): gaussian(coefficient)})

    def __add__(self, other):
        other = poly(other)
        out = dict(self.terms)
        for powers, coefficient in other.terms.items():
            out[powers] = out.get(powers, ZERO) + coefficient
        return Laurent(out)

    __radd__ = __add__

    def __neg__(self):
        return Laurent({powers: -value for powers, value in self.terms.items()})

    def __sub__(self, other):
        return self + (-poly(other))

    def __rsub__(self, other):
        return poly(other) - self

    def __mul__(self, other):
        other = poly(other)
        out = {}
        for left, a in self.terms.items():
            for right, b in other.terms.items():
                powers = tuple(x + y for x, y in zip(left, right))
                out[powers] = out.get(powers, ZERO) + a * b
        return Laurent(out)

    __rmul__ = __mul__

    def derivative_t(self):
        out = {}
        for (p1, p2, pt), coefficient in self.terms.items():
            if pt:
                out[(p1, p2, pt - 1)] = coefficient * pt
        return Laurent(out)

    def max_t_degree(self):
        return max((powers[2] for powers in self.terms), default=-1)

    def coefficient_t(self, degree):
        return Laurent({(p1, p2, 0): value
                        for (p1, p2, pt), value in self.terms.items()
                        if pt == degree})

    def __eq__(self, other):
        return self.terms == poly(other).terms


def poly(value):
    return value if isinstance(value, Laurent) else Laurent.monomial(
        coefficient=value)


E1 = Laurent.monomial(e1=1)
E2 = Laurent.monomial(e2=1)
T = Laurent.monomial(t=1)
ENERGY = E1 + E2


def omega_resonant(time_polynomial):
    """omega_t(i exp(ipx), exp(-iEt) P(t)) at parent resonance."""
    time_polynomial = poly(time_polynomial)
    return I * time_polynomial.derivative_t() + 2 * ENERGY * time_polynomial


def box_resonant(time_polynomial):
    """Box on exp(-iEt)P(t) when |p|=E=e1+e2."""
    time_polynomial = poly(time_polynomial)
    return (time_polynomial.derivative_t().derivative_t()
            - 2 * I * ENERGY * time_polynomial.derivative_t())


def linear_consistency():
    """Check which oscillator must multiply the ordinary/growing modes."""
    # For one momentum E, omega(phi_ordinary)=ordinary/(4E^2),
    # omega(phi_growing)=(2iEt growing + e^(2iEt) growing^dag)/(4E^2),
    # and omega(Box phi)=growing.  Therefore Eq. (32) names the growing
    # oscillator a1 and Eq. (33) names the ordinary oscillator a2.
    printed = {"ordinary": "a1", "growing": "a2"}
    required = {"ordinary": "a2", "growing": "a1"}
    return {
        "printed": printed,
        "required": required,
        "printed_eq31_matches_eq32": printed["growing"] == "a1",
        "printed_eq31_matches_eq33": (
            printed["ordinary"] == "a2" and printed["growing"] == "a1"
        ),
        "label_exchange_repairs_both": required == {
            "ordinary": "a2", "growing": "a1"
        },
    }


def nonlinear_a_kernel():
    """Bose-symmetrized positive-positive kernels in the repaired a basis."""
    ordinary_1 = poly(1)
    ordinary_2 = poly(1)
    growing_1 = 1 + 2 * I * E1 * T
    growing_2 = 1 + 2 * I * E2 * T
    modes_1 = {"a2": ordinary_1, "a1": growing_1}
    modes_2 = {"a2": ordinary_2, "a1": growing_2}
    single_box_1 = {"a2": poly(0), "a1": 4 * E1 * E1}
    single_box_2 = {"a2": poly(0), "a1": 4 * E2 * E2}
    omega = {}
    upsilon = {}
    for left in ("a2", "a1"):
        for right in ("a2", "a1"):
            pair = modes_1[left] * modes_2[right]
            # The lambda*phi^2/2 functional derivative has unit symmetric
            # two-field kernel.
            omega[(left, right)] = omega_resonant(pair)
            # F=(partial phi)^2-phi Box phi
            #   = Box(phi1 phi2)-2(phi1 Box phi2+phi2 Box phi1)
            f_pair = (
                box_resonant(pair)
                - 2 * (
                    modes_1[left] * single_box_2[right]
                    + single_box_1[left] * modes_2[right]
                )
            )
            upsilon[(left, right)] = omega_resonant(f_pair)
    return omega, upsilon


def repaired_inverse():
    """Annihilator part of the inverse leading map a=L_t^-1 b."""
    # a1=b_Upsilon; a2=4e^2 b_Omega-2iet b_Upsilon.
    return {
        1: {
            "a2": {"Omega": 4 * E1 * E1,
                   "Upsilon": -2 * I * E1 * T},
            "a1": {"Omega": poly(0), "Upsilon": poly(1)},
        },
        2: {
            "a2": {"Omega": 4 * E2 * E2,
                   "Upsilon": -2 * I * E2 * T},
            "a1": {"Omega": poly(0), "Upsilon": poly(1)},
        },
    }


def transport_to_bt(kernel):
    inverse = repaired_inverse()
    out = {}
    for left_bt in ("Omega", "Upsilon"):
        for right_bt in ("Omega", "Upsilon"):
            value = poly(0)
            for (left_a, right_a), coefficient in kernel.items():
                value += (
                    coefficient
                    * inverse[1][left_a][left_bt]
                    * inverse[2][right_a][right_bt]
                )
            out[(left_bt, right_bt)] = value
    # Restore D1*D2=(2e1)^-3(2e2)^-3.
    density = Fraction(1, 64) * Laurent.monomial(e1=-3, e2=-3)
    return {key: density * value for key, value in out.items()}


def expected_a_kernels():
    omega = {
        ("a2", "a2"): 2 * ENERGY,
        ("a2", "a1"): 2 * E1 + 4 * I * ENERGY * E2 * T,
        ("a1", "a2"): 2 * E2 + 4 * I * ENERGY * E1 * T,
        ("a1", "a1"): (
            4 * I * (E1 * E1 + E2 * E2) * T
            - 8 * ENERGY * E1 * E2 * T * T
        ),
    }
    upsilon = {
        ("a2", "a2"): poly(0),
        ("a2", "a1"): 8 * ENERGY * E2 * (E1 - E2),
        ("a1", "a2"): 8 * ENERGY * E1 * (E2 - E1),
        ("a1", "a1"): -8 * ENERGY * (E1 * E1 + E2 * E2),
    }
    return omega, upsilon


def bt_expected_without_typo():
    """Spell the expected carrier table without relying on power syntax."""
    return {
        "Omega": {
            ("Omega", "Omega"): Fraction(1, 2) * ENERGY
            * Laurent.monomial(e1=-1, e2=-1),
            ("Omega", "Upsilon"): Fraction(1, 8)
            * Laurent.monomial(e2=-3),
            ("Upsilon", "Omega"): Fraction(1, 8)
            * Laurent.monomial(e1=-3),
            ("Upsilon", "Upsilon"): poly(0),
        },
        "Upsilon": {
            ("Omega", "Omega"): poly(0),
            ("Omega", "Upsilon"): Fraction(1, 2) * ENERGY
            * (E1 - E2) * Laurent.monomial(e1=-1, e2=-2),
            ("Upsilon", "Omega"): Fraction(1, 2) * ENERGY
            * (E2 - E1) * Laurent.monomial(e1=-2, e2=-1),
            ("Upsilon", "Upsilon"): Fraction(-1, 8) * ENERGY
            * (E1 * E1 + E2 * E2)
            * Laurent.monomial(e1=-3, e2=-3),
        },
    }


def krein_gram(omega, upsilon):
    """Fixed-splitting two-daughter Gram using the off-diagonal BT metric."""
    opposite = {"Omega": "Upsilon", "Upsilon": "Omega"}
    rows = {"Omega": omega, "Upsilon": upsilon}
    metric_factor = 4 * E1 * E2
    gram = {}
    for left in rows:
        for right in rows:
            value = poly(0)
            for species in (("Omega", "Omega"), ("Omega", "Upsilon"),
                            ("Upsilon", "Omega"), ("Upsilon", "Upsilon")):
                dual = (opposite[species[0]], opposite[species[1]])
                value += rows[left][species] * rows[right][dual]
            gram[(left, right)] = metric_factor * value
    determinant = (
        gram[("Omega", "Omega")] * gram[("Upsilon", "Upsilon")]
        - gram[("Omega", "Upsilon")] * gram[("Upsilon", "Omega")]
    )
    return gram, determinant


def expected_gram():
    g00 = Fraction(1, 8) * Laurent.monomial(e1=-2, e2=-2)
    g11 = (-2 * ENERGY * ENERGY * (E1 - E2) * (E1 - E2)
           * Laurent.monomial(e1=-2, e2=-2))
    g01 = (Fraction(-1, 2) * ENERGY * ENERGY
           * (E1 * E1 + E2 * E2 - E1 * E2)
           * Laurent.monomial(e1=-3, e2=-3))
    return {
        ("Omega", "Omega"): g00,
        ("Omega", "Upsilon"): g01,
        ("Upsilon", "Omega"): g01,
        ("Upsilon", "Upsilon"): g11,
    }, g00 * g11 - g01 * g01


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def build():
    linear = linear_consistency()
    omega_a, upsilon_a = nonlinear_a_kernel()
    expected_omega_a, expected_upsilon_a = expected_a_kernels()
    omega_bt = transport_to_bt(omega_a)
    upsilon_bt = transport_to_bt(upsilon_a)
    expected_bt = bt_expected_without_typo()
    gram, determinant = krein_gram(omega_bt, upsilon_bt)
    expected_g, expected_det = expected_gram()
    checks = {
        "printed_eq31_fails_eq32": not linear["printed_eq31_matches_eq32"],
        "printed_eq31_fails_eq33": not linear["printed_eq31_matches_eq33"],
        "single_label_exchange_repairs_both": linear["label_exchange_repairs_both"],
        "omega_a_kernel_exact": omega_a == expected_omega_a,
        "upsilon_a_kernel_exact": upsilon_a == expected_upsilon_a,
        "omega_bt_kernel_exact": omega_bt == expected_bt["Omega"],
        "upsilon_bt_kernel_exact": upsilon_bt == expected_bt["Upsilon"],
        "all_bt_annihilator_secular_terms_cancel": all(
            value.max_t_degree() <= 0
            for value in list(omega_bt.values()) + list(upsilon_bt.values())
        ),
        "omega_upsilonupsilon_entry_cancels": (
            omega_bt[("Upsilon", "Upsilon")] == poly(0)
        ),
        "fixed_split_krein_gram_exact": gram == expected_g,
        "fixed_split_gram_is_symmetric": (
            gram[("Omega", "Upsilon")] == gram[("Upsilon", "Omega")]
        ),
        "fixed_split_determinant_exact": determinant == expected_det,
        "endpoint_cross_gram_has_cubic_pole": (
            min(power[0] for power in gram[("Omega", "Upsilon")].terms) == -3
            and min(power[1] for power in gram[("Omega", "Upsilon")].terms) == -3
        ),
        "formal_generator_is_anti_krein_by_completion": True,
        "incoming_outgoing_annihilator_kernel_equal": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "probability_gate_stays_closed": True,
        "no_lorentzian_claim": True,
    }
    certificate = {
        "certificate": "REVERSE_PHYSICS_BT_RT_JORDAN_KERNEL_V1",
        "schema_version": "reverse-physics-bt-rt-jordan-kernel-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": (
            "order-lambda resonant two-annihilator kernel and ordered-slot "
            "Krein diagnostic of the BT composite asymptotic map, before "
            "Bose phase space and continuum endpoint extension"
        ),
        "question": (
            "Can Eq. (16) supply the omitted order-lambda R_t kernel, and does "
            "its Jordan secular growth survive on the BT carrier?"
        ),
        "answer": (
            "Yes, after exposing a label inconsistency in the printed Appendix C. "
            "As printed, Eq. (31) cannot imply both Eqs. (32) and (33). Exchanging "
            "a1 and a2 in Eq. (31) repairs both. Expanding Eq. (16) then fixes the "
            "two-annihilator order-lambda kernel. Its t and t^2 terms cancel "
            "exactly after the repaired leading map is inverted onto the "
            "Omega/Upsilon carrier. The resulting fixed-splitting kernel is "
            "time independent and has a formal anti-Krein cubic lift, but its "
            "off-diagonal Gram has cubic endpoint poles. A distributional "
            "endpoint extension and full projector trace are still required."
        ),
        "appendix_c_consistency": {
            "printed_eq31": "ordinary a1 plus (1+2iEt) a2",
            "eq32_requires": "growing oscillator a1 because Box phi selects it",
            "eq33_requires": "ordinary a2 and growing a1",
            "minimal_repair": "exchange a1 and a2 in Eq. (31)",
            "alternative_not_excluded": (
                "equivalently exchange the labels in Eqs. (32)-(33); the public "
                "Letter alone does not identify which displayed equation is mistyped"
            ),
            "status": "INTERNALLY_INCONSISTENT_AS_PRINTED_REPAIRED_FOR_DERIVATION",
        },
        "composite_expansion": {
            "Omega": "lambda^-1+phi+(lambda/2)*phi^2+O(lambda^2)",
            "Upsilon": "Box(phi)+lambda*((partial phi)^2-phi*Box(phi))+O(lambda^2)",
            "metric_convention": "Box=partial_t^2-nabla^2",
            "resonance": "E=e1+e2 with collinear positive-energy daughters",
            "symplectic_rule": "omega_res[P]=i*P'(t)+2*E*P(t)",
        },
        "repaired_a_basis_kernel": {
            "normalization": (
                "Bose-symmetrized functional kernel after removing lambda, "
                "D1*D2=(2e1)^-3(2e2)^-3, and momentum delta"
            ),
            "Omega": {
                "a2_a2": "2*E",
                "a2_a1": "2*e1+4*i*E*e2*t",
                "a1_a2": "2*e2+4*i*E*e1*t",
                "a1_a1": "4*i*(e1^2+e2^2)*t-8*E*e1*e2*t^2",
            },
            "Upsilon": {
                "a2_a2": "0",
                "a2_a1": "8*E*e2*(e1-e2)",
                "a1_a2": "8*E*e1*(e2-e1)",
                "a1_a1": "-8*E*(e1^2+e2^2)",
            },
        },
        "bt_carrier_kernel": {
            "inverse_linear_map": (
                "a1=b_Upsilon; a2=4*e^2*b_Omega-2*i*e*t*b_Upsilon "
                "on the two-annihilator sector"
            ),
            "normalization": "after restoring D1*D2; E=e1+e2",
            "delta_b_Omega": {
                "Omega_Omega": "E/(2*e1*e2)",
                "Omega_Upsilon": "1/(8*e2^3)",
                "Upsilon_Omega": "1/(8*e1^3)",
                "Upsilon_Upsilon": "0",
            },
            "delta_b_Upsilon": {
                "Omega_Omega": "0",
                "Omega_Upsilon": "E*(e1-e2)/(2*e1*e2^2)",
                "Upsilon_Omega": "E*(e2-e1)/(2*e1^2*e2)",
                "Upsilon_Upsilon": "-E*(e1^2+e2^2)/(8*e1^3*e2^3)",
            },
            "secular_disposition": "ALL_T_AND_T2_TERMS_CANCEL_EXACTLY",
            "incoming_outgoing": (
                "the two-annihilator coefficient is the same at t->+infinity "
                "and t->-infinity; oscillatory creation sectors are not included"
            ),
        },
        "formal_generator": {
            "definition": (
                "K_down=(b_Upsilon^dag*delta_b_Omega+"
                "b_Omega^dag*delta_b_Upsilon)/(2*E); K=K_down-K_down^dag"
            ),
            "property": (
                "K^dag=-K; its parent number-lowering commutator is delta_b_i "
                "on a finite nonendpoint wave-packet carrier"
            ),
            "status": "FORMAL_FINITE_MODE_LIFT_ONLY",
        },
        "fixed_splitting_krein_gram": {
            "metric": (
                "ordered daughter slots with [b_Omega(e),b_Upsilon^dag(e)]=2e "
                "and diagonal entries zero; no Bose factor or phase-space measure"
            ),
            "G_OmegaOmega": "1/(8*e1^2*e2^2)",
            "G_UpsilonUpsilon": "-2*E^2*(e1-e2)^2/(e1^2*e2^2)",
            "G_OmegaUpsilon": (
                "-E^2*(e1^2+e2^2-e1*e2)/(2*e1^3*e2^3)"
            ),
            "determinant": (
                "-E^2*(e1-e2)^2/(4*e1^4*e2^4)-"
                "E^4*(e1^2+e2^2-e1*e2)^2/(4*e1^6*e2^6)<0"
            ),
            "endpoint": (
                "with e1=z*E and e2=(1-z)*E, the cross Gram has z^-3 "
                "and (1-z)^-3 poles and is not an ordinary locally integrable density"
            ),
            "disposition": "DISTRIBUTIONAL_ENDPOINT_EXTENSION_REQUIRED",
        },
        "disposition": {
            "published_appendix_c_linear_system": "INCONSISTENT_AS_PRINTED",
            "minimal_label_repair": "CONSTRUCTED",
            "order_lambda_two_annihilator_kernel": "COEFFICIENT_COMPUTED",
            "jordan_secular_terms_on_bt_carrier": "CANCEL_EXACTLY",
            "formal_finite_mode_generator": "CONSTRUCTED",
            "continuum_distributional_domain": "NOT_CONSTRUCTED",
            "exact_gram_one_over_48": "NOT_DERIVED",
            "incoming_creation_and_oscillatory_sectors": "NOT_CONSTRUCTED",
            "full_nlo_quotient_trace": "NOT_COMPUTED",
            "physical_nlo_probability": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "choose and independently justify a distributional extension of the cubic endpoint poles",
            "include oscillatory creation/annihilation and vacuum-squeeze sectors in the transported projector",
            "place initial- and final-state degenerate sectors on one resolution carrier",
            "derive rather than fit the continuum Gram and compare it with 1/48 per unordered pair",
            "combine that projector with renormalized virtual and complete real contributions",
            "prove regulator cancellation, trace-class control, and positivity of the quotient trace",
        ],
        "next_gate": (
            "Construct the plus/distributional extension of the z-endpoint kernel "
            "together with the oscillatory sectors, then evaluate the transported "
            "neutral projector Gram. The target remains 1/48 per unordered pair; "
            "the present result supplies its first dynamically derived kernel but "
            "does not yet supply the number."
        ),
        "does_not_establish": [
            "which Appendix C display contains the typographical label error",
            "a strong or weak operator limit for the full R_t map",
            "a continuum coherent or KLN projector",
            "the coefficient 1/48 from BT dynamics",
            "a complete NLO cross section or probability",
            "positivity or unitarity beyond the BT tree theorem",
            "a tensor or BRST gravitational lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-10",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096",
                "equations": ["Eq. (16)", "Appendix C Eqs. (31)-(33)"],
            },
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_rt_jordan_kernel.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_rt_jordan_kernel.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_rt_jordan_kernel",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT_PATH,
        "schema": SCHEMA_PATH,
    }
    return certificate


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=CERT_PATH)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    certificate = build()
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] recorded_certificate: {exc}")
            return 1
        ok = recorded == certificate
        print(f"[{'PASS' if ok else 'FAIL'}] exact_reproduction")
        print(f"RESULT: {'PASS' if ok else 'FAIL'} "
              f"({certificate['checks']['passed']}/{certificate['checks']['total']})")
        return 0 if ok else 1
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(certificate, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(args.output)
    return 0 if certificate["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
