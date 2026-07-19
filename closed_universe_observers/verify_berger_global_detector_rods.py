#!/usr/bin/env python3
"""Independent replay of the global Berger detector-rod formulas."""

from __future__ import annotations

import json

import sympy as sp

from closed_universe_observers import generate_berger_global_detector_rods as result


def main() -> int:
    payload = json.loads(result.CERTIFICATE.read_text())
    rebuilt = result.build()
    if payload != rebuilt:
        raise AssertionError("persisted global rod certificate drifted")
    if payload["exact_checks"]["event_relational_jacobians"] != [
        [["1", "0", "0", "0"], ["0", "1", "0", "0"], ["0", "0", "1", "0"], ["0", "0", "0", "1"]]
    ] * 2:
        raise AssertionError("detector-event rod charts are not identity charts")
    if sp.simplify(2 * result.OMEGA - sp.sqrt(58) / 3) != 0:
        raise AssertionError("rod stress temporal frequency was not independently replayed")
    if "T_rod^{ab}/2" not in payload["global_source_export"]["retained_metric_source"]:
        raise AssertionError("covariant metric Euler half-stress normalization dropped")
    flags = payload["flags"]
    if not flags["GLOBAL_COMPACT_ROD_CONFIGURATION_EXPORTED"] or not flags["GLOBAL_COMPACT_ROD_Q0_FORMULA_EXPORTED"]:
        raise AssertionError("global rod export flags dropped")
    if flags["COMPACT_TAUB_PROJECTION_COMPUTED"] or flags["PERTURBATIVE_BACKREACTED_ROD_BRANCH_CERTIFIED"]:
        raise AssertionError("compact nonlinear gate was over-promoted")
    print("BERGER_GLOBAL_DETECTOR_INDEXED_RODS independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
