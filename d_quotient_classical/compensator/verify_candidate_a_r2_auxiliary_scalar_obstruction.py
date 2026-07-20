#!/usr/bin/env python3
"""Independent replay of the Candidate-A auxiliary-scalaron obstruction.

This consumer intentionally does not import the producer.  It reconstructs
the auxiliary action, mixed cylinder Hessian, homogeneous full-equation
sector, Lee-Wald form, D evolution/charge, Einstein control and Berger
residual from the serialized certificate.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_CANDIDATE_A_R2_AUXILIARY_SCALAR_OBSTRUCTION_V1.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def dense(record: dict, locals_map: dict[str, object] | None = None) -> sp.Matrix:
    matrix = sp.zeros(record["row_count"], record["column_count"])
    for item in record["entries"]:
        matrix[item["row"], item["column"]] = sp.sympify(
            item["coefficient"], locals=locals_map or {}
        )
    stripped = dict(record)
    claimed = stripped.pop("sha256")
    if claimed != digest(stripped):
        raise AssertionError("independent matrix digest failure")
    return matrix


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text())
    if (
        payload["result_id"]
        != "COMPENSATOR_CANDIDATE_A_R2_AUXILIARY_SCALAR_OBSTRUCTION_V1"
        or payload["result_state"] != "OBSTRUCTED"
        or payload["dependency_tags"]
        != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    ):
        raise AssertionError("Candidate-A lifecycle boundary drifted")

    for item in payload["dependencies"].values():
        path = ROOT / item["path"]
        if sha(path) != item["sha256"]:
            raise AssertionError(f"dependency drift: {item['path']}")
        imported = json.loads(path.read_text())
        if imported.get("result_id", imported.get("schema")) != item["result_id"]:
            raise AssertionError(f"dependency identity drift: {item['path']}")

    R, chi, psi = sp.symbols("R chi psi")
    beta = -sp.Rational(1, 144)
    auxiliary = chi * R - chi**2 / (4 * beta) + R / 12 - sp.Rational(1, 4)
    shifted = sp.expand(auxiliary.subs(chi, psi - sp.Rational(1, 12)))
    if sp.expand(shifted - (psi * (R - 6) + 36 * psi**2)) != 0:
        raise AssertionError("independent auxiliary shift failed")
    if sp.expand(
        auxiliary.subs(chi, 2 * beta * R)
        + (R - 6) ** 2 / 144
    ) != 0:
        raise AssertionError("independent auxiliary elimination failed")

    mixed_record = payload["full_non_Einstein_Hessian_and_BV"][
        "full_action_hessian"
    ]["mixed_block_polynomial"]
    z = sp.symbols("z0:4", real=True)
    mixed = dense(mixed_record, {str(value): value for value in z})
    if mixed.T != mixed or mixed[10, 10] != 72:
        raise AssertionError("independent mixed-Hessian adjoint replay failed")

    P = sp.Symbol("P")
    scalar = payload["homogeneous_scalar_full_Hessian_sector"]
    H = dense(
        scalar["second_order_scalar_parent"]["H(P_2)"],
        {"P": P},
    )
    inverse = dense(
        scalar["second_order_scalar_parent"]["formal_inverse"],
        {"P": P},
    )
    if H != sp.Matrix([[0, -3 * P], [-3 * P, 72]]):
        raise AssertionError("independent scalar Hessian replay failed")
    if sp.simplify(H * inverse) != sp.eye(2):
        raise AssertionError("independent scalar Green inverse replay failed")

    velocity = dense(scalar["Lee_Wald_and_sign"]["velocity_Hessian"])
    if velocity.eigenvals() != {-3: 1, 3: 1}:
        raise AssertionError("independent kinetic-sign replay failed")
    omega = dense(scalar["Lee_Wald_and_sign"]["Cauchy_symplectic_matrix"])
    A = dense(scalar["D_evolution_and_charge"]["D_matrix"])
    K = dense(scalar["D_evolution_and_charge"]["Hamiltonian_Hessian"])
    lam = sp.Symbol("lambda")
    if (
        omega.det() != 81
        or A.T * omega + omega * A != sp.zeros(4)
        or A.T * omega != K
        or sp.factor(A.charpoly(lam).as_expr()) != (lam**2 - 2) ** 2
        or A**2 - 2 * sp.eye(4) == sp.zeros(4)
        or (A**2 - 2 * sp.eye(4)) ** 2 != sp.zeros(4)
    ):
        raise AssertionError("independent D/Lee-Wald/Jordan replay failed")

    if sp.Rational(1, 6) / (12 * beta) != -2:
        raise AssertionError("independent Einstein mass cross-check failed")

    q = sp.Rational(9, 40)
    Rb = (4 - q) / 2
    old_lambda = sp.Rational(119, 480)
    delta_F = Rb / 6 + beta * Rb**2 - (1 - old_lambda) / 4
    delta_F_prime = sp.Rational(1, 6) + 2 * beta * Rb
    ricci = [0, (2 - q) / 2, (2 - q) / 2, q / 2]
    metric = [-1, 1, 1, 1]
    residual = [
        sp.factor(delta_F_prime * ricci[i] - delta_F * metric[i] / 2)
        for i in range(4)
    ]
    serialized = [
        sp.Rational(value)
        for value in payload["comparison_disposition"]["Berger_compatibility"][
            "orthonormal_metric_Euler_residual"
        ]
    ]
    if residual != serialized or any(value == 0 for value in residual):
        raise AssertionError("independent Berger mismatch replay failed")

    gates = payload["comparison_disposition"]["seven_gate_disposition"]
    if (
        [row["gate"] for row in gates] != list(range(1, 8))
        or gates[4]["status"] != "FAIL"
        or gates[5]["status"] != "FAIL"
        or gates[6]["status"] != "FAIL"
        or payload["claim_flags"]["HADAMARD_STATE"]
        or payload["claim_flags"]["QUANTUM_MASTER_EQUATION"]
    ):
        raise AssertionError("Candidate-A fail-closed gate ledger drifted")

    print(
        "COMPENSATOR_CANDIDATE_A_R2_AUXILIARY_SCALAR_OBSTRUCTION_V1 "
        "INDEPENDENT REPLAY: PASS"
    )


if __name__ == "__main__":
    main()
