"""Certify a common Einstein--Maxwell/pure-Weyl--Maxwell product background.

The metric is a direct product of two oriented constant-curvature surfaces,

    M_2(k_1) x Sigma_2(k_2),

with Lorentzian first factor and Riemannian second factor.  An aligned Maxwell
field is a constant linear combination of their volume forms.  All symmetric
rank-two tensors then collapse to the two block metrics, making exact
same-metric, same-field incidence decidable without a coordinate ansatz.

This module certifies the background theorem only.  It does not construct the
linearized Einstein--Maxwell or Weyl--Maxwell BV complexes at that base point.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json"
SCHEMA_PATH = (
    ROOT
    / "bridge/einstein_sector/schema/einstein_maxwell_product_incidence.schema.json"
)


class EinsteinMaxwellProductIncidenceError(RuntimeError):
    """Raised when an exact product-incidence identity fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EinsteinMaxwellProductIncidenceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [
        [str(sp.factor(matrix[row, column])) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def _product_geometry() -> dict[str, Any]:
    """Derive curvature, Bach, and Maxwell tensors in an orthonormal frame."""

    k_1, k_2 = sp.symbols("k_1 k_2", real=True)
    electric, magnetic = sp.symbols("E P", real=True)
    alpha_b, kappa = sp.symbols("alpha_B kappa", positive=True, real=True)
    cosmological = sp.symbols("Lambda", real=True)
    eta = sp.diag(-1, 1, 1, 1)
    blocks = (0, 0, 1, 1)
    curvatures = (k_1, k_2)
    n = 4

    # Repository curvature convention:
    # R_abcd=k(g_ac g_bd-g_ad g_bc) on either two-dimensional factor.
    riemann = [
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
                    if (
                        blocks[first]
                        == blocks[second]
                        == blocks[third]
                        == blocks[fourth]
                    ):
                        curvature = curvatures[blocks[first]]
                        riemann[first][second][third][fourth] = sp.expand(
                            curvature
                            * (
                                eta[first, third] * eta[second, fourth]
                                - eta[first, fourth] * eta[second, third]
                            )
                        )

    ricci = sp.zeros(n)
    for second in range(n):
        for fourth in range(n):
            ricci[second, fourth] = sp.simplify(
                sum(
                    eta[first, third] * riemann[first][second][third][fourth]
                    for first in range(n)
                    for third in range(n)
                )
            )
    scalar = sp.factor(sp.trace(eta * ricci))
    schouten = sp.simplify((ricci - scalar * eta / 6) / 2)

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
                    weyl[first][second][third][fourth] = sp.simplify(
                        riemann[first][second][third][fourth]
                        - (
                            eta[first, third] * schouten[fourth, second]
                            - eta[first, fourth] * schouten[third, second]
                            - eta[second, third] * schouten[fourth, first]
                            + eta[second, fourth] * schouten[third, first]
                        )
                    )

    # The product is locally symmetric, hence nabla P=0.  In the repository
    # convention B_ac=P^bd C_abcd.
    schouten_up = sp.simplify(eta * schouten * eta)
    bach = sp.zeros(n)
    for first in range(n):
        for third in range(n):
            bach[first, third] = sp.factor(
                sum(
                    schouten_up[second, fourth]
                    * weyl[first][second][third][fourth]
                    for second in range(n)
                    for fourth in range(n)
                )
            )

    field_strength = sp.zeros(n)
    field_strength[0, 1] = electric
    field_strength[1, 0] = -electric
    field_strength[2, 3] = magnetic
    field_strength[3, 2] = -magnetic
    field_mixed = sp.simplify(field_strength * eta)
    field_squared = sp.factor(
        sum(
            eta[first, third]
            * eta[second, fourth]
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
            stress[first, second] = sp.factor(
                sum(
                    field_strength[first, index] * field_mixed[second, index]
                    for index in range(n)
                )
                - eta[first, second] * field_squared / 4
            )
    rho = sp.factor((electric**2 + magnetic**2) / 2)

    einstein = sp.simplify(ricci - scalar * eta / 2)
    einstein_residual = sp.simplify(
        einstein + cosmological * eta - kappa * stress
    )
    weyl_residual = sp.simplify(alpha_b * bach - stress)

    bach_amplitude = sp.factor((k_1 - k_2) * (k_1 + k_2) / 6)
    expected_bach = sp.diag(
        -bach_amplitude,
        bach_amplitude,
        -bach_amplitude,
        -bach_amplitude,
    )
    expected_stress = sp.diag(rho, -rho, rho, rho)
    _require(ricci == sp.diag(-k_1, k_1, k_2, k_2), "product Ricci changed")
    _require(sp.simplify(scalar - 2 * (k_1 + k_2)) == 0, "scalar changed")
    _require(bach == expected_bach, "product Bach tensor changed")
    _require(sp.simplify(sp.trace(eta * bach)) == 0, "Bach trace changed")
    _require(stress == expected_stress, "aligned Maxwell stress changed")
    _require(sp.simplify(sp.trace(eta * stress)) == 0, "Maxwell trace changed")

    incidence = {
        cosmological: (k_1 + k_2) / 2,
        rho: (k_2 - k_1) / (2 * kappa),
        alpha_b: 3 / (kappa * (k_1 + k_2)),
    }
    # SymPy cannot substitute an expression key such as rho, so impose the
    # incidence relation on E^2+P^2 directly.
    incidence_substitution = {
        cosmological: (k_1 + k_2) / 2,
        magnetic**2: (k_2 - k_1) / kappa - electric**2,
        alpha_b: 3 / (kappa * (k_1 + k_2)),
    }
    einstein_incident = einstein_residual.applyfunc(
        lambda value: sp.factor(
            value.subs(cosmological, incidence[cosmological]).subs(
                magnetic**2,
                (k_2 - k_1) / kappa - electric**2,
            )
        )
    )
    weyl_incident = weyl_residual.applyfunc(
        lambda value: sp.factor(
            value.subs(alpha_b, incidence[alpha_b]).subs(
                magnetic**2,
                (k_2 - k_1) / kappa - electric**2,
            )
        )
    )
    _require(einstein_incident == sp.zeros(4), "Einstein incidence failed")
    _require(weyl_incident == sp.zeros(4), "Weyl incidence failed")

    fixture_substitution = {
        k_1: 0,
        k_2: 1,
        alpha_b: 3,
        kappa: 1,
        cosmological: sp.Rational(1, 2),
        electric: 0,
        magnetic: 1,
    }
    _require(
        einstein_residual.subs(fixture_substitution) == sp.zeros(4),
        "rational fixture failed Einstein equation",
    )
    _require(
        weyl_residual.subs(fixture_substitution) == sp.zeros(4),
        "rational fixture failed Weyl equation",
    )

    return {
        "symbols": {
            "k_1": k_1,
            "k_2": k_2,
            "E": electric,
            "P": magnetic,
            "alpha_B": alpha_b,
            "kappa": kappa,
            "Lambda": cosmological,
        },
        "eta": eta,
        "ricci": ricci,
        "scalar": scalar,
        "schouten": schouten,
        "bach": bach,
        "field_strength": field_strength,
        "field_squared": field_squared,
        "stress": stress,
        "rho": rho,
        "einstein": einstein,
        "einstein_residual": einstein_residual,
        "weyl_residual": weyl_residual,
        "bach_amplitude": bach_amplitude,
        "incidence_substitution": incidence_substitution,
        "fixture_substitution": fixture_substitution,
    }


def build_certificate() -> dict[str, Any]:
    data = _product_geometry()
    symbols = data["symbols"]
    k_1 = symbols["k_1"]
    k_2 = symbols["k_2"]
    alpha_b = symbols["alpha_B"]
    kappa = symbols["kappa"]
    cosmological = symbols["Lambda"]
    magnetic = symbols["P"]
    fixture = data["fixture_substitution"]

    flat_k_2 = sp.factor(3 / (alpha_b * kappa))
    flat_lambda = sp.factor(flat_k_2 / 2)
    flat_rho = sp.factor(flat_k_2 / (2 * kappa))
    flat_magnetic_squared = sp.factor(flat_k_2 / kappa)
    sphere_radius_squared = sp.factor(1 / flat_k_2)

    # With q_min/(2 pi) int F=N and int_S2 vol=4 pi/k_2,
    # P=N k_2/(2 q_min).  Combining this with P^2=k_2/kappa and the
    # flat-branch incidence relation gives the discrete alpha_B condition.
    charge, flux_integer = sp.symbols("q_min N", positive=True, real=True)
    quantized_magnetic = sp.factor(flux_integer * k_2 / (2 * charge))
    quantized_alpha = sp.factor(3 * flux_integer**2 / (4 * charge**2))

    fixture_tensors = {
        name: matrix.subs(fixture)
        for name, matrix in (
            ("ricci", data["ricci"]),
            ("bach", data["bach"]),
            ("stress", data["stress"]),
            ("einstein_tensor", data["einstein"]),
            ("einstein_residual", data["einstein_residual"]),
            ("weyl_residual", data["weyl_residual"]),
        )
    }

    return {
        "schema": "einstein-maxwell-product-incidence-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_PRODUCT_INCIDENCE",
        "result_state": "CERTIFIED_EXACT_COMMON_BACKGROUND_TANGENT_COMPLEX_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "literature_context": {
                "title": "The Flat Critical Branch Between Nariai and Bertotti-Robinson Geometries as a Solution of Cosmological Einstein-Maxwell Theory",
                "arxiv": "2604.19168",
                "role": "context only; every certified tensor identity is derived independently by this generator",
            },
        },
        "conventions": {
            "signature": "(-,+,+,+)",
            "curvature": "R_abcd=k(g_ac g_bd-g_ad g_bc) on each two-dimensional factor",
            "weyl_maxwell_action": "S_WM=int sqrt(-g)[(alpha_B/8) C_abcd C^abcd-(1/4)F_ab F^ab]",
            "weyl_maxwell_equations": "alpha_B B_ab=T_ab; nabla_a F^ab=0; dF=0",
            "einstein_maxwell_action": "S_EM=int sqrt(-g)[(R-2Lambda)/(2kappa)-(1/4)F_ab F^ab]",
            "einstein_maxwell_equations": "G_ab+Lambda g_ab=kappa T_ab; nabla_a F^ab=0; dF=0",
            "bach": "B_ac=P^bd C_abcd because nabla P=0 on the locally symmetric product",
            "stress": "T_ab=F_ac F_b^c-(1/4)g_ab F_cd F^cd",
        },
        "ansatz": {
            "spacetime": "M_2(k_1) x Sigma_2(k_2)",
            "first_factor": "oriented Lorentzian constant-curvature surface",
            "second_factor": "oriented Riemannian constant-curvature surface",
            "field_strength": "F=E vol(M_2)+P vol(Sigma_2)",
            "maxwell_equations": "PASS because both factor volume forms are parallel, hence closed and coclosed",
            "energy_density": str(data["rho"]),
        },
        "exact_tensors": {
            "metric_orthonormal": _matrix_strings(data["eta"]),
            "ricci_orthonormal": _matrix_strings(data["ricci"]),
            "scalar_curvature": str(data["scalar"]),
            "schouten_orthonormal": _matrix_strings(data["schouten"]),
            "bach_orthonormal": _matrix_strings(data["bach"]),
            "bach_block_amplitude": str(data["bach_amplitude"]),
            "field_strength_orthonormal": _matrix_strings(data["field_strength"]),
            "field_squared": str(data["field_squared"]),
            "maxwell_stress_orthonormal": _matrix_strings(data["stress"]),
            "einstein_tensor_orthonormal": _matrix_strings(data["einstein"]),
        },
        "common_incidence_theorem": {
            "branch_assumptions": [
                "alpha_B>0",
                "kappa>0",
                "k_2>k_1",
                "k_1+k_2>0",
            ],
            "cosmological_constant": "(k_1+k_2)/2",
            "maxwell_energy_density": "(k_2-k_1)/(2*kappa)",
            "aligned_field_norm": "E^2+P^2=(k_2-k_1)/kappa",
            "coupling_curvature_incidence": "alpha_B*kappa*(k_1+k_2)=3",
            "einstein_maxwell_equation": "PASS componentwise",
            "pure_weyl_maxwell_equation": "PASS componentwise",
            "same_metric": True,
            "same_maxwell_field": True,
            "not_a_gauge_equivalence": True,
        },
        "degenerate_branches": {
            "k_1_equals_k_2": {
                "classification": "flux-free Einstein product in the common vacuum locus",
                "reason": "Einstein--Maxwell incidence forces rho=0 and the Bach tensor vanishes",
            },
            "k_1_plus_k_2_equals_zero_with_unequal_curvatures": {
                "classification": "no same-field incidence with nonzero Maxwell flux",
                "reason": "B=0 forces T=0 in pure Weyl--Maxwell, while Einstein--Maxwell requires rho=(k_2-k_1)/(2kappa)",
            },
        },
        "flat_critical_branch": {
            "local_geometry": "R^(1,1) x S^2",
            "compact_spatial_quotient": "R_t x S^1_L x S^2_r",
            "curvatures": {"k_1": "0", "k_2": str(flat_k_2)},
            "cosmological_constant": str(flat_lambda),
            "energy_density": str(flat_rho),
            "pure_magnetic_field_squared": str(flat_magnetic_squared),
            "sphere_radius_squared": str(sphere_radius_squared),
            "positive_energy_for_positive_couplings": True,
            "smooth_spatial_quotient": True,
            "compact_cauchy_topology": "S^1 x S^2",
            "global_timelike_killing_field": "partial_t",
            "relational_matter_clock": False,
            "asymptotically_flat": False,
        },
        "u1_flux_quantization": {
            "status": "OPTIONAL_GLOBAL_REFINEMENT",
            "normalization": "q_min/(2*pi) integral_(S^2) F=N in Z",
            "sphere_area": "4*pi/k_2",
            "magnetic_amplitude": str(quantized_magnetic),
            "flat_branch_discrete_coupling": f"alpha_B={quantized_alpha}",
            "rational_fixture": "q_min=1, N=2 gives alpha_B=3 and P=1",
            "warning": "changing the Maxwell kinetic normalization changes this coupling formula but not the local incidence theorem",
        },
        "rational_fixture": {
            "parameters": {
                "k_1": "0",
                "k_2": "1",
                "alpha_B": "3",
                "kappa": "1",
                "Lambda": "1/2",
                "E": "0",
                "P": "1",
            },
            "ricci_orthonormal": _matrix_strings(fixture_tensors["ricci"]),
            "bach_orthonormal": _matrix_strings(fixture_tensors["bach"]),
            "maxwell_stress_orthonormal": _matrix_strings(fixture_tensors["stress"]),
            "einstein_tensor_orthonormal": _matrix_strings(
                fixture_tensors["einstein_tensor"]
            ),
            "einstein_residual": _matrix_strings(
                fixture_tensors["einstein_residual"]
            ),
            "weyl_residual": _matrix_strings(fixture_tensors["weyl_residual"]),
            "both_metric_equations": "PASS",
        },
        "classification": {
            "exact_common_einstein_maxwell_weyl_maxwell_background_exists": True,
            "positive_energy_common_branch_exists": True,
            "compact_cauchy_spatial_quotient_exists": True,
            "common_background_is_a_relational_clock_background": False,
            "common_background_is_asymptotically_flat": False,
            "linearized_tangent_complex_map_constructed": False,
            "einstein_observable_embedding_constructed": False,
            "theories_proved_equivalent": False,
        },
        "next_gate": {
            "status": "OPEN",
            "target": "construct and compare the minimal Einstein--Maxwell and Diff x Weyl--Maxwell BV complexes at the certified identical base point",
            "required_checks": [
                "freeze both Hessians and gauge generators",
                "verify nilpotency, Noether identities, cyclicity, and Maxwell gauge rows",
                "construct an explicit tangent chain map or exact obstruction",
                "compare the helicity-two and photon cohomology before any residual quotient",
                "compare covariant presymplectic currents and charges",
            ],
        },
        "claim_flags": {
            "exact_nonlinear_background_incidence_certified": True,
            "same_metric_and_maxwell_field_certified": True,
            "positive_flat_critical_specialization_certified": True,
            "u1_flux_quantization_relation_certified": True,
            "tangent_bv_inclusion_certified": False,
            "relational_clock_certified": False,
            "lorentzian_green_complex_certified": False,
            "scattering_sector_certified": False,
            "quantum_claim": False,
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC certificate proves an exact nonlinear same-metric, same-Maxwell-field intersection of cosmological Einstein--Maxwell and pure Weyl--Maxwell solution loci, including a positive R^(1,1) x S^2 branch and its smooth spatial S^1 quotient. It proves no tangent BV inclusion, relational clock, stability, Green complex, asymptotic-flatness, observable embedding, scattering statement, or quantum equivalence.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_product_incidence --verify bridge/certificates/einstein_maxwell_product_incidence.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_product_incidence.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_product_incidence",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(
        payload == build_certificate(),
        f"Einstein--Maxwell product certificate is stale or altered: {path}",
    )


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
