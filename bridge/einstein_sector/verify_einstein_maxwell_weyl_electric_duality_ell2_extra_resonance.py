"""Independent verifier for electric-duality mixed removability."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_duality_ell2_extra_resonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_electric_duality_ell2_extra_resonance.schema.json"


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()

    theta = sp.symbols("theta", real=True)
    c, s = sp.cos(theta), sp.sin(theta)
    rotation = sp.Matrix([[c, s], [-s, c]])
    assert (rotation.T * rotation).applyfunc(sp.trigsimp) == sp.eye(2)
    electric = sp.Matrix(sp.symbols("e0:3", real=True))
    magnetic = sp.Matrix(sp.symbols("b0:3", real=True))
    ep, bp = c * electric + s * magnetic, c * magnetic - s * electric
    assert (ep * ep.T + bp * bp.T - electric * electric.T - magnetic * magnetic.T).applyfunc(sp.trigsimp) == sp.zeros(3)
    assert (ep.cross(bp) - electric.cross(magnetic)).applyfunc(sp.trigsimp) == sp.zeros(3, 1)

    classification = payload["classification"]
    assert classification["electric_Qe_times_ell2_extra_source_in_linear_image"] is True
    assert classification["mixed_correction_fixed_bundle_admissible"] is True
    assert classification["all_orders_fixed_bundle_duality_orbit"] is False
    assert classification["remaining_homogeneous_a_b_d_cross_sources_classified"] is False


if __name__ == "__main__":
    main()
