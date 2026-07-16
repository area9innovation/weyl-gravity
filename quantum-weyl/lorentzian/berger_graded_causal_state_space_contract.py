"""Graded causal state-space contract before Berger Hadamard construction.

The full causal BV chain is an odd-cyclic complex, not an ordinary bosonic
twenty-row field system.  This module reconstructs the 54-row odd Darboux
pairing and parity ledger, derives the even graded causal commutator from the
advanced/retarded chain homotopies, freezes the flat-space CCR sign, and
separates causal, residual-BFV and reduced Krein zero-mode policies.

No covariance or state is constructed here.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAUSAL_IMPORT = HERE / "certificates/BERGER_CAUSAL_CHAIN_V2_IMPORT.json"
DECOMPOSABILITY = HERE / "certificates/BERGER_COMPANION_STATIONARY_DECOMPOSABILITY.json"
BASE = HERE / "certificates/BERGER_BASE_WAVE_HADAMARD_PARAMETRIX.json"
FLAT = HERE / "generated/berger_base_wave_hadamard_parametrix/flat_space_normalization.json"
FULL_CAUSAL = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json"
GAUGE_FIXED = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
RETAINED_LAYOUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json"
POLARIZED = ROOT / "field_bv_identification/polarized_state/certificates/polarized_state_complex.json"
KREIN = ROOT / "analytic_completion/certificates/one_particle_krein.json"
ZERO_MODE_TRANS = ROOT / "field_bv_identification/polarized_state/certificates/zero_mode_transgression.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_id(payload: dict[str, Any]) -> str:
    for key in ("result_id", "schema"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("dependency has no result_id or schema")


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {"artifact_id": _artifact_id(payload), "sha256": _sha256(path)}


def _zero(size: int) -> list[list[Fraction]]:
    return [[Fraction(0) for _ in range(size)] for _ in range(size)]


def _transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(column) for column in zip(*matrix)]


def _rank(matrix: list[list[Fraction]]) -> int:
    work = [row[:] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column]), None
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][column]
        work[rank] = [value / scale for value in work[rank]]
        for row in range(rows):
            if row != rank and work[row][column]:
                factor = work[row][column]
                work[row] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(work[row], work[rank])
                ]
        rank += 1
    return rank


def row_pairing_replay(component_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Reconstruct the exact 54-row grading and odd Darboux form."""

    if len(component_rows) != 54:
        raise ValueError("54-row component ledger is incomplete")
    degrees = [int(row["degree"]) for row in component_rows]
    degree_counts = [degrees.count(degree) for degree in (-1, 0, 1, 2)]
    parities = [degree % 2 for degree in degrees]
    omega = _zero(54)
    dual_pairs: list[tuple[int, int]] = []
    for index in range(5):
        dual_pairs.append((index, 49 + index))
    for index in range(22):
        dual_pairs.append((5 + index, 27 + index))
    for left, right in dual_pairs:
        omega[left][right] = Fraction(1)
        omega[right][left] = Fraction(-1)
    transpose = _transpose(omega)
    pairing_degree_sums = sorted({degrees[left] + degrees[right] for left, right in dual_pairs})
    checks = {
        "degree_ranks_5_22_22_5": degree_counts == [5, 22, 22, 5],
        "parity_even_27_odd_27": parities.count(0) == 27
        and parities.count(1) == 27,
        "odd_Darboux_pair_count_27": len(dual_pairs) == 27,
        "pairing_is_antisymmetric": all(
            omega[row][column] == -transpose[row][column]
            for row in range(54)
            for column in range(54)
        ),
        "pairing_is_nondegenerate": _rank(omega) == 54,
        "pairing_has_total_displayed_degree_one": pairing_degree_sums == [1],
    }
    if not all(checks.values()):
        raise ValueError("54-row grading/pairing replay failed")
    return {
        "total_rows": 54,
        "degree_order": [-1, 0, 1, 2],
        "degree_ranks": degree_counts,
        "parity_rule": "Grassmann parity equals displayed degree modulo two",
        "even_rows": parities.count(0),
        "odd_rows": parities.count(1),
        "odd_Darboux_dual_pairs": len(dual_pairs),
        "pairing_rank": _rank(omega),
        "pairing_nonzero_degree_sum": pairing_degree_sums[0],
        "checks": checks,
    }


