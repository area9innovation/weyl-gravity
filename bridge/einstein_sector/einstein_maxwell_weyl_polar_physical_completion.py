"""Physical-ring, Einstein-image, and action-normalization completion for polar modes."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_polar_master_complex import _matrix as _source_matrix
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import (
    _action_operator,
    _equation_map,
    _generic_operator,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_physical_completion.schema.json"
OPERATOR_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json"
SOURCE_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_polar_master_complex.json"
PREFLIGHT_CERTIFICATE = ROOT / "bridge/certificates/einstein_weyl_polar_offshell_operator_preflight.json"


class PolarPhysicalCompletionError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolarPhysicalCompletionError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _minor(matrix: sp.MatrixBase, rows: tuple[int, ...], columns: tuple[int, ...]) -> sp.Expr:
    return sp.factor(matrix.extract(rows, columns).det())


def _physical_ring_audit() -> dict[str, Any]:
    hessian, (eigenvalue, momentum, frequency) = _action_operator()
    l, k, w = eigenvalue, momentum, frequency
    extra = sp.factor(w**2 - k**2 - l + sp.Rational(2, 3))
    einstein = sp.factor((w**2 - k**2) ** 2 - 2 * l * (w**2 - k**2) + l * (l - 2))

    _require(hessian[0, 3] == l, "polar I1 unit entry changed")

    i2_labels = [
        ((0, 1), (1, 3)),
        ((0, 1), (2, 3)),
        ((0, 2), (0, 3)),
        ((0, 2), (2, 3)),
        ((1, 2), (1, 2)),
    ]
    i2_coefficients = [
        sp.factor(
            (
                45 * k**2 * l**2 + 12 * k**2 * l + 20 * k**2
                - 120 * l**3 + 75 * l**2 * w**2 + 220 * l**2
                - 196 * l * w**2 + 376 * l - 132 * w**2 + 96
            )
            / (3 * (5 * l + 6) * (9 * l + 2))
        ),
        sp.factor(32 * k * w * (l + 2) * (15 * l + 7) / (3 * (5 * l + 6) * (9 * l + 2))),
        sp.factor(5 * l * (45 * l**2 + 12 * l + 20) / (3 * (5 * l + 6) * (9 * l + 2))),
        sp.factor(
            -(
                180 * k**2 * l**2 + 48 * k**2 * l + 80 * k**2
                - 45 * l**3 + 540 * l**2 * w**2 - 612 * l**2
                + 768 * l * w**2 + 44 * l + 144 * w**2 + 96
            )
            / (3 * (5 * l + 6) * (9 * l + 2))
        ),
        -sp.Rational(8, 3),
    ]
    i2_generators = [sp.factor(_minor(hessian, rows, columns) / l) for rows, columns in i2_labels]
    i2_target = sp.factor(-l * (3 * l - 2) ** 2 * (5 * l + 6) / (6 * (9 * l + 2)))
    _require(
        sp.factor(sum(coefficient * generator for coefficient, generator in zip(i2_coefficients, i2_generators)) - i2_target) == 0,
        "polar I2 Bezout witness changed",
    )

    i3_labels = [
        ((0, 1, 2), (0, 1, 2)),
        ((0, 1, 2), (0, 1, 3)),
        ((0, 1, 2), (1, 2, 3)),
    ]
    shared_i3_polynomial = sp.factor(
        9 * k**2 * l**2 - 30 * k**2 * l + 24 * k**2
        - 9 * l**2 * w**2 + 30 * l * w**2 - 16 * l - 24 * w**2 + 24
    )
    i3_coefficients = [
        sp.factor(
            3 * (l - 2)
            * (3 * k**2 * l - 4 * k**2 + 3 * l**2 - 3 * l * w**2 - 2 * l + 4 * w**2 - 4)
            / (l * (3 * l - 4) ** 2)
        ),
        sp.factor(3 * (l - 2) * shared_i3_polynomial / (8 * l * (3 * l - 4) ** 2)),
        sp.factor(-3 * (l - 2) * shared_i3_polynomial / (8 * l * (3 * l - 4) ** 2)),
    ]
    i3_generators = [
        sp.factor(_minor(hessian, rows, columns) / (3 * l**2 * extra))
        for rows, columns in i3_labels
    ]
    i3_target = sp.factor(3 * (l - 2) ** 3 * (3 * l - 2) ** 2 / (32 * (3 * l - 4) ** 2))
    _require(
        sp.factor(sum(coefficient * generator for coefficient, generator in zip(i3_coefficients, i3_generators)) - i3_target) == 0,
        "polar I3 Bezout witness changed",
    )
    all_three_minors = []
    for rows in itertools.combinations(range(4), 3):
        for columns in itertools.combinations(range(4), 3):
            value = _minor(hessian, rows, columns)
            if value != 0:
                quotient = sp.cancel(value / extra)
                _require(sp.denom(quotient).is_number, f"3-minor lost its p factor: {rows}/{columns}")
                all_three_minors.append(str(sp.factor(quotient)))

    determinant = sp.factor(hessian.det())
    expected_determinant = sp.factor(sp.Rational(9, 16) * l**3 * (l - 2) * extra**2 * einstein)
    _require(determinant == expected_determinant, "polar physical-ring determinant changed")
    resultant = sp.factor(sp.resultant(extra, einstein, w))
    _require(resultant == sp.Rational(4, 81) * (9 * l - 2) ** 2, "polar p-q resultant changed")

    zero_hessian = hessian.subs(k, 0)
    representatives = sp.Matrix([
        [0, -8],
        [1, 0],
        [0, -12 * l],
        [0, 3 * (3 * l - 2)],
    ])
    coefficient_field = sp.QQ.frac_field(l)
    shell_polynomial = sp.Poly(extra.subs(k, 0), w, domain=coefficient_field)

    def shell_reduce(value: sp.Expr) -> sp.Expr:
        numerator, denominator = sp.fraction(sp.cancel(value))
        reduced_numerator = sp.rem(sp.Poly(numerator, w, domain=coefficient_field), shell_polynomial).as_expr()
        reduced_denominator = sp.rem(sp.Poly(denominator, w, domain=coefficient_field), shell_polynomial).as_expr()
        return sp.factor(reduced_numerator / reduced_denominator)

    zero_defect = (zero_hessian * representatives).applyfunc(shell_reduce)
    _require(zero_defect == sp.zeros(4, 2), f"k=0 polar extra representatives failed: {zero_defect}")
    independence_minor = sp.factor(representatives[[1, 3], :].det())
    _require(sp.factor(independence_minor - 3 * (3 * l - 2)) == 0, "k=0 polar representatives lost independence")

    return {
        "physical_coefficient_ring": "R_phys^P=Q[lambda,k,lambda^(-1),(lambda-2)^(-1),(3lambda-2)^(-1),(3lambda-4)^(-1),(5lambda+6)^(-1),(9lambda+2)^(-1),(9lambda-2)^(-1)]",
        "polynomial_variable": "omega",
        "not_inverted": ["k", "omega", "p", "q"],
        "localization_factors_nonzero_for_every_physical_lambda_ge_6": True,
        "I1_unit_entry": "H[0,3]=lambda",
        "I2_Bezout_witness": {
            "normalized_generators": [str(value) for value in i2_generators],
            "minor_labels": [[list(rows), list(columns)] for rows, columns in i2_labels],
            "coefficients": [str(value) for value in i2_coefficients],
            "unit_target": str(i2_target),
            "identity_verified": True,
        },
        "I3_Bezout_witness": {
            "normalization": "minor/(3*lambda^2*p)",
            "normalized_generators": [str(value) for value in i3_generators],
            "minor_labels": [[list(rows), list(columns)] for rows, columns in i3_labels],
            "coefficients": [str(value) for value in i3_coefficients],
            "unit_target": str(i3_target),
            "all_nonzero_three_minors_divisible_by_p": True,
            "number_nonzero_three_minors": len(all_three_minors),
            "identity_verified": True,
        },
        "determinantal_ideals_over_R_phys_P_omega": {
            "I1": "(1)",
            "I2": "(1)",
            "I3": "(p)",
            "I4": "(p^2*q)",
            "invariant_factors_on_every_physical_fiber": ["1", "1", "p", "p*q"],
            "no_k_torsion": True,
        },
        "shells": {"p": str(extra), "q": str(einstein), "resultant": str(resultant)},
        "zero_momentum_audit": {
            "extra_representatives_order_At_B_Ct_U": _matrix_strings(representatives),
            "on_p_shell_defect": _matrix_strings(zero_defect),
            "independence_minor": str(independence_minor),
            "zero_momentum_retained": True,
        },
    }


def _normalization_audit() -> dict[str, Any]:
    a_time, mixed, a_space = sp.symbols("A_t B C_t")
    theta = sp.symbols("theta", real=True)
    background_inverse = sp.diag(-1, 1, 1, sp.csc(theta) ** 2)
    perturbation = sp.zeros(4)
    perturbation[0, 0] = a_time
    perturbation[0, 1] = perturbation[1, 0] = mixed
    perturbation[1, 1] = a_space
    inverse_variation = (-background_inverse * perturbation * background_inverse).applyfunc(sp.factor)
    _require(inverse_variation[0, 0] == -a_time, "00 inverse-metric variation changed")
    _require(inverse_variation[0, 1] == mixed, "01 inverse-metric variation changed")
    _require(inverse_variation[1, 1] == -a_space, "11 inverse-metric variation changed")

    harmonic_checks = []
    for ell in (2, 3, 4):
        harmonic = sp.legendre(ell, sp.cos(theta))
        scalar_norm = sp.integrate(sp.sin(theta) * harmonic**2, (theta, 0, sp.pi))
        axial_norm = sp.integrate(sp.sin(theta) * sp.diff(harmonic, theta) ** 2, (theta, 0, sp.pi))
        eigenvalue = ell * (ell + 1)
        _require(sp.simplify(axial_norm - eigenvalue * scalar_norm) == 0, f"axial harmonic norm failed at ell={ell}")
        harmonic_checks.append({
            "ell": ell,
            "lambda": eigenvalue,
            "scalar_norm_without_2pi": str(scalar_norm),
            "axial_one_form_norm_without_2pi": str(axial_norm),
            "ratio": str(sp.simplify(axial_norm / scalar_norm)),
        })

    tensor, (eigenvalue, _, _) = _generic_operator()
    action, _ = _action_operator()
    weights = sp.diag(-1, 2, -1, 2 * eigenvalue)
    _require((action - weights * tensor[[0, 1, 2, 7], :]).applyfunc(sp.factor) == sp.zeros(4), "action normalization changed")
    return {
        "four_dimensional_first_variation_convention": "delta S_WM=(1/2) integral sqrt(-g) (3B_ab-T_ab) delta g^ab + integral partial_a(sqrt(-g)F^ab) delta A_b",
        "common_rescaling": "the reduced Hessian represents 2*delta S_WM divided by the scalar harmonic norm and circle length",
        "inverse_metric_variation_00_01_11": [str(inverse_variation[0, 0]), str(inverse_variation[0, 1]), str(inverse_variation[1, 1])],
        "symmetric_01_contraction_multiplicity": 2,
        "Maxwell_axial_norm_identity": "integral_S2 X_a X^a=lambda*integral_S2 Y^2",
        "direct_Legendre_checks": harmonic_checks,
        "derived_row_weights": ["-1", "2", "-1", "2*lambda"],
        "row_selection": ["metric_00", "metric_01", "metric_11", "maxwell_axial_density"],
        "normalized_action_matrix": _matrix_strings(action),
        "identity_verified": True,
    }


def _primary_image_audit() -> dict[str, Any]:
    source, (eigenvalue, momentum, frequency) = _source_matrix()
    action, field_map, equation_map, symbols = _equation_map()
    _require(symbols == (eigenvalue, momentum, frequency), "polar symbol convention changed")
    _require((action * field_map - equation_map * source).applyfunc(sp.factor) == sp.zeros(4, 5), "polar chain square changed")
    mass = frequency**2 - momentum**2
    master = sp.Matrix([[mass - eigenvalue, 2 * eigenvalue], [1, mass - eigenvalue]])
    q = sp.factor(master.det())
    expected_q = sp.factor(mass**2 - 2 * eigenvalue * mass + eigenvalue * (eigenvalue - 2))
    _require(q == expected_q, "polar source master characteristic changed")
    _require(master[1, 0] == 1, "polar source master unit entry changed")
    p = sp.factor(mass - eigenvalue + sp.Rational(2, 3))
    resultant = sp.factor(sp.resultant(p, q, frequency))
    _require(resultant == sp.Rational(4, 81) * (9 * eigenvalue - 2) ** 2, "polar primary resultant changed")
    return {
        "source_master_presentation": _matrix_strings(master),
        "source_master_Smith_factors": ["1", str(q)],
        "source_module": "K[omega]/(q)",
        "source_module_K_dimension": 4,
        "target_physical_fiber_primary_decomposition": "(K[omega]/(p))^2 direct_sum K[omega]/(q)",
        "target_q_primary_K_dimension": 4,
        "chain_square": "H_P*S_P=J_P*E_P",
        "chain_square_verified": True,
        "source_solution_map_injective": True,
        "injectivity_inputs": [
            "the ell>=2 polar source gauge slice has no residual smooth gauge",
            "the target field-map kernel is the pure-Weyl vector (-1,0,1,1,0)",
            "the source sphere-tracefree row equals -1 on that vector",
        ],
        "q_annihilates_source_image": True,
        "q_is_a_unit_on_each_p_primary_summand": True,
        "p_q_resultant": str(resultant),
        "source_image_lies_in_complete_q_primary_summand": True,
        "dimension_equality_forces_surjectivity_onto_q_primary": True,
        "Einstein_image_equals_complete_q_primary_summand": True,
        "canonical_extra_polar_quotient_on_every_physical_fiber": "(K[omega]/(p))^2",
    }


def build_certificate() -> dict[str, Any]:
    operator = json.loads(OPERATOR_CERTIFICATE.read_text(encoding="utf-8"))
    source = json.loads(SOURCE_CERTIFICATE.read_text(encoding="utf-8"))
    preflight = json.loads(PREFLIGHT_CERTIFICATE.read_text(encoding="utf-8"))
    _require(operator["result_id"] == "EINSTEIN_MAXWELL_WEYL_POLAR_FULL_TENSOR", "target operator input changed")
    _require(operator["classification"]["polar_chain_map_constructed"] is True, "target chain square input changed")
    _require(source["result_id"] == "COMPACT_EM_POLAR_MASTER_COMPLEX", "source polar module input changed")
    _require(source["classification"]["ell_ge2_gauge_complete"] is True, "source gauge theorem changed")
    _require(preflight["target_Weyl_gauge_contraction"]["induced_map_on_Einstein_solution_kernel_injective"] is True, "polar injection input changed")
    return {
        "schema": "einstein-maxwell-weyl-polar-physical-completion-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_POLAR_PHYSICAL_COMPLETION",
        "result_state": "POLAR_PHYSICAL_RING_EINSTEIN_PRIMARY_IMAGE_AND_ACTION_NORMALIZATION_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_POLAR_ALL_PHYSICAL_ELL_K_OPERATOR_MODULE",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                str(path.relative_to(ROOT)): _sha256(path)
                for path in (OPERATOR_CERTIFICATE, SOURCE_CERTIFICATE, PREFLIGHT_CERTIFICATE)
            },
        },
        "domain": "polar ell>=2 Weyl-Maxwell coefficient complex on the fixed compact magnetic bundle, every allowed compact momentum including k=0, before ungauged and final residual descent",
        "action_normalization": _normalization_audit(),
        "physical_ring": _physical_ring_audit(),
        "Einstein_primary_image": _primary_image_audit(),
        "classification": {
            "action_row_weights_derived_from_four_dimensional_variation": True,
            "formal_self_adjointness_is_not_the_sole_normalization_argument": True,
            "physical_ring_determinantal_ideals_certified": True,
            "all_physical_lambda_and_compact_momenta_including_zero_certified": True,
            "Einstein_image_equals_complete_q_primary_summand": True,
            "canonical_extra_polar_quotient_two_p_summands": True,
            "polar_extra_Lee_Wald_current_certified": False,
            "ungauged_BV_lift_certified": False,
            "final_residual_descent_certified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The polar target contains exactly the complete Einstein q-primary module plus two additional p-primary cyclic summands on every physical ell>=2 compact-momentum fiber. The action normalization follows directly from the four-dimensional variational convention and harmonic norms. This is an off-shell coefficient/module theorem, not yet a statement about the polar extra Lee-Wald pairing or residual physical states.",
        "next_gate": "compute the direct four-dimensional polar extra Lee-Wald current and coefficient extractors, then lift the polynomial square to the ungauged Noether/BV complex and perform final residual descent",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC/REDUCED-MODE certificate closes physical specialization, primary-image identification, and reduced action normalization for polar ell>=2. It does not construct the polar extra Lee-Wald current, an ungauged BV chain map, final residual states, causal boundary data, scattering, or a quantum norm/ghost theorem.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_physical_completion --verify bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_physical_completion.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_physical_completion",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"stale polar physical-completion certificate: {path}")


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
