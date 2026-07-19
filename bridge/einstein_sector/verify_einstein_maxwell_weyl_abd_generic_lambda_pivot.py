"""Independent verifier for the generic-lambda a,b,d pivot theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_generic_lambda_pivot.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_abd_generic_lambda_pivot.schema.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = value["provenance"]
    for key in ("generator", "direct_engine", "fixture"):
        path = ROOT / provenance[f"{key}_path"]
        assert provenance[f"{key}_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    lam = sp.symbols("lambda", positive=True)
    gap = sp.sqrt(2 * lam)
    omega = sp.sqrt(lam - gap)
    axial = -3 * sp.I * omega * (3 * gap - 1)
    polar = lam**2 * (2 * lam - 1) / 6
    assert all(sp.simplify(axial.subs(lam, n * (n + 1))) != 0 for n in range(2, 12))
    assert all(polar.subs(lam, n * (n + 1)) > 0 for n in range(2, 12))
    classification = value["classification"]
    assert classification["generic_lambda_functional_form_proved_without_interpolation"] is True
    assert classification["all_fixed_ell_at_least_2_pivots_nonzero"] is True
    assert classification["complete_global_wave_cone_classified"] is False
    derivation = value["generic_lambda_derivation"]
    assert derivation["maximum_harmonic_jet_order"] >= derivation["Bach_Maxwell_maximum_sphere_derivative_order"] + 2
    assert "not an identification" in value["SO3_promotion"]["jet_normalization_role"]


if __name__ == "__main__":
    main()
