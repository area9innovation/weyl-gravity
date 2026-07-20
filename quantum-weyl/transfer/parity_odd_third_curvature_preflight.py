#!/usr/bin/env python3
"""Fail-closed preflight for the parity-odd third-curvature carrier quotient."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = (
    HERE
    / "certificates/PARITY_ODD_THIRD_CURVATURE_CARRIER_MANIFEST_PREFLIGHT.json"
)
SCHEMA = (
    HERE
    / "schema/parity-odd-third-curvature-carrier-manifest-preflight-v1.schema.json"
)
REQUEST = (
    ROOT
    / "planning/forge-requests/"
    "single-epsilon-labelled-jet-syzygy-quotient.json"
)
DEPENDENCIES = {
    "parity_even_nonlocal_manifest": (
        HERE
        / "certificates/FOUR_DIMENSIONAL_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST.json"
    ),
    "algebraic_cubic_weyl_carriers": (
        HERE / "certificates/FOUR_DIMENSIONAL_ALGEBRAIC_CUBIC_WEYL_CARRIERS.json"
    ),
    "four_dimensional_even_schouten_quotient": (
        ROOT
        / "quantum-weyl/local_bv/certificates/"
        "LOCAL_FOUR_DIMENSIONAL_SCHOUTEN_QUOTIENT_CERTIFICATE.json"
    ),
    "schouten_zero_weyl_image": (
        ROOT
        / "quantum-weyl/local_bv/certificates/"
        "LOCAL_SCHOUTEN_ZERO_WEYL_IMAGE_CERTIFICATE.json"
    ),
    "ambient_intrinsic_orbits": (
        ROOT
        / "quantum-weyl/local_bv/certificates/"
        "AFN0_AMBIENT_INTRINSIC_ORBIT_CERTIFICATE_DEGREES_THREE_FOUR.json"
    ),
}
EXPECTED_HASHES = {
    "parity_even_nonlocal_manifest": (
        "203cc58ea7d2b1cfd468bc660c616e8319250ab522614bcbc16410b1c7006c4c"
    ),
    "algebraic_cubic_weyl_carriers": (
        "921a5ce8ad89ca8289781883f5c72527008dae7e72c0e8bcbcf3dd7b61896b3d"
    ),
    "four_dimensional_even_schouten_quotient": (
        "e17eda0fdc3be3f53603b6a4bfaee727aa15787a856305c9c5e64a1091f8b0da"
    ),
    "schouten_zero_weyl_image": (
        "ffaecf1763e39297833d8958ee932dc10c86123f7112daeceaf3d94635be0b79"
    ),
    "ambient_intrinsic_orbits": (
        "f794a34a9cfe26c2bbdd5c621edec35e51a1705f5910fc43c7a84e7ff20a2d20"
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(payload["result_id"]),
        "sha256": _sha256(path),
    }


def build() -> dict[str, Any]:
    values = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    for name, path in DEPENDENCIES.items():
        if _sha256(path) != EXPECTED_HASHES[name]:
            raise ValueError(f"dependency hash drifted: {name}")

    even = values["parity_even_nonlocal_manifest"]
    algebraic = values["algebraic_cubic_weyl_carriers"]
    schouten = values["four_dimensional_even_schouten_quotient"]
    weyl_image = values["schouten_zero_weyl_image"]
    ambient = values["ambient_intrinsic_orbits"]
    if (
        even["claim_flags"][
            "PARITY_EVEN_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE"
        ]
        is not True
        or even["claim_flags"][
            "PARITY_ODD_DERIVATIVE_CARRIER_MANIFEST_COMPLETE"
        ]
        is not False
        or algebraic["tensor_carriers"]["parity_dimensions"]
        != {"even": 1, "odd": 1}
        or schouten["checks"]["parity_odd_weyl_sector"] != "NOT_COMPUTED"
        or weyl_image["checks"]["parity_odd_single_epsilon_enumeration"]
        != "NOT_COMPUTED"
        or weyl_image["odd_companion"]["status"]
        != "CONSTRUCTED_NOT_A_COMPLETE_BASIS"
        or ambient["checks"]["ambient_degree_five_six_graphs_not_materialized"]
        != "VERIFIED"
        or ambient["next_gates"]["algebraic_and_differential_Bianchi"]
        != "NOT_COMPUTED"
        or ambient["next_gates"]["integration_by_parts_quotient"]
        != "NOT_COMPUTED"
        or ambient["next_gates"]["dimension_specific_antisymmetrization"]
        != "NOT_COMPUTED"
    ):
        raise ValueError("parity-odd preflight capability boundary drifted")

    missing_operations = [
        "degree-six single-epsilon covariant-jet contraction generation",
        "module coefficients over labelled Box_1,Box_2,Box_3 with source-label action",
        "algebraic and differential Bianchi syzygies",
        "covariant-jet commutator syzygies through curvature order three",
        "integration-by-parts syzygies over the labelled-Laplacian module",
        "four-dimensional five-index Schouten syzygies with one epsilon",
        "locally exact Pontryagin/transgression submodule",
    ]
    result = {
        "schema": (
            "quantum-weyl-parity-odd-third-curvature-carrier-"
            "manifest-preflight-v1"
        ),
        "result_id": "PARITY_ODD_THIRD_CURVATURE_CARRIER_MANIFEST_PREFLIGHT",
        "result_state": (
            "OBSTRUCTED_MISSING_SINGLE_EPSILON_LABELLED_JET_SYZYGY_QUOTIENT"
        ),
        "lifecycle_state": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "scope": {
            "dimension": 4,
            "signature": "EUCLIDEAN",
            "background": (
                "noncompact asymptotically flat scalar-flat conformal representative"
            ),
            "curvature_order": 3,
            "parity": "ODD",
            "coefficient_module": (
                "real analytic functions of three labelled Laplacians on the "
                "declared kernel-free source complement"
            ),
        },
        "available_exact_inputs": {
            "zero_derivative_odd_anchor": (
                "one nonzero parity-odd algebraic C^3 class with one Hodge dual"
            ),
            "parity_even_nonlocal_quotient": {
                "raw_labelled_dimension": even["raw_module"][
                    "generic_label_orbit_dimension"
                ],
                "quotient_labelled_dimension": even["quotient_module"][
                    "generic_label_orbit_dimension"
                ],
                "functional_relation_rank": even["four_dimensional_identity"][
                    "relation_rank"
                ],
            },
            "single_epsilon_graph_enumerator": (
                "exact signed contraction-orbit enumeration only for bounded "
                "ambient total degrees three and four"
            ),
            "odd_hodge_companion": (
                "constructed existence witness, explicitly not a complete basis"
            ),
        },
        "capability_audit": {
            "raw_single_epsilon_contraction_graphs": (
                "AVAILABLE_ONLY_BELOW_REQUIRED_DEGREE"
            ),
            "degree_six_single_epsilon_factor_orbits": "NOT_MATERIALIZED",
            "labelled_laplacian_coefficient_module": "NOT_IMPLEMENTED",
            "differential_bianchi_syzygy_module": "NOT_IMPLEMENTED",
            "jet_commutator_syzygy_module": "NOT_IMPLEMENTED",
            "labelled_integration_by_parts_module": "NOT_IMPLEMENTED",
            "single_epsilon_four_dimensional_schouten_module": "NOT_IMPLEMENTED",
            "pontryagin_transgression_submodule": "NOT_IMPLEMENTED",
            "canonical_quotient_normal_form": "NOT_IMPLEMENTED",
        },
        "first_missing_operation": {
            "operation_id": "EXACT_SINGLE_EPSILON_LABELLED_JET_SYZYGY_QUOTIENT",
            "input": (
                "degree-six scalar contractions of three labelled Weyl/K jets "
                "and one epsilon over Q[Box_1,Box_2,Box_3] localized only by "
                "the declared kernel-free inverse policy"
            ),
            "quotient_by": missing_operations[2:],
            "required_outputs": [
                "canonical module basis and normal form",
                "complete syzygy matrix with exact generators",
                "S3 source-label action and stabilizers",
                "Pontryagin/transgression exact-submodule coordinates",
                "characteristic-zero quotient rank and dual nonmembership witnesses",
            ],
            "why_first": (
                "without this operation neither raw carrier generation nor "
                "equivalence of epsilon placements is exhaustive; consequently "
                "a quotient dimension or carrier list cannot be certified"
            ),
        },
        "missing_operation_ledger": missing_operations,
        "decision": {
            "complete_manifest": "NOT_COMPUTED",
            "canonical_representatives": "NOT_COMPUTED",
            "source_generic_stabilizers": "NOT_COMPUTED",
            "effective_labelled_channels": "NOT_COMPUTED",
            "functional_relations": "NOT_COMPUTED",
            "quotient_dimension": "NOT_COMPUTED",
            "coefficient_status": "NOT_COMPUTED",
            "sampling_used": False,
            "even_basis_dualization_promoted": False,
        },
        "forge_request": {
            "request_id": (
                "sf:forge-request/single-epsilon-labelled-jet-syzygy-quotient"
            ),
            "path": str(REQUEST.relative_to(ROOT)),
            "status": "REQUESTED",
        },
        "dependencies": {
            name: _reference(path, values[name])
            for name, path in DEPENDENCIES.items()
        },
        "claim_flags": {
            "EXACT_COMPLETENESS_BLOCKER_IDENTIFIED": True,
            "PARITY_ODD_DERIVATIVE_CARRIER_MANIFEST_COMPLETE": False,
            "PARITY_ODD_QUOTIENT_DIMENSION_COMPUTED": False,
            "PARITY_EVEN_DUALIZATION_ASSUMED_COMPLETE": False,
            "NUMERICAL_SAMPLING_PROMOTED": False,
            "PONTRYAGIN_CLASS_CONFLATED_WITH_NONLOCAL_ODD_SECTOR": False,
            "COEFFICIENT_COMPUTED": False,
            "QME_OR_LORENTZIAN_PROMOTED": False,
        },
        "next_gate": (
            "land and independently gate the exact single-epsilon labelled-jet "
            "syzygy quotient before enumerating or reducing the odd carriers"
        ),
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL preflight identifies the "
            "first exact missing operation preventing a complete parity-odd "
            "derivative-decorated third-curvature carrier manifest. Existing "
            "artifacts prove one algebraic odd C^3 anchor and can enumerate "
            "bounded single-epsilon contraction orbits, but they do not provide "
            "the degree-six labelled-jet module or its combined Bianchi, "
            "commutator, integration-by-parts, four-dimensional Schouten and "
            "Pontryagin/transgression syzygy quotient. Therefore no carrier "
            "basis, stabilizer list, functional relation or quotient dimension "
            "is promoted. This is a tooling/invariant-generation obstruction, "
            "not a vanishing theorem, coefficient, anomaly, QME, Lorentzian, "
            "state, particle or unitarity result."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if (
        value["decision"]["sampling_used"] is not False
        or value["decision"]["even_basis_dualization_promoted"] is not False
        or value["decision"]["quotient_dimension"] != "NOT_COMPUTED"
        or value["claim_flags"]["EXACT_COMPLETENESS_BLOCKER_IDENTIFIED"] is not True
        or any(
            value["claim_flags"][name] is not False
            for name in (
                "PARITY_ODD_DERIVATIVE_CARRIER_MANIFEST_COMPLETE",
                "PARITY_ODD_QUOTIENT_DIMENSION_COMPUTED",
                "PARITY_EVEN_DUALIZATION_ASSUMED_COMPLETE",
                "NUMERICAL_SAMPLING_PROMOTED",
                "PONTRYAGIN_CLASS_CONFLATED_WITH_NONLOCAL_ODD_SECTOR",
                "COEFFICIENT_COMPUTED",
                "QME_OR_LORENTZIAN_PROMOTED",
            )
        )
    ):
        raise ValueError("parity-odd preflight crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale parity-odd third-curvature preflight: {OUTPUT}")
    print(
        "PARITY-ODD THIRD-CURVATURE PREFLIGHT: "
        "OBSTRUCTED BY MISSING EXACT LABELLED-JET SYZYGY QUOTIENT"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
