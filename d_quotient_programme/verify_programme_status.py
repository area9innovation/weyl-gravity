#!/usr/bin/env python3
"""Generate and verify the cross-programme D-quotient status dossier."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "d_quotient_programme"
CERTIFICATE = PACKAGE / "certificates" / "D_QUOTIENT_PROGRAMME_STATUS.json"
REPORT = PACKAGE / "reports" / "consolidated-status.md"
GENERATOR_REGISTRY = PACKAGE / "registry" / "generators.json"
PHASE_REGISTRY = PACKAGE / "registry" / "phase_spaces.json"
CLASSICAL_SCALAR_CLOCK_CONTRIBUTION = PACKAGE / "contributions" / "classical-scalar-clock-vertical-slice.json"
CLASSICAL_NEUTRAL_CLOCK_CONTRIBUTION = PACKAGE / "contributions" / "classical-neutral-conformal-clock-pair.json"
CLASSICAL_NEUTRAL_CLOCK_HEALTH_CONTRIBUTION = PACKAGE / "contributions" / "classical-neutral-clock-bv-health.json"
CLASSICAL_HOMOGENEOUS_STEALTH_CONTRIBUTION = PACKAGE / "contributions" / "classical-homogeneous-positive-stealth-clock.json"
CLASSICAL_STANDARD_STEALTH_NO_GO_CONTRIBUTION = PACKAGE / "contributions" / "classical-standard-conformal-stealth-clock-no-go.json"
CLASSICAL_POSITIVE_BERGER_CLOCK_CONTRIBUTION = PACKAGE / "contributions" / "classical-positive-berger-clock-background.json"
CLASSICAL_BERGER_CLOCK_CHARGE_SEED_CONTRIBUTION = PACKAGE / "contributions" / "classical-berger-clock-charge-seed.json"
CLASSICAL_BERGER_FIXED_COUPLING_DELTA_CHARGE_CONTRIBUTION = PACKAGE / "contributions" / "classical-berger-fixed-coupling-delta-charge.json"
CLASSICAL_BERGER_MINIMAL_BV_CLOCK_SDR_CONTRIBUTION = PACKAGE / "contributions" / "classical-berger-minimal-bv-clock-sdr.json"
CLASSICAL_BERGER_RETAINED_MINIMAL_LAYOUT_CONTRIBUTION = PACKAGE / "contributions" / "classical-berger-retained-minimal-layout.json"
CLASSICAL_BERGER_GENERATOR_CONJUGATION_CONTRIBUTION = PACKAGE / "contributions" / "classical-berger-generator-conjugation.json"
CLASSICAL_BERGER_K_CARTAN_CONTRIBUTION = PACKAGE / "contributions" / "classical-berger-k-cartan-through-arity-three.json"
CLASSICAL_RELATIVE_FUNCTOR_PREFLIGHT_CONTRIBUTION = PACKAGE / "contributions" / "classical-relative-residual-observable-functor-preflight.json"
NONLINEAR_ND1_CONTRIBUTION = PACKAGE / "contributions" / "nonlinear-nd1-selected-residual-d-derivation.json"
NONLINEAR_BERGER_RETAINED_Q2_CONTRIBUTION = (
    PACKAGE
    / "contributions"
    / "nonlinear-berger-retained-q2-and-unary-no-go.json"
)
EINSTEIN_ED1A_CONTRIBUTION = PACKAGE / "contributions" / "einstein-ed1a-asymptotic-generator-gate.json"
EINSTEIN_BERGER_INCIDENCE_CONTRIBUTION = PACKAGE / "contributions" / "einstein-berger-incidence.json"
EINSTEIN_MAXWELL_PRODUCT_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-product-incidence.json"
EINSTEIN_MAXWELL_TANGENT_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-product-tangent-preflight.json"
EINSTEIN_MAXWELL_CHEVRETON_TANGENT_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-chevreton-tangent.json"
EINSTEIN_MAXWELL_SECOND_ORDER_FIXED_FLUX_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-second-order-fixed-flux.json"
EINSTEIN_MAXWELL_SECOND_ORDER_NULL_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-second-order-null-extension.json"
EINSTEIN_MAXWELL_PERIODIC_PHOTON_SECOND_ORDER_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-periodic-photon-second-order.json"
EINSTEIN_MAXWELL_PERIODIC_GRAVITON_SECOND_ORDER_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-periodic-graviton-second-order.json"
EINSTEIN_MAXWELL_OBSTRUCTION_BILINEAR_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-obstruction-bilinear-g1.json"
EINSTEIN_MAXWELL_COMPACT_DOMAIN_TAUB_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-compact-domain-taub-descent.json"
EINSTEIN_MAXWELL_HARMONIC_ADJOINT_BLOCK_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-harmonic-adjoint-block-preflight.json"
EINSTEIN_MAXWELL_AXIAL_MASTER_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-axial-master-complex.json"
EINSTEIN_MAXWELL_POLAR_MASTER_PREFLIGHT_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-polar-master-preflight.json"
EINSTEIN_MAXWELL_POLAR_MASTER_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-polar-master-complex.json"
EINSTEIN_MAXWELL_POLAR_EXCEPTIONAL_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-polar-exceptional-complex.json"
EINSTEIN_MAXWELL_RADIATIVE_SYMPLECTIC_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-radiative-symplectic-matching.json"
EINSTEIN_MAXWELL_EXCEPTIONAL_GLOBAL_SYMPLECTIC_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-exceptional-global-symplectic.json"
EINSTEIN_MAXWELL_WEYL_SYMPLECTIC_PREFLIGHT_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-symplectic-preflight.json"
EINSTEIN_MAXWELL_WEYL_AXIAL_ELL2_RESTRICTION_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-axial-ell2-restriction.json"
EINSTEIN_MAXWELL_WEYL_AXIAL_ALL_ELL_RESTRICTION_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-axial-all-ell-restriction.json"
EINSTEIN_MAXWELL_WEYL_POLAR_ALL_ELL_RESTRICTION_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-polar-all-ell-restriction.json"
EINSTEIN_MAXWELL_WEYL_RADIATIVE_RESTRICTION_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-radiative-restriction.json"
EINSTEIN_MAXWELL_WEYL_ELL1_PHYSICAL_RESTRICTION_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-ell1-physical-restriction.json"
EINSTEIN_MAXWELL_WEYL_STANDARD_HARMONIC_INCLUSION_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-standard-harmonic-inclusion.json"
EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_PREFLIGHT_CONTRIBUTION = PACKAGE / "contributions" / "einstein-weyl-relative-linear-triangle-preflight.json"
EINSTEIN_MAXWELL_WEYL_EXTRA_BRANCH_PREFLIGHT_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-extra-branch-preflight.json"
EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR_MODULE_PREFLIGHT_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-axial-operator-module-preflight.json"
EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-axial-operator.json"
EINSTEIN_MAXWELL_WEYL_POLAR_OPERATOR_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-polar-operator.json"
EINSTEIN_MAXWELL_WEYL_POLAR_PHYSICAL_COMPLETION_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-polar-physical-completion.json"
EINSTEIN_MAXWELL_WEYL_POLAR_LEE_WALD_COMPLETION_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-polar-lee-wald-completion.json"
EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_NOETHER_LIFT_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-polar-ungauged-noether-lift.json"
EINSTEIN_MAXWELL_WEYL_PLEBANSKI_HACYAN_STABILIZER_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-plebanski-hacyan-stabilizer.json"
EINSTEIN_MAXWELL_WEYL_MOMENT_MAP_TAUB_BRIDGE_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-moment-map-taub-bridge.json"
EINSTEIN_MAXWELL_WEYL_BALANCED_MIXED_SECOND_ORDER_EXTENSION_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-balanced-mixed-second-order-extension.json"
EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_GREEN_PAIRING_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-axial-extra-green-pairing.json"
EINSTEIN_MAXWELL_WEYL_AXIAL_LEE_WALD_COMPLETION_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-axial-lee-wald-completion.json"
EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_DETECTOR_TAUB_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-axial-extra-detector-taub.json"
EINSTEIN_MAXWELL_WEYL_AXIAL_QUADRATIC_CHANNEL_PREFLIGHT_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-axial-quadratic-channel-preflight.json"
EINSTEIN_MAXWELL_WEYL_AXIAL_EE_ELL2_SOURCE_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-axial-ee-ell2-source.json"
EINSTEIN_MAXWELL_WEYL_HERMITIAN_AXIAL_POLAR_ELL2_TAUB_CONTRIBUTION = PACKAGE / "contributions" / "einstein-maxwell-weyl-hermitian-axial-polar-ell2-taub.json"
QUANTUM_CARTAN_CONTRIBUTION = ROOT / "quantum-weyl" / "cartan" / "contributions" / "QUANTUM_CARTAN_BLOCKED.json"
QUANTUM_RELATIVE_CONTRIBUTION = PACKAGE / "contributions" / "quantum-relative-einstein-weyl-readiness.json"
PAPER_IX_CLAIM_TABLE = ROOT / "d_quotient_classical" / "certificates" / "PAPER_09_BERGER_CLAIM_TABLE.json"

TEAM_PATHS = {
    "classical": "d_quotient_classical/certificates/CLASSICAL_D_QUOTIENT_STATUS.json",
    "einstein_boundary": "bridge/certificates/d_quotient_asymptotic_seed.json",
    "nonlinear": "quantum-weyl/transfer/certificates/NONLINEAR_HOMOLOGICAL_TRANSFER_BOOTSTRAP.json",
    "quantum": "quantum-weyl/cartan/certificates/CARTAN_DEFECT_COMPLEX_PRECERTIFICATE.json",
}
PRE_SCALAR_CLASSICAL_STATUS_HASH = (
    "495de6865c8aa7bceb32a55769cd4f912da6d67035e899b8571843ab504457af"
)
PRE_BERGER_DELTA_CLASSICAL_STATUS_HASH = (
    "ca4a6f632aaf6d5cc903fcf1dee9a0c69d1d935b1b174df590ffcc430b59c776"
)
PRE_BERGER_MINIMAL_SDR_CLASSICAL_STATUS_HASH = (
    "12fe623360c36f359f9136db2e544ef4877f6f9e56ddec8fff3b32fd9c1b6350"
)
PRE_BERGER_NONZERO_WEIGHT_CLASSICAL_STATUS_HASH = (
    "64cd7e14f5a92cba1933185afd5bfc5d79a05941f6f160121c966bc1f6a69c44"
)
PRE_BERGER_SUPPORT_LOCAL_Q2_CLASSICAL_STATUS_HASH = (
    "89da9c898736fdcd6d21d68b6e53c523f036911702547baa6341a5bee6bd45c5"
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _last_commit(relative: str) -> str:
    return _git("log", "-1", "--format=%H", "--", relative)


def _committed_bytes(commit: str, relative: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{commit}:./{relative}"], cwd=ROOT
    )


def _team_input(relative: str) -> dict[str, str]:
    commit = _last_commit(relative)
    committed_hash = _sha256_bytes(_committed_bytes(commit, relative))
    return {"path": relative, "commit": commit, "sha256": committed_hash}


def _load_team_input(relative: str) -> dict[str, Any]:
    commit = _last_commit(relative)
    return json.loads(_committed_bytes(commit, relative).decode("utf-8"))


def _assert_team_inputs(data: dict[str, dict[str, Any]]) -> None:
    classical = data["classical"]
    if not (
        classical.get("schema") == "pure-weyl-classical-d-quotient-status-v1"
        and classical.get("claim_state") == "PARTIAL"
    ):
        raise AssertionError("classical D-quotient input drifted")
    compact = classical["settings"][0]
    if not (
        compact["setting_id"] == "vacuum_cylinder"
        and compact["verdict"] == "SECTOR_DEPENDENT"
        and {row["verdict"] for row in compact["sector_results"]}
        == {"D_CHARGED", "D_GAUGE"}
    ):
        raise AssertionError("compact classical sector split drifted")
    scalar_setting = next(
        row
        for row in classical["settings"]
        if row["setting_id"] == "cylinder_scalar_clock"
    )
    if not (
        scalar_setting["assessment_status"] == "OPEN"
        and scalar_setting["verdict"] is None
        and classical["work_packages"]["relational_clock"]["status"]
        == "PARTIAL"
        and classical["work_packages"]["relational_clock"]["evidence_refs"]
        == [
            "scalar_clock_vertical_slice",
            "neutral_conformal_clock_pair",
            "neutral_clock_bv_health_audit",
            "homogeneous_positive_conformal_stealth_clock",
            "inhomogeneous_conformal_stealth_clock_no_go",
            "positive_berger_clock_background",
            "berger_clock_reduced_charge_seed",
            "berger_fixed_coupling_delta_charge",
            "berger_minimal_bv_clock_sdr",
            "berger_retained_minimal_layout",
            "berger_retained_minimal_operator_preflight",
            "berger_retained_minimal_operator",
            "berger_causal_witness_preflight",
            "berger_clock_reattached_principal_witness",
            "berger_minimal_34_portable_contraction",
            "berger_nonminimal_algebraic_completion",
            "berger_gauge_fixed_nonminimal_completion",
            "berger_rational_fixture_q2_d_block",
            "berger_nonzero_d_weight_finite_block_no_go",
            "berger_all_weight_arity_two_d_cartan",
            "berger_54_row_local_d_action",
            "berger_support_local_q2",
            "berger_54_row_causal_homotopy_reduction",
        ]
    ):
        raise AssertionError("classical scalar-clock obstruction scope drifted")
    neutral_setting = next(
        row
        for row in classical["settings"]
        if row["setting_id"] == "cylinder_neutral_clock_pair"
    )
    if not (
        neutral_setting["assessment_status"] == "CERTIFIED"
        and neutral_setting["verdict"] == "D_GAUGE"
        and neutral_setting["claim_scope"] == "REDUCED_MODE"
        and neutral_setting["phase_space"]
        .startswith("compact_neutral_clock_pair_homogeneous")
    ):
        raise AssertionError("classical neutral-clock scope drifted")
    berger_setting = next(
        row
        for row in classical["settings"]
        if row["setting_id"] == "positive_berger_clock"
    )
    if not (
        berger_setting["assessment_status"] == "CERTIFIED"
        and berger_setting["verdict"] == "D_GAUGE"
        and berger_setting["claim_scope"] == "REDUCED_MODE"
        and berger_setting["charge_test"]["status"] == "CERTIFIED"
        and berger_setting["phase_space"].startswith(
            "positive_berger_fixed_coupling_linearized_solutions"
        )
    ):
        raise AssertionError("classical positive Berger fixed-coupling verdict drifted")

    einstein = data["einstein_boundary"]
    if not (
        einstein.get("result_state") == "KINEMATICS_PROVED_PHASE_SPACE_OPEN"
        and einstein.get("verdicts")
        == {
            "asymptotically_flat_D": "PHASE_SPACE_NOT_CLOSED",
            "einstein_sector": "EINSTEIN_OPEN",
        }
    ):
        raise AssertionError("Einstein/boundary generator gate drifted")

    nonlinear = data["nonlinear"]
    if not (
        nonlinear.get("result_state")
        == "CAUSAL_D_CARTAN_ARITY_TWO_HADAMARD_MOLLER_NULL_CONE_AND_AXIAL_WEYL_MAXWELL_IMPORTED_Q3_PAULI_JORDAN_AND_GLOBAL_HADAMARD_OPEN"
        and nonlinear.get("classical_freeze_gate") == "FAIL_CLOSED"
        and nonlinear["programme_stages"][1]["status"]
        == "COMPLETE_54_ROW_UNARY_CONTRACTION_LOCAL_D_AND_SUPPORT_LOCAL_Q2_IMPORTED_REPLAYED_AND_TRANSFERRED_TO_RETAINED_Q2_26_MINIMAL_RESIDUAL_ELL2_PENDING"
    ):
        raise AssertionError("nonlinear transfer gate drifted")

    quantum = data["quantum"]
    if not (
        quantum.get("result_state")
        == "ALGEBRAIC_ENGINE_READY_PHYSICAL_CANDIDATES_INPUT_BLOCKED"
        and quantum["input_gates"]["pure_weyl_QME"] == "NOT_RESTORED"
        and quantum["setting_ledger"][0]["verdict"]
        == "ANALYTIC_FRAMEWORK_MISSING"
    ):
        raise AssertionError("quantum Cartan/QME gate drifted")

    classical_hash = _sha256_bytes(
        _committed_bytes(
            _last_commit(TEAM_PATHS["classical"]), TEAM_PATHS["classical"]
        )
    )
    imported_hash = quantum["provenance"]["dependency_manifest"].get(
        "classical_D_quotient_status"
    )
    if imported_hash not in {
        classical_hash,
        PRE_SCALAR_CLASSICAL_STATUS_HASH,
        PRE_BERGER_DELTA_CLASSICAL_STATUS_HASH,
        PRE_BERGER_MINIMAL_SDR_CLASSICAL_STATUS_HASH,
        PRE_BERGER_NONZERO_WEIGHT_CLASSICAL_STATUS_HASH,
        PRE_BERGER_SUPPORT_LOCAL_Q2_CLASSICAL_STATUS_HASH,
    }:
        raise AssertionError("quantum team classical import is neither current nor a certified historical baseline")
    if imported_hash != classical_hash and quantum["setting_ledger"][0]["verdict"] != "ANALYTIC_FRAMEWORK_MISSING":
        raise AssertionError("quantum result promoted without importing the current scalar-clock status")


def _nonlinear_nd1_contribution() -> dict[str, Any]:
    contribution = _load(NONLINEAR_ND1_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "nonlinear"
        and contribution.get("setting_id") == "compact_selected_residual_HT1_q2"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id") == "compact_selected_residual_HT1"
        and contribution.get("lifecycle_layer") == "INTERACTING"
        and contribution.get("claim_status") == "PARTIAL"
        and contribution.get("verdict")
        == "SELECTED_RESIDUAL_D_DERIVATION_HOLDS_AT_ARITY_TWO"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("nonlinear ND1 contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("nonlinear ND1 contribution evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("nonlinear ND1 contribution evidence hash drifted")
    return contribution


def _nonlinear_berger_retained_q2_contribution() -> dict[str, Any]:
    contribution = _load(NONLINEAR_BERGER_RETAINED_Q2_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "nonlinear"
        and contribution.get("setting_id")
        == "compact_positive_berger_clock_retained_q2_26"
        and contribution.get("generator_id") == "K_Berger"
        and contribution.get("phase_space_id")
        == "positive_berger_fixed_coupling_linearized_solutions"
        and contribution.get("lifecycle_layer") == "INTERACTING"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict")
        == "RETAINED_Q2_26_COMPLETE_BARE_LOCAL_UNARY_K_CARTAN_OBSTRUCTED"
        and contribution.get("dependency_tags") == ["LOCAL-ALGEBRAIC"]
    ):
        raise AssertionError("nonlinear retained-q2 contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path, commit = evidence.get("path"), evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("nonlinear retained-q2 evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("nonlinear retained-q2 evidence hash drifted")
    if not any("54236" in statement for statement in contribution["established"]):
        raise AssertionError("nonlinear retained-q2 exact count dropped")
    return contribution


def _quantum_cartan_contribution() -> dict[str, Any]:
    contribution = _load(QUANTUM_CARTAN_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "quantum"
        and contribution.get("setting_id") == "vacuum_cylinder"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id") == "compact_quantum"
        and contribution.get("lifecycle_layer") == "QUANTUM"
        and contribution.get("claim_status") == "BLOCKED"
        and contribution.get("verdict") is None
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "LORENTZIAN-CAUSAL"]
    ):
        raise AssertionError("quantum Cartan contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("quantum Cartan contribution evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("quantum Cartan contribution evidence hash drifted")
    return contribution


def _quantum_relative_contribution() -> dict[str, Any]:
    contribution = _load(QUANTUM_RELATIVE_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "quantum"
        and contribution.get("setting_id")
        == "compact_einstein_maxwell_weyl_relative_quantum_readiness"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id")
        == "einstein_maxwell_product_compact_weyl_complete_standard_harmonic_tangent"
        and contribution.get("lifecycle_layer") == "QUANTUM"
        and contribution.get("claim_status") == "BLOCKED"
        and contribution.get("verdict") == "ANALYTIC_FRAMEWORK_MISSING"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"]
    ):
        raise AssertionError("relative quantum contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path, commit = evidence.get("path"), evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("relative quantum contribution evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("relative quantum contribution evidence hash drifted")
    return contribution


def _classical_berger_generator_conjugation_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_BERGER_GENERATOR_CONJUGATION_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id") == "compact_positive_berger_clock_generator_conjugation"
        and contribution.get("generator_id") == "K_Berger"
        and contribution.get("phase_space_id") == "positive_berger_fixed_coupling_linearized_solutions"
        and contribution.get("lifecycle_layer") == "CLASSICAL_CARTAN"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict") == "FROZEN_UNARY_GENERATOR_IS_K_RAW_D_AFFINE"
        and contribution.get("dependency_tags") == ["LOCAL-ALGEBRAIC"]
    ):
        raise AssertionError("classical Berger generator correction scope drifted")
    evidence = contribution.get("evidence", {})
    if _sha256_bytes(_committed_bytes(evidence["commit"], evidence["path"])) != evidence.get("sha256"):
        raise AssertionError("classical Berger generator correction evidence hash drifted")
    return contribution


def _classical_berger_k_cartan_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_BERGER_K_CARTAN_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id") == "compact_positive_berger_clock_k_cartan_through_arity_three"
        and contribution.get("generator_id") == "K_Berger"
        and contribution.get("phase_space_id") == "positive_berger_fixed_coupling_linearized_solutions"
        and contribution.get("lifecycle_layer") == "CLASSICAL_CARTAN"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict") == "K_CARTAN_CAUSAL_THROUGH_ARITY_THREE"
        and contribution.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    ):
        raise AssertionError("classical Berger K-Cartan contribution scope drifted")
    evidence = contribution.get("evidence", {})
    if _sha256_bytes(_committed_bytes(evidence["commit"], evidence["path"])) != evidence.get("sha256"):
        raise AssertionError("classical Berger K-Cartan evidence hash drifted")
    return contribution


def _classical_relative_functor_preflight_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_RELATIVE_FUNCTOR_PREFLIGHT_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id") == "compact_einstein_maxwell_weyl_relative_functor_preflight"
        and contribution.get("generator_id") == "H_product"
        and contribution.get("phase_space_id") == "einstein_maxwell_product_compact_weyl_complete_standard_harmonic_tangent"
        and contribution.get("lifecycle_layer") == "CLASSICAL_BV"
        and contribution.get("claim_status") == "BLOCKED"
        and contribution.get("verdict") == "BLOCKED_ON_EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1"
        and contribution.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("classical relative functor preflight scope drifted")
    evidence = contribution.get("evidence", {})
    if _sha256_bytes(_committed_bytes(evidence["commit"], evidence["path"])) != evidence.get("sha256"):
        raise AssertionError("classical relative functor preflight evidence hash drifted")
    return contribution


def _classical_scalar_clock_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_SCALAR_CLOCK_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id") == "compact_scalar_clock"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id") == "compact_scalar_clock"
        and contribution.get("lifecycle_layer") == "CLASSICAL_CHARGE"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict")
        == "SINGLE_SCALAR_CLOCK_BACKGROUND_OBSTRUCTED"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("classical scalar-clock contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("classical scalar-clock evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("classical scalar-clock evidence hash drifted")
    return contribution


def _classical_neutral_clock_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_NEUTRAL_CLOCK_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id") == "compact_neutral_clock_pair"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id")
        == "compact_neutral_clock_pair_homogeneous"
        and contribution.get("lifecycle_layer") == "CLASSICAL_CHARGE"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict") == "D_GAUGE"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("classical neutral-clock contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("classical neutral-clock evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("classical neutral-clock evidence hash drifted")
    return contribution


def _classical_neutral_clock_health_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_NEUTRAL_CLOCK_HEALTH_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id")
        == "compact_neutral_clock_pair_local_health"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id")
        == "compact_neutral_clock_pair_local_extension"
        and contribution.get("lifecycle_layer") == "CLASSICAL_CHARGE"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict")
        == "OPPOSITE_SIGN_LOCAL_HEALTH_OBSTRUCTED"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("classical neutral-clock health contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("classical neutral-clock health evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("classical neutral-clock health evidence hash drifted")
    return contribution


def _classical_homogeneous_stealth_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_HOMOGENEOUS_STEALTH_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id")
        == "compact_homogeneous_positive_stealth_clock"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id")
        == "compact_homogeneous_positive_stealth_scalar"
        and contribution.get("lifecycle_layer") == "CLASSICAL_CHARGE"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict")
        == "HOMOGENEOUS_STEALTH_CLOCK_OBSTRUCTED"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("classical homogeneous stealth contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("classical homogeneous stealth evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("classical homogeneous stealth evidence hash drifted")
    return contribution


def _classical_standard_stealth_no_go_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_STANDARD_STEALTH_NO_GO_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id")
        == "compact_standard_conformal_stealth_clock"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id")
        == "standard_conformal_scalar_stealth_clock_sector"
        and contribution.get("lifecycle_layer") == "CLASSICAL_CHARGE"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict")
        == "STANDARD_ONE_FIELD_STEALTH_CLOCK_NO_GO"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("classical standard stealth no-go contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("classical standard stealth no-go evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("classical standard stealth no-go evidence hash drifted")
    return contribution


def _classical_positive_berger_clock_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_POSITIVE_BERGER_CLOCK_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id") == "compact_positive_berger_clock"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id")
        == "positive_rotating_scalar_berger_background"
        and contribution.get("lifecycle_layer") == "CLASSICAL_CHARGE"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict")
        == "POSITIVE_BERGER_CLOCK_BACKGROUND_EXISTS"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("classical positive Berger-clock contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("classical positive Berger-clock evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("classical positive Berger-clock evidence hash drifted")
    return contribution


def _classical_berger_clock_charge_seed_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_BERGER_CLOCK_CHARGE_SEED_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id")
        == "compact_positive_berger_clock_reduced_charge"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id")
        == "positive_rotating_scalar_berger_background"
        and contribution.get("lifecycle_layer") == "CLASSICAL_CHARGE"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict")
        == "NONZERO_INTERNAL_CLOCK_MOMENTUM_TOTAL_D_OPEN"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("classical Berger charge-seed contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("classical Berger charge-seed evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("classical Berger charge-seed evidence hash drifted")
    return contribution


def _classical_berger_fixed_coupling_delta_charge_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_BERGER_FIXED_COUPLING_DELTA_CHARGE_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id")
        == "compact_positive_berger_clock_fixed_coupling_linearized"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id")
        == "positive_berger_fixed_coupling_linearized_solutions"
        and contribution.get("lifecycle_layer") == "CLASSICAL_CHARGE"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict") == "D_GAUGE"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("classical Berger fixed-coupling verdict scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("classical Berger fixed-coupling evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("classical Berger fixed-coupling evidence hash drifted")
    return contribution


def _classical_berger_minimal_bv_clock_sdr_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_BERGER_MINIMAL_BV_CLOCK_SDR_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id")
        == "compact_positive_berger_clock_minimal_bv_sdr"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id")
        == "positive_berger_fixed_coupling_linearized_solutions"
        and contribution.get("lifecycle_layer") == "CLASSICAL_BV"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict") == "MINIMAL_CLOCK_SECTOR_SDR"
        and contribution.get("dependency_tags") == ["LOCAL-ALGEBRAIC"]
    ):
        raise AssertionError("classical Berger minimal BV SDR scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("classical Berger minimal BV SDR evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("classical Berger minimal BV SDR evidence hash drifted")
    return contribution


def _classical_berger_retained_minimal_layout_contribution() -> dict[str, Any]:
    contribution = _load(CLASSICAL_BERGER_RETAINED_MINIMAL_LAYOUT_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "classical"
        and contribution.get("setting_id")
        == "compact_positive_berger_clock_retained_minimal_layout"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id")
        == "positive_berger_fixed_coupling_linearized_solutions"
        and contribution.get("lifecycle_layer") == "CLASSICAL_BV"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict") == "RETAINED_MINIMAL_LAYOUT_FROZEN"
        and contribution.get("dependency_tags") == ["LOCAL-ALGEBRAIC"]
    ):
        raise AssertionError("classical Berger retained layout scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("classical Berger retained layout evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("classical Berger retained layout evidence hash drifted")
    return contribution


def _einstein_ed1a_contribution() -> dict[str, Any]:
    contribution = _load(EINSTEIN_ED1A_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "einstein_boundary"
        and contribution.get("setting_id") == "asymptotic_real_cylinder_time"
        and contribution.get("generator_id") == "H_ESU"
        and contribution.get("phase_space_id") == "asymptotically_flat_full_Bach"
        and contribution.get("lifecycle_layer") == "LORENTZIAN_CAUSAL"
        and contribution.get("claim_status") == "PARTIAL"
        and contribution.get("verdict") == "PHASE_SPACE_NOT_CLOSED"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("Einstein E-D1a contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("Einstein E-D1a contribution evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("Einstein E-D1a contribution evidence hash drifted")
    return contribution


def _einstein_berger_incidence_contribution() -> dict[str, Any]:
    contribution = _load(EINSTEIN_BERGER_INCIDENCE_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "einstein_boundary"
        and contribution.get("setting_id")
        == "compact_positive_berger_clock_einstein_incidence"
        and contribution.get("generator_id") == "D_compact"
        and contribution.get("phase_space_id")
        == "positive_berger_fixed_coupling_linearized_solutions"
        and contribution.get("lifecycle_layer") == "CLASSICAL_BV"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict")
        == "EINSTEIN_TANGENT_NOT_APPLICABLE_AT_THIS_BACKGROUND"
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError("Einstein Berger-incidence contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("Einstein Berger-incidence evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("Einstein Berger-incidence evidence hash drifted")
    return contribution


def _einstein_maxwell_product_contribution() -> dict[str, Any]:
    contribution = _load(EINSTEIN_MAXWELL_PRODUCT_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "einstein_boundary"
        and contribution.get("setting_id")
        == "compact_einstein_maxwell_product_background"
        and contribution.get("generator_id") == "H_product"
        and contribution.get("phase_space_id")
        == "einstein_maxwell_product_background"
        and contribution.get("lifecycle_layer") == "CLASSICAL_BV"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict")
        == "COMMON_EINSTEIN_MAXWELL_WEYL_MAXWELL_BACKGROUND"
        and contribution.get("dependency_tags") == ["LOCAL-ALGEBRAIC"]
    ):
        raise AssertionError("Einstein--Maxwell product contribution scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("Einstein--Maxwell product evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("Einstein--Maxwell product evidence hash drifted")
    return contribution


def _einstein_maxwell_tangent_contribution() -> dict[str, Any]:
    contribution = _load(EINSTEIN_MAXWELL_TANGENT_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "einstein_boundary"
        and contribution.get("setting_id")
        == "compact_einstein_maxwell_product_tangent_preflight"
        and contribution.get("generator_id") == "H_product"
        and contribution.get("phase_space_id")
        == "einstein_maxwell_product_principal_tangent_complex"
        and contribution.get("lifecycle_layer") == "CLASSICAL_BV"
        and contribution.get("claim_status") == "PARTIAL"
        and contribution.get("verdict")
        == "PRINCIPAL_TANGENT_CHAIN_MAP_WITH_EXTRA_WEYL_CLASSES"
        and contribution.get("dependency_tags") == ["LOCAL-ALGEBRAIC"]
    ):
        raise AssertionError("Einstein--Maxwell tangent-preflight scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("Einstein--Maxwell tangent-preflight evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("Einstein--Maxwell tangent-preflight evidence hash drifted")
    return contribution


def _einstein_maxwell_chevreton_tangent_contribution() -> dict[str, Any]:
    contribution = _load(EINSTEIN_MAXWELL_CHEVRETON_TANGENT_CONTRIBUTION)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "einstein_boundary"
        and contribution.get("setting_id")
        == "compact_einstein_maxwell_product_on_shell_tangent"
        and contribution.get("generator_id") == "H_product"
        and contribution.get("phase_space_id")
        == "einstein_maxwell_product_on_shell_linear_tangents"
        and contribution.get("lifecycle_layer") == "CLASSICAL_BV"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict")
        == "FULL_ON_SHELL_LINEAR_TANGENT_INCLUSION_CHEVRETON"
        and contribution.get("dependency_tags") == ["LOCAL-ALGEBRAIC"]
    ):
        raise AssertionError("Einstein--Maxwell Chevreton tangent scope drifted")
    evidence = contribution.get("evidence", {})
    path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(path, str) or not isinstance(commit, str):
        raise AssertionError("Einstein--Maxwell Chevreton tangent evidence is incomplete")
    if _sha256_bytes(_committed_bytes(commit, path)) != evidence.get("sha256"):
        raise AssertionError("Einstein--Maxwell Chevreton tangent evidence hash drifted")
    return contribution


def _einstein_maxwell_second_order_contribution(
    path: Path, setting_id: str, phase_space_id: str, verdict: str
) -> dict[str, Any]:
    contribution = _load(path)
    if not (
        contribution.get("schema") == "pure-weyl-d-quotient-team-contribution-v1"
        and contribution.get("team_id") == "einstein_boundary"
        and contribution.get("setting_id") == setting_id
        and contribution.get("generator_id") == "H_product"
        and contribution.get("phase_space_id") == phase_space_id
        and contribution.get("lifecycle_layer") == "CLASSICAL_BV"
        and contribution.get("claim_status") == "CERTIFIED"
        and contribution.get("verdict") == verdict
        and contribution.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        raise AssertionError(f"Einstein--Maxwell second-order scope drifted: {setting_id}")
    evidence = contribution.get("evidence", {})
    evidence_path = evidence.get("path")
    commit = evidence.get("commit")
    if not isinstance(evidence_path, str) or not isinstance(commit, str):
        raise AssertionError(f"Einstein--Maxwell second-order evidence incomplete: {setting_id}")
    if _sha256_bytes(_committed_bytes(commit, evidence_path)) != evidence.get("sha256"):
        raise AssertionError(f"Einstein--Maxwell second-order evidence hash drifted: {setting_id}")
    return contribution


def build_certificate(base_commit: str | None = None) -> dict[str, Any]:
    team_data = {team: _load_team_input(path) for team, path in TEAM_PATHS.items()}
    _assert_team_inputs(team_data)
    inputs = {team: _team_input(path) for team, path in TEAM_PATHS.items()}
    scalar_clock_contribution = _classical_scalar_clock_contribution()
    neutral_clock_contribution = _classical_neutral_clock_contribution()
    neutral_clock_health_contribution = _classical_neutral_clock_health_contribution()
    homogeneous_stealth_contribution = _classical_homogeneous_stealth_contribution()
    standard_stealth_no_go_contribution = _classical_standard_stealth_no_go_contribution()
    positive_berger_clock_contribution = _classical_positive_berger_clock_contribution()
    berger_clock_charge_seed_contribution = _classical_berger_clock_charge_seed_contribution()
    berger_fixed_coupling_delta_charge_contribution = (
        _classical_berger_fixed_coupling_delta_charge_contribution()
    )
    berger_minimal_bv_clock_sdr_contribution = (
        _classical_berger_minimal_bv_clock_sdr_contribution()
    )
    berger_retained_minimal_layout_contribution = (
        _classical_berger_retained_minimal_layout_contribution()
    )
    berger_generator_conjugation_contribution = (
        _classical_berger_generator_conjugation_contribution()
    )
    berger_k_cartan_contribution = _classical_berger_k_cartan_contribution()
    relative_functor_preflight_contribution = (
        _classical_relative_functor_preflight_contribution()
    )
    ed1a_contribution = _einstein_ed1a_contribution()
    berger_incidence_contribution = _einstein_berger_incidence_contribution()
    maxwell_product_contribution = _einstein_maxwell_product_contribution()
    maxwell_tangent_contribution = _einstein_maxwell_tangent_contribution()
    maxwell_chevreton_tangent_contribution = (
        _einstein_maxwell_chevreton_tangent_contribution()
    )
    maxwell_second_order_fixed_flux_contribution = (
        _einstein_maxwell_second_order_contribution(
            EINSTEIN_MAXWELL_SECOND_ORDER_FIXED_FLUX_CONTRIBUTION,
            "compact_einstein_maxwell_second_order_fixed_flux",
            "einstein_maxwell_product_compact_fixed_flux_second_order",
            "SECOND_ORDER_FIXED_FLUX_OBSTRUCTION_FOR_RADION_AND_DUALITY",
        )
    )
    maxwell_second_order_null_contribution = (
        _einstein_maxwell_second_order_contribution(
            EINSTEIN_MAXWELL_SECOND_ORDER_NULL_CONTRIBUTION,
            "universal_cover_einstein_maxwell_second_order_null_extension",
            "einstein_maxwell_product_universal_cover_null_second_order",
            "NONZERO_CHEVRETON_NULL_TANGENT_EXTENDS_AT_SECOND_ORDER",
        )
    )
    maxwell_periodic_photon_contribution = (
        _einstein_maxwell_second_order_contribution(
            EINSTEIN_MAXWELL_PERIODIC_PHOTON_SECOND_ORDER_CONTRIBUTION,
            "compact_einstein_maxwell_periodic_photon_second_order",
            "einstein_maxwell_product_compact_fixed_charge_periodic_photon_second_order",
            "PERIODIC_PHOTON_SECOND_ORDER_FIXED_CHARGE_OBSTRUCTION",
        )
    )
    maxwell_periodic_graviton_contribution = (
        _einstein_maxwell_second_order_contribution(
            EINSTEIN_MAXWELL_PERIODIC_GRAVITON_SECOND_ORDER_CONTRIBUTION,
            "compact_einstein_maxwell_periodic_graviton_second_order",
            "einstein_maxwell_product_compact_fixed_charge_periodic_graviton_second_order",
            "PERIODIC_L2_GRAVITATIONAL_MODE_FIXED_CHARGE_OBSTRUCTION",
        )
    )
    maxwell_obstruction_bilinear_contribution = (
        _einstein_maxwell_second_order_contribution(
            EINSTEIN_MAXWELL_OBSTRUCTION_BILINEAR_CONTRIBUTION,
            "compact_einstein_maxwell_obstruction_bilinear_g1",
            "einstein_maxwell_product_compact_fixture_span_obstruction_bilinear",
            "G1_CONSTANT_LAPSE_OBSTRUCTION_BILINEAR_ON_FIXTURE_SPAN",
        )
    )
    maxwell_compact_domain_taub_contribution = (
        _einstein_maxwell_second_order_contribution(
            EINSTEIN_MAXWELL_COMPACT_DOMAIN_TAUB_CONTRIBUTION,
            "compact_einstein_maxwell_domain_taub_descent",
            "einstein_maxwell_product_compact_fixed_u1_harmonic_taub",
            "G1_FIXED_U1_DOMAIN_AND_RELATIVE_TAUB_DESCENT",
        )
    )
    maxwell_harmonic_adjoint_block_contribution = (
        _einstein_maxwell_second_order_contribution(
            EINSTEIN_MAXWELL_HARMONIC_ADJOINT_BLOCK_CONTRIBUTION,
            "compact_einstein_maxwell_harmonic_adjoint_block_preflight",
            "einstein_maxwell_product_compact_harmonic_block_preflight",
            "G1_AXIAL_N0_TOWER_AND_ADJOINT_PREFLIGHT",
        )
    )
    maxwell_axial_master_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_AXIAL_MASTER_CONTRIBUTION,
        "compact_einstein_maxwell_axial_master_complex",
        "einstein_maxwell_product_compact_axial_master_complex",
        "G1_AXIAL_ALL_MOMENTA_MASTER_COMPLEX",
    )
    maxwell_polar_master_preflight_contribution = (
        _einstein_maxwell_second_order_contribution(
            EINSTEIN_MAXWELL_POLAR_MASTER_PREFLIGHT_CONTRIBUTION,
            "compact_einstein_maxwell_polar_master_preflight",
            "einstein_maxwell_product_compact_polar_master_preflight",
            "G1_POLAR_ELL_GE2_MATRIX_PREFLIGHT",
        )
    )
    maxwell_polar_master_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_POLAR_MASTER_CONTRIBUTION,
        "compact_einstein_maxwell_polar_master_complex",
        "einstein_maxwell_product_compact_polar_master_complex",
        "G2_POLAR_ELL_GE2_ARBITRARY_LAMBDA_TENSOR_IDENTITY",
    )
    maxwell_polar_exceptional_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_POLAR_EXCEPTIONAL_CONTRIBUTION,
        "compact_einstein_maxwell_polar_exceptional_complex",
        "einstein_maxwell_product_compact_polar_exceptional_complex",
        "G2_POLAR_ALL_ELL_LINEAR_COMPLEX",
    )
    maxwell_radiative_symplectic_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_RADIATIVE_SYMPLECTIC_CONTRIBUTION,
        "compact_einstein_maxwell_radiative_symplectic_matching",
        "einstein_maxwell_product_compact_radiative_symplectic",
        "G2_RADIATIVE_COVARIANT_SYMPLECTIC_MATCHING",
    )
    maxwell_exceptional_global_symplectic_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_EXCEPTIONAL_GLOBAL_SYMPLECTIC_CONTRIBUTION,
        "compact_einstein_maxwell_exceptional_global_symplectic",
        "einstein_maxwell_product_compact_exceptional_global_symplectic",
        "G2_EXCEPTIONAL_GLOBAL_SYMPLECTIC_COMPLETION",
    )
    maxwell_weyl_symplectic_preflight_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_SYMPLECTIC_PREFLIGHT_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_symplectic_preflight",
        "einstein_maxwell_product_compact_weyl_symplectic_preflight",
        "G2_WEYL_SYMPLECTIC_PREFLIGHT_QUOTIENT_INJECTIVE",
    )
    maxwell_weyl_axial_ell2_restriction_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_AXIAL_ELL2_RESTRICTION_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_axial_ell2_restriction",
        "einstein_maxwell_product_compact_weyl_axial_ell2_restriction",
        "G1_AXIAL_ELL2_BRANCH_DEPENDENT_INDEFINITE_RESTRICTION",
    )
    maxwell_weyl_axial_all_ell_restriction_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_AXIAL_ALL_ELL_RESTRICTION_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_axial_all_ell_restriction",
        "einstein_maxwell_product_compact_weyl_axial_all_ell_restriction",
        "G1_AXIAL_ALL_ELL_GE2_BRANCH_DEPENDENT_INDEFINITE_RESTRICTION",
    )
    maxwell_weyl_polar_all_ell_restriction_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_POLAR_ALL_ELL_RESTRICTION_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_polar_all_ell_restriction",
        "einstein_maxwell_product_compact_weyl_polar_all_ell_restriction",
        "G2_POLAR_ALL_ELL_GE2_BRANCH_DEPENDENT_INDEFINITE_RESTRICTION",
    )
    maxwell_weyl_radiative_restriction_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_RADIATIVE_RESTRICTION_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_radiative_restriction",
        "einstein_maxwell_product_compact_weyl_standard_radiative_restriction",
        "G3_STANDARD_RADIATIVE_ALL_ELL_GE2_COMMON_SPECTRAL_NONDEGENERATE_INDEFINITE_RESTRICTION",
    )
    maxwell_weyl_ell1_physical_restriction_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_ELL1_PHYSICAL_RESTRICTION_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_ell1_physical_restriction",
        "einstein_maxwell_product_compact_weyl_ell1_physical_quotient",
        "G3_PHYSICAL_ELL1_ALL_N_M_FACTOR_FOUR_QUOTIENT_RESTRICTION",
    )
    maxwell_weyl_standard_harmonic_inclusion_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_STANDARD_HARMONIC_INCLUSION_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_standard_harmonic_inclusion",
        "einstein_maxwell_product_compact_weyl_complete_standard_harmonic_tangent",
        "G4_COMPLETE_STANDARD_HARMONIC_PULLBACK_NONDEGENERATE_BEFORE_FINAL_QUOTIENT",
    )
    relative_linear_triangle_preflight_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_PREFLIGHT_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_relative_linear_triangle_preflight",
        "einstein_maxwell_product_compact_weyl_principal_and_generic_axial_relative_triangle_preflight",
        "G2_PRINCIPAL_AND_GENERIC_AXIAL_OFFSHELL_RELATIVE_TRIANGLE_PREFLIGHT",
    )
    maxwell_weyl_extra_branch_preflight_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_EXTRA_BRANCH_PREFLIGHT_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_extra_branch_preflight",
        "einstein_maxwell_product_compact_weyl_extra_branch_preflight",
        "G2_CANONICAL_EXTRA_QUOTIENT_AND_FULL_BLOCK_SOLVE_CONTRACT",
    )
    maxwell_weyl_axial_operator_module_preflight_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR_MODULE_PREFLIGHT_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_axial_operator_module_preflight",
        "einstein_maxwell_product_compact_weyl_axial_operator_module_preflight",
        "G2_EXACT_AXIAL_GAUGE_MODULE_AND_OPERATOR_RAILS",
    )
    maxwell_weyl_axial_operator_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_axial_operator",
        "einstein_maxwell_product_compact_weyl_generic_axial_target_solution_module",
        "G2_GENERIC_AXIAL_TARGET_OPERATOR_AND_EXTRA_SOLUTION_MODULE",
    )
    maxwell_weyl_polar_operator_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_POLAR_OPERATOR_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_polar_operator",
        "einstein_maxwell_product_compact_weyl_generic_polar_target_solution_module",
        "G2_GENERIC_POLAR_TARGET_OPERATOR_AND_OFFSHELL_EINSTEIN_SQUARE",
    )
    maxwell_weyl_polar_physical_completion_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_POLAR_PHYSICAL_COMPLETION_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_polar_physical_completion",
        "einstein_maxwell_product_compact_weyl_physical_polar_target_solution_module",
        "G2_PHYSICAL_POLAR_EXTRA_QUOTIENT_AND_EINSTEIN_PRIMARY_IMAGE",
    )
    maxwell_weyl_polar_lee_wald_completion_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_POLAR_LEE_WALD_COMPLETION_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_polar_lee_wald_completion",
        "einstein_maxwell_product_compact_weyl_generic_polar_direct_lee_wald_block",
        "G2_GENERIC_POLAR_DIRECT_LEE_WALD_BLOCK_INERTIA_THREE_ONE",
    )
    maxwell_weyl_polar_ungauged_noether_lift_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_NOETHER_LIFT_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_polar_ungauged_noether_lift",
        "einstein_maxwell_product_compact_weyl_generic_polar_ungauged_noether_complex",
        "G2_GENERIC_POLAR_UNGAUGED_EQUATION_NOETHER_CHAIN_MAP",
    )
    maxwell_weyl_plebanski_hacyan_stabilizer_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_PLEBANSKI_HACYAN_STABILIZER_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_plebanski_hacyan_stabilizer_descent",
        "einstein_maxwell_product_compact_weyl_generic_stabilizer_representation",
        "G2_PH_STABILIZER_PRIMARY_EQUIVARIANT_ABSOLUTE_QUOTIENT_NOT_AUTHORIZED",
    )
    maxwell_weyl_moment_map_taub_bridge_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_MOMENT_MAP_TAUB_BRIDGE_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_moment_map_taub_bridge",
        "einstein_maxwell_product_compact_weyl_generic_fixed_bundle_moment_map_taub",
        "G2_GENERIC_PURE_EXTRA_FIXED_BUNDLE_TAUB_NO_GO",
    )
    maxwell_weyl_balanced_mixed_second_order_extension_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_BALANCED_MIXED_SECOND_ORDER_EXTENSION_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_balanced_mixed_second_order_extension",
        "einstein_maxwell_product_compact_weyl_ell2_k0_balanced_mixed_second_order_jet",
        "G1_BALANCED_MIXED_TANGENT_COMPLETE_SECOND_ORDER_EXTENSION",
    )
    maxwell_weyl_axial_extra_green_pairing_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_GREEN_PAIRING_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_axial_extra_green_pairing",
        "einstein_maxwell_product_compact_weyl_generic_axial_extra_reduced_green_pairing",
        "G2_GENERIC_AXIAL_EXTRA_NONRADICAL_REDUCED_GREEN_SIGNATURE_POSITIVE_TWO",
    )
    maxwell_weyl_axial_lee_wald_completion_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_AXIAL_LEE_WALD_COMPLETION_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_axial_lee_wald_completion",
        "einstein_maxwell_product_compact_weyl_generic_axial_direct_lee_wald_block",
        "G2_GENERIC_AXIAL_DIRECT_LEE_WALD_BLOCK_SIGNATURE_THREE_ONE",
    )
    maxwell_weyl_axial_extra_detector_taub_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_DETECTOR_TAUB_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_axial_extra_detector_taub",
        "einstein_maxwell_product_compact_weyl_axial_extra_ell2_k0_fixed_charge_taub",
        "G2_AXIAL_EXTRA_DETECTOR_AND_ELL2_K0_NEGATIVE_DEFINITE_TAUB_OBSTRUCTION",
    )
    maxwell_weyl_axial_quadratic_channel_preflight_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_AXIAL_QUADRATIC_CHANNEL_PREFLIGHT_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_axial_quadratic_channel_preflight",
        "einstein_maxwell_product_compact_weyl_axial_ee_finite_window_and_ell2_removable_block",
        "G2_AXIAL_EE_FINITE_RESONANCE_WINDOW_AND_FIRST_REMOVABLE_BLOCK",
    )
    maxwell_weyl_axial_ee_ell2_source_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_AXIAL_EE_ELL2_SOURCE_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_axial_ee_ell2_source",
        "einstein_maxwell_product_compact_weyl_axial_ee_ell2_sum_frequency_block",
        "G1_MIXED_EE_AXIAL_ELL2_SUM_FREQUENCY_BLOCK_EXPLICITLY_REMOVABLE",
    )
    maxwell_weyl_hermitian_axial_polar_ell2_taub_contribution = _einstein_maxwell_second_order_contribution(
        EINSTEIN_MAXWELL_WEYL_HERMITIAN_AXIAL_POLAR_ELL2_TAUB_CONTRIBUTION,
        "compact_einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub",
        "einstein_maxwell_product_compact_fixed_bundle_hermitian_axial_polar_ell2_minus_pair",
        "G1_HERMITIAN_AXIAL_POLAR_ELL2_MINUS_PAIR_POSITIVE_TAUB_FIXED_BUNDLE_NO_GO",
    )
    nd1_contribution = _nonlinear_nd1_contribution()
    berger_retained_q2_contribution = _nonlinear_berger_retained_q2_contribution()
    quantum_cartan_contribution = _quantum_cartan_contribution()
    quantum_relative_contribution = _quantum_relative_contribution()
    return {
        "schema": "pure-weyl-d-quotient-programme-status-v1",
        "result_id": "D_QUOTIENT_PROGRAMME_STATUS",
        "programme_base_commit": base_commit or _git("rev-parse", "HEAD"),
        "result_state": "CROSS_PROGRAMME_DOSSIER_ACTIVE_RESULTS_SECTOR_INDEXED",
        "claim_key": [
            "generator_id",
            "phase_space_id",
            "boundary_conditions",
            "lifecycle_layer",
        ],
        "registry_hashes": {
            "generator_registry": _sha256(GENERATOR_REGISTRY),
            "phase_space_registry": _sha256(PHASE_REGISTRY),
        },
        "team_inputs": inputs,
        "team_contributions": [
            {
                "path": str(CLASSICAL_SCALAR_CLOCK_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_SCALAR_CLOCK_CONTRIBUTION),
                "payload": scalar_clock_contribution,
            },
            {
                "path": str(CLASSICAL_NEUTRAL_CLOCK_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_NEUTRAL_CLOCK_CONTRIBUTION),
                "payload": neutral_clock_contribution,
            },
            {
                "path": str(CLASSICAL_NEUTRAL_CLOCK_HEALTH_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_NEUTRAL_CLOCK_HEALTH_CONTRIBUTION),
                "payload": neutral_clock_health_contribution,
            },
            {
                "path": str(CLASSICAL_HOMOGENEOUS_STEALTH_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_HOMOGENEOUS_STEALTH_CONTRIBUTION),
                "payload": homogeneous_stealth_contribution,
            },
            {
                "path": str(CLASSICAL_STANDARD_STEALTH_NO_GO_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_STANDARD_STEALTH_NO_GO_CONTRIBUTION),
                "payload": standard_stealth_no_go_contribution,
            },
            {
                "path": str(CLASSICAL_POSITIVE_BERGER_CLOCK_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_POSITIVE_BERGER_CLOCK_CONTRIBUTION),
                "payload": positive_berger_clock_contribution,
            },
            {
                "path": str(CLASSICAL_BERGER_CLOCK_CHARGE_SEED_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_BERGER_CLOCK_CHARGE_SEED_CONTRIBUTION),
                "payload": berger_clock_charge_seed_contribution,
            },
            {
                "path": str(CLASSICAL_BERGER_FIXED_COUPLING_DELTA_CHARGE_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_BERGER_FIXED_COUPLING_DELTA_CHARGE_CONTRIBUTION),
                "payload": berger_fixed_coupling_delta_charge_contribution,
            },
            {
                "path": str(CLASSICAL_BERGER_MINIMAL_BV_CLOCK_SDR_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_BERGER_MINIMAL_BV_CLOCK_SDR_CONTRIBUTION),
                "payload": berger_minimal_bv_clock_sdr_contribution,
            },
            {
                "path": str(CLASSICAL_BERGER_RETAINED_MINIMAL_LAYOUT_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_BERGER_RETAINED_MINIMAL_LAYOUT_CONTRIBUTION),
                "payload": berger_retained_minimal_layout_contribution,
            },
            {
                "path": str(CLASSICAL_BERGER_GENERATOR_CONJUGATION_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_BERGER_GENERATOR_CONJUGATION_CONTRIBUTION),
                "payload": berger_generator_conjugation_contribution,
            },
            {
                "path": str(CLASSICAL_BERGER_K_CARTAN_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_BERGER_K_CARTAN_CONTRIBUTION),
                "payload": berger_k_cartan_contribution,
            },
            {
                "path": str(CLASSICAL_RELATIVE_FUNCTOR_PREFLIGHT_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(CLASSICAL_RELATIVE_FUNCTOR_PREFLIGHT_CONTRIBUTION),
                "payload": relative_functor_preflight_contribution,
            },
            {
                "path": str(EINSTEIN_ED1A_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_ED1A_CONTRIBUTION),
                "payload": ed1a_contribution,
            },
            {
                "path": str(EINSTEIN_BERGER_INCIDENCE_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_BERGER_INCIDENCE_CONTRIBUTION),
                "payload": berger_incidence_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_PRODUCT_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_PRODUCT_CONTRIBUTION),
                "payload": maxwell_product_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_TANGENT_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_TANGENT_CONTRIBUTION),
                "payload": maxwell_tangent_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_CHEVRETON_TANGENT_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_CHEVRETON_TANGENT_CONTRIBUTION),
                "payload": maxwell_chevreton_tangent_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_SECOND_ORDER_FIXED_FLUX_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_SECOND_ORDER_FIXED_FLUX_CONTRIBUTION),
                "payload": maxwell_second_order_fixed_flux_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_SECOND_ORDER_NULL_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_SECOND_ORDER_NULL_CONTRIBUTION),
                "payload": maxwell_second_order_null_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_PERIODIC_PHOTON_SECOND_ORDER_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_PERIODIC_PHOTON_SECOND_ORDER_CONTRIBUTION),
                "payload": maxwell_periodic_photon_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_PERIODIC_GRAVITON_SECOND_ORDER_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_PERIODIC_GRAVITON_SECOND_ORDER_CONTRIBUTION),
                "payload": maxwell_periodic_graviton_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_OBSTRUCTION_BILINEAR_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_OBSTRUCTION_BILINEAR_CONTRIBUTION),
                "payload": maxwell_obstruction_bilinear_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_COMPACT_DOMAIN_TAUB_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_COMPACT_DOMAIN_TAUB_CONTRIBUTION),
                "payload": maxwell_compact_domain_taub_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_HARMONIC_ADJOINT_BLOCK_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_HARMONIC_ADJOINT_BLOCK_CONTRIBUTION),
                "payload": maxwell_harmonic_adjoint_block_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_AXIAL_MASTER_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_AXIAL_MASTER_CONTRIBUTION),
                "payload": maxwell_axial_master_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_POLAR_MASTER_PREFLIGHT_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_POLAR_MASTER_PREFLIGHT_CONTRIBUTION),
                "payload": maxwell_polar_master_preflight_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_POLAR_MASTER_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_POLAR_MASTER_CONTRIBUTION),
                "payload": maxwell_polar_master_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_POLAR_EXCEPTIONAL_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_POLAR_EXCEPTIONAL_CONTRIBUTION),
                "payload": maxwell_polar_exceptional_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_RADIATIVE_SYMPLECTIC_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_RADIATIVE_SYMPLECTIC_CONTRIBUTION),
                "payload": maxwell_radiative_symplectic_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_EXCEPTIONAL_GLOBAL_SYMPLECTIC_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_EXCEPTIONAL_GLOBAL_SYMPLECTIC_CONTRIBUTION),
                "payload": maxwell_exceptional_global_symplectic_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_SYMPLECTIC_PREFLIGHT_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_SYMPLECTIC_PREFLIGHT_CONTRIBUTION),
                "payload": maxwell_weyl_symplectic_preflight_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_AXIAL_ELL2_RESTRICTION_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_AXIAL_ELL2_RESTRICTION_CONTRIBUTION),
                "payload": maxwell_weyl_axial_ell2_restriction_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_AXIAL_ALL_ELL_RESTRICTION_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_AXIAL_ALL_ELL_RESTRICTION_CONTRIBUTION),
                "payload": maxwell_weyl_axial_all_ell_restriction_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_POLAR_ALL_ELL_RESTRICTION_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_POLAR_ALL_ELL_RESTRICTION_CONTRIBUTION),
                "payload": maxwell_weyl_polar_all_ell_restriction_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_RADIATIVE_RESTRICTION_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_RADIATIVE_RESTRICTION_CONTRIBUTION),
                "payload": maxwell_weyl_radiative_restriction_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_ELL1_PHYSICAL_RESTRICTION_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_ELL1_PHYSICAL_RESTRICTION_CONTRIBUTION),
                "payload": maxwell_weyl_ell1_physical_restriction_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_STANDARD_HARMONIC_INCLUSION_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_STANDARD_HARMONIC_INCLUSION_CONTRIBUTION),
                "payload": maxwell_weyl_standard_harmonic_inclusion_contribution,
            },
            {
                "path": str(EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_PREFLIGHT_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_PREFLIGHT_CONTRIBUTION),
                "payload": relative_linear_triangle_preflight_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_EXTRA_BRANCH_PREFLIGHT_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_EXTRA_BRANCH_PREFLIGHT_CONTRIBUTION),
                "payload": maxwell_weyl_extra_branch_preflight_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR_MODULE_PREFLIGHT_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR_MODULE_PREFLIGHT_CONTRIBUTION),
                "payload": maxwell_weyl_axial_operator_module_preflight_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR_CONTRIBUTION),
                "payload": maxwell_weyl_axial_operator_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_POLAR_OPERATOR_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_POLAR_OPERATOR_CONTRIBUTION),
                "payload": maxwell_weyl_polar_operator_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_POLAR_PHYSICAL_COMPLETION_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_POLAR_PHYSICAL_COMPLETION_CONTRIBUTION),
                "payload": maxwell_weyl_polar_physical_completion_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_POLAR_LEE_WALD_COMPLETION_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_POLAR_LEE_WALD_COMPLETION_CONTRIBUTION),
                "payload": maxwell_weyl_polar_lee_wald_completion_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_NOETHER_LIFT_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_NOETHER_LIFT_CONTRIBUTION),
                "payload": maxwell_weyl_polar_ungauged_noether_lift_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_PLEBANSKI_HACYAN_STABILIZER_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_PLEBANSKI_HACYAN_STABILIZER_CONTRIBUTION),
                "payload": maxwell_weyl_plebanski_hacyan_stabilizer_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_MOMENT_MAP_TAUB_BRIDGE_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_MOMENT_MAP_TAUB_BRIDGE_CONTRIBUTION),
                "payload": maxwell_weyl_moment_map_taub_bridge_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_BALANCED_MIXED_SECOND_ORDER_EXTENSION_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_BALANCED_MIXED_SECOND_ORDER_EXTENSION_CONTRIBUTION),
                "payload": maxwell_weyl_balanced_mixed_second_order_extension_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_GREEN_PAIRING_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_GREEN_PAIRING_CONTRIBUTION),
                "payload": maxwell_weyl_axial_extra_green_pairing_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_AXIAL_LEE_WALD_COMPLETION_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_AXIAL_LEE_WALD_COMPLETION_CONTRIBUTION),
                "payload": maxwell_weyl_axial_lee_wald_completion_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_DETECTOR_TAUB_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_DETECTOR_TAUB_CONTRIBUTION),
                "payload": maxwell_weyl_axial_extra_detector_taub_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_AXIAL_QUADRATIC_CHANNEL_PREFLIGHT_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_AXIAL_QUADRATIC_CHANNEL_PREFLIGHT_CONTRIBUTION),
                "payload": maxwell_weyl_axial_quadratic_channel_preflight_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_AXIAL_EE_ELL2_SOURCE_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_AXIAL_EE_ELL2_SOURCE_CONTRIBUTION),
                "payload": maxwell_weyl_axial_ee_ell2_source_contribution,
            },
            {
                "path": str(EINSTEIN_MAXWELL_WEYL_HERMITIAN_AXIAL_POLAR_ELL2_TAUB_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(EINSTEIN_MAXWELL_WEYL_HERMITIAN_AXIAL_POLAR_ELL2_TAUB_CONTRIBUTION),
                "payload": maxwell_weyl_hermitian_axial_polar_ell2_taub_contribution,
            },
            {
                "path": str(NONLINEAR_ND1_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(NONLINEAR_ND1_CONTRIBUTION),
                "payload": nd1_contribution,
            },
            {
                "path": str(NONLINEAR_BERGER_RETAINED_Q2_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(NONLINEAR_BERGER_RETAINED_Q2_CONTRIBUTION),
                "payload": berger_retained_q2_contribution,
            },
            {
                "path": str(QUANTUM_CARTAN_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(QUANTUM_CARTAN_CONTRIBUTION),
                "payload": quantum_cartan_contribution,
            },
            {
                "path": str(QUANTUM_RELATIVE_CONTRIBUTION.relative_to(ROOT)),
                "sha256": _sha256(QUANTUM_RELATIVE_CONTRIBUTION),
                "payload": quantum_relative_contribution,
            }
        ],
        "team_status": [
            {
                "team_id": "classical",
                "result_state": "BERGER_RAW_D_CHARGE_RIGIDITY_AND_K_CARTAN_THROUGH_ARITY_THREE_COMPLETE",
                "verdict": "RAW_D_LINEAR_NULLITY_K_CARTAN_THROUGH_ARITY_THREE_AFFINE_D_OPEN",
                "established": "Raw D has nonzero but fixed clock momentum and is presymplectically null on the declared fixed-coupling linearized phase space. The background-fixing generator is K_Berger=D-omega R. The complete 54-row complex has K-equivariant advanced and retarded chain contractions, exact support-local q2 and q3, and a cyclic two-sided-causal K-Cartan primitive through arity three. Affine raw-D Cartan, Hadamard, QME, and all-orders claims remain open.",
                "next_gate": "complete K-generator signoff and clean-tree replay for Paper IX; treat affine raw-D Cartan as a separate theorem",
            },
            {
                "team_id": "einstein_boundary",
                "result_state": "G2_PHYSICAL_AXIAL_AND_POLAR_EXTRA_MODULES_STANDARD_PULLBACK_FROZEN_POLAR_CURRENT_AND_RESIDUAL_DESCENT_OPEN",
                "verdict": "PHASE_SPACE_NOT_CLOSED",
                "established": "The complete fixed-bundle standard Einstein--Maxwell harmonic quotient embeds nondegenerately into Weyl--Maxwell before final residual quotient, with the full relative endomorphism classified. The axial target has a direct Lee--Wald completion. On every physical polar ell>=2 compact-momentum fiber, the target splits into the complete Einstein q-primary image plus two extra p-primary summands, with action normalization derived from the four-dimensional variation.",
                "next_gate": "compute the direct polar extra Lee--Wald current and extractors, lift the polar square to the ungauged BV/Noether complex, and perform final residual descent for both extra parities; independently complete the asymptotic Bach phase space and charge audit",
            },
            {
                "team_id": "nonlinear",
                "result_state": "BERGER_Q2_Q3_AND_CAUSAL_K_CARTAN_AVAILABLE_SIGNOFF_PENDING",
                "verdict": "CLASSICAL_K_CARTAN_THROUGH_ARITY_THREE_NONLINEAR_SIGNOFF_PENDING",
                "established": "The complete support-local q2 and q3 and the all-row causal homotopies are available. Under the authoritative generator correction they give the cyclic causal K_Berger Cartan recurrence through arity three. This does not construct affine raw-D Cartan, all-orders closure, a residual/BFV lift, or a quantum theorem.",
                "next_gate": "review and sign off the K_Berger generator interpretation and the through-arity-three claim boundary for Paper IX",
            },
            {
                "team_id": "quantum",
                "result_state": "ALGEBRAIC_ENGINE_AND_RELATIVE_G0_LEDGER_READY_ANALYTIC_FRAMEWORK_MISSING",
                "verdict": "ANALYTIC_FRAMEWORK_MISSING",
                "established": "the current required classical compact-cylinder settings are imported by content hash without quantum promotion; exact Cartan quotient mechanics, complete intrinsic Euler descent, hash-bound AFN0 closure witnesses, and a G0 Einstein--Weyl relative dependency ledger are registered",
                "next_gate": "import EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1 by content hash while completing the local anomaly/QME disposition; retain ANALYTIC_FRAMEWORK_MISSING before any relative anomaly or residual-transfer promotion",
            },
        ],
        "setting_ledger": [
            {
                "setting_id": "compact_unrestricted",
                "generator_id": "D_compact",
                "phase_space_id": "compact_P_lin",
                "boundary_conditions": "closed S3; no residual zero-charge restriction",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "CERTIFIED",
                "verdict": "D_CHARGED",
            },
            {
                "setting_id": "compact_taub_zero",
                "generator_id": "D_compact",
                "phase_space_id": "compact_P_Taub0",
                "boundary_conditions": "closed S3; all fifteen moment maps constrained to zero",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "CERTIFIED",
                "verdict": "D_GAUGE",
            },
            {
                "setting_id": "compact_derived_residual",
                "generator_id": "D_compact",
                "phase_space_id": "compact_P_der",
                "boundary_conditions": "selected closed-universe derived quotient",
                "lifecycle_layer": "CLASSICAL_CARTAN",
                "status": "CERTIFIED",
                "verdict": "D_GAUGE",
            },
            {
                "setting_id": "compact_scalar_clock",
                "generator_id": "D_compact",
                "phase_space_id": "compact_scalar_clock",
                "boundary_conditions": "closed unit S3; exact vacuum-cylinder one-real-scalar candidate",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "BLOCKED",
                "verdict": "SINGLE_SCALAR_CLOCK_BACKGROUND_OBSTRUCTED",
            },
            {
                "setting_id": "compact_neutral_clock_pair",
                "generator_id": "D_compact",
                "phase_space_id": "compact_neutral_clock_pair_homogeneous",
                "boundary_conditions": "closed unit S3; exact Bach-flat cylinder; H_D=0 and W nonzero; no surface flux",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "CERTIFIED",
                "verdict": "D_GAUGE",
            },
            {
                "setting_id": "compact_neutral_clock_pair_local_health",
                "generator_id": "D_compact",
                "phase_space_id": "compact_neutral_clock_pair_local_extension",
                "boundary_conditions": "local cylinder neighborhoods of the neutral winding orbit; all-row causal complex absent",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "BLOCKED",
                "verdict": "OPPOSITE_SIGN_LOCAL_HEALTH_OBSTRUCTED",
            },
            {
                "setting_id": "compact_homogeneous_positive_stealth_clock",
                "generator_id": "D_compact",
                "phase_space_id": "compact_homogeneous_positive_stealth_scalar",
                "boundary_conditions": "closed unit S3; homogeneous positive-sign conformal scalar with quartic Weyl-invariant potential",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "BLOCKED",
                "verdict": "HOMOGENEOUS_STEALTH_CLOCK_OBSTRUCTED",
            },
            {
                "setting_id": "compact_standard_conformal_stealth_clock",
                "generator_id": "D_compact",
                "phase_space_id": "standard_conformal_scalar_stealth_clock_sector",
                "boundary_conditions": "closed unit S3; complete standard positive-sign conformal scalar stealth family, including inhomogeneous configurations",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "BLOCKED",
                "verdict": "STANDARD_ONE_FIELD_STEALTH_CLOCK_NO_GO",
            },
            {
                "setting_id": "compact_positive_berger_clock",
                "generator_id": "D_compact",
                "phase_space_id": "positive_rotating_scalar_berger_background",
                "boundary_conditions": "closed Berger S3; q in ((5-sqrt(21))/2,1/4); exact stationary Bach-sourced background; perturbative reduction open",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "PARTIAL",
                "verdict": "POSITIVE_BERGER_CLOCK_BACKGROUND_EXISTS",
            },
            {
                "setting_id": "compact_positive_berger_clock_reduced_charge",
                "generator_id": "D_compact",
                "phase_space_id": "positive_rotating_scalar_berger_background",
                "boundary_conditions": "closed Berger S3; exact stationary background; reduced homogeneous scalar current only",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "PARTIAL",
                "verdict": "NONZERO_INTERNAL_CLOCK_MOMENTUM_TOTAL_D_OPEN",
            },
            {
                "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
                "generator_id": "D_compact",
                "phase_space_id": "positive_berger_fixed_coupling_linearized_solutions",
                "boundary_conditions": "closed Berger S3; smooth fixed-coupling linearized coupled solutions; no spatial boundary",
                "lifecycle_layer": "CLASSICAL_CHARGE",
                "status": "CERTIFIED",
                "verdict": "D_GAUGE",
            },
            {
                "setting_id": "compact_positive_berger_clock_minimal_bv_sdr",
                "generator_id": "D_compact",
                "phase_space_id": "positive_berger_fixed_coupling_linearized_solutions",
                "boundary_conditions": "closed Berger S3; nonzero rho and omega clock chart; smooth fixed-coupling linearized fields",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "MINIMAL_CLOCK_SECTOR_SDR",
            },
            {
                "setting_id": "compact_positive_berger_clock_retained_minimal_layout",
                "generator_id": "D_compact",
                "phase_space_id": "positive_berger_fixed_coupling_linearized_solutions",
                "boundary_conditions": "closed Berger S3; retained 26-row minimal component layout after the clock SDR",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "RETAINED_MINIMAL_LAYOUT_FROZEN",
            },
            {
                "setting_id": "compact_positive_berger_clock_generator_conjugation",
                "generator_id": "K_Berger",
                "phase_space_id": "positive_berger_fixed_coupling_linearized_solutions",
                "boundary_conditions": "closed Berger cylinder; co-rotating scalar dressing; raw D compared with K=D-omega R",
                "lifecycle_layer": "CLASSICAL_CARTAN",
                "status": "CERTIFIED",
                "verdict": "FROZEN_UNARY_GENERATOR_IS_K_RAW_D_AFFINE",
            },
            {
                "setting_id": "compact_positive_berger_clock_k_cartan_through_arity_three",
                "generator_id": "K_Berger",
                "phase_space_id": "positive_berger_fixed_coupling_linearized_solutions",
                "boundary_conditions": "closed Berger cylinder at q=9/40; complete 54-row gauge-fixed complex; compact-source Green domain; cyclic higher primitives have causal-hull support",
                "lifecycle_layer": "CLASSICAL_CARTAN",
                "status": "CERTIFIED",
                "verdict": "K_CARTAN_CAUSAL_THROUGH_ARITY_THREE",
            },
            {
                "setting_id": "compact_positive_berger_clock_einstein_incidence",
                "generator_id": "D_compact",
                "phase_space_id": "positive_berger_fixed_coupling_linearized_solutions",
                "boundary_conditions": "closed Berger S3; certified positive-clock background; same clock stress in the tested Einstein equation",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "EINSTEIN_TANGENT_NOT_APPLICABLE_AT_THIS_BACKGROUND",
            },
            {
                "setting_id": "compact_einstein_maxwell_product_background",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_background",
                "boundary_conditions": "R_t x S1_L x S2_r flat-critical product; aligned source-free Maxwell flux; tangent phase spaces and charges open",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "COMMON_EINSTEIN_MAXWELL_WEYL_MAXWELL_BACKGROUND",
            },
            {
                "setting_id": "compact_einstein_maxwell_product_tangent_preflight",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_principal_tangent_complex",
                "boundary_conditions": "principal symbols at rational noncharacteristic and null covectors; curved lower-order and global bundle data open",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "PARTIAL",
                "verdict": "PRINCIPAL_TANGENT_CHAIN_MAP_WITH_EXTRA_WEYL_CLASSES",
            },
            {
                "setting_id": "compact_einstein_maxwell_product_on_shell_tangent",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_on_shell_linear_tangents",
                "boundary_conditions": "complete linearized solution tangents at the parallel-flux product before residual quotient; off-shell BV, causal support, and global bundle data open",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "FULL_ON_SHELL_LINEAR_TANGENT_INCLUSION_CHEVRETON",
            },
            {
                "setting_id": "compact_einstein_maxwell_second_order_fixed_flux",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_fixed_flux_second_order",
                "boundary_conditions": "compact periodic product; magnetic flux fixed through epsilon squared; constant-radion and Maxwell-duality fixtures",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "SECOND_ORDER_FIXED_FLUX_OBSTRUCTION_FOR_RADION_AND_DUALITY",
            },
            {
                "setting_id": "universal_cover_einstein_maxwell_second_order_null_extension",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_universal_cover_null_second_order",
                "boundary_conditions": "polynomial null tangent on R^(1,1) x S2; nonperiodic and without causal/asymptotic completion",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "NONZERO_CHEVRETON_NULL_TANGENT_EXTENDS_AT_SECOND_ORDER",
            },
            {
                "setting_id": "compact_einstein_maxwell_periodic_photon_second_order",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_fixed_charge_periodic_photon_second_order",
                "boundary_conditions": "compact periodic product; electric and magnetic charges fixed through epsilon squared; smooth axisymmetric l=1, omega=2 photon--metric mode",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "PERIODIC_PHOTON_SECOND_ORDER_FIXED_CHARGE_OBSTRUCTION",
            },
            {
                "setting_id": "compact_einstein_maxwell_periodic_graviton_second_order",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_fixed_charge_periodic_graviton_second_order",
                "boundary_conditions": "compact periodic product; electric and magnetic charges fixed through epsilon squared; plus branch of one smooth odd-parity l=2 gravitational mode with flux-forced Maxwell dressing",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "PERIODIC_L2_GRAVITATIONAL_MODE_FIXED_CHARGE_OBSTRUCTION",
            },
            {
                "setting_id": "compact_einstein_maxwell_obstruction_bilinear_g1",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_fixture_span_obstruction_bilinear",
                "boundary_conditions": "compact product; declared radion, duality, l=1 photon, and l=2 gravitational-plus span; constant-lapse pairing; fixed and augmented charge fibres",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G1_CONSTANT_LAPSE_OBSTRUCTION_BILINEAR_ON_FIXTURE_SPAN",
            },
            {
                "setting_id": "compact_einstein_maxwell_domain_taub_descent",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_fixed_u1_harmonic_taub",
                "boundary_conditions": "compact product; smooth periodic fields on fixed compact U(1) bundle P_N with N=2; closed Cauchy slice; before final residual quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G1_FIXED_U1_DOMAIN_AND_RELATIVE_TAUB_DESCENT",
            },
            {
                "setting_id": "compact_einstein_maxwell_harmonic_adjoint_block_preflight",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_harmonic_block_preflight",
                "boundary_conditions": "compact fixed-P_N product; declared n=0 axial H_x/a_x tower; smooth periodic identity-component gauge group; before residual quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G1_AXIAL_N0_TOWER_AND_ADJOINT_PREFLIGHT",
            },
            {
                "setting_id": "compact_einstein_maxwell_axial_master_complex",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_axial_master_complex",
                "boundary_conditions": "fixed-P_N compact product; all periodic S1 momenta; standard axial harmonic gauge quotient; before residual quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G1_AXIAL_ALL_MOMENTA_MASTER_COMPLEX",
            },
            {
                "setting_id": "compact_einstein_maxwell_polar_master_preflight",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_polar_master_preflight",
                "boundary_conditions": "fixed-P_N compact product; standard polar Regge--Wheeler gauge; generic ell>=2 matrix; one full-tensor ell=2 plus-branch fixture; before residual quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G1_POLAR_ELL_GE2_MATRIX_PREFLIGHT",
            },
            {
                "setting_id": "compact_einstein_maxwell_polar_master_complex",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_polar_master_complex",
                "boundary_conditions": "fixed-P_N compact product; every periodic S1 momentum and every polar harmonic with ell>=2; complete polar Regge--Wheeler gauge; before residual quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_POLAR_ELL_GE2_ARBITRARY_LAMBDA_TENSOR_IDENTITY",
            },
            {
                "setting_id": "compact_einstein_maxwell_polar_exceptional_complex",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_polar_exceptional_complex",
                "boundary_conditions": "fixed-P_N compact product; exceptional polar ell=0,1; all periodic S1 momenta; smooth periodic identity-component gauge; before residual quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_POLAR_ALL_ELL_LINEAR_COMPLEX",
            },
            {
                "setting_id": "compact_einstein_maxwell_radiative_symplectic_matching",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_radiative_symplectic",
                "boundary_conditions": "fixed-P_N compact product; all periodic S1 momenta and m; radiative ell>=2 plus physical ell=1 quotient; before final residual quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_RADIATIVE_COVARIANT_SYMPLECTIC_MATCHING",
            },
            {
                "setting_id": "compact_einstein_maxwell_exceptional_global_symplectic",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_exceptional_global_symplectic",
                "boundary_conditions": "fixed-P_N compact product; generalized zero-frequency ell=0 and axial ell=1 sectors; smooth periodic identity-component gauge; before final residual quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_EXCEPTIONAL_GLOBAL_SYMPLECTIC_COMPLETION",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_symplectic_preflight",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_symplectic_preflight",
                "boundary_conditions": "fixed-P_N compact product; complete standard harmonic Einstein-Maxwell tangent including generalized global modes; smooth periodic identity-component gauges; before final residual SO(4,2) quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_WEYL_SYMPLECTIC_PREFLIGHT_QUOTIENT_INJECTIVE",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_axial_ell2_restriction",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_axial_ell2_restriction",
                "boundary_conditions": "fixed-P_N compact product; axial ell=2,m=0 Einstein-Maxwell tangent at arbitrary periodic momentum k; both physical branches; before final residual SO(4,2) quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G1_AXIAL_ELL2_BRANCH_DEPENDENT_INDEFINITE_RESTRICTION",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_axial_all_ell_restriction",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_axial_all_ell_restriction",
                "boundary_conditions": "fixed-P_N compact product; every standard axial ell>=2 Einstein-Maxwell tangent, all m, arbitrary periodic momentum k, both physical branches; before final residual SO(4,2) quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G1_AXIAL_ALL_ELL_GE2_BRANCH_DEPENDENT_INDEFINITE_RESTRICTION",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_polar_all_ell_restriction",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_polar_all_ell_restriction",
                "boundary_conditions": "fixed-P_N compact product; every standard polar ell>=2 Einstein-Maxwell tangent, all m, arbitrary periodic momentum k, both physical branches; before final residual SO(4,2) quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_POLAR_ALL_ELL_GE2_BRANCH_DEPENDENT_INDEFINITE_RESTRICTION",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_radiative_restriction",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_standard_radiative_restriction",
                "boundary_conditions": "fixed-P_N compact product; direct sum of every standard axial and polar ell>=2 Einstein-Maxwell tangent, all real harmonic multiplicities, arbitrary periodic momentum, both branches; before final residual SO(4,2) quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G3_STANDARD_RADIATIVE_ALL_ELL_GE2_COMMON_SPECTRAL_NONDEGENERATE_INDEFINITE_RESTRICTION",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_ell1_physical_restriction",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_ell1_physical_quotient",
                "boundary_conditions": "fixed-P_N compact product; every physical axial and polar ell=1 quotient mode, all m and arbitrary periodic momentum; before final residual SO(4,2) quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G3_PHYSICAL_ELL1_ALL_N_M_FACTOR_FOUR_QUOTIENT_RESTRICTION",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_standard_harmonic_inclusion",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_complete_standard_harmonic_tangent",
                "boundary_conditions": "fixed-P_N compact product; complete certified standard Einstein-Maxwell harmonic tangent including generalized global blocks; before final residual SO(4,2) quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G4_COMPLETE_STANDARD_HARMONIC_PULLBACK_NONDEGENERATE_BEFORE_FINAL_QUOTIENT",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_relative_linear_triangle_preflight",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_principal_and_generic_axial_relative_triangle_preflight",
                "boundary_conditions": "fixed-P_N compact product; covariant principal complex and generic axial ell>=2 Fourier-polynomial block; polar, exceptional, global and boundary curved rows open",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_PRINCIPAL_AND_GENERIC_AXIAL_OFFSHELL_RELATIVE_TRIANGLE_PREFLIGHT",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_relative_functor_preflight",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_complete_standard_harmonic_tangent",
                "boundary_conditions": "fixed-P_N compact product; on-shell standard harmonic inclusion imported; off-shell BV triangle and observable pullback absent",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "BLOCKED",
                "verdict": "BLOCKED_ON_EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_extra_branch_preflight",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_extra_branch_preflight",
                "boundary_conditions": "candidate full smooth periodic fixed-P_N Weyl-Maxwell harmonic solution complex; no bounded-time selection or final residual SO(4,2) quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_CANONICAL_EXTRA_QUOTIENT_AND_FULL_BLOCK_SOLVE_CONTRACT",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_axial_operator_module_preflight",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_axial_operator_module_preflight",
                "boundary_conditions": "generic axial ell>=2 exact differential coefficient/gauge module; symbolic k; exceptional loci retained; target operator not yet inserted",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_EXACT_AXIAL_GAUGE_MODULE_AND_OPERATOR_RAILS",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_axial_operator",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_generic_axial_target_solution_module",
                "boundary_conditions": "generic axial ell>=2 exact target solution module; fixed P_N; symbolic k and lambda; before Green/Lee-Wald completion and final residual quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_GENERIC_AXIAL_TARGET_OPERATOR_AND_EXTRA_SOLUTION_MODULE",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_polar_operator",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_generic_polar_target_solution_module",
                "boundary_conditions": "generic polar ell>=2 exact target Hessian on the Weyl slice; fixed P_N; symbolic k and lambda; before physical-ring, Lee-Wald, ungauged, and final residual completion",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_GENERIC_POLAR_TARGET_OPERATOR_AND_OFFSHELL_EINSTEIN_SQUARE",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_polar_physical_completion",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_physical_polar_target_solution_module",
                "boundary_conditions": "every physical polar ell>=2 and compact momentum including k=0; fixed P_N; before polar Lee-Wald, ungauged, and final residual completion",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_PHYSICAL_POLAR_EXTRA_QUOTIENT_AND_EINSTEIN_PRIMARY_IMAGE",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_polar_lee_wald_completion",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_generic_polar_direct_lee_wald_block",
                "boundary_conditions": "complete physical polar ell>=2 direct Lee-Wald solution block at every allowed compact momentum including k=0; before ungauged lift, final residual quotient, and causal boundary selection",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_GENERIC_POLAR_DIRECT_LEE_WALD_BLOCK_INERTIA_THREE_ONE",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_polar_ungauged_noether_lift",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_generic_polar_ungauged_noether_complex",
                "boundary_conditions": "generic polar ell>=2 Fourier-polynomial ungauged Einstein-Maxwell and Weyl-Maxwell equation/Noether complexes at every allowed compact momentum including k=0; fixed P_N; before cyclic enhancement, final residual quotient, and causal boundary selection",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_GENERIC_POLAR_UNGAUGED_EQUATION_NOETHER_CHAIN_MAP",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_plebanski_hacyan_stabilizer_descent",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_generic_stabilizer_representation",
                "boundary_conditions": "generic axial and polar ell>=2 q/p-primary modules at every allowed compact momentum on the fixed magnetic product; after local gauge reduction with the five background stabilizers retained as global symmetries; before a common moment-map/Taub-zero derived sector",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_PH_STABILIZER_PRIMARY_EQUIVARIANT_ABSOLUTE_QUOTIENT_NOT_AUTHORIZED",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_moment_map_taub_bridge",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_generic_fixed_bundle_moment_map_taub",
                "boundary_conditions": "generic axial and polar ell>=2 q/p-primary real solution space at every allowed compact momentum on fixed P_N; after local gauge reduction with the five background stabilizers retained; before mixed common-zero-locus, exceptional/global, cyclic, or causal completion",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_GENERIC_PURE_EXTRA_FIXED_BUNDLE_TAUB_NO_GO",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_balanced_mixed_second_order_extension",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_ell2_k0_balanced_mixed_second_order_jet",
                "boundary_conditions": "real axial ell=2,m=0,k=0 Einstein-minus plus second-extra balanced tangent at fixed P_N; after local gauge reduction and before stabilizer quotient, all-orders, cyclic, or causal completion",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G1_BALANCED_MIXED_TANGENT_COMPLETE_SECOND_ORDER_EXTENSION",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_axial_extra_green_pairing",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_generic_axial_extra_reduced_green_pairing",
                "boundary_conditions": "generic axial extra module with exact reduced-Hessian local Green current; physical ell>=2; before direct Lee-Wald match and final residual quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_GENERIC_AXIAL_EXTRA_NONRADICAL_REDUCED_GREEN_SIGNATURE_POSITIVE_TWO",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_axial_lee_wald_completion",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_generic_axial_direct_lee_wald_block",
                "boundary_conditions": "complete generic compact axial direct Lee-Wald solution block; before final residual quotient and causal boundary selection",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_GENERIC_AXIAL_DIRECT_LEE_WALD_BLOCK_SIGNATURE_THREE_ONE",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_axial_extra_detector_taub",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_axial_extra_ell2_k0_fixed_charge_taub",
                "boundary_conditions": "generic axial reduced detector; quadratic Taub verdict restricted to real ell=2,k=0 at fixed electric and magnetic charges; before final residual quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_AXIAL_EXTRA_DETECTOR_AND_ELL2_K0_NEGATIVE_DEFINITE_TAUB_OBSTRUCTION",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_axial_quadratic_channel_preflight",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_axial_ee_finite_window_and_ell2_removable_block",
                "boundary_conditions": "fixed-P_N compact product; parity-compatible axial-Einstein by polar-Einstein inputs; finite ell and momentum resonance window; first ell=2,k=0 removable sum-frequency block; before final residual quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G2_AXIAL_EE_FINITE_RESONANCE_WINDOW_AND_FIRST_REMOVABLE_BLOCK",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_axial_ee_ell2_source",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_axial_ee_ell2_sum_frequency_block",
                "boundary_conditions": "fixed-P_N compact product; complex axial-plus-polar Einstein ell=2,k=0 minus-branch input; four independent gauge-fixed axial sum-frequency rows; before final residual quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G1_MIXED_EE_AXIAL_ELL2_SUM_FREQUENCY_BLOCK_EXPLICITLY_REMOVABLE",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub",
                "generator_id": "H_product",
                "phase_space_id": "einstein_maxwell_product_compact_fixed_bundle_hermitian_axial_polar_ell2_minus_pair",
                "boundary_conditions": "fixed-P_N compact product; all real quadratures of the axial-polar Einstein ell=2,k=0 minus-frequency pair; fixed electric and magnetic charges; before final residual quotient",
                "lifecycle_layer": "CLASSICAL_BV",
                "status": "CERTIFIED",
                "verdict": "G1_HERMITIAN_AXIAL_POLAR_ELL2_MINUS_PAIR_POSITIVE_TAUB_FIXED_BUNDLE_NO_GO",
            },
            {
                "setting_id": "compact_selected_residual_HT1_q2",
                "generator_id": "D_compact",
                "phase_space_id": "compact_selected_residual_HT1",
                "boundary_conditions": "closed cylinder; selected endpoint-projected HT1 BFV q2 domain",
                "lifecycle_layer": "INTERACTING",
                "status": "PARTIAL",
                "verdict": "SELECTED_RESIDUAL_D_DERIVATION_HOLDS_AT_ARITY_TWO",
            },
            {
                "setting_id": "compact_positive_berger_clock_retained_q2_26",
                "generator_id": "K_Berger",
                "phase_space_id": "positive_berger_fixed_coupling_linearized_solutions",
                "boundary_conditions": "closed Berger cylinder; exact support-local 54-to-26 contraction; bare local unary K-Cartan ansatz",
                "lifecycle_layer": "INTERACTING",
                "status": "CERTIFIED",
                "verdict": "RETAINED_Q2_26_COMPLETE_BARE_LOCAL_UNARY_K_CARTAN_OBSTRUCTED",
            },
            {
                "setting_id": "compact_interacting",
                "generator_id": "K_Berger",
                "phase_space_id": "positive_berger_fixed_coupling_linearized_solutions",
                "boundary_conditions": "closed Berger cylinder at q=9/40; complete q2/q3 and causal K-Cartan through arity three; all-orders and residual/BFV extensions absent",
                "lifecycle_layer": "INTERACTING",
                "status": "PARTIAL",
                "verdict": "K_CARTAN_THROUGH_ARITY_THREE_ALL_ORDERS_AND_RESIDUAL_BFV_OPEN",
            },
            {
                "setting_id": "compact_quantum",
                "generator_id": "D_compact",
                "phase_space_id": "compact_quantum",
                "boundary_conditions": "renormalized observable algebra not constructed",
                "lifecycle_layer": "QUANTUM",
                "status": "BLOCKED",
                "verdict": "ANALYTIC_FRAMEWORK_MISSING",
            },
            {
                "setting_id": "compact_einstein_maxwell_weyl_relative_quantum_readiness",
                "generator_id": "D_compact",
                "phase_space_id": "einstein_maxwell_product_compact_weyl_complete_standard_harmonic_tangent",
                "boundary_conditions": "R_t x S1_L x S2; fixed N=2 compact bundle; standard harmonic tangent before final residual quotient; off-shell BV triangle and renormalized observable algebra absent",
                "lifecycle_layer": "QUANTUM",
                "status": "BLOCKED",
                "verdict": "ANALYTIC_FRAMEWORK_MISSING",
            },
            {
                "setting_id": "asymptotic_real_cylinder_time",
                "generator_id": "H_ESU",
                "phase_space_id": "asymptotically_flat_full_Bach",
                "boundary_conditions": "fixed Minkowski null boundary",
                "lifecycle_layer": "LORENTZIAN_CAUSAL",
                "status": "OPEN",
                "verdict": "PHASE_SPACE_NOT_CLOSED",
            },
            {
                "setting_id": "asymptotic_dilation",
                "generator_id": "D_M",
                "phase_space_id": "asymptotically_flat_full_Bach",
                "boundary_conditions": "full null-infinity data not yet closed",
                "lifecycle_layer": "LORENTZIAN_CAUSAL",
                "status": "OPEN",
                "verdict": None,
            },
            {
                "setting_id": "asymptotic_time_translation",
                "generator_id": "P_0",
                "phase_space_id": "asymptotically_flat_full_Bach",
                "boundary_conditions": "Bondi/ADM boundary conditions not yet completed for pure Weyl",
                "lifecycle_layer": "LORENTZIAN_CAUSAL",
                "status": "OPEN",
                "verdict": None,
            },
            {
                "setting_id": "lorentzian_dS_AdS",
                "generator_id": "UNSELECTED",
                "phase_space_id": "lorentzian_dS_AdS",
                "boundary_conditions": "not specified",
                "lifecycle_layer": "LORENTZIAN_CAUSAL",
                "status": "NOT_TESTED",
                "verdict": None,
            },
        ],
        "dependency_gate": [
            "the selected generator preserves the declared phase space and boundary data",
            "the generator is Hamiltonian with an integrable normalized charge",
            "the charge vanishes on the exact sector proposed for quotienting",
            "the zero-charge transformations close as a Lie algebra or declared algebroid",
            "the classical Cartan and causal homotopies exist in the declared support category",
            "Berger retained q1, the cyclic 54-to-26 contraction, K_Berger action, complete q2 and q3, advanced/retarded all-row Green homotopies, and the cyclic two-sided-causal K-Cartan recurrence through arity three are complete; affine raw-D Cartan, Hadamard, QME, and all-orders closure remain open",
            "the Einstein--Maxwell product common background is certified; its two tangent BV complexes, chain map, cohomology, presymplectic comparison, and all D/charge questions remain open",
            "the product principal tangent chain map is certified with two additional simple-symbol Weyl metric classes; the complete Einstein--Maxwell solution tangent also injects on shell by the Chevreton factorization, while off-shell BV rows, prolonged modes, cyclicity, presymplectic comparison, nonlinear closure, and all D/charge questions remain open",
            "the compact radion, duality, l=1 photon, and l=2 gravitational-plus fixtures assemble into a certified constant-lapse obstruction bilinear on their declared span, with exact charge-fibre cokernel behavior and relative Taub interpretation; the full harmonic domain and full cokernel remain open",
            "interacting promotion requires a scoped Cartan extension beyond the certified bare local unary no-go",
            "quantum promotion requires a restored QME and renormalized Ward identity",
        ],
        "publication_plan": {
            "current_form": "CROSS_PROGRAMME_VALIDATION_DOSSIER",
            "papers_VII_VIII": "completed theorem retained with explicit compact phase-space scope",
            "paper_IX": {
                "status": "WRITING_STARTED",
                "working_title": "A backreacting phase clock with fixed momentum in pure-Weyl gravity: fixed-coupling rigidity and causal BV Cartan analysis of the helical stabilizer",
                "promotion_gate": "K-generator classical/nonlinear/quantum signoff and clean-tree replay; affine raw-D Cartan is not required for the scoped K theorem",
                "theorem_frozen": False,
                "claim_table": _team_input(str(PAPER_IX_CLAIM_TABLE.relative_to(ROOT))),
            },
            "paper_X": {
                "status": "RESERVED_NOT_STARTED",
                "working_title": "Interaction and Quantum Stability of the Residual D-Quotient",
                "promotion_gate": "complete classical nonlinear export and applicable QME/Ward gate",
            },
        },
        "next_shared_gate": {
            "gate_id": "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1",
            "owner_order": ["einstein_boundary", "classical", "nonlinear", "quantum"],
            "rule": "The Einstein team must export the complete off-shell all-sector relative triangle with the declared acceptance flags. The classical team then imports it by commit and hash before constructing residual equivariance, cofiber compatibility, and observable pullback. A generic-axial preflight or on-shell inclusion cannot promote this gate.",
        },
        "claim_boundary": (
            "The dossier consolidates sector-indexed results. It does not promote a "
            "universal D-gauge verdict, an interacting Cartan theorem, a quantum "
            "anomaly result, or an asymptotic charge theorem."
        ),
    }


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "pure-weyl-d-quotient-programme-status-v1":
        errors.append("unsupported schema")
    if data.get("claim_key") != [
        "generator_id",
        "phase_space_id",
        "boundary_conditions",
        "lifecycle_layer",
    ]:
        errors.append("claim key drifted")
    teams = data.get("team_status", [])
    if [row.get("team_id") for row in teams] != [
        "classical",
        "einstein_boundary",
        "nonlinear",
        "quantum",
    ]:
        errors.append("four-team inventory drifted")
    quantum_contributions = {
        record.get("payload", {}).get("setting_id"): record.get("payload", {})
        for record in data.get("team_contributions", [])
        if record.get("payload", {}).get("team_id") == "quantum"
    }
    if not (
        set(quantum_contributions)
        == {
            "vacuum_cylinder",
            "compact_einstein_maxwell_weyl_relative_quantum_readiness",
        }
        and quantum_contributions["vacuum_cylinder"].get("claim_status") == "BLOCKED"
        and quantum_contributions["vacuum_cylinder"].get("verdict") is None
        and quantum_contributions[
            "compact_einstein_maxwell_weyl_relative_quantum_readiness"
        ].get("claim_status")
        == "BLOCKED"
        and quantum_contributions[
            "compact_einstein_maxwell_weyl_relative_quantum_readiness"
        ].get("verdict")
        == "ANALYTIC_FRAMEWORK_MISSING"
    ):
        errors.append("quantum blocked contribution inventory drifted")
    nonlinear_contributions = {
        record.get("payload", {}).get("setting_id")
        for record in data.get("team_contributions", [])
        if record.get("payload", {}).get("team_id") == "nonlinear"
    }
    if nonlinear_contributions != {
        "compact_selected_residual_HT1_q2",
        "compact_positive_berger_clock_retained_q2_26",
    }:
        errors.append("nonlinear contribution inventory drifted")
    contribution_ids = {
        record.get("payload", {}).get("setting_id")
        for record in data.get("team_contributions", [])
    }
    for setting_id in (
        "compact_positive_berger_clock_generator_conjugation",
        "compact_positive_berger_clock_k_cartan_through_arity_three",
        "compact_einstein_maxwell_weyl_relative_functor_preflight",
    ):
        if setting_id not in contribution_ids:
            errors.append(f"required classical contribution dropped: {setting_id}")
    einstein_contributions = {
        record.get("payload", {}).get("setting_id")
        for record in data.get("team_contributions", [])
        if record.get("payload", {}).get("team_id") == "einstein_boundary"
    }
    if einstein_contributions != {
        "asymptotic_real_cylinder_time",
        "compact_positive_berger_clock_einstein_incidence",
        "compact_einstein_maxwell_product_background",
        "compact_einstein_maxwell_product_tangent_preflight",
        "compact_einstein_maxwell_product_on_shell_tangent",
        "compact_einstein_maxwell_second_order_fixed_flux",
        "universal_cover_einstein_maxwell_second_order_null_extension",
        "compact_einstein_maxwell_periodic_photon_second_order",
        "compact_einstein_maxwell_periodic_graviton_second_order",
        "compact_einstein_maxwell_obstruction_bilinear_g1",
        "compact_einstein_maxwell_domain_taub_descent",
        "compact_einstein_maxwell_harmonic_adjoint_block_preflight",
        "compact_einstein_maxwell_axial_master_complex",
        "compact_einstein_maxwell_polar_master_preflight",
        "compact_einstein_maxwell_polar_master_complex",
        "compact_einstein_maxwell_polar_exceptional_complex",
        "compact_einstein_maxwell_radiative_symplectic_matching",
        "compact_einstein_maxwell_exceptional_global_symplectic",
        "compact_einstein_maxwell_weyl_symplectic_preflight",
        "compact_einstein_maxwell_weyl_axial_ell2_restriction",
        "compact_einstein_maxwell_weyl_axial_all_ell_restriction",
        "compact_einstein_maxwell_weyl_polar_all_ell_restriction",
        "compact_einstein_maxwell_weyl_radiative_restriction",
        "compact_einstein_maxwell_weyl_ell1_physical_restriction",
        "compact_einstein_maxwell_weyl_standard_harmonic_inclusion",
        "compact_einstein_maxwell_weyl_relative_linear_triangle_preflight",
        "compact_einstein_maxwell_weyl_extra_branch_preflight",
        "compact_einstein_maxwell_weyl_axial_operator_module_preflight",
        "compact_einstein_maxwell_weyl_axial_operator",
        "compact_einstein_maxwell_weyl_polar_operator",
        "compact_einstein_maxwell_weyl_polar_physical_completion",
        "compact_einstein_maxwell_weyl_polar_lee_wald_completion",
        "compact_einstein_maxwell_weyl_polar_ungauged_noether_lift",
        "compact_einstein_maxwell_weyl_plebanski_hacyan_stabilizer_descent",
        "compact_einstein_maxwell_weyl_moment_map_taub_bridge",
        "compact_einstein_maxwell_weyl_balanced_mixed_second_order_extension",
        "compact_einstein_maxwell_weyl_axial_extra_green_pairing",
        "compact_einstein_maxwell_weyl_axial_lee_wald_completion",
        "compact_einstein_maxwell_weyl_axial_extra_detector_taub",
        "compact_einstein_maxwell_weyl_axial_quadratic_channel_preflight",
        "compact_einstein_maxwell_weyl_axial_ee_ell2_source",
        "compact_einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub",
    }:
        errors.append("Einstein contribution inventory drifted")
    ledger = {row.get("setting_id"): row for row in data.get("setting_ledger", [])}
    required = {
        "compact_unrestricted": "D_CHARGED",
        "compact_taub_zero": "D_GAUGE",
        "compact_derived_residual": "D_GAUGE",
        "compact_scalar_clock": "SINGLE_SCALAR_CLOCK_BACKGROUND_OBSTRUCTED",
        "compact_neutral_clock_pair": "D_GAUGE",
        "compact_neutral_clock_pair_local_health": "OPPOSITE_SIGN_LOCAL_HEALTH_OBSTRUCTED",
        "compact_homogeneous_positive_stealth_clock": "HOMOGENEOUS_STEALTH_CLOCK_OBSTRUCTED",
        "compact_standard_conformal_stealth_clock": "STANDARD_ONE_FIELD_STEALTH_CLOCK_NO_GO",
        "compact_positive_berger_clock": "POSITIVE_BERGER_CLOCK_BACKGROUND_EXISTS",
        "compact_positive_berger_clock_reduced_charge": "NONZERO_INTERNAL_CLOCK_MOMENTUM_TOTAL_D_OPEN",
        "compact_positive_berger_clock_fixed_coupling_linearized": "D_GAUGE",
        "compact_positive_berger_clock_minimal_bv_sdr": "MINIMAL_CLOCK_SECTOR_SDR",
        "compact_positive_berger_clock_retained_minimal_layout": "RETAINED_MINIMAL_LAYOUT_FROZEN",
        "compact_positive_berger_clock_generator_conjugation": "FROZEN_UNARY_GENERATOR_IS_K_RAW_D_AFFINE",
        "compact_positive_berger_clock_k_cartan_through_arity_three": "K_CARTAN_CAUSAL_THROUGH_ARITY_THREE",
        "compact_positive_berger_clock_einstein_incidence": "EINSTEIN_TANGENT_NOT_APPLICABLE_AT_THIS_BACKGROUND",
        "compact_einstein_maxwell_product_background": "COMMON_EINSTEIN_MAXWELL_WEYL_MAXWELL_BACKGROUND",
        "compact_einstein_maxwell_product_tangent_preflight": "PRINCIPAL_TANGENT_CHAIN_MAP_WITH_EXTRA_WEYL_CLASSES",
        "compact_einstein_maxwell_product_on_shell_tangent": "FULL_ON_SHELL_LINEAR_TANGENT_INCLUSION_CHEVRETON",
        "compact_einstein_maxwell_second_order_fixed_flux": "SECOND_ORDER_FIXED_FLUX_OBSTRUCTION_FOR_RADION_AND_DUALITY",
        "universal_cover_einstein_maxwell_second_order_null_extension": "NONZERO_CHEVRETON_NULL_TANGENT_EXTENDS_AT_SECOND_ORDER",
        "compact_einstein_maxwell_periodic_photon_second_order": "PERIODIC_PHOTON_SECOND_ORDER_FIXED_CHARGE_OBSTRUCTION",
        "compact_einstein_maxwell_periodic_graviton_second_order": "PERIODIC_L2_GRAVITATIONAL_MODE_FIXED_CHARGE_OBSTRUCTION",
        "compact_einstein_maxwell_obstruction_bilinear_g1": "G1_CONSTANT_LAPSE_OBSTRUCTION_BILINEAR_ON_FIXTURE_SPAN",
        "compact_einstein_maxwell_domain_taub_descent": "G1_FIXED_U1_DOMAIN_AND_RELATIVE_TAUB_DESCENT",
        "compact_einstein_maxwell_harmonic_adjoint_block_preflight": "G1_AXIAL_N0_TOWER_AND_ADJOINT_PREFLIGHT",
        "compact_einstein_maxwell_axial_master_complex": "G1_AXIAL_ALL_MOMENTA_MASTER_COMPLEX",
        "compact_einstein_maxwell_polar_master_preflight": "G1_POLAR_ELL_GE2_MATRIX_PREFLIGHT",
        "compact_einstein_maxwell_polar_master_complex": "G2_POLAR_ELL_GE2_ARBITRARY_LAMBDA_TENSOR_IDENTITY",
        "compact_einstein_maxwell_polar_exceptional_complex": "G2_POLAR_ALL_ELL_LINEAR_COMPLEX",
        "compact_einstein_maxwell_radiative_symplectic_matching": "G2_RADIATIVE_COVARIANT_SYMPLECTIC_MATCHING",
        "compact_einstein_maxwell_exceptional_global_symplectic": "G2_EXCEPTIONAL_GLOBAL_SYMPLECTIC_COMPLETION",
        "compact_einstein_maxwell_weyl_symplectic_preflight": "G2_WEYL_SYMPLECTIC_PREFLIGHT_QUOTIENT_INJECTIVE",
        "compact_einstein_maxwell_weyl_axial_ell2_restriction": "G1_AXIAL_ELL2_BRANCH_DEPENDENT_INDEFINITE_RESTRICTION",
        "compact_einstein_maxwell_weyl_axial_all_ell_restriction": "G1_AXIAL_ALL_ELL_GE2_BRANCH_DEPENDENT_INDEFINITE_RESTRICTION",
        "compact_einstein_maxwell_weyl_polar_all_ell_restriction": "G2_POLAR_ALL_ELL_GE2_BRANCH_DEPENDENT_INDEFINITE_RESTRICTION",
        "compact_einstein_maxwell_weyl_radiative_restriction": "G3_STANDARD_RADIATIVE_ALL_ELL_GE2_COMMON_SPECTRAL_NONDEGENERATE_INDEFINITE_RESTRICTION",
        "compact_einstein_maxwell_weyl_ell1_physical_restriction": "G3_PHYSICAL_ELL1_ALL_N_M_FACTOR_FOUR_QUOTIENT_RESTRICTION",
        "compact_einstein_maxwell_weyl_standard_harmonic_inclusion": "G4_COMPLETE_STANDARD_HARMONIC_PULLBACK_NONDEGENERATE_BEFORE_FINAL_QUOTIENT",
        "compact_einstein_maxwell_weyl_relative_linear_triangle_preflight": "G2_PRINCIPAL_AND_GENERIC_AXIAL_OFFSHELL_RELATIVE_TRIANGLE_PREFLIGHT",
        "compact_einstein_maxwell_weyl_relative_functor_preflight": "BLOCKED_ON_EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1",
        "compact_einstein_maxwell_weyl_extra_branch_preflight": "G2_CANONICAL_EXTRA_QUOTIENT_AND_FULL_BLOCK_SOLVE_CONTRACT",
        "compact_einstein_maxwell_weyl_axial_operator_module_preflight": "G2_EXACT_AXIAL_GAUGE_MODULE_AND_OPERATOR_RAILS",
        "compact_einstein_maxwell_weyl_axial_operator": "G2_GENERIC_AXIAL_TARGET_OPERATOR_AND_EXTRA_SOLUTION_MODULE",
        "compact_einstein_maxwell_weyl_polar_operator": "G2_GENERIC_POLAR_TARGET_OPERATOR_AND_OFFSHELL_EINSTEIN_SQUARE",
        "compact_einstein_maxwell_weyl_polar_physical_completion": "G2_PHYSICAL_POLAR_EXTRA_QUOTIENT_AND_EINSTEIN_PRIMARY_IMAGE",
        "compact_einstein_maxwell_weyl_polar_lee_wald_completion": "G2_GENERIC_POLAR_DIRECT_LEE_WALD_BLOCK_INERTIA_THREE_ONE",
        "compact_einstein_maxwell_weyl_polar_ungauged_noether_lift": "G2_GENERIC_POLAR_UNGAUGED_EQUATION_NOETHER_CHAIN_MAP",
        "compact_einstein_maxwell_weyl_plebanski_hacyan_stabilizer_descent": "G2_PH_STABILIZER_PRIMARY_EQUIVARIANT_ABSOLUTE_QUOTIENT_NOT_AUTHORIZED",
        "compact_einstein_maxwell_weyl_moment_map_taub_bridge": "G2_GENERIC_PURE_EXTRA_FIXED_BUNDLE_TAUB_NO_GO",
        "compact_einstein_maxwell_weyl_balanced_mixed_second_order_extension": "G1_BALANCED_MIXED_TANGENT_COMPLETE_SECOND_ORDER_EXTENSION",
        "compact_einstein_maxwell_weyl_axial_extra_green_pairing": "G2_GENERIC_AXIAL_EXTRA_NONRADICAL_REDUCED_GREEN_SIGNATURE_POSITIVE_TWO",
        "compact_einstein_maxwell_weyl_axial_lee_wald_completion": "G2_GENERIC_AXIAL_DIRECT_LEE_WALD_BLOCK_SIGNATURE_THREE_ONE",
        "compact_einstein_maxwell_weyl_axial_extra_detector_taub": "G2_AXIAL_EXTRA_DETECTOR_AND_ELL2_K0_NEGATIVE_DEFINITE_TAUB_OBSTRUCTION",
        "compact_einstein_maxwell_weyl_axial_quadratic_channel_preflight": "G2_AXIAL_EE_FINITE_RESONANCE_WINDOW_AND_FIRST_REMOVABLE_BLOCK",
        "compact_einstein_maxwell_weyl_axial_ee_ell2_source": "G1_MIXED_EE_AXIAL_ELL2_SUM_FREQUENCY_BLOCK_EXPLICITLY_REMOVABLE",
        "compact_einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub": "G1_HERMITIAN_AXIAL_POLAR_ELL2_MINUS_PAIR_POSITIVE_TAUB_FIXED_BUNDLE_NO_GO",
        "compact_selected_residual_HT1_q2": "SELECTED_RESIDUAL_D_DERIVATION_HOLDS_AT_ARITY_TWO",
        "compact_positive_berger_clock_retained_q2_26": "RETAINED_Q2_26_COMPLETE_BARE_LOCAL_UNARY_K_CARTAN_OBSTRUCTED",
        "asymptotic_real_cylinder_time": "PHASE_SPACE_NOT_CLOSED",
    }
    for setting, verdict in required.items():
        if ledger.get(setting, {}).get("verdict") != verdict:
            errors.append(f"{setting} verdict drifted")
    if ledger.get("compact_neutral_clock_pair", {}).get("phase_space_id") != (
        "compact_neutral_clock_pair_homogeneous"
    ):
        errors.append("neutral-clock verdict escaped its homogeneous phase space")
    if ledger.get("compact_quantum", {}).get("verdict") != "ANALYTIC_FRAMEWORK_MISSING":
        errors.append("quantum verdict promoted before QME")
    relative_quantum = ledger.get(
        "compact_einstein_maxwell_weyl_relative_quantum_readiness", {}
    )
    if (
        relative_quantum.get("status") != "BLOCKED"
        or relative_quantum.get("verdict") != "ANALYTIC_FRAMEWORK_MISSING"
        or relative_quantum.get("phase_space_id")
        != "einstein_maxwell_product_compact_weyl_complete_standard_harmonic_tangent"
    ):
        errors.append("relative quantum readiness was dropped or promoted")
    if ledger.get("compact_interacting", {}).get("verdict") != (
        "K_CARTAN_THROUGH_ARITY_THREE_ALL_ORDERS_AND_RESIDUAL_BFV_OPEN"
    ):
        errors.append("Berger interaction row escaped its through-arity-three boundary")
    if ledger.get("compact_positive_berger_clock_retained_q2_26", {}).get(
        "status"
    ) != "CERTIFIED":
        errors.append("retained Berger q2_26 theorem was dropped")
    if ledger.get("compact_positive_berger_clock", {}).get("status") != "PARTIAL":
        errors.append("positive Berger background promoted before charge/BV audit")
    if ledger.get("compact_positive_berger_clock_reduced_charge", {}).get("status") != "PARTIAL":
        errors.append("Berger internal charge seed promoted to a total D verdict")
    if ledger.get("compact_positive_berger_clock_fixed_coupling_linearized", {}).get("status") != "CERTIFIED":
        errors.append("fixed-coupling Berger D_GAUGE theorem was dropped")
    if ledger.get("compact_positive_berger_clock_retained_minimal_layout", {}).get("status") != "CERTIFIED":
        errors.append("Berger retained minimal layout was dropped")
    if ledger.get("compact_positive_berger_clock_generator_conjugation", {}).get("status") != "CERTIFIED":
        errors.append("Berger D/K generator correction was dropped")
    if ledger.get("compact_positive_berger_clock_k_cartan_through_arity_three", {}).get("status") != "CERTIFIED":
        errors.append("Berger causal K-Cartan theorem was dropped")
    if ledger.get("compact_positive_berger_clock_minimal_bv_sdr", {}).get("status") != "CERTIFIED":
        errors.append("minimal Berger clock BV SDR was dropped")
    if ledger.get("compact_positive_berger_clock_einstein_incidence", {}).get("status") != "CERTIFIED":
        errors.append("Berger Einstein-incidence classification was dropped")
    if ledger.get("compact_einstein_maxwell_product_background", {}).get("status") != "CERTIFIED":
        errors.append("Einstein--Maxwell product common background was dropped")
    if ledger.get("compact_einstein_maxwell_product_tangent_preflight", {}).get("status") != "PARTIAL":
        errors.append("Einstein--Maxwell product tangent preflight was promoted or dropped")
    if ledger.get("compact_einstein_maxwell_product_on_shell_tangent", {}).get("status") != "CERTIFIED":
        errors.append("Einstein--Maxwell full on-shell tangent theorem was dropped")
    if ledger.get("compact_einstein_maxwell_second_order_fixed_flux", {}).get("status") != "CERTIFIED":
        errors.append("Einstein--Maxwell fixed-flux second-order obstruction was dropped")
    if ledger.get("universal_cover_einstein_maxwell_second_order_null_extension", {}).get("status") != "CERTIFIED":
        errors.append("Einstein--Maxwell null second-order extension was dropped")
    if ledger.get("compact_einstein_maxwell_periodic_photon_second_order", {}).get("status") != "CERTIFIED":
        errors.append("Einstein--Maxwell periodic photon second-order obstruction was dropped")
    if ledger.get("compact_einstein_maxwell_periodic_graviton_second_order", {}).get("status") != "CERTIFIED":
        errors.append("Einstein--Maxwell periodic gravitational-mode second-order obstruction was dropped")
    if ledger.get("compact_einstein_maxwell_obstruction_bilinear_g1", {}).get("status") != "CERTIFIED":
        errors.append("Einstein--Maxwell G1 obstruction bilinear was dropped")
    if ledger.get("compact_einstein_maxwell_domain_taub_descent", {}).get("status") != "CERTIFIED":
        errors.append("Einstein--Maxwell fixed-U1 domain/Taub descent was dropped")
    if ledger.get("compact_einstein_maxwell_harmonic_adjoint_block_preflight", {}).get("status") != "CERTIFIED":
        errors.append("Einstein--Maxwell harmonic/adjoint block preflight was dropped")
    if ledger.get("compact_einstein_maxwell_axial_master_complex", {}).get("status") != "CERTIFIED":
        errors.append("Einstein--Maxwell axial master complex was dropped")
    if ledger.get("compact_einstein_maxwell_polar_master_preflight", {}).get("status") != "CERTIFIED":
        errors.append("Einstein--Maxwell polar master preflight was dropped")
    if ledger.get("compact_einstein_maxwell_polar_master_complex", {}).get("status") != "CERTIFIED":
        errors.append("Einstein--Maxwell polar master complex was dropped")
    if ledger.get("compact_einstein_maxwell_polar_exceptional_complex", {}).get("status") != "CERTIFIED":
        errors.append("Einstein--Maxwell polar exceptional complex was dropped")
    if ledger.get("compact_einstein_maxwell_radiative_symplectic_matching", {}).get("status") != "CERTIFIED":
        errors.append("Einstein--Maxwell radiative symplectic theorem was dropped")
    if ledger.get("compact_einstein_maxwell_exceptional_global_symplectic", {}).get("status") != "CERTIFIED":
        errors.append("Einstein--Maxwell exceptional global symplectic theorem was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_symplectic_preflight", {}).get("status") != "CERTIFIED":
        errors.append("Einstein--Maxwell/Weyl--Maxwell symplectic preflight was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_axial_ell2_restriction", {}).get("status") != "CERTIFIED":
        errors.append("axial ell=2 Weyl--Maxwell restriction theorem was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_axial_all_ell_restriction", {}).get("status") != "CERTIFIED":
        errors.append("all-ell axial Weyl--Maxwell restriction theorem was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_polar_all_ell_restriction", {}).get("status") != "CERTIFIED":
        errors.append("all-ell polar Weyl--Maxwell restriction theorem was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_radiative_restriction", {}).get("status") != "CERTIFIED":
        errors.append("combined standard radiative Weyl--Maxwell restriction theorem was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_ell1_physical_restriction", {}).get("status") != "CERTIFIED":
        errors.append("physical ell=1 Weyl--Maxwell quotient restriction theorem was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_standard_harmonic_inclusion", {}).get("status") != "CERTIFIED":
        errors.append("complete standard-harmonic Weyl--Maxwell inclusion theorem was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_relative_linear_triangle_preflight", {}).get("status") != "CERTIFIED":
        errors.append("relative Einstein--Weyl linear triangle preflight was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_relative_functor_preflight", {}).get("status") != "BLOCKED":
        errors.append("relative functor preflight promoted before the off-shell triangle")
    if ledger.get("compact_einstein_maxwell_weyl_extra_branch_preflight", {}).get("status") != "CERTIFIED":
        errors.append("Weyl--Maxwell extra-branch preflight was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_axial_operator_module_preflight", {}).get("status") != "CERTIFIED":
        errors.append("Weyl--Maxwell axial operator-module preflight was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_axial_operator", {}).get("status") != "CERTIFIED":
        errors.append("Weyl--Maxwell generic axial operator theorem was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_polar_operator", {}).get("status") != "CERTIFIED":
        errors.append("Weyl--Maxwell generic polar operator theorem was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_polar_physical_completion", {}).get("status") != "CERTIFIED":
        errors.append("Weyl--Maxwell physical polar completion was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_polar_lee_wald_completion", {}).get("status") != "CERTIFIED":
        errors.append("Weyl--Maxwell generic polar direct Lee-Wald completion was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_polar_ungauged_noether_lift", {}).get("status") != "CERTIFIED":
        errors.append("Weyl--Maxwell generic polar ungauged Noether lift was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_plebanski_hacyan_stabilizer_descent", {}).get("status") != "CERTIFIED":
        errors.append("Weyl--Maxwell Plebanski--Hacyan stabilizer descent was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_moment_map_taub_bridge", {}).get("status") != "CERTIFIED":
        errors.append("Weyl--Maxwell moment-map/Taub bridge was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_balanced_mixed_second_order_extension", {}).get("status") != "CERTIFIED":
        errors.append("Weyl--Maxwell balanced mixed second-order extension was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_axial_extra_green_pairing", {}).get("status") != "CERTIFIED":
        errors.append("Weyl--Maxwell axial extra reduced-Green pairing was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_axial_lee_wald_completion", {}).get("status") != "CERTIFIED":
        errors.append("Weyl--Maxwell generic axial direct Lee-Wald completion was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_axial_extra_detector_taub", {}).get("status") != "CERTIFIED":
        errors.append("Weyl--Maxwell axial extra detector/Taub theorem was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_axial_quadratic_channel_preflight", {}).get("status") != "CERTIFIED":
        errors.append("Weyl--Maxwell axial quadratic-channel preflight was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_axial_ee_ell2_source", {}).get("status") != "CERTIFIED":
        errors.append("Weyl--Maxwell mixed EE axial ell=2 source theorem was dropped")
    if ledger.get("compact_einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub", {}).get("status") != "CERTIFIED":
        errors.append("Weyl--Maxwell Hermitian axial-polar ell=2 Taub theorem was dropped")
    paper_ix = data.get("publication_plan", {}).get("paper_IX", {})
    if paper_ix.get("status") != "WRITING_STARTED" or paper_ix.get("theorem_frozen") is not False:
        errors.append("Paper IX writing/freeze state drifted")
    claim_table = paper_ix.get("claim_table", {})
    if not (
        claim_table.get("path") == str(PAPER_IX_CLAIM_TABLE.relative_to(ROOT))
        and _sha256_bytes(_committed_bytes(claim_table.get("commit", ""), claim_table.get("path", "")))
        == claim_table.get("sha256")
    ):
        errors.append("Paper IX claim-table provenance drifted")
    return errors


def render_report(data: dict[str, Any]) -> str:
    team_rows = "\n".join(
        f"| {row['team_id']} | `{row['verdict']}` | {row['established']} | {row['next_gate']} |"
        for row in data["team_status"]
    )
    setting_rows = "\n".join(
        f"| {row['setting_id']} | `{row['generator_id']}` | `{row['phase_space_id']}` | {row['lifecycle_layer']} | `{row['status']}` | `{row['verdict'] if row['verdict'] is not None else 'OPEN'}` |"
        for row in data["setting_ledger"]
    )
    evidence_rows = "\n".join(
        f"- `{team}`: `{record['path']}` at `{record['commit']}`, SHA-256 `{record['sha256']}`"
        for team, record in data["team_inputs"].items()
    )
    contribution_rows = "\n".join(
        "| {team} | `{setting}` | `{generator}` | `{phase_space}` | `{status}` | `{verdict}` |".format(
            team=record["payload"]["team_id"],
            setting=record["payload"]["setting_id"],
            generator=record["payload"]["generator_id"],
            phase_space=record["payload"]["phase_space_id"],
            status=record["payload"]["claim_status"],
            verdict=(
                record["payload"]["verdict"]
                if record["payload"]["verdict"] is not None
                else "NO_VERDICT"
            ),
        )
        for record in data["team_contributions"]
    )
    return rf"""# Consolidated \(D\)-quotient programme status

