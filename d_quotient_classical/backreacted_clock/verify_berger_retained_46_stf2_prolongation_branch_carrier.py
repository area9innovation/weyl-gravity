#!/usr/bin/env python3
"""Independent exact verifier for the rank-46 STF2 graph carrier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (
    _matrix_from_record,
)
from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
    _is_zero,
)
from d_quotient_classical.backreacted_clock.berger_portable_coupled_64_unary_pairing_sdr import (
    _add,
    _adjoint,
    _identity,
    _multiply,
    _subtract,
)
from d_quotient_classical.backreacted_clock.berger_support_local_q2 import (
    _fixture_linear,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-46-stf2-prolongation-branch-carrier-v1.schema.json"
TYPED_36 = ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR.json"
WAVE = ROOT / "d_quotient_classical/generated/berger_metric_lower_by_two_biwave/rough_tensor_wave.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(record: dict):
    return [
        [_fixture_linear(entry) for entry in row]
        for row in _matrix_from_record(record)
    ]


def _artifact(payload: dict, name: str):
    record = payload["artifacts"][name]
    path = ROOT / record["path"]
    if _sha256(path) != record["sha256"]:
        raise AssertionError(f"artifact digest drifted: {name}")
    raw = json.loads(path.read_text())
    if raw["shape"] != record["shape"]:
        raise AssertionError(f"artifact shape drifted: {name}")
    return _fixture(raw)


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator(schema).validate(payload)
    for dependency in payload["dependency_refs"].values():
        path = ROOT / dependency["path"]
        if _sha256(path) != dependency["sha256"]:
            raise AssertionError(f"dependency digest drifted: {path}")
    for key in ("producer", "verifier", "tests", "schema"):
        path = ROOT / payload["provenance"][key]
        if _sha256(path) != payload["provenance"][f"{key}_sha256"]:
            raise AssertionError(f"provenance digest drifted: {key}")

    q = _artifact(payload, "q1_46")
    omega = _artifact(payload, "omega_46")
    iota = _artifact(payload, "iota_36_to_46")
    projection = _artifact(payload, "pi_46_to_36")
    homotopy = _artifact(payload, "S_46")
    T = _artifact(payload, "stf2_extractor_T")
    J = _artifact(payload, "stf2_right_inverse_J")
    F = _artifact(payload, "stf2_wave_F")
    typed = json.loads(TYPED_36.read_text())
    q36 = _fixture(typed["retained_complex"]["classical_unary_q1"])
    omega36 = _fixture(typed["retained_complex"]["typed_cyclic_pairing"])
    wave = _fixture(json.loads(WAVE.read_text()))

    checks = {
        "q1_46_squared_zero": _is_zero(_multiply(q, q)),
        "omega_46_antisymmetric": _is_zero(_add(_adjoint(omega), omega)),
        "q1_46_typed_cyclic": _is_zero(_add(_multiply(_adjoint(q), omega), _multiply(omega, q))),
        "pi_iota_identity": _is_zero(_subtract(_multiply(projection, iota), _identity(36))),
        "iota_chain_map": _is_zero(_subtract(_multiply(q, iota), _multiply(iota, q36))),
        "pi_chain_map": _is_zero(_subtract(_multiply(projection, q), _multiply(q36, projection))),
        "contraction_identity": _is_zero(_subtract(_add(_multiply(q, homotopy), _multiply(homotopy, q)), _subtract(_identity(46), _multiply(iota, projection)))),
        "homotopy_square_zero": _is_zero(_multiply(homotopy, homotopy)),
        "homotopy_iota_zero": _is_zero(_multiply(homotopy, iota)),
        "pi_homotopy_zero": _is_zero(_multiply(projection, homotopy)),
        "homotopy_typed_cyclic": _is_zero(_add(_multiply(_adjoint(homotopy), omega), _multiply(omega, homotopy))),
        "pairing_induced_by_iota": _is_zero(_subtract(_multiply(_multiply(_adjoint(iota), omega), iota), omega36)),
        "stf2_right_inverse": _is_zero(_subtract(_multiply(T, J), _identity(5))),
        "stf2_wave_order_two": max(entry.maximum_order for row in F for entry in row if entry.terms) == 2,
    }
    if checks != payload["exact_checks"] or not all(checks.values()):
        raise AssertionError(f"independent carrier replay failed: {checks}")
    if not _is_zero(_subtract(F, _multiply(T, wave))):
        raise AssertionError("F is not the exact T_STF Box_2 composite")

    rows = payload["carrier"]["component_rows"]
    if [row["index"] for row in rows] != list(range(46)):
        raise AssertionError("rank-46 row ordering drifted")
    degrees = [row["degree"] for row in rows]
    if [degrees.count(value) for value in (-1, 0, 1, 2)] != [4, 19, 19, 4]:
        raise AssertionError("rank-46 degree multiplicities drifted")
    if payload["flags"]["CANONICAL_BRANCH_PROJECTOR_CERTIFIED"]:
        raise AssertionError("carrier promoted to projector")
    if payload["flags"]["ELL3_BRANCH_MIXING_AUTHORIZED"]:
        raise AssertionError("carrier promoted to mixing table")
    print("BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1 independent verification: PASS")


if __name__ == "__main__":
    main()
