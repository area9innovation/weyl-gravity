"""Literal pure-Weyl polar Lee--Wald slice current before branch specialization."""

from __future__ import annotations

import sys
from pathlib import Path

import sympy as sp

# The legacy theta module supports script-style imports.  Register its Bach
# sibling directory so its historical imports resolve when this Phase-2 code
# is invoked through plain ``python -m`` or pytest.
LEGACY_MODULE_DIR = str(Path(__file__).resolve().parents[2])
if LEGACY_MODULE_DIR not in sys.path:
    sys.path.insert(0, LEGACY_MODULE_DIR)
from black_hole_programme.linearized_theta import LinearizedTheta
from black_hole_programme.weyl_geometry import Geometry


def build_raw_radial_current(ell: int) -> tuple[sp.Expr, list[sp.Expr], list[sp.Expr]]:
    """Build the exact sphere-integrated radial bilinear at an explicit ell.

    Explicit harmonics are used only as an independent interpolation rail;
    any generic-Lambda promotion additionally requires a degree bound and
    exact reconstruction from enough representations.
    """
    v, r, x, phi = sp.symbols("v r x phi")
    mass = sp.Symbol("m", positive=True)
    alpha = sp.Symbol("alpha", nonzero=True)
    coordinates = [v, r, x, phi]
    b0 = 1 - 2 * mass / r
    metric = sp.zeros(4)
    metric[0, 0] = -b0
    metric[0, 1] = metric[1, 0] = 1
    metric[2, 2] = r**2 / (1 - x**2)
    metric[3, 3] = r**2 * (1 - x**2)
    geometry = Geometry(coordinates, metric)
    p = sp.legendre(ell, x)

    def polar(tag: str) -> tuple[sp.Matrix, list[sp.Expr]]:
        functions = [sp.Function(name + tag)(v, r) for name in ("FA", "FB", "FC", "FK")]
        perturbation = sp.zeros(4)
        perturbation[0, 0] = functions[0] * p
        perturbation[0, 1] = perturbation[1, 0] = functions[1] * p
        perturbation[1, 1] = functions[2] * p
        perturbation[2, 2] = metric[2, 2] * functions[3] * p
        perturbation[3, 3] = metric[3, 3] * functions[3] * p
        return perturbation, functions

    left, left_functions = polar("a")
    right, right_functions = polar("b")
    current = LinearizedTheta(geometry, alpha).omega(left, right)[1]
    integrated = sp.cancel(
        sp.integrate(sp.integrate(current * r**2, (x, -1, 1)), (phi, 0, 2 * sp.pi))
    )
    return integrated, left_functions, right_functions


def build_symbolic_angular_current() -> tuple[sp.Expr, list[sp.Expr], list[sp.Expr], sp.Expr, sp.Symbol, sp.Symbol]:
    """Build the unintegrated radial current in a symbolic scalar harmonic."""
    v, r, x, phi = sp.symbols("v r x phi")
    mass = sp.Symbol("m", positive=True)
    alpha = sp.Symbol("alpha", nonzero=True)
    lam = sp.Symbol("Lambda")
    coordinates = [v, r, x, phi]
    b0 = 1 - 2 * mass / r
    metric = sp.zeros(4)
    metric[0, 0] = -b0
    metric[0, 1] = metric[1, 0] = 1
    metric[2, 2] = r**2 / (1 - x**2)
    metric[3, 3] = r**2 * (1 - x**2)
    geometry = Geometry(coordinates, metric)
    p = sp.Function("P")(x)

    def polar(tag: str) -> tuple[sp.Matrix, list[sp.Expr]]:
        functions = [sp.Function(name + tag)(v, r) for name in ("FA", "FB", "FC", "FK")]
        perturbation = sp.zeros(4)
        perturbation[0, 0] = functions[0] * p
        perturbation[0, 1] = perturbation[1, 0] = functions[1] * p
        perturbation[1, 1] = functions[2] * p
        perturbation[2, 2] = metric[2, 2] * functions[3] * p
        perturbation[3, 3] = metric[3, 3] * functions[3] * p
        return perturbation, functions

    left, left_functions = polar("a")
    right, right_functions = polar("b")
    # F^v is the slice-density component used by the radial-integrability
    # theorem.  F^r is a boundary flux and is not interchangeable with it.
    current = LinearizedTheta(geometry, alpha).omega(left, right)[0] * r**2
    return current, left_functions, right_functions, p, x, lam


