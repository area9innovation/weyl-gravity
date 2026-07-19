"""Independent verifier for the constant-twist wave counterexample."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_wave_counterexample.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_constant_twist_wave_counterexample.schema.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = value["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()
    matrix = sp.Matrix([[sp.sympify(entry, locals={"sqrt": sp.sqrt}) for entry in row] for row in value["adjoint_obstruction"]["position_matrix"]])
    projected = matrix * sp.Matrix([1, 0, 0, 0])
    assert projected == sp.Matrix([0, 24 * sp.sqrt(3), 0, 0])
    assert matrix.rank() == 2
    classification = value["classification"]
    assert classification["A_arbitrary_wave_branch_refuted"] is True
    assert classification["moment_maps_vanish_but_bounded_resonance_nonzero"] is True
    assert classification["wave_free_constant_twist_modulus_retained"] is True
    assert classification["complete_constant_twist_wave_zero_locus_classified"] is False
    assert len(value["affected_results"]) == 4


if __name__ == "__main__":
    main()
