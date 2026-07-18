#!/usr/bin/env python3
"""Certify finite-slab nested causal polynomial Green convolution."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_recoil_interval_stream import (
    RationalInterval,
    evaluate_nested_green_time_convolution_interval,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_FINITE_NESTED_TIME_CONVOLUTION.json"
SCHEMA = PACKAGE / "schema/berger-recoil-finite-nested-time-convolution-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-finite-nested-time-convolution.md"
DEPENDENCIES = {
    "mode_kernels": PACKAGE / "certificates/BERGER_FINITE_MODE_MAXWELL_EMITTER_GREEN_KERNELS.json",
    "shell_word": PACKAGE / "certificates/BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD.json",
}
SOURCE_FILES = [
    Path(__file__), PACKAGE / "berger_recoil_interval_stream.py",
    PACKAGE / "verify_berger_recoil_finite_nested_time_convolution.py",
    PACKAGE / "tests/test_berger_recoil_finite_nested_time_convolution.py",
    SCHEMA, REPORT,
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(**updates: Any) -> dict[str, object]:
    arguments: dict[str, Any] = {
        "source_coefficients": [RationalInterval.point(1), RationalInterval.point(1)],
        "source_remainder_upper": Fraction(0),
        "kernel_stages": [
            {"label": "retarded_Maxwell", "coefficients": [RationalInterval.point(2)], "uniform_remainder_upper": Fraction(0)},
            {"label": "retarded_massive", "coefficients": [RationalInterval.point(0), RationalInterval.point(1)], "uniform_remainder_upper": Fraction(0)},
        ],
        "slab_length": Fraction(1),
        "orientation": "retarded",
    }
    arguments.update(updates)
    return evaluate_nested_green_time_convolution_interval(**arguments)


def _mutation_detected(**updates: Any) -> bool:
    try:
        _fixture(**updates)
    except ValueError:
        return True
    return False


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if values["mode_kernels"]["flags"]["EXACT_FINITE_MODE_MASSIVE_TWO_FORM_GREEN_KERNELS_EXPORTED"] is not True:
        raise AssertionError("finite massive-kernel dependency dropped")
    if values["shell_word"]["flags"]["COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED"] is not True:
        raise AssertionError("nested recoil-word dependency dropped")
    fixture = _fixture()
    expected = ["0", "0", "0", "1/3", "1/12"]
    if [row["lower"] for row in fixture["polynomial_coefficients"]] != expected:
        raise AssertionError("nested beta-integral fixture drifted")
    advanced = _fixture(orientation="advanced")
    if advanced["polynomial_coefficients"] != fixture["polynomial_coefficients"]:
        raise AssertionError("advanced causal-coordinate fixture drifted")
    remainder_fixture = _fixture(
        source_remainder_upper=Fraction(1, 10),
        kernel_stages=[
            {"label": "bounded_kernel", "coefficients": [RationalInterval.point(2)], "uniform_remainder_upper": Fraction(1, 20)}
        ],
    )
    if remainder_fixture["uniform_remainder_upper"] != "61/200":
        raise AssertionError("uniform remainder propagation drifted")
    fixture_hash = hashlib.sha256(json.dumps(fixture, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    mutations = [
        {"name": "unknown_orientation", "detected": _mutation_detected(orientation="acausal")},
        {"name": "negative_source_remainder", "detected": _mutation_detected(source_remainder_upper=Fraction(-1))},
        {"name": "delete_all_kernel_stages", "detected": _mutation_detected(kernel_stages=[])},
    ]
    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result exports the public "
        "evaluate_nested_green_time_convolution_interval callable for supplied "
        "finite-slab polynomial interval enclosures. In retarded x=t-t_left or "
        "advanced x=t_right-t coordinates it composes any nonempty kernel list by "
        "the exact beta-integral coefficient formula and propagates uniform source/"
        "kernel remainders with rational arithmetic. A two-stage fixture is exactly "
        "x^3/3+x^4/12 and a nonzero-remainder fixture gives 61/200. This is a scoped "
        "causal convolution engine, not a binding of the actual Berger Maxwell/"
        "massive mode kernels, switches or detector coefficients. It therefore is "
        "not a complete recoil convolution backend and does not evaluate I_abc, a "
        "shell, a record, the cone, Bridge 3 or quantum data."
    )
    return {
        "schema": "closed-universe-berger-recoil-finite-nested-time-convolution-v1",
        "result_id": "BERGER_RECOIL_FINITE_NESTED_TIME_CONVOLUTION",
        "setting_id": values["shell_word"]["setting_id"],
        "claim_status": "FINITE_SLAB_POLYNOMIAL_CAUSAL_CONVOLUTION_ENGINE_CERTIFIED_PHYSICAL_BINDING_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "mode_scope": {
            "theory": "classical pure-Weyl gravity plus Berger clock, Maxwell detector and massive two-form emitters",
            "background": "compact positive Berger clock at fixed coupling",
            "boundaries": "one declared compact causal time slab; no spatial boundary",
            "charge_sector": "fixed-coupling Berger sector",
            "carrier": "supplied polynomial interval enclosures for causal Green kernels and sources",
            "degree": "time-convolution coefficient engine independent of form-block degree",
            "parity": "retarded or advanced causal orientation",
            "ell": "finite supplied mode block only; no all-shell binding",
            "m": "supplied block row",
            "k": "supplied passive column",
            "omega": "finite polynomial kernel plus uniform remainder on a rational slab",
        },
        "callable_contract": {
            "module": "closed_universe_observers.berger_recoil_interval_stream",
            "callable": "evaluate_nested_green_time_convolution_interval",
            "formula": "(K*f)(x)=integral_0^x K(x-y)f(y)dy; coefficient beta(i+1,j+1)",
            "remainder_rule": "L(P_sup rK + K_sup rP + rP rK) at each stage",
        },
        "fixtures": {"two_stage_canonical_sha256": fixture_hash, "advanced_coordinate_match": True, "remainder_upper": "61/200"},
        "mutation_results": mutations,
        "flags": {
            "FINITE_POLYNOMIAL_NESTED_TIME_CONVOLUTION_EXPORTED": True,
            "COMPLETE_PHYSICAL_NESTED_TIME_CONVOLUTION_BACKEND_EXPORTED": False,
            "ACTUAL_BERGER_MODE_KERNELS_BOUND": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BIND_ACTUAL_BERGER_MODE_KERNEL_SWITCH_AND_DETECTOR_INTERVALS_TO_NESTED_CONVOLUTION",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES]},
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
        raise SystemExit("stale finite nested time-convolution certificate")
    print("BERGER_RECOIL_FINITE_NESTED_TIME_CONVOLUTION generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
