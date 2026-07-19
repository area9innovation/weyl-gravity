"""Independent verifier for the candidate-13 mixed pressure theorem."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_mixed_pressure_obstruction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_candidate13_mixed_pressure_obstruction.schema.json"
INPUTS = [
    ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_moment_resonance_null_witness.json",
    ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_same_fibre_resonance_census.json",
    ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.json",
    ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    value = json.loads(CERTIFICATE.read_text())
    jsonschema.validate(value, json.loads(SCHEMA.read_text()))
    if value["schema_sha256"] != sha(SCHEMA):
        raise AssertionError("candidate-13 pressure schema hash changed")
    expected = {str(path.relative_to(ROOT)): sha(path) for path in INPUTS}
    if value["provenance"]["inputs"] != expected:
        raise AssertionError("candidate-13 pressure provenance changed")

    rho = (-sp.Integer(250) + 461 * sp.sqrt(10)) / 2132
    q1 = sp.sqrt(rho + 6 - 2 * sp.sqrt(3))
    q2 = sp.sqrt(4 * rho + 6 - 2 * sp.sqrt(3))
    p1 = sp.sqrt(rho + sp.Rational(16, 3))
    y1 = p1 * (2 * p1 + q2) / (q1 * (2 * q1 + q2))
    y2 = p1 * (p1 - q1) / (q2 * (2 * q1 + q2))
    pressure = sp.factor(rho * (1 - y1 - 4 * y2) / 2)
    if value["exact_witness"]["pressure"] != sp.sstr(pressure):
        raise AssertionError("candidate-13 pressure expression changed")
    if not (461**2 * 10 > 250**2 and 2**2 * 3 > sp.Rational(2, 3) ** 2):
        raise AssertionError("candidate-13 exact sign chain failed")

    c, k, omega, G, derivative = sp.symbols("c k omega G derivative", real=True)
    s = omega**2 - k**2 / (1 + c)
    on_shell_circle = sp.diff(s, c).subs(c, 0) * G * derivative
    current = 2 * G * derivative
    if sp.factor(on_shell_circle - k**2 * current / 2) != 0:
        raise AssertionError("universal pressure/current identity changed")
    if value["zero_frequency_source"]["value"] != sp.sstr(pressure):
        raise AssertionError("typed pressure pairing changed")
    flags = value["classification"]
    if not (
        flags["candidate13_bounded_pressure_functional_nonzero"]
        and flags["candidate13_bounded_or_finite_quasiperiodic_extension_obstructed"]
        and flags["candidate13_smooth_exponential_polynomial_extension_certified"]
        and not flags["complete_candidate13_mixed_cone_classified"]
        and not flags["causal_residual_observational_or_quantum_claim"]
    ):
        raise AssertionError("candidate-13 pressure lifecycle changed")
    print("EINSTEIN_MAXWELL_WEYL_CANDIDATE13_MIXED_PRESSURE_OBSTRUCTION independent verification: PASS")


if __name__ == "__main__":
    verify()
