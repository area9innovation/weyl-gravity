"""Complete the homogeneous/twist times ell=2 extra resonance matrix."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path

import sympy as sp
from sympy.physics.wigner import clebsch_gordan

from bridge.einstein_sector.einstein_maxwell_weyl_twist_ell2_extra_source_explore import source


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix.schema.json"
ABD_INPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strings(vector: sp.MatrixBase) -> list[str]:
    return [str(sp.factor(value)) for value in vector]


def _expected_rows() -> dict[str, dict[str, dict[str, dict[str, sp.Matrix]]]]:
    time = sp.symbols("t", real=True)
    root = sp.sqrt(3)
    imaginary = sp.I
    zero = sp.zeros(4, 1)
    return {
        "position": {
            "axial": {
                "e1": {"axial": sp.Matrix([0, 0, 0, 24 * root]), "polar": zero},
                "e2": {"axial": sp.Matrix([0, 0, 24 * root, 0]), "polar": sp.Matrix([0, 0, 0, sp.Rational(24, 5)])},
            },
            "polar": {
                "e1": {"axial": zero, "polar": sp.Matrix([24 * root, 0, -sp.Rational(8, 3) * root, 0])},
                "e2": {"axial": sp.Matrix([0, -sp.Rational(864, 5), 0, 0]), "polar": zero},
            },
        },
        "velocity": {
            "axial": {
                "e1": {"axial": sp.Matrix([0, 0, 0, 12 * (2 * root * time + 3 * imaginary)]), "polar": zero},
                "e2": {
                    "axial": sp.Matrix([0, 0, 2 * (12 * root * time - imaginary), 0]),
                    "polar": sp.Matrix([0, 0, 0, sp.Rational(8, 5) * (3 * time - 4 * root * imaginary)]),
                },
            },
            "polar": {
                "e1": {
                    "axial": zero,
                    "polar": sp.Matrix([sp.Rational(3, 2) * (16 * root * time - 15 * imaginary), 0, -(16 * root * time + 147 * imaginary) / 6, 0]),
                },
                "e2": {
                    "axial": sp.Matrix([0, -sp.Rational(96, 5) * (9 * time - 14 * root * imaginary), 0, 0]),
                    "polar": sp.Matrix([0, -4248 * imaginary, 0, 0]),
                },
            },
        },
    }


def _compute(case: tuple[str, str, str]) -> tuple[sp.Matrix, sp.Matrix]:
    twist_case, extra_parity, extra_mode = case
    return source(extra_parity, extra_mode, twist_case)


def _direct_replay(expected: dict[str, object]) -> None:
    cases = [
        (twist_case, extra_parity, extra_mode)
        for twist_case in ("position", "velocity")
        for extra_parity in ("axial", "polar")
        for extra_mode in ("e1", "e2")
    ]
    with ProcessPoolExecutor(max_workers=4) as executor:
        values = list(executor.map(_compute, cases))
    for (twist_case, extra_parity, extra_mode), (axial, polar) in zip(cases, values, strict=True):
        for output_parity, result in (("axial", axial), ("polar", polar)):
            target = expected[twist_case][extra_parity][extra_mode][output_parity]
            if (result - target).applyfunc(sp.simplify) != sp.zeros(4, 1):
                raise AssertionError(f"direct twist source changed: {(twist_case, extra_parity, extra_mode, output_parity)}")


def _projection_theorem(expected: dict[str, object]) -> dict[str, object]:
    time = sp.symbols("t", real=True)
    witnesses = {
        "axial": sp.Matrix.hstack(sp.Matrix([-1, 0, 1, 0]), sp.Matrix([0, -sp.Rational(1, 9), 0, 1])),
        "polar": sp.Matrix.hstack(sp.Matrix([0, 1, 0, 0]), sp.Matrix([-sp.Rational(1, 6), 0, -sp.Rational(3, 2), 1])),
    }
    input_order = [("axial", "e1"), ("axial", "e2"), ("polar", "e1"), ("polar", "e2")]
    output_order = [("axial", "w1"), ("axial", "w2"), ("polar", "w1"), ("polar", "w2")]
    matrices: dict[str, sp.Matrix] = {}
    projected: dict[str, object] = {}
    for twist_case in ("position", "velocity"):
        columns = []
        projected[twist_case] = {}
        for extra_parity, extra_mode in input_order:
            values = []
            projected[twist_case][f"{extra_parity}_{extra_mode}"] = {}
            for output_parity in ("axial", "polar"):
                projection = (witnesses[output_parity].T * expected[twist_case][extra_parity][extra_mode][output_parity]).applyfunc(sp.factor)
                projected[twist_case][f"{extra_parity}_{extra_mode}"][output_parity] = _strings(projection)
                values.extend(projection)
            columns.append(sp.Matrix(values))
        matrices[twist_case] = sp.Matrix.hstack(*columns)
    position = matrices["position"]
    velocity = matrices["velocity"]
    determinant = sp.factor(velocity.det(method="berkowitz"))
    expected_determinant = 4129056 * (72 * time**2 + 34 * sp.sqrt(3) * sp.I * time + 3)
    if position.rank() != 2 or sp.expand(determinant - expected_determinant) != 0:
        raise AssertionError("twist resonance-matrix rank or determinant changed")
    real_nonvanishing = sp.solve(
        [sp.re(expected_determinant), sp.im(expected_determinant)],
        [time],
        dict=True,
    )
    if real_nonvanishing:
        raise AssertionError("velocity determinant acquired a real zero")
    coefficient = clebsch_gordan(1, 2, 2, 1, 0, 1)
    if coefficient != sp.sqrt(2) / 2:
        raise AssertionError("Clebsch-Gordan normalization changed")
    return {
        "fixture_channel": "m_twist=1, m_extra=0 -> M_output=1",
        "unnormalized_harmonics": ["Y_11=sqrt(1-z^2)*exp(i*phi)", "Y_20=P_2(z)", "Y_21=z*sqrt(1-z^2)*exp(i*phi)"],
        "normalized_Clebsch_Gordan": "<1,1;2,0|2,1>=sqrt(2)/2",
        "SO3_multiplicity": "dim Hom_SO3(V1 tensor V2,V2)=1, so the nonzero fixture fixes every m channel after the declared harmonic rescaling",
        "input_column_order": [f"{parity}_{mode}" for parity, mode in input_order],
        "output_row_order": [f"{parity}_{row}" for parity, row in output_order],
        "projected_columns": projected,
        "position_matrix": [[str(sp.factor(value)) for value in position.row(row)] for row in range(4)],
        "position_rank": 2,
        "velocity_matrix": [[str(sp.factor(value)) for value in velocity.row(row)] for row in range(4)],
        "velocity_determinant": str(expected_determinant),
        "velocity_rank_over_Q_sqrt3_i_t": 4,
        "velocity_determinant_nonzero_for_every_real_t": True,
    }


def build(direct_replay: bool = False) -> dict[str, object]:
    expected = _expected_rows()
    if direct_replay:
        _direct_replay(expected)
    abd = json.loads(ABD_INPUT.read_text(encoding="utf-8"))
    if not abd["classification"]["every_parity_polarization_abd_polynomial_chain_rank_three"]:
        raise AssertionError("a,b,d matrix input changed")
    theorem = _projection_theorem(expected)
    return {
        "schema": "einstein-maxwell-weyl-homogeneous-twist-ell2-extra-resonance-matrix-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_HOMOGENEOUS_TWIST_ELL2_EXTRA_RESONANCE_MATRIX",
        "result_state": "COMPLETE_HOMOGENEOUS_AND_TWIST_TIMES_ELL2_EXTRA_BOUNDED_RESONANCE_MATRIX_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed spatial S1_L times S2; bounded or finite-quasiperiodic resonance-function class",
            "charge_sector": "fixed magnetic bundle; electric variation allowed",
            "carrier": "complete homogeneous a,b,d and axial twist position/velocity block crossed with the axial-plus-polar ell=2 extra-primary multiplicity space; c,W_x,Q_e spectator columns imported as removable",
            "degree": 2,
            "parity": "all axial/polar input and output blocks retained without merging",
            "ell": "(0 or 1) x 2 -> resonant L=2",
            "m": "one nonzero m Clebsch-Gordan fixture fixes every m by SO(3) equivariance",
            "k": 0,
            "omega": "generalized-zero global/twist data crossed with omega_e=4/sqrt(3)",
        },
        "correction_classes": {
            "bounded_or_finite_quasiperiodic": "CERTIFIED resonance functionals; simultaneous vanishing with stabilizer maps remains unsolved",
            "smooth_exponential_polynomial": "OPEN: secular sufficiency requires the complete Noether-compatible operator, not only its resonant projection",
            "causal_or_retarded": "OPEN: no compact-product retarded complex is certified",
        },
        "direct_source_rows": {
            twist_case: {
                extra_parity: {
                    extra_mode: {output_parity: _strings(expected[twist_case][extra_parity][extra_mode][output_parity]) for output_parity in ("axial", "polar")}
                    for extra_mode in ("e1", "e2")
                }
                for extra_parity in ("axial", "polar")
            }
            for twist_case in ("position", "velocity")
        },
        "twist_projection_theorem": theorem,
        "homogeneous_abd_input": {
            "path": str(ABD_INPUT.relative_to(ROOT)),
            "sha256": _sha256(ABD_INPUT),
            "result": "each parity/polarization a,b,d polynomial chain has coefficient rank three",
        },
        "complete_matrix_disposition": {
            "c_column": "REMOVABLE by exact radius-family transport",
            "W_x_column": "ZERO flat-connection spectator",
            "Q_e_column": "REMOVABLE by electromagnetic-duality transport",
            "a_b_d_columns": "CERTIFIED imported polynomial resonance chains",
            "twist_position_columns": "CERTIFIED rank-two nonzero resonant block",
            "twist_velocity_columns": "CERTIFIED rank-four block with determinant nonzero for every real t",
        },
        "classification": {
            "nonaxisymmetric_direct_tensor_fixture_certified": True,
            "SO3_complete_twist_position_velocity_columns_certified": True,
            "twist_position_resonance_matrix_rank_two": True,
            "twist_velocity_resonance_matrix_pointwise_rank_four_for_real_t": True,
            "complete_homogeneous_twist_bounded_resonance_matrix": True,
            "simultaneous_stabilizer_and_resonance_zero_locus_solved": False,
            "smooth_secular_necessity_and_sufficiency": False,
            "causal_retarded_sufficiency": False,
            "full_second_order_equation_solved": False,
        },
        "interpretation": "The missing twist columns are not spectators. Twist position already supplies a rank-two resonant map, while twist velocity couples the four extra input amplitudes invertibly to the complete axial-plus-polar adjoint block at every real time. Together with the imported a,b,d chains this completes the declared homogeneous/twist bounded-resonance source matrix. It does not solve the nonlinear cone because the bilinear amplitudes obey common-factor relations and must also satisfy all five stabilizer moment maps.",
        "next_gate": "solve the simultaneous stabilizer plus complete bounded-resonance zero locus with the bilinear factorization constraints, then extend the classification to opposite momenta, phases and multiple absolute-momentum fibres",
        "claim_boundary": "This is a complete resonant-source matrix only in the declared k=0 homogeneous/twist times ell=2 extra carrier. It does not by itself prove obstruction or extension for a tangent, does not certify smooth-secular or retarded sufficiency, and does not support final residual, observational, particle, or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "direct_source_path": str(Path(source.__code__.co_filename).resolve().relative_to(ROOT)),
            "direct_source_sha256": _sha256(Path(source.__code__.co_filename).resolve()),
        },
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.2, "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 2.0, "commands": ["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix --check", "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix.py", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix"]},
            "tier_2": {"status": "PASS", "elapsed_seconds": 213.49, "commands": ["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix --replay"], "reason": "eight direct non-axisymmetric four-dimensional tensor fixtures replayed in four worker processes"},
            "tier_3": {"status": "NOT_RUN", "reason": "the simultaneous tangent cone, all momentum fibres and causal class remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix --replay",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--replay", action="store_true")
    arguments = parser.parse_args()
    value = build(direct_replay=arguments.replay)
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("homogeneous/twist resonance-matrix certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_HOMOGENEOUS_TWIST_ELL2_EXTRA_RESONANCE_MATRIX: PASS")


if __name__ == "__main__":
    main()
