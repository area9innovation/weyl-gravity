"""Exact generic axial Weyl--Maxwell operator and extra solution module."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator_module_preflight.json"
FULL_TENSOR = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_full_tensor.json"
SOURCE_COMPLEX = ROOT / "bridge/certificates/einstein_maxwell_axial_master_complex.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_operator.schema.json"


class AxialOperatorError(RuntimeError):
    """Raised when an exact generic axial operator identity fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialOperatorError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero(matrix: sp.MatrixBase) -> bool:
    return matrix.applyfunc(lambda value: sp.factor(sp.expand(value))) == sp.zeros(matrix.rows, matrix.cols)


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _generic_rows() -> tuple[dict[str, sp.Expr], dict[str, sp.Symbol]]:
    eigenvalue, momentum, frequency = sp.symbols("lambda k omega", real=True)
    h_time, h_space, q_time, q_space = sp.symbols("h_t h_x q_t q_x")
    rows = {
        "metric_t": -(
            3 * h_time * momentum**4
            - 3 * h_time * momentum**2 * frequency**2
            + (6 * eigenvalue - 2) * h_time * momentum**2
            - 3 * (eigenvalue - 2) * h_time * frequency**2
            + eigenvalue * (3 * eigenvalue - 8) * h_time
            + 3 * h_space * momentum**3 * frequency
            - 3 * h_space * momentum * frequency**3
            + (3 * eigenvalue + 4) * h_space * momentum * frequency
            - 4 * q_time
        )
        / 4,
        "metric_x": (
            3 * h_time * momentum**3 * frequency
            - 3 * h_time * momentum * frequency**3
            + (3 * eigenvalue + 4) * h_time * momentum * frequency
            + 3 * h_space * momentum**2 * frequency**2
            - 3 * (eigenvalue - 2) * h_space * momentum**2
            - 3 * h_space * frequency**4
            + (6 * eigenvalue - 2) * h_space * frequency**2
            - eigenvalue * (3 * eigenvalue - 8) * h_space
            + 4 * q_space
        )
        / 4,
        "metric_angular": -(
            h_time * frequency + h_space * momentum
        ) * (3 * momentum**2 - 3 * frequency**2 + 3 * eigenvalue - 2) / 2,
        "maxwell_t": eigenvalue * h_time + (momentum**2 + eigenvalue) * q_time + momentum * frequency * q_space,
        "maxwell_x": -eigenvalue * h_space + momentum * frequency * q_time + (frequency**2 - eigenvalue) * q_space,
        "maxwell_angular": h_time * frequency + h_space * momentum + frequency * q_time + momentum * q_space,
    }
    return rows, {
        "lambda": eigenvalue,
        "k": momentum,
        "omega": frequency,
        "h_t": h_time,
        "h_x": h_space,
        "q_t": q_time,
        "q_x": q_space,
    }


def _sample_reconstruction(full_tensor: dict[str, Any], rows: dict[str, sp.Expr], symbols: dict[str, sp.Symbol]) -> dict[str, Any]:
    eigenvalue = symbols["lambda"]
    sample_checks = {}
    for ell in (2, 3, 4):
        sample = full_tensor["samples"][str(ell)]
        expected = {name: sp.sympify(value, locals=symbols) for name, value in sample["rows"].items()}
        actual = {name: sp.factor(value.subs(eigenvalue, ell * (ell + 1))) for name, value in rows.items()}
        for name in rows:
            _require(sp.factor(expected[name] - actual[name]) == 0, f"ell={ell} {name} reconstruction failed")
        sample_checks[str(ell)] = "all six rows exact"
    return {
        "SO3_equivariant_degree_bound": "a fourth-order natural tensor operator on scalar-derived axial harmonics is polynomial of degree at most two in lambda",
        "interpolation_nodes": [6, 12, 20],
        "exact_full_tensor_checks": sample_checks,
        "unique_degree_at_most_two_reconstruction": True,
        "branch_substitution_used": False,
    }


