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
SCHEMA_PATH = (
    ROOT / "bridge" / "einstein_sector" / "schema" / "bondi_bach_indicial.schema.json"
)


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


def _wave_action(
    expression: sp.Expr, u: sp.Symbol, r: sp.Symbol, angular: sp.Expr
) -> sp.Expr:
    """Apply the scalar flat wave operator in retarded coordinates."""

    return sp.expand(
        -2 * sp.diff(expression, u, r)
        + sp.diff(expression, r, 2)
        + 2 * (sp.diff(expression, r) - sp.diff(expression, u)) / r
        - angular * expression / r**2
    )


def _direct_wave_check() -> dict[str, str]:
    u, r = sp.symbols("u r", positive=True, real=True)
    weight, angular = sp.symbols("s L", real=True)
    f = sp.Function("f")(u)
    radial = r ** (-weight) * f

    # Box=-2 d_u d_r+d_r^2+(2/r)(d_r-d_u)+(1/r^2) Delta_S2.
    direct = sp.factor(_wave_action(radial, u, r, angular))
    a, b = wave_coefficients(weight, angular)
    expected = sp.factor(
        a * r ** (-weight - 1) * sp.diff(f, u)
        + b * r ** (-weight - 2) * f
    )
    _require(sp.simplify(direct - expected) == 0, "retarded wave formula is wrong")
    direct_biwave = sp.factor(_wave_action(direct, u, r, angular))
    c_second, c_first, c_zero = biwave_coefficients(weight, angular)
    expected_biwave = sp.factor(
        c_second * r ** (-weight - 2) * sp.diff(f, u, 2)
        + c_first * r ** (-weight - 3) * sp.diff(f, u)
        + c_zero * r ** (-weight - 4) * f
    )
    _require(
        sp.simplify(direct_biwave - expected_biwave) == 0,
        "direct retarded biwave formula is wrong",
    )
    return {
        "wave_operator": "-2 d_u d_r+d_r^2+(2/r)(d_r-d_u)+(1/r^2) Delta_S2",
        "action": (
            "Box[r^(-s)fY]=2(s-1)r^(-s-1)f'Y+"
            "[s(s-1)-L]r^(-s-2)fY"
        ),
        "direct_biwave_check": "PASS",
    }


def _direct_series_check() -> dict[str, Any]:
    """Extract finite-series coefficients and compare with both recursions."""

    u, r = sp.symbols("u r", positive=True, real=True)
    angular = sp.symbols("L", real=True)
    checked_weights = [0, 1, 3]
    term_count = 5

    for weight in checked_weights:
        functions = [sp.Function(f"f_{weight}_{index}")(u) for index in range(term_count)]
        series = sum(
            r ** (-weight - index) * function
            for index, function in enumerate(functions)
        )
        direct_wave = _wave_action(series, u, r, angular)
        direct_biwave = _wave_action(direct_wave, u, r, angular)

        for index, function in enumerate(functions):
            s_current = sp.Integer(weight + index)
            a_current, _ = wave_coefficients(s_current, angular)
            expected_wave = a_current * sp.diff(function, u)
            if index > 0:
                _, b_previous = wave_coefficients(s_current - 1, angular)
                expected_wave += b_previous * functions[index - 1]
            actual_wave = sp.expand(direct_wave).coeff(
                r, -(weight + index + 1)
            )
            _require(
                sp.simplify(actual_wave - expected_wave) == 0,
                f"wave series recurrence failed at p={weight}, j={index}",
            )

            c_current = biwave_coefficients(s_current, angular)[0]
            expected_biwave = c_current * sp.diff(function, u, 2)
            if index > 0:
                d_previous = biwave_coefficients(s_current - 1, angular)[1]
                expected_biwave += d_previous * sp.diff(functions[index - 1], u)
            if index > 1:
                e_previous = biwave_coefficients(s_current - 2, angular)[2]
                expected_biwave += e_previous * functions[index - 2]
            actual_biwave = sp.expand(direct_biwave).coeff(
                r, -(weight + index + 2)
            )
            _require(
                sp.simplify(actual_biwave - expected_biwave) == 0,
                f"biwave series recurrence failed at p={weight}, j={index}",
            )

    return {
        "method": "direct coefficient extraction from finite retarded series",
        "checked_integer_weights": checked_weights,
        "terms_per_weight": term_count,
        "wave_recurrence": "PASS",
        "biwave_recurrence": "PASS",
    }


