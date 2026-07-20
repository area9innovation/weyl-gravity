"""Independent verifier for the auxiliary-Schouten edge-pair preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/ASYMPTOTIC_BACH_AUXILIARY_SCHOUTEN_EDGE_PAIR_PREFLIGHT_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/asymptotic-bach-auxiliary-schouten-edge-pair-preflight-v1.schema.json"
ATLAS = ROOT / "residual_atlas/einstein-asymptotic-bach-auxiliary-schouten-edge-pair-fragment-v1.json"
INPUT_HASH = "6ccb79e0626ff81fa2ffbe79166f578e50436078eaab3787da5c826112434b7d"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def verify() -> None:
    certificate = _load(CERTIFICATE)
    schema = _load(SCHEMA)
    atlas = _load(ATLAS)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    assert certificate["schema_sha256"] == _sha256(SCHEMA)
    assert certificate["provenance"]["pinned_input_sha256"] == INPUT_HASH
    source = certificate["provenance"]["input"]
    assert _sha256(ROOT / source["path"]) == source["sha256"] == INPUT_HASH

    alpha, ricci2, scalar2 = sp.symbols("alpha_B Ricci2 R2", nonzero=True)
    q = alpha * (ricci2 - scalar2 / 3) / 4
    pi_dot_ricci = alpha * (ricci2 - scalar2 / 3) / 2
    pi_norm2 = alpha**2 * (ricci2 - 2 * scalar2 / 9) / 4
    pi_trace2 = alpha**2 * scalar2 / 36
    hamiltonian = sp.expand((pi_norm2 - pi_trace2) / alpha)
    assert sp.simplify(hamiltonian - q) == 0
    assert sp.simplify(pi_dot_ricci - hamiltonian - q) == 0

    identity = sp.eye(2)
    canonical = sp.zeros(2).row_join(identity).col_join((-identity).row_join(sp.zeros(2)))
    assert canonical.rank() == 4
    assert canonical.det() == 1
    exact = certificate["exact_auxiliary_legendre_transform"]
    assert sp.Matrix(exact["tracefree_normal_jet_principal_matrix"]) == canonical
    assert exact["tracefree_normal_jet_principal_rank"] == 4
    assert exact["tracefree_normal_jet_principal_determinant"] == "1"
    assert exact["metric_only_rank"] == 0
    assert exact["Weyl_ghost_action"]["delta_sigma_s_trace"] == "-alpha_B*box_sigma"
    assert exact["Weyl_ghost_action"]["delta_sigma_A_trace"] == "alpha_B*box_sigma"

    flags = certificate["classification"]
    assert flags["full_tensor_auxiliary_action_exactly_equivalent_modulo_Euler"] is True
    assert flags["prequotient_tracefree_normal_jet_principal_pairing_nondegenerate"] is True
    assert flags["full_Bondi_BV_BFV_phase_space_constructed"] is False
    assert flags["boundary_gauge_descent_certified"] is False
    assert flags["P0_charge_computed"] is False
    assert flags["D_M_charge_computed"] is False

    entry = atlas["entries"][0]
    assert entry["id"] == "einstein.asymptotic.minkowski.weyl.auxiliary_schouten_edge_pair"
    assert entry["mode_data"]["lee_wald"]["status"] == "CERTIFIED"
    assert entry["descriptions"]["symplectic"] == "OPEN"
    assert entry["evidence"][0]["sha256"] == _sha256(CERTIFICATE)


if __name__ == "__main__":
    verify()
    print("ASYMPTOTIC_BACH_AUXILIARY_SCHOUTEN_EDGE_PAIR_PREFLIGHT_V1 independent verification: PASS")
