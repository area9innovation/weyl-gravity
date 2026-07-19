"""Independent verifier for the multi-ell Einstein-minus pivot fixtures."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_general_ell_minus_pivot_fixtures.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_abd_general_ell_minus_pivot_fixtures.schema.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = value["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["helpers"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()
    lam = sp.symbols("lambda", positive=True)
    polar = lam**2 * (2 * lam - 1) / 6
    assert [polar.subs(lam, row["lambda"]) for row in value["fixtures"]] == [66, 552, 2600]
    classification = value["classification"]
    assert classification["ell2_and_ell3_complete_triangular_pivots_direct"] is True
    assert classification["symbolic_functional_form_or_degree_bound_proved"] is False
    assert classification["general_ell_pivot_theorem"] is False


if __name__ == "__main__":
    main()
