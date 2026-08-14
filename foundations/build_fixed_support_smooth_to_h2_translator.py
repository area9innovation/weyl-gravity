#!/usr/bin/env python3
"""Generate the fixed-support smooth-name to rational H2-code translator."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "foundations/results/FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1.json"
OUTPUT = ROOT / "foundations/results/FOUNDATIONAL_FIXED_SUPPORT_SMOOTH_TO_H2_TRANSLATOR_V1.json"
REPORT = ROOT / "foundations/reports/fixed-support-smooth-to-h2-translator-v1.md"
MARGINS = (Q(1, 8), Q(1, 16), Q(1, 32))


def enc(value: Q) -> list[int]:
    return [value.numerator, value.denominator]


def ceil_q(value: Q) -> int:
    return -(-value.numerator // value.denominator)


def rho4(value: int) -> int:
    """Least s with value <= 4**s."""
    if value < 1:
        raise ValueError(value)
    s = 0
    while value > 4**s:
        s += 1
    return s


def fixture(delta: Q) -> dict[str, Any]:
    c1 = Q(3, 2) / delta
    c2 = Q(6) / (delta * delta)
    factors = [Q(1), 1 + c1, Q(1), 1 + 2 * c1 + c2, 1 + c1, Q(1)]
    h2_constant = sum((value * value for value in factors), Q(0))
    integer_constant = ceil_q(h2_constant)
    shift = rho4(integer_constant)
    samples = []
    for precision in range(1, 9):
        input_index = precision + shift
        bound = h2_constant / 4**input_index
        samples.append({
            "precision": precision,
            "input_index": input_index,
            "h2_squared_error_bound": enc(bound),
            "target_bound": enc(Q(1, 4**precision)),
        })
    return {
        "margin": enc(delta),
        "cutoff_first_derivative_bound": enc(c1),
        "cutoff_second_derivative_bound": enc(c2),
        "component_factors": [enc(value) for value in factors],
        "h2_squared_constant": enc(h2_constant),
        "integer_majorant": integer_constant,
        "index_shift": shift,
        "precision_samples": samples,
    }


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: dict[str, Any]) -> str:
    projection = {key: value[key] for key in (
        "input_representation", "cutoff_code", "translation", "formal_proof", "fixtures",
    )}
    blob = json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(blob).hexdigest()


def build() -> dict[str, Any]:
    source = json.loads(SOURCE.read_text())
    proof = [
        {"id": "SUPPORT_ADVISED_SMOOTH_NAME", "base": "RCA_0", "statement": "Input consists of rational a<b and delta>0 with [a-delta,b+delta] inside the unit slab, together with rational periodic C2 approximant codes p_m satisfying the supplied uniform derivative bound max over |alpha|<=2 of ||D^alpha(p_m-phi)||_infinity <= 2^-m and supp(phi) contained in [a,b] times the circle."},
        {"id": "RATIONAL_CUTOFF", "base": "PRA", "depends_on": ["SUPPORT_ADVISED_SMOOTH_NAME"], "statement": "The cubic smoothstep h(r)=3r^2-2r^3 on each rational collar defines a rational global-C1 piecewise-polynomial cutoff chi, equal to one on [a,b] and zero outside [a-delta,b+delta], with |chi'|<=3/(2 delta) and |chi''|<=6/delta^2."},
        {"id": "PRODUCT_CODE", "base": "PRA", "depends_on": ["RATIONAL_CUTOFF"], "statement": "For q_n=chi p_(n+s), finite rational polynomial multiplication and partition refinement produce a rational periodic compact-time C1 piecewise-polynomial H2 test code in the prior carrier."},
        {"id": "EXACT_H2_MODULUS", "base": "RCA_0", "depends_on": ["PRODUCT_CODE"], "statement": "The six product-rule factors for derivatives 1,t,x,tt,tx,xx are 1, 1+C1, 1, 1+2C1+C2, 1+C1, 1. Their squared sum C_H2 bounds ||q_n-phi||_H2^2 by C_H2 4^-(n+s). Taking A=ceil(C_H2) and the least s with A<=4^s yields the fast bound 4^-n."},
        {"id": "TRANSLATOR", "base": "RCA_0", "depends_on": ["EXACT_H2_MODULUS"], "statement": "The map from the support-advised derivative name to the sequence q_n is uniform and supplies a valid name in the declared rational H2 completion. No choice principle selects support or a convergence modulus because both are components of the input name."},
        {"id": "REPRESENTATION_BOUNDARY", "base": "RCA_0", "depends_on": ["TRANSLATOR"], "statement": "This is a translator between two declared representations. It does not turn a bare extensional smooth function into a name, identify the unrestricted LF topology, or prove a weakest-base reversal."},
    ]
    value: dict[str, Any] = {
        "schema_version": "foundational-fixed-support-smooth-to-h2-translator-v1",
        "result_id": "FOUNDATIONAL_FIXED_SUPPORT_SMOOTH_TO_H2_TRANSLATOR_V1",
        "result_kind": "REPRESENTATION_TRANSLATOR_WITH_EXPLICIT_SUPPORT_AND_MODULUS",
        "lifecycle": "CERTIFIED",
        "created": "2026-08-14",
        "repository_base_commit": "8d2ceae41e73b748f4f6ca53277423e82697a29c",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "theorem": "Over RCA_0, every periodic smooth test on the unit cylinder carrying rational fixed-support advice and a supplied uniform derivative approximation rate through order two translates uniformly into the rational compact-time H2 test-code completion, with an explicit primitive-recursive index shift and without an application of choice.",
        "input_representation": {
            "id": "FIXED_SUPPORT_SMOOTH_DERIVATIVE_NAME_V1",
            "support_advice": "rationals a<b and delta>0, with support(phi) inside [a,b]x(R/Z) and [a-delta,b+delta] inside (0,1)",
            "approximants": "rational periodic C2 piecewise-polynomial codes p_m",
            "rate": "max_{|alpha|<=2} ||D^alpha(p_m-phi)||_infinity <= 2^-m",
            "advice_is_input": True,
            "bare_extensional_function_is_not_input": True,
        },
        "cutoff_code": {
            "smoothstep": "h(r)=3r^2-2r^3 for 0<=r<=1",
            "left_collar": "chi(t)=h((t-a+delta)/delta) on [a-delta,a]",
            "core": "chi(t)=1 on [a,b]",
            "right_collar": "chi(t)=h((b+delta-t)/delta) on [b,b+delta]",
            "outside": "chi(t)=0 outside [a-delta,b+delta]",
            "regularity": "global C1 and rational piecewise cubic",
            "support_preserved": True,
        },
        "translation": {
            "formula": "q_n=chi p_(n+s)",
            "target_representation": source["named_completion"]["id"],
            "target_carrier": source["result_id"],
            "h2_derivative_order": [[0, 0], [1, 0], [0, 1], [2, 0], [1, 1], [0, 2]],
            "constant_rule": "C1=3/(2 delta), C2=6/delta^2, C_H2=sum of squares of [1,1+C1,1,1+2C1+C2,1+C1,1]",
            "shift_rule": "A=ceil(C_H2); s is least natural with A<=4^s",
            "fast_bound": "||q_n-phi||_H2^2<=C_H2 4^-(n+s)<=4^-n",
            "choice_use": "NONE: support collar and derivative modulus are supplied name data",
        },
        "formal_proof": proof,
        "fixtures": [fixture(delta) for delta in MARGINS],
        "literature_context": [
            {"id": "pauly-steinberg-2018-representations", "citation": "Arno Pauly and Florian Steinberg, Comparing Representations for Function Spaces in Computable Analysis, Theory of Computing Systems 62 (2018), 557-582", "doi": "10.1007/s00224-016-9745-6", "url": "https://doi.org/10.1007/s00224-016-9745-6", "role": "Context for support advice and representation-sensitive function spaces.", "import_boundary": "The paper does not supply this exact cutoff or RCA_0 modulus certificate."},
            {"id": "van-schaftingen-2014-sobolev-interpolation", "citation": "Jean Van Schaftingen, Approximation in Sobolev spaces by piecewise affine interpolation, Journal of Mathematical Analysis and Applications 420 (2014), 40-47", "doi": "10.1016/j.jmaa.2014.05.036", "url": "https://doi.org/10.1016/j.jmaa.2014.05.036", "role": "Classical context for direct piecewise-polynomial Sobolev approximation.", "import_boundary": "No uniform name constructor or reverse-mathematical calibration is imported."},
        ],
        "provenance": {"inputs": [{"path": str(SOURCE.relative_to(ROOT)), "sha256": sha(SOURCE), "role": "target H2 representation and carrier"}]},
        "independent_checker": {"path": "foundations/check_fixed_support_smooth_to_h2_translator.py", "checks": ["proof DAG", "cubic cutoff endpoint jets", "three exact rational collars", "six product-rule factors", "minimal base-four shifts", "24 exact H2 inequalities", "source hash", "canonical digest"], "expected_digest": ""},
        "claim_flags": {
            "fixed_support_smooth_name_translated": True,
            "rational_h2_fast_name_constructed": True,
            "explicit_cutoff_and_modulus_constructed": True,
            "choice_principle_used": False,
            "bare_extensional_smooth_function_uniformly_named": False,
            "support_advice_eliminated": False,
            "full_lf_topology_identified": False,
            "weakest_base_or_reversal_proved": False,
            "causal_or_green_result_proved": False,
            "weyl_or_metric_bv_result_proved": False,
        },
        "does_not_establish": [
            "a name for a bare extensional smooth function without support and rate advice",
            "a uniform selection of compact support bounds",
            "the unrestricted LF topology of compactly supported smooth tests",
            "a weakest-base reversal or equivalence",
            "strict causal support or an advanced or retarded Green operator",
            "a variable-coefficient, curved-spacetime, Weyl, or metric-BV theorem",
        ],
        "next_gate": "Assemble the fixed-support translators over an explicit support index and compare the resulting represented union with the conventional LF test-function space without conflating sequential names with the full nonmetrizable topology.",
        "human_report": "foundations/reports/fixed-support-smooth-to-h2-translator-v1.md",
    }
    value["independent_checker"]["expected_digest"] = canonical_digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    lines = [
        "# Fixed-support smooth-name to rational H2 translator", "",
        f"**Result:** `{value['result_id']}`", "", "## Certified statement", "", value["theorem"], "",
        "## What the translator consumes", "",
        "The input is not an unnamed smooth function. It includes a rational support interval, a rational collar, rational periodic approximants, and the rate `2^-m` simultaneously controlling every derivative through order two.", "",
        "## Exact construction", "", "```text", "h(r) = 3r^2 - 2r^3", "q_n = chi p_(n+s)", "A = ceil(C_H2),  s = least integer with A <= 4^s", "||q_n-phi||_H2^2 <= 4^-n", "```", "",
        "| collar delta | C1 | C2 | integer A | shift s |", "|---:|---:|---:|---:|---:|",
    ]
    for row in value["fixtures"]:
        c1, c2 = row["cutoff_first_derivative_bound"], row["cutoff_second_derivative_bound"]
        lines.append(f"| {row['margin'][0]}/{row['margin'][1]} | {c1[0]}/{c1[1]} | {c2[0]}/{c2[1]} | {row['integer_majorant']} | {row['index_shift']} |")
    lines += [
        "", "## Logical reading", "",
        "No choice principle is used by this translation: the support collar and convergence rate are fields of the input name. Removing those fields is a different mathematical problem, not a harmless change of notation.", "",
        "## Reproduction", "", "```text",
        "python3 foundations/build_fixed_support_smooth_to_h2_translator.py --check",
        "python3 foundations/check_fixed_support_smooth_to_h2_translator.py",
        "python3 foundations/verify_fixed_support_smooth_to_h2_translator.py",
        "python3 -m unittest foundations.tests.test_fixed_support_smooth_to_h2_translator",
        "```", "", "## Boundaries", "",
    ]
    lines += ["- This does not establish " + item + "." for item in value["does_not_establish"]]
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_bytes, report_bytes = generated()
    outputs = ((OUTPUT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_FIXED_SUPPORT_SMOOTH_TO_H2_TRANSLATOR_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_FIXED_SUPPORT_SMOOTH_TO_H2_TRANSLATOR_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
