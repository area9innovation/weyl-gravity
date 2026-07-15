"""Exact retarded-radial indicial analysis for the flat TT Bach channel.

Each Cartesian TT polarization obeys ``Box^2 phi=0`` by the imported flat
operator certificate.  This module expands a scalar amplitude in retarded
coordinates,

    phi = sum_n r^(-p-n) f_n(u) Y_L(x),

where ``Delta_S2 Y_L=-L Y_L``, and derives the wave and biwave recursions
exactly.  It identifies the radiative indicial roots without pretending to
construct the complete tensor Bondi/BV complex.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge" / "certificates" / "bondi_bach_indicial.json"
FLAT_TT_INPUT = ROOT / "bridge" / "certificates" / "flat_tt_bach_operator.json"


class BondiBachIndicialError(RuntimeError):
    """Raised when an indicial or imported-scope identity fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise BondiBachIndicialError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wave_coefficients(weight: sp.Expr, angular: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
    """Return coefficients of ``r^(-s-1) f'`` and ``r^(-s-2) f``."""

    return 2 * (weight - 1), weight * (weight - 1) - angular


def biwave_coefficients(
    weight: sp.Expr, angular: sp.Expr
) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    """Return the ``f''``, ``f'``, and ``f`` coefficients in ``Box^2``."""

    a0, b0 = wave_coefficients(weight, angular)
    a1, b1 = wave_coefficients(weight + 1, angular)
    a2, b2 = wave_coefficients(weight + 2, angular)
    return (
        sp.factor(a0 * a1),
        sp.factor(a0 * b1 + b0 * a2),
        sp.factor(b0 * b2),
    )


def _direct_wave_check() -> dict[str, str]:
    u, r = sp.symbols("u r", positive=True, real=True)
    weight, angular = sp.symbols("s L", real=True)
    f = sp.Function("f")(u)
    radial = r ** (-weight) * f

    # Box=-2 d_u d_r+d_r^2+(2/r)(d_r-d_u)+(1/r^2) Delta_S2.
    direct = sp.factor(
        -2 * sp.diff(radial, u, r)
        + sp.diff(radial, r, 2)
        + 2 * (sp.diff(radial, r) - sp.diff(radial, u)) / r
        - angular * radial / r**2
    )
    a, b = wave_coefficients(weight, angular)
    expected = sp.factor(
        a * r ** (-weight - 1) * sp.diff(f, u)
        + b * r ** (-weight - 2) * f
    )
    _require(sp.simplify(direct - expected) == 0, "retarded wave formula is wrong")
    return {
        "wave_operator": "-2 d_u d_r+d_r^2+(2/r)(d_r-d_u)+(1/r^2) Delta_S2",
        "action": (
            "Box[r^(-s)fY]=2(s-1)r^(-s-1)f'Y+"
            "[s(s-1)-L]r^(-s-2)fY"
        ),
    }


def build_certificate() -> dict[str, Any]:
    flat = _load(FLAT_TT_INPUT)
    _require(
        flat.get("operator_identity") == "B_1(h_TT)=-(1/4) Box^2 h_TT",
        "flat TT Bach premise is missing",
    )
    _require(flat.get("helicity_commutator_zero") is True, "helicity premise failed")

    p, angular = sp.symbols("p L", real=True)
    c_second, c_first, c_zero = biwave_coefficients(p, angular)
    _require(c_second == 4 * p * (p - 1), "wrong radiative indicial polynomial")
    roots = sp.solve(c_second, p)
    _require(roots == [0, 1], "radiative indicial roots are not p=0,1")

    # The wave constraint on the p=1 series begins at r^-3:
    # 2 f_1' - L f_0 = 0.  The p=0 series instead has
    # Box phi=-2 r^-1 f_0' - L r^-2 f_0+..., so radiative f_0 is non-Einstein.
    a_one_next, _ = wave_coefficients(sp.Integer(2), angular)
    _, b_one = wave_coefficients(sp.Integer(1), angular)
    _require(a_one_next == 2 and b_one == -angular, "wrong p=1 wave constraint")
    a_zero, b_zero = wave_coefficients(sp.Integer(0), angular)
    _require(a_zero == -2 and b_zero == -angular, "wrong p=0 wave image")

    p_zero_biwave = biwave_coefficients(sp.Integer(0), angular)
    p_one_biwave = biwave_coefficients(sp.Integer(1), angular)
    _require(
        p_zero_biwave == (0, 0, angular * (angular - 2)),
        "wrong p=0 biwave coefficients",
    )
    _require(
        p_one_biwave == (0, -4 * angular, angular * (angular - 6)),
        "wrong p=1 biwave coefficients",
    )

    return {
        "schema": "pure-weyl-bondi-bach-indicial-v1",
        "result_id": "BONDI_BACH_RADIAL_INDICIAL_ROOTS",
        "result_state": "PROVED_REDUCED_RADIATIVE_CHANNEL",
        "source_commit": "69fa30d57db708627e86687289c1b5d241565f5e",
        "dependency_tags": ["REDUCED-MODE"],
        "input": {
            "path": str(FLAT_TT_INPUT.relative_to(ROOT)),
            "sha256": _sha256(FLAT_TT_INPUT),
            "operator": flat["operator_identity"],
        },
        "retarded_coordinates": {
            "metric": "ds^2=-du^2-2 du dr+r^2 q_AB dx^A dx^B",
            "angular_eigenmode": "Delta_S2 Y_L=-L Y_L",
            "series": "phi=sum_(n>=0) r^(-p-n) f_n(u) Y_L(x)",
            **_direct_wave_check(),
        },
        "biwave_single_term": {
            "f_second_coefficient_at_r^(-p-2)": str(c_second),
            "f_first_coefficient_at_r^(-p-3)": str(c_first),
            "f_coefficient_at_r^(-p-4)": str(c_zero),
        },
        "series_recursions": {
            "index_convention": "f_j=0 for j<0; s_j=p+j",
            "wave": (
                "2(s_j-1) d_u f_j+"
                "[s_(j-1)(s_(j-1)-1)-L] f_(j-1)=0"
            ),
            "biwave": (
                "4 s_j(s_j-1) d_u^2 f_j+"
                "4 s_(j-1)[s_(j-1)^2-1-L] d_u f_(j-1)+"
                "[s_(j-2)(s_(j-2)-1)-L]"
                "[(s_(j-2)+1)(s_(j-2)+2)-L] f_(j-2)=0"
            ),
            "leading_radiative_equation": "4p(p-1) d_u^2 f_0=0",
        },
        "radiative_indicial_polynomial": str(c_second),
        "radiative_indicial_roots": [str(root) for root in roots],
        "p1_einstein_falloff": {
            "cartesian_amplitude": "phi=r^-1 f_0(u,x)+O(r^-2)",
            "bondi_angular_metric": "h_AB=r C_AB+O(1)",
            "unphysical_angular_metric": "h_tilde_AB=r^-1 C_AB+O(r^-2)",
            "boundary_metric_changed": False,
            "leading_wave_constraint": "2 d_u f_1-L f_0=0",
            "interpretation": "ordinary Einstein radiative falloff after the wave constraint",
        },
        "p0_extra_bach_falloff": {
            "cartesian_amplitude": "phi=f_0(u,x)+O(r^-1)",
            "bondi_angular_metric": "h_AB=r^2 A_AB+O(r)",
            "unphysical_angular_metric": "h_tilde_AB=A_AB+O(r^-1)",
            "boundary_metric_changed": True,
            "wave_image": "Box phi=-2 r^-1 d_u f_0-L r^-2 f_0+O(r^-3 from f_1)",
            "non_einstein_if": "d_u f_0 is nonzero",
            "interpretation": "additional leading Bach radiative branch",
        },
        "kinematic_boundary_selection": {
            "condition": "fix h_tilde_AB at null infinity, equivalently require Cartesian TT h=O(r^-1)",
            "effect": "excludes the p=0 leading boundary-metric deformation while retaining p=1 radiation",
            "locality": "radial falloff condition at null infinity, not a future endpoint condition",
            "status": "KINEMATIC_ONLY",
        },
        "exceptional_and_coupled_sectors": [
            "angular values L=0 and L=2 make displayed subleading scalar coefficients degenerate",
            "TT constraints couple angular components and must be imposed in the full tensor recursion",
            "soft/memory and Coulombic data are not exhausted by the p=0 scalar-amplitude branch",
        ],
        "claim_flags": {
            "radiative_indicial_roots_classified": True,
            "p0_branch_changes_unphysical_boundary_metric": True,
            "fixed_boundary_metric_excludes_p0_kinematically": True,
            "full_tensor_bondi_recursion_constructed": False,
            "boundary_condition_preserved_by_causal_green_operators": False,
            "p0_branch_proved_non_gauge": False,
            "all_extra_weyl_channels_classified": False,
            "einstein_scattering_sector_recovered": False,
        },
        "scope_guards": [
            "exact for the scalar amplitude of each flat Cartesian TT polarization",
            "leading radiative indicial roots only",
            "not the complete tensor Bondi gauge or BV complex",
            "no surface-charge or symplectic-flux classification",
            "no nonlinear or global scattering theorem",
        ],
        "verification_command": (
            "python3 -m bridge.einstein_sector.bondi_bach_indicial --verify "
            "bridge/certificates/bondi_bach_indicial.json"
        ),
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"certificate is stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(
            json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
