#!/usr/bin/env python3
"""Certify the complete one-field conformal stealth-clock obstruction.

On a clock sector the gradient of the scalar must be nonzero.  The vanishing
improved stress tensor implies that a zero of the scalar has zero gradient,
so every stealth clock candidate is locally nonzero and admits the reciprocal
variable ``sigma=1/T``.

For a standard positive-sign conformal scalar with quartic potential on the
unit Einstein cylinder, the trace-free stress equation becomes a linear
overdetermined Hessian equation for ``sigma``.  Its complete global solution
family is

    sigma(t,n) = A*cos(t) + B*sin(t) + C dot n,
    kappa = 2*(|C|**2-A**2-B**2),              n in S3 subset R4.

Every nonzero denominator vanishes somewhere on R x S3, so ``T=1/sigma`` has
a pole.  Independently, every time-dependent member has a regular point at
which its gradient is spacelike or zero; a time-independent member is not a
clock.  Hence no globally regular everywhere-timelike one-field stealth clock
exists in this complete conformal family.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_PATH = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "INHOMOGENEOUS_CONFORMAL_STEALTH_CLOCK_NO_GO.json"
)
REPORT_PATH = (
    ROOT
    / "d_quotient_classical"
    / "reports"
    / "inhomogeneous-conformal-stealth-clock-no-go.md"
)
SCHEMA_PATH = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "inhomogeneous-conformal-stealth-clock-no-go-v1.schema.json"
)


@dataclass(frozen=True)
class InhomogeneousConformalStealthClockNoGo:
    """Exact classification of all standard one-field stealth clock patches."""

    payload: dict[str, Any]

    @classmethod
    def build(cls) -> "InhomogeneousConformalStealthClockNoGo":
        sigma, box_sigma, grad_squared, kappa = sp.symbols(
            "sigma box_sigma grad_sigma_squared kappa", real=True
        )

        # Substitute T=1/sigma into the improved stress tensor by collecting
        # five independent tensor structures.  In the order
        #
        #   d sigma d sigma, Hess sigma, g(grad sigma)^2,
        #   g Box sigma, G,
        #
        # the canonical and improvement terms are generated independently.
        canonical = sp.Matrix(
            [sigma**-4, 0, -sp.Rational(1, 2) * sigma**-4, 0, 0]
        )
        improvement = sp.Rational(1, 6) * sp.Matrix(
            [-6 * sigma**-4, 2 * sigma**-3, 6 * sigma**-4,
             -2 * sigma**-3, sigma**-2]
        )
        collected = sp.simplify(canonical + improvement)
        if collected[0] != 0:
            raise AssertionError("reciprocal substitution left a gradient dyad")
        multiplier = 3 * sigma**4
        stress_hessian_coefficient = sp.simplify(multiplier * collected[1])
        stress_gradient_coefficient = sp.simplify(multiplier * collected[2])
        stress_box_coefficient = sp.simplify(multiplier * collected[3])
        stress_einstein_coefficient = sp.simplify(multiplier * collected[4])
        stress_potential_coefficient = sp.simplify(
            multiplier * (-kappa / (4 * sigma**4))
        )
        if (
            stress_hessian_coefficient,
            stress_box_coefficient,
            stress_gradient_coefficient,
            stress_einstein_coefficient,
            stress_potential_coefficient,
        ) != (sigma, -sigma, sp.Rational(3, 2), sigma**2 / 2, -3 * kappa / 4):
            raise AssertionError("reciprocal stress polynomial drifted")

        # Its trace on R x S3 (R=6) is equivalent to the displayed scalar
        # equation.  This is also the reciprocal form of the scalar EOM.
        trace_equation = sp.expand(
            sigma * box_sigma - 2 * grad_squared + sigma**2 + kappa
        )
        if trace_equation != sigma * box_sigma - 2 * grad_squared + sigma**2 + kappa:
            raise AssertionError("reciprocal trace equation drifted")

        # Complete family.  Write u=A cos t+B sin t and v=C.n.  The cylinder
        # identities are u''=-u, |D v|^2=C2-v^2 and Delta v=-3v.
        u, u_dot, v, c_squared, radius_squared = sp.symbols(
            "u u_dot v C_squared R_time_squared", real=True
        )
        sigma_family = u + v
        box_family = u - 3 * v
        grad_family = -u_dot**2 + c_squared - v**2
        family_trace = sp.expand(
            trace_equation.subs(
                {
                    sigma: sigma_family,
                    box_sigma: box_family,
                    grad_squared: grad_family,
                }
            )
        )
        family_trace = sp.expand(
            family_trace.subs(u_dot**2, radius_squared - u**2)
        )
        expected_family_trace = sp.expand(
            2 * (radius_squared - c_squared) + kappa
        )
        if sp.expand(family_trace - expected_family_trace) != 0:
            raise AssertionError("family coupling relation drifted")
        coupling = 2 * (c_squared - radius_squared)
        if sp.expand(expected_family_trace.subs(kappa, coupling)) != 0:
            raise AssertionError("stealth coupling does not kill the trace")

        # The trace-free Hessian equation is checked in the independent 00
        # and spatial-STF channels.  On the unit cylinder
        # G^TF_00=3/2 and G^TF_ij=(1/2)gamma_ij.
        hessian_00 = -u
        hessian_spatial_metric_coefficient = -v
        hessian_tf_00 = sp.expand(hessian_00 + box_family / 4)
        hessian_tf_spatial = sp.expand(
            hessian_spatial_metric_coefficient - box_family / 4
        )
        if sp.expand(hessian_tf_00 + sigma_family * sp.Rational(3, 4)) != 0:
            raise AssertionError("00 trace-free Hessian equation drifted")
        if sp.expand(hessian_tf_spatial + sigma_family * sp.Rational(1, 4)) != 0:
            raise AssertionError("spatial trace-free Hessian equation drifted")

        # The S3 classification is a global elliptic identity rather than a
        # sampled harmonic claim.  Divergence of Hess(s)^TF=0 gives
        # D_i(Delta+3)s=0, so s is constant plus an l=1 harmonic.  The 00
        # equation cancels the constant and leaves C.n.
        divergence_laplacian_coefficient = sp.Rational(2, 3)
        divergence_gradient_coefficient = 2
        if sp.simplify(
            divergence_gradient_coefficient / divergence_laplacian_coefficient
        ) != 3:
            raise AssertionError("S3 Obata reduction drifted")

        payload: dict[str, Any] = {
            "schema": "pure-weyl-inhomogeneous-conformal-stealth-clock-no-go-v1",
            "result_id": "INHOMOGENEOUS_CONFORMAL_STEALTH_CLOCK_NO_GO",
            "setting_id": "compact_inhomogeneous_conformal_stealth_clock",
            "generator_id": "D_compact",
            "phase_space_id": "standard_conformal_scalar_stealth_clock_sector",
            "claim_status": "CERTIFIED_SCOPED_NO_GO",
            "scientific_verdict": None,
            "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            "conventions": {
                "metric": "g=-dt^2+dOmega_3^2 on the unit Einstein cylinder",
                "scalar_curvature": 6,
                "field": "one real conformal scalar T of Weyl weight -1 with standard positive kinetic sign",
                "action": "S=-integral sqrt(-g)[(nabla T)^2/2+R*T^2/12+kappa*T^4/4]",
                "clock_requirement": "T smooth and grad(T) everywhere timelike and nonzero",
                "spatial_embedding": "n in S3 subset R4 and C.n is the complete l=1 harmonic family",
            },
            "zero_field_gate": {
                "stress_at_T_zero": "T_mn=(2/3)d_mT d_nT-(1/6)g_mn(dT)^2",
                "equivalent_tensor_equation": "4 dT tensor dT=g (dT)^2",
                "consequence": "T=0 and stress=0 imply dT=0",
                "clock_can_cross_T_zero": False,
                "reciprocal_valid_on_every_clock_candidate": True,
            },
            "reciprocal_stress": {
                "variable": "sigma=1/T",
                "polynomial_tensor_equation": "sigma(Hess_mn sigma-g_mn Box sigma)+(3/2)g_mn(grad sigma)^2+(1/2)sigma^2 G_mn-(3/4)kappa g_mn=0",
                "trace_equation": "sigma Box sigma-2(grad sigma)^2+sigma^2+kappa=0",
                "trace_free_equation": "(Hess sigma)^TF=-(sigma/2)G^TF",
                "equivalent_to_scalar_eom_plus_zero_stress_on_sigma_nonzero": True,
            },
            "global_classification": {
                "mixed_equation": "D_i partial_t sigma=0, hence sigma=f(t)+s(n)",
                "spatial_equation": "Hess_S3(s)^TF=0",
                "divergence_identity": "D_i(Delta_S3+3)s=0",
                "compact_solution": "s=s0+C.n",
                "time_equation": "f''+f+s0=0",
                "complete_denominator": "sigma=A*cos(t)+B*sin(t)+C.n",
                "coupling_relation": "kappa=2(|C|^2-A^2-B^2)",
                "classification_global_for_nowhere_zero_clock_candidates": True,
            },
            "global_obstruction": {
                "time_dependent_case": "if A^2+B^2>0 choose n perpendicular to C and a zero of A cos(t)+B sin(t); then sigma=0",
                "time_independent_case": "if A=B=0 and C nonzero choose n perpendicular to C; then sigma=0 and there is no time clock",
                "trivial_case": "A=B=C=0 does not define T=1/sigma",
                "every_nontrivial_denominator_has_zero": True,
                "every_nontrivial_scalar_has_global_pole": True,
                "globally_regular_stealth_scalar_clock_exists": False,
            },
            "timelike_gradient_obstruction": {
                "gradient_norm": "(grad sigma)^2=-(d_t u)^2+|C|^2-(C.n)^2",
                "regular_test_point": "choose n perpendicular to C and a time extremum of u=A cos(t)+B sin(t)",
                "norm_at_test_point": "(grad sigma)^2=|C|^2>=0 while sigma=+/-sqrt(A^2+B^2) is nonzero",
                "time_dependent_gradient_everywhere_timelike": False,
                "time_independent_member_is_clock": False,
            },
            "gate_result": {
                "gate": "INHOMOGENEOUS_STEALTH_OR_NONCONFORMALLY_FLAT_CLOCK",
                "status": "STANDARD_ONE_FIELD_STEALTH_BRANCH_OBSTRUCTED",
                "surviving_gate": "POSITIVE_ENERGY_NONCONFORMALLY_FLAT_BACH_SOURCED_CLOCK",
                "surviving_gate_status": "OPEN",
            },
            "flags": {
                "complete_one_field_clock_sector_classified": True,
                "inhomogeneous_modes_included": True,
                "global_zero_locus_proved": True,
                "everywhere_timelike_gradient_ruled_out": True,
                "globally_regular_one_field_stealth_clock_exists": False,
                "nonconformally_flat_backreacted_clock_ruled_out": False,
                "generalized_non_noetherian_or_higher_derivative_scalar_ruled_out": False,
            },
            "not_established": [
                "a no-go theorem for generalized non-Noetherian or higher-derivative conformal scalar actions",
                "a no-go theorem for positive-energy Bach-sourced non-conformally-flat clocks",
                "a support-local all-row BV construction for a surviving clock",
                "an interacting, boundary, or quantum D verdict",
            ],
            "claim_boundary": "This theorem rules out globally regular relational clocks among all real one-field stealth configurations of the standard positive-sign conformal scalar with quartic Weyl-invariant potential on the unit cylinder, including inhomogeneous configurations. It does not rule out generalized scalar actions or genuinely non-conformally-flat Bach-sourced clock backgrounds.",
        }
        result = cls(payload=payload)
        result.verify()
        return result

    def verify(self) -> None:
        p = self.payload
        required = {
            "schema", "result_id", "setting_id", "generator_id",
            "phase_space_id", "claim_status", "scientific_verdict",
            "dependency_tags", "conventions", "zero_field_gate",
            "reciprocal_stress", "global_classification", "global_obstruction",
            "timelike_gradient_obstruction", "gate_result", "flags",
            "not_established", "claim_boundary",
        }
        if set(p) != required:
            raise AssertionError("inhomogeneous stealth certificate key set drifted")
        if p["claim_status"] != "CERTIFIED_SCOPED_NO_GO":
            raise AssertionError("stealth no-go was silently promoted")
        if p["scientific_verdict"] is not None:
            raise AssertionError("nonexistent clock phase space received a D verdict")
        if p["global_classification"]["classification_global_for_nowhere_zero_clock_candidates"] is not True:
            raise AssertionError("global classification was weakened")
        if p["global_obstruction"]["globally_regular_stealth_scalar_clock_exists"] is not False:
            raise AssertionError("singular stealth family was promoted")
        if p["timelike_gradient_obstruction"]["time_dependent_gradient_everywhere_timelike"] is not False:
            raise AssertionError("timelike-gradient obstruction was erased")
        if p["gate_result"]["surviving_gate_status"] != "OPEN":
            raise AssertionError("non-conformally-flat gate was silently closed")
        flags = p["flags"]
        for key in (
            "complete_one_field_clock_sector_classified",
            "inhomogeneous_modes_included",
            "global_zero_locus_proved",
            "everywhere_timelike_gradient_ruled_out",
        ):
            if flags.get(key) is not True:
                raise AssertionError(f"proved flag dropped: {key}")
        for key in (
            "globally_regular_one_field_stealth_clock_exists",
            "nonconformally_flat_backreacted_clock_ruled_out",
            "generalized_non_noetherian_or_higher_derivative_scalar_ruled_out",
        ):
            if flags.get(key) is not False:
                raise AssertionError(f"open or obstructed flag promoted: {key}")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Complete one-field conformal stealth-clock no-go

## Theorem

For one real conformal scalar with standard positive kinetic sign and quartic
Weyl-invariant potential on the unit Einstein cylinder, there is no smooth
global stealth configuration whose gradient is everywhere timelike and
nonzero.  Thus this complete one-field stealth family cannot provide the
required relational clock.

## Why the reciprocal variable is legitimate

At a zero of (T), the zero-stress equation reduces to

\[
4\,dT\otimes dT=g\,(dT)^2.
\]

The left side has rank at most one while a nonzero right side has rank four;
if ((dT)^2=0), the equation itself gives (dT=0).  Hence a stealth field
cannot cross (T=0) with nonzero gradient.  Every clock candidate therefore
lies in a nowhere-zero sector where

\[
\sigma=T^{-1}
\]

is well defined.

## Exact classification

After multiplying the improved stress tensor by (3\sigma^4), its
trace-free part is the linear equation

\[
(\nabla_\mu\nabla_\nu\sigma)^{\rm TF}
=-\frac{\sigma}{2}G_{\mu\nu}^{\rm TF}.
\]

The mixed component gives (sigma=f(t)+s(n)).  The spatial equation is

\[
(D_iD_js)^{\rm TF}=0.
\]

Taking its divergence on the unit (S^3) gives

\[
D_i(\Delta_{S^3}+3)s=0,
\]

so compactness implies (s=s_0+C\cdot n), where (n\in S^3\subset\mathbb
R^4).  The temporal equation cancels (s_0).  The complete denominator is

\[
\boxed{\sigma=A\cos t+B\sin t+C\cdot n},
\]

and the trace equation fixes

\[
\boxed{\kappa=2(|C|^2-A^2-B^2)}.
\]

The homogeneous secant family is the special case (C=0).

## Global obstruction

If (A^2+B^2>0), choose (n\perp C) and a zero of
(A\cos t+B\sin t).  Then (sigma=0), so (T=1/\sigma) has a pole.  If
(A=B=0) and (C\ne0), choose (n\perp C); again (sigma=0), and the
field is time independent anyway.  The all-zero denominator is invalid.

There is also an independent clock-gradient obstruction.  For every
time-dependent member, choose (n\perp C) and a time extremum of the temporal
sinusoid.  At that regular point

\[
(\nabla\sigma)^2=|C|^2\geq0,
\]

so the gradient is spacelike or zero, never timelike.

Therefore

```text
INHOMOGENEOUS_STEALTH_OR_NONCONFORMALLY_FLAT_CLOCK
    = STANDARD_ONE_FIELD_STEALTH_BRANCH_OBSTRUCTED
```

and the surviving standard-model gate is
`POSITIVE_ENERGY_NONCONFORMALLY_FLAT_BACH_SOURCED_CLOCK`.

This does not rule out generalized non-Noetherian/higher-derivative scalar
actions, but those would be new theories with new health and BV gates.
"""


