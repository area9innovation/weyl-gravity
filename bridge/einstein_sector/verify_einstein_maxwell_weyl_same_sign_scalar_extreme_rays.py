"""Independent verifier for the universal four-ray same-sign scalar cone."""

import hashlib
import itertools
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_extreme_rays.json"


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

    nodes = payload["moment_curve_reduction"]["ordered_nodes"]
    masses = [sp.sympify(node["mass_over_n_squared"]) for node in nodes]
    assert all((masses[index + 1] - masses[index]).is_positive is True for index in range(5))
    signs = [node["current_sign"] for node in nodes]
    supports = []
    for support in itertools.combinations(range(6), 4):
        selected = [signs[index] for index in support]
        if selected in ([-1, 1, -1, 1], [1, -1, 1, -1]):
            supports.append([nodes[index]["id"] for index in support])
    assert supports == [ray["support"] for ray in payload["extreme_rays"]]

    x = sp.symbols("x0:4")
    z = [1 / sp.prod(x[index] - x[j] for j in range(4) if j != index) for index in range(4)]
    for degree in range(3):
        assert sp.cancel(sum(z[index] * x[index] ** degree for index in range(4))) == 0
    assert [sp.sign(sp.N(value.subs(dict(zip(x, (1, 2, 3, 4)))))) for value in z] == [-1, 1, -1, 1]
    assert [row["candidate_index"] for row in payload["candidate_rows"]] == list(range(16, 22))
    assert all(row["ray_ids"] == ["R1", "R2", "R3", "R4"] for row in payload["candidate_rows"])
    flags = payload["classification"]
    assert flags["all_positive_rho_same_sign_scalar_cones_have_four_extreme_rays"]
    assert not flags["rotation_or_resonance_zero_loci_joined"]
    assert not flags["full_bounded_cones_classified"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_SCALAR_EXTREME_RAYS verifier: PASS")


if __name__ == "__main__":
    verify()
