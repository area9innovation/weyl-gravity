"""Independent verifier for the six candidatewise scalar cone audits."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_maxwell_weyl_collision_scalar_separation_classification import CURRENT_SIGN, MASS_SQUARED, feature


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_scalar_occupation_cones.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    for item in payload["provenance"]["inputs"].values():
        assert item["sha256"] == sha(ROOT / item["path"])
    labels = [(item["signed_momentum_n"], item["branch"]) for item in payload["occupation_order"]]
    expected = {
        ((1, "q_minus"), (1, first), (2, "q_minus"), (2, second))
        for first in ("p_extra", "q_plus") for second in ("p_extra", "q_plus")
    }
    for row in payload["candidate_rows"]:
        rho = sp.sympify(row["rho"])
        matrix = sp.Matrix.hstack(*[CURRENT_SIGN[branch] * feature(rho, n, branch) for n, branch in labels])
        assert matrix.rank() == 3
        assert all(matrix[:, support].det() != 0 for support in itertools.combinations(range(6), 3))
        supports = set()
        for ray in row["positive_extreme_rays"]:
            support = tuple(ray["support_indices"])
            block = matrix[:, support]
            weights = [sp.factor((-1) ** column * block[:, [j for j in range(4) if j != column]].det()) for column in range(4)]
            if weights[0].is_negative is True:
                weights = [-value for value in weights]
            assert all(value.is_positive is True for value in weights)
            assert [sp.sstr(value) for value in weights] == ray["cofactor_weights"]
            assert ray["kernel_remainder"] == ["0", "0", "0"]
            supports.add(tuple((item["signed_momentum_n"], item["branch"]) for item in ray["support"]))
        assert supports == expected and len(row["nonpositive_circuits"]) == 11
    flags = payload["classification"]
    assert flags["all_120_support_three_minors_nonzero"] and flags["all_90_support_four_circuits_classified"]
    assert flags["four_positive_extreme_rays_per_candidate"] and not flags["full_rotation_and_resonance_join_classified"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_COLLISION_SCALAR_OCCUPATION_CONES verifier: PASS")


if __name__ == "__main__":
    verify()
