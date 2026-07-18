#!/usr/bin/env python3
"""Independent fail-closed checks for the classical residual atlas."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
ATLAS = Path(__file__).with_name("classical-causal-atlas-fragment.json")
GENERATOR = Path(__file__).with_name("generate_classical_atlas_fragment.py")
SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    value = json.loads(ATLAS.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["generated_by_sha256"] != _sha(GENERATOR):
        raise AssertionError("generator hash mismatch")
    by_id = {entry["id"]: entry for entry in value["entries"]}
    if len(by_id) != len(value["entries"]):
        raise AssertionError("duplicate atlas id")
    for entry in value["entries"]:
        for evidence in entry["evidence"]:
            path = ROOT / evidence["path"]
            payload = json.loads(path.read_text())
            if _sha(path) != evidence["sha256"] or payload["result_id"] != evidence["result_id"]:
                raise AssertionError(f"evidence drift: {entry['id']}")
    for family in "eal":
        entry = by_id[f"classical.vacuum_cylinder.one_particle.{family}"]
        if entry["descriptions"]["causal"] != "CERTIFIED" or "not a positive residual particle" not in entry["claim_boundary"]:
            raise AssertionError("vacuum mode boundary drifted")
    for chirality in ("plus", "minus"):
        entry = by_id[f"classical.vacuum_cylinder.deformation.w_{chirality}_squared"]
        if "not a one-particle mode" not in entry["scope"]["carrier"]:
            raise AssertionError("W-square was promoted to particle")
    crosswalk = by_id["classical.crosswalk.bach_flat_parent_to_metric"]
    if set(crosswalk["descriptions"].values()) != {"NO_CERTIFIED_MAP"}:
        raise AssertionError("parent/metric crosswalk overpromoted")
    berger_crosswalk = by_id["classical.berger.crosswalk.retained36_to_einstein_extra"]
    if set(berger_crosswalk["descriptions"].values()) != {"NO_CERTIFIED_MAP"}:
        raise AssertionError("Berger Bridge 1 overpromoted")
    if "Bridge 1 is not activated" not in berger_crosswalk["claim_boundary"]:
        raise AssertionError("Berger Bridge 1 activation gate missing")
    transverse = by_id["classical.nariai.transverse_kantowski_sachs_tangent"]
    if transverse["descriptions"]["causal"] != "OPEN":
        raise AssertionError("transverse causal theorem overpromoted")
    transverse_ids = {item["result_id"] for item in transverse["evidence"]}
    if "NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1" not in transverse_ids:
        raise AssertionError("jet-aware parent-middle evidence missing")
    if "NARIAI_TRANSVERSE_FIRST_ORDER_SCHUR_SOLVE_V1" not in transverse_ids:
        raise AssertionError("first-order Schur evidence missing")
    if "NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1" not in transverse_ids:
        raise AssertionError("Phi-only shifted-chain obstruction evidence missing")
    if "NARIAI_TRANSVERSE_INCIDENCE_L1_RIGIDITY_V1" not in transverse_ids:
        raise AssertionError("incidence/L1 rigidity evidence missing")
    if "NARIAI_TRANSVERSE_NORMALIZED_L0_COUPLED_OBSTRUCTION_V1" not in transverse_ids:
        raise AssertionError("normalized-L0 coupled obstruction evidence missing")
    if "NARIAI_TRANSVERSE_K_SENSITIVITY_ADMISSIBILITY_V1" not in transverse_ids:
        raise AssertionError("K-sensitivity admissibility evidence missing")
    if "NARIAI_TRANSVERSE_PHI_SECOND_ORDER_OBSTRUCTION_V1" not in transverse_ids:
        raise AssertionError("order-two Phi obstruction evidence missing")
    if "NARIAI_TRANSVERSE_LINEARIZED_PBW_ASSOCIATIVITY_GATE_V1" not in transverse_ids:
        raise AssertionError("linearized PBW associativity gate missing")
    if "NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_REPLAY_V1" not in transverse_ids:
        raise AssertionError("associative middle replay missing")
    if "NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1" not in transverse_ids:
        raise AssertionError("factorized Hom/Schur replay missing")
    if "factorized adjunction before PBW normal ordering" not in transverse["claim_boundary"]:
        raise AssertionError("factorized Hom-adjoint boundary missing")
    if "upper relative-saddle row" not in transverse["claim_boundary"]:
        raise AssertionError("next rank-310 boundary missing")


if __name__ == "__main__":
    verify()
    print("CLASSICAL_CAUSAL_RESIDUAL_ATLAS_FRAGMENT_V1 independent verification: PASS")
