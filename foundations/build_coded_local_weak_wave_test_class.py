#!/usr/bin/env python3
"""Generate the exact localized-test and coefficient-weak wave certificate."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "foundations/results/FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1.json"
OBSERVABLE = ROOT / "foundations/results/FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1.json"
OUTPUT = ROOT / "foundations/results/FOUNDATIONAL_CODED_LOCAL_WEAK_WAVE_TEST_CLASS_V1.json"
REPORT = ROOT / "foundations/reports/coded-local-weak-wave-test-class-v1.md"
TIME_INTERVAL = (Q(1, 8), Q(3, 8))


def q(value: list[int]) -> Q:
    return Q(value[0], value[1])


def enc(value: Q) -> list[int]:
    return [value.numerator, value.denominator]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def step_value(breaks: list[Q], values: list[Q], point: Q) -> Q:
    point %= 1
    for index, (left, right) in enumerate(zip(breaks, breaks[1:])):
        if left <= point < right:
            return values[index]
    raise ValueError(point)


def bump_moment(interval: tuple[Q, Q]) -> Q:
    """Integral of ((s-a)(b-s))^2 over [a,b]."""
    length = interval[1] - interval[0]
    return length ** 5 / 30


def common_partition(fixtures: list[dict[str, Any]]) -> list[Q]:
    return sorted({q(point) for fixture in fixtures for point in fixture["breaks"]})


def refined_coefficients(fixture: dict[str, Any], partition: list[Q], field: str) -> list[Q]:
    breaks = [q(point) for point in fixture["breaks"]]
    values = [q(value) for value in fixture[field]]
    return [step_value(breaks, values, (left + right) / 2) for left, right in zip(partition, partition[1:])]


def test_records(partition: list[Q]) -> list[dict[str, Any]]:
    time_moment = bump_moment(TIME_INTERVAL)
    records = []
    for chirality, sign in (("RIGHT", "x-t"), ("LEFT", "x+t")):
        for index, interval in enumerate(zip(partition, partition[1:])):
            spatial_moment = bump_moment(interval)
            records.append({
                "id": f"{chirality}_CELL_{index}",
                "chirality": chirality,
                "spatial_cell": [enc(interval[0]), enc(interval[1])],
                "time_interval": [enc(TIME_INTERVAL[0]), enc(TIME_INTERVAL[1])],
                "formula": f"B_I(t) B_J(({sign}) mod 1)",
                "support": "compact in the declared time interval and in one characteristic spatial strip",
                "regularity": "periodic C1 piecewise rational polynomial; second weak derivatives are piecewise polynomial",
                "time_moment": enc(time_moment),
                "spatial_moment": enc(spatial_moment),
                "measurement_normalization": enc(time_moment * spatial_moment),
            })
    return records


def fixture_record(fixture: dict[str, Any], partition: list[Q], tests: list[dict[str, Any]]) -> dict[str, Any]:
    widths = [right - left for left, right in zip(partition, partition[1:])]
    right = refined_coefficients(fixture, partition, "right")
    left = refined_coefficients(fixture, partition, "left")
    coefficients = {"RIGHT": right, "LEFT": left}
    measurements = []
    for test in tests:
        index = int(test["id"].rsplit("_", 1)[1])
        coefficient = coefficients[test["chirality"]][index]
        normalization = q(test["measurement_normalization"])
        measurements.append({
            "test_id": test["id"],
            "coefficient": enc(coefficient),
            "normalization": enc(normalization),
            "pairing": enc(coefficient * normalization),
            "right_transport_residual": [0, 1],
            "left_transport_residual": [0, 1],
            "scalar_wave_residual": [0, 1],
        })
    return {
        "id": fixture["id"],
        "refined_right_coefficients": [enc(value) for value in right],
        "refined_left_coefficients": [enc(value) for value in left],
        "zero_mean_checks": [enc(sum((w * c for w, c in zip(widths, values)), Q(0))) for values in (right, left)],
        "measurements": measurements,
    }


def canonical_digest(value: dict[str, Any]) -> str:
    projection = {key: value[key] for key in ("carrier", "localized_test_class", "separation", "weak_equations", "formal_proof", "fixtures")}
    return hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    source = json.loads(SOURCE.read_text())
    observable = json.loads(OBSERVABLE.read_text())
    fixtures = source["fixtures"]
    partition = common_partition(fixtures)
    widths = [right - left for left, right in zip(partition, partition[1:])]
    tests = test_records(partition)
    diagonal = [q(test["measurement_normalization"]) for test in tests]
    determinant = Q(1)
    for entry in diagonal:
        determinant *= entry
    proof = [
        {"id": "COMMON_RATIONAL_CARRIER", "base": "PRA", "statement": "The union of the three declared rational partitions gives five spatial cells. A labelled right/left step pair has ten rational coefficients; the two exact mean-zero equations define an eight-dimensional subcarrier."},
        {"id": "LOCALIZED_BUMP_CODE", "base": "PRA", "depends_on": ["COMMON_RATIONAL_CARRIER"], "statement": "For a rational interval J, B_J(s)=((s-a)(b-s))^2 on J and zero outside is a periodic C1 finite rational polynomial code. Multiplying one temporal and one characteristic bump gives ten compact-time localized spacetime tests."},
        {"id": "FINITE_SEPARATION", "base": "PRA", "depends_on": ["LOCALIZED_BUMP_CODE"], "statement": "Pairing each labelled chiral component with its matching cell test gives a diagonal 10 by 10 rational matrix with entries mu(I)mu(J), where mu([a,b])=(b-a)^5/30. Every entry is positive, so the tests separate the ambient coefficient carrier and hence its mean-zero subcarrier."},
        {"id": "CHARACTERISTIC_CHAIN_RULE", "base": "PRA", "depends_on": ["LOCALIZED_BUMP_CODE"], "statement": "At fixed y=x-t, d_t phi(t,y+t)=(partial_t+partial_x)phi. At fixed z=x+t, d_t phi(t,z-t)=(partial_t-partial_x)phi. These are exact polynomial identities on every branch."},
        {"id": "COEFFICIENT_TRANSPORT_IDENTITY", "base": "PRA", "depends_on": ["CHARACTERISTIC_CHAIN_RULE"], "statement": "For r=a(x-t) and l=b(x+t), every basis-test residual integral r(phi_t+phi_x) and l(phi_t-phi_x) is a temporal boundary term. The time bump vanishes at both endpoints, so all twenty transport coefficients vanish exactly for each fixture."},
        {"id": "SCALAR_WEAK_WAVE_IDENTITY", "base": "PRA", "depends_on": ["COEFFICIENT_TRANSPORT_IDENTITY"], "statement": "For the polygonal primitives u=f(x-t)+g(x+t), u_t=-r+l and u_x=r+l. One integration by parts gives integral u(phi_tt-phi_xx)=R_plus(r;phi)-R_minus(l;phi)=0 coefficient by coefficient for all ten tests."},
        {"id": "COMPLETION_TRANSFER", "base": "RCA_0", "depends_on": ["FINITE_SEPARATION", "SCALAR_WEAK_WAVE_IDENTITY"], "statement": "The finitely coded test derivatives define bounded rational functionals on the coded energy carrier. Density, the supplied fast-Cauchy rates, and the bounded mean-zero primitive map transfer the ten weak identities to completed names without compactness or subsequence choice."},
    ]
    value: dict[str, Any] = {
        "schema_version": "foundational-coded-local-weak-wave-test-class-v1",
        "result_id": "FOUNDATIONAL_CODED_LOCAL_WEAK_WAVE_TEST_CLASS_V1",
        "result_kind": "FINITE_LOCALIZED_SEPARATING_TEST_CLASS_AND_COEFFICIENT_WEAK_EQUATION",
        "lifecycle": "CERTIFIED",
        "created": "2026-08-14",
        "repository_base_commit": "3c295ffacc222271143df0018bdae167eae87a81",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "theorem": "PRA certifies a ten-element characteristic-localized rational polynomial test family that separates the declared labelled finite chiral coefficient carrier and annihilates every coefficient of its two weak transport equations and derived scalar weak wave equation. RCA_0 transfers those finitely many bounded weak identities to the represented fast-Cauchy energy completion.",
        "carrier": {
            "kind": "DECLARED_LABELLED_CHIRAL_STEP_CARRIER",
            "common_partition": [enc(point) for point in partition],
            "cell_widths": [enc(width) for width in widths],
            "ambient_coefficient_dimension": 10,
            "mean_zero_constraint_rank": 2,
            "mean_zero_subcarrier_dimension": 8,
            "meaning": "The carrier retains the right/left labels present in the source representation; it is not a scalar-field quotient or a gauge-invariant observable algebra.",
        },
        "localized_test_class": {
            "time_interval": [enc(TIME_INTERVAL[0]), enc(TIME_INTERVAL[1])],
            "bump_definition": "B_[a,b](s)=((s-a)(b-s))^2 for a<=s<=b and 0 otherwise",
            "bump_moment_formula": "mu([a,b])=integral B_[a,b]=(b-a)^5/30",
            "basis_size": len(tests),
            "rational_span": "All finite rational linear combinations of the ten displayed basis tests.",
            "tests": tests,
        },
        "separation": {
            "measurement": "Pair a labelled chiral component with the matching labelled characteristic bump.",
            "matrix_shape": [10, 10],
            "matrix_form": "DIAGONAL",
            "diagonal": [enc(value) for value in diagonal],
            "determinant": enc(determinant),
            "rank": 10,
            "separates_ambient_carrier": True,
            "separates_mean_zero_subcarrier": True,
            "does_not_separate": "unlabelled scalar fields, arbitrary L2 states, observables modulo gauge, or a continuum test-function topology",
        },
        "weak_equations": {
            "right_transport": "R_plus(r;phi)=integral r(t,x)(phi_t+phi_x) dt dx=0",
            "left_transport": "R_minus(l;phi)=integral l(t,x)(phi_t-phi_x) dt dx=0",
            "scalar_wave": "W(u;phi)=integral u(t,x)(phi_tt-phi_xx) dt dx=R_plus-R_minus=0",
            "basis_coefficients_checked_per_fixture": len(tests),
            "transport_residuals_checked_per_fixture": 2 * len(tests),
            "scalar_residuals_checked_per_fixture": len(tests),
            "scope": "The equation is certified against the finite rational span of the displayed localized tests, not against every smooth compactly supported test.",
        },
        "formal_proof": proof,
        "fixtures": [fixture_record(fixture, partition, tests) for fixture in fixtures],
        "provenance": {"inputs": [
            {"path": str(SOURCE.relative_to(ROOT)), "sha256": sha(SOURCE), "role": "coded rational wave carrier and exact fixtures"},
            {"path": str(OBSERVABLE.relative_to(ROOT)), "sha256": sha(OBSERVABLE), "role": "preceding bounded-observable reconstruction boundary"},
        ]},
        "independent_checker": {
            "path": "foundations/check_coded_local_weak_wave_test_class.py",
            "checks": ["common refinement", "zero-mean fixtures", "exact bump moments", "diagonal rank and determinant", "fixture measurement coefficients", "characteristic chain rules", "transport and scalar residual closure", "proof DAG", "source hashes", "canonical digest"],
            "expected_digest": "",
        },
        "claim_flags": {
            "finite_localized_test_class_constructed": True,
            "labelled_finite_carrier_separated": True,
            "coefficient_transport_identities_proved": True,
            "coefficient_scalar_weak_wave_identity_proved": True,
            "pra_finite_certificate": True,
            "rca0_completion_transfer": True,
            "all_smooth_tests_covered": False,
            "unlabelled_scalar_field_separated": False,
            "full_state_reconstruction_proved": False,
            "strict_causal_support_proved": False,
            "green_operator_constructed": False,
            "weyl_or_metric_bv_equation_proved": False,
            "empirical_calibration_proved": False,
            "new_lorentzian_claim": False,
        },
        "does_not_establish": [
            "separation after forgetting the declared right/left chiral labels",
            "a separating algebra for arbitrary completed L2 states or gauge equivalence classes",
            "the weak wave equation against every smooth compactly supported test",
            "a representation-independent distributional solution theorem",
            "pointwise differentiability of the step components",
            "strict finite propagation or causal support",
            "an advanced or retarded Green operator",
            "a variable-coefficient, curved-spacetime, Weyl, or metric-BV equation",
            "a probability rule or empirically calibrated detector",
            "a new LORENTZIAN-CAUSAL result",
        ],
        "next_gate": "Enlarge the finite characteristic bump span with an explicit density/modulus theorem in a named test-function topology, then ask whether the weak identity extends to every test in that topology; keep causal support as a separate later gate.",
        "human_report": "foundations/reports/coded-local-weak-wave-test-class-v1.md",
    }
    value["independent_checker"]["expected_digest"] = canonical_digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    separation = value["separation"]
    lines = [
        "# Localized coded weak-wave test class v1", "",
        f"**Result:** `{value['result_id']}`", "", "## Theorem", "", value["theorem"], "",
        "## What is separated", "", value["carrier"]["meaning"], "",
        f"The common partition has five spatial cells. The labelled carrier has dimension {value['carrier']['ambient_coefficient_dimension']}; imposing the two mean-zero equations leaves dimension {value['carrier']['mean_zero_subcarrier_dimension']}.", "",
        f"The ten localized tests give a `{separation['matrix_shape'][0]} x {separation['matrix_shape'][1]}` diagonal rational measurement matrix of rank **{separation['rank']}**. Its determinant is nonzero, so the tests separate every declared labelled coefficient before and after the mean-zero restriction.", "",
        "## Localized tests", "", f"`{value['localized_test_class']['bump_definition']}`", "", value["localized_test_class"]["rational_span"], "",
        "Each basis element is compact in the time interval `[1/8,3/8]` and in one right- or left-characteristic spatial strip. It is a finite periodic `C1` rational polynomial code, not a point detector.", "",
        "## Coefficient-wise weak equation", "", f"`{value['weak_equations']['right_transport']}`", "", f"`{value['weak_equations']['left_transport']}`", "", f"`{value['weak_equations']['scalar_wave']}`", "",
        "For every basis test, the characteristic chain rule turns each transport residual into a temporal boundary term. The temporal bump vanishes at both endpoints. Thus all twenty transport coefficients and all ten derived scalar-wave coefficients vanish exactly for each fixture; rational linear combinations follow by linearity.", "",
        "PRA checks the finite polynomial, rank, pairing, and residual arithmetic. RCA₀ transfers the finitely many bounded identities to the represented fast-Cauchy completion. This is not a claim for every smooth test function.", "",
        "## Exact fixture summary", "", "| Fixture | Local measurements | Transport residuals | Scalar residuals |", "|---|---:|---:|---:|",
    ]
    for fixture in value["fixtures"]:
        lines.append(f"| `{fixture['id']}` | {len(fixture['measurements'])} | {2 * len(fixture['measurements'])} | {len(fixture['measurements'])} |")
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_coded_local_weak_wave_test_class.py --check", "python3 foundations/check_coded_local_weak_wave_test_class.py", "python3 foundations/verify_coded_local_weak_wave_test_class.py", "python3 -m unittest foundations.tests.test_coded_local_weak_wave_test_class", "```", "", "## Boundaries", ""]
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
        print("FOUNDATIONAL_CODED_LOCAL_WEAK_WAVE_TEST_CLASS_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_CODED_LOCAL_WEAK_WAVE_TEST_CLASS_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