def _operator_algebra(rows: dict[str, sp.Expr], symbols: dict[str, sp.Symbol]) -> dict[str, Any]:
    eigenvalue, momentum, frequency = symbols["lambda"], symbols["k"], symbols["omega"]
    coefficients = sp.Matrix([symbols["h_t"], symbols["h_x"], symbols["q_t"], symbols["q_x"]])
    equation_vector = sp.Matrix([rows["metric_t"], rows["metric_x"], rows["maxwell_t"], rows["maxwell_x"]])
    row_density = sp.diag(eigenvalue, -eigenvalue, 1, 1)
    hessian = (row_density * equation_vector).jacobian(coefficients).applyfunc(sp.factor)
    adjoint_hessian = hessian.subs({frequency: -frequency, momentum: -momentum}, simultaneous=True).T
    _require(_zero(hessian - adjoint_hessian), "gauge-fixed formal adjoint identity failed")

    determinant = sp.factor(hessian.det())
    einstein_factor = sp.factor((frequency**2 - momentum**2 - eigenvalue) ** 2 - 2 * eigenvalue)
    extra_factor = sp.factor(frequency**2 - momentum**2 - eigenvalue + sp.Rational(2, 3))
    expected_determinant = sp.factor(
        eigenvalue**3 * (eigenvalue - 2) * 9 * extra_factor**2 * einstein_factor / 16
    )
    _require(sp.factor(determinant - expected_determinant) == 0, "generic target determinant changed")

    coefficient_field = sp.QQ.frac_field(eigenvalue, momentum)
    determinantal_divisors = [sp.Integer(1)]
    for size in range(1, 5):
        gcd_polynomial: sp.Poly | None = None
        for row_indices in itertools.combinations(range(4), size):
            for column_indices in itertools.combinations(range(4), size):
                minor = hessian.extract(row_indices, column_indices).det()
                polynomial = sp.Poly(sp.cancel(minor), frequency, domain=coefficient_field)
                if polynomial.is_zero:
                    continue
                gcd_polynomial = polynomial if gcd_polynomial is None else sp.gcd(gcd_polynomial, polynomial)
                if gcd_polynomial.degree() == 0:
                    break
            if gcd_polynomial is not None and gcd_polynomial.degree() == 0:
                break
        _require(gcd_polynomial is not None, f"all size-{size} minors vanished")
        determinantal_divisors.append(sp.factor(gcd_polynomial.monic().as_expr()))
    invariant_factors = [
        sp.factor(sp.cancel(determinantal_divisors[index] / determinantal_divisors[index - 1]))
        for index in range(1, 5)
    ]
    expected_invariants = [1, 1, extra_factor, sp.factor(extra_factor * einstein_factor)]
    _require(all(sp.factor(actual - expected) == 0 for actual, expected in zip(invariant_factors, expected_invariants)), "Smith invariant factors changed")

    return {
        "coefficient_order": ["H_t", "H_x", "Q_t", "Q_x"],
        "equation_row_order": ["lambda*metric_t", "-lambda*metric_x", "maxwell_t", "maxwell_x"],
        "row_density_matrix": _matrix_strings(row_density),
        "gauge_fixed_Hessian_operator": _matrix_strings(hessian),
        "formal_adjoint_involution": "(omega,k)->(-omega,-k) followed by transpose",
        "formal_self_adjoint": True,
        "determinant": str(determinant),
        "monic_extra_factor_p": str(extra_factor),
        "Einstein_master_factor_q": str(einstein_factor),
        "determinantal_divisors": [str(value) for value in determinantal_divisors[1:]],
        "Smith_invariant_factors_over_F_omega": [str(value) for value in invariant_factors],
        "coefficient_field": "F=Frac(Q(lambda,k)); polynomial variable omega (equivalently D after omega=iD)",
    }


def _ungauged_noether_lift(rows: dict[str, sp.Expr], symbols: dict[str, sp.Symbol]) -> dict[str, Any]:
    frequency, momentum = symbols["omega"], symbols["k"]
    eigenvalue = symbols["lambda"]
    coefficients = sp.Matrix([symbols["h_t"], symbols["h_x"], symbols["q_t"], symbols["q_x"]])
    hessian = sp.Matrix(
        [
            eigenvalue * rows["metric_t"],
            -eigenvalue * rows["metric_x"],
            rows["maxwell_t"],
            rows["maxwell_x"],
        ]
    ).jacobian(coefficients)
    gauge = sp.Matrix(
        [
            [-sp.I * frequency, 0],
            [sp.I * momentum, 0],
            [2, 0],
            [0, -sp.I * frequency],
            [0, sp.I * momentum],
            [1, 1],
        ]
    )
    projection = sp.Matrix(
        [
            [1, 0, sp.I * frequency / 2, 0, 0, 0],
            [0, 1, -sp.I * momentum / 2, 0, 0, 0],
            [0, 0, -sp.I * frequency / 2, 1, 0, sp.I * frequency],
            [0, 0, sp.I * momentum / 2, 0, 1, -sp.I * momentum],
        ]
    )
    _require(_zero(projection * gauge), "Fourier gauge invariants changed")
    projection_adjoint = projection.subs({frequency: -frequency, momentum: -momentum}, simultaneous=True).T
    ungauged = (projection_adjoint * hessian * projection).applyfunc(sp.factor)
    gauge_adjoint = gauge.subs({frequency: -frequency, momentum: -momentum}, simultaneous=True).T
    _require(_zero(ungauged * gauge), "right Noether identity failed")
    _require(_zero(gauge_adjoint * ungauged), "left Noether identity failed")
    ungauged_adjoint = ungauged.subs({frequency: -frequency, momentum: -momentum}, simultaneous=True).T
    _require(_zero(ungauged - ungauged_adjoint), "ungauged formal adjoint identity failed")
    return {
        "ungauged_coefficient_order": ["h_t", "h_x", "h_2", "q_t", "q_x", "b"],
        "gauge_parameter_order": ["s", "r"],
        "Fourier_gauge_map": _matrix_strings(gauge),
        "Fourier_invariant_projection": _matrix_strings(projection),
        "ungauged_Hessian_operator": _matrix_strings(ungauged),
        "identities": {
            "K_G": "0",
            "L_ungauged_G": "0",
            "G_dagger_L_ungauged": "0",
            "L_ungauged_dagger": "L_ungauged",
        },
        "Noether_identities_verified": True,
        "formal_self_adjoint_verified": True,
        "no_D_or_k_inverse": True,
    }


