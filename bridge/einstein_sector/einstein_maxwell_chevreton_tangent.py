"""Full on-shell tangent inclusion via the Einstein--Maxwell Bach factorization.

For source-free four-dimensional Einstein--Maxwell solutions, the Bach tensor
differs from its cosmological Maxwell-stress term by the convention-adjusted
trace of the Chevreton tensor.  That trace is quadratic in nabla F.  The
certified product background has parallel Maxwell flux, so the Chevreton term
has vanishing value and first variation.  The tuned product incidence then
promotes the principal tangent inclusion to the complete on-shell linearized
equations, while leaving the off-shell BV chain map and second order open.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
BACKGROUND = ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json"
PREFLIGHT = ROOT / "bridge/certificates/einstein_maxwell_product_tangent_preflight.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_chevreton_tangent.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_chevreton_tangent.schema.json"


class ChevretonTangentError(RuntimeError):
    """Raised when an imported gate or exact tangent identity fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ChevretonTangentError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [
        [str(sp.factor(matrix[row, column])) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def _radion_fixture() -> dict[str, Any]:
    """Direct coordinate check of one nontrivial full lower-order tangent."""

    epsilon = sp.symbols("epsilon")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    n = 4

    def linear(expression: sp.Expr) -> sp.Expr:
        return sp.simplify(
            expression.subs(epsilon, 0)
            + epsilon * sp.diff(expression, epsilon).subs(epsilon, 0)
        )

    sine = sp.sin(theta)
    # phi=1 and psi=t^2 solve the complete spherically symmetric linearized
    # Einstein--Maxwell equations at k2=1, kappa=1, Lambda=1/2, P=1.
    metric = sp.diag(
        -(1 + 2 * epsilon * time**2),
        1 + 2 * epsilon * time**2,
        1 + 2 * epsilon,
        (1 + 2 * epsilon) * sine**2,
    )
    inverse = sp.diag(
        -(1 - 2 * epsilon * time**2),
        1 - 2 * epsilon * time**2,
        1 - 2 * epsilon,
        (1 - 2 * epsilon) / sine**2,
    )

    connection = [
        [[sp.S.Zero for _ in range(n)] for _ in range(n)] for _ in range(n)
    ]
    for target in range(n):
        for first in range(n):
            for second in range(n):
                connection[target][first][second] = linear(
                    sum(
                        inverse[target, index]
                        * (
                            sp.diff(metric[index, second], coordinates[first])
                            + sp.diff(metric[index, first], coordinates[second])
                            - sp.diff(metric[first, second], coordinates[index])
                        )
                        for index in range(n)
                    )
                    / 2
                )

    riemann = [
        [
            [[sp.S.Zero for _ in range(n)] for _ in range(n)]
            for _ in range(n)
        ]
        for _ in range(n)
    ]
    for target in range(n):
        for vector in range(n):
            for first in range(n):
                for second in range(n):
                    riemann[target][vector][first][second] = linear(
                        sp.diff(
                            connection[target][second][vector], coordinates[first]
                        )
                        - sp.diff(
                            connection[target][first][vector], coordinates[second]
                        )
                        + sum(
                            connection[target][first][middle]
                            * connection[middle][second][vector]
                            - connection[target][second][middle]
                            * connection[middle][first][vector]
                            for middle in range(n)
                        )
                    )

    ricci = sp.zeros(n)
    for first in range(n):
        for second in range(n):
            ricci[first, second] = linear(
                sum(
                    riemann[index][first][index][second] for index in range(n)
                )
            )
    scalar = linear(
        sum(
            inverse[first, second] * ricci[first, second]
            for first in range(n)
            for second in range(n)
        )
    )
    schouten = sp.zeros(n)
    for first in range(n):
        for second in range(n):
            schouten[first, second] = linear(
                (ricci[first, second] - scalar * metric[first, second] / 6) / 2
            )

    weyl = [
        [
            [[sp.S.Zero for _ in range(n)] for _ in range(n)]
            for _ in range(n)
        ]
        for _ in range(n)
    ]
    for first in range(n):
        for second in range(n):
            for third in range(n):
                for fourth in range(n):
                    lowered_riemann = linear(
                        sum(
                            metric[first, target]
                            * riemann[target][second][third][fourth]
                            for target in range(n)
                        )
                    )
                    weyl[first][second][third][fourth] = linear(
                        lowered_riemann
                        - (
                            metric[first, third] * schouten[fourth, second]
                            - metric[first, fourth] * schouten[third, second]
                            - metric[second, third] * schouten[fourth, first]
                            + metric[second, fourth] * schouten[third, first]
                        )
                    )

    derivative_schouten = [
        [[sp.S.Zero for _ in range(n)] for _ in range(n)] for _ in range(n)
    ]
    for derivative in range(n):
        for first in range(n):
            for second in range(n):
                derivative_schouten[derivative][first][second] = linear(
                    sp.diff(schouten[first, second], coordinates[derivative])
                    - sum(
                        connection[index][derivative][first]
                        * schouten[index, second]
                        + connection[index][derivative][second]
                        * schouten[first, index]
                        for index in range(n)
                    )
                )

    second_schouten = [
        [
            [[sp.S.Zero for _ in range(n)] for _ in range(n)]
            for _ in range(n)
        ]
        for _ in range(n)
    ]
    for outer in range(n):
        for inner in range(n):
            for first in range(n):
                for second in range(n):
                    second_schouten[outer][inner][first][second] = linear(
                        sp.diff(
                            derivative_schouten[inner][first][second],
                            coordinates[outer],
                        )
                        - sum(
                            connection[index][outer][inner]
                            * derivative_schouten[index][first][second]
                            + connection[index][outer][first]
                            * derivative_schouten[inner][index][second]
                            + connection[index][outer][second]
                            * derivative_schouten[inner][first][index]
                            for index in range(n)
                        )
                    )

    schouten_up = sp.zeros(n)
    for first in range(n):
        for second in range(n):
            schouten_up[first, second] = linear(
                sum(
                    inverse[first, left]
                    * inverse[second, right]
                    * schouten[left, right]
                    for left in range(n)
                    for right in range(n)
                )
            )
    bach = sp.zeros(n)
    for first in range(n):
        for second in range(n):
            laplacian = sum(
                inverse[outer, inner]
                * second_schouten[outer][inner][first][second]
                for outer in range(n)
                for inner in range(n)
            )
            mixed = sum(
                inverse[outer, inner]
                * second_schouten[outer][first][second][inner]
                for outer in range(n)
                for inner in range(n)
            )
            curvature = sum(
                schouten_up[inner, outer]
                * weyl[first][inner][second][outer]
                for inner in range(n)
                for outer in range(n)
            )
            bach[first, second] = linear(laplacian - mixed + curvature)

    field_strength = sp.zeros(n)
    field_strength[2, 3] = sine
    field_strength[3, 2] = -sine
    field_squared = linear(
        sum(
            inverse[first, third]
            * inverse[second, fourth]
            * field_strength[first, second]
            * field_strength[third, fourth]
            for first in range(n)
            for second in range(n)
            for third in range(n)
            for fourth in range(n)
        )
    )
    stress = sp.zeros(n)
    for first in range(n):
        for second in range(n):
            stress[first, second] = linear(
                sum(
                    field_strength[first, left]
                    * inverse[left, right]
                    * field_strength[second, right]
                    for left in range(n)
                    for right in range(n)
                )
                - metric[first, second] * field_squared / 4
            )

    einstein_residual = sp.zeros(n)
    weyl_residual = sp.zeros(n)
    for first in range(n):
        for second in range(n):
            einstein_residual[first, second] = linear(
                ricci[first, second]
                - scalar * metric[first, second] / 2
                + metric[first, second] / 2
                - stress[first, second]
            )
            weyl_residual[first, second] = linear(
                3 * bach[first, second] - stress[first, second]
            )

    # Maxwell divergence in density form.  The determinant is known exactly
    # to first order for this diagonal metric.
    volume_density = sine * (1 + 2 * epsilon * time**2 + 2 * epsilon)
    field_up = sp.zeros(n)
    for first in range(n):
        for second in range(n):
            field_up[first, second] = linear(
                sum(
                    inverse[first, left]
                    * inverse[second, right]
                    * field_strength[left, right]
                    for left in range(n)
                    for right in range(n)
                )
            )
    maxwell_divergence = sp.Matrix(
        [
            linear(
                sum(
                    sp.diff(
                        volume_density * field_up[first, second],
                        coordinates[first],
                    )
                    for first in range(n)
                )
                / volume_density
            )
            for second in range(n)
        ]
    )

    background_bach = bach.subs(epsilon, 0).applyfunc(sp.simplify)
    background_stress = stress.subs(epsilon, 0).applyfunc(sp.simplify)
    linearized_einstein = einstein_residual.diff(epsilon).subs(epsilon, 0).applyfunc(sp.simplify)
    linearized_weyl = weyl_residual.diff(epsilon).subs(epsilon, 0).applyfunc(sp.simplify)
    linearized_maxwell = maxwell_divergence.diff(epsilon).subs(epsilon, 0).applyfunc(sp.simplify)
    _require(3 * background_bach == background_stress, "fixture background Weyl equation failed")
    _require(linearized_einstein == sp.zeros(4), "radion Einstein tangent failed")
    _require(linearized_weyl == sp.zeros(4), "radion Weyl tangent failed")
    _require(linearized_maxwell == sp.zeros(4, 1), "radion Maxwell tangent failed")
    _require(
        linear(
            sum(
                inverse[first, second] * bach[first, second]
                for first in range(n)
                for second in range(n)
            )
        )
        == 0,
        "fixture Bach trace failed",
    )

    return {
        "metric_perturbation": "h=2*t^2*(-dt^2+dx^2)+2*dOmega_2^2",
        "radion": "phi=1",
        "base_conformal_mode": "psi=t^2",
        "maxwell_perturbation": "delta F=0 with fixed magnetic flux",
        "background_bach": _matrix_strings(background_bach),
        "background_stress": _matrix_strings(background_stress),
        "linearized_einstein_residual": _matrix_strings(linearized_einstein),
        "linearized_weyl_residual": _matrix_strings(linearized_weyl),
        "linearized_maxwell_residual": [str(value) for value in linearized_maxwell],
        "full_lower_order_coordinate_check": "PASS",
    }


def build_certificate() -> dict[str, Any]:
    background = _load(BACKGROUND)
    preflight = _load(PREFLIGHT)
    _require(
        background.get("result_id") == "EINSTEIN_MAXWELL_PRODUCT_INCIDENCE"
        and background.get("claim_flags", {}).get("exact_nonlinear_background_incidence_certified") is True,
        "common-background import gate changed",
    )
    _require(
        preflight.get("result_id") == "EINSTEIN_MAXWELL_PRODUCT_TANGENT_PREFLIGHT"
        and preflight.get("classification", {}).get("principal_bv_chain_map_constructed") is True
        and preflight.get("classification", {}).get("full_curved_tangent_chain_map_constructed") is False,
        "principal tangent preflight import gate changed",
    )

    alpha_b, kappa, cosmological, curvature_sum = sp.symbols(
        "alpha_B kappa Lambda K", nonzero=True, real=True
    )
    tuning = {
        curvature_sum: 2 * cosmological,
        alpha_b: 3 / (kappa * curvature_sum),
    }
    stress_coefficient = sp.factor(
        alpha_b * 2 * kappa * cosmological / 3
    ).subs(tuning)
    stress_coefficient = sp.simplify(stress_coefficient.subs(curvature_sum, 2 * cosmological))
    _require(stress_coefficient == 1, "Chevreton tangent tuning changed")

    epsilon, jet_one, jet_two = sp.symbols("epsilon J1 J2", real=True)
    quadratic_chevreton = (epsilon * jet_one) ** 2 + 3 * (
        epsilon * jet_one
    ) * (epsilon * jet_two) + 2 * (epsilon * jet_two) ** 2
    first_variation = sp.diff(quadratic_chevreton, epsilon).subs(epsilon, 0)
    second_variation = sp.factor(
        sp.diff(quadratic_chevreton, epsilon, 2).subs(epsilon, 0)
    )
    _require(first_variation == 0, "quadratic Chevreton first variation changed")
    _require(second_variation != 0, "quadratic Chevreton second-order gate vanished")

    fixture = _radion_fixture()
    return {
        "schema": "einstein-maxwell-chevreton-tangent-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_CHEVRETON_TANGENT",
        "result_state": "FULL_ON_SHELL_LINEAR_TANGENT_INCLUSION_CERTIFIED_OFF_SHELL_BV_AND_NONLINEAR_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                "common_background": {
                    "path": str(BACKGROUND.relative_to(ROOT)),
                    "sha256": _sha256(BACKGROUND),
                },
                "principal_tangent_preflight": {
                    "path": str(PREFLIGHT.relative_to(ROOT)),
                    "sha256": _sha256(PREFLIGHT),
                },
            },
            "primary_literature_identity": {
                "authors": "G. Bergqvist and I. Eriksson",
                "title": "The Chevreton Tensor and Einstein-Maxwell Spacetimes Conformal to Einstein Spaces",
                "arxiv": "gr-qc/0703073v2",
                "journal_doi": "10.1088/0264-9381/24/13/018",
                "source_equation": "Eq. (66), translated to the repository curvature, stress, and coupling conventions",
            },
        },
        "on_shell_factorization": {
            "domain": "four-dimensional source-free Einstein--Maxwell equations with cosmological constant Lambda",
            "repository_convention_identity": "B_mn-(2*kappa*Lambda/3)T_mn=C_Ch_mn",
            "C_Ch_definition": "convention-adjusted trace of the Chevreton electromagnetic superenergy tensor",
            "structural_property": "C_Ch is homogeneous quadratic in nabla F",
            "background_property": "nabla Fbar=0 because the aligned factor volume forms are parallel",
            "background_consequence": "C_Ch(gbar,Fbar)=0",
            "linearized_consequence": "delta C_Ch=0 for arbitrary (h,a) because the derivative of a quadratic form vanishes at nabla Fbar=0",
        },
        "tuning_deduction": {
            "product_relations": [
                "k_1+k_2=2*Lambda",
                "alpha_B*kappa*(k_1+k_2)=3",
            ],
            "coefficient": "alpha_B*(2*kappa*Lambda/3)=1",
            "symbolic_check": str(stress_coefficient),
            "linearized_metric_identity_on_einstein_maxwell_shell": "alpha_B*delta B_mn-delta T_mn=0",
            "linearized_maxwell_identity": "the source-free Maxwell equation is identical in both theories",
        },
        "theorem": {
            "statement": "Every solution of the complete linearized source-free Einstein--Maxwell equations at the certified parallel-flux product background solves the complete linearized pure-Weyl--Maxwell equations with the same (h,a).",
            "includes_curvature_lower_order_terms": True,
            "includes_background_flux_mixing_on_shell": True,
            "field_map": "identity on (h_mn,a_m)",
            "solution_tangent_map": "injective before quotient; quotient injectivity remains a separate gauge/global question",
            "not_an_off_shell_chain_map": True,
        },
        "quadratic_onset": {
            "generic_quadratic_fixture": "C(epsilon)=epsilon^2*(J1^2+3*J1*J2+2*J2^2)",
            "first_variation": str(first_variation),
            "second_variation": str(second_variation),
            "interpretation": "the Chevreton defect cannot obstruct the linear tangent inclusion but can first enter at second order",
        },
        "direct_radion_fixture": fixture,
        "relation_to_principal_preflight": {
            "principal_chain_map_retained": True,
            "ordinary_null_symbol_injection_retained": True,
            "lower_order_on_shell_solution_map_closed": True,
            "off_shell_equation_and_identity_row_maps_closed": False,
        },
        "classification": {
            "full_lower_order_on_shell_linear_tangent_inclusion": True,
            "ordinary_einstein_graviton_and_photon_tangents_survive_before_quotient": True,
            "off_shell_curved_minimal_bv_chain_map_constructed": False,
            "quotient_observable_injection_constructed": False,
            "covariant_presymplectic_map_constructed": False,
            "nonlinear_einstein_maxwell_sector_closure_certified": False,
            "second_order_chevreton_obstruction_computed_for_physical_modes": False,
        },
        "next_gate": {
            "status": "OPEN",
            "target": "compute the second-order Chevreton defect on representatives of the injected graviton-plus-photon cohomology and construct the off-shell curved BV row maps and cyclic pairing",
            "required_checks": [
                "prolong the fourth-order characteristic complex",
                "choose exact graviton and photon representatives on the product",
                "evaluate the quadratic Chevreton trace on their first-order Maxwell jets",
                "separate a genuine second-order obstruction from a removable Weyl/diffeomorphism term",
                "construct formal adjoints, magnetic-bundle patching, and the covariant presymplectic comparison",
            ],
        },
        "claim_flags": {
            "local_algebraic_full_on_shell_linear_result": True,
            "off_shell_bv_chain_map_claim": False,
            "nonlinear_closure_claim": False,
            "lorentzian_causal_claim": False,
            "observable_embedding_claim": False,
            "scattering_claim": False,
            "quantum_claim": False,
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC theorem proves the complete on-shell linearized Einstein--Maxwell solution tangent maps into the complete on-shell linearized pure-Weyl--Maxwell solution tangent at the certified parallel-flux product background. It uses the convention-adjusted Einstein--Maxwell Bach/Chevreton factorization and includes curvature and flux lower-order terms on shell. It does not construct the off-shell curved BV chain map, quotient injection, cyclic or presymplectic map, nonlinear closure, second-order physical obstruction, causal dynamics, observables, scattering, or quantum equivalence.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_chevreton_tangent --verify bridge/certificates/einstein_maxwell_chevreton_tangent.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_chevreton_tangent.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_chevreton_tangent",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"Chevreton tangent certificate is stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(
            json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
