"""Independent verifier for the compact harmonic/adjoint block preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_harmonic_adjoint_blocks.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate(path: Path = CERTIFICATE) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["result_id"] == "COMPACT_EM_HARMONIC_AND_ADJOINT_BLOCK_PREFLIGHT"
    assert payload["generality_level"] == "G1_BLOCK_PREFLIGHT_AXIAL_N0_TOWER"
    assert _sha256(ROOT / payload["schema_path"]) == payload["schema_sha256"]
    for relative, digest in payload["provenance"]["inputs"].items():
        assert _sha256(ROOT / relative) == digest

    eigenvalue, spectral = sp.symbols("lambda mu", positive=True)
    coupling = sp.Matrix([[eigenvalue, 2], [eigenvalue, eigenvalue]])
    characteristic = sp.factor((spectral * sp.eye(2) - coupling).det())
    assert sp.expand(characteristic - ((spectral - eigenvalue) ** 2 - 2 * eigenvalue)) == 0
    symmetrizer = sp.diag(eigenvalue, 2)
    assert symmetrizer * coupling == coupling.T * symmetrizer
    for sign in (1, -1):
        vector = sp.Matrix([1, sign * sp.sqrt(eigenvalue / 2)])
        omega_squared = eigenvalue + sign * sp.sqrt(2 * eigenvalue)
        assert (coupling * vector - omega_squared * vector).applyfunc(sp.simplify) == sp.zeros(2, 1)
        assert sp.simplify((vector.T * symmetrizer * vector)[0] - 2 * eigenvalue) == 0

    checks = payload["axial_n0_tower"]["new_direct_tensor_regressions"]
    assert [(row["ell"], row["lambda"]) for row in checks] == [(3, 12), (4, 20)]
    assert all(row["all_other_linear_rows_zero"] for row in checks)
    identity = payload["axial_n0_tower"]["all_ell_identity_proof"]
    assert identity["Einstein_angular_remainder_reduces_to"] == "0"
    assert identity["Maxwell_angular_remainder_reduces_to"] == "0"

    zero = payload["axial_n0_tower"]["physical_branch_classification"]["ell_1_minus"]
    assert zero["S1_monodromy"] == {
        "Delta_lambda": "-H_0*L*cos(theta)",
        "Delta_xi_phi": "H_0*L",
    }
    assert zero["global_classification"].startswith("LOCALLY_GAUGE_BUT_NOT_GENERATED")

    targets = payload["universal_adjoint_targets"]
    assert targets["metric_KID_dimension"] == 5
    assert len(targets["metric_KID_basis"]) == 5
    assert targets["complete_full_weyl_maxwell_adjoint_cokernel"] is False
    classification = payload["classification"]
    assert classification["declared_axial_n0_tower_all_ell_m"] is True
    assert classification["complete_axial_n0_gauge_quotient"] is False
    assert classification["full_harmonic_obstruction_theorem"] is False


if __name__ == "__main__":
    verify_certificate()
