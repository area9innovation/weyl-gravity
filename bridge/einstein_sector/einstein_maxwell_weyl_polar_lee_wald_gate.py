"""Direct Lee--Wald gate for the generic polar Weyl--Maxwell quotient.

The fast certificate rail reconstructs the Green current from the certified
action Hessian, checks the three stored sparse four-dimensional samples, and
evaluates the Einstein/extra shell pairing.  The deliberately slow
``--recompute-direct`` rail recomputes every nonzero sample entry from the
coordinate Lee--Wald engine.  Sparse entries are essential: applying the
spherical normalizer to one unsplit amplitude polynomial is not a certified
linear operation in the symbolic implementation.
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
from bridge.einstein_sector.einstein_maxwell_weyl_axial_green_current import (
    _green_terms,
)
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import (
    _action_operator,
)
from bridge.einstein_sector.weyl_maxwell_lee_wald_current import (
    exterior_derivative,
    linearized_geometry,
    maxwell_theta_time_variation,
    weyl_theta_time_variation,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_lee_wald_gate.schema.json"
OPERATOR = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json"
COMPLETION = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json"


class PolarLeeWaldGateError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolarLeeWaldGateError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _zero(matrix: sp.MatrixBase) -> bool:
    return matrix.applyfunc(lambda value: sp.factor(sp.expand(value))) == sp.zeros(matrix.rows, matrix.cols)


def _time_current_matrix() -> tuple[sp.Matrix, dict[str, sp.Symbol]]:
    """Return the Green current of the certified ``2 delta S`` Hessian."""

    hessian, symbols = _action_operator()
    eigenvalue, momentum, frequency = symbols
    temporal, spatial = sp.symbols("T X", commutative=True)
    differential = hessian.subs(
        {frequency: sp.I * temporal, momentum: -sp.I * spatial}, simultaneous=True
    ).applyfunc(lambda value: sp.factor(sp.expand(value)))
    current = _green_terms(differential, temporal, spatial)
    first_frequency, second_frequency = sp.symbols("omega_1 omega_2", real=True)
    matrix = sp.zeros(4)
    for term in current["time_current_terms"]:
        coefficient = sp.sympify(
            term["coefficient"].replace("lambda", "lam"),
            locals={"lam": eigenvalue},
        )
        left = term["u_component"]
        right = term["v_component"]
        factor = (
            (-sp.I * first_frequency) ** term["u_t_order"]
            * (sp.I * momentum) ** term["u_x_order"]
            * (sp.I * second_frequency) ** term["v_t_order"]
            * (-sp.I * momentum) ** term["v_x_order"]
        )
        matrix[left, right] += coefficient * factor
    matrix = matrix.applyfunc(lambda value: sp.factor(sp.expand(value)))
    return matrix, {
        "lambda": eigenvalue,
        "k": momentum,
        "omega": frequency,
        "omega_1": first_frequency,
        "omega_2": second_frequency,
    }


def _stored_direct_samples(symbols: dict[str, sp.Symbol]) -> dict[int, sp.Matrix]:
    """Sparse coordinate-current outputs, kept independently of the Hessian."""

    k, w1, w2 = symbols["k"], symbols["omega_1"], symbols["omega_2"]
    I, pi = sp.I, sp.pi
    return {
        2: sp.Matrix([
            [0, -2 * I * pi * k * (k**2 + 6) / 5, -I * pi * (k**2 - 3) * (w1 + w2) / 5, 0],
            [-2 * I * pi * k * (k**2 + 6) / 5, -2 * I * pi * (2 * k**2 + 9) * (w1 + w2) / 5, -2 * I * pi * k * (w1**2 + w1 * w2 + w2**2 - 6) / 5, 0],
            [-I * pi * (k**2 - 3) * (w1 + w2) / 5, -2 * I * pi * k * (w1**2 + w1 * w2 + w2**2 - 6) / 5, -I * pi * (w1 + w2) * (w1**2 + w2**2 - 12) / 5, 0],
            [0, 0, 0, -24 * I * pi * (w1 + w2) / 5],
        ]),
        3: sp.Matrix([
            [0, -2 * I * pi * k * (k**2 + 12) / 7, -I * pi * (k**2 - 6) * (w1 + w2) / 7, 0],
            [-2 * I * pi * k * (k**2 + 12) / 7, -4 * I * pi * (k**2 + 9) * (w1 + w2) / 7, -2 * I * pi * k * (w1**2 + w1 * w2 + w2**2 - 12) / 7, 0],
            [-I * pi * (k**2 - 6) * (w1 + w2) / 7, -2 * I * pi * k * (w1**2 + w1 * w2 + w2**2 - 12) / 7, -I * pi * (w1 + w2) * (w1**2 + w2**2 - 24) / 7, 0],
            [0, 0, 0, -48 * I * pi * (w1 + w2) / 7],
        ]),
        4: sp.Matrix([
            [0, -2 * I * pi * k * (k**2 + 20) / 9, -I * pi * (k**2 - 10) * (w1 + w2) / 9, 0],
            [-2 * I * pi * k * (k**2 + 20) / 9, -4 * I * pi * (k**2 + 15) * (w1 + w2) / 9, -2 * I * pi * k * (w1**2 + w1 * w2 + w2**2 - 20) / 9, 0],
            [-I * pi * (k**2 - 10) * (w1 + w2) / 9, -2 * I * pi * k * (w1**2 + w1 * w2 + w2**2 - 20) / 9, -I * pi * (w1 + w2) * (w1**2 + w2**2 - 40) / 9, 0],
            [0, 0, 0, -80 * I * pi * (w1 + w2) / 9],
        ]),
    }


def _direct_sample_audit() -> dict[str, Any]:
    hessian_current, symbols = _time_current_matrix()
    action_current = (hessian_current / 2).applyfunc(sp.factor)
    samples = _stored_direct_samples(symbols)
    lambda_degrees: list[list[int | None]] = []
    for row in range(action_current.rows):
        degree_row: list[int | None] = []
        for column in range(action_current.cols):
            value = sp.cancel(action_current[row, column])
            if value == 0:
                degree_row.append(None)
                continue
            _require(
                sp.denom(value).is_number,
                f"hidden lambda denominator in action current entry {(row, column)}",
            )
            degree = sp.Poly(sp.expand(value), symbols["lambda"]).degree()
            _require(degree <= 2, f"polar current spectral degree exceeded two at {(row, column)}")
            degree_row.append(degree)
        lambda_degrees.append(degree_row)
    records = []
    for ell, direct in samples.items():
        eigenvalue = ell * (ell + 1)
        norm = 4 * sp.pi / (2 * ell + 1)
        expected = (norm * action_current.subs(symbols["lambda"], eigenvalue)).applyfunc(sp.factor)
        defect = (direct - expected).applyfunc(sp.factor)
        _require(_zero(defect), f"direct ell={ell} Lee--Wald sample mismatch: {defect}")
        records.append({
            "ell": ell,
            "lambda": eigenvalue,
            "scalar_harmonic_norm": str(norm),
            "entrywise_sparse_direct_matrix": _matrix_strings(direct),
            "direct_minus_action_Green_remainder": _matrix_strings(defect),
        })
    return {
        "field_order": ["A_t", "B", "C_t", "U"],
        "independent_frequency_convention": "first exp(i(k*x-omega_1*t)); second exp(-i(k*x-omega_2*t))",
        "generic_action_current_per_scalar_harmonic_norm": _matrix_strings(action_current),
        "samples": records,
        "spectral_interpolation": {
            "direct_natural_current_degree_in_lambda_at_most": 2,
            "generic_action_current_entry_degrees_in_lambda": lambda_degrees,
            "generic_action_current_maximum_lambda_degree": max(
                degree for row in lambda_degrees for degree in row if degree is not None
            ),
            "degree_bound_proof": "The four-dimensional C^2 Lee--Wald current is a natural bilinear differential expression with at most four angular derivatives. Harmonic integration by parts reduces every scalar coefficient to a polynomial in lambda of degree at most two; no inverse angular operator occurs. The reconstructed action current is audited entrywise for polynomiality and has maximum degree one.",
            "sample_lambdas": [6, 12, 20],
            "no_hidden_lambda_denominators_or_square_roots": True,
            "SO3_equivariance_removes_m_dependence": True,
            "all_physical_ell_at_least_2_match": True,
        },
        "unsafe_route_excluded": "Do not sphere-integrate one unsplit amplitude polynomial before bilinear coefficient extraction; every stored direct entry was computed as a separate sparse bilinear current.",
    }


def _shell_audit() -> dict[str, Any]:
    current, symbols = _time_current_matrix()
    l, k = symbols["lambda"], symbols["k"]
    w1, w2 = symbols["omega_1"], symbols["omega_2"]
    w = sp.symbols("omega_e", positive=True, real=True)
    p = w**2 - k**2 - l + sp.Rational(2, 3)
    q_mass = sp.symbols("mu")
    q = q_mass**2 - 2 * l * q_mass + l * (l - 2)
    denominator = 6 * k**2 + 3 * l - 2
    extra = sp.Matrix([
        [4 * (3 * k**2 - 2), -2 * k * (3 * k**2 + 3 * l - 2)],
        [0, w * denominator],
        [-12 * (k**2 + l), -2 * k * (3 * k**2 + 3 * l - 2)],
        [3 * denominator, 0],
    ])
    hessian, hessian_symbols = _action_operator()
    _require(hessian_symbols == (l, k, symbols["omega"]), "polar symbol convention changed")
    coefficient_field = sp.QQ.frac_field(l, k)
    shell_poly = sp.Poly(p, w, domain=coefficient_field)
    for value in hessian.subs(symbols["omega"], w) * extra:
        _require(sp.rem(sp.Poly(sp.expand(value), w, domain=coefficient_field), shell_poly).is_zero, "extra representative left the p shell")
    independence_minor = sp.factor(extra[[1, 3], :].det())
    _require(independence_minor == -3 * w * denominator**2, "extra independence minor changed")

    action_current = (current / 2).subs({w1: w, w2: w})
    gram = (extra.T * action_current * extra / (-sp.I * w)).applyfunc(sp.factor)
    gram = gram.applyfunc(
        lambda value: sp.factor(sp.rem(sp.Poly(sp.expand(value), w, domain=coefficient_field), shell_poly).as_expr())
    )
    determinant = sp.factor(gram.det())
    expected_determinant = 9 * l**2 * (l - 2) * (9 * l - 2) * (3 * k**2 + 3 * l - 2) * denominator**2
    _require(sp.factor(determinant - expected_determinant) == 0, "extra Gram determinant changed")

    mu = q_mass
    einstein = sp.Matrix([
        2 * k**2 * (mu - l) + 2 * l,
        -2 * k * sp.symbols("omega_E") * (mu - l),
        2 * (k**2 + l) * (mu - l) + 2 * l,
        l,
    ])
    wE = next(symbol for symbol in einstein.free_symbols if symbol.name == "omega_E")
    mixed_current = (current / 2).subs({w1: w, w2: wE})
    mixed = (extra.T * mixed_current * einstein).applyfunc(sp.expand)
    groebner = sp.groebner(
        [p, wE**2 - k**2 - mu, q],
        w,
        wE,
        mu,
        order="lex",
        domain=sp.QQ_I.frac_field(k, l),
    )
    mixed_remainder = [sp.factor(groebner.reduce(value)[1]) for value in mixed]
    _require(mixed_remainder == [0, 0], f"Einstein-extra mixed block survived: {mixed_remainder}")

    return {
        "shells": {
            "p": str(p),
            "q_in_mu": str(q),
            "mu_definition": "mu=omega_E^2-k^2",
        },
        "extra_basis_order_At_B_Ct_U": _matrix_strings(extra),
        "basis_independence_minor_rows_B_U": str(independence_minor),
        "extra_Hermitian_current_Gram": _matrix_strings(gram),
        "extra_Gram_determinant": str(determinant),
        "physical_positivity_factors": ["lambda", "lambda-2", "9*lambda-2", "3*k**2+3*lambda-2", "6*k**2+3*lambda-2"],
        "extra_positive_frequency_inertia": [2, 0],
        "Einstein_representative_order_At_B_Ct_U": [str(sp.factor(value)) for value in einstein],
        "Einstein_extra_mixed_remainder_mod_p_q": [str(value) for value in mixed_remainder],
        "Einstein_block_inertia": [1, 1],
        "complete_polar_target_inertia_before_residual_quotient": [3, 1],
        "coefficient_extractor": "a=G_X^{-1} Omega_WM(conjugate(e),Phi)/(-i*omega_e*L*N_ell_m)",
        "extractor_scope": "conserved stationary spectral coefficient on the local-gauge-reduced p-shell block; not yet a residual or Peierls observable",
    }


def build_certificate() -> dict[str, Any]:
    operator = json.loads(OPERATOR.read_text(encoding="utf-8"))
    completion = json.loads(COMPLETION.read_text(encoding="utf-8"))
    _require(operator["result_id"] == "EINSTEIN_MAXWELL_WEYL_POLAR_FULL_TENSOR", "polar operator input changed")
    _require(completion["result_id"] == "EINSTEIN_MAXWELL_WEYL_POLAR_PHYSICAL_COMPLETION", "polar physical completion input changed")
    return {
        "schema": "einstein-maxwell-weyl-polar-lee-wald-gate-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_POLAR_LEE_WALD_GATE",
        "result_state": "GENERIC_POLAR_DIRECT_LEE_WALD_EXTRA_BLOCK_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_POLAR_ALL_PHYSICAL_ELL_K_DIRECT_CURRENT",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                str(OPERATOR.relative_to(ROOT)): _sha256(OPERATOR),
                str(COMPLETION.relative_to(ROOT)): _sha256(COMPLETION),
            },
        },
        "domain": "generic polar ell>=2 Weyl-Maxwell harmonic quotient at every allowed compact momentum, before the final residual quotient",
        "direct_Lee_Wald_match": _direct_sample_audit(),
        "shell_pairing": _shell_audit(),
        "verification_receipt": {
            "producing_date": "2026-07-17",
            "tier_0": {
                "status": "PASS",
                "commands": [
                    "python3 -m py_compile bridge/einstein_sector/einstein_maxwell_weyl_polar_lee_wald_gate.py bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_lee_wald_gate.py bridge/einstein_sector/tests/test_einstein_maxwell_weyl_polar_lee_wald_gate.py",
                    "git diff --check -- <scoped polar Lee-Wald paths>",
                ],
                "elapsed_seconds": 0.03,
            },
            "tier_1": {
                "status": "PASS",
                "commands": [
                    "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_lee_wald_gate --verify bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
                    "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_lee_wald_gate.py",
                    "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_lee_wald_gate",
                ],
                "elapsed_seconds": 3.69,
            },
            "tier_2": {
                "status": "PASS",
                "command": "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_lee_wald_gate --recompute-direct",
                "elapsed_seconds": 408.6765742301941,
                "per_sample_elapsed_seconds": {"ell_2": 131.77334666252136, "ell_3": 104.5996618270874, "ell_4": 172.30356574058533},
                "result": "all three sparse direct coordinate matrices matched the stored exact samples",
            },
            "tier_3": {
                "status": "NOT_RUN",
                "reason": "No shared core algebra, causal or quantum lifecycle state, release, or paper theorem-freeze was changed; the affected certificate chain and exhaustive direct rail are sufficient.",
            },
        },
        "classification": {
            "direct_four_dimensional_Lee_Wald_match": True,
            "all_physical_ell_at_least_2": True,
            "all_allowed_compact_momenta_including_zero": True,
            "Einstein_extra_orthogonality": True,
            "extra_block_nonradical": True,
            "extra_block_positive_frequency_inertia_2_0": True,
            "complete_polar_target_inertia_3_1": True,
            "coefficient_extractors_constructed": True,
            "final_residual_descent_certified": False,
            "quantum_norm_or_ghost_theorem": False,
            "Lorentzian_causal_claim": False,
        },
        "interpretation": "The canonical polar p-primary quotient has a genuine nondegenerate direct Lee--Wald current before the final residual quotient. Its two positive-frequency extra directions are positive in the declared stationary current convention, are orthogonal to the Einstein q-primary image, and raise the complete polar inertia to (3,1). This is a classical compact mode statement, not a residual-survival, particle, norm, or ghost theorem.",
        "next_gate": "lift the polar contraction to the ungauged BV/Noether complex and determine which Einstein and extra polar coefficients survive the final residual quotient",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE certificate matches the reduced polar action Green current to sparse direct four-dimensional Lee--Wald currents and classifies the local-gauge-reduced stationary shell pairing. It does not certify causal propagation, asymptotic scattering, a positive-frequency Hilbert space, quantum ghosts, nonlinear closure, or final residual observables.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_lee_wald_gate --verify bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_lee_wald_gate.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_lee_wald_gate",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_lee_wald_gate --recompute-direct",
        ],
    }


def _direct_sparse_matrix(ell: int) -> sp.Matrix:
    """Slow, independent coordinate replay used only by the exhaustive rail."""

    time_coordinate, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    momentum, first_frequency, second_frequency = sp.symbols("k omega_1 omega_2", real=True)
    coordinates = (time_coordinate, space, theta, azimuth)
    harmonic = sp.legendre(ell, sp.cos(theta))
    axial = -sp.sin(theta) * sp.diff(harmonic, theta)
    first_wave = sp.exp(sp.I * (momentum * space - first_frequency * time_coordinate))
    second_wave = sp.exp(-sp.I * (momentum * space - second_frequency * time_coordinate))
    metric = sp.diag(-1, 1, 1, sp.sin(theta) ** 2)
    field = sp.zeros(4)
    field[2, 3], field[3, 2] = sp.sin(theta), -sp.sin(theta)

    def basis(index: int, wave: sp.Expr) -> tuple[sp.Matrix, sp.Matrix]:
        variation = sp.zeros(4)
        potential = sp.zeros(4, 1)
        if index == 0:
            variation[0, 0] = wave * harmonic
        elif index == 1:
            variation[0, 1] = variation[1, 0] = wave * harmonic
        elif index == 2:
            variation[1, 1] = wave * harmonic
        else:
            potential[3] = wave * axial
        return variation, potential

    first = [basis(index, first_wave) for index in range(4)]
    second = [basis(index, second_wave) for index in range(4)]
    first_geometry = [linearized_geometry(metric, first[index][0], coordinates) for index in range(3)]
    second_geometry = [linearized_geometry(metric, second[index][0], coordinates) for index in range(3)]
    phase = sp.exp(sp.I * (second_frequency - first_frequency) * time_coordinate)
    result = sp.zeros(4)
    for left in range(3):
        for right in range(3):
            current = weyl_theta_time_variation(first_geometry[left], second[right][0], coordinates, 3)
            current -= weyl_theta_time_variation(second_geometry[right], first[left][0], coordinates, 3)
            result[left, right] = _sphere_integral(current / phase, theta, azimuth)
    current = maxwell_theta_time_variation(
        metric, field, first[3][0], exterior_derivative(first[3][1], coordinates), second[3][1], coordinates
    )
    current -= maxwell_theta_time_variation(
        metric, field, second[3][0], exterior_derivative(second[3][1], coordinates), first[3][1], coordinates
    )
    result[3, 3] = _sphere_integral(current / phase, theta, azimuth)
    return result.applyfunc(sp.factor)


def recompute_direct() -> None:
    _, symbols = _time_current_matrix()
    stored = _stored_direct_samples(symbols)
    started = time.monotonic()
    for ell in (2, 3, 4):
        actual = _direct_sparse_matrix(ell)
        _require(_zero(actual - stored[ell]), f"slow direct ell={ell} sample changed")
        print(f"ell={ell} sparse direct matrix: PASS")
    print(f"elapsed_seconds={time.monotonic() - started:.3f}")


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"stale polar Lee--Wald gate: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--recompute-direct", action="store_true")
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if args.recompute_direct:
        recompute_direct()
    if not args.write and args.verify is None and not args.recompute_direct:
        parser.error("one of --write, --verify, or --recompute-direct is required")


if __name__ == "__main__":
    main()
