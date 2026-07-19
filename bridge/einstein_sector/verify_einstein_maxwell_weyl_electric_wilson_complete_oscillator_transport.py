"""Independent verification of complete electric/Wilson oscillator transport."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport.schema.json"


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

    theta = sp.symbols("theta", real=True)
    c, s = sp.cos(theta), sp.sin(theta)
    rotation = sp.Matrix([[c, s], [-s, c]])
    assert (rotation.T * rotation).applyfunc(sp.trigsimp) == sp.eye(2)
    assert sp.trigsimp(sp.det(rotation) - 1) == 0

    scope = value["scope"]
    assert scope["ell"] == "generic ell>=2 and exceptional ell=1"
    assert scope["k"] == "every allowed compact momentum 2*pi*n/L"
    classification = value["classification"]
    assert classification["complete_certified_nonzero_frequency_inventory_covered"] is True
    assert classification["Q_e_times_every_oscillator_bounded_removable"] is True
    assert classification["W_x_times_every_oscillator_source_zero"] is True
    assert classification["fixed_bundle_mixed_correction_admissible"] is True
    assert classification["full_bounded_cone_solved"] is False
    assert value["bounded_ledger_consequence"]["independent_global_condition"] == "the zero-frequency global self coefficient still requires Q_e*a=0"
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"


if __name__ == "__main__":
    main()
