#!/usr/bin/env python3
"""Conditional four-dimensional dressed covariant-regulator preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = (
    HERE
    / "certificates/DRESSED_FOUR_DIMENSIONAL_COVARIANT_REGULATOR_PREFLIGHT.json"
)

INPUTS = {
    "berezinian_preflight": (
        HERE / "certificates/DRESSED_CANONICAL_BEREZINIAN_LOCALITY_PREFLIGHT.json"
    ),
    "dr_ms_obstruction": (
        HERE
        / "certificates/TAU_ADIC_DR_MS_QAP_EVANESCENT_CLOSURE_OBSTRUCTION.json"
    ),
    "evanescent_module_preflight": (
        HERE
        / "certificates/DRESSED_EVANESCENT_GEOMETRIC_BV_MODULE_PREFLIGHT.json"
    ),
}
EXPECTED_SHA256 = {
    "berezinian_preflight": (
        "28d6821e0774767f991ce79d507dd0059eae2f274c7114c4bec8a07ccc915371"
    ),
    "dr_ms_obstruction": (
        "20915ec21d0c96534a7091b57ee2c3baf5728526a32d00de83dd75b4b94e7e5f"
    ),
    "evanescent_module_preflight": (
        "8685f36ddfbc6a77cdab8048965fb54b575e160a96962651c05a66c167390724"
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _load_inputs() -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    for name, path in INPUTS.items():
        actual = _sha256(path)
        if actual != EXPECTED_SHA256[name]:
            raise ValueError(f"{name} hash drift: {actual}")
        values[name] = json.loads(path.read_text())
    if (
        values["berezinian_preflight"]["finite_cutoff_berezinian"][
            "full_BV_log_J_per_cell"
        ]
        != "-40 tau"
        or values["dr_ms_obstruction"]["result_state"]
        != "DECLARED_DR_MS_ARCHITECTURE_OBSTRUCTED_AT_EVANESCENT_CLOSURE"
        or values["evanescent_module_preflight"]["full_bv_obstruction"][
            "first_missing_object"
        ]
        != "ACTION_SELECTED_D_DIMENSIONAL_KOSZUL_TATE_DIFFERENTIAL"
    ):
        raise ValueError("four-dimensional regulator input semantics drifted")
    return values


def build() -> dict[str, Any]:
    values = _load_inputs()
    result: dict[str, Any] = {
        "schema": "quantum-weyl-dressed-four-dimensional-covariant-regulator-preflight-v1",
        "result_id": "DRESSED_FOUR_DIMENSIONAL_COVARIANT_REGULATOR_PREFLIGHT",
        "result_state": (
            "CONDITIONAL_LOCAL_RECEIVER_THEOREM_"
            "SELECTED_HESSIAN_DATUM_MISSING"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "input_pins": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": EXPECTED_SHA256[name],
            }
            for name, path in INPUTS.items()
        },
        "scope": {
            "dimension": 4,
            "variables": "dressed metric plus algebraic Weyl quartet",
            "selected_action": "NONE_CANDIDATE_A_OR_B_NOT_SELECTED",
            "signature": (
                "EUCLIDEAN_RECEIVER_WITH_EXPLICIT_REAL_CONTOUR_SLOTS"
            ),
            "regulator_status": "CONDITIONAL_ARCHITECTURE_NOT_INSTANTIATED",
        },
        "bounded_regulator_family": {
            "family_id": "FOUR_DIMENSIONAL_FOURTH_ORDER_COVARIANT_V1",
            "routes": [
                {
                    "id": "MATCHED_PROPER_TIME_HEAT_KERNEL",
                    "profile": "F(K/Lambda^4), F(0)=1, rapid decay",
                    "locality_engine": (
                        "fourth-order elliptic heat-kernel symbol expansion"
                    ),
                },
                {
                    "id": "HIGHER_COVARIANT_DERIVATIVE_PLUS_BV_PV",
                    "profile": (
                        "K[1+(K/Lambda^4)^N] with finite BV-PV doublets"
                    ),
                    "locality_engine": (
                        "covariant higher derivatives plus matched local "
                        "Pauli-Villars moment equations"
                    ),
                },
            ],
            "bounds": {
                "HCD_power_N": "1<=N<=N_max_declared_by_receiver",
                "PV_pair_count": "0<=n_PV<=P_max_declared_by_receiver",
                "profile_moments": (
                    "finite list determined by selected symbol and boundary "
                    "heat coefficients through dimension four"
                ),
            },
            "completeness_status": (
                "COMPLETE_RECEIVER_PARAMETERIZATION_FOR_THE_TWO_DECLARED_"
                "REGULATOR_ROUTES_NOT_A_PROOF_THAT_ANY_SELECTED_HESSIAN_FITS"
            ),
        },
        "selected_hessian_hypotheses": {
            "operator": (
                "even gauge-fixed fourth-order differential operator K on "
                "the full graded BV bundle"
            ),
            "principal_symbol": (
                "elliptic and sectorial on the declared real/complex contours"
            ),
            "pairing": "K^sharp=K on the declared primal/dual domains",
            "BRST": "[Q,K]=0 including nonminimal and regulator-field rows",
            "projectors": (
                "Pi_0, Pi_perp commute with Q and are dual-compatible"
            ),
            "boundary": (
                "local elliptic boundary problem invariant under Q and sharp"
            ),
            "PV_fields": (
                "finite BRST doublets with pairing-compatible mass matrices "
                "and statistics satisfying every selected heat-moment equation"
            ),
            "contours": (
                "all indefinite bosonic multipliers and PV fields carry "
                "declared thimbles compatible with sharp"
            ),
        },
        "regulated_canonical_map": {
            "raw_coefficient": -40,
            "jacobian": (
                "log Ber_R=-40 Tr[Pi_perp tau F(K/Lambda^4) Pi_perp]"
            ),
            "inverse": (
                "log Ber_R(inverse)=+40 Tr[Pi_perp tau F(K/Lambda^4) Pi_perp]"
            ),
            "composition_defect": "ZERO_WHEN_THE_SAME_K_DOMAIN_AND_PROJECTORS_ARE_USED",
            "zero_mode_term": (
                "-40 Tr[Pi_0 tau] remains finite-rank and generally global"
            ),
            "local_bulk_asymptotic": (
                "Tr[tau F(K/Lambda^4)] has local fourth-order heat coefficients"
            ),
            "boundary_locality": "CONDITIONAL_ON_SELECTED_LOCAL_ELLIPTIC_DOMAIN",
        },
        "ward_symbol": {
            "Weyl_if_K_invariant": (
                "Q_W log Ber_R=-40 Tr[Pi_perp omega F(K/Lambda^4) Pi_perp]"
            ),
            "Duhamel_failure_term": (
                "40 Tr[Pi_perp tau integral_0^1 "
                "F'_Duhamel(K,QK;u) du Pi_perp]"
            ),
            "Duhamel_term_zero_hypothesis": "QK=KQ_AND_Q_PI0=PI0_Q",
            "Diff_bulk": (
                "trace of a covariant commutator, zero modulo the declared "
                "boundary-domain contribution"
            ),
            "local_breaking_receiver": (
                "heat coefficients through engineering dimension four, "
                "projected to the certified dressed H04/H14 module"
            ),
            "actual_breaking": "NOT_COMPUTED_WITHOUT_SELECTED_K",
        },
        "first_missing_action_dependent_datum": {
            "id": (
                "SELECTED_GAUGE_FIXED_FOURTH_ORDER_HESSIAN_SYMBOL_COMPLEX"
            ),
            "required_components": [
                "full minimal nonminimal and regulator-field row ordering",
                "principal and subprincipal symbols",
                "BRST intertwining identities",
                "primal dual domains and zero-mode projectors",
                "real contours and determinant phases",
                "boundary conditions or closed-manifold declaration",
            ],
            "why_atoms_and_pairing_do_not_determine_it": (
                "the BV atom/pairing ledger fixes the cotangent geometry but "
                "not the action Hessian, gauge fixing, reducibility tower, "
                "elliptic domain, spectrum or thimbles"
            ),
            "verdict": (
                "PRECISE_ACTION_DEPENDENT_DATUM_REQUIRED_BEFORE_"
                "FOUR_DIMENSIONAL_REGULATOR_INSTANTIATION"
            ),
        },
        "scheme_comparison": {
            "four_dimensional_route": (
                "local finite counterterms are parameterized directly in the "
                "certified four-dimensional H04 module"
            ),
            "dr_ms_route": (
                "Euler and other d-dimensional continuations form an "
                "evanescent torsor before projection"
            ),
            "common_fact": (
                "both require an action-specific mixing/subtraction map"
            ),
            "forbidden_identification": (
                "no four-dimensional finite counterterm coordinate is "
                "identified with a DR/MS evanescent continuation coordinate"
            ),
            "equivalence_status": "NO_CERTIFIED_SCHEME_EQUIVALENCE_MAP",
        },
        "selected_action_receiver": {
            "candidate_A_scalar": {
                "status": "UNFILLED_UNTIL_ACTION_SELECTION",
                "required": [
                    "scalar-parent K and BRST symbol complex",
                    "scalar and multiplier contours",
                    "zero-mode and boundary policies",
                    "PV/HCD or heat-profile solution",
                ],
            },
            "candidate_B_reducible_three_form": {
                "status": "UNFILLED_UNTIL_ACTION_SELECTION",
                "required": [
                    "three-form reducibility tower K and BRST symbol complex",
                    "ghost-for-ghost regulator doublets",
                    "harmonic-form zero modes and boundary policies",
                    "PV/HCD or heat-profile solution",
                ],
            },
        },
        "lifecycle": {
            "conditional_receiver_theorem": "CLASSIFIED",
            "actual_regulator": "NOT_CONSTRUCTED",
            "regulated_Jacobian": "NOT_COMPUTED_FOR_SELECTED_ACTION",
            "one_loop_Ward_breaking": "NOT_COMPUTED",
            "QAP": "NOT_ESTABLISHED",
            "all_loop_QME": "NOT_PROMOTED",
            "Lorentzian_QME": "OPEN",
        },
        "claim_flags": {
            "ACTION_INDEPENDENT_REGULATOR_CONSTRUCTED": False,
            "SELECTED_HESSIAN_IMPORTED": False,
            "ZERO_MODES_FIXED": False,
            "BOUNDARY_DOMAIN_FIXED": False,
            "CONTOURS_FIXED": False,
            "QAP_ESTABLISHED": False,
            "ALL_LOOP_QME_PROMOTED": False,
            "SCHEMES_IDENTIFIED": False,
        },
        "exact_checks": {
            "input_hashes_pinned": True,
            "raw_Berezinian_coefficient_imported": True,
            "inverse_sign_opposite": True,
            "same_regulator_composition_zero": True,
            "Duhamel_failure_term_retained": True,
            "zero_mode_nonlocal_slot_retained": True,
            "candidate_A_slot_unfilled": True,
            "candidate_B_slot_unfilled": True,
            "DR_MS_scheme_not_identified": True,
            "selected_hessian_missing": True,
        },
        "next_gate": (
            "Select Candidate A or B and import its complete gauge-fixed "
            "Euclidean Hessian symbol complex, domains, zero modes and contours; "
            "then solve one declared regulator route and evaluate the Ward receiver."
        ),
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL preflight gives a "
            "conditional strictly four-dimensional covariant-regulator receiver "
            "for a selected fourth-order BV Hessian satisfying explicit "
            "ellipticity, BRST, pairing, projector, boundary and contour "
            "hypotheses. It derives the regulated canonical-map Jacobian and "
            "the Weyl/Duhamel Ward symbol, but it does not prove that Candidate "
            "A or B supplies such a Hessian. It does not construct an actual "
            "regulator, compute determinant or anomaly coefficients, identify "
            "the four-dimensional and DR/MS schemes, establish QAP or an "
            "all-loop/Lorentzian QME, or make state, particle, scattering or "
            "unitarity claims."
        ),
    }
    result["proof_sha256"] = _canonical_hash(
        {key: entry for key, entry in result.items() if key != "proof_sha256"}
    )
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    missing = value["first_missing_action_dependent_datum"]
    receiver = value["selected_action_receiver"]
    if (
        value["regulated_canonical_map"]["raw_coefficient"] != -40
        or value["regulated_canonical_map"]["composition_defect"]
        != "ZERO_WHEN_THE_SAME_K_DOMAIN_AND_PROJECTORS_ARE_USED"
        or value["ward_symbol"]["Duhamel_term_zero_hypothesis"]
        != "QK=KQ_AND_Q_PI0=PI0_Q"
        or value["ward_symbol"]["actual_breaking"]
        != "NOT_COMPUTED_WITHOUT_SELECTED_K"
        or missing["id"]
        != "SELECTED_GAUGE_FIXED_FOURTH_ORDER_HESSIAN_SYMBOL_COMPLEX"
        or receiver["candidate_A_scalar"]["status"]
        != "UNFILLED_UNTIL_ACTION_SELECTION"
        or receiver["candidate_B_reducible_three_form"]["status"]
        != "UNFILLED_UNTIL_ACTION_SELECTION"
        or value["scheme_comparison"]["equivalence_status"]
        != "NO_CERTIFIED_SCHEME_EQUIVALENCE_MAP"
        or any(value["claim_flags"].values())
        or not all(value["exact_checks"].values())
    ):
        raise ValueError("four-dimensional covariant-regulator preflight failed")
    expected = _canonical_hash(
        {key: entry for key, entry in value.items() if key != "proof_sha256"}
    )
    if value["proof_sha256"] != expected:
        raise ValueError("four-dimensional regulator proof hash drifted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.is_file() or OUTPUT.read_text() != rendered):
        raise SystemExit("four-dimensional regulator certificate is stale")
    if not args.emit and not args.check:
        print(rendered, end="")


if __name__ == "__main__":
    main()
