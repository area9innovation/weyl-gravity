#!/usr/bin/env python3
"""Certify exact callable aggregation of supplied Berger recoil channel intervals."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_recoil_interval_stream import (
    RationalInterval,
    evaluate_recoil_shell_interval,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_FINITE_SHELL_INTERVAL_AGGREGATOR.json"
SCHEMA = PACKAGE / "schema/berger-recoil-finite-shell-interval-aggregator-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-finite-shell-interval-aggregator.md"
DEPENDENCIES = {
    "per_shell_word": PACKAGE / "certificates/BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD.json",
    "haar": PACKAGE / "certificates/BERGER_HAAR_PROFILE_NORMALIZATION_REPAIR.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "berger_recoil_interval_stream.py",
    PACKAGE / "verify_berger_recoil_finite_shell_interval_aggregator.py",
    PACKAGE / "tests/test_berger_recoil_finite_shell_interval_aggregator.py",
    SCHEMA,
    REPORT,
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(*, omit_weight: bool = False, square_source_coupling: bool = False) -> dict[str, object]:
    inverse_volume = RationalInterval(Fraction(1, 10), Fraction(1, 9))
    result = evaluate_recoil_shell_interval(
        two_j=1,
        detector=1,
        source_preparation=0,
        source_coupling=Fraction(4) if square_source_coupling else Fraction(-2),
        feedback_couplings={0: Fraction(3), 1: Fraction(-1)},
        inverse_berger_volume=RationalInterval.point(1) if omit_weight else inverse_volume,
        channel_columns={
            0: [RationalInterval.point(1), RationalInterval.point(2)],
            1: [RationalInterval.point(4), RationalInterval.point(5)],
        },
    )
    return result


def missing_passive_column_mutation_detected() -> bool:
    try:
        evaluate_recoil_shell_interval(
            two_j=1,
            detector=0,
            source_preparation=0,
            source_coupling=Fraction(1),
            feedback_couplings={0: Fraction(1), 1: Fraction(1)},
            inverse_berger_volume=RationalInterval.point(1),
            channel_columns={
                0: [RationalInterval.point(1)],
                1: [RationalInterval.point(1), RationalInterval.point(1)],
            },
        )
    except ValueError as error:
        return "two_j+1 passive columns" in str(error)
    return False


def build() -> dict[str, object]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if values["per_shell_word"]["flags"]["ALL_FOUR_AB_AGGREGATE_STREAMS_SERIALIZED"] is not True:
        raise AssertionError("symbolic aggregate dependency dropped")
    if values["haar"]["flags"]["EXACT_BERGER_HAAR_DENSITY_EXPORTED"] is not True:
        raise AssertionError("Berger Haar dependency dropped")
    exact = fixture()
    expected = {"lower": "-16", "upper": "-72/5", "width": "8/5"}
    if exact["shell_interval"] != expected:
        raise AssertionError("exact shell fixture drifted")
    mutations = [
        {"name": "omit_Peter_Weyl_weight", "detected": fixture(omit_weight=True)["shell_interval"] != expected},
        {"name": "square_source_coupling", "detected": fixture(square_source_coupling=True)["shell_interval"] != expected},
        {"name": "drop_passive_column", "detected": missing_passive_column_mutation_detected(), "witness": "two_j=1 requires exactly two columns per feedback channel"},
    ]
    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result supplies the first "
        "callable Berger recoil interval backend. Given already-enclosed channel "
        "values I_abc[two_j,k], it uses exact rational interval arithmetic to sum "
        "all two_j+1 passive columns, apply g_b g_c^2, sum both feedback channels, "
        "and apply the interval Peter-Weyl weight (two_j+1)/Vol_Berger. A signed "
        "fixture evaluates exactly to [-16,-72/5], and mutations detect omission "
        "of the reconstruction weight, incorrect source-coupling squaring and a "
        "missing passive column. This does not construct detector-profile "
        "coefficients or nested advanced/retarded Green convolutions, aggregate "
        "multiple shells, apply a tail stopping rule, choose physical masses or "
        "couplings, evaluate recoil, restrict to the cone, activate Bridge 3 or "
        "make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-recoil-finite-shell-interval-aggregator-v1",
        "result_id": "BERGER_RECOIL_FINITE_SHELL_INTERVAL_AGGREGATOR",
        "setting_id": values["per_shell_word"]["setting_id"],
        "claim_status": "EXACT_CALLABLE_FINITE_SHELL_INTERVAL_AGGREGATION_CERTIFIED",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "mode_scope": values["per_shell_word"]["mode_scope"],
        "callable_contract": {
            "module": "closed_universe_observers.berger_recoil_interval_stream",
            "callable": "evaluate_recoil_shell_interval",
            "input": "two already-enclosed feedback-channel column lists plus exact couplings and a positive inverse-volume interval",
            "output": "exact rational enclosure for one detector/source/two_j shell",
            "formula": "((two_j+1)/Vol_Berger) g_b sum_c g_c^2 sum_k I_abc[two_j,k]",
        },
        "exact_fixture": exact,
        "mutation_results": mutations,
        "flags": {
            "CALLABLE_SHELL_INTERVAL_BACKEND_EXPORTED": True,
            "EXACT_RATIONAL_INTERVAL_ARITHMETIC": True,
            "PETER_WEYL_WEIGHT_AND_COUPLINGS_APPLIED": True,
            "DETECTOR_PROFILE_COEFFICIENT_PROVIDER_EXPORTED": False,
            "NESTED_TIME_CONVOLUTION_BACKEND_EXPORTED": False,
            "TAIL_AWARE_AGGREGATE_STOP_LOOP_EXPORTED": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "IMPLEMENT_DETECTOR_COEFFICIENT_AND_NESTED_TIME_CONVOLUTION_BACKENDS",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale Berger recoil finite-shell interval aggregator")
    print("BERGER_RECOIL_FINITE_SHELL_INTERVAL_AGGREGATOR generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