def derive_symbolic_literal_current() -> dict:
    """Legendre-reduce and Fourier-reduce the generic polar radial current."""
    current, left, right, p, x, lam = build_symbolic_angular_current()
    q = sp.diff(p, x)
    reduced = sp.cancel(
        sp.together(current.subs(sp.diff(p, x, 2), (2 * x * q - lam * p) / (1 - x**2)))
    )
    p_slot, q_slot = sp.symbols("Pslot Qslot")
    slotted = sp.expand(reduced.xreplace({p: p_slot, q: q_slot}))
    scalar_coefficient = sp.cancel(slotted.coeff(p_slot, 2))
    mixed_coefficient = sp.cancel(slotted.coeff(p_slot).coeff(q_slot))
    vector_coefficient = sp.cancel(slotted.coeff(q_slot, 2) / (1 - x**2))
    defect = sp.cancel(
        slotted
        - scalar_coefficient * p_slot**2
        - mixed_coefficient * p_slot * q_slot
        - (1 - x**2) * vector_coefficient * q_slot**2
    )
    if defect != 0:
        raise RuntimeError("symbolic angular current did not reduce to the scalar/vector norm basis")
    if scalar_coefficient.has(x) or mixed_coefficient != 0 or vector_coefficient.has(x):
        raise RuntimeError("symbolic angular current retained an unsupported angular coefficient")

    # The current already contains the r^2 sphere measure.  The exact norms
    # are int P_l^2 dx=2/(2l+1) and
    # int (1-x^2)(P_l')^2 dx=2 Lambda/(2l+1); phi contributes 2*pi.
    ell = sp.Symbol("ell", integer=True, nonnegative=True)
    integrated = sp.cancel(
        4 * sp.pi * (scalar_coefficient + lam * vector_coefficient) / (2 * ell + 1)
    )

    # Conjugate-frequency bilinear: left exp(-i omega v), right exp(+i omega v).
    v, r = sp.symbols("v r")
    omega = sp.Symbol("omega", real=True, nonzero=True)
    phase_substitution: dict[sp.Expr, sp.Expr] = {}
    radial_fields: dict[str, str] = {}
    for sign, fields, suffix in ((-1, left, "minus"), (1, right, "plus")):
        phase = sp.exp(sign * sp.I * omega * v)
        for field in fields:
            radial = sp.Function(field.func.__name__ + "_r")(r)
            radial_fields[field.func.__name__] = sp.sstr(radial)
            for derivative in integrated.atoms(sp.Derivative):
                if derivative.expr == field:
                    value = radial * phase
                    for variable, count in derivative.variable_count:
                        value = sp.diff(value, variable, count)
                    phase_substitution[derivative] = value
            phase_substitution[field] = radial * phase
    # The bilinear has net Fourier phase zero.  Evaluating at v=0 before
    # rational collection prevents a prohibitively large multivariate GCD
    # while preserving the exact stationary current.
    fourier_raw = integrated.subs(phase_substitution).doit().subs(v, 0)
    fourier_current = sp.factor_terms(sp.together(fourier_raw), clear=True)
    if fourier_current.has(v):
        raise RuntimeError("Fourier-reduced current retained v")

    return {
        "angular_basis": "P_l^2 and (1-x^2)*(P_l')^2",
        "angular_reduction_defect": sp.sstr(defect),
        "mixed_P_Pprime_coefficient": sp.sstr(mixed_coefficient),
        "norms": {
            "scalar": "2/(2*ell+1)",
            "vector": "2*Lambda/(2*ell+1)",
            "azimuth": "2*pi",
        },
        "frequency_pair": "left exp(-I*omega*v), right exp(+I*omega*v)",
        "radial_fields": radial_fields,
        "component": "F^v=omega^0",
        "sphere_measure": "r^2 dx dphi",
        "sphere_integrated_slice_current": sp.sstr(fourier_current),
        "literal_current_closed": True,
        "angular_sampling_used": False,
    }
