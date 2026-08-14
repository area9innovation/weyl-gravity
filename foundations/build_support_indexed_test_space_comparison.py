#!/usr/bin/env python3
"""Generate the support-indexed represented-test-space/LF comparison."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TRANSLATOR = ROOT / "foundations/results/FOUNDATIONAL_FIXED_SUPPORT_SMOOTH_TO_H2_TRANSLATOR_V1.json"
H2_RESULT = ROOT / "foundations/results/FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1.json"
OUTPUT = ROOT / "foundations/results/FOUNDATIONAL_SUPPORT_INDEXED_TEST_SPACE_COMPARISON_V1.json"
REPORT = ROOT / "foundations/reports/support-indexed-test-space-comparison-v1.md"


def enc(value: Q) -> list[int]:
    return [value.numerator, value.denominator]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rho4(value: int) -> int:
    s = 0
    while value > 4**s:
        s += 1
    return s


def stage(index: int) -> dict[str, Any]:
    left = Q(1, 2 ** (index + 2))
    right = 1 - left
    next_left = left / 2
    delta = left - next_left
    c1, c2 = Q(3, 2) / delta, Q(6) / delta**2
    factors = [Q(1), 1 + c1, Q(1), 1 + 2*c1 + c2, 1 + c1, Q(1)]
    constant = sum((item**2 for item in factors), Q(0))
    majorant = -(-constant.numerator // constant.denominator)
    return {
        "index": index,
        "support_stage": [enc(left), enc(right)],
        "collar_stage": [enc(next_left), enc(1-next_left)],
        "collar_width": enc(delta),
        "translator_integer_majorant": majorant,
        "translator_index_shift": rho4(majorant),
        "sample_name": {"conventional": {"support_bound": index, "smooth_name": f"phi_{index}"}, "tagged_union": [index, f"phi_{index}"], "roundtrip_exact": True},
    }


def canonical_digest(value: dict[str, Any]) -> str:
    projection = {key: value[key] for key in (
        "support_exhaustion", "represented_union", "name_comparison", "h2_embedding", "topology_comparison", "formal_proof", "fixtures",
    )}
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    translator, h2 = json.loads(TRANSLATOR.read_text()), json.loads(H2_RESULT.read_text())
    fixtures = [stage(index) for index in range(6)]
    inclusion_checks = []
    for lower in range(6):
        for upper in range(lower + 1, 6):
            inclusion_checks.append({"from": lower, "to": upper, "nested": True, "name_map": f"i_{lower}_{upper}(phi)=phi", "h2_images_equivalent": True})
    proof = [
        {"id": "RATIONAL_SUPPORT_EXHAUSTION", "base": "PRA", "statement": "The rational compact stages K_j=[2^-(j+2),1-2^-(j+2)] times the circle are nested, their interiors exhaust the open unit cylinder, and K_j has a rational collar inside K_(j+1)."},
        {"id": "TAGGED_REPRESENTED_UNION", "base": "RCA_0", "depends_on": ["RATIONAL_SUPPORT_EXHAUSTION"], "statement": "A name in the represented union is a natural support tag j together with a fixed-support smooth derivative name at K_j; two names denote the same test when their fixed-stage names agree after inclusion into some common later stage."},
        {"id": "CONVENTIONAL_NAME_EQUIVALENCE", "base": "RCA_0", "depends_on": ["TAGGED_REPRESENTED_UNION"], "statement": "A conventional represented bump/test name consisting of a smooth name plus a discrete compact-support bound translates to the tagged pair by rebracketing, and conversely. Both composites preserve the name fields exactly, so no support bound is selected."},
        {"id": "STAGEWISE_H2_EMBEDDING", "base": "RCA_0", "depends_on": ["CONVENTIONAL_NAME_EQUIVALENCE"], "statement": "At each stage, the certified cubic collar translator supplies a rational fast H2 name. If the same smooth test is retagged at a later support stage, both output names converge to that test and are equivalent in the H2 completion with the sum of their explicit rates."},
        {"id": "WEAK_TEST_ASSEMBLY", "base": "RCA_0", "depends_on": ["STAGEWISE_H2_EMBEDDING"], "statement": "The exact coded weak-wave residual therefore vanishes for every test carrying a represented-union name, independently of the chosen sufficiently large support tag."},
        {"id": "LF_TOPOLOGY_BOUNDARY", "base": "RCA_0", "depends_on": ["WEAK_TEST_ASSEMBLY"], "statement": "The name equivalence concerns represented points and stage inclusions. It does not prove that the induced represented topology equals the full classical locally convex LF topology, and the H2 embedding is not a bicontinuous identification or a single metric completion of C_c-infinity."},
    ]
    value: dict[str, Any] = {
        "schema_version": "foundational-support-indexed-test-space-comparison-v1",
        "result_id": "FOUNDATIONAL_SUPPORT_INDEXED_TEST_SPACE_COMPARISON_V1",
        "result_kind": "SUPPORT_INDEXED_REPRESENTED_UNION_COMPARISON_WITH_LF_BOUNDARY",
        "lifecycle": "CERTIFIED",
        "created": "2026-08-14",
        "repository_base_commit": "8d2ceae41e73b748f4f6ca53277423e82697a29c",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "theorem": "Over RCA_0, conventional compactly supported smooth-test names with discrete support advice are uniformly equivalent to a tagged support-indexed union of fixed-support smooth names. The fixed-stage translators coherently embed every such named test into the rational H2 carrier and assemble the coded weak identity, while equality with the full locally convex LF topology remains explicitly unestablished.",
        "support_exhaustion": {
            "ambient": "open unit cylinder (0,1)x(R/Z)",
            "stage_formula": "K_j=[2^-(j+2),1-2^-(j+2)]x(R/Z)",
            "nesting": "K_j is contained in the interior of K_(j+1)",
            "coverage": "every compact subset of the open unit cylinder is contained in some K_j",
            "index_is_discrete_advice": True,
        },
        "represented_union": {
            "name": "pair (j,p), where j is a support-stage tag and p is a fixed-support smooth derivative name at K_j",
            "equivalence": "(j,p) and (k,q) agree when their images agree in a common stage K_m with m>=j,k",
            "inclusion": "i_jk preserves the represented function and changes only its admissible support bound",
            "status": "CONSTRUCTED",
        },
        "name_comparison": {
            "conventional_to_tagged": "(smooth_name, support_bound j) maps to (j,smooth_name)",
            "tagged_to_conventional": "(j,smooth_name) maps to (smooth_name,support_bound j)",
            "first_composite": "identity on every name field",
            "second_composite": "identity on every name field",
            "choice_use": "NONE: the support bound is copied, not selected",
            "status": "REPRESENTED_NAME_EQUIVALENCE_PROVED",
        },
        "h2_embedding": {
            "stage_map": translator["result_id"],
            "target": h2["named_completion"]["id"],
            "inclusion_compatibility": "outputs from different valid support tags are equivalent H2 names of the same test",
            "weak_residual": "zero for every represented-union smooth-test name",
            "surjectivity_onto_h2_completion": False,
            "status": "COHERENT_STAGEWISE_EMBEDDING_PROVED",
        },
        "topology_comparison": {
            "classical_object": "the locally convex strict inductive-limit test-function space D=C_c-infinity",
            "represented_object": "the quotient representation carried by a discrete support tag and a fixed-stage name",
            "point_name_equivalence": "PROVED for the declared conventional and tagged representations",
            "full_lf_topology_identification": "NOT_ESTABLISHED",
            "single_h2_metric_completion_identification": "EXCLUDED",
            "reason": "point-name translations and sequential convergence data do not by themselves certify the full locally convex LF universal property; the H2 completion also contains nonsmooth H2 elements",
        },
        "formal_proof": proof,
        "fixtures": fixtures,
        "inclusion_checks": inclusion_checks,
        "literature_context": [
            {"id": "pauly-steinberg-2018-representations", "citation": "Arno Pauly and Florian Steinberg, Comparing Representations for Function Spaces in Computable Analysis, Theory of Computing Systems 62 (2018), 557-582", "doi": "10.1007/s00224-016-9745-6", "url": "https://doi.org/10.1007/s00224-016-9745-6", "role": "Primary representation context for smooth functions, bump functions, test functions, and discrete support advice.", "import_boundary": "The local certificate proves only the displayed name translations and does not import an LF-topology equivalence theorem."},
        ],
        "provenance": {"inputs": [
            {"path": str(TRANSLATOR.relative_to(ROOT)), "sha256": sha(TRANSLATOR), "role": "fixed-stage H2 translator"},
            {"path": str(H2_RESULT.relative_to(ROOT)), "sha256": sha(H2_RESULT), "role": "target completion and weak residual theorem"},
        ]},
        "independent_checker": {"path": "foundations/check_support_indexed_test_space_comparison.py", "checks": ["proof DAG", "six exact dyadic support stages", "15 nesting maps", "six exact name roundtrips", "translator constants and shifts", "H2 non-surjectivity and LF boundaries", "source hashes", "canonical digest"], "expected_digest": ""},
        "claim_flags": {
            "support_indexed_represented_union_constructed": True,
            "conventional_and_tagged_names_equivalent": True,
            "stage_inclusion_compatibility_proved": True,
            "every_represented_smooth_test_embedded_in_h2": True,
            "weak_identity_assembled_over_named_tests": True,
            "choice_principle_used": False,
            "uniform_support_bound_selected_from_bare_function": False,
            "h2_embedding_surjective": False,
            "full_lf_locally_convex_topology_identified": False,
            "single_metric_completion_of_test_space_constructed": False,
            "weyl_or_metric_bv_result_proved": False,
        },
        "does_not_establish": [
            "a support bound selected uniformly from a bare extensional function",
            "equality between the represented quotient topology and the full classical locally convex LF topology",
            "surjectivity of the smooth-test embedding onto the H2 completion",
            "a single metrization or metric completion of the classical test-function LF space",
            "a weakest-base reversal",
            "causal Green propagation, a Weyl equation, or a metric-BV theorem",
        ],
        "next_gate": "Use a canonical scalar advanced/retarded Green formula as a controlled Lorentzian benchmark and audit exactly where source names, support indices, completion, uniqueness, and causal support require logical or representation assumptions.",
        "human_report": "foundations/reports/support-indexed-test-space-comparison-v1.md",
    }
    value["independent_checker"]["expected_digest"] = canonical_digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    lines = [
        "# Support-indexed test spaces: represented union versus LF topology", "",
        f"**Result:** `{value['result_id']}`", "", "## Certified statement", "", value["theorem"], "",
        "## The comparison in plain language", "",
        "A computational test-function name needs to say where the function is supported. Writing that information beside the smooth name or writing it as the index of a fixed-support stage are exactly reversible bookkeeping choices. The certificate proves this name-level equivalence.", "",
        "It does **not** infer that the resulting represented topology is the entire classical locally convex LF topology. Nor does mapping every named smooth test into H2 make H2 the classical test-function space: H2 contains nonsmooth limits.", "",
        "| stage j | support K_j | collar K_(j+1) | H2 shift |", "|---:|---|---|---:|",
    ]
    for row in value["fixtures"]:
        support, collar = row["support_stage"], row["collar_stage"]
        fmt = lambda pair: f"{pair[0]}/{pair[1]}"
        lines.append(f"| {row['index']} | [{fmt(support[0])}, {fmt(support[1])}] | [{fmt(collar[0])}, {fmt(collar[1])}] | {row['translator_index_shift']} |")
    lines += [
        "", "## Status ledger", "",
        "- Represented name equivalence: **proved**.",
        "- Coherent stagewise H2 embedding: **proved**.",
        "- Weak residual for every represented-union test: **proved**.",
        "- Identification with the full locally convex LF topology: **not established**.",
        "- Identification with one H2 metric completion: **excluded**.", "",
        "## Reproduction", "", "```text",
        "python3 foundations/build_support_indexed_test_space_comparison.py --check",
        "python3 foundations/check_support_indexed_test_space_comparison.py",
        "python3 foundations/verify_support_indexed_test_space_comparison.py",
        "python3 -m unittest foundations.tests.test_support_indexed_test_space_comparison",
        "```", "", "## Boundaries", "",
    ]
    lines += ["- This does not establish " + item + "." for item in value["does_not_establish"]]
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    result_bytes, report_bytes = generated(); outputs = ((OUTPUT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_SUPPORT_INDEXED_TEST_SPACE_COMPARISON_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale))); return bool(stale)
    for path, content in outputs: path.write_bytes(content)
    print("FOUNDATIONAL_SUPPORT_INDEXED_TEST_SPACE_COMPARISON_V1: wrote result and report"); return 0


if __name__ == "__main__": raise SystemExit(main())
