#!/usr/bin/env python3
"""Generate the fail-closed classical causal/gauge/carrier atlas fragment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "classical-causal-atlas-fragment.json"
VACUUM_EVIDENCE = HERE / "CLASSICAL_VACUUM_CYLINDER_ATLAS_EVIDENCE_V1.json"
SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"
STATUSES = ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]
AXES = ["causal", "symplectic", "nonlinear", "observational", "quantum"]

LEGACY_VACUUM = {
    "four_flags": ROOT / "covariant_completion/certificates/four_flag_closure_status.json",
    "gram_transport": ROOT / "covariant_completion/certificates/covariant_gram_transport.json",
    "one_particle": ROOT / "analytic_completion/certificates/one_particle_krein.json",
    "positive_frequency": ROOT / "covariant_completion/certificates/positive_frequency_transform.json",
}
CERTS = {
    "vacuum": VACUUM_EVIDENCE,
    "Berger_green": ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json",
    "Berger_Cartan": ROOT / "d_quotient_classical/certificates/BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE.json",
    "Berger_charge": ROOT / "d_quotient_classical/certificates/BERGER_FIXED_COUPLING_DELTA_CHARGE.json",
    "Berger_redshift": ROOT / "d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json",
    "Berger_projector": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1.json",
    "Berger_bridge1_disposition": ROOT / "d_quotient_classical/certificates/BERGER_BRIDGE1_ADMISSIBLE_CARRIER_DISPOSITION_V1.json",
    "Nariai_conformal": ROOT / "d_quotient_classical/certificates/CONFORMAL_NARIAI_310_CAUSAL_TRANSFER_V1.json",
    "Nariai_single": ROOT / "d_quotient_classical/certificates/NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1.json",
    "Nariai_bridge_disposition": ROOT / "d_quotient_classical/certificates/NARIAI_CURVATURE_METRIC_BRIDGE_DISPOSITION_V1.json",
    "Nariai_transverse": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1.json",
    "Nariai_transverse_KS_obstruction": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_KANTOWSKI_SACHS_GLOBAL_OBSTRUCTION_V1.json",
    "Nariai_incidence": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1.json",
    "Nariai_PBW_gate": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PBW_CURVATURE_JET_GATE_V1.json",
    "Nariai_jet_aware_parent": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json",
    "Nariai_first_order_schur": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FIRST_ORDER_SCHUR_SOLVE_V1.json",
    "Nariai_Phi_only_obstruction": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1.json",
    "Nariai_incidence_L1_rigidity": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_INCIDENCE_L1_RIGIDITY_V1.json",
    "Nariai_normalized_L0_obstruction": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_NORMALIZED_L0_COUPLED_OBSTRUCTION_V1.json",
    "Nariai_K_admissibility": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_K_SENSITIVITY_ADMISSIBILITY_V1.json",
    "Nariai_Phi2_obstruction": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PHI_SECOND_ORDER_OBSTRUCTION_V1.json",
    "Nariai_PBW_associativity": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_PBW_ASSOCIATIVITY_GATE_V1.json",
    "Nariai_coefficient_jets": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_COEFFICIENT_JET_PBW_REQUIREMENTS_V1.json",
    "Nariai_splitting_jets": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS_V1.json",
    "Nariai_middle_replay": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_REPLAY_V1.json",
    "Nariai_factorized_schur": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1.json",
    "Nariai_upper_chain": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_RELATIVE_SADDLE_UPPER_CHAIN_V1.json",
    "Nariai_endpoint_target": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FACTORIZED_ENDPOINT_COMPLETION_V1.json",
    "Nariai_action_variation": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1.json",
    "Nariai_rank310_SDR_variation": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION_V1.json",
    "Nariai_formal_metric_green_variation": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION_V1.json",
    "Nariai_global_HPL_rank310_causal_variation": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_GLOBAL_HPL_RANK310_CAUSAL_VARIATION_V1.json",
    "Nariai_finite_HPL_incidence": ROOT / "d_quotient_classical/certificates/NARIAI_RANK310_FINITE_HPL_INCIDENCE_THEOREM_V1.json",
    "Nariai_KS_four_block_obstruction": ROOT / "d_quotient_classical/certificates/NARIAI_KS_FOUR_BLOCK_INCIDENCE_OBSTRUCTION_V1.json",
    "Nariai_six_block_HPL": ROOT / "d_quotient_classical/certificates/NARIAI_RANK310_SIX_BLOCK_FINITE_HPL_V1.json",
    "Nariai_KS_common_slab": ROOT / "d_quotient_classical/certificates/NARIAI_KS_COMMON_SLAB_CAUSAL_DOMAIN_V1.json",
    "Einstein_metric_biwave": ROOT / "d_quotient_classical/certificates/EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json",
    "Nariai_KS_rank310_transfer": ROOT / "d_quotient_classical/certificates/NARIAI_KS_RANK310_COMMON_SLAB_GREEN_TRANSFER_V1.json",
    "Bach_parent": ROOT / "d_quotient_classical/certificates/BACH_FLAT_PARENT_GREEN_STABILITY_V1.json",
    "Bach_rank310_SDR": ROOT / "d_quotient_classical/certificates/BACH_FLAT_RANK310_NATURAL_SDR_V1.json",
    "Bach_metric_biwave": ROOT / "d_quotient_classical/certificates/BACH_FLAT_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json",
    "Bach_rank310_causal": ROOT / "d_quotient_classical/certificates/BACH_FLAT_RANK310_CAUSAL_TRANSFER_V1.json",
    "candidate13_local_upgrade_obstruction": ROOT / "d_quotient_classical/certificates/CANDIDATE13_REDUCED_SOURCE_SUPPORT_LOCAL_UPGRADE_OBSTRUCTION_V1.json",
    "five_current_de_rham_carrier": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_CARRIER_V1.json",
    "five_current_de_rham_q2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_Q2_V1.json",
    "relative_238_cyclic_rank_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_238_ROW_CYCLIC_RANK_OBSTRUCTION_V1.json",
    "relative_316_cotangent_completion": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_316_ROW_COTANGENT_COMPLETION_V1.json",
    "relative_316_block_q2_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_316_BLOCK_DIAGONAL_Q2_OBSTRUCTION_V1.json",
    "relative_derived_taub_zero_pullback": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_DERIVED_TAUB_ZERO_PULLBACK_PREFLIGHT_V1.json",
    "relative_reduced_taub_factorization": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_REDUCED_TAUB_FACTORIZATION_V1.json",
    "relative_shifted_current_cone_preflight": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_SHIFTED_CURRENT_CONE_PREFLIGHT_V1.json",
    "relative_full_five_current_pbw": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FULL_FIVE_CURRENT_PBW_EXPORT_V1.json",
    "relative_order_zero_lift_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ZERO_LIFT_OBSTRUCTION_V1.json",
    "cone": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _legacy_id(path: Path) -> str:
    payload = json.loads(path.read_text())
    return str(payload.get("result_id", payload.get("schema", "UNIDENTIFIED")))


def vacuum_evidence() -> dict[str, Any]:
    records = {name: json.loads(path.read_text()) for name, path in LEGACY_VACUUM.items()}
    if not records["four_flags"]["flags"]["final_covariant_H4"]:
        raise AssertionError("vacuum covariant closure changed")
    if not records["gram_transport"]["status"]:
        raise AssertionError("vacuum Gram transport changed")
    if records["one_particle"]["classification"] != "infinite-index Krein space":
        raise AssertionError("vacuum one-particle carrier changed")
    if not (
        records["positive_frequency"]["harmonic_transform_isometry_on_algebraic_core"]
        and records["positive_frequency"]["normalized_metric_modes_map_to_unit_coefficients"]
        and records["positive_frequency"]["krein_signs"] == {"E": 1, "A": -1, "L": -1}
    ):
        raise AssertionError("vacuum positive-frequency transform changed")
    return {
        "schema": "classical-vacuum-cylinder-atlas-evidence-v1",
        "result_id": "CLASSICAL_VACUUM_CYLINDER_ATLAS_EVIDENCE_V1",
        "result_state": "VACUUM_CYLINDER_CAUSAL_SYMPLECTIC_AND_RESIDUAL_CARRIER_EVIDENCE_WRAPPED",
        "dependencies": {
            name: {"path": str(path.relative_to(ROOT)), "artifact_id": _legacy_id(path), "sha256": _sha(path)}
            for name, path in LEGACY_VACUUM.items()
        },
        "flags": {
            "causal_quasi_isomorphism": True,
            "EAL_Krein_carrier": True,
            "pairing_transport": True,
            "residual_H4_two_deformation_classes": True,
            "one_particle_residual_cohomology_zero": True,
            "Hadamard_or_interacting_quantum_theorem": False,
        },
        "claim_boundary": "This is a content-addressed adapter for legacy certificates that use schema identifiers instead of result_id. It adds no theorem and does not turn E/A/L modes or W-square deformation classes into quantum particles.",
    }


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


def _entry(identifier: str, scope: dict[str, Any], descriptions: dict[str, str], dispersion: tuple[str, str], lee_wald: tuple[str, str], taub: tuple[str, str], resonance: tuple[str, str], second: dict[str, Any], evidence: list[dict[str, str]], boundary: str) -> dict[str, Any]:
    return {
        "id": identifier,
        "scope": scope,
        "descriptions": descriptions,
        "mode_data": {
            "dispersion": _claim(*dispersion),
            "lee_wald": _claim(*lee_wald),
            "taub_maps": _claim(*taub),
            "resonance": _claim(*resonance),
            "second_order": second,
        },
        "evidence": evidence,
        "claim_boundary": boundary,
    }


VACUUM = {
    "theory": "free pure-Weyl gravity",
    "background": "unit conformal cylinder R_t x S3",
    "boundaries": "closed compact Cauchy surface S3; no spatial boundary",
    "charge_sector": "selected closed-universe absolute residual SO(4,2) quotient including D",
}
BERGER = {
    "theory": "pure-Weyl gravity plus two standard-sign rotating conformal scalars and retained Maxwell sector",
    "background": "fixed rational positive Berger clock",
    "boundaries": "R_t x compact Berger S3; no spatial boundary",
    "charge_sector": "fixed-coupling Taub/moment-map-zero clock sector; K_Berger=D-omega R is the stationary unary generator",
}
NARIAI = {
    "theory": "free pure-Weyl metric BV complex and normal-adjoint-tractor parent",
    "background": "unit Nariai dS2 x S2 and declared bounded smooth conformal orbit",
    "boundaries": "global compact Cauchy surface S1 x S2; no timelike boundary",
    "charge_sector": "unquotiented linear gauge complex; no residual state quotient imported",
}


def _scope(base: dict[str, Any], **updates: Any) -> dict[str, Any]:
    value = dict(base)
    value.update(updates)
    return value


def entries() -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    family_data = {
        "E": ("+1", "Einstein/lower-TT family, both chiralities"),
        "A": ("-1", "vector-descendant family, both chiralities"),
        "L": ("-1", "upper-TT/logarithmic family, both chiralities"),
    }
    for family, (sign, carrier) in family_data.items():
        values.append(_entry(
            f"classical.vacuum_cylinder.one_particle.{family.lower()}",
            _scope(VACUUM, carrier=carrier, degree=1, parity="both chiralities", ell="all allowed SO(4) levels", m="all", k="not a separate cylinder label", omega="positive and negative cylinder-energy shells"),
            {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
            ("CERTIFIED", f"The {family} all-level cylinder mode family is part of the exact E/A/L causal Cauchy carrier."),
            ("CERTIFIED", f"The normalized one-particle Krein sign is {sign} on {family}."),
            ("CERTIFIED", "The selected absolute residual CE complex has zero one-particle cohomology; this does not erase the causal solution family."),
            ("NOT_APPLICABLE", "No second-order resonance claim is needed for this linear carrier entry."),
            _second(("OPEN", "No all-mode bounded second-order classification."), ("OPEN", "No all-mode smooth-secular second-order classification."), ("OPEN", "No nonlinear retarded second-order classification.")),
            _evidence("vacuum", "cone"),
            "This is a classical causal one-particle mode family with an indefinite Krein sign, not a positive residual particle and not either W-square degree-four class.",
        ))
    for chirality in ("plus", "minus"):
        symbol = "+" if chirality == "plus" else "-"
        values.append(_entry(
            f"classical.vacuum_cylinder.deformation.w_{chirality}_squared",
            _scope(VACUUM, carrier=f"ghost-dressed degree-four deformation/vertex class [W_{symbol}^2], not a one-particle mode", degree=4, parity=f"chirality {symbol}", ell="NOT_APPLICABLE", m="NOT_APPLICABLE", k="NOT_APPLICABLE", omega="centered total residual weight zero"),
            {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
            ("NOT_APPLICABLE", "A composite deformation class has no one-particle dispersion relation."),
            ("CERTIFIED", "The complementary-degree residual pairing is positive definite and normalized to I2 on the two chiral classes."),
            ("CERTIFIED", "The covariant and residual H4 transports identify exactly these two classes."),
            ("NOT_APPLICABLE", "No propagation resonance is assigned to a deformation class."),
            _second(("NOT_APPLICABLE", "Not a first-order tangent mode."), ("NOT_APPLICABLE", "Not a first-order tangent mode."), ("NOT_APPLICABLE", "Not a first-order tangent mode.")),
            _evidence("vacuum"),
            "This is a vertex/deformation class. It must never be relabelled as a positive-norm graviton or one-particle state.",
        ))
    values.append(_entry(
        "classical.berger.retained_gravity_clock_maxwell",
        _scope(BERGER, carrier="complete 54-row gauge-fixed gravity-clock complex with typed retained 36-row gravity-clock-Maxwell carrier", degree="all BV degrees; physical local fields at degree 0", parity="all local tensor and Maxwell parities", ell="arbitrary four-dimensional jets; no harmonic truncation", m="all", k="all local covectors", omega="K_Berger weight; raw D action is affine"),
        {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "CERTIFIED", "quantum": "OPEN"},
        ("OPEN", "No complete Berger harmonic dispersion catalogue is asserted."),
        ("CERTIFIED", "The full and retained odd cyclic pairings and advanced/retarded adjoint reversal are exact."),
        ("CERTIFIED", "The clock momentum is nonzero but its variation vanishes on the declared fixed-coupling tangent; K_Berger, not raw affine D, is the stationary unary generator."),
        ("OPEN", "No complete Berger second-order resonance catalogue exists."),
        _second(("OPEN", "No finite-harmonic bounded Berger tangent cone."), ("OPEN", "No smooth-secular Berger tangent cone."), ("OPEN", "The unary retarded complex is certified, but the nonlinear causal second-order tangent cone is open.")),
        _evidence("Berger_green", "Berger_Cartan", "Berger_charge", "Berger_redshift", "cone"),
        "Causality is unary and the cyclic Cartan theorem stops at arity three. Raw affine D, arity four, Hadamard/QME, and a branch-resolved physical projector remain false.",
    ))
    values.append(_entry(
        "classical.berger.crosswalk.retained36_to_einstein_extra",
        _scope(BERGER, carrier="support-local Einstein-like/extra-Weyl dynamical branch projector on the retained 36-row carrier", degree="crosswalk", parity="all", ell="all", m="all", k="all", omega="all"),
        {axis: "NO_CERTIFIED_MAP" for axis in AXES},
        ("NO_CERTIFIED_MAP", "No support-local branch-resolved dispersion map exists on this carrier."),
        ("NO_CERTIFIED_MAP", "No branch-resolved pairing pullback exists."),
        ("NO_CERTIFIED_MAP", "No branch-resolved Taub map exists."),
        ("OBSTRUCTED", "The canonical support-local same-bundle projector is obstructed by the certified subprincipal witness."),
        _second(("NO_CERTIFIED_MAP", "No branch projector."), ("NO_CERTIFIED_MAP", "No branch projector."), ("NO_CERTIFIED_MAP", "No branch projector.")),
        _evidence("Berger_projector", "Berger_bridge1_disposition"),
        "Bridge 1 is not activated on Berger. The certified disposition selects the unsplit retained cyclic causal carrier as authoritative: the rank-36 projector and contractible rank-46 graph anchor are obstructed, while a relative cofiber, noncontractible mixed-bundle construction, and any all-mode REDUCED-MODE map remain open.",
    ))
    values.append(_entry(
        "classical.nariai.conformal_orbit.rank310_metric",
        _scope(NARIAI, background="bounded smooth global conformal orbit g_phi=exp(2phi)g_N with sup|exp(phi)-1|<1/9", carrier="metric four-row Bach complex and repaired rank-310 parent-detour graph", degree="all BV degrees", parity="all", ell="all smooth modes", m="all", k="all", omega="all"),
        {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("CERTIFIED", "The exact metric biwave endpoint and rank-310 graph carry advanced/retarded propagation on the declared class."),
        ("CERTIFIED", "The support-local SDR is cyclic and the causal homotopies satisfy adjoint reversal."),
        ("OPEN", "No nonlinear Taub/tangent-cone classification on the conformal orbit."),
        ("OPEN", "No nonlinear resonance classification."),
        _second(("OPEN", "No bounded nonlinear cone."), ("OPEN", "No smooth-secular nonlinear cone."), ("OPEN", "Unary causal homotopy is certified; nonlinear causal correction is open.")),
        _evidence("Nariai_conformal", "Nariai_single", "cone"),
        "This is the metric theorem on the conformal Nariai orbit only; transverse Bach-flat directions and Hadamard/nonlinear/quantum claims remain open.",
    ))
    values.append(_entry(
        "classical.nariai.crosswalk.normal_tractor_cylinder_to_metric",
        _scope(NARIAI, background="unit Nariai dS2 x S2", carrier="eight-block normal-tractor curvature-incidence cylinder -> four-row metric Bach complex", degree="crosswalk", parity="all", ell="all smooth modes", m="all", k="all", omega="all"),
        {axis: "NO_CERTIFIED_MAP" for axis in AXES},
        ("NO_CERTIFIED_MAP", "The normal-tractor cylinder and metric carriers have incompatible reducibility cohomology."),
        ("NO_CERTIFIED_MAP", "No pairing pullback is inferred across an obstructed quasi-isomorphism."),
        ("NOT_APPLICABLE", "No nonlinear Taub map is part of this unary carrier disposition."),
        ("OBSTRUCTED", "The H^-1 mismatch is at least 6-1=5 noncontractible reducibility directions."),
        _second(("NOT_APPLICABLE", "This is a unary crosswalk disposition."), ("NOT_APPLICABLE", "This is a unary crosswalk disposition."), ("NO_CERTIFIED_MAP", "The rejected cylinder does not transfer the metric Green homotopy.")),
        _evidence("Nariai_bridge_disposition"),
        "The direct normal-tractor cylinder-to-metric bridge is obstructed, but unit-Nariai causality is certified on the separate rank-310 curvature-corrected automorphism/parent-detour replacement. This row does not demote that replacement or promote a metric/parent bridge on every Bach-flat background.",
    ))
    values.append(_entry(
        "classical.bach_flat.open_parent_detour",
        _scope(NARIAI, background="every globally hyperbolic Bach-flat four-manifold; explicit relative ADM radius-1/4 ball around Nariai", carrier="normal-adjoint-tractor Yang-Mills detour parent, plus the natural rank-310 mapping cone and its four-row metric retract", degree="parent, rank-310 and metric complex degrees", parity="all", ell="NOT_APPLICABLE without additional symmetry", m="NOT_APPLICABLE", k="all local covectors", omega="all"),
        {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("CERTIFIED", "The parent detour, four-row metric Bach complex and all-row rank-310 mapping cone have advanced/retarded causal contractions on every background in the declared Bach-flat ADM class."),
        ("CERTIFIED", "The parent is cyclic under its tractor fibre pairing; the metric Volterra homotopy and cyclic rank-310 SDR give complementary-degree adjoint reversal and exact metric descent."),
        ("OPEN", "No class-wide nonlinear tangent cone."),
        ("NOT_APPLICABLE", "No finite harmonic resonance decomposition is assumed on the open parent class."),
        _second(("OPEN", "No bounded harmonic class is declared."), ("OPEN", "No smooth-secular class-wide theorem."), ("OPEN", "Unary parent Green homotopy does not by itself solve nonlinear sourced second order.")),
        _evidence("Bach_parent", "Bach_rank310_SDR", "Bach_metric_biwave", "Bach_rank310_causal", "cone"),
        "The metric endpoint closes without exact same-bundle factorization: the bare covariant companion gives scalar biwave leading symbol, the third-order covariant layer vanishes, and the remaining order-at-most-two operator is covered by the typed Volterra theorem. The natural cyclic SDR then lifts the metric homotopy to all 310 rows. The pure normal-tractor-parent-to-metric crosswalk remains fail-closed; the certified SDR has the curvature-corrected rank-310 cone, not the bare parent, as its source. Hadamard, nonlinear and quantum claims remain open.",
    ))
    values.append(_entry(
        "classical.nariai.transverse_kantowski_sachs_tangent",
        _scope(NARIAI, background="unit Nariai with transverse Kantowski-Sachs linearized Einstein tangent", carrier="complete ten-block rank-310 cyclic parent-detour graph through first variation", degree="all BV degrees along one background tangent", parity="homogeneous scalar anisotropy", ell=0, m=0, k=0, omega="nonstationary sinh(t), sinh(2t) profile"),
        {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("CERTIFIED", "The displayed tangent solves the complete linearized fixed-Lambda Einstein equations and is linearized Bach-flat."),
        ("CERTIFIED", "The cyclic HPL variation preserves inclusion/projection adjunction and the opposite-sided Green adjoint identity through formal first order; no standalone physical Lee-Wald norm is assigned to the tangent."),
        ("OPEN", "No second-order Taub classification or exact nonlinear family is certified."),
        ("CERTIFIED", "The global natural full-complex variation and normalized cyclic basic perturbation lemma give support-local rank-310 inclusion, projection and homotopy variations. For every finite differential retaining the certified four-block incidence, both HPL resolvents terminate after one correction and the full cyclic SDR identities hold coefficientwise in Q[epsilon]. The induced formal advanced/retarded chain contraction is exact through first order. No exact nonzero-epsilon geometric family is claimed."),
        _second(("OPEN", "No bounded correction theorem."), ("OPEN", "No smooth-secular correction theorem."), ("OPEN", "No transverse retarded SDR theorem.")),
        _evidence("Nariai_transverse", "Nariai_incidence", "Nariai_PBW_gate", "Nariai_jet_aware_parent", "Nariai_first_order_schur", "Nariai_Phi_only_obstruction", "Nariai_incidence_L1_rigidity", "Nariai_normalized_L0_obstruction", "Nariai_K_admissibility", "Nariai_Phi2_obstruction", "Nariai_PBW_associativity", "Nariai_coefficient_jets", "Nariai_splitting_jets", "Nariai_middle_replay", "Nariai_factorized_schur", "Nariai_upper_chain", "Nariai_endpoint_target", "Nariai_action_variation", "Nariai_rank310_SDR_variation", "Nariai_formal_metric_green_variation", "Nariai_global_HPL_rank310_causal_variation", "Nariai_finite_HPL_incidence", "cone"),
        "The replacement coefficient-jet algebra agrees with direct symbolic composition. Corrected HPL splittings close the first square; the associative replay closes the parent and shifted-chain identities; factorized adjunction before PBW normal ordering gives the exact cyclic Hom adjoint and compressed Schur; the upper relative-saddle chain closes; the endpoint solve has a unique 15-term algebraic cyclic completion; direct action-leading coefficients plus Noether uniqueness identify the full Bach-Hessian variation; and all twenty-one differentiated ten-block SDR identities vanish with no dropped row, including the explicit inclusion/projection adjunction. The global tangent is generated by a slabwise exact Einstein family. The normalized basic perturbation lemma globalizes the full SDR without treating the one-point Taylor table as a coefficient field, and the induced Duhamel formula gives an all-row same-sided formal causal contraction. The finite-incidence theorem removes any HPL convergence or nonlocal-denominator issue. This row remains the tangent theorem at epsilon=0; the separate exact-branch atlas row carries the nonzero-epsilon common-slab geometric and causal promotion, while the whole-cylinder nonzero family remains false.",
    ))
    values.append(_entry(
        "classical.nariai.transverse_kantowski_sachs_exact_branch",
        _scope(NARIAI, background="exact transverse Kantowski-Sachs Einstein branch through unit Nariai", boundaries="for every finite T, a certified small-parameter family on the open globally hyperbolic slab (-T,T) x S1 x S2 with one common wider causal cone; no whole-cylinder nonzero branch", carrier="complete ten-block rank-310 normal-tractor/BGG mapping cone and its four-row trace-free metric Bach retract", degree="all rank-310 and metric BV degrees on the slab; homogeneous background parameter at degree 0", parity="homogeneous scalar anisotropy background; all BV-complex parities", ell="all smooth complex modes; background tangent ell=0", m="all; background tangent m=0", k="all local covectors; background tangent k=0", omega="nonstationary exact Einstein evolution"),
        {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OBSTRUCTED", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("CERTIFIED", "On every common slab, the natural six-block rank-310 cyclic SDR transports the Einstein/partially-massless metric biwave homotopies to exact all-row advanced and retarded Green homotopies, with metric descent."),
        ("CERTIFIED", "The rank-310 SDR is cyclic and its all-row Green homotopies satisfy complementary-degree adjoint reversal; no global Lee-Wald phase space is assigned across the finite-time singular endpoint."),
        ("OPEN", "No second-order Taub classification beyond the exact homogeneous branch."),
        ("OBSTRUCTED", "The areal radius reaches zero with divergent Weyl curvature at finite proper time in one direction."),
        _second(("OBSTRUCTED", "The nonzero branch is not bounded or globally quasiperiodic on all R."), ("OBSTRUCTED", "The exact branch cannot remain smooth on the whole cylinder."), ("NO_CERTIFIED_MAP", "Slabwise evolution does not supply a whole-cylinder retarded causal bridge.")),
        _evidence("Nariai_transverse_KS_obstruction", "Nariai_KS_four_block_obstruction", "Nariai_six_block_HPL", "Nariai_KS_common_slab", "Einstein_metric_biwave", "Nariai_KS_rank310_transfer"),
        "The branch integrates the certified tangent on every fixed compact time slab but is globally singular for every nonzero 0<|epsilon|<1. In the declared fixed-coordinate tracefree transport, the finite conformal-Killing symbol first changes at order epsilon squared, so the four-block HPL theorem cannot be applied unchanged. The complete six-block operator algebra including k and ksharp has terminating HPL resolvents, an exact cyclic SDR, and two forced quadratic metric cross terms. The natural normal-BGG splittings, Yang--Mills detour middle, action Bach Hessian and their adjoints bind those six blocks on each common slab; the curved triangular graph transform includes the automorphism and first-splitting rows. Combining that support-local cyclic SDR with the complete four-row metric endpoint gives exact rank-310 advanced/retarded homotopies and metric descent. No component-expanded PBW dump is claimed or required. The nonzero family remains singular at finite time, so this is not a whole-cylinder theorem, a non-Einstein Bach-flat metric transfer, or a Hadamard/quantum result. This singularity is not a no-go for other non-Einstein Bach-flat deformations or alternative declared causal subdomains.",
    ))
    values.append(_entry(
        "classical.crosswalk.bach_flat_parent_to_metric",
        _scope(NARIAI, background="open Bach-flat parent class <-> metric Bach complexes away from the certified conformal Nariai orbit", carrier="support-local parent/metric SDR", degree="crosswalk", parity="all", ell="all", m="all", k="all", omega="all"),
        {axis: "NO_CERTIFIED_MAP" for axis in AXES},
        ("NO_CERTIFIED_MAP", "No class-wide metric endpoint crosswalk."),
        ("NO_CERTIFIED_MAP", "No class-wide metric current pullback."),
        ("NO_CERTIFIED_MAP", "No class-wide charge-sector crosswalk."),
        ("NO_CERTIFIED_MAP", "No class-wide mode/resonance crosswalk."),
        _second(("NO_CERTIFIED_MAP", "No metric crosswalk."), ("NO_CERTIFIED_MAP", "No metric crosswalk."), ("NO_CERTIFIED_MAP", "No metric crosswalk.")),
        _evidence("Bach_parent"),
        "The universal parent theorem must not be promoted to a metric theorem outside the certified conformal Nariai orbit.",
    ))
    values.append(_entry(
        "classical.crosswalk.candidate13_reduced_source_to_local_bv",
        _scope(NARIAI, theory="Einstein-Maxwell source relative to Weyl-Maxwell target", background="candidate-13 compact magnetic Plebanski-Hacyan product", boundaries="R_t x closed S1_L x S2 before final residual quotient", charge_sector="fixed magnetic U(1) bundle P_N with N=2", carrier="finite generic candidate-13 bounded/smooth derived-source receiver -> support-local equation-level BV cofiber", degree=2, parity="both axial and polar", ell="input ell=2; outputs L=0,...,4", m="all allowed m,M", k="signed n=1,-2 fibres and conjugates", omega="zero and eighteen selected finite-frequency receiver components"),
        {"causal": "NO_CERTIFIED_MAP", "symplectic": "NO_CERTIFIED_MAP", "nonlinear": "OBSTRUCTED", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("NO_CERTIFIED_MAP", "The declared Fourier/harmonic receiver and modewise inverses are not support-local causal operators."),
        ("NO_CERTIFIED_MAP", "The noncyclic three-form triangle does not supply one transported cyclic pairing on the reduced-source pullback."),
        ("OBSTRUCTED", "Direct promotion of the declared reduced receiver is blocked by an exact support-expansion witness."),
        ("CERTIFIED", "The bounded and smooth coefficientwise receivers remain exact REDUCED-MODE results."),
        _second(("CERTIFIED", "The bounded finite-quasiperiodic zero locus is exact in mode space."), ("CERTIFIED", "The smooth exponential-polynomial zero locus is exact in mode space."), ("NO_CERTIFIED_MAP", "No causal-retarded derived-source crosswalk is supplied.")),
        _evidence("candidate13_local_upgrade_obstruction"),
        "The obstruction applies to direct reuse of the declared global mode projectors and inverses. It does not rule out a new local equation-level cofiber or a larger noncontractible mixed-bundle carrier, and it does not demote the support-local unary relative triangle.",
    ))
    values.append(_entry(
        "classical.crosswalk.compact_product_five_current_de_rham_carrier",
        _scope(NARIAI, theory="Einstein-Maxwell source relative to Weyl-Maxwell target", background="compact magnetic Plebanski-Hacyan product, including candidate-13", boundaries="R_t x closed oriented S1_L x S2 with fixed N=2 magnetic bundle", charge_sector="H,P_x,J_1,J_2,J_3 simultaneous zero-charge derived sector", carrier="160-row shifted de Rham current resolution and cyclic cotangent completion", degree="-2,...,3 with ranks (5,25,50,50,25,5)", parity="odd cotangent pairing; both source parities", ell="not harmonic-reduced", m="not harmonic-reduced", k="not harmonic-reduced", omega="not harmonic-reduced"),
        {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("NO_CERTIFIED_MAP", "The support-local unary carrier is selected, but no Green homotopy has been constructed."),
        ("CERTIFIED", "The 160-row carrier has an exact odd pairing and Stokes-compatible unary differential."),
        ("CERTIFIED", "The action-derived current q2 and density-dual equation-field operation replay exactly on the 188-row physical-current interface; the full 238-row relative mapping-cofiber morphism remains open."),
        ("NOT_APPLICABLE", "This is an equation-level derived-source carrier, not an observable or particle map."),
        _second(("NOT_APPLICABLE", "No bounded-mode claim is made by the local de Rham carrier."), ("CERTIFIED", "For closed currents, dB=-j presents the five zero-charge conditions without projectors."), ("NO_CERTIFIED_MAP", "Causal Green data remain open.")),
        _evidence("five_current_de_rham_carrier", "five_current_de_rham_q2"),
        "The carrier resolves only the five stabilizer-current classes. Its q2 theorem covers the 14+14 Hessian interface and all 160 current-carrier rows, not every ghost, identity and antifield row of the 78-row relative mapping cofiber. It does not encode candidate-13's eighteen spectral resonance receivers, repair the relative f2, authorize arity three, or supply causal or quantum transport.",
    ))
    values.append(_entry(
        "classical.crosswalk.compact_product_relative_238_cyclic_completion",
        _scope(NARIAI, theory="Einstein-Maxwell source relative to Weyl-Maxwell target", background="compact magnetic Plebanski-Hacyan product", boundaries="support-local off-shell bundle complex before harmonic or causal reduction", charge_sector="H,P_x,J_1,J_2,J_3 simultaneous derived zero-charge sector", carrier="fixed direct sum of the 78-row relative mapping cofiber and 160-row five-current de Rham/cotangent carrier", degree="-2,...,3 with ranks (10,45,78,69,31,5)", parity="candidate nondegenerate BV odd pairing of degree one", ell="not harmonic-reduced", m="not harmonic-reduced", k="not harmonic-reduced", omega="not harmonic-reduced"),
        {"causal": "NO_CERTIFIED_MAP", "symplectic": "OBSTRUCTED", "nonlinear": "OBSTRUCTED", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("NO_CERTIFIED_MAP", "The fixed support-local carrier has no causal Green construction."),
        ("OBSTRUCTED", "Degree-one odd nondegeneracy would require equal ranks in degrees d and 1-d; the exact deficits are 5, 14 and 9."),
        ("OBSTRUCTED", "No coefficient or cross-incidence choice can make this fixed 238-row carrier a cyclic BV q1/q2 complex."),
        ("NOT_APPLICABLE", "This is a carrier-rank obstruction, not a harmonic resonance calculation."),
        _second(("NOT_APPLICABLE", "No reduced-mode tangent claim is made."), ("NOT_APPLICABLE", "No smooth-secular tangent claim is made."), ("NO_CERTIFIED_MAP", "No causal-retarded completion is supplied.")),
        _evidence("five_current_de_rham_carrier", "five_current_de_rham_q2", "relative_238_cyclic_rank_obstruction"),
        "The obstruction is only to a nondegenerate degree-one odd pairing on the fixed 238-row direct sum. An add-only repair needs at least 28 rows, with one rank-minimal profile adding 9 rows in degree 1, 14 in degree 2 and 5 in degree 3, but this is necessary rather than sufficient. Noncyclic or presymplectic 238-row complexes, regradings or quotients, and larger mixed-bundle cyclic carriers remain open; no causal or quantum conclusion follows.",
    ))
    values.append(_entry(
        "classical.crosswalk.compact_product_relative_316_cotangent_carrier",
        _scope(NARIAI, theory="Einstein-Maxwell source relative to Weyl-Maxwell target", background="compact magnetic Plebanski-Hacyan product", boundaries="support-local off-shell bundle complex before harmonic or causal reduction", charge_sector="H,P_x,J_1,J_2,J_3 simultaneous derived zero-charge sector", carrier="160-row current resolution direct-summed with T*[1] of the complete 78-row relative mapping cone", degree="-2,...,3 with ranks (10,51,97,97,51,10)", parity="canonical nondegenerate BV odd pairing of degree one", ell="not harmonic-reduced", m="not harmonic-reduced", k="not harmonic-reduced", omega="not harmonic-reduced"),
        {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OBSTRUCTED", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("NO_CERTIFIED_MAP", "The unary cotangent carrier has no advanced/retarded Green homotopy."),
        ("CERTIFIED", "The canonical cone/cotangent pairing is nondegenerate and q1-cyclic on all 316 rows."),
        ("OBSTRUCTED", "The block-diagonal full-domain q2 projects to the certified nonzero direct-f2 Taub obstruction."),
        ("NOT_APPLICABLE", "This is an off-shell carrier, not an observable or particle map."),
        _second(("NOT_APPLICABLE", "No reduced-mode tangent claim is made."), ("NOT_APPLICABLE", "No smooth-secular tangent claim is made."), ("NO_CERTIFIED_MAP", "No causal-retarded completion is supplied.")),
        _evidence("relative_238_cyclic_rank_obstruction", "relative_316_cotangent_completion", "relative_316_block_q2_obstruction"),
        "This carrier resolves the 238-row rank obstruction by adjoining the full 78-row odd cotangent of the relative cone, not by identifying unlike bundles at the 28-row rank lower bound. Its pairing is the canonical cone/cotangent pairing, not either standard action-derived form; the generic inertia obstruction is therefore retained rather than refuted. The cotangent adjoint is factorized and not PBW-expanded. Projection proves that a complete full-domain q2 is obstructed while the unary operator remains block diagonal. A genuine derived Taub-zero homotopy pullback, nonzero typed unary cross-incidence, modified endpoint or different background remains open; current comparison, causal and quantum claims are absent.",
    ))
    values.append(_entry(
        "classical.crosswalk.compact_product_derived_taub_zero_pullback",
        _scope(NARIAI, theory="Einstein-Maxwell source relative to Weyl-Maxwell target", background="compact magnetic Plebanski-Hacyan product", boundaries="support-local off-shell derived zero locus before harmonic or causal reduction", charge_sector="quadratic zero locus of the H,P_x,J_1,J_2,J_3 relative moment map", carrier="full unary tangent complex with 160-row local current resolution, 188-row q1/q2 interface and shifted 316-row cyclic candidate T*[1](Cone(iota) direct_sum K_P[1])", degree="unary tangent unchanged; first derived constraint at Taylor arity two; shifted candidate ranks (5,25,56,72,72,56,25,5) in degrees -3,...,4", parity="canonical current/cotangent parity, relative morphism pairing still open", ell="not harmonic-reduced", m="not harmonic-reduced", k="not harmonic-reduced", omega="not harmonic-reduced"),
        {"causal": "NO_CERTIFIED_MAP", "symplectic": "OPEN", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("NO_CERTIFIED_MAP", "No advanced/retarded homotopy has been constructed for the derived relative pullback."),
        ("OPEN", "The local current and unary cotangent pairings are certified separately, but their relative action-pairing comparison is not."),
        ("OPEN", "The relative obstruction class factors exactly through the five Taub charges in normalized smooth finite-harmonic quotient coordinates. The required support-local lift A:K_P->C_W and its shifted 316-row cyclic carrier are typed, and the complete current C_X is portable. The complete unrestricted order-zero top descent has only five Maxwell de Rham tails and cannot repair the strict f2=0 incidence; positive differential order and nonzero f2 remain open."),
        ("NOT_APPLICABLE", "This is an equation-level derived source, not an observable or particle identification."),
        _second(("OPEN", "The five-charge factorization does not include the extra polynomial and resonant obstruction functionals of the bounded category."), ("CERTIFIED", "On Sym^2 H0 of every finite real standard-mode set in the smooth-secular category, ker D equals ker M_pol and the normalized quotient-coordinate factor is I5."), ("NO_CERTIFIED_MAP", "No causal-retarded lift of the factorization is available.")),
        _evidence("five_current_de_rham_carrier", "five_current_de_rham_q2", "relative_316_cotangent_completion", "relative_316_block_q2_obstruction", "relative_derived_taub_zero_pullback", "relative_reduced_taub_factorization", "relative_shifted_current_cone_preflight", "relative_full_five_current_pbw", "relative_order_zero_lift_obstruction"),
        "The relative moment map has zero constant and linear terms, so the derived Taub-zero condition does not restrict the unary tangent complex and does not require a nonzero unary cross-incidence. Its first local equation is d_H B_X+j_X(u,u)/2=0 at arity two. In the finite-harmonic smooth-secular target quotient, the complete five-dimensional cokernel theorem makes the normalized evaluation map an isomorphism and gives D=A M_pol with quotient-coordinate matrix I5 on Sym^2 H0, including cross-block pairs. This is not a serialized all-mode PBW matrix or a support-local lift. The current-level lift is typed as a degree-zero chain map A:K_P->C_W. Because K_P[1] belongs inside the derived mapping cone before cotangent completion, its canonical cyclic candidate is a regraded 316-row carrier with degree profile (5,25,56,72,72,56,25,5), not the existing block-diagonal 316 profile. The complete C_X input is a profile-deduplicated portable table with 30,494 canonical terms, 60,890 ordered terms after symmetric expansion and 239 exact coefficient profiles, bound to all 14 source-field and 20 P3 rows; coefficient jets stop at order one. The complete unrestricted order-zero ansatz has 310 coefficients and a 480-equation rational top-descent system of rank 305. Its five-dimensional kernel consists only of Maxwell de Rham tails, so every metric output of A1 vanishes and a normalized fourth-order metric Delta2 term obstructs Delta2=A1 C with f2=0. This is scoped to order zero: positive-order lifts, nonzero f2 and alternate current improvements remain open. No repaired relative q2, action-pairing transport, causal bridge or quantum transfer is certified.",
    ))
    return values


def build() -> dict[str, Any]:
    value = {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "d_quotient_classical",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha(Path(__file__)),
        "status_vocabulary": STATUSES,
        "description_axes": AXES,
        "entries": entries(),
        "verification_commands": [
            "python3 -m d_quotient_classical.atlas.generate_classical_atlas_fragment --check",
            "python3 residual_atlas/validate_fragment.py d_quotient_classical/atlas/classical-causal-atlas-fragment.json",
            "python3 d_quotient_classical/atlas/verify_classical_atlas_fragment.py",
            "python3 -m unittest d_quotient_classical.atlas.tests.test_classical_atlas_fragment",
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
    wrapper = vacuum_evidence()
    if args.write:
        VACUUM_EVIDENCE.write_text(json.dumps(wrapper, indent=2, sort_keys=True) + "\n")
        OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    else:
        if json.loads(VACUUM_EVIDENCE.read_text()) != wrapper:
            raise AssertionError("vacuum evidence wrapper is stale")
        if json.loads(OUTPUT.read_text()) != build():
            raise AssertionError("classical atlas fragment is stale")
    print("CLASSICAL_CAUSAL_RESIDUAL_ATLAS_FRAGMENT_V1: PASS")


if __name__ == "__main__":
    main()
