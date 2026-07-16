"""Exact parity/resonance ledger and first removable EE axial target block."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import sympy as sp
from sympy.physics.wigner import wigner_3j

from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import _generic_rows


ROOT = Path(__file__).resolve().parents[2]
AXIAL_EINSTEIN = ROOT / "bridge/certificates/einstein_maxwell_axial_master_complex.json"
POLAR_EINSTEIN = ROOT / "bridge/certificates/einstein_maxwell_polar_master_complex.json"
AXIAL_TARGET = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json"
PROJECTOR = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_extra_projector.json"
ADJOINT = ROOT / "bridge/certificates/einstein_maxwell_weyl_target_adjoint_witness.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_quadratic_channel_preflight.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_quadratic_channel_preflight.schema.json"


class AxialQuadraticChannelPreflightError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialQuadraticChannelPreflightError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _squarefree(value: int) -> tuple[int, int]:
    outside = 1
    inside = value
    divisor = 2
    while divisor * divisor <= inside:
        square = divisor * divisor
        while inside % square == 0:
            outside *= divisor
            inside //= square
        divisor += 1
    return outside, inside


def _add_radical(terms: dict[int, Fraction], coefficient: Fraction, radicand: int) -> None:
    outside, inside = _squarefree(radicand)
    terms[inside] = terms.get(inside, Fraction(0)) + coefficient * outside
    if terms[inside] == 0:
        del terms[inside]


def _resonance_polynomial_terms(
    ell_axial: int,
    ell_polar: int,
    ell_extra: int,
    momentum_axial: int,
    momentum_polar: int,
    branch_axial: int,
    branch_polar: int,
) -> dict[int, Fraction]:
    """Canonical radical expansion of (C-A-B)^2-4AB."""

    lam_a = ell_axial * (ell_axial + 1)
    lam_p = ell_polar * (ell_polar + 1)
    lam_x = ell_extra * (ell_extra + 1)
    rational_a = Fraction(momentum_axial**2 + lam_a)
    rational_b = Fraction(momentum_polar**2 + lam_p)
    rational_c = Fraction((momentum_axial + momentum_polar) ** 2 + lam_x) - Fraction(2, 3)
    delta = rational_c - rational_a - rational_b
    rad_a = 2 * lam_a
    rad_b = 2 * lam_p
    terms: dict[int, Fraction] = {}
    _add_radical(
        terms,
        delta**2 + Fraction(rad_a + rad_b) - 4 * rational_a * rational_b,
        1,
    )
    _add_radical(
        terms,
        branch_axial * (-2 * delta - 4 * rational_b),
        rad_a,
    )
    _add_radical(
        terms,
        branch_polar * (-2 * delta - 4 * rational_a),
        rad_b,
    )
    _add_radical(terms, -2 * branch_axial * branch_polar, rad_a * rad_b)
    return terms


def _terms_expression(terms: dict[int, Fraction]) -> sp.Expr:
    return sp.factor(
        sum(
            sp.Rational(coefficient.numerator, coefficient.denominator)
            * (1 if radicand == 1 else sp.sqrt(radicand))
            for radicand, coefficient in terms.items()
        )
    )


def _resonance_ledger() -> dict[str, Any]:
    scanned = 0
    exact = []
    nearest: tuple[float, tuple[int, ...]] | None = None
    for ell_axial in range(2, 9):
        for ell_polar in range(2, 9):
            for ell_extra in range(2, 9):
                if not abs(ell_axial - ell_polar) <= ell_extra <= ell_axial + ell_polar:
                    continue
                if (ell_axial + ell_polar - ell_extra) % 2:
                    continue
                lam_a = ell_axial * (ell_axial + 1)
                lam_p = ell_polar * (ell_polar + 1)
                lam_x = ell_extra * (ell_extra + 1)
                for momentum_axial in range(-4, 5):
                    for momentum_polar in range(-4, 5):
                        momentum_extra = momentum_axial + momentum_polar
                        for branch_axial in (-1, 1):
                            for branch_polar in (-1, 1):
                                terms = _resonance_polynomial_terms(
                                    ell_axial,
                                    ell_polar,
                                    ell_extra,
                                    momentum_axial,
                                    momentum_polar,
                                    branch_axial,
                                    branch_polar,
                                )
                                a = momentum_axial**2 + lam_a + branch_axial * math.sqrt(2 * lam_a)
                                b = momentum_polar**2 + lam_p + branch_polar * math.sqrt(2 * lam_p)
                                c = momentum_extra**2 + lam_x - 2 / 3
                                for temporal_sign in (-1, 1):
                                    scanned += 1
                                    defect = abs((math.sqrt(a) + temporal_sign * math.sqrt(b)) ** 2 - c)
                                    label = (
                                        ell_axial,
                                        ell_polar,
                                        ell_extra,
                                        momentum_axial,
                                        momentum_polar,
                                        branch_axial,
                                        branch_polar,
                                        temporal_sign,
                                    )
                                    if nearest is None or defect < nearest[0]:
                                        nearest = (defect, label)
                                    if not terms:
                                        exact.append(label)
    _require(scanned == 97848, "declared resonance scan cardinality changed")
    _require(not exact, "an exact resonance entered the declared scan window")
    assert nearest is not None
    _require(
        nearest[1] == (2, 4, 6, -3, 0, -1, -1, 1),
        f"nearest resonance fixture changed: {nearest[1]}",
    )
    nearest_terms = _resonance_polynomial_terms(*nearest[1][0:7])
    nearest_polynomial = _terms_expression(nearest_terms)
    _require(nearest_polynomial != 0, "nearest case became exactly resonant")
    return {
        "input_channel": "axial Einstein x polar Einstein -> axial Weyl-Maxwell",
        "selection_rules": {
            "circle_momentum": "k_X=k_A+k_P",
            "sphere_triangle": "|ell_A-ell_P|<=ell_X<=ell_A+ell_P",
            "axial_parity": "ell_A+ell_P-ell_X is even",
            "magnetic_number": "m_X=m_A+m_P",
            "temporal_frequency": "omega_X=|omega_A +/- omega_P|",
        },
        "window": {"ell_A": [2, 8], "ell_P": [2, 8], "ell_X": [2, 8], "k_A": [-4, 4], "k_P": [-4, 4]},
        "exact_method": "expand ((C-A-B)^2-4AB) in a canonical squarefree-radical basis over Q; zero requires every rational coefficient to vanish",
        "temporal_sign_and_branch_cases_scanned": scanned,
        "exact_resonances": exact,
        "no_exact_resonance_in_window": True,
        "nearest_nonresonant_case": {
            "labels": list(nearest[1]),
            "label_order": ["ell_A", "ell_P", "ell_X", "k_A", "k_P", "branch_A", "branch_P", "temporal_sign"],
            "numerical_absolute_shell_defect": repr(nearest[0]),
            "exact_squared_resonance_polynomial": str(nearest_polynomial),
            "exact_nonzero": True,
        },
    }


def _first_removable_block() -> dict[str, Any]:
    rows, symbols = _generic_rows()
    coefficients = sp.Matrix([symbols[name] for name in ("h_t", "h_x", "q_t", "q_x")])
    equations = sp.Matrix([rows[name] for name in ("metric_t", "metric_x", "maxwell_t", "maxwell_x")])
    hessian = (sp.diag(symbols["lambda"], -symbols["lambda"], 1, 1) * equations).jacobian(coefficients)
    root = sp.sqrt(3)
    source_frequency_squared = 24 - 8 * root
    fixture = hessian.subs(
        {symbols["lambda"]: 6, symbols["k"]: 0, symbols["omega"] ** 2: source_frequency_squared}
    ).applyfunc(sp.simplify)
    determinant = sp.factor(fixture.det())
    inverse = fixture.inv().applyfunc(lambda value: sp.factor(sp.radsimp(value)))
    _require((fixture * inverse).applyfunc(sp.simplify) == sp.eye(4), "fixture inverse failed")
    _require(determinant != 0, "selected EE block became resonant")
    gaunt = wigner_3j(2, 2, 2, 0, 0, 0)
    _require(gaunt == -sp.sqrt(70) / 35, "selected angular coupling witness changed")
    source = sp.Matrix(sp.symbols("S_1:5"))
    correction = (inverse * source).applyfunc(sp.factor)
    return {
        "input_modes": {
            "axial_Einstein": "ell=2,m=0,k=0, minus master branch",
            "polar_Einstein": "ell=2,m=0,k=0, minus master branch",
            "temporal_channel": "positive-frequency sum",
            "output": "axial ell=2,m=0,k=0 coefficient block",
            "angular_allowed_witness": str(gaunt),
        },
        "source_frequency_squared": str(source_frequency_squared),
        "extra_shell_frequency_squared": "16/3",
        "extra_shell_defect_p": str(sp.factor(source_frequency_squared - 6 + sp.Rational(2, 3))),
        "Einstein_shell_defect_q": str(sp.factor((source_frequency_squared - 6) ** 2 - 12)),
        "target_Hessian_row_order": ["lambda*metric_t", "-lambda*metric_x", "maxwell_t", "maxwell_x"],
        "target_Hessian_coefficient_order": ["H_t", "H_x", "Q_t", "Q_x"],
        "target_Hessian": [[str(value) for value in fixture.row(row)] for row in range(4)],
        "determinant": str(determinant),
        "inverse": [[str(value) for value in inverse.row(row)] for row in range(4)],
        "quadratic_source_convention": "S=D^2E_WM[Phi_A^(1),Phi_P^(1)], the mixed axial-polar component of (1/2)D^2E_WM[Phi_A^(1)+Phi_P^(1),Phi_A^(1)+Phi_P^(1)], in the density-weighted target row order",
        "universal_second_order_correction": [str(value) for value in correction],
        "inverse_identity_verified": True,
        "verdict": "every quadratic source vector in this selected harmonic-frequency block is removable by the displayed unique algebraic Phi^(2)=L_WM^(-1)S",
        "normal_extra_shell_projection": "NOT_APPLICABLE: the source frequency is off the extra shell, so the shell projector Pi_X must not be applied",
        "source_tensor_coefficient_computed": False,
    }


def build_certificate() -> dict[str, Any]:
    inputs = [AXIAL_EINSTEIN, POLAR_EINSTEIN, AXIAL_TARGET, PROJECTOR, ADJOINT]
    records = [json.loads(path.read_text(encoding="utf-8")) for path in inputs]
    expected = [
        "COMPACT_EM_AXIAL_MASTER_COMPLEX",
        "COMPACT_EM_POLAR_MASTER_COMPLEX",
        "EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR",
        "EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_PROJECTOR",
        "EINSTEIN_MAXWELL_WEYL_TARGET_CONSTANT_LAPSE_ADJOINT_WITNESS",
    ]
    _require([record["result_id"] for record in records] == expected, "preflight input result changed")
    return {
        "schema": "einstein-maxwell-weyl-axial-quadratic-channel-preflight-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_QUADRATIC_CHANNEL_PREFLIGHT",
        "result_state": "EXACT_EE_TO_AXIAL_EXTRA_RESONANCE_LEDGER_AND_FIRST_UNIVERSALLY_REMOVABLE_BLOCK_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_FINITE_CHANNEL_LEDGER_AND_ONE_REMOVABLE_EE_BLOCK",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {str(path.relative_to(ROOT)): _sha256(path) for path in inputs},
        },
        "correction_space_contract": {
            "smooth_global": "allows generalized/secular temporal corrections",
            "bounded_normal_mode": "forbids secular temporal corrections",
            "shared_fixed_bundle_condition": "second-order magnetic Chern-class lift is zero",
            "use_rule": "a nonzero quadratic coefficient is an obstruction only after pairing with a target adjoint cokernel class; off-shell finite blocks are solved by the target inverse",
        },
        "parity_and_resonance_ledger": _resonance_ledger(),
        "first_EE_block": _first_removable_block(),
        "classification": {
            "parity_error_in_axial_by_axial_projection_avoided": True,
            "finite_exact_resonance_window_classified": True,
            "first_selected_EE_output_block_removable_for_arbitrary_source": True,
            "actual_quadratic_source_tensor_computed": False,
            "general_nonlinear_Einstein_sector_closed": False,
            "all_harmonics_resonance_free": False,
            "Lorentzian_causal_claim": False,
        },
        "interpretation": "Axial output from two Einstein inputs must use an axial-polar pair. No such pair in the declared finite window lands exactly on an axial extra normal-mode shell. The lowest allowed EE sum-frequency block is fully invertible, so even a nonzero quadratic defect there is removable and cannot be a Taub no-go. This is one blockwise extension result, not nonlinear closure of the Einstein sector.",
        "next_gate": "compute the explicit mixed axial-polar D^2E_WM tensor coefficient for the selected ell=2 block and insert it into the displayed inverse; then expand the exact resonance ledger or attack constant-lapse difference-frequency channels",
        "claim_boundary": "The resonance result is a finite exact REDUCED-MODE scan, and the inverse is one algebraic harmonic block. Neither establishes all-mode nonlinear closure, a spacetime-local correction, causal well-posedness, boundary selection, scattering, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_quadratic_channel_preflight --verify bridge/certificates/einstein_maxwell_weyl_axial_quadratic_channel_preflight.json",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_quadratic_channel_preflight",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"stale quadratic channel preflight: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and args.verify is None:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
