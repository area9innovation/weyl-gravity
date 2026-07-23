"""Build the paper-ready classification from a certified channel handoff.

This producer is deliberately separate from the fail-closed scaffold in
``produce.py``.  It emits no classification when the typed global handoff is
absent, and it never calls the available one-sided future-regular relation a
full two-ended scattering matrix.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from jsonschema import Draft202012Validator

from black_hole_programme.phase3.axial_global_connection_matrix_v5.chunks.verify_channel_handoff_schema import (
    validate as validate_handoff_schema,
)

from .affine_adapter import json_ready, validate_channel_handoff_algebra


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
HANDOFF = ROOT / (
    "black_hole_programme/phase3/axial_global_connection_matrix_v5/"
    "chunks/channel-handoff-v6.json"
)
OUTPUT = HERE / "activated-certificate.json"
SCHEMA = HERE / "activated-schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _origin_summary(cell_result: dict, endpoint: str) -> dict:
    blocks = cell_result["origin_blocks"][endpoint]
    return {
        "additional": json_ready(blocks["additional"]),
        "einstein": json_ready(blocks["einstein"]),
        "einstein_additional_mixed_status": blocks["mixed_status"],
        "einstein_additional_mixed_rank": blocks["mixed_rank"],
    }


def build_classification(handoff: dict, *, handoff_sha256: str) -> dict:
    algebra = validate_channel_handoff_algebra(handoff)
    cells = []
    for cell in handoff["cells"]:
        cell_id = cell["cell_id"]
        if cell["disposition"] != "CERTIFIED":
            cells.append(
                {
                    "cell_id": cell_id,
                    "omega_interval": cell["omega_interval"],
                    "disposition": "UNRESOLVED",
                    "shortfall": cell["shortfall"],
                }
            )
            continue
        result = algebra["certified_cells"][cell_id]
        payload = cell["validated_payload"]
        multipliers = payload["classification_witnesses"]["multiplier_bounds"]
        cells.append(
            {
                "cell_id": cell_id,
                "omega_interval": cell["omega_interval"],
                "disposition": "CERTIFIED",
                "future_horizon_regular_domain_dimension": 3,
                "additional_origin_dimension": 2,
                "einstein_origin_dimension": 1,
                "Iminus": {
                    "populated_dimension": result["Cminus_rank"],
                    "physical_quotient_dimension": result["inertia"][
                        "gminus"
                    ].complex_inertia[0]
                    + result["inertia"]["gminus"].complex_inertia[1],
                    "inertia": list(
                        result["inertia"]["gminus"].complex_inertia
                    ),
                    "origins": _origin_summary(result, "Iminus"),
                },
                "Iplus": {
                    "populated_dimension": result["Cplus_rank"],
                    "physical_quotient_dimension": result["inertia"][
                        "gplus"
                    ].complex_inertia[0]
                    + result["inertia"]["gplus"].complex_inertia[1],
                    "inertia": list(
                        result["inertia"]["gplus"].complex_inertia
                    ),
                    "origins": _origin_summary(result, "Iplus"),
                },
                "Hplus_outward_inertia": list(
                    result["inertia"]["GHplus"].complex_inertia
                ),
                "additional_global_direction_survives": True,
                "current_conservation": {
                    "identity": "GHplus+gplus-gminus=0",
                    "structural_identity_witness": payload["endpoint_forms"][
                        "conservation"
                    ]["structural_identity_witness"],
                    "affine_enclosure_independently_checked": result[
                        "conservation_enclosure_independently_checked"
                    ],
                },
                "one_sided_relation": {
                    "input": "Iminus",
                    "output": "Hplus_direct_sum_Iplus",
                    "definition": {
                        "horizon_coefficients": "Cminus^{-1}*a_Iminus",
                        "Iplus_coefficients": (
                            "Cplus*Cminus^{-1}*a_Iminus"
                        ),
                    },
                    "input_gram": "Gminus",
                    "output_gram": "GHplus_outward_direct_sum_Gplus",
                    "J_isometry_identity": (
                        "S^dagger*(GHplus_outward direct_sum Gplus)*S"
                        "=Gminus"
                    ),
                    "Cminus_inverse_whole_cell_certified": True,
                    "bounded_wavepacket_multiplier_certified": True,
                    "full_two_ended_scattering_matrix": False,
                },
                "wavepacket_multiplier_bounds": multipliers,
                "provenance": payload["provenance"],
            }
        )

    all_resolved = not algebra["unresolved_cells"]
    return {
        "schema": (
            "phase3-black-hole-axial-global-finite-flux-channel-"
            "classification-activated-v1"
        ),
        "result_id": (
            "PURE_WEYL_PHASE3_AXIAL_GLOBAL_FINITE_FLUX_CHANNEL_"
            "CLASSIFICATION_ACTIVATED_V1"
        ),
        "lifecycle": "CERTIFIED" if all_resolved else "SCOPED_SHORTFALL",
        "dependency_tags": ["LORENTZIAN-CAUSAL", "REDUCED-MODE"],
        "scope": {
            "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild exterior with M=1",
            "sector": "axial ell=2",
            "pilot_frequency_interval": ["1/2", "129/256"],
            "positive_frequency_core": "C_c^infinity((1/2,129/256);C^3)",
            "completion": "L2([1/2,129/256];C^3)",
            "relation": "Iminus to Hplus direct_sum Iplus",
            "missing_boundary_block": "Hminus incoming data",
        },
        "input": {
            "handoff_path": str(HANDOFF.relative_to(ROOT)),
            "handoff_sha256": handoff_sha256,
            "handoff_schema": handoff["schema"],
        },
        "cells": cells,
        "parent": {
            "exact_contiguous_cover": True,
            "all_cells_resolved": all_resolved,
            "unresolved_cells": algebra["unresolved_cells"],
            "additional_global_channel_classified": all_resolved,
            "wavepacket_extension_certified": all_resolved,
            "current_conservation_certified": all_resolved,
            "one_sided_J_isometry_constructed": all_resolved,
            "full_scattering_matrix_constructed": False,
        },
        "does_not_establish": [
            "a two-ended scattering matrix because Hminus incoming data are absent",
            "the remainder of M*omega in [129/256,3/4]",
            "polar parity or ell values other than two",
            "upper-half-plane pole exclusion or linear stability",
            "a positive CPT metric, particles or unitarity",
            "that a negative endpoint or populated flux direction is a quantum ghost",
        ],
    }


def verify_document(document: dict) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(document),
        key=lambda error: list(error.path),
    )
    if errors:
        path = ".".join(str(part) for part in errors[0].path) or "root"
        raise ValueError(f"{path}: {errors[0].message}")
    cells = document["cells"]
    cursor = Fraction(1, 2)
    upper = Fraction(129, 256)
    for index, cell in enumerate(cells):
        if cell["cell_id"] != f"q{index}":
            raise ValueError("activated cells are not ordered q0,q1,...")
        lo, hi = map(Fraction, cell["omega_interval"])
        if lo != cursor or hi <= lo:
            raise ValueError(
                "activated cells have a gap, overlap, or reversed interval"
            )
        cursor = hi
    if cursor != upper:
        raise ValueError("activated cells do not exactly cover the pilot interval")
    certified = [cell for cell in cells if cell["disposition"] == "CERTIFIED"]
    unresolved = [cell for cell in cells if cell["disposition"] == "UNRESOLVED"]
    parent = document["parent"]
    if parent["all_cells_resolved"] != (not unresolved):
        raise ValueError("parent resolved flag disagrees with cells")
    if parent["unresolved_cells"] != [cell["cell_id"] for cell in unresolved]:
        raise ValueError("parent unresolved-cell ledger disagrees with cells")
    if parent["additional_global_channel_classified"] != (not unresolved):
        raise ValueError("additional-channel promotion crosses unresolved cell")
    for cell in certified:
        if (
            cell["future_horizon_regular_domain_dimension"] != 3
            or cell["additional_origin_dimension"] != 2
            or cell["einstein_origin_dimension"] != 1
        ):
            raise ValueError("certified horizon-origin dimensions changed")
        if not cell["additional_global_direction_survives"]:
            raise ValueError("certified full-rank cell deleted additional origins")
        conservation = cell["current_conservation"]
        witness = conservation["structural_identity_witness"]
        if (
            witness["kind"] != "verified-action-current-identity"
            or not conservation["affine_enclosure_independently_checked"]
        ):
            raise ValueError(
                "certified cell lacks structural and affine current conservation"
            )
        relation = cell["one_sided_relation"]
        if (
            not relation["Cminus_inverse_whole_cell_certified"]
            or not relation["bounded_wavepacket_multiplier_certified"]
            or relation["full_two_ended_scattering_matrix"]
        ):
            raise ValueError("certified one-sided relation has invalid scope")
        for endpoint in ("Iminus", "Iplus"):
            data = cell[endpoint]
            if data["populated_dimension"] != 3:
                raise ValueError("certified populated dimension is not three")
            if sum(data["inertia"]) != 3:
                raise ValueError("certified inertia does not sum to three")
            if data["physical_quotient_dimension"] != (
                data["inertia"][0] + data["inertia"][1]
            ):
                raise ValueError("physical quotient/inertia mismatch")
            origins = data["origins"]
            for name, dimension in (("additional", 2), ("einstein", 1)):
                restricted = origins[name]
                if restricted["status"] == "CERTIFIED" and sum(
                    restricted["inertia"]
                ) != dimension:
                    raise ValueError(
                        f"{endpoint} {name} restricted inertia has wrong dimension"
                    )
            mixed_status = origins["einstein_additional_mixed_status"]
            mixed_rank = origins["einstein_additional_mixed_rank"]
            if (
                (mixed_status == "EXACT_ZERO" and mixed_rank != 0)
                or (mixed_status == "CERTIFIED_NONZERO" and mixed_rank != 1)
                or (mixed_status == "UNRESOLVED" and mixed_rank is not None)
            ):
                raise ValueError(f"{endpoint} origin-mixing witness is inconsistent")
    if document["parent"]["full_scattering_matrix_constructed"]:
        raise ValueError("one-sided handoff called a full scattering matrix")
    if document["parent"]["current_conservation_certified"] != (not unresolved):
        raise ValueError("parent current-conservation flag disagrees with cells")
    if document["parent"]["one_sided_J_isometry_constructed"] != (
        not unresolved
    ):
        raise ValueError("parent one-sided relation flag disagrees with cells")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not HANDOFF.exists():
        print("NOT_ACTIVATED: typed global channel handoff is absent")
        return 4
    handoff = json.loads(HANDOFF.read_text())
    validate_handoff_schema(handoff)
    document = build_classification(handoff, handoff_sha256=sha256(HANDOFF))
    verify_document(document)
    if args.check:
        if not OUTPUT.exists() or json.loads(OUTPUT.read_text()) != document:
            print("REFUSED: activated certificate drift or absence")
            return 3
    else:
        OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print("PASS: activated axial global channel classification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
