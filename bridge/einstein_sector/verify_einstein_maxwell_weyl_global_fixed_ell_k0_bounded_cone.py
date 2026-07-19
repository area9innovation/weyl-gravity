"""Independent verifier for the global fixed-ell bounded cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_fixed_ell_k0_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_global_fixed_ell_k0_bounded_cone.schema.json"


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
    cone = value["complete_bounded_cone"]
    assert cone["union_is_necessary_and_sufficient"] is False
    assert "a=b=d=Q_e=0" in cone["certified_wave_subcone"]
    assert "A=B=0" in cone["certified_wave_subcone"]
    assert cone["nonzero_A_wave_stratum"].startswith("OPEN")
    classification = value["classification"]
    assert classification["every_fixed_generic_ell_global_bounded_cone_classified"] is False
    assert classification["A_arbitrary_wave_branch_withdrawn"] is True
    assert classification["A_zero_wave_subcone_certified"] is True
    assert classification["cross_ell_superpositions_classified"] is False
    assert classification["nonzero_momentum_classified"] is False
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    matrix = sp.Matrix([[2, 0, 2, 0], [0, -2, 0, -2], [2, 0, 2, 0], [0, -2, 0, -2]])
    s0, s1 = sp.symbols("S0 S1")
    assert matrix * sp.Matrix([s0 / 2, -s1 / 2, 0, 0]) == sp.Matrix([s0, s1, s0, s1])


if __name__ == "__main__":
    main()
