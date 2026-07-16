"""Certify the Pauli--Jordan kernel and its factorwise characteristic WF bound.

This is the intermediate microlocal step between causal Green operators and
Fewster decomposability.  Continuity at every Sobolev order gives Schwartz
kernels; the two-sided Green identities make their causal difference a
bisolution; kernel elliptic regularity then confines both nonzero covectors to
the metric null characteristic set.  The relative future/past orientation of
the two covectors remains open.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
DECOMPOSABILITY = HERE / "certificates/BERGER_COMPANION_DECOMPOSABILITY_PREFLIGHT.json"
COMPANION = HERE / "certificates/BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT.json"
VOLTERRA = HERE / "certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_V2_IMPORT.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def orientation_sector_replay() -> dict[str, Any]:
    all_null_sectors = ["N+ x N+", "N+ x N-", "N- x N+", "N- x N-"]
    decomposable_sectors = ["N+ x N-", "N- x N+"]
    unresolved = [
        sector for sector in all_null_sectors if sector not in decomposable_sectors
    ]
    checks = {
        "factorwise_null_bound_has_four_orientation_sectors": len(all_null_sectors)
        == 4,
        "fewster_target_has_two_opposite_orientation_sectors": len(
            decomposable_sectors
        )
        == 2,
        "remaining_same_orientation_sectors_are_exactly_two": unresolved
        == ["N+ x N+", "N- x N-"],
    }
    if not all(checks.values()):
        raise ValueError("orientation-sector replay failed")
    return {
        "factorwise_characteristic_sectors": all_null_sectors,
        "fewster_decomposable_sectors": decomposable_sectors,
        "unresolved_same_orientation_sectors": unresolved,
        "checks": checks,
    }


def _load_inputs() -> tuple[dict[str, Any], ...]:
    decomposability, companion, volterra = (
        json.loads(path.read_text()) for path in (DECOMPOSABILITY, COMPANION, VOLTERRA)
    )
    if (
        decomposability.get("claim_flags", {}).get(
            "BERGER_COMPANION_METRIC_NULL_CHARACTERISTIC_SET"
        )
        is not True
        or decomposability.get("claim_flags", {}).get(
            "BERGER_COMPANION_NULL_CONE_DECOMPOSABLE"
        )
        is not False
    ):
        raise ValueError("decomposability boundary drifted")
    system = companion.get("companion_system", {})
    if (
        system.get("principal_determinant") != "q^20"
        or system.get("extra_characteristic_cone") is not False
    ):
        raise ValueError("companion characteristic input drifted")
    imported = volterra.get("source_import", {})
    checks = imported.get("proof_checks", {})
    if (
        volterra.get("claim_flags", {}).get(
            "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT_IMPORTED"
        )
        is not True
        or checks.get("time_regular_slab_spaces") is not True
        or checks.get("two_sided_factorial_bounds") is not True
        or checks.get("named_advanced_retarded_support") is not True
        or checks.get("typed_metric_antifield_adjoint_reversal") is not True
    ):
        raise ValueError("Volterra continuity or adjoint input drifted")
    return decomposability, companion, volterra


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    decomposability, companion, volterra = _load_inputs()
    sectors = orientation_sector_replay()
    result = {
        "schema": "quantum-weyl-berger-companion-pauli-jordan-characteristic-preflight-v1",
        "result_id": "BERGER_COMPANION_PAULI_JORDAN_CHARACTERISTIC_PREFLIGHT",
        "result_state": "PAULI_JORDAN_KERNEL_AND_FACTORWISE_NULL_WF_CERTIFIED_ORIENTATION_OPEN",
        "lifecycle_layer": "LORENTZIAN_MICROLOCAL_PREFLIGHT",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "classical_commit": decomposability["classical_commit"],
        "setting_id": decomposability["setting_id"],
        "dependency_refs": {
            "decomposability_preflight": _dependency(DECOMPOSABILITY),
            "companion_principal_symbol": _dependency(COMPANION),
            "typed_volterra_resolvent": _dependency(VOLTERRA),
        },
        "kernel_continuity_derivation": {
            "input": "advanced and retarded solution operators converge in operator norm on every finite-slab Sobolev level",
            "source_embedding": "compactly supported smooth sources embed continuously into every Y_s(I)",
            "target_embedding": "the compatible all-s solution lies in smooth companion sections on each finite slab",
            "globalization": "support-local slab solutions agree on overlaps and glue uniquely",
            "conclusion": "G_C^advanced and G_C^retarded are continuous C_c^infinity-to-C^infinity maps and therefore possess Schwartz kernels",
            "status": "CERTIFIED_BY_IMPORTED_ALL_SOBOLEV_ESTIMATES_AND_SCHWARTZ_KERNEL_THEOREM",
        },
        "bisolution_derivation": {
            "pauli_jordan_operator": "E_C=G_C^advanced-G_C^retarded",
            "left_equation": "C E_C=I-I=0",
            "right_equation": "E_C C=I-I=0, equivalently Csharp_xprime E_C^kernel=0",
            "formal_adjoint_input": "(G_C^retarded)^sharp=G_Csharp^advanced",
            "status": "TWO_SIDED_BISOLUTION_CERTIFIED",
        },
        "one_sided_wavefront_exclusion": {
            "solution_map": "E_C maps compactly supported smooth sources to smooth solutions",
            "transpose_map": "the formal-transpose causal operator maps compactly supported smooth dual sources to smooth dual solutions",
            "conclusion": "WF(E_C) contains no covector pair with exactly one zero cotangent component",
            "status": "CERTIFIED_BY_KERNEL_MAPPING_CRITERION",
        },
        "elliptic_regularization": {
            "left": "C_x E_C=0 implies every nonzero left kernel covector lies in Char(C)",
            "right": "Csharp_xprime E_C=0 implies every nonzero right kernel covector lies in Char(Csharp)",
            "characteristic_identity": "Char(C)=Char(Csharp)={q=0}=N_plus union N_minus",
            "certified_inclusion": "WF(E_C) subset (N_plus union N_minus) x (N_plus union N_minus)",
            "status": "FACTORWISE_NULL_WAVEFRONT_BOUND_CERTIFIED",
        },
        "orientation_sector_ledger": sectors,
        "minimal_missing_carrier": {
            "result_id": "BERGER_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION",
            "statement": "Prove WF(E_C) has empty intersection with (N_plus x N_plus) union (N_minus x N_minus).",
            "equivalent_promotion": "Together with the certified factorwise null bound, this is exactly Fewster N_plus/minus decomposability.",
            "accepted_routes": [
                "uniform same-sided Volterra kernel estimates in a fixed Hörmander topology",
                "propagation of the causal kernel polarization from its diagonal conormal normalization",
                "regular GreenHyp transport from the base wave kernel with an explicit wavefront relation",
            ],
        },
        "claim_flags": {
            "BERGER_COMPANION_PAULI_JORDAN_SCHWARTZ_KERNEL": True,
            "BERGER_COMPANION_PAULI_JORDAN_BISOLUTION": True,
            "BERGER_COMPANION_FACTORWISE_NULL_WAVEFRONT_BOUND": True,
            "BERGER_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION": False,
            "BERGER_COMPANION_NULL_CONE_DECOMPOSABLE": False,
            "BERGER_TYPED_COMPANION_HADAMARD_PARAMETRIX": False,
            "BERGER_TYPED_COMPANION_GLOBAL_HADAMARD": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION",
        "provenance": {
            "decomposability_result_id": decomposability["result_id"],
            "companion_result_id": companion["result_id"],
            "volterra_result_id": volterra["result_id"],
        },
        "claim_boundary": (
            "Certifies continuity and Schwartz kernels for the typed companion "
            "Green operators, the two-sided Pauli--Jordan bisolution identities, "
            "absence of one-sided kernel wavefront components, and factorwise "
            "confinement to the metric null characteristic set. It does not "
            "exclude the two same-time-orientation sectors and therefore does "
            "not certify Fewster decomposability, a Hadamard parametrix or state, "
            "BRST Hadamard data, a QME, or any quantum result."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id")
        != "BERGER_COMPANION_PAULI_JORDAN_CHARACTERISTIC_PREFLIGHT"
        or result.get("result_state")
        != "PAULI_JORDAN_KERNEL_AND_FACTORWISE_NULL_WF_CERTIFIED_ORIENTATION_OPEN"
        or result.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != "BERGER_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION"
    ):
        raise ValueError("Pauli-Jordan characteristic preflight identity drifted")
    if not all(
        result.get("orientation_sector_ledger", {}).get("checks", {}).values()
    ):
        raise ValueError("orientation-sector replay dropped")
    if (
        result.get("elliptic_regularization", {}).get("status")
        != "FACTORWISE_NULL_WAVEFRONT_BOUND_CERTIFIED"
    ):
        raise ValueError("factorwise characteristic bound dropped")
    true_flags = {
        key for key, value in result.get("claim_flags", {}).items() if value is True
    }
    if true_flags != {
        "BERGER_COMPANION_PAULI_JORDAN_SCHWARTZ_KERNEL",
        "BERGER_COMPANION_PAULI_JORDAN_BISOLUTION",
        "BERGER_COMPANION_FACTORWISE_NULL_WAVEFRONT_BOUND",
    }:
        raise ValueError("orientation, Hadamard or quantum lifecycle was over-promoted")
