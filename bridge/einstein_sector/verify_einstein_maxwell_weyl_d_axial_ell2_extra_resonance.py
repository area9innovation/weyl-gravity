"""Independent verifier for the d-times-axial-extra adjoint map."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_d_axial_ell2_extra_resonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_d_axial_ell2_extra_resonance.schema.json"


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()

    root = sp.sqrt(3)
    hessian = sp.Matrix([[6, 0, 6, 0], [0, -54, 0, -6], [6, 0, 6, 0], [0, -6, 0, -sp.Rational(2, 3)]])
    witnesses = sp.Matrix.hstack(sp.Matrix([-1, 0, 1, 0]), sp.Matrix([0, -sp.Rational(1, 9), 0, 1]))
    sources = sp.Matrix.hstack(
        sp.Matrix([-72 * root * sp.I, 0, 0, 0]),
        sp.Matrix([0, -4 * root * sp.I / 3, 0, -4 * root * sp.I]),
    )
    assert hessian.rank() == 2
    assert hessian.T * witnesses == sp.zeros(4, 2)
    pairing = (witnesses.T * sources).applyfunc(sp.factor)
    assert pairing == sp.diag(72 * root * sp.I, -sp.Rational(104, 27) * root * sp.I)
    assert sp.factor(pairing.det()) == 832
    stored = payload["pairing_theorem"]
    locals_ = {"I": sp.I, "sqrt": sp.sqrt}
    stored_pairing = sp.Matrix([[sp.sympify(value, locals=locals_) for value in row] for row in stored["adjoint_pairing_matrix"]])
    assert stored_pairing == pairing
    classification = payload["classification"]
    assert classification["d_cross_adjoint_map_invertible"] is True
    assert classification["full_second_order_equation_solved"] is False
    assert classification["polar_d_cross_block_classified"] is False


if __name__ == "__main__":
    main()
