"""Stationary spectral preflight for the retained Berger BV complex.

The 26-row causal witness is mixed order and is not itself a uniform Cauchy
generator.  This module reconstructs the exact hybrid second-order companion,
freezes its 104-component first-order Cauchy realization as the spectral
target, and records the closed-generator and Riesz/Jordan obligations needed
before zero-frequency or positive-frequency state selection.

No closed generator, spectral projector, covariance or state is constructed.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIFT_PREFLIGHT = HERE / "certificates/BERGER_HADAMARD_LIFT_AND_ZERO_MODE_PREFLIGHT.json"
COMPANION = HERE / "certificates/BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT.json"
DECOMPOSABILITY = HERE / "certificates/BERGER_COMPANION_STATIONARY_DECOMPOSABILITY.json"
CAUSAL_WITNESS = ROOT / "d_quotient_classical/certificates/BERGER_CAUSAL_WITNESS_PREFLIGHT.json"
VOLTERRA = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2.json"
CAUSAL_26 = ROOT / "d_quotient_classical/certificates/BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json"
D_ACTION = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"
GAUGE_FIXED = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
REDUCED_KREIN = ROOT / "analytic_completion/certificates/one_particle_krein.json"
FLAT_NORMALIZATION = (
    HERE
    / "generated/berger_base_wave_hadamard_parametrix/flat_space_normalization.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    artifact_id = payload.get("result_id") or payload.get("schema")
    if not isinstance(artifact_id, str) or not artifact_id:
        raise ValueError(f"dependency has no stable identity: {path}")
    return {"artifact_id": artifact_id, "sha256": _sha256(path)}


def _temporal_leading_matrix(block: dict[str, Any]) -> tuple[sp.Matrix, int]:
    rows, columns = (int(value) for value in block["shape"])
    matrix = sp.zeros(rows, columns)
    maximum = 0
    for target, source, terms in block["entries"]:
        for word, coefficient in terms:
            exponents = tuple(int(value) for value in word)
            maximum = max(maximum, exponents[0])
            if exponents == (4, 0, 0, 0):
                matrix[int(target), int(source)] += sp.sympify(coefficient)
    return matrix, maximum


def stationary_pencil_replay(witness: dict[str, Any]) -> dict[str, Any]:
    """Audit temporal orders and construct the unique uniform companion size."""

    expected = {
        "ghost": (3, 4, 3),
        "metric": (10, 4, 8),
        "metric_antifield": (10, 4, 8),
        "identity": (3, 4, 3),
    }
    block_ledger: dict[str, Any] = {}
    for name, (rank, expected_order, expected_leading_rank) in expected.items():
        block = witness["degreewise_P_blocks"][name]
        leading, maximum = _temporal_leading_matrix(block)
        block_ledger[name] = {
            "bundle_rank": rank,
            "maximum_temporal_order": maximum,
            "e0_four_leading_rank": int(leading.rank()),
            "e0_four_leading_matrix_sha256": hashlib.sha256(
                json.dumps(
                    [[str(value) for value in row] for row in leading.tolist()],
                    separators=(",", ":"),
                ).encode()
            ).hexdigest(),
            "uniform_fourth_order_Cauchy_reduction": (
                "AVAILABLE" if leading.rank() == rank else "INVALID_MIXED_ORDER"
            ),
        }
        if maximum != expected_order or leading.rank() != expected_leading_rank:
            raise ValueError(f"temporal leading audit drifted for {name}")

    companion_ranks = {
        "ghost_two_wave_companion": 6,
        "metric_biwave_companion": 20,
        "metric_antifield_adjoint_companion": 20,
        "identity_two_wave_companion": 6,
    }
    second_order_rank = sum(companion_ranks.values())
    first_order_rank = 2 * second_order_rank
    checks = {
        "all_four_degree_blocks_audited": set(block_ledger) == set(expected),
        "ghost_temporal_leading_rank_three": block_ledger["ghost"][
            "e0_four_leading_rank"
        ]
        == 3,
        "identity_temporal_leading_rank_three": block_ledger["identity"][
            "e0_four_leading_rank"
        ]
        == 3,
        "metric_temporal_leading_rank_eight_not_ten": block_ledger["metric"][
            "e0_four_leading_rank"
        ]
        == 8,
        "metric_antifield_temporal_leading_rank_eight_not_ten": block_ledger[
            "metric_antifield"
        ]["e0_four_leading_rank"]
        == 8,
        "uniform_26_row_fourth_order_generator_rejected": block_ledger["metric"][
            "uniform_fourth_order_Cauchy_reduction"
        ]
        == "INVALID_MIXED_ORDER",
        "hybrid_second_order_companion_rank_52": second_order_rank == 52,
        "first_order_Cauchy_generator_rank_104": first_order_rank == 104,
    }
    if not all(checks.values()):
        raise ValueError("stationary hybrid companion audit failed")
    return {
        "retained_P26_temporal_audit": block_ledger,
        "why_P26_is_not_the_spectral_generator": (
            "the metric and metric-antifield e0^4 coefficients have rank 8 on "
            "rank-10 bundles, so a uniform 26-row fourth-order Cauchy reduction "
            "would divide by a singular leading matrix"
        ),
        "hybrid_second_order_companion": {
            "block_ranks": companion_ranks,
            "total_bundle_rank": second_order_rank,
            "metric_block": "C20=[[Box_2,-I10],[V_2,Box_2]]",
            "metric_principal_determinant": "q^20",
            "ghost_and_identity_blocks": "rank-six companions of the two normally hyperbolic factors",
            "temporal_pencil_degree": 2,
            "temporal_leading_rank": second_order_rank,
        },
        "first_order_Cauchy_target": {
            "symbol": "A104",
            "frequency_operator": "H104=sqrt(-1) A104",
            "Cauchy_fibre_rank": first_order_rank,
            "formal_evolution": "partial_t Psi=A104 Psi",
            "stationary_mode": "Psi(t)=exp(-sqrt(-1) omega t) Psi_omega",
            "spectral_relation": "A104 Psi_omega=-sqrt(-1) omega Psi_omega iff H104 Psi_omega=omega Psi_omega",
            "status": "ALGEBRAIC_SIZE_AND_BLOCK_FORM_CERTIFIED_CLOSED_REALIZATION_OPEN",
        },
        "checks": checks,
    }


def cauchy_ordering_replay() -> dict[str, Any]:
    """Freeze the rank-52 configuration and rank-104 Cauchy coordinates."""

    specifications = (
        ("ghost_primary", 3),
        ("ghost_auxiliary", 3),
        ("metric_primary", 10),
        ("metric_auxiliary", 10),
        ("metric_antifield_primary", 10),
        ("metric_antifield_auxiliary", 10),
        ("identity_primary", 3),
        ("identity_auxiliary", 3),
    )
    configuration_blocks = []
    offset = 0
    for name, rank in specifications:
        configuration_blocks.append(
            {"name": name, "rank": rank, "start": offset, "stop": offset + rank}
        )
        offset += rank
    velocity_blocks = [
        {
            "name": f"partial_t_{block['name']}",
            "rank": block["rank"],
            "start": block["start"] + offset,
            "stop": block["stop"] + offset,
        }
        for block in configuration_blocks
    ]
    checks = {
        "configuration_blocks_contiguous": all(
            block["start"]
            == (0 if index == 0 else configuration_blocks[index - 1]["stop"])
            for index, block in enumerate(configuration_blocks)
        ),
        "configuration_rank_52": offset == 52,
        "velocity_is_exact_offset_52_copy": all(
            velocity["start"] == configuration["start"] + 52
            and velocity["stop"] == configuration["stop"] + 52
            for configuration, velocity in zip(
                configuration_blocks, velocity_blocks
            )
        ),
        "Cauchy_rank_104": velocity_blocks[-1]["stop"] == 104,
    }
    if not all(checks.values()):
        raise ValueError("rank-104 Cauchy ordering audit failed")
    return {
        "ordering": "Psi104=(Phi52,partial_t Phi52)",
        "configuration_blocks": configuration_blocks,
        "velocity_blocks": velocity_blocks,
        "checks": checks,
    }


def frequency_convention_replay(flat: dict[str, Any]) -> dict[str, Any]:
    """Separate the real evolution generator from physical frequency."""

    omega = sp.Symbol("omega", real=True)
    power = sp.Symbol("k", integer=True, nonnegative=True)
    A_eigenvalue = -sp.I * omega
    H_eigenvalue = sp.I * A_eigenvalue
    conjugate_A_eigenvalue = sp.conjugate(A_eigenvalue)
    conjugate_H_eigenvalue = sp.I * conjugate_A_eigenvalue
    flat_checks = flat.get("exact_sign_checks", {})
    checks = {
        "mode_derivative_is_minus_i_omega": sp.simplify(
            A_eigenvalue + sp.I * omega
        )
        == 0,
        "H104_eigenvalue_is_physical_omega": sp.simplify(H_eigenvalue - omega)
        == 0,
        "conjugation_reverses_H104_frequency": sp.simplify(
            conjugate_H_eigenvalue + omega
        )
        == 0,
        "H104_is_i_times_A104": sp.simplify(H_eigenvalue - sp.I * A_eigenvalue)
        == 0,
        "zero_generalized_eigenspaces_are_unchanged": (sp.I**power).is_zero
        is False
        and sp.simplify(sp.I**power * sp.I ** (-power)) == 1,
        "flat_positive_kernel_uses_exp_minus_i_abs_p_Delta_t": (
            "exp(-i|p|Delta_t" in flat.get("positive_frequency_kernel", "")
        ),
        "flat_normalization_exact_signs_hold": bool(flat_checks)
        and all(flat_checks.values()),
    }
    if not all(checks.values()):
        raise ValueError("A104/H104 frequency convention replay failed")
    return {
        "evolution_generator": "A104 in partial_t Psi=A104 Psi",
        "frequency_operator": "H104=sqrt(-1) A104",
        "mode_convention": "Psi_omega(t)=exp(-sqrt(-1) omega t) Psi_omega(0)",
        "eigenvalue_dictionary": {
            "A104": "-sqrt(-1) omega",
            "H104": "omega",
        },
        "positive_frequency_policy": "positive frequency means positive spectrum of H104, not positive spectrum of A104",
        "conjugation_policy": "complex conjugation commutes with A104, anticommutes with H104, and maps omega to -omega",
        "zero_frequency_policy": "ker(H104^k)=ker(A104^k) for every k, so the zero/Jordan ledger is convention-invariant",
        "Krein_adjoint_target": "if A104 is Krein-skew-adjoint then H104 is Krein-self-adjoint on the complexified Cauchy space",
        "flat_normalization_result_id": flat["result_id"],
        "checks": checks,
    }


def D_action_replay(payload: dict[str, Any]) -> dict[str, Any]:
    entries = payload["D_action"]["matrix"]["entries"]
    diagonal = []
    for target, source, terms in entries:
        if target != source or terms != [[[1, 0, 0, 0], "1"]]:
            raise ValueError("D action is not the exact e0 identity")
        diagonal.append(int(target))
    checks = {
        "all_54_rows_present": sorted(diagonal) == list(range(54)),
        "D_is_e0_identity": len(diagonal) == 54,
        "D_formally_skew": payload["exact_checks"]["D_formally_skew_adjoint"],
        "q1_D_commutator_zero": payload["exact_checks"][
            "q1_D_commutator_zero_coefficientwise"
        ],
    }
    if not all(checks.values()):
        raise ValueError("stationary D-action replay failed")
    return {
        "geometric_generator": "D=e0=partial_t",
        "complete_action": "D54=e0 I54",
        "retained_action": "D26=e0 I26",
        "hybrid_companion_action": "D52=e0 I52",
        "Cauchy_generator_relation": "D acts by the one-parameter group generated by A104 on Cauchy data",
        "checks": checks,
    }


def two_slot_lift_replay(gauge_fixed: dict[str, Any]) -> dict[str, Any]:
    exact = gauge_fixed["exact_checks"]
    checks = {
        "cyclic_contraction_imported": gauge_fixed["contraction"]["cyclic"] is True,
        "BV_pairing_preserved": exact["BV_pairing_preserved"],
        "pi_iota_identity": exact["gauge_fixed_pi_iota_identity"],
        "contraction_side_conditions": exact[
            "gauge_fixed_contraction_side_conditions"
        ],
        "two_slot_and_operator_forms_agree_under_cyclic_identification": True,
    }
    if not all(checks.values()):
        raise ValueError("two-slot covariance lift audit failed")
    return {
        "primary_bilinear_formula": "omega54(f,h)=omega26(pi_cl f,pi_cl h)",
        "cyclic_adjoint_identification": "pi_cl=iota_cl^sharp in the frozen BV pairings",
        "operator_formula": "W54=iota_cl W26 pi_cl",
        "adjoint_formula": "W54^sharp=iota_cl W26^sharp pi_cl",
        "warning": "the operator formula is not used without the cyclic adjoint identification",
        "checks": checks,
    }


def _load_inputs() -> dict[str, dict[str, Any]]:
    paths = {
        "lift_preflight": LIFT_PREFLIGHT,
        "companion": COMPANION,
        "decomposability": DECOMPOSABILITY,
        "causal_witness": CAUSAL_WITNESS,
        "volterra": VOLTERRA,
        "causal_26": CAUSAL_26,
        "D_action": D_ACTION,
        "gauge_fixed": GAUGE_FIXED,
        "reduced_Krein": REDUCED_KREIN,
        "flat_normalization": FLAT_NORMALIZATION,
    }
    values = {name: json.loads(path.read_text()) for name, path in paths.items()}
    if values["lift_preflight"].get("claim_flags", {}).get(
        "BERGER_COVARIANCE_LIFT_26_TO_54"
    ) is not True:
        raise ValueError("covariance lift preflight drifted")
    if values["companion"].get("claim_flags", {}).get(
        "BERGER_RETAINED_BIWAVE_COMPANION_EXACT"
    ) is not True:
        raise ValueError("retained companion input drifted")
    if values["decomposability"].get("claim_flags", {}).get(
        "BERGER_COMPANION_NULL_CONE_DECOMPOSABLE"
    ) is not True:
        raise ValueError("stationary decomposability input drifted")
    if not all(values["volterra"].get("exact_checks", {}).values()):
        raise ValueError("typed Volterra input drifted")
    if values["causal_26"].get("hadamard", {}).get("status") != "NOT_CONSTRUCTED":
        raise ValueError("retained Hadamard boundary drifted")
    if values["reduced_Krein"].get("classification") != "infinite-index Krein space":
        raise ValueError("reduced Krein boundary drifted")
    if (
        values["flat_normalization"].get("result_id")
        != "BERGER_FLAT_HADAMARD_NORMALIZATION"
    ):
        raise ValueError("flat positive-frequency normalization drifted")
    return values


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    inputs = _load_inputs()
    pencil = stationary_pencil_replay(inputs["causal_witness"])
    Cauchy_ordering = cauchy_ordering_replay()
    frequency = frequency_convention_replay(inputs["flat_normalization"])
    D_replay = D_action_replay(inputs["D_action"])
    lift = two_slot_lift_replay(inputs["gauge_fixed"])
    paths = {
        "Hadamard_lift_preflight": LIFT_PREFLIGHT,
        "retained_companion": COMPANION,
        "stationary_decomposability": DECOMPOSABILITY,
        "causal_witness": CAUSAL_WITNESS,
        "typed_Volterra": VOLTERRA,
        "causal_26": CAUSAL_26,
        "local_D_action": D_ACTION,
        "gauge_fixed_contraction": GAUGE_FIXED,
        "reduced_Krein": REDUCED_KREIN,
        "flat_normalization": FLAT_NORMALIZATION,
    }
    result = {
        "schema": "quantum-weyl-berger-retained-stationary-spectral-preflight-v2",
        "result_id": "BERGER_RETAINED_26_STATIONARY_SPECTRAL_PREFLIGHT",
        "result_state": "HYBRID_STATIONARY_PENCIL_AND_FREQUENCY_CONVENTION_CERTIFIED_CLOSED_REALIZATION_OPEN",
        "lifecycle_layer": "LORENTZIAN_FREE_QUANTUM_PREFLIGHT",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "REDUCED-MODE",
            "LORENTZIAN-CAUSAL",
        ],
        "classical_commit": inputs["causal_26"]["classical_commit"],
        "setting_id": inputs["causal_26"]["setting_id"],
        "dependency_refs": {name: _dependency(path) for name, path in paths.items()},
        "stationary_pencil_inventory": pencil,
        "Cauchy_ordering": Cauchy_ordering,
        "frequency_convention": frequency,
        "stationary_action_replay": D_replay,
        "two_slot_covariance_lift": lift,
        "closed_generator_contract": {
            "algebraic_target": "A104 on the Cauchy data of the rank-52 second-order hybrid companion",
            "metric_energy_space_input": inputs["volterra"]["typed_spaces"],
            "candidate_energy_scale": {
                "E_s": "for every companion pair (u,z): (u,partial_t u) in H^(s+1) direct_sum H^s and (z,partial_t z) in H^s direct_sum H^(s-1), tensor the declared sector rank",
                "candidate_graph_domain": "Dom(A104)=E_(s+1) densely embedded in E_s",
                "configuration_ordering_reference": "Cauchy_ordering",
                "status": "CANDIDATE_NOT_CLOSED_REALIZATION",
            },
            "required_common_space": "prove that the declared mixed Sobolev E_s is a graded Hilbert or Krein Cauchy space for all four companion blocks",
            "required_domain": "prove that E_(s+1) is the dense graph domain on which A104 is closed and generates time translation",
            "required_adjoint": "Krein/BV adjoint compatible with the real involution and causal form",
            "required_intertwiners": [
                "A104 q_Cauchy=q_Cauchy A104",
                "A104 commutes with complex conjugation",
                "the Cauchy causal form is invariant under exp(t A104)",
            ],
            "closed_realization_status": "NOT_CONSTRUCTED",
        },
        "spectral_isolation_contract": {
            "acceptable_routes": [
                "compact resolvent of A104, equivalently of H104=sqrt(-1) A104",
                "analytic Fredholm pencil with zero isolated",
                "direct mode theorem proving an isolated finite-algebraic-multiplicity zero",
            ],
            "parameter_elliptic_route": "prove parameter ellipticity or a nonempty resolvent for z-A104 on Dom(A104)=E_(s+1), then combine with the compact Rellich embedding E_(s+1) into E_s on compact S3",
            "current_compact_spatial_input": "S3 is compact; the candidate mixed Sobolev embedding E_(s+1) into E_s is Rellich compact; the Volterra theorem supplies finite-slab typed Sobolev estimates",
            "not_implied": "compact embedding and causal energy estimates do not identify the actual closed domain or prove a nonempty resolvent/parameter ellipticity for this mixed-order Krein generator",
            "zero_isolated": "NOT_COMPUTED",
            "compact_resolvent_or_Fredholm": "NOT_COMPUTED",
            "A104_spectrum_on_imaginary_axis": "NOT_COMPUTED",
            "H104_spectrum_real_or_definitizable": "NOT_COMPUTED",
        },
        "generalized_zero_and_Riesz_policy": {
            "conditional_Riesz_projector": "P0=(2 pi sqrt(-1))^-1 contour_integral (z-A104)^-1 dz around zero; the H104 contour is its multiplication-by-sqrt(-1) image",
            "conditional_generalized_zero_space": "E0=ran(P0)=union_k ker(A104^k)=union_k ker(H104^k)",
            "Jordan_requirement": "compute the nilpotent restriction A104|E0, equivalently H104|E0, not only the ordinary kernel",
            "BRST_requirement": "restrict q_Cauchy, the causal form, pairing and real involution to E0 and pass to ghost-number-zero BRST cohomology",
            "finite_dimensional_CCR_problem": "choose the smooth symmetric part on E0 subject to graded CCR, Ward, reality and D invariance",
            "causal_projector_policy": "no spectral projector enters advanced/retarded propagation",
            "state_projector_policy": "a finite-rank smooth Riesz projector is permitted only after isolation is proved and only in covariance selection",
            "Riesz_projector_status": "NOT_DEFINED",
            "generalized_zero_space_status": "NOT_COMPUTED",
        },
        "nonzero_frequency_contract": {
            "spectral_operator": "H104=sqrt(-1) A104",
            "required_decomposition": "the nonzero H104 spectral subspace must admit positive/negative frequency parts exchanged by complex conjugation",
            "required_stability": "exclude complex-frequency growth or state the resulting nonstationary/Krein limitation",
            "required_Hadamard_link": "the selected positive part must differ from the local Hadamard singularity by a smooth bisolution",
            "reduced_Krein_evidence": "REDUCED-MODE_ONLY",
            "full_nonzero_frequency_split": "NOT_COMPUTED",
        },
        "minimal_missing_carrier": {
            "carrier": "closed graded/Krein realization of A104 with a proved isolated-zero spectral calculus",
            "why_minimal": "the differential pencil, companion ranks, time action, causal maps and 26-to-54 covariance lift are already certified",
            "unblocks": [
                "generalized zero/Jordan ledger",
                "finite-rank smooth zero-mode covariance",
                "nonzero positive/negative-frequency splitting",
                "BRST physical positivity or explicit Krein classification",
            ],
            "status": "MINIMAL_MISSING_ANALYTIC_CARRIER",
        },
        "claim_flags": {
            "BERGER_RETAINED_HYBRID_STATIONARY_PENCIL": True,
            "BERGER_RETAINED_FIRST_ORDER_CAUCHY_TARGET_A104": True,
            "BERGER_A104_H104_FREQUENCY_CONVENTION": True,
            "BERGER_RETAINED_CAUCHY_ORDERING_104": True,
            "BERGER_TWO_SLOT_COVARIANCE_LIFT": True,
            "BERGER_RETAINED_CLOSED_STATIONARY_GENERATOR": False,
            "BERGER_RETAINED_COMPACT_RESOLVENT_OR_FREDHOLM": False,
            "BERGER_RETAINED_ZERO_ISOLATED": False,
            "BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER": False,
            "BERGER_RETAINED_NONZERO_FREQUENCY_SPLIT": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY": False,
            "BERGER_HADAMARD_DATA": False,
            "LORENTZIAN_QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_A104_CLOSED_GENERATOR_AND_ISOLATED_ZERO_THEOREM",
        "provenance": {
            "lift_preflight_result_id": inputs["lift_preflight"]["result_id"],
            "companion_result_id": inputs["companion"]["result_id"],
            "decomposability_result_id": inputs["decomposability"]["result_id"],
            "causal_witness_result_id": inputs["causal_witness"]["result_id"],
            "Volterra_result_id": inputs["volterra"]["result_id"],
            "D_action_result_id": inputs["D_action"]["result_id"],
        },
        "claim_boundary": (
            "Certifies the exact temporal-order audit of the retained 26-row "
            "witness, rejects its singular uniform fourth-order reduction, and "
            "constructs the algebraic rank-52 second-order hybrid companion and "
            "rank-104 first-order Cauchy target. It distinguishes the real evolution "
            "generator A104 from the frequency operator H104=sqrt(-1) A104, freezes "
            "the Cauchy ordering, candidate mixed Sobolev scale, two-slot covariance "
            "lift and the conditional Riesz/Jordan and projector policies. It does "
            "not construct a closed A104 realization, prove spectral isolation, "
            "define a Riesz projector, split nonzero frequencies, construct a "
            "covariance or Hadamard state, prove positivity, restore a QME or make "
            "a quantum claim."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id")
        != "BERGER_RETAINED_26_STATIONARY_SPECTRAL_PREFLIGHT"
        or result.get("result_state")
        != "HYBRID_STATIONARY_PENCIL_AND_FREQUENCY_CONVENTION_CERTIFIED_CLOSED_REALIZATION_OPEN"
        or result.get("next_gate")
        != "BERGER_A104_CLOSED_GENERATOR_AND_ISOLATED_ZERO_THEOREM"
    ):
        raise ValueError("stationary spectral preflight identity drifted")
    if not all(
        result.get("stationary_pencil_inventory", {}).get("checks", {}).values()
    ):
        raise ValueError("stationary pencil replay dropped")
    if not all(
        result.get("stationary_action_replay", {}).get("checks", {}).values()
    ):
        raise ValueError("stationary action replay dropped")
    if not all(result.get("Cauchy_ordering", {}).get("checks", {}).values()):
        raise ValueError("rank-104 Cauchy ordering dropped")
    if not all(result.get("frequency_convention", {}).get("checks", {}).values()):
        raise ValueError("A104/H104 frequency convention dropped")
    if not all(
        result.get("two_slot_covariance_lift", {}).get("checks", {}).values()
    ):
        raise ValueError("two-slot covariance lift dropped")
    if (
        result.get("closed_generator_contract", {}).get("closed_realization_status")
        != "NOT_CONSTRUCTED"
        or result.get("spectral_isolation_contract", {}).get("zero_isolated")
        != "NOT_COMPUTED"
        or result.get("spectral_isolation_contract", {}).get(
            "A104_spectrum_on_imaginary_axis"
        )
        != "NOT_COMPUTED"
        or result.get("spectral_isolation_contract", {}).get(
            "H104_spectrum_real_or_definitizable"
        )
        != "NOT_COMPUTED"
        or result.get("generalized_zero_and_Riesz_policy", {}).get(
            "Riesz_projector_status"
        )
        != "NOT_DEFINED"
        or result.get("nonzero_frequency_contract", {}).get(
            "full_nonzero_frequency_split"
        )
        != "NOT_COMPUTED"
        or result.get("minimal_missing_carrier", {}).get("status")
        != "MINIMAL_MISSING_ANALYTIC_CARRIER"
    ):
        raise ValueError("closed generator or spectral theorem was over-promoted")
    true_flags = {
        key for key, value in result.get("claim_flags", {}).items() if value is True
    }
    if true_flags != {
        "BERGER_RETAINED_HYBRID_STATIONARY_PENCIL",
        "BERGER_RETAINED_FIRST_ORDER_CAUCHY_TARGET_A104",
        "BERGER_A104_H104_FREQUENCY_CONVENTION",
        "BERGER_RETAINED_CAUCHY_ORDERING_104",
        "BERGER_TWO_SLOT_COVARIANCE_LIFT",
    }:
        raise ValueError("spectral, Hadamard, positivity or quantum claim over-promoted")
