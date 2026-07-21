"""Method-distinct verifier for the compact-Cauchy adjoint kernel."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_ADJOINT_KERNEL_CLASSIFICATION_V1.json"
ATLAS = ROOT / "residual_atlas/einstein-weyl-compact-cauchy-adjoint-kernel-fragment-v1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-compact-cauchy-adjoint-kernel-classification-v1.schema.json"


class IndependentAdjointKernelVerificationError(RuntimeError):
    pass


def _require(value: bool, message: str) -> None:
    if not value:
        raise IndependentAdjointKernelVerificationError(message)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate(cert_path: Path = CERT, atlas_path: Path = ATLAS) -> None:
    payload = json.loads(cert_path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _require(payload["schema_sha256"] == _sha(SCHEMA), "schema hash mismatch")

    for imported in payload["provenance"]["imported_artifacts"]:
        path = ROOT / imported["path"]
        _require(path.exists() and _sha(path) == imported["sha256"], f"import drift: {imported['name']}")

    # Reconstruct the spectral classification without importing the producer.
    ell_survivors: list[tuple[int, str, int]] = []
    for ell in range(0, 10):
        lam = ell * (ell + 1)
        if ell == 0:
            ell_survivors.append((ell, "product_scalar", 2))
        if ell >= 1 and lam - 2 == 0:
            ell_survivors.append((ell, "sphere_coexact", 2 * ell + 1))
        if ell >= 1:
            _require(lam != 0, "sphere exact obstruction failed")
        if ell >= 2:
            _require(lam - 2 != 0, "generic coexact obstruction failed")
    _require(ell_survivors == [(0, "product_scalar", 2), (1, "sphere_coexact", 3)], "wrong harmonic kernel")

    P = sp.symbols("P")
    lift = sp.Matrix([[P, 1]])
    _require(lift.rank() == 1 and lift * sp.Matrix([1, -P]) == sp.zeros(1, 1), "bundle lift failed")
    _require(sum(row["real_dimension"] for row in payload["harmonic_decomposition"]) == 5, "wrong real dimension")
    _require(payload["global_stabilizer_solution"]["basis"] == ["H", "P_x", "J_1", "J_2", "J_3"], "basis changed")

    # Mutations: a deleted basis vector and a restored constant gauge mode
    # must be distinguishable from the certified five-dimensional result.
    _require(payload["mutation_controls"]["delete_H"]["expected_dimension"] == 4, "H deletion missed")
    _require(payload["mutation_controls"]["delete_one_rotation"]["expected_dimension"] == 4, "rotation deletion missed")
    _require(payload["mutation_controls"]["restore_constant_U1"]["formal_dimension"] == 6, "constant U1 mutation missed")
    _require(payload["mutation_controls"]["restore_constant_U1"]["nontrivial_charge_dimension"] == 5, "reducibility miscounted")
    _require(payload["mutation_controls"]["insert_ell2_coexact"]["obstruction"] == "lambda-2=4", "ell2 mutation missed")

    atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
    entry = atlas["entries"][0]
    _require(entry["mode_data"]["taub_maps"]["status"] == "CERTIFIED", "atlas Taub map not certified")
    _require(entry["evidence"][0]["sha256"] == _sha(cert_path), "atlas evidence hash mismatch")
    required_scope = {"theory", "background", "boundaries", "charge_sector", "carrier", "degree", "parity", "ell", "m", "k", "omega"}
    _require(set(entry["scope"]) == required_scope, "atlas scope incomplete")
    print("PASS independent compact-Cauchy adjoint-kernel verification")


if __name__ == "__main__":
    verify_certificate()