def _source_and_extra_modules(rows: dict[str, sp.Expr], symbols: dict[str, sp.Symbol]) -> dict[str, Any]:
    eigenvalue, momentum, frequency = symbols["lambda"], symbols["k"], symbols["omega"]
    h_time, h_space, q_time, q_space = symbols["h_t"], symbols["h_x"], symbols["q_t"], symbols["q_x"]
    mass = sp.symbols("s", real=True)
    H, Q = sp.symbols("H Q")
    transverse = {h_time: momentum * H, h_space: -frequency * H, q_time: momentum * Q, q_space: -frequency * Q}
    source_einstein = (eigenvalue - mass) * H + 2 * Q
    source_maxwell = eigenvalue * H + (eigenvalue - mass) * Q
    target_polynomial = (3 * eigenvalue - 2 - 3 * mass) * source_einstein - 6 * source_maxwell
    mass_shell_polynomial = sp.Poly(frequency**2 - momentum**2 - mass, frequency)
    def reduce_mass_shell(expression: sp.Expr) -> sp.Expr:
        return sp.factor(sp.rem(sp.Poly(sp.expand(expression), frequency), mass_shell_polynomial).as_expr())

    metric_t_image = reduce_mass_shell(rows["metric_t"].subs(transverse))
    metric_x_image = reduce_mass_shell(rows["metric_x"].subs(transverse))
    _require(sp.factor(metric_t_image + momentum * target_polynomial / 4) == 0, "source metric-t image identity failed")
    _require(sp.factor(metric_x_image - frequency * target_polynomial / 4) == 0, "source metric-x image identity failed")
    _require(sp.factor(rows["metric_angular"].subs(transverse)) == 0, "source angular image identity failed")

    extra_shell = frequency**2 - momentum**2 - eigenvalue + sp.Rational(2, 3)
    extra_representatives = [
        sp.Matrix([-(momentum**2 + eigenvalue), momentum * frequency, eigenvalue, 0]),
        sp.Matrix([-momentum * frequency, momentum**2 - sp.Rational(2, 3), 0, eigenvalue]),
    ]
    coefficient_vector = sp.Matrix([h_time, h_space, q_time, q_space])
    normalized_equations = sp.Matrix([
        eigenvalue * rows["metric_t"],
        -eigenvalue * rows["metric_x"],
        rows["maxwell_t"],
        rows["maxwell_x"],
    ])
    hessian = normalized_equations.jacobian(coefficient_vector)
    divisor = sp.Poly(extra_shell, frequency)
    for index, representative in enumerate(extra_representatives):
        image = hessian * representative
        for value in image:
            remainder = sp.rem(sp.Poly(sp.factor(value), frequency), divisor).as_expr()
            _require(sp.factor(remainder) == 0, f"extra representative {index} failed")

    resultant_locus = sp.factor(sp.Rational(4, 9) - 2 * eigenvalue)
    return {
        "mass_variable": "s=omega^2-k^2",
        "source_master_rows": ["E=(lambda-s)H+2Q", "M=lambda*H+(lambda-s)Q"],
        "target_source_image_identity": "P_W=(3*lambda-2-3*s)*E-6*M",
        "source_image_annihilation_verified": True,
        "generic_extra_support": "p=s-lambda+2/3=0",
        "extra_representatives_order_Ht_Hx_Qt_Qx": [[str(value) for value in vector] for vector in extra_representatives],
        "two_independent_extra_cyclic_summands": True,
        "generic_localized_target_module": "F[omega]/(p) + F[omega]/(p*q)",
        "CRT_decomposition_away_from_resultant": "(F[omega]/(p))^2 + F[omega]/(q)",
        "canonical_extra_quotient_away_from_resultant": "Q_extra_ax=(F[omega]/(p))^2",
        "p_q_resultant_locus": str(resultant_locus) + "=0, equivalently lambda=2/9",
        "physical_ell_ge_2_disjoint_from_resultant": True,
        "geometric_multiplicity_on_generic_extra_root": 2,
        "Jordan_enhancement_on_physical_ell_ge_2": False,
    }


