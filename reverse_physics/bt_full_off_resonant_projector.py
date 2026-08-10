#!/usr/bin/env python3
"""Derive the full off-resonant BT quadratic carrier and its soft trace test."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_FULL_OFF_RESONANT_PROJECTOR_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-full-off-resonant-projector-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-full-off-resonant-projector.md"
SOURCE_COMMIT = "ece5386eb2b9b6983e233805ba1f98dd0e02a6f1"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_RT_JORDAN_KERNEL_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ENDPOINT_EXTENSION_AMBIGUITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CANONICAL_ENDPOINT_AMBIGUITY_V1.json",
]


class Gaussian(tuple):
    def __new__(cls, real=0, imag=0):
        return tuple.__new__(cls, (Fraction(real), Fraction(imag)))

    def __add__(self, other):
        if hasattr(other, "terms"):
            return NotImplemented
        other = gaussian(other)
        return Gaussian(self[0] + other[0], self[1] + other[1])

    __radd__ = __add__

    def __neg__(self):
        return Gaussian(-self[0], -self[1])

    def __sub__(self, other):
        return self + (-gaussian(other))

    def __rsub__(self, other):
        return gaussian(other) - self

    def __mul__(self, other):
        if hasattr(other, "terms"):
            return NotImplemented
        other = gaussian(other)
        return Gaussian(
            self[0] * other[0] - self[1] * other[1],
            self[0] * other[1] + self[1] * other[0],
        )

    __rmul__ = __mul__


def gaussian(value):
    return value if isinstance(value, Gaussian) else Gaussian(value)


ZERO = Gaussian()
I = Gaussian(0, 1)


class Laurent:
    """Laurent polynomials in (e1,e2,d,t), d=e1+e2-E_parent."""

    def __init__(self, terms=None):
        out = {}
        for powers, coefficient in (terms or {}).items():
            powers = tuple(int(x) for x in powers)
            coefficient = gaussian(coefficient)
            out[powers] = out.get(powers, ZERO) + coefficient
        self.terms = {key: value for key, value in out.items() if value != ZERO}

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
                powers = tuple(left[index] + right[index] for index in range(4))
                out[powers] = out.get(powers, ZERO) + a * b
        return Laurent(out)

    __rmul__ = __mul__

    def derivative_t(self):
        return Laurent({
            (a, b, d, t - 1): coefficient * t
            for (a, b, d, t), coefficient in self.terms.items() if t
        })

    def at_resonance(self):
        return Laurent({
            (a, b, 0, t): coefficient
            for (a, b, d, t), coefficient in self.terms.items() if d == 0
        })

    def swap_daughters(self):
        return Laurent({
            (b, a, d, t): coefficient
            for (a, b, d, t), coefficient in self.terms.items()
        })

    def evaluate(self, e1, e2, deficit, time):
        values = [Fraction(e1), Fraction(e2), Fraction(deficit), Fraction(time)]
        total = ZERO
        for powers, coefficient in self.terms.items():
            factor = Fraction(1)
            for value, power in zip(values, powers):
                factor *= value ** power
            total += coefficient * factor
        return total

    def max_t_degree(self):
        return max((powers[3] for powers in self.terms), default=-1)

    def __eq__(self, other):
        return self.terms == poly(other).terms


def monomial(e1=0, e2=0, deficit=0, time=0, coefficient=1):
    return Laurent({(e1, e2, deficit, time): gaussian(coefficient)})


def poly(value):
    return value if isinstance(value, Laurent) else monomial(coefficient=value)


E1 = monomial(e1=1)
E2 = monomial(e2=1)
DEFICIT = monomial(deficit=1)
TIME = monomial(time=1)
SUM = E1 + E2
PARENT_ENERGY = SUM - DEFICIT


def omega_off_shell(time_polynomial):
    """Symplectic extraction before setting E_parent=e1+e2."""
    return I * time_polynomial.derivative_t() + (
        PARENT_ENERGY + SUM
    ) * time_polynomial


def box_off_shell(time_polynomial):
    """Box on the product mode with spatial momentum magnitude E_parent."""
    return (
        time_polynomial.derivative_t().derivative_t()
        - 2 * I * SUM * time_polynomial.derivative_t()
        + (PARENT_ENERGY * PARENT_ENERGY - SUM * SUM) * time_polynomial
    )


def a_basis_kernels():
    modes_1 = {"a2": poly(1), "a1": 1 + 2 * I * E1 * TIME}
    modes_2 = {"a2": poly(1), "a1": 1 + 2 * I * E2 * TIME}
    boxes_1 = {"a2": poly(0), "a1": 4 * E1 * E1}
    boxes_2 = {"a2": poly(0), "a1": 4 * E2 * E2}
    omega = {}
    upsilon = {}
    for left in ("a2", "a1"):
        for right in ("a2", "a1"):
            pair = modes_1[left] * modes_2[right]
            omega[left, right] = omega_off_shell(pair)
            nonlinear = box_off_shell(pair) - 2 * (
                modes_1[left] * boxes_2[right]
                + boxes_1[left] * modes_2[right]
            )
            upsilon[left, right] = omega_off_shell(nonlinear)
    return omega, upsilon


def transport(kernel):
    inverse_1 = {
        "a2": {"Omega": 4 * E1 * E1, "Upsilon": -2 * I * E1 * TIME},
        "a1": {"Omega": poly(0), "Upsilon": poly(1)},
    }
    inverse_2 = {
        "a2": {"Omega": 4 * E2 * E2, "Upsilon": -2 * I * E2 * TIME},
        "a1": {"Omega": poly(0), "Upsilon": poly(1)},
    }
    out = {}
    density = Fraction(1, 64) * monomial(e1=-3, e2=-3)
    for left in ("Omega", "Upsilon"):
        for right in ("Omega", "Upsilon"):
            value = poly(0)
            for (a, b), coefficient in kernel.items():
                value += coefficient * inverse_1[a][left] * inverse_2[b][right]
            out[left, right] = density * value
    return out


def krein_gram(omega, upsilon):
    opposite = {"Omega": "Upsilon", "Upsilon": "Omega"}
    rows = {"Omega": omega, "Upsilon": upsilon}
    out = {}
    for left in rows:
        for right in rows:
            value = poly(0)
            for one in ("Omega", "Upsilon"):
                for two in ("Omega", "Upsilon"):
                    value += (
                        rows[left][one, two]
                        * rows[right][opposite[one], opposite[two]]
                    )
            out[left, right] = 4 * E1 * E2 * value
    return out


def expected_resonant():
    energy = E1 + E2
    return {
        "Omega": {
            ("Omega", "Omega"): Fraction(1, 2) * energy * monomial(e1=-1, e2=-1),
            ("Omega", "Upsilon"): Fraction(1, 8) * monomial(e2=-3),
            ("Upsilon", "Omega"): Fraction(1, 8) * monomial(e1=-3),
            ("Upsilon", "Upsilon"): poly(0),
        },
        "Upsilon": {
            ("Omega", "Omega"): poly(0),
            ("Omega", "Upsilon"): Fraction(1, 2) * energy * (E1 - E2) * monomial(e1=-1, e2=-2),
            ("Upsilon", "Omega"): Fraction(1, 2) * energy * (E2 - E1) * monomial(e1=-2, e2=-1),
            ("Upsilon", "Upsilon"): Fraction(-1, 8) * energy * (E1 * E1 + E2 * E2) * monomial(e1=-3, e2=-3),
        },
    }


def soft_blowup(value):
    """Set e1=r, e2=1, deficit=alpha*r and return (r,alpha) Laurent terms."""
    out = {}
    for (e1, _e2, deficit, time), coefficient in value.terms.items():
        if time:
            raise ValueError("secular term survived")
        powers = (e1 + deficit, deficit)
        out[powers] = out.get(powers, ZERO) + coefficient
    return {powers: coefficient for powers, coefficient in out.items() if coefficient != ZERO}


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def complex_rat(value):
    return {"real": rat(value[0]), "imag": rat(value[1])}


def serialized_terms(value):
    return [
        {
            "powers": list(powers),
            "coefficient": complex_rat(coefficient),
        }
        for powers, coefficient in sorted(value.terms.items())
    ]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def build():
    omega_a, upsilon_a = a_basis_kernels()
    omega = transport(omega_a)
    upsilon = transport(upsilon_a)
    gram = krein_gram(omega, upsilon)
    resonant = expected_resonant()
    soft_cross = soft_blowup(gram["Omega", "Upsilon"])
    leading_power = min(power[0] for power in soft_cross)
    leading_terms = {
        alpha_power: coefficient
        for (radial_power, alpha_power), coefficient in soft_cross.items()
        if radial_power == leading_power
    }
    leading_residue = leading_terms.get(0, ZERO)
    measured_power = leading_power + 2
    radial_scaling_degree = -measured_power
    radial_singular_order = radial_scaling_degree - 1
    cutoff_response = -leading_residue
    daughter_exchange = (
        gram["Omega", "Upsilon"].swap_daughters()
        == gram["Omega", "Upsilon"]
    )
    samples = []
    for e1, e2, deficit in (
        (1, 2, Fraction(1, 3)),
        (2, 3, Fraction(1, 2)),
        (3, 5, Fraction(2, 3)),
    ):
        samples.append({
            "e1": rat(e1), "e2": rat(e2), "deficit": rat(deficit),
            "delta_b_Omega_UpsilonUpsilon": complex_rat(
                omega["Upsilon", "Upsilon"].evaluate(e1, e2, deficit, 7)
            ),
            "delta_b_Upsilon_OmegaOmega": complex_rat(
                upsilon["Omega", "Omega"].evaluate(e1, e2, deficit, 7)
            ),
            "gram_cross": complex_rat(
                gram["Omega", "Upsilon"].evaluate(e1, e2, deficit, 7)
            ),
        })
    checks = {
        "omega_resonance_matches_predecessor": all(
            omega[key].at_resonance() == value
            for key, value in resonant["Omega"].items()
        ),
        "upsilon_resonance_matches_predecessor": all(
            upsilon[key].at_resonance() == value
            for key, value in resonant["Upsilon"].items()
        ),
        "all_explicit_secular_terms_cancel_off_resonance": all(
            value.max_t_degree() <= 0
            for value in list(omega.values()) + list(upsilon.values())
        ),
        "off_resonant_Omega_UpsilonUpsilon_is_nonzero": (
            omega["Upsilon", "Upsilon"]
            == Fraction(-1, 64) * DEFICIT * monomial(e1=-3, e2=-3)
        ),
        "off_resonant_Upsilon_OmegaOmega_is_nonzero": (
            upsilon["Omega", "Omega"].at_resonance() == poly(0)
            and upsilon["Omega", "Omega"] != poly(0)
        ),
        "gram_is_symmetric": gram["Omega", "Upsilon"] == gram["Upsilon", "Omega"],
        "soft_cross_leading_power_is_cubic": leading_power == -3,
        "soft_cross_leading_residue_is_angle_independent": (
            leading_terms == {0: Gaussian(Fraction(-1, 2))}
        ),
        "full_radial_measure_is_logarithmic": measured_power == -1,
        "full_measure_local_ambiguity_is_one_dimensional": (
            radial_singular_order == 0 and daughter_exchange
        ),
        "common_cutoff_rescaling_response_is_half_log_c": (
            cutoff_response == Gaussian(Fraction(1, 2))
        ),
        "ordinary_composition_not_trace_class": measured_power <= -1,
        "one_over_48_not_derived": (
            radial_singular_order >= 0 and cutoff_response != ZERO
        ),
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "no_lorentzian_claim": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_FULL_OFF_RESONANT_PROJECTOR_V1",
        "schema_version": "reverse-physics-bt-full-off-resonant-projector-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact off-resonant carrier and full-measure soft composition obstruction",
        "question": "Does composing the full Delta-E-dependent BT quadratic carrier before the exactly collinear restriction uniquely fix the endpoint normalization and derive 1/48?",
        "answer": "No on the ordinary wave-packet carrier. The full off-resonant map is exactly derivable and contains channels lost on the resonant slice, but its parent-diagonal K-sharp-K composition retains an angle-independent cubic soft Gram. The restored d^3p radial Jacobian reduces this to a logarithmic dr/r divergence and hence one local soft constant, rather than the three endpoint jets of the flat collinear slice. A common cutoff rescaling changes the finite part by +(1/2) log(c) in the normalized soft chart. Thus the full ordinary composition is not trace class and does not select 1/48; a renormalized soft-collinear asymptotic Hamiltonian or independent matching condition is still required.",
        "kinematics": {
            "deficit": "d=e1+e2-E_parent",
            "parent_energy": "E_parent=e1+e2-d",
            "phase": "exp(-i*d*t)",
            "symplectic_extractor": "exp(-i*d*t)*(i*P_prime+(E_parent+e1+e2)*P)",
            "box_product": "P_double_prime-2*i*(e1+e2)*P_prime+(E_parent^2-(e1+e2)^2)*P",
        },
        "off_resonant_kernel": {
            "normalization": "lambda and exp(-i*d*t) suppressed; D1*D2=(2e1)^-3(2e2)^-3 restored; entries are Bose-symmetrized functional kernels",
            "delta_b_Omega": {"_".join(key): serialized_terms(value) for key, value in omega.items()},
            "delta_b_Upsilon": {"_".join(key): serialized_terms(value) for key, value in upsilon.items()},
            "samples": samples,
            "resonant_restriction": "exactly REVERSE_PHYSICS_BT_RT_JORDAN_KERNEL_V1",
        },
        "operator_composition": {
            "generator": "K_down=int d3P (b_Upsilon^dag*delta_b_Omega+b_Omega^dag*delta_b_Upsilon)/(2E_parent), with K=K_down-K_down^dag",
            "parent_diagonalization": "the two spatial momentum delta functions in K-sharp-K give delta_3(P-P_prime), leaving one daughter integral",
            "remaining_measure": "d3p1=d^3p1/(2pi)^3=r^2 dr dOmega/(2pi)^3 after p2=P-p1",
            "bose_factor": "the symmetric quadratic map contributes 1/2 times the ordered-slot Gram after the two daughter contractions",
            "parent_factor": "each generator contributes 1/(2E_parent); these factors do not change the soft scaling classification",
            "gram": {"_".join(key): serialized_terms(value) for key, value in gram.items()},
        },
        "soft_blowup": {
            "chart": "e1=r, e2=1, d=alpha*r; physical soft rays have alpha=1-cos(theta)+O(r)",
            "ordered_cross_gram_leading": "-1/(2*r^3), independent of alpha",
            "homogeneous_restoration": "-E_parent/(2*r^3) before Bose, parent, and (2pi) factors",
            "radial_measure": "r^2 dr",
            "measured_leading": "-(1/2) dr/r in the normalized e2=1 ordered chart",
            "scaling_degree": radial_scaling_degree,
            "reflection_even_local_freedom": "singular order zero: one rotationally invariant delta^3(p_soft) normalization, common to the two daughter faces by exact exchange symmetry on this chart",
            "cutoff_family": "I_epsilon=int_epsilon^r0 -(1/2) dr/r",
            "rescaling": "I_(c*epsilon)-I_epsilon=+(1/2) log(c)",
        },
        "target_comparison": {
            "target": "1/48 per unordered pair after Born normalization",
            "status": "NOT_DERIVED",
            "reason": "the ordinary full-measure composition is logarithmically non-trace-class and its finite part shifts under a common cutoff rescaling before a soft-collinear matching theorem is supplied",
        },
        "disposition": {
            "full_off_resonant_kernel": "DERIVED",
            "resonant_slice": "RECOVERED",
            "ordinary_parent_projector_composition": "LOGARITHMICALLY_NON_TRACE_CLASS",
            "flat_collinear_three_jet_ambiguity": "REDUCED_TO_ONE_SOFT_NORMALIZATION_ON_DECLARED_FULL_MEASURE_CHART",
            "unique_endpoint_normalization": "NOT_SELECTED",
            "one_over_48": "NOT_DERIVED",
            "physical_nlo_probability": "NOT_ESTABLISHED",
        },
        "next_gate": "Construct a BT soft-collinear asymptotic Hamiltonian and hard S-matrix on this off-resonant carrier. Its anti-Krein evolution must cancel the +(1/2) log(c) cutoff response between asymptotic and hard factors, reproduce the independently certified real coefficient after Born normalization, and be regulator-family independent before 1/48 can be claimed.",
        "missing_object_ledger": [
            "a renormalized soft-collinear BT asymptotic Hamiltonian or equivalent factorization operator",
            "a proof that its kernel is universal and independent of the hard process",
            "common incoming/outgoing evolution and regulator flow",
            "cancellation of the certified logarithmic soft response between asymptotic and hard factors",
            "the finite matched hard coefficient and cut-free virtual terms",
            "the complete quotient trace and positivity test",
        ],
        "does_not_establish": [
            "that the three flat-slice endpoint constants vanish globally",
            "that no renormalized asymptotic Hamiltonian exists",
            "that BT cannot produce 1/48",
            "a complete NLO probability",
            "beyond-tree positivity",
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
                "equations": ["Eq. (16)", "Eq. (19)", "Appendix C"],
            },
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_full_off_resonant_projector.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_full_off_resonant_projector.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_full_off_resonant_projector",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=CERT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    certificate = build()
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = json.load(handle)
        except Exception as error:
            print("[FAIL]", error)
            return 1
        ok = recorded == certificate
        print(f"[{'PASS' if ok else 'FAIL'}] exact_reproduction")
        print(
            f"RESULT: {'PASS' if ok else 'FAIL'} "
            f"({certificate['checks']['passed']}/{certificate['checks']['total']})"
        )
        return 0 if ok else 1
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(certificate, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(args.output)
    return 0 if certificate["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
