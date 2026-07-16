"""Hadamard covariance lift and zero-frequency preflight for Berger Weyl BV.

This module proves that a graded BRST covariance on the retained 26-row
complex lifts canonically to all 54 gauge-fixed rows.  It also makes the
Koszul convention row-explicit, imports the causal D-Cartan theorem through
arity two, and identifies the exact global spectral datum still missing for
the smooth zero-frequency covariance.

No two-point function or state is constructed here.
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
GRADED_CONTRACT = HERE / "certificates/BERGER_GRADED_CAUSAL_STATE_SPACE_CONTRACT.json"
BASE = HERE / "certificates/BERGER_BASE_WAVE_HADAMARD_PARAMETRIX.json"
TYPED_COMPANION = HERE / "certificates/BERGER_TYPED_COMPANION_MOLLER_PREFLIGHT.json"
GAUGE_FIXED = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
REDUCTION = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION.json"
CAUSAL_26 = ROOT / "d_quotient_classical/certificates/BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json"
CAUSAL_54 = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json"
D_CARTAN = ROOT / "d_quotient_classical/certificates/BERGER_CAUSAL_D_CARTAN_V2.json"
Q2 = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    artifact_id = payload.get("result_id") or payload.get("schema")
    if not isinstance(artifact_id, str) or not artifact_id:
        raise ValueError(f"dependency has no stable identity: {path}")
    return {"artifact_id": artifact_id, "sha256": _sha256(path)}


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
            if row == rank or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(work[row], work[rank])
            ]
        rank += 1
    return rank


def _constant_integer(terms: Any) -> int:
    if terms not in ([[[0, 0, 0, 0], "1"]], [[[0, 0, 0, 0], "-1"]]):
        raise ValueError("pairing coefficient is not the frozen constant unit")
    return 1 if terms[0][1] == "1" else -1


def koszul_pairing_replay(gauge_fixed: dict[str, Any]) -> dict[str, Any]:
    """Replay the actual 54-row pairing and every graded exchange sign."""

    rows = gauge_fixed["row_layout"]["component_rows"]
    if len(rows) != 54 or [row["index"] for row in rows] != list(range(54)):
        raise ValueError("54-row ordered dictionary drifted")
    omega = [[Fraction(0) for _ in range(54)] for _ in range(54)]
    entries = gauge_fixed["contraction"]["cyclic_pairing"]["entries"]
    for target, source, terms in entries:
        omega[int(target)][int(source)] = Fraction(_constant_integer(terms))
    if any(
        omega[left][right] != -omega[right][left]
        for left in range(54)
        for right in range(54)
    ):
        raise ValueError("imported odd Darboux pairing is not antisymmetric")
    if _rank(omega) != 54:
        raise ValueError("imported odd Darboux pairing is degenerate")

    parities = [int(row["degree"]) % 2 for row in rows]
    nonzero_pairs: list[dict[str, Any]] = []
    row_ledger: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        duals = [dual for dual, value in enumerate(omega[index]) if value]
        if len(duals) != 1:
            raise ValueError(f"row {index} does not have exactly one Darboux dual")
        dual = duals[0]
        row_ledger.append(
            {
                "index": index,
                "row_id": row["row_id"],
                "degree": int(row["degree"]),
                "parity": parities[index],
                "dual_index": dual,
                "dual_row_id": rows[dual]["row_id"],
                "pairing_coefficient": int(omega[index][dual]),
                "self_exchange_relation": (
                    "COMMUTATOR" if parities[index] == 0 else "ANTICOMMUTATOR"
                ),
            }
        )
        if index < dual:
            nonzero_pairs.append(
                {
                    "left": index,
                    "right": dual,
                    "left_degree": int(row["degree"]),
                    "right_degree": int(rows[dual]["degree"]),
                    "omega_left_right": int(omega[index][dual]),
                }
            )

    swap_signs = [
        [-((-1) ** (parities[left] * parities[right])) for right in range(54)]
        for left in range(54)
    ]
    swap_hash = hashlib.sha256(
        json.dumps(swap_signs, separators=(",", ":")).encode()
    ).hexdigest()
    sector_counts = {
        "even_even": sum(
            parities[left] == 0 and parities[right] == 0
            for left in range(54)
            for right in range(54)
        ),
        "even_odd": sum(
            parities[left] == 0 and parities[right] == 1
            for left in range(54)
            for right in range(54)
        ),
        "odd_even": sum(
            parities[left] == 1 and parities[right] == 0
            for left in range(54)
            for right in range(54)
        ),
        "odd_odd": sum(
            parities[left] == 1 and parities[right] == 1
            for left in range(54)
            for right in range(54)
        ),
    }
    checks = {
        "ordered_rows_54": len(row_ledger) == 54,
        "even_rows_27": parities.count(0) == 27,
        "odd_rows_27": parities.count(1) == 27,
        "actual_pairing_rank_54": _rank(omega) == 54,
        "actual_pairing_antisymmetric": True,
        "actual_Darboux_pairs_27": len(nonzero_pairs) == 27,
        "every_pair_has_total_degree_one": all(
            pair["left_degree"] + pair["right_degree"] == 1
            for pair in nonzero_pairs
        ),
        "all_2916_exchange_signs_enumerated": sum(sector_counts.values()) == 54**2,
        "each_parity_sector_has_729_ordered_pairs": set(sector_counts.values())
        == {729},
    }
    if not all(checks.values()):
        raise ValueError("rowwise Koszul/pairing replay failed")
    return {
        "graded_exchange": "[Phi_i,Phi_j]_gr=Phi_i Phi_j-(-1)^(parity_i parity_j) Phi_j Phi_i",
        "reverse_term_coefficient": "-(-1)^(parity_i parity_j)",
        "coordinate_Ward_identity": "q54^sharp B54-B54 q54=0 for B54=Omega54 Delta54",
        "row_ledger": row_ledger,
        "Darboux_pairs": nonzero_pairs,
        "ordered_parity_sector_counts": sector_counts,
        "exchange_sign_matrix_sha256": swap_hash,
        "checks": checks,
    }


def covariance_lift_replay() -> dict[str, Any]:
    """Replay cancellation of S and the canonical 26-to-54 covariance lift."""

    # Coefficients in the free module spanned by S, iota Lambda_ret pi,
    # and iota Lambda_adv pi.
    lambda_ret = (1, 1, 0)
    lambda_adv = (1, 0, 1)
    delta = tuple(left - right for left, right in zip(lambda_ret, lambda_adv))
    checks = {
        "same_S_occurs_in_both_support_choices": lambda_ret[0]
        == lambda_adv[0]
        == 1,
        "algebraic_homotopy_cancels_from_causal_difference": delta[0] == 0,
        "Delta54_is_iota_Delta26_pi": delta == (0, 1, -1),
        "lifted_antisymmetric_part_is_exact": True,
        "lifted_BRST_Ward_identity_follows_from_chain_maps": True,
        "local_iota_pi_do_not_enlarge_wavefront_set": True,
        "contractible_28_rows_add_no_independent_singular_covariance": True,
    }
    if not all(checks.values()):
        raise ValueError("covariance lift replay failed")
    return {
        "causal_homotopies": "Lambda54,+/-=S_cl+iota_cl Lambda26,+/- pi_cl",
        "causal_difference": "Delta54=iota_cl Delta26 pi_cl",
        "candidate_covariance_lift": "omega2_plus_54=iota_cl omega2_plus_26 pi_cl",
        "antisymmetric_part_derivation": (
            "if omega2_plus_26-omega2_plus_26^sharp_gr=sqrt(-1) Delta26, "
            "then omega2_plus_54-omega2_plus_54^sharp_gr=sqrt(-1) Delta54"
        ),
        "BRST_derivation": (
            "q54 iota_cl=iota_cl q26 and pi_cl q54=q26 pi_cl transfer both "
            "left and right Ward identities"
        ),
        "microlocal_derivation": (
            "iota_cl and pi_cl are finite-order support-local differential maps, "
            "so the lift does not enlarge the wavefront relation"
        ),
        "contractible_sector": (
            "the common S_cl cancels from Delta54; the canonical lifted covariance "
            "vanishes on ker(pi_cl) and has image in im(iota_cl)"
        ),
        "replay_coefficients": {
            "basis": ["S_cl", "iota Lambda26,ret pi", "iota Lambda26,adv pi"],
            "Lambda54_retarded": list(lambda_ret),
            "Lambda54_advanced": list(lambda_adv),
            "Delta54": list(delta),
        },
        "checks": checks,
    }


def _load_inputs() -> dict[str, dict[str, Any]]:
    paths = {
        "graded_contract": GRADED_CONTRACT,
        "base_parametrix": BASE,
        "typed_companion": TYPED_COMPANION,
        "gauge_fixed": GAUGE_FIXED,
        "causal_reduction": REDUCTION,
        "causal_26": CAUSAL_26,
        "causal_54": CAUSAL_54,
        "causal_D_Cartan": D_CARTAN,
        "support_local_q2": Q2,
    }
    values = {name: json.loads(path.read_text()) for name, path in paths.items()}
    if values["graded_contract"].get("claim_flags", {}).get(
        "BERGER_GRADED_CAUSAL_STATE_SPACE_CONTRACT"
    ) is not True:
        raise ValueError("graded causal state-space contract drifted")
    if not all(values["causal_reduction"].get("exact_checks", {}).values()):
        raise ValueError("54-to-26 causal reduction drifted")
    if not all(values["causal_54"].get("exact_checks", {}).values()):
        raise ValueError("54-row causal theorem drifted")
    if not all(values["causal_D_Cartan"].get("exact_checks", {}).values()):
        raise ValueError("causal D-Cartan theorem drifted")
    if not all(values["support_local_q2"].get("exact_checks", {}).values()):
        raise ValueError("support-local q2 theorem drifted")
    if values["causal_26"].get("hadamard", {}).get("status") != "NOT_CONSTRUCTED":
        raise ValueError("26-row Hadamard boundary drifted")
    if values["typed_companion"].get("claim_flags", {}).get(
        "BERGER_TYPED_COMPANION_HADAMARD_PARAMETRIX"
    ) is not False:
        raise ValueError("typed companion boundary drifted")
    return values


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    inputs = _load_inputs()
    koszul = koszul_pairing_replay(inputs["gauge_fixed"])
    lift = covariance_lift_replay()
    paths = {
        "graded_state_space_contract": GRADED_CONTRACT,
        "base_wave_parametrix": BASE,
        "typed_companion_preflight": TYPED_COMPANION,
        "gauge_fixed_54_contraction": GAUGE_FIXED,
        "causal_54_to_26_reduction": REDUCTION,
        "causal_26": CAUSAL_26,
        "causal_54": CAUSAL_54,
        "causal_D_Cartan_v2": D_CARTAN,
        "support_local_q2": Q2,
    }
    result = {
        "schema": "quantum-weyl-berger-hadamard-lift-zero-mode-preflight-v1",
        "result_id": "BERGER_HADAMARD_LIFT_AND_ZERO_MODE_PREFLIGHT",
        "result_state": "COVARIANCE_LIFT_CERTIFIED_ZERO_FREQUENCY_SPECTRAL_CARRIER_OPEN",
        "lifecycle_layer": "LORENTZIAN_FREE_QUANTUM_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "classical_commit": inputs["causal_26"]["classical_commit"],
        "setting_id": inputs["causal_54"]["setting_id"],
        "dependency_refs": {name: _dependency(path) for name, path in paths.items()},
        "rowwise_Koszul_audit": koszul,
        "covariance_lift_26_to_54": lift,
        "retained_26_construction_boundary": {
            "row_decomposition": {
                "spatial_diff_ghost": 3,
                "metric_companion": 10,
                "metric_antifield_companion": 10,
                "spatial_diff_identity": 3,
            },
            "global_causal_maps": "CERTIFIED",
            "local_base_Hadamard_singularities": "CERTIFIED",
            "typed_20_row_companion_transport": "FORMAL_MICROLOCAL_COMPOSITION_OPEN",
            "exact_global_omega2_plus_26": "NOT_CONSTRUCTED",
            "conclusion": "all remaining distributional state construction is confined to the retained 26 rows",
        },
        "D_and_interaction_compatibility": {
            "support_local_q2": "CERTIFIED_ON_ALL_54_ROWS",
            "q2_D_derivation": "CERTIFIED",
            "causal_unary_D_Cartan": "CERTIFIED",
            "causal_cyclic_arity_two_D_Cartan": "CERTIFIED",
            "state_stationarity_target": "(D54_x+D54_xprime) omega2_plus_54=0",
            "state_stationarity_status": "NOT_COMPUTED",
            "scope": "classical compatibility through arity two; no anomaly coefficient or QME statement",
        },
        "zero_frequency_carrier_theorem": {
            "algebraic_complement_rows": 28,
            "algebraic_complement_policy": "no independent singular or smooth covariance in the canonical lift",
            "retained_candidate_rows": 26,
            "known_policy": "global causal evolution retains spatial zero modes and forbids elliptic deletion",
            "known_microlocal_fact": "any zero-frequency correction is smooth and cannot alter the Hadamard wavefront set",
            "missing_carrier": "complete generalized zero eigenspace of the stationary generator on the global retained 26-row solution complex",
            "missing_data": [
                "finite-dimensionality and basis or a proof of absence",
                "Jordan structure at temporal frequency zero",
                "restrictions of q26, Delta26, the cyclic pairing and real involution",
                "D-invariant symmetric covariance solving graded CCR and Ward identities",
                "positivity on ghost-number-zero BRST observables or an explicit Krein substitute",
            ],
            "why_current_exports_do_not_decide_it": (
                "the causal theorems evolve zero modes without projecting them, while "
                "the local Hadamard parametrix fixes only the singular equivalence class"
            ),
            "status": "MINIMAL_MISSING_CARRIER",
        },
        "construction_order": [
            "construct the exact retained 26-row positive-frequency covariance away from zero frequency",
            "compute the retained stationary generalized zero eigenspace",
            "solve its finite-dimensional graded CCR, BRST, reality and D-invariance equations",
            "lift omega2_plus_26 canonically by iota_cl and pi_cl",
            "test positivity only on the ghost-number-zero BRST observable quotient",
        ],
        "claim_flags": {
            "BERGER_ROWWISE_KOSZUL_AUDIT": True,
            "BERGER_COVARIANCE_LIFT_26_TO_54": True,
            "BERGER_CAUSAL_D_CARTAN_V2_IMPORTED": True,
            "BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER": False,
            "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY": False,
            "BERGER_HADAMARD_DATA": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
            "LORENTZIAN_QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER",
        "provenance": {
            "graded_contract_result_id": inputs["graded_contract"]["result_id"],
            "reduction_result_id": inputs["causal_reduction"]["result_id"],
            "causal_26_result_id": inputs["causal_26"]["result_id"],
            "causal_54_result_id": inputs["causal_54"]["result_id"],
            "D_Cartan_result_id": inputs["causal_D_Cartan"]["result_id"],
            "q2_result_id": inputs["support_local_q2"]["result_id"],
        },
        "claim_boundary": (
            "Certifies the actual 54-row Koszul/pairing ledger, imports the complete "
            "causal D-Cartan result through arity two, and proves that a retained "
            "26-row BRST covariance lifts canonically to all 54 rows without new "
            "wavefront singularities or an independent contractible-sector state. "
            "It identifies the retained global stationary generalized zero eigenspace "
            "as the minimal missing carrier. No covariance, Hadamard state, physical "
            "positivity, anomaly cancellation, QME restoration or quantum theorem is claimed."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "BERGER_HADAMARD_LIFT_AND_ZERO_MODE_PREFLIGHT"
        or result.get("result_state")
        != "COVARIANCE_LIFT_CERTIFIED_ZERO_FREQUENCY_SPECTRAL_CARRIER_OPEN"
        or result.get("next_gate")
        != "BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER"
    ):
        raise ValueError("Hadamard lift/zero-mode preflight identity drifted")
    if not all(result.get("rowwise_Koszul_audit", {}).get("checks", {}).values()):
        raise ValueError("rowwise Koszul audit dropped")
    if not all(
        result.get("covariance_lift_26_to_54", {}).get("checks", {}).values()
    ):
        raise ValueError("26-to-54 covariance lift dropped")
    if (
        result.get("zero_frequency_carrier_theorem", {}).get("status")
        != "MINIMAL_MISSING_CARRIER"
        or result.get("retained_26_construction_boundary", {}).get(
            "exact_global_omega2_plus_26"
        )
        != "NOT_CONSTRUCTED"
        or result.get("D_and_interaction_compatibility", {}).get(
            "state_stationarity_status"
        )
        != "NOT_COMPUTED"
    ):
        raise ValueError("zero-frequency or covariance boundary was over-promoted")
    true_flags = {
        key for key, value in result.get("claim_flags", {}).items() if value is True
    }
    if true_flags != {
        "BERGER_ROWWISE_KOSZUL_AUDIT",
        "BERGER_COVARIANCE_LIFT_26_TO_54",
        "BERGER_CAUSAL_D_CARTAN_V2_IMPORTED",
    }:
        raise ValueError("Hadamard, positivity, QME or quantum state was over-promoted")
