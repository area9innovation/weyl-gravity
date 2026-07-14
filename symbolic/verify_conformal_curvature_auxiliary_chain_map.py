#!/usr/bin/env python3
"""Verify the coefficientwise auxiliary-to-curvature equation chain map."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_retract.curvature_auxiliary_chain_map import (
    CurvatureAuxiliaryEquationChainMap,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_curvature_auxiliary_chain_map.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    chain_map = CurvatureAuxiliaryEquationChainMap.build(workers=args.workers)
    certificate = chain_map.certificate()
    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", CERTIFICATE.relative_to(ROOT))

    if args.guards:
        if not certificate["first_chain_relation_exact"]:
            raise AssertionError("first chain relation regressed")
        if certificate["exhaustive_jet_certificate"][
            "E_curv_T_minus_H_Bach_defect"
        ]:
            raise AssertionError("exhaustive curvature factorization regressed")
        if not certificate["differential_ac_generation"]["included"]:
            raise AssertionError("differential a,c generators were omitted")
        if certificate["B_identity_emitted"]:
            raise AssertionError("identity map was inferred from equation data")
        if certificate["mapping_cylinder_cotangent_kernel_assembled"]:
            raise AssertionError("cotangent cylinder was assembled too early")
        if certificate["warranted_atomic_flags"] or certificate["status_flags_promoted"]:
            raise AssertionError("chain-map audit promoted a project flag")
        print("CURVATURE-AUXILIARY CHAIN-MAP GUARDS: 6/6 PASS")

    print(
        "CURVATURE-AUXILIARY CHAIN MAP: EQUATION SQUARE EXACT; "
        "IDENTITY SQUARE OPEN"
    )


if __name__ == "__main__":
    main()
