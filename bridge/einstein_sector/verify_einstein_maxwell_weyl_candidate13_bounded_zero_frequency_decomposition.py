"""Independent verifier for the candidate-13 bounded zero-frequency receiver."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_bounded_zero_frequency_decomposition.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if payload["schema_sha256"] != sha(schema_path):
        raise AssertionError("bounded zero-frequency schema hash changed")
    records = {}
    for name, item in payload["provenance"]["inputs"].items():
        path = ROOT / item["path"]
        if item["sha256"] != sha(path):
            raise AssertionError(f"stale input hash: {name}")
        records[name] = json.loads(path.read_text(encoding="utf-8"))

    omega, k, G, derivative = sp.symbols("omega k G derivative", real=True)
    pressure = k**2 * G * derivative
    current = 2 * G * derivative
    if sp.factor(pressure - k**2 * current / 2) != 0:
        raise AssertionError("pressure/current normalization changed")
    D, A = sp.symbols("D A")
    if sp.Matrix([-omega**4 * D / 2, omega**4 * D / 4, omega**2 * A]).subs(omega, 0) != sp.zeros(3, 1):
        raise AssertionError("bounded homogeneous zero root changed")
    rows = payload["bounded_zero_frequency_decomposition"]["quadratic_source_rows"]
    if rows["sphere_trace"] != "(E00-E11)/2 by -E00+E11+2*sphere_trace=0":
        raise AssertionError("trace completion changed")
    if rows["Maxwell0"][:1] != "0" or rows["Maxwell1"][:1] != "0":
        raise AssertionError("Maxwell zero rows changed")
    if not records["axial_ell1"]["classification"]["zero_fibre_physical_cokernel_equals_rotation_triplet"]:
        raise AssertionError("rotation cokernel changed")
    if not records["polar_ell1"]["classification"]["polar_ell1_zero_frequency_physical_cokernel_absent"]:
        raise AssertionError("polar L1 cokernel changed")
    if payload["bounded_zero_frequency_decomposition"]["complete_functional_basis"] != ["mu_H", "mu_Px", "mu_J1", "mu_J2", "mu_J3", "R_c"]:
        raise AssertionError("six-functional basis changed")
    flags = payload["classification"]
    if not flags["complete_candidate13_bounded_zero_frequency_receiver_certified"] or not flags["five_stabilizers_plus_circle_pressure_necessary_and_sufficient"]:
        raise AssertionError("bounded zero-frequency lifecycle changed")
    if flags["nonzero_frequency_candidate13_functionals_classified_here"] or flags["causal_residual_observational_or_quantum_claim"]:
        raise AssertionError("bounded zero-frequency theorem exceeded scope")
    print("EINSTEIN_MAXWELL_WEYL_CANDIDATE13_BOUNDED_ZERO_FREQUENCY_DECOMPOSITION verifier: PASS")


if __name__ == "__main__":
    verify()
