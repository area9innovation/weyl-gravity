#!/usr/bin/env python3
"""Independent audit of the parity-odd third-curvature completeness blocker."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = (
    HERE
    / "certificates/PARITY_ODD_THIRD_CURVATURE_CARRIER_MANIFEST_PREFLIGHT.json"
)
SCHEMA = (
    HERE
    / "schema/parity-odd-third-curvature-carrier-manifest-preflight-v1.schema.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rejects(schema: dict, payload: dict) -> bool:
    return bool(list(Draft202012Validator(schema).iter_errors(payload)))


def verify() -> dict:
    stored = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(stored)

    # This rail does not import or call the producer. It follows the stored
    # dependency paths and independently verifies both their content hashes
    # and the precise open-operation statements that force the obstruction.
    dependencies = {}
    for name, reference in stored["dependencies"].items():
        path = ROOT / reference["path"]
        if _sha256(path) != reference["sha256"]:
            raise ValueError(f"independent dependency hash mismatch: {name}")
        payload = json.loads(path.read_text())
        if payload["result_id"] != reference["result_id"]:
            raise ValueError(f"independent result-id mismatch: {name}")
        dependencies[name] = payload

    even = dependencies["parity_even_nonlocal_manifest"]
    algebraic = dependencies["algebraic_cubic_weyl_carriers"]
    schouten = dependencies["four_dimensional_even_schouten_quotient"]
    weyl = dependencies["schouten_zero_weyl_image"]
    ambient = dependencies["ambient_intrinsic_orbits"]
    if even["scope"]["parity"] != "EVEN_ONLY":
        raise ValueError("even source unexpectedly claims odd completeness")
    if algebraic["tensor_carriers"]["parity_dimensions"]["odd"] != 1:
        raise ValueError("algebraic odd existence anchor disappeared")
    if schouten["checks"]["parity_odd_weyl_sector"] != "NOT_COMPUTED":
        raise ValueError("four-dimensional source no longer has declared odd gap")
    if weyl["odd_companion"]["status"] != "CONSTRUCTED_NOT_A_COMPLETE_BASIS":
        raise ValueError("odd Hodge companion boundary drifted")
    required_open = {
        "algebraic_and_differential_Bianchi",
        "covariant_jet_commutators",
        "integration_by_parts_quotient",
        "dimension_specific_antisymmetrization",
    }
    if any(ambient["next_gates"][name] != "NOT_COMPUTED" for name in required_open):
        raise ValueError("ambient open-operation ledger drifted")
    if ambient["next_gates"]["total_degrees_five_six_intrinsic_orbits"] != (
        "NOT_COMPUTED_FACTORED_ONLY"
    ):
        raise ValueError("degree-six materialization boundary drifted")

    operation = stored["first_missing_operation"]
    if set(operation["quotient_by"]) != {
        "algebraic and differential Bianchi syzygies",
        "covariant-jet commutator syzygies through curvature order three",
        "integration-by-parts syzygies over the labelled-Laplacian module",
        "four-dimensional five-index Schouten syzygies with one epsilon",
        "locally exact Pontryagin/transgression submodule",
    }:
        raise ValueError("first missing syzygy operation is incomplete")
    request = json.loads(
        (
            ROOT
            / "planning/forge-requests/"
            "single-epsilon-labelled-jet-syzygy-quotient.json"
        ).read_text()
    )
    if (
        request["id"] != stored["forge_request"]["request_id"]
        or request["body"]["state"] != "REQUESTED"
        or "quantum-parity-odd-third-curvature-carrier-manifest"
        not in request["body"]["depends_on"][0]
    ):
        raise ValueError("typed Forge request does not close the recorded gap")

    mutations = []
    for flag in (
        "PARITY_ODD_DERIVATIVE_CARRIER_MANIFEST_COMPLETE",
        "PARITY_ODD_QUOTIENT_DIMENSION_COMPUTED",
        "PARITY_EVEN_DUALIZATION_ASSUMED_COMPLETE",
        "NUMERICAL_SAMPLING_PROMOTED",
        "PONTRYAGIN_CLASS_CONFLATED_WITH_NONLOCAL_ODD_SECTOR",
        "COEFFICIENT_COMPUTED",
        "QME_OR_LORENTZIAN_PROMOTED",
    ):
        mutation = deepcopy(stored)
        mutation["claim_flags"][flag] = True
        mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["decision"]["quotient_dimension"] = 10
    mutations.append(mutation)
    mutation = deepcopy(stored)
    mutation["first_missing_operation"]["quotient_by"].pop()
    mutations.append(mutation)
    for mutation in mutations:
        if not _rejects(schema, mutation):
            raise ValueError("claim-boundary mutation passed the strict schema")

    print("parity-odd third-curvature preflight independent audit: PASS")
    return stored


if __name__ == "__main__":
    verify()
