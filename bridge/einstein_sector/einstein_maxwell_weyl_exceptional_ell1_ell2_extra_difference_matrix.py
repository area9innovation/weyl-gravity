"""Certify the complete exceptional-ell1/ell2-extra L=1 difference matrix."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_ell2_extra_difference_source_explore import source


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_ell2_extra_difference_matrix.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ell1_ell2_extra_difference_matrix.schema.json"
INPUTS = {
    "ad_pivots": ROOT / "bridge/certificates/einstein_maxwell_weyl_ad_exceptional_ell1_resonance_pivots.json",
    "exceptional_self": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_all_m_resonance.json",
    "difference_census": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_difference_frequency_nonresonance.json",
    "d_control": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_ell2_extra_resonance_completion.json",
}


class ExceptionalDifferenceMatrixError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ExceptionalDifferenceMatrixError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _compute(case: tuple[str, str, str]) -> tuple[tuple[str, str, str], sp.Matrix]:
    return case, source(*case)


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["ad_pivots"]["classification"]["exceptional_times_ell2_extra_difference_collision_open"], "a/d pivot gate changed")
    _require(records["exceptional_self"]["classification"]["complete_all_m_exceptional_ell1_two_polarization_cone_second_order_obstructed"], "exceptional self tensor changed")
    _require(records["difference_census"]["classification"]["no_k0_difference_frequency_collision"], "frequency census changed")
    _require(records["d_control"]["classification"]["d_cross_adjoint_map_invertible_in_both_parities"], "d control input changed")

    cases = [(exceptional, extra, mode) for exceptional in ("axial", "polar") for extra in ("axial", "polar") for mode in ("e1", "e2")]
    with ProcessPoolExecutor(max_workers=4) as executor:
        computed = list(executor.map(_compute, cases))
    sources = {case: value.applyfunc(sp.factor) for case, value in computed}
    expected = {
        ("axial", "axial", "e1"): [0, 0, 0, 0],
        ("axial", "axial", "e2"): [-sp.Rational(476, 15), 0, sp.Rational(116, 45), -16],
        ("axial", "polar", "e1"): [-sp.Rational(4, 5), 0, -sp.Rational(4, 5), 0],
        ("axial", "polar", "e2"): [0, sp.Rational(2016, 5), 0, -sp.Rational(96, 5)],
        ("polar", "axial", "e1"): [0, 0, 0, 0],
        ("polar", "axial", "e2"): [-sp.Rational(32, 5), 0, -sp.Rational(32, 5), 0],
        ("polar", "polar", "e1"): [2, 0, -sp.Rational(22, 15), -sp.Rational(8, 5)],
        ("polar", "polar", "e2"): [0, -sp.Rational(864, 5), 0, 0],
    }
    for case, values in expected.items():
        _require(sources[case] == sp.Matrix(values), f"direct difference source changed for {case}")

    witnesses = {
        "axial": sp.Matrix([0, -sp.Rational(1, 3), 0, 1]),
        "polar": sp.Matrix([0, 1, 0, 0]),
    }
    projections: dict[tuple[str, str, str], sp.Expr] = {}
    for case, value in sources.items():
        output_parity = "polar" if case[0] == case[1] else "axial"
        projections[case] = sp.factor((witnesses[output_parity].T * value)[0])
    nonzero = {case: value for case, value in projections.items() if value != 0}
    _require(nonzero == {
        ("axial", "polar", "e2"): -sp.Rational(768, 5),
        ("polar", "polar", "e2"): -sp.Rational(864, 5),
    }, "sparse difference matrix changed")

    return {
        "schema": "einstein-maxwell-weyl-exceptional-ell1-ell2-extra-difference-matrix-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELL1_ELL2_EXTRA_DIFFERENCE_MATRIX",
        "result_state": "COMPLETE_EXCEPTIONAL_ELL1_TIMES_ELL2_EXTRA_L1_DIFFERENCE_MATRIX_CERTIFIED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded/finite-quasiperiodic compatibility",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "one conjugate exceptional ell=1 extra dipole crossed with one positive-frequency ell=2 extra primary",
            "degree": 2,
            "parity": "all four exceptional/extra parity pairs and both ell2 extra multiplicities",
            "ell": "1 x 2 -> L=1 projection",
            "m": "axisymmetric direct tensor fixtures; SO3 covariant extension remains a separate tensor assembly",
            "k": 0,
            "omega": "2*omega_exceptional-omega_exceptional=omega_exceptional with omega_exceptional^2=4/3",
        },
        "input_order": [
            "exceptional_axial x extra_axial_e1",
            "exceptional_axial x extra_axial_e2",
            "exceptional_axial x extra_polar_e1",
            "exceptional_axial x extra_polar_e2",
            "exceptional_polar x extra_axial_e1",
            "exceptional_polar x extra_axial_e2",
            "exceptional_polar x extra_polar_e1",
            "exceptional_polar x extra_polar_e2"
        ],
        "direct_source_rows": {
            "/".join(case): [str(value) for value in sources[case]] for case in cases
        },
        "adjoint_projections": {
            "/".join(case): str(projections[case]) for case in cases
        },
        "sparse_matrix": {
            "axial_output": "R_ax=-(768/5)*conj(x_exceptional_axial)*y_extra_polar_e2",
            "polar_output": "R_pol=-(864/5)*conj(x_exceptional_polar)*y_extra_polar_e2",
            "all_other_axisymmetric_columns": "0",
            "rank_per_output_parity": 1,
            "unique_control_amplitude": "ell2 polar e2"
        },
        "joint_d_equations": {
            "axial_L1": "(8*sqrt(3)*I/9)*d*x_exceptional_axial-(768/5)*conj(x_exceptional_axial)*y_extra_polar_e2=0",
            "polar_L1": "-sqrt(3)*I*d*x_exceptional_polar-(864/5)*conj(x_exceptional_polar)*y_extra_polar_e2=0",
            "interpretation": "for a nonzero exceptional component the d relation fixes the unique polar-e2 control amplitude up to the exceptional phase; simultaneous axial and polar occupation imposes an additional relative-phase compatibility"
        },
        "classification": {
            "all_eight_axisymmetric_difference_columns_direct_four_dimensional": True,
            "six_adjoint_columns_zero": True,
            "two_adjoint_columns_nonzero": True,
            "unique_ell2_polar_e2_control_amplitude": True,
            "joint_d_L1_compatibility_equations_explicit": True,
            "SO3_all_m_tensor_assembled": False,
            "exceptional_L2_self_and_d_control_solved_jointly": False,
            "complete_exceptional_mixed_bounded_zero_locus_solved": False,
            "causal_or_quantum_claim": False
        },
        "interpretation": "The only axisymmetric oscillator-pair source capable of screening the exceptional d pivot uses the second polar ell=2 extra representative. The complete eight-column calculation reduces the next bounded-cone gate to one complex control amplitude and two displayed L1 equations, but the L2 exceptional self-defect, moment maps and all-m tensor must still be imposed.",
        "next_gate": "assemble the SO3 tensor and solve the displayed L1 equations jointly with the exceptional L2 self-defect, the d-times-polar-e2 L2 control column and the five stabilizer moment maps",
        "claim_boundary": "This is the complete axisymmetric L1 difference-frequency coefficient matrix. It does not yet prove an all-m cone, solve the L2 self channel, classify nonzero momentum, construct causal propagation, descend residual states, or make particle or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "direct_source_helper": {"path": str(Path(source.__code__.co_filename).resolve().relative_to(ROOT)), "sha256": _sha256(Path(source.__code__.co_filename).resolve())},
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()}
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_ell2_extra_difference_matrix --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_ell1_ell2_extra_difference_matrix.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_ell1_ell2_extra_difference_matrix"
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise ExceptionalDifferenceMatrixError("exceptional difference matrix certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELL1_ELL2_EXTRA_DIFFERENCE_MATRIX: PASS")


if __name__ == "__main__":
    main()