def build_certificate() -> dict[str, Any]:
    preflight = _load(PREFLIGHT)
    full_tensor = _load(FULL_TENSOR)
    source = _load(SOURCE_COMPLEX)
    _require(preflight["result_id"] == "EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR_MODULE_PREFLIGHT", "preflight changed")
    _require(full_tensor["result_id"] == "EINSTEIN_MAXWELL_WEYL_AXIAL_ELL2_FULL_TENSOR", "full-tensor fixture changed")
    _require(source["result_id"] == "COMPACT_EM_AXIAL_MASTER_COMPLEX", "source axial complex changed")
    rows, symbols = _generic_rows()
    reconstruction = _sample_reconstruction(full_tensor, rows, symbols)
    operator = _operator_algebra(rows, symbols)
    noether = _ungauged_noether_lift(rows, symbols)
    modules = _source_and_extra_modules(rows, symbols)
    return {
        "schema": "einstein-maxwell-weyl-axial-operator-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR",
        "result_state": "GENERIC_AXIAL_OPERATOR_NOETHER_SMITH_AND_EXTRA_SOLUTION_MODULE_CERTIFIED_GREEN_AND_PAIRING_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_GENERIC_AXIAL_TARGET_OPERATOR_AND_EXTRA_MODULE",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                str(path.relative_to(ROOT)): _sha256(path)
                for path in (PREFLIGHT, FULL_TENSOR, SOURCE_COMPLEX)
            },
        },
        "domain": "generic axial ell>=2 fixed-bundle coefficient complex on R_t x S1 x S2, before final residual quotient, over exact symbolic lambda and k",
        "generic_equation_rows": {name: str(sp.factor(value)) for name, value in rows.items()},
        "spectral_polynomial_reconstruction": reconstruction,
        "operator_algebra": operator,
        "ungauged_Noether_lift": noether,
        "source_and_extra_modules": modules,
        "denominator_and_exceptional_loci": {
            "inverted_by_gauge_contraction": ["2"],
            "generic_coefficient_field_localizes": ["nonzero polynomials in lambda and k used by Smith reduction"],
            "physical_domain": "lambda=ell(ell+1)>=6; real discrete k",
            "separate_strata_still_required": ["lambda=0", "lambda=2", "lambda=2/9 algebraic p-q collision"],
            "k_zero_retained": True,
            "omega_zero_not_inverted": True,
        },
        "rails": {
            "target_operator_inserted": True,
            "ell2_independent_full_tensor_replay_passed": True,
            "ell3_ell4_exact_reconstruction_samples_passed": True,
            "reduced_formal_Hessian_verified": True,
            "direct_second_variation_of_four_dimensional_action_verified": False,
            "Noether_identities_verified": True,
            "formal_adjoint_verified": True,
            "source_image_annihilation_replayed": True,
            "Smith_module_and_extra_quotient_verified": True,
            "off_shell_local_Green_current_verified": False,
            "full_Einstein_extra_Lee_Wald_matrix_verified": False,
        },
        "classification": {
            "generic_axial_target_operator_constructed": True,
            "Einstein_solution_module_is_a_proper_submodule": True,
            "canonical_generic_axial_extra_solution_module_computed": True,
            "two_extra_algebraic_polarizations": True,
            "extra_presymplectic_nonradical_or_norm_certified": False,
            "extra_particle_certified": False,
            "Lorentzian_causal_claim": False,
            "quantum_claim": False,
        },
        "interpretation": "The generic axial Weyl-Maxwell tangent is now strictly larger than the Einstein-Maxwell tangent as an exact reduced differential module. Away from the recorded p-q collision, the canonical quotient by the Einstein image is two copies of the extra quadratic factor p=omega^2-k^2-lambda+2/3. These are algebraic solution polarizations before the residual quotient, not yet particles: their Lee-Wald pairing, radical status, sign, and causal boundary admissibility remain uncomputed.",
        "next_gate": "derive the off-shell local Green current and direct four-dimensional action Hessian, then compute the complete Einstein/extra Lee-Wald matrix and decide whether either extra cyclic summand is nonradical on the declared compact phase space",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem certifies the generic axial operator, Noether lift, exact invariant factors, source inclusion, and canonical generic extra solution quotient. It does not certify a local Green current, covariant phase-space norm, positive-frequency Hilbert space, causal propagation, boundary selection, scattering state, or quantum particle.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_operator --verify bridge/certificates/einstein_maxwell_weyl_axial_operator.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_axial_operator.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_operator",
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_ell2_full_tensor --verify bridge/certificates/einstein_maxwell_weyl_axial_ell2_full_tensor.json",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"stale axial operator certificate: {path}")


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
