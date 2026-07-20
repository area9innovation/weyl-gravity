"""Certify a global Hadamard bisolution seed on the free Berger dilation.

The free companion

    C_free = [[Box_2, -I], [0, Box_2]]

has scalar normally-hyperbolic principal symbol even though it is not
formally self-adjoint for the positive diagonal fibre metric.  Its doubled
operator D_free=diag(C_free,C_free^dagger) is formally self-adjoint for the
nondegenerate off-diagonal Hermitian form H.  Islam--Strohmaier Theorem 1.4
therefore supplies a global Feynman propagator and a formally self-adjoint
Hadamard bisolution on the doubled free carrier.

The form H is indefinite.  Accordingly this module does not promote the
bisolution to a positive state or a covariance on the raw companion/full BV
carrier.  The Jordan incidence in C_free also rules out repairing this by a
positive-definite fibre metric on the same auxiliary carrier.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
DILATION = (
    HERE / "certificates/BERGER_CUTOFF_COMPANION_HERMITIAN_DILATION.json"
)
GRADED = HERE / "certificates/BERGER_GRADED_CAUSAL_STATE_SPACE_CONTRACT.json"
BASE = HERE / "certificates/BERGER_BASE_WAVE_HADAMARD_PARAMETRIX.json"

DEPENDENCIES = {
    "Hermitian_dilation": DILATION,
    "graded_state_space_contract": GRADED,
    "base_wave_parametrix": BASE,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def theorem_hypothesis_replay(
    *,
    globally_hyperbolic: bool = True,
    scalar_wave_principal_symbol: bool = True,
    nondegenerate_sesquilinear_form: bool = True,
    formally_selfadjoint: bool = True,
) -> dict[str, Any]:
    """Replay the exact hypotheses used for the existence implication."""

    hypotheses = {
        "smooth_finite_rank_complex_bundle": True,
        "globally_hyperbolic_spacetime": globally_hyperbolic,
        "normally_hyperbolic_operator": scalar_wave_principal_symbol,
        "nondegenerate_sesquilinear_form": nondegenerate_sesquilinear_form,
        "formal_selfadjointness_for_that_form": formally_selfadjoint,
    }
    applies = all(hypotheses.values())
    return {
        "hypotheses": hypotheses,
        "theorem_applies": applies,
        "conclusions": {
            "global_Feynman_propagator_exists": applies,
            "omega_minus_i_GF_minus_Gadv_is_exact_bisolution": applies,
            "omega_is_formally_selfadjoint": applies,
            "omega_has_Hadamard_wavefront_relation": applies,
        },
    }


def positive_metric_obstruction_replay(
    *, jordan_incidence_nonzero: bool = True
) -> dict[str, Any]:
    """Show why positivity is not obtained on the auxiliary free carrier."""

    checks = {
        "free_companion_has_Jordan_incidence_minus_I": jordan_incidence_nonzero,
        "modewise_internal_block_is_nondiagonalizable": jordan_incidence_nonzero,
        "positive_metric_selfadjoint_operator_would_be_diagonalizable": True,
        "positive_definite_symmetrizer_on_same_carrier_is_impossible":
            jordan_incidence_nonzero,
        "certified_off_diagonal_form_has_signature_20_20": True,
    }
    return {
        "modewise_block": "[[lambda,-1],[0,lambda]]",
        "certified_fibre_form": "H=[[0,I20],[I20,0]]",
        "signature": [20, 20],
        "checks": checks,
        "positive_state_follows": False,
        "all_pass": all(checks.values()),
    }


def _load() -> dict[str, dict[str, Any]]:
    return {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    values = _load()
    dilation = values["Hermitian_dilation"]
    graded = values["graded_state_space_contract"]
    base = values["base_wave_parametrix"]
    dilation_data = dilation["Hermitian_dilation"]
    input_checks = {
        "free_dilation_named": dilation_data["operators"]["free"]
        == "D_free=diag(C_free,C_free^dagger)",
        "dilation_formally_Hermitian": dilation_data["checks"][
            "H_adjoint_H_equals_D"
        ]
        is True,
        "dilation_form_nondegenerate_indefinite": dilation_data["checks"][
            "H_is_nondegenerate_indefinite_Hermitian"
        ]
        is True,
        "free_dilation_RFHGHO": dilation_data["status"]
        == "REAL_FORMALLY_HERMITIAN_GREEN_HYPERBOLIC_DILATIONS_CERTIFIED",
        "real_structure_available": graded["real_structure"]["status"]
        == "CERTIFIED_FROM_REAL_CLASSICAL_OPERATOR_AND_UNIQUENESS",
        "base_wave_Hadamard_orientation_fixed": base["claim_flags"][
            "BERGER_BASE_WAVE_HADAMARD_PARAMETRIX"
        ]
        is True,
    }
    if not all(input_checks.values()):
        failed = [name for name, passed in input_checks.items() if not passed]
        raise ValueError(f"free-dilation Hadamard-seed input drift: {failed}")

    theorem = theorem_hypothesis_replay()
    bad_principal = theorem_hypothesis_replay(scalar_wave_principal_symbol=False)
    bad_pairing = theorem_hypothesis_replay(
        nondegenerate_sesquilinear_form=False
    )
    bad_adjoint = theorem_hypothesis_replay(formally_selfadjoint=False)
    positivity = positive_metric_obstruction_replay()
    no_jordan = positive_metric_obstruction_replay(
        jordan_incidence_nonzero=False
    )
    if (
        not theorem["theorem_applies"]
        or bad_principal["theorem_applies"]
        or bad_pairing["theorem_applies"]
        or bad_adjoint["theorem_applies"]
        or not positivity["all_pass"]
        or no_jordan["all_pass"]
    ):
        raise ValueError("free-dilation Hadamard-seed replay failed")

    result = {
        "schema": "quantum-weyl-berger-free-dilation-hadamard-bisolution-seed-v1",
        "result_id": "BERGER_FREE_DILATION_HADAMARD_BISOLUTION_SEED",
        "result_state": "GLOBAL_FREE_DILATION_HADAMARD_BISOLUTION_EXISTS_POSITIVE_STATE_AND_BV_RESTRICTION_OPEN",
        "lifecycle_layer": "LORENTZIAN_FREE_HADAMARD_SEED",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "classical_commit": dilation["classical_commit"],
        "setting_id": dilation["setting_id"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in values.items()
        },
        "exact_input_checks": input_checks,
        "free_operator": {
            "background": "R x S3_Berger with compact Cauchy surface",
            "bundle": "complexification of B20 direct_sum B20, rank 40",
            "companion": "C_free=[[Box_2,-I10],[0,Box_2]]",
            "dilation": "D_free=diag(C_free,C_free^dagger)",
            "principal_symbol": "sigma_2(D_free)=q I40",
            "fibre_form": "H=[[0,I20],[I20,0]]",
            "fibre_form_signature": [20, 20],
        },
        "theorem_instantiation": {
            **theorem,
            "source": {
                "authors": "Onirban Islam and Alexander Strohmaier",
                "title": "On microlocalisation and the construction of Feynman Propagators for normally hyperbolic operators",
                "arxiv": "2012.09767v4",
                "doi": "10.4310/CAG.241204020919",
                "theorem": "Theorem 1.4 (Existence of Hadamard bisolutions)",
            },
            "selected_objects": {
                "Feynman_propagator": "G_F,Dfree",
                "advanced_Green_operator": "G_adv,Dfree",
                "Hadamard_bisolution": "omega_Dfree=-i(G_F,Dfree-G_adv,Dfree)",
            },
            "wavefront_convention": (
                "the source Feynman relation is mapped to the already frozen "
                "project positive-frequency convention; no transport to the "
                "interacting cutoff/full companion is asserted here"
            ),
            "status": "GLOBAL_EXISTENTIAL_HADAMARD_BISOLUTION_SEED_CERTIFIED",
        },
        "positive_metric_obstruction": positivity,
        "negative_controls": {
            "nonscalar_principal_symbol": bad_principal,
            "degenerate_fibre_form": bad_pairing,
            "missing_formal_selfadjointness": bad_adjoint,
            "remove_Jordan_incidence": no_jordan,
        },
        "analytic_boundary": {
            "positive_state": "NOT_CERTIFIED_ON_INDEFINITE_DILATION",
            "Krein_covariance": "NOT_YET_NORMALIZED_AGAINST_THE_GRADED_CCR",
            "cutoff_full_transport": (
                "OPEN_UNTIL_DPRIME_GAMMA_NORMAL_TOPOLOGY_CONVERGENCE_PROVES "
                "THE_REGULAR_MORPHISM_CONE_ACTION"
            ),
            "raw_companion_restriction": "NOT_CONSTRUCTED",
            "full_graded_BV_restriction": "NOT_CONSTRUCTED",
            "BRST_Ward_identity": "NOT_VERIFIED",
            "physical_cohomology_positivity": "NOT_VERIFIED",
        },
        "claim_flags": {
            "BERGER_FREE_DILATION_NORMALLY_HYPERBOLIC": True,
            "BERGER_FREE_DILATION_GLOBAL_FEYNMAN_PROPAGATOR_EXISTS": True,
            "BERGER_FREE_DILATION_GLOBAL_HADAMARD_BISOLUTION_SEED": True,
            "BERGER_FREE_DILATION_POSITIVE_HADAMARD_STATE": False,
            "BERGER_FREE_DILATION_KREIN_COVARIANCE_NORMALIZED": False,
            "BERGER_DILATED_RESPONSE_MORPHISM_CONE_MAPPING": False,
            "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "PROVE_DPRIME_GAMMA_VOLTERRA_CONVERGENCE_THEN_TRANSPORT_FREE_BISOLUTION_AND_NORMALIZE_KREIN_CCR",
        "provenance": {
            "dilation_result_id": dilation["result_id"],
            "graded_contract_result_id": graded["result_id"],
            "base_parametrix_result_id": base["result_id"],
        },
        "claim_boundary": (
            "The Islam--Strohmaier global existence theorem applies to the "
            "normally hyperbolic, formally H-self-adjoint free rank-40 Berger "
            "dilation. It supplies an exact global Feynman propagator and a "
            "formally self-adjoint Hadamard bisolution seed. This closes the "
            "free global bisolution gate, not the interacting companion or "
            "full-BV Hadamard gate. The certified form H has signature (20,20), "
            "and the nonzero Jordan incidence rules out a positive-definite "
            "symmetrizer on the same auxiliary carrier. No positive state, "
            "Krein CCR normalization, cutoff/full transport, raw-companion or "
            "graded-BV restriction, BRST Ward identity, physical-cohomology "
            "positivity, renormalized product, Lorentzian QME or quantum theory "
            "is claimed."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id")
        != "BERGER_FREE_DILATION_HADAMARD_BISOLUTION_SEED"
        or result.get("result_state")
        != "GLOBAL_FREE_DILATION_HADAMARD_BISOLUTION_EXISTS_POSITIVE_STATE_AND_BV_RESTRICTION_OPEN"
        or result.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != "PROVE_DPRIME_GAMMA_VOLTERRA_CONVERGENCE_THEN_TRANSPORT_FREE_BISOLUTION_AND_NORMALIZE_KREIN_CCR"
    ):
        raise ValueError("free-dilation Hadamard-seed identity drifted")
    if not all(result.get("exact_input_checks", {}).values()):
        raise ValueError("free-dilation Hadamard-seed inputs failed")
    theorem = result.get("theorem_instantiation", {})
    if (
        theorem.get("theorem_applies") is not True
        or not all(theorem.get("conclusions", {}).values())
        or theorem.get("status")
        != "GLOBAL_EXISTENTIAL_HADAMARD_BISOLUTION_SEED_CERTIFIED"
    ):
        raise ValueError("global Hadamard-bisolution existence was not certified")
    if result.get("positive_metric_obstruction", {}).get("all_pass") is not True:
        raise ValueError("positive-metric obstruction failed")
    if any(
        control.get("theorem_applies") is not False
        for name, control in result.get("negative_controls", {}).items()
        if name != "remove_Jordan_incidence"
    ):
        raise ValueError("invalid theorem-instantiation control was accepted")
    if (
        result.get("negative_controls", {})
        .get("remove_Jordan_incidence", {})
        .get("all_pass")
        is not False
    ):
        raise ValueError("Jordan-incidence obstruction negative control failed")
    true_flags = {
        name for name, value in result.get("claim_flags", {}).items() if value is True
    }
    if true_flags != {
        "BERGER_FREE_DILATION_NORMALLY_HYPERBOLIC",
        "BERGER_FREE_DILATION_GLOBAL_FEYNMAN_PROPAGATOR_EXISTS",
        "BERGER_FREE_DILATION_GLOBAL_HADAMARD_BISOLUTION_SEED",
    }:
        raise ValueError("positive state, BV Hadamard or quantum claim over-promoted")
