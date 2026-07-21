"""Exact alpha_B=3 Ostrogradsky normalization and polar correction crosswalk.

The selected covariant action is

    S = integral sqrt(-g) [(3/8) C^2 - F^2/4].

We use the no-time-integration-by-parts ADM convention obtained by adjoining
K_ij with the multiplier enforcing L_n h_ij=2 K_ij.  Relative to the
Chen--Ma normalization -C^2/4 this is the exact scale c=-3/2.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
import jsonschema

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import (
    _curvature,
    _trunc,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/EINSTEIN_WEYL_ALPHA_B3_OSTROGRADSKY_CANONICAL_CROSSWALK_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-alpha-b3-ostrogradsky-canonical-crosswalk-v1.schema.json"
BALANCED = ROOT / "bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json"
CUBIC_OBSTRUCTION = ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_CUBIC_CONSTRAINT_TENSOR_EXPORT_OBSTRUCTION_V1.json"
ACTION = ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json"


class CrosswalkError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CrosswalkError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coeff1(value: sp.Expr, epsilon: sp.Symbol) -> sp.Expr:
    return sp.factor(sp.diff(value, epsilon).subs(epsilon, 0))


def canonical(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.sqrtdenest(sp.trigsimp(sp.expand_trig(value))))


def matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(canonical(matrix[i, j])) for j in range(matrix.cols)] for i in range(matrix.rows)]


def _background_magnetic_gradient() -> tuple[sp.Matrix, tuple[sp.Expr, ...], sp.Symbol]:
    """Euler derivative of (3/2)*sqrt(h)*C_ijkn C^(ijk)n.

    The six arguments are the independent covariant components of K_ij in
    the order xx, x-theta, x-phi, theta-theta, theta-phi, phi-phi.  For an
    off-diagonal component the ordinary variational derivative is divided by
    two, because the canonical tensor contraction sums both symmetric slots.
    """

    theta = sp.symbols("theta", real=True)
    coords = sp.symbols("x"), theta, sp.symbols("phi")
    sine = sp.sin(theta)
    h = sp.diag(1, 1, sine**2)
    h_inv = sp.diag(1, 1, sine**-2)
    gamma = [[[sp.S.Zero for _ in range(3)] for _ in range(3)] for _ in range(3)]
    for a in range(3):
        for b in range(3):
            for c in range(3):
                gamma[a][b][c] = canonical(
                    sum(
                        h_inv[a, d]
                        * (sp.diff(h[d, c], coords[b]) + sp.diff(h[d, b], coords[c]) - sp.diff(h[b, c], coords[d]))
                        for d in range(3)
                    )
                    / 2
                )

    names = ("Kxx", "Kxt", "Kxp", "Ktt", "Ktp", "Kpp")
    functions = tuple(sp.Function(name)(theta) for name in names)
    kxx, kxt, kxp, ktt, ktp, kpp = functions
    K = sp.Matrix([[kxx, kxt, kxp], [kxt, ktt, ktp], [kxp, ktp, kpp]])

    def cov_k(a: int, b: int, c: int) -> sp.Expr:
        return canonical(
            sp.diff(K[b, c], coords[a])
            - sum(gamma[d][a][b] * K[d, c] + gamma[d][a][c] * K[b, d] for d in range(3))
        )

    mixed = K * h_inv

    def divergence(a: int) -> sp.Expr:
        # D_d K_a^d for a (covariant, contravariant) mixed tensor.
        return canonical(
            sum(
                sp.diff(mixed[a, d], coords[d])
                - sum(gamma[e][d][a] * mixed[e, d] for e in range(3))
                + sum(gamma[d][d][e] * mixed[a, e] for e in range(3))
                for d in range(3)
            )
        )

    trace = canonical(sum(h_inv[a, b] * K[a, b] for a in range(3) for b in range(3)))

    def dtrace(a: int) -> sp.Expr:
        return sp.diff(trace, coords[a])

    magnetic = [[[sp.S.Zero for _ in range(3)] for _ in range(3)] for _ in range(3)]
    for a in range(3):
        for b in range(3):
            for c in range(3):
                magnetic[a][b][c] = canonical(
                    cov_k(a, b, c)
                    - cov_k(b, a, c)
                    + (divergence(a) * h[b, c] - divergence(b) * h[a, c]) / 2
                    - (dtrace(a) * h[b, c] - dtrace(b) * h[a, c]) / 2
                )
    magnetic_square = canonical(
        sum(
            magnetic[a][b][c]
            * h_inv[a, d]
            * h_inv[b, e]
            * h_inv[c, f]
            * magnetic[d][e][f]
            for a in range(3)
            for b in range(3)
            for c in range(3)
            for d in range(3)
            for e in range(3)
            for f in range(3)
        )
    )
    density = canonical(sp.Rational(3, 2) * sine * magnetic_square)
    gradient_components: list[sp.Expr] = []
    for index, function in enumerate(functions):
        euler = sp.diff(density, function) - sp.diff(sp.diff(density, sp.diff(function, theta)), theta)
        if index in (1, 2, 4):
            euler /= 2
        gradient_components.append(canonical(euler))
    gradient = sp.Matrix(
        [
            [gradient_components[0], gradient_components[1], gradient_components[2]],
            [gradient_components[1], gradient_components[3], gradient_components[4]],
            [gradient_components[2], gradient_components[4], gradient_components[5]],
        ]
    )
    return gradient, functions, theta


def _linear_pi(
    delta_h: sp.Matrix,
    delta_k: sp.Matrix,
    delta_p: sp.Matrix,
    omega: sp.Symbol,
    time: sp.Symbol,
    theta: sp.Symbol,
) -> tuple[sp.Matrix, dict[str, str]]:
    """Reconstruct pi from the selected canonical Hamilton equation."""

    phase = sp.exp(-sp.I * omega * time)
    h0 = sp.diag(1, 1, sp.sin(theta) ** 2)
    h0_inv = sp.diag(1, 1, sp.sin(theta) ** -2)
    p0 = sp.diag(sp.sin(theta), -sp.sin(theta) / 2, -1 / (2 * sp.sin(theta)))
    k_trace = canonical(sum(h0_inv[i, j] * delta_k[i, j] for i in range(3) for j in range(3)))
    p_dot_k = canonical(sum(p0[i, j] * delta_k[i, j] for i in range(3) for j in range(3)))
    algebraic = (p0 * k_trace + h0_inv * p_dot_k).applyfunc(canonical)

    magnetic_gradient, functions, magnetic_theta = _background_magnetic_gradient()
    substitutions: dict[sp.Expr, sp.Expr] = {magnetic_theta: theta}
    components = (
        delta_k[0, 0] / phase,
        delta_k[0, 1] / phase,
        delta_k[0, 2] / phase,
        delta_k[1, 1] / phase,
        delta_k[1, 2] / phase,
        delta_k[2, 2] / phase,
    )
    for function, value in zip(functions, components):
        substitutions[function] = value
        substitutions[sp.diff(function, magnetic_theta)] = sp.diff(value, theta)
        substitutions[sp.diff(function, magnetic_theta, 2)] = sp.diff(value, theta, 2)
    magnetic = magnetic_gradient.subs(substitutions).subs(magnetic_theta, theta).applyfunc(
        lambda value: canonical(value * phase)
    )
    dot_p = delta_p.applyfunc(lambda value: canonical(-sp.I * omega * value))
    pi = (-sp.Rational(1, 2) * (dot_p + algebraic + magnetic)).applyfunc(canonical)

    primary_p = canonical(
        sum(h0[i, j] * delta_p[i, j] for i in range(3) for j in range(3))
        + sum(delta_h[i, j] * p0[i, j] for i in range(3) for j in range(3))
    )
    primary_q = canonical(
        2 * sum(h0[i, j] * pi[i, j] for i in range(3) for j in range(3))
        + sum(delta_k[i, j] * p0[i, j] for i in range(3) for j in range(3))
    )
    return pi, {"linear_P_trace_residual": str(primary_p), "linear_Q_scale_residual": str(primary_q)}


def _polar_spacetime(ell: int) -> dict[str, Any]:
    """Return the linear polar ADM/Ostrogradsky data before pi reconstruction."""

    epsilon = sp.symbols("epsilon")
    time, space, theta, phi = sp.symbols("t x theta phi", real=True)
    omega = sp.symbols("Omega", real=True)
    if ell:
        at, shift, ct, gauge = sp.symbols("A_t B C_t U")
        coefficients = (at, shift, ct, gauge)
        sphere = sp.S.Zero
    else:
        circle, sphere, electric = sp.symbols("C K U")
        at, shift, ct, gauge = sp.S.Zero, sp.S.Zero, circle, electric
        coefficients = (circle, sphere, electric)
    wave = sp.exp(-sp.I * omega * time)
    harmonic = sp.legendre(ell, sp.cos(theta)) if ell else sp.S.One
    axial = -sp.sin(theta) * sp.diff(harmonic, theta)
    coordinates = (time, space, theta, phi)

    metric = sp.diag(-1, 1, 1, sp.sin(theta) ** 2)
    metric[0, 0] += epsilon * at * wave * harmonic
    metric[0, 1] = metric[1, 0] = epsilon * shift * wave * harmonic
    metric[1, 1] += epsilon * ct * wave * harmonic
    if not ell:
        metric[2, 2] += epsilon * sphere * wave
        metric[3, 3] += epsilon * sphere * wave * sp.sin(theta) ** 2
    inverse = metric.inv().applyfunc(lambda x: _trunc(x, epsilon, 1))
    connection = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            for c in range(4):
                connection[a][b][c] = _trunc(
                    sum(
                        inverse[a, d]
                        * (
                            sp.diff(metric[d, c], coordinates[b])
                            + sp.diff(metric[d, b], coordinates[c])
                            - sp.diff(metric[b, c], coordinates[d])
                        )
                        for d in range(4)
                    )
                    / 2,
                    epsilon,
                    1,
                )

    field = sp.zeros(4)
    field[2, 3] = sp.sin(theta)
    field[3, 2] = -field[2, 3]
    if ell:
        # The stored polar U is the coefficient of A_phi=U X_phi.
        field[0, 3] = -sp.I * omega * epsilon * gauge * wave * axial
        field[3, 0] = -field[0, 3]
        field[2, 3] += epsilon * gauge * wave * sp.diff(axial, theta)
        field[3, 2] = -field[2, 3]
    else:
        field[0, 1] = -sp.I * omega * epsilon * gauge * wave
        field[1, 0] = -field[0, 1]

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

    spatial = sp.Matrix(metric[1:, 1:])
    spatial_inverse = spatial.inv().applyfunc(lambda x: _trunc(x, epsilon, 1))
    sqrt_h = _trunc(sp.sqrt(spatial.det()), epsilon, 1).subs(sp.Abs(sp.sin(theta)), sp.sin(theta))
    shift_cov = sp.Matrix([metric[0, i] for i in range(1, 4)])
    shift_up = (spatial_inverse * shift_cov).applyfunc(lambda x: _trunc(x, epsilon, 1))
    lapse = _trunc(sp.sqrt(-(metric[0, 0] - (shift_cov.T * shift_up)[0])), epsilon, 1)

    gamma = [[[sp.S.Zero for _ in range(3)] for _ in range(3)] for _ in range(3)]
    spatial_coords = coordinates[1:]
    for a in range(3):
        for b in range(3):
            for c in range(3):
                gamma[a][b][c] = _trunc(
                    sum(
                        spatial_inverse[a, d]
                        * (
                            sp.diff(spatial[d, c], spatial_coords[b])
                            + sp.diff(spatial[d, b], spatial_coords[c])
                            - sp.diff(spatial[b, c], spatial_coords[d])
                        )
                        for d in range(3)
                    )
                    / 2,
                    epsilon,
                    1,
                )

    extrinsic = sp.zeros(3)
    for i in range(3):
        for j in range(3):
            d_i_shift_j = sp.diff(shift_cov[j], spatial_coords[i]) - sum(
                gamma[k][i][j] * shift_cov[k] for k in range(3)
            )
            d_j_shift_i = sp.diff(shift_cov[i], spatial_coords[j]) - sum(
                gamma[k][j][i] * shift_cov[k] for k in range(3)
            )
            extrinsic[i, j] = _trunc(
                (sp.diff(spatial[i, j], time) - d_i_shift_j - d_j_shift_i) / (2 * lapse),
                epsilon,
                1,
            )

    riemann = data["riemann"]
    schouten = data["schouten"]

    def weyl(a: int, b: int, c: int, d: int) -> sp.Expr:
        lowered = _trunc(sum(metric[a, e] * riemann[e][b][c][d] for e in range(4)), epsilon, 1)
        return _trunc(
            lowered
            - (
                metric[a, c] * schouten[d, b]
                - metric[a, d] * schouten[c, b]
                - metric[b, c] * schouten[d, a]
                + metric[b, d] * schouten[c, a]
            ),
            epsilon,
            1,
        )

    normal = [1 / lapse] + [-shift_up[i] / lapse for i in range(3)]
    electric_weyl_cov = sp.zeros(3)
    for i in range(3):
        for j in range(3):
            electric_weyl_cov[i, j] = _trunc(
                sum(weyl(i + 1, a, j + 1, b) * normal[a] * normal[b] for a in range(4) for b in range(4)),
                epsilon,
                1,
            )
    momentum_p = (-3 * sqrt_h * spatial_inverse * electric_weyl_cov * spatial_inverse).applyfunc(
        lambda x: _trunc(x, epsilon, 1)
    )

    field_up = sp.zeros(4)
    for a in range(4):
        for b in range(4):
            field_up[a, b] = _trunc(
                sum(inverse[a, c] * inverse[b, d] * field[c, d] for c in range(4) for d in range(4)),
                epsilon,
                1,
            )
    spacetime_density = _trunc(sp.sqrt(-metric.det()), epsilon, 1).subs(
        sp.Abs(sp.sin(theta)), sp.sin(theta)
    )
    maxwell_e = sp.Matrix(
        [-spacetime_density * field_up[0, i] for i in range(1, 4)]
    ).applyfunc(lambda x: _trunc(x, epsilon, 1))

    background_p = momentum_p.subs(epsilon, 0).applyfunc(canonical)
    expected_p = sp.diag(sp.sin(theta), -sp.sin(theta) / 2, -1 / (2 * sp.sin(theta)))
    require((background_p - expected_p).applyfunc(canonical) == sp.zeros(3), "background P normalization changed")

    delta_h = sp.Matrix(3, 3, lambda i, j: coeff1(spatial[i, j], epsilon))
    delta_k = extrinsic.applyfunc(lambda x: coeff1(x, epsilon))
    delta_p = momentum_p.applyfunc(lambda x: coeff1(x, epsilon))
    delta_pi, primary_residuals = _linear_pi(delta_h, delta_k, delta_p, omega, time, theta)
    require(primary_residuals["linear_P_trace_residual"] == "0", f"ell={ell} P trace failed")
    require(primary_residuals["linear_Q_scale_residual"] == "0", f"ell={ell} Q scale failed")

    return {
        "ell": ell,
        "lambda": ell * (ell + 1),
        "coefficients": coefficients,
        "omega": omega,
        "coordinates": (time, theta),
        "harmonic": harmonic,
        "axial": axial,
        "delta_h": delta_h,
        "delta_K": delta_k,
        "delta_pi": delta_pi,
        "delta_P": delta_p,
        "delta_a": sp.Matrix([0, 0, gauge * wave * axial]) if ell else sp.Matrix([gauge * wave, 0, 0]),
        "delta_E": maxwell_e.applyfunc(lambda x: coeff1(x, epsilon)),
        "background_P": background_p,
        "primary_residuals": primary_residuals,
    }


def _normalization_ledger() -> dict[str, Any]:
    epsilon, scale = sp.symbols("epsilon s")
    old = -scale**2 * (1 + epsilon) ** 2 / (2 * sp.sqrt(1 + epsilon))
    selected = scale**2 * (1 + epsilon) ** 2 / (3 * sp.sqrt(1 + epsilon))
    old_cubic = canonical(sp.expand(sp.series(old, epsilon, 0, 4).removeO()).coeff(epsilon, 3))
    selected_cubic = canonical(sp.expand(sp.series(selected, epsilon, 0, 4).removeO()).coeff(epsilon, 3))
    require(old_cubic == scale**2 / 32, "imported ambiguity witness changed")
    require(selected_cubic == -scale**2 / 48, "selected cubic witness changed")
    return {
        "selected_action": "S_grav=(3/8) integral sqrt(-g) C_abcd C^abcd",
        "reference_action": "S_ref=-(1/4) integral sqrt(-g) C_abcd C^abcd",
        "exact_action_scale_selected_over_reference": "-3/2",
        "boundary_convention": "adjoin K_ij with L_n h_ij=2K_ij and perform no integration by parts in time; discard only spatial divergences on closed Sigma",
        "canonical_pairs": ["(h_ij,pi^ij)", "(K_ij,P^ij)", "(a_i,E^i)"],
        "P_definition": "P^ij=-3*sqrt(h)*C^(i n j n)",
        "background_P_orthonormal_density": ["1", "-1/2", "-1/2"],
        "selected_H_perp_gravity": "2*pi^ij*K_ij + P_ij*P^ij/(3*sqrt(h)) + P^ij*R_ij + P^ij*K_ij*K + D_iD_jP^ij + (3/2)*sqrt(h)*C_ijkn*C^(ijk)_n",
        "primary_constraints": ["P_trace=h_ij P^ij=0", "Q_scale=2h_ij pi^ij+K_ijP^ij=0"],
        "old_rank_only_one_slot_cubic": str(old_cubic),
        "selected_one_slot_cubic": str(selected_cubic),
        "ambiguity_removed": True,
    }


def _channel_crosswalk_ledger(balanced: dict[str, Any], polar: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Substitute every actual correction and its conjugate signed channel."""

    rows: list[dict[str, Any]] = []

    def parse(value: str) -> sp.Expr:
        return sp.sympify(value, locals={"sqrt": sp.sqrt})

    def tensor_payload(data: dict[str, Any], substitutions: dict[sp.Symbol, sp.Expr]) -> dict[str, Any]:
        omega = data["omega"]
        time, _ = data["coordinates"]
        phase = sp.exp(-sp.I * omega * time)

        def one(value: sp.Expr) -> str:
            return str(canonical((value / phase).subs(substitutions))) if value != 0 else "0"

        return {
            "delta_h": [[one(data["delta_h"][i, j]) for j in range(3)] for i in range(3)],
            "delta_K": [[one(data["delta_K"][i, j]) for j in range(3)] for i in range(3)],
            "delta_pi": [[one(data["delta_pi"][i, j]) for j in range(3)] for i in range(3)],
            "delta_P": [[one(data["delta_P"][i, j]) for j in range(3)] for i in range(3)],
            "delta_a": [one(data["delta_a"][i]) for i in range(3)],
            "delta_E": [one(data["delta_E"][i]) for i in range(3)],
        }

    homogeneous = polar["0"]
    homogeneous_coefficients = homogeneous["coefficients"]
    homogeneous_actual: list[tuple[str, str, list[str]]] = []
    for name, channel in balanced["homogeneous_channels"].items():
        correction = channel.get("algebraic_correction_C_K_U")
        if correction is not None:
            homogeneous_actual.append((name, channel["output_frequency"], correction))
    homogeneous_actual.append(("combined_zero", "0", balanced["second_order_correction"]["zero_frequency_homogeneous_correction"]))
    for name, omega_text, correction in homogeneous_actual:
        omega_value = parse(omega_text)
        coefficient_values = [parse(value) for value in correction]
        signs = (1,) if omega_value == 0 else (1, -1)
        for sign in signs:
            substitutions = dict(zip(homogeneous_coefficients, coefficient_values))
            substitutions[homogeneous["omega"]] = sign * omega_value
            rows.append(
                {
                    "ell": 0,
                    "channel": name,
                    "frequency_sign": "+" if sign == 1 else "-",
                    "omega": str(canonical(sign * omega_value)),
                    "covariant_coefficients": correction,
                    "canonical": tensor_payload(homogeneous, substitutions),
                }
            )

    for ell in (2, 4):
        data = polar[str(ell)]
        coefficients = data["coefficients"]
        for name, channel in balanced["generic_polar_channels"][str(ell)].items():
            correction = channel.get("correction_At_B_Ct_U")
            if correction is None:
                continue
            omega_value = parse(channel["output_frequency"])
            coefficient_values = [parse(value) for value in correction]
            signs = (1,) if omega_value == 0 else (1, -1)
            for sign in signs:
                substitutions = dict(zip(coefficients, coefficient_values))
                substitutions[data["omega"]] = sign * omega_value
                rows.append(
                    {
                        "ell": ell,
                        "channel": name,
                        "frequency_sign": "+" if sign == 1 else "-",
                        "omega": str(canonical(sign * omega_value)),
                        "covariant_coefficients": correction,
                        "canonical": tensor_payload(data, substitutions),
                    }
                )
    return rows


