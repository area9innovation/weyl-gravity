"""Independent verifier for the balanced homogeneous/twist fixture."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_balanced_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_homogeneous_twist_balanced_second_order.schema.json"


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()
    a, B, t = sp.symbols("a B t", real=True)
    local = {"a": a, "B": B, "t": t}
    correction = payload["second_order_correction"]
    k0 = sp.sympify(correction["homogeneous_L0"]["K2"], locals=local)
    assert sp.factor(sp.diff(k0, t, 4) / 2 + sp.Rational(16, 3) * B**2) == 0
    assert all(value == "0" for value in correction["polar_L2"]["all_eight_row_remainders"].values())
    assert all(value == "0" for value in correction["axial_L1"]["all_six_row_remainders"].values())
    classification = payload["classification"]
    assert classification["nonzero_homogeneous_twist_velocity_common_zero_tangent_second_order_extendible"] is True
    assert classification["full_twist_velocity_cone_classified"] is False


if __name__ == "__main__":
    main()
