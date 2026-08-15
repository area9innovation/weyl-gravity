#!/usr/bin/env python3
"""Build the receipt for the exact arbitrary-rational-jet Bach evaluator prototype."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from cylinder_polarized_bach_evaluator import (
    Jet,
    PAIRS,
    ZERO_MULTIINDEX,
    bach_euler_density_coefficient,
    brinkmann_background,
    conformal_metric_fixture,
    cylinder_background_invariants,
    polarized_bach_euler_density,
    polarized_weyl_trace_identity,
    ppwave_profile_fixture,
    sparse_fixture,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_CYLINDER_POLARIZED_BACH_EVALUATOR_V1.json"
REPORT = HERE / "REPORT_STRICT_CYLINDER_POLARIZED_BACH_EVALUATOR_V1.md"
ENGINE = HERE / "cylinder_polarized_bach_evaluator.py"
INPUTS = (
    ("quantum-weyl/classical_import/certificates/STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1.json", "STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1", "fail-closed multi-fixture target contract"),
    ("covariant_completion/certificates/linearized_bach.json", "LINEARIZED_BACH_CYLINDER", "action-normalized unary cylinder control"),
    ("bridge/certificates/ppwave_bach_branch_closure.json", "PPWAVE_BACH_BRANCH_CLOSURE", "arbitrary-profile pp-wave zero theorem"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _serialize(values: dict[tuple[int, int], Fraction]) -> list[dict[str, object]]:
    return [{"output_pair": list(pair), "coefficient": str(values[pair])} for pair in PAIRS]


def _all_zero(values: dict[tuple[int, int], Fraction]) -> bool:
    return all(value == 0 for value in values.values())


def _algebra_checks() -> dict[str, bool]:
    x = Jet.from_terms(3, ((0, 0, ZERO_MULTIINDEX, 1), (1, 0, (1, 0, 0, 0), 2), (0, 1, (0, 1, 0, 0), -3)))
    inverse_defect = x * x.reciprocal() - Jet.constant(3, 1)
    square = Jet.from_terms(3, ((0, 0, ZERO_MULTIINDEX, 1), (1, 0, (0, 0, 1, 0), 2), (0, 1, (0, 0, 0, 1), 2), (1, 1, (0, 0, 1, 1), 4)))
    root = square.sqrt()
    derivative_left = (x * square).derivative(2)
    derivative_right = x.derivative(2) * square.truncate(2) + x.truncate(2) * square.derivative(2)
    return {
        "reciprocal_exact_in_square_free_bivariate_quotient": not inverse_defect.terms,
        "sqrt_exact_in_square_free_bivariate_quotient": not (root * root - square).terms,
        "coordinate_derivative_leibniz_exact": derivative_left == derivative_right,
        "no_floating_point_scalar_type": all(isinstance(value, Fraction) for jet in (x, square, root) for *_, value in jet.terms),
    }


def build() -> dict[str, Any]:
    benchmark = json.loads((ROOT / INPUTS[0][0]).read_text())
    linear = json.loads((ROOT / INPUTS[1][0]).read_text())
    ppwave = json.loads((ROOT / INPUTS[2][0]).read_text())
    if benchmark.get("result_id") != INPUTS[0][1] or benchmark["coverage_diagnosis"].get("general_arbitrary_input_cylinder_tensor_available"):
        raise ValueError("benchmark contract drift")
    if linear.get("normalization", "").split(" times")[0] != "-2":
        raise ValueError("linearized action normalization drift")
    if not ppwave["restricted_nonlinear_tensor"].get("q2_identically_zero_for_arbitrary_ppwave_profiles"):
        raise ValueError("pp-wave zero theorem drift")

    first, second = sparse_fixture(1), sparse_fixture(2)
    direct = polarized_bach_euler_density(first, second)
    swapped = polarized_bach_euler_density(second, first)
    trace_defect = polarized_weyl_trace_identity(first, second)
    ppwave_trials = []
    for left_seed, right_seed in ((3, 7), (1, 9), (4, 6)):
        result = polarized_bach_euler_density(ppwave_profile_fixture(left_seed), ppwave_profile_fixture(right_seed), background=brinkmann_background())
        ppwave_trials.append({"left_seed": left_seed, "right_seed": right_seed, "all_ten_outputs_zero": _all_zero(result), "result_sha256": digest(_serialize(result))})
    omega = {ZERO_MULTIINDEX: Fraction(3, 2), (1, 0, 0, 0): -2, (0, 1, 1, 0): Fraction(5, 3), (0, 0, 0, 4): Fraction(-1, 7)}
    conformal = conformal_metric_fixture(omega)
    conformal_unary = bach_euler_density_coefficient(conformal, {}, 1, 0)
    exact_checks = {
        **_algebra_checks(),
        "cylinder_background_geometry_exact": cylinder_background_invariants() == {
            "ricci_lower": [["0", "0", "0", "0"], ["0", "2", "0", "0"], ["0", "0", "2", "0"], ["0", "0", "0", "2"]],
            "scalar": "6",
            "weyl_background_nonzero_components": 0,
            "bach_background_nonzero_components": 0,
        },
        "arbitrary_sparse_trial_swap_symmetric": direct == swapped,
        "arbitrary_sparse_trial_nonlinear_nonzero": any(value != 0 for value in direct.values()),
        "twice_polarized_weyl_trace_identity_zero": trace_defect == 0,
        "three_ppwave_polynomial_trials_zero": all(item["all_ten_outputs_zero"] for item in ppwave_trials),
        "local_conformal_unary_trial_zero": _all_zero(conformal_unary),
    }
    if not all(exact_checks.values()):
        raise ValueError("one or more evaluator prototype checks failed")

    stages = [
        {"stage": "P0_BIVARIATE_EXACT_JETS", "status": "PROTOTYPE_EXECUTED", "evidence": "exact reciprocal, square-root and Leibniz identities over Fraction in Q[a,b]/(a^2,b^2)"},
        {"stage": "P1_CYLINDER_GEOMETRIC_PIPELINE", "status": "PROTOTYPE_EXECUTED", "evidence": "inverse, Levi-Civita, curvature, Schouten, Weyl, Cotton/Bach, action normalization, raising and densitization evaluated through jet order four"},
        {"stage": "P2_LOCAL_IDENTITIES", "status": "PARTIAL", "evidence": "swap symmetry and the differentiated Weyl trace identity pass; differentiated Diff Noether remains open"},
        {"stage": "P3_PHYSICAL_FIXTURE_ADAPTERS", "status": "PARTIAL", "evidence": "three exact Brinkmann polynomial pairs replay the pp-wave zero slice; HT1B cylinder mode adapters remain open"},
        {"stage": "P4_PORTABLE_AST_EXPORT", "status": "OPEN", "evidence": "the evaluator accepts concrete exact jets but has not serialized the universal coefficient table"},
    ]
    trial_payload = {
        "input_kind": "two deterministic non-special sparse rational cylinder four-jets",
        "left_seed": 1,
        "right_seed": 2,
        "output": _serialize(direct),
        "nonzero_output_count": sum(value != 0 for value in direct.values()),
        "swapped_output_sha256": digest(_serialize(swapped)),
        "trace_identity_defect": str(trace_defect),
    }
    value: dict[str, Any] = {
        "schema": "strict-cylinder-polarized-bach-evaluator-v1",
        "result_id": "STRICT_CYLINDER_POLARIZED_BACH_EVALUATOR_V1",
        "result_kind": "EXACT_ARBITRARY_RATIONAL_JET_EVALUATOR_PROTOTYPE",
        "result_state": "EVALUATOR_PROTOTYPE_EXECUTED_UNIVERSAL_AST_AND_DIFF_IDENTITY_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "99d4020850ef9cd394a5cfd9e1001228f430e2e2",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "target": "coefficient of a*b in the ten-component contravariant action Euler density on the unit conformal cylinder",
            "input_interface": "two arbitrary mappings from symmetric metric component and four-coordinate multiindex to exact rational normalized Taylor coefficient",
            "input_metric_jet_order": 4,
            "parameter_algebra": "Q[a,b]/(a^2,b^2)",
            "taylor_factorial": "coordinate coefficients are derivative/alpha!; the a*b coefficient has no hidden factor",
            "action_normalization": "B_action=-2 B_standard",
            "output_scalar_type": "fractions.Fraction",
            "support_boundary": "pointwise local four-jet evaluation implies no inverse differential operator, but a portable support-local AST is not yet exported",
        },
        "algorithm": [item["operation"] for item in benchmark["candidate_program_contract"]],
        "exact_checks": exact_checks,
        "cylinder_background_invariants": cylinder_background_invariants(),
        "arbitrary_sparse_trial": trial_payload,
        "ppwave_restriction_trials": ppwave_trials,
        "conformal_unary_trial": {"omega_jet": [{"multiindex": list(alpha), "coefficient": str(coefficient)} for alpha, coefficient in omega.items()], "all_ten_outputs_zero": _all_zero(conformal_unary), "result_sha256": digest(_serialize(conformal_unary))},
        "benchmark_stage_progress": stages,
        "open_acceptance_gates": [
            "independent exhaustive comparison with the serialized cylinder linearized Bach operator",
            "differentiated Diff Noether identity with connection and density variations",
            "HT1B E/A/L mode adapters and exact S3 integrations for both nonzero channels",
            "universal 10 x 10 fourth-jet component table and portable tensor-natural AST",
            "independent second implementation or coefficient-level receiver replay",
        ],
        "canonical_hashes": {},
        "implementation": {"path": str(ENGINE.relative_to(ROOT)), "sha256": sha(ENGINE)},
        "provenance": {"inputs": [{"path": path, "result_or_artifact_id": result_id, "sha256": sha(ROOT / path), "role": role} for path, result_id, role in INPUTS]},
        "claim_flags": {
            "EXACT_ARBITRARY_RATIONAL_JET_INTERFACE_EXECUTED": True,
            "CYLINDER_GEOMETRIC_PIPELINE_PROTOTYPE_EXECUTED": True,
            "GENERAL_UNIVERSAL_COMPONENT_AST_EXPORTED": False,
            "ALL_BENCHMARK_GATES_PASSED": False,
            "STRICT_HSTAR_Q2_ROW_PORTABLE": False,
            "STRICT_SUPPORT_LOCAL_Q2_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_CAUSAL_CERTIFIED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "a universal symbolic coefficient table or portable tensor-natural h-star q2 row",
            "exhaustive agreement with the independently serialized unary cylinder operator",
            "the differentiated diffeomorphism Noether identity for arbitrary fifth test jets",
            "the two nonzero HT1B mode-channel densities or their exact S3 projections",
            "that three polynomial pp-wave evaluations replace the existing arbitrary-profile theorem",
            "a complete six-row support-local q2, local D action, or any interaction receiver identity",
            "a passed classical import gate, causal Green homotopy, Hadamard state, QME restoration, or Lorentzian quantum theory",
        ],
        "independent_checker": "quantum-weyl/classical_import/check_strict_cylinder_polarized_bach_evaluator.py",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_CYLINDER_POLARIZED_BACH_EVALUATOR_V1.md",
    }
    value["canonical_hashes"] = {
        "scope_sha256": digest(value["scope"]),
        "exact_checks_sha256": digest(exact_checks),
        "arbitrary_sparse_trial_sha256": digest(trial_payload),
        "ppwave_restriction_trials_sha256": digest(ppwave_trials),
        "benchmark_stage_progress_sha256": digest(stages),
    }
    return value


def render(value: dict[str, Any]) -> str:
    stages = "\n".join(f"| `{item['stage']}` | `{item['status']}` | {item['evidence']} |" for item in value["benchmark_stage_progress"])
    checks = "\n".join(f"| `{name}` | `PASS` |" for name, passed in value["exact_checks"].items() if passed)
    outputs = "\n".join(f"| `{tuple(item['output_pair'])}` | `{item['coefficient']}` |" for item in value["arbitrary_sparse_trial"]["output"])
    return f"""# Strict cylinder polarized-Bach evaluator prototype v1

