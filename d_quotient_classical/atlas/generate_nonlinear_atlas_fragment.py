#!/usr/bin/env python3
"""Generate the fail-closed nonlinear residual-atlas fragment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


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
    "abd_extra_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.json",
    "exceptional_ell1_cofiber": ROOT / "bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json",
    "relative_linfinity_preflight": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_LINFINITY_THROUGH_ARITY_THREE_PREFLIGHT_V1.json",
    "identity_cyclic_obstruction": ROOT / "bridge/certificates/einstein_weyl_generic_identity_cyclic_obstruction.json",
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
            "claim_boundary": "Bridge 2 is INPUT_BLOCKED. It activates only after an admissible same-background mixed-bundle, noncontractible-cofiber, or explicitly REDUCED-MODE branch map passes the importer. The importer requires the complete atlas mode scope and content-addressed crosswalk, chain, inclusion/projection/cofiber, pairing, gauge/nondynamical, K_Berger-equivariance, cohomology and independent-verifier evidence. The compact-product mode-pair row is not a Berger crosswalk. Projected cohomology, cyclic deformation nontriviality and admissible removal remain NO_CERTIFIED_MAP, and q4 is not authorized.",
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
    abd_scope = {
        **product_common,
        "carrier": "homogeneous generalized-zero Einstein block crossed with the generic ell=2 extra-primary block",
        "degree": 2,
        "parity": "axial and polar output sectors kept separate",
        "ell": "0 x 2 -> 2",
        "m": "m=0 direct fixtures; every m by SO(3) equivariance",
        "k": 0,
        "omega": "generalized zero crossed with omega_e=4/sqrt(3)",
    }
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
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": _mode_data(
                _second(
                    ("OPEN", "The generic axial cofiber is certified, but its complete branchwise quadratic obstruction map has not been assembled."),
                    ("OPEN", "No complete smooth-secular relative obstruction map is certified."),
                    ("NO_CERTIFIED_MAP", "No compact-product causal Green carrier is certified."),
                ),
                dispersion=("CERTIFIED", "The q-primary Einstein shells and p-primary extra shell are explicitly separated."),
                pairing=("CERTIFIED", "The action-derived Einstein and extra blocks are orthogonal, with inertias (1,1) and (2,0); the fixed identity chain map has a separately certified nonradical cyclic defect."),
                taub=("OPEN", "Only selected quadratic source and moment-map blocks are certified; the complete generic map is open."),
                resonance=("OPEN", "No complete all-input generic axial resonance table is certified."),
            ),
            "evidence": _evidence("relative_branch_dictionary", "identity_cyclic_obstruction", "dictionary"),
            "claim_boundary": "This is a same-background generic-axial derived cofiber and action-pairing map. Its fixed identity field inclusion is obstructed from being a strict cyclic map; corrected nonidentity or chain-homotopy cyclic morphisms remain open. It is a sectoral Bridge-1 input, not the all-sector EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1 and not a Berger crosswalk. No complete q2/q3 relative morphism, cohomology operation or cyclic deformation verdict is promoted.",
        },
        {
            "id": "nonlinear.product.bridge1.generic_polar_relative_branch_map",
            "scope": product_polar_scope,
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": _mode_data(
                _second(
                    ("OPEN", "The polar solution cofiber is certified; the fixed identity cyclic map is obstructed, while corrected cyclic maps and the complete quadratic obstruction map remain open."),
                    ("OPEN", "No complete smooth-secular relative obstruction map is certified."),
                    ("NO_CERTIFIED_MAP", "No compact-product causal Green carrier is certified."),
                ),
                dispersion=("CERTIFIED", "The q-primary Einstein shells and p-primary extra shell are explicitly separated."),
                pairing=("CERTIFIED", "The direct action-derived polar Einstein/extra pairing is nondegenerate and orthogonal; its nonradical defect obstructs strict cyclicity of the fixed identity chain map."),
                taub=("OPEN", "The polar source fixtures do not yet constitute the complete relative obstruction map."),
                resonance=("OPEN", "The fixed identity cyclic route is obstructed; corrected nonidentity/homotopy maps and the complete all-input polar resonance table remain open."),
            ),
            "evidence": _evidence("relative_branch_dictionary", "identity_cyclic_obstruction", "dictionary"),
            "claim_boundary": "This is a same-background generic-polar solution cofiber with a certified direct pairing. Strict cyclic compatibility of its fixed identity field map is obstructed; corrected nonidentity or chain-homotopy cyclic morphisms and final residual descent are open. It therefore does not activate a cyclic relative L_infinity theorem or the global Bridge-1 gate.",
        },
        {
            "id": "nonlinear.product.homogeneous_abd_times_ell2_extra.partial_resonance_matrix",
            "scope": abd_scope,
            "descriptions": {"causal": "OPEN", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": _mode_data(
                _second(
                    ("OPEN", "All a,b,d compatibility columns are exact, but twist position/velocity columns and the simultaneous zero locus remain missing."),
                    ("OPEN", "Secular sufficiency requires the complete operator and is not inferred from the projected source matrix."),
                    ("OPEN", "No compact-product retarded complex is certified."),
                ),
                dispersion=("CERTIFIED", "The output lies on the generic ell=2 extra shell omega_e=4/sqrt(3)."),
                pairing=("CERTIFIED", "The exact axial and polar adjoint bases define the displayed compatibility polynomials."),
                taub=("OPEN", "The stabilizer and complete bounded-resonance common zero locus has not been solved."),
                resonance=("CERTIFIED", "Within each parity and polarization, the a,b,d projected polynomial columns have exact rank three."),
            ),
            "evidence": _evidence("abd_extra_source", "relative_branch_dictionary", "dictionary"),
            "claim_boundary": "This certifies a partial D^2E=q2 source/compatibility matrix on the compact product background. Its homogeneous global input leg has only an on-shell map lifecycle. No individual mode is declared obstructed: twist position and velocity may contribute to the same extra-shell channel. Smooth-secular, causal, final-residual, observational and quantum conclusions remain open or NO_CERTIFIED_MAP.",
        },
        {
            "id": "nonlinear.product.bridge1.exceptional_ell1_k0_solution_cofiber",
            "scope": exceptional_scope,
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": _mode_data(
                _second(
                    ("OPEN", "The exact solution cofiber does not supply the exceptional off-shell q1/q2 relative morphism."),
                    ("OPEN", "No exceptional smooth-secular relative obstruction map is certified."),
                    ("NO_CERTIFIED_MAP", "No compact-product causal Green carrier is certified."),
                ),
                dispersion=("CERTIFIED", "CRT projectors separate twist omega^2=0, extra omega^2=4/3 and standard omega^2=4 at k=0."),
                pairing=("CERTIFIED", "The extra Gram matrix diag(16,3) is nonradical and orthogonal to the standard image."),
                taub=("OPEN", "The solution cofiber alone does not define the complete exceptional quadratic obstruction map."),
                resonance=("OPEN", "No complete exceptional nonlinear resonance table is certified."),
            ),
            "evidence": _evidence("exceptional_ell1_cofiber", "relative_branch_dictionary", "dictionary"),
            "claim_boundary": "This is an exact same-background REDUCED-MODE solution cofiber only at ell=1,k=0. The exceptional off-shell ghost-field-equation-identity chain map, nonzero-k cofiber and final residual descent remain open, so this row does not activate cyclic Bridge 2.",
        },
        {
            "id": "nonlinear.product.bridge2.relative_linfinity_through_arity_three_preflight",
            "scope": relative_linfinity_scope,
            "descriptions": {axis: "NO_CERTIFIED_MAP" for axis in AXES},
            "mode_data": _mode_data(
                _second(
                    ("NO_CERTIFIED_MAP", "The full off-shell relative triangle and both same-background product Taylor payloads are missing."),
                    ("NO_CERTIFIED_MAP", "No full relative morphism exists on which to compare smooth-secular correction classes."),
                    ("NO_CERTIFIED_MAP", "No compact-product retarded relative morphism is certified."),
                ),
                dispersion=("NO_CERTIFIED_MAP", "Sectoral solution cofibers do not supply the full off-shell relative carrier."),
                pairing=("NO_CERTIFIED_MAP", "The required full-BV cyclic pairing compatibility has not been imported on both sides of the triangle."),
                taub=("NO_CERTIFIED_MAP", "Selected D^2E=q2 source blocks do not constitute the complete relative cokernel map."),
                resonance=("NO_CERTIFIED_MAP", "Delta2, the arity-three morphism defect and their cohomology images have not been computed."),
            ),
            "evidence": _evidence("relative_linfinity_preflight", "relative_branch_dictionary", "dictionary", "mixed_obstruction"),
            "claim_boundary": "Compact-product Bridge 2 is INPUT_BLOCKED until Bridge 1 supplies EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1 and complete same-background Einstein-Maxwell and Weyl-Maxwell q1,q2,q3 payloads. Sectoral cofibers, on-shell maps, selected D^2E sources and all Berger tensors are ineligible substitutes. Cohomology survival, cyclic deformation nontriviality and admissible removal remain NO_CERTIFIED_MAP. The Berger filtered-cyclic ell3 obstruction is preserved, and q4 is not authorized.",
        },
        {
            "id": "nonlinear.product.bridge1.generic_identity_cyclic_compatibility_obstruction",
            "scope": identity_cyclic_scope,
            "descriptions": {"causal": "NOT_APPLICABLE", "symplectic": "OBSTRUCTED", "nonlinear": "NO_CERTIFIED_MAP", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": _mode_data(
                _second(
                    ("NO_CERTIFIED_MAP", "The obstructed fixed identity map cannot activate the bounded relative interaction problem."),
                    ("NO_CERTIFIED_MAP", "No corrected cyclic relative map has been certified for the smooth-secular problem."),
                    ("NO_CERTIFIED_MAP", "No compact-product causal Green relative morphism is certified."),
                ),
                dispersion=("CERTIFIED", "The obstruction is evaluated on both q-primary Einstein-Maxwell shells for every generic physical harmonic."),
                pairing=("OBSTRUCTED", "The induced solution-pairing defect D=R-I is nonzero and rank two in both axial and polar parity blocks."),
                taub=("NOT_APPLICABLE", "This is a linear cyclic-pairing obstruction, not a quadratic adjoint-cokernel verdict."),
                resonance=("NOT_APPLICABLE", "No nonlinear harmonic resonance is decided by the linear pairing defect."),
            ),
            "evidence": _evidence("identity_cyclic_obstruction", "relative_branch_dictionary"),
            "claim_boundary": "Only strict cyclic compatibility of the certified generic chain maps with their fixed identity field inclusion and standard action-derived pairings is obstructed. Corrected nonidentity symplectic maps, pairing improvements, cyclic maps up to declared chain homotopy, exceptional/global sectors and final residual descent remain OPEN or NO_CERTIFIED_MAP. This result does not by itself decide Delta2, ell3 on cohomology, observables, particles or quantum states.",
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
