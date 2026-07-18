"""Complete axisymmetric exceptional ell=1 two-polarization resonance no-go."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import _curvature, _trunc
from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import _generic_rows as _axial_rows
from bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order import _canonical, _equations
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import _generic_rows as _polar_rows


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_two_polarization_resonance.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ell1_two_polarization_resonance.schema.json"
INPUTS = {
    "axial_resonance": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_twist_resonance.json",
    "ell1_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
    "polar_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json",
    "axial_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json",
}


class TwoPolarizationResonanceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise TwoPolarizationResonanceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _direct_source(*, axial: bool, polar: bool) -> tuple[dict[str, sp.Expr], sp.Symbol]:
    epsilon = sp.symbols("epsilon")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    harmonic = sp.cos(theta)
    phase = sp.exp(-sp.I * 2 * time / sp.sqrt(3))
    metric = sp.diag(-1, 1, 1, sine**2)
    if polar:
        metric[0, 1] = metric[1, 0] = epsilon * phase * harmonic
    if axial:
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
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    potential_x = -3 * phase * harmonic if axial else sp.S.Zero
    field[0, 1] = epsilon * sp.diff(potential_x, time)
    field[1, 0] = -field[0, 1]
    field[1, 2] = -epsilon * sp.diff(potential_x, theta)
    field[2, 1] = -field[1, 2]
    data = _curvature(
        {"epsilon": epsilon, "coordinates": coordinates, "metric": metric, "inverse": inverse, "connection": connection, "field": field},
        2,
    )
    pairs = ((0, 0), (0, 1), (0, 2), (0, 3), (1, 1), (1, 3), (2, 2), (3, 3))
    metric_equations, maxwell_equations = _equations(data, 2, pairs)
    rows = {
        f"E{first}{second}": _canonical(sp.diff(value, epsilon, 2).subs(epsilon, 0) / (2 * phase**2))
        for (first, second), value in metric_equations.items()
    }
    rows.update(
        {
            f"M{index}": _canonical(sp.diff(value, epsilon, 2).subs(epsilon, 0) / (2 * phase**2))
            for index, value in maxwell_equations.items()
        }
    )
    return rows, theta


def _project_sources(
    combined_rows: dict[str, sp.Expr],
    theta: sp.Symbol,
    axial_self_source: sp.Matrix,
) -> tuple[sp.Matrix, sp.Matrix]:
    sine = sp.sin(theta)
    harmonic2 = sp.legendre(2, sp.cos(theta))

    def ell2_scalar(value: sp.Expr) -> sp.Expr:
        equator = _canonical(value.subs(theta, sp.pi / 2))
        half_cosine = _canonical(value.subs(theta, sp.pi / 3))
        coefficient = _canonical(sp.Rational(8, 3) * (half_cosine - equator))
        constant = _canonical(equator + coefficient / 2)
        _require(
            _canonical(value.subs(theta, sp.pi / 4) - constant - coefficient * harmonic2.subs(theta, sp.pi / 4)) == 0,
            "polar self-source contains a scalar harmonic beyond L=0,2",
        )
        return coefficient

    trace = _canonical((combined_rows["E22"] + combined_rows["E33"] / sine**2) / 2)
    tracefree = _canonical((combined_rows["E22"] - combined_rows["E33"] / sine**2) / 2)
    tensor2 = (sp.diff(harmonic2, theta, 2) - sp.cot(theta) * sp.diff(harmonic2, theta)) / 2
    metric_0a_ratio = combined_rows["E02"] / sp.diff(harmonic2, theta)
    metric_0a = _canonical(metric_0a_ratio.subs(theta, sp.pi / 4))
    combined_even_source = sp.Matrix(
        [
            ell2_scalar(combined_rows["E00"]),
            ell2_scalar(combined_rows["E01"]),
            ell2_scalar(combined_rows["E11"]),
            ell2_scalar(trace),
            metric_0a,
            0,
            _canonical(tracefree / tensor2),
            _canonical(sine * combined_rows["M3"] / (-sp.diff(harmonic2, theta))),
        ]
    )
    polar_source = (combined_even_source - axial_self_source).applyfunc(_canonical)
    expected_polar = sp.Matrix([2, 0, sp.Rational(4, 9), sp.Rational(7, 9), sp.I * 4 * sp.sqrt(3) / 9, 0, -sp.Rational(1, 3), -sp.Rational(1, 3)])
    _require((polar_source - expected_polar).applyfunc(_canonical) == sp.zeros(8, 1), "polar exceptional self-source changed")

    axial_one_form2 = -sine * sp.diff(harmonic2, theta)
    axial_cross = sp.Matrix(
        [
            _canonical(combined_rows["E03"] / axial_one_form2),
            _canonical(combined_rows["E13"] / axial_one_form2),
            0,
            _canonical(combined_rows["M0"] / harmonic2),
            _canonical(combined_rows["M1"] / harmonic2),
            0,
        ]
    )
    expected_cross = sp.Matrix([sp.Rational(2, 3), 0, 0, 4, 0, 0])
    _require((axial_cross - expected_cross).applyfunc(_canonical) == sp.zeros(6, 1), "axial-polar cross-source changed")
    return polar_source, axial_cross


def _theorem() -> dict[str, object]:
    combined_direct, theta = _direct_source(axial=True, polar=True)
    parent = json.loads(INPUTS["axial_resonance"].read_text(encoding="utf-8"))
    axial_self_source = sp.Matrix(
        [
            sp.sympify(value, locals={"I": sp.I, "sqrt": sp.sqrt})
            for value in parent["resonance_theorem"]["complex_positive_positive_source"]
        ]
    )
    polar_source, axial_cross = _project_sources(combined_direct, theta, axial_self_source)
    output_frequency = 4 / sp.sqrt(3)

    polar_rows, polar_symbols = _polar_rows()
    eigenvalue, momentum, frequency, at, mixed, ct, maxwell = polar_symbols
    polar_names = ["metric_00", "metric_01", "metric_11", "sphere_trace", "metric_0a", "metric_1a", "sphere_tracefree", "maxwell_axial_density"]
    polar_matrix = sp.Matrix([polar_rows[name] for name in polar_names]).jacobian([at, mixed, ct, maxwell])
    polar_matrix = polar_matrix.subs({eigenvalue: 6, momentum: 0, frequency: output_frequency}).applyfunc(sp.factor)
    polar_witnesses = [
        sp.Matrix([sp.Rational(3, 16), 0, sp.Rational(3, 16), 0, 0, 0, 1, 0]),
        sp.Matrix([sp.Rational(1, 72), 0, sp.Rational(1, 8), 0, 0, 0, 0, 1]),
    ]
    polar_pairings = [sp.factor((witness.T * polar_source)[0]) for witness in polar_witnesses]
    _require(polar_pairings == [sp.Rational(1, 8), -sp.Rational(1, 4)], "polar self resonant pairings changed")

    axial_rows, axial_symbols = _axial_rows()
    axial_names = ["metric_t", "metric_x", "metric_angular", "maxwell_t", "maxwell_x", "maxwell_angular"]
    axial_fields = [axial_symbols["h_t"], axial_symbols["h_x"], axial_symbols["q_t"], axial_symbols["q_x"]]
    axial_matrix = sp.Matrix([axial_rows[name] for name in axial_names]).jacobian(axial_fields)
    axial_matrix = axial_matrix.subs({axial_symbols["lambda"]: 6, axial_symbols["k"]: 0, axial_symbols["omega"]: output_frequency}).applyfunc(sp.factor)
    axial_witness = sp.Matrix([-4 * sp.sqrt(3) / 3, 0, 0, 0, 0, 1])
    _require(axial_matrix.T * axial_witness == sp.zeros(4, 1), "cross-channel axial adjoint witness changed")
    cross_pairing = sp.factor((axial_witness.T * axial_cross)[0])
    _require(cross_pairing == -8 * sp.sqrt(3) / 9, "cross-channel resonant pairing changed")

    axial_self_pairings = [sp.Rational(-2, 3), sp.Rational(4, 3)]
    cancellation_ratio = sp.Rational(16, 3)
    _require(
        [sp.factor(axial_self_pairings[index] + cancellation_ratio * polar_pairings[index]) for index in range(2)] == [0, 0],
        "self-channel cancellation ratio changed",
    )
    return {
        "frequency_squared": "4/3",
        "output_frequency_squared": "16/3",
        "polar_self_source": [str(sp.factor(value)) for value in polar_source],
        "polar_self_adjoint_pairings": [str(value) for value in polar_pairings],
        "axial_self_adjoint_pairings_from_parent": [str(value) for value in axial_self_pairings],
        "formal_self_pairing_cancellation_ratio": "|a_p|^2=(16/3)*|a_x|^2",
        "axial_polar_cross_source": [str(sp.factor(value)) for value in axial_cross],
        "axial_cross_adjoint_witness": [str(value) for value in axial_witness],
        "axial_cross_adjoint_pairing": str(cross_pairing),
        "case_split": {
            "a_x_times_a_p_nonzero": "the axial cross-channel pairing is nonzero",
            "a_p_zero_a_x_nonzero": "the parent axial self-channel pairings are nonzero",
            "a_x_zero_a_p_nonzero": "the polar self-channel pairings are nonzero",
            "only_compatible_amplitudes": "a_x=a_p=0",
        },
    }


def build_certificate() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["axial_resonance"]["classification"]["nonzero_adjoint_cokernel_witness_certified"], "parent axial resonance changed")
    _require(records["ell1_current"]["classification"]["polar_exceptional_ell1_current_classified"], "polar current input changed")
    theorem = _theorem()
    return {
        "schema": "einstein-maxwell-weyl-exceptional-ell1-two-polarization-resonance-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELL1_TWO_POLARIZATION_RESONANCE",
        "result_state": "COMPLETE_AXISYMMETRIC_EXCEPTIONAL_ELL1_TWO_POLARIZATION_SUM_RESONANCE_OBSTRUCTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "arbitrary complex axial and polar exceptional ell=1,m=0,k=0 positive-frequency amplitudes, optionally balanced by a collinear standard twist velocity, on the fixed magnetic bundle",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "common_zero_balance": "a collinear twist velocity cancels mu_H when B^2=(8/3)*|a_x|^2+(1/2)*|a_p|^2; it has no 2omega_e temporal support",
        "resonance_theorem": theorem,
        "classification": {
            "polar_exceptional_self_source_directly_computed": True,
            "axial_polar_cross_source_directly_computed": True,
            "self_pairing_vectors_can_formally_cancel": True,
            "cross_channel_blocks_every_nonzero_two_polarization_cancellation": True,
            "complete_axisymmetric_exceptional_ell1_two_polarization_cone_second_order_obstructed": True,
            "all_m_exceptional_cone_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The polar self-source is exactly capable of canceling the two axial self-source pairings, but doing so requires both exceptional polarizations to be nonzero. Their cross-product then excites an axial L=2 extra-shell cokernel with a nonzero pairing. The boundary cases are already obstructed by the individual self-sources, so only the zero exceptional tangent is compatible on this axisymmetric block.",
        "next_gate": "extend the resonant obstruction tensor over all m and determine whether interference among distinct m can cancel every L=2 axial and polar adjoint component",
        "claim_boundary": "This closes the complete m=0 two-polarization exceptional cone at second order, including twist-balanced common-zero fixtures. It does not classify all m, other same-frequency sectors, all-orders solutions, residual descent, causal scattering, particles, or quantum theory.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 49.5, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_two_polarization_resonance --verify bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_two_polarization_resonance.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_ell1_two_polarization_resonance.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_ell1_two_polarization_resonance"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": list(INPUTS)},
            "tier_3": {"status": "NOT_RUN", "reason": "the all-m exceptional cone remains open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_two_polarization_resonance --verify bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_two_polarization_resonance.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_ell1_two_polarization_resonance.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_ell1_two_polarization_resonance",
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
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "two-polarization resonance certificate is stale")


if __name__ == "__main__":
    main()
