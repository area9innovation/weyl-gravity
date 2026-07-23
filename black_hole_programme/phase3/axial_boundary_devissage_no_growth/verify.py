#!/usr/bin/env python3
"""Exact verifier for axial boundary devissage and LHP no-growth."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
R = sp.Symbol("r", positive=True)
W = sp.Symbol("omega")
T = sp.Symbol("t")
I = sp.I


class BoundaryDevissageError(AssertionError):
    """Raised when a boundary map, factor, or claim boundary drifts."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise BoundaryDevissageError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expr(value: str | int) -> sp.Expr:
    return sp.sympify(value, locals={"r": R, "omega": W, "I": I})


def _zero(value: sp.Expr) -> bool:
    return sp.cancel(sp.together(value)) == 0


def _parse_head(rows: list[list[str]]) -> tuple[list[sp.Expr], list[sp.Expr]]:
    parsed = [[_expr(item) for item in row] for row in rows]
    return [row[0] for row in parsed], [row[1] for row in parsed]


def _outgoing_spin_one_amplitude(
    rows: list[list[str]], power: str
) -> sp.Expr:
    """Leading y amplitude for y=r^2(r-2)L_RW P at infinity."""
    p = _expr(power)
    p_coeffs, q_coeffs = _parse_head(rows)
    p_series = sum(value * T**index for index, value in enumerate(p_coeffs))
    q_series = sum(value * T**index for index, value in enumerate(q_coeffs))
    radial_derivative = (
        -2 * I * W * p_series
        + p * T * p_series
        - T**2 * sp.diff(p_series, T)
    )
    r = 1 / T
    z = (
        2 * p_series / (r**2 * (r - 2))
        + 2 * radial_derivative / (r * (r - 2))
        - 2 * I * W * q_series / (r * (r - 2))
    )
    y = sp.expand(sp.cancel(r**2 * (r - 2) * z))
    # XI2 has the spin-one power already. XI3 is one power lower and its
    # leading y term is the coefficient of t^-1.
    target_power = 0 if _zero(p + 4 * I * W) else -1
    return sp.cancel(sp.expand(y).coeff(T, target_power))


def _metric_outgoing_amplitude(
    head: list[str], power: str, U_rows: list[list[str]]
) -> sp.Expr:
    """Leading RW master amplitude of the EI2 formal germ."""
    p = _expr(power)
    coefficients = [_expr(value) for value in head]
    h = sum(value * T**index for index, value in enumerate(coefficients))
    f = -2 * I * W * h + p * T * h - T**2 * sp.diff(h, T)
    U = sp.Matrix([[_expr(value) for value in row] for row in U_rows])
    r_sub = {R: 1 / T}
    psi = sp.cancel(U[0, 0].subs(r_sub) * h + U[0, 1].subs(r_sub) * f)
    # H1 carries r^(1-4iw); the master carries r^(-4iw), hence t^1.
    return sp.cancel(sp.limit(psi / T, T, 0))


