#!/usr/bin/env python3
"""Certify the conserved clock momentum on the positive Berger background.

This is the first, deliberately scoped, part of the full covariant charge
audit.  The rotating scalar pair has a global O(2) symmetry.  Its phase is
canonically conjugate to a nonzero conserved charge, and cylinder time
translation agrees on the background with omega times that internal
rotation.  The calculation proves that the clock has genuine matter momentum;
it does not identify the total gravitational-plus-matter D charge.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_PATH = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "BERGER_CLOCK_REDUCED_CHARGE_SEED.json"
)
REPORT_PATH = (
    ROOT
    / "d_quotient_classical"
    / "reports"
    / "berger-clock-reduced-charge-seed.md"
)
SCHEMA_PATH = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "berger-clock-reduced-charge-seed-v1.schema.json"
)


class BergerClockChargeSeed:
    """Exact homogeneous current and helical-symmetry certificate."""

    def __init__(self, payload: dict[str, Any]):
        self.payload = payload

    @classmethod
    def build(cls) -> "BergerClockChargeSeed":
        q, a, alpha_b, quartic = sp.symbols(
            "q a alpha_B lambda", positive=True, real=True
        )
        rho_squared = 2 * alpha_b * (1 - 4 * q) / a**2
        omega_squared = q / (4 * a**2 * (1 - 4 * q))
        omega = sp.sqrt(omega_squared)
        # The Maurer--Cartan normalization used by the Berger producer has
        # [e_i,e_j]=epsilon_ij^k e_k at a=c=1.  The corresponding SU(2)
        # Euler-angle volume is V_0=16 pi^2 (round radius two).
        volume_0 = 16 * sp.pi**2
        volume = volume_0 * a**3 * sp.sqrt(q)

        charge_density = sp.factor(sp.powdenest(rho_squared * omega, force=True))
        charge = sp.factor(sp.powdenest(volume * charge_density, force=True))
        expected_density = alpha_b * sp.sqrt(q * (1 - 4 * q)) / a**3
        expected_charge = 16 * sp.pi**2 * alpha_b * q * sp.sqrt(1 - 4 * q)
        if sp.simplify(charge_density - expected_density) != 0:
            raise AssertionError("clock charge density drifted")
        if sp.simplify(charge - expected_charge) != 0:
            raise AssertionError("integrated clock charge drifted")

        energy_density = sp.factor(alpha_b * (1 - q) ** 2 / (6 * a**4))
        energy = sp.factor(volume * energy_density)

        rho, angular_frequency, time = sp.symbols(
            "rho omega t", positive=True, real=True
        )
        fields = sp.Matrix(
            [rho * sp.cos(angular_frequency * time),
             rho * sp.sin(angular_frequency * time)]
        )
        internal_rotation = sp.Matrix([-fields[1], fields[0]])
        helical_defect = sp.simplify(
            sp.diff(fields, time) - angular_frequency * internal_rotation
        )
        if helical_defect != sp.zeros(2, 1):
            raise AssertionError("helical D/O(2) identity drifted")
        wronskian = sp.trigsimp(
            fields[0] * sp.diff(fields[1], time)
            - fields[1] * sp.diff(fields[0], time)
        )
        if sp.simplify(wronskian - rho**2 * angular_frequency) != 0:
            raise AssertionError("O(2) current drifted")
        if sp.diff(wronskian, time) != 0:
            raise AssertionError("O(2) current is not conserved")

        # Derive the current and its presymplectic contraction from the
        # covariant scalar action.  The conformal coupling depends only on
        # rho^2=T_1^2+T_2^2, whose O(2) variation vanishes, so its metric
        # improvement potential gives no cross term against R.
        field_1, field_2, velocity_1, velocity_2 = sp.symbols(
            "T_1 T_2 v_1 v_2", real=True
        )
        dfield_1, dfield_2, dvelocity_1, dvelocity_2 = sp.symbols(
            "dT_1 dT_2 dv_1 dv_2", real=True
        )
        volume_symbol, dvolume = sp.symbols("V dV", real=True)
        rotation_field = sp.Matrix([-field_2, field_1])
        rotation_velocity = sp.Matrix([-velocity_2, velocity_1])
        invariant_radius_defect = sp.expand(
            2 * field_1 * rotation_field[0]
            + 2 * field_2 * rotation_field[1]
        )
        if invariant_radius_defect != 0:
            raise AssertionError("O(2) invariance of rho^2 drifted")
        charge_polynomial = field_1 * velocity_2 - field_2 * velocity_1
        charge_variation = sp.expand(
            dvolume * charge_polynomial
            + volume_symbol
            * (
                dfield_1 * velocity_2
                + field_1 * dvelocity_2
                - dfield_2 * velocity_1
                - field_2 * dvelocity_1
            )
        )
        # Omega=delta p_A wedge delta T_A with p_A=V v_A, evaluated as
        # Omega(delta,R).  Keeping dV proves the identity also for metric
        # variations that change the Cauchy volume.
        presymplectic_contraction = sp.expand(
            (volume_symbol * dvelocity_1 + velocity_1 * dvolume)
            * rotation_field[0]
            + (volume_symbol * dvelocity_2 + velocity_2 * dvolume)
            * rotation_field[1]
            - volume_symbol * rotation_velocity[0] * dfield_1
            - volume_symbol * rotation_velocity[1] * dfield_2
        )
        if sp.expand(presymplectic_contraction - charge_variation) != 0:
            raise AssertionError("scalar presymplectic/O(2)-charge identity drifted")

        # At fixed theory couplings z=alpha_B lambda, q is isolated.  The
        # open q interval classifies theories/backgrounds; it is not a
        # one-theory tangent direction.
        coupling_product = alpha_b * quartic
        fixed_coupling_equation = sp.expand(
            q**2 - 5 * q + 1
            + 6 * coupling_product * (1 - 4 * q) ** 2
        )
        coupling_solution = -(q**2 - 5 * q + 1) / (6 * (1 - 4 * q) ** 2)
        fixed_coupling_derivative = sp.factor(
            sp.diff(fixed_coupling_equation, q).subs(
                coupling_product, coupling_solution
            )
        )
        expected_derivative = 3 * (6 * q - 1) / (4 * q - 1)
        if sp.simplify(fixed_coupling_derivative - expected_derivative) != 0:
            raise AssertionError("fixed-coupling q derivative drifted")

        fixture = {
            q: sp.Rational(9, 40),
            a: 1,
            alpha_b: 5,
        }
        fixture_charge_density = sp.simplify(charge_density.subs(fixture))
        fixture_charge = sp.simplify(charge.subs(fixture))
        fixture_energy_density = sp.simplify(energy_density.subs(fixture))
        fixture_energy = sp.simplify(energy.subs(fixture))
        if fixture_charge_density != sp.Rational(3, 4):
            raise AssertionError("fixture charge density drifted")
        if fixture_charge != 9 * sp.pi**2 * sp.sqrt(10) / 5:
            raise AssertionError("fixture integrated charge drifted")
        if fixture_energy_density != sp.Rational(961, 1920):
            raise AssertionError("fixture energy density drifted")
        if fixture_energy != 961 * sp.pi**2 * sp.sqrt(10) / 800:
            raise AssertionError("fixture integrated energy drifted")

        payload: dict[str, Any] = {
            "schema": "pure-weyl-berger-clock-reduced-charge-seed-v1",
            "result_id": "BERGER_CLOCK_REDUCED_CHARGE_SEED",
            "setting_id": "compact_positive_berger_clock",
            "phase_space_id": "positive_rotating_scalar_berger_background",
            "claim_status": "CERTIFIED_REDUCED_CHARGE_SEED",
            "scientific_verdict": None,
            "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            "conventions": {
                "metric_signature": "(-,+,+,+)",
                "authoritative_matter_action": "S_m=int sqrt(-g){-(1/2) sum_A nabla T_A.nabla T_A -(R/12) rho^2 -(lambda/4) rho^4}",
                "spatial_volume": "Vol(S3_Berger)=16 pi^2 a^3 sqrt(q)",
                "maurer_cartan_volume": "V_0=int sigma_1 wedge sigma_2 wedge sigma_3=16 pi^2",
                "future_charge_density": "n_mu j^mu=T_1 dot(T_2)-T_2 dot(T_1)",
                "internal_rotation": "R(T_1,T_2)=(-T_2,T_1)",
                "scalar_presymplectic_convention": "Omega_Sigma=sum_A int delta(sqrt(h) n.nabla T_A) wedge delta T_A",
            },
            "exact_identities": {
                "helical_action": "L_D(T_1,T_2)=omega R(T_1,T_2)",
                "current_density": "j_R=rho^2 omega",
                "current_conservation": "partial_t j_R=0",
                "integrated_charge": "Q_R=16 pi^2 alpha_B q sqrt(1-4q)",
                "matter_energy_density": "epsilon=alpha_B(1-q)^2/(6a^4)",
                "integrated_matter_energy": "E_m=(8 pi^2/3) alpha_B sqrt(q)(1-q)^2/a",
            },
            "fixed_coupling_audit": {
                "coupling_equation": "q^2-5q+1+6(alpha_B lambda)(1-4q)^2=0",
                "on_shell_q_derivative": "3(6q-1)/(4q-1)",
                "derivative_nonzero_on_interval": True,
                "stationary_fixed_coupling_consequence": "delta q=0",
                "scale_direction": "a is the common Weyl scale; Q_R is independent of a",
                "warning": "The open q interval is a family across coupling products alpha_B lambda, not a physical tangent inside one fixed theory.",
            },
            "covariant_current_audit": {
                "scalar_potential": "theta_m^mu(delta T)=-sum_A nabla^mu T_A delta T_A plus the metric-only conformal-improvement potential",
                "internal_current": "j_R^mu=T_1 nabla^mu T_2-T_2 nabla^mu T_1 up to the declared future-density orientation",
                "improvement_cross_term": "ZERO because delta_R g=0 and delta_R(T_1^2+T_2^2)=0",
                "presymplectic_identity": "Omega_m(delta,R)=delta Q_R",
                "derived_from_action": True,
            },
            "helical_presymplectic_audit": {
                "background_metric_action": "L_D g=0",
                "background_scalar_action": "L_D T=omega R T",
                "pure_weyl_cross_term": "Omega_W(delta,L_D g)=0",
                "identity": "Omega_total(delta,L_D)=omega delta Q_R for every allowed linearized tangent delta at the background",
                "decision_rule": "D is non-null iff the fixed-coupling allowed tangent space contains a delta with delta Q_R nonzero.",
                "allowed_delta_Q_tangent_constructed": False,
            },
            "clock_interpretation": {
                "phase": "theta=omega t mod 2pi",
                "canonical_phase_momentum": "p_theta=Q_R",
                "charge_nonzero_on_open_interval": True,
                "standard_sign_target": True,
                "interpretation": "The rotating phase carries a nonzero conserved global O(2) momentum and is therefore a genuine matter clock candidate, not a cost-free scalar gauge label.",
            },
            "rational_fixture": {
                "q": "9/40",
                "a": "1",
                "alpha_B": "5",
                "V_0": "16 pi^2",
                "charge_density": "3/4",
                "integrated_charge": "9 pi^2 sqrt(10)/5",
                "matter_energy_density": "961/1920",
                "integrated_matter_energy": "961 pi^2 sqrt(10)/800",
            },
            "flags": {
                "global_internal_charge_computed": True,
                "helical_D_internal_relation_computed": True,
                "fixed_coupling_tangent_audited": True,
                "covariant_internal_current_derived": True,
                "helical_presymplectic_identity_derived": True,
                "total_covariant_D_charge_computed": False,
                "gravitational_and_matter_presymplectic_currents_combined": False,
                "support_local_all_row_bv_retract_constructed": False,
            },
            "next_gate": "TOTAL_BERGER_D_PRESYMPLECTIC_AUDIT",
            "not_established": [
                "whether gravitational and matter contributions make total D gauge, charged, sector-dependent, or non-Hamiltonian",
                "the full linearized solution and allowed-variation space at fixed theory couplings",
                "existence or absence of a fixed-coupling allowed tangent with delta Q_R nonzero",
                "the all-row support-local BV contraction and causal Green homotopy",
            ],
            "claim_boundary": "The certificate derives the covariant internal current, fixes the SU(2) volume, proves the nonzero clock momentum, audits the fixed-coupling stationary family, and derives Omega_total(delta,L_D)=omega delta Q_R on the Berger background. It does not establish whether an allowed fixed-coupling linearized tangent has delta Q_R nonzero, so it assigns no total D verdict.",
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        p = self.payload
        required = {
            "schema", "result_id", "setting_id", "phase_space_id",
            "claim_status", "scientific_verdict", "dependency_tags",
            "conventions", "exact_identities", "fixed_coupling_audit",
            "covariant_current_audit", "helical_presymplectic_audit",
            "clock_interpretation",
            "rational_fixture", "flags", "next_gate", "not_established",
            "claim_boundary",
        }
        if set(p) != required:
            raise AssertionError("Berger charge-seed key set drifted")
        if p["scientific_verdict"] is not None:
            raise AssertionError("reduced clock momentum was promoted to a D verdict")
        if p["clock_interpretation"]["charge_nonzero_on_open_interval"] is not True:
            raise AssertionError("nonzero clock momentum was erased")
        if p["helical_presymplectic_audit"]["allowed_delta_Q_tangent_constructed"] is not False:
            raise AssertionError("fixed-coupling delta-Q tangent was silently promoted")
        flags = p["flags"]
        for key in (
            "global_internal_charge_computed",
            "helical_D_internal_relation_computed",
            "fixed_coupling_tangent_audited",
            "covariant_internal_current_derived",
            "helical_presymplectic_identity_derived",
        ):
            if flags.get(key) is not True:
                raise AssertionError(f"proved charge-seed flag dropped: {key}")
        for key in (
            "total_covariant_D_charge_computed",
            "gravitational_and_matter_presymplectic_currents_combined",
            "support_local_all_row_bv_retract_constructed",
        ):
            if flags.get(key) is not False:
                raise AssertionError(f"open charge flag promoted: {key}")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Berger clock reduced charge seed

The positive Berger background carries a nonzero conserved matter clock
momentum.  If \(R(T_1,T_2)=(-T_2,T_1)\), then

\[
\mathcal L_D(T_1,T_2)=\omega R(T_1,T_2),
\]

and the standard-sign scalar \(O(2)\) current has future charge density

\[
j_R=T_1\dot T_2-T_2\dot T_1=\rho^2\omega>0.
\]

The Maurer--Cartan normalization fixes the Berger volume to

\[
\operatorname{Vol}(S^3_{\rm Berger})=16\pi^2a^3\sqrt q,
\]

and the exact background relations give

\[
Q_R=16\pi^2\alpha_Bq\sqrt{1-4q}>0.
\]

Thus the phase is canonically paired with genuine conserved matter momentum;
it is not a cost-free scalar gauge marker.  This makes it a plausible
physical clock.

## Fixed-coupling warning

The background relation at fixed theory couplings is

\[
q^2-5q+1+6(\alpha_B\lambda)(1-4q)^2=0.
\]

Its on-shell derivative is

\[
\frac{3(6q-1)}{4q-1}\ne0
\]

throughout the certified interval. Hence \(\delta q=0\) inside the
stationary fixed-coupling family. The open \(q\)-interval classifies a family
of theories/backgrounds; it is not a tangent direction of one fixed theory.

## Covariant current and helical identity

Direct variation of the conformal-scalar action gives

\[
\Omega_{\rm m}(\delta,R)=\delta Q_R.
\]

The curvature-improvement cross term vanishes because
\(\delta_Rg=0\) and \(\delta_R(T_1^2+T_2^2)=0\). Since the Berger metric is
stationary while \(\mathcal L_DT=\omega RT\), the full current obeys

\[
\boxed{\Omega_{\rm total}(\delta,\mathcal L_D)=\omega\,\delta Q_R.}
\]

The remaining question is therefore precise: does the allowed fixed-coupling
linearized solution space contain a tangent with \(\delta Q_R\ne0\)?

The result is not yet the total \(D\)-charge theorem.  The next gate,

```text
TOTAL_BERGER_D_PRESYMPLECTIC_AUDIT
```

must combine the pure-Weyl and improved scalar presymplectic currents on the
complete fixed-coupling linearized solution space.  Only that calculation can
classify total \(D\) as gauge, charged, sector-dependent, or non-Hamiltonian.
"""


