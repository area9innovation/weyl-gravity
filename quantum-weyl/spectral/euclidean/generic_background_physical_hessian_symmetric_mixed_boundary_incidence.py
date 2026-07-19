#!/usr/bin/env python3
"""Assemble the symmetric-point triangle/contact logarithmic incidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from .generic_background_ghost_n3_five_carrier_projection import (
    CHANNELS,
    _carrier_value,
    _transverse_tracefree_basis,
)
from .generic_background_physical_hessian_mixed_h1_h2_corner_fixture import (
    MOMENTA,
    TT_BASIS_INDICES,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_SYMMETRIC_MIXED_BOUNDARY_INCIDENCE.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-symmetric-mixed-boundary-incidence-v1.schema.json"
DEPENDENCIES = {
    "isolated_triangle_obstruction": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_INTEGRATION_OBSTRUCTION.json",
    "generic_contact_projection": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_RESIDUE_PROJECTION.json",
    "equal_box_mixed_fixture": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MIXED_H1_H2_CORNER_FIXTURE.json",
    "common_Mellin_extension": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MELLIN_SUBTRACTION_SCALE_ROW.json",
}


def _q(value: Any) -> dict[str, int]:
    value = sp.Rational(value)
    return {"numerator": int(value.p), "denominator": int(value.q)}


def _from_q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": value["result_id"],
        "sha256": _sha256(path),
    }


def _evaluate_contact(row: dict[str, Any]) -> sp.Rational:
    numerator = sum(
        _from_q(term["coefficient"])
        for term in row["single_endpoint_terms"]
    )
    return sp.Rational(numerator)  # x1=x2=x3=1


def _fixture_carriers() -> list[sp.Rational]:
    momenta = [sp.Matrix(row) for row in MOMENTA]
    bases = [_transverse_tracefree_basis(momentum) for momentum in momenta]
    tensors = [
        bases[leg][basis_index]
        for leg, basis_index in enumerate(TT_BASIS_INDICES)
    ]
    return [
        sp.Rational(_carrier_value(carrier, momenta, tensors, labels))
        for carrier, labels in CHANNELS
    ]


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    obstruction = values["isolated_triangle_obstruction"]
    contacts = values["generic_contact_projection"]
    fixture = values["equal_box_mixed_fixture"]
    mellin = values["common_Mellin_extension"]
    if (
        obstruction["claim_flags"]["M14_RAISES_RELATIVE_QUOTIENT_RANK_BY_ONE"]
        is not True
        or contacts["claim_flags"]["GENERIC_H1_H2_CONTACT_ENDPOINT_KERNELS_EVALUATED"]
        is not True
        or mellin["claim_flags"]["FIXTURE_SCALE_ROW_COMPUTED"] is not True
    ):
        raise ValueError("mixed-boundary incidence dependency is not active")

    rows = []
    for channel_index, triangle in enumerate(obstruction["channel_rows"]):
        # The obstruction row is one ordered triangle.  The full polarized
        # trace-log contains all six orderings.  Contact rows already include
        # their -1/2 trace-log weight and are doubled over the two endpoints.
        triangle_full = 6 * _from_q(triangle["log_corner_coefficient"])
        contact_full = 2 * sum(
            _evaluate_contact(contacts["projection_rows"][11 * leg + channel_index])
            for leg in range(3)
        )
        rows.append(
            {
                "channel_id": triangle["channel_id"],
                "carrier_id": contacts["projection_rows"][channel_index]["carrier_id"],
                "label_order": contacts["projection_rows"][channel_index]["label_order"],
                "triangle_ordering_multiplicity": 6,
                "triangle_full_log_coefficient": _q(triangle_full),
                "contact_endpoint_count": 6,
                "contact_full_log_coefficient": _q(contact_full),
                "combined_log_mu2_coefficient": _q(triangle_full + contact_full),
            }
        )

    if any(
        sum(_from_q(rows[index][field]) for index in range(7, 10)) != 0
        for field in (
            "triangle_full_log_coefficient",
            "contact_full_log_coefficient",
            "combined_log_mu2_coefficient",
        )
    ):
        raise ValueError("mixed incidence left the symmetric I28 quotient section")

    carriers = _fixture_carriers()
    triangle_value = sum(
        carriers[index] * _from_q(row["triangle_full_log_coefficient"])
        for index, row in enumerate(rows)
    )
    contact_value = sum(
        carriers[index] * _from_q(row["contact_full_log_coefficient"])
        for index, row in enumerate(rows)
    )
    combined_value = triangle_value + contact_value
    expected = fixture["combined_raw_logarithm"]
    if (
        _q(triangle_value) != expected["three_H1_corner_coefficient"]
        or _q(contact_value) != expected["mixed_H1_H2_endpoint_coefficient"]
        or _q(combined_value) != expected["sum"]
        or _q(combined_value) != mellin["renormalization_scale_row"]["coefficient"]
    ):
        raise ValueError("mixed boundary incidence lost the equal-box tensor fixture")

    result = {
        "schema": "quantum-weyl-generic-background-physical-hessian-symmetric-mixed-boundary-incidence-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_SYMMETRIC_MIXED_BOUNDARY_INCIDENCE",
        "result_state": "SYMMETRIC_POINT_TRIANGLE_CONTACT_BOUNDARY_INCIDENCE_ASSEMBLED_H2_CANCELLATION_REFUTED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": contacts["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "kinematics": "x1=x2=x3=1",
            "carrier": "scalar-flat ten-dimensional five-carrier quotient",
            "subtraction": "common resolved-boundary Mellin minimal subtraction",
        },
        "incidence_convention": {
            "triangle_ordering_multiplicity": 6,
            "contact_trace_log_weight": "already included in endpoint residue",
            "contact_endpoint_multiplicity_per_cell": 2,
            "contact_cell_count": 3,
            "overall_loop_prefactor": "(4*pi)^-2 excluded",
        },
        "channel_rows": rows,
        "equal_box_tensor_reconstruction": {
            "TT_basis_indices": list(TT_BASIS_INDICES),
            "carrier_values": [_q(value) for value in carriers],
            "triangle_full_log_coefficient": _q(triangle_value),
            "contact_full_log_coefficient": _q(contact_value),
            "combined_log_mu2_coefficient": _q(combined_value),
            "identity": "-1975/72+2704/27=15707/216",
        },
        "M14_disposition": {
            "symmetric_point_algebraic_H2_cancellation": "REFUTED",
            "combined_scale_row": "NONZERO",
            "common_Mellin_distribution_extension": "FIXED",
            "generic_box_disposition": "NOT_COMPUTED",
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "claim_flags": {
            "SYMMETRIC_POINT_TRIANGLE_CONTACT_INCIDENCE_ASSEMBLED": True,
            "SYMMETRIC_POINT_H2_CANCELLATION_OF_M14_REFUTED": True,
            "SYMMETRIC_POINT_COMBINED_SCALE_ROW_COMPUTED": True,
            "COMMON_MELLIN_EXTENSION_RENORMALIZES_NONZERO_COMBINED_ROW": True,
            "GENERIC_BOX_TRIANGLE_CONTACT_INCIDENCE_ASSEMBLED": False,
            "GENERIC_PHYSICAL_M14_DISPOSED": False,
            "FINITE_LOCAL_MIXED_ROWS_FIXED": False,
            "PHYSICAL_THIRD_CURVATURE_FORM_FACTORS_COMPLETE": False,
            "QME_OR_ANOMALY_STATUS_CHANGED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "next_gate": "COMPUTE_GENERIC_BOX_TRIANGLE_CORNER_RESIDUE_ROWS_AND_ASSEMBLE_FULL_BOUNDARY_INCIDENCE",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL certificate assembles the full six-ordering triangle corner row with all six H1-H2 contact endpoints at x1=x2=x3=1. It proves that algebraic H2 does not cancel the symmetric-point M14 divergence and that the common Mellin extension yields the nonzero scale row 15707/216 before (4*pi)^-2. It does not assemble generic-box triangle corner residues, fix finite local rows, dispose generic M14, complete physical form factors, change the QME or anomaly disposition, or certify a Lorentzian theory.",
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text() != rendered:
            raise SystemExit("stored symmetric mixed-boundary incidence is stale")
        print("symmetric physical mixed-boundary incidence: PASS")
        return 0
    OUTPUT.write_text(rendered)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
