#!/usr/bin/env python3
"""Independent verifier for the rank-46 branch-projector solver contract."""

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
    _adjoint,
    _identity,
    _multiply,
    _subtract,
)
from d_quotient_classical.backreacted_clock.berger_support_local_q2 import (
    _fixture_linear,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_SOLVER_CONTRACT_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-46-stf2-branch-projector-solver-contract-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix(path: Path):
    record = json.loads(path.read_text())
    return [
        [_fixture_linear(entry) for entry in row]
        for row in _matrix_from_record(record)
    ]


def verify() -> dict:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for record in value["dependency_refs"].values():
        path = ROOT / record["path"]
        if _sha256(path) != record["sha256"]:
            raise ValueError(f"solver-contract dependency drifted: {path}")
    for path_text, expected in value["provenance"]["source_manifest"].items():
        path = ROOT / path_text
        if _sha256(path) != expected:
            raise ValueError(f"solver-contract source drifted: {path}")

    carrier_path = ROOT / value["dependency_refs"]["rank_46_STF2_graph_carrier"]["path"]
    carrier = json.loads(carrier_path.read_text())
    artifacts = carrier["artifacts"]
    U = _matrix(ROOT / artifacts["graph_shear_U_46"]["path"])
    U_inverse = _matrix(ROOT / artifacts["graph_shear_U_46_inverse"]["path"])
    omega = _matrix(ROOT / artifacts["omega_46"]["path"])
    if not _is_zero(_subtract(_multiply(U, U_inverse), _identity(46))):
        raise ValueError("solver-contract graph shear inverse failed")
    if not _is_zero(
        _subtract(_multiply(_multiply(_adjoint(U), omega), U), omega)
    ):
        raise ValueError("solver-contract graph shear cyclicity failed")

    partition = value["row_partition"]
    flattened = sorted(sum(partition.values(), []))
    if flattened != list(range(46)):
        raise ValueError("solver-contract row partition is not exhaustive")
    if len(partition["gravity_configuration_rows"]) ** 2 != 225:
        raise ValueError("solver-contract independent coefficient count failed")
    equations = value["exact_acceptance_equations"]
    for marker in ("P_E^2=P_E", "[q1_46,P_E]=[q1_46,P_X]=0", "[K_Berger_46,P_E]=[K_Berger_46,P_X]=0"):
        if marker not in equations:
            raise ValueError(f"solver-contract equation missing: {marker}")
    if value["claim_flags"]["BRANCH_PROJECTOR_ACCEPTED"]:
        raise ValueError("solver contract promoted to projector")
    if value["claim_flags"]["ELL3_BRANCH_MIXING_AUTHORIZED"]:
        raise ValueError("solver contract promoted to mixing table")
    return value


if __name__ == "__main__":
    verify()
    print("BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_SOLVER_CONTRACT_V1 independent verification: PASS")
