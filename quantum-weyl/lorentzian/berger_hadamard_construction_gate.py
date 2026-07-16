"""Fail-closed construction gate for a BRST-compatible Berger Hadamard state."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAUSAL_IMPORT = HERE / "certificates/BERGER_CAUSAL_CHAIN_V2_IMPORT.json"
POLARIZED_LEDGER = (
    ROOT
    / "field_bv_identification/polarized_state/certificates/polarized_state_complex.json"
)
KREIN_LEDGER = ROOT / "analytic_completion/certificates/one_particle_krein.json"

REQUIRED_HADAMARD_CHECKS = (
    "left_bisolution",
    "right_bisolution",
    "graded_CCR_antisymmetric_part",
    "Hadamard_wavefront_set",
    "BRST_compatibility_left",
    "BRST_compatibility_right",
    "graded_hermiticity_and_reality",
    "D_stationarity",
    "zero_mode_policy",
    "positivity_or_Krein_policy",
    "complete_54_row_coverage",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    causal = json.loads(CAUSAL_IMPORT.read_text())
    polarized = json.loads(POLARIZED_LEDGER.read_text())
    krein = json.loads(KREIN_LEDGER.read_text())
    if (
        causal.get("result_id") != "BERGER_CAUSAL_CHAIN_V2_IMPORT"
        or causal.get("result_state")
        != "CAUSAL_CHAIN_V2_IMPORTED_THROUGH_ARITY_TWO_HADAMARD_OPEN"
        or causal.get("claim_flags", {}).get(
            "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2_IMPORTED"
        )
        is not True
        or causal.get("claim_flags", {}).get("BERGER_HADAMARD_DATA") is not False
        or causal.get("claim_flags", {}).get("QUANTUM_CLAIM") is not False
    ):
        raise ValueError("causal-chain v2 boundary drifted")
    if (
        polarized.get("schema") != "pure-weyl-polarized-state-complex-v1"
        or polarized.get("category")
        != "D-finite SO(4)-finite selected positive-frequency polarization"
        or "L_+ and L_- are complementary Lagrangian polarizations"
        not in polarized.get("proved", [])
        or "a Hilbert or Krein completion of the algebraic Fock space"
        not in polarized.get("not_proved", [])
    ):
        raise ValueError("reduced positive-frequency ledger drifted")
    if (
        krein.get("schema") != "pure-weyl-one-particle-krein-v1"
        or krein.get("classification") != "infinite-index Krein space"
        or krein.get("fundamental_symmetry")
        != "+1 on E and -1 on A,L in both chiralities"
        or "not a distributional completion" not in krein.get("scope_guards", [])
    ):
        raise ValueError("reduced Krein ledger drifted")
    return causal, polarized, krein


@lru_cache(maxsize=1)
def evaluate_gate() -> dict[str, Any]:
    causal, polarized, krein = _load_inputs()
    result = {
        "schema": "quantum-weyl-berger-hadamard-construction-gate-v1",
        "result_id": "BERGER_HADAMARD_CONSTRUCTION_GATE",
        "result_state": "CAUSAL_COMMUTATOR_READY_REDUCED_POLARIZATION_ONLY_HADAMARD_KERNEL_OPEN",
        "lifecycle_layer": "LORENTZIAN_FREE_QUANTUM_PREFLIGHT",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "REDUCED-MODE",
            "LORENTZIAN-CAUSAL",
        ],
        "classical_commit": causal["provenance"]["classical_commit"],
        "setting_id": causal["setting_id"],
        "available_inputs": {
            "causal_chain": {
                "status": "IMPORTED",
                "rows": 54,
                "advanced_retarded_homotopies": True,
                "causal_D_Cartan_arities": [1, 2],
                "certificate": str(CAUSAL_IMPORT.relative_to(ROOT)),
                "sha256": _sha256(CAUSAL_IMPORT),
            },
            "positive_frequency_ledger": {
                "status": "REDUCED_MODE_EVIDENCE_ONLY",
                "category": polarized["category"],
                "state_complex": polarized["state_complex"],
                "certificate": str(POLARIZED_LEDGER.relative_to(ROOT)),
                "sha256": _sha256(POLARIZED_LEDGER),
            },
            "one_particle_Krein_ledger": {
                "status": "REDUCED_MODE_EVIDENCE_ONLY_NOT_DISTRIBUTIONAL",
                "classification": krein["classification"],
                "fundamental_symmetry": krein["fundamental_symmetry"],
                "certificate": str(KREIN_LEDGER.relative_to(ROOT)),
                "sha256": _sha256(KREIN_LEDGER),
            },
        },
        "logical_separation": {
            "causal_propagator": "AVAILABLE_FROM_ADVANCED_MINUS_RETARDED_V2_GREEN_DATA",
            "complex_structure_or_covariance": "NOT_CONSTRUCTED_ON_54_ROW_DISTRIBUTIONAL_COMPLEX",
            "reduced_positive_frequency_is_full_Hadamard_evidence": False,
            "reduced_Krein_completion_is_covariant_distributional_completion": False,
        },
        "construction_route": [
            {
                "stage": "BASE_ROUGH_WAVE_HADAMARD_PARAMETRIX",
                "status": "NEXT",
                "output": "omega_Box2_plus and ghost-wave analogues with WF proof",
            },
            {
                "stage": "TYPED_COMPANION_MOLLER_TRANSPORT",
                "status": "BLOCKED_PREVIOUS_STAGE",
                "output": "omega_C20_plus respecting X_s/Y_s and A10 graph pullback",
            },
            {
                "stage": "ASSEMBLE_26_ROW_BRST_COVARIANCE",
                "status": "BLOCKED_PREVIOUS_STAGE",
                "output": "omega26_plus with CCR, bisolution and q26 Ward identities",
            },
            {
                "stage": "LIFT_TO_54_ROWS",
                "status": "BLOCKED_PREVIOUS_STAGE",
                "output": "omega54_plus through the support-local cyclic SDR",
            },
            {
                "stage": "ZERO_MODE_AND_KREIN_POLICY",
                "status": "BLOCKED_PREVIOUS_STAGE",
                "output": "smooth zero-mode completion and declared physical/Krein positivity",
            },
            {
                "stage": "HADAMARD_CERTIFICATION",
                "status": "BLOCKED_PREVIOUS_STAGE",
                "output": "all eleven distributional proof checks",
            },
        ],
        "required_kernel_export": {
            "result_id": "BERGER_54_ROW_BRST_HADAMARD_TWO_POINT",
            "kernels": ["omega2_plus_54", "omega2_minus_54", "Delta_54"],
            "required_checks": list(REQUIRED_HADAMARD_CHECKS),
            "required_row_count": 54,
            "required_dependency_tags": ["LORENTZIAN-CAUSAL"],
            "proof_policy": "CONTENT_ADDRESSED_DISTRIBUTIONAL_AND_MICROLOCAL_ARTIFACTS",
        },
        "blockers": [
            "no 54-row distributional two-point kernel",
            "no full-field complex structure or covariance operator",
            "no microlocal wavefront-set proof",
            "no BRST Ward proof for a two-point kernel",
            "no smooth treatment of retained zero-frequency modes",
            "no covariant positivity/Krein policy tied to the BV pairing",
        ],
        "claim_flags": {
            "BERGER_CAUSAL_COMMUTATOR_AVAILABLE": True,
            "BERGER_REDUCED_POSITIVE_FREQUENCY_LEDGER_AVAILABLE": True,
            "BERGER_BASE_WAVE_HADAMARD_PARAMETRIX": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_HADAMARD_DATA": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
            "LORENTZIAN_QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_BASE_WAVE_HADAMARD_PARAMETRIX",
        "provenance": {
            "causal_result_id": causal["result_id"],
            "polarized_schema": polarized["schema"],
            "Krein_schema": krein["schema"],
        },
        "claim_boundary": (
            "The repaired causal v2 chain supplies the full classical commutator "
            "infrastructure, while the existing positive-frequency and Krein ledgers "
            "remain reduced-mode state-side evidence. No distributional 54-row "
            "two-point kernel, Hadamard wavefront theorem, BRST-compatible covariance, "
            "renormalized product, QME restoration or quantum result is claimed."
        ),
    }
    validate_gate(result)
    return result


def validate_gate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "BERGER_HADAMARD_CONSTRUCTION_GATE"
        or result.get("result_state")
        != "CAUSAL_COMMUTATOR_READY_REDUCED_POLARIZATION_ONLY_HADAMARD_KERNEL_OPEN"
        or result.get("dependency_tags")
        != ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"]
        or result.get("classical_commit")
        != "743183594a7a33dbb869154dafd7eb2c3482bac0"
        or result.get("next_gate") != "BERGER_BASE_WAVE_HADAMARD_PARAMETRIX"
    ):
        raise ValueError("Hadamard gate identity drifted")
    route = result.get("construction_route", [])
    if len(route) != 6 or route[0].get("status") != "NEXT" or any(
        row.get("status") != "BLOCKED_PREVIOUS_STAGE" for row in route[1:]
    ):
        raise ValueError("Hadamard construction ordering drifted")
    if result.get("required_kernel_export", {}).get("required_checks") != list(
        REQUIRED_HADAMARD_CHECKS
    ):
        raise ValueError("Hadamard proof obligations drifted")
    expected_true = {
        "BERGER_CAUSAL_COMMUTATOR_AVAILABLE",
        "BERGER_REDUCED_POSITIVE_FREQUENCY_LEDGER_AVAILABLE",
    }
    flags = result.get("claim_flags", {})
    if {name for name, value in flags.items() if value is True} != expected_true:
        raise ValueError("Hadamard lifecycle was over-promoted")
    separation = result.get("logical_separation", {})
    if (
        separation.get("reduced_positive_frequency_is_full_Hadamard_evidence")
        is not False
        or separation.get(
            "reduced_Krein_completion_is_covariant_distributional_completion"
        )
        is not False
    ):
        raise ValueError("reduced-mode evidence was promoted to Hadamard evidence")
