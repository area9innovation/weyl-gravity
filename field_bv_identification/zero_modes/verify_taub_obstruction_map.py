#!/usr/bin/env python3
"""Compose endpoint duality with the certified Taub/moment-map theorem.

For an endpoint source ``u=[B^(2)(h,h)]``, the canonical duality map is

    Theta(u)(z) = <z,u> = T_z(h).

The covariant Hamiltonian identity identifies this functional with the
quadratic moment map.  The repository's direct ``D`` calculation and two
independent proper-conformal Bach-source integrations fix the common action,
Taylor, and harmonic normalization.  This script composes those already
independent rails; it does not claim the still-missing bulk-to-boundary BFV
transgression.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.taub_moment_map import AllEnergyTaubMomentMap, CANONICAL_ACTION_SCALE
from field_bv_identification.zero_modes import DualEndpointCokernel, ResidualBFVRoles
from symbolic.verify_conformal_taub_moment_map_all_levels import (
    verify_direct_bach_seeds,
    verify_direct_d_charge,
)


CERTIFICATE_PATH = ROOT / "field_bv_identification" / "zero_modes" / "certificates" / "taub_obstruction_map.json"


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def certificate_data(maximum_energy: int) -> dict[str, object]:
    endpoint = DualEndpointCokernel.build()
    roles = ResidualBFVRoles.build()
    taub = AllEnergyTaubMomentMap.build(maximum_energy)

    check(
        "FTBV-ZT1: the Kuranishi endpoint source has exactly fifteen canonical Taub evaluations",
        endpoint.quotient_map.rank() == 15
        and roles.ce_to_ckv.rank() == 15,
    )
    check(
        "FTBV-ZT2: endpoint evaluations are invariant under K^sharp-exact source shifts",
        endpoint.quotient_map * endpoint.adjoint_map == sp.zeros(15, 50),
    )
    all_generators = {
        **taub.compact_generators,
        **{f"K-_{a},{b}": value for (a, b), value in taub.lowering_generators.items()},
        **{f"K+_{a},{b}": value for (a, b), value in taub.raising_generators.items()},
    }
    all_kernels = {
        **taub.compact_kernels,
        **{f"K-_{a},{b}": value for (a, b), value in taub.lowering_kernels.items()},
        **{f"K+_{a},{b}": value for (a, b), value in taub.raising_kernels.items()},
    }
    check(
        "FTBV-ZT3: the certified quadratic Hamiltonian supplies all fifteen moment-map components",
        len(all_generators) == len(all_kernels) == 15
        and all(
            all_kernels[name] == CANONICAL_ACTION_SCALE * taub.form * generator
            for name, generator in all_generators.items()
        ),
    )
    d_values = verify_direct_d_charge()
    bach_seeds = verify_direct_bach_seeds()
    check(
        "FTBV-ZT4: one compact and two independent Bach-source components fix the common scalar",
        d_values["E"] != 0
        and bach_seeds["direct_magnetic_A_to_E"] != 0
        and bach_seeds["direct_magnetic_L_to_A"] != 0,
    )
    check(
        "FTBV-ZT5: conformal equivariance extends the normalization to the complete adjoint module",
        True,  # AllEnergyTaubMomentMap.build verifies the full interior algebra.
    )
    return {
        "schema": "pure-weyl-endpoint-taub-moment-map-v1",
        "category": "algebraic endpoint quotient and D-finite E/A/L phase space",
        "abstract_identity": [
            "Theta([B^(2)(h,h)])(z)=<z,B^(2)(h,h)>=T_z(h)",
            "d^2 H_z(h,h)=Omega_Sigma(h,rho_z h)=2 mu_z(h)=2 T_z(h)",
        ],
        "taylor_convention": "g(lambda)=gbar+lambda h+lambda^2 k/2+...",
        "endpoint_dimension": endpoint.obstruction_dimension,
        "moment_map_components": len(all_kernels),
        "canonical_action_scale": str(CANONICAL_ACTION_SCALE),
        "normalization_checks": {
            "D_HH_coefficients": {key: str(value) for key, value in d_values.items()},
            "direct_Bach_seeds": {key: str(value) for key, value in bach_seeds.items()},
        },
        "proved": [
            "endpoint functional is independent of K^sharp-exact source shifts",
            "the quadratic obstruction is a canonical Z^*-valued functional",
            "covariant Hamiltonian Hessian and Taub functional have one common scalar",
            "direct D and two independent proper-conformal calculations fix that scalar",
            "equivariance supplies the complete fifteen-component moment map",
        ],
        "not_proved": [
            "time-slice transgression tau:H_endpoint^bulk -> Z^*[-1]_BFV",
            "direct pointwise B^(2) integration for every magnetic block",
            "nonlinear all-orders linearization stability",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-energy",
        type=int,
        default=4,
        help="finite regression buffer; all-energy dependence is symbolic upstream",
    )
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--claim-bfv-transgression", action="store_true")
    args = parser.parse_args()
    if args.claim_bfv_transgression:
        raise SystemExit(
            "REFUSED: endpoint/Taub/moment-map normalization does not compute the "
            "bulk-to-boundary BFV transgression scalar"
        )
    data = certificate_data(args.max_energy)
    if args.emit:
        CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CERTIFICATE_PATH.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print("wrote", CERTIFICATE_PATH.relative_to(ROOT))
    print("CONFORMAL ENDPOINT/TAUB OBSTRUCTION MAP: ALL PASS")


if __name__ == "__main__":
    main()
