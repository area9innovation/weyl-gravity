"""Independent exact verifier for the moving-square contraction theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_moving_square_contraction.json"


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

    # Reconstruct the normalized Cartan-square moment radius independently.
    p, q, u = sp.symbols("p q u", nonnegative=True)
    norm_square = sp.expand((p**2 + q**2) ** 2 - (p**2 - q**2) ** 2 / 3)
    assert sp.expand(
        3 * norm_square - 2 * (p**2 + q**2) ** 2 - 4 * p**2 * q**2
    ) == 0
    # Therefore p^2+q^2=1 and u=2pq give ||S||^2=(2+u^2)/3.
    radius = 3 * u / (2 + u**2)
    assert sp.factor(sp.diff(radius, u) - 3 * (2 - u**2) / (2 + u**2) ** 2) == 0
    assert radius.subs(u, 0) == 0 and radius.subs(u, 1) == 1

    # Reconstruct the moving-direction cancellation and the zero crossing.
    alpha, delta, s = sp.symbols("alpha delta s", real=True)
    coefficient = s * alpha + (1 - s) * delta
    scale = sp.cancel(s * alpha / coefficient)
    assert sp.factor(-s * alpha + coefficient * scale) == 0
    assert sp.factor(sp.diff(scale, s) - alpha * delta / coefficient**2) == 0
    zero = sp.cancel(-delta / (alpha - delta))
    assert sp.simplify(coefficient.subs(s, zero)) == 0
    assert sp.simplify(coefficient - s * alpha - (1 - s) * delta) == 0

    flags = payload["classification"]
    assert flags["normalized_cartan_square_moment_image_closed_ball"]
    assert flags["uniform_kernel_scaling_moving_square_ansatz_classified"]
    assert flags["alpha_delta_positive_complete_singular_stratum_contracts_to_hub"]
    assert flags["square_factor_vertex_off_balance_contracts_to_hub"]
    assert flags["opposite_sign_interior_zero_obstruction_certified"]
    assert flags["zero_alpha_complete_stratum_contracts_to_hub"]
    assert "coefficient-zero square pre-rotation" in payload["complete_ansatz_disposition"]["alpha_zero"]
    assert "former endpoint-continuity claim" in payload["interpretation"]
    assert "SO(3) acts transitively" in payload["cartan_square_moment_ball"]["direction_orbits"]
    assert not flags["candidate17_complete_singular_rotation_zero_fibre_connected"]
    assert not flags["candidate20_off_balance_complete_singular_rotation_zero_fibre_connected"]
    assert not flags["general_nonradial_no_go"]
    assert not flags["nonuniform_scaling_classified"]
    assert "not to paths that deform the K factor" in payload["interpretation"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_MOVING_SQUARE_CONTRACTION verifier: PASS")


if __name__ == "__main__":
    verify()
