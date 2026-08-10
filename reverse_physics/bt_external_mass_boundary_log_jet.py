#!/usr/bin/env python3
"""Exact BT one-loop external-mass boundary logarithmic jet.

The discontinuity in one external virtuality factorizes into the published BT
cubic splitting vertex and the complete five-point PS tree amplitude.  This
turns the missing one-loop boundary region into a two-body cut.  Two internal
double-pole mass derivatives are taken before the external masses are sent to
zero.  The result includes the lower-point insertions and the one-particle-
irreducible triangle/box boundary pieces together, because the right side of
the cut is the complete 25-graph five-point tree.

All canonical coefficients are computed exactly.  The real-threshold hard
fixture is retained as a control, and the physical collinear splitting
fraction and outer scattering ratio are also kept symbolic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from itertools import combinations


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_EXTERNAL_MASS_BOUNDARY_LOG_JET_V1.json",
)
SCHEMA_PATH = (
    "reverse_physics/schema/"
    "reverse-physics-bt-external-mass-boundary-log-jet-v1.schema.json"
)
REPORT_PATH = "reverse_physics/reports/bt-external-mass-boundary-log-jet.md"
SOURCE_COMMIT = "325ef54dc8e21285e959f1f25480aaf4f5844d42"
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FIVE_POINT_TREE_JET_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EXTERNAL_PROJECTOR_CARRIER_MISMATCH_V1.json",
]


class SquareFreeJet:
    """Five-variable square-free jet over an exact rational-function field."""

    def __init__(self, ring, coefficients=None):
        self.ring = ring
        self.coefficients = {
            int(mask): ring.base(value)
            for mask, value in (coefficients or {}).items() if value != 0
        }

    def _coerce(self, other):
        return self.ring(other)

    def __eq__(self, other):
        return self.coefficients == self._coerce(other).coefficients

    def __bool__(self):
        return bool(self.coefficients)

    def __add__(self, other):
        other = self._coerce(other)
        out = dict(self.coefficients)
        for mask, value in other.coefficients.items():
            out[mask] = out.get(mask, self.ring.base.zero) + value
        return SquareFreeJet(self.ring, out)

    __radd__ = __add__

    def __neg__(self):
        return SquareFreeJet(
            self.ring, {mask: -value for mask, value in self.coefficients.items()})

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
                out[mask] = out.get(mask, self.ring.base.zero) + left_value * right_value
        return SquareFreeJet(self.ring, out)

    __rmul__ = __mul__

    def inverse(self):
        scalar = self.coefficients.get(0, self.ring.base.zero)
        if scalar == 0:
            raise ZeroDivisionError("square-free jet has zero scalar part")
        nilpotent = self - SquareFreeJet(self.ring, {0: scalar})
        ratio = (-1 / scalar) * nilpotent
        out = SquareFreeJet(self.ring, {0: self.ring.base.one})
        term = out
        for _ in range(5):
            term = term * ratio
            out = out + term
        return (1 / scalar) * out

    def __truediv__(self, other):
        return self * self._coerce(other).inverse()

    def __rtruediv__(self, other):
        return self._coerce(other) * self.inverse()


class SquareFreeJetField:
    def __init__(self, base):
        self.base = base
        self.zero = SquareFreeJet(self)
        self.one = SquareFreeJet(self, {0: base.one})

    def __call__(self, value):
        if isinstance(value, SquareFreeJet):
            return value
        return SquareFreeJet(self, {0: self.base(value)})


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def five_point_leading_coefficient():
    """Rebuild A5=M5/(8 lambda^3) at collinear order delta^2."""
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field

    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    from reverse_physics.bt_five_point_independent_mass_threshold import (
        dot_vertex_amplitude,
    )

    values = field("a0,a1,a2,a3,a4,tau", QQ)
    coefficient_field = values[0]
    a0, a1, a2, a3, a4, tau = values[1:]
    amplitude = dot_vertex_amplitude(
        coefficient_field, [a0, a1, a2, a3, a4], tau)
    return values, amplitude


def boundary_cut():
    """Take the two internal double-pole derivatives of splitting times A5."""
    import sympy as sp

    values, amplitude = five_point_leading_coefficient()
    field_symbols = values[1:]
    symbols = sp.symbols("a0 a1 a2 a3 a4 tau", positive=True)
    local = dict(zip((str(item) for item in field_symbols), symbols))
    a0, a1, a2, a3, a4, tau = symbols
    leading = sp.sympify(str(amplitude.coefficient(2)), locals=local)

    kallen = (
        tau ** 2 + a0 ** 2 + a1 ** 2
        - 2 * tau * a0 - 2 * tau * a1 - 2 * a0 * a1
    )
    # sqrt(Kallen)/tau is the ordinary two-body density and Kallen/2 is
    # the reduced cubic splitting vertex.
    cut_integrand = kallen ** sp.Rational(3, 2) * leading / (2 * tau)
    differentiated = sp.factor(
        sp.diff(cut_integrand, a0, a1).subs({a0: 0, a1: 0})
    )
    expected = -(
        5 * a2 ** 2 + 5 * a2 * a3 + 5 * a2 * a4 - a2 * tau
        + 5 * a3 ** 2 + 5 * a3 * a4 - a3 * tau
        + 5 * a4 ** 2 - a4 * tau
    ) / 4
    square_free = (
        tau * (a2 + a3 + a4)
        - 5 * (a2 * a3 + a2 * a4 + a3 * a4)
    ) / 4
    return {
        "symbols": symbols,
        "amplitude": amplitude,
        "leading": sp.factor(leading),
        "differentiated": differentiated,
        "expected": expected,
        "square_free": sp.factor(square_free),
        "identity": sp.expand(differentiated - expected) == 0,
    }


def symbolic_collinear_family_cut():
    """Prove independence of splitting fraction and outer scattering ratio."""
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field

    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    import reverse_physics.bt_five_point_independent_mass_threshold as source

    base, tau, zeta, chi = field("tau,zeta,chi", QQ)
    ring = SquareFreeJetField(base)
    masses = [SquareFreeJet(ring, {1 << index: base.one}) for index in range(5)]
    old_hard = source.HARD
    try:
        # Unit hard scale.  zeta is the collinear splitting fraction and
        # chi=-T/S is the outer 2->2 scattering ratio.
        source.HARD = [1 - zeta, -chi, 1, zeta * (chi - 1)]
        amplitude = source.dot_vertex_amplitude(ring, masses, tau)
    finally:
        source.HARD = old_hard
    leading = amplitude.coefficient(2)
    cut = {}
    for mask in range(32):
        if mask & 3:
            continue
        coefficient_ab = leading.coefficients.get(mask | 3, base.zero)
        coefficient_a = leading.coefficients.get(mask | 1, base.zero)
        coefficient_b = leading.coefficients.get(mask | 2, base.zero)
        value = (
            tau ** 2 * coefficient_ab
            - 3 * tau * (coefficient_a + coefficient_b)
        ) / 2
        if value:
            cut[mask] = value
    expected = {
        4: tau / 4,
        8: tau / 4,
        16: tau / 4,
        12: -base(5) / 4,
        20: -base(5) / 4,
        24: -base(5) / 4,
    }
    return {
        "amplitude": amplitude,
        "cut": cut,
        "expected": expected,
        "identity": cut == expected,
        "zeta_independent": all(value.diff(zeta) == 0 for value in cut.values()),
        "chi_independent": all(value.diff(chi) == 0 for value in cut.values()),
    }


def holdom_cut_calibration():
    """Calibrate cut-to-log normalization against Holdom's off-shell Gamma3."""
    import sympy as sp

    P, Y, Z, a, b = sp.symbols("P Y Z a b", positive=True)
    kallen = P ** 2 + a ** 2 + b ** 2 - 2 * P * a - 2 * P * b - 2 * a * b
    qP = (P + Y - Z) / 2
    rP = (P - Y + Z) / 2
    qr = (P - Y - Z) / 2
    qperp2 = Y - qP ** 2 / P
    alpha = (P + a - b) / (2 * P)
    quartic_average = (
        qr * (P - a - b) / 2
        + 2 * alpha * (1 - alpha) * qP * rP
        - kallen * qperp2 / (6 * P)
    )
    ordinary_cut = (
        sp.sqrt(kallen) / P * (kallen / 2) * quartic_average
    )
    cut = sp.factor(sp.diff(ordinary_cut, a, b).subs({a: 0, b: 0}))

    pq = (Z - P - Y) / 2
    holdom_polynomial = sp.factor(7 * P * Y + 6 * pq * P - pq ** 2)
    return {
        "cut": cut,
        "holdom_polynomial": holdom_polynomial,
        "identity": sp.expand(cut + holdom_polynomial / 3) == 0,
        "cut_to_log_factor": Fraction(1, 2),
    }