**Result:** `{value['result_id']}`

**State:** `{value['result_state']}`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

An executable, dependency-free exact evaluator now accepts two arbitrary
rational metric four-jets and returns the coefficient of `a*b` in all ten
components of the action-normalized contravariant Euler density. It evaluates
the full metric inverse → connection → curvature → Weyl → Bach → density
pipeline in `Q[a,b]/(a^2,b^2)`, so the polarized coefficient has no hidden
factorial.

This is a prototype evaluator, not yet the universal component AST required
by Gate A. It evaluates any supplied exact jet, but it has not enumerated and
serialized every basis input pair or received an independent coefficient-level
replay.

## Exact checks

| Check | Status |
|---|---|
{checks}

The background replay gives `Ric=diag(0,2,2,2)`, scalar curvature `6`, and
zero Weyl and Bach tensors. Three exact polynomial Brinkmann profile pairs
return zero in all ten outputs. A local infinitesimal Weyl direction returns
zero in the unary row. The nonlinear cylinder trial is symmetric under input
exchange and satisfies the twice-polarized identity `coeff_ab(g_mn E^mn)=0`.

## Non-special cylinder smoke result

| Output pair | Exact coefficient |
|---|---:|
{outputs}

Nine of ten components are nonzero, which prevents the zero-slice test from
becoming a vacuous implementation.

## Benchmark progress

| Stage | State | Evidence |
|---|---|---|
{stages}

## Still required

""" + "\n".join(f"- {item}." for item in value["open_acceptance_gates"]) + f"""

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_cylinder_polarized_bach_evaluator.py --check
python3 quantum-weyl/classical_import/check_strict_cylinder_polarized_bach_evaluator.py
python3 quantum-weyl/classical_import/verify_strict_cylinder_polarized_bach_evaluator.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_cylinder_polarized_bach_evaluator.py -v
```

## Does not establish

""" + "\n".join(f"- {item}." for item in value["does_not_establish"]) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_CYLINDER_POLARIZED_BACH_EVALUATOR_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_CYLINDER_POLARIZED_BACH_EVALUATOR_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
