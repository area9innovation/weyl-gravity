#!/usr/bin/env python3
"""Generate the fail-closed nonlinear residual-atlas fragment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"
OUTPUT = ROOT / "d_quotient_classical/atlas/nonlinear-atlas-fragment.json"
STATUSES = ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]
AXES = ["causal", "symplectic", "nonlinear", "observational", "quantum"]
CERTS = {
    "mixed_obstruction": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_POSITIVE_JET_FULL_BV_OBSTRUCTION_V1.json",
    "dictionary": ROOT / "d_quotient_classical/certificates/NONLINEAR_SOURCE_TRANSFER_TANGENT_CONE_DICTIONARY_V1.json",
    "cone": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
    "branch_projector": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1.json",
    "axial_ee_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ee_ell2_source.json",
    "branch_importer": ROOT / "d_quotient_classical/certificates/BERGER_MIXED_ELL3_BRANCH_PROJECTION_IMPORTER_PREFLIGHT_V1.json",
    "relative_branch_dictionary": ROOT / "bridge/certificates/einstein_weyl_relative_branch_dictionary.json",
    "homogeneous_twist_extra_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix.json",
    "homogeneous_twist_extra_cone": ROOT / "d_quotient_classical/certificates/PH_HOMOGENEOUS_TWIST_ELL2_EXTRA_BOUNDED_TANGENT_CONE_V1.json",
    "homogeneous_twist_extra_bounded_obstruction": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_bounded_correction_obstruction.json",
    "homogeneous_twist_polynomial_correction": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_collinear_second_order.json",
    "global_extra_smooth_extension": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_smooth_secular_second_order.json",
    "circumference_transport_primitive": ROOT / "bridge/certificates/einstein_maxwell_weyl_circumference_ell2_extra_transport_primitive.json",
    "exceptional_ell1_cofiber": ROOT / "bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json",
    "exceptional_ell1_nonzero_k_cofiber": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json",
    "exceptional_global_offshell": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1.json",
    "covariant_chain_map": ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1.json",
    "relative_linfinity_preflight": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_LINFINITY_THROUGH_ARITY_THREE_PREFLIGHT_V1.json",
    "einstein_product_taylor": ROOT / "bridge/certificates/EINSTEIN_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1.json",
    "weyl_product_taylor": ROOT / "bridge/certificates/WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1.json",
    "relative_arity_two_defect": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ARITY_TWO_DEFECT_V1.json",
    "relative_f2_taub_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_F2_TAUB_OBSTRUCTION_V1.json",
    "relative_charge_koszul_preflight": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CHARGE_KOSZUL_RECEIVER_PREFLIGHT_V1.json",
    "relative_standard_charge_q2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_STANDARD_RADIATIVE_CHARGE_Q2_V1.json",
    "relative_complete_standard_charge_q2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_COMPLETE_STANDARD_FIVE_CHARGE_Q2_V1.json",
    "relative_finite_charge_locality_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FINITE_CHARGE_SUPPORT_LOCAL_LIFT_OBSTRUCTION_V1.json",
    "relative_polarized_noether_current_seed": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_POLARIZED_NOETHER_CURRENT_SEED_V1.json",
    "relative_hessian_green_current_cone": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_HESSIAN_GREEN_CURRENT_CONE_V1.json",
    "identity_cyclic_obstruction": ROOT / "bridge/certificates/einstein_weyl_generic_identity_cyclic_obstruction.json",
    "generic_cyclic_map_inertia_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _evidence(*names: str) -> list[dict[str, str]]:
    rows = []
    for name in names:
        path = CERTS[name]
        payload = json.loads(path.read_text())
        rows.append({"path": str(path.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": _sha(path)})
    return rows


SMOOTH_REQUIRED_MANIFEST_PATHS = {
    "bridge/certificates/einstein_maxwell_weyl_global_extra_bounded_correction_obstruction.json",
    "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_collinear_second_order.json",
    "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order.json",
    "bridge/einstein_sector/einstein_maxwell_weyl_global_extra_smooth_secular_second_order.py",
    "bridge/einstein_sector/schema/einstein_maxwell_weyl_global_extra_smooth_secular_second_order.schema.json",
    "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
    "d_quotient_classical/certificates/PH_HOMOGENEOUS_TWIST_ELL2_EXTRA_BOUNDED_TANGENT_CONE_V1.json",
}


def smooth_extension_payload_ready(payload: dict[str, Any], *, verify_manifest: bool = True) -> bool:
    """Accept only the exact, fully receipted smooth correction-class theorem."""

    try:
        flags = payload["classification"]
        classes = payload["correction_classes"]
        scope = payload["scope"]
        receipt = payload["verification_receipt"]
        commands = payload["verification_commands"]
        manifest = payload["source_manifest"]
        required_true = (
            "complete_nonzero_extra_common_zero_orbit_covered",
            "complete_quadratic_channel_ledger",
            "all_nonstabilizer_smooth_secular_cokernels_zero",
            "smooth_exponential_polynomial_second_order_correction_exists",
        )
        required_false = (
            "coefficient_explicit_correction_printed",
            "bounded_correction_exists",
            "causal_retarded_map_certified",
            "all_orders_integrability",
        )
        if payload["result_id"] != "EINSTEIN_MAXWELL_WEYL_GLOBAL_EXTRA_SMOOTH_SECULAR_SECOND_ORDER":
            return False
        if payload["lifecycle_state"] != "CERTIFIED":
            return False
        if set(payload["dependency_tags"]) != {"LOCAL-ALGEBRAIC", "REDUCED-MODE"}:
            return False
        if scope["background"] != "compact magnetically supported Plebanski-Hacyan product" or scope["k"] != 0:
            return False
        if not all(flags[name] is True for name in required_true):
            return False
        if not all(flags[name] is False for name in required_false):
            return False
        if not classes["bounded_or_finite_quasiperiodic"].startswith("OBSTRUCTED"):
            return False
        if not classes["smooth_exponential_polynomial"].startswith("CERTIFIED"):
            return False
        if not classes["causal_or_retarded"].startswith("NO_CERTIFIED_MAP"):
            return False
        if receipt["tier_1"]["status"] != "PASS":
            return False
        if not any("verify_einstein_maxwell_weyl_global_extra_smooth_secular_second_order.py" in command for command in commands):
            return False
        if not SMOOTH_REQUIRED_MANIFEST_PATHS.issubset(manifest):
            return False
        if verify_manifest:
            for relative, expected in manifest.items():
                path = ROOT / relative
                if not path.is_file() or _sha(path) != expected:
                    return False
    except (KeyError, TypeError, ValueError):
        return False
    return True


def smooth_extension_import_ready() -> bool:
    path = CERTS["global_extra_smooth_extension"]
    if not path.is_file():
        return False
    try:
        payload = json.loads(path.read_text())
        schema_path = ROOT / payload["schema_path"]
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(payload)
    except (KeyError, OSError, SchemaError, TypeError, ValidationError, ValueError):
        return False
    return smooth_extension_payload_ready(payload)


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def _second(bounded: tuple[str, str], secular: tuple[str, str], causal: tuple[str, str]) -> dict[str, Any]:
    return {
        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
        "bounded_or_finite_quasiperiodic": _claim(*bounded),
        "smooth_secular": _claim(*secular),
        "causal_retarded": _claim(*causal),
    }


def _mode_data(second: dict[str, Any], *, dispersion: tuple[str, str], pairing: tuple[str, str], taub: tuple[str, str], resonance: tuple[str, str]) -> dict[str, Any]:
    return {
        "dispersion": _claim(*dispersion),
        "lee_wald": _claim(*pairing),
        "taub_maps": _claim(*taub),
        "resonance": _claim(*resonance),
        "second_order": second,
    }


def bridge2_entry(importer: dict[str, Any], fallback_scope: dict[str, Any]) -> dict[str, Any]:
    activated = importer["claim_flags"]["BRIDGE_2_ACTIVATED"] is True
    if not activated:
        return {
            "id": "nonlinear.berger.bridge2.invariant_interaction_to_physical_branches",
            "scope": fallback_scope,
            "descriptions": {axis: "NO_CERTIFIED_MAP" for axis in AXES},
            "mode_data": _mode_data(
                _second(
                    ("NO_CERTIFIED_MAP", "No same-background branch map exists on which to project the bounded obstruction problem."),
                    ("NO_CERTIFIED_MAP", "No same-background branch map exists on which to project the secular correction problem."),
                    ("NO_CERTIFIED_MAP", "No same-background branch map exists on which to project the retarded correction problem."),
                ),
                dispersion=("NO_CERTIFIED_MAP", "Branch-labelled Berger dispersion requires bridge 1."),
                pairing=("NO_CERTIFIED_MAP", "Branch pairing transport is an acceptance condition of bridge 1."),
                taub=("NO_CERTIFIED_MAP", "The landed D^2E-q2 dictionary cannot be evaluated branchwise before bridge 1."),
                resonance=("NO_CERTIFIED_MAP", "The filtered-cyclic ell3 obstruction is certified only on the unsplit retained carrier."),
            ),
            "evidence": _evidence("branch_importer", "mixed_obstruction", "dictionary"),
            "claim_boundary": "Bridge 2 is INPUT_BLOCKED. It activates only after an admissible same-background mixed-bundle, noncontractible-cofiber, or explicitly REDUCED-MODE branch map passes the importer. The importer requires the complete atlas mode scope and typed, schema-validated, content-addressed crosswalk, chain, inclusion/projection/cofiber, pairing, gauge/nondynamical, K_Berger-equivariance, cohomology and independent-verifier evidence. The compact-product mode-pair row is not a Berger crosswalk. Projected cohomology, cyclic deformation nontriviality and admissible removal remain NO_CERTIFIED_MAP, and q4 is not authorized.",
        }

    summary = importer["imported_branch_map"]
    if not isinstance(summary, dict):
        raise ValueError("activated bridge 2 lacks imported branch-map summary")
    causal_ready = "LORENTZIAN-CAUSAL" in summary["dependency_tags"]
    causal_status = "OPEN" if causal_ready else "NO_CERTIFIED_MAP"
    causal_statement = (
        "The imported branch map is Lorentzian-causal tagged, but the projected retarded correction problem has not been computed."
        if causal_ready else
        "The imported branch map has no LORENTZIAN-CAUSAL certificate."
    )
    return {
        "id": "nonlinear.berger.bridge2.invariant_interaction_to_physical_branches",
        "scope": summary["mode_scope"],
        "descriptions": {
            "causal": causal_status,
            "symplectic": "CERTIFIED",
            "nonlinear": "OPEN",
            "observational": "NO_CERTIFIED_MAP",
            "quantum": "NO_CERTIFIED_MAP",
        },
        "mode_data": _mode_data(
            _second(
                ("OPEN", "Bridge 1 is imported; the branch-projected bounded obstruction map remains to be computed."),
                ("OPEN", "Bridge 1 is imported; the branch-projected secular correction problem remains to be computed."),
                (causal_status, causal_statement),
            ),
            dispersion=("OPEN", "The certified branch carrier is available, but branchwise nonlinear harmonic selection has not been computed."),
            pairing=("CERTIFIED", "Pairing transport and the induced cohomology map passed the Bridge-1 importer."),
            taub=("OPEN", "Apply the landed D^2E-q2 dictionary on the imported carrier to decide adjoint-cokernel reach."),
            resonance=("OPEN", "The unsplit filtered-cyclic ell3 obstruction is preserved; its projected cohomology/deformation disposition remains open."),
        ),
        "evidence": _evidence("branch_importer", "mixed_obstruction", "dictionary"),
        "claim_boundary": "Bridge 1 has activated Bridge 2 on the explicitly imported same-background carrier. This certifies carrier, chain/cohomology and pairing readiness only. The projected ell2/ell3 operation, cohomology survival, cyclic deformation class and admissible-removal verdict remain OPEN; q4 is not authorized.",
    }


def entries() -> list[dict[str, Any]]:
    branch_importer = json.loads(CERTS["branch_importer"].read_text())
    relative_linfinity = json.loads(CERTS["relative_linfinity_preflight"].read_text())
    linear_triangle_imported = relative_linfinity["input_status"]["relative_linear_triangle"] == "IMPORTED"
    einstein_taylor_imported = relative_linfinity["input_status"]["einstein_product_q2_q3"] == "IMPORTED"
    weyl_taylor_imported = relative_linfinity["input_status"]["weyl_product_q2_q3"] == "IMPORTED"
    all_relative_inputs_imported = (
        linear_triangle_imported
        and einstein_taylor_imported
        and weyl_taylor_imported
    )
    relative_arity_two = json.loads(CERTS["relative_arity_two_defect"].read_text())
    relative_arity_two_computed = (
        relative_arity_two["result_state"]
        == "NONZERO_STRICT_ARITY_TWO_DEFECT_F2_SOLVE_REQUIRED"
    )
    relative_f2 = json.loads(CERTS["relative_f2_taub_obstruction"].read_text())
    relative_f2_obstructed = (
        relative_f2["result_state"]
        == "FROZEN_UNARY_RELATIVE_F2_OBSTRUCTED_BY_NONZERO_CONSTANT_LAPSE_CLASS"
        and relative_f2["classification"]["frozen_unary_full_domain_f2_exists"] is False
    )
    relative_charge_koszul = json.loads(CERTS["relative_charge_koszul_preflight"].read_text())
    relative_charge_receiver_selected = (
        relative_charge_koszul["result_state"]
        == "DERIVED_RELATIVE_CHARGE_RECEIVER_SELECTED_OFFSHELL_LIFT_OPEN"
        and relative_charge_koszul["classification"]["reduced_mode_koszul_square_zero"] is True
        and relative_charge_koszul["classification"]["relative_f2_repaired"] is False
    )
    smooth_extension_ready = smooth_extension_import_ready()
    berger = {
        "theory": "pure-Weyl gravity plus rotating Berger clocks and Maxwell",
        "background": "fixed rational positive Berger clock",
        "boundaries": "R_t x compact Berger S3; no spatial boundary",
        "charge_sector": "fixed-coupling retained sector with K_Berger=D-omega R",
    }
    obstruction_scope = {
        **berger,
        "carrier": "typed 36-row retained full-BV gravity-clock-Maxwell carrier; mixed quartic action sector represented by ell3",
        "degree": "all BV degrees participating in the 22-row dual functional",
        "parity": "graded mixed gravity-Maxwell",
        "ell": "NO_CERTIFIED_MAP from local PBW jets to Berger harmonics",
        "m": "NO_CERTIFIED_MAP",
        "k": "local PBW derivative axes 0 and 1 in the witness; no mode covector crosswalk",
        "omega": "NO_CERTIFIED_MAP; raw D is affine and the local witness is not a K_Berger eigenmode",
    }
    crosswalk_scope = {
        **berger,
        "carrier": "crosswalk from the retained 36-row mixed ell3 carrier to Einstein-like, extra-Weyl, topological and Maxwell residual branches",
        "degree": "crosswalk",
        "parity": "all",
        "ell": "all",
        "m": "all",
        "k": "all",
        "omega": "all",
    }
    cone_scope = {
        "theory": "finite-harmonic nonlinear gauge equation with complete Noether and gauge reduction",
        "background": "any fixed background satisfying the declared finite-block hypotheses",
        "boundaries": "fixed as part of the correction operator domain",
        "charge_sector": "declared stabilizer moment-map sector",
        "carrier": "finite direct sum of first-order harmonic solution blocks and all quadratically selected output blocks",
        "degree": 1,
        "parity": "arbitrary fixed graded block",
        "ell": "declared finite set",
        "m": "declared finite set",
        "k": "declared finite set or NOT_APPLICABLE in compact harmonic language",
        "omega": "declared finite frequency set",
    }
    axial_ee_scope = {
        "theory": "Einstein-Maxwell embedded in pure-Weyl/Weyl-Maxwell gravity",
        "background": "unit-magnetic fixed-P_N product background on R_t x S1_L x S2",
        "boundaries": "compact S1_L x S2; no spatial boundary",
        "charge_sector": "fixed unit magnetic charge after local Diff x U(1) reduction",
        "carrier": "four independent gauge-fixed axial output rows before the final residual quotient",
        "degree": "degree-zero inputs; equation-row quadratic-source output",
        "parity": "odd axial-polar input pair to axial output",
        "ell": 2,
        "m": 0,
        "k": 0,
        "omega": "two positive-frequency minus-branch inputs at sqrt(6-2sqrt(3)); sum-frequency output 2*sqrt(6-2sqrt(3))",
    }
    bridge2_scope = {
        **berger,
        "carrier": "prospective admissible same-background branch map from the retained interaction carrier or an explicitly crosswalked enlargement",
        "degree": "all declared BV degrees and induced cohomology map",
        "parity": "all",
        "ell": "NO_CERTIFIED_MAP pending bridge 1",
        "m": "NO_CERTIFIED_MAP pending bridge 1",
        "k": "NO_CERTIFIED_MAP pending bridge 1",
        "omega": "NO_CERTIFIED_MAP pending bridge 1",
    }
    product_common = {
        "theory": "Einstein-Maxwell source and Weyl-Maxwell target",
        "background": "compactified magnetically supported Plebanski-Hacyan R_t x S1_L x S2 fixture",
        "boundaries": "closed Cauchy slice S1_L x S2; before final residual quotient",
        "charge_sector": "fixed magnetic U(1) bundle P_N with N=2; electric tangent allowed",
    }
    product_axial_scope = {
        **product_common,
        "carrier": "generic axial Fourier-polynomial coefficient complex and its reduced solution module",
        "degree": 1,
        "parity": "axial",
        "ell": ">=2",
        "m": "all",
        "k": "2*pi*n/L, every n in Z including zero",
        "omega": "q-primary Einstein shells and p-primary extra shell",
    }
    product_polar_scope = {
        **product_common,
        "carrier": "generic polar gauge-fixed coefficient system and its reduced solution module",
        "degree": 1,
        "parity": "polar",
        "ell": ">=2",
        "m": "all",
        "k": "2*pi*n/L, every n in Z including zero",
        "omega": "q-primary Einstein shells and p-primary extra shell",
    }
    homogeneous_twist_scope = json.loads(CERTS["homogeneous_twist_extra_source"].read_text())["scope"]
    exceptional_scope = {
        **product_common,
        "carrier": "exceptional local-gauge-reduced axial and polar ell=1,k=0 solution modules",
        "degree": 1,
        "parity": "axial and polar kept separate",
        "ell": 1,
        "m": "all three real SO(3) components",
        "k": 0,
        "omega": "twist omega^2=0 axially, extra omega^2=4/3, standard omega^2=4",
    }
    exceptional_nonzero_k_scope = {
        **product_common,
        "carrier": "exceptional local-gauge-reduced axial and polar ell=1 solution modules at nonzero compact momentum",
        "degree": 1,
        "parity": "axial and polar kept separate",
        "ell": 1,
        "m": "all three real SO(3) components",
        "k": "2*pi*n/L with n!=0",
        "omega": "standard omega^2=k^2+4 and extra omega^2=k^2+4/3",
    }
    relative_linfinity_scope = {
        **product_common,
        "carrier": "prospective full off-shell Einstein--Weyl relative BV triangle with complete same-background Einstein-Maxwell and Weyl-Maxwell q1,q2,q3 Taylor payloads",
        "degree": "all BV degrees",
        "parity": "all axial, polar, exceptional and global sectors",
        "ell": "all sectors required by the full relative triangle",
        "m": "all sectors required by the full relative triangle",
        "k": "all compact-product Fourier sectors required by the full relative triangle",
        "omega": "all product-mode frequencies required by the full relative triangle",
    }
    relative_charge_scope = relative_charge_koszul["scope"]
    relative_charge_q2 = json.loads(CERTS["relative_standard_charge_q2"].read_text())
    relative_charge_q2_scope = relative_charge_q2["scope"]
    relative_complete_charge_q2 = json.loads(CERTS["relative_complete_standard_charge_q2"].read_text())
    relative_complete_charge_q2_scope = relative_complete_charge_q2["scope"]
    relative_locality_obstruction = json.loads(CERTS["relative_finite_charge_locality_obstruction"].read_text())
    relative_locality_obstruction_scope = relative_locality_obstruction["scope"]
    relative_current_seed = json.loads(CERTS["relative_polarized_noether_current_seed"].read_text())
    relative_current_seed_scope = relative_current_seed["scope"]
    relative_green_cone = json.loads(CERTS["relative_hessian_green_current_cone"].read_text())
    relative_green_cone_scope = relative_green_cone["scope"]
    identity_cyclic_scope = json.loads(CERTS["identity_cyclic_obstruction"].read_text())["scope"]
    return [
        {
            "id": "nonlinear.berger.retained_mixed_ell3.filtered_cyclic_obstruction",
            "scope": obstruction_scope,
            "descriptions": {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OBSTRUCTED", "observational": "NO_CERTIFIED_MAP", "quantum": "OPEN"},
            "mode_data": _mode_data(
                _second(
                    ("NO_CERTIFIED_MAP", "The local PBW ell3 carrier has no bounded harmonic crosswalk."),
                    ("NO_CERTIFIED_MAP", "The local PBW ell3 carrier has no smooth-secular harmonic crosswalk."),
                    ("NO_CERTIFIED_MAP", "The algebraic contraction homotopy is not an interacting retarded correction."),
                ),
                dispersion=("NOT_APPLICABLE", "A quartic retained deformation representative has no one-particle dispersion relation."),
                pairing=("OPEN", "Cyclicity is certified, but no branch-resolved Lee-Wald norm is assigned."),
                taub=("NOT_APPLICABLE", "This ell3 deformation obstruction is not the quadratic q2 tangent-cone obstruction."),
                resonance=("OBSTRUCTED", "The first associated-graded cyclic redefinition equation has a normalized exact dual obstruction."),
            ),
            "evidence": _evidence("mixed_obstruction", "dictionary"),
            "claim_boundary": "The mixed ell3 representative is unremovable only within the declared nonnegative filtered derivative-aware cyclic F2/F3 class. Its branch, cohomology, particle, causal and quantum images remain open or lack a certified map.",
        },
        {
            "id": "nonlinear.berger.crosswalk.retained36_to_residual_branches",
            "scope": crosswalk_scope,
            "descriptions": {axis: "NO_CERTIFIED_MAP" for axis in AXES},
            "mode_data": _mode_data(
                _second(
                    ("NO_CERTIFIED_MAP", "No retained-to-branch harmonic projector."),
                    ("NO_CERTIFIED_MAP", "No retained-to-branch harmonic projector."),
                    ("NO_CERTIFIED_MAP", "No retained-to-branch causal projector."),
                ),
                dispersion=("NO_CERTIFIED_MAP", "No branch-resolved dispersion pullback."),
                pairing=("NO_CERTIFIED_MAP", "No branch-resolved pairing pullback."),
                taub=("NO_CERTIFIED_MAP", "No branch-resolved quadratic-source/cokernel table."),
                resonance=("OBSTRUCTED", "The requested support-local same-bundle rank-36 branch projector is obstructed."),
            ),
            "evidence": _evidence("branch_projector", "mixed_obstruction"),
            "claim_boundary": "Do not identify retained rows with Einstein-like, extra-Weyl, topological or Maxwell residual modes. A different noncontractible mixed-bundle carrier or explicitly REDUCED-MODE nonlocal split remains possible.",
        },
        {
            "id": "nonlinear.abstract.finite_harmonic.tangent_cone_naturality",
            "scope": cone_scope,
            "descriptions": {"causal": "NOT_APPLICABLE", "symplectic": "NOT_APPLICABLE", "nonlinear": "CERTIFIED", "observational": "NOT_APPLICABLE", "quantum": "NOT_APPLICABLE"},
            "mode_data": _mode_data(
                _second(
                    ("CERTIFIED", "Z2^C is the zero locus of moment and bounded-resonance cokernel maps."),
                    ("CERTIFIED", "Secular right inverses remove only the resonances admitted by the declared exponential-polynomial class."),
                    ("CERTIFIED", "For compatible compact sources and a declared retarded inverse, propagation resonances are removed while static moment maps remain."),
                ),
                dispersion=("NOT_APPLICABLE", "This is an abstract finite-block image/cokernel theorem."),
                pairing=("NOT_APPLICABLE", "No physical norm is assigned by the abstract theorem."),
                taub=("CERTIFIED", "The stabilizer part of the reduced adjoint cokernel is the moment map mu_X."),
                resonance=("CERTIFIED", "Complementary obstruction maps R_j^C depend on the declared correction class."),
            ),
            "evidence": _evidence("cone", "dictionary"),
            "claim_boundary": "The complete obstruction zero locus is natural under field/equation isomorphisms that preserve the harmonic carrier, domains, boundaries, Noether/gauge reduction and correction class. It supplies no background-specific mode classification.",
        },
        {
            "id": "nonlinear.product.axial_polar_einstein_minus_to_axial_extra.ell2_m0_k0_sum_frequency",
            "scope": axial_ee_scope,
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "OPEN", "nonlinear": "CERTIFIED", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": _mode_data(
                _second(
                    ("CERTIFIED", "The selected four-row source is off both target normal shells and has an explicit exact harmonic correction."),
                    ("CERTIFIED", "The same exact nonresonant correction is admissible in the smooth-secular class."),
                    ("NO_CERTIFIED_MAP", "No retarded Green realization of this reduced-mode correction is certified."),
                ),
                dispersion=("CERTIFIED", "Both inputs lie on the certified minus branch; their sum frequency is off the selected axial target shells."),
                pairing=("OPEN", "No final residual Lee-Wald pairing or norm is established by this source certificate."),
                taub=("CERTIFIED", "The nonzero D^2E source lies in the image of the selected four-row Hessian block, so it does not reach that block's adjoint cokernel."),
                resonance=("CERTIFIED", "The selected sum-frequency block is nonresonant and explicitly removable by a second-order correction."),
            ),
            "evidence": _evidence("axial_ee_source", "relative_branch_dictionary", "dictionary"),
            "claim_boundary": "This is one REDUCED-MODE axial ell=2,m=0,k=0 sum-frequency source block on the compact product background. Its exact second-order correction is not a cyclic L_infinity field redefinition, and the polar input leg still lacks cyclic BV compatibility. Even outputs, conjugate/difference frequencies, the complete real tangent, final residual descent, causal propagation and the Berger retained carrier remain separate or NO_CERTIFIED_MAP.",
        },
        bridge2_entry(branch_importer, bridge2_scope),
        {
            "id": "nonlinear.product.bridge1.generic_axial_relative_branch_map",
            "scope": product_axial_scope,
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "OBSTRUCTED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": _mode_data(
                _second(
                    ("OPEN", "The generic axial cofiber is certified, but its complete branchwise quadratic obstruction map has not been assembled."),
                    ("OPEN", "No complete smooth-secular relative obstruction map is certified."),
                    ("NO_CERTIFIED_MAP", "No compact-product causal Green carrier is certified."),
                ),
                dispersion=("CERTIFIED", "The q-primary Einstein shells and p-primary extra shell are explicitly separated."),
                pairing=("OBSTRUCTED", "The action-derived Einstein source form is positive, while the Weyl form restricted to the complete q-primary image has inertia (1,1); congruence invariance obstructs every standard-pairing cyclic cohomology isomorphism."),
                taub=("OPEN", "Only selected quadratic source and moment-map blocks are certified; the complete generic map is open."),
                resonance=("OPEN", "No complete all-input generic axial resonance table is certified."),
            ),
            "evidence": _evidence("relative_branch_dictionary", "identity_cyclic_obstruction", "generic_cyclic_map_inertia_obstruction", "dictionary"),
            "claim_boundary": "This is a same-background generic-axial derived cofiber and action-pairing map. The inertia mismatch obstructs every real-structure-preserving product-equivariant cyclic cohomology isomorphism for the standard action-derived pairings, not only the fixed identity map. A noncyclic three-form triangle and an explicitly pairing-changed theorem remain open. It is a sectoral Bridge-1 input, not the all-sector EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1 and not a Berger crosswalk. No complete q2/q3 relative morphism, cohomology operation or deformation verdict is promoted.",
        },
        {
            "id": "nonlinear.product.bridge1.generic_polar_relative_branch_map",
            "scope": product_polar_scope,
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "OBSTRUCTED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": _mode_data(
                _second(
                    ("OPEN", "The polar solution cofiber is certified; every standard-pairing cyclic cohomology isomorphism is obstructed, while the noncyclic three-form triangle and complete quadratic obstruction map remain open."),
                    ("OPEN", "No complete smooth-secular relative obstruction map is certified."),
                    ("NO_CERTIFIED_MAP", "No compact-product causal Green carrier is certified."),
                ),
                dispersion=("CERTIFIED", "The q-primary Einstein shells and p-primary extra shell are explicitly separated."),
                pairing=("OBSTRUCTED", "The positive Einstein form and indefinite restricted Weyl form have different inertia, obstructing every standard-pairing cyclic cohomology isomorphism."),
                taub=("OPEN", "The polar source fixtures do not yet constitute the complete relative obstruction map."),
                resonance=("OPEN", "The standard-pairing cyclic route is obstructed; the noncyclic three-form triangle and complete all-input polar resonance table remain open."),
            ),
            "evidence": _evidence("relative_branch_dictionary", "identity_cyclic_obstruction", "generic_cyclic_map_inertia_obstruction", "dictionary"),
            "claim_boundary": "This is a same-background generic-polar solution cofiber with a certified direct pairing. The standard action-derived pairings have incompatible inertia on physical cohomology, so every real-structure-preserving product-equivariant cyclic correction is obstructed. A noncyclic three-form triangle, a pairing-changed theorem and final residual descent remain open. It therefore does not activate a cyclic relative L_infinity theorem or the global Bridge-1 gate.",
        },
        {
            "id": "nonlinear.product.homogeneous_twist_times_ell2_extra.complete_bounded_resonance_matrix",
            "scope": homogeneous_twist_scope,
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": _mode_data(
                _second(
                    ("OPEN", "The complete declared bounded-resonance functionals are certified, but their simultaneous zero locus with all five stabilizer moment maps and the bilinear factorization constraints has not been solved."),
                    ("OPEN", "Smooth-secular sufficiency requires the complete Noether-compatible operator and is not inferred from the resonant projection."),
                    ("NO_CERTIFIED_MAP", "No compact-product retarded complex or causal correction carrier is certified."),
                ),
                dispersion=("CERTIFIED", "The generalized-zero homogeneous/twist inputs are crossed with the resonant ell=2 extra shell omega_e=4/sqrt(3) at k=0."),
                pairing=("CERTIFIED", "Exact axial and polar adjoint bases define the resonance functionals; the same-background relative dictionary imports their action-derived pairing context."),
                taub=("OPEN", "The common zero locus of the five stabilizer moment maps and the complete resonance matrix remains unsolved."),
                resonance=("CERTIFIED", "The a,b,d chains are exact; twist position has rank two and twist velocity has pointwise rank four for every real time, with all m fixed by SO(3) equivariance."),
            ),
            "evidence": _evidence("homogeneous_twist_extra_source", "relative_branch_dictionary", "dictionary", "cone"),
            "claim_boundary": "This certifies the complete declared k=0 homogeneous/twist times ell=2 extra bounded-resonance source matrix on the compact Plebanski-Hacyan background. It does not solve the simultaneous stabilizer/resonance zero locus, prove obstruction or extension for a tangent, supply the all-sector off-shell cyclic relative triangle, activate Berger or compact-product Bridge 2, or establish smooth-secular, causal, residual, observational, particle or quantum claims.",
        },
        {
            "id": "nonlinear.product.homogeneous_twist_times_ell2_extra.bounded_tangent_cone",
            "scope": homogeneous_twist_scope,
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": _mode_data(
                _second(
                    ("OBSTRUCTED", "Every nonzero point on the complete aligned orbit has B nonzero, and its zero-frequency polar L=2 metric_00 source contains the uncancellable coefficient -7*B^2*t^2; no bounded finite-quasiperiodic correction exists."),
                    (
                        "CERTIFIED" if smooth_extension_ready else "OPEN",
                        "Every orbit point admits a real smooth spatially periodic finite exponential-polynomial second-order correction; the complete finite channel ledger has no nonstabilizer cokernel after the five moment maps vanish. The potential p-shell circumference cross resonance has a coefficient-explicit ordinary harmonic primitive on all six axial and eight polar rows, so that actual source needs no secular prefactor."
                        if smooth_extension_ready else
                        "The full eight-row zero-frequency polar L=2 twist-self source has an exact polynomial primitive with all remainders zero; the complete global-extra mixed-channel smooth correction awaits a schema-valid, content-addressed certificate with a PASS Tier-1 receipt.",
                    ),
                    ("NO_CERTIFIED_MAP", "No compact-product retarded BV complex or causal correction carrier is certified."),
                ),
                dispersion=("CERTIFIED", "The theorem uses the generalized-zero homogeneous/twist block and the k=0 ell=2 extra shell omega_e=4/sqrt(3)."),
                pairing=("CERTIFIED", "The exact action-derived occupation and twist moment maps are imported in the same reduced carrier."),
                taub=("CERTIFIED", "The full declared nonzero-extra common zero locus of all five stabilizer maps and completed resonance functionals is the aligned SO(3) orbit; no off-axis branch remains."),
                resonance=("CERTIFIED", "Exact coefficient elimination gives a=b=d=0 and rank stratification forces the extra tensor and twist position to align with the twist-velocity axis."),
            ),
            "evidence": _evidence(*(("global_extra_smooth_extension", "circumference_transport_primitive") if smooth_extension_ready else ()), "homogeneous_twist_extra_bounded_obstruction", "homogeneous_twist_polynomial_correction", "homogeneous_twist_extra_cone", "homogeneous_twist_extra_source", "relative_branch_dictionary", "dictionary", "cone"),
            "claim_boundary": (
                "The correction-class split is certified on every nonzero point of the complete aligned orbit in the declared single-k=0 homogeneous/twist times ell=2 extra REDUCED-MODE carrier: bounded/finite-quasiperiodic corrections are obstructed, while smooth exponential-polynomial corrections exist. This correction-class-specific theorem does not cover causal corrections, opposite momenta or multiple fibres, activate either cyclic Bridge 2, descend to final cohomology, or establish observational, particle or quantum claims."
                if smooth_extension_ready else
                "The bounded/finite-quasiperiodic second-order problem is obstructed on every nonzero point of the complete aligned orbit in the declared single-k=0 homogeneous/twist times ell=2 extra REDUCED-MODE carrier. This correction-class-specific no-go does not obstruct smooth secular or causal corrections, cover opposite momenta or multiple fibres, activate either cyclic Bridge 2, descend to final cohomology, or establish observational, particle or quantum claims."
            ),
        },
        {
            "id": "nonlinear.product.bridge1.exceptional_ell1_k0_solution_cofiber",
            "scope": exceptional_scope,
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": _mode_data(
                _second(
                    ("OPEN", "The exceptional all-row q1 map and its natural support-local covariant globalization are exact, but the q2 relative morphism remains open."),
                    ("OPEN", "No exceptional smooth-secular relative obstruction map is certified."),
                    ("NO_CERTIFIED_MAP", "No compact-product causal Green carrier is certified."),
                ),
                dispersion=("CERTIFIED", "CRT projectors separate twist omega^2=0, extra omega^2=4/3 and standard omega^2=4 at k=0."),
                pairing=("CERTIFIED", "The extra Gram matrix diag(16,3) is nonradical and orthogonal to the standard image."),
                taub=("OPEN", "The solution cofiber alone does not define the complete exceptional quadratic obstruction map."),
                resonance=("OPEN", "No complete exceptional nonlinear resonance table is certified."),
            ),
            "evidence": _evidence("exceptional_ell1_cofiber", "exceptional_global_offshell", "covariant_chain_map", "relative_branch_dictionary", "dictionary"),
            "claim_boundary": "This is an exact same-background REDUCED-MODE solution cofiber at ell=1,k=0. Its q1 coefficient map is now the harmonic reduction of one certified natural support-local minimal chain map, but the cofiber selection itself remains REDUCED-MODE; q2 and final residual descent remain open, so this row does not activate Bridge 2.",
        },
        {
            "id": "nonlinear.product.bridge1.exceptional_ell1_nonzero_k_solution_cofiber",
            "scope": exceptional_nonzero_k_scope,
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": _mode_data(
                _second(
                    ("OPEN", "The all-row q1 map, its natural support-local globalization and the solution cofiber are exact; the q2 relative morphism remains open."),
                    ("OPEN", "No nonzero-k smooth-secular relative obstruction map is certified."),
                    ("NO_CERTIFIED_MAP", "No compact-product causal Green carrier is certified."),
                ),
                dispersion=("CERTIFIED", "The standard shell omega^2-k^2=4 is the Einstein image and the extra shell omega^2-k^2=4/3 is a one-class cofiber in each parity."),
                pairing=("CERTIFIED", "Polynomial extra representatives have positive Gram weight 4*(3*k^2+4) in each parity and are orthogonal to the standard image."),
                taub=("OPEN", "The solution cofiber alone does not define the nonzero-k quadratic tangent cone."),
                resonance=("OPEN", "No complete nonzero-k nonlinear resonance table is certified."),
            ),
            "evidence": _evidence("exceptional_ell1_nonzero_k_cofiber", "exceptional_global_offshell", "covariant_chain_map", "relative_branch_dictionary", "dictionary"),
            "claim_boundary": "This is an exact same-background REDUCED-MODE solution cofiber for ell=1 at nonzero compact momentum. Its q1 coefficient map is now the reduction of one natural support-local minimal chain map. It does not supply q2, perform final residual descent, or activate Bridge 2.",
        },
        {
            "id": "nonlinear.product.bridge2.relative_linfinity_through_arity_three_preflight",
            "scope": relative_linfinity_scope,
            "descriptions": {
                "causal": "NO_CERTIFIED_MAP",
                "symplectic": "OBSTRUCTED",
                "nonlinear": "OBSTRUCTED" if relative_f2_obstructed else "OPEN" if linear_triangle_imported else "NO_CERTIFIED_MAP",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
            "mode_data": _mode_data(
                _second(
                    (
                        "OBSTRUCTED" if relative_f2_obstructed else "OPEN" if linear_triangle_imported else "NO_CERTIFIED_MAP",
                        (
                            "The frozen unary map has a nonzero relative constant-lapse Taub class on the certified ell=2 plus mode, so no f2 valued in the full smooth periodic fixed-bundle target domain can solve the arity-two morphism equation."
                            if relative_f2_obstructed
                            else
                            "The strict Delta2 operator is computed exactly with 50854 nonzero coefficients; the support-local f2 homotopy solve is active and neither existence nor obstruction is yet promoted."
                            if relative_arity_two_computed
                            else "The noncyclic all-row linear triangle, endpoints and both complete same-background q1/q2/q3 payloads are imported; Delta2 and the allowed f2 homotopy solve are now active."
                            if all_relative_inputs_imported
                            else "The noncyclic all-row linear triangle, endpoints and complete Einstein-Maxwell q1/q2/q3 payload are imported; the same-background Weyl-Maxwell payload is still missing."
                            if einstein_taylor_imported
                            else "The noncyclic all-row linear triangle and endpoints are imported; both same-background product q2/q3 payloads are still missing."
                        )
                        if linear_triangle_imported
                        else "The support-local minimal q1 chain map is certified, but the noncyclic three-form triangle, finite endpoints and both same-background product q2/q3 payloads are missing.",
                    ),
                    (
                        "OBSTRUCTED" if relative_f2_obstructed else "NO_CERTIFIED_MAP",
                        "The same constant-lapse adjoint class annihilates q1-exact smooth periodic corrections even when secular time dependence is admitted; alternative Taub-zero/cofiber architectures remain open."
                        if relative_f2_obstructed
                        else "No full relative morphism exists on which to compare smooth-secular correction classes.",
                    ),
                    ("NO_CERTIFIED_MAP", "No compact-product retarded relative morphism is certified."),
                ),
                dispersion=(
                    "CERTIFIED" if linear_triangle_imported else "NO_CERTIFIED_MAP",
                    "The complete support-local mapping cofiber and all declared solution cofibers are imported."
                    if linear_triangle_imported
                    else "Sectoral solution cofibers do not supply the full off-shell relative carrier.",
                ),
                pairing=("OBSTRUCTED", "A standard-pairing cyclic relative triangle is impossible by the generic inertia theorem; the certified replacement keeps the Einstein, pulled-back Weyl and relative forms distinct."),
                taub=(
                    "CERTIFIED" if relative_f2_obstructed else "OPEN" if linear_triangle_imported else "NO_CERTIFIED_MAP",
                    "The certified ell=2 plus mode pairs with the target constant-lapse class as -54*(1+sqrt(3))/5, obstructing f2 on the full frozen carrier."
                    if relative_f2_obstructed
                    else "Selected D^2E=q2 source blocks do not constitute the complete relative cokernel map.",
                ),
                resonance=(
                    "OBSTRUCTED" if relative_f2_obstructed else "OPEN" if linear_triangle_imported else "NO_CERTIFIED_MAP",
                    "The direct full-domain morphism stops at arity two: the nonzero relative Taub class obstructs f2, so arity three is not authorized until a Taub-zero or cofiber architecture is declared."
                    if relative_f2_obstructed
                    else "The strict Delta2 operator is exact and nonzero; its f2 primitive, the arity-three morphism defect and their cohomology images remain open."
                    if relative_arity_two_computed
                    else "Delta2, the arity-three morphism defect and their cohomology images have not been computed.",
                ),
            ),
            "evidence": _evidence("relative_linfinity_preflight", "einstein_product_taylor", "weyl_product_taylor", "relative_arity_two_defect", "relative_f2_taub_obstruction", "relative_charge_koszul_preflight", "covariant_chain_map", "relative_branch_dictionary", "generic_cyclic_map_inertia_obstruction", "dictionary", "mixed_obstruction"),
            "claim_boundary": (
                "Compact-product NONCYCLIC_THREE_FORM linear Bridge 1 and both complete same-background q1/q2/q3 payloads are imported, but the frozen direct full-domain morphism is obstructed at arity two. The certified ell=2 plus cocycle has relative constant-lapse pairing -54*(1+sqrt(3))/5, while every q1_W-exact smooth periodic fixed-bundle correction pairs to zero; hence no f2 extends the frozen f1 on that carrier and arity three is not authorized. The post-obstruction REDUCED-MODE architecture is now selected: retain the unary mapping cofiber and encode the five stabilizer charges by a Koszul derived Taub-zero-locus receiver; its complete off-shell local lift remains OPEN or NO_CERTIFIED_MAP according to category. The standard-pairing cyclic route remains separately obstructed, all Berger tensors remain ineligible substitutes, and q4 is not authorized."
                if relative_f2_obstructed
                else
                "Compact-product NONCYCLIC_THREE_FORM linear Bridge 1 and both complete executable same-background q1/q2/q3 payloads are imported. The strict Delta2 operator is exact and nonzero, so the support-local f2 solve is active; f2 existence or obstruction, the arity-three defect, cohomology survival and admissible removal remain OPEN or NO_CERTIFIED_MAP. The standard-pairing cyclic route remains obstructed, all Berger tensors remain ineligible substitutes, and q4 is not authorized."
                if relative_arity_two_computed
                else "Compact-product NONCYCLIC_THREE_FORM linear Bridge 1 and both complete executable same-background q1/q2/q3 payloads are imported. The relative morphism solve is active, but Delta2, the allowed f2 correction, the arity-three defect, cohomology survival and admissible removal remain OPEN or NO_CERTIFIED_MAP. The standard-pairing cyclic route remains obstructed, all Berger tensors remain ineligible substitutes, and q4 is not authorized."
                if all_relative_inputs_imported
                else "Compact-product NONCYCLIC_THREE_FORM linear Bridge 1 and the complete executable same-background Einstein-Maxwell q1/q2/q3 payload are imported. Bridge 2 remains INPUT_BLOCKED only on the Weyl-Maxwell payload. The standard-pairing cyclic route is obstructed; all Berger tensors remain ineligible substitutes. Delta2, the arity-three defect, cohomology survival and admissible removal remain OPEN or NO_CERTIFIED_MAP, and q4 is not authorized."
                if linear_triangle_imported
                else "Compact-product Bridge 2 remains INPUT_BLOCKED after certification of the natural support-local minimal q1 map: Bridge 1 must still supply the V2 noncyclic three-form EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1 with finite endpoints, and complete same-background Einstein-Maxwell and Weyl-Maxwell q2/q3 payloads remain absent. A standard-pairing cyclic triangle is obstructed. Sectoral cofibers, on-shell maps, selected D^2E sources and all Berger tensors are ineligible substitutes. Cohomology survival, deformation nontriviality and admissible removal remain NO_CERTIFIED_MAP. The Berger filtered-cyclic ell3 obstruction is preserved, and q4 is not authorized."
            ),
        },
        {
            "id": "nonlinear.product.bridge2.relative_charge_koszul_receiver_preflight",
            "scope": relative_charge_scope,
            "descriptions": {
                "causal": "NO_CERTIFIED_MAP",
                "symplectic": "CERTIFIED" if relative_charge_receiver_selected else "OPEN",
                "nonlinear": "OPEN",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
            "mode_data": _mode_data(
                _second(
                    ("OPEN", "The five-charge derived zero locus is defined, but its complete standard-radiative common zero locus and bounded correction problem are not classified."),
                    ("OPEN", "The reduced Koszul receiver does not yet supply the off-shell smooth-secular f2 equation."),
                    ("NO_CERTIFIED_MAP", "No compact-product retarded relative Koszul/BV lift is certified."),
                ),
                dispersion=("CERTIFIED", "The standard Einstein plus/minus branches and their exact relative weights are imported for every ell>=2 and compact momentum."),
                pairing=("CERTIFIED", "The relative solution form is iota^*Omega_WM-Omega_EM, and its five stabilizer moment maps are represented by the reduced Koszul differential."),
                taub=("CERTIFIED", "Five Killing charges are retained; constant U1 reducibility is not a sixth Taub charge. The ell=2 plus H component is -54*(1+sqrt(3))/5."),
                resonance=("OPEN", "The architecture is selected, but the complete off-shell five-charge polarization and repaired relative f2 remain open; arity three is unauthorized."),
            ),
            "evidence": _evidence("relative_charge_koszul_preflight", "relative_standard_charge_q2", "relative_f2_taub_obstruction", "relative_arity_two_defect", "relative_linfinity_preflight"),
            "claim_boundary": "This REDUCED-MODE row selects a derived charge receiver, not a support-local nonlinear morphism. The certified unary mapping cofiber is retained; the five connected-isometry moment maps enter through a square-zero 32-dimensional exterior Koszul presentation. The constant U1 endpoint remains reducibility. Exceptional/global charge formulas, a complete off-shell polarization, support-local BV extension, repaired f2, arity three, causal propagation, observables, particles and quantum transfer remain OPEN or NO_CERTIFIED_MAP.",
        },
        {
            "id": "nonlinear.product.bridge2.standard_radiative_five_charge_q2",
            "scope": relative_charge_q2_scope,
            "descriptions": {
                "causal": "NO_CERTIFIED_MAP",
                "symplectic": "CERTIFIED",
                "nonlinear": "CERTIFIED",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
            "mode_data": _mode_data(
                _second(
                    ("OPEN", "The five charge outputs are exact, but bounded solvability also requires the non-charge resonance functionals."),
                    ("OPEN", "The reduced charge bracket does not itself construct a smooth-secular f2 correction."),
                    ("NO_CERTIFIED_MAP", "No retarded local-current lift of the global charge bracket is certified."),
                ),
                dispersion=("CERTIFIED", "Both standard Einstein branches, both parities, every ell>=2 and every compact momentum are included."),
                pairing=("CERTIFIED", "The exact axial/polar Einstein coefficient forms, angular weight and relative branch multipliers define the charge bracket."),
                taub=("CERTIFIED", "q2_charge,X=<zeta_X,Delta2>; its diagonal half is the relative moment map for all five stabilizers. The H witness is -108*(1+sqrt(3))/5 before the diagonal half."),
                resonance=("OPEN", "This operation records the five persistent charge obstructions but does not include exceptional/global inputs or non-charge bounded resonances."),
            ),
            "evidence": _evidence("relative_standard_charge_q2", "relative_charge_koszul_preflight", "relative_f2_taub_obstruction"),
            "claim_boundary": "This is an exact five-output arity-two operation on the standard-radiative REDUCED-MODE relative receiver. It records rather than cancels the direct f2 obstruction. Exceptional/global source cohomology, off-shell local jets, a support-local BV/Koszul lift, repaired f2, arity three, causal propagation, observables, particles and quantum transfer remain OPEN or NO_CERTIFIED_MAP.",
        },
        {
            "id": "nonlinear.product.bridge2.complete_standard_source_five_charge_q2",
            "scope": relative_complete_charge_q2_scope,
            "descriptions": {
                "causal": "NO_CERTIFIED_MAP",
                "symplectic": "CERTIFIED",
                "nonlinear": "CERTIFIED",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
            "mode_data": _mode_data(
                _second(
                    ("OPEN", "The complete five-charge Hessian is known, but the common zero locus depends on the bounded, smooth-secular or causal correction class."),
                    ("OPEN", "No smooth-secular f2 primitive is constructed by this charge operation."),
                    ("NO_CERTIFIED_MAP", "No retarded support-local current-density lift is certified."),
                ),
                dispersion=("CERTIFIED", "The input is the complete standard source decomposition: generic radiative, physical ell1, homogeneous and twist blocks."),
                pairing=("CERTIFIED", "All four source/target pairing blocks and every cross-block zero are exact."),
                taub=("CERTIFIED", "The symmetric q2 has precisely the five connected-isometry outputs; constant U1 reducibility is absent."),
                resonance=("OPEN", "The operation records all five charge obstructions, but non-charge resonant functionals and correction-class solvability remain separate."),
            ),
            "evidence": _evidence("relative_complete_standard_charge_q2", "relative_standard_charge_q2", "relative_charge_koszul_preflight", "relative_f2_taub_obstruction"),
            "claim_boundary": "This REDUCED-MODE operation covers the complete certified standard Einstein-Maxwell source cohomology, including exceptional/global standard blocks. It excludes target-only extra Weyl cofiber inputs and does not define a local-current or support-local BV/Koszul lift, solve a correction-class tangent cone, repair f2, authorize arity three, or establish causal, observational, particle or quantum equivalence.",
        },
        {
            "id": "nonlinear.product.bridge2.direct_finite_charge_support_local_lift_obstruction",
            "scope": relative_locality_obstruction_scope,
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OBSTRUCTED", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": _mode_data(
                _second(
                    ("OBSTRUCTED", "A nonzero support-local differential map cannot land directly in constant global charge rows."),
                    ("OPEN", "The horizontal Noether-current/divergence cone is the minimal admissible local carrier, but its coefficients are not exported."),
                    ("NO_CERTIFIED_MAP", "Cauchy-slice integration is a later global operation, not a support-preserving local map."),
                ),
                dispersion=("NOT_APPLICABLE", "This is a support-category theorem, not a dispersion calculation."),
                pairing=("CERTIFIED", "The nonzero complete-standard charge q2 supplies the contradiction witness."),
                taub=("CERTIFIED", "The H diagonal is -108*(1+sqrt(3))/5, so the finite receiver cannot be represented by the zero local map."),
                resonance=("NOT_APPLICABLE", "The obstruction precedes correction-class resonance analysis."),
            ),
            "evidence": _evidence("relative_finite_charge_locality_obstruction", "relative_complete_standard_charge_q2", "relative_charge_koszul_preflight"),
            "claim_boundary": "Only the direct support-local lift into constant finite charge rows is obstructed. The global reduced-mode charge receiver remains certified, while a local horizontal 3-form current to 4-form divergence cone, its cyclic dual completion, causal enlargement and later Cauchy-slice integration remain OPEN or NO_CERTIFIED_MAP.",
        },
        {
            "id": "nonlinear.product.bridge2.polarized_relative_noether_current_seed",
            "scope": relative_current_seed_scope,
            "descriptions": {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": _mode_data(
                _second(
                    ("OPEN", "The local current is exported, but no bounded correction theorem follows before the off-shell divergence cone is certified."),
                    ("OPEN", "The local current is exported, but no smooth-secular f2 primitive is constructed."),
                    ("OPEN", "The seed is support local; its divergence cone and retarded Green enlargement remain unconstructed."),
                ),
                dispersion=("NOT_APPLICABLE", "This is a local current-density construction, not a dispersion calculation."),
                pairing=("CERTIFIED", "All four action-derived relative Lee-Wald components and their symmetric stabilizer polarization are exported."),
                taub=("OPEN", "Cauchy-slice integration has not yet been replayed against every block of the complete five-charge q2."),
                resonance=("OPEN", "The off-shell current divergence and equation-row factorization remain the next gate."),
            ),
            "evidence": _evidence("relative_polarized_noether_current_seed", "relative_finite_charge_locality_obstruction", "relative_complete_standard_charge_q2"),
            "claim_boundary": "This LOCAL-ALGEBRAIC row certifies a nonzero support-local polarized relative Noether-current seed with a bundle-covariant Maxwell stabilizer lift. It does not certify the off-shell horizontal divergence cone, cyclic dual rows, equality of all integrated five-charge blocks, a repaired f2, arity three, retarded propagation, an observable, a particle map or a quantum transfer.",
        },
        {
            "id": "nonlinear.product.bridge2.relative_hessian_green_current_cone",
            "scope": relative_green_cone_scope,
            "descriptions": {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": _mode_data(
                _second(
                    ("OPEN", "The off-shell current cone is exact, but no bounded relative f2 is produced before stabilizer precomposition."),
                    ("OPEN", "The current cone does not construct a smooth-secular correction."),
                    ("OPEN", "No retarded inverse has yet been transported through the current cone."),
                ),
                dispersion=("NOT_APPLICABLE", "This is an all-field local Green-concomitant identity."),
                pairing=("CERTIFIED", "The antisymmetric current is derived from the complete action Hessians and their certified cyclic pairings."),
                taub=("OPEN", "The five stabilizer actions and Cauchy integrations remain to be applied."),
                resonance=("OPEN", "The Green-current/Lee-Wald improvement comparison remains open."),
            ),
            "evidence": _evidence("relative_hessian_green_current_cone", "relative_polarized_noether_current_seed", "relative_complete_standard_charge_q2"),
            "claim_boundary": "The complete fourteen-field relative Hessian has an exact finite-order antisymmetric Green current and coefficientwise off-shell divergence identity. This does not yet identify it with the Lee-Wald representative up to a horizontal improvement, precompose all five stabilizer actions, add cyclic BV-dual rows, reproduce every global charge block, repair f2, authorize arity three, or establish causal, observational, particle or quantum claims.",
        },
        {
            "id": "nonlinear.product.bridge1.generic_standard_pairing_cyclic_map_inertia_obstruction",
            "scope": identity_cyclic_scope,
            "descriptions": {"causal": "NOT_APPLICABLE", "symplectic": "OBSTRUCTED", "nonlinear": "NO_CERTIFIED_MAP", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": _mode_data(
                _second(
                    ("NO_CERTIFIED_MAP", "The standard-pairing cyclic map is obstructed and cannot activate the bounded relative interaction problem."),
                    ("NO_CERTIFIED_MAP", "The noncyclic three-form triangle has not been certified for the smooth-secular problem."),
                    ("NO_CERTIFIED_MAP", "No compact-product causal Green relative morphism is certified."),
                ),
                dispersion=("CERTIFIED", "The obstruction is evaluated on both q-primary Einstein-Maxwell shells for every generic physical harmonic."),
                pairing=("OBSTRUCTED", "The Einstein source form has inertia (2,0), while the Weyl form on the complete q-primary target has inertia (1,1), in both axial and polar parity blocks."),
                taub=("NOT_APPLICABLE", "This is a linear cyclic-pairing obstruction, not a quadratic adjoint-cokernel verdict."),
                resonance=("NOT_APPLICABLE", "No nonlinear harmonic resonance is decided by the linear pairing defect."),
            ),
            "evidence": _evidence("identity_cyclic_obstruction", "generic_cyclic_map_inertia_obstruction", "relative_branch_dictionary"),
            "claim_boundary": "Every real-structure-preserving product-equivariant cohomology-isomorphic correction is obstructed from being cyclic for the standard action-derived pairings on the generic physical fibres. This includes corrected nonidentity maps, declared chain-homotopy repairs and cohomologically exact current improvements. A noncyclic off-shell triangle carrying three distinct forms, an explicitly pairing-changed theorem, exceptional/global sectors and final residual descent remain OPEN or NO_CERTIFIED_MAP. This result does not by itself decide Delta2, ell3 on cohomology, observables, particles or quantum states.",
        },
    ]


def build() -> dict[str, Any]:
    value = {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "d_quotient_nonlinear",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha(Path(__file__)),
        "status_vocabulary": STATUSES,
        "description_axes": AXES,
        "entries": entries(),
        "verification_commands": [
            "python3 -m d_quotient_classical.atlas.generate_nonlinear_atlas_fragment --check",
            "python3 residual_atlas/validate_fragment.py d_quotient_classical/atlas/nonlinear-atlas-fragment.json",
            "python3 -m unittest d_quotient_classical.atlas.tests.test_nonlinear_atlas_fragment",
        ],
    }
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif json.loads(OUTPUT.read_text()) != value:
        raise AssertionError("nonlinear atlas fragment is stale")
    print("NONLINEAR_RESIDUAL_ATLAS_FRAGMENT_V1: PASS")


if __name__ == "__main__":
    main()
