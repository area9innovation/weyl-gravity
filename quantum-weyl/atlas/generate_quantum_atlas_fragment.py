#!/usr/bin/env python3
"""Generate the common-envelope quantum residual-atlas fragment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from analytic_completion.one_particle.krein import FAMILIES, FORM_SIGN
from bridge.metric_preimages.all_energy import BRANCH_MINIMUM


HERE = Path(__file__).resolve().parent
QROOT = HERE.parent
ROOT = QROOT.parent
OUTPUT = HERE / "quantum-atlas-fragment.json"
SCHEMA = HERE / "schema/quantum-residual-atlas-fragment-v1.schema.json"
COMMON_SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"
STATUSES = ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]
AXES = ["causal", "symplectic", "nonlinear", "observational", "quantum"]

DEPENDENCIES = {
    "polarized_state": ROOT / "field_bv_identification/polarized_state/certificates/polarized_state_complex.json",
    "one_particle_krein": ROOT / "analytic_completion/certificates/one_particle_krein.json",
    "positive_frequency_transform": ROOT / "covariant_completion/certificates/positive_frequency_transform.json",
    "curvature_CCR": QROOT / "lorentzian/certificates/CURVATURE_IMAGE_PRESYMPLECTIC_CCR_ALGEBRA.json",
    "Berger_causal_chain": QROOT / "lorentzian/certificates/BERGER_CAUSAL_CHAIN_V2_IMPORT.json",
    "Berger_Hadamard_gate": QROOT / "lorentzian/certificates/BERGER_HADAMARD_CONSTRUCTION_GATE.json",
    "Slavnov_preflight": QROOT / "anomalies/certificates/REGULATED_SLAVNOV_BREAKING_ASSEMBLY_PREFLIGHT.json",
    "Euclidean_elliptic_complex": QROOT / "spectral/euclidean/certificates/REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX.json",
    "nonconformal_coefficient_match": QROOT / "spectral/euclidean/certificates/REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH.json",
    "regulated_Slavnov_breaking": QROOT / "anomalies/certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json",
    "unitary_matter_no_go": QROOT / "anomalies/certificates/UNITARY_CONFORMAL_MATTER_CANCELLATION_NO_GO.json",
    "WZ_compensator_preflight": QROOT / "anomalies/certificates/WESS_ZUMINO_COMPENSATOR_EXTENSION_PREFLIGHT.json",
    "WZ_cotangent_lift": QROOT / "anomalies/certificates/WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json",
    "WZ_extended_local_BV": QROOT / "anomalies/certificates/WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY.json",
    "one_loop_Q1_disposition": QROOT / "transfer/certificates/ONE_LOOP_SLAVNOV_Q1_DISPOSITION.json",
    "anomaly_induced_Gamma1": QROOT / "transfer/certificates/ANOMALY_INDUCED_NONLOCAL_GAMMA1.json",
    "flat_TT_log_Gamma1": QROOT / "transfer/certificates/FLAT_TT_LOGARITHMIC_GAMMA1.json",
    "general_tangent_cone": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
    "finite_k0_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order.json",
    "smooth_secular_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order.json",
    "bounded_resonance_divisor": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_id(value: dict[str, Any]) -> str:
    identifier = value.get("result_id") or value.get("certificate_id") or value.get("schema")
    return str(identifier) if identifier is not None else "UNIDENTIFIED"


def _evidence(values: dict[str, dict[str, Any]], *names: str) -> list[dict[str, str]]:
    return [
        {
            "path": str(DEPENDENCIES[name].relative_to(ROOT)),
            "result_id": _artifact_id(values[name]),
            "sha256": _sha256(DEPENDENCIES[name]),
        }
        for name in names
    ]


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def _second_order(
    bounded: tuple[str, str],
    secular: tuple[str, str],
    causal: tuple[str, str],
) -> dict[str, Any]:
    return {
        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
        "bounded_or_finite_quasiperiodic": _claim(*bounded),
        "smooth_secular": _claim(*secular),
        "causal_retarded": _claim(*causal),
    }


def _quantum_data(
    entry_kind: str,
    tags: list[str],
    *,
    imported: tuple[str, str],
    cocycle: tuple[str, str],
    exactness: tuple[str, str],
    pairing: tuple[str, str],
    complex_structure: tuple[str, str],
    hadamard: tuple[str, str],
    state_space: tuple[str, str],
    qme: tuple[str, str],
    lifecycle: tuple[str, str],
    particle: tuple[str, str],
    crosswalk: tuple[str, str],
) -> dict[str, Any]:
    return {
        "entry_kind": entry_kind,
        "dependency_tags": tags,
        "classical_mode_imported": _claim(*imported),
        "BRST_cocycle": _claim(*cocycle),
        "BRST_exactness": _claim(*exactness),
        "pairing_status": _claim(*pairing),
        "compatible_complex_structure": _claim(*complex_structure),
        "Hadamard_two_point_function": _claim(*hadamard),
        "state_space_status": _claim(*state_space),
        "anomaly_QME_dependency": _claim(*qme),
        "lifecycle_state": _claim(*lifecycle),
        "particle_interpretation": _claim(*particle),
        "carrier_crosswalk": _claim(*crosswalk),
    }


def _entry(
    identifier: str,
    scope: dict[str, Any],
    descriptions: dict[str, str],
    mode_data: dict[str, Any],
    quantum_data: dict[str, Any],
    evidence: list[dict[str, str]],
    boundary: str,
) -> dict[str, Any]:
    return {
        "id": identifier,
        "scope": scope,
        "descriptions": descriptions,
        "mode_data": mode_data,
        "quantum_data": quantum_data,
        "evidence": evidence,
        "claim_boundary": boundary,
    }


def _validate_inputs(values: dict[str, dict[str, Any]]) -> None:
    polarized = values["polarized_state"]
    krein = values["one_particle_krein"]
    transform = values["positive_frequency_transform"]
    curvature = values["curvature_CCR"]
    causal = values["Berger_causal_chain"]
    hadamard = values["Berger_Hadamard_gate"]
    slavnov = values["Slavnov_preflight"]
    elliptic = values["Euclidean_elliptic_complex"]
    coefficient = values["nonconformal_coefficient_match"]
    breaking = values["regulated_Slavnov_breaking"]
    matter_no_go = values["unitary_matter_no_go"]
    wz_preflight = values["WZ_compensator_preflight"]
    wz_lift = values["WZ_cotangent_lift"]
    wz_extended = values["WZ_extended_local_BV"]
    q1_disposition = values["one_loop_Q1_disposition"]
    anomaly_induced = values["anomaly_induced_Gamma1"]
    flat_tt_log = values["flat_TT_log_Gamma1"]
    general = values["general_tangent_cone"]
    k0 = values["finite_k0_cone"]
    smooth = values["smooth_secular_cone"]
    resonance = values["bounded_resonance_divisor"]

    if (
        FAMILIES != ("E", "A", "L")
        or BRANCH_MINIMUM != {"E": 2, "A": 3, "L": 4}
        or FORM_SIGN != {"E": 1, "A": -1, "L": -1}
        or polarized.get("schema") != "pure-weyl-polarized-state-complex-v1"
        or "L_+ and L_- are complementary Lagrangian polarizations"
        not in polarized.get("proved", [])
        or krein.get("classification") != "infinite-index Krein space"
        or transform.get("krein_signs") != {"A": -1, "E": 1, "L": -1}
        or transform.get("normalized_metric_modes_map_to_unit_coefficients") is not True
    ):
        raise ValueError("vacuum-cylinder reduced mode input drifted")

    comparison = curvature.get("observable_comparison", {})
    if (
        comparison.get("final_covariant_H4") != ["W_+^2", "W_-^2"]
        or comparison.get("final_H4_Gram") != [[1, 0], [0, 1]]
        or curvature.get("claim_flags", {}).get("CURVATURE_HADAMARD_STATE_CONSTRUCTED")
        is not False
        or causal.get("claim_flags", {}).get("BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2_IMPORTED")
        is not True
        or causal.get("claim_flags", {}).get("BERGER_HADAMARD_DATA") is not False
        or hadamard.get("logical_separation", {}).get("complex_structure_or_covariance")
        != "NOT_CONSTRUCTED_ON_54_ROW_DISTRIBUTIONAL_COMPLEX"
        or hadamard.get("claim_flags", {}).get("BERGER_HADAMARD_DATA") is not False
    ):
        raise ValueError("covariant/ Berger import boundary drifted")

    if (
        slavnov.get("claim_flags", {}).get("REGULATED_SLAVNOV_BREAKING_COMPUTED")
        is not False
        or slavnov.get("claim_flags", {}).get("QME_RESTORED") is not False
        or slavnov.get("claim_flags", {}).get("QME_OBSTRUCTED") is not False
    ):
        raise ValueError("QME lifecycle boundary drifted")
    if (
        elliptic.get("claim_flags", {}).get(
            "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED"
        )
        is not True
        or coefficient.get("claim_flags", {}).get("REPOSITORY_C2_COEFFICIENT_COMPUTED")
        is not True
        or coefficient.get("coefficient_result", {}).get("coefficients", {}).get("C2")
        != {"numerator": 199, "denominator": 30}
        or breaking.get("classification", {}).get("status") != "NONTRIVIAL"
        or breaking.get("qme_disposition", {}).get("status")
        != "OBSTRUCTED_STRICT_FIELD_CONTENT"
        or matter_no_go.get("classification", {}).get("solution_set") != "EMPTY"
        or matter_no_go.get("classification", {}).get("qme_status")
        != "REMAINS_OBSTRUCTED_IN_DECLARED_MATTER_CLASS"
        or wz_preflight.get("result_state")
        != "AFN0_DIFF_COMPLETED_WZ_PRIMITIVE_CERTIFIED_FULL_EXTENDED_BV_OPEN"
        or wz_preflight.get("qme_lifecycle", {}).get(
            "extended_AFN0_one_loop_breaking"
        )
        != "EXACT_REMOVABLE"
        or wz_preflight.get("qme_lifecycle", {}).get("full_extended_BV_QME")
        != "NOT_CERTIFIED"
        or wz_lift.get("contractible_quartet", {}).get("status")
        != "EXACT_CONTRACTIBLE_WEYL_QUARTET_IN_DRESSED_VARIABLES"
        or wz_extended.get("H14", {}).get("even_quotient_dimension") != 0
        or wz_extended.get("H14", {}).get("odd_quotient_dimension") != 0
        or wz_extended.get("one_loop_QME", {}).get("status")
        != "QME_RESTORED_AT_ONE_LOOP_LOCAL_EUCLIDEAN_TAU_ADIC_EXTENDED_THEORY"
        or wz_extended.get("lifecycle", {}).get("residual_transfer")
        != "FORBIDDEN_EXTENDED_CLASSICAL_CONTRACTION_NOT_SUPPLIED"
        or q1_disposition.get("finite_counterterm_ambiguity", {}).get(
            "bulk_response_rank"
        )
        != 2
        or q1_disposition.get("decision", {}).get("complete_Q1")
        != "NO_CERTIFIED_OPERATOR"
        or q1_disposition.get("decision", {}).get("residual_transfer")
        != "FORBIDDEN"
        or anomaly_induced.get("claim_flags", {}).get(
            "ANOMALY_INDUCED_REPRESENTATIVE_SUPPLIED"
        )
        is not True
        or anomaly_induced.get("decision", {}).get("complete_finite_nonlocal_Gamma1")
        != "NO_CERTIFIED_FUNCTIONAL"
        or flat_tt_log.get("exact_logarithmic_form_factor", {}).get(
            "logarithmic_coefficient"
        )
        != {"numerator": -199, "denominator": 60}
        or flat_tt_log.get("claim_flags", {}).get("FLAT_TT_LOG_COEFFICIENT_FIXED")
        is not True
        or flat_tt_log.get("claim_flags", {}).get("FINITE_C2_NORMALIZATION_FIXED")
        is not False
        or flat_tt_log.get("decision", {}).get("complete_Q1")
        != "NO_CERTIFIED_OPERATOR"
    ):
        raise ValueError("coefficient-bearing QME disposition drifted")

    if (
        general.get("result_state")
        != "ABSTRACT_CORRECTION_CLASS_SENSITIVE_TANGENT_CONE_THEOREM_CERTIFIED"
        or general.get("theorem", {}).get("formula")
        != "Z_2^C={u in ker(q1): mu_X(u)=0 and R_j^C(u)=0 for every output block j}"
        or set(general.get("correction_classes", {}))
        != {"BOUNDED_OR_FINITE_QUASIPERIODIC", "SMOOTH_SECULAR", "CAUSAL_RETARDED"}
        or any(row.get("status") != "CERTIFIED" for row in general["correction_classes"].values())
        or general.get("flags", {}).get("BACKGROUND_SPECIFIC_TANGENT_CONE_CLASSIFICATION")
        is not False
        or k0.get("classification", {}).get(
            "complete_common_stabilizer_zero_cone_second_order_extendible"
        )
        is not True
        or smooth.get("classification", {}).get(
            "complete_fixed_ell_absolute_k_common_zero_cone_second_order_extendible"
        )
        is not True
        or resonance.get("classification", {}).get(
            "bounded_or_finite_quasiperiodic_extension_follows_from_moment_maps_alone"
        )
        is not False
    ):
        raise ValueError("finite-harmonic correction-class input drifted")


def _mode_entries(values: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    evidence = _evidence(
        values,
        "polarized_state",
        "one_particle_krein",
        "positive_frequency_transform",
        "Slavnov_preflight",
    )
    for chirality in (1, -1):
        for family in FAMILIES:
            minimum = BRANCH_MINIMUM[family]
            sign = FORM_SIGN[family]
            rows.append(
                _entry(
                    f"quantum.cylinder.mode_family.{family.lower()}.chirality_{'plus' if chirality > 0 else 'minus'}",
                    {
                        "theory": "free pure-Weyl BV-BFV gravity",
                        "background": "vacuum conformal cylinder R x S3",
                        "boundaries": "compact S3 Cauchy surface; selected positive-frequency boundary polarization",
                        "charge_sector": "ghost-number-zero one-particle reduced cylinder sector",
                        "carrier": f"normalized {family} energy-tower oscillator in chirality {chirality:+d}",
                        "degree": 0,
                        "parity": f"chirality {chirality:+d}; parity exchanges the opposite-chirality partner",
                        "ell": "NO_CERTIFIED_MAP: SO(4) irrep labels are not crosswalked to ell",
                        "m": "NO_CERTIFIED_MAP: magnetic index M is not crosswalked to one m convention",
                        "k": "NOT_APPLICABLE on S3",
                        "omega": f"positive cylinder energy n with n>={minimum}",
                    },
                    {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "OBSTRUCTED"},
                    {
                        "dispersion": _claim("CERTIFIED", f"positive cylinder energy n>={minimum}"),
                        "lee_wald": _claim("CERTIFIED", f"reduced Krein sign {sign:+d}"),
                        "taub_maps": _claim("NOT_APPLICABLE", "no second-order tangent-cone restriction is claimed for this all-energy family row"),
                        "resonance": _claim("OPEN", "no same-background full-BV stationary/Hadamard spectral theorem"),
                        "second_order": _second_order(
                            ("OPEN", "not classified for this mode family"),
                            ("OPEN", "not classified for this mode family"),
                            ("NO_CERTIFIED_MAP", "no same-background causal tangent-cone crosswalk"),
                        ),
                    },
                    _quantum_data(
                        "MODE_FAMILY",
                        ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
                        imported=("CERTIFIED", "YES: selected reduced E/A/L oscillator"),
                        cocycle=("CERTIFIED", "survives the selected polarized classical BRST retraction"),
                        exactness=("CERTIFIED", "nonexact in the selected reduced complex"),
                        pairing=("CERTIFIED", f"Krein sign {sign:+d}"),
                        complex_structure=("OPEN", "reduced positive-frequency polarization only"),
                        hadamard=("OPEN", "no same-background full-BV distributional kernel"),
                        state_space=("CERTIFIED", "infinite-index Krein reduced mode; not physical positivity"),
                        qme=("OBSTRUCTED", "strict fixed-field-content local Euclidean QME is obstructed at one loop"),
                        lifecycle=("OBSTRUCTED", "classical reduced carrier remains; strict interacting quantum lifecycle is blocked"),
                        particle=("NO_CERTIFIED_MAP", "no Lorentzian particle interpretation"),
                        crosswalk=("CERTIFIED", "real phase-space mode to selected positive-frequency oscillator"),
                    ),
                    evidence + _evidence(values, "regulated_Slavnov_breaking"),
                    "This is a REDUCED-MODE classical state carrier. It is not a same-background covariant Hadamard state, physical positivity theorem, or Lorentzian particle entry.",
                )
            )
    return rows


def _residual_entries(values: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    evidence = _evidence(values, "curvature_CCR", "Slavnov_preflight", "regulated_Slavnov_breaking")
    for class_id, chirality in (("W_+^2", "+"), ("W_-^2", "-")):
        partner = "W_-^2" if chirality == "+" else "W_+^2"
        rows.append(
            _entry(
                f"quantum.cylinder.residual_deformation.{class_id.lower().replace('^', '_').replace('+', 'plus').replace('-', 'minus')}",
                {
                    "theory": "free pure-Weyl BV observable cohomology",
                    "background": "vacuum conformal cylinder R x S3",
                    "boundaries": "closed cylinder with all fifteen residual conformal generators gauged",
                    "charge_sector": "centered residual cohomology H4 at delta=0",
                    "carrier": class_id,
                    "degree": 4,
                    "parity": f"chiral {chirality}; parity partner is {partner}",
                    "ell": "NOT_APPLICABLE: two-particle ghost-dressed deformation class",
                    "m": "NOT_APPLICABLE: two-particle ghost-dressed deformation class",
                    "k": "NOT_APPLICABLE",
                    "omega": "NOT_APPLICABLE: not a one-particle frequency",
                },
                {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OBSTRUCTED"},
                {
                    "dispersion": _claim("NOT_APPLICABLE", "deformation class, not a one-particle shell"),
                    "lee_wald": _claim("CERTIFIED", "unit diagonal Gram entry in the final covariant H4 basis"),
                    "taub_maps": _claim("NOT_APPLICABLE", "not a first-order tangent mode"),
                    "resonance": _claim("NOT_APPLICABLE", "not a one-particle shell"),
                    "second_order": _second_order(
                        ("NOT_APPLICABLE", "not a tangent mode"),
                        ("NOT_APPLICABLE", "not a tangent mode"),
                        ("NOT_APPLICABLE", "not a tangent mode"),
                    ),
                },
                _quantum_data(
                    "NONPARTICLE_RESIDUAL_CLASS",
                    ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
                    imported=("CERTIFIED", "YES: non-particle residual class"),
                    cocycle=("CERTIFIED", "closed class in final covariant H4"),
                    exactness=("CERTIFIED", "nonexact H4 class"),
                    pairing=("CERTIFIED", "unit diagonal Gram entry"),
                    complex_structure=("NOT_APPLICABLE", "not a one-particle carrier"),
                    hadamard=("NOT_APPLICABLE", "not a one-particle carrier"),
                    state_space=("NOT_APPLICABLE", "deformation/vertex class"),
                    qme=("OBSTRUCTED", "strict fixed-field-content local Euclidean QME fails before H3-H4-H5 transfer"),
                    lifecycle=("OBSTRUCTED", "classical deformation class remains certified; strict quantum survival is not defined"),
                    particle=("CERTIFIED", "NOT_A_PARTICLE"),
                    crosswalk=("CERTIFIED", "curvature graph image to final free BV cohomology"),
                ),
                evidence,
                "This is a deformation/vertex class, not a one-particle generator or particle Hilbert-space basis. Its free cohomology and Gram entry do not decide quantum survival.",
            )
        )
    return rows


def _berger_gap(values: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return _entry(
        "quantum.berger.carrier_gap.retained_26_stationary_modes",
        {
            "theory": "pure-Weyl gravity plus positive scalar clock at fixed coupling",
            "background": "compact positive Berger clock",
            "boundaries": "R x S3 with compact Cauchy surfaces",
            "charge_sector": "retained 26-row classical BV carrier",
            "carrier": "causal 26-row complex; stationary spectral mode basis not supplied",
            "degree": "all retained BV degrees",
            "parity": "NO_CERTIFIED_MAP",
            "ell": "NO_CERTIFIED_MAP",
            "m": "NO_CERTIFIED_MAP",
            "k": "NO_CERTIFIED_MAP",
            "omega": "NO_CERTIFIED_MAP: generalized-zero and nonzero spectrum not imported",
        },
        {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "OBSTRUCTED"},
        {
            "dispersion": _claim("NO_CERTIFIED_MAP", "no stationary physical mode basis"),
            "lee_wald": _claim("NO_CERTIFIED_MAP", "carrier pairing exists but has no modewise restriction"),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "no per-mode tangent-cone ledger"),
            "resonance": _claim("NO_CERTIFIED_MAP", "generalized zero and nonzero stationary spectrum not imported"),
            "second_order": _second_order(
                ("OPEN", "Berger finite-harmonic cone not classified"),
                ("OPEN", "Berger finite-harmonic cone not classified"),
                ("OPEN", "Berger causal carrier exists but its nonlinear tangent cone is not classified"),
            ),
        },
        _quantum_data(
            "CARRIER_IMPORT_GAP",
            ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
            imported=("NO_CERTIFIED_MAP", "NO: causal carrier imported, no stationary mode crosswalk"),
            cocycle=("NO_CERTIFIED_MAP", "no per-mode cohomology ledger"),
            exactness=("NO_CERTIFIED_MAP", "no per-mode cohomology ledger"),
            pairing=("NO_CERTIFIED_MAP", "carrier pairing has no modewise restriction"),
            complex_structure=("OPEN", "not constructed on the 54-row distributional complex"),
            hadamard=("OPEN", "not constructed"),
            state_space=("OPEN", "reduced Krein evidence does not define a Berger physical state space"),
            qme=("OBSTRUCTED", "strict fixed-field-content local Euclidean QME is obstructed"),
            lifecycle=("OBSTRUCTED", "classical causal import remains; strict interacting quantum lifecycle is blocked"),
            particle=("NO_CERTIFIED_MAP", "no mode basis or Hadamard state"),
            crosswalk=("NO_CERTIFIED_MAP", "retained 26 rows to stationary physical modes"),
        ),
        _evidence(values, "Berger_causal_chain", "Berger_Hadamard_gate", "Slavnov_preflight", "regulated_Slavnov_breaking"),
        "The 26/54-row causal carrier is imported, but it is not a stationary mode ledger. No physical mode, complex structure, Hadamard state, or particle is inferred.",
    )


def _tangent_crosswalk(values: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return _entry(
        "quantum.crosswalk.classical_tangent_cone_to_interacting_brst",
        {
            "theory": "classical finite-harmonic second-order theory to renormalized BV quantum theory",
            "background": "crosswalk only; every background requires its own certified carrier",
            "boundaries": "correction-class dependent",
            "charge_sector": "declared stabilizer moment-map zero sector",
            "carrier": "Z2^C classical tangent cone to a quantum BRST insertion",
            "degree": 2,
            "parity": "all declared finite-harmonic sectors",
            "ell": "finite declared block set",
            "m": "finite declared block set",
            "k": "finite declared block set",
            "omega": "bounded/quasiperiodic, smooth-secular, or causal/retarded",
        },
        {"causal": "NO_CERTIFIED_MAP", "symplectic": "NO_CERTIFIED_MAP", "nonlinear": "CERTIFIED", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
        {
            "dispersion": _claim("NOT_APPLICABLE", "abstract finite-block image/cokernel criterion"),
            "lee_wald": _claim("NO_CERTIFIED_MAP", "no universal quantum pairing follows from the classical criterion"),
            "taub_maps": _claim("CERTIFIED", "Z2^C={u: mu_X(u)=0 and R_j^C(u)=0}"),
            "resonance": _claim("CERTIFIED", "R_j^C depends on the correction class fixed before the cokernel"),
            "second_order": _second_order(
                ("OBSTRUCTED", "abstract criterion certified; opposite-momentum moment-map-only fixture fails on a nonempty resonance divisor"),
                ("CERTIFIED", "abstract criterion and fixed-(ell,|k|) smooth-secular fixture certified in declared scope"),
                ("NO_CERTIFIED_MAP", "abstract compatible-source retarded criterion certified, but no background-specific Green theorem is imported"),
            ),
        },
        _quantum_data(
            "CLASSICAL_TO_QUANTUM_CROSSWALK",
            ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            imported=("CERTIFIED", "abstract classical correction-class theorem imported by content hash"),
            cocycle=("NO_CERTIFIED_MAP", "no quantum BRST insertion constructed"),
            exactness=("NO_CERTIFIED_MAP", "no primitive or nonmembership witness constructed"),
            pairing=("NO_CERTIFIED_MAP", "no coefficient-bearing quantum pairing"),
            complex_structure=("NOT_APPLICABLE", "classical second-order solvability crosswalk"),
            hadamard=("NO_CERTIFIED_MAP", "no background-specific causal quantum state"),
            state_space=("NO_CERTIFIED_MAP", "no interacting quantum state space"),
            qme=("CERTIFIED", "strict one-loop local Euclidean QME is obstructed and the tau-adic compensator-extended one-loop local Euclidean QME is restored; one conditional anomaly-induced Euclidean Gamma1 representative and the flat-TT universal logarithmic coefficient -199/60 are fixed, but the curved remainder, finite constants and complete Q1 are underdetermined"),
            lifecycle=("NO_CERTIFIED_MAP", "QME disposition, an anomaly-induced Euclidean Gamma1 representative and the flat-TT universal logarithmic momentum dependence are complete in scope, but curved completion, finite constants, complete Q1, Bridge 2, and an extended same-background classical carrier map are absent"),
            particle=("NO_CERTIFIED_MAP", "classical obstruction is not ghost removal"),
            crosswalk=("NO_CERTIFIED_MAP", "classical obstruction to interacting BRST disappearance or quantum constraint"),
        ),
        _evidence(values, "general_tangent_cone", "finite_k0_cone", "smooth_secular_cone", "bounded_resonance_divisor", "Slavnov_preflight", "regulated_Slavnov_breaking", "WZ_compensator_preflight", "WZ_cotangent_lift", "WZ_extended_local_BV", "one_loop_Q1_disposition", "anomaly_induced_Gamma1", "flat_TT_log_Gamma1"),
        "Classical second-order obstruction does not imply BRST disappearance, a loop interaction, a quantum constraint, BRST exactness, or ghost removal. The coefficient-bearing QME disposition is complete—strict obstructed, tau-adic compensator extension restored locally at one Euclidean loop—and one conditional anomaly-induced Paneitz/Riegert Gamma1 representative is fixed. The nonzero-momentum flat-TT logarithmic coefficient -199/60 and its scheme-independent momentum difference are also fixed. Curved completion, finite C2/R2 normalization, global Green data and complete Q1 remain open. Bridge 2 and a same-background extended classical carrier map are absent, so no interacting-BRST insertion crosswalk is certified.",
    )


def _guard_entries(values: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    specs = [
        ("local_anomaly_class", "local ghost-number-one anomaly class such as omega C2 or omega E4", ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], ("Slavnov_preflight", "regulated_Slavnov_breaking", "unitary_matter_no_go", "WZ_compensator_preflight", "WZ_cotangent_lift", "WZ_extended_local_BV", "one_loop_Q1_disposition", "anomaly_induced_Gamma1", "flat_TT_log_Gamma1")),
        ("euclidean_determinant_factor", "round-S4 TT or ghost determinant factor", ["EUCLIDEAN-SPECTRAL"], ("Slavnov_preflight", "Euclidean_elliptic_complex", "nonconformal_coefficient_match")),
        ("flat_tt_log_form_factor", "nonzero-momentum flat-TT logarithmic effective-action form factor", ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"], ("regulated_Slavnov_breaking", "one_loop_Q1_disposition", "flat_TT_log_Gamma1")),
        ("curvature_observable_generator", "support-local curvature-graph CCR generator", ["LORENTZIAN-CAUSAL"], ("curvature_CCR",)),
    ]
    rows = []
    for key, carrier, tags, evidence_names in specs:
        rows.append(
            _entry(
                f"quantum.crosswalk.{key}_to_particle",
                {
                    "theory": "pure-Weyl quantum programme",
                    "background": "carrier-specific; no cross-background identification",
                    "boundaries": "carrier-specific",
                    "charge_sector": "not a certified physical one-particle sector",
                    "carrier": carrier,
                    "degree": "carrier-specific",
                    "parity": "carrier-specific",
                    "ell": "NO_CERTIFIED_MAP",
                    "m": "NO_CERTIFIED_MAP",
                    "k": "NO_CERTIFIED_MAP",
                    "omega": "NO_CERTIFIED_MAP",
                },
                {axis: "NO_CERTIFIED_MAP" for axis in AXES},
                {
                    "dispersion": _claim("NO_CERTIFIED_MAP", "not a physical residual mode shell"),
                    "lee_wald": _claim("NO_CERTIFIED_MAP", "no particle pairing crosswalk"),
                    "taub_maps": _claim("NOT_APPLICABLE", "non-mode carrier guard"),
                    "resonance": _claim("NOT_APPLICABLE", "non-mode carrier guard"),
                    "second_order": _second_order(
                        ("NOT_APPLICABLE", "non-mode carrier guard"),
                        ("NOT_APPLICABLE", "non-mode carrier guard"),
                        ("NOT_APPLICABLE", "non-mode carrier guard"),
                    ),
                },
                _quantum_data(
                    "NON_MODE_PARTICLE_GUARD",
                    tags,
                    imported=("CERTIFIED", "carrier imported only in its declared non-particle role"),
                    cocycle=("NOT_APPLICABLE", "carrier-specific; no physical residual mode imported"),
                    exactness=("NOT_APPLICABLE", "carrier-specific; no physical residual mode imported"),
                    pairing=("NO_CERTIFIED_MAP", "no particle pairing crosswalk"),
                    complex_structure=("NO_CERTIFIED_MAP", "no particle complex structure crosswalk"),
                    hadamard=("NO_CERTIFIED_MAP", "no particle Hadamard crosswalk"),
                    state_space=("NO_CERTIFIED_MAP", "no particle state-space crosswalk"),
                    qme=(("CERTIFIED", "strict local Euclidean QME is obstructed; the tau-adic compensator-extended local Euclidean QME is restored at one loop, and this carrier's coefficient is bound to that disposition") if key in {"local_anomaly_class", "flat_tt_log_form_factor"} else ("OPEN", "carrier retains its own anomaly/QME dependency")),
                    lifecycle=("NO_CERTIFIED_MAP", "not a particle lifecycle entry"),
                    particle=("NO_CERTIFIED_MAP", "forbidden without an explicit physical residual-mode crosswalk"),
                    crosswalk=("NO_CERTIFIED_MAP", "non-mode carrier to particle"),
                ),
                _evidence(values, *evidence_names),
                "This carrier remains valid in its local, spectral, or observable-algebra role, but no certified map turns it into a particle entry.",
            )
        )
    return rows


def entries(values: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return (
        _mode_entries(values)
        + _residual_entries(values)
        + [_berger_gap(values), _tangent_crosswalk(values)]
        + _guard_entries(values)
    )


def validate_fragment(value: dict[str, Any]) -> None:
    for schema_path in (SCHEMA, COMMON_SCHEMA):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
    ids = [entry["id"] for entry in value["entries"]]
    if len(ids) != len(set(ids)) or len(ids) != 14:
        raise ValueError("quantum atlas entry count or uniqueness drifted")
    by_id = {entry["id"]: entry for entry in value["entries"]}
    residual = [entry for entry in value["entries"] if entry["quantum_data"]["entry_kind"] == "NONPARTICLE_RESIDUAL_CLASS"]
    if len(residual) != 2 or any(
        entry["quantum_data"]["particle_interpretation"]
        != _claim("CERTIFIED", "NOT_A_PARTICLE")
        for entry in residual
    ):
        raise ValueError("residual deformation class was promoted to a particle")
    berger = by_id["quantum.berger.carrier_gap.retained_26_stationary_modes"]
    if berger["quantum_data"]["classical_mode_imported"]["status"] != "NO_CERTIFIED_MAP":
        raise ValueError("Berger carrier was promoted to a spectral mode ledger")
    tangent = by_id["quantum.crosswalk.classical_tangent_cone_to_interacting_brst"]
    if (
        tangent["quantum_data"]["carrier_crosswalk"]["status"] != "NO_CERTIFIED_MAP"
        or tangent["quantum_data"]["anomaly_QME_dependency"]["status"] != "CERTIFIED"
        or tangent["quantum_data"]["lifecycle_state"]["status"] != "NO_CERTIFIED_MAP"
    ):
        raise ValueError("classical tangent obstruction was promoted without the QME bridge")
    guards = [entry for entry in value["entries"] if entry["quantum_data"]["entry_kind"] == "NON_MODE_PARTICLE_GUARD"]
    if len(guards) != 4 or any(
        entry["quantum_data"]["particle_interpretation"]["status"] != "NO_CERTIFIED_MAP"
        for entry in guards
    ):
        raise ValueError("non-mode carrier was promoted to a particle")


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    _validate_inputs(values)
    value = {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "quantum",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha256(Path(__file__)),
        "status_vocabulary": STATUSES,
        "description_axes": AXES,
        "entries": entries(values),
        "verification_commands": [
            "PYTHONPATH=quantum-weyl python3 -m atlas.generate_quantum_atlas_fragment --check",
            "PYTHONPATH=quantum-weyl python3 -m atlas.verify_quantum_atlas_fragment",
            "PYTHONPATH=quantum-weyl python3 -m unittest atlas.tests.test_quantum_atlas_fragment",
            "python3 residual_atlas/validate_fragment.py quantum-weyl/atlas/quantum-atlas-fragment.json",
        ],
    }
    validate_fragment(value)
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale quantum atlas fragment: {OUTPUT}")
    print("quantum residual-atlas fragment: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
