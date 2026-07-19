"""Crosswalk the candidate-13 cone into the relative Einstein--Weyl receiver."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_CANDIDATE13_DERIVED_SOURCE_CROSSWALK_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-relative-candidate13-derived-source-crosswalk-v1.schema.json"
INPUTS = {
    "linear_triangle": ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1.json",
    "branch_dictionary": ROOT / "bridge/certificates/einstein_weyl_relative_branch_dictionary.json",
    "current_cofiber_receiver": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CURRENT_COFIBER_ASSEMBLY_V1.json",
    "full_domain_f2_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_F2_TAUB_OBSTRUCTION_V1.json",
    "candidate13_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_complete_mixed_cone.json",
    "scalar_separation": ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_scalar_separation_no_go.json",
    "pressure_obstruction": ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_mixed_pressure_obstruction.json",
    "bounded_zero_block": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_bounded_zero_block.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    triangle = records["linear_triangle"]
    dictionary = records["branch_dictionary"]
    receiver = records["current_cofiber_receiver"]
    obstruction = records["full_domain_f2_obstruction"]
    cone = records["candidate13_cone"]
    separation = records["scalar_separation"]

    required_triangle_flags = {
        "OFF_SHELL_CHAIN_MAP_ALL_BV_ROWS",
        "SUPPORT_LOCAL_MAPPING_COFIBER",
        "GLOBAL_ENDPOINTS_INCLUDED",
        "THREE_ACTION_DERIVED_FORMS_EXPORTED",
        "GENERIC_STANDARD_PAIRING_CYCLIC_OBSTRUCTION_RESPECTED",
        "H_PRODUCT_EQUIVARIANT",
        "INDEPENDENT_VERIFIER_PASS",
    }
    actual_triangle_flags = {key for key, value in triangle["acceptance_flags"].items() if value}
    require(required_triangle_flags <= actual_triangle_flags, "relative linear triangle acceptance changed")
    dictionary_flags = dictionary["classification"]
    require(dictionary_flags["generic_axial_and_polar_solution_cofibers_certified"], "relative branch dictionary changed")
    require(dictionary_flags["same_background_only"] and not dictionary_flags["cross_background_mode_identification_made"], "relative background boundary changed")
    receiver_flags = receiver["classification"]
    require(receiver_flags["mapping_cofiber_and_current_receiver_assembled"], "relative current receiver changed")
    require(receiver_flags["charge_projected_arity_two_descent_exact"], "relative charge projection changed")
    require(not receiver_flags["full_relative_arity_two_morphism_constructed"], "relative f2 unexpectedly promoted")
    obstruction_flags = obstruction["classification"]
    require(not obstruction_flags["frozen_unary_full_domain_f2_exists"], "full-domain f2 obstruction changed")
    require(not obstruction_flags["taub_zero_restricted_source_obstructed"], "derived-source route was closed")
    cone_flags = cone["classification"]
    require(cone_flags["complete_candidate13_bounded_tangent_cone_formula_certified"], "candidate-13 bounded cone changed")
    require(cone_flags["candidate13_known_bounded_functional_ledger_certified"], "candidate-13 known bounded ledger changed")
    require(cone_flags["complete_candidate13_bounded_functional_ledger_certified"], "candidate-13 bounded ledger changed")
    require(cone_flags["complete_candidate13_smooth_tangent_cone_formula_certified"], "candidate-13 smooth cone changed")
    require(cone_flags["candidate13_complete_bounded_cone_is_origin"], "candidate-13 bounded origin theorem changed")
    require(not cone_flags["nonzero_mixed_bounded_point_exists"], "candidate-13 nonzero bounded point appeared")
    require(cone_flags["nonzero_mixed_bounded_point_nonexistence_certified"], "candidate-13 bounded nonexistence certificate changed")
    require(separation["classification"]["exact_rational_Farkas_functional_certified"], "candidate-13 scalar separator changed")
    require(separation["classification"]["candidate13_complete_bounded_cone_is_origin"], "candidate-13 scalar origin theorem changed")
    require(records["pressure_obstruction"]["classification"]["candidate13_bounded_or_finite_quasiperiodic_extension_obstructed"], "candidate-13 pressure witness changed")
    require(records["bounded_zero_block"]["classification"]["five_stabilizers_plus_circle_pressure_complete_on_finite_generic_zero_block"], "bounded zero-block theorem changed")

    return {
        "schema": "pure-weyl-relative-candidate13-derived-source-crosswalk-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_WEYL_RELATIVE_CANDIDATE13_DERIVED_SOURCE_CROSSWALK_V1",
        "result_state": "TYPED_BOUNDED_AND_SMOOTH_DERIVED_SOURCE_PULLBACKS_CERTIFIED_FULL_DOMAIN_F2_OBSTRUCTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "candidate-13 compact magnetic Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed magnetic U1 bundle P_N with N=2",
            "carrier": "generic ell=2 Einstein q-primary image plus p-primary relative cofiber on the signed n=1,-2 candidate-13 fibres",
            "degree": "unary relative triangle plus quadratic reduced-source constraint",
            "parity": "both axial and polar",
            "ell": "input ell=2; quadratic outputs L=0,...,4",
            "m": "all m and every allowed output M",
            "k": "signed n=1,-2 fibres and reality conjugates",
            "omega": "all generic branch shells and quadratic signed sums",
        },
        "relative_triangle": {
            "f1": "the certified same-background support-local off-shell Einstein-Maxwell to Weyl-Maxwell chain map",
            "cofiber": "the certified support-local mapping cofiber; on generic solution cohomology its p-primary classes are the relative extra coordinates and its q-primary classes are the Einstein image",
            "pairing": "noncyclic three-form triangle retaining the source, pulled-back target, and cofiber action-derived forms separately",
            "cross_background_identification": "NO_CERTIFIED_MAP",
        },
        "quadratic_receiver": {
            "equation": "L_WM v=-(1/2)D^2E_WM[u,u]",
            "zero_block_map": {
                "target": "five-current cone / five-generator Koszul receiver",
                "components": ["mu_H", "mu_Px", "mu_J1", "mu_J2", "mu_J3"],
                "status": "CERTIFIED",
            },
            "relative_resonance_map": {
                "target": "18-dimensional complex candidate-13 L4 reduced adjoint-cokernel coefficient space",
                "components": "R_13,1,...,R_13,18",
                "status": "CERTIFIED",
            },
            "bounded_pressure_map": {
                "target": "one-dimensional bounded homogeneous pressure receiver",
                "components": "R_c=(1/2) sum k_j^2 h_j",
                "status": "CERTIFIED",
            },
            "combined_bounded_map": "O2_candidate13,bounded=(mu_H,mu_Px,mu_J1,mu_J2,mu_J3,R_c,R_13,1,...,R_13,18)",
            "typing": "the five current components, one bounded pressure component and eighteen finite-frequency relative-cofiber components are distinct summands and are never identified",
        },
        "derived_source_pullback": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {
                "status": "CERTIFIED",
                "domain": "O2_candidate13,bounded^{-1}(0)={0} on the declared candidate-13 generic carrier",
                "sufficiency": "the complete bounded receiver exhausts the reduced adjoint cokernel, and the exact scalar separator D in span(mu_H,mu_Px,R_c) is strictly positive on every nonzero declared coefficient vector",
            },
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {
                "status": "CERTIFIED",
                "domain": "{mu_H=mu_Px=mu_J1=mu_J2=mu_J3=0}",
                "sufficiency": "the eighteen finite-frequency relative components admit secular inverses",
            },
            "CAUSAL_RETARDED": {
                "status": "NO_CERTIFIED_MAP",
                "domain": "NO_CERTIFIED_MAP",
            },
            "smooth_nonempty": "the axial m=0 Einstein-minus/extra-primary witness is a nonzero point of the smooth pullback",
            "bounded_witness_disposition": "the same witness is excluded because R_c<0; in fact every nonzero declared tangent is excluded from the bounded pullback by the scalar separator",
        },
        "morphism_disposition": {
            "full_domain_support_local_f2": "OBSTRUCTED",
            "derived_reduced_source_second_order_solve": "CERTIFIED_BOUNDED_AND_SMOOTH_ON_THEIR_DECLARED_ZERO_LOCI",
            "full_relative_arity_two_morphism": "OPEN",
            "arity_three_authorized": False,
            "reason": "both declared reduced zero loci solve the quadratic extension equation in their correction classes, but the restriction does not construct a support-local BV subcomplex or repair the frozen-unary full-domain f2 equation",
        },
        "classification": {
            "same_background_relative_branch_crosswalk_certified": True,
            "candidate13_five_plus_pressure_plus_eighteen_quadratic_receiver_typed": True,
            "bounded_derived_source_pullback_certified": True,
            "bounded_derived_source_known_necessary_ledger_certified": True,
            "bounded_derived_source_pullback_is_origin": True,
            "nonzero_mixed_bounded_derived_source_point_exists": False,
            "nonzero_mixed_bounded_derived_source_point_nonexistence_certified": True,
            "smooth_derived_source_pullback_certified": True,
            "nonzero_mixed_smooth_derived_source_point_certified": True,
            "full_domain_f2_obstruction_preserved": True,
            "support_local_BV_derived_subcomplex_constructed": False,
            "full_relative_arity_two_morphism_constructed": False,
            "arity_three_authorized": False,
            "cross_background_causal_observational_or_quantum_claim": False,
        },
        "interpretation": "The candidate-13 theorem realizes correction-class-sensitive reduced-mode derived-source pullbacks for the relative current-cofiber assembly. The bounded pullback is exactly the origin because its pressure-enhanced scalar charge combination is definite, whereas the smooth pullback is the nontrivial five-current zero set. The displayed mixed witness belongs only to the smooth pullback.",
        "next_gate": "test other collision circumferences for analogous scalar separators while keeping each background and carrier distinct; do not start arity three on the obstructed full-domain morphism",
        "claim_boundary": "This is a same-background REDUCED-MODE bounded and smooth derived-source crosswalk. It is not a support-local derived BV subcomplex, full-domain f2 repair, arity-three morphism, causal functor, cross-background map, observable, particle theorem, or quantum claim.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_weyl_relative_candidate13_derived_source_crosswalk --check",
            "python3 -m bridge.einstein_sector.verify_einstein_weyl_relative_candidate13_derived_source_crosswalk",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_relative_candidate13_derived_source_crosswalk",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered, encoding="utf-8")
    elif not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
        raise AssertionError("candidate-13 relative derived-source crosswalk is stale")
    print("EINSTEIN_WEYL_RELATIVE_CANDIDATE13_DERIVED_SOURCE_CROSSWALK_V1: PASS")


if __name__ == "__main__":
    main()
