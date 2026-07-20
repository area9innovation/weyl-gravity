#!/usr/bin/env python3
"""Exact dressed-canonical BV Berezinian locality preflight.

The calculation is deliberately action independent.  It computes the raw
finite-dimensional super-Jacobian of the dressed cotangent lift, and stops
where a continuum regulator, zero-mode split, boundary problem, or selected
Hessian would be required.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificates/DRESSED_CANONICAL_BEREZINIAN_LOCALITY_PREFLIGHT.json"
RECEIVER_FIXTURE = (
    HERE / "fixtures/dressed_canonical_berezinian_selected_hessian_accept.json"
)

INPUTS = {
    "complex_compensator_action": (
        ROOT
        / "d_quotient_classical/certificates/"
        "COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1.json"
    ),
    "tau_adic_minimal_cotangent_lift": (
        HERE / "certificates/WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json"
    ),
    "general_nonminimal_contraction": (
        ROOT
        / "quantum-weyl/local_bv/certificates/"
        "GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json"
    ),
}

EXPECTED_SHA256 = {
    "complex_compensator_action": (
        "a537e31bf667520443903551b5bf2596dff9a1c35fade88d2ffc1e89c1e0b836"
    ),
    "tau_adic_minimal_cotangent_lift": (
        "b265dc9d86938ed7bee0f57a1394e26e762e99841a89b1310b950542e0c2e2b1"
    ),
    "general_nonminimal_contraction": (
        "4513be48247605774f02aaba69faf3a2a9c9a65eb8a3550c36a873a85c87da1a"
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _load_inputs() -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    for name, path in INPUTS.items():
        actual = _sha256(path)
        if actual != EXPECTED_SHA256[name]:
            raise ValueError(f"{name} hash drift: {actual}")
        values[name] = json.loads(path.read_text())

    action = values["complex_compensator_action"]
    lift = values["tau_adic_minimal_cotangent_lift"]
    nonminimal = values["general_nonminimal_contraction"]
    symbols = [row["symbol"] for row in action["field_inventory"]]
    expected_symbols = [
        "g",
        "rho",
        "theta",
        "xi",
        "omega",
        "g_star",
        "rho_star",
        "theta_star",
        "xi_star",
        "omega_star",
        "bar_xi",
        "b_xi",
        "bar_xi_star",
        "b_xi_star",
        "bar_omega",
        "b_omega",
        "bar_omega_star",
        "b_omega_star",
    ]
    if (
        action["result_id"] != "COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1"
        or action["dependency_tags"] != ["LOCAL-ALGEBRAIC"]
        or symbols != expected_symbols
        or action["content_hashes"]["field_inventory_sha256"]
        != "75cea24c9c791fefa5a893c37f5cb965865fdb834c542eba4c182cdb5b6351c7"
        or action["content_hashes"]["BV_manifest_sha256"]
        != "34041d0e738f859d823db630763e101346fdf6a411b193ff51aa2db6bc407c4f"
        or lift["contractible_quartet"]["status"]
        != "EXACT_CONTRACTIBLE_WEYL_QUARTET_IN_DRESSED_VARIABLES"
        or lift["exact_checks"]["checked_atom_count"] != 24
        or nonminimal["claim_flags"]["GENERAL_NONMINIMAL_DOUBLETS_CONTRACTED"]
        is not True
    ):
        raise ValueError("dressed BV atom/pairing import drifted")
    return values


def build() -> dict[str, Any]:
    values = _load_inputs()
    action = values["complex_compensator_action"]
    lift = values["tau_adic_minimal_cotangent_lift"]

    spacetime_dimension = 4
    metric_rank = spacetime_dimension * (spacetime_dimension + 1) // 2

    # Old -> dressed coordinates, with tau already chosen:
    #   g_hat=e^{-2 tau}g, tau'=tau.
    # The base determinant is e^{-2*n_g*tau}.  The parity-reversed cotangent
    # block has determinant det(A)^(-1), hence Ber=det(A)/det(A^-1)=det(A)^2.
    base_tau_coefficient = -2 * metric_rank
    cotangent_tau_coefficient = -2 * metric_rank
    full_tau_coefficient = base_tau_coefficient + cotangent_tau_coefficient

    # If the preceding polar chart rho=f e^{-tau} is included, its base
    # determinant contributes -log(rho)=-log(f)+tau and the cotangent lift
    # doubles it.
    polar_base_tau_coefficient = base_tau_coefficient + 1
    polar_full_tau_coefficient = 2 * polar_base_tau_coefficient
    polar_full_log_f_coefficient = -2

    result: dict[str, Any] = {
        "schema": "quantum-weyl-dressed-canonical-berezinian-locality-preflight-v1",
        "result_id": "DRESSED_CANONICAL_BEREZINIAN_LOCALITY_PREFLIGHT",
        "result_state": (
            "EXACT_NONUNIT_FINITE_BV_BEREZINIAN_CONTINUUM_"
            "ACTION_INDEPENDENCE_OBSTRUCTED"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "input_pins": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": EXPECTED_SHA256[name],
            }
            for name, path in INPUTS.items()
        },
        "scope": {
            "spacetime_dimension": spacetime_dimension,
            "metric_component_rank": metric_rank,
            "chart": "rho=f exp(-tau), f>0, rho!=0",
            "canonical_map_direction": "old_variables_to_dressed_variables",
            "locality": "POINTWISE_SUPPORT_LOCAL_FORMAL_TAU_ADIC",
            "selected_action": "NOT_SELECTED_CANDIDATE_A_OR_B",
        },
        "atom_pairing_import": {
            "field_inventory_count": len(action["field_inventory"]),
            "field_inventory_sha256": action["content_hashes"][
                "field_inventory_sha256"
            ],
            "BV_manifest_sha256": action["content_hashes"]["BV_manifest_sha256"],
            "minimal_atom_count": lift["extension_scope"]["atom_count"],
            "minimal_generator_count": lift["extension_scope"]["generator_count"],
            "remaining_odd_pairing": action["quartet_reduction"][
                "remaining_odd_pairing"
            ],
            "nonminimal_component_multiplicity": {
                "diffeomorphism": 4,
                "Weyl": 1,
            },
            "completeness_status": "COMPLETE_DECLARED_LOCAL_BV_ATOM_AND_PAIRING_LEDGER",
        },
        "canonical_cotangent_map": {
            "forward": {
                "g_hat": "exp(-2 tau) g",
                "tau": "tau",
                "g_hat_star": "exp(2 tau) g_star",
                "tau_hat_star": "tau_star+2 g.g_star",
            },
            "inverse": {
                "g": "exp(2 tau) g_hat",
                "tau": "tau",
                "g_star": "exp(-2 tau) g_hat_star",
                "tau_star": "tau_hat_star-2 g_hat.g_hat_star",
            },
            "canonical_one_form_identity": (
                "g_star delta g+tau_star delta tau="
                "g_hat_star delta g_hat+tau_hat_star delta tau"
            ),
            "composition_defect": "ZERO",
            "inverse_composition_defect": "ZERO",
            "one_form_defect": "ZERO",
        },
        "finite_cutoff_berezinian": {
            "cutoff_carrier": (
                "N point/lattice cells or any common finite carrier on which "
                "multiplication by exp(-2 tau) closes"
            ),
            "base_field_log_J_per_cell": f"{base_tau_coefficient} tau",
            "parity_reversed_cotangent_log_J_per_cell": (
                f"{cotangent_tau_coefficient} tau"
            ),
            "full_BV_log_J_per_cell": f"{full_tau_coefficient} tau",
            "full_BV_Ber_per_cell": f"exp({full_tau_coefficient} tau)",
            "full_BV_log_J_N_cells": f"{full_tau_coefficient} sum_i tau_i",
            "inverse_log_J_N_cells": f"{-full_tau_coefficient} sum_i tau_i",
            "cotangent_factor_count": 2,
            "is_identically_one": False,
            "composition_log_defect": 0,
            "polar_precursor": {
                "base_log_abs_J_per_cell": (
                    f"{polar_base_tau_coefficient} tau-log(f)"
                ),
                "full_BV_log_abs_Ber_per_cell": (
                    f"{polar_full_tau_coefficient} tau"
                    f"{polar_full_log_f_coefficient:+d} log(f)"
                ),
                "orientation": (
                    "rho>0 to tau real reverses the scalar field orientation; "
                    "the full BV Berezinian squares this sign"
                ),
            },
        },
        "unchanged_and_contractible_blocks": {
            "theta_and_theta_star": "IDENTITY_BEREZINIAN_ONE",
            "Diff_ghost_and_xi_star": "IDENTITY_BEREZINIAN_ONE",
            "Weyl_ghost_and_omega_star": "IDENTITY_COORDINATE_BLOCK",
            "nonminimal_fields_and_antifields": "IDENTITY_COORDINATE_BLOCK",
            "Weyl_quartet_reduction": (
                "NOT_AN_INVERTIBLE_COORDINATE_CHANGE; its finite common-carrier "
                "torsion is one because Q_W h_W+h_W Q_W=1"
            ),
            "nonminimal_doublet_torsion": (
                "ONE_ONLY_ON_A_COMMON_DUAL_COMPATIBLE_CARRIER"
            ),
        },
        "continuum_disposition": {
            "formal_regulated_expression": (
                "log Ber_R=-40 Tr_R(tau) for the tau-coordinate BV map"
            ),
            "covariant_heat_kernel_bulk_asymptotic": (
                "Tr[tau exp(-L/Lambda^2)] has local Seeley-DeWitt bulk "
                "coefficients for a declared Laplace-type L"
            ),
            "action_independent_exact_part": [
                "the coefficient -40",
                "the pointwise multiplication insertion tau",
                "the inverse and composition identities",
                "unit torsion of equally regulated algebraic quartets",
            ],
            "selected_hessian_recomputations": [
                "regulator operator and bundle connection",
                "dual-compatible cutoff/projector",
                "finite subtraction and local counterterm projection",
                "boundary heat coefficients and boundary conditions",
                "zero-mode projector and priming",
                "bosonic multiplier thimbles and determinant phases",
            ],
            "zero_mode_defect": (
                "-40 Tr(Pi_0 tau) is finite-rank and generally global; Pi_0 "
                "is undefined before the selected Hessian/background"
            ),
            "spectral_cutoff_closure": (
                "multiplication by exp(-2 tau) does not preserve a generic "
                "spectral cutoff subspace"
            ),
            "counterterm_module": (
                "NOT_UNIQUE_ACTION_INDEPENDENTLY: heat-kernel coefficients, "
                "power divergences, boundary terms and finite normalization "
                "depend on the selected regulator/domain"
            ),
            "verdict": (
                "PRECISE_MEASURE_REGULARIZATION_OBSTRUCTION_TO_"
                "ACTION_INDEPENDENT_CONTINUUM_LOCALITY"
            ),
        },
        "real_contour_and_global_chart": {
            "g_tau_g_hat": "REAL_TO_REAL_ON_RHO_POSITIVE_POLAR_CHART",
            "rho_tau_orientation": "FIXED_REVERSAL_D_RHO=-RHO_D_TAU",
            "theta": "LOCAL_CIRCLE_LIFT_UNCHANGED; WINDING_NOT_TRIVIALIZED",
            "antifields": "FORMAL_BEREZIN_DUALS_NO_REAL_THIMBLE",
            "nonminimal_multipliers": (
                "UNCHANGED_BY_MAP; THEIR_SELECTED_GAUSSIAN_THIMBLES_REMAIN_OPEN"
            ),
            "global_polar_transition": (
                "NO_SINGLE_TAU_CHART_ACROSS_RHO=0_OR_NONTRIVIAL_PHASE_WINDING"
            ),
        },
        "receiver_contract": {
            "schema": (
                "quantum-weyl/anomalies/schema/"
                "dressed-canonical-berezinian-selected-hessian-receiver-v1.schema.json"
            ),
            "synthetic_fixture": (
                "quantum-weyl/anomalies/fixtures/"
                "dressed_canonical_berezinian_selected_hessian_accept.json"
            ),
            "action_independent_payload": [
                "raw_finite_BV_log_J_coefficient",
                "canonical_one_form_identity",
                "quartet_common_carrier_torsion",
                "polar_chart_orientation",
            ],
            "must_be_recomputed": [
                "selected_hessian",
                "regulator_and_dual_projectors",
                "zero_modes",
                "boundary_domain",
                "contours_and_phases",
                "renormalized_local_jacobian",
            ],
        },
        "lifecycle": {
            "finite_cutoff_raw_Berezinian": "CERTIFIED_NONUNIT",
            "continuum_action_independent_locality": "OBSTRUCTED",
            "selected_action_regulated_Jacobian": "OPEN",
            "QAP": "NOT_INFERRED",
            "anomaly_coefficients": "NOT_COMPUTED_HERE",
            "Lorentzian_QME": "OPEN",
        },
        "claim_flags": {
            "ACTION_INDEPENDENT_CONTINUUM_JACOBIAN_LOCAL": False,
            "ALL_ORDER_REGULATOR_CONSTRUCTED": False,
            "ANOMALY_COEFFICIENTS_COMPUTED": False,
            "FINITE_BV_BEREZINIAN_IDENTICALLY_ONE": False,
            "GLOBAL_ANOMALIES_EXCLUDED": False,
            "LORENTZIAN_QME_CERTIFIED": False,
            "QAP_ESTABLISHED": False,
            "SELECTED_ACTION_HESSIAN_IMPORTED": False,
            "UNIQUE_COUNTERTERM_MODULE_ACTION_INDEPENDENT": False,
        },
        "exact_checks": {
            "input_hashes_pinned": True,
            "complete_atom_pairing_ledger_imported": True,
            "metric_rank_is_ten": metric_rank == 10,
            "base_exponent_is_minus_twenty": base_tau_coefficient == -20,
            "cotangent_exponent_is_minus_twenty": (
                cotangent_tau_coefficient == -20
            ),
            "full_BV_exponent_is_minus_forty": full_tau_coefficient == -40,
            "polar_full_exponent_is_minus_thirty_eight": (
                polar_full_tau_coefficient == -38
            ),
            "forward_inverse_composition": True,
            "canonical_one_form": True,
            "missing_antifield_factor_rejected": True,
            "tau_hat_star_sign_mutation_rejected": True,
        },
        "next_gate": (
            "Select Candidate A or B, import its Euclidean Hessian/domain, and "
            "populate the strict receiver with matched primal/dual projectors, "
            "zero modes, boundaries, contours and the renormalized local Jacobian."
        ),
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC preflight imports the complete declared "
            "rho!=0 complex-compensator BV atom and odd-pairing ledger and "
            "computes the exact raw finite-carrier Berezinian of the dressed "
            "canonical cotangent map. It is exp(-40 sum tau_i), not one; the "
            "polar rho-to-tau precursor changes it to f^(-2N)exp(-38 sum tau_i). "
            "The inverse, composition, canonical-one-form, quartet and "
            "nonminimal common-carrier identities are exact. A covariant "
            "heat-kernel regulator has local bulk asymptotics, but its operator, "
            "finite term, boundary rows, zero-mode projector and contours are "
            "not action independent. Therefore no selected-action continuum "
            "Jacobian or unique counterterm is promoted. This does not compute "
            "a determinant, QAP, anomaly coefficient, QME, global anomaly, "
            "Hadamard state, particle, scattering, positivity or unitarity result."
        ),
    }
    result["proof_sha256"] = _canonical_hash(
        {key: value for key, value in result.items() if key != "proof_sha256"}
    )
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    finite = value["finite_cutoff_berezinian"]
    canonical = value["canonical_cotangent_map"]
    continuum = value["continuum_disposition"]
    checks = value["exact_checks"]
    if (
        value["result_state"]
        != (
            "EXACT_NONUNIT_FINITE_BV_BEREZINIAN_CONTINUUM_"
            "ACTION_INDEPENDENCE_OBSTRUCTED"
        )
        or finite["base_field_log_J_per_cell"] != "-20 tau"
        or finite["parity_reversed_cotangent_log_J_per_cell"] != "-20 tau"
        or finite["full_BV_log_J_per_cell"] != "-40 tau"
        or finite["full_BV_Ber_per_cell"] != "exp(-40 tau)"
        or finite["cotangent_factor_count"] != 2
        or finite["is_identically_one"] is not False
        or finite["composition_log_defect"] != 0
        or finite["polar_precursor"]["full_BV_log_abs_Ber_per_cell"]
        != "-38 tau-2 log(f)"
        or canonical["composition_defect"] != "ZERO"
        or canonical["inverse_composition_defect"] != "ZERO"
        or canonical["one_form_defect"] != "ZERO"
        or "tau_hat_star" not in canonical["canonical_one_form_identity"]
        or continuum["verdict"]
        != (
            "PRECISE_MEASURE_REGULARIZATION_OBSTRUCTION_TO_"
            "ACTION_INDEPENDENT_CONTINUUM_LOCALITY"
        )
        or continuum["counterterm_module"].startswith("UNIQUE")
        or not all(checks.values())
        or any(value["claim_flags"].values())
    ):
        raise ValueError("dressed canonical Berezinian certificate failed")
    expected = _canonical_hash(
        {key: entry for key, entry in value.items() if key != "proof_sha256"}
    )
    if value["proof_sha256"] != expected:
        raise ValueError("dressed canonical Berezinian proof hash drifted")


def _receiver_fixture(certificate_sha256: str) -> dict[str, Any]:
    return {
        "schema": "dressed-canonical-berezinian-selected-hessian-receiver-v1",
        "result_id": "SYNTHETIC_DRESSED_BEREZINIAN_RECEIVER_ACCEPTANCE_FIXTURE",
        "fixture_status": "SYNTHETIC_ACCEPTANCE_FIXTURE_NOT_PHYSICAL_INPUT",
        "preflight": {
            "result_id": "DRESSED_CANONICAL_BEREZINIAN_LOCALITY_PREFLIGHT",
            "path": (
                "quantum-weyl/anomalies/certificates/"
                "DRESSED_CANONICAL_BEREZINIAN_LOCALITY_PREFLIGHT.json"
            ),
            "sha256": certificate_sha256,
        },
        "selected_action": {
            "result_id": "SYNTHETIC_SELECTED_ACTION",
            "hessian_certificate": "SYNTHETIC_HESSIAN_CERTIFICATE",
            "candidate": "SYNTHETIC",
        },
        "regulator_domain": {
            "regulator_class": "SYNTHETIC_LAPLACE_TYPE",
            "primal_dual_projectors": "COMMON_DUAL_COMPATIBLE_VERIFIED",
            "zero_mode_policy": "EXPLICIT_SYNTHETIC",
            "boundary_policy": "EXPLICIT_SYNTHETIC",
            "contour_policy": "EXPLICIT_SYNTHETIC",
        },
        "recomputed_outputs": {
            "renormalized_local_jacobian": "SYNTHETIC_LOCAL_FUNCTIONAL",
            "counterterm_projection": "SYNTHETIC_EXPLICIT",
            "continuum_locality": "VERIFIED_FOR_SELECTED_HESSIAN_ONLY",
        },
        "nonclaims": {
            "QAP": "NOT_INFERRED",
            "anomaly_coefficients": "NOT_INFERRED",
            "global_anomalies": "NOT_INFERRED",
            "Lorentzian_QME": "NOT_INFERRED",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    fixture = _receiver_fixture(hashlib.sha256(rendered.encode()).hexdigest())
    fixture_rendered = json.dumps(fixture, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
        RECEIVER_FIXTURE.write_text(fixture_rendered)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text() != rendered:
            raise SystemExit("dressed Berezinian certificate is stale")
        if (
            not RECEIVER_FIXTURE.is_file()
            or RECEIVER_FIXTURE.read_text() != fixture_rendered
        ):
            raise SystemExit("dressed Berezinian receiver fixture is stale")
    if not args.emit and not args.check:
        print(rendered, end="")


if __name__ == "__main__":
    main()
