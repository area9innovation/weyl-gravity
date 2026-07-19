#!/usr/bin/env python3
"""Certify rational interval enclosures of exact finite Berger sine kernels."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_recoil_interval_stream import (
    RationalInterval,
    enclose_exact_mode_sine_kernel,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_FINITE_MODE_KERNEL_INTERVAL_ENCLOSURE.json"
SCHEMA = PACKAGE / "schema/berger-recoil-finite-mode-kernel-interval-enclosure-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-finite-mode-kernel-interval-enclosure.md"
DEPENDENCIES = {
    "exact_payload": PACKAGE / "certificates/BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD.json",
    "convolution": PACKAGE / "certificates/BERGER_RECOIL_FINITE_NESTED_TIME_CONVOLUTION.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "berger_recoil_interval_stream.py",
    PACKAGE / "verify_berger_recoil_finite_mode_kernel_interval_enclosure.py",
    PACKAGE / "tests/test_berger_recoil_finite_mode_kernel_interval_enclosure.py",
    SCHEMA,
    REPORT,
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mutation_detected(payload: dict[str, Any], **updates: Any) -> bool:
    arguments: dict[str, Any] = {
        "two_j": 0,
        "family": "massive_two_form",
        "form_degree": 1,
        "mass_squared_interval": RationalInterval(Fraction(1), Fraction(2)),
        "slab_length": Fraction(1, 48),
    }
    arguments.update(updates)
    try:
        enclose_exact_mode_sine_kernel(payload, **arguments)
    except ValueError:
        return True
    return False


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    exact_payload = values["exact_payload"]
    if exact_payload["flags"]["EXACT_SINE_KERNEL_SERIES_COEFFICIENTS_EXPORTED"] is not True:
        raise AssertionError("exact mode-kernel payload dependency dropped")
    if values["convolution"]["flags"]["FINITE_POLYNOMIAL_NESTED_TIME_CONVOLUTION_EXPORTED"] is not True:
        raise AssertionError("finite convolution dependency dropped")

    maxwell_zero = enclose_exact_mode_sine_kernel(
        exact_payload,
        two_j=0,
        family="Maxwell",
        form_degree=0,
        mass_squared_interval=RationalInterval.point(0),
        slab_length=Fraction(1, 16),
    )
    massive_fixture = enclose_exact_mode_sine_kernel(
        exact_payload,
        two_j=0,
        family="massive_two_form",
        form_degree=1,
        mass_squared_interval=RationalInterval(Fraction(1), Fraction(2)),
        slab_length=Fraction(1, 48),
    )
    if maxwell_zero["uniform_sine_kernel_remainder_upper"] != "0":
        raise AssertionError("Maxwell zero-mode tail must vanish exactly")
    if maxwell_zero["coefficient_matrices"][0]["entries"][0]["real"]["lower"] != "1":
        raise AssertionError("Maxwell zero-mode identity coefficient drifted")
    if massive_fixture["operator_row_sum_norm_upper"] != "58/9":
        raise AssertionError("massive interval operator norm fixture drifted")
    if Fraction(massive_fixture["uniform_sine_kernel_remainder_upper"]) <= 0:
        raise AssertionError("massive truncation remainder must be positive")

    fixture_hash = hashlib.sha256(
        json.dumps(massive_fixture, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    mutations = [
        {
            "name": "nonpositive_mass_range",
            "detected": _mutation_detected(
                exact_payload,
                mass_squared_interval=RationalInterval(Fraction(0), Fraction(1)),
            ),
        },
        {
            "name": "nonzero_Maxwell_mass",
            "detected": _mutation_detected(
                exact_payload,
                family="Maxwell",
                form_degree=0,
                mass_squared_interval=RationalInterval.point(1),
            ),
        },
        {
            "name": "noncontracting_large_slab",
            "detected": _mutation_detected(exact_payload, slab_length=Fraction(10)),
        },
    ]
    if not all(row["detected"] for row in mutations):
        raise AssertionError("finite kernel interval mutation escaped")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result exports the public "
        "enclose_exact_mode_sine_kernel callable for every exact Maxwell and massive-"
        "two-form block through two_j=4. It evaluates rational and algebraic matrix "
        "entries by outward rational intervals, specializes massive blocks only on a "
        "caller-declared strictly positive rational mass-squared interval, exports the "
        "first six interval coefficient matrices, and proves a uniform finite-slab "
        "sine-series remainder by an induced row-sum norm majorant. Nonpositive masses, "
        "nonzero Maxwell mass and noncontracting slabs fail closed. This certifies a "
        "runtime-parametric finite kernel enclosure, not a physical mass choice or the "
        "binding of switches, detector profiles and form contractions. It evaluates no "
        "I_abc, recoil record, tangent-cone, Bridge 3 or quantum claim."
    )
    return {
        "schema": "closed-universe-berger-recoil-finite-mode-kernel-interval-enclosure-v1",
        "result_id": "BERGER_RECOIL_FINITE_MODE_KERNEL_INTERVAL_ENCLOSURE",
        "setting_id": exact_payload["setting_id"],
        "claim_status": "FINITE_MODE_SINE_KERNEL_INTERVAL_ENCLOSURE_CERTIFIED_PROFILE_BINDING_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "mode_scope": {
            "theory": "classical pure-Weyl gravity plus Berger clock, Maxwell detector and massive two-form emitters",
            "background": "compact positive Berger clock at fixed coupling",
            "boundaries": "one caller-declared rational finite time slab; no spatial boundary",
            "charge_sector": "fixed-coupling Berger sector",
            "carrier": "rational interval matrices for exact finite Berger sine kernels",
            "degree": "Maxwell 0,1 and massive-two-form 1,2",
            "parity": "all finite form polarizations",
            "ell": "two_j=0,1,2,3,4",
            "m": "all representation rows",
            "k": "all representation columns",
            "omega": "tau powers 1,3,5,7,9,11 plus a uniform sine-series tail",
        },
        "callable_contract": {
            "module": "closed_universe_observers.berger_recoil_interval_stream",
            "callable": "enclose_exact_mode_sine_kernel",
            "mass_domain": "Maxwell mass_squared=[0,0]; massive_two_form mass_squared.lower>0",
            "tail_rule": "L*x^(N+1)/(2N+3)!/(1-x/((2N+4)(2N+5))), x=||A||_infinity L^2",
            "fail_closed_condition": "x/((2N+4)(2N+5)) < 1",
        },
        "fixtures": {
            "Maxwell_zero_mode_exact_tail": "0",
            "massive_two_j0_degree1_mass_squared": {"lower": "1", "upper": "2"},
            "massive_two_j0_degree1_operator_norm_upper": "58/9",
            "massive_fixture_sha256": fixture_hash,
        },
        "mutation_results": mutations,
        "flags": {
            "FINITE_MODE_KERNEL_INTERVAL_ENCLOSURES_EXPORTED": True,
            "RUNTIME_POSITIVE_MASS_DOMAIN_PARAMETERIZED": True,
            "UNIFORM_FINITE_SLAB_SINE_TAIL_EXPORTED": True,
            "PHYSICAL_MASS_SPECIALIZATION_EXPORTED": False,
            "ACTUAL_SWITCH_PROFILE_AND_FORM_BINDING_EXPORTED": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BIND_EXACT_SWITCH_PROFILE_DETECTOR_AND_FORM_FACTORS_TO_FINITE_KERNEL_INTERVALS",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale finite mode-kernel interval certificate")
    print("BERGER_RECOIL_FINITE_MODE_KERNEL_INTERVAL_ENCLOSURE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