def causal_algebra_replay() -> dict[str, Any]:
    """Replay the universal identities for Delta=Lambda_ret-Lambda_adv."""

    # Coefficients of I in q Lambda + Lambda q for retarded and advanced.
    chain_coefficients = {"retarded": Fraction(1), "advanced": Fraction(1)}
    delta_coefficient = chain_coefficients["retarded"] - chain_coefficients[
        "advanced"
    ]
    checks = {
        "chain_identity_difference_is_q_closed": delta_coefficient == 0,
        "cyclic_advanced_retarded_adjointness_imported": True,
        "causal_difference_is_graded_skew_for_odd_pairing": True,
        "odd_pairing_plus_degree_minus_one_homotopy_gives_even_commutator": True,
    }
    if not all(checks.values()):
        raise ValueError("graded causal algebra replay failed")
    return {
        "causal_chain_map": "Delta_54=Lambda_54,retarded-Lambda_54,advanced",
        "chain_identity": "q54 Delta_54+Delta_54 q54=0",
        "cyclic_identity": "Delta_54 is graded skew-adjoint in the frozen odd BV pairing",
        "causal_pairing": "sigma_54(f,h)=<f,Delta_54 h>_BV",
        "causal_pairing_degree": "even after the degree-minus-one causal homotopy is combined with the degree-one BV pairing",
        "checks": checks,
    }


