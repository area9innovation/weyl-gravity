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
    berger = by_id["classical.berger.retained_gravity_clock_maxwell"]
    berger_evidence = {item["result_id"] for item in berger["evidence"]}
    if (
        "BERGER_26_ROW_SMOOTH_BIKERNEL_HOMOTOPY_SUPPORT_GATE_V1"
        not in berger_evidence
        or "cutoff-escape continuity obstruction"
        not in berger["claim_boundary"]
        or "no one-sided support profile" not in berger["claim_boundary"]
    ):
        raise AssertionError("Berger bikernel support gate missing or overpromoted")
    for family in "eal":
        entry = by_id[f"classical.vacuum_cylinder.one_particle.{family}"]
        if entry["descriptions"]["causal"] != "CERTIFIED" or "not a positive residual particle" not in entry["claim_boundary"]:
            raise AssertionError("vacuum mode boundary drifted")
    for chirality in ("plus", "minus"):
        entry = by_id[f"classical.vacuum_cylinder.deformation.w_{chirality}_squared"]
        if "not a one-particle mode" not in entry["scope"]["carrier"]:
            raise AssertionError("W-square was promoted to particle")
        if "GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1" not in {
            item["result_id"] for item in entry["evidence"]
        }:
            raise AssertionError("vacuum transfer-theorem crosswalk absent")
    nariai = by_id["classical.nariai.conformal_orbit.rank310_metric"]
    if (
        "GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1"
        not in {item["result_id"] for item in nariai["evidence"]}
        or "does not identify it with the conformal-cylinder modes"
        not in nariai["claim_boundary"]
    ):
        raise AssertionError("Nariai transfer-theorem boundary drifted")
    wz = by_id["classical.vacuum_cylinder.local_bv.wz_tau_adic_d_cartan"]
    wz_ids = {item["result_id"] for item in wz["evidence"]}
    if (
        "WESS_ZUMINO_D_CARTAN_CONTRACTION_V1" not in wz_ids
        or wz["descriptions"]["symplectic"] != "CERTIFIED"
        or wz["descriptions"]["causal"] != "NOT_APPLICABLE"
        or wz["descriptions"]["quantum"] != "OPEN"
        or "not the Berger clock" not in wz["claim_boundary"]
        or "Minkowski D_M projection is explicitly not exported"
        not in wz["claim_boundary"]
    ):
        raise AssertionError("Wess-Zumino D-Cartan atlas boundary drifted")
    stability = by_id["classical.crosswalk.weak_background_causal_vs_residual_d"]
    if (
        stability["descriptions"]["causal"] != "CERTIFIED"
        or stability["descriptions"]["symplectic"] != "NO_CERTIFIED_MAP"
        or "WEAK_BACKGROUND_CAUSAL_VS_D_STABILITY_V1"
        not in {item["result_id"] for item in stability["evidence"]}
        or "Causal stability and residual-D stability are separate"
        not in stability["claim_boundary"]
        or "NO_CERTIFIED_MAP" not in stability["claim_boundary"]
        or "Hadamard and quantum claims remain open" not in stability["claim_boundary"]
    ):
        raise AssertionError("weak-background causal-versus-D boundary drifted")
    crosswalk = by_id["classical.crosswalk.bach_flat_parent_to_metric"]
    if set(crosswalk["descriptions"].values()) != {"NO_CERTIFIED_MAP"}:
        raise AssertionError("parent/metric crosswalk overpromoted")
    nariai_crosswalk = by_id["classical.nariai.crosswalk.normal_tractor_cylinder_to_metric"]
    if set(nariai_crosswalk["descriptions"].values()) != {"NO_CERTIFIED_MAP"}:
        raise AssertionError("Nariai normal-tractor cylinder crosswalk overpromoted")
    if "rank-310" not in nariai_crosswalk["claim_boundary"]:
        raise AssertionError("Nariai replacement carrier boundary missing")
    candidate13 = by_id["classical.crosswalk.candidate13_reduced_source_to_local_bv"]
    if candidate13["descriptions"]["causal"] != "NO_CERTIFIED_MAP":
        raise AssertionError("candidate-13 reduced source was promoted causally")
    if candidate13["descriptions"]["nonlinear"] != "OBSTRUCTED":
        raise AssertionError("candidate-13 category obstruction missing")
    if "new local equation-level cofiber" not in candidate13["claim_boundary"]:
        raise AssertionError("candidate-13 obstruction was overgeneralized")
    de_rham = by_id["classical.crosswalk.compact_product_five_current_de_rham_carrier"]
    if de_rham["descriptions"]["symplectic"] != "CERTIFIED" or de_rham["descriptions"]["causal"] != "NO_CERTIFIED_MAP":
        raise AssertionError("five-current de Rham carrier lifecycle changed")
    if de_rham["descriptions"]["nonlinear"] != "CERTIFIED":
        raise AssertionError("five-current de Rham q2 interface theorem missing")
    if "EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_Q2_V1" not in {item["result_id"] for item in de_rham["evidence"]}:
        raise AssertionError("five-current de Rham q2 evidence missing")
    if "eighteen spectral resonance" not in de_rham["claim_boundary"]:
        raise AssertionError("five-current carrier was overextended to candidate-13 resonances")
    completion = by_id["classical.crosswalk.compact_product_relative_238_cyclic_completion"]
    if completion["descriptions"]["symplectic"] != "OBSTRUCTED" or completion["descriptions"]["nonlinear"] != "OBSTRUCTED":
        raise AssertionError("fixed 238-row cyclic rank obstruction missing")
    if completion["descriptions"]["causal"] != "NO_CERTIFIED_MAP":
        raise AssertionError("fixed 238-row obstruction was overpromoted causally")
    if "at least 28 rows" not in completion["claim_boundary"] or "necessary rather than sufficient" not in completion["claim_boundary"]:
        raise AssertionError("fixed 238-row minimal-enlargement boundary missing")
    if "EINSTEIN_WEYL_RELATIVE_238_ROW_CYCLIC_RANK_OBSTRUCTION_V1" not in {item["result_id"] for item in completion["evidence"]}:
        raise AssertionError("fixed 238-row rank evidence missing")
    cotangent = by_id["classical.crosswalk.compact_product_relative_316_cotangent_carrier"]
    if cotangent["descriptions"]["symplectic"] != "CERTIFIED" or cotangent["descriptions"]["nonlinear"] != "OBSTRUCTED":
        raise AssertionError("316-row unary cotangent lifecycle changed")
    if cotangent["descriptions"]["causal"] != "NO_CERTIFIED_MAP":
        raise AssertionError("316-row cotangent carrier was overpromoted causally")
    if "not either standard action-derived form" not in cotangent["claim_boundary"] or "full-domain q2 is obstructed" not in cotangent["claim_boundary"]:
        raise AssertionError("316-row cotangent claim boundary missing")
    if "EINSTEIN_WEYL_RELATIVE_316_BLOCK_DIAGONAL_Q2_OBSTRUCTION_V1" not in {item["result_id"] for item in cotangent["evidence"]}:
        raise AssertionError("316-row projected q2 obstruction missing")
    pullback = by_id["classical.crosswalk.compact_product_derived_taub_zero_pullback"]
    if pullback["descriptions"]["nonlinear"] != "OPEN" or pullback["descriptions"]["causal"] != "NO_CERTIFIED_MAP":
        raise AssertionError("derived Taub-zero pullback gate was overpromoted")
    if pullback["descriptions"]["symplectic"] != "OPEN":
        raise AssertionError("derived pullback action-pairing comparison was overpromoted")
    if "does not restrict the unary tangent complex" not in pullback["claim_boundary"]:
        raise AssertionError("quadratic Taylor placement missing from atlas")
    if "EINSTEIN_WEYL_RELATIVE_DERIVED_TAUB_ZERO_PULLBACK_PREFLIGHT_V1" not in {item["result_id"] for item in pullback["evidence"]}:
        raise AssertionError("derived pullback preflight evidence missing")
    if pullback["mode_data"]["second_order"]["smooth_secular"]["status"] != "CERTIFIED":
        raise AssertionError("reduced smooth factorization theorem missing")
    if pullback["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] != "OPEN":
        raise AssertionError("smooth factorization was overpromoted to bounded corrections")
    if "not a serialized all-mode PBW matrix" not in pullback["claim_boundary"]:
        raise AssertionError("abstract quotient-coordinate matrix was overpromoted")
    if "EINSTEIN_WEYL_RELATIVE_REDUCED_TAUB_FACTORIZATION_V1" not in {item["result_id"] for item in pullback["evidence"]}:
        raise AssertionError("reduced Taub factorization evidence missing")
    if "EINSTEIN_WEYL_RELATIVE_SHIFTED_CURRENT_CONE_PREFLIGHT_V1" not in {item["result_id"] for item in pullback["evidence"]}:
        raise AssertionError("shifted current-cone preflight evidence missing")
    if "degree-zero chain map A:K_P->C_W" not in pullback["claim_boundary"]:
        raise AssertionError("typed support-local lift missing from atlas")
    if "not the existing block-diagonal 316 profile" not in pullback["claim_boundary"]:
        raise AssertionError("distinct 316-row gradings were conflated")
    if "EINSTEIN_WEYL_RELATIVE_FULL_FIVE_CURRENT_PBW_EXPORT_V1" not in {item["result_id"] for item in pullback["evidence"]}:
        raise AssertionError("portable full-current evidence missing")
    if "30,494 canonical terms" not in pullback["claim_boundary"] or "V1 current table" not in pullback["claim_boundary"]:
        raise AssertionError("portable current scope or order boundary missing")
    if "EINSTEIN_WEYL_RELATIVE_ORDER_ZERO_LIFT_OBSTRUCTION_V1" not in {item["result_id"] for item in pullback["evidence"]}:
        raise AssertionError("order-zero lift obstruction evidence missing")
    if "rank 305" not in pullback["claim_boundary"] or "Order two" not in pullback["claim_boundary"]:
        raise AssertionError("order-zero obstruction scope missing")
    if "EINSTEIN_WEYL_RELATIVE_ENDPOINT_NORMALIZATION_V1" not in {item["result_id"] for item in pullback["evidence"]}:
        raise AssertionError("endpoint normalization evidence missing")
    if "A2(P_X^4)=X^mu c_mu_star" not in pullback["claim_boundary"]:
        raise AssertionError("endpoint normalization formula missing")
    if "EINSTEIN_WEYL_RELATIVE_ORDER_ONE_INVARIANT_ANSATZ_V1" not in {item["result_id"] for item in pullback["evidence"]}:
        raise AssertionError("order-one invariant ansatz evidence missing")
    if "406 unknowns" not in pullback["claim_boundary"] or "complete through coefficient-jet order two" not in pullback["claim_boundary"]:
        raise AssertionError("order-one solver contract missing")
    evidence_ids = {item["result_id"] for item in pullback["evidence"]}
    if "EINSTEIN_WEYL_RELATIVE_HESSIAN_SECOND_CURRENT_INPUT_V1" not in evidence_ids:
        raise AssertionError("second-current Hessian coefficient-depth evidence missing")
    if "EINSTEIN_WEYL_RELATIVE_FULL_FIVE_CURRENT_SECOND_JET_EXPORT_V1" not in evidence_ids:
        raise AssertionError("streamed second-current export evidence missing")
    if "36,539 canonical terms" not in pullback["claim_boundary"] or "twenty independently hashed chunks" not in pullback["claim_boundary"]:
        raise AssertionError("streamed second-current census missing")
    if "EINSTEIN_WEYL_RELATIVE_ORDER_ONE_CHAIN_OBSTRUCTION_V1" not in evidence_ids:
        raise AssertionError("order-one chain obstruction evidence missing")
    if "rank 398 and augmented rank 399" not in pullback["claim_boundary"]:
        raise AssertionError("order-one obstruction ranks missing")
    if "before f2 can be tested" not in pullback["claim_boundary"]:
        raise AssertionError("f2 dependency boundary missing")
    if "EINSTEIN_WEYL_RELATIVE_ORDER_TWO_OBSTRUCTION_SENSITIVITY_V1" not in evidence_ids:
        raise AssertionError("order-two obstruction-sensitivity evidence missing")
    if "626-dimensional invariant A1 order-two symbol space" not in pullback["claim_boundary"]:
        raise AssertionError("order-two invariant sensitivity census missing")
    if "sensitivity has rank one and is surjective" not in pullback["claim_boundary"]:
        raise AssertionError("order-two obstruction quotient action missing")
    if "does not establish that a simultaneous order-two chain map exists" not in pullback["claim_boundary"]:
        if "complete endpoint-normalized chain map is obstructed through order two" not in pullback["claim_boundary"]:
            raise AssertionError("order-two sensitivity disposition missing")
    if "EINSTEIN_WEYL_RELATIVE_ORDER_TWO_TOP_DESCENT_OBSTRUCTION_V1" not in evidence_ids:
        raise AssertionError("legal order-two top-descent evidence missing")
    if "1056-by-712 matrix" not in pullback["claim_boundary"] or "kernel dimension 196" not in pullback["claim_boundary"]:
        raise AssertionError("legal top-descent census missing")
    if "four-row exact rowspace witness" not in pullback["claim_boundary"]:
        raise AssertionError("top-descent rowspace witness missing")
    if "EINSTEIN_WEYL_RELATIVE_ORDER_THREE_DESCENT_OBSTRUCTION_V1" not in evidence_ids:
        raise AssertionError("order-three descent-obstruction evidence missing")
    if "all 5,600 raw cubic A1 coefficients" not in pullback["claim_boundary"]:
        raise AssertionError("order-three raw cubic census missing")
    if "complete endpoint-normalized chain map is obstructed through order three" not in pullback["claim_boundary"]:
        raise AssertionError("order-three obstruction disposition missing")
    if "EINSTEIN_WEYL_RELATIVE_ALL_ORDER_ENDPOINT_PAIRING_OBSTRUCTION_V1" not in evidence_ids:
        raise AssertionError("all-order endpoint-pairing obstruction evidence missing")
    if "EINSTEIN_WEYL_RELATIVE_COMPENSATED_ENDPOINT_CHAIN_OBSTRUCTION_V1" not in evidence_ids:
        raise AssertionError("compensated endpoint chain obstruction evidence missing")
    if "fixed diffeomorphism-only endpoint is obstructed at every finite differential order" not in pullback["claim_boundary"]:
        raise AssertionError("all-order fixed-endpoint disposition missing")
    if "corrected endpoint A2_comp" not in pullback["claim_boundary"]:
        raise AssertionError("correlated Maxwell endpoint repair missing")
    if "rank 3 and augmented rank 4" not in pullback["claim_boundary"]:
        raise AssertionError("compensated flat-symbol rank obstruction missing")
    if "xi has nonzero normal form modulo (tau,xi^2)" not in pullback["claim_boundary"]:
        raise AssertionError("compensated polynomial nonmembership missing")
    if "minimal GL(4)-covariant tensor-symbol repair adjoins Lambda^2(T^*M)" not in pullback["claim_boundary"]:
        raise AssertionError("minimal antisymmetric carrier repair missing")
    if "full chain map are absent" not in pullback["claim_boundary"]:
        raise AssertionError("compensated endpoint was overpromoted")
    if pullback["mode_data"]["taub_maps"]["status"] != "OBSTRUCTED":
        raise AssertionError("order-one relative incidence not fail-closed")
    berger_crosswalk = by_id["classical.berger.crosswalk.retained36_to_einstein_extra"]
    if set(berger_crosswalk["descriptions"].values()) != {"NO_CERTIFIED_MAP"}:
        raise AssertionError("Berger Bridge 1 overpromoted")
    if "Bridge 1 is not activated" not in berger_crosswalk["claim_boundary"]:
        raise AssertionError("Berger Bridge 1 activation gate missing")
    berger_cauchy = by_id[
        "classical.berger.crosswalk.retained26_to_frozen104_cauchy_bv"
    ]
    if berger_cauchy["descriptions"]["causal"] != "OBSTRUCTED":
        raise AssertionError("frozen Berger q26 Cauchy obstruction missing")
    if berger_cauchy["descriptions"]["quantum"] != "NO_CERTIFIED_MAP":
        raise AssertionError("rejected Berger Cauchy carrier was promoted")
    if (
        "five new degree-zero rows and one new degree-one row"
        not in berger_cauchy["claim_boundary"]
        or "cyclic rank completion raises this to ten"
        not in berger_cauchy["claim_boundary"]
        or "at least 104 added rows"
        not in berger_cauchy["claim_boundary"]
        or "doubled-cone strictification is nilpotent"
        not in berger_cauchy["claim_boundary"]
        or "208 added, 312 total"
        not in berger_cauchy["claim_boundary"]
        or "cone cohomology (13,57,57,13)"
        not in berger_cauchy["claim_boundary"]
        or "retained q26 cohomology (1,1,1,1)"
        not in berger_cauchy["claim_boundary"]
        or "ranks (23,56,23)"
        not in berger_cauchy["claim_boundary"]
        or "not a PBW operator extension"
        not in berger_cauchy["claim_boundary"]
    ):
        raise AssertionError("Berger carrier-extension boundary missing")
    berger_cauchy_ids = {
        item["result_id"] for item in berger_cauchy["evidence"]
    }
    if "BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1" not in berger_cauchy_ids:
        raise AssertionError("Berger Cauchy obstruction evidence missing")
    if (
        "BERGER_Q26_MINIMAL_SIX_ROW_CYCLIC_OBSTRUCTION_V1"
        not in berger_cauchy_ids
    ):
        raise AssertionError("Berger minimal six-row cyclic evidence missing")
    if (
        "BERGER_Q26_FINITE_ROW_MODULE_CLOSURE_LOWER_BOUND_V1"
        not in berger_cauchy_ids
    ):
        raise AssertionError("Berger finite-row module closure evidence missing")
    if (
        "BERGER_Q26_104_ROW_CANONICAL_CONE_LIFT_OBSTRUCTION_V1"
        not in berger_cauchy_ids
    ):
        raise AssertionError("Berger canonical 104-row cone evidence missing")
    if (
        "BERGER_Q26_104_ROW_CONE_NEXT_DEFECT_MODULE_V1"
        not in berger_cauchy_ids
    ):
        raise AssertionError("Berger cone next-defect evidence missing")
    if (
        "BERGER_Q26_104_ROW_FULLY_MIXED_CONE_SDR_OBSTRUCTION_V1"
        not in berger_cauchy_ids
    ):
        raise AssertionError("Berger fully mixed cone SDR evidence missing")
    if (
        "BERGER_Q26_104_ROW_NONCONE_RATIONAL_NILPOTENCE_FEASIBILITY_V1"
        not in berger_cauchy_ids
    ):
        raise AssertionError("Berger non-cone feasibility evidence missing")
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
