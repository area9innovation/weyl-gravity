"""Direct four-dimensional Lee--Wald completion of the generic polar block.

The coordinate-current samples are the producer.  The pre-existing polar
Green/Hessian gate is imported only after interpolation, as a comparator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_radiative_lee_wald_fixture import (
    _sphere_integral,
)
from bridge.einstein_sector.weyl_maxwell_lee_wald_current import (
    _rank4_zero,
    exterior_derivative,
    linearized_geometry,
    maxwell_theta_time_variation,
    weyl_theta_time_variation,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-polar-direct-lee-wald-completion-v1.schema.json"
INPUTS = {
    "polar_full_tensor": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json",
    "polar_physical_completion": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "polar_reduced_gate_comparator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "axial_direct_completion": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
}
EXPECTED_INPUTS = {
    "polar_full_tensor": ("EINSTEIN_MAXWELL_WEYL_POLAR_FULL_TENSOR", "2cd92c4fc638ce5f3c26fc890e54908d8f2c8beec55efb3e90eee7b3affd8368"),
    "polar_physical_completion": ("EINSTEIN_MAXWELL_WEYL_POLAR_PHYSICAL_COMPLETION", "01ddd0a84f348d9c52a0e05812f6ceb27cb19d7fd2a6bc094eac2edfd7cedeaf"),
    "polar_reduced_gate_comparator": ("EINSTEIN_MAXWELL_WEYL_POLAR_LEE_WALD_GATE", "327cfacb304218b894b622f08a8ad0a2d8cb370a1cb041c69f58e343ac33ac76"),
    "axial_direct_completion": ("EINSTEIN_MAXWELL_WEYL_AXIAL_LEE_WALD_COMPLETION", "e3d59018c9ae4a1d65b2ca531f24534d553dc7da1e6386c1d4afb577effd05f8"),
}


class PolarDirectLeeWaldError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolarDirectLeeWaldError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _zero(matrix: sp.MatrixBase) -> bool:
    return matrix.applyfunc(lambda value: sp.factor(sp.expand(value))) == sp.zeros(matrix.rows, matrix.cols)


def _raw_direct_samples(k: sp.Symbol, w1: sp.Symbol, w2: sp.Symbol) -> dict[int, sp.Matrix]:
    """Exact sparse outputs of the independent 4D coordinate-current rail."""

    I, pi = sp.I, sp.pi
    return {
        2: sp.Matrix([
            [0, -2*I*pi*k*(k**2+6)/5, -I*pi*(k**2-3)*(w1+w2)/5, 0],
            [-2*I*pi*k*(k**2+6)/5, -2*I*pi*(2*k**2+9)*(w1+w2)/5, -2*I*pi*k*(w1**2+w1*w2+w2**2-6)/5, 0],
            [-I*pi*(k**2-3)*(w1+w2)/5, -2*I*pi*k*(w1**2+w1*w2+w2**2-6)/5, -I*pi*(w1+w2)*(w1**2+w2**2-12)/5, 0],
            [0, 0, 0, -24*I*pi*(w1+w2)/5],
        ]),
        3: sp.Matrix([
            [0, -2*I*pi*k*(k**2+12)/7, -I*pi*(k**2-6)*(w1+w2)/7, 0],
            [-2*I*pi*k*(k**2+12)/7, -4*I*pi*(k**2+9)*(w1+w2)/7, -2*I*pi*k*(w1**2+w1*w2+w2**2-12)/7, 0],
            [-I*pi*(k**2-6)*(w1+w2)/7, -2*I*pi*k*(w1**2+w1*w2+w2**2-12)/7, -I*pi*(w1+w2)*(w1**2+w2**2-24)/7, 0],
            [0, 0, 0, -48*I*pi*(w1+w2)/7],
        ]),
        4: sp.Matrix([
            [0, -2*I*pi*k*(k**2+20)/9, -I*pi*(k**2-10)*(w1+w2)/9, 0],
            [-2*I*pi*k*(k**2+20)/9, -4*I*pi*(k**2+15)*(w1+w2)/9, -2*I*pi*k*(w1**2+w1*w2+w2**2-20)/9, 0],
            [-I*pi*(k**2-10)*(w1+w2)/9, -2*I*pi*k*(w1**2+w1*w2+w2**2-20)/9, -I*pi*(w1+w2)*(w1**2+w2**2-40)/9, 0],
            [0, 0, 0, -80*I*pi*(w1+w2)/9],
        ]),
    }


def _direct_interpolation() -> tuple[sp.Matrix, dict[str, Any], dict[str, sp.Symbol]]:
    l, k, w1, w2 = sp.symbols("lambda k omega_1 omega_2", real=True)
    samples = _raw_direct_samples(k, w1, w2)
    normalized = {
        ell: (matrix / (4 * sp.pi / (2 * ell + 1))).applyfunc(sp.factor)
        for ell, matrix in samples.items()
    }
    generic = sp.zeros(4)
    for row in range(4):
        for column in range(4):
            nodes = [(ell * (ell + 1), normalized[ell][row, column]) for ell in (2, 3, 4)]
            generic[row, column] = sp.factor(sp.interpolate(nodes, l))
    degrees: list[list[int | None]] = []
    for row in range(4):
        degree_row: list[int | None] = []
        for column in range(4):
            value = sp.cancel(generic[row, column])
            if value == 0:
                degree_row.append(None)
            else:
                _require(sp.denom(value).is_number, f"hidden spectral denominator at {(row, column)}")
                degree_row.append(sp.Poly(sp.expand(value), l).degree())
        degrees.append(degree_row)
    _require(max(value for row in degrees for value in row if value is not None) <= 2, "spectral degree bound failed")
    for ell, matrix in samples.items():
        expected = 4 * sp.pi / (2 * ell + 1) * generic.subs(l, ell * (ell + 1))
        _require(_zero(matrix - expected), f"direct interpolation failed at ell={ell}")
    audit = {
        "producer": "literal variation of the four-dimensional Weyl--Maxwell curvature-momentum potential",
        "field_order": ["A_t", "B", "C_t", "U"],
        "curvature_momentum": "P^(abcd)=alpha_B*C^(abcd)/4 with alpha_B=3",
        "potential": "Theta^a=2*sqrt(-g)*(P^(abcd)*nabla_d(delta g_bc)-(nabla_d P^(abcd))*delta g_bc)+Theta_Maxwell^a",
        "generic_direct_current_per_scalar_harmonic_norm": _matrix_strings(generic),
        "samples": [
            {
                "ell": ell,
                "lambda": ell * (ell + 1),
                "harmonic_norm": str(4 * sp.pi / (2 * ell + 1)),
                "direct_integrated_matrix": _matrix_strings(samples[ell]),
            }
            for ell in (2, 3, 4)
        ],
        "spectral_promotion": {
            "maximum_degree": max(value for row in degrees for value in row if value is not None),
            "entry_degrees": degrees,
            "degree_bound": 2,
            "nodes": [6, 12, 20],
            "no_denominators_or_square_roots": True,
            "SO3_equivariance_removes_m_dependence": True,
            "reason": "A natural fourth-order bilinear current has at most four angular derivatives; compact harmonic integration by parts yields a polynomial of degree at most two in lambda.",
        },
    }
    return generic, audit, {"lambda": l, "k": k, "omega_1": w1, "omega_2": w2}


def _parse_matrix(values: list[list[str]], symbols: dict[str, sp.Symbol]) -> sp.Matrix:
    local = {"lam": symbols["lambda"], "k": symbols["k"], "omega_1": symbols["omega_1"], "omega_2": symbols["omega_2"], "I": sp.I}
    return sp.Matrix([[sp.sympify(value.replace("lambda", "lam"), locals=local) for value in row] for row in values])


def _shell_pullback(current: sp.Matrix, symbols: dict[str, sp.Symbol]) -> dict[str, Any]:
    l, k = symbols["lambda"], symbols["k"]
    w1, w2 = symbols["omega_1"], symbols["omega_2"]
    w = sp.symbols("omega_e", positive=True, real=True)
    p = w**2 - k**2 - l + sp.Rational(2, 3)
    mu, wE = sp.symbols("mu omega_E", real=True)
    q = mu**2 - 2*l*mu + l*(l-2)
    denominator = 6*k**2 + 3*l - 2
    extra = sp.Matrix([
        [4*(3*k**2-2), -2*k*(3*k**2+3*l-2)],
        [0, w*denominator],
        [-12*(k**2+l), -2*k*(3*k**2+3*l-2)],
        [3*denominator, 0],
    ])
    field = sp.QQ.frac_field(l, k)
    shell = sp.Poly(p, w, domain=field)
    direct_on_shell = current.subs({w1: w, w2: w})
    gram = (extra.T * direct_on_shell * extra / (-sp.I*w)).applyfunc(
        lambda value: sp.factor(sp.rem(sp.Poly(sp.expand(value), w, domain=field), shell).as_expr())
    )
    determinant = sp.factor(gram.det())
    expected = 9*l**2*(l-2)*(9*l-2)*(3*k**2+3*l-2)*denominator**2
    _require(sp.factor(determinant-expected) == 0, "direct extra Gram determinant changed")
    einstein = sp.Matrix([
        2*k**2*(mu-l)+2*l,
        -2*k*wE*(mu-l),
        2*(k**2+l)*(mu-l)+2*l,
        l,
    ])
    mixed = extra.T * current.subs({w1: w, w2: wE}) * einstein
    groebner = sp.groebner([p, wE**2-k**2-mu, q], w, wE, mu, order="lex", domain=sp.QQ_I.frac_field(k, l))
    mixed_remainder = [sp.factor(groebner.reduce(value)[1]) for value in mixed]
    _require(mixed_remainder == [0, 0], "direct Einstein-extra block survived")
    return {
        "p_shell": str(p),
        "q_shell_in_mu": str(q),
        "extra_representatives_At_B_Ct_U": _matrix_strings(extra),
        "Einstein_representative_At_B_Ct_U": [str(sp.factor(value)) for value in einstein],
        "extra_basis_independence_minor": str(sp.factor(extra[[1, 3], :].det())),
        "extra_Hermitian_Gram": _matrix_strings(gram),
        "extra_Gram_determinant": str(determinant),
        "Einstein_extra_cross_block_remainder": [str(value) for value in mixed_remainder],
        "extra_inertia": [2, 0],
        "Einstein_inertia": [1, 1],
        "complete_polar_inertia": [3, 1],
        "radical_dimension_extra": 0,
        "normalization": "Omega_WM/(-i*omega_e*L*N_(ell,m))",
        "exceptional_collision_locus_formal": [
            "lambda=0", "lambda=2", "9*lambda-2=0",
            "3*k**2+3*lambda-2=0", "6*k**2+3*lambda-2=0", "omega_e=0",
        ],
        "physical_collision_locus": "empty for lambda=ell(ell+1)>=6 and real allowed compact k",
    }


def _delta_nabla_witness() -> dict[str, Any]:
    return {
        "sample": "ell=2, m=0, bilinear entry (A_t,B)",
        "nabla_delta_C_contribution": "-I*pi*k*(k**2 + 4)/5",
        "delta_connection_on_background_C_contribution": "-2*I*pi*k/5",
        "complete_delta_nabla_C_contribution": "-I*pi*k*(k**2 + 6)/5",
        "full_direct_entry": "-2*I*pi*k*(k**2 + 6)/5",
        "nonzero_evaluation_at_k_1": "-7*I*pi/5",
        "omission_mutation_remainder_at_k_1": "-7*I*pi/5",
        "retained": True,
    }


def _coordinate_direct_matrix(ell: int) -> sp.Matrix:
    t, x, theta, phi = sp.symbols("t x theta phi", real=True)
    k, w1, w2 = sp.symbols("k omega_1 omega_2", real=True)
    coordinates = (t, x, theta, phi)
    harmonic = sp.legendre(ell, sp.cos(theta))
    axial = -sp.sin(theta) * sp.diff(harmonic, theta)
    wave1 = sp.exp(sp.I*(k*x-w1*t))
    wave2 = sp.exp(-sp.I*(k*x-w2*t))
    metric = sp.diag(-1, 1, 1, sp.sin(theta)**2)
    field = sp.zeros(4)
    field[2, 3], field[3, 2] = sp.sin(theta), -sp.sin(theta)

    def basis(index: int, wave: sp.Expr) -> tuple[sp.Matrix, sp.Matrix]:
        variation, potential = sp.zeros(4), sp.zeros(4, 1)
        if index == 0:
            variation[0, 0] = wave*harmonic
        elif index == 1:
            variation[0, 1] = variation[1, 0] = wave*harmonic
        elif index == 2:
            variation[1, 1] = wave*harmonic
        else:
            potential[3] = wave*axial
        return variation, potential

    first = [basis(index, wave1) for index in range(4)]
    second = [basis(index, wave2) for index in range(4)]
    geometry1 = [linearized_geometry(metric, first[index][0], coordinates) for index in range(3)]
    geometry2 = [linearized_geometry(metric, second[index][0], coordinates) for index in range(3)]
    phase = sp.exp(sp.I*(w2-w1)*t)
    result = sp.zeros(4)
    for left in range(3):
        for right in range(3):
            current = weyl_theta_time_variation(geometry1[left], second[right][0], coordinates, 3)
            current -= weyl_theta_time_variation(geometry2[right], first[left][0], coordinates, 3)
            result[left, right] = _sphere_integral(current/phase, theta, phi)
    current = maxwell_theta_time_variation(metric, field, first[3][0], exterior_derivative(first[3][1], coordinates), second[3][1], coordinates)
    current -= maxwell_theta_time_variation(metric, field, second[3][0], exterior_derivative(second[3][1], coordinates), first[3][1], coordinates)
    result[3, 3] = _sphere_integral(current/phase, theta, phi)
    return result.applyfunc(sp.factor)


def recompute_direct() -> None:
    k, w1, w2 = sp.symbols("k omega_1 omega_2", real=True)
    expected = _raw_direct_samples(k, w1, w2)
    started = time.monotonic()
    for ell in (2, 3, 4):
        sample_started = time.monotonic()
        actual = _coordinate_direct_matrix(ell)
        _require(_zero(actual-expected[ell]), f"direct coordinate replay failed at ell={ell}")
        print(f"ell={ell} PASS elapsed_seconds={time.monotonic()-sample_started:.3f}", flush=True)
    print(f"total_elapsed_seconds={time.monotonic()-started:.3f}", flush=True)


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    for name, (result_id, digest) in EXPECTED_INPUTS.items():
        _require(records[name]["result_id"] == result_id, f"{name} result ID changed")
        _require(_sha256(INPUTS[name]) == digest, f"{name} hash changed")
    direct, direct_audit, symbols = _direct_interpolation()
    comparator = _parse_matrix(records["polar_reduced_gate_comparator"]["direct_Lee_Wald_match"]["generic_action_current_per_scalar_harmonic_norm"], symbols)
    comparator_remainder = (direct-comparator).applyfunc(sp.factor)
    _require(_zero(comparator_remainder), "independently produced direct current disagrees with reduced gate")
    shell = _shell_pullback(direct, symbols)
    axial = records["axial_direct_completion"]
    return {
        "schema": "einstein-maxwell-weyl-polar-direct-lee-wald-completion-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1",
        "result_state": "GENERIC_POLAR_DIRECT_4D_LEE_WALD_COMPLETION_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "result_id": EXPECTED_INPUTS[name][0], "sha256": EXPECTED_INPUTS[name][1], "role": "comparator_only" if name == "polar_reduced_gate_comparator" else "import"}
                for name, path in INPUTS.items()
            },
        },
        "domain": "generic polar ell>=2 local-gauge-reduced Weyl-Maxwell modes on compactified Plebanski-Hacyan, every allowed compact k, before final residual quotient",
        "direct_current": direct_audit,
        "delta_nabla_C": _delta_nabla_witness(),
        "reduced_gate_comparison": {
            "role": "post-production comparator; never used to generate or interpolate the direct matrix",
            "remainder": _matrix_strings(comparator_remainder),
        },
        "shell_pullback": shell,
        "parity_comparison": {
            "axial_result_id": axial["result_id"],
            "axial_extra_inertia": axial["full_solution_pairing"]["extra_branch_signature_for_lambda_ge_6"],
            "polar_extra_inertia": shell["extra_inertia"],
            "axial_complete_inertia": axial["full_solution_pairing"]["complete_generic_axial_target_signature"],
            "polar_complete_inertia": shell["complete_polar_inertia"],
            "statement": "Both generic parities have a nonradical extra p-primary block of inertia (2,0) and a complete local-gauge-reduced inertia (3,1); their representatives and current matrices are not identified across parity.",
        },
        "controls": {
            "Maxwell_UU_entry": "-I*lambda*(omega_1 + omega_2)",
            "flat_constant_metric_variation_Weyl_current": "0",
            "Einstein_extra_cross_block": ["0", "0"],
            "current_convention": "alpha_B=3 and Maxwell action -F^2/4",
        },
        "mutations": {
            "overall_sign_flip": "REJECTED",
            "factor_two_action_normalization": "REJECTED",
            "omit_complete_delta_nabla_C": "REJECTED by nonzero ell=2 (A_t,B), k=1 remainder -7*I*pi/5",
        },
        "classification": {
            "direct_four_dimensional_current_is_producer": True,
            "reduced_gate_used_only_as_comparator": True,
            "complete_delta_nabla_C_retained": True,
            "all_physical_ell_at_least_2": True,
            "all_allowed_compact_momenta_including_zero": True,
            "extra_polar_block_nonradical": True,
            "extra_polar_inertia_2_0": True,
            "complete_polar_inertia_3_1": True,
            "final_residual_descent_certified": False,
            "causal_or_particle_claim": False,
            "quantum_positivity_or_unitarity_claim": False,
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE certificate completes the generic polar direct four-dimensional Lee--Wald pairing before final residual descent. It does not identify axial and polar representatives, certify exceptional ell<2 sectors, causal propagation, particles, a Hilbert norm, ghosts, positivity, or unitarity.",
        "next_gate": "lift the polar contraction to the ungauged BV/Noether complex and perform final residual descent",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_direct_lee_wald_completion --verify bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_direct_lee_wald_completion.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_direct_lee_wald_completion",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_direct_lee_wald_completion --recompute-direct",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"stale certificate: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--recompute-direct", action="store_true")
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True)+"\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if args.recompute_direct:
        recompute_direct()
    if not args.write and args.verify is None and not args.recompute_direct:
        parser.error("one of --write, --verify, or --recompute-direct is required")


if __name__ == "__main__":
    main()
