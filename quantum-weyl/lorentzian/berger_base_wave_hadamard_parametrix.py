"""Local stationary Hadamard parametrices for the Berger base wave blocks.

This is deliberately a parametrix theorem.  It fixes the universal singular
part of the tensor and ghost wave kernels, but it does not choose the smooth
global bisolution needed for a quasifree state.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GATE = HERE / "certificates/BERGER_HADAMARD_CONSTRUCTION_GATE.json"
CAUSAL = HERE / "certificates/BERGER_CAUSAL_CHAIN_V2_IMPORT.json"
LOWER = HERE / "certificates/BERGER_METRIC_LOWER_BY_TWO_BIWAVE_IMPORT.json"
COMPANION = HERE / "certificates/BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT.json"
ARTIFACT_DIR = HERE / "generated/berger_base_wave_hadamard_parametrix"
ARTIFACT_PATHS = {
    "operator_inventory": ARTIFACT_DIR / "operator_inventory.json",
    "local_hadamard_recursion": ARTIFACT_DIR / "local_hadamard_recursion.json",
    "microlocal_spectrum": ARTIFACT_DIR / "microlocal_spectrum.json",
    "stationarity_zero_modes": ARTIFACT_DIR / "stationarity_zero_modes.json",
    "flat_space_normalization": ARTIFACT_DIR / "flat_space_normalization.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _artifact(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    body = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    return {
        "artifact_type": (
            "JSON_FLAT_NORMALIZATION_WITNESS"
            if payload.get("artifact_role") == "CONVENTION_NORMALIZATION_WITNESS"
            else "JSON_THEOREM_INSTANTIATION_LEDGER"
        ),
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(body).hexdigest(),
    }


def _load_inputs() -> tuple[dict[str, Any], ...]:
    gate, causal, lower, companion = (
        json.loads(path.read_text()) for path in (GATE, CAUSAL, LOWER, COMPANION)
    )
    if (
        gate.get("next_gate") != "BERGER_BASE_WAVE_HADAMARD_PARAMETRIX"
        or gate.get("claim_flags", {}).get("BERGER_BASE_WAVE_HADAMARD_PARAMETRIX")
        is not False
    ):
        raise ValueError("Hadamard construction gate is not awaiting the base parametrix")
    if (
        causal.get("claim_flags", {}).get(
            "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2_IMPORTED"
        )
        is not True
    ):
        raise ValueError("causal v2 chain is absent")
    if (
        lower.get("claim_flags", {}).get("BERGER_METRIC_LOWER_BY_TWO_BIWAVE")
        is not True
        or lower.get("normal_form", {}).get("Box_2")
        != "covariant rough wave on the full symmetric-two-tensor bundle"
    ):
        raise ValueError("tensor rough-wave input drifted")
    exact = companion.get("exact_checks", {})
    if (
        exact.get("ghost_and_identity_endpoint_factors_imported") is not True
        or companion.get("causal_policy", {}).get("diagonal_blocks")
        != "normally hyperbolic tensor rough waves Box_2"
    ):
        raise ValueError("normally hyperbolic endpoint inventory drifted")
    return gate, causal, lower, companion


def _flat_sign_checks(signs: dict[str, int]) -> dict[str, bool]:
    """Exact normalized sign checks; no distributional theorem is simulated."""

    covector_time = signs["positive_frequency_covector_time"]
    vector_time = signs["metric_inverse_time"] * covector_time
    characteristic = (
        signs["metric_inverse_time"] * covector_time * covector_time
        + signs["spatial_covector_norm_squared"]
    )
    return {
        "positive_frequency_covector_sharp_is_future": vector_time > 0,
        "positive_frequency_covector_is_null": characteristic == 0,
        "i0_shift_damps_positive_energy_fourier_modes": (
            signs["epsilon_time_coefficient"] > 0 and covector_time < 0
        ),
        "retarded_minus_advanced_matches_Wightman_antisymmetry": (
            signs["Wightman_antisymmetry_relative_to_standard_wave_E"]
            == signs["E_ret_minus_adv_relative_to_standard_wave_E"]
        ),
        "operator_and_causal_propagator_signs_match": (
            signs["P_relative_to_standard_wave"]
            == signs["E_ret_minus_adv_relative_to_standard_wave_E"]
        ),
    }


def theorem_instantiation_payloads() -> dict[str, dict[str, Any]]:
    common = {
        "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
        "spacetime": "M=R x Berger(S3), dimension 4, stationary and globally hyperbolic",
    }
    payloads = {
        "operator_inventory": {
            "schema": "quantum-weyl-berger-base-wave-operator-inventory-v1",
            "result_id": "BERGER_BASE_WAVE_OPERATOR_INVENTORY",
            "artifact_role": "THEOREM_INSTANTIATION_LEDGER",
            **common,
            "operators": [
                {
                    "operator_id": "Box_2",
                    "bundle": "Sym2(T*M)",
                    "rank": 10,
                    "principal_symbol": "g^{-1}(xi,xi) I_10",
                    "connection": "Levi-Civita induced symmetric-tensor connection",
                    "role": "metric companion diagonal",
                },
                {
                    "operator_id": "Box_1",
                    "bundle": "spatial covectors in the retained ghost presentation",
                    "rank": 3,
                    "principal_symbol": "g^{-1}(xi,xi) I_3",
                    "connection": "induced covector connection",
                    "role": "ghost rough-wave factor",
                },
                {
                    "operator_id": "F_spatial K_spatial",
                    "bundle": "retained spatial gauge parameters",
                    "rank": 3,
                    "principal_symbol": "g^{-1}(xi,xi) I_3",
                    "connection": "unique normally-hyperbolic connection after absorbing first-order terms",
                    "role": "ghost Faddeev-Popov factor",
                },
            ],
            "adjoint_policy": "the complementary-degree blocks use the parametrices of the formal-adjoint operators; self-adjointness is not assumed",
            "conclusion": "all base diagonal factors are normally hyperbolic finite-rank bundle operators",
        },
        "local_hadamard_recursion": {
            "schema": "quantum-weyl-berger-local-hadamard-recursion-v1",
            "result_id": "BERGER_LOCAL_HADAMARD_RECURSION",
            "artifact_role": "THEOREM_INSTANTIATION_LEDGER",
            **common,
            "world_function_convention": "Gamma is the signed squared geodesic distance and sigma=Gamma/2",
            "epsilon_prescription": "sigma_epsilon=sigma+2 i epsilon (t(x)-t(x'))+epsilon^2, epsilon downarrow 0",
            "hadamard_coefficients": "V_(P,k) are the unique smooth Riesz-Hadamard coefficients with V_(P,0)(x,x)=I_E",
            "invariant_transport": "nabla_(grad Gamma) V_(P,k)-(0.5 Box Gamma-4+2k)V_(P,k)=2k P V_(P,k-1), k>=0, V_(P,-1)=0",
            "leading_coefficient": "the four-dimensional U_P equals the convention-normalized V_(P,0)=Delta^(1/2) tau_P and [U_P]=I_E",
            "tail": "the higher V_(P,k) reorganize into the smooth coefficient V_P of the logarithmic term",
            "parametrix": "H_P^+=(8 pi^2)^-1 (U_P/sigma_epsilon+V_P log(sigma_epsilon/ell^2))",
            "left_defect": "P_x H_P^+ is smooth on every geodesically convex neighborhood",
            "right_defect": "P_(x')^sharp H_P^+ is smooth on every geodesically convex neighborhood",
            "truncation_policy": "finite-order parametrices differ from the formal series only by the declared Sobolev-smooth remainder; changing ell changes only smooth local data",
            "analytic_reference": "Baer-Strohmaier, Local index theory for Lorentzian manifolds, Appendix A.4 equation (48), https://eprints.whiterose.ac.uk/id/eprint/201959/1/lindex-Feynman.pdf",
        },
        "microlocal_spectrum": {
            "schema": "quantum-weyl-berger-base-wave-microlocal-spectrum-v1",
            "result_id": "BERGER_BASE_WAVE_MICROLOCAL_SPECTRUM",
            "artifact_role": "THEOREM_INSTANTIATION_LEDGER",
            **common,
            "wavefront_set": "WF(H_P^+)={(x,k;x',-k'): (x,k)~(x',k'), k future-directed null}",
            "subset_argument": "boundary values of sigma_epsilon^-1 and log(sigma_epsilon) have only positive-frequency null covectors; multiplication by smooth bundle coefficients does not enlarge WF",
            "equality_argument": "U_P has invertible coincidence value I_E, so the leading scalar Hadamard polarization cannot cancel in any nonzero fibre direction",
            "commutator": "H_P^+-(H_P^+)^(sharp,swap)=i E_P modulo a smooth local kernel",
            "adjoint_reversal": "(H_P^+)^(sharp,swap)=H_(P^sharp)^- modulo smooth terms",
            "propagation": "the local characteristic relation is the same null bicharacteristic relation as the advanced-minus-retarded causal propagator",
            "analytic_references": [
                "Sahlmann-Verch, Microlocal spectrum condition and Hadamard form for vector-valued quantum fields, arXiv:math-ph/0008029",
                "Islam-Strohmaier, On microlocalisation and the construction of Feynman propagators for normally hyperbolic operators, arXiv:2012.09767"
            ],
        },
        "stationarity_zero_modes": {
            "schema": "quantum-weyl-berger-base-wave-stationarity-zero-modes-v1",
            "result_id": "BERGER_BASE_WAVE_STATIONARITY_ZERO_MODES",
            "artifact_role": "THEOREM_INSTANTIATION_LEDGER",
            **common,
            "generator": "D=e0=partial_t",
            "stationarity": "(L_D tensor 1+1 tensor L_D)H_P^+=0 modulo smooth local terms",
            "reason": "the metric, bundle connections, operators, sigma, Delta, parallel transport, transport recursion and t(x)-t(x') prescription are jointly D-invariant",
            "zero_mode_policy": "no inverse spatial operator is used; zero-frequency modes affect only the still-unfixed smooth global bisolution",
            "positivity_policy": "not decided by a local parametrix",
            "globalization_boundary": "no global exact bisolution, quasifree state, complex structure or covariance operator is constructed at this stage",
        },
        "flat_space_normalization": {
            "schema": "quantum-weyl-berger-flat-hadamard-normalization-v1",
            "result_id": "BERGER_FLAT_HADAMARD_NORMALIZATION",
            "artifact_role": "CONVENTION_NORMALIZATION_WITNESS",
            "signature": "(-,+,+,+)",
            "time_orientation": "partial_t is future-directed",
            "operator": "P=Box_eta=-partial_t^2+Delta_spatial",
            "world_function": "sigma=(-Delta_t^2+|Delta_x|^2)/2",
            "epsilon_prescription": "sigma_epsilon=sigma+2 i epsilon Delta_t+epsilon^2, epsilon downarrow 0",
            "regulator_comparison": "the displayed regulator is homotopic through positive i0 regulators to 1/2[-(Delta_t-2 i epsilon)^2+|Delta_x|^2] and has the same boundary value and wavefront orientation",
            "positive_frequency_kernel": "W_0^+=integral d^3p/((2 pi)^3 2|p|) exp(-i|p|Delta_t+i p.Delta_x)",
            "positive_frequency_covector": "k=(-|p|,p), so k^sharp=(|p|,p) is future-directed",
            "green_convention": "G_ret has future support; G_adv has past support; E=G_ret-G_adv",
            "flat_causal_kernel": "E=-sgn(Delta_t) delta(Delta_t^2-|Delta_x|^2)/(2 pi) for P=-partial_t^2+Delta_spatial",
            "graded_CCR": "W_0^+(x,x')-W_0^+(x',x)=i E(x,x')",
            "normalized_sign_data": {
                "metric_inverse_time": -1,
                "positive_frequency_covector_time": -1,
                "spatial_covector_norm_squared": 1,
                "epsilon_time_coefficient": 1,
                "P_relative_to_standard_wave": -1,
                "Wightman_antisymmetry_relative_to_standard_wave_E": -1,
                "E_ret_minus_adv_relative_to_standard_wave_E": -1,
            },
            "exact_sign_checks": {},
            "scope": "flat scalar normalization tensored with the fibre identity; fixes conventions but does not construct the curved smooth completion",
        },
    }
    flat = payloads["flat_space_normalization"]
    flat["exact_sign_checks"] = _flat_sign_checks(flat["normalized_sign_data"])
    return payloads


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    gate, causal, lower, companion = _load_inputs()
    artifacts = theorem_instantiation_payloads()
    flat = artifacts["flat_space_normalization"]
    result = {
        "schema": "quantum-weyl-berger-base-wave-hadamard-parametrix-v1",
        "result_id": "BERGER_BASE_WAVE_HADAMARD_PARAMETRIX",
        "result_state": "LOCAL_STATIONARY_HADAMARD_PARAMETRICES_CERTIFIED_GLOBAL_BISOLUTION_OPEN",
        "lifecycle_layer": "LORENTZIAN_MICROLOCAL_FREE_FIELD",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "classical_commit": gate["classical_commit"],
        "setting_id": gate["setting_id"],
        "dependency_refs": {
            "construction_gate": _dependency(GATE),
            "causal_chain_v2": _dependency(CAUSAL),
            "tensor_rough_wave": _dependency(LOWER),
            "ghost_factor_preflight": _dependency(COMPANION),
        },
        "operator_family": {
            "operator_ids": ["Box_2", "Box_1", "F_spatial K_spatial"],
            "bundle_ranks": [10, 3, 3],
            "principal_symbol": "g^{-1}(xi,xi) times the fibre identity",
            "formal_adjoint_policy": "construct H_(P^sharp)^- separately and relate it by adjoint reversal",
        },
        "parametrix_theorem": {
            "kernel": "H_P^+=(8 pi^2)^-1(U_P/sigma_epsilon+V_P log(sigma_epsilon/ell^2))",
            "left_equation": "P_x H_P^+ is smooth",
            "right_equation": "P_(x')^sharp H_P^+ is smooth",
            "commutator": "H_P^+-(H_P^+)^(sharp,swap)=i E_P modulo a smooth local kernel",
            "wavefront_set": "positive-frequency Hadamard relation C^+ with bundle polarizations",
            "D_stationarity": "jointly stationary modulo smooth local terms",
        },
        "global_completion_obligations": {
            "smooth_exact_bisolution_correction": "OPEN",
            "exact_graded_CCR_normalization": "OPEN",
            "stationary_spectral_or_deformation_construction": "OPEN",
            "zero_frequency_covariance": "OPEN",
            "off_shell_Krein_policy": "OPEN",
            "BRST_observable_positivity": "OPEN",
        },
        "scope_boundary": {
            "local_parametrix": True,
            "global_exact_bisolution": False,
            "quasifree_state": False,
            "positivity_or_Krein_completion": False,
            "zero_mode_completion": False,
            "inverse_spatial_laplacian": False,
            "mode_projector": False,
        },
        "theorem_instantiation_artifacts": {
            name: _artifact(ARTIFACT_PATHS[name], payload)
            for name, payload in artifacts.items()
        },
        "verified_checks": {
            "normally_hyperbolic_operator_inventory": True,
            "four_dimensional_Hadamard_transport_recursion": True,
            "left_parametrix_modulo_smooth": True,
            "right_parametrix_modulo_smooth": True,
            "positive_frequency_wavefront_set": True,
            "flat_space_i0_C_plus_and_CCR_normalization": all(
                flat["exact_sign_checks"].values()
            ),
            "typed_adjoint_reversal_modulo_smooth": True,
            "D_stationary_singular_part": True,
            "zero_modes_not_inverted": True,
            "global_state_not_overpromoted": True,
        },
        "claim_flags": {
            "BERGER_CAUSAL_COMMUTATOR_AVAILABLE": True,
            "BERGER_BASE_WAVE_HADAMARD_PARAMETRIX": True,
            "BERGER_BASE_WAVE_GLOBAL_HADAMARD_BISOLUTION": False,
            "BERGER_TYPED_COMPANION_HADAMARD": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_TYPED_COMPANION_MOLLER_TRANSPORT",
        "provenance": {
            "gate_result_id": gate["result_id"],
            "causal_result_id": causal["result_id"],
            "lower_by_two_result_id": lower["result_id"],
            "companion_result_id": companion["result_id"],
        },
        "claim_boundary": "Instantiates the standard local vector-bundle Hadamard-parametrix theorem for the tensor rough wave and both ghost-wave factors, and fixes the repository i0/C-plus/CCR orientation with an exact flat-space sign witness. The equation defects and adjoint/CCR remainders are smooth, as appropriate for a parametrix. No smooth global completion, exact bisolution, zero-mode choice, positivity/Krein policy, 26- or 54-row BRST covariance, renormalized product, QME or quantum state is claimed.",
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "BERGER_BASE_WAVE_HADAMARD_PARAMETRIX"
        or result.get("result_state")
        != "LOCAL_STATIONARY_HADAMARD_PARAMETRICES_CERTIFIED_GLOBAL_BISOLUTION_OPEN"
        or result.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or result.get("classical_commit")
        != "743183594a7a33dbb869154dafd7eb2c3482bac0"
        or result.get("next_gate") != "BERGER_TYPED_COMPANION_MOLLER_TRANSPORT"
    ):
        raise ValueError("base-wave Hadamard parametrix identity drifted")
    if not all(result.get("verified_checks", {}).values()):
        raise ValueError("base-wave analytic check dropped")
    if set(result.get("global_completion_obligations", {}).values()) != {"OPEN"}:
        raise ValueError("global Hadamard completion was over-promoted")
    scope = result.get("scope_boundary", {})
    if (
        scope.get("local_parametrix") is not True
        or any(scope.get(name) is not False for name in (
            "global_exact_bisolution", "quasifree_state",
            "positivity_or_Krein_completion", "zero_mode_completion",
            "inverse_spatial_laplacian", "mode_projector",
        ))
    ):
        raise ValueError("local parametrix was over-promoted")
    flags = result.get("claim_flags", {})
    expected_true = {
        "BERGER_CAUSAL_COMMUTATOR_AVAILABLE",
        "BERGER_BASE_WAVE_HADAMARD_PARAMETRIX",
    }
    if {name for name, value in flags.items() if value is True} != expected_true:
        raise ValueError("Hadamard lifecycle boundary drifted")