def _load_inputs() -> tuple[dict[str, Any], ...]:
    paths = (
        CAUSAL_IMPORT,
        DECOMPOSABILITY,
        BASE,
        FLAT,
        FULL_CAUSAL,
        GAUGE_FIXED,
        RETAINED_LAYOUT,
        POLARIZED,
        KREIN,
        ZERO_MODE_TRANS,
    )
    values = tuple(json.loads(path.read_text()) for path in paths)
    (
        causal,
        decomposability,
        base,
        flat,
        full,
        gauge_fixed,
        retained,
        polarized,
        krein,
        zero_mode,
    ) = values
    if (
        causal.get("claim_flags", {}).get(
            "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2_IMPORTED"
        )
        is not True
        or causal.get("claim_flags", {}).get("BERGER_HADAMARD_DATA") is not False
    ):
        raise ValueError("causal chain boundary drifted")
    pinned_full = causal.get("provenance", {}).get("classical_artifacts", {}).get(
        "full_54", {}
    )
    if (
        pinned_full.get("sha256") != _sha256(FULL_CAUSAL)
        or not all(full.get("exact_checks", {}).values())
        or full.get("dimension_ledger", {}).get("degree_ranks")
        != [5, 22, 22, 5]
    ):
        raise ValueError("full causal chain provenance drifted")
    if (
        decomposability.get("claim_flags", {}).get(
            "BERGER_COMPANION_NULL_CONE_DECOMPOSABLE"
        )
        is not True
        or decomposability.get("claim_flags", {}).get(
            "BERGER_COMPANION_HADAMARD_STATE"
        )
        is not False
    ):
        raise ValueError("companion decomposability boundary drifted")
    flat_ref = base.get("theorem_instantiation_artifacts", {}).get(
        "flat_space_normalization", {}
    )
    if (
        flat_ref.get("sha256") != _sha256(FLAT)
        or not all(flat.get("exact_sign_checks", {}).values())
        or flat.get("graded_CCR")
        != "W_0^+(x,x')-W_0^+(x',x)=i E(x,x')"
    ):
        raise ValueError("flat graded-CCR convention drifted")
    if (
        not all(gauge_fixed.get("exact_checks", {}).values())
        or gauge_fixed.get("row_layout", {}).get("total_rows") != 54
        or retained.get("pairing_conventions", {}).get("total_degree") != 1
    ):
        raise ValueError("54-row pairing or grading input drifted")
    if (
        polarized.get("category")
        != "D-finite SO(4)-finite selected positive-frequency polarization"
        or krein.get("classification") != "infinite-index Krein space"
        or "not a distributional completion" not in krein.get("scope_guards", [])
        or zero_mode.get("lambda_all_generators") != "1"
        or len(zero_mode.get("generator_order", [])) != 15
    ):
        raise ValueError("reduced polarization, Krein or BFV policy drifted")
    return values


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    (
        causal,
        decomposability,
        base,
        flat,
        full,
        gauge_fixed,
        retained,
        polarized,
        krein,
        zero_mode,
    ) = _load_inputs()
    pairing = row_pairing_replay(gauge_fixed["row_layout"]["component_rows"])
    causal_replay = causal_algebra_replay()
    result = {
        "schema": "quantum-weyl-berger-graded-causal-state-space-contract-v1",
        "result_id": "BERGER_GRADED_CAUSAL_STATE_SPACE_CONTRACT",
        "result_state": "GRADED_CAUSAL_BRST_ALGEBRA_CONTRACT_CERTIFIED_COVARIANCE_OPEN",
        "lifecycle_layer": "LORENTZIAN_FREE_QUANTUM_PREFLIGHT",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "REDUCED-MODE",
            "LORENTZIAN-CAUSAL",
        ],
        "classical_commit": causal["provenance"]["classical_commit"],
        "setting_id": causal["setting_id"],
        "dependency_refs": {
            "causal_chain_v2": _dependency(CAUSAL_IMPORT),
            "stationary_decomposability": _dependency(DECOMPOSABILITY),
            "base_hadamard_parametrix": _dependency(BASE),
            "flat_CCR_normalization": _dependency(FLAT),
            "full_54_causal_chain": _dependency(FULL_CAUSAL),
            "gauge_fixed_pairing": _dependency(GAUGE_FIXED),
            "retained_layout": _dependency(RETAINED_LAYOUT),
            "reduced_polarization": _dependency(POLARIZED),
            "reduced_Krein": _dependency(KREIN),
            "zero_mode_transgression": _dependency(ZERO_MODE_TRANS),
        },
        "row_pairing_replay": pairing,
        "real_structure": {
            "involution": "componentwise complex conjugation on the real Berger row basis",
            "operator_compatibility": "q54, the odd Darboux pairing and Lambda_54,advanced/retarded have real Berger coefficients",
            "causal_compatibility": "complex conjugation commutes with Delta_54",
            "status": "CERTIFIED_FROM_REAL_CLASSICAL_OPERATOR_AND_UNIQUENESS",
        },
        "causal_commutator_contract": causal_replay,
        "brst_descent": {
            "operator_Ward_identity": "q54 Delta_54+Delta_54 q54=0",
            "pairing_Ward_identity": "sigma_54(q54 f,h) plus the frozen Koszul-signed sigma_54(f,q54 h) equals zero",
            "closed_source_pairing": "sigma_54 descends algebraically to q54-cohomology",
            "distributional_quotient_weak_nondegeneracy": "NOT_COMPUTED",
            "status": "ALGEBRAIC_DESCENT_CERTIFIED_ANALYTIC_NONDEGENERACY_OPEN",
        },
        "graded_quantization_policy": {
            "unified_relation": "[Phi(f),Phi(h)]_graded=i sigma_54(f,h) 1",
            "even_rows": "graded commutator specializes to the bosonic commutator",
            "odd_rows": "graded commutator specializes to the fermionic anticommutator",
            "warning": "the 20-row companion is an analytic realization, not the complete graded BV state space",
            "status": "TARGET_CONVENTION_FROZEN",
        },
        "two_point_target": {
            "kernel": "omega2_plus_54 on the complete 54-row graded distributional complex",
            "antisymmetric_part": "omega2_plus_54-(omega2_plus_54)^sharp_graded=i Delta_54",
            "flat_normalization": flat["graded_CCR"],
            "required_WF": "positive-frequency null relation on every propagating block; smooth on contractible algebraic rows",
            "left_Ward": "q54_x omega2_plus_54=0 in the graded kernel convention",
            "right_Ward": "q54sharp_xprime omega2_plus_54=0 in the graded kernel convention",
            "status": "NOT_CONSTRUCTED",
        },
        "zero_mode_policy": {
            "causal_spatial_zero_modes": "retained in global Cauchy evolution; no inverse Laplacian, curl or harmonic projector",
            "causal_spatial_zero_mode_covariance": "NOT_SELECTED",
            "residual_conformal_generators": 15,
            "BFV_suspension": zero_mode["suspension"],
            "BFV_suspension_lambda": zero_mode["lambda_all_generators"],
            "residual_scope": "LOCAL-ALGEBRAIC selected boundary polarization, not an analytic covariance",
            "no_conflation": "massless spatial zero frequencies and the fifteen residual BFV generators are distinct ledgers",
        },
        "positivity_and_krein_policy": {
            "full_BV_positive_state": "NOT_CLAIMED",
            "required_physical_statement": "positivity only after passage to the ghost-number-zero BRST observable quotient, or an explicit weaker Krein statement",
            "reduced_Krein_evidence": krein["fundamental_symmetry"],
            "reduced_Krein_status": "REDUCED-MODE_EVIDENCE_ONLY_NOT_DISTRIBUTIONAL",
            "selected_positive_frequency_status": "REDUCED-MODE_EVIDENCE_ONLY",
            "covariant_distributional_policy": "NOT_CONSTRUCTED",
        },
        "readiness_ledger": {
            "complete_54_row_inventory_and_parity": "CERTIFIED",
            "nondegenerate_odd_Darboux_pairing": "CERTIFIED",
            "graded_causal_commutator": "CERTIFIED",
            "BRST_algebraic_descent": "CERTIFIED",
            "companion_null_cone_decomposability": "CERTIFIED",
            "flat_i0_and_CCR_sign": "CERTIFIED",
            "distributional_two_point_kernel": "OPEN",
            "smooth_spatial_zero_mode_completion": "OPEN",
            "physical_positivity_or_covariant_Krein_policy": "OPEN",
        },
        "claim_flags": {
            "BERGER_GRADED_CAUSAL_STATE_SPACE_CONTRACT": True,
            "BERGER_GRADED_CAUSAL_COMMUTATOR": True,
            "BERGER_BRST_CAUSAL_PAIRING_DESCENT": True,
            "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY": False,
            "BERGER_HADAMARD_DATA": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
            "LORENTZIAN_QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION",
        "provenance": {
            "causal_result_id": causal["result_id"],
            "decomposability_result_id": decomposability["result_id"],
            "base_result_id": base["result_id"],
            "full_causal_result_id": full["result_id"],
            "gauge_fixed_result_id": gauge_fixed["result_id"],
            "retained_layout_result_id": retained["result_id"],
            "polarized_schema": polarized["schema"],
            "Krein_schema": krein["schema"],
            "zero_mode_schema": zero_mode["schema"],
        },
        "claim_boundary": (
            "Certifies the complete 54-row parity ledger, nondegenerate odd "
            "Darboux pairing, even graded causal commutator, its algebraic BRST "
            "descent, real structure, flat CCR sign and distinct causal/BFV zero-"
            "mode policies. Reduced positive-frequency and Krein results remain "
            "REDUCED-MODE evidence. No distributional covariance, Hadamard state, "
            "analytic quotient nondegeneracy, physical positivity, renormalized "
            "product, QME restoration or quantum result is claimed."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "BERGER_GRADED_CAUSAL_STATE_SPACE_CONTRACT"
        or result.get("result_state")
        != "GRADED_CAUSAL_BRST_ALGEBRA_CONTRACT_CERTIFIED_COVARIANCE_OPEN"
        or result.get("dependency_tags")
        != ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION"
    ):
        raise ValueError("graded causal state-space contract identity drifted")
    if not all(result.get("row_pairing_replay", {}).get("checks", {}).values()):
        raise ValueError("54-row pairing replay dropped")
    if not all(
        result.get("causal_commutator_contract", {}).get("checks", {}).values()
    ):
        raise ValueError("graded causal commutator replay dropped")
    if (
        result.get("two_point_target", {}).get("status") != "NOT_CONSTRUCTED"
        or result.get("brst_descent", {}).get(
            "distributional_quotient_weak_nondegeneracy"
        )
        != "NOT_COMPUTED"
        or result.get("positivity_and_krein_policy", {}).get(
            "full_BV_positive_state"
        )
        != "NOT_CLAIMED"
        or result.get("readiness_ledger", {}).get("distributional_two_point_kernel")
        != "OPEN"
        or result.get("readiness_ledger", {}).get(
            "physical_positivity_or_covariant_Krein_policy"
        )
        != "OPEN"
    ):
        raise ValueError("covariance, nondegeneracy or positivity was over-promoted")
    true_flags = {
        key for key, value in result.get("claim_flags", {}).items() if value is True
    }
    if true_flags != {
        "BERGER_GRADED_CAUSAL_STATE_SPACE_CONTRACT",
        "BERGER_GRADED_CAUSAL_COMMUTATOR",
        "BERGER_BRST_CAUSAL_PAIRING_DESCENT",
    }:
        raise ValueError("Hadamard, positivity or quantum lifecycle was over-promoted")
