"""Independent verifier for the compact obstruction-bilinear certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_obstruction_bilinear.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate(path: Path = CERTIFICATE) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["result_id"] == "EINSTEIN_MAXWELL_OBSTRUCTION_BILINEAR_G1"
    assert payload["generality_level"] == "G1_DECLARED_FIXTURE_SPAN"
    assert _sha256(ROOT / payload["schema_path"]) == payload["schema_sha256"]
    for relative, digest in payload["provenance"]["inputs"].items():
        assert _sha256(ROOT / relative) == digest

    matrix = sp.Matrix(
        [[sp.sympify(value, locals={"sqrt": sp.sqrt}) for value in row] for row in payload["bilinear"]["matrix"]]
    )
    expected = sp.diag(
        -2,
        -sp.Rational(1, 2),
        -sp.Rational(16, 3),
        -12 * sp.sqrt(3) - sp.Rational(72, 5),
    )
    assert (matrix - expected).applyfunc(sp.simplify) == sp.zeros(4)
    assert matrix == matrix.T
    assert payload["bilinear"]["radion_duality_direct_tensor_check"]["polarized_entry"] == "0"

    coefficients = sp.Matrix(sp.symbols("a_R a_D a_P a_G", real=True))
    quadratic = sp.sympify(
        payload["bilinear"]["quadratic_form"],
        locals={str(symbol): symbol for symbol in coefficients} | {"sqrt": sp.sqrt},
    )
    assert sp.simplify(quadratic - (coefficients.T * expected * coefficients)[0]) == 0

    fibres = payload["charge_fibres"]
    assert fibres["fixed_electric_fixed_magnetic"]["constant_lapse_cokernel"] == "C_H survives"
    assert fibres["variable_electric_fixed_magnetic"]["constant_lapse_cokernel"].startswith("C_H survives")
    assert fibres["variable_magnetic"]["constant_lapse_cokernel"] == "C_H is removed from the augmented cokernel"
    assert fibres["variable_magnetic"]["required_lift"] == "p=Q(v) cancels this component of the extension equation"
    assert payload["taub_relation"]["classification"] == "RELATIVE_TAUB_MOMENT_MAP_COMPONENT"
    assert payload["classification"]["full_harmonic_obstruction_theorem"] is False


if __name__ == "__main__":
    verify_certificate()
