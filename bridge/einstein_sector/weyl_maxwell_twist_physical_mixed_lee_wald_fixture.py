"""Direct mixed current for axial ell=1 twist and physical modes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_exceptional_global_symplectic import _twist_variation
from bridge.einstein_sector.einstein_maxwell_radiative_lee_wald_fixture import _axial_variation
from bridge.einstein_sector.weyl_maxwell_lee_wald_current import weyl_maxwell_current_time

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/weyl_maxwell_twist_physical_mixed_lee_wald_fixture.json"


class MixedCurrentFixtureError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MixedCurrentFixtureError(message)


def _direct_fixture() -> dict[str, Any]:
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    frequency = sp.symbols("omega", real=True)
    twist_position, twist_velocity, physical = sp.symbols("A B p", real=True)
    sine = sp.sin(theta)
    harmonic = sp.cos(theta)
    axial_one_form = -sine * sp.diff(harmonic, theta)
    wave = sp.exp(-sp.I * frequency * time)
    metric = sp.diag(-1, 1, 1, sine**2)
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine

    density = weyl_maxwell_current_time(
        metric,
        field,
        _twist_variation(
            twist_position,
            twist_velocity,
            time,
            harmonic,
            axial_one_form,
        ),
        _axial_variation(
            physical,
            physical,
            wave,
            harmonic,
            axial_one_form,
            sp.Integer(0),
            frequency,
        ),
        (time, space, theta, azimuth),
        sp.Integer(3),
    )
    # Remove the common non-angular wave before trigonometric expansion. This
    # is an exact factorization, not an evaluation at a time slice.
    angular_density = sp.factor(sp.cancel(density / wave))
    _require(not angular_density.has(sp.exp), "wave factor did not separate")
    integrated = sp.factor(
        2
        * sp.pi
        * sp.integrate(
            sp.trigsimp(sp.expand_trig(angular_density), method="fu"),
            (theta, 0, sp.pi),
        )
        * wave
    )
    expected = (
        -2
        * sp.I
        * sp.pi
        * frequency
        * physical
        * (frequency**2 - 4)
        * (
            frequency * (twist_position + twist_velocity * time)
            - sp.I * twist_velocity
        )
        * wave
    )
    _require(sp.simplify(integrated - expected) == 0, "mixed current factorization changed")
    quotient = sp.cancel(integrated / (frequency**2 - 4))
    _require(not sp.cancel(quotient).has(theta), "angular coordinate survived quotient")
    on_shell_remainder = sp.rem(
        sp.Poly(sp.expand(integrated / wave), frequency),
        sp.Poly(frequency**2 - 4, frequency),
    ).as_expr()
    _require(on_shell_remainder == 0, "mixed current is nonzero on the physical shell")
    return {
        "representatives": {
            "twist": "h_(x,a)=(A+B*t)X_a, a_x=-(A+B*t)Y_10",
            "physical": "(H,Q)=(p,p), k=0, wave=exp(-I*omega*t)",
        },
        "harmonic": "Y_10=cos(theta), N_10=4*pi/3",
        "physical_dispersion": "omega^2=4",
        "integrated_coordinate_current_per_unit_x": str(integrated),
        "exact_factor": "omega^2-4",
        "on_shell_polynomial_remainder": "0",
        "full_time_identity": True,
        "includes_twist_position_A": True,
        "includes_twist_Jordan_partner_Bt": True,
        "opposite_order_current": "minus the displayed current by antisymmetry",
        "all_m_extension": "SO(3) equivariance gives the same zero for every real ell=1 harmonic; orthogonal m labels have zero cross-pairing",
    }


def build_fixture() -> dict[str, Any]:
    return {
        "schema": "weyl-maxwell-twist-physical-mixed-lee-wald-fixture-v1",
        "result_id": "WEYL_MAXWELL_TWIST_PHYSICAL_MIXED_LEE_WALD_FIXTURE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "mixed Weyl-Maxwell current between the generalized axial ell=1 twist block and the physical axial ell=1 quotient oscillator at n=0, before final residual quotient",
        "current_convention": "omega^t=delta1 theta^t(delta2)-delta2 theta^t(delta1); literal action coefficient alpha_B=3",
        "direct_current": _direct_fixture(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    fixture = build_fixture()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        _require(json.loads(args.verify.read_text(encoding="utf-8")) == fixture, f"stale mixed fixture: {args.verify}")
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
