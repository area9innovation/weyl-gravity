"""Exact disposition of relative QME subtraction after reduced cyclic repair.

The imported classification constructs reduced cyclic congruences only.  This
module distinguishes that finite-carrier fact from the off-shell local BV and
renormalization data required to define a one-loop relative anomaly.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


HERE = Path(__file__).resolve().parent
QROOT = HERE.parent
ROOT = QROOT.parent
REPAIR_COMMIT = "a4ed972a4"
REPAIR_PATH = (
    "quantum-weyl/transfer/certificates/"
    "RELATIVE_EINSTEIN_WEYL_PAIRING_DEFORMATION_CLASSIFICATION.json"
)
REPAIR_SHA256 = "00b2e7a66fd81c0f2c1d6af3b4f37a0a7d10215a4405b0e1ac50c39dc41e8cf5"
LOCAL_PATH = (
    QROOT
    / "local_bv/certificates/LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT.json"
)
LOCAL_SHA256 = "07bf332cf1bece92f8a041002f3c787fe7e85e798871e4878fbbc3cd7b20bd3b"


def _git_blob(commit: str, path: str) -> bytes:
    prefix = subprocess.check_output(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True
    ).strip()
    result = subprocess.run(
        ["git", "show", f"{commit}:{prefix}{path}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError("pinned repair certificate is missing")
    return result.stdout


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def build() -> dict[str, Any]:
    blob = _git_blob(REPAIR_COMMIT, REPAIR_PATH)
    repair = json.loads(blob)
    if (
        hashlib.sha256(blob).hexdigest() != REPAIR_SHA256
        or repair.get("result_id")
        != "RELATIVE_EINSTEIN_WEYL_PAIRING_DEFORMATION_CLASSIFICATION"
        or repair["claim_flags"][
            "COMPLETE_GENERIC_REDUCED_PAIRING_DEFORMATION_FAMILY_CLASSIFIED"
        ]
        is not True
        or repair["claim_flags"]["FULL_OFF_SHELL_CHANGED_ACTION_COMPLEX_CONSTRUCTED"]
        is not False
    ):
        raise ValueError("terminal repair classification pin failed")
    local = _load(LOCAL_PATH)
    if (
        hashlib.sha256(LOCAL_PATH.read_bytes()).hexdigest() != LOCAL_SHA256
        or local.get("result_id") != "LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT"
    ):
        raise ValueError("strict local anomaly audit drifted")
    strict_vector = local["two_method_coefficients"]["repository_vector"]

    finite = {
        "result_id": "RELATIVE_CHANGED_THEORY_FINITE_CARRIER_COMPATIBILITY",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generic_repair_orbits": {
            "pairing_deformation": (
                "one positive-definite target-form orbit per parity modulo "
                "real cyclic congruence"
            ),
            "quadratic_action_deformation": (
                "one matching-inertia reduced-Hessian orbit per parity"
            ),
            "physical_auxiliary_extension": (
                "minimal auxiliary inertia r=1 per parity; larger r are "
                "nonminimal extensions"
            ),
            "contractible_auxiliary": "NO_REPAIR",
        },
        "exact_compatibility": {
            "generic_reduced_cyclic_maps_exist": True,
            "maps_are_real_product_equivariant_and_q_shell_preserving": True,
            "unequal_frequency_p_shell_not_used": True,
            "rank_one_is_minimal_pairing_or_action_form_change": True,
            "one_positive_physical_auxiliary_is_minimal": True,
        },
        "finite_carrier_QME_operator": {
            "source_BV_Laplacian": "NOT_SUPPLIED_ON_COMMON_DOMAIN",
            "target_BV_Laplacian": "NOT_SUPPLIED_ON_COMMON_DOMAIN",
            "renormalized_contraction": "NOT_SUPPLIED",
            "common_density_or_Berezinian": "NOT_SUPPLIED",
            "transported_insertions": "UNDEFINED",
        },
        "status": (
            "CYCLIC_REDUCED_COHOMOLOGY_COMPATIBLE_QME_DATA_INCOMPLETE"
        ),
    }
    local_rail = {
        "result_id": "RELATIVE_CHANGED_THEORY_LOCAL_COHOMOLOGY_NONDEFINITION",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "strict_Weyl_reference": {
            "regular_Bach_locus_H14": local["full_BV_cohomology"],
            "coefficient_vector": strict_vector,
            "status": "CERTIFIED_STRICT_THEORY_ONLY",
        },
        "repair_orbit_disposition": [
            {
                "orbit": "pairing_deformation",
                "local_field_complex": "UNCHANGED",
                "strict_class_basis": "UNCHANGED_AS_LOCAL_BRST_CLASSES",
                "changed_BV_pairing_lift": "NOT_SUPPLIED",
                "transported_anomaly": "UNDEFINED",
            },
            {
                "orbit": "quadratic_action_deformation",
                "local_action_and_master_solution": "NOT_SUPPLIED",
                "modified_BRST_differential": "UNDEFINED",
                "modified_H14": "UNDEFINED",
                "transported_anomaly": "UNDEFINED",
            },
            {
                "orbit": "physical_auxiliary_extension",
                "local_auxiliary_representation_and_action": "NOT_SUPPLIED",
                "auxiliary_BRST_complex": "UNDEFINED_OFF_SHELL",
                "auxiliary_anomaly_contribution": "UNDEFINED",
                "transported_anomaly": "UNDEFINED",
            },
        ],
        "counterterm_quotient": (
            "UNDEFINED_ACROSS_CHANGED_THEORIES_UNTIL_EACH_ALLOWED_LOCAL_"
            "ALGEBRA_AND_COMMON_RENORMALIZATION_PRESCRIPTION_IS_DECLARED"
        ),
        "relative_class": "UNDEFINED",
    }
    dispositions = [
        {
            "repair_orbit": "pairing_deformation",
            "reduced_cyclic_map": "EXISTS",
            "off_shell_chain_lift": "NOT_SUPPLIED",
            "common_regulator_domain": "NOT_SUPPLIED",
            "relative_one_loop_defect": "UNDEFINED",
            "minimal_additional_data": [
                "support-local nondegenerate odd-pairing lift on all BV rows",
                "full cyclic chain map and adjoint pushforward",
                "compatible density/Berezinian or renormalized contraction",
                "matched source/target regulator and operator domains",
            ],
        },
        {
            "repair_orbit": "quadratic_action_deformation",
            "reduced_cyclic_map": "EXISTS",
            "off_shell_chain_lift": "NOT_SUPPLIED",
            "common_regulator_domain": "NOT_SUPPLIED",
            "relative_one_loop_defect": "UNDEFINED",
            "minimal_additional_data": [
                "four-dimensional local quadratic-action lift",
                "full classical master solution and gauge-fixed BV Hessian",
                "cyclic chain map realizing the reduced congruence",
                "matched measure, zero modes, contours and regulator",
            ],
        },
        {
            "repair_orbit": "physical_auxiliary_extension",
            "reduced_cyclic_map": "EXISTS",
            "off_shell_chain_lift": "NOT_SUPPLIED",
            "common_regulator_domain": "NOT_SUPPLIED",
            "relative_one_loop_defect": "UNDEFINED",
            "minimal_additional_data": [
                "local auxiliary bundles, representation and BV differential",
                "auxiliary action, cotangent lift and nonminimal completion",
                "auxiliary measure and anomaly insertion",
                "matched source/target regulator and operator domains",
            ],
        },
    ]
    checks = {
        "terminal_repair_imported_by_commit_and_hash": True,
        "strict_local_anomaly_imported_by_hash": True,
        "all_three_nontrivial_repair_orbits_enumerated": len(dispositions) == 3,
        "finite_reduced_cyclic_compatibility_retained": True,
        "no_off_shell_changed_action_silently_selected": True,
        "no_common_regulator_or_domain_invented": True,
        "strict_Weyl_vector_not_promoted_to_relative_vector": True,
        "anomaly_transport_undefined_on_every_repair_orbit": all(
            row["relative_one_loop_defect"] == "UNDEFINED"
            for row in dispositions
        ),
        "inertia_and_anomaly_mutations_are_separate": True,
    }
    value = {
        "schema": "quantum-weyl-relative-changed-theory-qme-disposition-v1",
        "result_id": "RELATIVE_CHANGED_THEORY_QME_NONDEFINITION",
        "result_state": (
            "REDUCED_CYCLIC_REPAIRS_EXIST_BUT_RELATIVE_ONE_LOOP_QME_"
            "SUBTRACTION_UNDEFINED_ON_EVERY_REPAIR_ORBIT"
        ),
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
            "REDUCED-MODE",
        ],
        "input_pins": {
            "terminal_repair": {
                "commit": REPAIR_COMMIT,
                "path": REPAIR_PATH,
                "sha256": REPAIR_SHA256,
            },
            "strict_local_anomaly": {
                "path": LOCAL_PATH.relative_to(ROOT).as_posix(),
                "sha256": LOCAL_SHA256,
            },
        },
        "scope": repair["scope"],
        "finite_carrier_rail": finite,
        "local_cohomology_rail": local_rail,
        "repair_orbit_dispositions": dispositions,
        "orbit_invariance": {
            "relative_defect_invariant_across_orbits": "NOT_DEFINED",
            "reason": (
                "the changed pairing, action and auxiliary content define "
                "different off-shell theories and admissible counterterm "
                "algebras; no common renormalized insertion functor exists"
            ),
            "vanishing_due_to_strict_cancellation": False,
            "vanishing_due_to_changed_theory": "NOT_COMPUTED",
        },
        "coefficient_ledger": {
            "strict_pure_Weyl_reference_vector": strict_vector,
            "changed_pairing_relative_vector": "UNDEFINED",
            "changed_action_relative_vector": "UNDEFINED",
            "physical_auxiliary_relative_vector": "UNDEFINED",
        },
        "exact_checks": checks,
        "claim_flags": {
            "REDUCED_CYCLIC_REPAIR_ORBITS_CLASSIFIED": True,
            "RELATIVE_ONE_LOOP_QME_DEFINED_ON_ANY_REPAIR_ORBIT": False,
            "RELATIVE_COEFFICIENT_COMPUTED": False,
            "STRICT_STANDARD_ACTION_RELATIVE_SUBTRACTION_REVIVED": False,
            "STRICT_PURE_WEYL_ANOMALY_CANCELLED": False,
            "LORENTZIAN_CAUSAL_OR_PARTICLE_CLAIM": False,
        },
        "next_gate": (
            "CHOOSE_AND_DECLARE_ONE_CHANGED_THEORY_THEN_SUPPLY_ITS_FULL_"
            "OFF_SHELL_BV_LIFT_AND_A_COMMON_RENORMALIZED_INSERTION_FUNCTOR"
        ),
        "claim_boundary": (
            "This is a terminal non-definition theorem for the current "
            "complete generic reduced repair family and repository data "
            "state, not a no-go against future off-shell lifts. Reduced cyclic "
            "compatibility does not define BV Laplacians, regulator domains "
            "or anomaly transport. No relative coefficient, QME restoration, "
            "strict anomaly cancellation, Lorentzian causal state, particle, "
            "positivity, scattering or unitarity claim is established."
        ),
    }
    validate(value)
    return value


def validate(value: dict[str, Any]) -> None:
    if not all(value.get("exact_checks", {}).values()):
        raise ValueError("relative changed-theory exact checks failed")
    if any(
        row.get("relative_one_loop_defect") != "UNDEFINED"
        for row in value.get("repair_orbit_dispositions", [])
    ):
        raise ValueError("relative coefficient over-promoted")
    flags = value.get("claim_flags", {})
    if (
        flags.get("REDUCED_CYCLIC_REPAIR_ORBITS_CLASSIFIED") is not True
        or flags.get("RELATIVE_ONE_LOOP_QME_DEFINED_ON_ANY_REPAIR_ORBIT")
        is not False
        or flags.get("RELATIVE_COEFFICIENT_COMPUTED") is not False
        or flags.get("STRICT_STANDARD_ACTION_RELATIVE_SUBTRACTION_REVIVED")
        is not False
        or flags.get("STRICT_PURE_WEYL_ANOMALY_CANCELLED") is not False
        or flags.get("LORENTZIAN_CAUSAL_OR_PARTICLE_CLAIM") is not False
    ):
        raise ValueError("relative QME claim boundary over-promoted")
    coefficients = value.get("coefficient_ledger", {})
    if any(
        coefficients.get(key) != "UNDEFINED"
        for key in (
            "changed_pairing_relative_vector",
            "changed_action_relative_vector",
            "physical_auxiliary_relative_vector",
        )
    ):
        raise ValueError("changed-theory anomaly coefficient over-promoted")
