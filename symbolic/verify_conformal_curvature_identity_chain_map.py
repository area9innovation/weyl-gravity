#!/usr/bin/env python3
"""Verify the auxiliary-to-curvature identity chain map."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_retract.curvature_identity_chain_map import (
    CurvatureAuxiliaryIdentityChainMap,
)


CERTIFICATE_DIR = ROOT / "covariant_completion" / "certificates"
OUTPUT = CERTIFICATE_DIR / "curved_curvature_identity_chain_map.json"
EQUATION = CERTIFICATE_DIR / "curved_curvature_auxiliary_chain_map.json"
RETRACT = CERTIFICATE_DIR / "curved_chain_maps.json"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _must_fail(candidate: CurvatureAuxiliaryIdentityChainMap, label: str) -> None:
    try:
        candidate.verify()
    except AssertionError:
        return
    raise AssertionError(f"negative guard did not fail: {label}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    chain_map = CurvatureAuxiliaryIdentityChainMap.build()
    certificate = chain_map.certificate(
        equation_certificate=_load(EQUATION),
        retract_certificate=_load(RETRACT),
    )
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    if args.guards:
        if not certificate["second_chain_relation_exact"]:
            raise AssertionError("identity chain relation regressed")
        if certificate["coefficientwise_identity_square"]["defect_counts"] != [
            0,
            0,
            0,
            0,
            0,
        ]:
            raise AssertionError("a derivative/zeroth identity table regressed")
        if certificate["B_identity"]["maximum_order"] != 0:
            raise AssertionError("B_identity ceased to be pointwise")
        if certificate["B_identity"]["nonzero_coefficients"] != 4:
            raise AssertionError("B_identity coefficient coverage drifted")
        if certificate["mapping_cylinder_cotangent_kernel_assembled"]:
            raise AssertionError("mapping cylinder was assembled prematurely")
        if certificate["warranted_atomic_flags"] or certificate[
            "status_flags_promoted"
        ]:
            raise AssertionError("identity-map producer promoted a status flag")

        bad_map = sp.MutableDenseMatrix(chain_map.auxiliary_identity_map)
        bad_map[12, 4] += 1
        _must_fail(
            replace(chain_map, auxiliary_identity_map=bad_map),
            "identity coefficient mutation",
        )
        bad_defects = list(chain_map.metric_chain_defects)
        bad_defects[0] = bad_defects[0].copy()
        bad_defects[0][0, 0] = 1
        _must_fail(
            replace(chain_map, metric_chain_defects=tuple(bad_defects)),
            "temporal chain-square mutation",
        )
        print("CURVATURE IDENTITY CHAIN-MAP GUARDS: 8/8 PASS")

    print(
        "CURVATURE IDENTITY CHAIN MAP: N A=B C EXACT; "
        "MAPPING-CYLINDER ASSEMBLY REMAINS SEPARATE"
    )


if __name__ == "__main__":
    main()
