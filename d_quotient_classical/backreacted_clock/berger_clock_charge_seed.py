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
        q, a, alpha_b, volume_0 = sp.symbols(
            "q a alpha_B V_0", positive=True, real=True
        )
        rho_squared = 2 * alpha_b * (1 - 4 * q) / a**2
        omega_squared = q / (4 * a**2 * (1 - 4 * q))
        omega = sp.sqrt(omega_squared)
        volume = volume_0 * a**3 * sp.sqrt(q)

        charge_density = sp.factor(sp.powdenest(rho_squared * omega, force=True))
        charge = sp.factor(sp.powdenest(volume * charge_density, force=True))
        expected_density = alpha_b * sp.sqrt(q * (1 - 4 * q)) / a**3
        expected_charge = volume_0 * alpha_b * q * sp.sqrt(1 - 4 * q)
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

        fixture = {
            q: sp.Rational(9, 40),
            a: 1,
            alpha_b: 5,
            volume_0: 1,
        }
        fixture_charge_density = sp.simplify(charge_density.subs(fixture))
        fixture_charge = sp.simplify(charge.subs(fixture))
        fixture_energy_density = sp.simplify(energy_density.subs(fixture))
        fixture_energy = sp.simplify(energy.subs(fixture))
        if fixture_charge_density != sp.Rational(3, 4):
            raise AssertionError("fixture charge density drifted")
        if fixture_charge != 9 * sp.sqrt(10) / 80:
            raise AssertionError("fixture integrated charge drifted")
        if fixture_energy_density != sp.Rational(961, 1920):
            raise AssertionError("fixture energy density drifted")
        if fixture_energy != 961 * sp.sqrt(10) / 12800:
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
                "spatial_volume": "Vol(S3_Berger)=V_0 a^3 sqrt(q)",
                "future_charge_density": "n_mu j^mu=T_1 dot(T_2)-T_2 dot(T_1)",
                "internal_rotation": "R(T_1,T_2)=(-T_2,T_1)",
            },
            "exact_identities": {
                "helical_action": "L_D(T_1,T_2)=omega R(T_1,T_2)",
                "current_density": "j_R=rho^2 omega",
                "current_conservation": "partial_t j_R=0",
                "integrated_charge": "Q_R=V_0 alpha_B q sqrt(1-4q)",
                "matter_energy_density": "epsilon=alpha_B(1-q)^2/(6a^4)",
                "integrated_matter_energy": "E_m=V_0 alpha_B sqrt(q)(1-q)^2/(6a)",
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
                "V_0": "1",
                "charge_density": "3/4",
                "integrated_charge": "9 sqrt(10)/80",
                "matter_energy_density": "961/1920",
                "integrated_matter_energy": "961 sqrt(10)/12800",
            },
            "flags": {
                "global_internal_charge_computed": True,
                "helical_D_internal_relation_computed": True,
                "total_covariant_D_charge_computed": False,
                "gravitational_and_matter_presymplectic_currents_combined": False,
                "support_local_all_row_bv_retract_constructed": False,
            },
            "next_gate": "TOTAL_BERGER_D_PRESYMPLECTIC_AUDIT",
            "not_established": [
                "whether gravitational and matter contributions make total D gauge, charged, sector-dependent, or non-Hamiltonian",
                "the full linearized solution and allowed-variation space at fixed theory couplings",
                "the all-row support-local BV contraction and causal Green homotopy",
            ],
            "claim_boundary": "The certificate proves a nonzero conserved internal clock momentum and the exact helical relation between D and O(2) rotation on the Berger background. It does not equate Q_R with the total D charge and assigns no D verdict.",
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        p = self.payload
        required = {
            "schema", "result_id", "setting_id", "phase_space_id",
            "claim_status", "scientific_verdict", "dependency_tags",
            "conventions", "exact_identities", "clock_interpretation",
            "rational_fixture", "flags", "next_gate", "not_established",
            "claim_boundary",
        }
        if set(p) != required:
            raise AssertionError("Berger charge-seed key set drifted")
        if p["scientific_verdict"] is not None:
            raise AssertionError("reduced clock momentum was promoted to a D verdict")
        if p["clock_interpretation"]["charge_nonzero_on_open_interval"] is not True:
            raise AssertionError("nonzero clock momentum was erased")
        flags = p["flags"]
        for key in (
            "global_internal_charge_computed",
            "helical_D_internal_relation_computed",
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

Writing the Berger volume as

\[
\operatorname{Vol}(S^3_{\rm Berger})=V_0a^3\sqrt q,
\]

the exact background relations give

\[
Q_R=V_0\alpha_Bq\sqrt{1-4q}>0.
\]

Thus the phase is canonically paired with genuine conserved matter momentum;
it is not a cost-free scalar gauge marker.  This makes it a plausible
physical clock.

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
