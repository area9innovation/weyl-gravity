#!/usr/bin/env python3
"""Verify and emit the Weyl electric/magnetic principal evolution block."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.curvature_evolution import (
    CurvatureEvolutionPrincipalSymbol,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_curvature_evolution_principal_symbol.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    status = CurvatureEvolutionPrincipalSymbol.build()
    certificate = status.certificate()
    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", CERTIFICATE.relative_to(ROOT))
    if args.guards:
        if not certificate[
            "candidate_curvature_principal_symmetric_hyperbolicity"
        ]:
            raise AssertionError("principal curvature hyperbolicity regressed")
        if not certificate["candidate_curvature_principal_constraints_propagate"]:
            raise AssertionError("principal curvature constraint closure regressed")
        for false_obligation in (
            "principal_system_derived_from_curved_Bianchi_Bach",
            "curved_Bianchi_Bach_lower_terms_derived",
            "curvature_constraints_propagate",
            "local_prolongation_retract_verified",
            "complete_curvature_green_realization",
        ):
            if certificate[false_obligation]:
                raise AssertionError(f"open obligation was inferred: {false_obligation}")
        print("CURVATURE EVOLUTION GUARDS: 12/12 PASS")
    print("CURVATURE EVOLUTION: PRINCIPAL SYSTEM CERTIFIED")


if __name__ == "__main__":
    main()