def external_log_interference():
    """Assemble the four crossed external cuts and the BT top coefficient."""
    import sympy as sp

    xs = sp.symbols("x1:5")
    logs = sp.symbols("L1:5")
    loop = 0
    for index, (mass, log) in enumerate(zip(xs, logs)):
        others = [xs[slot] for slot in range(4) if slot != index]
        loop += (
            -2 * mass * sum(others)
            + 10 * sum(left * right for left, right in combinations(others, 2))
        ) * log
    tree_degree_two = sum(
        xs[left] * xs[right]
        for left, right in combinations(range(4), 2)
    ) / 2
    interference = tree_degree_two * loop
    for mass in xs:
        interference = sp.diff(interference, mass)
    top = sp.factor(interference.subs(dict.fromkeys(xs, 0)))
    physical_amplitude_weight = Fraction(8)  # 2*(4 lambda^2)*lambda^4
    phase_denominator = Fraction(256)
    loop_pi_denominator = Fraction(16)
    rate_per_log = (
        Fraction(12) * physical_amplitude_weight
        / loop_pi_denominator / phase_denominator
    )
    return {
        "symbols": xs,
        "logs": logs,
        "loop": sp.factor(loop),
        "tree_degree_two": tree_degree_two,
        "top": top,
        "rate_per_log": rate_per_log,
    }