## Interpretation

There is no universal yes/no verdict for \(D\).  The authoritative claim key is

```text
(generator, phase space, boundary conditions, lifecycle layer)
```

The compact result is sector-dependent: \(D\) is charged on the unrestricted
locally reduced linearized space, and it becomes gauge only after restriction
to the full Taub/moment-map zero fibre and the selected derived quotient.
The one-real-scalar exact-cylinder and complete standard stealth-clock routes
are obstructed. A distinct neutral two-field reference sector supplies a
scoped homogeneous `D_GAUGE` theorem but fails its positive-health audit. The
first healthy background candidate is now exact: a non-conformally-flat Berger
cylinder supports two standard-sign rotating conformal scalars with positive
quartic potential, dominant-energy stress, timelike phase, and full raw clock
incidence. Its fixed-coupling linearized charge gate is also closed: the lapse
constraint fixes \(\delta Q_R=0\), compact averaging excludes an inhomogeneous
escape, and the scoped verdict is `D_GAUGE`. The clock rows contract
support-locally and cyclically, the retained minimal `q1` is complete, and the
selected gauge fermion gives an exact support-local cyclic gauge-fixed
54-to-26 contraction. The complete `q2` has now been transferred exactly to a
retained 26-row operation with 54,236 canonical nonzero coefficients; its
arity-two and odd-Darboux cyclicity defects vanish. This retained operation is
not yet the minimal residual/cohomology `ell2`. The bare local unary D-Cartan
equation is independently obstructed by an exact characteristic-rank mismatch,
but the conditional causal transfer, rank-one wave prolongation, and cyclic
36-row analytic realization are now imported. Advanced/retarded Green
operators, causal support, retained endpoint transport, and any residual/BFV
promotion remain open. The Einstein-incidence audit separately classifies this
background as a non-Einstein Weyl--matter branch.

