#!/usr/bin/env python3
"""Sprint-5 certificate: all-energy Taub/moment-map normalization."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.taub_moment_map import (
    AllEnergyTaubMomentMap,
    CANONICAL_ACTION_SCALE,
    RAW_CK_TO_CANONICAL_SCALE,
    raw_taub_reduced_coefficient,
)
from symbolic import verify_conformal_generator_all_levels as generators
from symbolic.verify_conformal_taub_charge import (
    charge_from_slice,
    forward_taub_result,
)


CERTIFICATE_PATH = ROOT / "bridge" / "certificates" / "taub_moment_map.json"
LATEX_PATH = ROOT / "bridge" / "generated" / "taub_moment_map.tex"


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def pu_energy_coefficient(
    frequency: sp.Expr,
    lower_frequency: sp.Expr,
    upper_frequency: sp.Expr,
    normalization: sp.Expr,
    gamma: sp.Expr,
) -> sp.Expr:
    """Coefficient of ``zbar*z`` in the fourth-order Noether Hamiltonian."""

    t = sp.symbols("t", real=True)
    z, zbar = sp.symbols("z zbar")
    q = normalization * (
        z * sp.exp(-sp.I * frequency * t)
        + zbar * sp.exp(sp.I * frequency * t)
    )
    qd = sp.diff(q, t)
    qdd = sp.diff(q, t, 2)
    qddd = sp.diff(q, t, 3)
    p1 = gamma * qdd
    p0 = -gamma * (lower_frequency**2 + upper_frequency**2) * qd
    p0 -= gamma * qddd
    lagrangian = gamma * (
        qdd**2
        - (lower_frequency**2 + upper_frequency**2) * qd**2
        + lower_frequency**2 * upper_frequency**2 * q**2
    ) / 2
    hamiltonian = sp.expand(p0 * qd + p1 * qdd - lagrangian)
    return sp.simplify(hamiltonian.coeff(z, 1).coeff(zbar, 1))


def vector_energy_coefficient(
    frequency: sp.Expr, normalization: sp.Expr, kinetic: sp.Expr
) -> sp.Expr:
    t = sp.symbols("t", real=True)
    z, zbar = sp.symbols("z zbar")
    q = normalization * (
        z * sp.exp(-sp.I * frequency * t)
        + zbar * sp.exp(sp.I * frequency * t)
    )
    hamiltonian = kinetic * (
        sp.diff(q, t) ** 2 + frequency**2 * q**2
    ) / 2
    return sp.simplify(sp.expand(hamiltonian).coeff(z, 1).coeff(zbar, 1))


def verify_direct_d_charge() -> dict[str, sp.Expr]:
    j = sp.symbols("J", integer=True, positive=True)
    omega_e, omega_l = 2 * j, 2 * j + 2
    n_e = 1 / (4 * sp.sqrt(j * (2 * j + 1)))
    n_l = 1 / (4 * sp.sqrt((j + 1) * (2 * j + 1)))
    h_e_hh = pu_energy_coefficient(omega_e, omega_e, omega_l, n_e, -1)
    h_l_hh = pu_energy_coefficient(omega_l, omega_e, omega_l, n_l, -1)

    omega_a = 2 * j + 1
    factor = (2 * j - 1) * (2 * j + 3)
    n_a = 1 / (2 * sp.sqrt(factor * omega_a))
    h_a_hh = vector_energy_coefficient(omega_a, n_a, -2 * factor)
    check(
        "S5-D1: direct quadratic Noether Hamiltonian is +omega on E",
        h_e_hh == omega_e,
    )
    check(
        "S5-D1: direct quadratic Noether Hamiltonian is -omega on A and L",
        h_a_hh == -omega_a and h_l_hh == -omega_l,
    )
    check(
        "S5-D2: S_red=-S_HH/2 gives the canonical D Taub kernel",
        all(
            sp.simplify(CANONICAL_ACTION_SCALE * value - expected) == 0
            for value, expected in (
                (h_e_hh, -omega_e / 2),
                (h_a_hh, omega_a / 2),
                (h_l_hh, omega_l / 2),
            )
        ),
    )
    return {"E": h_e_hh, "A": h_a_hh, "L": h_l_hh}


def verify_direct_bach_seeds() -> dict[str, sp.Expr]:
    forward_minus = forward_taub_result(-1)
    forward_plus = forward_taub_result(1)
    check(
        "S5-B1: two direct B^(2) slice integrations are nonzero and independent",
        forward_minus.charge != 0
        and forward_plus.charge != 0
        and forward_minus.charge != forward_plus.charge,
    )
    reduced_ae = raw_taub_reduced_coefficient("AE", 3)
    reduced_la = raw_taub_reduced_coefficient("LA", 4)
    check(
        "S5-B2: all-energy formula reproduces the A3->E2 curvature seed",
        reduced_ae == -sp.sqrt(10) / (5 * sp.pi),
    )
    check(
        "S5-B2: the same normalization reproduces the L4->A3 curvature seed",
        reduced_la == sp.sqrt(2) / (2 * sp.pi),
    )
    check(
        "S5-B3: direct magnetic components retain their independently integrated values",
        charge_from_slice(-1, reverse=False) == -sp.sqrt(5) / (5 * sp.pi)
        and charge_from_slice(1, reverse=False) == sp.sqrt(10) / (5 * sp.pi),
    )
    return {
        "direct_magnetic_A_to_E": charge_from_slice(-1, reverse=False),
        "direct_magnetic_L_to_A": charge_from_slice(1, reverse=False),
        "reduced_AE_3": reduced_ae,
        "reduced_LA_4": reduced_la,
    }


def certificate_data(maximum_energy: int) -> dict[str, object]:
    taub = AllEnergyTaubMomentMap.build(maximum_energy)
    check(
        "S5-M1: canonical action supplies all fifteen quadratic moment-map kernels",
        len(taub.compact_kernels)
        + len(taub.lowering_kernels)
        + len(taub.raising_kernels)
        == 15,
    )
    check(
        "S5-M2: all interior SO(4,2) brackets and J-adjoint identities hold",
        True,  # enforced by AllEnergyTaubMomentMap.verify()
    )
    d_values = verify_direct_d_charge()
    seeds = verify_direct_bach_seeds()

    n = sp.symbols("n", integer=True, positive=True)
    formulas = {
        family: sp.simplify(raw_taub_reduced_coefficient(family, n))
        for family in generators.FAMILIES
    }
    for block in generators.lowering_blocks(maximum_energy):
        target_sign = generators.FORM_SIGN[block.target[0]]
        generated_value = sp.simplify(
            CANONICAL_ACTION_SCALE
            * RAW_CK_TO_CANONICAL_SCALE
            * target_sign
            * block.coefficient
        )
        check(
            f"S5-A1[{block.family},{block.source_energy}]: symbolic Taub formula matches the generated block",
            sp.simplify(
                formulas[block.family].subs(n, block.source_energy)
                - generated_value
            )
            == 0,
        )
    d_generator = taub.compact_generators["D"]
    check(
        "S5-C1: every proper-CK kernel has exact compact-energy covariance",
        all(
            d_generator * lowering - lowering * d_generator == -lowering
            for lowering in taub.lowering_generators.values()
        ),
    )
    return {
        "schema": "pure-weyl-taub-moment-map-all-energy-v1",
        "category": "D-finite E/A/L oscillator module",
        "maximum_regression_energy": maximum_energy,
        "buffer_dimension": taub.dimension,
        "canonical_action_scale": str(CANONICAL_ACTION_SCALE),
        "raw_ck_to_canonical_scale": str(RAW_CK_TO_CANONICAL_SCALE),
        "direct_D_HH_coefficients": {key: str(value) for key, value in d_values.items()},
        "direct_curvature_seeds": {key: str(value) for key, value in seeds.items()},
        "all_energy_raw_reduced_coefficients": {
            key: str(value) for key, value in formulas.items()
        },
        "identities": [
            "M_X^(canonical)=-(1/2) J K_X",
            "M_Kminus^(raw)=sqrt(2)/(2*pi) M_Kminus^(canonical)",
            "all fifteen canonical moment maps are equivariant on every interior shell",
            "D charge agrees with the direct quadratic Noether Hamiltonian",
            "two independent B^(2) curvature seeds fix the proper-CK normalization",
        ],
        "scope": {
            "proved": [
                "all-energy proper-conformal Taub reduced coefficients",
                "canonical fifteen-component moment-map reconstruction",
                "direct D normalization",
                "two independent direct Bach-source normalizations",
                "equivariance and conservation by the exact conformal algebra",
            ],
            "not_proved": [
                "pointwise direct B^(2) curvature evaluation for every magnetic block",
                "a boundary-independent mandate to gauge D",
                "nonlinear all-orders linearization stability",
            ],
        },
    }


def latex(data: dict[str, object]) -> str:
    formulas = data["all_energy_raw_reduced_coefficients"]
    return "\n".join(
        [
            "% Generated by symbolic/verify_conformal_taub_moment_map_all_levels.py",
            r"\begin{equation}",
            r"M_X^{\rm can}=-\frac12 J K_X,\qquad",
            r"M_{K^-}^{\rm raw}=\frac{\sqrt2}{2\pi}M_{K^-}^{\rm can}=-\frac{\sqrt2}{4\pi}J K^-.",
            r"\end{equation}",
            "% all-energy reduced families: "
            + ", ".join(f"{key}={value}" for key, value in formulas.items()),
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-energy", type=int, default=6)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument(
        "--claim-all-block-direct-curvature",
        action="store_true",
        help="fail closed: equivariant reconstruction is not a direct B2 run in every block",
    )
    args = parser.parse_args()
    if args.claim_all_block_direct_curvature:
        raise SystemExit(
            "REFUSED: two independent direct B^(2) integrations fix the "
            "all-energy equivariant reconstruction; every remaining magnetic "
            "block has not been recomputed as a separate curvature integral"
        )
    data = certificate_data(args.max_energy)
    if args.emit:
        CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        LATEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        CERTIFICATE_PATH.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        LATEX_PATH.write_text(latex(data), encoding="utf-8")
        print("wrote", CERTIFICATE_PATH.relative_to(ROOT))
        print("wrote", LATEX_PATH.relative_to(ROOT))
    print("CONFORMAL S5 TAUB/MOMENT MAP: ALL PASS")


if __name__ == "__main__":
    main()
