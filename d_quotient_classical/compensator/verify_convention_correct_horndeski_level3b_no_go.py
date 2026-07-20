#!/usr/bin/env python3
"""Independent raw-ADM and cylinder replay of the Level-3b no-go."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/COMPENSATOR_CONVENTION_CORRECT_HORNDESKI_LEVEL3B_NO_GO_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/compensator-convention-correct-horndeski-level3b-no-go-v1.schema.json"
IMPORT_HASHES = {
    "literal_level3": "2e687331b6985b3a84c54a0f05b210bee5e3ac06d5659b5603ac9bc25f61dfed",
    "P2_freeze": "9bda4b758616427bdbf401a499ffd2b7cd9dd69a87223f05fcdf636bb31cd533",
    "trace_obstruction": "db1f998a0920adb94cf4fcbffb1b9eb2ea6537876aff9513aac4e4d9ec2b51b9",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _dense(record: dict[str, Any]) -> sp.Matrix:
    result = sp.zeros(record["row_count"], record["column_count"])
    for item in record["entries"]:
        result[item["row"], item["column"]] = sp.sympify(item["coefficient"])
    return result


def _raw_adm_replay(payload: dict[str, Any]) -> None:
    X, F, Fx, h, A = sp.symbols("X F F_X h A")
    box_over_y = A - 3 * h
    Hessian2_over_y2 = A**2 + 3 * h**2
    Q = sp.expand(-X * (box_over_y**2 - Hessian2_over_y2))
    if Q != -6 * X * h**2 + 6 * X * A * h:
        raise AssertionError("RAW_Q_REPLAY_MISMATCH")
    F_R_reduced = -6 * F * h**2 + 12 * X * Fx * A * h
    corrected = sp.expand(F_R_reduced - 2 * Fx * Q)
    if sp.expand(corrected + 6 * (F - 2 * X * Fx) * h**2) != 0:
        raise AssertionError("HORNDESKI_CANCELLATION_REPLAY_MISMATCH")
    H = sp.hessian(corrected, (h, A))
    if H.det() != 0 or H * sp.Matrix([0, 1]) != sp.zeros(2, 1):
        raise AssertionError("HORNDESKI_DEGENERACY_REPLAY_MISMATCH")
    if _dense(payload["exact_adm_degeneracy"]["velocity_Hessian"]) != H:
        raise AssertionError("SERIALIZED_ADM_HESSIAN_MISMATCH")


def _stationary_replay(payload: dict[str, Any]) -> None:
    M = sp.Matrix(
        [[0, 36, 3, 1, 0, 0, 0], [0, 12, -1, -1, 0, 0, 0]]
    )
    serialized = _dense(
        payload["complete_cylinder_stationary_locus"]["stationary_matrix"]
    )
    if serialized != M or M.rank() != 2 or len(M.nullspace()) != 5:
        raise AssertionError("CYLINDER_STATIONARY_REPLAY_MISMATCH")
    alpha_R, M2, p0 = sp.symbols("alpha_R M2 p0")
    solution = sp.solve(
        [36 * alpha_R + 3 * M2 + p0, 12 * alpha_R - M2 - p0],
        [M2, p0],
        dict=True,
    )
    if solution != [{M2: -24 * alpha_R, p0: 36 * alpha_R}]:
        raise AssertionError("CYLINDER_SOLUTION_REPLAY_MISMATCH")


def _quadratic_replay(payload: dict[str, Any]) -> None:
    p1, f1, w2, k2 = sp.symbols("p1 f1 omega_squared k_squared")
    symbol = sp.factor(
        2 * p1 * (-w2 + k2) - 4 * f1 * (3 * w2 - k2)
    )
    expected = -2 * (p1 + 6 * f1) * w2 + 2 * (p1 + 2 * f1) * k2
    if sp.expand(symbol - expected) != 0:
        raise AssertionError("CLOCK_SYMBOL_REPLAY_MISMATCH")
    if sp.factor(
        sp.sympify(payload["full_cylinder_quadratic_separator"]["clock_symbol"])
        - symbol
    ) != 0:
        raise AssertionError("SERIALIZED_CLOCK_SYMBOL_MISMATCH")
    split = sp.Matrix([[0, -3], [-3, 0]])
    P = sp.Matrix([[1, 1], [1, -1]])
    if P.T * split * P != sp.diag(-6, 6):
        raise AssertionError("SPLIT_CONGRUENCE_REPLAY_MISMATCH")


def verify(value: dict[str, Any] | None = None) -> None:
    payload = value if value is not None else json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    for name, expected in IMPORT_HASHES.items():
        item = payload["imports"][name]
        if _sha(ROOT / item["path"]) != expected or item["sha256"] != expected:
            raise AssertionError(f"{name} import drifted")
    _raw_adm_replay(payload)
    _stationary_replay(payload)
    _quadratic_replay(payload)
    for field, section in (
        ("imports_sha256", "imports"),
        ("adm_sha256", "exact_adm_degeneracy"),
        ("stationary_sha256", "complete_cylinder_stationary_locus"),
        ("hessian_sha256", "full_cylinder_quadratic_separator"),
        ("strata_sha256", "stratified_no_go"),
        ("unary_sha256", "unary_constraint_charge_and_gates"),
        ("verdict_sha256", "terminal_verdict"),
    ):
        if payload["content_hashes"][field] != _digest(payload[section]):
            raise AssertionError(f"{field} drifted")
    if (
        payload["stratified_no_go"]["common_seven_gate_good_locus"] != "EMPTY"
        or payload["terminal_verdict"]["selected_level3b_action"]
        or payload["unary_constraint_charge_and_gates"]["selected_action"]
        or payload["unary_constraint_charge_and_gates"]["support_local_causal_parent"]
        or payload["unary_constraint_charge_and_gates"]["nonlinear_q2"]
        or any(payload["claim_flags"].values())
    ):
        raise AssertionError("CLAIM_BOUNDARY_DRIFT")


def main() -> None:
    verify()
    print(
        "COMPENSATOR_CONVENTION_CORRECT_HORNDESKI_LEVEL3B_NO_GO_V1 "
        "independent raw-ADM/cylinder replay: PASS"
    )


if __name__ == "__main__":
    main()
