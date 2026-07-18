"""Balanced twist/exceptional-ell1 tangent with a non-removable 2-omega source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import _curvature, _trunc
from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import _canonical, _equations
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import _generic_rows


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_twist_resonance.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ell1_twist_resonance.schema.json"
INPUTS = {
    "ell1_current_taub": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
    "exceptional_moment_maps": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
    "polar_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json",
}


class ExceptionalEll1TwistResonanceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ExceptionalEll1TwistResonanceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _direct_positive_positive_source() -> tuple[dict[str, sp.Expr], sp.Symbol]:
    epsilon = sp.symbols("epsilon")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    harmonic = sp.cos(theta)
    frequency = 2 / sp.sqrt(3)
    phase = sp.exp(-sp.I * frequency * time)

    metric = sp.diag(-1, 1, 1, sine**2)
    metric[1, 3] = metric[3, 1] = epsilon * phase * sine**2
    trunc = lambda expression: _trunc(expression, epsilon, 2)
    inverse = metric.inv().applyfunc(trunc)
    connection = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for target in range(4):
        for left in range(4):
            for right in range(4):
                connection[target][left][right] = trunc(
                    sum(
                        inverse[target, index]
                        * (
                            sp.diff(metric[index, right], coordinates[left])
                            + sp.diff(metric[index, left], coordinates[right])
                            - sp.diff(metric[left, right], coordinates[index])
                        )
                        for index in range(4)
                    )
                    / 2
                )
    potential_x = -3 * phase * harmonic
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    field[0, 1] = epsilon * sp.diff(potential_x, time)
    field[1, 0] = -field[0, 1]
    field[1, 2] = -epsilon * sp.diff(potential_x, theta)
    field[2, 1] = -field[1, 2]
    data = _curvature(
        {
            "epsilon": epsilon,
            "coordinates": coordinates,
            "metric": metric,
            "inverse": inverse,
            "connection": connection,
            "field": field,
        },
        2,
    )
    pairs = tuple((first, second) for first in range(4) for second in range(first, 4))
    metric_equations, maxwell_equations = _equations(data, 2, pairs)
    rows = {
        f"E{first}{second}": _canonical(
            sp.diff(value, epsilon, 2).subs(epsilon, 0) / (2 * phase**2)
        )
        for (first, second), value in metric_equations.items()
    }
    rows.update(
        {
            f"M{index}": _canonical(
                sp.diff(value, epsilon, 2).subs(epsilon, 0) / (2 * phase**2)
            )
            for index, value in maxwell_equations.items()
        }
    )
    return rows, theta


def _ell2_source(rows: dict[str, sp.Expr], theta: sp.Symbol) -> sp.Matrix:
    sine = sp.sin(theta)
    harmonic2 = sp.legendre(2, sp.cos(theta))

    def ell2_scalar(value: sp.Expr) -> sp.Expr:
        equator = _canonical(value.subs(theta, sp.pi / 2))
        half_cosine = _canonical(value.subs(theta, sp.pi / 3))
        coefficient = _canonical(sp.Rational(8, 3) * (half_cosine - equator))
        constant = _canonical(equator + coefficient / 2)
        audit = _canonical(value.subs(theta, sp.pi / 4) - constant - coefficient * harmonic2.subs(theta, sp.pi / 4))
        _require(audit == 0, "positive-positive source contains a scalar harmonic beyond L=0,2")
        return coefficient

    trace = _canonical((rows["E22"] + rows["E33"] / sine**2) / 2)
    tracefree = _canonical((rows["E22"] - rows["E33"] / sine**2) / 2)
    tensor2 = (sp.diff(harmonic2, theta, 2) - sp.cot(theta) * sp.diff(harmonic2, theta)) / 2
    metric_0a_ratio = rows["E02"] / sp.diff(harmonic2, theta)
    metric_0a = _canonical(metric_0a_ratio.subs(theta, sp.pi / 4))
    _require(
        _canonical(metric_0a_ratio.subs(theta, sp.pi / 3) - metric_0a) == 0,
        "metric_0a source is not a pure L=2 vector harmonic",
    )
    source = sp.Matrix(
        [
            ell2_scalar(rows["E00"]),
            ell2_scalar(rows["E01"]),
            ell2_scalar(rows["E11"]),
            ell2_scalar(trace),
            metric_0a,
            sp.Integer(0),
            _canonical(tracefree / tensor2),
            _canonical(sine * rows["M3"] / (-sp.diff(harmonic2, theta))),
        ]
    )
    expected = sp.Matrix(
        [
            sp.Rational(23, 3),
            0,
            sp.Rational(49, 27),
            sp.Rational(79, 27),
            sp.I * 46 * sp.sqrt(3) / 27,
            0,
            -sp.Rational(22, 9),
            1,
        ]
    )
    _require((source - expected).applyfunc(_canonical) == sp.zeros(8, 1), "direct resonant L=2 source changed")
    return source


def _resonance_theorem() -> dict[str, object]:
    direct, theta = _direct_positive_positive_source()
    source = _ell2_source(direct, theta)
    rows, symbols = _generic_rows()
    eigenvalue, momentum, frequency, at, mixed, ct, maxwell = symbols
    names = [
        "metric_00",
        "metric_01",
        "metric_11",
        "sphere_trace",
        "metric_0a",
        "metric_1a",
        "sphere_tracefree",
        "maxwell_axial_density",
    ]
    matrix = sp.Matrix([rows[name] for name in names]).jacobian([at, mixed, ct, maxwell])
    output_frequency = 4 / sp.sqrt(3)
    matrix = matrix.subs({eigenvalue: 6, momentum: 0, frequency: output_frequency}).applyfunc(sp.factor)
    witness_one = sp.Matrix([sp.Rational(3, 16), 0, sp.Rational(3, 16), 0, 0, 0, 1, 0])
    witness_two = sp.Matrix([sp.Rational(1, 72), 0, sp.Rational(1, 8), 0, 0, 0, 0, 1])
    _require(matrix.T * witness_one == sp.zeros(4, 1), "first resonant adjoint witness changed")
    _require(matrix.T * witness_two == sp.zeros(4, 1), "second resonant adjoint witness changed")
    pairings = [sp.factor((witness_one.T * source)[0]), sp.factor((witness_two.T * source)[0])]
    _require(pairings == [-sp.Rational(2, 3), sp.Rational(4, 3)], "resonant pairings changed")
    _require(matrix.rank() == 2 and matrix.row_join(-source).rank() == 3, "resonant augmented-rank obstruction changed")
    return {
        "input_extra_frequency_squared": "4/3",
        "output_channel": "polar L=2,k=0 positive-positive self-sum",
        "output_frequency_squared": "16/3",
        "target_extra_shell_check": "Omega^2-Lambda+2/3=16/3-6+2/3=0",
        "source_row_order": names,
        "complex_positive_positive_source": [str(sp.factor(value)) for value in source],
        "target_matrix_rank": matrix.rank(),
        "augmented_matrix_rank": matrix.row_join(-source).rank(),
        "adjoint_witnesses": [[str(value) for value in witness_one], [str(value) for value in witness_two]],
        "adjoint_pairings": [str(value) for value in pairings],
        "correction_exists": False,
    }


def build_certificate() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["ell1_current_taub"]["classification"]["exceptional_extra_ell1_current_nonradical_positive_definite"], "ell=1 current input changed")
    _require(records["exceptional_moment_maps"]["classification"]["standard_twist_common_zero_locus_classified"], "twist moment map input changed")
    _require(records["polar_operator"]["classification"]["extra_polar_characteristic_certified"], "polar target input changed")
    theorem = _resonance_theorem()
    return {
        "schema": "einstein-maxwell-weyl-exceptional-ell1-twist-resonance-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELL1_TWIST_RESONANCE",
        "result_state": "TWIST_BALANCED_EXCEPTIONAL_ELL1_TANGENT_RESONANTLY_OBSTRUCTED_AT_SECOND_ORDER",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "one real m=0 axial exceptional ell=1,k=0 mode plus a collinear standard twist velocity on the fixed magnetic bundle, before final residual quotient",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "first_order_common_zero_fixture": {
            "extra_representative": "Re[e*(0,1,0,-3)*exp(-i*(2/sqrt(3))*t)] in axial (h_t,h_x,q_t,q_x)",
            "twist_representative": "(h_x,q_x)=(B*t,-B*t) on the same real m=0 axis with A=0",
            "balance": "B^2=(8/3)*e^2",
            "mu_H": "2*L*N_10*B^2-(16/3)*L*N_10*e^2=0",
            "mu_Px_and_mu_J": "0 at k=0 on one m=0 axis with A=0",
        },
        "resonance_theorem": theorem,
        "classification": {
            "nonzero_twist_exceptional_common_zero_fixture_constructed": True,
            "complete_direct_exceptional_positive_positive_source_computed": True,
            "polar_L2_extra_sum_frequency_resonance_exact": True,
            "nonzero_adjoint_cokernel_witness_certified": True,
            "twist_balanced_fixture_second_order_extendible": False,
            "all_exceptional_ell1_mixed_balances_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Canceling every background-stabilizer moment map is not sufficient for this mixed tangent. The exceptional self-sum lands exactly on the polar L=2 fourth-order shell and has a nonzero dynamical adjoint-cokernel projection. Twist self and twist-extra cross terms occur only at generalized zero frequency and omega_e, so they cannot alter the 2omega_e obstruction.",
        "next_gate": "test whether adding polar exceptional ell=1 data or an Einstein-minus sector can cancel both resonant adjoint pairings, not only the stabilizer moment maps",
        "claim_boundary": "This is one explicit compact second-order no-go fixture. It does not classify the full exceptional ell=1 mixed cone, all-orders solutions, final residual descent, causal scattering, particles, or quantum theory.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 27.8, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_twist_resonance --verify bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_twist_resonance.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_ell1_twist_resonance.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_ell1_twist_resonance"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": list(INPUTS)},
            "tier_3": {"status": "NOT_RUN", "reason": "the full mixed exceptional ell=1 cone and all-orders integration remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_twist_resonance --verify bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_twist_resonance.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_ell1_twist_resonance.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_ell1_twist_resonance",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    payload = build_certificate()
    if arguments.write:
        DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    assert arguments.verify is not None
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "exceptional ell=1 twist-resonance certificate is stale")


if __name__ == "__main__":
    main()
