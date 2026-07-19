"""Independent verifier for the axisymmetric rotation critical locus."""

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_axisymmetric_rotation_singularity.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == sha(ROOT / provenance["generator_path"])
    for item in provenance["inputs"].values():
        assert item["sha256"] == sha(ROOT / item["path"])

    m = [-2, -1, 0, 1, 2]
    weight = sp.diag(1, sp.Rational(1, 4), sp.Rational(1, 6), sp.Rational(1, 4), 1)
    jp = sp.zeros(5)
    jm = sp.zeros(5)
    for index, value in enumerate(m):
        if value < 2:
            jp[index + 1, index] = 2 - value
        if value > -2:
            jm[index - 1, index] = 2 + value
    t1 = (jp + jm) / 2
    t2 = (jp - jm) / (2 * sp.I)
    t3 = sp.diag(*m)
    e0 = sp.Matrix([0, 0, 1, 0, 0])
    covectors = [sp.simplify(weight * item * e0) for item in (t1, t2, t3)]
    assert covectors[2] == sp.zeros(5, 1)
    gram = sp.Matrix([[sp.re((covectors[i].conjugate().T * covectors[j])[0]) for j in range(2)] for i in range(2)])
    assert gram.rank() == 2 and gram.det() > 0
    stored = payload["spin_two_certificate"]
    assert stored["basis_order"] == m
    assert stored["T1_T2_real_gram_determinant"] == str(sp.factor(gram.det()))
    theorem = payload["jacobian_rank_theorem"]
    assert theorem["origin"]["rank_d_mu_J"] == 0
    assert theorem["every_nonzero_section_point"]["rank_d_mu_J"] == 2
    assert theorem["candidate_indices"] == list(range(16, 22))
    flags = payload["classification"]
    assert flags["all_nonzero_axisymmetric_section_points_rotation_critical"]
    assert flags["rotation_jacobian_rank_exactly_two"]
    assert not flags["implicit_function_regular_seed_available_on_axisymmetric_section"]
    assert not flags["local_real_zero_set_components_classified"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_AXISYMMETRIC_ROTATION_SINGULARITY verifier: PASS")


if __name__ == "__main__":
    verify()
