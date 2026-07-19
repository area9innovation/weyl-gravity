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
    nariai_crosswalk = by_id["classical.nariai.crosswalk.normal_tractor_cylinder_to_metric"]
    if set(nariai_crosswalk["descriptions"].values()) != {"NO_CERTIFIED_MAP"}:
        raise AssertionError("Nariai normal-tractor cylinder crosswalk overpromoted")
    if "rank-310" not in nariai_crosswalk["claim_boundary"]:
        raise AssertionError("Nariai replacement carrier boundary missing")
    berger_crosswalk = by_id["classical.berger.crosswalk.retained36_to_einstein_extra"]
    if set(berger_crosswalk["descriptions"].values()) != {"NO_CERTIFIED_MAP"}:
        raise AssertionError("Berger Bridge 1 overpromoted")
    if "Bridge 1 is not activated" not in berger_crosswalk["claim_boundary"]:
        raise AssertionError("Berger Bridge 1 activation gate missing")
    transverse = by_id["classical.nariai.transverse_kantowski_sachs_tangent"]

    bach_open = by_id["classical.bach_flat.open_parent_detour"]
    bach_ids = {item["result_id"] for item in bach_open["evidence"]}
    if "BACH_FLAT_RANK310_NATURAL_SDR_V1" not in bach_ids:
        raise AssertionError("class-wide Bach-flat rank-310 SDR missing")
    if "BACH_FLAT_METRIC_BIWAVE_GREEN_HOMOTOPY_V1" not in bach_ids:
        raise AssertionError("class-wide Bach-flat metric homotopy missing")
    if "BACH_FLAT_RANK310_CAUSAL_TRANSFER_V1" not in bach_ids:
        raise AssertionError("class-wide Bach-flat rank-310 causal transfer missing")
    if "pure normal-tractor-parent-to-metric crosswalk remains fail-closed" not in bach_open["claim_boundary"]:
        raise AssertionError("Bach-flat pure-parent crosswalk boundary missing")
    if transverse["descriptions"]["causal"] != "CERTIFIED":
        raise AssertionError("formal transverse causal theorem missing")
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
    if "NARIAI_TRANSVERSE_RELATIVE_SADDLE_UPPER_CHAIN_V1" not in transverse_ids:
        raise AssertionError("upper relative-saddle replay missing")
    if "NARIAI_TRANSVERSE_FACTORIZED_ENDPOINT_COMPLETION_V1" not in transverse_ids:
        raise AssertionError("factorized endpoint target missing")
    if "NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1" not in transverse_ids:
        raise AssertionError("action Bach-Hessian variation missing")
    if "NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION_V1" not in transverse_ids:
        raise AssertionError("complete rank-310 SDR variation missing")
    if "NARIAI_TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION_V1" not in transverse_ids:
        raise AssertionError("formal metric Green variation missing")
    if "NARIAI_TRANSVERSE_GLOBAL_HPL_RANK310_CAUSAL_VARIATION_V1" not in transverse_ids:
        raise AssertionError("global HPL rank-310 causal variation missing")
    if "NARIAI_RANK310_FINITE_HPL_INCIDENCE_THEOREM_V1" not in transverse_ids:
        raise AssertionError("finite HPL incidence theorem missing")
    if "factorized adjunction before PBW normal ordering" not in transverse["claim_boundary"]:
        raise AssertionError("factorized Hom-adjoint boundary missing")
    if "direct action-leading coefficients plus Noether uniqueness" not in transverse["claim_boundary"]:
        raise AssertionError("action-Hessian closure boundary missing")
    if "tangent theorem at epsilon=0" not in transverse["claim_boundary"]:
        raise AssertionError("next transverse causal boundary missing")
    if "nonlocal-denominator" not in transverse["claim_boundary"]:
        raise AssertionError("finite HPL consequence missing")
    transverse_exact = by_id["classical.nariai.transverse_kantowski_sachs_exact_branch"]
    if transverse_exact["descriptions"]["causal"] != "CERTIFIED":
        raise AssertionError("KS common-slab metric Green theorem missing")
    if transverse_exact["descriptions"]["nonlinear"] != "OBSTRUCTED":
        raise AssertionError("transverse exact-family obstruction missing")
    if transverse_exact["mode_data"]["second_order"]["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("slabwise family was promoted to a global causal bridge")
    exact_ids = {item["result_id"] for item in transverse_exact["evidence"]}
    if "NARIAI_KS_FOUR_BLOCK_INCIDENCE_OBSTRUCTION_V1" not in exact_ids:
        raise AssertionError("finite KS incidence obstruction missing")
    if "NARIAI_RANK310_SIX_BLOCK_FINITE_HPL_V1" not in exact_ids:
        raise AssertionError("six-block finite HPL theorem missing")
    if "NARIAI_KS_COMMON_SLAB_CAUSAL_DOMAIN_V1" not in exact_ids:
        raise AssertionError("KS common-slab causal-domain theorem missing")
    if "EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1" not in exact_ids:
        raise AssertionError("Einstein metric biwave theorem missing")
    if "NARIAI_KS_RANK310_COMMON_SLAB_GREEN_TRANSFER_V1" not in exact_ids:
        raise AssertionError("KS rank-310 common-slab transfer missing")
    if "two forced quadratic metric cross terms" not in transverse_exact["claim_boundary"]:
        raise AssertionError("six-block HPL consequence missing")
    if "complete four-row metric endpoint" not in transverse_exact["claim_boundary"]:
        raise AssertionError("metric endpoint promotion missing")
    if "exact rank-310 advanced/retarded homotopies" not in transverse_exact["claim_boundary"]:
        raise AssertionError("rank-310 transfer was not promoted")
    if "not a whole-cylinder theorem" not in transverse_exact["claim_boundary"]:
        raise AssertionError("whole-cylinder boundary was lost")


if __name__ == "__main__":
    verify()
    print("CLASSICAL_CAUSAL_RESIDUAL_ATLAS_FRAGMENT_V1 independent verification: PASS")
