#!/usr/bin/env python3
"""Independent verifier for the selected changed-action no-lift gate.

This module deliberately does not import the producer.  It reloads all six
pinned artifacts, reconstructs the exact rational ranks and two polynomial
cokernel functionals, and attacks the fail-closed lifecycle with mutations.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from local_bv.schema_validation import validate_instance


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERTIFICATE = HERE / "certificates/RELATIVE_OFFSHELL_CHANGED_ACTION_BV_LIFT_OBSTRUCTION_V1.json"
SCHEMA = HERE / "schema/relative-offshell-changed-action-bv-lift-obstruction-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def _poly(value: object, lam: sp.Symbol) -> sp.Poly:
    expr = sp.sympify(str(value).replace("lambda", "lam"), locals={"lam": lam})
    return sp.Poly(sp.expand(expr), lam)


def _semantic_check(certificate: dict[str, Any]) -> None:
    selected = certificate["selected_repair_orbit"]
    if (
        selected["selection"] != "QUADRATIC_ACTION_DEFORMATION_ONLY"
        or selected["pairing_deformation_mixed_in"] is not False
        or selected["physical_auxiliary_extension_mixed_in"] is not False
        or selected["axial_and_polar_treated_together"] is not True
    ):
        raise ValueError("repair-orbit isolation failed")
    obstruction = certificate["exact_obstruction"]
    if (
        obstruction["first_invariant_obstruction"]
        != "AXIAL_22_LAMBDA_COEFFICIENT"
        or obstruction["unrestricted_q_primary_preimage_exists"] is not False
        or obstruction["same_background_preimage_exists"] is not False
        or obstruction["p_shell_separation_preserving_preimage_exists"] is not False
    ):
        raise ValueError("action no-lift was over-promoted")
    disposition = certificate["noether_and_bv_disposition"]
    if disposition["requested_changed_local_action"] != "OBSTRUCTED":
        raise ValueError("changed action disposition drifted")
    for key in (
        "requested_changed_master_action",
        "requested_changed_BV_differential",
        "requested_changed_odd_pairing",
        "requested_changed_nonminimal_sector",
        "requested_changed_gauge_fixed_operator",
        "requested_full_40_to_38_cyclic_chain_lift",
        "common_density_measure_domain_regulator",
    ):
        if disposition[key] != "NOT_ACTIVATED":
            raise ValueError(f"downstream BV gate over-promoted: {key}")
    q = certificate["relative_quantum_disposition"]
    if (
        q["relative_anomaly_coefficients"] != "NOT_COMPUTED"
        or q["relative_one_loop_QME"] != "UNDEFINED"
        or q["strict_pure_Weyl_coefficients_imported_as_relative"] is not False
    ):
        raise ValueError("relative QME or coefficient over-promoted")
    flags = certificate["claim_flags"]
    if (
        flags["REQUESTED_REDUCED_REPAIR_HAS_LOCAL_ACTION_PREIMAGE"] is not False
        or flags["FULL_OFFSHELL_CHANGED_BV_LIFT_CONSTRUCTED"] is not False
        or flags["RELATIVE_ANOMALY_COEFFICIENT_COMPUTED"] is not False
        or flags["RELATIVE_QME_DEFINED"] is not False
        or flags["LORENTZIAN_CAUSAL_CLAIM"] is not False
    ):
        raise ValueError("claim boundary over-promoted")


def verify() -> dict[str, Any]:
    certificate = _load(CERTIFICATE)
    schema = _load(SCHEMA)
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    _semantic_check(certificate)

    for ref in certificate["input_pins"].values():
        path = ROOT / ref["path"]
        if not path.is_file() or _sha(path) != ref["sha256"]:
            raise ValueError(f"input pin mismatch: {ref['path']}")

    pairing_ref = certificate["input_pins"]["terminal_pairing_deformation_classification"]
    qme_ref = certificate["input_pins"]["terminal_changed_theory_qme_nondefinition"]
    action_ref = certificate["input_pins"]["complete_action_response"]
    receipt_ref = certificate["input_pins"]["complete_action_response_receipt"]
    pairing = _load(ROOT / pairing_ref["path"])
    qme = _load(ROOT / qme_ref["path"])
    action = _load(ROOT / action_ref["path"])
    receipt = _load(ROOT / receipt_ref["path"])

    labels = {
        row["dual_minimal_source_action_repair"]["theory_label"]
        for row in pairing["sector_classification"]
    }
    if labels != {"ACTION_CHANGED_EINSTEIN_Q_PRIMARY_REDUCED_THEORY"}:
        raise ValueError("selected reduced action orbit drifted upstream")
    if qme["claim_flags"]["RELATIVE_ONE_LOOP_QME_DEFINED_ON_ANY_REPAIR_ORBIT"] is not False:
        raise ValueError("terminal relative-QME nondefinition drifted")
    if receipt["independent_rail"]["status"] != "PASS" or receipt["independent_rail"]["producer_payload_imported"] is not False:
        raise ValueError("upstream action-variation independent rail drifted")

    basis = action["basis_reduction"]
    relations = sp.Matrix(
        [[sp.Rational(value) for value in row] for row in basis["relation_matrix"]]
    )
    if relations.shape != (7, 10) or relations.rank() != 7:
        raise ValueError("complete action quotient replay failed")
    if basis["complete_action_basis"] != ["1", "R", "F2", "RiemFF", "F2sq", "P2"]:
        raise ValueError("complete action basis drifted")

    lam = sp.symbols("lambda", real=True)
    response = action["q_primary_response"]
    target = action["exact_cokernel"]["requested_source_action_shift"]
    values = {
        "axial_image": _poly(response["general_axial"][1][1], lam).coeff_monomial(lam),
        "axial_target": _poly(target["axial"][1][1], lam).coeff_monomial(lam),
        "polar_image": _poly(response["general_polar"][1][1], lam).coeff_monomial(lam**2),
        "polar_target": _poly(target["polar"][1][1], lam).coeff_monomial(lam**2),
    }
    if values != {
        "axial_image": 0,
        "axial_target": -9,
        "polar_image": 0,
        "polar_target": sp.Rational(-9, 4),
    }:
        raise ValueError("cokernel functional replay failed")

    cross = sp.Matrix(
        [
            [sp.Rational(value) for value in row]
            for row in action["p_shell_cross_response"]["zero_cross_constraint_matrix"]
        ]
    )
    if cross.shape != (17, 6) or cross.rank() != 6 or len(cross.nullspace()) != 0:
        raise ValueError("p-shell full-column-rank replay failed")

    mutations = [
        ("selected_repair_orbit", "selection", "PAIRING_DEFORMATION_ONLY"),
        ("selected_repair_orbit", "pairing_deformation_mixed_in", True),
        ("exact_obstruction", "unrestricted_q_primary_preimage_exists", True),
        ("noether_and_bv_disposition", "requested_changed_master_action", "CONSTRUCTED"),
        ("relative_quantum_disposition", "relative_anomaly_coefficients", "COEFFICIENT_COMPUTED"),
        ("claim_flags", "RELATIVE_QME_DEFINED", True),
        ("claim_flags", "LORENTZIAN_CAUSAL_CLAIM", True),
    ]
    for section, key, value in mutations:
        mutant = deepcopy(certificate)
        mutant[section][key] = value
        try:
            _semantic_check(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"overclaim mutation escaped: {section}.{key}")

    action_mutant = deepcopy(action)
    action_mutant["exact_cokernel"]["requested_source_action_shift"]["axial"][1][1] = "0"
    if _poly(action_mutant["exact_cokernel"]["requested_source_action_shift"]["axial"][1][1], lam).coeff_monomial(lam) == -9:
        raise ValueError("rank-one wall mutation was not effective")

    return certificate


def main() -> int:
    verify()
    print("RELATIVE OFFSHELL CHANGED-ACTION BV-LIFT independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
