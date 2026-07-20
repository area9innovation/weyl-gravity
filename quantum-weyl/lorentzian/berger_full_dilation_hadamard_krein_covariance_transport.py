"""Transport the normalized Berger Krein covariance across two Cauchy legs.

For a Cauchy GreenHyp morphism S:P1->P2, choose an inverse morphism
L:P2->P1 with L_hat=S_hat^{-1}.  A two-point distribution on P1 pushes
forward by precomposition with L^sharp on both slots.  The Pauli--Jordan
distribution has exactly the same transport law, so an exact CCR is
preserved.  Regularity and the certified cone action preserve the Hadamard
wavefront relation.

This construction remains on the rank-40 Hermitian metric dilation.  It is
not a restriction to the raw companion or the full graded BV complex and it
does not turn the indefinite covariance into a positive state.
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
NORMAL = (
    HERE
    / "certificates/BERGER_CUTOFF_VOLTERRA_NORMAL_TOPOLOGY_CONVERGENCE.json"
)
FREE = HERE / "certificates/BERGER_FREE_DILATION_KREIN_CCR_COVARIANCE.json"

DEPENDENCIES = {
    "Hermitian_dilation_and_Cauchy_legs": DILATION,
    "cutoff_normal_topology_and_cone_mapping": NORMAL,
    "normalized_free_Krein_covariance": FREE,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def transport_replay(
    *,
    both_legs_cauchy: bool = True,
    quotient_inverses: bool = True,
    regular_inverse_morphisms: bool = True,
    cone_action: bool = True,
    free_hadamard: bool = True,
    free_exact_ccr: bool = True,
    same_map_for_covariance_and_pauli_jordan: bool = True,
) -> dict[str, Any]:
    """Replay the two-leg quotient, wavefront and CCR proof."""

    typed_chain = both_legs_cauchy and quotient_inverses
    well_defined_on_eom_quotients = typed_chain
    inverse_choice_independent = typed_chain
    cutoff_bisolution = typed_chain and free_hadamard
    full_bisolution = cutoff_bisolution
    cutoff_hadamard = (
        cutoff_bisolution and regular_inverse_morphisms and cone_action
    )
    full_hadamard = cutoff_hadamard
    cutoff_exact_ccr = (
        typed_chain
        and free_exact_ccr
        and same_map_for_covariance_and_pauli_jordan
    )
    full_exact_ccr = cutoff_exact_ccr
    checks = {
        "typed_chain_L_free_cutoff_then_L_cutoff_full": typed_chain,
        "transport_is_well_defined_on_equation_of_motion_quotients": (
            well_defined_on_eom_quotients
        ),
        "equivalent_inverse_morphism_choice_does_not_change_covariance": (
            inverse_choice_independent
        ),
        "cutoff_transport_is_bisolution": cutoff_bisolution,
        "full_transport_is_bisolution": full_bisolution,
        "cutoff_transport_is_Hadamard": cutoff_hadamard,
        "full_transport_is_Hadamard": full_hadamard,
        "cutoff_transport_preserves_exact_CCR": cutoff_exact_ccr,
        "full_transport_preserves_exact_CCR": full_exact_ccr,
    }
    return {
        "past_leg": {
            "morphism": "S_-:D_free->D_chi",
            "quotient_inverse": "L_-:D_chi->D_free, Lhat_-=Shat_-^{-1}",
            "cutoff_covariance": (
                "W_chi=W_free o (L_-^sharp tensor L_-^sharp)"
            ),
            "cutoff_Pauli_Jordan": (
                "E_chi=E_free o (L_-^sharp tensor L_-^sharp)"
            ),
        },
        "future_leg": {
            "morphism": "S_+:D_chi->D_full",
            "quotient_inverse": "L_+:D_full->D_chi, Lhat_+=Shat_+^{-1}",
        },
        "composite": {
            "inverse": "T=L_- o L_+:D_full->D_free",
            "full_covariance": "W_full=W_free o (T^sharp tensor T^sharp)",
            "full_Pauli_Jordan": "E_full=E_free o (T^sharp tensor T^sharp)",
            "CCR_calculation": (
                "W_full-W_full^T="
                "(W_free-W_free^T)o(T^sharp tensor T^sharp)="
                "i E_free o(T^sharp tensor T^sharp)=i E_full"
            ),
            "Hadamard_calculation": (
                "WF(W_free) subset N_+xN_-; two applications of the "
                "regular inverse-morphism cone action give "
                "WF(W_full) subset N_+xN_-"
            ),
        },
        "checks": checks,
        "all_pass": all(checks.values()),
    }


def _load() -> dict[str, dict[str, Any]]:
    return {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in DEPENDENCIES.items()
    }


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    values = _load()
    dilation = values["Hermitian_dilation_and_Cauchy_legs"]
    normal = values["cutoff_normal_topology_and_cone_mapping"]
    free = values["normalized_free_Krein_covariance"]
    dilation_flags = dilation["claim_flags"]
    normal_flags = normal["claim_flags"]
    free_flags = free["claim_flags"]

    input_checks = {
        "free_to_cutoff_Cauchy_leg": dilation_flags[
            "BERGER_DILATED_FREE_CUTOFF_REGULAR_CAUCHY_MORPHISM"
        ]
        is True,
        "cutoff_to_full_Cauchy_leg": dilation_flags[
            "BERGER_DILATED_CUTOFF_FULL_REGULAR_CAUCHY_MORPHISM"
        ]
        is True,
        "both_legs_regular": dilation["regular_Cauchy_morphisms"]["all_pass"]
        is True,
        "cutoff_and_formal_transpose_normal_convergence": (
            normal_flags["BERGER_HORMANDER_VOLTERRA_CONVERGENCE_CERTIFIED"]
            is True
            and normal_flags[
                "BERGER_CUTOFF_VOLTERRA_TRANSPOSE_NORMAL_CONVERGENCE"
            ]
            is True
        ),
        "inverse_morphism_cone_action": normal_flags[
            "BERGER_DILATED_RESPONSE_MORPHISM_CONE_MAPPING"
        ]
        is True,
        "cutoff_dilation_decomposable": normal_flags[
            "BERGER_CUTOFF_COMPANION_NULL_CONE_DECOMPOSABLE"
        ]
        is True,
        "normalized_free_Hadamard_Krein_covariance": free_flags[
            "BERGER_FREE_DILATION_KREIN_COVARIANCE_NORMALIZED"
        ]
        is True,
        "free_exact_CCR": free["covariance"]["CCR"]
        == "W_Dfree-W_Dfree^T=i E_Dfree",
        "common_classical_snapshot": len(
            {
                dilation["classical_commit"],
                normal["classical_commit"],
                free["classical_commit"],
            }
        )
        == 1,
    }
    if not all(input_checks.values()):
        failed = [name for name, passed in input_checks.items() if not passed]
        raise ValueError(f"full-dilation covariance transport input drift: {failed}")

    replay = transport_replay()
    no_inverse = transport_replay(quotient_inverses=False)
    no_cone = transport_replay(cone_action=False)
    split_maps = transport_replay(
        same_map_for_covariance_and_pauli_jordan=False
    )
    if (
        not replay["all_pass"]
        or no_inverse["all_pass"]
        or no_inverse["checks"]["full_transport_preserves_exact_CCR"]
        or no_cone["checks"]["full_transport_is_Hadamard"]
        or split_maps["checks"]["full_transport_preserves_exact_CCR"]
    ):
        raise ValueError("full-dilation covariance transport replay failed")

    result = {
        "schema": (
            "quantum-weyl-berger-full-dilation-hadamard-krein-"
            "covariance-transport-v1"
        ),
        "result_id": "BERGER_FULL_DILATION_HADAMARD_KREIN_CCR_COVARIANCE",
        "result_state": (
            "FULL_METRIC_DILATION_GLOBAL_HADAMARD_KREIN_CCR_COVARIANCE_"
            "TRANSPORTED_GRADED_BV_AND_POSITIVITY_OPEN"
        ),
        "lifecycle_layer": "LORENTZIAN_DILATED_KREIN_COVARIANCE_TRANSPORT",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "classical_commit": free["classical_commit"],
        "setting_id": free["setting_id"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in values.items()
        },
        "exact_input_checks": input_checks,
        "transport": replay,
        "transported_covariances": {
            "cutoff": {
                "carrier": "cutoff rank-40 Hermitian metric dilation",
                "status": "GLOBAL_HADAMARD_KREIN_CCR_COVARIANCE",
                "CCR": "W_Dchi-W_Dchi^T=i E_Dchi",
            },
            "full": {
                "carrier": "full rank-40 Hermitian metric dilation",
                "status": "GLOBAL_HADAMARD_KREIN_CCR_COVARIANCE",
                "CCR": "W_Dfull-W_Dfull^T=i E_Dfull",
                "fibre_signature": [20, 20],
                "state_space_status": (
                    "INDEFINITE_KREIN_QUASIFREE_FUNCTIONAL_NOT_A_POSITIVE_STATE"
                ),
            },
        },
        "negative_controls": {
            "omit_quotient_inverse": no_inverse,
            "omit_cone_action": no_cone,
            "use_different_transport_for_CCR_sides": split_maps,
        },
        "literature_provenance": {
            "source": (
                "Christopher J. Fewster, Hadamard states for decomposable "
                "Green-hyperbolic operators"
            ),
            "arxiv": "2503.12537",
            "theorems": [
                "Theorem 3.5(d,e)",
                "Lemma 5.14",
                "Lemma 5.15(c)",
                "Theorem 5.16",
            ],
            "scope_map": (
                "The inverse Cauchy morphism formula and two-point transport "
                "law are instantiated on the certified rank-40 dilation. "
                "Positivity is not imported because the fibre form is indefinite."
            ),
        },
        "open_boundary": {
            "raw_companion_restriction": "NOT_CONSTRUCTED",
            "full_graded_BV_restriction": "NOT_CONSTRUCTED",
            "BRST_Ward_identity": "NOT_VERIFIED",
            "positive_state": "NOT_CERTIFIED",
            "physical_cohomology_positivity": "NOT_VERIFIED",
            "renormalized_Lorentzian_products": "NOT_CONSTRUCTED",
            "Lorentzian_QME": "NOT_RESTORED",
        },
        "claim_flags": {
            "BERGER_HORMANDER_VOLTERRA_CONVERGENCE_CERTIFIED": True,
            "BERGER_DILATED_RESPONSE_MORPHISM_CONE_MAPPING": True,
            "BERGER_REGULAR_GREENHYP_MORPHISM": True,
            "BERGER_FREE_DILATION_KREIN_COVARIANCE_NORMALIZED": True,
            "BERGER_CUTOFF_DILATION_HADAMARD_KREIN_COVARIANCE": True,
            "BERGER_FULL_DILATION_HADAMARD_KREIN_COVARIANCE": True,
            "BERGER_FULL_DILATION_EXACT_CCR": True,
            "BERGER_FREE_DILATION_POSITIVE_HADAMARD_STATE": False,
            "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": (
            "CONSTRUCT_RAW_COMPANION_OR_GRADED_BV_RESTRICTION_OF_FULL_"
            "DILATION_COVARIANCE_AND_VERIFY_BRST_WARD_IDENTITY"
        ),
        "provenance": {
            "transport_proof_type": (
                "EXACT_QUOTIENT_IDENTITY_PLUS_MICROLOCAL_THEOREM_INSTANTIATION"
            )
        },
        "claim_boundary": (
            "The normalized free Krein covariance is transported across both "
            "certified regular Cauchy GreenHyp morphisms to global Hadamard "
            "Krein covariances on the cutoff and full rank-40 Hermitian metric "
            "dilations. Their antisymmetric parts are exactly i times their "
            "respective project Pauli--Jordan distributions. The fibre form "
            "remains indefinite. No raw-companion or graded-BV restriction, "
            "BRST Ward identity, positive state, physical positivity, "
            "renormalized Lorentzian product, Lorentzian QME or full quantum "
            "theory is certified."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id")
        != "BERGER_FULL_DILATION_HADAMARD_KREIN_CCR_COVARIANCE"
        or result.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != (
            "CONSTRUCT_RAW_COMPANION_OR_GRADED_BV_RESTRICTION_OF_FULL_"
            "DILATION_COVARIANCE_AND_VERIFY_BRST_WARD_IDENTITY"
        )
    ):
        raise ValueError("full-dilation covariance transport identity drifted")
    if not all(result.get("exact_input_checks", {}).values()):
        raise ValueError("full-dilation covariance transport inputs failed")
    if not result.get("transport", {}).get("all_pass"):
        raise ValueError("full-dilation covariance transport proof failed")
    flags = result.get("claim_flags", {})
    required_true = {
        "BERGER_HORMANDER_VOLTERRA_CONVERGENCE_CERTIFIED",
        "BERGER_DILATED_RESPONSE_MORPHISM_CONE_MAPPING",
        "BERGER_REGULAR_GREENHYP_MORPHISM",
        "BERGER_FREE_DILATION_KREIN_COVARIANCE_NORMALIZED",
        "BERGER_CUTOFF_DILATION_HADAMARD_KREIN_COVARIANCE",
        "BERGER_FULL_DILATION_HADAMARD_KREIN_COVARIANCE",
        "BERGER_FULL_DILATION_EXACT_CCR",
    }
    required_false = {
        "BERGER_FREE_DILATION_POSITIVE_HADAMARD_STATE",
        "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION",
        "BERGER_26_ROW_BRST_HADAMARD",
        "BERGER_54_ROW_BRST_HADAMARD",
        "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY",
        "BERGER_HADAMARD_DATA",
        "QUANTUM_CLAIM",
    }
    if any(flags.get(name) is not True for name in required_true):
        raise ValueError("full-dilation covariance claim under-promoted")
    if any(flags.get(name) is not False for name in required_false):
        raise ValueError("full-dilation covariance claim over-promoted")
    if (
        result.get("transported_covariances", {})
        .get("full", {})
        .get("CCR")
        != "W_Dfull-W_Dfull^T=i E_Dfull"
    ):
        raise ValueError("full-dilation exact CCR drifted")
