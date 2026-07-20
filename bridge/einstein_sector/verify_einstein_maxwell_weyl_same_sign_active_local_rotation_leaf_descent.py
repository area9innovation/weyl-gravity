"""Independent verifier for local lifted-rotation descent through current leaves."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_local_rotation_leaf_descent.json"


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

    phase_item = payload["provenance"]["inputs"]["phase_reduced_divisors"]
    phase = json.loads((ROOT / phase_item["path"]).read_text())
    flags = phase["classification"]
    assert all(
        flags[name]
        for name in (
            "candidate17_regular_fixed_occupation_phase_reduced_divisor_classified",
            "candidate18_regular_fixed_occupation_phase_reduced_divisor_classified",
            "candidate20_regular_fixed_occupation_phase_reduced_divisor_classified",
            "constant_corank_local_leaf_quotient_classified",
        )
    )

    # Independent exact linear-algebra model of the universal identity.
    # The last two columns span the radical of this rank-four two-form.
    omega = sp.Matrix(
        [
            [0, 1, 0, 0, 0, 0],
            [-1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, -1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ]
    )
    radical = sp.Matrix.hstack(sp.eye(6)[:, 4], sp.eye(6)[:, 5])
    generators = sp.Matrix(
        [
            [1, 0, 2],
            [0, 1, 1],
            [2, 1, 0],
            [1, -1, 1],
            [3, 0, -2],
            [0, 4, 1],
        ]
    )
    moment_differentials = generators.T * omega
    assert omega * radical == sp.zeros(6, 2)
    assert moment_differentials * radical == sp.zeros(3, 2)

    theorem = payload["presymplectic_descent_theorem"]
    assert theorem["radical_annihilation"] == "for r in R, d<mu,xi>(r)=Omega_U(xi_sharp,r)=0"
    assert theorem["zero_fibre_commutation"] == "(mu^{-1}(0) intersect U_0)/R is canonically mu_bar^{-1}(0)"
    result = payload["classification"]
    assert result["moment_map_basic_on_current_radical"]
    assert result["local_zero_fibre_and_radical_reductions_commute"]
    assert not result["node_phases_identified_with_rotations"]
    assert not result["global_rotation_zero_fibre_connected"]
    assert not result["global_leaf_space_or_Hausdorff_quotient_classified"]
    assert not result["singular_locus_reduction_classified"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_ACTIVE_LOCAL_ROTATION_LEAF_DESCENT verifier: PASS")


if __name__ == "__main__":
    verify()
