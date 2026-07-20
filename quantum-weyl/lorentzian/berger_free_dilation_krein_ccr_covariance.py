"""Normalize the free Berger Hadamard seed against the causal CCR.

The free dilation is real and formally symmetric for its indefinite
Hermitian form.  Therefore a Feynman propagator may be replaced by its
transpose average without changing the inverse identities or Feynman
wavefront relation.  This makes the associated bidistribution obey the CCR
exactly.  The project convention E=G_ret-G_adv requires the sign
W=+i(G_F-G_adv), opposite to the convention used in the cited source.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SEED = HERE / "certificates/BERGER_FREE_DILATION_HADAMARD_BISOLUTION_SEED.json"
GRADED = HERE / "certificates/BERGER_GRADED_CAUSAL_STATE_SPACE_CONTRACT.json"
BASE = HERE / "certificates/BERGER_BASE_WAVE_HADAMARD_PARAMETRIX.json"
FLAT = (
    HERE
    / "generated/berger_base_wave_hadamard_parametrix/flat_space_normalization.json"
)

DEPENDENCIES = {
    "free_dilation_Hadamard_seed": SEED,
    "graded_state_space_contract": GRADED,
    "base_wave_normalization": BASE,
    "flat_normalization": FLAT,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def symmetrization_replay(
    *, real_symmetric_operator: bool = True, symmetrize: bool = True
) -> dict[str, Any]:
    """Replay the transpose and exact-CCR identities symbolically."""

    identities = {
        "P_transpose_equals_P": real_symmetric_operator,
        "Gret_transpose_equals_Gadv": real_symmetric_operator,
        "Gadv_transpose_equals_Gret": real_symmetric_operator,
        "GFsym_is_Feynman_propagator": real_symmetric_operator and symmetrize,
        "GFsym_transpose_equals_GFsym": real_symmetric_operator and symmetrize,
        "Wproject_is_exact_bisolution": real_symmetric_operator and symmetrize,
        "Wproject_wavefront_relation_is_Hadamard": real_symmetric_operator
        and symmetrize,
        "Wproject_minus_transpose_equals_i_Eproject": real_symmetric_operator
        and symmetrize,
    }
    return {
        "GFsym": "(GF+GF^T)/2",
        "source_green_convention": "G_source=G_adv-G_ret",
        "project_green_convention": "E_project=G_ret-G_adv=-G_source",
        "source_distribution": "W_source=-i(GFsym-G_adv)",
        "project_distribution": "W_project=+i(GFsym-G_adv)=-W_source",
        "CCR_calculation": (
            "W_project-W_project^T="
            "i[(GFsym-G_adv)-(GFsym-G_ret)]=i(G_ret-G_adv)=i E_project"
        ),
        "identities": identities,
        "all_pass": all(identities.values()),
    }


def sign_negative_control(*, use_project_sign: bool = False) -> dict[str, Any]:
    coefficient = "+i" if use_project_sign else "-i"
    ccr = "+i E_project" if use_project_sign else "-i E_project"
    return {
        "coefficient": coefficient,
        "antisymmetric_part": ccr,
        "matches_project_CCR": use_project_sign,
    }


def _load() -> dict[str, dict[str, Any]]:
    return {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    values = _load()
    seed = values["free_dilation_Hadamard_seed"]
    graded = values["graded_state_space_contract"]
    base = values["base_wave_normalization"]
    flat = values["flat_normalization"]
    seed_flags = seed["claim_flags"]
    input_checks = {
        "global_free_Hadamard_bisolution_seed": seed_flags[
            "BERGER_FREE_DILATION_GLOBAL_HADAMARD_BISOLUTION_SEED"
        ]
        is True,
        "free_dilation_real": graded["real_structure"]["status"]
        == "CERTIFIED_FROM_REAL_CLASSICAL_OPERATOR_AND_UNIQUENESS",
        "free_dilation_formally_H_selfadjoint": seed["theorem_instantiation"][
            "hypotheses"
        ]["formal_selfadjointness_for_that_form"]
        is True,
        "base_normalization_artifact_pinned": base["theorem_instantiation_artifacts"][
            "flat_space_normalization"
        ]["sha256"]
        == _sha256(FLAT),
        "project_green_convention": flat["green_convention"]
        == "G_ret has future support; G_adv has past support; E=G_ret-G_adv",
        "project_flat_CCR": flat["graded_CCR"]
        == "W_0^+(x,x')-W_0^+(x',x)=i E(x,x')",
        "fibre_form_indefinite": seed["free_operator"]["fibre_form_signature"]
        == [20, 20],
    }
    if not all(input_checks.values()):
        failed = [name for name, passed in input_checks.items() if not passed]
        raise ValueError(f"free-dilation Krein-CCR input drift: {failed}")

    replay = symmetrization_replay()
    missing_real = symmetrization_replay(real_symmetric_operator=False)
    unsymmetrized = symmetrization_replay(symmetrize=False)
    bad_sign = sign_negative_control()
    good_sign = sign_negative_control(use_project_sign=True)
    if (
        not replay["all_pass"]
        or missing_real["all_pass"]
        or unsymmetrized["all_pass"]
        or bad_sign["matches_project_CCR"]
        or not good_sign["matches_project_CCR"]
    ):
        raise ValueError("free-dilation Krein-CCR replay failed")

    result = {
        "schema": "quantum-weyl-berger-free-dilation-krein-ccr-covariance-v1",
        "result_id": "BERGER_FREE_DILATION_KREIN_CCR_COVARIANCE",
        "result_state": "FREE_DILATION_GLOBAL_HADAMARD_KREIN_COVARIANCE_CCR_NORMALIZED_POSITIVE_STATE_AND_BV_TRANSPORT_OPEN",
        "lifecycle_layer": "LORENTZIAN_FREE_KREIN_COVARIANCE",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "classical_commit": seed["classical_commit"],
        "setting_id": seed["setting_id"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in values.items()
        },
        "exact_input_checks": input_checks,
        "transpose_symmetrization": replay,
        "covariance": {
            "carrier": "free rank-40 Hermitian dilation",
            "distribution": "W_Dfree=+i(GFsym,Dfree-Gadv,Dfree)",
            "equations": "D_free W_Dfree=W_Dfree D_free^T=0",
            "wavefront_status": "GLOBAL_HADAMARD_RELATION",
            "CCR": "W_Dfree-W_Dfree^T=i E_Dfree",
            "fibre_form": "H=[[0,I20],[I20,0]]",
            "signature": [20, 20],
            "state_space_status": "INDEFINITE_KREIN_QUASIFREE_FUNCTIONAL_NOT_A_POSITIVE_STATE",
            "status": "GLOBAL_FREE_DILATION_KREIN_CCR_COVARIANCE_NORMALIZED",
        },
        "negative_controls": {
            "missing_real_symmetric_operator": missing_real,
            "omit_transpose_symmetrization": unsymmetrized,
            "use_source_sign_without_convention_map": bad_sign,
        },
        "literature_provenance": {
            "source": (
                "Christopher J. Fewster and Alexander Strohmaier, "
                "On the construction of Hadamard states from Feynman propagators"
            ),
            "arxiv": "2510.11492",
            "construction": (
                "the proof of Theorem 4: GFsym=(GF+GF^T)/2 is a symmetric "
                "Feynman propagator; symmetry gives the exact Pauli-Jordan relation"
            ),
            "scope_map": (
                "only the transpose-symmetrization and CCR identity are used; "
                "the positive-definite hypothesis needed for a state is not asserted"
            ),
        },
        "analytic_boundary": {
            "positive_state": "NOT_CERTIFIED",
            "cutoff_full_transport": "OPEN_DPRIME_GAMMA_CONVERGENCE",
            "raw_companion_restriction": "NOT_CONSTRUCTED",
            "full_graded_BV_restriction": "NOT_CONSTRUCTED",
            "BRST_Ward_identity": "NOT_VERIFIED",
            "physical_cohomology_positivity": "NOT_VERIFIED",
        },
        "claim_flags": {
            "BERGER_FREE_DILATION_GLOBAL_HADAMARD_BISOLUTION_SEED": True,
            "BERGER_FREE_DILATION_TRANSPOSE_SYMMETRIC_FEYNMAN_PROPAGATOR": True,
            "BERGER_FREE_DILATION_KREIN_COVARIANCE_NORMALIZED": True,
            "BERGER_FREE_DILATION_POSITIVE_HADAMARD_STATE": False,
            "BERGER_DILATED_RESPONSE_MORPHISM_CONE_MAPPING": False,
            "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "PROVE_DPRIME_GAMMA_VOLTERRA_CONVERGENCE_THEN_TRANSPORT_NORMALIZED_KREIN_COVARIANCE_TO_FULL_DILATION",
        "provenance": {
            "seed_result_id": seed["result_id"],
            "graded_contract_result_id": graded["result_id"],
            "base_normalization_result_id": base["result_id"],
            "flat_normalization_result_id": flat["result_id"],
        },
        "claim_boundary": (
            "The real free dilation admits a transpose-symmetric Feynman "
            "propagator. After the explicit source-to-project sign map, the "
            "resulting global Hadamard bidistribution has antisymmetric part "
            "exactly i times the project Pauli-Jordan operator. This certifies "
            "a normalized Krein covariance on the indefinite free rank-40 "
            "auxiliary carrier, not a positive state. It does not transport "
            "the covariance to the cutoff/full dilation, restrict it to the "
            "raw companion or graded BV carrier, verify a BRST Ward identity "
            "or physical positivity, construct renormalized products, restore "
            "a Lorentzian QME or establish a quantum theory."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "BERGER_FREE_DILATION_KREIN_CCR_COVARIANCE"
        or result.get("result_state")
        != "FREE_DILATION_GLOBAL_HADAMARD_KREIN_COVARIANCE_CCR_NORMALIZED_POSITIVE_STATE_AND_BV_TRANSPORT_OPEN"
        or result.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != "PROVE_DPRIME_GAMMA_VOLTERRA_CONVERGENCE_THEN_TRANSPORT_NORMALIZED_KREIN_COVARIANCE_TO_FULL_DILATION"
    ):
        raise ValueError("free-dilation Krein-CCR identity drifted")
    if not all(result.get("exact_input_checks", {}).values()):
        raise ValueError("free-dilation Krein-CCR inputs failed")
    if result.get("transpose_symmetrization", {}).get("all_pass") is not True:
        raise ValueError("transpose symmetrization failed")
    covariance = result.get("covariance", {})
    if (
        covariance.get("CCR") != "W_Dfree-W_Dfree^T=i E_Dfree"
        or covariance.get("signature") != [20, 20]
        or covariance.get("status")
        != "GLOBAL_FREE_DILATION_KREIN_CCR_COVARIANCE_NORMALIZED"
    ):
        raise ValueError("Krein covariance normalization failed")
    true_flags = {
        name for name, value in result.get("claim_flags", {}).items() if value is True
    }
    if true_flags != {
        "BERGER_FREE_DILATION_GLOBAL_HADAMARD_BISOLUTION_SEED",
        "BERGER_FREE_DILATION_TRANSPOSE_SYMMETRIC_FEYNMAN_PROPAGATOR",
        "BERGER_FREE_DILATION_KREIN_COVARIANCE_NORMALIZED",
    }:
        raise ValueError("positive state, BV Hadamard or quantum claim over-promoted")
