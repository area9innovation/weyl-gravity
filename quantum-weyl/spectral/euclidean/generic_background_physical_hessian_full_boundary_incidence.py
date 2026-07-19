#!/usr/bin/env python3
"""Assemble the generic physical triangle/contact logarithmic incidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from .generic_background_physical_hessian_triangle_corner_residues import (
    BOXES,
    _from_q,
    _q,
    _serialize,
)
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
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_FULL_BOUNDARY_INCIDENCE.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-full-boundary-incidence-v1.schema.json"
TRIANGLE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_CORNER_RESIDUES.json"
CONTACTS = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_RESIDUE_PROJECTION.json"
SYMMETRIC = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_SYMMETRIC_MIXED_BOUNDARY_INCIDENCE.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": value["result_id"],
        "sha256": _sha256(path),
    }


def _expression(row: dict[str, Any], term_key: str = "numerator_terms") -> sp.Expr:
    numerator = sum(
        _from_q(term["coefficient"])
        * sp.prod(box**power for box, power in zip(BOXES, term["box_exponents"]))
        for term in row[term_key]
    )
    denominator = sp.prod(
        box**power for box, power in zip(BOXES, row["box_denominator_exponents"])
    )
    return sp.cancel(numerator / denominator)


def _fixture_carriers() -> list[sp.Rational]:
    momenta = [sp.Matrix(row) for row in MOMENTA]
    bases = [_transverse_tracefree_basis(momentum) for momentum in momenta]
    tensors = [bases[leg][basis] for leg, basis in enumerate(TT_BASIS_INDICES)]
    return [
        sp.Rational(_carrier_value(carrier, momenta, tensors, labels))
        for carrier, labels in CHANNELS
    ]


def build() -> dict[str, Any]:
    triangle = json.loads(TRIANGLE.read_text())
    contacts = json.loads(CONTACTS.read_text())
    symmetric = json.loads(SYMMETRIC.read_text())
    if (
        triangle["claim_flags"]["GENERIC_BOX_TRIANGLE_CORNER_RESIDUE_ROWS_COMPUTED"]
        is not True
        or contacts["claim_flags"]["ALL_THREE_CONTACT_CELLS_PROJECTED"] is not True
        or symmetric["claim_flags"]["SYMMETRIC_POINT_TRIANGLE_CONTACT_INCIDENCE_ASSEMBLED"]
        is not True
    ):
        raise ValueError("full-boundary incidence dependency is not active")

    rows = []
    expressions = []
    for index, triangle_row in enumerate(triangle["channel_rows"]):
        triangle_total = _expression(triangle_row["six_ordering_total"])
        contact_total = 2 * sum(
            _expression(contacts["projection_rows"][11 * leg + index], "single_endpoint_terms")
            for leg in range(3)
        )
        combined = sp.cancel(triangle_total + contact_total)
        expressions.append((triangle_total, contact_total, combined))
        rows.append(
            {
                "channel_id": triangle_row["channel_id"],
                "carrier_id": triangle_row["carrier_id"],
                "label_order": triangle_row["label_order"],
                "triangle_six_ordering_scale_row": _serialize(triangle_total),
                "contact_six_endpoint_scale_row": _serialize(contact_total),
                "combined_scale_row": _serialize(combined),
                "combined_status": "NONZERO" if combined != 0 else "ZERO",
            }
        )

    for component in range(3):
        if sp.cancel(sum(expressions[index][component] for index in range(7, 10))) != 0:
            raise ValueError("full generic incidence violates the I28 quotient relation")

    carriers = _fixture_carriers()
    values = [
        sp.cancel(sum(carriers[index] * expressions[index][component] for index in range(11)))
        for component in range(3)
    ]
    fixture_boxes = tuple(int(sp.Matrix(row).dot(sp.Matrix(row))) for row in MOMENTA)
    evaluated = [sp.Rational(value.subs(dict(zip(BOXES, fixture_boxes)))) for value in values]
    expected = symmetric["equal_box_tensor_reconstruction"]
    if (
        _q(evaluated[0]) != expected["triangle_full_log_coefficient"]
        or _q(evaluated[1]) != expected["contact_full_log_coefficient"]
        or _q(evaluated[2]) != expected["combined_log_mu2_coefficient"]
    ):
        raise ValueError("generic incidence lost the exact TT fixture")

    nonzero = [row["channel_id"] for row in rows if row["combined_status"] == "NONZERO"]
    result = {
        "schema": "quantum-weyl-generic-background-physical-hessian-full-boundary-incidence-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_FULL_BOUNDARY_INCIDENCE",
        "result_state": "GENERIC_TRIANGLE_CONTACT_BOUNDARY_INCIDENCE_ASSEMBLED_M14_NONZERO_RENORMALIZED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": triangle["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "box_domain": "x1*x2*x3 nonzero",
            "carrier": "scalar-flat ten-dimensional five-carrier quotient",
            "subtraction": "common resolved-boundary Mellin minimal subtraction",
            "overall_loop_prefactor": "(4*pi)^-2 excluded",
        },
        "incidence_convention": {
            "triangle_ordering_count": 6,
            "contact_cell_count": 3,
            "contact_endpoints_per_cell": 2,
            "contact_trace_log_weight": "included in source residue",
        },
        "channel_rows": rows,
        "generic_disposition": {
            "nonzero_combined_channel_ids": nonzero,
            "nonzero_combined_channel_count": len(nonzero),
            "M14": "NONZERO_SCALE_ROW_RENORMALIZED_BY_COMMON_MELLIN_EXTENSION",
            "algebraic_H2_cancellation": "REFUTED_GENERICALLY",
            "finite_local_part": "NOT_FIXED",
        },
        "exact_fixture_replay": {
            "box_invariants": list(fixture_boxes),
            "triangle": _q(evaluated[0]),
            "contacts": _q(evaluated[1]),
            "combined": _q(evaluated[2]),
        },
        "dependencies": {
            "triangle": _reference(TRIANGLE),
            "contacts": _reference(CONTACTS),
            "symmetric_incidence": _reference(SYMMETRIC),
        },
        "claim_flags": {
            "FULL_TRIANGLE_CONTACT_BOUNDARY_INCIDENCE_ASSEMBLED": True,
            "GENERIC_PHYSICAL_M14_DISPOSED": True,
            "GENERIC_PHYSICAL_M14_NONZERO_SCALE_ROW": True,
            "GENERIC_ALGEBRAIC_H2_CANCELLATION_REFUTED": True,
            "GENERIC_I28_QUOTIENT_RELATION_PRESERVED": True,
            "FINITE_LOCAL_MIXED_ROWS_FIXED": False,
            "PHYSICAL_THIRD_CURVATURE_FORM_FACTORS_COMPLETE": False,
            "QME_OR_ANOMALY_STATUS_CHANGED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "next_gate": "FIX_FINITE_LOCAL_MIXED_ROWS_AND_ASSEMBLE_PHYSICAL_THIRD_CURVATURE_FORM_FACTORS",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL certificate assembles the generic logarithmic boundary incidence of all six physical H1^3 triangle orderings and all six H1-H2 contact endpoints. The combined generic scale row is nonzero, so algebraic H2 cancellation is refuted and M14 is disposed as a nonzero row renormalized by the common Mellin extension. It does not fix the finite local part, complete the five physical form factors, alter the certified anomaly or QME disposition, or certify a Lorentzian theory.",
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
            raise SystemExit("stored full physical boundary incidence is stale")
        print("generic physical full boundary incidence: PASS")
        return 0
    OUTPUT.write_text(rendered)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
