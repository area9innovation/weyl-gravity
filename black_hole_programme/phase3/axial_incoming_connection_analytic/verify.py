#!/usr/bin/env python3
"""Exact endpoint-assignment verifier for analytic invertibility of Tminus."""
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
W = sp.Symbol("omega", positive=True, real=True)
I = sp.I


class ConnectionError(AssertionError):
    """Raised when endpoint assignments or the analytic theorem drift."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ConnectionError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expr(value: str | int) -> sp.Expr:
    return sp.sympify(value, locals={"r": R, "omega": W, "I": I})


def _zero(value: sp.Expr) -> bool:
    return sp.cancel(sp.together(value)) == 0


def _parse_vector(values: list[str]) -> sp.Matrix:
    return sp.Matrix([_expr(value) for value in values])


def _spin_one_amplitude(vector: sp.Matrix, radius: sp.Expr) -> sp.Expr:
    """Leading y=r^2(r-2)Z amplitude from Z=L_RW P."""
    P, Pprime, Q = vector[0], vector[1], vector[2]
    return sp.factor(2 * P + 2 * radius * Pprime - 2 * I * W * radius * Q)


def _infinity_state(head: dict[str, Any]) -> sp.Matrix:
    rate = _expr(head["rate"])
    power = _expr(head["power"])
    coefficients = [
        (_expr(pair[0]), _expr(pair[1]))
        for pair in head["coefficients_PQ"]
    ]
    p = sum(
        coefficient[0] * R ** (power - order)
        for order, coefficient in enumerate(coefficients)
    )
    q = sum(
        coefficient[1] * R ** (power - order)
        for order, coefficient in enumerate(coefficients)
    )
    return sp.Matrix([
        p,
        rate * p + sp.diff(p, R),
        q,
        rate * q + sp.diff(q, R),
    ])


def verify_certificate(data: dict[str, Any]) -> None:
    _require(
        data.get("schema") == "phase3-axial-incoming-connection-analytic-v1",
        "wrong schema",
    )
    _require(data.get("lifecycle") == "CLASSIFIED", "wrong lifecycle")
    _require(
        data.get("dependency_tags") == ["LORENTZIAN-CAUSAL", "REDUCED-MODE"],
        "dependency boundary drift",
    )
    declaration = data["declaration"]
    _require(
        declaration["horizon_regular_basis"] == ["XH0a", "XH0b", "EH0"]
        and declaration["Iminus_basis"] == ["XI0", "XI1", "EI0"],
        "endpoint basis order drift",
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
        _require(
            len(reference["commit"]) == 40
            and all(character in "0123456789abcdef" for character in reference["commit"]),
            f"invalid import commit: {name}",
        )
        imports[name] = json.loads(full.read_text())

    contract = imports["connection_contract"]["basis_contract"]
    _require(
        contract["future_regular_origin_order"] == ["XH0a", "XH0b", "EH0"]
        and contract["Iminus_selector"] == [0, 1, 4],
        "connection-selector contract drift",
    )

    triangular = imports["triangular_factorization"]
    _require(
        triangular["claim_flags"]["complete_RW_RW_Lx_triangular_filtration_certified"]
        is True
        and triangular["claim_flags"]["Lx_spin_one_RW_gauge_certified"] is True,
        "factor filtration import drift",
    )

    complete = imports["complete_reconstruction"]
    horizon_lifts = complete["endpoint_bases"]["horizon"]["additional_lifts"]
    h_a = _parse_vector(horizon_lifts["XH0a"]["carrier_leading_vector"])
    h_b = _parse_vector(horizon_lifts["XH0b"]["carrier_leading_vector"])
    amp_a = _spin_one_amplitude(h_a, sp.Integer(2))
    amp_b = _spin_one_amplitude(h_b, sp.Integer(2))
    horizon = data["horizon_factor_frame"]
    _require(
        _zero(amp_a - _expr(horizon["spin_one_quotient_amplitudes"]["XH0a"]))
        and _zero(amp_b - _expr(horizon["spin_one_quotient_amplitudes"]["XH0b"])),
        "horizon spin-one quotient amplitudes drift",
    )
    ratio = sp.cancel(amp_a / amp_b)
    carrier_rw_vector = h_a - ratio * h_b
    _require(
        _zero(_spin_one_amplitude(carrier_rw_vector, sp.Integer(2))),
        "horizon carrier RW combination does not kill the spin-one quotient",
    )
    h_rw = sp.factor(carrier_rw_vector[0])
    _require(
        _zero(h_rw - _expr(horizon["carrier_RW_horizon_amplitude"])),
        "horizon carrier RW amplitude drift",
    )
    _require(
        _zero(amp_b - _expr(horizon["spin_one_horizon_amplitude"])),
        "horizon spin-one normalization drift",
    )

    # The metric master amplitude follows from the exact U map.  Its second
    # coefficient vanishes at the future horizon, so only H1_head[0]=1 enters.
    U = sp.Matrix([
        [_expr(value) for value in row]
        for row in triangular["Einstein_kernel_RW_equivalence"][
            "U_H1F_to_PsiPsiPrime"
        ]
    ])
    h_metric = sp.factor(sp.limit(U[0, 0], R, 2, dir="+"))
    _require(
        _zero(h_metric - _expr(horizon["metric_RW_horizon_amplitude"])),
        "metric RW horizon amplitude drift",
    )

    infinity_heads = complete["endpoint_bases"]["infinity"][
        "carrier_coefficient_heads"
    ]
    state_0 = _infinity_state(infinity_heads["XI0"])
    state_1 = _infinity_state(infinity_heads["XI1"])
    amp_0 = sp.factor(sp.limit(_spin_one_amplitude(state_0, R), R, sp.oo))
    amp_1 = sp.factor(sp.limit(_spin_one_amplitude(state_1, R), R, sp.oo))
    infinity = data["Iminus_factor_frame"]
    _require(
        _zero(amp_0 - _expr(infinity["spin_one_quotient_amplitudes"]["XI0"]))
        and _zero(amp_1 - _expr(infinity["spin_one_quotient_amplitudes"]["XI1"])),
        "Iminus spin-one quotient amplitudes drift",
    )
    carrier_incoming = state_0 - I * state_1 / W
    _require(
        _zero(sp.limit(_spin_one_amplitude(carrier_incoming, R), R, sp.oo)),
        "Iminus carrier RW combination does not kill the spin-one quotient",
    )
    _require(
        _zero(
            sp.limit(carrier_incoming[0], R, sp.oo)
            - _expr(infinity["carrier_RW_incoming_amplitude"])
        ),
        "Iminus carrier RW normalization drift",
    )
    _require(
        _zero(amp_1 - _expr(infinity["spin_one_incoming_amplitude"])),
        "Iminus spin-one normalization drift",
    )
    metric_incoming = sp.factor(sp.limit(U[0, 0], R, sp.oo))
    _require(
        _zero(metric_incoming - _expr(infinity["metric_RW_incoming_amplitude"])),
        "Iminus metric RW normalization drift",
    )

    _require(
        horizon["factor_order"] == infinity["factor_order"]
        and horizon["change_of_basis_determinant"] == "1"
        and infinity["change_of_basis_determinant"] == "1",
        "factor-frame crosswalk drift",
    )

    potentials = data["factor_potentials"]
    f = (R - 2) / R
    V2 = _expr(potentials["spin_two"]["V2"])
    V1 = _expr(potentials["spin_one"]["V1"])
    _require(
        _zero(V2 - f * (6 / R**2 - 6 / R**3))
        and _zero(V1 - f * 6 / R**2),
        "RW potentials drift",
    )
    _require(
        _zero(
            sp.integrate(V2 / f, (R, 2, sp.oo))
            - _expr(potentials["spin_two"]["L1_integral"])
        )
        and _zero(
            sp.integrate(V1 / f, (R, 2, sp.oo))
            - _expr(potentials["spin_one"]["L1_integral"])
        ),
        "short-range L1 audit drift",
    )
    _require(
        sp.simplify(sp.conjugate(V1) - V1) == 0
        and sp.simplify(sp.conjugate(V2) - V2) == 0,
        "real-potential condition drift",
    )

    prefactor = sp.factor(
        (h_rw / _expr(infinity["carrier_RW_incoming_amplitude"]))
        * (amp_b / _expr(infinity["spin_one_incoming_amplitude"]))
        * (h_metric / _expr(infinity["metric_RW_incoming_amplitude"]))
    )
    theorem = data["determinant_theorem"]
    _require(
        _zero(prefactor - _expr(theorem["rational_prefactor"])),
        "connection determinant prefactor drift",
    )
    modulus_squared = sp.factor(prefactor * sp.conjugate(prefactor))
    _require(
        _zero(modulus_squared - _expr(theorem["prefactor_modulus_squared"])),
        "prefactor modulus drift",
    )
    _require(
        theorem["nonzero_on_pilot_interval"] is True
        and theorem["Tminus_rank"] == 3
        and theorem["Tminus_invertible"] is True,
        "analytic Tminus conclusion drift",
    )
    wronskian = data["Wronskian_gate"]
    _require(
        wronskian["identity"]
        == "abs(A_in_s)**2-abs(A_out_s)**2=1"
        and "A_in_s is nonzero" in wronskian["consequence"],
        "Wronskian nonvanishing gate drift",
    )

    flags = data["claim_flags"]
    for proved in (
        "horizon_frame_factor_adapted_certified",
        "Iminus_frame_factor_adapted_certified",
        "global_Tminus_exists_by_short_range_Jost_theory",
        "global_Tminus_invertible_on_real_pilot_certified",
    ):
        _require(flags[proved] is True, f"proved incoming claim demoted: {proved}")
    for forbidden in (
        "Tplus_rank_certified",
        "reflection_amplitudes_nonzero_certified",
        "upper_half_plane_pole_exclusion_certified",
        "full_scattering_or_stability_certified",
    ):
        _require(flags[forbidden] is False, f"unproved outgoing claim promoted: {forbidden}")
    limits = set(data["does_not_establish"])
    _require(
        "invertibility or any fixed rank of the Iplus outgoing/reflection block Tplus"
        in limits
        and "nonvanishing of either spin-one or spin-two reflection amplitude"
        in limits
        and "absence of complex-frequency poles or quasinormal instabilities"
        in limits,
        "outgoing/stability boundary drift",
    )


def verify() -> None:
    verify_certificate(json.loads(CERTIFICATE.read_text()))
    print("PASS analytic invertibility of the axial incoming connection Tminus")


if __name__ == "__main__":
    verify()
