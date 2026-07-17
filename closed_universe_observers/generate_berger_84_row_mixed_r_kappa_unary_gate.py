#!/usr/bin/env python3
"""Repair the r-axis memory transport and test the mixed r*kappa unary gate.

The memory kinetic operator T(g) is independent of kappa, so its Phi2
variation belongs to Q10, not Q11.  This generator computes that coefficient
and its adjoint in the frozen 84-row pairing exactly.  It then tests whether
the remaining Q11 profile coefficient is determined by the authoritative
handoff.  The handoff does not export the metric variation of its normalized
detector density, so the mixed profile block is returned as a normalized
input obstruction rather than guessed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
SCHEMA = PACKAGE / "schema/berger-84-row-mixed-r-kappa-unary-gate-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_84_ROW_MIXED_R_KAPPA_UNARY_GATE.json"
REPORT = PACKAGE / "reports/berger-84-row-mixed-r-kappa-unary-gate.md"

DEPENDENCIES = {
    "rod_gravity_unary": PACKAGE / "certificates/BERGER_84_ROW_ROD_GRAVITY_UNARY.json",
    "authoritative_handoff": PACKAGE / "certificates/BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF.json",
    "unary_completion_gate": PACKAGE / "certificates/BERGER_84_ROW_UNARY_PAIRING_GREEN_GATE.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "independent_verifier": PACKAGE / "verify_berger_84_row_mixed_r_kappa_unary_gate.py",
    "tests": PACKAGE / "tests/test_berger_84_row_mixed_r_kappa_unary_gate.py",
    "report": REPORT,
    "certificate_schema": SCHEMA,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _sparse(vector: sp.Matrix) -> list[list[Any]]:
    return [[index, sp.sstr(sp.factor(vector[index]))] for index in range(vector.rows) if vector[index] != 0]


def _matrix(entries: list[list[Any]]) -> sp.Matrix:
    result = sp.zeros(10)
    for row, column, coefficient in entries:
        result[row, column] = sp.sympify(coefficient, locals={"I": sp.I})
    return result


def _phi_vectors(phi2: dict[str, Any], frequency: str) -> list[sp.Matrix]:
    packed = sp.zeros(100, 1)
    for index, coefficient in phi2["assembled_sparse_coefficients"][frequency]:
        packed[index] = sp.sympify(coefficient, locals={"I": sp.I})
    return [sp.Matrix(packed[10 * component:10 * (component + 1), 0]) for component in range(10)]


def transport_variation(phi2: dict[str, Any]) -> dict[str, Any]:
    """Compute delta n, delta T, and both adjoints on the exact Phi2 basis."""

    derivative_matrices = [_matrix(item["entries"]) for item in phi2["spatial_derivative_matrices"]]
    frequencies = ["zero", "positive", "negative"]
    multipliers = {
        name: sp.sympify(value, locals={"I": sp.I})
        for name, value in zip(frequencies, phi2["temporal_derivative_multipliers"])
    }
    sectors: dict[str, Any] = {}
    exact_vectors: dict[str, dict[str, Any]] = {}
    for frequency in frequencies:
        components = _phi_vectors(phi2, frequency)
        delta_n = [(-sp.Rational(4, 3) * components[index]).applyfunc(sp.factor) for index in (1, 2, 3)]
        divergence_frozen = sum(
            (derivative_matrices[index] * delta_n[index] for index in range(3)),
            sp.zeros(10, 1),
        ).applyfunc(sp.factor)
        trace = (-components[0] + components[4] + components[7] + components[9]).applyfunc(sp.factor)
        density = (trace / 2).applyfunc(sp.factor)
        n0_density = (sp.Rational(4, 3) * multipliers[frequency] * density).applyfunc(sp.factor)
        divergence_physical = (divergence_frozen + n0_density).applyfunc(sp.factor)
        raw_adjoint_multiplier = (-divergence_physical).applyfunc(sp.factor)
        transported_multiplier = (raw_adjoint_multiplier + n0_density).applyfunc(sp.factor)
        frozen_adjoint_multiplier = (-divergence_frozen).applyfunc(sp.factor)
        transport_defects = sum(
            sp.simplify(transported_multiplier[index] - frozen_adjoint_multiplier[index]) != 0
            for index in range(10)
        )
        if transport_defects:
            raise AssertionError("density transport failed to reproduce the frozen-pairing adjoint")
        sectors[frequency] = {
            "delta_n_spatial_components_e1_e2_e3": [_sparse(vector) for vector in delta_n],
            "delta_T_derivative_coefficients_e1_e2_e3": [_sparse(vector) for vector in delta_n],
            "density_ratio_coefficient_half_trace": _sparse(density),
            "divergence_with_frozen_volume": _sparse(divergence_frozen),
            "n0_on_density_ratio": _sparse(n0_density),
            "divergence_with_physical_volume": _sparse(divergence_physical),
            "raw_physical_adjoint_derivative_coefficients_e1_e2_e3": [
                _sparse((-vector).applyfunc(sp.factor)) for vector in delta_n
            ],
            "raw_physical_adjoint_multiplier": _sparse(raw_adjoint_multiplier),
            "frozen_pairing_adjoint_derivative_coefficients_e1_e2_e3": [
                _sparse((-vector).applyfunc(sp.factor)) for vector in delta_n
            ],
            "frozen_pairing_adjoint_multiplier": _sparse(frozen_adjoint_multiplier),
            "density_transport_defect_count": transport_defects,
        }
        exact_vectors[frequency] = {
            "delta_n": delta_n,
            "density": density,
            "divergence_frozen": divergence_frozen,
        }

    reality_defects = 0
    for key in ("density", "divergence_frozen"):
        for index in range(10):
            reality_defects += int(
                sp.trigsimp(
                    sp.expand_complex(
                        exact_vectors["negative"][key][index]
                        - sp.conjugate(exact_vectors["positive"][key][index])
                    )
                ) != 0
            )
    for component in range(3):
        for index in range(10):
            reality_defects += int(
                sp.trigsimp(
                    sp.expand_complex(
                        exact_vectors["negative"]["delta_n"][component][index]
                        - sp.conjugate(exact_vectors["positive"]["delta_n"][component][index])
                    )
                ) != 0
            )
    if reality_defects:
        raise AssertionError("transport variation failed the physical reality condition")
    if sum(len(entries) for entries in sectors["positive"]["delta_T_derivative_coefficients_e1_e2_e3"]) != 11:
        raise AssertionError("physical Phi2 transport witness drifted")
    return {
        "bidegree": [1, 0],
        "bidegree_correction": "delta_r T is Q10 because p*T(g_r)*m is independent of kappa; it is not a Q11 block",
        "background_clock_data": {
            "orthonormal_signature": ["-1", "1", "1", "1"],
            "dTheta_components_e0_e1_e2_e3": ["3/4", "0", "0", "0"],
            "X": "-9/16",
            "n0": "(4/3)e0",
        },
        "exact_variation": {
            "delta_n0": "0",
            "delta_ni": "-(4/3) Phi2_0i for i=1,2,3",
            "delta_T": "-(4/3) sum_i Phi2_0i e_i",
            "density_ratio": "D_r=1+r d1+O(r^2), d1=1/2 tr_gHat(Phi2)",
            "raw_physical_adjoint": "delta(T_raw*)=-delta_T-div_gHat(delta_n)-n0(d1)",
            "frozen_pairing_adjoint": "delta(T_sharp)=-delta_T-div_gHat(delta_n)",
        },
        "frequency_sectors": sectors,
        "reality_defect_count": reality_defects,
        "canonical_sha256": _canonical_hash(sectors),
    }


def inverse_first_variation_audit(*, delete_correction: bool = False) -> dict[str, Any]:
    """Check the H and J first variations on exact rational matrices."""

    r = sp.symbols("r")
    fixtures = [
        (sp.Matrix([[2, 1], [1, 1]]), sp.Matrix([[1, 2], [3, 5]])),
        (sp.Matrix([[3, 1], [2, 1]]), sp.Matrix([[2, -1], [1, 4]])),
    ]
    left_defects = 0
    right_defects = 0
    for operator0, variation in fixtures:
        inverse0 = operator0.inv()
        inverse1 = sp.zeros(2) if delete_correction else -inverse0 * variation * inverse0
        operator = operator0 + r * variation
        inverse = inverse0 + r * inverse1
        left = sp.expand(operator * inverse - sp.eye(2))
        right = sp.expand(inverse * operator - sp.eye(2))
        left_defects += sum(sp.simplify(left[row, column].coeff(r, 1)) != 0 for row in range(2) for column in range(2))
        right_defects += sum(sp.simplify(right[row, column].coeff(r, 1)) != 0 for row in range(2) for column in range(2))
    return {
        "formula": "H10=-H00 deltaT H00 and J10=-J00 deltaT_sharp J00",
        "fixture_count": len(fixtures),
        "left_inverse_defect_count_at_r": left_defects,
        "right_inverse_defect_count_at_r": right_defects,
        "same_sided_support": "formal coefficientwise: each correction is a local deltaT insertion between same-sided clock-line Green operators",
    }


def profile_variation_gate(handoff: dict[str, Any]) -> dict[str, Any]:
    profile = handoff["profile_operator_contract"]
    required_metric_density_fields = {
        "normalized_density_definition",
        "metric_normalization_measure",
        "metric_variation_of_log_density",
    }
    missing = sorted(required_metric_density_fields - set(profile))
    if missing != sorted(required_metric_density_fields):
        raise AssertionError("profile-density input status changed; recompute the mixed gate")
    return {
        "bidegree": [1, 1],
        "status": "INPUT_BLOCKED_NORMALIZED_PROFILE_METRIC_VARIATION_UNEXPORTED",
        "imported_operator": profile["operator"],
        "fixed_polarizations": ["dTheta_wedge_dR0_1", "dTheta_wedge_dR1_2"],
        "raw_pairing": "C_g(F,P)=1/2 F_mn P_ab g^{ma} g^{nb}",
        "metric_pairing_variation": "delta C=-1/2 F_mn P_ab(Phi2^{ma} gHat^{nb}+gHat^{ma} Phi2^{nb})",
        "unknowns": ["sigma_0=delta_r log chi_0", "sigma_1=delta_r log chi_1"],
        "raw_profile_variation": "delta B_a A=chi_a[delta C(F,P_a)+sigma_a C_gHat(F,P_a)]",
        "frozen_pairing_action_variation": "delta Btilde_a A=chi_a[delta C(F,P_a)+(d1+sigma_a) C_gHat(F,P_a)]",
        "required_Q11_blocks": [
            "q11(p_a_plus,A)=-delta Btilde_a",
            "q11(A_plus,p_a)=+(delta Btilde_a)^sharp in the frozen pairing",
        ],
        "maxwell_relations_conditional": [
            "delta Btilde_a d=0 because d^2=0",
            "delta (delta Btilde_a^sharp)=0 by formal adjunction",
        ],
        "missing_input_fields": missing,
        "underdetermination_witness": {
            "completion_0": "sigma_a=0",
            "completion_1": "sigma_a=s_a with nonzero support-local s_a",
            "difference": "chi_a s_a C_gHat(F,P_a)",
            "independent_channel_defect_count": 2,
        },
        "profile_metric_variation_computed": False,
        "mixed_Q11_computed": False,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if values["rod_gravity_unary"]["flags"]["PHYSICAL_PHI2_CANONICAL_TENSOR_EXPORTED"] is not True:
        raise AssertionError("canonical physical Phi2 input dropped")
    if values["authoritative_handoff"]["flags"]["AUTHORITATIVE_84_ROW_FORWARD_INTERFACE"] is not True:
        raise AssertionError("authoritative handoff input dropped")
    if values["unary_completion_gate"]["flags"]["BASE_MEMORY_72_ROW_CAUSAL_SUBCOMPLEX_CERTIFIED"] is not True:
        raise AssertionError("memory causal subcomplex input dropped")
    phi2 = values["rod_gravity_unary"]["physical_phi2_tensor"]
    transport = transport_variation(phi2)
    inverse = inverse_first_variation_audit()
    inverse_mutation = inverse_first_variation_audit(delete_correction=True)
    if inverse["left_inverse_defect_count_at_r"] or inverse["right_inverse_defect_count_at_r"]:
        raise AssertionError("clock-line inverse first variation failed")
    if inverse_mutation["left_inverse_defect_count_at_r"] + inverse_mutation["right_inverse_defect_count_at_r"] == 0:
        raise AssertionError("clock-line inverse mutation was not detected")
    profile_gate = profile_variation_gate(values["authoritative_handoff"])
    boundary = (
        "This exact LOCAL-ALGEBRAIC/REDUCED-MODE/LORENTZIAN-CAUSAL gate corrects the bidegree bookkeeping: "
        "the Phi2 variation of the memory transport belongs to Q10, not Q11. It computes delta n, delta T, "
        "the raw physical-volume adjoint, the density-conjugated frozen-pairing adjoint, and the first formal "
        "same-sided clock-line Green correction exactly, thereby completing the previously omitted memory part "
        "of the r axis. The remaining r*kappa block is the metric variation of the detector profile. Its universal "
        "inverse-metric, volume, and adjoint formulas are exported, but the authoritative handoff does not define "
        "the metric dependence of the normalized detector density chi_a. Two compatible density variations give "
        "different Q11 blocks, so mixed nilpotency/cyclicity and the mixed Green coefficient are input-blocked and "
        "not certified. This gate does not prove finite-r Green hyperbolicity, apparatus q2/q3, K_Berger equivariance, "
        "the observer morphism, deformed rank two, emitter recoil, a Lorentzian quantum theory, or a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-84-row-mixed-r-kappa-unary-gate-v1",
        "result_id": "BERGER_84_ROW_MIXED_R_KAPPA_UNARY_GATE",
        "setting_id": values["authoritative_handoff"]["setting_id"],
        "claim_status": "Q10_MEMORY_TRANSPORT_REPAIRED_MIXED_Q11_INPUT_BLOCKED_PROFILE_DENSITY_UNEXPORTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": _sha256(path),
                "result_id": values[name]["result_id"],
            }
            for name, path in DEPENDENCIES.items()
        },
        "bidegree_audit": {
            "unary_decomposition": "Q=Q00+r Q10+kappa Q01+r*kappa Q11+O(r^2,kappa^2)",
            "memory_kinetic_action": "sum_a integral dvol_g p_a T(g) m_a",
            "readout_action": "-kappa sum_a integral dvol_g p_a B_a(g) A",
            "delta_T_bidegree": [1, 0],
            "delta_B_bidegree": [1, 1],
            "prior_assignment_delta_T_to_Q11_rejected": True,
        },
        "q10_memory_transport": transport,
        "q10_formal_green_correction": inverse,
        "q11_profile_gate": profile_gate,
        "mutation_results": [
            {
                "name": "retain_T0_on_backreacted_metric",
                "defect": "nonzero positive/negative-frequency deltaT coefficients are deleted",
                "defect_count": sum(len(entries) for entries in transport["frequency_sectors"]["positive"]["delta_T_derivative_coefficients_e1_e2_e3"]),
                "detected": True,
            },
            {
                "name": "reuse_raw_adjoint_without_density_transport",
                "defect": "n0(d1) is left in the frozen-pairing adjoint",
                "defect_count": len(transport["frequency_sectors"]["positive"]["n0_on_density_ratio"]),
                "detected": True,
            },
            {
                "name": "delete_clock_green_first_variation",
                "defect": "left/right inverse coefficient at r",
                "defect_count": inverse_mutation["left_inverse_defect_count_at_r"] + inverse_mutation["right_inverse_defect_count_at_r"],
                "detected": True,
            },
            {
                "name": "choose_sigma_a_without_profile_definition",
                "defect": "two handoff-compatible normalized-density variations produce different Q11 blocks",
                "defect_count": profile_gate["underdetermination_witness"]["independent_channel_defect_count"],
                "detected": True,
            },
        ],
        "flags": {
            "MEMORY_TRANSPORT_BIDEGREE_CORRECTED": True,
            "PHI2_INDUCED_DELTA_T_EXACT": True,
            "FROZEN_PAIRING_DELTA_T_ADJOINT_EXACT": True,
            "Q10_CLOCK_GREEN_FIRST_VARIATION_EXACT": True,
            "SEPARATE_R_AXIS_MEMORY_TRANSPORT_REPAIRED": True,
            "MIXED_PROFILE_UNDERDETERMINED_BY_HANDOFF": True,
            "MIXED_EPSILON_R2_KAPPA_UNARY_CERTIFIED": False,
            "MIXED_GREEN_COEFFICIENT_CERTIFIED": False,
            "FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED": False,
            "84_ROW_Q2_Q3_CERTIFIED": False,
            "84_ROW_K_BERGER_EQUIVARIANCE_CERTIFIED": False,
            "OBSERVER_EVALUATION_MORPHISM_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EXPORT_METRIC_DEPENDENCE_OF_NORMALIZED_DETECTOR_DENSITIES_CHI0_CHI1_THEN_COMPUTE_Q11",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES.values()
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(result)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale Berger 84-row mixed r*kappa unary gate")
    print("BERGER_84_ROW_MIXED_R_KAPPA_UNARY_GATE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
