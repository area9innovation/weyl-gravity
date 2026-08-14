#!/usr/bin/env python3
"""Generate the exact coded-wave observable reconstruction certificate."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "foundations/results/FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1.json"
OUTPUT = ROOT / "foundations/results/FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1.json"
REPORT = ROOT / "foundations/reports/coded-wave-observable-reconstruction-v1.md"

OBSERVABLE = {
    "id": "PERIODIC_TENT_SMEARED_CHIRAL_AMPLITUDE",
    "test_breaks": [[0, 1], [1, 2], [1, 1]],
    "test_values": [[0, 1], [1, 1], [0, 1]],
    "test_l2_squared": [1, 3],
    "formula": "O_h(t;p)=integral_0^1 h(x)[T_t a(x)+T_-t b(x)] dx",
    "operational_reading": "A bounded spatially smeared amplitude of the two chiral wave components; h is a declared detector profile, not a probability rule.",
}
PRECISIONS = list(range(1, 7))
ANCHOR_PHASES = [Q(0), Q(1, 4), Q(1, 2), Q(3, 4)]


def q(value: list[int]) -> Q:
    return Q(value[0], value[1])


def enc(value: Q) -> list[int]:
    return [value.numerator, value.denominator]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def step_value(breaks: list[Q], values: list[Q], x: Q) -> Q:
    x %= 1
    for index, (left, right) in enumerate(zip(breaks, breaks[1:])):
        if left <= x < right:
            return values[index]
    raise ValueError(x)


def translate_step(breaks: list[Q], values: list[Q], shift: Q) -> tuple[list[Q], list[Q]]:
    shift %= 1
    translated_breaks = sorted({Q(0), Q(1), *((point + shift) % 1 for point in breaks[:-1])})
    translated_values = [step_value(breaks, values, (left + right) / 2 - shift) for left, right in zip(translated_breaks, translated_breaks[1:])]
    return translated_breaks, translated_values


def polygonal_value(breaks: list[Q], values: list[Q], x: Q) -> Q:
    if x == 1:
        return values[-1]
    x %= 1
    for index, (left, right) in enumerate(zip(breaks, breaks[1:])):
        if left <= x < right:
            weight = (x - left) / (right - left)
            return values[index] + weight * (values[index + 1] - values[index])
    raise ValueError(x)


def integrate_polygonal_times_step(test_breaks: list[Q], test_values: list[Q], step: tuple[list[Q], list[Q]]) -> Q:
    breaks = sorted(set(test_breaks + step[0]))
    total = Q(0)
    for left, right in zip(breaks, breaks[1:]):
        constant = step_value(step[0], step[1], (left + right) / 2)
        test_integral = (right - left) * (polygonal_value(test_breaks, test_values, left) + polygonal_value(test_breaks, test_values, right)) / 2
        total += constant * test_integral
    return total


def observable_value(item: dict[str, Any], time: Q) -> Q:
    breaks = [q(value) for value in item["breaks"]]
    right = [q(value) for value in item["right"]]
    left = [q(value) for value in item["left"]]
    test_breaks = [q(value) for value in OBSERVABLE["test_breaks"]]
    test_values = [q(value) for value in OBSERVABLE["test_values"]]
    return integrate_polygonal_times_step(test_breaks, test_values, translate_step(breaks, right, time)) + integrate_polygonal_times_step(test_breaks, test_values, translate_step(breaks, left, -time))


def l1_norm(breaks: list[Q], values: list[Q]) -> Q:
    return sum(((right - left) * abs(value) for left, right, value in zip(breaks, breaks[1:], values)), Q(0))


def lipschitz_constant(breaks: list[Q], values: list[Q]) -> Q:
    return max((abs((right_value - left_value) / (right - left)) for left, right, left_value, right_value in zip(breaks, breaks[1:], values, values[1:])), default=Q(0))


def binary_ceiling_exponent(value: Q) -> int:
    exponent = 0
    bound = Q(1)
    while value > bound:
        bound *= 2
        exponent += 1
    return exponent


def samples(item: dict[str, Any], cutoff: int) -> list[Q]:
    denominator = 2 ** cutoff
    return [observable_value(item, Q(index, denominator)) for index in range(denominator + 1)]


def sample_digest(values: list[Q]) -> str:
    return hashlib.sha256(json.dumps([enc(value) for value in values], separators=(",", ":")).encode()).hexdigest()


def fixture_record(item: dict[str, Any]) -> dict[str, Any]:
    breaks = [q(value) for value in item["breaks"]]
    right = [q(value) for value in item["right"]]
    left = [q(value) for value in item["left"]]
    test_breaks = [q(value) for value in OBSERVABLE["test_breaks"]]
    test_values = [q(value) for value in OBSERVABLE["test_values"]]
    test_lipschitz = lipschitz_constant(test_breaks, test_values)
    component_l1 = [l1_norm(breaks, right), l1_norm(breaks, left)]
    observable_lipschitz = test_lipschitz * sum(component_l1, Q(0))
    binary_exponent = binary_ceiling_exponent(observable_lipschitz)
    rows = []
    for precision in PRECISIONS:
        cutoff = precision + binary_exponent + 1
        values = samples(item, cutoff)
        rows.append({
            "precision": precision,
            "cutoff_index": cutoff,
            "grid_intervals": 2 ** cutoff,
            "sample_count": len(values),
            "uniform_error_bound": enc(observable_lipschitz / (2 ** cutoff)),
            "requested_tolerance": enc(Q(1, 2 ** precision)),
            "sample_sha256": sample_digest(values),
        })
    return {
        "id": item["id"],
        "source_state": {key: item[key] for key in ("breaks", "right", "left")},
        "component_l1_norms": [enc(value) for value in component_l1],
        "test_lipschitz_constant": enc(test_lipschitz),
        "observable_lipschitz_constant": enc(observable_lipschitz),
        "binary_ceiling_exponent": binary_exponent,
        "cutoff_formula": f"N(k)=k+{binary_exponent + 1}",
        "anchor_values": [{"phase": enc(phase), "value": enc(observable_value(item, phase))} for phase in ANCHOR_PHASES],
        "approximants": rows,
    }


def canonical_digest(result: dict[str, Any]) -> str:
    projection = {key: result[key] for key in ("theorem", "declared_observable", "finite_approximant", "cutoff_theorem", "formal_proof", "fixtures")}
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    source = json.loads(SOURCE.read_text())
    fixtures = [fixture_record(item) for item in source["fixtures"]]
    proof = [
        {"id": "EXACT_RATIONAL_SAMPLES", "base": "PRA", "statement": "For a rational step-pair p, rational periodic polygonal detector h, and dyadic q, the translated partition and O_h(q;p) are finite rational data computable by bounded exact arithmetic."},
        {"id": "BOUNDED_LINEAR_OBSERVABLE", "base": "RCA_0", "depends_on": ["EXACT_RATIONAL_SAMPLES"], "statement": "Cauchy-Schwarz gives |O_h(t;p)-O_h(t;p')|^2<=2 norm_2(h)^2 d(p,p')^2. Thus the rational smeared functional is linear and extends uniquely and boundedly to the coded energy completion."},
        {"id": "OBSERVABLE_LIPSCHITZ_BOUND", "base": "PRA", "depends_on": ["EXACT_RATIONAL_SAMPLES"], "statement": "With K=Lip(h)(norm_1(a)+norm_1(b)), change of variables and the polygonal Lipschitz inequality give |O_h(t;p)-O_h(s;p)|<=K d_circle(t,s) first for rational s,t."},
        {"id": "FINITE_DYADIC_INTERPOLANT", "base": "PRA", "depends_on": ["EXACT_RATIONAL_SAMPLES"], "statement": "A_m is the periodic rational polygonal interpolation of the 2^m+1 exact samples O_h(j/2^m;p); it is a finite code."},
        {"id": "UNIFORM_INTERPOLATION_BOUND", "base": "RCA_0", "depends_on": ["OBSERVABLE_LIPSCHITZ_BOUND", "FINITE_DYADIC_INTERPOLANT"], "statement": "The rational Lipschitz map has a unique real-time extension, and every t between adjacent dyadic nodes satisfies |A_m(t)-O_h(t;p)|<=K 2^-m; hence the same bound holds uniformly on every coded bounded interval."},
        {"id": "EXPLICIT_CUTOFF", "base": "PRA", "depends_on": ["OBSERVABLE_LIPSCHITZ_BOUND"], "statement": "Let ell(K) be the least natural ell with K<=2^ell, taking ell(0)=0. The primitive-recursive cutoff N(k)=k+ell(K)+1 gives K 2^-N(k)<=2^-(k+1)<2^-k."},
        {"id": "UNIFORM_RECONSTRUCTION", "base": "RCA_0", "depends_on": ["BOUNDED_LINEAR_OBSERVABLE", "UNIFORM_INTERPOLATION_BOUND", "EXPLICIT_CUTOFF"], "statement": "The subsequence A_N(k) is a prescribed-rate uniform Cauchy name for O_h on the coded circle and therefore converges uniformly on every rational bounded time interval with the displayed cutoff."},
    ]
    result: dict[str, Any] = {
        "schema_version": "foundational-coded-wave-observable-reconstruction-v1",
        "result_id": "FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1",
        "result_kind": "EXPLICIT_UNIFORM_OBSERVABLE_RECONSTRUCTION",
        "lifecycle": "CERTIFIED",
        "created": "2026-08-14",
        "repository_base_commit": "af7d497462698fc5c612d8a68bf84f9b72722c02",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "theorem": "RCA_0 proves that, for each declared mean-zero rational step-pair p and the declared rational periodic polygonal detector h, the finite dyadic rational polygonal approximants A_N(k) converge uniformly to the smeared chiral observable O_h on every rational bounded time interval. The explicit cutoff is N(k)=k+ell(K)+1, where K=Lip(h)(norm_1(a)+norm_1(b)) and ell(K) is the least natural ell with K<=2^ell; the certified error is at most K 2^-N(k)<=2^-(k+1)<2^-k.",
        "declared_observable": OBSERVABLE,
        "finite_approximant": {
            "definition": "A_m is the periodic piecewise-linear interpolation in time through the exact rational samples (j/2^m,O_h(j/2^m;p)) for 0<=j<=2^m.",
            "finiteness": "A_m contains 2^m intervals and 2^m+1 rational sample values; no completed function or numerical oracle is stored in a finite approximant.",
            "time_domain": "The observable and every approximant are one-periodic. Therefore the global circle bound restricts to every interval [-T,T] for positive rational T without changing the cutoff.",
        },
        "cutoff_theorem": {
            "input": "precision k in N and the exact rational finite codes for p and h",
            "data_constant": "K=Lip(h)(norm_1(a)+norm_1(b))",
            "binary_ceiling": "ell(K)=least ell in N with K<=2^ell; ell(0)=0",
            "cutoff": "N(k)=k+ell(K)+1",
            "uniform_bound": "sup_{|t|<=T}|A_N(k)(t)-O_h(t;p)|<=K*2^-N(k)<=2^-(k+1)<2^-k for every positive rational T",
            "logical_strength": "The finite codes, K, ell(K), samples, and cutoff are primitive recursive; RCA_0 supplies the coded real-time extension and the uniform-limit statement.",
        },
        "formal_proof": proof,
        "fixtures": fixtures,
        "provenance": {"source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE), "source_result_id": source["result_id"]},
        "independent_checker": {
            "path": "foundations/check_coded_wave_observable_reconstruction.py",
            "checks": ["source fixture identity", "periodic polygonal detector closure", "exact L1 and Lipschitz constants", "primitive-recursive cutoff inequality", "exact dyadic sample hashes", "independent fine-grid stress bound", "formal dependency DAG", "canonical digest"],
            "expected_digest": "",
        },
        "claim_flags": {
            "declared_rational_initial_data": True,
            "declared_bounded_linear_observable": True,
            "finite_rational_approximants_constructed": True,
            "uniform_bounded_time_convergence_proved": True,
            "explicit_cutoff_function_proved": True,
            "rca0_upper_bound_proved": True,
            "fixed_fixture_arithmetic_primitive_recursive": True,
            "weakest_base_proved": False,
            "full_state_reconstruction_proved": False,
            "localized_spacetime_distribution_proved": False,
            "causal_support_proved": False,
            "green_operator_constructed": False,
            "empirical_calibration_proved": False,
            "new_lorentzian_claim": False,
        },
        "does_not_establish": [
            "that RCA_0 is necessary or the weakest base",
            "uniform reconstruction for unnamed convergent data without a supplied rate or finite rational code",
            "reconstruction of the full wave state from this one smeared observable",
            "a point-local field observable or probability rule",
            "a localized spacetime-distributional weak equation",
            "finite propagation, causal support, or an advanced/retarded Green operator",
            "a variable-coefficient, curved-spacetime, biwave, or metric-BV theorem",
            "empirical calibration of the detector profile",
            "a new LORENTZIAN-CAUSAL result",
        ],
        "next_gate": "Replace the single detector profile by a coded separating localized test class and prove the coefficient-weak spacetime equation without promoting strict causal support.",
        "human_report": "foundations/reports/coded-wave-observable-reconstruction-v1.md",
    }
    result["independent_checker"]["expected_digest"] = canonical_digest(result)
    return result


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Coded wave observable reconstruction v1", "",
        f"**Result:** `{result['result_id']}`", "", "## Theorem", "", result["theorem"], "",
        "This is the first foundations certificate that carries declared rational wave data through a finite approximation sequence to a named observable with a uniform-in-time error bound. It reconstructs one observable, not the full field.", "",
        "## Declared observable", "", f"`{result['declared_observable']['formula']}`", "", result["declared_observable"]["operational_reading"], "",
        "## Finite approximants and cutoff", "", result["finite_approximant"]["definition"], "", f"The cutoff is `{result['cutoff_theorem']['cutoff']}` and the certificate proves", "", f"`{result['cutoff_theorem']['uniform_bound']}`.", "",
        "The cutoff is independent of the displayed bounded interval because the cylinder observable is one-periodic. All samples and cutoff arithmetic are finite and primitive recursive; RCA₀ is used for the coded real-time extension and uniform-limit assertion.", "",
        "## Proof ledger", "", "| Stage | Base | Establishes |", "|---|---|---|",
    ]
    lines += [f"| `{stage['id']}` | `{stage['base']}` | {stage['statement']} |" for stage in result["formal_proof"]]
    lines += ["", "## Exact fixtures", "", "| Initial datum | K | Cutoff | Exact approximation checks |", "|---|---:|---|---:|"]
    for fixture in result["fixtures"]:
        lines.append(f"| `{fixture['id']}` | `{fixture['observable_lipschitz_constant']}` | `{fixture['cutoff_formula']}` | {len(fixture['approximants'])} |")
    lines += ["", "Each approximation row records the exact grid size, rational uniform bound, requested tolerance, and SHA-256 digest of every exact rational sample. The independent checker regenerates those samples and also tests the interpolants on a strictly finer rational grid.", "", "## Reproduction", "", "```text", "python3 foundations/build_coded_wave_observable_reconstruction.py --check", "python3 foundations/check_coded_wave_observable_reconstruction.py", "python3 foundations/verify_coded_wave_observable_reconstruction.py", "python3 -m unittest foundations.tests.test_coded_wave_observable_reconstruction", "```", "", "## Boundaries", ""]
    lines += ["- This does not establish " + item + "." for item in result["does_not_establish"]]
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes]:
    result = build()
    return (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode(), render(result).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_bytes, report_bytes = generated()
    outputs = ((OUTPUT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
