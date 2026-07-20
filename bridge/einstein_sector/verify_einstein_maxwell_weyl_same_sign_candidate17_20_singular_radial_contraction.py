"""Independent exact verifier for the candidate-17/20 radial contraction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_singular_radial_contraction.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    assert payload["provenance"]["generator_sha256"] == sha(ROOT / payload["provenance"]["generator_path"])
    for item in payload["provenance"]["inputs"].values():
        assert item["sha256"] == sha(ROOT / item["path"])

    # Reconstruct the transfer identity without importing the producer.
    wm, wp, am, ap, bm, bp, s = sp.symbols("wm wp am ap bm bp s")
    original_square = wp * ap - wm * am
    transferred_square = wp * (ap + (1 - s**2) * bp) - wm * (am + (1 - s**2) * bm)
    original_kernel_moment = -original_square
    total = sp.expand(transferred_square + s**2 * original_kernel_moment)
    delta = wp * (ap + bp) - wm * (am + bm)
    assert sp.factor(total - (1 - s**2) * delta) == 0
    assert sp.expand(ap + (1 - s**2) * bp + s**2 * bp - (ap + bp)) == 0
    assert sp.expand(am + (1 - s**2) * bm + s**2 * bm - (am + bm)) == 0

    common_item = payload["provenance"]["inputs"]["common_square"]
    common = json.loads((ROOT / common_item["path"]).read_text())["classification"]
    assert common["candidate20_rotation_balance_divisor_nonempty"]
    assert common["candidate17_rotation_coefficient_strictly_negative_on_complete_nonzero_active_cone"]
    hub_item = payload["provenance"]["inputs"]["connected_hub"]
    hub = json.loads((ROOT / hub_item["path"]).read_text())["classification"]
    assert hub["candidate20_double_singular_rotation_zero_hub_connected"]

    theorem = payload["candidate20_balance_theorem"]
    assert theorem["every_rotation_zero_point_in_each_singular_component_has_radial_path_to_hub"]
    assert theorem["complete_singular_union_rotation_zero_fibre_connected"]
    obstruction = payload["off_balance_obstruction"]
    assert obstruction["residual"] == "(1-t^2)*delta*mu_square"
    assert not obstruction["nonradial_no_go_proved"]
    assert "choose any common-square direction" in payload["radial_transfer"]["square_vertex_case"]
    flags = payload["classification"]
    assert flags["square_factor_vertex_case_included"]
    assert flags["candidate20_balance_complete_singular_union_contracts_to_hub"]
    assert not flags["candidate17_complete_singular_rotation_zero_fibre_connected"]
    assert not flags["candidate20_off_balance_complete_singular_rotation_zero_fibre_connected"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_SINGULAR_RADIAL_CONTRACTION verifier: PASS")


if __name__ == "__main__":
    verify()
