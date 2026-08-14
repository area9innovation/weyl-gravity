#!/usr/bin/env python3
"""Independent exact checker for the named H2 weak-wave completion."""
from __future__ import annotations

from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1.json"
SOURCE = ROOT / "foundations/results/FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1.json"
FINITE_TESTS = ROOT / "foundations/results/FOUNDATIONAL_CODED_LOCAL_WEAK_WAVE_TEST_CLASS_V1.json"
DERIVATIVES = [[0, 0], [1, 0], [0, 1], [2, 0], [1, 1], [0, 2]]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def q(value: list[int]) -> Q:
    return Q(value[0], value[1])


def enc(value: Q) -> list[int]:
    return [value.numerator, value.denominator]


def ceil_q(value: Q) -> int:
    return -(-value.numerator // value.denominator)


def ell(value: int) -> int:
    if value < 1:
        raise ArithmeticError(value)
    return (value - 1).bit_length()


def canonical_digest(value: dict[str, Any]) -> str:
    projection = {key: value[key] for key in (
        "rational_test_codes", "named_completion", "state_distribution_map",
        "continuity_bounds", "extension_theorem", "formal_proof", "fixtures",
    )}
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if value is None else value
    source, finite = load(SOURCE), load(FINITE_TESTS)
    errors: list[str] = []
    codes = result.get("rational_test_codes", {})
    if codes.get("derivative_multiindices") != DERIVATIVES or codes.get("countable") is not True:
        errors.append("H2 derivative carrier")
    for token in ("rational polyhedral", "rational coefficients", "global C1", "rational polygon"):
        if token not in " ".join(str(codes.get(key, "")) for key in codes):
            errors.append("test-code vocabulary " + token)
    if codes.get("prior_ten_tests_embedded") != finite.get("result_id"):
        errors.append("finite test embedding")

    completion = result.get("named_completion", {})
    if "4^-i" not in completion.get("name", "") or completion.get("density_status") != "BY_DECLARED_REPRESENTATION":
        errors.append("fast H2 name")
    if "does not" not in completion.get("excluded_inference", "") and "no H2 name" not in completion.get("excluded_inference", ""):
        errors.append("representation exclusion")

    stages = result.get("formal_proof", [])
    expected_ids = [
        "RATIONAL_TEST_CODE", "FINITE_CODE_WEAK_IDENTITY", "NAMED_H2_COMPLETION",
        "ENERGY_TO_SPACETIME_BOUND", "EXPLICIT_RESIDUAL_MODULUS", "WEAK_EXTENSION",
        "REPRESENTATION_BOUNDARY",
    ]
    if [stage.get("id") for stage in stages] != expected_ids:
        errors.append("proof stage identity")
    if [stage.get("base") for stage in stages] != ["PRA", "PRA", "RCA_0", "RCA_0", "RCA_0", "RCA_0", "RCA_0"]:
        errors.append("proof bases")
    seen: set[str] = set()
    for stage in stages:
        if not set(stage.get("depends_on", [])) <= seen:
            errors.append("proof dependency order " + str(stage.get("id")))
        seen.add(str(stage.get("id")))

    source_by_id = {fixture["id"]: fixture for fixture in source.get("fixtures", [])}
    fixtures = result.get("fixtures", [])
    if [fixture.get("id") for fixture in fixtures] != list(source_by_id):
        errors.append("fixture identity")
    modulus_checks = 0
    minimality_checks = 0
    for fixture in fixtures:
        original = source_by_id.get(fixture.get("id"), {})
        energies = [q(value) for value in original.get("chiral_energies", [])]
        if len(energies) != 2:
            errors.append("source energies " + str(fixture.get("id")))
            continue
        right, left = energies
        total = right + left
        expected_factors = {
            "right_transport": max(1, ceil_q(2 * right)),
            "left_transport": max(1, ceil_q(2 * left)),
            "scalar_wave": max(1, ceil_q(4 * total)),
            "state_distribution_pairing": max(1, ceil_q(2 * total)),
        }
        expected_offsets = {name: ell(factor) for name, factor in expected_factors.items()}
        if fixture.get("right_energy") != enc(right) or fixture.get("left_energy") != enc(left) or fixture.get("total_energy") != enc(total):
            errors.append("fixture energy closure " + fixture["id"])
        if fixture.get("integer_continuity_factors") != expected_factors or fixture.get("binary_cutoff_offsets") != expected_offsets:
            errors.append("continuity factor or offset " + fixture["id"])
        for factor in expected_factors.values():
            offset = ell(factor)
            if factor > 2**offset or (offset > 0 and factor <= 2 ** (offset - 1)):
                errors.append("binary cutoff minimality " + fixture["id"])
            minimality_checks += 1
        samples = fixture.get("precision_samples", [])
        if [sample.get("precision") for sample in samples] != list(range(1, 9)):
            errors.append("precision sample identity " + fixture["id"])
        for sample in samples:
            precision = sample.get("precision", 0)
            for name, factor in expected_factors.items():
                cutoff = precision + expected_offsets[name]
                bound = Q(factor, 4**cutoff)
                if sample.get(name + "_index") != cutoff or sample.get(name + "_squared_error_bound") != enc(bound) or bound > Q(1, 4**precision):
                    errors.append("exact modulus " + fixture["id"] + ":" + name + ":" + str(precision))
                modulus_checks += 1

    flags = result.get("claim_flags", {})
    for flag in (
        "rational_h2_test_code_carrier_constructed", "named_h2_test_completion_constructed",
        "explicit_residual_modulus_proved", "weak_solution_extended_to_every_named_h2_test",
        "represented_smooth_tests_covered", "continuous_distributional_state_map_constructed",
        "energy_image_evolution_wellposed",
    ):
        if flags.get(flag) is not True:
            errors.append("positive flag " + flag)
    for flag in (
        "bare_extensional_smooth_tests_uniformly_named", "full_lf_test_topology_reconstructed",
        "uniqueness_among_arbitrary_distributions_proved", "strict_causal_support_proved",
        "green_operator_constructed", "weyl_or_metric_bv_equation_proved",
        "empirical_calibration_proved", "new_lorentzian_claim",
    ):
        if flags.get(flag) is not False:
            errors.append("boundary flag " + flag)

    state_map = result.get("state_distribution_map", {})
    if state_map.get("well_defined_on_names") is not True or "not among every abstract distributional solution" not in state_map.get("uniqueness_scope", ""):
        errors.append("distribution map boundary")
    extension = result.get("extension_theorem", {})
    for key in ("completed_right_transport", "completed_left_transport", "completed_scalar_wave"):
        if "every declared H2 test name" not in extension.get(key, ""):
            errors.append("named extension " + key)
    for token in ("bare extensional", "LF topology", "causal support", "Green"):
        if token not in extension.get("not_covered", ""):
            errors.append("extension boundary " + token)

    pins = {item.get("path"): item.get("sha256") for item in result.get("provenance", {}).get("inputs", [])}
    expected_pins = {
        str(SOURCE.relative_to(ROOT)): hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        str(FINITE_TESTS.relative_to(ROOT)): hashlib.sha256(FINITE_TESTS.read_bytes()).hexdigest(),
    }
    if pins != expected_pins:
        errors.append("source provenance hashes")
    digest = canonical_digest(result)
    if digest != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical digest")
    return errors, {
        "digest": digest,
        "fixtures": len(fixtures),
        "h2_derivatives": len(codes.get("derivative_multiindices", [])),
        "modulus_checks": modulus_checks,
        "cutoff_minimality_checks": minimality_checks,
    }


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
