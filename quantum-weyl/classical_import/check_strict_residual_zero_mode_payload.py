#!/usr/bin/env python3
"""Independently replay the serialized strict residual zero-mode payload."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def matrix(payload: dict[str, Any], label: str, errors: list[str]) -> sp.Matrix:
    try:
        rows, columns = payload["shape"]
        output = sp.zeros(rows, columns)
        seen: set[tuple[int, int]] = set()
        for row, column, raw in payload["entries"]:
            key = (row, column)
            if key in seen or not (0 <= row < rows and 0 <= column < columns):
                errors.append(f"{label} duplicate or out-of-range entry")
                continue
            seen.add(key)
            value = sp.Rational(raw)
            if value == 0:
                errors.append(f"{label} explicitly stores zero")
            output[row, column] = value
        body = {"shape": [rows, columns], "entries": payload["entries"]}
        if payload.get("nonzero_entries") != len(seen) or payload.get("sha256") != digest(body):
            errors.append(f"{label} count or canonical hash")
        return output
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"{label} malformed: {exc}")
        return sp.zeros(0)


def structure_tensor(payload: dict[str, Any], errors: list[str]) -> list[list[list[sp.Rational]]]:
    tensor = [[[sp.Rational(0) for _ in range(15)] for _ in range(15)] for _ in range(15)]
    seen: set[tuple[int, int, int]] = set()
    for first, second, target, raw in payload.get("entries", []):
        key = (first, second, target)
        if key in seen or any(not 0 <= index < 15 for index in key):
            errors.append("structure tensor duplicate or out-of-range entry")
            continue
        seen.add(key)
        value = sp.Rational(raw)
        if value == 0:
            errors.append("structure tensor explicitly stores zero")
        tensor[first][second][target] = value
    body = {
        "convention": payload.get("convention"),
        "generator_order": payload.get("generator_order"),
        "generator_compact_degrees": payload.get("generator_compact_degrees"),
        "entries": payload.get("entries"),
        "tensor_shape": payload.get("tensor_shape"),
    }
    if payload.get("nonzero_entries") != len(seen) or payload.get("sha256") != digest(body):
        errors.append("structure tensor count or canonical hash")
    return tensor


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value.get("schema") != "strict-residual-zero-mode-payload-v1" or value.get("result_id") != "STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1":
        errors.append("result identity")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
        errors.append("dependency tags")

    zero = value.get("zero_mode_basis", {})
    matrices = zero.get("matrices", {})
    decoded = {name: matrix(payload, name, errors) for name, payload in matrices.items()}
    expected_shapes = {
        "ce_to_ckv_permutation": (15, 15),
        "gauge_map_K": (50, 65),
        "cyclic_adjoint_K_sharp": (65, 50),
        "gauge_endpoint_pairing": (65, 65),
        "metric_equation_pairing": (50, 50),
        "primal_basis_Z": (65, 15),
        "primal_coordinate_map": (15, 65),
        "primal_projector": (65, 65),
        "dual_basis_Z_dual": (65, 15),
        "dual_quotient_map": (15, 65),
        "dual_projector": (65, 65),
    }
    if set(decoded) != set(expected_shapes) or any(decoded.get(name, sp.zeros(0)).shape != shape for name, shape in expected_shapes.items()):
        errors.append("matrix inventory or shapes")
        return errors

    permutation = decoded["ce_to_ckv_permutation"]
    K = decoded["gauge_map_K"]
    K_sharp = decoded["cyclic_adjoint_K_sharp"]
    J_GI = decoded["gauge_endpoint_pairing"]
    J_ME = decoded["metric_equation_pairing"]
    primal = decoded["primal_basis_Z"]
    primal_coordinates = decoded["primal_coordinate_map"]
    P_primal = decoded["primal_projector"]
    dual = decoded["dual_basis_Z_dual"]
    dual_coordinates = decoded["dual_quotient_map"]
    P_dual = decoded["dual_projector"]

    if permutation.T * permutation != sp.eye(15):
        errors.append("CE/CKV permutation")
    if K.rank() != 50 or primal.rank() != 15 or K * primal != sp.zeros(50, 15):
        errors.append("primal kernel")
    if primal_coordinates * primal != sp.eye(15) or P_primal != primal * primal_coordinates or P_primal * P_primal != P_primal:
        errors.append("primal coordinates/projector")
    if J_GI.rank() != 65 or J_ME.rank() != 50 or J_GI * K_sharp != K.T * J_ME:
        errors.append("cyclic adjoint")
    if K_sharp.rank() != 50 or dual.rank() != 15 or dual_coordinates * K_sharp != sp.zeros(15, 50):
        errors.append("dual quotient")
    if dual_coordinates * dual != sp.eye(15) or P_dual != dual * dual_coordinates or P_dual * P_dual != P_dual:
        errors.append("dual coordinates/projector")
    if primal.T * J_GI * dual != sp.eye(15):
        errors.append("primal-dual normalized pairing")
    if sp.Matrix.hstack(K_sharp, dual).rank() != 65:
        errors.append("endpoint direct-sum decomposition")

    zero_body = {key: zero[key] for key in (
        "coefficient_field", "chart_ordering", "canonical_generator_order",
        "canonical_dual_order", "compact_degrees", "dual_compact_degrees",
        "legacy_ckv_order", "matrices",
    )}
    if zero.get("sha256") != digest(zero_body):
        errors.append("zero-mode basis hash")
    if len(zero.get("chart_ordering", {}).get("gauge_parameter_65", [])) != 65 or len(zero.get("chart_ordering", {}).get("metric_50", [])) != 50:
        errors.append("chart ordering")

    structure_payload = value.get("so42_structure_constants", {})
    f = structure_tensor(structure_payload, errors)
    names = structure_payload.get("generator_order", [])
    if len(names) != 15 or len(set(names)) != 15:
        errors.append("generator order")
    for first in range(15):
        if sum(f[first][second][second] for second in range(15)) != 0:
            errors.append("unimodularity")
            break
        for second in range(15):
            if any(f[first][second][target] + f[second][first][target] != 0 for target in range(15)):
                errors.append("antisymmetry")
                break
    jacobi_defects = 0
    for first in range(15):
        for second in range(15):
            for third in range(15):
                for target in range(15):
                    defect = sum(
                        f[second][third][middle] * f[first][middle][target]
                        + f[third][first][middle] * f[second][middle][target]
                        + f[first][second][middle] * f[third][middle][target]
                        for middle in range(15)
                    )
                    jacobi_defects += int(defect != 0)
    if jacobi_defects:
        errors.append(f"Jacobi defects {jacobi_defects}")

    representation = value.get("residual_representation", {})
    records = representation.get("matrices", [])
    if len(records) != 15:
        errors.append("representation matrix count")
    rhos: list[sp.Matrix] = []
    for generator, record in enumerate(records):
        adjoint = matrix(record.get("adjoint_on_Z", {}), f"adjoint[{generator}]", errors)
        coadjoint = matrix(record.get("coadjoint_on_Z_dual", {}), f"coadjoint[{generator}]", errors)
        rho = matrix(record.get("rho_on_Z_plus_Z_dual", {}), f"rho[{generator}]", errors)
        expected_adjoint = sp.Matrix(15, 15, lambda target, source: f[generator][source][target])
        if record.get("generator_index") != generator or record.get("generator") != names[generator]:
            errors.append(f"representation label {generator}")
        if adjoint != expected_adjoint or coadjoint != -adjoint.T or rho != sp.diag(adjoint, coadjoint):
            errors.append(f"representation coefficients {generator}")
        rhos.append(rho)
    if len(rhos) == 15:
        for first in range(15):
            for second in range(15):
                expected = sp.zeros(30)
                for target in range(15):
                    expected += f[first][second][target] * rhos[target]
                if rhos[first] * rhos[second] - rhos[second] * rhos[first] != expected:
                    errors.append(f"representation bracket {first},{second}")
                    break
    representation_body = {
        "carrier_order": representation.get("carrier_order"),
        "matrices": representation.get("matrices"),
        "representation_identity": representation.get("representation_identity"),
    }
    if representation.get("sha256") != digest(representation_body):
        errors.append("representation payload hash")

    q_res = value.get("residual_differential_q_res_0", {})
    q_matrix = matrix(q_res.get("degree_zero_unary_matrix", {}), "q_res_0", errors)
    if q_matrix.shape != (30, 30) or q_matrix != sp.zeros(30) or q_matrix * q_matrix != sp.zeros(30):
        errors.append("q_res_0")
    q_body = {key: q_res[key] for key in (
        "carrier_order", "degree_zero_unary_matrix", "meaning", "nonlinear_CE_structure_sha256"
    )}
    if q_res.get("sha256") != digest(q_body) or q_res.get("nonlinear_CE_structure_sha256") != structure_payload.get("sha256"):
        errors.append("q_res_0 hash/link")

    canonical = value.get("canonical_hashes", {})
    expected_canonical = {
        "zero_mode_basis_sha256": zero.get("sha256"),
        "structure_constants_sha256": structure_payload.get("sha256"),
        "representation_matrices_sha256": representation.get("sha256"),
        "q_res_0_sha256": q_res.get("sha256"),
    }
    if canonical != expected_canonical:
        errors.append("canonical hashes")
    snapshot = value.get("residual_snapshot", {})
    snapshot_body = {key: snapshot[key] for key in ("theory", "background", "canonical_hashes", "input_sha256")}
    if snapshot.get("sha256") != digest(snapshot_body) or snapshot.get("canonical_hashes") != canonical:
        errors.append("residual snapshot hash")
    for path, expected in snapshot.get("input_sha256", {}).items():
        source = ROOT / path
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            errors.append("input provenance " + path)

    flags = value.get("claim_flags", {})
    for key in (
        "STRICT_PRIMAL_FIFTEEN_MODE_BASIS_SERIALIZED",
        "STRICT_DUAL_FIFTEEN_MODE_BASIS_SERIALIZED",
        "STRICT_SO42_STRUCTURE_CONSTANTS_SERIALIZED",
        "STRICT_RESIDUAL_REPRESENTATION_MATRICES_SERIALIZED",
        "STRICT_Q_RES_0_SERIALIZED",
        "STRICT_RESIDUAL_ZERO_MODE_IDENTITIES_REPLAYED",
        "M5_RESIDUAL_EXACT_PAYLOAD_COMPLETE",
    ):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("COMMON_GATE_A_FREEZE_BOUND", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
        if flags.get(key) is not False:
            errors.append("fail-closed flag " + key)
    expected_digest = digest({
        "zero_mode_basis": zero,
        "so42_structure_constants": structure_payload,
        "residual_representation": representation,
        "residual_differential_q_res_0": q_res,
        "residual_snapshot": snapshot,
        "claim_flags": flags,
    })
    if value.get("independent_checker", {}).get("expected_digest") != expected_digest:
        errors.append("independent digest")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_RESIDUAL_ZERO_MODE_PAYLOAD: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
