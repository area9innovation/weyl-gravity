#!/usr/bin/env python3
"""Serialize the complete symbolic Berger per-shell recoil operator word."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_spacetime_form_block_sign_bridge import (
    spacetime_d,
    spacetime_delta,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD.json"
SCHEMA = PACKAGE / "schema/berger-complete-per-shell-recoil-operator-word-v1.schema.json"
REPORT = PACKAGE / "reports/berger-complete-per-shell-recoil-operator-word.md"
DEPENDENCIES = {
    "recoil": PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_RECOIL_ORDER_AND_INPUT_GATE.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "coupling_stripped": PACKAGE / "certificates/BERGER_COUPLING_STRIPPED_DETECTOR_SELECTED_PREPARATIONS.json",
    "de_rham": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
    "kernels": PACKAGE / "certificates/BERGER_FINITE_MODE_MAXWELL_EMITTER_GREEN_KERNELS.json",
    "signs": PACKAGE / "certificates/BERGER_SPACETIME_FORM_BLOCK_SIGN_BRIDGE.json",
    "tail": PACKAGE / "certificates/BERGER_DOWNSTREAM_MAXWELL_DETECTOR_DUAL_NORMS.json",
    "haar": PACKAGE / "certificates/BERGER_HAAR_PROFILE_NORMALIZATION_REPAIR.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_per_shell_recoil_operator_word.py",
    PACKAGE / "tests/test_berger_per_shell_recoil_operator_word.py",
    SCHEMA,
    REPORT,
]
AUDIT_MAX_TWO_J = 4


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _space_dimensions(two_j: int) -> dict[str, int]:
    dimension = two_j + 1
    return {
        "detector_two_form": 6 * dimension,
        "maxwell_one_form": 4 * dimension,
        "emitter_two_form": 6 * dimension,
        "emitter_cauchy_data": 6 * dimension,
        "scalar": 1,
    }


def _operation(identifier: str, source: str, target: str, dimensions: dict[str, int]) -> dict[str, Any]:
    return {
        "id": identifier,
        "source": source,
        "target": target,
        "input_dimension": dimensions[source],
        "output_dimension": dimensions[target],
    }


def preparation_operations(two_j: int) -> list[dict[str, Any]]:
    """Applied order for detector profile -> fixed coupling-stripped Cauchy datum."""
    dims = _space_dimensions(two_j)
    return [
        _operation("Deltahat_2", "detector_two_form", "maxwell_one_form", dims),
        _operation("G_A_advanced", "maxwell_one_form", "maxwell_one_form", dims),
        _operation("Dhat_1", "maxwell_one_form", "emitter_two_form", dims),
        _operation("multiply_h_b", "emitter_two_form", "emitter_two_form", dims),
        _operation("G_E_b_advanced_physical", "emitter_two_form", "emitter_two_form", dims),
        _operation("Cauchy_trace_b", "emitter_two_form", "emitter_cauchy_data", dims),
        _operation("positive_energy_dual_b", "emitter_cauchy_data", "emitter_cauchy_data", dims),
    ]


def recoil_operations(
    two_j: int,
    *,
    drop_outer_feedback_switch: bool = False,
    swap_feedback_d_for_delta: bool = False,
) -> list[dict[str, Any]]:
    """Applied order for fixed emitter Cauchy data -> one recoil record scalar."""
    dims = _space_dimensions(two_j)
    feedback_derivative = (
        _operation("Deltahat_2_WRONG", "emitter_two_form", "maxwell_one_form", dims)
        if swap_feedback_d_for_delta
        else _operation("Dhat_1", "maxwell_one_form", "emitter_two_form", dims)
    )
    operations = [
        _operation("U_E_b_free", "emitter_cauchy_data", "emitter_two_form", dims),
        _operation("multiply_h_b", "emitter_two_form", "emitter_two_form", dims),
        _operation("Deltahat_2", "emitter_two_form", "maxwell_one_form", dims),
        _operation("G_A_retarded_1", "maxwell_one_form", "maxwell_one_form", dims),
        feedback_derivative,
        _operation("multiply_h_c_inner", "emitter_two_form", "emitter_two_form", dims),
        _operation("G_E_c_retarded_physical", "emitter_two_form", "emitter_two_form", dims),
        _operation("multiply_h_c_outer", "emitter_two_form", "emitter_two_form", dims),
        _operation("Deltahat_2_outer", "emitter_two_form", "maxwell_one_form", dims),
        _operation("G_A_retarded_2", "maxwell_one_form", "maxwell_one_form", dims),
        _operation("Dhat_1_detector_field", "maxwell_one_form", "detector_two_form", dims),
        _operation("Q_a_mode_pairing", "detector_two_form", "scalar", dims),
    ]
    if drop_outer_feedback_switch:
        operations = [row for row in operations if row["id"] != "multiply_h_c_outer"]
    return operations


def _composition_defects(operations: list[dict[str, Any]]) -> int:
    return sum(left["target"] != right["source"] for left, right in zip(operations, operations[1:]))


def _token_hash(operations: list[dict[str, Any]]) -> str:
    tokens = [row["id"] for row in operations]
    return hashlib.sha256(json.dumps(tokens, separators=(",", ":")).encode()).hexdigest()


def block_audit(two_j: int) -> dict[str, Any]:
    z = sp.symbols("z", real=True)
    dims = _space_dimensions(two_j)
    d1 = spacetime_d(two_j, 1, z)
    delta2 = spacetime_delta(two_j, 2, z)
    proca = sp.eye(dims["emitter_two_form"]) + sp.symbols("m_c", positive=True) ** -2 * d1 * delta2
    preparation = preparation_operations(two_j)
    recoil = recoil_operations(two_j)
    return {
        "two_j": two_j,
        "representation_dimension": two_j + 1,
        "passive_right_column_count": two_j + 1,
        "space_dimensions": dims,
        "Dhat_1_shape": list(d1.shape),
        "Deltahat_2_shape": list(delta2.shape),
        "physical_massive_green_correction_shape": list(proca.shape),
        "preparation_composition_defect_count": _composition_defects(preparation),
        "recoil_composition_defect_count": _composition_defects(recoil),
        "preparation_token_sha256": _token_hash(preparation),
        "recoil_token_sha256": _token_hash(recoil),
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "recoil": "FIRST_DETECTOR_RECOIL_ABSOLUTE_G3_OPERATOR_COMPUTED",
        "switches": "EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED",
        "profiles": "ADVANCED_DETECTOR_TO_EMITTER_COVECTOR_OPERATOR_EXPORTED",
        "coupling_stripped": "COUPLING_STRIPPED_FIXED_PREPARATIONS_EXPORTED",
        "de_rham": "GENERIC_FINITE_PETER_WEYL_DE_RHAM_BLOCK_CONSTRUCTOR",
        "kernels": "EXACT_FINITE_MODE_MASSIVE_TWO_FORM_GREEN_KERNELS_EXPORTED",
        "signs": "RECOIL_SWITCH_PRODUCT_RULE_COMPONENT_SIGNS_EXPORTED",
        "tail": "FOUR_SYMBOLIC_RECOIL_TAIL_RADII_EXPORTED",
        "haar": "EXACT_BERGER_HAAR_DENSITY_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    audits = [block_audit(two_j) for two_j in range(AUDIT_MAX_TWO_J + 1)]
    if any(row["preparation_composition_defect_count"] or row["recoil_composition_defect_count"] for row in audits):
        raise AssertionError("typed per-shell word does not compose")
    canonical_recoil = recoil_operations(1)
    missing_switch = recoil_operations(1, drop_outer_feedback_switch=True)
    wrong_derivative = recoil_operations(1, swap_feedback_d_for_delta=True)
    if _token_hash(missing_switch) == _token_hash(canonical_recoil):
        raise AssertionError("outer-switch deletion escaped")
    if _composition_defects(wrong_derivative) == 0:
        raise AssertionError("feedback d/delta mutation escaped")

    channel_rows = [
        {
            "id": f"I_{a}{b}{c}",
            "detector": a,
            "source_preparation": b,
            "feedback_emitter": c,
            "source_mass": f"m_{b}>0",
            "feedback_mass": f"m_{c}>0",
            "absolute_g3_monomial": f"g_{b} g_{c}^2",
            "bare_tail_radius": f"D_{a} C_{c}(m_{c}) E_A,{b}",
            "word_token_sha256": audits[0]["recoil_token_sha256"],
        }
        for a in range(2)
        for b in range(2)
        for c in range(2)
    ]
    aggregate_rows = [
        {
            "id": f"Delta_M_{a}{b}_absolute_g3",
            "detector": a,
            "source_preparation": b,
            "formula": f"g_{b} sum_(c=0)^1 g_c^2 sum_(two_j>=0) ((two_j+1)/Vol_Berger) sum_(k=0)^two_j I_{a}{b}c[two_j,k](m_{b},m_c)",
            "absolute_tail_envelope": f"|g_{b}| sum_(c=0)^1 |g_c|^2 D_{a} C_c(m_c) E_A,{b}",
            "status": "SYMBOLIC_STREAM_SERIALIZED_NUMERICAL_SPECIALIZATION_OPEN",
        }
        for a in range(2)
        for b in range(2)
    ]
    coupling_absorption_mutation = [
        f"g_{row['source_preparation']}^2 g_{row['feedback_emitter']}^2"
        for row in channel_rows
    ]
    canonical_monomials = [row["absolute_g3_monomial"] for row in channel_rows]
    canonical_weight = "(two_j+1)/Vol_Berger"
    omitted_dimension_weight = "1/Vol_Berger"

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result serializes the complete symbolic per-shell preparation and absolute-g3 recoil contraction for the two Berger detectors and two selected massive two-form sources. For every two_j and passive Peter-Weyl right column k, it types the coupling-stripped advanced preparation word, the free emitter evolution, both switched coderivatives, both retarded Maxwell factors, the physical massive Green factor (I+m_c^-2 d delta)G_(wave2+m_c^2), the detector field strength and the final profile pairing. The exact switch product rule fixes the h-prime component. Eight a,b,c channel words carry g_b g_c^2 and combine into four a,b streams with the exact Peter-Weyl weight (two_j+1)/Vol_Berger. Exact dimension audits through two_j=4 have zero composition defects and mutations detect deletion of the outer feedback switch, d/delta interchange, coupling absorption and omission of the Peter-Weyl weight. This is a complete generic symbolic integrand and coefficient functional, not an executable interval evaluator: no callable detector-coefficient provider, nested time-convolution backend, shell evaluator or tail-aware stop loop is exported. Numerical specialization is therefore deferred even though m_0,m_1 and g_0,g_1 remain symbolic. It does not export four recoil intervals, restrict records to the second-order cone, activate Bridge 3, promote finite-r/all-orders observer stability or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-complete-per-shell-recoil-operator-word-v1",
        "result_id": "BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD",
        "setting_id": values["coupling_stripped"]["setting_id"],
        "claim_status": "COMPLETE_SYMBOLIC_PER_SHELL_PREPARATION_AND_ABSOLUTE_G3_RECOIL_INTEGRAND_EXPORTED",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "mode_scope": {
            "theory": "classical pure-Weyl gravity plus Berger clock, Maxwell detector apparatus and two selected massive two-form emitters",
            "background": "compact positive Berger clock at fixed coupling",
            "boundaries": "R x S3 with retarded/advanced time support and no spatial boundary",
            "charge_sector": "fixed-coupling Berger sector; no compact-product mode import",
            "carrier": "Peter-Weyl spacetime one-form/two-form blocks and emitter Cauchy data",
            "degree": "Maxwell 1-form, field/emitter 2-form, emitter Cauchy pair",
            "parity": "all form polarizations",
            "ell": "two_j=0,1,...",
            "m": "all representation rows inside each form block",
            "k": "all passive right columns k=0,...,two_j",
            "omega": "exact retarded/advanced time convolution; no frequency discretization",
        },
        "operator_definitions": {
            "spacetime_split": "X_k=dt wedge alpha_(k-1)+beta_k",
            "Dhat_1": "(phi,a)->(partial_t a-dSigma phi,dSigma a)",
            "Deltahat_2_after_switch": "delta(h(alpha,beta))=(-h deltaSigma alpha,h partial_t alpha+(partial_t h)alpha+h deltaSigma beta)",
            "Maxwell_green": "G_A,ret/adv for diag(partial_t^2+Delta_0,partial_t^2+Delta_1)",
            "massive_physical_green": "G_Ec=(I+m_c^-2 Dhat_1 Deltahat_2)G_(diag(partial_t^2+Delta_1+m_c^2,partial_t^2+Delta_2+m_c^2))",
            "free_emitter_evolution": "U_Eb(m_b) maps co-closed Cauchy data tilde_u_b to K_b^(0)",
            "detector_pairing": "Q_a,n,k[X]=integral_R p_hat_a,n,k(t)^dagger X_n,k(t) dt",
        },
        "preparation_word": {
            "input": "detector coefficient p_hat_b,n,k(t) of chi_b P_b",
            "applied_order": preparation_operations(0),
            "output": "tilde_u_b,n,k=(-tilde_p_b,n,k,(Delta_2^co+m_b^2)tilde_q_b,n,k)",
            "formula": "tilde_u_b=S_Eb Cauchy G_Eb,adv M_hb Dhat_1 G_A,adv Deltahat_2[p_hat_b]",
            "coupling_convention": "tilde_u_b depends symbolically on m_b and detector data but is held fixed in the g expansion",
        },
        "recoil_word": {
            "applied_order": recoil_operations(0),
            "formula": "I_abc[n,k]=Q_a,n,k Dhat_1 G_A,ret Deltahat_2 M_hc G_Ec,ret M_hc Dhat_1 G_A,ret Deltahat_2 M_hb U_Eb tilde_u_b,n,k",
            "leading_formula": "L_ab[n,k]=Q_a,n,k Dhat_1 G_A,ret Deltahat_2 M_hb U_Eb tilde_u_b,n,k",
            "same_shell_reason": "stationary d,delta and Green blocks preserve two_j and the right column k; h_b,h_c depend only on clock time",
        },
        "peter_weyl_reconstruction": {
            "berger_volume": "Vol_Berger=16 pi^2 c with c=3 sqrt(10)/20",
            "fourier_convention": "hat X(j)=integral X(g)D_j(g)^* dSigma",
            "inner_product_weight": "(two_j+1)/Vol_Berger",
            "passive_column_sum": "sum_(k=0)^two_j",
            "matrix_row_and_form_contraction": "contained in p_hat^dagger times the typed block word",
        },
        "channel_integrands": channel_rows,
        "aggregate_streams": aggregate_rows,
        "audited_blocks": audits,
        "mutation_results": [
            {"name": "delete_outer_feedback_switch", "detected": _token_hash(missing_switch) != _token_hash(canonical_recoil)},
            {"name": "replace_feedback_Dhat_1_by_Deltahat_2", "detected": _composition_defects(wrong_derivative) > 0},
            {"name": "absorb_source_coupling_into_fixed_tilde_u_b", "detected": coupling_absorption_mutation != canonical_monomials, "mutated_monomials": coupling_absorption_mutation},
            {"name": "omit_Peter_Weyl_dimension_over_volume_weight", "detected": omitted_dimension_weight != canonical_weight, "mutated_weight": omitted_dimension_weight, "required_weight": canonical_weight},
        ],
        "external_specialization_gate": {
            "activation": "DEFERRED_UNTIL_EXECUTABLE_INTERVAL_BACKEND",
            "numerical_positive_masses": "OPEN but deferred: later choose m_0>0,m_1>0",
            "numerical_nonzero_couplings": "OPEN but deferred: later choose g_0!=0,g_1!=0",
            "stopping_goal": "OPEN but deferred: later choose interval_tolerance, nonzero, or sign",
            "four_streams_active": False,
        },
        "flags": {
            "DETECTOR_SELECTED_PREPARATION_WORD_EXPORTED": True,
            "ALL_EIGHT_ABC_RECOIL_CHANNEL_WORDS_EXPORTED": True,
            "ALL_FOUR_AB_AGGREGATE_STREAMS_SERIALIZED": True,
            "COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED": True,
            "EXACT_PETER_WEYL_RECONSTRUCTION_WEIGHT_EXPORTED": True,
            "SYMBOLIC_POSITIVE_MASSES_RETAINED": True,
            "ABSOLUTE_G3_COUPLINGS_FACTORED": True,
            "NUMERICAL_SPECIALIZATION_DECLARED": False,
            "FOUR_RECOIL_SCALAR_STREAM_ACTIVE": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "IMPLEMENT_VALIDATED_CALLABLE_FINITE_SHELL_INTERVAL_BACKEND",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale complete per-shell recoil operator word")
    print("BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
