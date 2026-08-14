#!/usr/bin/env python3
"""Independent exact checker for the model-scoped GR/Cassini assembly."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1.json"
EINSTEIN_SOURCE = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_EINSTEIN_CLASSIFICATION_V1.json"
CONTROL_SOURCE = ROOT / "foundations/standard-gr-observational-control-v1.json"

ALL_OBLIGATIONS = {
    "KINEMATICS_OBSERVABLES", "STATE_EXISTENCE", "STATE_REPRESENTATION",
    "PROBABILITY_RULE", "PHYSICAL_STATE_SELECTION", "GENERATOR_SPECTRAL_DYNAMICS",
    "EVOLUTION_WELLPOSEDNESS", "CAUSAL_PROPAGATION_GREEN", "GAUGE_BV_COHOMOLOGY",
    "INTERACTION_CONSTRUCTION", "COUNTERTERM_CLASSIFICATION", "ANOMALY_CLASSIFICATION",
    "RENORMALIZED_PRODUCTS", "QME_RESTORATION", "RESIDUAL_QUANTUM_TRANSFER",
    "RECONSTRUCTION_LIMITS",
}
REQUIRED = {"KINEMATICS_OBSERVABLES", "INTERACTION_CONSTRUCTION", "RECONSTRUCTION_LIMITS"}
TOUCHED = {"CAUSAL_PROPAGATION_GREEN", "GAUGE_BV_COHOMOLOGY"}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def fraction(value: dict[str, Any]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if value is None else value
    errors: list[str] = []

    if result.get("result_id") != "FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1":
        errors.append("result identity")
    if digest(result) != result.get("canonical_digest"):
        errors.append("canonical digest")

    sources = {item.get("path"): item for item in result.get("provenance", {}).get("inputs", [])}
    for path in (EINSTEIN_SOURCE, CONTROL_SOURCE):
        relative = str(path.relative_to(ROOT))
        item = sources.get(relative)
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if not item or item.get("sha256") != actual:
            errors.append("source pin " + relative)
    einstein = load(EINSTEIN_SOURCE)
    if einstein.get("certificate") != "REVERSE_PHYSICS_EINSTEIN_CLASSIFICATION_V1" or not einstein.get("checks", {}).get("ok"):
        errors.append("Einstein source gate")
    control = load(CONTROL_SOURCE)
    cassini = next((item for item in control.get("records", []) if item.get("id") == "GR_CASSINI_SHAPIRO_2003"), None)
    if cassini is None:
        errors.append("Cassini source record")

    model = result.get("model_identity", {})
    if model.get("id") != "STANDARD_GR_VACUUM_SOLAR_EXTERIOR" or model.get("benchmark") != "SOLAR_SYSTEM" or model.get("comparison_id") != "GR_CASSINI_SHAPIRO_2003":
        errors.append("single model scope")

    exact = result.get("exact_prediction_rail", {})
    field = exact.get("field_equation_derivation", {})
    residuals = field.get("substitution_residuals", {})
    if set(residuals) != {"r_fprime_plus_f_minus_1", "fprime_over_r_plus_half_fsecond"} or any(fraction(item) != 0 for item in residuals.values()):
        errors.append("vacuum equation residuals")
    if field.get("solution") != "f(r)=1-2m/r" or field.get("integration") != "(r f)'=1, hence f=1+C/r; Newtonian normalization fixes C=-2m":
        errors.append("field equation integration")

    # Independent coefficient calculation.  Expand the rational factors by
    # multiplying the proposed coefficient vector back by its denominator.
    iso = exact.get("isotropic_translation", {})
    a = [fraction(item) for item in iso.get("A_coefficients_through_x2", [])]
    b = [fraction(item) for item in iso.get("B_coefficients_through_x2", [])]
    gtt = [fraction(item) for item in iso.get("gtt_coefficients_through_x2", [])]
    denominator = [Fraction(1), Fraction(1), Fraction(1, 4)]
    recovered_numerator = [
        a[0] * denominator[0],
        a[1] * denominator[0] + a[0] * denominator[1],
        a[2] * denominator[0] + a[1] * denominator[1] + a[0] * denominator[2],
    ] if len(a) == 3 else []
    if recovered_numerator != [Fraction(1), Fraction(-1), Fraction(1, 4)]:
        errors.append("independent lapse series identity")
    if b != [Fraction(1), Fraction(2), Fraction(3, 2)] or gtt != [Fraction(-1), Fraction(2), Fraction(-2)] or gtt != [-item for item in a]:
        errors.append("independent isotropic coefficients")

    ppn = exact.get("ppn_identification", {})
    beta = fraction(ppn.get("beta", {"numerator": 0, "denominator": 1}))
    gamma = fraction(ppn.get("gamma", {"numerator": 0, "denominator": 1}))
    gamma_minus_one = fraction(ppn.get("gamma_minus_one", {"numerator": 1, "denominator": 1}))
    if beta != 1 or gamma != 1 or gamma_minus_one != 0 or (len(gtt) == 3 and -gtt[2] / 2 != beta) or (len(b) == 3 and b[1] / 2 != gamma):
        errors.append("independent PPN identification")

    propagation = [fraction(item) for item in exact.get("null_delay", {}).get("sqrt_B_over_A_coefficients_through_x2", [])]
    # Direct first derivative at x=0 of (1+x/2)^3/(1-x/2): 3/2+1/2=2.
    independent_delay_coefficient = Fraction(3, 2) + Fraction(1, 2)
    if len(propagation) < 2 or propagation[:2] != [Fraction(1), independent_delay_coefficient] or fraction(exact["null_delay"]["first_order_delay_coefficient"]) != 1 + gamma:
        errors.append("independent null-delay coefficient")

    empirical = result.get("empirical_comparison_rail", {})
    central = fraction(empirical.get("reported_gamma_minus_one", {"numerator": 0, "denominator": 1}))
    uncertainty = fraction(empirical.get("reported_plus_minus_uncertainty", {"numerator": 1, "denominator": 1}))
    predicted = fraction(empirical.get("exact_prediction_gamma_minus_one", {"numerator": 1, "denominator": 1}))
    band = empirical.get("reported_band", {})
    lower = fraction(band.get("lower", {"numerator": 0, "denominator": 1}))
    upper = fraction(band.get("upper", {"numerator": 0, "denominator": 1}))
    distance = fraction(empirical.get("absolute_standardized_distance", {"numerator": 0, "denominator": 1}))
    if central != Fraction(21, 1_000_000) or uncertainty != Fraction(23, 1_000_000):
        errors.append("Cassini transcription")
    if lower != central - uncertainty or upper != central + uncertainty or predicted != 0 or not lower <= predicted <= upper:
        errors.append("comparison band arithmetic")
    if distance != Fraction(21, 23) or empirical.get("prediction_inside_reported_band") is not True:
        errors.append("comparison distance")

    mask = result.get("applicability_mask", [])
    by_obligation = {item.get("obligation"): item.get("status") for item in mask}
    if set(by_obligation) != ALL_OBLIGATIONS or {key for key, status in by_obligation.items() if status == "IN_SCOPE_REQUIRED"} != REQUIRED or {key for key, status in by_obligation.items() if status == "TOUCHED_NOT_REQUIRED"} != TOUCHED:
        errors.append("applicability partition")
    if any(status not in {"IN_SCOPE_REQUIRED", "TOUCHED_NOT_REQUIRED", "OUT_OF_SCOPE"} for status in by_obligation.values()):
        errors.append("applicability vocabulary")
    summary = result.get("applicability_summary", {})
    if summary != {"total_atlas_obligations": 16, "required": 3, "required_satisfied": 3, "touched_not_required": 2, "out_of_scope": 11}:
        errors.append("applicability summary")

    stages = result.get("stages", [])
    interfaces = result.get("interfaces", [])
    stage_ids = [item.get("id") for item in stages]
    if stage_ids != ["FIELD_EQUATIONS", "EXTERIOR_SOLUTION", "PPN_REDUCTION", "NULL_OBSERVABLE", "CASSINI_PARAMETER_MAP", "EMPIRICAL_COMPARISON"]:
        errors.append("prediction stage closure")
    if len(interfaces) != 5 or any(item.get("from") != stage_ids[index] or item.get("to") != stage_ids[index + 1] for index, item in enumerate(interfaces)):
        errors.append("ordered interface closure")
    if [item.get("status") for item in interfaces] != ["CERTIFIED", "CERTIFIED", "CERTIFIED", "REGISTERED", "REGISTERED"]:
        errors.append("typed interface statuses")

    rails = {item.get("id"): item.get("status") for item in result.get("maturity_rails", [])}
    expected_rails = {
        "MODEL_IDENTITY": "SATISFIED",
        "APPLICABILITY": "SATISFIED",
        "CROSS_STAGE_COMPOSITION": "SATISFIED_WITH_TYPED_BOUNDARY",
        "PREDICTION_DERIVATION": "SATISFIED",
        "OBSERVABLE_IDENTIFICATION": "SATISFIED_WITH_TYPED_BOUNDARY",
        "EMPIRICAL_COMPARISON": "SUPPORTED_IN_DECLARED_SCOPE",
        "ROBUSTNESS_OUT_OF_SAMPLE": "NOT_ASSESSED",
    }
    if rails != expected_rails:
        errors.append("maturity rails")
    disposition = result.get("assembly_disposition", {})
    if disposition != {"status": "BOUNDED_PREDICTION_ASSEMBLY_COMPLETE", "complete_within_declared_scope": True, "empirically_supported_within_declared_scope": True, "complete_theory": False}:
        errors.append("bounded assembly disposition")

    flags = result.get("claim_flags", {})
    for key in (
        "single_model_identity_declared", "applicability_mask_complete",
        "vacuum_field_equation_to_solution_derived", "isotropic_coordinate_translation_exact",
        "ppn_gamma_equals_one_derived_exactly", "null_delay_gamma_plus_one_coefficient_derived",
        "cassini_observable_map_registered", "prediction_inside_reported_band",
        "bounded_prediction_assembly_complete",
    ):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "raw_cassini_data_reanalysed", "cassini_likelihood_reproduced",
        "robustness_out_of_sample_assessed", "all_solar_system_tests_covered",
        "complete_standard_gr_theory_established", "weyl_gravity_empirically_supported",
        "quantum_lifecycle_promoted",
    ):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)

    return errors, {
        "required_obligations": len(REQUIRED),
        "stages": len(stages),
        "interfaces": len(interfaces),
        "exact_interfaces": sum(item.get("status") == "CERTIFIED" for item in interfaces),
        "ppn_gamma": str(gamma),
        "delay_coefficient": str(independent_delay_coefficient),
        "reported_band": [str(lower), str(upper)],
        "standardized_distance": str(distance),
        "bounded_complete": disposition.get("complete_within_declared_scope"),
    }


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
