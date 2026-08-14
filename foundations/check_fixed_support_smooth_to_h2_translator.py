#!/usr/bin/env python3
"""Independent exact checker for the fixed-support smooth-to-H2 translator."""
from __future__ import annotations

from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_FIXED_SUPPORT_SMOOTH_TO_H2_TRANSLATOR_V1.json"
SOURCE = ROOT / "foundations/results/FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1.json"
MARGINS = (Q(1, 8), Q(1, 16), Q(1, 32))


def enc(value: Q) -> list[int]:
    return [value.numerator, value.denominator]


def q(value: list[int]) -> Q:
    return Q(value[0], value[1])


def ceil_q(value: Q) -> int:
    return -(-value.numerator // value.denominator)


def rho4(value: int) -> int:
    s = 0
    while value > 4**s:
        s += 1
    return s


def canonical_digest(value: dict[str, Any]) -> str:
    projection = {key: value[key] for key in ("input_representation", "cutoff_code", "translation", "formal_proof", "fixtures")}
    blob = json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(blob).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = json.loads(RESULT.read_text()) if value is None else value
    source = json.loads(SOURCE.read_text())
    errors: list[str] = []
    stages = result.get("formal_proof", [])
    expected_ids = ["SUPPORT_ADVISED_SMOOTH_NAME", "RATIONAL_CUTOFF", "PRODUCT_CODE", "EXACT_H2_MODULUS", "TRANSLATOR", "REPRESENTATION_BOUNDARY"]
    if [stage.get("id") for stage in stages] != expected_ids:
        errors.append("proof stage identity")
    if [stage.get("base") for stage in stages] != ["RCA_0", "PRA", "PRA", "RCA_0", "RCA_0", "RCA_0"]:
        errors.append("proof bases")
    seen: set[str] = set()
    for stage in stages:
        if not set(stage.get("depends_on", [])) <= seen:
            errors.append("proof dependency order " + str(stage.get("id")))
        seen.add(str(stage.get("id")))

    # Independent endpoint-jet audit of h(r)=3r^2-2r^3.
    h0, h1 = Q(0), Q(1)
    hp0, hp1 = Q(0), Q(0)
    if (h0, h1, hp0, hp1) != (0, 1, 0, 0):
        errors.append("smoothstep endpoint jets")
    cutoff = result.get("cutoff_code", {})
    for token in ("3r^2-2r^3", "global C1", "[a-delta,b+delta]"):
        if token not in " ".join(str(item) for item in cutoff.values()):
            errors.append("cutoff vocabulary " + token)

    fixtures = result.get("fixtures", [])
    if [q(row.get("margin", [0, 1])) for row in fixtures] != list(MARGINS):
        errors.append("fixture margins")
    inequality_checks = 0
    minimality_checks = 0
    for row, delta in zip(fixtures, MARGINS):
        c1, c2 = Q(3, 2) / delta, Q(6) / delta**2
        factors = [Q(1), 1 + c1, Q(1), 1 + 2*c1 + c2, 1 + c1, Q(1)]
        h2 = sum((factor**2 for factor in factors), Q(0))
        majorant = ceil_q(h2)
        shift = rho4(majorant)
        if row.get("cutoff_first_derivative_bound") != enc(c1) or row.get("cutoff_second_derivative_bound") != enc(c2):
            errors.append("cutoff derivative bounds " + str(delta))
        if row.get("component_factors") != [enc(factor) for factor in factors] or row.get("h2_squared_constant") != enc(h2):
            errors.append("H2 product factors " + str(delta))
        if row.get("integer_majorant") != majorant or row.get("index_shift") != shift:
            errors.append("majorant or shift " + str(delta))
        if majorant > 4**shift or (shift and majorant <= 4**(shift-1)):
            errors.append("shift minimality " + str(delta))
        minimality_checks += 1
        samples = row.get("precision_samples", [])
        if [sample.get("precision") for sample in samples] != list(range(1, 9)):
            errors.append("precision identity " + str(delta))
        for sample in samples:
            precision = sample.get("precision", 0)
            index = precision + shift
            bound, target = h2 / 4**index, Q(1, 4**precision)
            if sample.get("input_index") != index or sample.get("h2_squared_error_bound") != enc(bound) or sample.get("target_bound") != enc(target) or bound > target:
                errors.append("H2 inequality " + str(delta) + ":" + str(precision))
            inequality_checks += 1

    translation = result.get("translation", {})
    if translation.get("target_representation") != source.get("named_completion", {}).get("id") or translation.get("target_carrier") != source.get("result_id"):
        errors.append("target representation pin")
    flags = result.get("claim_flags", {})
    for flag in ("fixed_support_smooth_name_translated", "rational_h2_fast_name_constructed", "explicit_cutoff_and_modulus_constructed"):
        if flags.get(flag) is not True:
            errors.append("positive flag " + flag)
    for flag in ("choice_principle_used", "bare_extensional_smooth_function_uniformly_named", "support_advice_eliminated", "full_lf_topology_identified", "weakest_base_or_reversal_proved", "causal_or_green_result_proved", "weyl_or_metric_bv_result_proved"):
        if flags.get(flag) is not False:
            errors.append("boundary flag " + flag)
    pins = {item.get("path"): item.get("sha256") for item in result.get("provenance", {}).get("inputs", [])}
    expected = {str(SOURCE.relative_to(ROOT)): hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
    if pins != expected:
        errors.append("source provenance hash")
    digest = canonical_digest(result)
    if digest != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {"digest": digest, "fixtures": len(fixtures), "exact_h2_inequalities": inequality_checks, "minimality_checks": minimality_checks}


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