## Four-team ledger

| Team | Current verdict | Established | Next gate |
|---|---|---|---|
{team_rows}

## Setting ledger

| Setting | Generator | Phase space | Layer | Status | Verdict |
|---|---|---|---|---|---|
{setting_rows}

## Shared dependency gate

""" + "\n".join(
        f"{index}. {gate}" for index, gate in enumerate(data["dependency_gate"], 1)
    ) + f"""

## Registered scoped contributions

| Team | Setting | Generator | Phase space | Status | Verdict |
|---|---|---|---|---|---|
{contribution_rows}

## Publication decision

This remains a cross-programme validation dossier. Paper IX status is
`{data['publication_plan']['paper_IX']['status']}` and theorem freeze is
`{data['publication_plan']['paper_IX']['theorem_frozen']}`. Its freeze gate is:
{data['publication_plan']['paper_IX']['promotion_gate']}.
Paper X remains reserved for interaction/quantum stability after its separate
classical-export and QME gates.

The immediate shared calculation is
`{data['next_shared_gate']['gate_id']}`: {data['next_shared_gate']['rule']}

## Imported evidence

{evidence_rows}

## Claim boundary

{data['claim_boundary']}

## Verification

```bash
python3 d_quotient_programme/verify_programme_status.py --check --guards
```
"""


def _check_inputs_against_certificate(data: dict[str, Any]) -> None:
    for team, record in data["team_inputs"].items():
        relative = record["path"]
        if relative != TEAM_PATHS[team]:
            raise AssertionError(f"{team} input path drifted")
        if _sha256_bytes(_committed_bytes(record["commit"], relative)) != record["sha256"]:
            raise AssertionError(f"{team} committed evidence hash drifted")
    if _sha256(GENERATOR_REGISTRY) != data["registry_hashes"]["generator_registry"]:
        raise AssertionError("generator registry drifted")
    if _sha256(PHASE_REGISTRY) != data["registry_hashes"]["phase_space_registry"]:
        raise AssertionError("phase-space registry drifted")


def mutation_guards(data: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def reject(name: str, mutant: dict[str, Any]) -> None:
        if not validate(mutant):
            failures.append(name)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "compact_unrestricted")["verdict"] = "D_GAUGE"
    reject("erase_compact_charge", mutant)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "compact_scalar_clock")["verdict"] = "D_GAUGE"
    reject("erase_single_scalar_clock_obstruction", mutant)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "compact_neutral_clock_pair")["phase_space_id"] = "compact_scalar_clock"
    reject("erase_neutral_clock_scope", mutant)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "compact_neutral_clock_pair_local_health")["verdict"] = "D_GAUGE"
    reject("erase_neutral_clock_health_obstruction", mutant)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "compact_homogeneous_positive_stealth_clock")["verdict"] = "D_GAUGE"
    reject("erase_homogeneous_stealth_obstruction", mutant)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "compact_standard_conformal_stealth_clock")["verdict"] = "D_GAUGE"
    reject("erase_standard_stealth_no_go", mutant)

    mutant = deepcopy(data)
    berger = next(
        row
        for row in mutant["setting_ledger"]
        if row["setting_id"] == "compact_positive_berger_clock"
    )
    berger["status"] = "CERTIFIED"
    berger["verdict"] = "D_GAUGE"
    reject("promote_Berger_background_before_charge", mutant)

    mutant = deepcopy(data)
    charge_seed = next(
        row
        for row in mutant["setting_ledger"]
        if row["setting_id"] == "compact_positive_berger_clock_reduced_charge"
    )
    charge_seed["status"] = "CERTIFIED"
    charge_seed["verdict"] = "D_CHARGED"
    reject("promote_internal_clock_charge_to_total_D", mutant)

    mutant = deepcopy(data)
    berger_linearized = next(
        row
        for row in mutant["setting_ledger"]
        if row["setting_id"]
        == "compact_positive_berger_clock_fixed_coupling_linearized"
    )
    berger_linearized["verdict"] = "D_CHARGED"
    reject("erase_fixed_coupling_Berger_D_GAUGE", mutant)

    mutant = deepcopy(data)
    retained_layout = next(
        row
        for row in mutant["setting_ledger"]
        if row["setting_id"]
        == "compact_positive_berger_clock_retained_minimal_layout"
    )
    retained_layout["verdict"] = "RETAINED_MINIMAL_OPERATOR_COMPLETE"
    reject("promote_Berger_layout_to_operator", mutant)

    for setting_id, guard_name in (
        (
            "compact_positive_berger_clock_generator_conjugation",
            "drop_Berger_generator_conjugation_contribution",
        ),
        (
            "compact_positive_berger_clock_k_cartan_through_arity_three",
            "drop_Berger_k_cartan_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_relative_functor_preflight",
            "drop_classical_relative_functor_preflight_contribution",
        ),
    ):
        mutant = deepcopy(data)
        mutant["team_contributions"] = [
            record
            for record in mutant["team_contributions"]
            if record["payload"]["setting_id"] != setting_id
        ]
        reject(guard_name, mutant)

    mutant = deepcopy(data)
    relative_preflight = next(
        row
        for row in mutant["setting_ledger"]
        if row["setting_id"]
        == "compact_einstein_maxwell_weyl_relative_functor_preflight"
    )
    relative_preflight["status"] = "CERTIFIED"
    relative_preflight["verdict"] = "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1"
    reject("promote_relative_functor_before_offshell_triangle", mutant)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "compact_quantum")["verdict"] = "CARTAN_QUANTUM_EXACT"
    reject("promote_quantum_before_QME", mutant)

    mutant = deepcopy(data)
    next(
        record["payload"]
        for record in mutant["team_contributions"]
        if record["payload"]["setting_id"] == "vacuum_cylinder"
    )["claim_status"] = "CERTIFIED"
    reject("promote_quantum_contribution_before_QME", mutant)

    mutant = deepcopy(data)
    relative_quantum = next(
        row
        for row in mutant["setting_ledger"]
        if row["setting_id"]
        == "compact_einstein_maxwell_weyl_relative_quantum_readiness"
    )
    relative_quantum["status"] = "CERTIFIED"
    relative_quantum["verdict"] = "CARTAN_QUANTUM_EXACT"
    reject("promote_relative_quantum_before_triangle_and_QME", mutant)

    mutant = deepcopy(data)
    mutant["team_contributions"] = [
        record
        for record in mutant["team_contributions"]
        if record["payload"]["setting_id"]
        != "compact_einstein_maxwell_weyl_relative_quantum_readiness"
    ]
    reject("drop_relative_quantum_readiness_contribution", mutant)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "compact_selected_residual_HT1_q2")["verdict"] = "INTERACTING_CARTAN_EXISTS"
    reject("promote_selected_residual_to_full_cartan", mutant)

    mutant = deepcopy(data)
    retained_q2 = next(
        row
        for row in mutant["setting_ledger"]
        if row["setting_id"]
        == "compact_positive_berger_clock_retained_q2_26"
    )
    retained_q2["verdict"] = "INTERACTING_CARTAN_EXISTS"
    reject("promote_retained_q2_to_interacting_cartan", mutant)

    mutant = deepcopy(data)
    mutant["team_contributions"] = [
        record
        for record in mutant["team_contributions"]
        if record["payload"]["setting_id"]
        != "compact_positive_berger_clock_retained_q2_26"
    ]
    reject("drop_retained_q2_and_unary_no_go_contribution", mutant)

    mutant = deepcopy(data)
    next(row for row in mutant["setting_ledger"] if row["setting_id"] == "asymptotic_real_cylinder_time")["verdict"] = "D_GAUGE"
    reject("promote_asymptotic_generator_before_phase_space", mutant)

    mutant = deepcopy(data)
    next(
        row
        for row in mutant["setting_ledger"]
        if row["setting_id"]
        == "compact_positive_berger_clock_einstein_incidence"
    )["verdict"] = "EINSTEIN_TANGENT_EMBEDDED"
    reject("promote_Berger_nonincidence_to_tangent_embedding", mutant)

    mutant = deepcopy(data)
    mutant["team_contributions"] = [
        record
        for record in mutant["team_contributions"]
        if record["payload"]["setting_id"]
        != "compact_positive_berger_clock_einstein_incidence"
    ]
    reject("drop_Berger_Einstein_incidence_contribution", mutant)

    mutant = deepcopy(data)
    mutant["team_contributions"] = [
        record
        for record in mutant["team_contributions"]
        if record["payload"]["setting_id"]
        != "compact_einstein_maxwell_product_background"
    ]
    reject("drop_Einstein_Maxwell_product_contribution", mutant)

    mutant = deepcopy(data)
    mutant["team_contributions"] = [
        record
        for record in mutant["team_contributions"]
        if record["payload"]["setting_id"]
        != "compact_einstein_maxwell_product_tangent_preflight"
    ]
    reject("drop_Einstein_Maxwell_tangent_preflight_contribution", mutant)

    mutant = deepcopy(data)
    mutant["team_contributions"] = [
        record
        for record in mutant["team_contributions"]
        if record["payload"]["setting_id"]
        != "compact_einstein_maxwell_product_on_shell_tangent"
    ]
    reject("drop_Einstein_Maxwell_Chevreton_tangent_contribution", mutant)

    for setting_id, guard_name in (
        (
            "compact_einstein_maxwell_second_order_fixed_flux",
            "drop_Einstein_Maxwell_fixed_flux_second_order_contribution",
        ),
        (
            "universal_cover_einstein_maxwell_second_order_null_extension",
            "drop_Einstein_Maxwell_null_second_order_contribution",
        ),
        (
            "compact_einstein_maxwell_periodic_photon_second_order",
            "drop_Einstein_Maxwell_periodic_photon_second_order_contribution",
        ),
        (
            "compact_einstein_maxwell_periodic_graviton_second_order",
            "drop_Einstein_Maxwell_periodic_graviton_second_order_contribution",
        ),
        (
            "compact_einstein_maxwell_obstruction_bilinear_g1",
            "drop_Einstein_Maxwell_obstruction_bilinear_contribution",
        ),
        (
            "compact_einstein_maxwell_domain_taub_descent",
            "drop_Einstein_Maxwell_compact_domain_taub_contribution",
        ),
        (
            "compact_einstein_maxwell_harmonic_adjoint_block_preflight",
            "drop_Einstein_Maxwell_harmonic_adjoint_block_contribution",
        ),
        (
            "compact_einstein_maxwell_axial_master_complex",
            "drop_Einstein_Maxwell_axial_master_contribution",
        ),
        (
            "compact_einstein_maxwell_polar_master_preflight",
            "drop_Einstein_Maxwell_polar_master_preflight_contribution",
        ),
        (
            "compact_einstein_maxwell_polar_master_complex",
            "drop_Einstein_Maxwell_polar_master_contribution",
        ),
        (
            "compact_einstein_maxwell_polar_exceptional_complex",
            "drop_Einstein_Maxwell_polar_exceptional_contribution",
        ),
        (
            "compact_einstein_maxwell_radiative_symplectic_matching",
            "drop_Einstein_Maxwell_radiative_symplectic_contribution",
        ),
        (
            "compact_einstein_maxwell_exceptional_global_symplectic",
            "drop_Einstein_Maxwell_exceptional_global_symplectic_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_symplectic_preflight",
            "drop_Einstein_Maxwell_Weyl_symplectic_preflight_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_axial_ell2_restriction",
            "drop_Einstein_Maxwell_Weyl_axial_ell2_restriction_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_axial_all_ell_restriction",
            "drop_Einstein_Maxwell_Weyl_axial_all_ell_restriction_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_polar_all_ell_restriction",
            "drop_Einstein_Maxwell_Weyl_polar_all_ell_restriction_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_radiative_restriction",
            "drop_Einstein_Maxwell_Weyl_combined_radiative_restriction_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_ell1_physical_restriction",
            "drop_Einstein_Maxwell_Weyl_ell1_physical_restriction_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_standard_harmonic_inclusion",
            "drop_Einstein_Maxwell_Weyl_standard_harmonic_inclusion_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_relative_linear_triangle_preflight",
            "drop_Einstein_Weyl_relative_linear_triangle_preflight_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_extra_branch_preflight",
            "drop_Einstein_Maxwell_Weyl_extra_branch_preflight_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_axial_operator_module_preflight",
            "drop_Einstein_Maxwell_Weyl_axial_operator_module_preflight_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_axial_operator",
            "drop_Einstein_Maxwell_Weyl_axial_operator_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_polar_operator",
            "drop_Einstein_Maxwell_Weyl_polar_operator_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_polar_physical_completion",
            "drop_Einstein_Maxwell_Weyl_polar_physical_completion_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_polar_lee_wald_completion",
            "drop_Einstein_Maxwell_Weyl_polar_lee_wald_completion_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_polar_ungauged_noether_lift",
            "drop_Einstein_Maxwell_Weyl_polar_ungauged_noether_lift_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_plebanski_hacyan_stabilizer_descent",
            "drop_Einstein_Maxwell_Weyl_Plebanski_Hacyan_stabilizer_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_moment_map_taub_bridge",
            "drop_Einstein_Maxwell_Weyl_moment_map_Taub_bridge_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_balanced_mixed_second_order_extension",
            "drop_Einstein_Maxwell_Weyl_balanced_mixed_second_order_extension_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_axial_extra_green_pairing",
            "drop_Einstein_Maxwell_Weyl_axial_extra_green_pairing_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_axial_lee_wald_completion",
            "drop_Einstein_Maxwell_Weyl_axial_lee_wald_completion_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_axial_extra_detector_taub",
            "drop_Einstein_Maxwell_Weyl_axial_extra_detector_taub_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_axial_quadratic_channel_preflight",
            "drop_Einstein_Maxwell_Weyl_axial_quadratic_channel_preflight_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_axial_ee_ell2_source",
            "drop_Einstein_Maxwell_Weyl_axial_ee_ell2_source_contribution",
        ),
        (
            "compact_einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub",
            "drop_Einstein_Maxwell_Weyl_hermitian_axial_polar_ell2_taub_contribution",
        ),
    ):
        mutant = deepcopy(data)
        mutant["team_contributions"] = [
            record
            for record in mutant["team_contributions"]
            if record["payload"]["setting_id"] != setting_id
        ]
        reject(guard_name, mutant)

    mutant = deepcopy(data)
    mutant["publication_plan"]["paper_IX"]["theorem_frozen"] = True
    reject("freeze_paper_IX_before_signoff", mutant)

    mutant = deepcopy(data)
    mutant["claim_key"] = ["team_id"]
    reject("replace_sector_key_with_team_vote", mutant)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    if args.emit:
        data = build_certificate()
        errors = validate(data)
        if errors:
            raise AssertionError("; ".join(errors))
        CERTIFICATE.parent.mkdir(parents=True, exist_ok=True)
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        CERTIFICATE.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(render_report(data), encoding="utf-8")
        print("wrote", CERTIFICATE)
        print("wrote", REPORT)
        return 0

    data = _load(CERTIFICATE)
    errors = validate(data)
    if errors:
        raise AssertionError("; ".join(errors))
    _check_inputs_against_certificate(data)
    expected = build_certificate(data["programme_base_commit"])
    if data != expected:
        raise AssertionError("programme certificate does not match exact regeneration")
    if REPORT.read_text(encoding="utf-8") != render_report(data):
        raise AssertionError("consolidated report drifted")
    if args.guards:
        failures = mutation_guards(data)
        if failures:
            raise AssertionError("mutation guards failed: " + ", ".join(failures))
        print("mutation guards: PASS")
    print(CERTIFICATE, "PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