def _validate_contract(payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA_PATH)
    _require(
        schema.get("$id") == "pure-weyl-bondi-bach-indicial-v2",
        "wrong Bondi/Bach indicial schema id",
    )
    for key in schema.get("required", []):
        _require(key in payload, f"indicial certificate is missing required field {key}")
    _require(payload.get("schema") == schema.get("$id"), "schema id mismatch")
    _require(
        payload.get("schema_path")
        == "bridge/einstein_sector/schema/bondi_bach_indicial.schema.json",
        "schema path mismatch",
    )
    _require(payload.get("schema_sha256") == _sha256(SCHEMA_PATH), "schema hash mismatch")
    _require(
        payload.get("result_id") == "BONDI_BACH_RADIAL_INDICIAL_ROOTS",
        "result id mismatch",
    )
    _require(
        payload.get("result_state")
        == "PROVED_REDUCED_RADIATIVE_CHANNEL_WITH_P1_OBSTRUCTION",
        "result state mismatch",
    )
    _require(payload.get("dependency_tags") == ["REDUCED-MODE"], "wrong dependency tag")
    _require(payload.get("radiative_indicial_roots") == ["0", "1"], "root list mismatch")
    provenance = payload.get("provenance", {})
    _require(
        provenance.get("generator_path")
        == "bridge/einstein_sector/bondi_bach_indicial.py",
        "generator path mismatch",
    )
    _require(
        provenance.get("generator_sha256") == _sha256(Path(__file__)),
        "generator hash mismatch",
    )
    flags = payload.get("claim_flags", {})
    required_flags = schema.get("properties", {}).get("claim_flags", {}).get(
        "required", []
    )
    _require(set(flags) == set(required_flags), "claim flag inventory mismatch")
    for key in required_flags:
        _require(isinstance(flags.get(key), bool), f"claim flag {key} is not boolean")
    _require(
        flags.get("p1_non_einstein_obstruction_identified") is True,
        "p=1 obstruction missing",
    )
    _require(
        flags.get("p0_nonzero_L_wave_kernel_trivial") is True,
        "p=0 wave-kernel result missing",
    )
    _require(
        flags.get("fixed_boundary_metric_isolates_full_einstein_sector") is False,
        "boundary metric was incorrectly promoted to full Einstein selection",
    )
    _require(
        payload.get("full_tensor_completion_gate", {}).get("status")
        == "OPEN_FAIL_CLOSED"
        and flags.get("full_tensor_bondi_recursion_constructed") is False,
        "full tensor Bondi recursion was promoted without its completion gate",
    )


