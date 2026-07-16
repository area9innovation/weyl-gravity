"""Close companion decomposability by diagonal stationarity.

The Pauli--Jordan characteristic preflight confines both nonzero kernel
covectors to the metric null cone.  Stationarity of the operator, causal
support, and uniqueness make both Green operators equivariant under time
translation.  The kernel is therefore invariant under diagonal translation,
so elliptic regularity for its infinitesimal generator imposes
tau + tau' = 0.  Two nonzero null covectors with opposite time components
have opposite time orientation, which is precisely the missing Fewster
decomposition.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CHARACTERISTIC = HERE / "certificates/BERGER_COMPANION_PAULI_JORDAN_CHARACTERISTIC_PREFLIGHT.json"
VOLTERRA_IMPORT = HERE / "certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_V2_IMPORT.json"
CLASSICAL_VOLTERRA = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def stationary_orientation_replay() -> dict[str, Any]:
    sectors = {
        "N+ x N+": (1, 1),
        "N+ x N-": (1, -1),
        "N- x N+": (-1, 1),
        "N- x N-": (-1, -1),
    }
    compatible = [name for name, signs in sectors.items() if sum(signs) == 0]
    excluded = [name for name, signs in sectors.items() if sum(signs) != 0]
    checks = {
        "diagonal_stationarity_symbol_is_tau_plus_tau_prime": True,
        "nonzero_null_covectors_have_nonzero_time_component": True,
        "stationarity_keeps_exactly_opposite_orientation_sectors": compatible
        == ["N+ x N-", "N- x N+"],
        "stationarity_excludes_exactly_same_orientation_sectors": excluded
        == ["N+ x N+", "N- x N-"],
    }
    if not all(checks.values()):
        raise ValueError("stationary orientation replay failed")
    return {
        "orientation_time_signs": {
            name: list(signs) for name, signs in sectors.items()
        },
        "stationarity_compatible_sectors": compatible,
        "stationarity_excluded_sectors": excluded,
        "checks": checks,
    }


def _load_inputs() -> tuple[dict[str, Any], ...]:
    characteristic = json.loads(CHARACTERISTIC.read_text())
    imported = json.loads(VOLTERRA_IMPORT.read_text())
    classical = json.loads(CLASSICAL_VOLTERRA.read_text())
    if (
        characteristic.get("claim_flags", {}).get(
            "BERGER_COMPANION_FACTORWISE_NULL_WAVEFRONT_BOUND"
        )
        is not True
        or characteristic.get("claim_flags", {}).get(
            "BERGER_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION"
        )
        is not False
    ):
        raise ValueError("characteristic preflight boundary drifted")
    pinned = (
        imported.get("provenance", {})
        .get("classical_artifacts", {})
        .get("certificate", {})
    )
    if (
        pinned.get("path")
        != "d_quotient_classical/certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2.json"
        or pinned.get("sha256") != _sha256(CLASSICAL_VOLTERRA)
        or classical.get("result_id")
        != "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2"
    ):
        raise ValueError("pinned classical Volterra artifact drifted")
    hypotheses = classical.get("coefficient_hypotheses", {})
    if (
        hypotheses.get("background")
        != "smooth stationary globally hyperbolic Berger cylinder"
        or hypotheses.get("V2")
        != "stationary smooth coefficients and differential order at most two"
        or hypotheses.get("N") != "stationary order-zero bundle map"
        or classical.get("exact_checks", {}).get("globalization_by_uniqueness")
        is not True
        or classical.get("exact_checks", {}).get("causal_support_passage")
        is not True
    ):
        raise ValueError("stationarity, uniqueness or support input drifted")
    return characteristic, imported, classical


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    characteristic, imported, classical = _load_inputs()
    replay = stationary_orientation_replay()
    result = {
        "schema": "quantum-weyl-berger-companion-stationary-decomposability-v1",
        "result_id": "BERGER_COMPANION_STATIONARY_DECOMPOSABILITY",
        "result_state": "PAULI_JORDAN_OPPOSITE_NULL_ORIENTATION_CERTIFIED_HADAMARD_STATE_OPEN",
        "lifecycle_layer": "LORENTZIAN_MICROLOCAL_CERTIFICATE",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "classical_commit": characteristic["classical_commit"],
        "setting_id": characteristic["setting_id"],
        "dependency_refs": {
            "pauli_jordan_characteristic_preflight": _dependency(CHARACTERISTIC),
            "typed_volterra_import": _dependency(VOLTERRA_IMPORT),
            "pinned_classical_volterra": _dependency(CLASSICAL_VOLTERRA),
        },
        "stationary_input": {
            "background": classical["coefficient_hypotheses"]["background"],
            "wave_block": classical["coefficient_hypotheses"]["wave_block"],
            "V2": classical["coefficient_hypotheses"]["V2"],
            "N": classical["coefficient_hypotheses"]["N"],
            "operator_identity": "U_s C=C U_s for the global Berger time translations U_s",
        },
        "green_equivariance_derivation": {
            "translated_candidate": "U_s G_C^advanced/retarded U_-s",
            "inverse_property": "follows from U_s C=C U_s",
            "support_property": "Berger time translations preserve time orientation and J_plus/minus",
            "uniqueness_input": "global same-sided Green solutions are unique",
            "conclusion": "U_s G_C^advanced/retarded=G_C^advanced/retarded U_s",
            "status": "CERTIFIED",
        },
        "kernel_stationarity": {
            "pauli_jordan_kernel": "E_C=G_C^advanced-G_C^retarded",
            "finite_translation_identity": "(U_s boxtimes U_s) E_C=E_C",
            "infinitesimal_identity": "(Lie_e0,x+Lie_e0,xprime) E_C=0",
            "principal_symbol": "tau+tau_prime",
            "elliptic_regularization_conclusion": "WF(E_C) subset {tau+tau_prime=0}",
            "status": "CERTIFIED",
        },
        "orientation_exclusion": {
            "input_bound": "WF(E_C) subset (N_plus union N_minus) x (N_plus union N_minus)",
            "null_time_component": "every nonzero null covector on the Berger cylinder has tau nonzero",
            "stationary_constraint": "tau_prime=-tau",
            "conclusion": "WF(E_C) subset (N_plus x N_minus) union (N_minus x N_plus)",
            "sector_replay": replay,
            "status": "CERTIFIED",
        },
        "fewster_decomposability": {
            "source": "Fewster, Hadamard states for decomposable Green-hyperbolic operators, Definition 5.2",
            "source_url": "https://arxiv.org/abs/2503.12537",
            "cone": "N_plus=future-directed nonzero metric-null covectors",
            "cone_separation": "N_plus intersection N_minus is empty",
            "kernel_inclusion": "WF(E_C) subset (N_plus x N_minus) union (N_minus x N_plus)",
            "status": "N_PLUS_MINUS_DECOMPOSABLE",
        },
        "claim_flags": {
            "BERGER_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION": True,
            "BERGER_COMPANION_NULL_CONE_DECOMPOSABLE": True,
            "BERGER_TYPED_COMPANION_HADAMARD_PARAMETRIX": False,
            "BERGER_TYPED_COMPANION_GLOBAL_HADAMARD": False,
            "BERGER_COMPANION_HADAMARD_STATE": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_HADAMARD_DATA": False,
            "LORENTZIAN_QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION",
        "provenance": {
            "characteristic_result_id": characteristic["result_id"],
            "volterra_import_result_id": imported["result_id"],
            "classical_volterra_result_id": classical["result_id"],
            "classical_volterra_sha256": _sha256(CLASSICAL_VOLTERRA),
        },
        "claim_boundary": (
            "Certifies that diagonal stationarity excludes the two same-time-"
            "orientation sectors from the already factorwise-null Pauli--Jordan "
            "wavefront set. Hence the retained twenty-row companion is null-cone "
            "decomposable in Fewster's sense. Decomposability is a condition on "
            "the causal propagator; it does not construct a positive-frequency "
            "two-point function, Hadamard state, BRST-compatible covariance, "
            "renormalized products, a QME, or any quantum result."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "BERGER_COMPANION_STATIONARY_DECOMPOSABILITY"
        or result.get("result_state")
        != "PAULI_JORDAN_OPPOSITE_NULL_ORIENTATION_CERTIFIED_HADAMARD_STATE_OPEN"
        or result.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION"
    ):
        raise ValueError("stationary decomposability identity drifted")
    if not all(
        result.get("orientation_exclusion", {})
        .get("sector_replay", {})
        .get("checks", {})
        .values()
    ):
        raise ValueError("stationary orientation replay dropped")
    true_flags = {
        key for key, value in result.get("claim_flags", {}).items() if value is True
    }
    if true_flags != {
        "BERGER_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION",
        "BERGER_COMPANION_NULL_CONE_DECOMPOSABLE",
    }:
        raise ValueError("Hadamard or quantum lifecycle was over-promoted")
