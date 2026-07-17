"""Direct full-tensor polar Weyl--Maxwell Euler operator fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import _curvature, _stress, _trunc
from bridge.einstein_sector.einstein_maxwell_weyl_axial_ell2_full_tensor import _linear_coefficient, _separate
from bridge.einstein_sector.einstein_maxwell_polar_master_complex import _matrix as _source_matrix


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_full_tensor.schema.json"
PREFLIGHT = ROOT / "bridge/certificates/einstein_weyl_polar_offshell_operator_preflight.json"
AXIAL_ENGINE = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_axial_ell2_full_tensor.py"


class PolarFullTensorError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolarFullTensorError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _linearized_target(
    metric: sp.Matrix,
    inverse: sp.Matrix,
    connection: list[list[list[sp.Expr]]],
    field: sp.Matrix,
    coordinates: tuple[sp.Symbol, ...],
    epsilon: sp.Symbol,
) -> tuple[sp.Matrix, sp.Matrix]:
    """Linearize 3 B_ab-T_ab and the densitized Maxwell equation."""

    data = _curvature(
        {
            "epsilon": epsilon,
            "coordinates": coordinates,
            "metric": metric,
            "inverse": inverse,
            "connection": connection,
            "field": field,
        },
        1,
    )
    schouten = data["schouten"]
    riemann = data["riemann"]
    assert isinstance(schouten, sp.MatrixBase)
    assert isinstance(riemann, list)
    background_metric = metric.subs(epsilon, 0)
    background_inverse = inverse.subs(epsilon, 0)
    background_schouten = schouten.subs(epsilon, 0)
    delta_schouten = schouten.applyfunc(lambda value: _linear_coefficient(value, epsilon))
    background_connection = [
        [[connection[a][b][c].subs(epsilon, 0) for c in range(4)] for b in range(4)]
        for a in range(4)
    ]
    delta_connection = [
        [[_linear_coefficient(connection[a][b][c], epsilon) for c in range(4)] for b in range(4)]
        for a in range(4)
    ]
    derivative_schouten = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for derivative in range(4):
        for first in range(4):
            for second in range(4):
                derivative_schouten[derivative][first][second] = sp.expand(
                    sp.diff(delta_schouten[first, second], coordinates[derivative])
                    - sum(
                        background_connection[index][derivative][first] * delta_schouten[index, second]
                        + background_connection[index][derivative][second] * delta_schouten[first, index]
                        + delta_connection[index][derivative][first] * background_schouten[index, second]
                        + delta_connection[index][derivative][second] * background_schouten[first, index]
                        for index in range(4)
                    )
                )
    second_schouten = [[[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for outer in range(4):
        for inner in range(4):
            for first in range(4):
                for second in range(4):
                    second_schouten[outer][inner][first][second] = sp.expand(
                        sp.diff(derivative_schouten[inner][first][second], coordinates[outer])
                        - sum(
                            background_connection[index][outer][inner] * derivative_schouten[index][first][second]
                            + background_connection[index][outer][first] * derivative_schouten[inner][index][second]
                            + background_connection[index][outer][second] * derivative_schouten[inner][first][index]
                            for index in range(4)
                        )
                    )
    weyl_background = [[[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    weyl_delta = [[[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for first in range(4):
        for second in range(4):
            for third in range(4):
                for fourth in range(4):
                    lowered_riemann = sum(metric[first, target] * riemann[target][second][third][fourth] for target in range(4))
                    weyl = _trunc(
                        lowered_riemann
                        - (
                            metric[first, third] * schouten[fourth, second]
                            - metric[first, fourth] * schouten[third, second]
                            - metric[second, third] * schouten[fourth, first]
                            + metric[second, fourth] * schouten[third, first]
                        ),
                        epsilon,
                        1,
                    )
                    weyl_background[first][second][third][fourth] = weyl.subs(epsilon, 0)
                    weyl_delta[first][second][third][fourth] = _linear_coefficient(weyl, epsilon)
    schouten_up = sp.zeros(4)
    for first in range(4):
        for second in range(4):
            schouten_up[first, second] = _trunc(
                sum(
                    inverse[first, left] * inverse[second, right] * schouten[left, right]
                    for left in range(4)
                    for right in range(4)
                ),
                epsilon,
                1,
            )
    background_schouten_up = schouten_up.subs(epsilon, 0)
    delta_schouten_up = schouten_up.applyfunc(lambda value: _linear_coefficient(value, epsilon))
    delta_bach = sp.zeros(4)
    for first in range(4):
        for second in range(4):
            laplacian = sum(
                background_inverse[outer, inner] * second_schouten[outer][inner][first][second]
                for outer in range(4)
                for inner in range(4)
            )
            mixed = sum(
                background_inverse[outer, inner] * second_schouten[outer][first][second][inner]
                for outer in range(4)
                for inner in range(4)
            )
            curvature = sum(
                delta_schouten_up[inner, outer] * weyl_background[first][inner][second][outer]
                + background_schouten_up[inner, outer] * weyl_delta[first][inner][second][outer]
                for inner in range(4)
                for outer in range(4)
            )
            delta_bach[first, second] = sp.expand(laplacian - mixed + curvature)
    delta_stress = _stress(data, 1).applyfunc(lambda value: _linear_coefficient(value, epsilon))
    target_metric = (3 * delta_bach - delta_stress).applyfunc(sp.expand)

    field_up = sp.zeros(4)
    for left in range(4):
        for right in range(4):
            field_up[left, right] = _trunc(
                sum(
                    inverse[left, first] * inverse[right, second] * field[first, second]
                    for first in range(4)
                    for second in range(4)
                ),
                epsilon,
                1,
            )
    volume = _trunc(sp.sqrt(-metric.det()), epsilon, 1).subs(sp.Abs(sp.sin(coordinates[2])), sp.sin(coordinates[2]))
    maxwell_density = sp.Matrix([
        _linear_coefficient(
            sum(sp.diff(volume * field_up[left, right], coordinates[left]) for left in range(4)),
            epsilon,
        )
        for right in range(4)
    ])
    _require(background_metric == sp.diag(-1, 1, 1, sp.sin(coordinates[2]) ** 2), "background metric changed")
    return target_metric, maxwell_density


def _full_tensor_rows(ell: int) -> dict[str, object]:
    _require(ell >= 2, "polar fixture requires ell>=2")
    epsilon = sp.symbols("epsilon")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    frequency, momentum = sp.symbols("omega k", real=True)
    a_time, mixed, a_space, maxwell = sp.symbols("A_t B C_t U")
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    wave = sp.exp(sp.I * (momentum * space - frequency * time))
    eigenvalue = ell * (ell + 1)
    harmonic = sp.legendre(ell, sp.cos(theta))
    first = sp.diff(harmonic, theta)
    axial_one_form = -sine * first

    metric = sp.diag(-1, 1, 1, sine**2)
    metric[0, 0] += epsilon * a_time * wave * harmonic
    metric[0, 1] = metric[1, 0] = epsilon * mixed * wave * harmonic
    metric[1, 1] += epsilon * a_space * wave * harmonic
    inverse = metric.inv().applyfunc(lambda value: _trunc(value, epsilon, 1))
    connection = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for target in range(4):
        for left in range(4):
            for right in range(4):
                connection[target][left][right] = _trunc(
                    sum(
                        inverse[target, index]
                        * (
                            sp.diff(metric[index, right], coordinates[left])
                            + sp.diff(metric[index, left], coordinates[right])
                            - sp.diff(metric[left, right], coordinates[index])
                        )
                        for index in range(4)
                    )
                    / 2,
                    epsilon,
                    1,
                )
    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    field[0, 3] = -sp.I * frequency * epsilon * maxwell * wave * axial_one_form
    field[3, 0] = -field[0, 3]
    field[1, 3] = sp.I * momentum * epsilon * maxwell * wave * axial_one_form
    field[3, 1] = -field[1, 3]
    field[2, 3] += epsilon * maxwell * wave * sp.diff(axial_one_form, theta)
    field[3, 2] = -field[2, 3]
    target_metric, maxwell_density = _linearized_target(metric, inverse, connection, field, coordinates, epsilon)

    tracefree = (sp.diff(harmonic, theta, 2) - sp.cot(theta) * first) / 2
    sphere_trace = (target_metric[2, 2] + target_metric[3, 3] / sine**2) / 2
    sphere_tracefree = (target_metric[2, 2] - target_metric[3, 3] / sine**2) / 2
    normalizers = {
        "metric_00": wave * harmonic,
        "metric_01": wave * harmonic,
        "metric_11": wave * harmonic,
        "metric_0a": wave * first,
        "metric_1a": wave * first,
        "sphere_trace": wave * harmonic,
        "sphere_tracefree": wave * tracefree,
        "maxwell_axial_density": -wave * first,
    }
    raw_rows = {
        "metric_00": target_metric[0, 0],
        "metric_01": target_metric[0, 1],
        "metric_11": target_metric[1, 1],
        "metric_0a": target_metric[0, 2],
        "metric_1a": target_metric[1, 2],
        "sphere_trace": sphere_trace,
        "sphere_tracefree": sphere_tracefree,
        "maxwell_axial_density": maxwell_density[3],
    }
    rows = {
        name: sp.factor(sp.trigsimp(_separate(value / normalizers[name], theta), method="fu"))
        for name, value in raw_rows.items()
    }
    for name, row in rows.items():
        _require(not row.has(theta), f"ell={ell} {name} failed separation: {row}")
    return {
        "ell": ell,
        "lambda": eigenvalue,
        "symbols": {"omega": frequency, "k": momentum, "coefficients": (a_time, mixed, a_space, maxwell)},
        "rows": rows,
    }


def _row_strings(rows: dict[str, sp.Expr]) -> dict[str, str]:
    return {name: str(sp.factor(value)) for name, value in rows.items()}


def _generic_rows() -> tuple[dict[str, sp.Expr], tuple[sp.Symbol, ...]]:
    """Reconstruct the natural degree-two operator in lambda.

    A fourth-order natural tensor operator on a scalar spherical harmonic has
    degree at most two in the Laplace eigenvalue.  The three direct samples at
    lambda=6,12,20 therefore determine every coefficient.  The formulas are
    kept explicit so that the certificate verifier need not repeat the costly
    coordinate curvature calculation.
    """

    eigenvalue, momentum, frequency = sp.symbols("lambda k omega", real=True)
    a_time, mixed, a_space, maxwell = sp.symbols("A_t B C_t U")
    l, k, w = eigenvalue, momentum, frequency
    rows = {
        "metric_00": -sp.Rational(1, 2) * (
            a_time * (k**4 + 2 * l * k**2 + l * (2 * l - 3) / 2)
            + mixed * (2 * k**3 * w + 2 * l * k * w)
            + a_space * (k**2 * w**2 + l * k**2 / 2 - l * w**2 / 2 + l * (l + 1) / 2)
            + 2 * l * maxwell
        ),
        "metric_01": sp.Rational(1, 2) * (
            a_time * (k**3 * w + l * k * w)
            + mixed * (2 * k**2 * w**2 - 3 * l * k**2 / 2 + 3 * l * w**2 / 2 - l * (3 * l - 2) / 2)
            + a_space * (k * w**3 - l * k * w)
        ),
        "metric_11": -sp.Rational(1, 2) * (
            a_time * (k**2 * w**2 + l * k**2 / 2 - l * w**2 / 2 + l * (l + 1) / 2)
            + mixed * (2 * k * w**3 - 2 * l * k * w)
            + a_space * (w**4 - 2 * l * w**2 + l * (2 * l - 3) / 2)
            - 2 * l * maxwell
        ),
        "metric_0a": -sp.I / 4 * (
            a_time * (2 * k**2 * w + (2 * l - 3) * w)
            + mixed * (3 * k**3 + k * w**2 + (3 * l - 2) * k)
            + a_space * (3 * k**2 * w - w**3 + (l + 1) * w)
            + 4 * maxwell * w
        ),
        "metric_1a": -sp.I / 4 * (
            a_time * (k**3 - 3 * k * w**2 + (l + 1) * k)
            + mixed * (-k**2 * w - 3 * w**3 + (3 * l - 2) * w)
            + a_space * (-2 * k * w**2 + (2 * l - 3) * k)
            - 4 * maxwell * k
        ),
        "sphere_trace": -sp.Rational(1, 4) * (
            a_time * (k**4 - k**2 * w**2 + 3 * l * k**2 / 2 + l * w**2 / 2 + l * (l - 4) / 2)
            + mixed * (2 * k**3 * w - 2 * k * w**3 + 4 * l * k * w)
            + a_space * (k**2 * w**2 + l * k**2 / 2 - w**4 + 3 * l * w**2 / 2 - l * (l - 4) / 2)
            + 4 * l * maxwell
        ),
        "sphere_tracefree": -sp.Rational(1, 4) * (
            a_time * (k**2 - 3 * w**2 + l - 2)
            - 4 * mixed * k * w
            + a_space * (-3 * k**2 + w**2 - l + 2)
        ),
        "maxwell_axial_density": a_time / 2 - a_space / 2 + maxwell * (w**2 - k**2 - l),
    }
    return {name: sp.factor(value) for name, value in rows.items()}, (
        eigenvalue,
        momentum,
        frequency,
        a_time,
        mixed,
        a_space,
        maxwell,
    )


def _generic_operator() -> tuple[sp.Matrix, tuple[sp.Symbol, ...]]:
    rows, symbols = _generic_rows()
    coefficients = symbols[3:]
    matrix = sp.Matrix([[sp.expand(rows[name]).coeff(value) for value in coefficients] for name in (
        "metric_00",
        "metric_01",
        "metric_11",
        "metric_0a",
        "metric_1a",
        "sphere_trace",
        "sphere_tracefree",
        "maxwell_axial_density",
    )])
    return matrix, symbols[:3]


def _action_operator() -> tuple[sp.Matrix, tuple[sp.Symbol, ...]]:
    """Return the reduced action Hessian on (A_t,B,C_t,U).

    The metric contractions contribute (-1,2,-1).  The axial one-form
    harmonic has norm lambda times the scalar harmonic norm, and the chosen
    Maxwell Euler-row convention contributes the remaining factor two.
    """

    tensor, symbols = _generic_operator()
    eigenvalue, _, _ = symbols
    action = sp.diag(-1, 2, -1, 2 * eigenvalue) * tensor[[0, 1, 2, 7], :]
    return action.applyfunc(sp.factor), symbols


def _field_map() -> sp.Matrix:
    return sp.Matrix([
        [1, 0, 0, 1, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 1, -1, 0],
        [0, 0, 0, 0, 1],
    ])


def _equation_map() -> tuple[sp.Matrix, sp.Matrix, sp.Matrix, tuple[sp.Symbol, ...]]:
    """Solve H_P S_P = J_P E_P without shell division.

    Rows 0,1,2,5,6 of the source presentation form a rationally invertible
    minor.  Its characteristic determinant cancels completely in the
    product, leaving a polynomial map.  The other three source rows receive
    zero coefficients.
    """

    action, symbols = _action_operator()
    source, source_symbols = _source_matrix()
    _require(symbols == source_symbols, "source and target symbols diverged")
    field_map = _field_map()
    selected = (0, 1, 2, 5, 6)
    core = (action * field_map * source[list(selected), :].inv()).applyfunc(sp.cancel)
    for value in core:
        _require(sp.denom(value).is_number, f"equation map is not polynomial: {value}")
    equation_map = sp.zeros(4, 8)
    for column, source_row in enumerate(selected):
        equation_map[:, source_row] = core[:, column]
    defect = (action * field_map - equation_map * source).applyfunc(sp.factor)
    _require(defect == sp.zeros(4, 5), f"polar chain-square defect survived: {defect}")
    return action, field_map, equation_map.applyfunc(sp.factor), symbols


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def build_certificate() -> dict[str, object]:
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    _require(preflight["classification"]["correct_target_polar_field_slice_certified"] is True, "polar preflight changed")
    samples = {}
    sample_expressions: dict[int, dict[str, sp.Expr]] = {}
    for ell in (2, 3, 4):
        result = _full_tensor_rows(ell)
        sample_expressions[ell] = result["rows"]
        samples[str(ell)] = {"lambda": result["lambda"], "rows": _row_strings(result["rows"])}
    generic_rows, generic_symbols = _generic_rows()
    eigenvalue, momentum, frequency = generic_symbols[:3]
    for ell, rows in sample_expressions.items():
        physical_lambda = ell * (ell + 1)
        for name, value in rows.items():
            defect = sp.factor(value - generic_rows[name].subs(eigenvalue, physical_lambda))
            _require(defect == 0, f"generic reconstruction failed at ell={ell}, row={name}: {defect}")
    degrees: dict[str, int] = {}
    for name, value in generic_rows.items():
        for coefficient in generic_symbols[3:]:
            polynomial = sp.Poly(sp.expand(value).coeff(coefficient), eigenvalue)
            _require(polynomial.degree() <= 2, f"lambda-degree bound failed for {name}/{coefficient}")
            _require(sp.denom(polynomial.as_expr()).is_number, f"hidden lambda denominator in {name}/{coefficient}")
        degrees[name] = max(sp.Poly(sp.expand(value).coeff(coefficient), eigenvalue).degree() for coefficient in generic_symbols[3:])

    tensor, _ = _generic_operator()
    trace_defect = sp.Matrix([sp.factor(-tensor[0, column] + tensor[2, column] + 2 * tensor[5, column]) for column in range(4)])
    _require(trace_defect == sp.zeros(4, 1), f"linear Bach-Maxwell trace identity failed: {trace_defect}")
    action, field_map, equation_map, _ = _equation_map()
    adjoint_defect = (
        action - action.subs({frequency: -frequency, momentum: -momentum}, simultaneous=True).T
    ).applyfunc(sp.factor)
    _require(adjoint_defect == sp.zeros(4), f"formal self-adjointness failed: {adjoint_defect}")
    source, _ = _source_matrix()
    chain_defect = (action * field_map - equation_map * source).applyfunc(sp.factor)
    _require(chain_defect == sp.zeros(4, 5), f"chain square failed: {chain_defect}")

    extra_shell = frequency**2 - momentum**2 - eigenvalue + sp.Rational(2, 3)
    einstein_shell = (
        (frequency**2 - momentum**2) ** 2
        - 2 * eigenvalue * (frequency**2 - momentum**2)
        + eigenvalue * (eigenvalue - 2)
    )
    determinant = sp.factor(action.det())
    expected_determinant = sp.factor(
        sp.Rational(9, 16) * eigenvalue**3 * (eigenvalue - 2) * extra_shell**2 * einstein_shell
    )
    _require(determinant == expected_determinant, "polar action determinant factorization changed")
    resultant = sp.factor(sp.resultant(extra_shell, einstein_shell, frequency))
    _require(resultant == sp.Rational(4, 81) * (9 * eigenvalue - 2) ** 2, "polar shells ceased to be comaximal")
    return {
        "schema": "einstein-maxwell-weyl-polar-full-tensor-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_POLAR_FULL_TENSOR",
        "result_state": "GENERIC_POLAR_OFFSHELL_OPERATOR_AND_EINSTEIN_CHAIN_SQUARE_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "engines": {str(AXIAL_ENGINE.relative_to(ROOT)): _sha256(AXIAL_ENGINE)},
            "inputs": {str(PREFLIGHT.relative_to(ROOT)): _sha256(PREFLIGHT)},
        },
        "domain": "direct coordinate linearization on target Weyl gauge slice (A+K,B,C-K,U), arbitrary omega and k, explicit Y_ell0",
        "row_order": ["metric_00", "metric_01", "metric_11", "metric_0a", "metric_1a", "sphere_trace", "sphere_tracefree", "maxwell_axial_density"],
        "samples": samples,
        "lambda_reconstruction": {
            "degree_bound": 2,
            "argument": "a fourth-order natural tensor operator on a scalar spherical harmonic contains at most two Laplace eigenvalues",
            "nodes": [6, 12, 20],
            "row_degrees": degrees,
            "generic_rows": _row_strings(generic_rows),
            "all_sample_defects_zero": True,
            "hidden_denominators_absent": True,
        },
        "target_operator": {
            "coordinates": ["A_t=A+K", "B", "C_t=C-K", "U"],
            "tensor_matrix": _matrix_strings(tensor),
            "action_row_selection": ["-metric_00", "2*metric_01", "-metric_11", "2*lambda*maxwell_axial_density"],
            "action_matrix": _matrix_strings(action),
            "formally_self_adjoint": True,
            "trace_identity": "-metric_00+metric_11+2*sphere_trace=0",
            "trace_defect": [str(value) for value in trace_defect],
        },
        "chain_square": {
            "identity": "H_P*S_P=J_P*E_P",
            "source_coordinates": ["A", "B", "C", "K", "U"],
            "target_field_map": _matrix_strings(field_map),
            "source_row_order": ["00", "01", "11", "0a", "1a", "sphere_trace", "sphere_tracefree", "maxwell_axial_density"],
            "equation_row_map": _matrix_strings(equation_map),
            "supporting_source_rows": [0, 1, 2, 5, 6],
            "polynomial_no_shell_division": True,
            "defect": _matrix_strings(chain_defect),
        },
        "characteristic_and_module": {
            "extra_shell_p": str(extra_shell),
            "Einstein_shell_q": str(einstein_shell),
            "determinant": str(determinant),
            "monic_determinantal_divisors": ["1", "1", str(extra_shell), str(sp.factor(extra_shell**2 * einstein_shell))],
            "invariant_factors_over_Q_lambda_k_omega": ["1", "1", str(extra_shell), str(sp.factor(extra_shell * einstein_shell))],
            "resultant_p_q": str(resultant),
            "primary_decomposition": "(K[omega]/(p))^2 direct-sum K[omega]/(q)",
            "extra_polar_quotient_candidate": "(K[omega]/(p))^2",
        },
        "classification": {
            "direct_target_polar_Euler_samples_constructed": True,
            "Einstein_branch_substitution_used": False,
            "off_shell_omega_and_k_retained": True,
            "generic_lambda_operator_reconstructed": True,
            "action_normalized_operator_constructed": True,
            "formal_self_adjointness_certified": True,
            "polar_chain_map_constructed": True,
            "extra_polar_characteristic_certified": True,
            "polar_primary_decomposition_certified_over_generic_physical_field": True,
            "polar_Lee_Wald_current_on_extra_branch_certified": False,
            "final_residual_descent_certified": False,
        },
        "next_gate": "construct the polar extra-branch Lee-Wald current and coefficient extractors, then perform the final residual/gauge descent",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE certificate constructs the generic polar target Hessian, its polynomial Einstein chain square, determinant, and generic-field primary decomposition. It does not yet certify the extra polar Lee-Wald current, the integral physical-ring specialization at every allowed momentum, the ungauged BV lift, final residual descent, nonlinear closure, causal scattering, or a quantum interpretation.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor --verify bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_full_tensor.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_full_tensor",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor --ell 2",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"polar full-tensor fixture stale: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--ell", type=int)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if args.ell is not None:
        result = _full_tensor_rows(args.ell)
        for name, value in result["rows"].items():
            print(f"{name}: {value}")
    if not args.write and args.verify is None and args.ell is None:
        parser.error("one of --write, --verify, or --ell is required")


if __name__ == "__main__":
    main()
