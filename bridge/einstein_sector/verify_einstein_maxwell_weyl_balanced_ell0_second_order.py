"""Independent exact verifier for the balanced mixed second-order extension."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import (
    _action_operator,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_balanced_ell0_second_order.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expr(value: str, local: dict[str, sp.Expr] | None = None) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, **(local or {})})


def _vector(values: list[str], local: dict[str, sp.Expr] | None = None) -> sp.Matrix:
    return sp.Matrix([_expr(value, local) for value in values])


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == _sha256(ROOT / provenance["generator_path"])
    assert provenance["tensor_helper_sha256"] == _sha256(ROOT / provenance["tensor_helper_path"])
    assert provenance["polar_operator_engine_sha256"] == _sha256(ROOT / provenance["polar_operator_engine_path"])
    for relative_path, expected_hash in provenance["inputs"].items():
        assert expected_hash == _sha256(ROOT / relative_path)

    noether_audit = payload["dependent_row_completion"]["Noether_completion"]
    lam, frequency = sp.symbols("lambda omega", real=True)
    local = {"I": sp.I, "lam": lam, "omega": frequency}
    noether = sp.Matrix(
        [
            [sp.sympify(value.replace("lambda", "lam"), locals=local) for value in row]
            for row in noether_audit["k0_target_Noether_map"]
        ]
    )
    selector = sp.zeros(4, 8)
    for row, column in enumerate(noether_audit["independent_equation_indices"]):
        selector[row, column] = 1
    assert sp.factor(selector.col_join(noether).det()) == -4
    assert noether_audit["selector_plus_Noether_determinant"] == "-4"

    polarization = payload["real_channel_polarization"]
    assert (
        polarization["self_sum_factor"],
        polarization["self_zero_factor"],
        polarization["cross_sum_factor"],
        polarization["cross_difference_factor"],
    ) == ("1/8", "1/4", "1/4", "1/4")

    omega = sp.symbols("Omega", real=True)
    homogeneous = sp.Matrix(
        [[_expr(value, {"Omega": omega}) for value in row] for row in payload["homogeneous_operator"]["matrix"]]
    )
    expected = sp.Matrix(
        [[0, 0, 0], [-omega**4 / 2, omega**4 / 2, 0], [omega**4 / 4, -omega**4 / 4, 0], [0, 0, omega**2]]
    )
    assert homogeneous == expected
    for name, row in payload["homogeneous_channels"].items():
        if name in ("Einstein_zero", "extra_zero"):
            continue
        source = _vector(row["source_rows_E00_E11_E22_Maxwell1"])
        if name == "combined_zero":
            assert source == sp.zeros(4, 1)
            continue
        assert row["operator_remainder"] == ["0", "0", "0", "0"]
        if name in ("Einstein_self_sum", "extra_self_sum"):
            frequency = _expr(row["output_frequency"])
            correction = _vector(row["algebraic_correction_C_K_U"])
            assert (homogeneous.subs(omega, frequency) * correction + source).applyfunc(sp.simplify) == sp.zeros(4, 1)
        else:
            assert sp.simplify(source[0]) == 0
            assert sp.simplify(source[1] + 2 * source[2]) == 0

    action, (eigenvalue, momentum, frequency) = _action_operator()
    for ell, channels in payload["generic_polar_channels"].items():
        for name, row in channels.items():
            if name in ("Einstein_zero", "extra_zero"):
                continue
            assert row["operator_remainder"] == ["0", "0", "0", "0"]
            if name in ("Einstein_self_sum", "extra_self_sum", "combined_zero"):
                source = _vector(row["source_action_rows"])
                output_frequency = _expr(row["output_frequency"])
                correction = _vector(row["correction_At_B_Ct_U"])
                block = action.subs({eigenvalue: int(ell) * (int(ell) + 1), momentum: 0, frequency: output_frequency})
                assert (block * correction + source).applyfunc(sp.simplify) == sp.zeros(4, 1)
            else:
                assert row["correction_At_B_Ct_U"]

    classification = payload["classification"]
    assert classification["all_dependent_polar_tensor_rows_Noether_completed"] is True
    assert classification["real_channel_factors_certified"] is True
    assert classification["fixed_charge_and_reality_audit_passed"] is True
    assert payload["global_charge_reality_audit"]["all_declared_charge_and_reality_checks_pass"] is True
    for row in payload["homogeneous_channels"].values():
        correction = row.get("algebraic_correction_C_K_U")
        if correction is not None:
            assert correction[2] == "0"
    assert classification["complete_second_order_extension_constructed"] is True
    assert classification["remaining_adjoint_obstruction_exhibited"] is False
    assert payload["second_order_correction"]["complete_for_declared_tangent"] is True
    assert payload["second_order_correction"]["all_operator_remainders_zero"] is True


if __name__ == "__main__":
    verify_certificate()
