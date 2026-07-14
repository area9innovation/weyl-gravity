#!/usr/bin/env python3
"""Verify the degree-minus-one curvature graph chain square."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_retract.curvature_state_gauge_chain_map import (
    CurvatureStateGaugeChainMap,
)


OUTPUT = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_curvature_state_gauge_chain_map.json"
)


def main() -> int:
    certificate = CurvatureStateGaugeChainMap.build().certificate()
    OUTPUT.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    jets = certificate["exhaustive_jet_certificate"]
    checks = {
        "full_nine_ghost_coverage": (
            jets["diffeomorphism_jets"] == 140
            and jets["Weyl_scalar_jets"] == 15
            and jets["boost_components"] == 4
        ),
        "diffeomorphism_square_exact": jets["diffeomorphism_defects"] == 0,
        "Weyl_scalar_square_exact": jets["Weyl_scalar_defects"] == 0,
        "auxiliary_metric_block_exact": jets["auxiliary_metric_block_defects"] == 0,
        "T_state_K_aux_exact": certificate["T_state_K_aux_exact"],
        "support_local": certificate["support_local"],
    }
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(f"certificate: {OUTPUT.relative_to(ROOT)}")
    print(
        "CURVATURE STATE-GAUGE CHAIN-MAP GUARDS: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
