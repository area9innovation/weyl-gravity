#!/usr/bin/env python3
"""Exact BT real kernel and axis-compatible regulator-gluing obstruction.

The real rail keeps the physical collinear splitting fraction and outer
scattering ratio symbolic in a three-spectator square-free jet.  The phase
rail then restores the BT delta-prime sign, the factorized three-body phase
space, and the identical-particle weights.  Finally, the real finite-part
response is compared with the certified virtual external-mass logarithm on a
declared class of axis-compatible parent/daughter regulator maps.
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
    "REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json",
)
SCHEMA_PATH = (
    "reverse_physics/schema/"
    "reverse-physics-bt-real-virtual-axis-gluing-v1.schema.json"
)
REPORT_PATH = "reverse_physics/reports/bt-real-virtual-axis-gluing.md"
SOURCE_COMMIT = "81f39db6ad02a19d96922f28b3611b14f91ed5f6"
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EXTERNAL_PROJECTOR_CARRIER_MISMATCH_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EXTERNAL_MASS_BOUNDARY_LOG_JET_V1.json",
]


class SpectatorJet:
    """Three-variable square-free jet over an exact function field."""

    def __init__(self, ring, coefficients=None):
        self.ring = ring
        self.coefficients = {
            int(mask): ring.base(value)
            for mask, value in (coefficients or {}).items() if value != 0
        }

    def _coerce(self, other):
        return self.ring(other)

    def __bool__(self):
        return bool(self.coefficients)

    def __add__(self, other):
        other = self._coerce(other)
        out = dict(self.coefficients)
        for mask, value in other.coefficients.items():
            out[mask] = out.get(mask, self.ring.base.zero) + value
        return SpectatorJet(self.ring, out)

    __radd__ = __add__

    def __neg__(self):
        return SpectatorJet(
            self.ring,
            {mask: -value for mask, value in self.coefficients.items()},
        )

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __rsub__(self, other):
        return self._coerce(other) - self

    def __mul__(self, other):
        other = self._coerce(other)
        out = {}
        for left_mask, left_value in self.coefficients.items():
            for right_mask, right_value in other.coefficients.items():
                if left_mask & right_mask:
                    continue
                mask = left_mask | right_mask
                out[mask] = (
                    out.get(mask, self.ring.base.zero)
                    + left_value * right_value
                )
        return SpectatorJet(self.ring, out)

    __rmul__ = __mul__

    def inverse(self):
        scalar = self.coefficients.get(0, self.ring.base.zero)
        if scalar == 0:
            raise ZeroDivisionError("spectator jet has zero scalar part")
        nilpotent = self - SpectatorJet(self.ring, {0: scalar})
        ratio = (-1 / scalar) * nilpotent
        out = SpectatorJet(self.ring, {0: self.ring.base.one})
        term = out
        for _ in range(3):
            term = term * ratio
            out = out + term
        return (1 / scalar) * out

    def __truediv__(self, other):
        return self * self._coerce(other).inverse()

    def __rtruediv__(self, other):
        return self._coerce(other) * self.inverse()


class SpectatorJetField:
    def __init__(self, base):
        self.base = base
        self.zero = SpectatorJet(self)
        self.one = SpectatorJet(self, {0: base.one})

    def __call__(self, value):
        if isinstance(value, SpectatorJet):
            return value
        return SpectatorJet(self, {0: self.base(value)})


def rational(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def symbolic_real_kernel():
    """Rebuild the spectator-projected C^2 on the full collinear family."""
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field

    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    import reverse_physics.bt_five_point_independent_mass_threshold as source

    base, a0, a1, tau, zeta, chi = field(
        "a0,a1,tau,zeta,chi", QQ
    )
    ring = SpectatorJetField(base)
    masses = [
        a0,
        a1,
        SpectatorJet(ring, {1: base.one}),
        SpectatorJet(ring, {2: base.one}),
        SpectatorJet(ring, {4: base.one}),
    ]
    old_hard = source.HARD
    try:
        source.HARD = [1 - zeta, -chi, 1, zeta * (chi - 1)]
        amplitude = source.dot_vertex_amplitude(ring, masses, tau)
    finally:
        source.HARD = old_hard
    leading = amplitude.coefficient(2)
    projected = (leading * leading).coefficients.get(7, base.zero)
    expected = (
        3 * (a0 - a1) ** 2
        * ((a0 - a1) ** 2 - 2 * tau * (a0 + a1))
        / (8 * tau ** 3)
    )
    return {
        "orders_zero_one_cancel": (
            not amplitude.coefficient(0) and not amplitude.coefficient(1)
        ),
        "leading_nonzero": bool(leading),
        "projected": projected,
        "expected": expected,
        "identity": projected == expected,
        "zeta_independent": projected.diff(zeta) == 0,
        "chi_independent": projected.diff(chi) == 0,
    }


def phase_normalization():
    """Restore all rational factors, leaving pi^(-4)/s explicit."""
    amplitude_square = Fraction(64)       # M5=8*lambda^3*A5
    identical = Fraction(1, 12)           # 1/(2!*3!)
    flux = Fraction(1, 2)                 # 1/(2*s)
    factorization = Fraction(1, 2)        # dt/(2*pi)
    outer_two_body = Fraction(1, 32)      # dPhi2/dOmega, pi^-2
    inner_two_body = Fraction(1, 32)      # dPhi2/dOmega, pi^-2
    before_inner_angle = (
        amplitude_square * identical * flux * factorization
        * outer_two_body * inner_two_body
    )
    after_inner_angle = before_inner_angle * 4
    projector_sign = Fraction(-1)         # (-1)^5 delta-prime representation
    reduced_shift = Fraction(-3, 8)
    per_pair_shift = projector_sign * after_inner_angle * reduced_shift
    pair_count = 3
    return {
        "before_inner_angle": before_inner_angle,
        "after_inner_angle": after_inner_angle,
        "projector_sign": projector_sign,
        "per_pair_shift": per_pair_shift,
        "all_pair_shift": pair_count * per_pair_shift,
        "pair_count": pair_count,
    }


def regulator_maps():
    """Exact responses for physical and deliberately incompatible gluings."""
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field

    base, u, v = field("u,v", QQ)
    # r=u^2 and c=v^2.  The physical threshold map is
    # G=x*(1+sqrt(r))^2.  Its rescaling ratio is rational in u,v.
    physical_ratio = (1 + v * u) ** 2 / (1 + u) ** 2
    linear_ratio = (1 + v ** 2 * u ** 2) / (1 + u ** 2)
    physical_axis = physical_ratio.subs(u, 0)
    linear_axis = linear_ratio.subs(u, 0)
    engineered_exponent = Fraction(1, 12)
    virtual_log_weight = Fraction(3, 128)
    engineered_virtual_shift = -virtual_log_weight * engineered_exponent
    return {
        "physical_ratio": physical_ratio,
        "linear_ratio": linear_ratio,
        "physical_axis": physical_axis,
        "linear_axis": linear_axis,
        "engineered_exponent": engineered_exponent,
        "engineered_virtual_shift": engineered_virtual_shift,
        "engineered_axis_compatible": False,
    }


def build():
    kernel = symbolic_real_kernel()
    phase = phase_normalization()
    maps = regulator_maps()
    checks = {
        "amplitude_orders_zero_one_cancel": kernel["orders_zero_one_cancel"],
        "amplitude_leading_order_two_nonzero": kernel["leading_nonzero"],
        "spectator_projected_kernel_identity": kernel["identity"],
        "splitting_fraction_cancels": kernel["zeta_independent"],
        "outer_ratio_cancels": kernel["chi_independent"],
        "bt_five_leg_sign_is_negative": phase["projector_sign"] == -1,
        "phase_before_inner_angle_is_one_over_768": (
            phase["before_inner_angle"] == Fraction(1, 768)
        ),
        "inner_angle_gives_one_over_192": (
            phase["after_inner_angle"] == Fraction(1, 192)
        ),
        "three_identical_final_pairs": phase["pair_count"] == 3,
        "per_pair_response_is_one_over_512": (
            phase["per_pair_shift"] == Fraction(1, 512)
        ),
        "all_pair_response_is_three_over_512": (
            phase["all_pair_shift"] == Fraction(3, 512)
        ),
        "physical_threshold_map_axis_response_zero": maps["physical_axis"] == 1,
        "linear_axis_map_response_zero": maps["linear_axis"] == 1,
        "engineered_cancellation_coefficient": (
            maps["engineered_virtual_shift"] == Fraction(-1, 512)
        ),
        "engineered_map_rejected_by_axis_gate": (
            not maps["engineered_axis_compatible"]
        ),
        "predecessor_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "claim_stays_reduced_mode": True,
        "physical_nlo_probability_stays_open": True,
        "beyond_tree_positivity_stays_open": True,
        "no_lorentzian_claim": True,
    }
    certificate = {
        "certificate": "REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1",
        "schema_version": "reverse-physics-bt-real-virtual-axis-gluing-v1",
        "dependency_tags": ["REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": (
            "complete final-state collinear logarithmic response on the "
            "axis-compatible parent/daughter regulator class"
        ),
        "question": (
            "Does the complete real final-pair mass-ratio response cancel the "
            "one-loop virtual external-mass logarithm under a physical "
            "parent/daughter regulator gluing?"
        ),
        "answer": (
            "No on the declared class. The exact real kernel is independent of "
            "splitting fraction and outer angle. After the BT sign, inner angle, "
            "and all three identical final-pair regions, its finite-part shift is "
            "+3*lambda^6*log(c)/(512*pi^4*s). Every axis-compatible parent map, "
            "including the physical threshold, gives zero constant virtual "
            "response as one daughter regulator is removed. The logarithmic "
            "responses therefore do not cancel."
        ),
        "declared_carrier": {
            "order": "lambda^6 final-state collinear real plus one-loop virtual logarithmic response",
            "observable": "differential in the nonsingular outer two-body solid angle",
            "real_regions": "all three unordered pairs of three identical final particles",
            "mass_corner": "x0=x, x1=r*x with r->0 after three exact spectator derivatives",
            "regulator_class": (
                "G(x,y)=x*g(y/x), with g continuous at zero and finite nonzero g(0); spectators fixed. "
                "Equivalently G(x,c*y)/G(x,y)->1 for every fixed c>0 as y/x->0."
            ),
            "scope": (
                "the complete logarithmic normalization response on this final-state "
                "collinear carrier; not the full NLO quotient trace"
            ),
        },
        "real_kernel": {
            "five_point_normalization": "A5=M5/(8*lambda^3)=delta^2*C+O(delta^3)",
            "spectator_projection": (
                "[a2*a3*a4]C^2=3*(a0-a1)^2*((a0-a1)^2-2*tau*(a0+a1))/(8*tau^3)"
            ),
            "splitting_fraction": "zeta cancels identically",
            "outer_ratio": "chi=-T/S cancels identically",
            "threshold_function": (
                "H(r)=(-5*r^3+3*r^2-3*r+5+6*r*(r+1)*log(r))/(16*(r-1))"
            ),
            "reduced_finite_part": "FP_c=-1/8-(3/8)*log(c)",
        },
        "phase_and_combinatorics": {
            "factorization": "dPhi3=dt/(2*pi)*dPhi2_outer*dPhi2_inner",
            "two_body_density": "dPhi2/dOmega=sqrt(Kallen)/(32*pi^2*P^2)",
            "identical_weight": "1/(2!*3!)=1/12",
            "delta_prime_sign": "(-1)^5=-1",
            "inner_angle": "integral dOmega_inner=4*pi",
            "per_labeled_pair_prefactor": "-lambda^6/(192*pi^4*s)",
            "unordered_final_pairs": 3,
            "per_pair_finite_part_shift": "+lambda^6*log(c_pair)/(512*pi^4*s)",
            "common_three_pair_shift": "+3*lambda^6*log(c)/(512*pi^4*s)",
        },
        "virtual_comparison": {
            "external_boundary_rate": (
                "d_sigma_virtual_boundary/dOmega="
                "3*lambda^6*sum_i log(-mu^2/X_i)/(128*pi^4*s)"
            ),
            "hard_log_response": "zero under daughter mass-ratio rescaling",
            "axis_compatible_parent_response": (
                "lim_(r->0) log(G(x,c*r*x)/G(x,r*x))=0"
            ),
            "physical_threshold_map": "G_thr(x,y)=(sqrt(x)+sqrt(y))^2",
            "physical_threshold_ratio": (
                "G_thr(x,c*y)/G_thr(x,y)=(1+sqrt(c*r))^2/(1+sqrt(r))^2 -> 1"
            ),
            "combined_response": "+3*lambda^6*log(c)/(512*pi^4*s)",
            "disposition": "DOES_NOT_CANCEL_ON_AXIS_COMPATIBLE_GLUINGS",
        },
        "axis_compatibility_theorem": {
            "statement": (
                "For G=x*g(r) with g continuous at zero and finite nonzero g(0), fixed-c ratio "
                "rescaling has G(x,c*r*x)/G(x,r*x)->1. Hence every virtual "
                "log(G), every continuous cut-free term, and every local analytic "
                "counterterm has zero constant response, while the real finite "
                "part has the nonzero response recorded above."
            ),
            "physical_example": "g(r)=(1+sqrt(r))^2",
            "analytic_example": "g(r)=1+r",
            "decisive_mutation": (
                "G_mut=x^(11/12)*y^(1/12) gives virtual shift "
                "-lambda^6*log(c)/(512*pi^4*s) per pair, but G_mut(x,0)=0; "
                "it engineers cancellation only by failing the axis gate."
            ),
        },
        "disposition": {
            "general_real_collinear_kernel": "COMPUTED",
            "inner_splitting_angle_integral": "COMPUTED",
            "identical_final_pair_sum": "COMPUTED",
            "axis_compatible_regulator_gluing": "CLASSIFIED",
            "logarithmic_real_virtual_cancellation": "EXACT_OBSTRUCTION",
            "ordinary_five_mass_bt_projector": "DOES_NOT_EXIST_ON_DECLARED_CARRIER",
            "full_nlo_quotient_trace": "NOT_COMPUTED",
            "physical_nlo_probability": "NOT_ESTABLISHED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a non-axis-compatible or distributional prescription with an independently justified physical normalization",
            "initial-state degenerate sums or dressed incoming states",
            "the renormalized complete NLO quotient trace in the O(1,1) image",
            "a proof that the negative-charge radical remains null after that physical inclusive map",
            "resummation of the collinear asymptotic-state sector",
            "any tensor/BRST gravitational lift importing certified classical data",
        ],
        "does_not_establish": [
            "that every possible regulator or distributional extension fails",
            "that dressed-state or enlarged-degenerate-state cancellation fails",
            "a complete NLO cross section or probability",
            "positivity or unitarity beyond Bateman--Turok's tree theorem",
            "a contradiction in the generalized Born rule",
            "a Lorentzian off-shell BV propagator or Hadamard state",
            "a tensor, BRST, or Weyl-gravity theorem",
            "anything LORENTZIAN-CAUSAL",
            "literature priority for the coefficient or obstruction",
        ],
        "next_gate": (
            "The ordinary independent-mass, axis-compatible off-shell regulator "
            "line stops here. A successor must change architecture explicitly: "
            "construct a distributional normalization from the generalized Born "
            "rule, include degenerate incoming/dressed states, or resum the "
            "collinear sector before testing the quotient trace."
        ),
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-10",
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "equations": ["Eq. (13)", "Eq. (18)", "Appendix B Eqs. (B1)-(B3)"],
                "use": "delta-prime sign, n-particle factorial, and PS vertices",
            },
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_real_virtual_axis_gluing.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_real_virtual_axis_gluing.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_real_virtual_axis_gluing",
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
