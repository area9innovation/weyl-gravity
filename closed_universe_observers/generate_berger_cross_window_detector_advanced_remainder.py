#!/usr/bin/env python3
"""Certify the D1 advanced-Maxwell remainder on the earlier h0 window."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import (
    _remainder_audit,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER.json"
SCHEMA = PACKAGE / "schema/berger-cross-window-detector-advanced-maxwell-remainder-v1.schema.json"
REPORT = PACKAGE / "reports/berger-cross-window-detector-advanced-maxwell-remainder.md"
DEPENDENCIES = {
    "detector_image": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_cross_window_detector_advanced_remainder.py",
    PACKAGE / "tests/test_berger_cross_window_detector_advanced_remainder.py",
    SCHEMA,
    REPORT,
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _detector_support(value: dict[str, Any], detector: str) -> tuple[Fraction, Fraction]:
    row = next(
        row
        for row in value["exact_detector_profiles"]["detectors"]
        if row["id"] == detector
    )
    return tuple(Fraction(entry) for entry in row["physical_time_support"])


def _switch_support(value: dict[str, Any], switch_id: str) -> tuple[Fraction, Fraction]:
    row = next(
        row
        for row in value["causal_support_audit"]["switches"]
        if row["id"] == switch_id
    )
    return tuple(Fraction(entry) for entry in row["support_physical_time"])


def build() -> dict[str, Any]:
    values = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    required = {
        "detector_image": "UNIFORM_TIME_KERNEL_SERIES_REMAINDER_EXPORTED",
        "profiles": "EXACT_DETECTOR_CLOCK_PROFILES_SERIALIZED",
        "switches": "EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    detector_support = _detector_support(values["profiles"], "D1")
    switch_support = _switch_support(values["switches"], "h_0")
    if not switch_support[1] < detector_support[0]:
        raise AssertionError("D1/h0 strict advanced support separation was lost")
    detector_center = sum(detector_support, Fraction(0)) / 2
    t_interval = (
        detector_center - switch_support[1],
        detector_center - switch_support[0],
    )
    tau_interval = (
        detector_support[0] - switch_support[1],
        detector_support[1] - switch_support[0],
    )
    rows = [
        {
            "two_j": two_j,
            "uniform_entire_series_remainders": _remainder_audit(
                two_j, tau_interval[1]
            ),
        }
        for two_j in range(5)
    ]
    if any(
        Fraction(row["uniform_entire_series_remainders"][key]) < 0
        for row in rows
        for key in (
            "spatial_cosine_entry_remainder_upper",
            "temporal_sine_entry_remainder_upper",
        )
    ):
        raise AssertionError("cross-window remainder must be nonnegative")

    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result extends only "
        "the existing D1 finite-mode advanced-Maxwell polynomial remainder to "
        "the earlier h0 feedback window. Exact supports give "
        "source_time-t in [7/24,3/8] and T=t_D1-t in [5/16,17/48]. The same "
        "order-five exact polynomial coefficients remain valid, while fresh "
        "entire-series tails are certified for every two_j=0,...,4. This is "
        "not a new detector profile, a higher-shell theorem, an I_100 value, "
        "a physical mass specialization, a quotient/cone/Bridge-3 result or a "
        "quantum claim."
    )
    return {
        "schema": "closed-universe-berger-cross-window-detector-advanced-maxwell-remainder-v1",
        "result_id": "BERGER_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER",
        "setting_id": values["detector_image"]["setting_id"],
        "claim_status": "D1_ADVANCED_MAXWELL_REMAINDER_CERTIFIED_ON_H0_WINDOW_TWO_J0_TO_4",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "mode_scope": {
            "theory": "classical pure-Weyl gravity plus Berger clock and Maxwell detector",
            "background": "compact positive Berger clock at fixed coupling",
            "boundaries": "h0 compact feedback window strictly before the D1 detector window; no spatial boundary",
            "charge_sector": "fixed-coupling Berger sector",
            "carrier": "D1 finite-mode advanced Maxwell one-form polynomial evaluated on h0",
            "degree": 1,
            "parity": "D1 transverse detector polarization",
            "ell": "two_j=0,...,4",
            "m": "all component-major one-form rows",
            "k": "all passive columns k=0,...,two_j",
            "omega": "order-five entire-series remainder for source_time-t in [7/24,3/8]",
        },
        "cross_window": {
            "detector": "D1",
            "feedback_switch": "h_0",
            "detector_support_physical_time": [str(x) for x in detector_support],
            "feedback_support_physical_time": [str(x) for x in switch_support],
            "T_interval": [str(x) for x in t_interval],
            "kernel_tau_interval": [str(x) for x in tau_interval],
            "strict_advanced_support_separation": True,
        },
        "mode_remainders": rows,
        "mutation_results": [
            {
                "name": "reuse_corresponding_D1_h1_tau_max_3_over_16",
                "detected": tau_interval[1] != Fraction(3, 16),
            }
        ],
        "flags": {
            "D1_ADVANCED_MAXWELL_POLYNOMIAL_REMAINDER_ON_H0_EXPORTED": True,
            "CROSS_WINDOW_REMAINDERS_TWO_J0_TO_4_EXPORTED": True,
            "CROSS_WINDOW_ADVANCED_MAXWELL_IMAGE_ABOVE_TWO_J4_EXPORTED": False,
            "I_100_INTERVAL_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EVALUATE_CAUSALLY_ALLOWED_I_100_WITH_THE_CROSS_WINDOW_REMAINDER",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES
            ],
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
    if args.check and (
        not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered
    ):
        raise SystemExit("certificate drift")
    print("BERGER_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
