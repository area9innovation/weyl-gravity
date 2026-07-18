#!/usr/bin/env python3
"""Independently verify the generated Berger recoil graph-norm gate."""

import json

from closed_universe_observers.generate_berger_recoil_chain_graph_norm_gate import (
    CERTIFICATE,
    build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert value["spectral_typing"]["massive_inverse_candidate"][1][1] == "1/m2"
    assert value["route_disposition"]["factorwise_L2_dual_bound_from_current_tail"] == "NO_CERTIFIED_MAP"
    assert value["route_disposition"]["full_recoil_operator_unbounded_theorem"] == "NOT_CLAIMED"
    assert all(row["detected"] for row in value["mutation_results"])
    print("Berger recoil-chain graph-norm gate verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