def _write(result: BergerClockChargeSeed) -> None:
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: BergerClockChargeSeed) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError(f"stale certificate: {CERTIFICATE_PATH}")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError(f"stale report: {REPORT_PATH}")
    if not SCHEMA_PATH.is_file():
        raise AssertionError(f"missing schema: {SCHEMA_PATH}")


def _guards(result: BergerClockChargeSeed) -> None:
    mutations = (
        ("premature D verdict", ("scientific_verdict",), "D_CHARGED"),
        ("erase clock charge", ("clock_interpretation", "charge_nonzero_on_open_interval"), False),
        ("erase current", ("flags", "global_internal_charge_computed"), False),
        ("erase helical relation", ("flags", "helical_D_internal_relation_computed"), False),
        ("erase fixed-coupling audit", ("flags", "fixed_coupling_tangent_audited"), False),
        ("erase covariant current", ("flags", "covariant_internal_current_derived"), False),
        ("erase helical current identity", ("flags", "helical_presymplectic_identity_derived"), False),
        ("promote delta-Q tangent", ("helical_presymplectic_audit", "allowed_delta_Q_tangent_constructed"), True),
        ("promote total charge", ("flags", "total_covariant_D_charge_computed"), True),
        ("promote current comparison", ("flags", "gravitational_and_matter_presymplectic_currents_combined"), True),
        ("promote BV", ("flags", "support_local_all_row_bv_retract_constructed"), True),
    )
    passed = 0
    for label, path, value in mutations:
        payload = deepcopy(result.payload)
        target: Any = payload
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            BergerClockChargeSeed(payload).verify()
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
    result = BergerClockChargeSeed.build()
    if args.write:
        _write(result)
    if args.check:
        _check(result)
    if args.guards:
        _guards(result)
    if not (args.write or args.check or args.guards):
        print(result.report_text())
    if args.write or args.check:
        print(CERTIFICATE_PATH, "PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
