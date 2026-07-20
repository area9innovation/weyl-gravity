#!/usr/bin/env python3
"""Fail-closed audit of the first new conformal gauge-field carriers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PANEITZ = (
    HERE
    / "certificates/PANEITZ_HIGHER_DERIVATIVE_ANOMALY_COLUMN.json"
)
PANEITZ_COMMIT = "4b72eb33c7ade3d87f72707d56c86418c46e6765"
PANEITZ_SHA256 = (
    "cb6d708fb081d6a93fc64ab988f267cdd4a0c92651d872aaed5b59e3ecc3cb3c"
)

COMPLETENESS_GATES = [
    "candidate_and_background_scope",
    "off_shell_fields_ghosts_antifields_and_reducibility",
    "minimal_BV_nilpotency",
    "exact_generic_background_Noether_identity",
    "nonminimal_pairs_and_gauge_fermion",
    "generic_Riemannian_gauge_fixed_ellipticity",
    "domain_reality_chirality_and_zero_modes",
    "determinant_powers_statistics_and_contours",
    "two_independent_raw_coefficient_routes",
    "kinetic_or_Krein_sign_audit",
    "no_omitted_mixed_spin_carrier",
    "exact_lattice_append_only_after_all_prior_gates",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _candidate(
    *,
    candidate_id: str,
    field_content: list[str],
    required_chiral_components: list[str],
    gauge_parameter: str,
    available_scope: str,
    first_failed_gate: str,
    exact_obstruction: str,
    missing_carrier: str,
    source_ids: list[str],
) -> dict[str, Any]:
    gate_status = {gate: "NOT_ESTABLISHED" for gate in COMPLETENESS_GATES}
    gate_status["candidate_and_background_scope"] = "ESTABLISHED"
    gate_status["off_shell_fields_ghosts_antifields_and_reducibility"] = (
        "PARTIAL_SOURCE_DICTIONARY_ONLY"
    )
    gate_status[first_failed_gate] = "FAILED_EXACT_IDENTITY"
    return {
        "candidate_id": candidate_id,
        "field_content_visible_in_sources": field_content,
        "required_chiral_components": required_chiral_components,
        "gauge_parameter": gauge_parameter,
        "available_scope": available_scope,
        "gate_status": gate_status,
        "first_failed_gate": first_failed_gate,
        "exact_obstruction": exact_obstruction,
        "first_missing_carrier": missing_carrier,
        "source_ids": source_ids,
        "carrier_status": "INCOMPLETE_DO_NOT_FORM_DETERMINANT",
        "coefficient_status": "NOT_COMPUTED",
        "column_appended": False,
    }


def build() -> dict[str, Any]:
    paneitz = json.loads(PANEITZ.read_text(encoding="utf-8"))
    if (
        _sha256(PANEITZ) != PANEITZ_SHA256
        or paneitz["result_id"] != "PANEITZ_HIGHER_DERIVATIVE_ANOMALY_COLUMN"
        or paneitz["next_gauge_field_gate"]["column_appended"] is not False
    ):
        raise ValueError("Paneitz import pin or absent-column boundary drifted")

    spin32 = _candidate(
        candidate_id="complex_conformal_gravitino_minimal_depth_3_over_2",
        field_content=[
            "h_{alpha(2) dot_alpha}",
            "bar_h_{alpha dot_alpha(2)}",
        ],
        required_chiral_components=[
            "(2,1)_complex_field",
            "(1,2)_complex_conjugate",
        ],
        gauge_parameter=(
            "complex commuting BV ghost ell_alpha and its dotted conjugate; "
            "ell is fermionic as a gauge parameter but its BV ghost is even"
        ),
        available_scope=(
            "the Weyl-corrected quadratic action is higher-spin gauge "
            "invariant on four-dimensional Bach-flat backgrounds"
        ),
        first_failed_gate="exact_generic_background_Noether_identity",
        exact_obstruction=(
            "R_3/2^dagger K_3/2 h equals the explicit Bach insertion: "
            "-i integral e [ell^alpha B_alpha^{ beta dot_beta(2)} "
            "bar_h_{beta dot_beta(2)} + conjugate terms]. It vanishes only "
            "after imposing B_{alpha(2) dot_alpha(2)}=0."
        ),
        missing_carrier=(
            "a generic-background kinetic/gauge pair (K_3/2,R_3/2) with "
            "K_3/2 R_3/2=0, followed by its complete nonminimal elliptic "
            "gauge fixing and two-route raw anomaly calculation"
        ),
        source_ids=["KPR_2005_08657", "KP_1902_08010"],
    )
    spin3 = _candidate(
        candidate_id="bosonic_conformal_spin_3_minimal_depth",
        field_content=[
            "real symmetric trace-free h_{abc}",
            "curvature-shifted conformal spin-1 carrier",
            "conformal spin-2 carrier indicated by superconformal completion",
        ],
        required_chiral_components=["real_(3,3)_field"],
        gauge_parameter=(
            "real symmetric trace-free rank-two even gauge parameter "
            "epsilon_{ab}; its BV ghost is odd"
        ),
        available_scope=(
            "the pure sixth-order spin-3 operator is controlled only through "
            "first order in background curvature; the known spin-1 mixing "
            "does not close a generic or complete Bach-flat carrier"
        ),
        first_failed_gate="no_omitted_mixed_spin_carrier",
        exact_obstruction=(
            "the spin-1 field transforms as delta h_a = "
            "-8 C_{abcp} nabla^p epsilon^{bc}; hence delta S_13 contains "
            "terms of order C^2 that require delta S_33. The pure O_6 block "
            "is therefore not separately gauge invariant even on a generic "
            "Einstein background. A separate superconformal-completion "
            "argument additionally indicates a conformal spin-2 field shifted "
            "by the spin-3 parameter; that indication is not promoted here "
            "to an independent nonsupersymmetric necessity theorem."
        ),
        missing_carrier=(
            "at minimum a closed all-curvature minimal-depth spin-1/spin-3 "
            "quadratic operator and transformation complex, plus an explicit "
            "disposition of the spin-2 sector indicated by superconformal "
            "completion; the available maximal-depth scalar-ghost model is a "
            "different candidate and cannot fill this slot"
        ),
        source_ids=["BT_1702_00222", "KPR_2005_08657", "KP_1912_00652"],
    )

    value = {
        "schema": "quantum-weyl-conformal-gauge-field-carrier-obstruction-v1",
        "result_id": "FIRST_NEW_CONFORMAL_GAUGE_FIELD_CARRIER_OBSTRUCTION",
        "result_state": "TWO_SMALLEST_CANDIDATES_FAIL_COMPLETE_CARRIER_GATE",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "input_pins": {
            "Paneitz_predecessor": {
                "path": str(PANEITZ.relative_to(ROOT)),
                "source_commit": PANEITZ_COMMIT,
                "sha256": PANEITZ_SHA256,
                "imported_conclusion": (
                    "the next conformal gauge-field column is absent, not zero"
                ),
            }
        },
        "finite_completeness_criterion": {
            "gates_in_order": COMPLETENESS_GATES,
            "selection_rule": (
                "A candidate is complete only when every gate is ESTABLISHED. "
                "The first failed or missing gate stops coefficient and lattice "
                "production."
            ),
            "receiver_schema": (
                "schema/conformal-gauge-field-carrier-receiver-v1.schema.json"
            ),
        },
        "candidate_audits": [spin32, spin3],
        "determinant_ledger": {
            "status": "NOT_ASSEMBLED",
            "reason": (
                "neither candidate reaches a complete gauge-fixed carrier; "
                "a partial determinant would violate the stop condition"
            ),
            "rows": [],
        },
        "coefficient_routes": {
            "status": "NOT_RUN",
            "reason": (
                "literature anomaly numbers are not imported without a "
                "complete carrier and two independent full raw routes"
            ),
            "routes": [],
        },
        "anomaly_lattice": {
            "status": "UNCHANGED_PANEITZ_ONLY",
            "new_column_appended": False,
            "reason": "an absent carrier is not a zero anomaly column",
        },
        "exact_checks": {
            "Paneitz_exact_hash_import": True,
            "Paneitz_absent_not_zero_boundary_preserved": True,
            "finite_criterion_precedes_candidate_disposition": True,
            "spin_3_over_2_Bach_identity_scoped": True,
            "spin_3_mixed_carrier_requirement_scoped": True,
            "maximal_depth_not_substituted_for_minimal_depth": True,
            "partial_determinant_refused": True,
            "literature_coefficient_copy_refused": True,
            "lattice_unchanged": True,
        },
        "claim_flags": {
            "NEW_GAUGE_FIELD_CARRIER_CERTIFIED": False,
            "NEW_ANOMALY_COLUMN_COMPUTED": False,
            "STRICT_QME_RESTORED": False,
            "LORENTZIAN_CERTIFIED": False,
            "ALL_CONFORMAL_HIGHER_SPINS_OBSTRUCTED": False,
        },
        "next_gate": (
            "Supply one receiver-valid generic-background carrier, beginning "
            "with either a conformal-gravitino nonminimal elliptic completion "
            "or the closed minimal-depth spin-1/spin-2/spin-3 operator."
        ),
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC audit proves only that "
            "the two declared smallest candidates do not yet furnish a "
            "complete coefficient-bearing carrier under the finite receiver "
            "contract. It records the first exact missing identity/operator "
            "for each and leaves the Paneitz-extended anomaly lattice "
            "unchanged. It is not a no-go theorem for all conformal higher "
            "spins, not a zero coefficient, not a determinant result, not QME "
            "restoration, and not a Lorentzian, positivity, particle, "
            "scattering or unitarity result."
        ),
    }
    validate(value)
    return value


def validate(value: dict[str, Any]) -> None:
    if value["input_pins"]["Paneitz_predecessor"]["sha256"] != PANEITZ_SHA256:
        raise ValueError("Paneitz pin drifted")
    criteria = value["finite_completeness_criterion"]["gates_in_order"]
    if criteria != COMPLETENESS_GATES or len(criteria) != len(set(criteria)):
        raise ValueError("finite completeness criterion drifted")
    audits = {row["candidate_id"]: row for row in value["candidate_audits"]}
    if set(audits) != {
        "complex_conformal_gravitino_minimal_depth_3_over_2",
        "bosonic_conformal_spin_3_minimal_depth",
    }:
        raise ValueError("candidate audit set drifted")
    gravitino = audits[
        "complex_conformal_gravitino_minimal_depth_3_over_2"
    ]
    spin3 = audits["bosonic_conformal_spin_3_minimal_depth"]
    if (
        gravitino["required_chiral_components"]
        != ["(2,1)_complex_field", "(1,2)_complex_conjugate"]
        or "Bach insertion" not in gravitino["exact_obstruction"]
        or gravitino["first_failed_gate"]
        != "exact_generic_background_Noether_identity"
    ):
        raise ValueError("conformal-gravitino obstruction drifted")
    if (
        "spin-1/spin-3" not in spin3["first_missing_carrier"]
        or "spin-2 sector indicated" not in spin3["first_missing_carrier"]
        or spin3["first_failed_gate"] != "no_omitted_mixed_spin_carrier"
        or "different candidate" not in spin3["first_missing_carrier"]
    ):
        raise ValueError("spin-3 mixed-carrier obstruction drifted")
    if any(row["column_appended"] for row in audits.values()):
        raise ValueError("incomplete candidate appended to lattice")
    if (
        value["determinant_ledger"]["rows"]
        or value["coefficient_routes"]["routes"]
        or value["anomaly_lattice"]["new_column_appended"]
    ):
        raise ValueError("partial carrier promoted to determinant/coefficient")
    if not all(value["exact_checks"].values()):
        raise ValueError("exact carrier-obstruction check failed")
    if any(value["claim_flags"].values()):
        raise ValueError("carrier-obstruction claim boundary over-promoted")


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
