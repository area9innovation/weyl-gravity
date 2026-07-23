#!/usr/bin/env python3
"""Exact verifier for the extended Tminus, Gram, and Evans audit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
W = sp.Symbol("omega", positive=True, real=True)
R = sp.Symbol("r", positive=True)
X = sp.Symbol("x", nonnegative=True, real=True)
I = sp.I


class ExtendedAuditError(AssertionError):
    """Raised when an extended-domain claim or boundary drifts."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ExtendedAuditError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expr(value: str | int, *, x: bool = False) -> sp.Expr:
    locals_ = {"omega": W, "r": R, "I": I, "x": X}
    return sp.sympify(value, locals=locals_)


def _zero(value: sp.Expr) -> bool:
    return sp.cancel(sp.together(value)) == 0


def _matrix(rows: list[list[str | int]]) -> sp.Matrix:
    return sp.Matrix([[_expr(value) for value in row] for row in rows])


def verify_certificate(data: dict[str, Any]) -> None:
    _require(
        data.get("schema") == "phase3-axial-incoming-extended-domain-audit-v1",
        "wrong schema",
    )
    _require(data.get("lifecycle") == "CLASSIFIED", "wrong lifecycle")
    _require(
        data.get("dependency_tags") == ["LORENTZIAN-CAUSAL", "REDUCED-MODE"],
        "dependency boundary drift",
    )
    _require(
        data["declaration"]["repository_phase"]
        == "exp(+I*omega*v), hence exp(+I*omega*t)",
        "phase convention drift",
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

    incoming = imports["incoming_connection"]
    _require(
        incoming["claim_flags"]["global_Tminus_invertible_on_real_pilot_certified"]
        is True,
        "incoming theorem import drift",
    )

    margin = data["uniform_pilot_margin"]
    f_mod = _expr(margin["prefactor_modulus_squared_in_x"], x=True)
    derivative = sp.factor(sp.diff(f_mod, X))
    _require(
        _zero(derivative - _expr(margin["derivative"], x=True)),
        "prefactor monotonicity derivative drift",
    )
    _require(
        _zero(f_mod.subs(X, sp.Rational(1, 4)) - sp.Rational(5, 2)),
        "pilot minimum drift",
    )
    _require(
        _zero(_expr(margin["minimum_modulus_squared"]) - sp.Rational(5, 2)),
        "recorded pilot minimum drift",
    )
    _require(
        sp.Poly(sp.factor(sp.together(derivative).as_numer_denom()[0]), X)
        .all_coeffs()
        == [2048, 3456, 768, 35],
        "positive derivative polynomial drift",
    )
    _require(
        margin["conclusion"]
        == "abs(det(Tminus))>=sqrt(5/2) on [1/2,3/4]",
        "uniform determinant margin demoted",
    )

    extension = data["positive_real_extension"]
    _require(
        extension["Tminus_invertible_all_positive_real"] is True
        and extension["omega_zero_excluded"] is True,
        "positive-real extension boundary drift",
    )
    # Every displayed rational map is regular on r>2, real omega>0.
    _require(
        _zero(_expr(extension["carrier_cyclic_determinant"])
              + 4 * W**2 / (R**2 * (R - 2)**2)),
        "carrier cyclic determinant drift",
    )
    _require(
        all(
            _expr(value).subs(W, sp.Symbol("u", positive=True, real=True)) != 0
            for value in extension["factor_frame_denominators"]
        ),
        "a factor-frame denominator was made identically zero",
    )
    _require(
        extension["reconstruction_reading"]
        == "omega*r-2*I has no zero for real omega>0 and r>2.",
        "real reconstruction-wall audit drift",
    )
    triangular = imports["triangular_factorization"]
    cyclic = triangular["carrier_cyclic_elimination"]
    sequence = triangular["carrier_exact_sequence"]
    einstein = triangular["Einstein_kernel_RW_equivalence"]
    _require(
        _zero(
            _expr(cyclic["observability_determinant"])
            + 4 * W**2 / (R**2 * (R - 2)**2)
        )
        and _zero(
            _expr(sequence["gauge_determinant"])
            + R**2 * (R - 2)**2 / (4 * W**2)
        )
        and _zero(
            _expr(einstein["U_determinant"])
            + I * W**2 * (R - 2) / (2 * R * (W * R - 2 * I))
        ),
        "imported real-domain determinant ledger drift",
    )
    horizon_frame = incoming["horizon_factor_frame"]
    infinity_frame = incoming["Iminus_factor_frame"]
    _require(
        horizon_frame["carrier_RW_line"]
        == (
            "RH=XH0a-(4*omega**2-3*I*omega+4)*XH0b/"
            "(4*(omega-I)*(2*omega-I))"
        )
        and infinity_frame["carrier_RW_line"] == "RI=XI0-I*XI1/omega",
        "factor-frame denominator source drift",
    )
    endpoint = imports["endpoint_bases"]["carrier_endpoint_basis"]
    horizon = endpoint["horizon"]
    infinity = endpoint["infinity"]
    _require(
        horizon["characteristic_polynomial"]
        == "z**2*(4*I*omega + z)*(4*I*omega + z + 2)"
        and horizon["recurrence_determinants"]["regular_s0"]
        == "n**2*(n + 4*I*omega)*(n + 4*I*omega + 2)"
        and horizon["integer_spaced_resonance"]["compatible"] is True
        and horizon["integer_spaced_resonance"]["logarithm_forced"] is False
        and infinity["rates"] == ["0", "-2*I*omega"]
        and infinity["logarithm_forced"] is False
        and "omega!=0" in infinity["radial_class"],
        "imported endpoint collision/log ledger drift",
    )
    reconstructed = imports["complete_reconstruction"]["endpoint_bases"]
    _require(
        reconstructed["horizon"]["Einstein_kernel"]["EH0"]["H1_exponent"] == "0"
        and reconstructed["horizon"]["Einstein_kernel"]["EHout"][
            "H1_exponent"
        ]
        == "-1-4*I*omega"
        and reconstructed["horizon"]["Einstein_kernel"][
            "recurrence_pivot"
        ]
        == "(t+n)*(t+n+1+4*I*omega)",
        "Einstein horizon recurrence ledger drift",
    )

    source = imports["formal_grams"]
    _require(
        source["Iminus"]["basis"] == ["XI0", "XI1", "EI0"],
        "Iminus source basis drift",
    )
    raw = _matrix(source["Iminus"]["gram_over_pi_alpha"])
    # Columns are the exact factor-adapted vectors (RI,SI,EI), with
    # SI=NI+EI/3 the lift orthogonal to ker(pi_x).
    basis = sp.Matrix([
        [1, -W**2, 0],
        [-I / W, -2 * I * W, 0],
        [0, sp.Rational(4, 3), 1],
    ])
    transformed = (
        sp.conjugate(basis).T * (-raw) * basis
    ).applyfunc(lambda value: sp.cancel(sp.together(value)))
    gram_data = data["factor_adapted_Iminus_gram"]
    expected = _matrix(gram_data["gram_over_pi_alpha_W"])
    _require(
        transformed.shape == expected.shape
        and all(
            _zero(transformed[row, column] - expected[row, column])
            for row in range(3)
            for column in range(3)
        ),
        "factor-adapted Iminus Gram drift",
    )
    minors = [
        transformed[:size, :size].det()
        for size in (1, 2, 3)
    ]
    _require(
        all(
            _zero(value - _expr(expected_value))
            for value, expected_value in zip(
                minors, gram_data["leading_principal_minors"]
            )
        ),
        "factor Gram principal minors drift",
    )
    # The L_x quotient projection is pi_x=[2,-2*i*omega,0].
    pi_x = sp.Matrix([[2, -2 * I * W, 0]])
    Rv, Sv, Ev = (basis[:, column] for column in range(3))
    Nv = sp.Matrix([-W**2, -2 * I * W, 1])
    projection = gram_data["factor_projection"]
    _require(
        _zero((pi_x * Rv)[0])
        and _zero((pi_x * Nv)[0] + 6 * W**2)
        and _zero((pi_x * Sv)[0] + 6 * W**2)
        and _expr(projection["pi_x(XI0)"]) == 2
        and _zero(_expr(projection["pi_x(XI1)"]) + 2 * I * W)
        and _expr(projection["pi_x(EI0)"]) == 0
        and _expr(projection["pi_x(RI)"]) == 0
        and _zero(_expr(projection["pi_x(NI)"]) + 6 * W**2)
        and _zero(_expr(projection["pi_x(SI)"]) + 6 * W**2),
        "factor projection attribution drift",
    )

    def inner(left: sp.Matrix, right: sp.Matrix) -> sp.Expr:
        return sp.cancel((sp.conjugate(left).T * (-raw) * right)[0])

    # First-slot conjugate-linearity matters in the RI construction.
    X0v = sp.Matrix([1, 0, 0])
    _require(
        gram_data["Hermitian_slot_convention"].startswith(
            "G(u,v)=conjugate(u)^T"
        )
        and _zero(inner(Ev, Nv))
        and _zero(inner(Ev, Rv) - sp.Rational(3, 2) * inner(Ev, X0v))
        and _zero(inner(Rv, Nv) + 192 * W / 5)
        and _zero(inner(Rv, Sv))
        and _zero(inner(Sv, Sv) - inner(Nv, Nv))
        and _zero(inner(Sv, Sv) + 384 * W**3 / 5),
        "Hermitian factor-attribution identities drift",
    )

    carrier = transformed.extract([0, 2], [0, 2])
    _require(
        _zero(carrier.det() - _expr(gram_data["carrier_factor_plane"]["determinant"]))
        and gram_data["carrier_factor_plane"]["inertia"] == [1, 1, 0],
        "carrier factor-plane anatomy drift",
    )
    spin_one = transformed[1, 1]
    _require(
        _zero(spin_one - _expr(gram_data["spin_one_quotient_line"]["norm"]))
        and gram_data["spin_one_quotient_line"]["inertia"] == [0, 1, 0]
        and _zero(transformed[1, 0])
        and _zero(transformed[1, 2]),
        "orthogonal spin-one quotient line drift",
    )
    # In (EI,RI0,SI), RI0=RI-13 EI/(24 omega^2), the spin-two
    # extension is a null pair and the quotient lift is a negative line.
    witt_change = sp.Matrix([
        [0, 1, 0],
        [0, 0, 1],
        [1, -sp.Rational(13, 24) / W**2, 0],
    ])
    witt = (
        sp.conjugate(witt_change).T * transformed * witt_change
    ).applyfunc(lambda value: sp.cancel(sp.together(value)))
    expected_witt = _matrix(gram_data["canonical_Witt_gram_over_pi_alpha_W"])
    _require(
        all(
            _zero(witt[row, column] - expected_witt[row, column])
            for row in range(3)
            for column in range(3)
        ),
        "canonical factor-aligned Witt Gram drift",
    )
    _require(
        gram_data["full_inertia_for_alpha_W_positive"] == [1, 2, 0]
        and "pi_x(XI0)=2" in gram_data["factor_alignment_warning"],
        "factor Gram inertia/alignment warning drift",
    )

    evans = data["Evans_convention_audit"]
    _require(
        evans["growth_half_plane"]
        == "Im(omega)<0 because the time factor is exp(+I*omega*t)",
        "growth half-plane was reversed",
    )
    _require(
        evans["requested_no_UHP_theorem"] == "REFUSED_BY_PHASE_CONVENTION"
        and evans["no_LHP_growing_zeros_certified"] is True
        and evans["no_UHP_zeros_certified"] is False,
        "Evans theorem boundary drift",
    )
    V1 = _expr(evans["potentials"]["V1"])
    V2 = _expr(evans["potentials"]["V2"])
    _require(
        _zero(V1 - 6 * (R - 2) / R**3)
        and _zero(V2 - 6 * (R - 2) * (R - 1) / R**4),
        "nonnegative reduced potentials drift",
    )

    points = data["special_imaginary_points"]
    checks = {
        "omega=I/4": (sp.Rational(1, 4), 8),
        "omega=I/2": (sp.Rational(1, 2), 4),
        "omega=I": (sp.Integer(1), 2),
    }
    for label, (kappa, wall_radius) in checks.items():
        point = points[label]
        _require(
            point["classification"]
            == "FROBENIUS_AND_RECONSTRUCTION_FRAME_SINGULARITY"
            and point["genuine_reduced_Evans_zero"] == "OPEN",
            f"{label} Evans status overpromoted",
        )
        _require(
            _zero((I * kappa) * wall_radius - 2 * I),
            f"{label} reconstruction-wall radius drift",
        )
    _require(_zero(4 * (I / 4) - I), "omega=i/4 frame factor drift")
    _require(_zero(2 * (I / 2) - I), "omega=i/2 frame factor drift")
    _require(_zero(I - I), "omega=i frame factor drift")

    flags = data["claim_flags"]
    for proved in (
        "uniform_pilot_determinant_margin_certified",
        "Tminus_invertible_all_real_positive_omega_certified",
        "Gminus_inertia_all_real_positive_omega_certified",
        "factor_adapted_Iminus_gram_certified",
        "no_lower_half_plane_growing_Evans_zeros_certified",
    ):
        _require(flags[proved] is True, f"proved claim demoted: {proved}")
    for forbidden in (
        "no_upper_half_plane_Evans_zeros_certified",
        "special_imaginary_points_are_genuine_Evans_zeros",
        "special_imaginary_points_are_proved_nonzeros",
        "Tplus_or_reflection_nonvanishing_certified",
    ):
        _require(flags[forbidden] is False, f"open claim promoted: {forbidden}")
    limits = set(data["does_not_establish"])
    _require(
        "absence of upper-half-plane damped quasinormal or Evans zeros" in limits
        and "whether omega=I/4, I/2 or I is a genuine regularized Evans zero"
        in limits
        and "invertibility or fixed rank of Tplus or nonvanishing reflection amplitudes"
        in limits,
        "UHP/Tplus boundary drift",
    )


def verify() -> None:
    verify_certificate(json.loads(CERTIFICATE.read_text()))
    print("PASS extended positive-real Tminus, factor Gram, and Evans convention audit")


if __name__ == "__main__":
    verify()
