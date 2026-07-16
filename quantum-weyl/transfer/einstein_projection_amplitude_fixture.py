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


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{EINSTEIN_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned Einstein-sector artifact {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned Einstein-sector JSON is not an object: {relative}")
    return value


def _artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": EINSTEIN_COMMIT,
        "sha256": hashlib.sha256(_git_blob(relative)).hexdigest(),
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


def build_certificate_payload() -> dict[str, Any]:
    theorem = _git_json(EINSTEIN_CERTIFICATE)
    validate_einstein_input(theorem)
    sources = {
        name: _artifact(relative)
        for name, relative in (
            ("einstein_certificate", EINSTEIN_CERTIFICATE),
            ("einstein_producer", EINSTEIN_PRODUCER),
            ("einstein_tests", EINSTEIN_TEST),
            ("einstein_report", EINSTEIN_REPORT),
        )
    }
    return {
        "schema": "quantum-weyl-einstein-projection-amplitude-fixture-v1",
        "result_id": "EINSTEIN_PROJECTION_MHV_REFERENCE_FIXTURE",
        "result_state": "REFERENCE_MHV_FIXTURE_EXACT_NONLINEAR_EINSTEIN_PROJECTION_INPUT_BLOCKED",
        "lifecycle_layer": "INTERACTING",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "generality_assessment": {
            "target": "G5_EINSTEIN_PROJECTION_AND_ONE_AMPLITUDE_FIXTURE",
            "achieved": "G5_PREREQUISITE_REFERENCE_FIXTURE_AND_INPUT_CONTRACT",
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
                "nonlinear Einstein tangent projection or exact tangency proof",
                "helicity normalization and coupling dictionary",
            ],
            "evaluation": "compare the projected (--+) coefficient with the stripped reference after applying the declared normalization",
            "branch_leakage_test": "project the nonlinear source onto every certified extra-Weyl complement and require zero for tangency",
            "execution_authorized": False,
            "blocked_by": "complete support-local q2 and nonlinear Einstein projection",
        },
        "reference_fixture": build_mhv_fixture(),
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
            "EINSTEIN_SOLUTION_INCLUSION_IMPORTED": True,
            "PHYSICAL_TRANSFERRED_Q2_PROJECTED": False,
            "NONLINEAR_EINSTEIN_TANGENCY_TESTED": False,
            "AMPLITUDE_MATCH_TO_CONFORMAL_GRAVITY_VERTEX": False,
            "LORENTZIAN_SCATTERING_CERTIFIED": False,
            "G5_PROMOTED": False,
        },
        "provenance": {
            "einstein_commit": EINSTEIN_COMMIT,
            "einstein_sources": sources,
            "einstein_sources_sha256": hashlib.sha256(
                json.dumps(sources, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
        },
        "next_gate": "IMPORT_SUPPORT_LOCAL_Q2_THEN_CONSTRUCT_NONLINEAR_EINSTEIN_PROJECTION",
        "claim_boundary": "This LOCAL-ALGEBRAIC G5 prerequisite imports the exact Einstein solution-locus inclusion and computes one exact complex spinor-helicity reference value for the stripped Einstein (--+) three-graviton amplitude. It does not project a conformal-gravity vertex: the complete support-local q2, a nonlinear Einstein tangent projector or tangency theorem, an asymptotic scattering-state map, and causal normalization are absent.",
    }
