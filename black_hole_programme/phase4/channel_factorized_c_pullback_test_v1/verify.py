"""Independent verifier for the channel-factorized C pullback certificate."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, getcontext
from pathlib import Path

import sympy as sp

from .exact import adjoint, criterion_fixture, inertia_from_eigenvalues

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def verify_path(path: Path) -> None:
    cert = _load(path)
    _require(
        cert["schema"] == "phase4-channel-factorized-c-pullback-test-v1",
        "schema drift",
    )

    for name, metadata in cert["imports"].items():
        path = ROOT / metadata["path"]
        _require(path.is_file(), f"missing import {name}")
        _require(_sha(path) == metadata["sha256"], f"hash drift for {name}")

    incoming = _load(
        ROOT
        / "black_hole_programme/phase3/axial_incoming_extended_domain_audit/certificate.json"
    )
    scope = _load(
        ROOT
        / "black_hole_programme/phase3/axial_transport_free_outgoing_defect_preflight_v1/certificate.json"
    )
    horizon = _load(
        ROOT
        / "black_hole_programme/phase3/axial_horizon_grassmann_mobius_to_r4_taylor2/future_horizon_outward_gram.json"
    )
    outgoing = _load(
        ROOT
        / "black_hole_programme/phase3/axial_outgoing_population_cell_half_v1/certificate.json"
    )
    scalar = _load(
        ROOT
        / "black_hole_programme/phase3/axial_scalar_reflection_cell_half_v1/certificate.json"
    )

    _require(
        incoming["factor_adapted_Iminus_gram"]["full_inertia_for_alpha_W_positive"]
        == [1, 2, 0],
        "incoming inertia drift",
    )
    _require(horizon["rank"] == 3, "horizon rank drift")
    _require(
        outgoing["claim_flags"]["Tplus_invertible_on_declared_cell"],
        "outgoing invertibility drift",
    )
    _require(
        scope["tier_A_transport_free_determinant"][
            "certified_full_typed_Tminus_matrix_available"
        ]
        is False,
        "typed Tminus availability changed",
    )

    positive = criterion_fixture("positive")
    _require(positive["L_G_self_adjoint"], "positive L not G-self-adjoint")
    _require(positive["L_diagonalizable"], "positive L not diagonalizable")
    _require(positive["H0_inertia"] == (3, 0, 0), "G*C not positive")
    _require(positive["KH_C_inertia"] == (3, 0, 0), "KH*C not positive")
    _require(
        positive["Kplus_C_inertia"] == (3, 0, 0), "Kplus*C not positive"
    )

    negative = criterion_fixture("negative_eigenvalue")
    _require(
        negative["KH_C_inertia"] != (3, 0, 0),
        "negative eigenvalue mutation was accepted",
    )
    nonreal = criterion_fixture("nonreal_pair")
    _require(nonreal["L_G_self_adjoint"], "nonreal control lost G self-adjointness")
    _require(
        any("I" in value for value in nonreal["spectrum"]),
        "nonreal mutation lost complex spectrum",
    )
    jordan = criterion_fixture("jordan")
    _require(jordan["L_G_self_adjoint"], "Jordan control lost G self-adjointness")
    _require(not jordan["L_diagonalizable"], "Jordan mutation was accepted")

    # Re-derive the pullback determinant formula on a generic diagonal fixture.
    G = sp.diag(sp.Rational(2), -sp.Rational(3), -sp.Rational(5))
    H = sp.diag(sp.Rational(7), -sp.Rational(11), -sp.Rational(13))
    A = sp.diag(sp.Rational(17), sp.Rational(19), sp.Rational(23))
    KH = adjoint(A) * H * A
    L = G.inv() * KH
    lhs = sp.factor(L.det())
    rhs = sp.factor(
        adjoint(A).det() * A.det() * H.det() / G.det()
    )
    _require(sp.simplify(lhs - rhs) == 0, "determinant ratio identity failed")
    _require(
        sp.simplify(lhs - adjoint(A).det() * A.det()) != 0,
        "mutation dropping endpoint determinant ratio was accepted",
    )

    getcontext().prec = 70
    l2 = Decimal(
        scalar["certified_lower_bounds"]["spin_2"]["abs_A_out_squared_lower"]
    )
    l1 = Decimal(
        scalar["certified_lower_bounds"]["spin_1"]["abs_A_out_squared_lower"]
    )
    upper = Decimal(1) / ((Decimal(1) + l2) ** 2 * (Decimal(1) + l1))
    recorded = cert["physical_audit"]["partial_determinant_information"][
        "cell_bound"
    ]
    _require(recorded == f"0<det(L_H)<{upper}", "cell product bound drift")
    _require(Decimal(0) < upper < Decimal(1), "product upper bound not strict")

    flags = cert["claim_flags"]
    _require(flags["spectral_criterion_exact"], "theorem flag absent")
    _require(
        not flags["physical_full_typed_Tminus_available"],
        "missing typed matrix promoted",
    )
    _require(
        not flags["physical_generalized_spectrum_certified"],
        "undefined spectrum promoted",
    )
    _require(
        not flags["physical_channel_factorized_C_certified"],
        "factorized C existence promoted",
    )
    _require(
        not flags["physical_channel_factorized_C_obstructed"],
        "factorized C obstruction promoted",
    )
def verify() -> None:
    verify_path(HERE / "certificate.json")
    print("PASS channel-factorized C criterion and fail-closed physical audit")


if __name__ == "__main__":
    verify()