def verify_certificate(data: dict[str, Any]) -> None:
    _require(
        data.get("schema") == "phase3-axial-boundary-devissage-no-growth-v1",
        "wrong schema",
    )
    _require(data.get("lifecycle") == "CLASSIFIED", "wrong lifecycle")
    _require(
        data.get("dependency_tags") == ["LORENTZIAN-CAUSAL", "REDUCED-MODE"],
        "dependency boundary drift",
    )
    declaration = data["declaration"]
    _require(
        declaration["phase"]
        == "exp(+I*omega*v)=exp(+I*omega*t)*exp(+I*omega*rstar)"
        and declaration["growth_domain"] == "Im(omega)<0",
        "repository phase or growth half-plane drift",
    )

    imports: dict[str, dict[str, Any]] = {}
    for name, reference in data["imports"].items():
        path = Path(reference["path"])
        _require(
            not path.is_absolute() and ".." not in path.parts,
            f"unsafe import path: {name}",
        )
        full = ROOT / path
        _require(full.is_file(), f"missing import: {name}")
        _require(_sha256(full) == reference["sha256"], f"hash drift: {name}")
        imports[name] = json.loads(full.read_text())

    triangular = imports["triangular_factorization"]
    _require(
        triangular["claim_flags"][
            "complete_RW_RW_Lx_triangular_filtration_certified"
        ]
        is True,
        "three-factor filtration import drift",
    )
    _require(
        triangular["complete_six_state_filtration"][
            "diagonal_factor_order_after_reordering"
        ]
        == [
            "L_RW Einstein metric kernel",
            "L_RW carrier submodule",
            "L_x carrier quotient",
        ],
        "filtration order drift",
    )

    scalar = data["scalar_boundary_problem"]
    V2 = _expr(scalar["potentials"]["spin_two"])
    V1 = _expr(scalar["potentials"]["spin_one"])
    _require(
        _zero(V2 - 6 * (R - 2) * (R - 1) / R**4)
        and _zero(V1 - 6 * (R - 2) / R**3),
        "reduced potential drift",
    )
    _require(
        scalar["spin_two_LHP_kernel_dimension"] == 0
        and scalar["spin_one_LHP_kernel_dimension"] == 0
        and "Im(omega)<0" in scalar["no_mode_argument"],
        "scalar no-growth theorem drift",
    )

    incoming = imports["analytic_incoming_connection"]
    horizon = data["local_boundary_maps"]["future_horizon"]
    imported_horizon = incoming["horizon_factor_frame"]
    _require(
        horizon["spin_one_quotient_amplitudes"]
        == imported_horizon["spin_one_quotient_amplitudes"]
        and horizon["carrier_spin_two_horizon_amplitude"]
        == imported_horizon["carrier_RW_horizon_amplitude"]
        and horizon["spin_one_horizon_amplitude"]
        == imported_horizon["spin_one_horizon_amplitude"]
        and horizon["metric_spin_two_horizon_amplitude"]
        == imported_horizon["metric_RW_horizon_amplitude"],
        "horizon factor frame drift",
    )
    # All horizon normalizations have zeros/poles only on the real axis at
    # zero or in the upper half-plane.
    h_carrier = _expr(horizon["carrier_spin_two_horizon_amplitude"])
    h_spin_one = _expr(horizon["spin_one_horizon_amplitude"])
    h_metric = _expr(horizon["metric_spin_two_horizon_amplitude"])
    _require(
        _zero(h_carrier - I * W * (4 * W - I) / (2 * (W - I)))
        and _zero(h_spin_one - 4 * (W - I) * (2 * W - I))
        and _zero(h_metric + I * W * (4 * W - I) / (4 * (W - I))),
        "horizon normalization algebra drift",
    )

    complete = imports["complete_reconstruction"]
    infinity = complete["endpoint_bases"]["infinity"]
    heads = infinity["carrier_coefficient_heads"]
    out = data["local_boundary_maps"]["pure_outgoing_infinity"]
    amp2 = _outgoing_spin_one_amplitude(
        heads["XI2"]["coefficients_PQ"], heads["XI2"]["power"]
    )
    amp3 = _outgoing_spin_one_amplitude(
        heads["XI3"]["coefficients_PQ"], heads["XI3"]["power"]
    )
    _require(
        _zero(amp2 - _expr(out["spin_one_quotient_amplitudes"]["XI2"]))
        and _zero(amp3 - _expr(out["spin_one_quotient_amplitudes"]["XI3"])),
        "outgoing spin-one quotient amplitudes drift",
    )
    combination = -I * (16 * W**2 - 4 * I * W - 5) / W
    _require(
        _zero(amp2 + combination * amp3),
        "outgoing carrier RW combination does not kill the quotient",
    )
    metric = infinity["Einstein_kernel"]["EI2"]
    U_rows = triangular["Einstein_kernel_RW_equivalence"][
        "U_H1F_to_PsiPsiPrime"
    ]
    metric_amplitude = _metric_outgoing_amplitude(
        metric["H1_head"], metric["H1_power"], U_rows
    )
    _require(
        _zero(metric_amplitude - _expr(out["metric_spin_two_outgoing_amplitude"]))
        and _zero(amp3 - _expr(out["spin_one_outgoing_amplitude"])),
        "outgoing factor normalization drift",
    )

    regularities = data["local_boundary_maps"]["complex_frequency_regularities"]
    _require(
        regularities["nonzero_in_LHP"]
        == [
            "omega",
            "omega-I",
            "2*omega-I",
            "4*omega-I",
            "omega*r-2*I for r>2",
        ],
        "LHP denominator ledger drift",
    )
    # For omega=a-i*kappa, kappa>0, the recurrence factors have positive
    # real parts n+4*kappa and n+2+4*kappa.
    a = sp.Symbol("a", real=True)
    kappa = sp.Symbol("kappa", positive=True, real=True)
    n = sp.Symbol("n", positive=True, integer=True)
    lower = a - I * kappa
    _require(
        sp.re(n + 4 * I * lower) == n + 4 * kappa
        and sp.re(n + 2 + 4 * I * lower) == n + 4 * kappa + 2,
        "LHP horizon recurrence audit drift",
    )
    intrinsic = data["intrinsic_boundary_map_audit"]
    sequence = triangular["carrier_exact_sequence"]
    kernel = triangular["Einstein_kernel_RW_equivalence"]
    _require(
        sequence["exact_sequence"] == "0 -> M_RW -> M_A4 -> M_x -> 0"
        and sequence["quotient_reading"].startswith(
            "K maps a carrier state to (Z,Z_prime)"
        )
        and kernel["chain_identity"] == "U_prime+U*K2=A_RW*U"
        and intrinsic["frame_independence_certified"] is True
        and "normalization denominators do not define" in intrinsic["reading"],
        "intrinsic boundary-map audit drift",
    )

    devissage = data["boundary_devissage"]
    _require(
        devissage["filtration_order"]
        == [
            "metric spin-two Regge-Wheeler kernel",
            "carrier spin-two Regge-Wheeler submodule",
            "spin-one L_x quotient",
        ]
        and len(devissage["successive_elimination"]) == 3
        and devissage["conclusion"]
        == (
            "The complete six-state axial ell=2 Bach system has no nonzero "
            "future-horizon-regular, pure-outgoing separated mode with "
            "Im(omega)<0."
        ),
        "boundary devissage conclusion drift",
    )
    _require(
        "surjectivity is not assumed" in devissage["boundary_exactness"],
        "two-ended exactness was overclaimed",
    )

    evans = data["regularized_Evans"]
    _require(
        evans["definition"] == "E_reg(omega)=A_in_2(omega)**2*A_in_1(omega)"
        and evans["multiplicities"] == {"spin_two": 2, "spin_one": 1}
        and evans["zero_free_in_growth_domain"] is True,
        "regularized Evans theorem drift",
    )
    smith = data["simple_spin_two_QNM_extension_gate"]
    _require(
        smith["status"] == "OPEN_EXACT_NEXT_GATE"
        and smith["frame_law"] == "c -> u*c+a*d where u is a unit and d is in O."
        and smith["invariant_extension_class"]
        == "[c] in O/(a), defined up to multiplication by a unit."
        and smith["valuation_formula"]["first_Smith_valuation"] == "min(m,n)"
        and smith["valuation_formula"]["second_Smith_valuation"]
        == "2*m-min(m,n)"
        and smith["Smith_cases"]["Gamma_star_nonzero"] == "diag(1,delta**2)"
        and smith["Smith_cases"][
            "Gamma_star_zero_with_first_order_divisibility_and_nondegenerate_residual"
        ]
        == "diag(delta,delta)"
        and smith["claim"] == "No Smith case is selected by the present certificate.",
        "simple-QNM Fredholm/Smith gate drift",
    )
    # In the local DVR, the first determinantal ideal is generated by
    # (a,c), while the determinant is a^2.  Representative exact powers
    # verify the stated valuation law without selecting a physical c.
    delta = sp.Symbol("delta")
    for m in range(1, 5):
        for n_order in range(0, 7):
            a_local = delta**m
            c_local = delta**n_order
            first = min(
                sp.Poly(a_local, delta).as_dict().keys().__iter__().__next__()[0],
                sp.Poly(c_local, delta).as_dict().keys().__iter__().__next__()[0],
            )
            determinant_order = 2 * m
            _require(
                first == min(m, n_order)
                and determinant_order - first == 2 * m - min(m, n_order),
                "local Smith valuation identity drift",
            )
    _require(
        smith["spectral_derivative_next_test"]
        == "Test whether c == q*A_in_2_prime modulo A_in_2 in O/(A_in_2)."
        and smith["spectral_derivative_status"].startswith(
            "OPEN: neither the congruence nor nonvanishing"
        ),
        "spectral-derivative next gate was promoted or changed",
    )
    direct_integral = data["positive_real_direct_integral_context"]
    _require(
        _zero(_expr(direct_integral["factor_Witt_majorant_weights"]["null_pair"])
              - 576 * W / 5)
        and _zero(
            _expr(direct_integral["factor_Witt_majorant_weights"]["negative_line"])
            - sp.Rational(32, 15) / W
        )
        and direct_integral["omega_zero"] == "separate threshold; not included",
        "positive-frequency weighted-majorant context drift",
    )
    upper = data["upper_half_plane_frame_events"]
    _require(
        upper["classification"]
        == "DAMPED_UHP_FROBENIUS_OR_RECONSTRUCTION_FRAME_EVENTS"
        and upper["regularized_Evans_status"]
        == "OPEN_PENDING_LOCAL_ANALYTIC_PATCHES"
        and "damped, not growing" in upper["phase_reading"],
        "special UHP points overclassified",
    )

    flags = data["claim_flags"]
    for proved in (
        "factor_maps_preserve_LHP_horizon_and_outgoing_germs_certified",
        "endpoint_germ_filtration_exact_certified",
        "full_six_state_no_LHP_growing_separated_modes_certified",
        "intrinsic_regularized_Evans_zero_free_in_LHP_certified",
    ):
        _require(flags[proved] is True, f"proved claim demoted: {proved}")
    for forbidden in (
        "time_domain_linear_stability_certified",
        "upper_half_plane_Evans_status_certified",
        "special_UHP_points_classified_as_Evans_zeros_or_nonzeros",
        "simple_QNM_extension_Smith_case_certified",
    ):
        _require(flags[forbidden] is False, f"open claim promoted: {forbidden}")
    limits = set(data["does_not_establish"])
    _require(
        "time-domain boundedness, decay, completeness or a full PDE stability theorem"
        in limits
        and "absence of damped upper-half-plane quasinormal or Evans zeros"
        in limits
        and "the regularized Evans status of omega=I/4, I/2 or I" in limits,
        "stability/UHP boundary drift",
    )
    _require(
        "the Fredholm extension pairing or Smith type at a simple damped spin-two QNM"
        in limits,
        "simple-QNM extension boundary drift",
    )


def verify() -> None:
    verify_certificate(json.loads(CERTIFICATE.read_text()))
    print("PASS axial boundary devissage and LHP separated-mode no-growth")


if __name__ == "__main__":
    verify()
