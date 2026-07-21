#!/usr/bin/env python3
"""Independent exact replay of the counterflow causal-BV promotion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1.json"
RECEIVER = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_RECEIVER_CONTRACT_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _dense(record: dict[str, object]) -> sp.Matrix:
    matrix = sp.zeros(int(record["row_count"]), int(record["column_count"]))
    core = {"row_count": record["row_count"], "column_count": record["column_count"], "entries": record["entries"]}
    if _digest(core) != record["sha256"]:
        raise AssertionError("operator matrix hash failed")
    for entry in record["entries"]:
        matrix[int(entry["row"]), int(entry["column"])] = sp.Rational(entry["coefficient"])
    return matrix


def _check_imports(result: dict[str, object]) -> dict[str, object]:
    values = {}
    for key, row in result["imports"].items():
        path = ROOT / row["path"]
        value = json.loads(path.read_text())
        if _sha(path) != row["sha256"] or value["result_id"] != row["result_id"] or row["oracle_fields_consumed"] != []:
            raise AssertionError(f"import failed: {key}")
        values[key] = value
    if values["gauge_fixed_54"]["flags"]["BERGER_COMPLETE_GAUGE_FIXED_UNARY_EXPORT"] is not True:
        raise AssertionError("54-row BV carrier unavailable")
    if values["green_54"]["flags"]["BERGER_CAUSAL_GREEN_HOMOTOPY_V2"] is not True:
        raise AssertionError("54-row Green homotopy unavailable")
    if values["D_action_54"]["flags"]["BERGER_LOCAL_D_ACTION_EQUIVARIANT"] is not True:
        raise AssertionError("54-row K action unavailable")
    if values["K_Cartan_54"]["flags"]["BERGER_CAUSAL_D_CARTAN_V2"] is not True:
        raise AssertionError("54-row K Cartan unavailable")
    return values


def _check_action(values: dict[str, object], payload: dict[str, object]) -> None:
    selected = values["preflight"]["selected_fixture"]["parameters"]
    old = values["positive_clock"]["rational_fixture"]
    checks = {
        "alpha_B": sp.Rational(selected["alpha_B"]) == sp.Rational(old["alpha_B"]),
        "Omega": sp.Rational(selected["Omega"]) == sp.Rational(old["omega"]),
        "rho_squared": sp.Rational(old["rho_squared"]) == 1,
        "V0_equals_lambda_over_4": sp.Rational(selected["V0"]) == sp.Rational(old["lambda"]) / 4,
        "Einstein_from_conformal_coupling": sp.Rational(selected["M_P_squared"]) / 2 == -sp.Rational(1, 12),
        "relative_phase_coefficient": sp.Rational(selected["mu_squared"]) == 1,
    }
    if checks != payload["action_equivalence"]["checks"] or not all(checks.values()):
        raise AssertionError("action equivalence failed")
    # Direct square check in the selected normalization.
    x1, x2, a = sp.symbols("x1 x2 a")
    chi = (x1 + x2) / 2
    psi = x1 - x2
    if sp.expand(2 * (x1 - a) ** 2 + 2 * (x2 - a) ** 2 - 4 * (chi - a) ** 2 - psi**2) != 0:
        raise AssertionError("selected phase split failed")


def _check_u1(payload: dict[str, object]) -> None:
    extension = payload["u1_minimal_nonminimal_extension"]
    q = _dense(extension["Q_changed_basis"])
    s = _dense(extension["S_changed_basis"])
    if q**2 != sp.zeros(10) or q * s + s * q != sp.eye(10):
        raise AssertionError("independent algebraic SDR failed")
    if sum(extension["changed_basis_component_ranks"]) != 16:
        raise AssertionError("extension component count failed")

    # Replay the original-row nilpotency with d and delta treated as commuting
    # formal differential operators on this linear complex.
    chi, A, ghost, Astar, chistar, cstar, barc, b, bstar, barcstar = sp.symbols("chi A ghost Astar chistar cstar barc b bstar barcstar")
    d, delta = sp.symbols("d delta")
    variables = (chi, A, ghost, Astar, chistar, cstar, barc, b, bstar, barcstar)
    B = A - d * chi
    images = {chi: ghost, A: d * ghost, ghost: 0, Astar: -4 * B, chistar: 4 * delta * B, cstar: chistar + delta * Astar, barc: b, b: 0, bstar: -barcstar, barcstar: 0}

    def Q(expr: sp.Expr) -> sp.Expr:
        return sp.expand(sum(sp.diff(expr, variable) * images[variable] for variable in variables))

    if any(sp.simplify(Q(images[variable])) != 0 for variable in variables):
        raise AssertionError("original-row Q squared failed")
    e_A, e_chi = -4 * B, 4 * delta * B
    if sp.expand(e_chi + delta * e_A) != 0:
        raise AssertionError("action Noether identity failed")
    if extension["gauge_fixing"]["Coulomb_inverse"]:
        raise AssertionError("nonlocal Coulomb inverse introduced")


def _check_parent_and_cartan(result: dict[str, object], payload: dict[str, object]) -> None:
    parent = payload["complete_parent"]
    if parent["old_component_rank"] + parent["extension_component_rank"] != parent["complete_component_rank"] or parent["complete_component_rank"] != 70:
        raise AssertionError("70-component ledger failed")
    if not parent["no_spatial_inverse"] or not parent["zero_modes_retained"]:
        raise AssertionError("locality/zero-mode boundary failed")
    cartan = payload["Cartan_ledger"]
    if cartan["D"]["decomposition"] != "D=K+Omega R_rel" or "not gauge" not in cartan["D"]["charge"]:
        raise AssertionError("D/K decomposition failed")
    if cartan["K"]["identification"] != "the imported D_helical=partial_t plus compensating internal rotation":
        raise AssertionError("helical K crosswalk failed")
    if cartan["U1_diag"]["charge"] != "Q_diag=0 by local Gauss":
        raise AssertionError("diagonal U1 Cartan failed")
    flags = result["claim_flags"]
    forbidden = ("COULOMB_INVERSE", "UNRESTRICTED_D_GAUGE", "HADAMARD", "NONLINEAR_Q2", "QME_OR_QUANTUM")
    if any(flags[key] for key in forbidden):
        raise AssertionError("claim boundary promoted")


def _check_receiver(receiver: dict[str, object]) -> None:
    if _digest({k: v for k, v in receiver.items() if k != "content_sha256"}) != receiver["content_sha256"]:
        raise AssertionError("receiver canonical hash failed")
    if set(receiver["receivers"]) != {"Observer", "Nonlinear", "Bridge", "Quantum"}:
        raise AssertionError("receiver set incomplete")
    for row in receiver["receivers"].values():
        if row["required_parent_state"] != "CERTIFIED_70_COMPONENT_SUPPORT_LOCAL_CAUSAL_BV_PARENT" or len(row["forbidden_promotions"]) != 5:
            raise AssertionError("receiver fail-closed contract failed")


def verify() -> None:
    result = json.loads(RESULT.read_text())
    payload = json.loads(PAYLOAD.read_text())
    receiver = json.loads(RECEIVER.read_text())
    if _sha(PAYLOAD) != result["payload_ref"]["sha256"] or _sha(RECEIVER) != result["receiver_contract_ref"]["sha256"]:
        raise AssertionError("referenced artifact byte hash failed")
    if _digest({k: v for k, v in payload.items() if k != "content_sha256"}) != payload["content_sha256"]:
        raise AssertionError("payload canonical hash failed")
    values = _check_imports(result)
    _check_action(values, payload)
    _check_u1(payload)
    _check_parent_and_cartan(result, payload)
    _check_receiver(receiver)
    expected = {"parent_sha256": _digest(result["complete_parent"]), "Cartan_sha256": _digest(result["Cartan_ledger"]), "current_pairing_sha256": _digest(result["clock_current_and_pairing"]), "terminal_sha256": _digest(result["terminal_verdict"]), "boundary_sha256": _digest(result["claim_boundary"])}
    if result["content_hashes"] != expected:
        raise AssertionError("certificate content hashes failed")
    print("TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1 independent replay: PASS")


if __name__ == "__main__":
    verify()
