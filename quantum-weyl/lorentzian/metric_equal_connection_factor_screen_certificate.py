#!/usr/bin/env python3
"""Emit or check the exact Berger equal-connection factor screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from local_bv.schema_validation import validate_instance

from .metric_equal_connection_factor_screen import HERE, SETTING_ID, evaluate_screen


OUTPUT = HERE / "certificates/BERGER_METRIC_EQUAL_CONNECTION_FACTOR_SCREEN.json"
SCHEMA = HERE / "schema/berger-metric-equal-connection-factor-screen-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest() -> dict[str, str]:
    paths = (
        "metric_equal_connection_factor_screen.py",
        "metric_equal_connection_factor_screen_certificate.py",
        "schema/berger-metric-equal-connection-factor-screen-v1.schema.json",
        "tests/test_metric_equal_connection_factor_screen.py",
        "../reports/berger-metric-equal-connection-factor-screen.md",
    )
    return {path: _sha256(HERE / path) for path in paths}


def build_certificate() -> dict[str, Any]:
    screen = evaluate_screen()
    if not all(screen["exact_checks"].values()):
        raise ValueError("an exact equal-connection factor check failed")
    return {
        "schema": "quantum-weyl-berger-metric-equal-connection-factor-screen-v1",
        "result_id": "BERGER_METRIC_EQUAL_CONNECTION_FACTOR_SCREEN",
        "result_state": "LOWER_BY_TWO_AND_METRIC_CONE_NO_GO_IMPORTED_HYBRID_RETAINED_ROUTE_REQUIRED",
        "lifecycle_layer": "CLASSICAL_BV_CAUSAL_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "setting_id": SETTING_ID,
        "ansatz": {
            "coefficient_class": "invariant coefficients in Q(alpha_B,u,v)",
            "factor_form": "(Box_0 I10 + Gamma^a e_a + E)(Box_0 I10 + Gamma^a e_a + F)",
            "shared_first_order_connection": True,
            "potentials": "arbitrary order-zero 10x10 matrices",
        },
        "screen": screen,
        "claim_flags": {
            "BERGER_METRIC_LOWER_BY_TWO_BIWAVE_IMPORTED": True,
            "BERGER_CANONICAL_ROUGH_WAVE_FACTOR_NO_GO_IMPORTED": True,
            "BERGER_RAW_ENDPOINT_METRIC_CONE_NO_GO_IMPORTED": True,
            "EQUAL_CONNECTION_LAPLACE_FACTOR_ANSATZ": False,
            "UNEQUAL_SUBPRINCIPAL_FACTOR_ANSATZ": "OPEN",
            "AUXILIARY_OR_FIRST_ORDER_REALIZATION": "OPEN",
            "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS": False,
            "QUANTUM_CLAIM": False,
        },
        "next_architectures": [
            "HYBRID_RETAINED_CAUSAL_CHAIN_HOMOTOPY",
            "WIDER_CHARACTERISTIC_CONE_GREEN_INVERSE_NONPHYSICAL_OPTION",
        ],
        "upstream_next_gate": "BERGER_LOWER_BY_TWO_CAUSAL_RESOLVENT",
        "next_gate": "BERGER_HYBRID_RETAINED_CAUSAL_CHAIN_HOMOTOPY",
        "manifest": _manifest(),
        "claim_boundary": (
            "Pins and independently replays the classical lower-by-two tensor-biwave normal "
            "form and its canonical rough-wave factor no-go, then independently replays the "
            "full-endpoint metric-cone obstruction. The normalized quadratic-symbol "
            "witness additionally rules out only the invariant-coefficient "
            "two-factor scalar-principal ansatz in which both factors share the uniquely "
            "determined first-order connection. It does not obstruct unequal subprincipal "
            "factors or wider-cone Green inverses. A background-metric-causal inverse on arbitrary "
            "13-row sources is ruled out; the hybrid retained chain route remains open. No "
            "Green hyperbolicity or causal support theorem, "
            "the retained 26-row homotopy, Hadamard data, D-Cartan transfer, QME restoration, or "
            "a Lorentzian quantum theory."
        ),
    }


def _validate(certificate: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError(f"factor-screen schema validation failed: {errors}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build_certificate()
    _validate(certificate)
    if args.emit:
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    if args.check:
        if not OUTPUT.exists() or json.loads(OUTPUT.read_text(encoding="utf-8")) != certificate:
            raise SystemExit("equal-connection factor-screen certificate drifted")
    print("Berger equal-connection factor screen: exact normalized obstruction")


if __name__ == "__main__":
    main()