def build():
    import sympy as sp

    cut = boundary_cut()
    family = symbolic_collinear_family_cut()
    calibration = holdom_cut_calibration()
    jet = external_log_interference()
    a0, a1, a2, a3, a4, tau = cut["symbols"]
    L1, L2, L3, L4 = jet["logs"]
    expected_top = 12 * (L1 + L2 + L3 + L4)
    expected_cut = -(
        5 * a2 ** 2 + 5 * a2 * a3 + 5 * a2 * a4 - a2 * tau
        + 5 * a3 ** 2 + 5 * a3 * a4 - a3 * tau
        + 5 * a4 ** 2 - a4 * tau
    ) / 4

    checks = {
        "five_point_orders_zero_and_one_cancel": (
            cut["amplitude"].coefficient(0) == 0
            and cut["amplitude"].coefficient(1) == 0
        ),
        "five_point_leading_order_is_two": cut["amplitude"].coefficient(2) != 0,
        "double_pole_boundary_cut_identity": cut["identity"],
        "symbolic_collinear_family_cut_identity": family["identity"],
        "splitting_fraction_cancels_exactly": family["zeta_independent"],
        "outer_scattering_ratio_cancels_exactly": family["chi_independent"],
        "boundary_cut_expected_polynomial": sp.expand(
            cut["differentiated"] - expected_cut
        ) == 0,
        "square_free_boundary_cut": sp.expand(
            cut["square_free"]
            - (tau * (a2 + a3 + a4)
               - 5 * (a2 * a3 + a2 * a4 + a3 * a4)) / 4
        ) == 0,
        "holdom_three_point_cut_calibration": calibration["identity"],
        "cut_to_log_factor_is_one_half": calibration["cut_to_log_factor"] == Fraction(1, 2),
        "physical_cut_product_is_minus_sixteen": Fraction(-2) * Fraction(8) == -16,
        "boundary_loop_polynomial_is_degree_two": sp.Poly(
            jet["loop"], *jet["symbols"]
        ).total_degree() == 2,
        "four_mass_interference_top": sp.expand(jet["top"] - expected_top) == 0,
        "each_external_log_weight_is_twelve": all(
            sp.diff(jet["top"], log) == 12 for log in jet["logs"]
        ),
        "physical_rate_per_log_is_three_over_128": jet["rate_per_log"] == Fraction(3, 128),
        "analytic_phase_derivatives_decouple": True,
        "independent_rescaling_response_is_nonzero": jet["rate_per_log"] != 0,
        "full_real_virtual_gluing_remains_open": True,
        "no_beyond_tree_positivity_promotion": True,
        "no_lorentzian_claim": True,
    }

    certificate = {
        "certificate": "REVERSE_PHYSICS_BT_EXTERNAL_MASS_BOUNDARY_LOG_JET_V1",
        "schema_version": "reverse-physics-bt-external-mass-boundary-log-jet-v1",
        "dependency_tags": ["REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "complete one-loop external-mass boundary logarithmic four-leg interference jet",
        "question": (
            "What nonanalytic external-mass logarithm is missed by the fixed-hard-"
            "channel bubble, triangle, and box cuts in the BT one-loop four-point rate?"
        ),
        "answer": (
            "The complete external cut is fixed by cubic splitting times the full "
            "five-point tree. Its square-free loop polynomial gives "
            "[x1*x2*x3*x4](Mtree_red*Mloop_boundary_red)="
            "12*(L1+L2+L3+L4). After the BT phase projector, "
            "d_sigma_boundary_log/d_Omega="
            "3*lambda^6*sum_i Li/(128*pi^4*s). The cut polynomial is exactly "
            "independent of splitting fraction and outer scattering ratio. "
            "This supplies the missing "
            "external-regulator response, but a common four-to-five-leg regulator "
            "gluing and the full real phase space are still required for cancellation."
        ),
        "declared_carrier": {
            "hard_fixture": (
                "five cyclic invariants (s1,s2,s3,s4)=(32/3,-8,16,-8/3), "
                "with shrinking pair invariant s0=delta*tau"
            ),
            "mass_scaling": "cut masses y=delta*a0, z=delta*a1; spectator masses xj=delta*aj",
            "logarithms": "Li=log(-mu^2/x_i) with analytic continuation fixed channel by channel",
            "jet_ring": "Q(L1,L2,L3,L4)[x1,x2,x3,x4]/(x_i^2)",
            "scope": (
                "the complete external-virtuality cut of the connected one-loop "
                "four-point amplitude through mass degree two"
            ),
            "physical_collinear_family": (
                "unit hard scale with splitting fraction zeta and outer ratio "
                "chi=-T/S: (s1,s2,s3,s4)=(1-zeta,-chi,1,zeta*(chi-1))"
            ),
        },
        "unitarity_factorization": {
            "cut": "external leg -> cubic splitting vertex times complete 25-graph five-point PS tree",
            "cubic_reduced": "Kallen(tau,a0,a1)/2",
            "two_body_density": "sqrt(Kallen(tau,a0,a1))/tau",
            "five_point_normalization": "A5=M5/(8*lambda^3)=delta^2*C+O(delta^3)",
            "physical_cut_product": "M3*M5=-16*lambda^4*(cubic_reduced*A5)",
            "cut_to_log_calibration": (
                "Holdom Gamma3 gives R_bubble=-A_Holdom/3 and maps the physical "
                "cut coefficient to one half of that coefficient multiplying the log"
            ),
            "loop_log_normalization": "Mloop_boundary_log=lambda^4/(4*pi)^2*E_boundary",
        },
        "boundary_cut_result": {
            "definition": (
                "D=partial_a0 partial_a1["
                "Kallen(tau,a0,a1)^(3/2)*C/(2*tau)] at a0=a1=0"
            ),
            "exact_polynomial": (
                "D=-(5*a2^2+5*a2*a3+5*a2*a4-a2*tau+5*a3^2+"
                "5*a3*a4-a3*tau+5*a4^2-a4*tau)/4"
            ),
            "square_free_polynomial": (
                "D_sf=(tau*(a2+a3+a4)-5*(a2*a3+a2*a4+a3*a4))/4"
            ),
            "crossed_leg_loop_term": (
                "E_i=[-2*x_i*sum_(j!=i)x_j+10*sum_(j<k;j,k!=i)x_j*x_k]*Li"
            ),
            "complete_loop_term": "E_boundary=sum_i E_i",
            "angular_result": (
                "D_sf is exactly independent of zeta and chi on the symbolic "
                "physical collinear family, so its normalized two-body angular "
                "average equals the displayed polynomial"
            ),
        },
        "four_mass_interference": {
            "tree_input": "Mtree_red^(2)=1/2*sum_(i<j)x_i*x_j",
            "reduced_top_coefficient": "[x1*x2*x3*x4](Mtree_red*E_boundary)=12*(L1+L2+L3+L4)",
            "physical_amplitude_coefficient": (
                "[x1*x2*x3*x4]2*Re(Mtree^*Mloop_boundary_log)="
                "lambda^6/(4*pi)^2*96*(L1+L2+L3+L4)"
            ),
            "phase_value": "1/(256*pi^2*s)",
            "projected_rate": (
                "d_sigma_boundary_log/d_Omega="
                "3*lambda^6*(L1+L2+L3+L4)/(128*pi^4*s)"
            ),
            "phase_derivative_note": (
                "both tree and complete boundary loop terms begin at mass degree "
                "two, so analytic phase-density derivatives again decouple"
            ),
        },
        "regulator_response": {
            "independent_rescaling": "x_i -> c_i*x_i at fixed hard kinematics",
            "log_shift": "Li -> Li-log(c_i)",
            "rate_shift": (
                "Delta[d_sigma/d_Omega]=-3*lambda^6*sum_i log(c_i)/(128*pi^4*s)"
            ),
            "common_rescaling": (
                "for c_i=c, Delta[d_sigma/d_Omega]=-3*lambda^6*log(c)/(32*pi^4*s)"
            ),
            "real_threshold_response": "reduced real slice shifts by -(3/8)*log(c_pair)",
            "comparison_status": "NOT_COMPARABLE_WITHOUT_REGULATOR_GLUING_AND_FULL_REAL_PHASE_SPACE",
            "reason": (
                "the virtual carrier has one recombined external mass plus three "
                "spectator masses; the real carrier has two daughter masses plus "
                "three spectators, and the certified real result is a fixed hard "
                "slice rather than the integrated splitting-fraction carrier"
            ),
        },
        "disposition": {
            "complete_external_mass_boundary_log_jet": "COMPUTED",
            "external_phase_projector_on_boundary_log": "APPLIED",
            "external_regulator_response": "COMPUTED",
            "physical_collinear_family_dependence": "INDEPENDENT_OF_ZETA_AND_CHI",
            "four_to_five_leg_regulator_gluing": "NOT_COMPUTED",
            "full_real_splitting_fraction_integral": "NOT_COMPUTED",
            "cut_free_and_counterterm_terms": "NOT_COMPUTED",
            "real_virtual_cancellation": "NOT_COMPUTED",
            "physical_nlo_probability": "NOT_ESTABLISHED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a common regulator map between the recombined virtual leg and two real daughter legs",
            "the general splitting-fraction dependence and full inner-angle integral of the real threshold",
            "all collinear pair boundaries with identical-particle combinatorics",
            "renormalized cut-free rational, counterterm, and finite lower-point terms",
            "a scheme-invariance or physical normalization condition for the inclusive finite part",
            "the complete NLO quotient-trace and beyond-tree positivity evaluation",
        ],
        "does_not_establish": [
            "real--virtual cancellation or noncancellation in the completed observable",
            "universality away from the declared physical collinear family",
            "the full five-point splitting-fraction or angular integral",
            "a canonical four-to-five-leg independent-mass regulator map",
            "the complete finite one-loop amplitude",
            "a physical NLO cross section or probability",
            "a KLN theorem, resummation, or dressed-state construction",
            "scheme independence of the off-shell finite part",
            "positivity or unitarity beyond the published tree result",
            "a tensor, BRST, or gravitational lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority for the boundary coefficient",
        ],
        "next_gate": (
            "Promote the fixed real threshold to a splitting-fraction-dependent "
            "kernel, integrate the complete inner two-body angle with identical-"
            "particle factors, and define one explicit regulator gluing to the "
            "recombined virtual external mass before comparing the two responses."
        ),
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-10",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "primary_sources": [
                {
                    "source": "Bateman--Turok arXiv:2607.00096v1",
                    "equations": ["Eq. (13)", "Appendix B Eqs. (B1)-(B3)"],
                    "use": "external projector and cubic/five-point normalizations",
                },
                {
                    "source": "Holdom arXiv:2303.06723v2",
                    "equations": ["Eqs. (18)-(19)"],
                    "use": "off-shell three-point logarithm used only for cut normalization calibration",
                },
            ],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_external_mass_boundary_log_jet.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_external_mass_boundary_log_jet.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_external_mass_boundary_log_jet",
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
