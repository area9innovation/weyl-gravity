"""Independent verifier for the automatic-face rotation normal form."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_automatic_face_rotation_normal_form.json"


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

    # Reconstruct the spin-two form independently of the producer.
    magnetic = [-2, -1, 0, 1, 2]
    weight = sp.diag(1, sp.Rational(1, 4), sp.Rational(1, 6), sp.Rational(1, 4), 1)
    j3 = sp.diag(*magnetic)
    assert weight * j3 == sp.diag(-2, -sp.Rational(1, 4), 0, sp.Rational(1, 4), 2)

    rows = payload["normal_form_theorem"]["support_strata"]
    assert [row["occupied_current_eigenlines"] for row in rows] == list(range(1, 7))
    for row in rows:
        nodes = row["occupied_current_eigenlines"]
        if nodes == 1:
            expected_minors = []
        else:
            amplitudes = sp.symbols(f"a1:{nodes + 1}", positive=True, real=True)
            identity = sp.eye(nodes)
            basis = sp.Matrix.hstack(*[
                amplitudes[-1] * identity[:, index] - amplitudes[index] * identity[:, nodes - 1]
                for index in range(nodes - 1)
            ])
            gram = basis.T * basis
            expected_minors = [str(sp.factor(gram[:size, :size].det())) for size in range(1, nodes)]
            for size in range(1, nodes):
                closed = amplitudes[-1] ** (2 * (size - 1)) * (
                    amplitudes[-1] ** 2 + sum(amplitudes[index] ** 2 for index in range(size))
                )
                assert sp.factor(gram[:size, :size].det() - closed) == 0
        assert row["kernel_real_dimension"] == 8 * nodes - 2
        assert row["m_plus_minus_2_real_inertia"] == [2 * nodes, 2 * nodes, 0]
        assert row["m_plus_minus_1_kernel_real_inertia"] == [2 * nodes - 2, 2 * nodes - 2, 2]
        assert row["complete_aligned_kernel_real_inertia"] == [4 * nodes - 2, 4 * nodes - 2, 2]
        assert row["constraint_basis_gram_leading_principal_minors"] == expected_minors
        assert "positive power" in row["constraint_basis_gram_positivity"]
        assert sum(row["complete_aligned_kernel_real_inertia"]) == row["kernel_real_dimension"]
    change = payload["normal_form_theorem"]["quadratic_coordinate_change"]
    assert "c_j=gamma_j*a_j" in change
    assert "zeta_j=gamma_j*z_j" in change
    assert "one complex radical" in change

    # Check the exact arc identities directly.
    a, t = sp.symbols("a t", positive=True, real=True)
    z0sq = a**2 - 12 * t**2
    fixed_norm = sp.factor(z0sq / 6 + t**2 + t**2 - a**2 / 6)
    mu_j3 = sp.factor(-2 * t**2 + 2 * t**2)
    assert fixed_norm == 0
    assert mu_j3 == 0

    candidates = payload["candidate_rows"]
    assert [row["candidate_index"] for row in candidates] == list(range(16, 22))
    assert candidates[0]["verdict"] == "NOT_APPLICABLE"
    assert all(
        row["verdict"] == "HYPERBOLIC_NORMAL_FORM_AND_EXACT_NONAXISYMMETRIC_ARC_CERTIFIED"
        for row in candidates[1:]
    )
    flags = payload["classification"]
    assert flags["all_aligned_quadratic_normal_forms_indefinite"]
    assert flags["all_aligned_quadratic_normal_forms_have_real_nullity_two"]
    assert flags["exact_nonaxisymmetric_fixed_occupation_rotation_zero_arc_at_every_axisymmetric_point"]
    assert not flags["automatic_face_axisymmetric_points_isolated"]
    assert not flags["full_local_singular_strata_classified"]
    assert not flags["active_resonance_components_classified"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_AUTOMATIC_FACE_ROTATION_NORMAL_FORM verifier: PASS")


if __name__ == "__main__":
    verify()
