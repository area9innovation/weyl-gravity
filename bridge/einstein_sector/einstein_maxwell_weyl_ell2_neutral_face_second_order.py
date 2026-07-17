"""Second-order extension of the axial ell=2 neutral mixed face."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import _polar_action_operator


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_neutral_face_second_order.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_neutral_face_second_order.schema.json"
INPUTS = {
    "balanced_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json",
    "k0_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
}


class NeutralFaceSecondOrderError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise NeutralFaceSecondOrderError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.radsimp(sp.simplify(value)))


def _parse_vector(values: list[str], local: dict[str, Any]) -> sp.Matrix:
    return sp.Matrix([sp.sympify(value, locals=local) for value in values])


def _algebraic_nonzero(value: sp.Expr) -> dict[str, str | bool]:
    z = sp.symbols("z")
    polynomial = sp.Poly(sp.minpoly(value, z), z)
    constant = polynomial.TC()
    _require(constant != 0, f"algebraic nonzero witness failed for {value}")
    return {
        "value": str(_canonical(value)),
        "minimal_polynomial": str(polynomial.as_expr()),
        "nonzero_constant_term": str(constant),
        "certified_nonzero": True,
    }


def _source_data(record: dict[str, Any]) -> tuple[sp.Matrix, dict[int, sp.Matrix], tuple[sp.Symbol, ...]]:
    symbols = sp.symbols("h_1 q_1 omega_1 h_2 q_2 omega_2", real=True)
    local = {str(symbol): symbol for symbol in symbols} | {"I": sp.I, "sqrt": sp.sqrt}
    source = record["bilinear_source_polynomial"]
    homogeneous = _parse_vector(source["homogeneous_rows"], local)
    generic = {
        int(ell): _parse_vector(values, local)
        for ell, values in source["generic_action_rows_by_ell"].items()
    }
    return homogeneous, generic, symbols


def _branches() -> dict[str, tuple[sp.Expr, sp.Expr, sp.Expr]]:
    root = sp.sqrt(3)
    return {
        "minus": (-2, 2 * root, sp.sqrt(6 - 2 * root)),
        "extra": (-sp.Rational(2, 3), 6, 4 / root),
        "plus": (-2, -2 * root, sp.sqrt(6 + 2 * root)),
    }


def _substitute(source: sp.Matrix, symbols: tuple[sp.Symbol, ...], left: tuple[sp.Expr, sp.Expr, sp.Expr], right: tuple[sp.Expr, sp.Expr, sp.Expr], right_frequency_sign: int, factor: sp.Expr) -> tuple[sp.Matrix, sp.Expr]:
    h1, q1, w1, h2, q2, w2 = symbols
    substitution = {h1: left[0], q1: left[1], w1: left[2], h2: right[0], q2: right[1], w2: right_frequency_sign * right[2]}
    return (factor * source.subs(substitution)).applyfunc(_canonical), _canonical(left[2] + right_frequency_sign * right[2])


def _raw_balance(homogeneous: sp.Matrix, symbols: tuple[sp.Symbol, ...]) -> tuple[dict[str, Any], dict[str, sp.Matrix], sp.Expr]:
    branches = _branches()
    zero_sources = {
        name: _substitute(homogeneous, symbols, branch, branch, -1, sp.Rational(1, 4))[0]
        for name, branch in branches.items()
    }
    tau = {name: _canonical(source[0]) for name, source in zero_sources.items()}
    _require(all(source[1] == source[3] == 0 and _canonical(source[0] - 2 * source[2]) == 0 for source in zero_sources.values()), "zero-source collinearity changed")
    _require(tau["minus"] > 0 and tau["extra"] < 0 and tau["plus"] < 0, "Taub sign pattern changed")
    x_plus, x_extra = sp.symbols("x_plus x_extra", nonnegative=True, real=True)
    x_minus = _canonical(-(tau["plus"] * x_plus + tau["extra"] * x_extra) / tau["minus"])
    combined = (x_minus * zero_sources["minus"] + x_extra * zero_sources["extra"] + x_plus * zero_sources["plus"]).applyfunc(_canonical)
    _require(combined == sp.zeros(4, 1), "balanced homogeneous source did not vanish")
    return {
        "raw_squared_amplitudes": "x_plus,x_extra>=0 and x_minus as displayed; arbitrary constant phases are allowed",
        "Taub_coefficients": {name: str(value) for name, value in tau.items()},
        "x_minus": str(x_minus),
        "zero_source_vectors_E00_E11_E22_Maxwell1": {name: [str(value) for value in source] for name, source in zero_sources.items()},
        "collinearity": "each vector equals tau_branch*(1,0,1/2,0)",
        "combined_zero_source": [str(value) for value in combined],
        "entire_positive_quadrant_face_clears_homogeneous_cokernel": True,
    }, zero_sources, x_minus


def _nonzero_channels(homogeneous: sp.Matrix, generic: dict[int, sp.Matrix], symbols: tuple[sp.Symbol, ...]) -> dict[str, Any]:
    branches = _branches()
    definitions: list[tuple[str, str, str, int, sp.Rational]] = []
    names = list(branches)
    for name in names:
        definitions.append((f"{name}_self_sum", name, name, 1, sp.Rational(1, 8)))
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            definitions.append((f"{left}_{right}_sum", left, right, 1, sp.Rational(1, 4)))
            definitions.append((f"{left}_{right}_difference", left, right, -1, sp.Rational(1, 4)))

    homogeneous_operator_record = json.loads(INPUTS["balanced_source"].read_text())["homogeneous_operator"]
    Omega = sp.symbols("Omega", real=True)
    local = {"Omega": Omega, "I": sp.I}
    homogeneous_operator = sp.Matrix([[sp.sympify(value, locals=local) for value in row] for row in homogeneous_operator_record["matrix"]])
    action, (eigenvalue, momentum, frequency) = _polar_action_operator()
    output: dict[str, Any] = {}
    for label, left_name, right_name, sign, factor in definitions:
        homogeneous_source, output_frequency = _substitute(homogeneous, symbols, branches[left_name], branches[right_name], sign, factor)
        _require(output_frequency != 0, f"{label} lost nonzero frequency")
        block0 = homogeneous_operator.subs(Omega, output_frequency)
        correction0 = sp.Matrix([2 * homogeneous_source[1] / output_frequency**4, 0, -homogeneous_source[3] / output_frequency**2]).applyfunc(_canonical)
        remainder0 = (block0 * correction0 + homogeneous_source).applyfunc(_canonical)
        _require(remainder0 == sp.zeros(4, 1), f"{label} homogeneous correction failed")
        generic_rows: dict[str, Any] = {}
        for ell, source_polynomial in generic.items():
            source, source_frequency = _substitute(source_polynomial, symbols, branches[left_name], branches[right_name], sign, factor)
            _require(_canonical(source_frequency - output_frequency) == 0, "channel frequency mismatch")
            lam = sp.Integer(ell * (ell + 1))
            p_value = _canonical(output_frequency**2 - (lam - sp.Rational(2, 3)))
            q_value = _canonical((output_frequency**2 - lam) ** 2 - 2 * lam)
            p_witness = _algebraic_nonzero(p_value)
            q_witness = _algebraic_nonzero(q_value)
            block = action.subs({eigenvalue: lam, momentum: 0, frequency: output_frequency})
            determinant = _canonical(block.det())
            _require(determinant != 0, f"ell={ell} {label} determinant vanished")
            generic_rows[str(ell)] = {
                "source_action_rows": [str(value) for value in source],
                "p_shell_witness": p_witness,
                "q_shell_witness": q_witness,
                "operator_determinant": str(determinant),
                "correction": "-H_P(lambda,0,Omega)^(-1)*S; unique because the displayed exact determinant is nonzero",
            }
        output[label] = {
            "input_branches": [left_name, right_name],
            "channel_kind": "sum" if sign == 1 else "difference",
            "real_polarization_factor": str(factor),
            "output_frequency": str(output_frequency),
            "output_frequency_nonzero_witness": _algebraic_nonzero(output_frequency),
            "homogeneous_source_rows": [str(value) for value in homogeneous_source],
            "homogeneous_correction_C_K_U": [str(value) for value in correction0],
            "homogeneous_remainder": [str(value) for value in remainder0],
            "generic_polar_outputs": generic_rows,
        }
    return output


def _zero_generic_channels(generic: dict[int, sp.Matrix], symbols: tuple[sp.Symbol, ...], x_minus: sp.Expr) -> dict[str, Any]:
    branches = _branches()
    x_plus, x_extra = sp.symbols("x_plus x_extra", nonnegative=True, real=True)
    action, (eigenvalue, momentum, frequency) = _polar_action_operator()
    output: dict[str, Any] = {}
    for ell, source_polynomial in generic.items():
        sources = {name: _substitute(source_polynomial, symbols, branch, branch, -1, sp.Rational(1, 4))[0] for name, branch in branches.items()}
        combined = (x_minus * sources["minus"] + x_extra * sources["extra"] + x_plus * sources["plus"]).applyfunc(_canonical)
        lam = sp.Integer(ell * (ell + 1))
        block = action.subs({eigenvalue: lam, momentum: 0, frequency: 0})
        determinant = _canonical(block.det())
        _require(determinant != 0, f"ell={ell} zero block became singular")
        correction = (-block.inv() * combined).applyfunc(_canonical)
        remainder = (block * correction + combined).applyfunc(_canonical)
        _require(remainder == sp.zeros(4, 1), f"ell={ell} zero correction failed")
        output[str(ell)] = {
            "combined_source_action_rows": [str(value) for value in combined],
            "operator_determinant": str(determinant),
            "correction_At_B_Ct_U": [str(value) for value in correction],
            "operator_remainder": [str(value) for value in remainder],
        }
    return output


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["balanced_source"]["classification"]["complete_second_order_extension_constructed"], "balanced source input changed")
    _require(records["k0_cone"]["classification"]["full_generic_k0_common_zero_cone_classified"], "k=0 cone input changed")
    homogeneous, generic, symbols = _source_data(records["balanced_source"])
    balance, _, x_minus = _raw_balance(homogeneous, symbols)
    nonzero = _nonzero_channels(homogeneous, generic, symbols)
    zero_generic = _zero_generic_channels(generic, symbols, x_minus)
    return {
        "schema": "einstein-maxwell-weyl-ell2-neutral-face-second-order-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_AXIAL_NEUTRAL_FACE_SECOND_ORDER",
        "result_state": "TWO_PARAMETER_ELL2_AXIAL_NEUTRAL_FACE_SECOND_ORDER_EXTENDIBLE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_ELL2_M0_AXIAL_THREE_BRANCH_FACE",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
            "source_reuse": "the direct four-dimensional bilinear source polynomial is imported content-addressed from Paper 91's independently verified source certificate; no competing curvature reconstruction is introduced",
        },
        "domain": "real axial ell=2,m=0,k=0 first-order tangents spanning Einstein-plus, the second extra representative, and Einstein-minus, with arbitrary constant branch phases",
        "branch_representatives_Ht_Hx_Qt_Qx": {
            "minus": ["0", "-2", "0", "2*sqrt(3)"],
            "extra": ["0", "-2/3", "0", "6"],
            "plus": ["0", "-2", "0", "-2*sqrt(3)"],
        },
        "raw_amplitude_balance": balance,
        "nonzero_frequency_channel_ledger": nonzero,
        "zero_frequency_ell2_ell4_channels": zero_generic,
        "second_order_correction": {
            "construction": "sum the displayed homogeneous corrections and unique polar inverse corrections, multiplying unit self/cross sources by the corresponding branch amplitudes and phases, then add complex conjugates",
            "all_zero_frequency_homogeneous_sources_cancel": True,
            "all_nine_nonzero_frequency_pair_types_removable": True,
            "all_zero_frequency_ell2_ell4_sources_removable": True,
            "all_dependent_rows": "follow from the same constant-determinant Noether completion imported with the bilinear source certificate",
            "smooth_spatially_periodic_finite_quasiperiodic_correction": True,
        },
        "classification": {
            "paper91_boundary_ray_strictly_extended": True,
            "two_parameter_positive_quadrant_face_second_order_extendible": True,
            "arbitrary_constant_relative_phases_allowed": True,
            "complete_k0_density_cone_second_order_classified": False,
            "other_m_parity_extra_polarizations_classified": False,
            "all_orders_integrability": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "interpretation": "Paper 91's balanced ray is not isolated even after the full second-order equation is imposed. On the declared axial ell=2,m=0 face, the three zero-frequency source vectors are the same cokernel vector multiplied by their Taub coefficients. Therefore every Taub-balanced positive combination cancels the only non-removable homogeneous source, while all sum/difference and ell=2,4 zero channels are off-shell invertible.",
        "next_gate": "repeat the source-vector rank test for other m, parity, extra polarization, and ell; a rank increase would cut the general density cone below its Taub-zero locus",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem extends a declared two-parameter axial ell=2,m=0 face through second order. It does not classify the complete k=0 density cone, opposite-momentum phases, exceptional fourth-order modes, all-orders solutions, or causal/quantum physics.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_ell2_neutral_face_second_order --verify bridge/certificates/einstein_maxwell_weyl_ell2_neutral_face_second_order.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_neutral_face_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_neutral_face_second_order",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"ell=2 neutral-face certificate stale: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