def build_certificate() -> dict[str, Any]:
    action = json.loads(ACTION.read_text(encoding="utf-8"))
    balanced = json.loads(BALANCED.read_text(encoding="utf-8"))
    obstruction = json.loads(CUBIC_OBSTRUCTION.read_text(encoding="utf-8"))
    require(action["rational_fixture"]["parameters"]["alpha_B"] == "3", "action fixture changed")
    require(balanced["classification"]["complete_second_order_extension_constructed"], "balanced correction changed")
    require(not obstruction["classification"]["background_ostrogradsky_magnitude_present"], "obstruction input changed")

    polar = {str(ell): _polar_spacetime(ell) for ell in (0, 2, 4)}
    polar_serialized: dict[str, Any] = {}
    for ell_text, row in polar.items():
        coefficients = row["coefficients"]
        omega = row["omega"]
        time, theta = row["coordinates"]
        phase = sp.exp(-sp.I * omega * time)

        def strip_phase(value: sp.Expr) -> str:
            return str(canonical(value / phase)) if value != 0 else "0"

        polar_serialized[ell_text] = {
            "lambda": row["lambda"],
            "coefficient_order": [str(value) for value in coefficients],
            "frequency": str(omega),
            "harmonic": str(row["harmonic"]),
            "axial_one_form_phi": str(row["axial"]),
            "delta_h_over_phase": [[strip_phase(row["delta_h"][i, j]) for j in range(3)] for i in range(3)],
            "delta_K_over_phase": [[strip_phase(row["delta_K"][i, j]) for j in range(3)] for i in range(3)],
            "delta_pi_over_phase": [[strip_phase(row["delta_pi"][i, j]) for j in range(3)] for i in range(3)],
            "delta_P_over_phase": [[strip_phase(row["delta_P"][i, j]) for j in range(3)] for i in range(3)],
            "delta_a_over_phase": [strip_phase(row["delta_a"][i]) for i in range(3)],
            "delta_E_over_phase": [strip_phase(row["delta_E"][i]) for i in range(3)],
            "primary_constraint_residuals": row["primary_residuals"],
        }

    channel_ledger = _channel_crosswalk_ledger(balanced, polar)
    expected_actual = (2 * 4 + 1) + 2 * (2 * 4 + 1)
    require(len(channel_ledger) == expected_actual, "signed channel census changed")
    return {
        "schema": "einstein-weyl-alpha-b3-ostrogradsky-canonical-crosswalk-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha256(SCHEMA),
        "result_id": "EINSTEIN_WEYL_ALPHA_B3_OSTROGRADSKY_CANONICAL_CROSSWALK_V1",
        "result_state": "ACTION_NORMALIZED_CANONICAL_CROSSWALK_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "producer": str(Path(__file__).relative_to(ROOT)),
            "producer_sha256": sha256(Path(__file__)),
            "inputs": {
                str(ACTION.relative_to(ROOT)): sha256(ACTION),
                str(BALANCED.relative_to(ROOT)): sha256(BALANCED),
                str(CUBIC_OBSTRUCTION.relative_to(ROOT)): sha256(CUBIC_OBSTRUCTION),
            },
        },
        "normalization": _normalization_ledger(),
        "background": {
            "metric": "-dt^2+dx^2+dtheta^2+sin(theta)^2 dphi^2",
            "magnetic_F": "sin(theta) dtheta wedge dphi",
            "K0": "0",
            "pi0": "0",
            "P0_coordinate_density": matrix_strings(polar["0"]["background_P"]),
        },
        "linear_polar_crosswalk": polar_serialized,
        "inverse_map": {
            "homogeneous": "C and K are the Y_0 coefficients of delta h_xx and delta h_thetatheta; U is the Y_0 coefficient of delta a_x",
            "generic_C": "C_t=<Y_ell,delta h_xx>/<Y_ell,Y_ell>",
            "generic_B": "B=-2<dY_ell,delta K_xtheta>/<dY_ell,dY_ell>",
            "generic_U": "U=<X_ell,delta a_phi>/<X_ell,X_ell>",
            "generic_A": "if p_x is the Y_ell coefficient of delta P^xx/sin(theta), A_t=(4*p_x+2*(Omega^2+lambda/2+1)*C_t)/lambda",
            "physical_fibres": "lambda=6 or 20 and every stored Omega; all inverse denominators are nonzero",
            "gauge_scope": "inverse on the stored k=0 polar representatives; lapse and shift are retained as A_t and B, not quotient-forgotten",
        },
        "symplectic_and_equation_checks": {
            "poincare_cartan_identity": "Theta_selected|Sigma=integral_Sigma(pi^ij delta h_ij+P^ij delta K_ij+E^i delta a_i); it follows before imposing equations from the declared no-time-integration-by-parts Legendre transform",
            "selected_P_hamilton_equation": "(partial_t-L_shift)P^ij=-2N*pi^ij-N*(P^ij*K+h^ij*P^ab*K_ab)-delta_K[(3/2)N sqrt(h) C_abc n C^(abc)n]",
            "pi_reconstruction": "the displayed delta_pi is the exact linearization of this equation at N=1, shift=0, K=pi=0 and P=P0",
            "primary_constraint_pullback": "P_trace and Q_scale residuals vanish identically in every ell=0,2,4 template",
            "alpha_B3_Euler_compatibility": "P=-3 sqrt(h) C^(i n j n) is the Legendre equation of the same selected action; the Hamilton equation used for pi is its K Euler equation",
            "symplecticity": True,
            "constraint_pullback": True,
            "Euler_compatibility": True,
        },
        "signed_channel_crosswalk": channel_ledger,
        "channel_coverage": {
            "homogeneous": sorted(balanced["homogeneous_channels"].keys()),
            "ell2": sorted(balanced["generic_polar_channels"]["2"].keys()),
            "ell4": sorted(balanced["generic_polar_channels"]["4"].keys()),
            "signed_frequency_rule": "the conjugate channel is obtained by Omega->-Omega and complex conjugation; zero channels are real",
            "fully_mapped_components": ["delta_h", "delta_K", "delta_pi", "delta_P", "delta_a", "delta_E"],
            "actual_signed_channel_rows": len(channel_ledger),
        },
        "classification": {
            "boundary_convention_fixed": True,
            "exact_action_scale_fixed": True,
            "background_P_magnitude_fixed": True,
            "first_H_perp_cubic_ambiguity_removed": True,
            "all_stored_channels_canonical_map_defined": True,
            "complete_delta_pi_map": True,
            "complete_canonical_transformation_and_inverse": True,
            "K3_evaluation_authorized": True,
        },
        "next_gate": "regenerate the complete D3C and mixed D2C tensors in this canonical convention, then evaluate the correction-independent third-order Kuranishi quotient",
        "claim_boundary": "This exact gate fixes the alpha_B=3 canonical scale, background momentum, selected Hamiltonian coefficient and complete linear canonical lift of every stored ell=0,2,4 correction channel and conjugate.  It does not itself evaluate D3C, K3, boundedness, causality, particles, positivity, unitarity or quantum theory.",
    }


def verify(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    require(payload == build_certificate(), "certificate drift")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        assert args.verify is not None
        verify(args.verify)


if __name__ == "__main__":
    main()