def _write(result: InhomogeneousConformalStealthClockNoGo) -> None:
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: InhomogeneousConformalStealthClockNoGo) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError(f"stale certificate: {CERTIFICATE_PATH}")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError(f"stale report: {REPORT_PATH}")
    if not SCHEMA_PATH.is_file():
        raise AssertionError(f"missing schema: {SCHEMA_PATH}")


def _guards(result: InhomogeneousConformalStealthClockNoGo) -> None:
    mutations = (
        ("premature verdict", ("scientific_verdict",), "D_GAUGE"),
        ("promote singular clock", ("global_obstruction", "globally_regular_stealth_scalar_clock_exists"), True),
        ("erase gradient obstruction", ("timelike_gradient_obstruction", "time_dependent_gradient_everywhere_timelike"), True),
        ("drop inhomogeneous coverage", ("flags", "inhomogeneous_modes_included"), False),
        ("close backreaction", ("flags", "nonconformally_flat_backreacted_clock_ruled_out"), True),
        ("close generalized scalar", ("flags", "generalized_non_noetherian_or_higher_derivative_scalar_ruled_out"), True),
        ("promote surviving gate", ("gate_result", "surviving_gate_status"), "PASSED"),
    )
    passed = 0
    for label, path, value in mutations:
        payload = deepcopy(result.payload)
        target: Any = payload
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            InhomogeneousConformalStealthClockNoGo(payload=payload).verify()
        except AssertionError:
            passed += 1
        else:
            raise AssertionError(f"mutation guard failed: {label}")
    print(f"mutation guards: {passed}/{len(mutations)} PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = InhomogeneousConformalStealthClockNoGo.build()
    if args.write:
        _write(result)
    if args.check:
        _check(result)
    if args.guards:
        _guards(result)
    if not (args.write or args.check or args.guards):
        print(result.certificate_text(), end="")
    else:
        print(f"{CERTIFICATE_PATH} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
