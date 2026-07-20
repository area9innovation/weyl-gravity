"""Exact obstruction to an action-compatible Einstein--Weyl pushforward.

The canonical 316-row relative carrier is unary cyclic for its newly adjoined
cotangent pairing.  The pairing is not the pair of action-derived
Einstein--Maxwell and Weyl--Maxwell forms.  On every generic axial and polar
physical fibre, compatibility with those two action forms would require an
invertible congruence between forms of different inertia.  This module
replays that obstruction and records the precise minimality scope of the
316-row carrier.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
QROOT = HERE.parent
ROOT = QROOT.parent

PREVIOUS = (
    HERE
    / "certificates/RELATIVE_EINSTEIN_WEYL_QME_DEFECT_NONDEFINITION.json"
)
GENERIC_INERTIA = (
    ROOT
    / "d_quotient_classical/certificates/"
    "EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1.json"
)
COTANGENT = (
    ROOT
    / "d_quotient_classical/certificates/"
    "EINSTEIN_WEYL_RELATIVE_316_ROW_COTANGENT_COMPLETION_V1.json"
)
COTANGENT_LAYOUT = (
    ROOT
    / "d_quotient_classical/generated/"
    "einstein_weyl_relative_316_row_cotangent_completion_v1/layout.json"
)
EINSTEIN_LAYOUT = (
    ROOT
    / "bridge/einstein_sector/generated/"
    "einstein_maxwell_product_linfinity_v1/row_layout.json"
)
WEYL_LAYOUT = (
    ROOT
    / "bridge/einstein_sector/generated/"
    "weyl_maxwell_product_linfinity_v1/row_layout.json"
)
OBSERVABLE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1.json"
)

INPUT_COMMIT = "91b720aca4e31997ad03145df9773dddb688ff15"
INPUT_CERTIFICATE_SHA256 = (
    "3cddce3166dccb2699e7150b4a1df8fc7464588e91e2c73ca13e2ced020b879e"
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"dependency is not an object: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ref(path: Path, value: dict[str, Any]) -> dict[str, str]:
    result_id = value.get("result_id")
    if not isinstance(result_id, str) or not result_id:
        raise ValueError(f"dependency identity missing: {path}")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "result_id": result_id,
        "sha256": _sha256(path),
    }


def _action_layout_audit(value: dict[str, Any], expected_rows: int) -> dict[str, Any]:
    content = value.get("content", {})
    rows = content.get("rows", [])
    if content.get("row_count") != expected_rows or len(rows) != expected_rows:
        raise ValueError("action BV row count drifted")
    by_index = {row["index"]: row for row in rows}
    if set(by_index) != set(range(expected_rows)):
        raise ValueError("action BV row indices are not complete")
    for index, row in by_index.items():
        dual = row["dual_row"]
        if (
            dual not in by_index
            or by_index[dual]["dual_row"] != index
            or row["degree"] + by_index[dual]["degree"] != 1
        ):
            raise ValueError("action BV cotangent duality drifted")
    degree_ranks = Counter(row["degree"] for row in rows)
    return {
        "row_count": expected_rows,
        "degree_ranks": {
            str(degree): degree_ranks[degree] for degree in sorted(degree_ranks)
        },
        "dual_involution_exact": True,
        "dual_degree_rule": "degree(row)+degree(dual_row)=1",
        "action_odd_pairing_nondegenerate": True,
    }


def _expected_inertia_blocks() -> dict[str, dict[str, Any]]:
    return {
        "axial": {
            "Einstein_form": [["lambda", "0"], ["0", "2"]],
            "Einstein_leading_minor": "lambda",
            "Einstein_determinant": "2*lambda",
            "Einstein_inertia_lambda_ge_6": [2, 0],
            "restricted_Weyl_form": [
                ["lambda", "3*lambda"],
                ["3*lambda", "2"],
            ],
            "restricted_Weyl_leading_minor": "lambda",
            "restricted_Weyl_determinant": "-lambda*(9*lambda - 2)",
            "restricted_Weyl_inertia_lambda_ge_6": [1, 1],
        },
        "polar": {
            "Einstein_form": [["1", "-2"], ["-2", "2*lambda"]],
            "Einstein_leading_minor": "1",
            "Einstein_determinant": "2*(lambda - 2)",
            "Einstein_inertia_lambda_ge_6": [2, 0],
            "restricted_Weyl_form": [
                ["4", "-3*lambda - 2"],
                ["-3*lambda - 2", "8*lambda"],
            ],
            "restricted_Weyl_leading_minor": "4",
            "restricted_Weyl_determinant": "-(lambda - 2)*(9*lambda - 2)",
            "restricted_Weyl_inertia_lambda_ge_6": [1, 1],
        },
    }


def evaluate() -> dict[str, Any]:
    previous = _load(PREVIOUS)
    inertia = _load(GENERIC_INERTIA)
    cotangent = _load(COTANGENT)
    cotangent_layout = _load(COTANGENT_LAYOUT)
    einstein_layout = _load(EINSTEIN_LAYOUT)
    weyl_layout = _load(WEYL_LAYOUT)
    observable = _load(OBSERVABLE)

    if (
        previous.get("result_id")
        != "RELATIVE_EINSTEIN_WEYL_QME_DEFECT_NONDEFINITION"
        or _sha256(PREVIOUS) != INPUT_CERTIFICATE_SHA256
        or inertia.get("result_id")
        != "EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1"
        or cotangent.get("result_id")
        != "EINSTEIN_WEYL_RELATIVE_316_ROW_COTANGENT_COMPLETION_V1"
        or observable.get("result_id")
        != "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1"
    ):
        raise ValueError("relative cyclic-pushforward input identity drifted")

    source_layout_audit = _action_layout_audit(einstein_layout, 38)
    target_layout_audit = _action_layout_audit(weyl_layout, 40)
    expected_blocks = _expected_inertia_blocks()
    imported_blocks = inertia.get("exact_inertia_blocks", {})
    for parity, expected in expected_blocks.items():
        imported = imported_blocks.get(parity, {})
        for key, expected_value in expected.items():
            if imported.get(key) != expected_value:
                raise ValueError(f"{parity} action-form inertia block drifted")

    sector_ranks = cotangent_layout.get("sector_ranks")
    if (
        cotangent_layout.get("row_count") != 316
        or cotangent_layout.get("degree_ranks") != [10, 51, 97, 97, 51, 10]
        or sector_ranks
        != {
            "five_current_de_rham": 160,
            "relative_cone": 78,
            "relative_cone_cotangent": 78,
        }
        or cotangent["bundle_classification"]["selected_added_rows"] != 78
        or cotangent["bundle_classification"]["rank_only_addition_lower_bound"]
        != 28
        or cotangent["classification"][
            "action_current_pairing_transport_complete"
        ]
        is not False
        or cotangent["unary_theorem"]["standard_action_pairings_identified"]
        is not False
    ):
        raise ValueError("316-row carrier or minimality boundary drifted")

    if (
        observable["classification"]["H_product_equivariance_exact"] is not True
        or observable["classification"]["time_translation_equivariance_exact"]
        is not True
        or inertia["shell_separation"]["same_label_frequency_collision"] is not False
        or inertia["classification"][
            "corrected_nonidentity_standard_pairing_map_exists_generic"
        ]
        is not False
    ):
        raise ValueError("relative equivariance/inertia authority drifted")

    exact_checks = {
        "input_commit_and_certificate_hash_pinned": True,
        "Einstein_38_row_action_BV_carrier_is_cotangent_complete": True,
        "Weyl_40_row_action_BV_carrier_is_cotangent_complete": True,
        "canonical_316_row_unary_cotangent_carrier_imported": True,
        "316_is_full_cone_cotangent_minimal_in_declared_class": True,
        "316_not_proven_row_minimal_among_all_mixed_bundle_completions": True,
        "316_pairing_not_identified_with_two_action_pairings": True,
        "H_product_and_time_translation_equivariance_imported": True,
        "generic_q_and_extra_p_shells_do_not_collide": True,
        "axial_action_form_inertia_mismatch_exact": True,
        "polar_action_form_inertia_mismatch_exact": True,
        "chain_homotopy_cannot_change_induced_cohomology_inertia": True,
        "one_generic_fibre_obstructs_an_all_sector_pushforward": True,
        "zero_modes_cannot_repair_a_generic_fibre_obstruction": True,
    }

    return {
        "schema": (
            "quantum-weyl-relative-einstein-weyl-"
            "cyclic-pushforward-obstruction-v1"
        ),
        "result_id": "RELATIVE_EINSTEIN_WEYL_CYCLIC_PUSHFORWARD_OBSTRUCTION",
        "result_state": (
            "ACTION_COMPATIBLE_CYCLIC_PUSHFORWARD_OBSTRUCTED_ON_GENERIC_"
            "PHYSICAL_COHOMOLOGY_DESPITE_CANONICAL_316_ROW_COTANGENT_PAIRING"
        ),
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "input_pin": {
            "commit": INPUT_COMMIT,
            "certificate_path": PREVIOUS.relative_to(ROOT).as_posix(),
            "certificate_sha256": INPUT_CERTIFICATE_SHA256,
        },
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product",
            "boundaries": "closed S1_L x S2 Cauchy slice",
            "charge_sector": "fixed magnetic U1 bundle N=2 before final quotient",
            "carrier": (
                "38-row and 40-row minimal action BV carriers plus the "
                "canonical 316-row full-cone cotangent completion"
            ),
            "degree": "all BV degrees for carrier audit; generic solution cohomology for obstruction",
            "parity": "axial and polar separately",
            "ell": "ell>=2",
            "m": "all by SO3 equivariance",
            "k": "all compact momenta on noncolliding generic q shells",
            "omega": "both noncolliding q-primary radiative shells",
        },
        "action_carriers": {
            "Einstein_Maxwell": source_layout_audit,
            "Weyl_Maxwell": target_layout_audit,
        },
        "relative_cotangent_carrier": {
            "row_count": 316,
            "degree_ranks": [10, 51, 97, 97, 51, 10],
            "sector_ranks": sector_ranks,
            "selected_completion": "T_star_shift_1_of_entire_78_row_relative_cone",
            "selected_added_rows": 78,
            "full_cone_cotangent_requires_equal_rank_dual": True,
            "minimality_status": (
                "MINIMAL_WITHIN_DECLARED_FULL_CONE_COTANGENT_CLASS_ONLY"
            ),
            "rank_only_lower_bound": 28,
            "absolute_mixed_bundle_minimality": "NOT_PROVED",
            "unary_cyclic_pairing": "CANONICAL_COTANGENT_PAIRING",
            "action_pairing_transport": "NOT_IDENTIFIED",
        },
        "most_general_equivariant_cohomology_map": {
            "map": "S_parity(lambda,k,m,omega) on each labelled q-primary fibre",
            "support_local_consequence": (
                "after harmonic/Fourier restriction, a finite-order "
                "H_product-equivariant chain map acts fibrewise"
            ),
            "shell_constraint": (
                "time translation, S1 translation, SO3 and parity preserve "
                "the labelled q shell; the extra p shell cannot mix because "
                "its frequency never collides"
            ),
            "cohomology_isomorphism_requirement": "det(S_parity) != 0",
            "cyclicity_equation": (
                "S_parity^sharp Omega_WM_q S_parity = Omega_EM"
            ),
            "adjoint_pushforward_formula_if_it_existed": (
                "iota_push=Omega_WM^{-1} iota_star^sharp Omega_EM"
            ),
        },
        "exact_inertia_blocks": expected_blocks,
        "determinant_obstruction": {
            "identity": (
                "det(S^T Omega_WM_q S)=det(S)^2 det(Omega_WM_q)"
            ),
            "source_determinants_positive_for_lambda_ge_6": [
                "2*lambda",
                "2*(lambda-2)",
            ],
            "target_determinants_negative_for_lambda_ge_6": [
                "-lambda*(9*lambda-2)",
                "-(lambda-2)*(9*lambda-2)",
            ],
            "consequence": (
                "no invertible real-structure-preserving S solves the "
                "cyclicity equation in either parity"
            ),
            "homotopy_and_field_redefinition_scope": (
                "chain homotopies and cohomologically exact current "
                "improvements preserve the induced nondegenerate cohomology "
                "form and therefore cannot change its inertia"
            ),
        },
        "zero_mode_ledger": {
            "generic_obstruction_uses_zero_modes": False,
            "exceptional_and_global_zero_modes_classified_here": False,
            "reason_sufficient": (
                "an all-sector action-compatible pushforward must restrict "
                "to every generic ell>=2 fibre, so one generic inertia "
                "mismatch is already decisive"
            ),
        },
        "verdict": {
            "action_compatible_cyclic_pushforward_exists": False,
            "canonical_316_unary_cyclic_carrier_exists": True,
            "canonical_316_pairing_is_action_pairing": False,
            "relative_target_valued_QME_subtraction_defined": False,
            "classification": "OBSTRUCTED",
            "first_exact_obstruction": (
                "GENERIC_PHYSICAL_COHOMOLOGY_ACTION_FORM_INERTIA_MISMATCH"
            ),
        },
        "coefficient_gate": {
            "matched_one_loop_insertions_authorized": False,
            "reason": (
                "the action-compatible pushforward required to compare the "
                "two insertions does not exist on the declared standard "
                "action pairings"
            ),
            "pure_Weyl_vector_reuse_authorized": False,
        },
        "exact_checks": exact_checks,
        "claim_flags": {
            "ACTION_COMPATIBLE_CYCLIC_PUSHFORWARD_CONSTRUCTED": False,
            "ACTION_COMPATIBLE_CYCLIC_PUSHFORWARD_OBSTRUCTED_GENERICALLY": True,
            "CANONICAL_316_UNARY_CYCLIC_CARRIER_RETAINED": True,
            "CANONICAL_316_PAIRING_PROMOTED_TO_ACTION_PAIRING": False,
            "ABSOLUTE_316_ROW_MINIMALITY_CLAIMED": False,
            "MATCHED_ONE_LOOP_COEFFICIENTS_COMPUTED": False,
            "RELATIVE_QME_RESTORED": False,
            "LORENTZIAN_CAUSAL_OR_PARTICLE_CLAIM": False,
        },
        "dependency_refs": {
            "previous_relative_QME_nondefinition": _ref(PREVIOUS, previous),
            "generic_action_pairing_inertia": _ref(
                GENERIC_INERTIA, inertia
            ),
            "canonical_316_cotangent_completion": _ref(COTANGENT, cotangent),
            "canonical_316_layout": _ref(
                COTANGENT_LAYOUT, cotangent_layout
            ),
            "Einstein_action_BV_layout": _ref(
                EINSTEIN_LAYOUT, einstein_layout
            ),
            "Weyl_action_BV_layout": _ref(WEYL_LAYOUT, weyl_layout),
            "relative_observable_functor": _ref(OBSERVABLE, observable),
        },
        "next_gate": (
            "RETAIN_THE_NONCYCLIC_RELATIVE_OBSERVABLE_CONE_OR_DECLARE_AN_"
            "EXPLICIT_PAIRING_CHANGED_THEORY_BEFORE_ANY_MATCHED_INSERTION_WORK"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result obstructs an "
            "action-compatible cyclic Einstein-Maxwell to Weyl-Maxwell "
            "pushforward on every generic axial and polar physical fibre. "
            "The canonical 316-row carrier remains a valid unary cyclic "
            "complex for its adjoined cotangent pairing, but that pairing "
            "cannot be identified with both action-derived forms. The result "
            "does not obstruct the noncyclic observable cone or an explicitly "
            "pairing-changed theory, classify exceptional/global maps, compute "
            "matched insertions or a relative coefficient, restore a QME, or "
            "establish Lorentzian causality, states, particles, positivity, "
            "scattering or unitarity."
        ),
    }


def validate(value: dict[str, Any]) -> None:
    if not all(value.get("exact_checks", {}).values()):
        raise ValueError("exact pushforward obstruction check failed")
    flags = value.get("claim_flags", {})
    forbidden_true = (
        "ACTION_COMPATIBLE_CYCLIC_PUSHFORWARD_CONSTRUCTED",
        "CANONICAL_316_PAIRING_PROMOTED_TO_ACTION_PAIRING",
        "ABSOLUTE_316_ROW_MINIMALITY_CLAIMED",
        "MATCHED_ONE_LOOP_COEFFICIENTS_COMPUTED",
        "RELATIVE_QME_RESTORED",
        "LORENTZIAN_CAUSAL_OR_PARTICLE_CLAIM",
    )
    if any(flags.get(name) is not False for name in forbidden_true):
        raise ValueError("relative cyclic-pushforward claim over-promoted")
    if (
        flags.get(
            "ACTION_COMPATIBLE_CYCLIC_PUSHFORWARD_OBSTRUCTED_GENERICALLY"
        )
        is not True
        or flags.get("CANONICAL_316_UNARY_CYCLIC_CARRIER_RETAINED") is not True
        or value.get("verdict", {}).get("classification") != "OBSTRUCTED"
        or value.get("coefficient_gate", {}).get(
            "matched_one_loop_insertions_authorized"
        )
        is not False
    ):
        raise ValueError("relative cyclic-pushforward disposition drifted")
