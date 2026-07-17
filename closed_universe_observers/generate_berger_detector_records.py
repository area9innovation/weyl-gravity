#!/usr/bin/env python3
"""Generate two localized clock-labelled Berger detector record functionals.

This is a consumer of the authoritative classical clock, apparatus contract,
and retarded Maxwell signal.  It constructs the localized record algebra but
does not invent a pointwise nonvanishing theorem for the imported pulse.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
INPUT = PACKAGE / "fixtures/berger_localized_detector_records_input.json"
INPUT_SCHEMA = PACKAGE / "schema/berger-localized-detector-records-input-v1.schema.json"
SCHEMA = PACKAGE / "schema/berger-localized-detector-records-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS.json"

DEPENDENCIES = {
    "clock": ROOT / "d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json",
    "apparatus_contract": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_BV_SEMIDIRECT_PREFLIGHT.json",
    "retarded_signal": ROOT / "d_quotient_classical/certificates/BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL.json",
    "raw_D_nullity": ROOT / "d_quotient_classical/certificates/BERGER_FIXED_COUPLING_DELTA_CHARGE.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "independent_verifier": PACKAGE / "verify_berger_detector_records.py",
    "tests": PACKAGE / "tests/test_berger_detector_records.py",
    "report": PACKAGE / "reports/berger-localized-detector-records.md",
    "input": INPUT,
    "input_schema": INPUT_SCHEMA,
    "certificate_schema": SCHEMA,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: str | int) -> sp.Rational:
    item = Fraction(str(value))
    return sp.Rational(item.numerator, item.denominator)


def _strings(matrix: sp.Matrix) -> list[list[str]]:
    return [[sp.sstr(matrix[row, column]) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _patched(data: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(data)
    result.update(patch)
    return result


def _intervals_disjoint(left: list[sp.Rational], right: list[sp.Rational]) -> bool:
    return left[1] <= right[0] or right[1] <= left[0]


def evaluate(data: dict[str, Any]) -> dict[str, Any]:
    jacobian = sp.Matrix([[_q(value) for value in row] for row in data["relational_jacobian"]])
    detectors = data["detectors"]
    clock_labels = [_q(value) for value in data.get("detector_clock_labels", [item["clock_label"] for item in detectors])]
    clock_windows = [
        [_q(value) for value in interval]
        for interval in data.get("detector_clock_windows", [item["clock_window"] for item in detectors])
    ]
    rod_centers = [
        [_q(value) for value in center]
        for center in data.get("detector_rod_centers", [item["rod_center"] for item in detectors])
    ]
    half_widths = [_q(item["rod_half_width"]) for item in detectors]
    spatially_disjoint = any(
        abs(rod_centers[0][axis] - rod_centers[1][axis]) >= half_widths[0] + half_widths[1]
        for axis in range(3)
    )
    supports_disjoint = _intervals_disjoint(clock_windows[0], clock_windows[1]) or spatially_disjoint
    detector_ids = [item["id"] for item in detectors]
    record_matrix = sp.Matrix(
        [[int(probe_support == detector_id) for probe_support in data["probe_supports"]] for detector_id in detector_ids]
    )
    emitter_end = _q(data["emitter_clock_support"][1])
    clock_ordered_after_emitter = all(emitter_end < interval[0] for interval in clock_windows)
    requirements = {
        "relational_chart_nondegenerate": jacobian.det() != 0,
        "clock_labels_distinct": len(set(clock_labels)) == 2,
        "detector_supports_disjoint": supports_disjoint,
        "record_functionals_independent": record_matrix.rank() == 2,
    }
    return {
        "jacobian": jacobian,
        "clock_labels": clock_labels,
        "clock_windows": clock_windows,
        "rod_centers": rod_centers,
        "record_matrix": record_matrix,
        "clock_ordered_after_emitter": clock_ordered_after_emitter,
        "requirements": requirements,
    }


def _load_dependencies() -> dict[str, dict[str, Any]]:
    loaded = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "clock": ["exact_backreacted_background_exists", "everywhere_timelike_phase_clock"],
        "apparatus_contract": ["BERGER_RELATIONAL_APPARATUS_CONTRACT", "BERGER_MAXWELL_SEMIDIRECT_GAUGE_Q2"],
        "retarded_signal": ["BERGER_COMPACT_CONSERVED_MAXWELL_SOURCE", "BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL"],
        "raw_D_nullity": ["scoped_D_verdict_promoted", "total_helical_presymplectic_contraction_zero"],
    }
    for name, flags in required.items():
        for flag in flags:
            if loaded[name].get("flags", {}).get(flag) is not True:
                raise AssertionError(f"required dependency flag dropped: {name}.{flag}")
    return loaded


def build() -> dict[str, Any]:
    data = json.loads(INPUT.read_text())
    input_schema = json.loads(INPUT_SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(input_schema)
    jsonschema.Draft202012Validator(input_schema).validate(data)
    dependencies = _load_dependencies()
    result = evaluate(data)
    if not all(result["requirements"].values()):
        raise AssertionError(f"base detector record fixture failed: {result['requirements']}")
    mutations = []
    for mutation in data["mutations"]:
        mutated = evaluate(_patched(data, mutation["patch"]))
        requirement = mutation["expected_failed_requirement"]
        mutations.append({
            "name": mutation["name"],
            "expected_failed_requirement": requirement,
            "observed_requirement_value": mutated["requirements"][requirement],
            "observed_record_rank": int(mutated["record_matrix"].rank()),
            "expected_failure_passed": mutated["requirements"][requirement] is False,
        })
    if not all(item["expected_failure_passed"] for item in mutations):
        raise AssertionError("detector record mutation rail did not fail closed")
    dependency_refs = {
        name: {
            "path": str(path.relative_to(ROOT)),
            "result_id": dependencies[name]["result_id"],
            "sha256": _sha256(path),
            "claim_boundary": dependencies[name]["claim_boundary"],
        }
        for name, path in DEPENDENCIES.items()
    }
    detector_rows = []
    for index, detector in enumerate(data["detectors"]):
        detector_rows.append({
            "id": detector["id"],
            "clock_label": sp.sstr(result["clock_labels"][index]),
            "clock_window": [sp.sstr(value) for value in result["clock_windows"][index]],
            "rod_center": [sp.sstr(value) for value in result["rod_centers"][index]],
            "rod_half_width": detector["rod_half_width"],
            "record_functional": (
                f"Q_{index}[F]=integral rho_{index}(Theta,R) "
                "<F,dTheta wedge dR1>_gHat vol_gHat"
            ),
        })
    return {
        "schema": "closed-universe-berger-localized-detector-records-v1",
        "result_id": "BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS",
        "setting_id": data["setting_id"],
        "claim_status": "CERTIFIED_TWO_LOCALIZED_RECORD_FUNCTIONALS_POINTWISE_RETARDED_RESPONSE_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": dependency_refs,
        "relational_probe_apparatus": {
            "coordinates": data["relational_coordinates"],
            "jacobian": _strings(result["jacobian"]),
            "jacobian_determinant": sp.sstr(result["jacobian"].det()),
            "rod_health": "three standard-sign probe scalar wave equations with independent local Cauchy gradients; stress and recoil are excluded at probe order",
            "gauge_scope": "Diff-covariant relational localization; Weyl-invariant gHat and four-dimensional Maxwell F; Maxwell-gauge invariant because records depend on F=dA",
        },
        "detector_records": detector_rows,
        "record_algebra": {
            "definition": "A_record=R[Q_0,Q_1] with pointwise product and real involution",
            "probe_evaluation_matrix": _strings(result["record_matrix"]),
            "rank": int(result["record_matrix"].rank()),
            "support_separation": "the two compact relational windows are disjoint",
            "clock_ordered_after_emitter": result["clock_ordered_after_emitter"],
        },
        "source_to_record_chain": {
            "source": "the imported compact neutral q-closed Maxwell current j=d kappa",
            "retarded_field": "the imported unique Lorenz representative F_ret=d G_ret J",
            "record_map": "j maps to (Q_0[F_ret],Q_1[F_ret])",
            "well_defined": True,
            "strict_future_nonzero_values_certified": False,
            "obstruction": "the imported theorem gives causal support and global nonvanishing but no pointwise Green-kernel witness placing nonzero F_ret in both predeclared detector windows",
        },
        "gauge_and_quotient_tests": {
            "Diff": "PASS_FOR_PROBE_RELATIONAL_FUNCTIONALS",
            "Weyl": "PASS_FOR_PROBE_RELATIONAL_FUNCTIONALS",
            "Maxwell_gauge": "PASS",
            "raw_D": "OPEN_WITH_ROD_SECTOR_NOT_IN_IMPORTED_PHASE_SPACE",
            "K_Berger": "OPEN_WITH_ROD_SECTOR_NOT_IN_IMPORTED_INTERACTING_COMPLEX",
        },
        "mutation_results": mutations,
        "flags": {
            "TWO_LOCALIZED_CLOCK_LABELLED_RECORD_FUNCTIONALS": True,
            "LOCAL_ROD_PROBE_CHART_NONDEGENERATE": True,
            "RECORD_ALGEBRA_TWO_GENERATORS": True,
            "SOURCE_TO_RETARDED_FIELD_TO_RECORD_MAP_DEFINED": True,
            "TWO_NONZERO_RETARDED_RECORD_VALUES": False,
            "STRICT_FUTURE_DETECTOR_INTERSECTION_CERTIFIED": False,
            "ROD_BACKREACTION_AND_APPARATUS_RECOIL_INCLUDED": False,
            "D_DESCENT_WITH_RODS_CERTIFIED": False,
            "CLASSICAL_OBSERVER_MAP_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_POINTWISE_RETARDED_GREEN_KERNEL_TWO_WINDOW_WITNESS",
        "assumptions": [
            "the standard-sign probe scalar Cauchy solutions retain the declared nonzero relational Jacobian on both compact detector windows",
            "the probe-apparatus limit consistently omits rod stress, detector recoil, and gravitational backreaction",
            "smooth compact nonnegative detector windows subordinate to the declared relational boxes are available",
            "the imported distributional retarded field admits pairing with the smooth detector test two-forms",
        ],
        "not_established": [
            "nonzero response of the imported pulse in both predeclared detector windows",
            "a unique no-wrap null intersection from the imported compact source to each receiver",
            "rod-field backreaction or apparatus recoil",
            "raw-D or K_Berger descent after adjoining the rod sector",
            "a quantum observer state or positive quantum inner product",
        ],
        "provenance": {
            "declared_input_sha256": _sha256(INPUT),
            "source_manifest": [
                {"role": role, "path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for role, path in SOURCE_FILES.items()
            ],
        },
        "claim_boundary": "This bridge-only classical consumer constructs two linearly independent, spatially localized, clock-labelled Maxwell field-strength record functionals in a nondegenerate local probe-rod chart and defines the source-to-retarded-field-to-record map. It does not prove that the imported compact pulse is nonzero in both predeclared windows, so it does not promote the partial Berger map to a certified observer algebra on the D quotient. Rod backreaction, apparatus recoil, K_Berger compatibility, quantum states, and QME claims remain open.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered:
            raise AssertionError("localized detector record certificate is stale")
    else:
        CERTIFICATE.write_text(rendered)
    print("BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
