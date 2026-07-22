#!/usr/bin/env python3
"""Generate the publication-independent Bridge Phase-1 claim manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "bridge/phase1"
OUT = BASE / "BRIDGE_PHASE1_EINSTEIN_EXTRA_CONTRIBUTION_V1.json"
AUDIT = ROOT / "planning/paper-coverage/bridge-phase1-einstein-extra-materiality-2026-07-22.json"

SOURCES = {
    "linear_exact_sequence": "bridge/certificates/EINSTEIN_WEYL_PARITY_COMPLETE_RESIDUAL_EXACT_SEQUENCE_MAXIMAL_V1.json",
    "symplectic_extension": "bridge/certificates/EINSTEIN_WEYL_SYMPLECTIC_EXTENSION_CLASSIFICATION_V1.json",
    "axial_lee_wald": "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_lee_wald": "bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1.json",
    "finite_harmonic_cone": "bridge/certificates/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1.json",
    "kuranishi_carrier": "bridge/certificates/EINSTEIN_WEYL_CONSTRAINT_ALGEBROID_KURANISHI_CARRIER_V1.json",
    "mixed_charge_correspondence": "bridge/certificates/EINSTEIN_WEYL_MIXED_CHARGE_DERIVED_CORRESPONDENCE_V1.json",
    "third_order_evaluation": "bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_EVALUATION_V1.json",
    "paper13_disposition": "bridge/einstein_sector/receipts/PAPER13_THIRD_ORDER_KURANISHI_DISPOSITION_V1_TIER_RECEIPT.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_sources() -> tuple[dict, dict]:
    imports, docs = {}, {}
    for role, rel in SOURCES.items():
        path = ROOT / rel
        doc = json.loads(path.read_text())
        docs[role] = doc
        imports[role] = {
            "path": rel,
            "result_id": doc["result_id"],
            "result_state": doc.get("result_state", "NOT_APPLICABLE_RECEIPT_OR_THEOREM_FREEZE"),
            "lifecycle_state": doc["lifecycle_state"],
            "sha256": sha(path),
        }
    return imports, docs


def scope(parity: str, carrier: str, degree: str, harmonic: str, charge: str) -> dict:
    return {
        "theory": "Einstein-Maxwell source, Weyl-Maxwell target and extra cofiber",
        "background": "compactified magnetically supported Plebanski-Hacyan product",
        "boundaries": "closed S1_L x S2 before final stabilizer reduction",
        "charge_fibre": charge,
        "carrier": carrier,
        "degree": degree,
        "parity": parity,
        "harmonic_support": harmonic,
    }


def build_manifest() -> dict:
    imports, d = load_sources()
    assert d["linear_exact_sequence"]["classification"]["parity_complete_table_certified"]
    assert d["symplectic_extension"]["classification"]["admissible_corrected_parity_complete_cyclic_split"] is False
    assert d["axial_lee_wald"]["classification"]["direct_four_dimensional_Lee_Wald_match"]
    assert d["polar_lee_wald"]["classification"]["direct_four_dimensional_current_is_producer"]
    assert d["finite_harmonic_cone"]["classification"]["five_and_only_five_EP_cokernel_covectors"]
    assert d["mixed_charge_correspondence"]["classification"]["separate_neutral_projection_exists"] is False
    assert d["third_order_evaluation"]["classification"]["global_K3_class_zero"]
    assert d["third_order_evaluation"]["classification"]["bounded_third_order_extension"] is False

    rows = [
        {
            "row_id": "parity_complete_linear_carrier", "sequence": 0, "source": "linear_exact_sequence",
            "scope": scope("axial and polar separately", "pre-residual H0 short exact sequence", "linear", "all certified ell,m,k,omega strata", "fixed magnetic bundle; Q_e, W_x and twist holonomies retained"),
            "claim": "The Einstein image injects and the extra cofiber is exact at pre-residual H0 in both parities.",
            "disposition": "CERTIFIED_PRERESIDUAL_ONLY", "representative_dependence": "INTRINSIC",
            "correction_class": "NOT_APPLICABLE", "lifecycle": "CLASSIFIED",
        },
        {
            "row_id": "parity_complete_descended_pairing", "sequence": 1, "source": "symplectic_extension",
            "scope": scope("axial and polar separately", "finite-harmonic solution pairing", "linear symplectic", "generic ell>=2 plus certified exceptional and homogeneous blocks", "same fixed charge fibre as the linear carrier"),
            "claim": "The target has a canonical orthogonal extra complement, but no declared parity-complete cyclic identification with the source form.",
            "disposition": "ORTHOGONAL_SPLIT_CERTIFIED_CYCLIC_IDENTIFICATION_OBSTRUCTED", "representative_dependence": "SCHUR_COMPLEMENT_INTRINSIC_RAW_LIFT_DEPENDENT",
            "correction_class": "SHELL_AND_TIME_TRANSLATION_PRESERVING_COMPLEX_LINEAR", "lifecycle": "CLASSIFIED",
        },
        {
            "row_id": "axial_direct_lee_wald", "sequence": 2, "source": "axial_lee_wald",
            "scope": scope("axial", "local-gauge-reduced generic solution module", "linear symplectic", "ell>=2, every real compact k", "before final residual quotient"),
            "claim": "The direct four-dimensional Lee-Wald current gives extra inertia (2,0), full inertia (3,1), and zero Einstein-extra shell mixing.",
            "disposition": "CERTIFIED", "representative_dependence": "DIRECT_CURRENT_NORMALIZED",
            "correction_class": "NOT_APPLICABLE", "lifecycle": "CLASSIFIED",
        },
        {
            "row_id": "polar_direct_lee_wald", "sequence": 3, "source": "polar_lee_wald",
            "scope": scope("polar", "local-gauge-reduced generic solution module", "linear symplectic", "ell>=2, every allowed compact k", "before final residual quotient"),
            "claim": "The independent direct four-dimensional polar current gives extra inertia (2,0) and full inertia (3,1), without identifying polar representatives with axial ones.",
            "disposition": "CERTIFIED", "representative_dependence": "DIRECT_CURRENT_NORMALIZED",
            "correction_class": "NOT_APPLICABLE", "lifecycle": "CLASSIFIED",
        },
        {
            "row_id": "finite_harmonic_second_order_cone", "sequence": 4, "source": "finite_harmonic_cone",
            "scope": scope("all certified parities", "complete finite-support harmonic blocks", "second order", "finite harmonic sums", "five stabilizer covectors H,P_x,J1,J2,J3"),
            "claim": "Exactly five exponential-polynomial cokernel covectors remain; bounded corrections additionally require every polynomial and characteristic-shell functional to vanish.",
            "disposition": "FORMAL_EP_THEOREM_FROZEN_BOUNDED_LEDGER_FROZEN_ZERO_LOCUS_OPEN", "representative_dependence": "INTRINSIC_AT_SECOND_ORDER",
            "correction_class": "FINITE_EXPONENTIAL_POLYNOMIAL_VS_BOUNDED_QUASIPERIODIC", "lifecycle": "THEOREM_FROZEN",
        },
        {
            "row_id": "two_jet_charge_carrier", "sequence": 5, "source": "kuranishi_carrier",
            "scope": scope("all finite-harmonic branches; exact witness axial", "five-charge Koszul two-jet carrier", "second-order Kuranishi", "finite sums; witness ell=2,m=k=0", "total charge zero, not separately neutral Einstein and extra projections"),
            "claim": "The two-jet five-charge carrier is certified, while the ambient cofiber projection does not descend to separate charge-zero fibres.",
            "disposition": "CARRIER_CERTIFIED_LINEAR_COFIBER_PULLBACK_OBSTRUCTED", "representative_dependence": "INTRINSIC_BALANCED_CHARGE_CANCELLATION",
            "correction_class": "FORMAL_TWO_JET", "lifecycle": "CLASSIFIED",
        },
        {
            "row_id": "mixed_charge_derived_correspondence", "sequence": 6, "source": "mixed_charge_correspondence",
            "scope": scope("branchwise; exact witness axial", "homotopy pullback with explicit charge-transfer coordinate", "second-order derived correspondence", "arbitrary finite sums; exact witness ell=2,m=k=0", "anti-diagonal five-charge transfer retained"),
            "claim": "The mixed-charge homotopy pullback has d^2=0 and retains balanced cancellation; separate neutral projections remain obstructed.",
            "disposition": "CERTIFIED_CORRESPONDENCE_SEPARATE_NEUTRAL_PROJECTIONS_OBSTRUCTED", "representative_dependence": "INTRINSIC_TWO_JET",
            "correction_class": "FORMAL_TWO_JET", "lifecycle": "CLASSIFIED",
        },
        {
            "row_id": "balanced_axial_third_order", "sequence": 7, "source": "third_order_evaluation",
            "scope": scope("axial", "balanced Einstein-minus plus second extra-primary tangent", "third order", "input ell=2,m=k=0; closure ell=2,4,6", "fixed N=2 and Q_e; no Wilson-line shift"),
            "claim": "The intrinsic global K3 class vanishes, but all four original shells obstruct bounded extension for the certified second-order representative; a smooth secular preimage exists.",
            "disposition": "GLOBAL_QUOTIENT_CERTIFIED_BOUNDED_REPRESENTATIVE_OBSTRUCTED_SMOOTH_SECULAR_CERTIFIED", "representative_dependence": "GLOBAL_K3_CORRECTION_INDEPENDENT_SHELL_VERDICT_REPRESENTATIVE_SCOPED",
            "correction_class": "BOUNDED_QUASIPERIODIC_VS_SMOOTH_EXPONENTIAL_POLYNOMIAL; CAUSAL_RETARDED_NO_CERTIFIED_MAP", "lifecycle": "THEOREM_FROZEN",
        },
    ]
    traces = [
        {"branch_id": "einstein_image_axial", "linear": "CERTIFIED", "pairing": "CERTIFIED_INERTIA_1_1", "taub": "FIVE_COVECTOR_MAP_CERTIFIED", "second_order": "FINITE_HARMONIC_CRITERION_CERTIFIED", "third_order": "ONLY_BALANCED_FIXTURE_CROSSWALK; NO_BRANCHWIDE_THEOREM"},
        {"branch_id": "extra_axial", "linear": "CERTIFIED", "pairing": "CERTIFIED_NONRADICAL_INERTIA_2_0", "taub": "FIVE_COVECTOR_MAP_CERTIFIED", "second_order": "FINITE_HARMONIC_CRITERION_CERTIFIED", "third_order": "BALANCED_FIXTURE_GLOBAL_K3_ZERO; BOUNDED_REPRESENTATIVE_OBSTRUCTED; SMOOTH_SECULAR_SOLVABLE"},
        {"branch_id": "einstein_image_polar", "linear": "CERTIFIED", "pairing": "CERTIFIED_INERTIA_1_1", "taub": "FIVE_COVECTOR_MAP_CERTIFIED", "second_order": "FINITE_HARMONIC_CRITERION_CERTIFIED", "third_order": "NO_CERTIFIED_MAP"},
        {"branch_id": "extra_polar", "linear": "CERTIFIED", "pairing": "CERTIFIED_NONRADICAL_INERTIA_2_0", "taub": "FIVE_COVECTOR_MAP_CERTIFIED", "second_order": "FINITE_HARMONIC_CRITERION_CERTIFIED", "third_order": "NO_CERTIFIED_MAP"},
    ]
    return {
        "schema": "pure-weyl-bridge-phase1-einstein-extra-contribution-v1",
        "result_id": "BRIDGE_PHASE1_EINSTEIN_EXTRA_CONTRIBUTION_V1",
        "result_state": "PHASE1_EINSTEIN_EXTRA_STRUCTURAL_CONTRIBUTION_FROZEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": imports, "rows": rows, "branch_traces": traces,
        "adversarial_mutations": {
            "missing_polar_branch": "REJECTED_PARITY_COMPLETE_LINEAR_AND_DIRECT_POLAR_CURRENT_REQUIRED",
            "charge_fibre_conflation": "REJECTED_TOTAL_ZERO_DOES_NOT_IMPLY_SEPARATELY_NEUTRAL_PROJECTIONS",
            "smooth_implies_bounded": "REJECTED_SECULAR_EXPONENTIAL_POLYNOMIAL_PREIMAGE_IS_NOT_BOUNDED",
            "bounded_shell_is_intrinsic": "REJECTED_SHELL_RESULT_IS_SCOPED_TO_CERTIFIED_SECOND_ORDER_REPRESENTATIVE",
            "einstein_inclusion_is_symplectic_equivalence": "REJECTED_SOURCE_AND_TARGET_IMAGE_INERTIAS_DIFFER",
        },
        "terminal_summary": {
            "parity_complete_preresidual_linear_carrier": True,
            "parity_complete_direct_generic_pairing": True,
            "einstein_inclusion_symplectic_equivalence": False,
            "separate_neutral_branch_projection": False,
            "five_covector_second_order_theorem": True,
            "balanced_global_K3_class_zero": True,
            "balanced_bounded_third_order_for_certified_representative": False,
            "balanced_smooth_secular_third_order": True,
            "causal_retarded_third_order": "NO_CERTIFIED_MAP",
        },
        "claim_boundary": {
            "establishes": ["the exact publication-independent Bridge Phase-1 Einstein/extra structural chain", "the correction-class and representative dependence of the certified second- and third-order statements"],
            "does_not_establish": ["a final residual symplectic equivalence", "a complete bounded common zero locus", "a branchwide third-order theorem", "causal propagation", "particles, positivity, stability, scattering, unitarity or quantum theory"],
        },
    }


def build_audit(manifest: dict) -> dict:
    papers = {
        "10": ROOT / "paper/10-compact-einstein-maxwell-weyl-phase-space-claim-map.json",
        "13": ROOT / "paper/13-compact-weyl-maxwell-second-order-tangent-cone-claim-map.json",
        "91": ROOT / "paper/91-charge-fibre-taub-bridge-claim-map.json",
        "92": ROOT / "paper/92-extra-axial-lee-wald-bridge.md",
    }
    p10 = json.loads(papers["10"].read_text())
    p13 = json.loads(papers["13"].read_text())
    p91 = json.loads(papers["91"].read_text())
    p92 = papers["92"].read_text()
    records = [
        {"paper": "10", "source_sha256": sha(papers["10"]), "status": "SCOPED_CORRECTION_REQUIRED", "finding": "Claim map still marks polar_extra_branch_classified=false although the direct polar Lee-Wald completion is certified.", "requested_change": "A separate Paper 10 owner should import the polar certificate and update only parity/completeness boundaries; do not broaden to final residual, causal or particle claims.", "check": p10["explicit_nonclaims"]["polar_extra_branch_classified"] is False},
        {"paper": "13", "source_sha256": sha(papers["13"]), "status": "ALIGNED_THEOREM_FROZEN", "finding": "The claim map separates global K3=0 from representative-scoped bounded-shell obstruction and keeps the full bounded quotient open.", "requested_change": "NONE", "check": p13["certified_scope"]["balanced_third_order_bounded_shells_for_certified_v"] == "OBSTRUCTED_ON_ALL_FOUR_OCCUPIED_ORIGINAL_SHELLS"},
        {"paper": "91", "source_sha256": sha(papers["91"]), "status": "ALIGNED_SCOPED_SECOND_ORDER", "finding": "The pure-extra obstruction and balanced mixed Einstein-extra extension are kept on their declared fixed-bundle carrier.", "requested_change": "NONE", "check": p91["certified_claims"]["generic_polar_extra_current_positive_and_Einstein_orthogonal"] is True},
        {"paper": "92", "source_sha256": sha(papers["92"]), "status": "ALIGNED_LINEAR_CROSSWALK", "finding": "The crosswalk records both parities, inertia (3,1), the symplectic non-equivalence and nonlinear charge-fibre boundary.", "requested_change": "NONE", "check": "no parity-complete admissible cyclic direct sum" in p92 and "polar inertia is $(2,0)$" in p92},
    ]
    assert all(r["check"] for r in records)
    for r in records: r.pop("check")
    return {
        "schema": "pure-weyl-paper-materiality-record-v1",
        "result_id": "BRIDGE_PHASE1_EINSTEIN_EXTRA_PAPER_MATERIALITY_2026_07_22",
        "source_result_id": manifest["result_id"], "source_sha256": hashlib.sha256((json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()).hexdigest(),
        "records": records,
        "claim_boundary": "This reverse audit requests a separate scoped Paper 10 correction; it does not edit or promote Papers 10, 13, 91 or 92.",
    }


def main() -> int:
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit", action="store_true"); g.add_argument("--check", action="store_true"); args = ap.parse_args()
    manifest = build_manifest(); audit = build_audit(manifest)
    outputs = {OUT: manifest, AUDIT: audit}
    if args.emit:
        for path, obj in outputs.items(): path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
        return 0
    for path, obj in outputs.items():
        expected = json.dumps(obj, indent=2, sort_keys=True) + "\n"
        if not path.exists() or path.read_text() != expected: raise SystemExit(f"FAIL: stale {path.relative_to(ROOT)}")
    print("PASS: Bridge Phase-1 Einstein/extra manifest and reverse materiality audit are current")
    return 0


if __name__ == "__main__": raise SystemExit(main())
