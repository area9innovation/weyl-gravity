"""Independent verifier for the homogeneous nonzero-frequency quotient."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.schema.json"


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["engines"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()

    omega, circle, sphere, holonomy = sp.symbols("omega C K A_x")
    expected = [0, 0, -omega**4 * (circle - sphere) / 2, omega**4 * (circle - sphere) / 4, 0, omega**2 * holonomy]
    locals_ = {"omega": omega, "C": circle, "K": sphere, "A_x": holonomy}
    rows = [sp.sympify(value, locals=locals_) for value in payload["operator_theorem"]["rows"]]
    assert [sp.factor(rows[index] - expected[index]) for index in range(6)] == [0] * 6

    gauge = sp.Matrix([
        [-2 * sp.I * omega, 0, -2, 0],
        [0, -sp.I * omega, 0, 0],
        [0, 0, 2, 0],
        [0, 0, 2, 0],
        [0, 0, 0, -sp.I * omega],
        [0, 0, 0, 0],
    ])
    assert gauge.rank() == 4
    invariant_rows = sp.Matrix([[0, 0, 1, -1, 0, 0], [0, 0, 0, 0, 0, 1]])
    assert invariant_rows * gauge == sp.zeros(2, 4)
    assert payload["operator_theorem"]["nonzero_frequency_quotient_dimension"] == 0
    assert payload["classification"]["homogeneous_extra_oscillatory_weyl_modes_absent"] is True


if __name__ == "__main__":
    main()
