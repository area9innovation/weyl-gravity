"""Exact all-ell two-parity q-minus resonance matrix on the tuned divisor."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_qminus_parity_resonance_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_symbolic_ell_qminus_parity_resonance_matrix.schema.json"
PBW_SLICE = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_weyl_symbolic_ell_qminus_parity_pbw_slice.json"
INPUTS = {
    "axial_all_ell": ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_axial_qminus_obstruction.json",
    "ell2_direct_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_parity_resonance_matrix.json",
    "symbolic_collision": ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_qminus_self_collision.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _symbols() -> tuple[sp.Symbol, ...]:
    ell = sp.symbols("ell", integer=True, positive=True)
    root, momentum = sp.symbols("r k", positive=True, real=True)
    return ell, root, momentum


def _parse_slice() -> dict[str, sp.Expr]:
    payload = json.loads(PBW_SLICE.read_text(encoding="utf-8"))
    _require(
        payload["result_id"] == "EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_QMINUS_PARITY_PBW_SLICE",
        "parity PBW slice identity changed",
    )
    _require(payload["extraction"]["highest_weight_isolates_L_2ell"], "top-output isolation changed")
    _require(payload["extraction"]["maximum_total_derivative_order"] == 4, "q2 differential order changed")
    ell, root, momentum = _symbols()
    local = {
        "ell": ell,
        "r": root,
        "k": momentum,
        "C_ell": sp.binomial(2 * ell, ell) ** 2 / sp.binomial(4 * ell, 2 * ell),
    }
    return {
        key: sp.factor(sp.sympify(value, locals=local))
        for key, value in payload["reduced_axisymmetric_pairings"].items()
    }


def symbolic_result() -> dict[str, sp.Expr]:
    ell, root, momentum = _symbols()
    pairings = _parse_slice()
    axial = pairings["polar_output_from_axial_axial"]
    polar = pairings["polar_output_from_polar_polar"]
    cross = pairings["axial_output_from_axial_plus_polar_minus"]
    eigenvalue = ell * (ell + 1)
    _require(sp.factor(polar + eigenvalue * axial / 2) == 0, "polar/axial diagonal ratio changed")

    cross_a = 3 * ell**3 + 8 * ell**2 + 5 * ell
    cross_b = 2 * ell**2 + 5 * ell + 1
    cross_norm = sp.factor(cross_a**2 - 2 * ell * (ell + 1) * cross_b**2)
    expected_norm = ell * (ell - 1) ** 3 * (ell + 1) * (ell + 2)
    _require(sp.factor(cross_norm - expected_norm) == 0, "cross nonvanishing factorization changed")

    a_plus, a_minus, p_plus, p_minus = sp.symbols("a_plus a_minus p_plus p_minus")
    diagonal_polynomial = sp.expand(a_plus * a_minus - eigenvalue * p_plus * p_minus / 2)
    cross_polynomial = sp.expand(a_plus * p_minus - a_minus * p_plus)
    sheet_scale = sp.sqrt(eigenvalue / 2)
    for sign in (-1, 1):
        substitution = {a_plus: sign * sheet_scale * p_plus, a_minus: sign * sheet_scale * p_minus}
        _require(sp.simplify(diagonal_polynomial.subs(substitution)) == 0, "diagonal sheet changed")
        _require(sp.simplify(cross_polynomial.subs(substitution)) == 0, "cross sheet changed")

    return {
        "ell": ell,
        "root": root,
        "momentum": momentum,
        "eigenvalue": eigenvalue,
        "axial": axial,
        "polar": polar,
        "cross": cross,
        "cross_a": cross_a,
        "cross_b": cross_b,
        "cross_norm": cross_norm,
        "diagonal_polynomial": diagonal_polynomial,
        "cross_polynomial": cross_polynomial,
        "sheet_scale": sheet_scale,
    }


def build_certificate() -> dict[str, object]:
    inputs = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    axial_input = inputs["axial_all_ell"]
    _require(
        axial_input["classification"]["coefficient_strictly_positive_every_integer_ell_ge_2"],
        "all-ell axial input changed",
    )
    _require(
        inputs["symbolic_collision"]["classification"]["unique_nonzero_frequency_collision_is_L_2ell_K0_p_shell"],
        "unique shell input changed",
    )
    result = symbolic_result()
    ell = result["ell"]
    root = result["root"]
    momentum = result["momentum"]
    assert isinstance(ell, sp.Symbol) and isinstance(root, sp.Symbol) and isinstance(momentum, sp.Symbol)

    stored_axial = sp.sympify(
        axial_input["symbolic_adjoint_pairing"]["axisymmetric_pairing"],
        locals={"ell": ell, "r": root},
    )
    _require(sp.factor(result["axial"] - stored_axial) == 0, "axial slice disagrees with frozen theorem")

    ell2 = inputs["ell2_direct_matrix"]["resonance_matrix"]
    ell2_substitution = {
        ell: 2,
        root: 2 * sp.sqrt(3),
        momentum: sp.sqrt(2 * sp.sqrt(3) - sp.Rational(7, 6)),
    }
    _require(
        sp.factor(sp.sqrtdenest(result["axial"].subs(ell2_substitution)) - sp.sympify(ell2["axial_diagonal_coefficient"])) == 0,
        "ell=2 axial diagonal replay changed",
    )
    _require(
        sp.factor(result["polar"].subs(ell2_substitution) / result["axial"].subs(ell2_substitution) - sp.sympify(ell2["polar_over_axial_diagonal_ratio"])) == 0,
        "ell=2 polar diagonal replay changed",
    )
    _require(
        sp.factor(sp.sqrtdenest(result["cross"].subs(ell2_substitution)) - sp.sympify(ell2["cross_coefficient"])) == 0,
        "ell=2 cross replay changed",
    )

    slice_payload = json.loads(PBW_SLICE.read_text(encoding="utf-8"))
    return {
        "schema": "einstein-maxwell-weyl-symbolic-ell-qminus-parity-resonance-matrix-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_QMINUS_PARITY_RESONANCE_MATRIX",
        "result_state": "ALL_ELL_TUNED_QMINUS_TWO_PARITY_RESONANCE_MATRIX_AND_NULL_VARIETY_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_EVERY_INTEGER_ELL_AT_ONE_TUNED_NONZERO_MOMENTUM_FIBRE",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 with circumference tuned separately for each ell",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "axial and polar Einstein-minus coefficients at opposite tuned compact momenta inside the common-zero construction",
            "degree": 2,
            "parity": "both input parities; polar and axial p-primary L=2ell outputs kept separate",
            "ell": "every integer input ell>=2; output L=2*ell",
            "m": "axisymmetric input and output, derived through the exact highest-weight coefficient",
            "k": "+/-sqrt(sqrt(2*ell*(ell+1))-ell/2-1/6)",
            "omega": "input omega_minus and output Omega=2*omega_minus",
        },
        "resonance_matrix": {
            "coefficient_symbols": ["a_+", "a_-", "p_+", "p_-"],
            "R_axial_diagonal": str(result["axial"]),
            "R_polar_diagonal": str(result["polar"]),
            "X_axial_polar": str(result["cross"]),
            "polar_output_functional": "R_axial_diagonal*(a_+*a_- - ell*(ell+1)*p_+*p_-/2)",
            "axial_output_functional": "X_axial_polar*(a_+*p_- - a_-*p_+)",
            "polar_over_axial_diagonal_ratio": "-ell*(ell+1)/2",
        },
        "nonvanishing_proofs": {
            "axial_diagonal": "strictly positive by the imported all-ell axial theorem",
            "polar_diagonal": "strictly negative because its ratio to the positive axial coefficient is -ell*(ell+1)/2",
            "cross_A_ell": str(result["cross_a"]),
            "cross_B_ell": str(result["cross_b"]),
            "cross_norm_factorization": str(result["cross_norm"]),
            "cross_sign_for_positive_k": "strictly negative: A_ell>sqrt(2*ell*(ell+1))*B_ell",
        },
        "resonance_zero_variety": {
            "equations": [str(result["diagonal_polynomial"]), str(result["cross_polynomial"])],
            "coordinate_planes": [
                "a_+=p_+=0 with (a_-,p_-) arbitrary",
                "a_-=p_-=0 with (a_+,p_+) arbitrary",
            ],
            "two_momentum_sheets": [
                "a_+=+sqrt(ell*(ell+1)/2)*p_+ and a_-=+sqrt(ell*(ell+1)/2)*p_-",
                "a_+=-sqrt(ell*(ell+1)/2)*p_+ and a_-=-sqrt(ell*(ell+1)/2)*p_-",
            ],
            "set_theoretic_completeness": "If neither signed-momentum vector vanishes, the cross equation makes them proportional and the diagonal equation fixes the common ratio to either signed square root; the remaining cases are the two coordinate planes.",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {
                "status": "OPEN",
                "certified_substatement": "off the displayed zero variety the unique p-shell collision obstructs bounded correction; complete all-channel inversion on the two sheets is not certified for general ell",
            },
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {
                "status": "CERTIFIED",
                "reason": "the finite p-shell resonances admit the certified secular inverse once the stabilizer moment maps vanish",
            },
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "action_derived_two_parity_matrix_computed": True,
            "all_three_coefficients_nonzero_every_integer_ell_ge_2": True,
            "complete_resonance_zero_variety_classified": True,
            "nonzero_two_momentum_null_sheets_exist_every_integer_ell_ge_2": True,
            "general_all_channel_bounded_extension_on_null_sheets": False,
            "fixed_circumference_or_multiple_abs_momentum_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The all-ell obstruction is parity-indefinite rather than definite: pure axial and pure polar products have opposite polar-output signs, and the axial-polar source supplies the independent axial-output equation. Their common zero set consists of two one-sided planes and two nonzero mixed-parity sheets. Thus the unique resonance admits cancellation at every ell, but this matrix alone does not prove a complete bounded second-order correction on those sheets.",
        "next_gate": "test all remaining output channels on the two symbolic mixed-parity sheets, then join the result to the fixed-circumference finite-multimomentum source matrix",
        "claim_boundary": "This theorem classifies only the unique L=2ell q-minus sum-frequency resonance matrix at one separately tuned |k| for each ell>=2. It does not certify full bounded extension on the null sheets, one fixed circumference, multiple |k| joins, causal transport, final residual descent, observation or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "pbw_slice": {"path": str(PBW_SLICE.relative_to(ROOT)), "sha256": _sha256(PBW_SLICE)},
            "parent_q2_sha256": slice_payload["parent"]["q2_sha256"],
            "parent_action_sha256": slice_payload["parent"]["action_sha256"],
            "parent_row_layout_sha256": slice_payload["parent"]["row_layout_sha256"],
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_symbolic_ell_qminus_parity_resonance_matrix --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_symbolic_ell_qminus_parity_resonance_matrix.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_symbolic_ell_qminus_parity_resonance_matrix",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build_certificate()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        _require(json.loads(OUTPUT.read_text(encoding="utf-8")) == value, "stale symbolic parity certificate")
    print("EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_QMINUS_PARITY_RESONANCE_MATRIX: PASS")


if __name__ == "__main__":
    main()
