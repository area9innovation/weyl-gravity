"""Independent verifier for the locked all-m physical moment intersection."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_ell2_extra_difference_source_explore import (
    POLAR_EXTRA,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ALL_M_MOMENT_INTERSECTION_V1.json"
ATLAS = ROOT / "residual_atlas/einstein-exceptional-all-m-moment-intersection-fragment.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-exceptional-all-m-moment-intersection-v1.schema.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stf(matrix: sp.Matrix) -> sp.Matrix:
    return (matrix - sp.trace(matrix) * sp.eye(3) / 3).applyfunc(sp.expand)


def _exceptional_self_zero_check() -> None:
    a = sp.Matrix(sp.symbols("a0:3"))
    q = sp.Matrix(sp.symbols("q0:3"))
    tensors = (
        _stf(a * a.T - q * q.T),
        _stf(a * q.T + q * a.T),
    )
    equations: list[sp.Expr] = []
    for tensor in tensors:
        equations.extend([tensor[0, 0], tensor[1, 1], tensor[0, 1], tensor[0, 2], tensor[1, 2]])
    variables = tuple(a) + tuple(q)
    basis = sp.groebner(equations, *variables, order="grevlex")
    assert basis.is_zero_dimensional
    expressions = [sp.factor(value.as_expr()) for value in basis.polys]
    assert any(sp.expand(value - q[2] ** 5) == 0 for value in expressions)
    assert any(
        sp.expand(value - (a[2] ** 3 - 3 * a[2] * q[2] ** 2)) == 0
        for value in expressions
    )


def _angular_forms() -> tuple[sp.Expr, sp.Matrix]:
    z = sp.symbols("z", real=True)
    v1 = sp.integrate(z**2, (z, -1, 1)) * 2 * sp.pi
    basis = [
        sp.diag(1, -1, 0),
        sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 0]]),
        sp.Matrix([[0, 0, 1], [0, 0, 0], [1, 0, 0]]),
        sp.Matrix([[0, 0, 0], [0, 0, 1], [0, 1, 0]]),
        sp.diag(sp.Rational(-1, 2), sp.Rational(-1, 2), 1),
    ]
    gram = sp.Matrix(
        5,
        5,
        lambda row, column: sp.Rational(8, 15)
        * sp.pi
        * sp.trace(basis[row].T * basis[column]),
    )
    assert all(sp.factor(gram[:size, :size].det()) > 0 for size in range(1, 6))
    return v1, gram


def _rest_weights(payload: dict[str, Any]) -> None:
    inputs = payload["provenance"]["inputs"]
    polar = _load(ROOT / inputs["polar_current"]["path"])
    lam, momentum = sp.symbols("lam k", real=True)
    gram = sp.Matrix(
        [
            [
                sp.sympify(value.replace("lambda", "lam"), locals={"lam": lam, "k": momentum})
                for value in row
            ]
            for row in polar["shell_pairing"]["extra_Hermitian_current_Gram"]
        ]
    )
    assert sp.factor(gram[0, 0].subs({lam: 6, momentum: 0})) == 22464
    omega_e = sp.symbols("omega_e", real=True)
    basis = sp.Matrix(
        [
            [
                sp.sympify(
                    value.replace("lambda", "lam"),
                    locals={"lam": lam, "k": momentum, "omega_e": omega_e},
                )
                for value in row
            ]
            for row in polar["shell_pairing"]["extra_basis_order_At_B_Ct_U"]
        ]
    )
    assert tuple(basis[:, 0].subs({lam: 6, momentum: 0})) == POLAR_EXTRA["e2"]
    assert payload["current_normalization"]["direct_source_e2_equals_polar_current_first_basis_at_rest"] == [
        str(value) for value in POLAR_EXTRA["e2"]
    ]
    exceptional = _load(ROOT / inputs["sign_theorem"]["path"])
    assert exceptional["harmonic_sign_ledger"]["exceptional_extra_ell1"]["k_zero_Gram"] == ["16", "3"]


def _shell_check(payload: dict[str, Any]) -> None:
    mu = sp.symbols("mu")
    q = lambda lam, value: sp.factor(
        (mu**2 - 2 * lam * mu + lam * (lam - 2)).subs(mu, value)
    )
    assert [q(lam, 12) for lam in (6, 12)] == [24, -24]
    assert all(q(lam, sp.Rational(64, 3)) != 0 for lam in (6, 12, 20))
    ledger = payload["certified_bounded_functional_ledger"]
    assert ledger["X_plus_Y_q_residuals"] == {"6": "24", "12": "-24"}
    assert all(sp.sympify(value) != 0 for value in ledger["Y_plus_Y_q_residuals"].values())


def _rank_witness_check(payload: dict[str, Any]) -> None:
    witnesses = payload["complex_resonance_incidence"]["rank_stratum_witnesses_with_x_zero"]
    rank_three = sp.Matrix(witnesses["rank_3"])
    rank_two = sp.Matrix(witnesses["rank_2"])
    rank_one = sp.Matrix(
        [[sp.sympify(value, locals={"I": sp.I}) for value in row] for row in witnesses["rank_1_complex"]]
    )
    assert [rank_three.rank(), rank_two.rank(), rank_one.rank()] == [3, 2, 1]
    assert all(sp.trace(value) == 0 for value in (rank_three, rank_two, rank_one))
    assert rank_one != sp.zeros(3)


def verify_payload(payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    provenance = payload["provenance"]
    assert _sha256(ROOT / provenance["producer_path"]) == provenance["producer_sha256"]
    assert _sha256(ROOT / provenance["schema_path"]) == provenance["schema_sha256"]
    for record in provenance["inputs"].values():
        path = ROOT / record["path"]
        assert _sha256(path) == record["sha256"]
        assert _load(path)["result_id"] == record["result_id"]
    helper = provenance["source_helper"]
    assert _sha256(ROOT / helper["path"]) == helper["sha256"]
    assert payload["input_gate"]["exact_hashes"]["all_m_incidence"] == (
        "b4eed34422acf0574ec9098d1893ac5c5c496bfdf223e8e77bd483ef6adc7ab4"
    )
    assert subprocess.run(
        ["git", "merge-base", "--is-ancestor", payload["input_gate"]["required_commit"], "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    ).returncode == 0

    _rest_weights(payload)
    v1, v2_gram = _angular_forms()
    assert v1 == 4 * sp.pi / 3
    assert v2_gram.det() > 0
    _exceptional_self_zero_check()
    _shell_check(payload)
    _rank_witness_check(payload)

    maps = payload["moment_maps"]
    assert maps["five_maps"]["mu_H"].startswith("-(L/4)*sum_s")
    assert maps["strict_sign"]["positive_coefficients"] == [
        "L>0",
        "omega^2=k^2+4/3>0",
        "16>0",
        "3>0",
        "22464>0",
        "W1 positive",
        "W2 positive",
    ]
    for case in payload["physical_intersection_theorem"].values():
        assert case["physical_common_zero"] == "x_ax,s=x_pol,s=Y_s=0 for every retained direction s"
        assert case["real_radical"]["statement"].endswith("maximal ideal of the origin")
    assert payload["physical_intersection_theorem"]["k_zero"]["real_radical"]["number_of_real_generators"] == 22
    assert payload["physical_intersection_theorem"]["nonzero_abs_k_with_both_directions"]["real_radical"]["number_of_real_generators"] == 44

    classification = payload["classification"]
    assert classification["five_stabilizer_moment_maps_computed_in_cartesian_coordinates"] is True
    assert classification["positive_and_negative_travel_directions_retained_separately"] is True
    assert classification["rank_one_complex_stratum_survives_resonance_incidence"] is True
    assert classification["rank_one_real_STF_stratum_absent"] is True
    assert classification["physical_common_zero_is_origin"] is True
    assert classification["opposite_direction_resonance_only_complex_variety_classified"] is False
    assert classification["causal_all_orders_residual_observer_particle_quantum_claim"] is False


def verify_certificate() -> None:
    payload = _load(CERTIFICATE)
    verify_payload(payload)
    atlas = _load(ATLAS)
    assert atlas["generated_by_sha256"] == _sha256(ROOT / atlas["generated_by"])
    assert len(atlas["entries"]) == 1
    entry = atlas["entries"][0]
    assert entry["evidence"][0]["sha256"] == _sha256(CERTIFICATE)
    assert entry["mode_data"]["taub_maps"]["status"] == "CERTIFIED"
    assert entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] == "OBSTRUCTED"
    assert entry["mode_data"]["second_order"]["smooth_secular"]["status"] == "OBSTRUCTED"
    assert entry["mode_data"]["second_order"]["causal_retarded"]["status"] == "NO_CERTIFIED_MAP"


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ALL_M_MOMENT_INTERSECTION_V1 independent verification: PASS")
