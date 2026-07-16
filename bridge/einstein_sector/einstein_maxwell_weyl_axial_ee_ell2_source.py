"""Direct mixed axial-polar EE source in the lowest axial ell=2 target block."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import (
    _curvature,
    _stress,
    _trunc,
)


ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_quadratic_channel_preflight.json"
AXIAL_EINSTEIN = ROOT / "bridge/certificates/einstein_maxwell_axial_master_complex.json"
POLAR_EINSTEIN = ROOT / "bridge/certificates/einstein_maxwell_polar_master_complex.json"
AXIAL_TARGET = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json"
TENSOR_HELPER = ROOT / "bridge/einstein_sector/einstein_maxwell_periodic_photon_second_order.py"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ee_ell2_source.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_ee_ell2_source.schema.json"


class AxialEEEll2SourceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialEEEll2SourceError(message)


def _canonical(expression: sp.Expr) -> sp.Expr:
    return sp.factor(sp.sqrtdenest(sp.trigsimp(sp.expand_trig(expression))))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _geometry(order: int = 2) -> dict[str, object]:
    epsilon = sp.symbols("epsilon")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    frequency = sp.symbols("omega", positive=True, real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    wave = sp.exp(-sp.I * frequency * time)
    harmonic = sp.legendre(2, sp.cos(theta))
    harmonic_prime = sp.diff(harmonic, theta)
    axial_one_form = -sine * harmonic_prime
    root = sp.sqrt(3)
    tr = lambda expression: _trunc(expression, epsilon, order)

    # Axial minus-branch Einstein representative, rescaled by omega:
    # (h_t,h_x,q_t,q_x)=(0,-2,0,2sqrt(3)).
    axial_h_space = -2
    axial_q_space = 2 * root

    # Polar minus-branch Einstein representative with U=1:
    # (A,B,C,K,U)=(2-2sqrt(3),0,2-2sqrt(3),2sqrt(3),1).
    polar_a = 2 - 2 * root
    polar_c = polar_a
    polar_k = 2 * root
    polar_u = 1

    metric = sp.diag(-1, 1, 1, sine**2)
    metric[0, 0] += epsilon * polar_a * wave * harmonic
    metric[1, 1] += epsilon * polar_c * wave * harmonic
    metric[2, 2] += epsilon * polar_k * wave * harmonic
    metric[3, 3] += epsilon * polar_k * wave * harmonic * sine**2
    metric[1, 3] = metric[3, 1] = epsilon * axial_h_space * wave * axial_one_form
    inverse = metric.inv().applyfunc(tr)
    connection = [
        [[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)
    ]
    for target in range(4):
        for first in range(4):
            for second in range(4):
                connection[target][first][second] = tr(
                    sum(
                        inverse[target, index]
                        * (
                            sp.diff(metric[index, second], coordinates[first])
                            + sp.diff(metric[index, first], coordinates[second])
                            - sp.diff(metric[first, second], coordinates[index])
                        )
                        for index in range(4)
                    )
                    / 2
                )

    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    # Axial q_x Y dx gives f_tx and f_xtheta.
    field[0, 1] = -sp.I * frequency * epsilon * axial_q_space * wave * harmonic
    field[1, 0] = -field[0, 1]
    field[1, 2] = -epsilon * axial_q_space * wave * harmonic_prime
    field[2, 1] = -field[1, 2]
    # Polar a_a=U X_a gives f_tphi and the sphere curl.
    field[0, 3] = -sp.I * frequency * epsilon * polar_u * wave * axial_one_form
    field[3, 0] = -field[0, 3]
    field[2, 3] += epsilon * polar_u * wave * sp.diff(axial_one_form, theta)
    field[3, 2] = -field[2, 3]
    return {
        "epsilon": epsilon,
        "frequency": frequency,
        "coordinates": coordinates,
        "metric": metric,
        "inverse": inverse,
        "connection": connection,
        "field": field,
        "harmonic": harmonic,
        "axial_one_form": axial_one_form,
    }


def _source() -> dict[str, sp.Expr]:
    order = 2
    geometry = _geometry(order)
    data = _curvature(geometry, order)
    epsilon = geometry["epsilon"]
    frequency = geometry["frequency"]
    coordinates = geometry["coordinates"]
    metric = geometry["metric"]
    inverse = geometry["inverse"]
    connection = geometry["connection"]
    field = geometry["field"]
    harmonic = geometry["harmonic"]
    axial_one_form = geometry["axial_one_form"]
    assert isinstance(epsilon, sp.Symbol)
    assert isinstance(frequency, sp.Symbol)
    assert isinstance(coordinates, tuple)
    assert isinstance(metric, sp.MatrixBase)
    assert isinstance(inverse, sp.MatrixBase)
    assert isinstance(connection, list)
    assert isinstance(field, sp.MatrixBase)
    assert isinstance(harmonic, sp.Expr)
    assert isinstance(axial_one_form, sp.Expr)
    riemann = data["riemann"]
    schouten = data["schouten"]
    assert isinstance(riemann, list)
    assert isinstance(schouten, sp.MatrixBase)
    tr = lambda expression: _trunc(expression, epsilon, order)

    derivative_schouten = [
        [[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)
    ]
    for derivative in range(4):
        for first in range(4):
            for second in range(4):
                derivative_schouten[derivative][first][second] = tr(
                    sp.diff(schouten[first, second], coordinates[derivative])
                    - sum(
                        connection[index][derivative][first] * schouten[index, second]
                        + connection[index][derivative][second] * schouten[first, index]
                        for index in range(4)
                    )
                )

    def second_schouten(outer: int, inner: int, first: int, second: int) -> sp.Expr:
        return tr(
            sp.diff(derivative_schouten[inner][first][second], coordinates[outer])
            - sum(
                connection[index][outer][inner] * derivative_schouten[index][first][second]
                + connection[index][outer][first] * derivative_schouten[inner][index][second]
                + connection[index][outer][second] * derivative_schouten[inner][first][index]
                for index in range(4)
            )
        )

    schouten_up = sp.zeros(4)
    for first in range(4):
        for second in range(4):
            schouten_up[first, second] = tr(
                sum(
                    inverse[first, left] * inverse[second, right] * schouten[left, right]
                    for left in range(4)
                    for right in range(4)
                )
            )

    def weyl(first: int, second: int, third: int, fourth: int) -> sp.Expr:
        lowered = tr(
            sum(metric[first, target] * riemann[target][second][third][fourth] for target in range(4))
        )
        return tr(
            lowered
            - (
                metric[first, third] * schouten[fourth, second]
                - metric[first, fourth] * schouten[third, second]
                - metric[second, third] * schouten[fourth, first]
                + metric[second, fourth] * schouten[third, first]
            )
        )

    stress = _stress(data, order)

    def metric_equation(first: int) -> sp.Expr:
        second = 3
        laplacian = sum(
            inverse[outer, inner] * second_schouten(outer, inner, first, second)
            for outer in range(4)
            for inner in range(4)
        )
        mixed = sum(
            inverse[outer, inner] * second_schouten(outer, first, second, inner)
            for outer in range(4)
            for inner in range(4)
        )
        curvature = sum(
            schouten_up[inner, outer] * weyl(first, inner, second, outer)
            for inner in range(4)
            for outer in range(4)
        )
        return tr(3 * tr(laplacian - mixed + curvature) - stress[first, second])

    metric_equations = {index: metric_equation(index) for index in (0, 1)}

    field_up = sp.zeros(4)
    for left in range(4):
        for right in range(4):
            field_up[left, right] = tr(
                sum(
                    inverse[left, a] * inverse[right, b] * field[a, b]
                    for a in range(4)
                    for b in range(4)
                )
            )
    volume = tr(sp.sqrt(-metric.det())).subs(sp.Abs(sp.sin(coordinates[2])), sp.sin(coordinates[2]))
    maxwell_equations = {
        right: tr(
            sum(sp.diff(volume * field_up[left, right], coordinates[left]) for left in range(4))
            / volume
        )
        for right in (0, 1)
    }

    time, _, theta, _ = coordinates
    frequency_squared = 6 - 2 * sp.sqrt(3)
    metric_second = {
        index: _canonical(
            sp.expand(equation)
            .coeff(epsilon, 2)
            .subs(time, 0)
            .subs(frequency**2, frequency_squared)
        )
        for index, equation in metric_equations.items()
    }
    maxwell_second = {
        index: _canonical(
            sp.expand(equation)
            .coeff(epsilon, 2)
            .subs(time, 0)
            .subs(frequency**2, frequency_squared)
        )
        for index, equation in maxwell_equations.items()
    }

    metric_norm = sp.integrate(axial_one_form**2 / sp.sin(theta), (theta, 0, sp.pi))
    scalar_norm = sp.integrate(harmonic**2 * sp.sin(theta), (theta, 0, sp.pi))
    _require(metric_norm == sp.Rational(12, 5), "axial ell=2 norm changed")
    _require(scalar_norm == sp.Rational(2, 5), "scalar ell=2 norm changed")
    metric_projection = {
        index: _canonical(
            sp.integrate(source * axial_one_form / sp.sin(theta), (theta, 0, sp.pi))
            / metric_norm
        )
        for index, source in metric_second.items()
    }
    maxwell_projection = {
        index: _canonical(
            sp.integrate(source * harmonic * sp.sin(theta), (theta, 0, sp.pi))
            / scalar_norm
        )
        for index, source in maxwell_second.items()
    }
    return {
        "metric_t_coordinate_source": metric_second[0],
        "metric_x_coordinate_source": metric_second[1],
        "maxwell_t_coordinate_source": maxwell_second[0],
        "maxwell_x_coordinate_source": maxwell_second[1],
        "metric_t_projection": metric_projection[0],
        "metric_x_projection": metric_projection[1],
        "maxwell_t_projection": maxwell_projection[0],
        "maxwell_x_projection": maxwell_projection[1],
        "density_weighted_S1": 6 * metric_projection[0],
        "density_weighted_S2": -6 * metric_projection[1],
        "density_weighted_S3": maxwell_projection[0],
        "density_weighted_S4": maxwell_projection[1],
    }


def _correction(source: dict[str, sp.Expr]) -> dict[str, Any]:
    root = sp.sqrt(3)
    target_block = sp.Matrix(
        [
            [342 - 144 * root, 0, 6, 0],
            [0, 2322 - 1320 * root, 0, -6],
            [6, 0, 6, 0],
            [0, -6, 0, 18 - 8 * root],
        ]
    )
    source_block = sp.Matrix(
        [source[f"density_weighted_S{index}"] for index in range(1, 5)]
    )
    correction = (target_block.inv() * source_block).applyfunc(
        lambda value: sp.factor(sp.radsimp(value))
    )
    remainder = (target_block * correction - source_block).applyfunc(sp.simplify)
    _require(remainder == sp.zeros(4, 1), "second-order correction did not solve the selected source block")
    return {
        "target_subblock_order": ["lambda*metric_t", "-lambda*metric_x", "maxwell_t", "maxwell_x"],
        "coefficient_subblock_order": ["H_t", "H_x", "Q_t", "Q_x"],
        "target_subblock": [[str(value) for value in target_block.row(row)] for row in range(4)],
        "source_subblock": [str(value) for value in source_block],
        "correction_subblock": [str(value) for value in correction],
        "equation": "L_WM(Phi^(2))=S_AP with S_AP=D^2E_WM[Phi_A^(1),Phi_P^(1)]",
        "operator_remainder": [str(value) for value in remainder],
        "explicit_selected_block_correction": True,
    }


def _linear_input_checks() -> dict[str, Any]:
    root = sp.sqrt(3)
    frequency_squared = 6 - 2 * root
    axial_matrix = sp.Matrix(
        [
            [6, 0, 2, 0],
            [0, -6 + frequency_squared, 0, -2],
            [6, 0, 6, 0],
            [0, -6, 0, -6 + frequency_squared],
        ]
    )
    axial = sp.Matrix([0, -2, 0, 2 * root])
    _require((axial_matrix * axial).applyfunc(sp.simplify) == sp.zeros(4, 1), "axial input left its Einstein shell")

    # Directly use the certified polar coefficient matrix at k=0.
    polar = sp.Matrix([2 - 2 * root, 0, 2 - 2 * root, 2 * root, 1])
    eigenvalue = 6
    omega = sp.symbols("omega", real=True)
    polar_matrix = sp.Matrix(
        [
            [0, 0, 3, 3, -6],
            [0, 3, 0, 0, 0],
            [3, 0, 0, -(6 - 2 * omega**2) / 2, 6],
            [0, 0, sp.I * omega / 2, sp.I * omega / 2, -sp.I * omega],
            [0, sp.I * omega / 2, 0, 0, 0],
            [sp.Rational(3, 2), 0, -(6 - 2 * omega**2) / 4, (omega**2 + 2) / 2, -6],
            [sp.Rational(1, 2), 0, -sp.Rational(1, 2), 0, 0],
            [sp.Rational(1, 2), 0, -sp.Rational(1, 2), 1, -6 + omega**2],
        ]
    )
    polar_image = (polar_matrix * polar).subs(omega**2, frequency_squared).applyfunc(sp.simplify)
    _require(polar_image == sp.zeros(8, 1), "polar input left its Einstein shell")
    return {
        "frequency_squared": str(frequency_squared),
        "axial_representative_Ht_Hx_Qt_Qx": [str(value) for value in axial],
        "polar_representative_A_B_C_K_U": [str(value) for value in polar],
        "axial_operator_remainder": ["0", "0", "0", "0"],
        "polar_operator_remainder": ["0"] * 8,
        "both_inputs_on_certified_minus_branch": True,
    }


def build_certificate() -> dict[str, Any]:
    inputs = [PREFLIGHT, AXIAL_EINSTEIN, POLAR_EINSTEIN, AXIAL_TARGET]
    records = [json.loads(path.read_text(encoding="utf-8")) for path in inputs]
    _require(
        [record["result_id"] for record in records]
        == [
            "EINSTEIN_MAXWELL_WEYL_AXIAL_QUADRATIC_CHANNEL_PREFLIGHT",
            "COMPACT_EM_AXIAL_MASTER_COMPLEX",
            "COMPACT_EM_POLAR_MASTER_COMPLEX",
            "EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR",
        ],
        "source input result changed",
    )
    source = _source()
    correction = _correction(source)
    return {
        "schema": "einstein-maxwell-weyl-axial-ee-ell2-source-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_EE_ELL2_SOURCE_AND_CORRECTION",
        "result_state": "MIXED_AXIAL_POLAR_EE_ELL2_SUM_FREQUENCY_SOURCE_NONZERO_AND_EXPLICITLY_REMOVABLE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_ONE_MIXED_EE_AXIAL_OUTPUT_BLOCK",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "tensor_helper_path": str(TENSOR_HELPER.relative_to(ROOT)),
            "tensor_helper_sha256": _sha256(TENSOR_HELPER),
            "inputs": {str(path.relative_to(ROOT)): _sha256(path) for path in inputs},
        },
        "domain": {
            "spacetime": "R_t x S1_L x S2 on the unit magnetic fixed-P_N product background",
            "input": "complex positive-frequency sum of the axisymmetric ell=2,k=0 axial and polar Einstein-Maxwell minus-branch representatives",
            "output": "the axial ell=2,m=0,k=0 sum-frequency projection of the quadratic Weyl-Maxwell source",
            "frequency": "omega=sqrt(6-2sqrt(3)); output frequency 2omega",
            "quotient": "after local Diff x U(1) reduction and before final residual quotient",
        },
        "linear_inputs": _linear_input_checks(),
        "quadratic_source": {
            "definition": "S_AP=D^2E_WM[Phi_A^(1),Phi_P^(1)], equal to the axial-polar component of (1/2)D^2E_WM[Phi_A^(1)+Phi_P^(1),Phi_A^(1)+Phi_P^(1)]",
            "direct_method": "second coordinate expansion of 3B_ab-T_ab and div(F)^b with the explicit P_2(cos theta) fields; project tphi and xphi against X_phi and Maxwell t and x against P_2",
            "metric_t_coordinate_source": str(source["metric_t_coordinate_source"]),
            "metric_x_coordinate_source": str(source["metric_x_coordinate_source"]),
            "maxwell_t_coordinate_source": str(source["maxwell_t_coordinate_source"]),
            "maxwell_x_coordinate_source": str(source["maxwell_x_coordinate_source"]),
            "metric_t_projection": str(source["metric_t_projection"]),
            "metric_x_projection": str(source["metric_x_projection"]),
            "maxwell_t_projection": str(source["maxwell_t_projection"]),
            "maxwell_x_projection": str(source["maxwell_x_projection"]),
            "density_weighted_source_Ht_Hx_Qt_Qx_rows": [
                str(source[f"density_weighted_S{index}"])
                for index in range(1, 5)
            ],
            "source_nonzero": any(source[f"density_weighted_S{index}"] != 0 for index in range(1, 5)),
            "parity_statement": "axial-by-polar is odd and can project to the axial target; the displayed ell=2 projection is one component of the full quadratic source",
        },
        "second_order_correction": correction,
        "classification": {
            "actual_mixed_quadratic_source_tensor_projection_computed": True,
            "gauge_fixed_four_independent_row_block_complete": True,
            "dependent_angular_rows_directly_replayed": False,
            "selected_axial_sum_frequency_block_nonzero": True,
            "selected_axial_sum_frequency_block_removable": True,
            "metric_t_and_maxwell_t_rows_computed": True,
            "complete_second_order_correction_for_combined_tangent": False,
            "even_AA_and_PP_output_blocks_computed": False,
            "conjugate_and_difference_frequency_blocks_computed": False,
            "general_nonlinear_Einstein_sector_closed": False,
            "Lorentzian_causal_claim": False,
        },
        "interpretation": "The first parity-correct Einstein-to-axial-extra channel genuinely has a nonzero quadratic Weyl-Maxwell source, but it is off both target normal shells and the exact Hessian inverse removes the complete four-independent-row gauge-fixed axial ell=2 sum-frequency block. Thus this block is an explicit removable defect, not an obstruction and not evidence that an extra homogeneous graviton was produced.",
        "next_gate": "compute the even axial-axial and polar-polar outputs and conjugate/difference-frequency blocks for the same real tangent; only their combined correction or a target-adjoint pairing can decide full second-order extension",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem solves the four independent gauge-fixed rows of one axial ell=2 sum-frequency output block. The dependent angular rows are controlled by the imported Noether identities but are not directly replayed here. It does not give the even outputs, the complete Phi^(2) for a real tangent, all harmonic outputs, general nonlinear closure, final residual descent, causal evolution, scattering, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_ee_ell2_source --verify bridge/certificates/einstein_maxwell_weyl_axial_ee_ell2_source.json",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_ee_ell2_source --verify-exhaustive bridge/certificates/einstein_maxwell_weyl_axial_ee_ell2_source.json",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_ee_ell2_source",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload["result_id"] == "EINSTEIN_MAXWELL_WEYL_AXIAL_EE_ELL2_SOURCE_AND_CORRECTION", "result id changed")
    _require(payload["schema_sha256"] == _sha256(SCHEMA_PATH), "schema hash changed")
    provenance = payload["provenance"]
    _require(provenance["generator_sha256"] == _sha256(Path(__file__)), "generator hash changed")
    _require(provenance["tensor_helper_sha256"] == _sha256(TENSOR_HELPER), "tensor helper hash changed")
    for relative, digest in provenance["inputs"].items():
        _require(_sha256(ROOT / relative) == digest, f"input hash changed: {relative}")
    source_values = payload["quadratic_source"]["density_weighted_source_Ht_Hx_Qt_Qx_rows"]
    local = {"sqrt": sp.sqrt}
    source = {
        f"density_weighted_S{index + 1}": sp.sympify(value, locals=local)
        for index, value in enumerate(source_values)
    }
    replay = _correction(source)
    stored = payload["second_order_correction"]
    _require(stored["target_subblock"] == replay["target_subblock"], "stored target block changed")
    _require(stored["correction_subblock"] == replay["correction_subblock"], "stored correction changed")
    _require(stored["operator_remainder"] == replay["operator_remainder"], "stored correction remainder changed")
    for stored_value, replay_value in zip(stored["source_subblock"], replay["source_subblock"]):
        _require(sp.simplify(sp.sympify(stored_value) - sp.sympify(replay_value)) == 0, "stored source replay changed")


def verify_exhaustive_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"stale exhaustive EE source certificate: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--verify-exhaustive", type=Path)
    args = parser.parse_args()
    if args.print:
        print(json.dumps({key: str(value) for key, value in _source().items()}, indent=2, sort_keys=True))
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if args.verify_exhaustive:
        verify_exhaustive_certificate(args.verify_exhaustive)
    if not any((args.print, args.write, args.verify, args.verify_exhaustive)):
        parser.error("one of --print, --write, --verify, or --verify-exhaustive is required")


if __name__ == "__main__":
    main()