def build_certificate() -> dict[str, Any]:
    flat = _load(FLAT_TT_INPUT)
    _require(
        flat.get("operator_identity") == "B_1(h_TT)=-(1/4) Box^2 h_TT",
        "flat TT Bach premise is missing",
    )
    _require(flat.get("helicity_commutator_zero") is True, "helicity premise failed")

    p, angular = sp.symbols("p L", real=True)
    index = sp.symbols("j", integer=True, nonnegative=True)
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

    u = sp.symbols("u", real=True)
    f_zero = sp.Function("f_0")(u)
    f_one = sp.Function("f_1")(u)
    kappa = 2 * sp.diff(f_one, u) - angular * f_zero
    p_one_next_bach = 8 * sp.diff(f_one, u, 2) - 4 * angular * sp.diff(f_zero, u)
    _require(
        sp.simplify(p_one_next_bach - 4 * sp.diff(kappa, u)) == 0,
        "p=1 Bach obstruction identity failed",
    )

    certificate = {
        "schema": "pure-weyl-bondi-bach-indicial-v2",
        "schema_path": "bridge/einstein_sector/schema/bondi_bach_indicial.schema.json",
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "BONDI_BACH_RADIAL_INDICIAL_ROOTS",
        "result_state": "PROVED_REDUCED_RADIATIVE_CHANNEL_WITH_P1_OBSTRUCTION",
        "provenance": {
            "input_base_commit": "1f87e38d3282defef2e69867dd53f7deac70bec6",
            "generator_path": "bridge/einstein_sector/bondi_bach_indicial.py",
            "generator_sha256": _sha256(Path(__file__)),
        },
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
            "equation_rule": "sum of the listed terms equals zero",
            "wave_terms": [
                {
                    "field": "d_u f_j",
                    "coefficient": str(
                        sp.factor(wave_coefficients(p + index, angular)[0])
                    ),
                },
                {
                    "field": "f_(j-1)",
                    "coefficient": str(
                        sp.factor(wave_coefficients(p + index - 1, angular)[1])
                    ),
                },
            ],
            "biwave_terms": [
                {
                    "field": "d_u^2 f_j",
                    "coefficient": str(
                        sp.factor(biwave_coefficients(p + index, angular)[0])
                    ),
                },
                {
                    "field": "d_u f_(j-1)",
                    "coefficient": str(
                        sp.factor(biwave_coefficients(p + index - 1, angular)[1])
                    ),
                },
                {
                    "field": "f_(j-2)",
                    "coefficient": str(
                        sp.factor(biwave_coefficients(p + index - 2, angular)[2])
                    ),
                },
            ],
            "leading_radiative_equation": "4p(p-1) d_u^2 f_0=0",
            "machine_check": _direct_series_check(),
        },
        "radiative_root_definition": (
            "f_0(u,x) is treated as freely variable radiative data, so the "
            "coefficient of d_u^2 f_0 must vanish identically"
        ),
        "radiative_indicial_polynomial": str(c_second),
        "radiative_indicial_roots": [str(root) for root in roots],
        "p1_einstein_compatible_falloff": {
            "cartesian_amplitude": "phi=r^-1 f_0(u,x)+O(r^-2)",
            "bondi_angular_metric": "h_AB=r C_AB+O(1)",
            "unphysical_angular_metric": "h_tilde_AB=r^-1 C_AB+O(r^-2)",
            "boundary_metric_changed": False,
            "kappa_definition": "kappa(x)=2 d_u f_1-L f_0",
            "bach_next_recursion": "4 d_u kappa=0",
            "bach_allows": (
                "kappa is arbitrary u-independent angular data in this scalar recursion"
            ),
            "einstein_subconstraint": "kappa=0",
            "formal_extension": (
                "for every later j>=1 the coefficient of d_u^2 f_j is "
                "4(j+1)j, which is nonzero, so the scalar recursion can be "
                "continued without imposing an algebraic condition on kappa"
            ),
            "interpretation": (
                "Einstein-compatible falloff containing both the Einstein wave "
                "subspace and a same-falloff non-Einstein Bach datum"
            ),
        },
        "p0_extra_bach_falloff": {
            "cartesian_amplitude": "phi=f_0(u,x)+O(r^-1)",
            "bondi_angular_metric": "h_AB=r^2 A_AB+O(r)",
            "unphysical_angular_metric": "h_tilde_AB=A_AB+O(r^-1)",
            "boundary_metric_changed": True,
            "wave_image": "Box phi=-2 r^-1 d_u f_0-L r^-2 f_0+O(r^-3 from f_1)",
            "wave_recursion_first_two_orders": ["d_u f_0=0", "L f_0=0"],
            "wave_kernel_conclusion": (
                "for L nonzero, a nonzero p=0 leading datum cannot lie in the wave kernel"
            ),
            "scalar_exception": "L=0 permits only u-independent leading f_0 at these orders",
            "interpretation": "additional leading Bach radiative branch",
        },
        "kinematic_boundary_selection": {
            "condition": (
                "delta h_tilde_AB restricted to null infinity is zero in the "
                "selected completion"
            ),
            "representative_falloff": (
                "in the chosen flat Cartesian TT representative, h_ij=O(r^-1)"
            ),
            "effect": (
                "excludes the leading p=0 boundary-metric deformation while "
                "retaining p=1 falloff"
            ),
            "does_not_exclude": "the u-independent kappa datum inside the p=1 Bach recursion",
            "gauge_invariant_equivalence_to_representative_falloff_proved": False,
            "locality": (
                "radial falloff condition at null infinity, not a future endpoint "
                "condition"
            ),
            "status": "KINEMATIC_LEADING_BRANCH_ONLY",
        },
        "exceptional_and_coupled_sectors": [
            "L=0 and L=2 are scalar-recurrence degeneracies, not certified physical spin-2 exceptional modes",
            "TT constraints couple angular components and must be imposed in the full tensor recursion",
            "the physical angular spectrum must be recomputed with tensor or spin-weighted harmonics",
            "soft/memory and Coulombic data are not exhausted by the p=0 scalar-amplitude branch",
        ],
        "full_tensor_completion_gate": {
            "status": "OPEN_FAIL_CLOSED",
            "reason": (
                "Cartesian TT scalar amplitudes do not supply the Bondi radial "
                "constraint hierarchy, residual gauge action, or physical spin-2 "
                "angular spectrum"
            ),
            "required_objects": [
                "linear Bondi-gauge ansatz for h_uu, h_ur, h_uA, and trace-free h_AB",
                "all independent linearized Bach rows expanded in inverse radius",
                "radial constraint and supplementary-equation hierarchy",
                "tensor or spin-weighted spherical-harmonic angular operators",
                "boundary-preserving residual Diff x Weyl transformations",
                "decision whether the reduced p=1 kappa datum survives the tensor constraints",
            ],
            "promotion_rule": (
                "full_tensor_bondi_recursion_constructed remains false until all "
                "required objects have exact machine checks"
            ),
        },
        "claim_flags": {
            "radiative_indicial_roots_classified": True,
            "p0_branch_changes_unphysical_boundary_metric": True,
            "p0_nonzero_L_wave_kernel_trivial": True,
            "p1_non_einstein_obstruction_identified": True,
            "fixed_boundary_metric_excludes_leading_p0_kinematically": True,
            "p1_falloff_proved_einstein": False,
            "fixed_boundary_metric_isolates_full_einstein_sector": False,
            "full_tensor_bondi_recursion_constructed": False,
            "boundary_condition_preserved_by_causal_green_operators": False,
            "p0_branch_proved_non_gauge": False,
            "all_extra_weyl_channels_classified": False,
            "einstein_scattering_sector_recovered": False,
        },
        "scope_guards": [
            "exact for the scalar amplitude of each flat Cartesian TT polarization",
            "leading radiative indicial roots only",
            "p=1 is Einstein-compatible falloff, not an Einstein-sector equivalence",
            "not the complete tensor Bondi gauge or BV complex",
            "no surface-charge or symplectic-flux classification",
            "no nonlinear or global scattering theorem",
        ],
        "verification_command": (
            "python3 -m bridge.einstein_sector.bondi_bach_indicial --verify "
            "bridge/certificates/bondi_bach_indicial.json"
        ),
    }
    _validate_contract(certificate)
    return certificate


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
