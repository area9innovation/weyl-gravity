"""Fail-closed Einstein-projection contract with an exact MHV reference fixture."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import sympy as sp


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
EINSTEIN_COMMIT = "7e87281c416f4c4f98edfe61ae05829f4b48593a"
EINSTEIN_CERTIFICATE = "bridge/certificates/einstein_sector_theorem.json"
EINSTEIN_PRODUCER = "bridge/einstein_sector/certificate.py"
EINSTEIN_TEST = "bridge/einstein_sector/tests/test_certificate.py"
EINSTEIN_REPORT = "reports/einstein-sector-theorem.md"
DEFECT_COMMIT = "7963aa0cc4dcd23154dcef8ea431c98816f96fb2"
DEFECT_CERTIFICATE = "bridge/certificates/compensated_einstein_sourced_defect_preflight.json"
DEFECT_PRODUCER = "bridge/einstein_sector/compensated_einstein_sourced_defect_preflight.py"
DEFECT_TEST = "bridge/einstein_sector/tests/test_compensated_einstein_sourced_defect_preflight.py"
DEFECT_REPORT = "reports/compensated-einstein-sourced-defect-preflight.md"
PROJECTOR_COMMIT = "0d4c744313d17fb357954e3ac456adacb6ff5a17"
PROJECTOR_CERTIFICATE = "bridge/certificates/compensated_einstein_local_projectors.json"
PROJECTOR_PRODUCER = "bridge/einstein_sector/compensated_einstein_local_projectors.py"
PROJECTOR_TEST = "bridge/einstein_sector/tests/test_compensated_einstein_local_projectors.py"
PROJECTOR_REPORT = "reports/compensated-einstein-local-projectors.md"

REFERENCE_SETTING = {
    "setting_id": "complexified_flat_pure_weyl_to_einstein_three_point",
    "background_id": "four_dimensional_minkowski",
    "phase_space_id": "complex_on_shell_massless_three_point",
    "source_theory_id": "pure_weyl_conformal_gravity",
    "target_sector_id": "einstein_helicity_sector",
    "normalization_id": "stripped_einstein_shape_v1",
}
BERGER_SETTING_IDS = (
    "compact_positive_berger_clock_fixed_coupling_linearized",
    "compact_positive_berger_clock_rational_fixture_stationary_homogeneous",
)


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_blob(relative: str, commit: str = EINSTEIN_COMMIT) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned artifact {relative} at {commit}")
    return result.stdout


def _git_json(relative: str, commit: str = EINSTEIN_COMMIT) -> dict[str, Any]:
    value = json.loads(_git_blob(relative, commit))
    if not isinstance(value, dict):
        raise ValueError(f"pinned Einstein-sector JSON is not an object: {relative}")
    return value


def _artifact(relative: str, commit: str = EINSTEIN_COMMIT) -> dict[str, str]:
    return {
        "path": relative,
        "commit": commit,
        "sha256": hashlib.sha256(_git_blob(relative, commit)).hexdigest(),
    }


def validate_einstein_input(payload: dict[str, Any]) -> None:
    if (
        payload.get("schema") != "pure-weyl-einstein-sector-theorem-v1"
        or payload.get("result_id") != "CLASSICAL_EINSTEIN_SECTOR_THEOREM"
        or payload.get("result_state") != "PROVED_WITH_OPEN_BOUNDARY_RAIL"
    ):
        raise ValueError("Einstein-sector theorem identity drifted")
    classification = payload.get("classification", {})
    flags = payload.get("claim_flags", {})
    one_particle = payload.get("one_particle_before_residual_quotient", {})
    if (
        classification.get("einstein_as_exact_solution_sector") != "ESTABLISHED"
        or flags.get("exact_local_solution_inclusion") is not True
        or flags.get("local_helicity_two_modes_present") is not True
        or one_particle.get("helicity_weights") != ["+2", "-2"]
        or one_particle.get("local_bv_cohomology") != "W+ direct-sum W-"
    ):
        raise ValueError("Einstein inclusion or helicity input drifted")
    for name in (
        "observable_algebra_embedding",
        "asymptotically_flat_scattering_recovered",
        "einstein_sector_causally_closed_at_null_infinity",
        "ordinary_helicity_two_scattering_space_recovered",
        "lorentzian_quantum_theorem",
    ):
        if flags.get(name) is not False:
            raise ValueError("Einstein projection boundary was promoted")


def validate_defect_input(payload: dict[str, Any]) -> None:
    flags = payload.get("claim_flags", {})
    theorem = payload.get("source_compatibility_theorem", {})
    if (
        payload.get("schema") != "compensated-einstein-sourced-defect-preflight-v1"
        or payload.get("result_id") != "COMPENSATED_EINSTEIN_SOURCED_DEFECT_PREFLIGHT"
        or payload.get("result_state")
        != "SOURCE_COMPATIBILITY_CLASSIFIED_COMPENSATED_BV_OPEN"
        or theorem.get("einstein_defect") != "Delta_mn=G1_mn(h_hat)-T_mn/c1"
        or theorem.get("necessary_and_sufficient_same_source_condition")
        != "Q(T)=0"
        or flags.get("gauge_covariant_einstein_defect_defined") is not True
    ):
        raise ValueError("Einstein-defect preflight identity drifted")
    for name in (
        "einstein_defect_chain_map_constructed",
        "nonlinear_einstein_truncation_proved",
        "einstein_scattering_equivalence_proved",
        "null_infinity_closure_proved",
    ):
        if flags.get(name) is not False:
            raise ValueError("Einstein-defect boundary was promoted")


def validate_projector_input(payload: dict[str, Any]) -> None:
    flags = payload.get("claim_flags", {})
    quotient = payload.get("quotient_polynomial_theorem", {})
    if (
        payload.get("schema") != "compensated-einstein-local-projectors-v1"
        or payload.get("result_id") != "COMPENSATED_EINSTEIN_LOCAL_PROJECTORS"
        or payload.get("result_state")
        != "LOCAL_ON_SHELL_TT_BRANCH_SPLITTING_CERTIFIED"
        or quotient.get("einstein_projector") != "Pi_E=1+y/M2"
        or flags.get("on_shell_projectors_derived") is not True
        or flags.get("pure_weyl_limit_singular") is not True
    ):
        raise ValueError("reduced-TT projector input drifted")
    for name in (
        "full_metric_diff_weyl_bv_projector_constructed",
        "local_projector_on_unreduced_metric_bv_complex",
        "nonlinear_projector_constructed",
        "source_compatible_einstein_defect_complex_constructed",
    ):
        if flags.get(name) is not False:
            raise ValueError("reduced-TT projector boundary was promoted")


def classify_setting(candidate: dict[str, Any]) -> dict[str, Any]:
    """Route a prospective q2 block without conflating physical settings."""

    setting_id = candidate.get("setting_id")
    if setting_id in BERGER_SETTING_IDS:
        return {
            "compatible": False,
            "route": "BERGER_REDUCED_MODE_CARTAN_RAIL",
            "reason": "BACKGROUND_PHASE_SPACE_AND_OBSERVABLE_MISMATCH",
        }
    mismatches = [
        name
        for name, expected in REFERENCE_SETTING.items()
        if candidate.get(name) != expected
    ]
    if mismatches:
        return {
            "compatible": False,
            "route": "REJECT_UNDECLARED_OR_MISMATCHED_SETTING",
            "reason": "MISMATCH:" + ",".join(mismatches),
        }
    return {
        "compatible": True,
        "route": "EINSTEIN_DEFECT_TANGENCY_GATE",
        "reason": "SETTING_METADATA_EXACT",
    }


def _bracket(left: sp.Matrix, right: sp.Matrix) -> sp.Expr:
    return sp.expand(left[0] * right[1] - left[1] * right[0])


def _momentum(lam: sp.Matrix, tilde: sp.Matrix) -> sp.Matrix:
    return lam * tilde.T


def build_mhv_fixture() -> dict[str, Any]:
    """Evaluate the stripped (--+) Einstein three-point amplitude exactly."""

    lambdas = (
        sp.Matrix([1, 0]),
        sp.Matrix([0, 1]),
        sp.Matrix([-1, -1]),
    )
    tildes = (sp.Matrix([1, 0]),) * 3
    momenta = tuple(_momentum(lam, tilde) for lam, tilde in zip(lambdas, tildes))
    if sum(momenta, sp.zeros(2)) != sp.zeros(2):
        raise ValueError("MHV fixture violates momentum conservation")
    if any(momentum.det() != 0 for momentum in momenta):
        raise ValueError("MHV fixture contains a non-null momentum")

    angle12 = _bracket(lambdas[0], lambdas[1])
    angle23 = _bracket(lambdas[1], lambdas[2])
    angle31 = _bracket(lambdas[2], lambdas[0])
    square_brackets = [
        _bracket(tildes[first], tildes[second])
        for first, second in ((0, 1), (1, 2), (2, 0))
    ]
    if [angle12, angle23, angle31] != [1, 1, 1] or square_brackets != [0, 0, 0]:
        raise ValueError("MHV fixture is not on the holomorphic three-point branch")
    stripped_amplitude = sp.factor(angle12**6 / (angle23**2 * angle31**2))
    if stripped_amplitude != 1:
        raise ValueError("MHV fixture reference amplitude drifted")

    t1, t2, t3 = sp.symbols("t1 t2 t3", nonzero=True)
    scaling = sp.factor((t1 * t2) ** 6 / ((t2 * t3) ** 2 * (t3 * t1) ** 2))
    if scaling != t1**4 * t2**4 / t3**4:
        raise ValueError("MHV fixture little-group weights drifted")
    exchanged = sp.factor(
        _bracket(lambdas[1], lambdas[0]) ** 6
        / (
            _bracket(lambdas[0], lambdas[2]) ** 2
            * _bracket(lambdas[2], lambdas[1]) ** 2
        )
    )
    if exchanged != stripped_amplitude:
        raise ValueError("MHV fixture negative-leg exchange symmetry failed")

    def rows(matrix: sp.Matrix) -> list[list[str]]:
        return [[str(matrix[row, column]) for column in range(matrix.cols)] for row in range(matrix.rows)]

    return {
        "helicities": [-2, -2, 2],
        "branch": "holomorphic_complex_three_point_kinematics",
        "lambda_spinors": [[str(value) for value in spinor] for spinor in lambdas],
        "tilde_lambda_spinors": [[str(value) for value in spinor] for spinor in tildes],
        "momenta_bispinors": [rows(momentum) for momentum in momenta],
        "momentum_sum_zero": True,
        "all_momenta_null": True,
        "angle_brackets_12_23_31": ["1", "1", "1"],
        "square_brackets_12_23_31": ["0", "0", "0"],
        "stripped_formula": "<12>^6/(<23>^2<31>^2)",
        "stripped_value": "1",
        "little_group_factor": "t1^4*t2^4*t3^-4",
        "negative_leg_exchange_symmetric": True,
    }


def build_anti_mhv_fixture() -> dict[str, Any]:
    """Evaluate the stripped (++-) parity-conjugate amplitude exactly."""

    lambdas = (sp.Matrix([1, 0]),) * 3
    tildes = (
        sp.Matrix([1, 0]),
        sp.Matrix([0, 1]),
        sp.Matrix([-1, -1]),
    )
    momenta = tuple(_momentum(lam, tilde) for lam, tilde in zip(lambdas, tildes))
    if sum(momenta, sp.zeros(2)) != sp.zeros(2):
        raise ValueError("anti-MHV fixture violates momentum conservation")
    if any(momentum.det() != 0 for momentum in momenta):
        raise ValueError("anti-MHV fixture contains a non-null momentum")

    squares = [
        _bracket(tildes[first], tildes[second])
        for first, second in ((0, 1), (1, 2), (2, 0))
    ]
    angles = [
        _bracket(lambdas[first], lambdas[second])
        for first, second in ((0, 1), (1, 2), (2, 0))
    ]
    if squares != [1, 1, 1] or angles != [0, 0, 0]:
        raise ValueError("anti-MHV fixture is not on the anti-holomorphic branch")
    stripped_amplitude = sp.factor(
        squares[0] ** 6 / (squares[1] ** 2 * squares[2] ** 2)
    )
    if stripped_amplitude != 1:
        raise ValueError("anti-MHV fixture reference amplitude drifted")
    exchanged = sp.factor(
        _bracket(tildes[1], tildes[0]) ** 6
        / (
            _bracket(tildes[0], tildes[2]) ** 2
            * _bracket(tildes[2], tildes[1]) ** 2
        )
    )
    if exchanged != stripped_amplitude:
        raise ValueError("anti-MHV fixture positive-leg exchange symmetry failed")

    t1, t2, t3 = sp.symbols("t1 t2 t3", nonzero=True)
    scaling = sp.factor(
        (t1**-1 * t2**-1) ** 6
        / ((t2**-1 * t3**-1) ** 2 * (t3**-1 * t1**-1) ** 2)
    )
    if scaling != t3**4 / (t1**4 * t2**4):
        raise ValueError("anti-MHV fixture little-group weights drifted")

    def rows(matrix: sp.Matrix) -> list[list[str]]:
        return [
            [str(matrix[row, column]) for column in range(matrix.cols)]
            for row in range(matrix.rows)
        ]

    return {
        "helicities": [2, 2, -2],
        "branch": "anti_holomorphic_complex_three_point_kinematics",
        "lambda_spinors": [
            [str(value) for value in spinor] for spinor in lambdas
        ],
        "tilde_lambda_spinors": [
            [str(value) for value in spinor] for spinor in tildes
        ],
        "momenta_bispinors": [rows(momentum) for momentum in momenta],
        "momentum_sum_zero": True,
        "all_momenta_null": True,
        "angle_brackets_12_23_31": ["0", "0", "0"],
        "square_brackets_12_23_31": ["1", "1", "1"],
        "stripped_formula": "[12]^6/([23]^2[31]^2)",
        "stripped_value": "1",
        "little_group_factor": "t1^-4*t2^-4*t3^4",
        "positive_leg_exchange_symmetric": True,
        "parity_conjugate_of_reference_fixture": True,
    }


def build_certificate_payload() -> dict[str, Any]:
    theorem = _git_json(EINSTEIN_CERTIFICATE)
    validate_einstein_input(theorem)
    defect = _git_json(DEFECT_CERTIFICATE, DEFECT_COMMIT)
    validate_defect_input(defect)
    projector = _git_json(PROJECTOR_CERTIFICATE, PROJECTOR_COMMIT)
    validate_projector_input(projector)
    einstein_sources = {
        name: _artifact(relative)
        for name, relative in (
            ("einstein_certificate", EINSTEIN_CERTIFICATE),
            ("einstein_producer", EINSTEIN_PRODUCER),
            ("einstein_tests", EINSTEIN_TEST),
            ("einstein_report", EINSTEIN_REPORT),
        )
    }
    defect_sources = {
        name: _artifact(relative, DEFECT_COMMIT)
        for name, relative in (
            ("defect_certificate", DEFECT_CERTIFICATE),
            ("defect_producer", DEFECT_PRODUCER),
            ("defect_tests", DEFECT_TEST),
            ("defect_report", DEFECT_REPORT),
        )
    }
    projector_sources = {
        name: _artifact(relative, PROJECTOR_COMMIT)
        for name, relative in (
            ("projector_certificate", PROJECTOR_CERTIFICATE),
            ("projector_producer", PROJECTOR_PRODUCER),
            ("projector_tests", PROJECTOR_TEST),
            ("projector_report", PROJECTOR_REPORT),
        )
    }
    return {
        "schema": "quantum-weyl-einstein-projection-amplitude-fixture-v1",
        "result_id": "EINSTEIN_PROJECTION_MHV_REFERENCE_FIXTURE",
        "result_state": "PARITY_PAIR_EXACT_SETTING_DEFECT_NORMALIZATION_GATES_READY_Q2_BLOCKED",
        "lifecycle_layer": "INTERACTING",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "generality_assessment": {
            "target": "G5_EINSTEIN_PROJECTION_AND_ONE_AMPLITUDE_FIXTURE",
            "achieved": "G5_PREREQUISITE_PARITY_PAIR_AND_FAIL_CLOSED_INPUT_GATES",
            "promotion_to_G5_authorized": False,
        },
        "einstein_input": {
            "exact_solution_inclusion_available": True,
            "local_helicity_module": "W+ direct-sum W-",
            "helicity_weights": [2, -2],
            "nonlinear_support_local_projection_available": False,
            "observable_or_scattering_state_embedding_available": False,
        },
        "projection_contract": {
            "future_input": "physical support-local transferred cubic tensor ell2",
            "required_objects": [
                "complete support-local BV q2",
                "verified physical contraction pi_cl/iota_cl/S_cl",
                "full-BV gauge-covariant Einstein-defect chain map and nonlinear tangency proof",
                "helicity normalization and coupling dictionary",
            ],
            "evaluation": "compare the projected (--+) coefficient with the stripped reference after applying the declared normalization",
            "branch_leakage_test": "apply the certified full-BV Einstein-defect map to the nonlinear source and require zero or a declared exact primitive",
            "execution_authorized": False,
            "blocked_by": "complete support-local q2 and full-BV nonlinear Einstein-defect chain map",
        },
        "setting_compatibility_contract": {
            "reference_setting": REFERENCE_SETTING,
            "required_exact_fields": list(REFERENCE_SETTING),
            "known_berger_setting_ids": list(BERGER_SETTING_IDS),
            "known_berger_route": "BERGER_REDUCED_MODE_CARTAN_RAIL",
            "strict_exact_match_before_tangency_gate": True,
            "berger_input_compatible_with_flat_einstein_fixture": False,
            "execution_authorized": False,
        },
        "einstein_defect_tangency_contract": {
            "imported_linearized_defect": "Delta_mn=G1_mn(h_hat)-T_mn/c1",
            "imported_same_source_condition": "Q(T)=0",
            "future_test": "apply an exported full-BV nonlinear Einstein-defect chain map to q2(iota_E x,iota_E y) and require zero or a certified q1-exact trivialization",
            "reduced_TT_projector_available_for_nonzero_M2": True,
            "reduced_TT_projector_used_for_full_BV_projection": False,
            "reduced_TT_projector_valid_in_pure_weyl_limit": False,
            "full_BV_defect_chain_map_available": False,
            "nonlinear_tangency_proved": False,
            "execution_authorized": False,
        },
        "normalization_contract": {
            "normalization_id": "stripped_einstein_shape_v1",
            "reference_quantity": "dimensionless stripped helicity factor",
            "included": [
                "spinor-bracket shape",
                "helicity assignment",
                "little-group weights",
            ],
            "excluded": [
                "overall gravitational coupling",
                "phase convention",
                "delta function",
                "conformal-gravity action normalization",
            ],
            "comparison_rule": "shape and little-group weights may be compared now; an overall coefficient match is forbidden until every excluded factor is declared",
            "overall_coefficient_match_authorized": False,
        },
        "reference_fixture": build_mhv_fixture(),
        "parity_conjugate_fixture": build_anti_mhv_fixture(),
        "literature_reference": {
            "authors": "Tim Adamo and Lionel Mason",
            "title": "Conformal and Einstein gravity from twistor actions",
            "arxiv": "1307.5043v2",
            "doi": "10.1088/0264-9381/31/4/045014",
            "equation": "Eq. (6.2), flat-space Lambda->0 stripped three-point factor",
            "url": "https://arxiv.org/abs/1307.5043",
        },
        "claim_flags": {
            "REFERENCE_MHV_FIXTURE_COMPUTED": True,
            "REFERENCE_ANTI_MHV_FIXTURE_COMPUTED": True,
            "SETTING_COMPATIBILITY_GATE_IMPLEMENTED": True,
            "EINSTEIN_DEFECT_PREFLIGHT_IMPORTED": True,
            "NORMALIZATION_CONTRACT_LOCKED": True,
            "EINSTEIN_SOLUTION_INCLUSION_IMPORTED": True,
            "PHYSICAL_TRANSFERRED_Q2_PROJECTED": False,
            "NONLINEAR_EINSTEIN_TANGENCY_TESTED": False,
            "AMPLITUDE_MATCH_TO_CONFORMAL_GRAVITY_VERTEX": False,
            "LORENTZIAN_SCATTERING_CERTIFIED": False,
            "G5_PROMOTED": False,
        },
        "provenance": {
            "einstein_commit": EINSTEIN_COMMIT,
            "einstein_sources": einstein_sources,
            "einstein_sources_sha256": hashlib.sha256(
                json.dumps(
                    einstein_sources, sort_keys=True, separators=(",", ":")
                ).encode()
            ).hexdigest(),
            "defect_commit": DEFECT_COMMIT,
            "defect_sources": defect_sources,
            "defect_sources_sha256": hashlib.sha256(
                json.dumps(
                    defect_sources, sort_keys=True, separators=(",", ":")
                ).encode()
            ).hexdigest(),
            "projector_commit": PROJECTOR_COMMIT,
            "projector_sources": projector_sources,
            "projector_sources_sha256": hashlib.sha256(
                json.dumps(
                    projector_sources, sort_keys=True, separators=(",", ":")
                ).encode()
            ).hexdigest(),
        },
        "next_gate": "IMPORT_SETTING_MATCHED_SUPPORT_LOCAL_Q2_AND_FULL_BV_EINSTEIN_DEFECT_MAP",
        "claim_boundary": "This LOCAL-ALGEBRAIC G5 prerequisite imports the exact Einstein solution-locus inclusion, computes an exact parity pair of stripped complex three-graviton reference values, and installs strict setting, defect, and normalization gates. Berger reduced-mode inputs are routed away from flat scattering. The compensated defect result is only linearized preflight, while the available projectors act only on reduced TT fields at nonzero M2 and are singular in the pure-Weyl limit. No conformal-gravity vertex, nonlinear Einstein tangency, coefficient match, asymptotic scattering-state map, or causal amplitude is certified.",
    }
