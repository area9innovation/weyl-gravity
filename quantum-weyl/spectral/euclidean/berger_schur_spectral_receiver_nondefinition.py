#!/usr/bin/env python3
"""Build the fail-closed Berger five-form-factor receiver disposition."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/BERGER_SCHUR_SPECTRAL_RECEIVER_NONDEFINITION_V1.json"
SCHEMA = HERE / "schema/berger-schur-spectral-receiver-nondefinition-v1.schema.json"

DEPENDENCIES = {
    "parameterized_family": HERE / "certificates/PARAMETERIZED_PARITY_EVEN_FIVE_FORM_FACTOR_FAMILY.json",
    "independent_family_audit": HERE / "certificates/PARAMETERIZED_PARITY_EVEN_FIVE_FORM_FACTOR_FAMILY_INDEPENDENT_AUDIT.json",
    "background_shortfall": HERE / "certificates/BACKGROUND_SPECIFIC_FIVE_FORM_FACTOR_SPECTRAL_REALIZATION_SHORTFALL.json",
    "normalized_variation": HERE / "certificates/NORMALIZED_SCHUR_PSEUDODIFFERENTIAL_VARIATION.json",
    "low_blocks": HERE / "certificates/SCALAR_FLAT_BERGER_VECTOR_SCHUR_LOW_BLOCKS.json",
    "high_mode_obstruction": HERE / "certificates/SCALAR_FLAT_BERGER_VECTOR_SCHUR_HIGH_MODE_TRACE_MAJORANT_OBSTRUCTION_V1.json",
    "generic_kernel_nonuniqueness": HERE / "certificates/GENERIC_PRIMED_SCHUR_FINITE_RELATIVE_TRACE_KERNEL_NONUNIQUENESS.json",
    "m23_surrogate_obstruction": HERE / "certificates/SCALAR_FLAT_BERGER_SCHUR_SURROGATE_OBSTRUCTION.json",
}
PINNED = {
    "parameterized_family": "b615a8aedb305e8014ad904a8bc2648fe149678aa201d65217164eecf9e791f0",
    "independent_family_audit": "254670931510a3d70a63556bd4734f3ce32486ad0d810143f04e88756cff7aaf",
    "background_shortfall": "45c0debd97f904f80d4454d69582515761a97eafb83e9babc69af91eadcab890",
    "normalized_variation": "5e437f7feed2044fd4ab7254388556536e41bf74a874398ece47f1d8b88f4a95",
    "low_blocks": "58d8646e3aedc1a897a8e6d05d6128f0e0eb4f885225443b9133f1c1968914f0",
    "high_mode_obstruction": "73b4ec7e13df4ca55477d13f2bbfd4d2bf398eee6f8a313fb74d28a246cd7157",
    "generic_kernel_nonuniqueness": "dd114394a10d0669bcbdad88adbec31e789a37f264c39d314b2e672a4baae89c",
    "m23_surrogate_obstruction": "687aa26ec62e34dfa9adde53f4d1793741a97b9829c7dee55b71f11f6d54f2d5",
}
REQUESTS = {
    "M21": ROOT / "planning/forge-requests/global-spectral-resolvent-relative-determinant.json",
    "M23": ROOT / "planning/forge-requests/scalar-flat-berger-spectral-measure.json",
}
REQUEST_HASHES = {
    "M21": "e165d4f9e6c86bc012df6f655abb9fddc97d77eb13a7d1a07bd167c0738d2632",
    "M23": "f22cdec8cbba70620a1847c26d7da9cbc074a873781dec425bb6d9249e753f9c",
}

COORDINATES = [
    "I10_123",
    "I24_123", "I24_213", "I24_312",
    "I25_123", "I25_213", "I25_312",
    "I28_123", "I28_132",
    "I29_123",
]
CARRIERS = {
    "I10": ["I10_123"],
    "I24": ["I24_123", "I24_213", "I24_312"],
    "I25": ["I25_123", "I25_213", "I25_312"],
    "I28": ["I28_123", "I28_132"],
    "I29": ["I29_123"],
}
MISSING = (
    "REGULATED_B1_PLUS_FINITE_PART_B2_PLUS_TRACE_CLASS_B3_ON_COMPLETE_"
    "PRIMED_BERGER_VECTOR_SCHUR_SPECTRUM"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(name: str) -> dict[str, str]:
    path = DEPENDENCIES[name]
    actual = _sha256(path)
    if actual != PINNED[name]:
        raise ValueError(f"{name} hash drifted: {actual}")
    payload = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": payload["result_id"],
        "sha256": actual,
    }


def _request(name: str) -> dict[str, str]:
    path = REQUESTS[name]
    actual = _sha256(path)
    if actual != REQUEST_HASHES[name]:
        raise ValueError(f"{name} request hash drifted: {actual}")
    payload = json.loads(path.read_text())
    if payload["body"]["state"] != "ACCEPTED":
        raise ValueError(f"{name} request lifecycle drifted")
    return {
        "path": str(path.relative_to(ROOT)),
        "request_id": payload["id"],
        "sha256": actual,
        "status": "ACCEPTED_NOT_LANDED",
    }


def _rational(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def build() -> dict[str, Any]:
    family = json.loads(DEPENDENCIES["parameterized_family"].read_text())
    shortfall = json.loads(DEPENDENCIES["background_shortfall"].read_text())
    low = json.loads(DEPENDENCIES["low_blocks"].read_text())
    variation = json.loads(DEPENDENCIES["normalized_variation"].read_text())
    high = json.loads(DEPENDENCIES["high_mode_obstruction"].read_text())
    generic = json.loads(DEPENDENCIES["generic_kernel_nonuniqueness"].read_text())

    if family["canonical_quotient_section"]["coordinates"] != COORDINATES:
        raise ValueError("frozen quotient coordinates drifted")
    if family["ambiguity_module"]["rank"] != 10:
        raise ValueError("frozen ambiguity rank drifted")
    if variation["results"]["variation_orders"] != [-2, -4, -6]:
        raise ValueError("Schur insertion orders drifted")
    if low["claim_flags"]["ALL_REPRESENTATION_BLOCKS_COMPUTED"] is not False:
        raise ValueError("low-block scope unexpectedly promoted")
    if high["trace_ideal_disposition"]["first_insertion_absolute_trace_majorant"] != "DOES_NOT_EXIST":
        raise ValueError("high-mode B1 obstruction missing")
    if generic["claim_flags"]["EXACT_FINITE_KERNEL_NONUNIQUENESS_PROVED"] is not True:
        raise ValueError("generic finite-kernel nonuniqueness not certified")

    digests = family["parameterized_family"]["universal_partial_BV_channel_row_digests"]
    coordinate_ledger = []
    for carrier, coordinates in CARRIERS.items():
        for coordinate in coordinates:
            coordinate_ledger.append({
                "carrier": carrier,
                "coordinate": coordinate,
                "universal_partial_BV_status": "COMPUTED",
                "universal_partial_BV_digest": digests[coordinate],
                "finite_Schur_status": "NONDEFINED",
                "complete_coordinate_status": "NONDEFINED",
                "smallest_missing_spectral_object": MISSING,
            })

    carrier_ledger = [{
        "carrier": carrier,
        "coordinates": coordinates,
        "universal_partial_BV_status": "COMPUTED",
        "complete_function_status": "NONDEFINED",
        "reason": "rank-ten finite Schur ambiguity and absent complete regulated Berger spectrum",
    } for carrier, coordinates in CARRIERS.items()]

    curvature = shortfall["candidate_background"]
    scalar = Fraction(curvature["scalar_curvature"]["numerator"], curvature["scalar_curvature"]["denominator"])
    ricci2 = Fraction(curvature["ricci_squared"]["numerator"], curvature["ricci_squared"]["denominator"])
    wres_k = (scalar * scalar + 4 * ricci2) / 9
    wres_k2 = (scalar * scalar + 2 * ricci2) / 27
    scale = (5 * scalar * scalar + 22 * ricci2) / 54

    certificate = {
        "$schema": "../schema/berger-schur-spectral-receiver-nondefinition-v1.schema.json",
        "schema": "quantum-weyl-berger-schur-spectral-receiver-nondefinition-v1",
        "result_id": "BERGER_SCHUR_SPECTRAL_RECEIVER_NONDEFINITION_V1",
        "result_state": "MAXIMAL_CERTIFIED_INPUT_ASSEMBLED_FIVE_COMPLETE_FUNCTIONS_NONDEFINED",
        "lifecycle_state": "PARAMETERIZED_RECEIVER_SPECIALIZED_GLOBAL_FINITE_INPUT_STILL_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "input_commit": "0200fc87b",
        "dependencies": {name: _reference(name) for name in DEPENDENCIES},
        "external_math_requests": {name: _request(name) for name in REQUESTS},
        "background_and_conventions": {
            "background": curvature["background_id"],
            "metric": curvature["metric"],
            "orientation": curvature["orientation"],
            "domain_status": "EXACT_LOW_BLOCKS_ONLY_GLOBAL_COMMON_DOMAIN_NOT_CERTIFIED",
            "priming_status": "LOW_BLOCK_SCALAR_CONSTANT_AND_FIVE_A1_KILLING_ZEROS_CERTIFIED_ONLY",
            "phase_and_contour": curvature["candidate_contour"],
            "phase_and_contour_status": "DECLARED_NOT_GLOBALLY_CERTIFIED",
            "reference_scale": curvature["reference_scale"],
            "insertion_convention": "B1=-(1/3)Delta0^-1 delta W d Delta0^-1; B2 order -4; B3 order -6",
            "local_global_subtraction": "LOCAL_WODZICKI_ROWS_EXACT; REGULATED_FINITE_GLOBAL_ROWS_ABSENT",
        },
        "independent_local_scale_replay": {
            "scalar_curvature": _rational(scalar),
            "ricci_squared": _rational(ricci2),
            "Wres_K_density_without_(4pi)^-2": _rational(wres_k),
            "Wres_K2_density_without_(4pi)^-2": _rational(wres_k2),
            "dlogmu_logDet3_density_without_(4pi)^-2": _rational(scale),
            "status": "EXACT_LOCAL_ROWS_ONLY",
        },
        "zero_pole_replay": {
            "scope": "2j<=2 and abs(n)<=1",
            "matched_low_block_zero_poles": "VERIFIED_BY_IMPORTED_EXACT_THEOREM",
            "all_mode_continuation": "NONDEFINED",
            "finite_exceptional_block_census": "NONDEFINED",
        },
        "receiver": {
            "coordinate_order": COORDINATES,
            "dimension": 10,
            "ambiguity_matrix": [[int(i == j) for j in range(10)] for i in range(10)],
            "ambiguity_rank": 10,
            "transpose_kernel_dimension": 0,
            "eliminated_relation": "I28_123+I28_132+I28_231=0",
            "coordinate_ledger": coordinate_ledger,
            "carrier_ledger": carrier_ledger,
            "complete_function_count": 0,
            "universal_partial_BV_carrier_count": 5,
        },
        "spectral_disposition": {
            "B1": "ORDINARY_ABSOLUTE_TRACE_OBSTRUCTED_REGULATED_VALUE_NOT_COMPUTED",
            "B2": "FINITE_PART_NOT_COMPUTED",
            "B3": "COMPLETE_TRACE_CLASS_TAIL_NOT_COMPUTED",
            "complete_A_t_high_mode_coercivity": "NOT_COMPUTED",
            "smallest_missing_spectral_object": MISSING,
            "next_gate": "LANDED_M21_OR_M23_REPLACEMENT_WITH_REGULATOR_SUBTRACTION_COMPLETE_PRIMING_AND_CERTIFIED_GLOBAL_TAIL",
        },
        "claim_flags": {
            "TERMINAL_VARIATION_AND_BLOCK_RESULTS_IMPORTED": True,
            "MAXIMAL_CERTIFIED_BERGER_INPUT_ASSEMBLED": True,
            "LOCAL_SCALE_ROWS_REPLAYED_EXACTLY": True,
            "COORDINATE_BY_COORDINATE_NONDEFINITION_EMITTED": True,
            "UNIVERSAL_PARTIAL_BV_SUMMAND_PRESERVED": True,
            "M21_OR_M23_GLOBAL_PAYLOAD_LANDED": False,
            "COMPLETE_FIVE_FUNCTIONS_COMPUTED": False,
            "GLOBAL_DETERMINANT_OR_FINITE_TRACE_COMPUTED": False,
            "SCALAR_SURROGATE_USED": False,
            "ANOMALY_COEFFICIENT_LIFECYCLE_CHANGED": False,
            "QME_OR_LORENTZIAN_HADAMARD_PROMOTED": False,
        },
        "paper12_disposition": "NO_UPDATE_COEFFICIENT_LIFECYCLE_UNCHANGED",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL receiver integration imports the exact normalized "
            "Schur variations, low blocks, high-mode B1 trace obstruction, frozen rank-ten affine receiver, "
            "and accepted-but-unlanded M21/M23 requests. It preserves all ten universal partial-BV coordinate "
            "rows and independently replays the three exact local scale rows. Because the ordinary B1 trace "
            "is obstructed and no regulated B1, finite-part B2, complete B3 tail, global priming or exceptional "
            "continuation has landed, every complete Berger carrier function remains NONDEFINED. It does not "
            "use the scalar surrogate, compute a determinant or anomaly coefficient, change Paper 12, restore "
            "a QME, or establish any Lorentzian, Hadamard, state, particle, positivity or unitarity claim."
        ),
    }
    validate(certificate)
    return certificate


def validate(certificate: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build()
    rendered = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale Berger receiver certificate: {OUTPUT}")
    print("BERGER SCHUR SPECTRAL RECEIVER: 0/5 COMPLETE; EXACT NONDEFINITION LEDGER")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
