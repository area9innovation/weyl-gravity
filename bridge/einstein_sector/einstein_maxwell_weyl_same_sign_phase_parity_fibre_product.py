"""Assemble the exact bounded phase/parity fibre products for candidates 16--21."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_phase_parity_fibre_product.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_phase_parity_fibre_product.schema.json"
INPUTS = {
    "scalar_cones": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_scalar_occupation_cones.json",
    "sections": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_cone_sections.json",
    "same_fibre": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_same_fibre_census.json",
    "finite_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json",
    "isolated": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json",
    "target_doublet_L3": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_target_doublet_L3_zero_varieties.json",
    "scalar_L1": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L1_zero_varieties.json",
    "multiplicity_two_L3": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties.json",
    "regular_pencil_L4": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_regular_pencil_L4_zero_varieties.json",
    "scalar_L4": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L4_zero_varieties.json",
}

CANDIDATE_SOURCE = {
    16: "target_doublet_L3",
    17: "scalar_L1",
    18: "multiplicity_two_L3",
    19: "regular_pencil_L4",
    20: "scalar_L1",
    21: "scalar_L4",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decomposition(record: dict, candidate_index: int) -> dict:
    value = record["decompositions"]
    rows = value if isinstance(value, list) else [item for item in value.values() if isinstance(item, dict)]
    return next(row for row in rows if row.get("candidate_index") == candidate_index)


def geometry(row: dict) -> dict[str, object]:
    zero = row.get("zero_variety", row)
    components = zero.get("irreducible_components_over_C")
    if isinstance(components, list):
        component_count = len(components)
        dimensions = sorted({item["dimension_over_C"] for item in components})
    else:
        component_count = int(components)
        dimensions = [zero["dimension_over_C"]]
    result: dict[str, object] = {
        "ambient_dimension_over_C": zero["ambient_dimension_over_C"],
        "irreducible_components_over_C": component_count,
        "component_dimensions_over_C": dimensions,
    }
    if "factorization" in zero:
        result["factorization"] = zero["factorization"]
    return result


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    scalar = records["scalar_cones"]
    sections = records["sections"]
    same_fibre = records["same_fibre"]
    finite = records["finite_cone"]
    if not scalar["classification"]["all_six_scalar_occupation_cones_classified"]:
        raise AssertionError("scalar occupation theorem changed")
    if not sections["classification"]["bounded_to_scalar_occupation_projection_surjective"]:
        raise AssertionError("bounded section theorem changed")
    if not same_fibre["classification"]["all_864_target_shell_defects_nonzero"]:
        raise AssertionError("same-fibre census changed")
    if not finite["classification"]["complete_reduced_adjoint_cokernel_decomposition_certified"]:
        raise AssertionError("finite-harmonic cokernel theorem changed")
    if "exactly when all five mu_X and every finite R_" not in finite["bounded_resonance_functionals"]["necessity_and_sufficiency"]:
        raise AssertionError("bounded necessity-and-sufficiency theorem changed")

    scalar_rows = {row["candidate_index"]: row for row in scalar["candidate_rows"]}
    isolated_rows = {
        candidate_index: row
        for candidate_index, row in enumerate(records["isolated"]["candidate_ledger"]["rows"], start=1)
    }
    candidate_rows = []
    for candidate_index in range(16, 22):
        source_name = CANDIDATE_SOURCE[candidate_index]
        row = decomposition(records[source_name], candidate_index)
        isolated = isolated_rows[candidate_index]
        if row["rho"] != scalar_rows[candidate_index]["rho"] or row["rho"] != isolated["rho"]:
            raise AssertionError(f"candidate {candidate_index} background mismatch")
        if row["fibre_id"] != f"L{isolated['output_ell']}_candidate_{candidate_index}":
            raise AssertionError(f"candidate {candidate_index} carrier mismatch")
        candidate_rows.append({
            "candidate_index": candidate_index,
            "rho": row["rho"],
            "signed_momenta": [1, 2],
            "output_ell": isolated["output_ell"],
            "temporal_channel": isolated["admissible_temporal_channel"],
            "resonance_fibre_id": row["fibre_id"],
            "resonance_certificate": str(INPUTS[source_name].relative_to(ROOT)),
            "resonance_geometry": geometry(row),
            "physical_amplitude_carrier": "complex positive-frequency ell=2 axial/polar coefficients with conjugate reality completion",
            "bounded_cone_formula": {
                "display": "Z_i^bounded = pi_i^{-1}(C_i) intersect mu_J^{-1}(0) intersect V(B_i)",
                "occupation_map": "pi_i records the six nonnegative absolute-current occupations for q_minus,p_extra,q_plus on n=1,2",
                "scalar_factor": "C_i = {y>=0: mu_H(y)=mu_Px(y)=R_c(y)=0}, the certified four-ray scalar cone",
                "rotation_factor": "mu_J=(mu_J1,mu_J2,mu_J3)=0 on the physical amplitude carrier",
                "phase_parity_factor": f"V(B_i) is the zero set of the complete cross-fibre resonant map in {row['fibre_id']}",
                "same_fibre_factor": "no further nonzero-frequency condition: all 864 candidatewise target-shell defects exclude zero",
                "necessity_and_sufficiency": "the complete finite-harmonic reduced adjoint-cokernel theorem makes simultaneous vanishing equivalent to a bounded or finite-quasiperiodic second-order correction",
            },
            "verdict": "EXACT_EQUATIONAL_FIBRE_PRODUCT_CERTIFIED_REAL_COMPONENT_DECOMPOSITION_OPEN",
        })

    return {
        "schema": "einstein-maxwell-weyl-same-sign-phase-parity-fibre-product-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_PHASE_PARITY_FIBRE_PRODUCT",
        "result_state": "SIX_EXACT_BOUNDED_FIBRE_PRODUCT_FORMULAS_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_COMPLETE_EQUATIONAL_BOUNDED_CONE_FORMULA_ON_SIX_DISTINCT_COLLISION_BACKGROUNDS",
        "scope": {
            **sections["scope"],
            "carrier": "complete generic ell=2 axial/polar positive-frequency amplitude carrier on signed n=(1,2), with all relative phases and conjugate reality completion",
            "correction_class": "bounded or finite-quasiperiodic",
        },
        "candidate_rows": candidate_rows,
        "classification": {
            "all_six_bounded_cones_have_exact_necessary_and_sufficient_equational_formulas": True,
            "all_six_cross_fibre_complex_resonance_varieties_decomposed": True,
            "all_same_fibre_nonzero_frequency_rows_removable": True,
            "all_six_scalar_occupation_cones_classified": True,
            "bounded_projection_onto_every_scalar_cone_surjective": True,
            "all_relative_phases_and_both_parities_retained_in_formula": True,
            "all_three_rotation_moment_maps_retained_in_formula": True,
            "all_six_real_hermitian_phase_parity_intersections_decomposed": False,
            "componentwise_topology_or_singular_strata_classified": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The six open cones are no longer unspecified amplitude ideals. Each is an exact Hermitian-algebraic fibre product of a known four-ray occupation cone, the lifted SO(3) zero level, and a fully decomposed complex resonance variety. The remaining task is the real component and singular-stratum decomposition of these six intersections.",
        "next_gate": "decompose the six Hermitian intersections component by component, beginning with the irreducible odd-L candidates 16,17,18,20; do not rederive the scalar cone or cross-fibre complex varieties",
        "claim_boundary": "This is a complete necessary-and-sufficient equational description in the bounded correction class. It is not an irreducible real-semialgebraic decomposition, an all-orders theorem, or a causal, residual, observational or quantum map.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_phase_parity_fibre_product --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_phase_parity_fibre_product",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_phase_parity_fibre_product",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text() != rendered:
        raise AssertionError("same-sign phase/parity fibre-product certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_PHASE_PARITY_FIBRE_PRODUCT: PASS")


if __name__ == "__main__":
    main()
