#!/usr/bin/env python3
"""Generate the named H2-test completion and weak-wave extension certificate."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "foundations/results/FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1.json"
FINITE_TESTS = ROOT / "foundations/results/FOUNDATIONAL_CODED_LOCAL_WEAK_WAVE_TEST_CLASS_V1.json"
OUTPUT = ROOT / "foundations/results/FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1.json"
REPORT = ROOT / "foundations/reports/coded-weak-wave-h2-test-completion-v1.md"
SLAB_LENGTH = Q(1)
DERIVATIVES = [(0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2)]


def q(value: list[int]) -> Q:
    return Q(value[0], value[1])


def enc(value: Q) -> list[int]:
    return [value.numerator, value.denominator]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ceil_q(value: Q) -> int:
    return -(-value.numerator // value.denominator)


def binary_length(value: int) -> int:
    """Least ell with value <= 2**ell, for positive value."""
    if value < 1:
        raise ValueError(value)
    return (value - 1).bit_length()


def fixture_record(fixture: dict[str, Any]) -> dict[str, Any]:
    right, left = (q(value) for value in fixture["chiral_energies"])
    total = right + left
    factors = {
        "right_transport": max(1, ceil_q(2 * SLAB_LENGTH * right)),
        "left_transport": max(1, ceil_q(2 * SLAB_LENGTH * left)),
        "scalar_wave": max(1, ceil_q(4 * SLAB_LENGTH * total)),
        "state_distribution_pairing": max(1, ceil_q(2 * SLAB_LENGTH * total)),
    }
    offsets = {name: binary_length(value) for name, value in factors.items()}
    samples = []
    for precision in range(1, 9):
        row = {"precision": precision}
        for name, factor in factors.items():
            cutoff = precision + offsets[name]
            row[name + "_index"] = cutoff
            row[name + "_squared_error_bound"] = enc(Q(factor, 4**cutoff))
        samples.append(row)
    return {
        "id": fixture["id"],
        "right_energy": enc(right),
        "left_energy": enc(left),
        "total_energy": enc(total),
        "integer_continuity_factors": factors,
        "binary_cutoff_offsets": offsets,
        "cutoff_rule": "N_F(k)=k+ell(A_F), where ell(A) is least e with A<=2^e",
        "precision_samples": samples,
    }


def canonical_digest(value: dict[str, Any]) -> str:
    projection = {key: value[key] for key in (
        "rational_test_codes", "named_completion", "state_distribution_map",
        "continuity_bounds", "extension_theorem", "formal_proof", "fixtures",
    )}
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    source = json.loads(SOURCE.read_text())
    finite = json.loads(FINITE_TESTS.read_text())
    fixtures = [fixture_record(fixture) for fixture in source["fixtures"]]
    proof = [
        {"id": "RATIONAL_TEST_CODE", "base": "PRA", "statement": "A finite rational polyhedral partition of the unit time cylinder, rational polynomial pieces, exact C1 matching equations, periodic spatial traces, and a supplied rational zero collar at both temporal faces form a primitive-recursively enumerable test-code carrier. Every derivative-square integral through order two is rational and exactly decidable by triangulation and polynomial integration."},
        {"id": "FINITE_CODE_WEAK_IDENTITY", "base": "PRA", "depends_on": ["RATIONAL_TEST_CODE"], "statement": "On every cell the characteristic chain rules are polynomial identities. Interior C1 traces cancel, periodic spatial faces cancel, and both temporal traces vanish. Hence every rational test code has exact right/left transport residual zero and exact scalar weak-wave residual zero for every rational polygonal state code."},
        {"id": "NAMED_H2_COMPLETION", "base": "RCA_0", "depends_on": ["RATIONAL_TEST_CODE"], "statement": "A completed test is a supplied fast Cauchy name of rational test codes with squared H2 distance at most 4^-i for all later indices. The dense embedding and its modulus are therefore part of the representation, not extracted from bare convergence."},
        {"id": "ENERGY_TO_SPACETIME_BOUND", "base": "RCA_0", "statement": "For mean-zero chiral derivatives of total energy E, their anchored primitives obey ||f||_2^2<=||f'||_2^2 and ||g||_2^2<=||g'||_2^2. On a unit slab, ||u||_2^2<=2E, while the right and left transported derivatives have squared spacetime norms E_right and E_left."},
        {"id": "EXPLICIT_RESIDUAL_MODULUS", "base": "RCA_0", "depends_on": ["NAMED_H2_COMPLETION", "ENERGY_TO_SPACETIME_BOUND"], "statement": "Cauchy-Schwarz gives |R_plus(delta phi)|^2<=2 E_right ||delta phi||_H2^2, |R_minus(delta phi)|^2<=2 E_left ||delta phi||_H2^2, and |W(delta phi)|^2<=4 E ||delta phi||_H2^2. Replacing each rational factor by its integer ceiling A gives the primitive-recursive cutoff N_F(k)=k+ell(A)."},
        {"id": "WEAK_EXTENSION", "base": "RCA_0", "depends_on": ["FINITE_CODE_WEAK_IDENTITY", "EXPLICIT_RESIDUAL_MODULUS"], "statement": "Every approximating code has residual exactly zero and the displayed modulus makes the residual sequence fast Cauchy with zero limit. Thus the transport and scalar weak-wave identities hold for every test carrying the declared H2 name."},
        {"id": "REPRESENTATION_BOUNDARY", "base": "RCA_0", "depends_on": ["WEAK_EXTENSION"], "statement": "The result covers a smooth periodic compact-time test whenever an H2 fast name is supplied. It does not uniformly manufacture such a name from an extensional smooth function, identify the nonmetrizable global test-function topology, or prove uniqueness among arbitrary distributions outside the represented energy image."},
    ]
    value: dict[str, Any] = {
        "schema_version": "foundational-coded-weak-wave-h2-test-completion-v1",
        "result_id": "FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1",
        "result_kind": "REPRESENTATION_AWARE_SOBOLEV_TEST_COMPLETION_AND_WEAK_SOLUTION_EXTENSION",
        "lifecycle": "CERTIFIED",
        "created": "2026-08-14",
        "repository_base_commit": "e75bac393108c75601a84f9b0931050a8a1f816d",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "theorem": "Over RCA_0, rational periodic compact-time C1 piecewise-polynomial test codes admit a named H2 completion. The coded-circle energy solution defines a continuous spacetime functional on that completion, and the exact finite-code transport and scalar weak-wave identities extend to every supplied fast H2 test name with an explicit primitive-recursive cutoff.",
        "rational_test_codes": {
            "domain": "unit time slab [0,1] times the rational circle R/Z",
            "partition": "finite rational polyhedral partition compatible with the periodic spatial seam",
            "pieces": "bivariate polynomials with rational coefficients",
            "matching": "value and first weak-derivative traces match on every interior face; value and first-derivative traces match periodically at x=0 and x=1",
            "temporal_support": "the code is identically zero on supplied rational collars [0,epsilon_0] and [epsilon_1,1] with 0<epsilon_0<epsilon_1<1",
            "regularity": "global C1 with piecewise-polynomial weak derivatives through order two",
            "h2_squared_norm": "sum over (a,b) with a+b<=2 of integral |partial_t^a partial_x^b phi|^2",
            "derivative_multiindices": [list(item) for item in DERIVATIVES],
            "exact_arithmetic": "rational polygon triangulation and monomial integration",
            "countable": True,
            "prior_ten_tests_embedded": finite["result_id"],
        },
        "named_completion": {
            "id": "H2_TEST_NAME_UNIT_CYLINDER_V1",
            "name": "a sequence q_i of rational test codes satisfying ||q_i-q_j||_H2^2<=4^-i whenever i<=j",
            "equality": "two names are equal when their cross-distance tends to zero with a supplied diagonal rate",
            "dense_embedding": "the constant fast name embeds every rational test code",
            "density_status": "BY_DECLARED_REPRESENTATION",
            "smooth_test_admission": "a conventional smooth periodic compact-time test is covered when supplied with such a fast H2 code name",
            "excluded_inference": "no H2 name is extracted uniformly from an extensional smooth test without representation data",
        },
        "state_distribution_map": {
            "formula": "J_z(phi)=integral_[0,1]x(R/Z) u_z(t,x) phi(t,x) dt dx",
            "state_input": source["representation"]["completed_state"],
            "target": "continuous linear functionals on the named H2 test completion",
            "squared_bound": "|J_z(phi)|^2<=2 E(z) ||phi||_H2^2",
            "well_defined_on_names": True,
            "evolution_compatibility": "the unique coded energy evolution from the source certificate has the displayed weak representation",
            "uniqueness_scope": "unique inside the represented coded energy-solution image, not among every abstract distributional solution",
        },
        "continuity_bounds": {
            "right_transport": "|R_plus(r;delta phi)|^2<=2 E_right ||delta phi||_H2^2",
            "left_transport": "|R_minus(l;delta phi)|^2<=2 E_left ||delta phi||_H2^2",
            "scalar_wave": "|W(u;delta phi)|^2<=4 E_total ||delta phi||_H2^2",
            "distribution_pairing": "|J_z(delta phi)|^2<=2 E_total ||delta phi||_H2^2",
            "cutoff": "For integer A bounding the displayed rational factor, N_F(k)=k+ell(A) ensures squared residual error <=4^-k.",
        },
        "extension_theorem": {
            "finite_code_residuals": "exactly zero",
            "completed_right_transport": "zero for every declared H2 test name",
            "completed_left_transport": "zero for every declared H2 test name",
            "completed_scalar_wave": "zero for every declared H2 test name",
            "covered_smooth_tests": "every smooth periodic compact-time test supplied with a declared fast H2 name",
            "not_covered": "bare extensional C_c-infinity tests without a name, the full LF topology of all compact supports, arbitrary distributional solutions, causal support, or Green operators",
        },
        "formal_proof": proof,
        "fixtures": fixtures,
        "literature_context": [
            {
                "id": "pauly-steinberg-2018-representations",
                "citation": "Arno Pauly and Florian Steinberg, Comparing Representations for Function Spaces in Computable Analysis, Theory of Computing Systems 62 (2018), 557-582",
                "doi": "10.1007/s00224-016-9745-6",
                "url": "https://link.springer.com/article/10.1007/s00224-016-9745-6",
                "role": "Representation context: names determine the effective topology; compact support is additional discrete advice, and the full test-function space is not metrizable.",
                "import_boundary": "Context only; it does not prove this cylinder certificate or an RCA_0 reversal.",
            },
            {
                "id": "van-schaftingen-2014-sobolev-interpolation",
                "citation": "Jean Van Schaftingen, Approximation in Sobolev spaces by piecewise affine interpolation, Journal of Mathematical Analysis and Applications 420 (2014), 40-47",
                "doi": "10.1016/j.jmaa.2014.05.036",
                "url": "https://arxiv.org/abs/1312.5986",
                "role": "Classical context: direct piecewise-polynomial approximation in Sobolev norms is available without first invoking smooth density.",
                "import_boundary": "The local theorem defines its completion by supplied names; it does not import a uniform H2 name constructor from this paper.",
            },
        ],
        "provenance": {"inputs": [
            {"path": str(SOURCE.relative_to(ROOT)), "sha256": sha(SOURCE), "role": "coded energy solution and exact fixture energies"},
            {"path": str(FINITE_TESTS.relative_to(ROOT)), "sha256": sha(FINITE_TESTS), "role": "finite localized test class and exact finite-code weak identity"},
        ]},
        "independent_checker": {
            "path": "foundations/check_coded_weak_wave_h2_test_completion.py",
            "checks": ["test-code vocabulary", "H2 multiindices", "proof DAG", "source energy closure", "continuity factors", "binary cutoff minimality", "96 exact modulus inequalities", "representation and causal boundaries", "source hashes", "canonical digest"],
            "expected_digest": "",
        },
        "claim_flags": {
            "rational_h2_test_code_carrier_constructed": True,
            "named_h2_test_completion_constructed": True,
            "explicit_residual_modulus_proved": True,
            "weak_solution_extended_to_every_named_h2_test": True,
            "represented_smooth_tests_covered": True,
            "continuous_distributional_state_map_constructed": True,
            "energy_image_evolution_wellposed": True,
            "bare_extensional_smooth_tests_uniformly_named": False,
            "full_lf_test_topology_reconstructed": False,
            "uniqueness_among_arbitrary_distributions_proved": False,
            "strict_causal_support_proved": False,
            "green_operator_constructed": False,
            "weyl_or_metric_bv_equation_proved": False,
            "empirical_calibration_proved": False,
            "new_lorentzian_claim": False,
        },
        "does_not_establish": [
            "a uniform algorithm assigning an H2 name to every bare extensional smooth test",
            "the nonmetrizable LF topology of the unrestricted classical test-function space",
            "a representation-independent distribution theory or weakest-base reversal",
            "uniqueness among arbitrary distributional weak solutions outside the coded energy image",
            "pointwise differentiability of the step chiral derivatives",
            "strict finite propagation or causal support",
            "an advanced or retarded Green operator",
            "a variable-coefficient, curved-spacetime, Weyl, or metric-BV equation",
            "a probability rule or empirical calibration",
            "a new LORENTZIAN-CAUSAL result",
        ],
        "next_gate": "Compare the named H2 representation with the conventional fixed-support smooth-test representation by constructing a uniform name translator under explicit derivative/modulus advice; treat the global LF support topology and causal Green support as separate gates.",
        "human_report": "foundations/reports/coded-weak-wave-h2-test-completion-v1.md",
    }
    value["independent_checker"]["expected_digest"] = canonical_digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    lines = [
        "# Named H2 test completion for the coded weak wave", "",
        f"**Result:** `{value['result_id']}`", "", "## Theorem", "", value["theorem"], "",
        "## Why this is the right next gate", "",
        "The previous ten localized tests proved exact finite compatibility but did not justify the phrase ‘for every smooth test’. This result enlarges the test carrier to all fast H2 names of rational periodic compact-time C1 piecewise-polynomial codes. The convergence rate is mathematical input, so RCA₀ can extend the residual without selecting a modulus from bare convergence.", "",
        "That distinction is substantive. The global classical space of compactly supported smooth tests is not metrizable; fixing the unit slab and declaring an H2 name chooses a particular represented carrier rather than silently recovering the entire classical test-function topology.", "",
        "## Exact continuity rail", "",
        "```text", value["continuity_bounds"]["right_transport"], value["continuity_bounds"]["left_transport"], value["continuity_bounds"]["scalar_wave"], "```", "",
        "If A is the integer ceiling of the relevant factor, `N_F(k)=k+ell(A)` forces squared error at most `4^-k`. Every rational approximant has residual exactly zero, hence every named limit does too.", "",
        "## Fixture cutoffs", "", "| Fixture | right offset | left offset | wave offset | distribution offset |", "|---|---:|---:|---:|---:|",
    ]
    for fixture in value["fixtures"]:
        o = fixture["binary_cutoff_offsets"]
        lines.append(f"| `{fixture['id']}` | {o['right_transport']} | {o['left_transport']} | {o['scalar_wave']} | {o['state_distribution_pairing']} |")
    lines += [
        "", "## What now counts as a test", "",
        "A test is a fast H2 Cauchy name of rational finite codes. A conventional smooth periodic compact-time test is included when such a name is supplied. The theorem does not manufacture that name from an otherwise unspecified smooth function.", "",
        "## Literature placement", "",
        "Pauly and Steinberg make the representation issue explicit: names determine effective topology, while compact support requires extra advice. Van Schaftingen supplies classical context for direct piecewise-polynomial approximation in Sobolev norms. Neither reference is treated as proving this exact RCA₀ certificate.", "",
        "## Reproduction", "", "```text",
        "python3 foundations/build_coded_weak_wave_h2_test_completion.py --check",
        "python3 foundations/check_coded_weak_wave_h2_test_completion.py",
        "python3 foundations/verify_coded_weak_wave_h2_test_completion.py",
        "python3 -m unittest foundations.tests.test_coded_weak_wave_h2_test_completion",
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
        print("FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
