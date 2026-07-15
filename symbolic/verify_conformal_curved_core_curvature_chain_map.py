#!/usr/bin/env python3
"""Verify and emit the corrected curved metric-core curvature chain map."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_retract.curved_core_curvature_chain_map import (  # noqa: E402
    CurvedCoreCurvatureChainMap,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
OUTPUT = CERTIFICATES / "curved_core_curvature_chain_map.json"


def _load(name: str) -> dict[str, object]:
    return json.loads((CERTIFICATES / name).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    result = CurvedCoreCurvatureChainMap.build()
    certificate = result.certificate(
        equation_certificate=_load("curved_curvature_auxiliary_chain_map.json"),
        curved_retract_certificate=_load("curved_deformation_retract_status.json"),
    )

    if args.guards:
        bad_equation = _load("curved_curvature_auxiliary_chain_map.json")
        bad_equation["A_equation"]["sha256"] = "0" * 64
        try:
            result.certificate(
                equation_certificate=bad_equation,
                curved_retract_certificate=_load(
                    "curved_deformation_retract_status.json"
                ),
            )
        except AssertionError:
            pass
        else:
            raise AssertionError("a drifted curved A table was accepted")

        bad_retract = _load("curved_deformation_retract_status.json")
        bad_retract["promotion_criteria"]["curved_p_is_chain_map"] = False
        try:
            result.certificate(
                equation_certificate=_load(
                    "curved_curvature_auxiliary_chain_map.json"
                ),
                curved_retract_certificate=bad_retract,
            )
        except AssertionError:
            pass
        else:
            raise AssertionError("an open curved projection was accepted")

        # The derivative part of p_I is allowed only in its fifth core row,
        # and B_core must annihilate it coefficientwise.
        p_identity = dict(result.identity_projection_coefficients)
        for multiindex, matrix in p_identity.items():
            if sum(multiindex):
                mutated = matrix.copy()
                mutated[0, 0] = 1
                if result.core_identity_attachment * mutated == matrix.zeros(14, 9):
                    raise AssertionError("p_I derivative-image guard is ineffective")

    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    print(
        "curved core curvature chain map: "
        "A=A_core p_E, B=B_core p_I, both lifted squares exact"
    )


if __name__ == "__main__":
    main()
