"""Independent verifier for the compact moment-map/Taub bridge."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_polar_lee_wald_gate import (
    _time_current_matrix,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_moment_map_taub_bridge.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expr(value: str, local: dict[str, sp.Expr]) -> sp.Expr:
    return sp.sympify(value.replace("lambda", "lam"), locals=local)


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    assert payload["provenance"]["generator_sha256"] == _sha256(ROOT / payload["provenance"]["generator_path"])
    for record in payload["provenance"]["inputs"].values():
        assert record["sha256"] == _sha256(ROOT / record["path"])

    records = {
        name: json.loads((ROOT / record["path"]).read_text(encoding="utf-8"))
        for name, record in payload["provenance"]["inputs"].items()
    }
    l, k, w = sp.symbols("lambda k omega", real=True)
    local = {"lam": l, "k": k, "omega": w, "I": sp.I}
    extra_gram = sp.Matrix(
        [[_expr(value, local) for value in row] for row in records["axial_extra_pairing"]["pairing"]["normalized_Gram"]]
    ).subs({l: 6, k: 0, w: 4 / sp.sqrt(3)})
    direct_extra = sp.Matrix(
        [[sp.sympify(value) for value in row] for row in records["extra_taub_fixture"]["quadratic_source"]["constant_lapse_Taub_matrix"]]
    )
    assert (-sp.Rational(16, 3) * sp.Rational(1, 20) * extra_gram).applyfunc(sp.simplify) == direct_extra

    root = sp.sqrt(3)
    omega_squared = 6 - 2 * root
    axial_norm = _expr(
        records["axial_pairing"]["full_solution_pairing"]["Einstein_minus_branch_norm"],
        {"lam": l, "sqrt": sp.sqrt},
    ).subs(l, 6)
    axial_direct = _expr(
        records["einstein_taub_fixture"]["weyl_maxwell_taub"]["cosine_amplitude_matrix_A_P"][0][0],
        {"sqrt": sp.sqrt},
    )
    assert sp.simplify(-axial_norm / 20 - axial_direct) == 0

    current, symbols = _time_current_matrix()
    sl, sk, w1, w2 = symbols["lambda"], symbols["k"], symbols["omega_1"], symbols["omega_2"]
    omega = sp.sqrt(omega_squared)
    representative = sp.Matrix([12, 0, 12 - 24 * root, 6])
    action_current = (current / 2).subs({sl: 6, sk: 0, w1: omega, w2: omega})
    polar_fixture_gram = sp.simplify((representative.T * action_current * representative)[0] / (-sp.I * omega) / 36)
    polar_direct = _expr(
        records["einstein_taub_fixture"]["weyl_maxwell_taub"]["cosine_amplitude_matrix_A_P"][1][1],
        {"sqrt": sp.sqrt},
    )
    assert sp.simplify(-omega_squared * polar_fixture_gram / 20 - polar_direct) == 0

    tau = sp.symbols("tau", real=True)
    symplectic = sp.Matrix([[0, sp.I * w], [-sp.I * w, 0]])
    real_part = sp.Matrix([sp.Rational(1, 2), sp.Rational(1, 2)])
    actions = {
        "H": sp.diag(-sp.I * w, sp.I * w),
        "P_x": sp.diag(sp.I * k, -sp.I * k),
        "J_a": sp.diag(sp.I * tau, -sp.I * tau),
    }
    factors = {
        name: sp.simplify((real_part.T * symplectic * action * real_part)[0] / 2)
        for name, action in actions.items()
    }
    assert factors == {"H": -w**2 / 4, "P_x": k * w / 4, "J_a": tau * w / 4}
    assert payload["generic_moment_maps"]["complex_to_real_algebra"]["exact"] is True

    assert records["axial_pairing"]["full_solution_pairing"]["extra_branch_signature_for_lambda_ge_6"] == [2, 0]
    assert records["polar_pairing"]["shell_pairing"]["extra_positive_frequency_inertia"] == [2, 0]
    classification = payload["classification"]
    assert classification["generic_covariant_moment_map_Taub_equality_certified"] is True
    assert classification["all_nonzero_generic_pure_extra_fixed_bundle_tangents_second_order_obstructed"] is True
    assert classification["mixed_Einstein_extra_zero_locus_classified"] is False
    assert classification["absolute_stabilizer_quotient_certified"] is False
    assert payload["verification_receipt"]["tier_0"]["status"] == "PASS"
    assert payload["verification_receipt"]["tier_1"]["status"] == "PASS"


if __name__ == "__main__":
    verify_certificate()
