"""Frozen generalized-connection contract for the four-dimensional Euler tower.

This module fixes gradings and the source-to-project normalization before the
large symbolic expansion.  It does not assert closure of the intrinsic Euler
descent; it only makes every later component expansion reproducible.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from .algebra import canonical_sha256


EULER_BIDEGREES = ((1, 4), (2, 3), (3, 2), (4, 1), (5, 0))


def _fraction(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def generalized_connection_dictionary() -> dict[str, Any]:
    """Return the immutable grading dictionary used by Euler expansion."""

    generators = [
        {
            "symbol": "omega",
            "role": "weyl_ghost",
            "bidegrees": [{"ghost_number": 1, "form_degree": 0}],
            "total_degree": 1,
            "grassmann_parity": "odd",
            "engineering_dimension": 0,
            "weyl_weight": 0,
            "tensor_type": "scalar",
            "index_symmetries": [],
        },
        {
            "symbol": "dx^mu",
            "role": "horizontal_form_carrier",
            "bidegrees": [{"ghost_number": 0, "form_degree": 1}],
            "total_degree": 1,
            "grassmann_parity": "odd_total_degree",
            "engineering_dimension": -1,
            "weyl_weight": 0,
            "tensor_type": "contravariant_coordinate_label",
            "index_symmetries": [],
        },
        {
            "symbol": "partial_mu omega",
            "role": "ghost_component_of_tilde_omega",
            "bidegrees": [{"ghost_number": 1, "form_degree": 0}],
            "total_degree": 1,
            "grassmann_parity": "odd",
            "engineering_dimension": 1,
            "weyl_weight": 0,
            "tensor_type": "covector",
            "index_symmetries": [],
        },
        {
            "symbol": "K_mu_nu dx^nu",
            "role": "form_component_of_tilde_omega",
            "bidegrees": [{"ghost_number": 0, "form_degree": 1}],
            "total_degree": 1,
            "grassmann_parity": "odd_total_degree",
            "engineering_dimension": 1,
            "weyl_weight": 0,
            "tensor_type": "covector_valued_one_form",
            "index_symmetries": ["K_mu_nu = K_nu_mu"],
        },
        {
            "symbol": "tilde_omega_mu",
            "role": "generalized_connection",
            "definition": "partial_mu omega - K_mu_nu dx^nu",
            "bidegrees": [
                {"ghost_number": 1, "form_degree": 0},
                {"ghost_number": 0, "form_degree": 1},
            ],
            "total_degree": 1,
            "grassmann_parity": "odd_total_degree",
            "engineering_dimension": 1,
            "weyl_weight": 0,
            "tensor_type": "inhomogeneous_covector_total_form",
            "index_symmetries": [],
        },
        {
            "symbol": "Gamma^mu_(nu rho) dx^rho",
            "role": "levi_civita_connection_one_form",
            "bidegrees": [{"ghost_number": 0, "form_degree": 1}],
            "total_degree": 1,
            "grassmann_parity": "odd_total_degree",
            "engineering_dimension": 0,
            "weyl_weight": "INHOMOGENEOUS_CONNECTION",
            "tensor_type": "endomorphism_valued_one_form",
            "index_symmetries": ["Gamma^mu_(nu rho) = Gamma^mu_(rho nu)"],
        },
        {
            "symbol": "W^mu_nu",
            "role": "weyl_curvature_two_form",
            "definition": "(1/2) dx^rho dx^sigma W^mu_(lambda rho sigma) g^(lambda nu)",
            "bidegrees": [{"ghost_number": 0, "form_degree": 2}],
            "total_degree": 2,
            "grassmann_parity": "even_total_degree",
            "engineering_dimension": 0,
            "weyl_weight": 0,
            "tensor_type": "endomorphism_valued_two_form",
            "index_symmetries": ["Weyl tensor algebraic symmetries", "algebraic Bianchi"],
        },
        {
            "symbol": "epsilon_mu_nu_rho_sigma",
            "role": "orientation_tensor",
            "bidegrees": [{"ghost_number": 0, "form_degree": 0}],
            "total_degree": 0,
            "grassmann_parity": "even",
            "engineering_dimension": 0,
            "weyl_weight": 4,
            "tensor_type": "totally_antisymmetric_covariant_rank_four",
            "index_symmetries": ["total antisymmetry"],
        },
    ]
    payload = {
        "schema_version": "generalized-connection-v1",
        "spacetime_dimension": 4,
        "coordinate_engineering_convention": "[dx] = -1",
        "schouten_convention": "K_ab = 1/2 (Ric_ab - R g_ab/6)",
        "orientation_convention": "frozen project epsilon orientation",
        "generators": generators,
        "dictionary_status": "FROZEN_FOR_BIDEGREE_EXPANSION",
    }
    return {**payload, "dictionary_sha256": canonical_sha256(payload)}


def euler_normalization_contract() -> dict[str, Any]:
    """Resolve the source coefficients by a single top-component rescaling."""

    source = (Fraction(1, 4), Fraction(-1), Fraction(1))
    project_top_target = Fraction(1)
    global_scale = project_top_target / source[0]
    project = tuple(global_scale * value for value in source)
    if project != (Fraction(1), Fraction(-4), Fraction(4)):
        raise AssertionError("Euler source-to-project normalization drifted")
    payload = {
        "source_formula": "(-1)^p/2^p * m!/(r!p!), p=m-r, m=2",
        "component_order": "increasing r = 0,1,2; bidegrees (1,4),(2,3),(3,2)",
        "source_coefficients": [_fraction(value) for value in source],
        "source_top_component": "(1/4) omega epsilon_abcd R^ab wedge R^cd",
        "project_top_component": "omega E4, E4 = epsilon_abcd R^ab wedge R^cd",
        "global_source_to_project_scale": _fraction(global_scale),
        "project_coefficients": [_fraction(value) for value in project],
        "legacy_unverified_vector": [_fraction(value) for value in (4, -4, 1)],
        "legacy_vector_status": "REJECTED_AS_UNDERIVED_CARRIER_RESCALING",
        "normalization_rule": "one global rescaling fixed by the top component; no r-dependent carrier rescaling",
        "normalization_status": "RESOLVED_FOR_FROZEN_SOURCE_CARRIERS",
        "tower_closure_status": "NOT_COMPUTED",
    }
    return {**payload, "normalization_sha256": canonical_sha256(payload)}


def _carrier_signatures(ghost_number: int, form_degree: int) -> list[dict[str, int]]:
    """Enumerate coarse total-degree-five Euler carrier signatures.

    A signature contains one explicit anomaly ghost, zero or more copies of
    the inhomogeneous total-degree-one ``tilde_omega``, and Weyl two-forms.
    This is exhaustive for that frozen carrier algebra, not for the complete
    tensor quotient.
    """

    signatures: list[dict[str, int]] = []
    for tilde_count in range(5):
        for weyl_count in range(3):
            if 1 + tilde_count + 2 * weyl_count != 5:
                continue
            for ghost_tilde_count in range(tilde_count + 1):
                form_tilde_count = tilde_count - ghost_tilde_count
                if 1 + ghost_tilde_count != ghost_number:
                    continue
                if form_tilde_count + 2 * weyl_count != form_degree:
                    continue
                signatures.append(
                    {
                        "explicit_omega_count": 1,
                        "tilde_omega_ghost_component_count": ghost_tilde_count,
                        "tilde_omega_form_component_count": form_tilde_count,
                        "weyl_two_form_count": weyl_count,
                    }
                )
    return signatures


def euler_bidegree_manifests() -> tuple[dict[str, Any], ...]:
    """Return content-addressable manifests for every Euler descent bidegree."""

    normalization = euler_normalization_contract()
    coefficients = normalization["project_coefficients"]
    manifests: list[dict[str, Any]] = []
    for index, (ghost_number, form_degree) in enumerate(EULER_BIDEGREES):
        d_sign = 1 if ghost_number % 2 == 0 else -1
        signatures = _carrier_signatures(ghost_number, form_degree)
        payload = {
            "manifest_version": "euler-bidegree-v1",
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
            "ghost_number": ghost_number,
            "form_degree": form_degree,
            "total_degree": ghost_number + form_degree,
            "total_differential": "D = Q_W + (-1)^ghost_number d_h",
            "d_h_sign_on_this_component": d_sign,
            "descent_equation_to_next_bidegree": (
                None
                if index == len(EULER_BIDEGREES) - 1
                else f"Q_W a^{form_degree}_{ghost_number} "
                f"{'+' if (ghost_number + 1) % 2 == 0 else '-'} "
                f"d_h a^{form_degree - 1}_{ghost_number + 1} = 0"
            ),
            "source_template_coefficient": coefficients[index] if index < 3 else None,
            "coarse_carrier_signatures": signatures,
            "coarse_carrier_signature_count": len(signatures),
            "dictionary_sha256": generalized_connection_dictionary()[
                "dictionary_sha256"
            ],
            "normalization_sha256": normalization["normalization_sha256"],
            "coverage_scope": "FROZEN_GENERALIZED_CONNECTION_CARRIER_ALGEBRA",
            "tensor_orbit_status": "NOT_COMPUTED",
            "canonical_quotient_status": "NOT_COMPUTED",
            "closure_status": "NOT_COMPUTED",
        }
        manifests.append({**payload, "manifest_sha256": canonical_sha256(payload)})
    if tuple((row["ghost_number"], row["form_degree"]) for row in manifests) != EULER_BIDEGREES:
        raise AssertionError("Euler bidegree coverage drifted")
    if any(row["total_degree"] != 5 for row in manifests):
        raise AssertionError("Euler total degree drifted")
    return tuple(manifests)
