#!/usr/bin/env python3
"""Audit bulk endpoint, residual ghost, BFV momentum, and constraint roles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from field_bv_identification.zero_modes import ResidualBFVRoles


CERTIFICATE_PATH = ROOT / "field_bv_identification" / "zero_modes" / "certificates" / "residual_bfv_roles.json"


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def certificate_data() -> dict[str, object]:
    audit = ResidualBFVRoles.build()
    by_symbol = {role.symbol: role for role in audit.roles}
    check(
        "FTBV-ZR1: local nonzero ghosts plus one residual ghost copy exhaust G",
        audit.ghost_replacement_basis.rank() == 65,
    )
    check(
        "FTBV-ZR2: exact endpoint directions plus one obstruction quotient exhaust I",
        audit.endpoint_decomposition_basis.rank() == 65,
    )
    check(
        "FTBV-ZR3: the residual BFV cotangent pair is exactly 15+15 dimensional",
        audit.ghost_symplectic_form.shape == (30, 30)
        and audit.ghost_symplectic_form.rank() == 30
        and audit.ghost_symplectic_form.T == -audit.ghost_symplectic_form,
    )
    check(
        "FTBV-ZR4: endpoint, momentum, and moment-map value are not conflated",
        by_symbol["b_a"].is_bfv_coordinate
        and not by_symbol["[u]"].is_bfv_coordinate
        and not by_symbol["mu_a"].is_bfv_coordinate,
    )
    check(
        "FTBV-ZR5: the missing one-scalar transgression remains explicit",
        "scalar lambda open" in by_symbol["b_a"].transgression_relation,
    )
    return {
        "schema": "pure-weyl-residual-bfv-role-audit-v1",
        "category": "bulk zero-mode extraction before time-slice transgression",
        "roles": [role.__dict__ for role in audit.roles],
        "counts": {
            "local_nonzero_ghosts": 50,
            "residual_ghosts": 15,
            "bulk_endpoint_exact_directions": 50,
            "bulk_endpoint_obstruction_quotient": 15,
            "BFV_ghost_momenta": 15,
            "moment_map_coordinate_count": 0,
        },
        "identities": [
            "G = G_perp direct-sum Z",
            "I = im K^sharp direct-sum H_endpoint",
            "Omega_gh = delta b_a wedge delta c^a is nondegenerate",
            "mu is a Z^*-valued function, not a third coordinate copy",
        ],
        "open": [
            "tau:H_endpoint^bulk -> Z^*[-1]_BFV",
            "the scalar lambda in tau=lambda Theta",
            "the orientation/sign fixed by the time-slice boundary form",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--claim-no-duplication-transfer", action="store_true")
    args = parser.parse_args()
    if args.claim_no_duplication_transfer:
        raise SystemExit(
            "REFUSED: dimensions and roles are certified, but no-duplication as a "
            "BV-to-BFV transfer theorem requires the missing scalar transgression"
        )
    data = certificate_data()
    if args.emit:
        CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CERTIFICATE_PATH.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print("wrote", CERTIFICATE_PATH.relative_to(ROOT))
    print("CONFORMAL RESIDUAL BFV ROLE AUDIT: ALL PASS")


if __name__ == "__main__":
    main()
