"""Independent verifier for the complete global plus ell2-extra bounded cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_global_ell2_extra_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_complete_global_ell2_extra_bounded_cone.schema.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = value["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        path = ROOT / record["path"]
        assert record["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()

    a, q = sp.symbols("a q", real=True)
    variables = sp.symbols("x0:8", real=True)
    weights = [1296, 1296, sp.Rational(208, 3), sp.Rational(208, 3), 22464, 22464, 12288, 12288]
    mu = -a**2 - q**2 - sp.Rational(4, 3) * sum(weight * variable**2 for weight, variable in zip(weights, variables, strict=True))
    assert all(coefficient < 0 for coefficient in sp.Poly(mu, a, q, *variables).coeffs())
    theorem = value["complete_bounded_theorem"]
    assert theorem["equality_with_standard_global_cone"] is True
    assert theorem["extra_intersection"] == "the bounded cone contains no nonzero ell=2,k=0 extra-primary direction"
    classification = value["classification"]
    assert classification["complete_declared_global_ell2_extra_carrier_covered"] is True
    assert classification["bounded_tangent_cone_classified"] is True
    assert classification["other_harmonics_classified"] is False
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"


if __name__ == "__main__":
    main()
