#!/usr/bin/env python3
"""Independent replay of the Berger one-loop K-Cartan nondefinition."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPO = ROOT.parents[1]
OUTPUT = HERE / "certificates/BERGER_K_ONE_LOOP_INSERTION_NONDEFINITION_V1.json"
SCHEMA = HERE / "schema/berger-k-one-loop-insertion-nondefinition-v1.schema.json"
ATLAS = ROOT / "residual_atlas/positive-berger-k-one-loop-insertion-nondefinition-fragment-v1.json"
ATLAS_SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _historical(pin: dict[str, str]) -> dict[str, Any]:
    data = subprocess.run(
        [
            "git",
            "show",
            f"{pin['source_commit']}:physics/symplectic-reconstruction/{pin['path']}",
        ],
        cwd=REPO,
        check=True,
        capture_output=True,
    ).stdout
    if hashlib.sha256(data).hexdigest() != pin["sha256"]:
        raise ValueError(f"independent dependency drift: {pin['path']}")
    return json.loads(data)


def verify_payload(value: dict[str, Any]) -> None:
    Draft202012Validator(_load(SCHEMA)).validate(value)
    dependencies = {
        name: _historical(pin) for name, pin in value["input_pins"].items()
    }

    breaking = dependencies["one_loop_breaking_disposition"]
    if (
        breaking["result_id"]
        != "BERGER_COMPLEX_CLOCK_ONE_LOOP_BREAKING_NONDEFINITION_V1"
        or breaking["result_state"]
        != "NONDEFINED_MISSING_ACTION_DERIVED_EUCLIDEAN_BV_INTEGRATION_SLICE"
        or breaking["quotient_disposition"]["actual_breaking"] != "NONDEFINED"
        or breaking["quotient_disposition"]["actual_counterterm"]
        != "NONDEFINED_COEFFICIENTS"
        or any(
            row["prequotient_coefficient"] != "NONDEFINED"
            or row["counterterm_coefficient"] != "NONDEFINED"
            for row in breaking["coefficient_ledger"]
        )
    ):
        raise ValueError("independent one-loop predecessor replay failed")

    signoff = dependencies["classical_k_cartan_signoff"]
    generator = dependencies["generator_conjugation_audit"]
    cyclic = dependencies["classical_gauge_fixed_cyclic_complex"]
    if (
        signoff["review_status"] != "SIGNED_SCOPED_K_THEOREM"
        or signoff["review_scope"]["gauge_fixed_rows"] != 54
        or signoff["review_scope"]["certified_generator"]
        != "K_Berger=D-omega R"
        or not signoff["flags"]["K_BERGER_CARTAN_THROUGH_ARITY_THREE"]
        or signoff["flags"]["RAW_D_CARTAN_CERTIFIED"]
    ):
        raise ValueError("independent classical K signoff replay failed")
    if (
        generator["exact_conjugation"]["K_zero_arity"] != ["0", "0"]
        or generator["exact_conjugation"]["raw_D_zero_arity"]
        != ["0", "omega*rho"]
        or generator["exact_conjugation"]["rotation_generator"]
        != [[0, -1], [1, 0]]
        or not generator["flags"]["EXPORTED_UNARY_GENERATOR_IS_K"]
        or generator["flags"]["EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D"]
    ):
        raise ValueError("independent K/raw-D replay failed")
    if (
        cyclic["result_id"] != "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION"
        or cyclic["row_layout"]["total_rows"] != 54
        or not cyclic["exact_checks"]["gauge_fixed_classical_unary_q1_squared_zero"]
        or not cyclic["exact_checks"]["gauge_fixed_classical_unary_q1_cyclic_by_canonical_transport"]
        or not cyclic["exact_checks"]["BV_pairing_preserved"]
    ):
        raise ValueError("independent cyclic-complex replay failed")

    request = dependencies["integration_slice_request"]
    receiver = dependencies["integration_slice_receiver"]
    Draft202012Validator.check_schema(receiver)
    if (
        request["body"]["state"] != "REQUESTED"
        or "phase-shift-current and K_Berger Ward carriers"
        not in request["body"]["stop_condition"]
        or "54-row BRST matrix" not in request["body"]["forbid"]
    ):
        raise ValueError("independent producer-request replay failed")

    ledger = value["operator_ledger"]
    missing_quantum = (
        "Gamma1_regulated",
        "breaking_A1",
        "counterterm_B1",
        "Q1",
        "iota_K_1",
        "L_K_1",
        "cartan_defect_A_K_1",
    )
    if (
        ledger["Q0"] != "CERTIFIED"
        or ledger["iota_K_0"] != "CERTIFIED_CLASSICAL"
        or ledger["L_K_0"] != "CERTIFIED_CLASSICAL"
        or any(ledger[name] != "NOT_DEFINED" for name in missing_quantum)
    ):
        raise ValueError("operator ledger crossed its boundary")

    defect = value["defect_target"]
    if (
        defect["formula"]
        != "A_K^(1)=[Q0,iota_K^(1)]_+ + [Q1,iota_K^(0)]_+ - L_K^(1)"
        or defect["classification"]
        != "NONDEFINED_UPSTREAM_Q1_AND_RENORMALIZED_INSERTIONS_ABSENT"
        or defect["local_quotient_reduction"]
        != "NOT_ENTERED_UNDEFINED_DEFECT"
        or defect["raw_D_disposition"]
        != "SEPARATE_AFFINE_GENERATOR_NO_QUANTUM_D_IDENTITY_INFERRED"
    ):
        raise ValueError("defect target was over-promoted")

    first = value["first_missing_operator"]
    if (
        first["id"] != "Q1_BERGER_COMPLEX_CLOCK_ONE_LOOP"
        or first["status"] != "NOT_DEFINED"
        or first["upstream_first_missing_input"]
        != "POSITIVE_BERGER_COMPLEX_CLOCK_EUCLIDEAN_BV_INTEGRATION_SLICE_V1"
    ):
        raise ValueError("first missing operator drifted")

    phase = value["phase_boundary_zero_mode_ledger"]
    if (
        phase["rotation_generator_R"] != "CERTIFIED_CLASSICAL_MATRIX"
        or phase["phase_shift_current_regulated_insertion"] != "NOT_EXPORTED"
        or phase["K_Berger_regulated_Ward_carrier"] != "NOT_EXPORTED"
        or not phase["zero_mode_and_stabilizer_projectors"].startswith("NOT_DEFINED")
    ):
        raise ValueError("phase/current/zero-mode boundary drifted")

    if any(value["claim_flags"].values()):
        raise ValueError("claim flags crossed the nondefinition boundary")
    if (
        value["classical_import"]["real_structure"]
        != "NOT_EXPORTED_IN_IMPORTED_54_ROW_K_SIGNOFF"
        or value["verification_disposition"]["quantum_real_structure"]
        != "NOT_DEFINED_CLASSICAL_REAL_STRUCTURE_NOT_EXPORTED"
    ):
        raise ValueError("real-structure import was over-promoted")
    if value["one_loop_import"]["zero_quotient_implication"] != (
        "CONDITIONAL_REMOVABILITY_ONLY_AFTER_A_REGULATED_CONSISTENT_BREAKING_IS_COMPUTED"
    ):
        raise ValueError("zero quotient was used as a zero-defect shortcut")

    atlas = _load(ATLAS)
    Draft202012Validator(_load(ATLAS_SCHEMA)).validate(atlas)
    row = atlas["entries"][0]
    if (
        len(atlas["entries"]) != 1
        or row["quantum_data"]["entry_kind"] != "NON_MODE_PARTICLE_GUARD"
        or row["quantum_data"]["BRST_exactness"]["status"]
        != "NO_CERTIFIED_MAP"
        or row["quantum_data"]["anomaly_QME_dependency"]["status"] != "OPEN"
        or row["quantum_data"]["particle_interpretation"]["status"]
        != "NOT_APPLICABLE"
        or row["evidence"][0]["sha256"]
        != hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    ):
        raise ValueError("fail-closed atlas row drifted")


def verify() -> dict[str, Any]:
    value = _load(OUTPUT)
    verify_payload(value)
    print("Berger one-loop K-Cartan first-missing-operator independent audit: PASS")
    return value


if __name__ == "__main__":
    verify()
