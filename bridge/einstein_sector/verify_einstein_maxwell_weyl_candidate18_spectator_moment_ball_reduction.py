"""Independent verification of the candidate-18 spectator reduction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_CANDIDATE18_SPECTATOR_MOMENT_BALL_REDUCTION_V1.json"
ATLAS = ROOT / "residual_atlas/einstein-candidate18-spectator-moment-ball-reduction-fragment-v1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-candidate18-spectator-moment-ball-reduction-v1.schema.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _independent_spin_two_check() -> None:
    root6 = sp.sqrt(6)
    jx = sp.Matrix([
        [0, 1, 0, 0, 0],
        [1, 0, root6 / 2, 0, 0],
        [0, root6 / 2, 0, root6 / 2, 0],
        [0, 0, root6 / 2, 0, 1],
        [0, 0, 0, 1, 0],
    ])
    jy = sp.Matrix([
        [0, sp.I, 0, 0, 0],
        [-sp.I, 0, sp.I * root6 / 2, 0, 0],
        [0, -sp.I * root6 / 2, 0, sp.I * root6 / 2, 0],
        [0, 0, -sp.I * root6 / 2, 0, sp.I],
        [0, 0, 0, -sp.I, 0],
    ])
    jz = sp.diag(-2, -1, 0, 1, 2)
    assert jx.H == jx and jy.H == jy and jz.H == jz
    assert sp.simplify(jx * jy - jy * jx - sp.I * jz) == sp.zeros(5)
    assert sp.simplify(jx**2 + jy**2 + jz**2) == 6 * sp.eye(5)
    x, y = sp.symbols("x y", nonnegative=True, real=True)
    state = sp.Matrix([0, 0, x, 0, y])
    assert sp.simplify((state.H * state)[0]) == x**2 + y**2
    assert [sp.simplify((state.H * t * state)[0]) for t in (jx, jy, jz)] == [0, 0, 2 * y**2]


def verify_payload(payload: dict[str, Any]) -> None:
    Draft202012Validator(_load(SCHEMA)).validate(payload)
    for record in payload["provenance"]["inputs"].values():
        path = ROOT / record["path"]
        assert _sha256(path) == record["sha256"]
        assert _load(path)["result_id"] == record["result_id"]
    _independent_spin_two_check()

    parent = _load(ROOT / payload["provenance"]["inputs"]["parent_gate"]["path"])
    assert parent["selected_invariant_gate"]["ambient_real_dimension"] == 60
    assert payload["spectator_representation"]["real_dimension"] == 20
    active = payload["active_coordinate_gate"]
    assert active["ambient_real_dimension"] == 40
    assert active["spectator_slack"] == "H_s=6*N_plus-H_f"
    assert active["exact_spectator_existence_conditions"] == [
        "H_s>=0",
        "|M_f|^2<=4*H_s^2",
    ]
    theorem = payload["spectator_moment_ball_theorem"]
    assert theorem["image_at_fixed_norm"] == "{nu in R^3: |nu|<=2*H_s}"
    assert theorem["all_ten_spectators_retained"]
    assert payload["remaining_strict_gate"]["strictly_smaller_than_parent"]

    classification = payload["classification"]
    assert classification["spectator_moment_image_exact_ball"]
    assert classification["spectator_moment_fibres_connected"]
    assert classification["ten_spectators_retained_by_exact_fibre_reconstruction"]
    assert classification["active_40_real_semialgebraic_gate_exact"]
    assert not classification["active_real_radical_classified"]
    assert not classification["full_U1_squared_SO3_orbit_quotient_classified"]
    assert not classification["every_component_meets_central_bridge"]
    assert not classification["complex_irreducibility_substituted_for_real_connectedness"]


def verify_certificate() -> None:
    payload = _load(CERTIFICATE)
    verify_payload(payload)
    atlas = _load(ATLAS)
    entry = atlas["entries"][0]
    assert entry["evidence"][0]["sha256"] == _sha256(CERTIFICATE)
    assert entry["descriptions"]["nonlinear"] == "OPEN"
    assert entry["mode_data"]["taub_maps"]["status"] == "CERTIFIED"
    assert entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] == "OPEN"


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_CANDIDATE18_SPECTATOR_MOMENT_BALL_REDUCTION_V1 independent verification: PASS")
