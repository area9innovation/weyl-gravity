"""Independent verifier for the exceptional ell=1 static target."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_nonzero_static.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell1_nonzero_static.schema.json"


def _matrix(values: list[list[str]], k: sp.Symbol) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(value, locals={"k": k}) for value in row] for row in values])


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for path, digest in provenance["engines"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
    record = provenance["input"]
    assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"]

    k, omega = sp.symbols("k omega", real=True)
    replay = payload["direct_replay"]
    axial_full = sp.Matrix([[sp.sympify(value, locals={"k": k, "omega": omega}) for value in row] for row in replay["axial"]["full_Fourier_action_Hessian"]])
    polar_full = sp.Matrix([[sp.sympify(value, locals={"k": k, "omega": omega}) for value in row] for row in replay["polar"]["full_Fourier_action_Hessian"]])
    axial_full_gauge = sp.Matrix([sp.sympify(value, locals={"k": k, "omega": omega}) for value in replay["axial"]["full_Fourier_residual_gauge"]])
    polar_full_gauge = sp.Matrix([sp.sympify(value, locals={"k": k, "omega": omega}) for value in replay["polar"]["full_Fourier_residual_gauge"]])
    assert (axial_full * axial_full_gauge).applyfunc(sp.factor) == sp.zeros(4, 1)
    assert (polar_full * polar_full_gauge).applyfunc(sp.factor) == sp.zeros(4, 1)
    assert (
        axial_full - axial_full.subs({omega: -omega, k: -k}, simultaneous=True).T
    ).applyfunc(sp.factor) == sp.zeros(4)
    assert (
        polar_full - polar_full.subs({omega: -omega, k: -k}, simultaneous=True).T
    ).applyfunc(sp.factor) == sp.zeros(4)
    expected_shells = (k**2 - omega**2 + 4) * (3 * k**2 - 3 * omega**2 + 4)
    assert sp.factor(sp.sympify(replay["axial"]["three_by_three_determinantal_divisor"], locals={"k": k, "omega": omega}) - expected_shells) == 0
    assert sp.factor(sp.sympify(replay["polar"]["three_by_three_determinantal_divisor"], locals={"k": k, "omega": omega}) - expected_shells / 3) == 0
    axial = _matrix(replay["axial"]["action_Hessian"], k)
    polar = _matrix(replay["polar"]["action_Hessian"], k)
    axial_gauge = sp.Matrix([sp.sympify(value, locals={"k": k}) for value in replay["axial"]["residual_gauge"]])
    polar_gauge = sp.Matrix([sp.sympify(value, locals={"k": k}) for value in replay["polar"]["residual_gauge"]])
    assert axial == axial.T and polar == polar.T
    assert (axial * axial_gauge).applyfunc(sp.factor) == sp.zeros(4, 1)
    assert (polar * polar_gauge).applyfunc(sp.factor) == sp.zeros(4, 1)
    assert sp.factor(axial.extract((0, 1, 2), (0, 1, 2)).det()) == k**2 * (k**2 + 4) * (3 * k**2 + 4)
    assert sp.factor(polar.extract((0, 1, 2), (0, 1, 2)).det()) == (k**2 + 4) * (3 * k**2 + 4) / 2
    assert payload["static_consequence"]["every_Noether_compatible_static_L1_source_is_removable"] is True


if __name__ == "__main__":
    main()
