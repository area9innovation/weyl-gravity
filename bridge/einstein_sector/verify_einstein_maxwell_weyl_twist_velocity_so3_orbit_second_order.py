"""Independent verifier for the SO(3) twist-velocity corollary."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_velocity_so3_orbit_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_twist_velocity_so3_orbit_second_order.schema.json"


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()
    pi = sp.pi
    gram = sp.Matrix([[sp.sympify(value, locals={"pi": pi}) for value in row] for row in payload["harmonic_geometry"]["Gram_matrix"]])
    assert gram == sp.eye(3) * 4 * pi / 3
    assert payload["classification"]["complete_A_zero_twist_velocity_SO3_orbit_second_order_extendible"] is True
    assert payload["classification"]["nonzero_collinear_twist_position_classified"] is False


if __name__ == "__main__":
    main()
