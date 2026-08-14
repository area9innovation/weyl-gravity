#!/usr/bin/env python3
"""Independent exact checker for the support-indexed test-space comparison."""
from __future__ import annotations

from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_SUPPORT_INDEXED_TEST_SPACE_COMPARISON_V1.json"
TRANSLATOR = ROOT / "foundations/results/FOUNDATIONAL_FIXED_SUPPORT_SMOOTH_TO_H2_TRANSLATOR_V1.json"
H2_RESULT = ROOT / "foundations/results/FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1.json"


def q(value: list[int]) -> Q: return Q(value[0], value[1])
def enc(value: Q) -> list[int]: return [value.numerator, value.denominator]


def rho4(value: int) -> int:
    s = 0
    while value > 4**s: s += 1
    return s


def canonical_digest(value: dict[str, Any]) -> str:
    projection = {key: value[key] for key in ("support_exhaustion", "represented_union", "name_comparison", "h2_embedding", "topology_comparison", "formal_proof", "fixtures")}
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = json.loads(RESULT.read_text()) if value is None else value
    translator, h2_result = json.loads(TRANSLATOR.read_text()), json.loads(H2_RESULT.read_text())
    errors: list[str] = []
    stages = result.get("formal_proof", [])
    expected = ["RATIONAL_SUPPORT_EXHAUSTION", "TAGGED_REPRESENTED_UNION", "CONVENTIONAL_NAME_EQUIVALENCE", "STAGEWISE_H2_EMBEDDING", "WEAK_TEST_ASSEMBLY", "LF_TOPOLOGY_BOUNDARY"]
    if [stage.get("id") for stage in stages] != expected: errors.append("proof stage identity")
    if [stage.get("base") for stage in stages] != ["PRA", "RCA_0", "RCA_0", "RCA_0", "RCA_0", "RCA_0"]: errors.append("proof bases")
    seen: set[str] = set()
    for stage in stages:
        if not set(stage.get("depends_on", [])) <= seen: errors.append("proof dependency order " + str(stage.get("id")))
        seen.add(str(stage.get("id")))
    fixtures = result.get("fixtures", [])
    if [row.get("index") for row in fixtures] != list(range(6)): errors.append("fixture indices")
    name_roundtrips = 0
    for index, row in enumerate(fixtures):
        left = Q(1, 2**(index+2)); right = 1-left; next_left = left/2; delta = left/2
        if row.get("support_stage") != [enc(left), enc(right)] or row.get("collar_stage") != [enc(next_left), enc(1-next_left)] or row.get("collar_width") != enc(delta):
            errors.append("support stage " + str(index))
        c1, c2 = Q(3, 2)/delta, Q(6)/delta**2
        factors = [Q(1),1+c1,Q(1),1+2*c1+c2,1+c1,Q(1)]
        constant = sum((item**2 for item in factors), Q(0)); majorant = -(-constant.numerator//constant.denominator)
        if row.get("translator_integer_majorant") != majorant or row.get("translator_index_shift") != rho4(majorant):
            errors.append("translator shift " + str(index))
        sample = row.get("sample_name", {})
        conventional, tagged = sample.get("conventional", {}), sample.get("tagged_union", [])
        if tagged != [conventional.get("support_bound"), conventional.get("smooth_name")] or sample.get("roundtrip_exact") is not True:
            errors.append("name roundtrip " + str(index))
        name_roundtrips += 1
    inclusions = result.get("inclusion_checks", [])
    expected_pairs = [(i,j) for i in range(6) for j in range(i+1,6)]
    if [(row.get("from"),row.get("to")) for row in inclusions] != expected_pairs: errors.append("inclusion pair closure")
    for row in inclusions:
        if row.get("nested") is not True or row.get("h2_images_equivalent") is not True: errors.append("inclusion assertion")
    h2_embedding = result.get("h2_embedding", {})
    if h2_embedding.get("stage_map") != translator.get("result_id") or h2_embedding.get("target") != h2_result.get("named_completion", {}).get("id") or h2_embedding.get("surjectivity_onto_h2_completion") is not False:
        errors.append("H2 embedding boundary")
    topology = result.get("topology_comparison", {})
    if topology.get("full_lf_topology_identification") != "NOT_ESTABLISHED" or topology.get("single_h2_metric_completion_identification") != "EXCLUDED": errors.append("LF topology boundary")
    flags = result.get("claim_flags", {})
    for flag in ("support_indexed_represented_union_constructed", "conventional_and_tagged_names_equivalent", "stage_inclusion_compatibility_proved", "every_represented_smooth_test_embedded_in_h2", "weak_identity_assembled_over_named_tests"):
        if flags.get(flag) is not True: errors.append("positive flag " + flag)
    for flag in ("choice_principle_used", "uniform_support_bound_selected_from_bare_function", "h2_embedding_surjective", "full_lf_locally_convex_topology_identified", "single_metric_completion_of_test_space_constructed", "weyl_or_metric_bv_result_proved"):
        if flags.get(flag) is not False: errors.append("boundary flag " + flag)
    pins = {item.get("path"): item.get("sha256") for item in result.get("provenance", {}).get("inputs", [])}
    expected_pins = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (TRANSLATOR,H2_RESULT)}
    if pins != expected_pins: errors.append("source provenance hashes")
    digest = canonical_digest(result)
    if digest != result.get("independent_checker", {}).get("expected_digest"): errors.append("canonical digest")
    return errors, {"digest": digest, "support_stages": len(fixtures), "name_roundtrips": name_roundtrips, "inclusion_checks": len(inclusions)}


def main() -> int:
    errors, summary = check(); print(json.dumps({"status":"PASS" if not errors else "FAIL","errors":errors,**summary},sort_keys=True)); return bool(errors)


if __name__ == "__main__": raise SystemExit(main())
