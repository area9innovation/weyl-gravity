#!/usr/bin/env python3
"""Exact symbolic-Lambda polar harmonic and Ricci reconstruction preflight.

This bounded Phase-2 producer replaces the hard-coded P2, dP2 and W tensor
used by the existing polar Schwarzschild chain with a generic scalar harmonic
P satisfying the Legendre equation.  It constructs the even vector and STF
tensor harmonics, derives the complete trace-coupled polar Bianchi cascade,
and audits the first downstream object required by the requested metric and
literal-current theorem.

The generic seven-row linearized-Ricci map is constructed literally in polar
Regge--Wheeler gauge.  The output retains the three propagating constraint
rows, records its representation denominators, and identifies the functional
Weyl-radical direction.  The later pure-Weyl current table remains fail-closed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from black_hole_programme.weyl_geometry import Geometry
from black_hole_programme.phase2.general_l_polar.symbolic_reconstruction import derive_symbolic_reconstruction
from black_hole_programme.phase2.general_l_polar.literal_current import derive_symbolic_literal_current
from black_hole_programme.phase2.general_l_polar.generic_carrier_asymptotics import derive_generic_carrier_asymptotics
from black_hole_programme.phase2.general_l_polar.sourced_lift import derive_leading_lift_preflight


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"
ATLAS = ROOT / "residual_atlas/phase2-black-hole-general-l-polar-disposition-fragment-v1.json"
PRODUCER = Path(__file__).resolve()
VERIFIER = HERE / "verify_general_l_polar_disposition.py"
TESTS = HERE / "tests/test_general_l_polar_disposition.py"
RECONSTRUCTION = HERE / "symbolic_reconstruction.py"
LITERAL_CURRENT = HERE / "literal_current.py"
CARRIER_ASYMPTOTICS = HERE / "generic_carrier_asymptotics.py"
SOURCED_LIFT = HERE / "sourced_lift.py"
SOURCED_LIFT_PILOT = HERE / "sourced_lift_depth2_pilot.json"
SOURCED_LIFT_PILOT_PRODUCER = HERE / "produce_sourced_lift_depth2_pilot.py"

INPUTS = {
    "general_l_axial_control": (
        ROOT / "black_hole_programme/certificates/BH2_GENERAL_L_STRUCTURAL.json",
        "PURE_WEYL_BH2_GENERAL_L_STRUCTURAL",
    ),
    "polar_split": (
        ROOT / "black_hole_programme/certificates/BH2B_POLAR_SPLIT.json",
        "PURE_WEYL_BH2B_POLAR_SPLIT",
    ),
    "polar_l2_carrier": (
        ROOT / "black_hole_programme/certificates/BH2B_POLAR_REACH.json",
        "PURE_WEYL_BH2B_POLAR_REACH",
    ),
    "polar_l2_einstein_reconstruction": (
        ROOT / "black_hole_programme/certificates/BH2B_POLAR_EINSTEIN.json",
        "PURE_WEYL_BH2B_POLAR_EINSTEIN",
    ),
    "polar_l2_composed_current": (
        ROOT / "black_hole_programme/certificates/BH2B_COMPOSED_REPAIR.json",
        "PURE_WEYL_BH2B_COMPOSED_REPAIR",
    ),
    "polar_l2_asymptotic_metric": (
        ROOT / "black_hole_programme/certificates/BH2C_POLAR_METRIC_INDICIAL.json",
        "PURE_WEYL_BH2C_POLAR_METRIC_INDICIAL",
    ),
    "polar_l2_flux_class": (
        ROOT / "black_hole_programme/certificates/BH2C_POLAR_FLUX_CLASS.json",
        "PURE_WEYL_BH2C_POLAR_FLUX_CLASS",
    ),
    "polar_quantifier_repair": (
        ROOT / "black_hole_programme/certificates/BH2_POLAR_QUANTIFIER_REPAIR.json",
        "PURE_WEYL_BH2_POLAR_QUANTIFIER_REPAIR",
    ),
    "polar_l2_cross_flux": (
        ROOT / "black_hole_programme/certificates/BH2B_POLAR_CROSS_FLUX.json",
        "PURE_WEYL_BH2B_POLAR_CROSS_FLUX",
    ),
}


class PolarDispositionError(RuntimeError):
    """Raised when an exact preflight identity fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolarDispositionError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _legendre_reduce(expression: sp.Expr, p: sp.Expr, x: sp.Symbol, lam: sp.Symbol) -> sp.Expr:
    """Reduce derivatives of P to the basis (P,P') via its eigen-equation."""
    result = sp.expand(expression)
    p_prime = sp.diff(p, x)
    for order in range(10, 1, -1):
        derivative = sp.diff(p, (x, order))
        if result.has(derivative):
            replacement = sp.diff((2 * x * p_prime - lam * p) / (1 - x**2), x, order - 2)
            result = sp.expand(sp.together(result.subs(derivative, replacement)))
    return sp.cancel(sp.together(result))


def _import_gate() -> tuple[list[dict[str, str]], dict[str, Any]]:
    imports: list[dict[str, str]] = []
    payloads: dict[str, Any] = {}
    for name, (path, result_id) in INPUTS.items():
        _require(path.exists(), f"missing input: {path}")
        payload = _load(path)
        _require(payload.get("result_id") == result_id, f"result-id drift: {name}")
        imports.append(
            {
                "name": name,
                "path": str(path.relative_to(ROOT)),
                "result_id": result_id,
                "result_token": payload.get("result_token", ""),
                "sha256": _sha256(path),
            }
        )
        payloads[name] = payload
    return imports, payloads


def derive_harmonics_and_bianchi() -> dict[str, Any]:
    v, r, x, phi = sp.symbols("v r x phi")
    mass = sp.Symbol("m", positive=True)
    lam = sp.Symbol("Lambda")
    coordinates = [v, r, x, phi]
    schwarzschild = 1 - 2 * mass / r
    metric = sp.zeros(4)
    metric[0, 0] = -schwarzschild
    metric[0, 1] = metric[1, 0] = 1
    metric[2, 2] = r**2 / (1 - x**2)
    metric[3, 3] = r**2 * (1 - x**2)
    geometry = Geometry(coordinates, metric)
    inverse = geometry.ginv

    p = sp.Function("P")(x)
    p_prime = sp.diff(p, x)
    vector_x = p_prime
    tensor_xx = sp.cancel((x * p_prime - lam * p / 2) / (1 - x**2))
    tensor_pp = sp.cancel(-(1 - x**2) * (x * p_prime - lam * p / 2))
    tensor_trace = _legendre_reduce(
        inverse[2, 2] * tensor_xx + inverse[3, 3] * tensor_pp, p, x, lam
    )
    _require(tensor_trace == 0, "generic polar tensor harmonic is not tracefree")

    # Independent two-sphere tensor-divergence calculation from the metric,
    # without using the four-dimensional polar carrier.
    sphere_coordinates = [x, phi]
    sphere_metric = sp.diag(1 / (1 - x**2), 1 - x**2)
    sphere_inverse = sphere_metric.inv()
    sphere_gamma = [
        [
            [
                sp.cancel(
                    sum(
                        sphere_inverse[a0, d0]
                        * (
                            sp.diff(sphere_metric[d0, c0], sphere_coordinates[b0])
                            + sp.diff(sphere_metric[d0, b0], sphere_coordinates[c0])
                            - sp.diff(sphere_metric[b0, c0], sphere_coordinates[d0])
                        )
                        / 2
                        for d0 in range(2)
                    )
                )
                for c0 in range(2)
            ]
            for b0 in range(2)
        ]
        for a0 in range(2)
    ]
    tensor = sp.diag(tensor_xx, tensor_pp)

    def sphere_covector_divergence(index: int) -> sp.Expr:
        value = 0
        for a0 in range(2):
            for c0 in range(2):
                if sphere_inverse[a0, c0] == 0:
                    continue
                covariant = sp.diff(tensor[a0, index], sphere_coordinates[c0])
                for h0 in range(2):
                    covariant -= sphere_gamma[h0][c0][a0] * tensor[h0, index]
                    covariant -= sphere_gamma[h0][c0][index] * tensor[a0, h0]
                value += sphere_inverse[a0, c0] * covariant
        return _legendre_reduce(sp.cancel(value), p, x, lam)

    expected_divergence = [-(lam - 2) * p_prime / 2, sp.Integer(0)]
    for index in range(2):
        _require(
            _legendre_reduce(sphere_covector_divergence(index) - expected_divergence[index], p, x, lam) == 0,
            f"generic polar tensor divergence failed at sphere index {index}",
        )

    # Integrated Bochner identity on the unit sphere:
    # ||Hess Y||^2=(Lambda^2-Lambda)N and
    # ||Hess^TF Y||^2=||Hess Y||^2-(Lambda^2/2)N.
    stf_norm_multiplier = sp.factor(lam**2 - lam - lam**2 / 2)
    _require(stf_norm_multiplier == lam * (lam - 2) / 2, "STF norm multiplier changed")

    p2 = (3 * x**2 - 1) / 2
    tensor_xx_l2 = sp.cancel(tensor_xx.subs(lam, 6).subs(p, p2).doit())
    tensor_pp_l2 = sp.cancel(tensor_pp.subs(lam, 6).subs(p, p2).doit())
    _require(tensor_xx_l2 == sp.Rational(3, 2), "P2 W_xx control failed")
    _require(
        sp.factor(tensor_pp_l2 + sp.Rational(3, 2) * (1 - x**2) ** 2) == 0,
        "P2 W_phiphi control failed",
    )

    fields = [sp.Function(name)(v, r) for name in ("A", "Bc", "Cc", "D", "Ec", "F", "Gc")]
    a, bc, cc, d, ec, f, gc = fields
    carrier = sp.zeros(4)
    carrier[0, 0] = a * p
    carrier[0, 1] = carrier[1, 0] = bc * p
    carrier[1, 1] = cc * p
    carrier[0, 2] = carrier[2, 0] = d * vector_x
    carrier[1, 2] = carrier[2, 1] = ec * vector_x
    carrier[2, 2] = metric[2, 2] * f * p + gc * tensor_xx
    carrier[3, 3] = metric[3, 3] * f * p + gc * tensor_pp
    trace = sp.cancel(
        sum(inverse[i, j] * carrier[i, j] for i in range(4) for j in range(4))
    )
    _require(
        _legendre_reduce(trace - (2 * bc + schwarzschild * cc + 2 * f) * p, p, x, lam) == 0,
        "carrier trace formula failed",
    )

    def bianchi_row(index: int) -> sp.Expr:
        raw = sum(
            inverse[i, e] * geometry.covd2(carrier, e, i, index)
            for i in range(4)
            for e in range(4)
            if inverse[i, e] != 0
        ) - sp.diff(trace, coordinates[index]) / 2
        reduced = _legendre_reduce(sp.cancel(raw), p, x, lam)
        harmonic = p if index < 2 else p_prime
        stripped = _legendre_reduce(sp.cancel(reduced / harmonic), p, x, lam)
        _require(not stripped.has(x, p, p_prime), f"Bianchi row {index} did not strip")
        return stripped

    rows = [bianchi_row(index) for index in range(3)]
    solution_d = sp.solve(sp.Eq(rows[0], 0), d)
    _require(len(solution_d) == 1, "D cascade row is not uniquely solvable")
    row_r = sp.cancel(rows[1].subs(d, solution_d[0]).doit())
    solution_ec = sp.solve(sp.Eq(row_r, 0), ec)
    _require(len(solution_ec) == 1, "Ec cascade row is not uniquely solvable")
    row_x = sp.cancel(rows[2].subs({d: solution_d[0], ec: solution_ec[0]}).doit())
    solution_gc = sp.solve(sp.Eq(row_x, 0), gc)
    _require(len(solution_gc) == 1, "Gc cascade row is not uniquely solvable")

    coefficients = [
        sp.cancel(sp.diff(rows[0], d)),
        sp.cancel(sp.diff(row_r, ec)),
        sp.cancel(sp.diff(row_x, gc)),
    ]
    _require(coefficients == [-lam / r**2, -lam / r**2, (2 - lam) / (2 * r**2)], "cascade pivots changed")

    return {
        "harmonic_conventions": {
            "scalar": "Y=P_Lambda(x), (1-x^2)P''=2xP'-Lambda P",
            "vector_x": "D_x Y=P'",
            "tensor_definition": "Y_AB^TF=D_A D_B Y+(Lambda/2)gamma_AB Y",
            "tensor_xx": sp.sstr(tensor_xx),
            "tensor_phiphi": sp.sstr(tensor_pp),
            "trace": "0",
            "divergence": "D^A Y_AB^TF=-(Lambda-2)/2 D_B Y",
            "integrated_norms_relative_to_NLambda": {
                "scalar": "1",
                "vector": "Lambda",
                "STF_tensor": "Lambda*(Lambda-2)/2",
            },
            "STF_norm_derivation": "Bochner: ||Hess Y||^2=(Lambda^2-Lambda)N; subtract the trace square Lambda^2*N/2",
            "P2_positive_control": {"Lambda": 6, "W_xx": "3/2", "W_phiphi": "-3*(1-x^2)^2/2"},
        },
        "carrier": {
            "components": ["A", "Bc", "Cc", "D", "Ec", "F", "Gc"],
            "trace": "(2*Bc+(1-2*m/r)*Cc+2*F)*P",
            "free_after_bianchi": ["A", "Bc", "Cc", "F"],
            "solved_in_order": ["D", "Ec", "Gc"],
        },
        "bianchi_cascade": {
            "stripped_rows": [sp.sstr(row) for row in rows],
            "solutions": {
                "D": sp.sstr(solution_d[0]),
                "Ec": sp.sstr(solution_ec[0]),
                "Gc": sp.sstr(solution_gc[0]),
            },
            "pivot_coefficients": [sp.sstr(value) for value in coefficients],
            "generic_domain": "Lambda=l(l+1), integer l>=2; pivots Lambda and Lambda-2 are nonzero",
            "exceptional_representations": {"Lambda=0": "l=0", "Lambda=2": "l=1"},
            "symbolic_lambda_closed": True,
            "angular_sampling_used": False,
        },
    }


def audit_downstream_gate(payloads: dict[str, Any]) -> dict[str, Any]:
    reach = payloads["polar_l2_carrier"]
    einstein = payloads["polar_l2_einstein_reconstruction"]
    metric = payloads["polar_l2_asymptotic_metric"]
    flux = payloads["polar_l2_flux_class"]
    repair = payloads["polar_quantifier_repair"]
    cross = payloads["polar_l2_cross_flux"]
    _require(reach["claim_flags"]["general_l_certified"] is False, "l2 carrier falsely generic")
    _require(einstein["claim_flags"]["general_l_certified"] is False, "l2 Einstein reconstruction falsely generic")
    _require(metric["claim_flags"]["general_l_certified"] is False, "l2 metric indicial falsely generic")
    _require(flux["claim_flags"]["general_l_certified"] is False, "l2 flux class falsely generic")
    _require(repair["claim_flags"]["generic_real_frequency_certified"] is False, "polar quantifier unexpectedly closed")
    _require(cross["claim_flags"]["cross_block_nonzero_certified"] is True, "l2 cross witness lost")
    _require(cross["claim_flags"]["invariant_extra_sign_certified"] is False, "l2 XX ambiguity unexpectedly closed")
    exact_cross_witness = cross["fixtures"]["flux_matrix_rho_1_4"]["E|X0"]
    _require(exact_cross_witness not in ("0", "0.0", ""), "l2 exact cross witness vanished")
    return {
        "first_missing_object": "SYMBOLIC_LAMBDA_SOURCED_POLAR_METRIC_JETS_WITH_ALL_SEVEN_CONSTRAINTS",
        "precise_contract": {
            "constructed": "the exact symbolic-Lambda sphere-integrated Lee-Wald radial bilinear on arbitrary polar metric pairs",
            "constructed_branch_data": "generic-Lambda homogeneous metric master, conformal-slice Bach-carrier rates/powers, and exact leading source-forcing preflight",
            "typed_need": "fraction-free order-by-order sourced metric jets for all six carrier branches, with literal vv/vr/angP residuals through the current depth",
            "downstream": "substitute those certified jets into F^v and prove the EE/EX/XX leading coefficients nonzero or list their exact exceptional set",
        },
        "change_of_splitting": {
            "lift": "X_prime=X+E*T",
            "EE_prime": "EE",
            "EX_prime": "EX+EE*T",
            "XX_prime": "XX+T_dagger*EX+XE*T+T_dagger*EE*T",
            "consequence": "nonzero EX makes XX representative-dependent even when EE=0",
        },
        "power_filtered_fixture_class": {
            "scope": "ell=2, omega=3/5 only",
            "mu0": {"EE": "identically zero", "EX_leading_power": 1, "XX_leading_power": 2},
            "mu_minus_2omega": {"EE_leading_power": -2, "EX_leading_power": 3, "XX_leading_power": 4},
            "invariance": "X->X+beta E changes only lower-power terms, so the divergent XX leading class is splitting-invariant at this fixture",
            "generic_lambda_promoted": False,
        },
        "exact_domain_witness": {
            "ell": 2,
            "omega": "3/5",
            "source": "BH2B_POLAR_CROSS_FLUX",
            "E_X0_exact_expression": exact_cross_witness,
            "cross_nonzero_certified": True,
            "logic": "the nonzero cross pairing proves full-entry representative dependence, but not loss of the power-filtered leading divergence class",
        },
        "why_no_import_closes_it": {
            "polar_carrier_scope": "l=2",
            "polar_einstein_reconstruction_scope": "l=2",
            "polar_asymptotic_metric_scope": "l=2",
            "polar_literal_flux_scope": "l=2 fixture/frequency scopes",
            "generic_omega_route_B_closed": False,
        },
        "not_used_as_obstruction": [
            "a nonterminating symbolic run",
            "an exponent-only inference",
            "failure of the independent axial theorem",
            "a proof that no symbolic-Lambda reconstruction exists",
        ],
        "bounded_diagnostic": {
            "solver_update": "DomainMatrix fraction-field RREF supersedes the earlier multivariate-GCD implementation",
            "depth_2_outcome": "zero branches 0/1/2 and oscillatory branch 1 solved; oscillatory branches 0/2 exceeded separate 180-second bounds",
            "reading": "the two bounded non-results are computational bottlenecks, not mathematical obstructions or timeout theorems",
            "first_specific_bottleneck": "oscillatory branch index 0 at metric depth 2 under the present DomainMatrix solver",
            "required_architecture": "cache carrier jets per simple projected power, expose RREF pivot denominators, and impose all-seven residuals coefficient by coefficient",
        },
        "exact_depth_requirements": {
            "literal_current": "metric depth 2 for the first potentially nonintegrable X coefficient",
            "zero_branches_by_j": {"1": 3, "2": 4, "3": 5},
            "oscillatory_branches_by_j": {"1": 3, "2": 4, "3": 5},
            "carrier_depth_rule": "metric depth + 4 because reconstruction consumes source derivatives through order 4",
            "worst_case": "zero-shell j=3 requires metric depth 5 and carrier depth 9",
        },
        "disposition": "SHORTFALL_AFTER_LITERAL_CURRENT_AND_BRANCH_PREFLIGHT",
    }


def load_bounded_depth2_pilot(reconstruction: dict[str, Any], carrier: dict[str, Any]) -> dict[str, Any]:
    """Import the content-addressed exhaustive pilot without replaying it."""
    pilot = _load(SOURCED_LIFT_PILOT)
    canonical = lambda value: hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    _require(pilot["input_subobject_sha256"]["ricci_to_metric_reconstruction"] == canonical(reconstruction), "pilot reconstruction input drift")
    _require(pilot["input_subobject_sha256"]["generic_carrier_asymptotics"] == canonical(carrier), "pilot carrier input drift")
    _require(pilot["solution_denominator_factors"] == ["Lambda", "Lambda - 2"], "pilot solution walls changed")
    return pilot


def build_certificate() -> dict[str, Any]:
    imports, payloads = _import_gate()
    exact = derive_harmonics_and_bianchi()
    exact["ricci_to_metric_reconstruction"] = derive_symbolic_reconstruction()
    exact["literal_lee_wald_current"] = derive_symbolic_literal_current()
    exact["literal_current_filtration"] = {
        "expanded_terms": 272,
        "raw_radial_jet_groups": 79,
        "exact_oriented_nonzero_groups": 79,
        "coarse_unordered_support_classes": 23,
        "coarse_projection_is_not_an_algebraic_reduction": True,
        "component_pairs": ["AB", "AC", "AK", "BB", "BC", "BK", "CC", "CK", "KK"],
        "maximum_derivative_order": {"A": 3, "B": 2, "C": 2, "K": 3},
        "maximum_coefficient_radial_weight": 2,
        "zero_shell_first_XX_coefficient": "8*I*pi*alpha*omega*(4*B1a*B1b+3*I*omega*B1a*C2b-3*I*omega*B1b*C2a-4*omega**2*C2a*C2b)/(3*(2*ell+1))",
        "zero_shell_metric_depth": 2,
        "oscillatory_layers": {"weight_plus_2": "0", "weight_plus_1": "0", "first_discriminating_metric_depth": 2},
        "audit": "exact filtration of the serialized F^v bilinear; all-seven closure remains separate",
    }
    exact["generic_carrier_asymptotics"] = derive_generic_carrier_asymptotics()
    exact["leading_sourced_lift_preflight"] = derive_leading_lift_preflight(
        exact["ricci_to_metric_reconstruction"], exact["generic_carrier_asymptotics"]
    )
    exact["bounded_sourced_lift_depth2_pilot"] = load_bounded_depth2_pilot(
        exact["ricci_to_metric_reconstruction"], exact["generic_carrier_asymptotics"]
    )
    missing = audit_downstream_gate(payloads)
    return {
        "schema": "phase2-black-hole-general-l-polar-disposition-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "PHASE2_BLACK_HOLE_GENERAL_L_POLAR_DISPOSITION",
        "result_state": "SYMBOLIC_LAMBDA_POLAR_LITERAL_CURRENT_AND_DEPTH2_BRANCH_PILOT_CERTIFIED_SOURCED_JET_SHORTFALL",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "strict pure-Weyl gravity",
            "background": "Schwarzschild in ingoing Eddington-Finkelstein coordinates, symbolic m",
            "parity": "polar/even",
            "harmonics": "Lambda=l(l+1), integer l>=2",
            "frequency": "symbolic omega; the universal F^v bilinear is certified, while the branch-specialized current table is absent",
        },
        "provenance": {
            "declared_input_commit": "4a212883aefa5525cc847d0c12763c74c1c3411a",
            "implementation_base_commit": "7166839b7a685357d8d7088c4db00de06171dc41",
            "producer": str(PRODUCER.relative_to(ROOT)),
            "producer_sha256": _sha256(PRODUCER),
            "verifier": str(VERIFIER.relative_to(ROOT)),
            "verifier_sha256": _sha256(VERIFIER),
            "tests": str(TESTS.relative_to(ROOT)),
            "tests_sha256": _sha256(TESTS),
            "reconstruction_module": str(RECONSTRUCTION.relative_to(ROOT)),
            "reconstruction_module_sha256": _sha256(RECONSTRUCTION),
            "literal_current_module": str(LITERAL_CURRENT.relative_to(ROOT)),
            "literal_current_module_sha256": _sha256(LITERAL_CURRENT),
            "carrier_asymptotics_module": str(CARRIER_ASYMPTOTICS.relative_to(ROOT)),
            "carrier_asymptotics_module_sha256": _sha256(CARRIER_ASYMPTOTICS),
            "sourced_lift_module": str(SOURCED_LIFT.relative_to(ROOT)),
            "sourced_lift_module_sha256": _sha256(SOURCED_LIFT),
            "sourced_lift_pilot": str(SOURCED_LIFT_PILOT.relative_to(ROOT)),
            "sourced_lift_pilot_sha256": _sha256(SOURCED_LIFT_PILOT),
            "sourced_lift_pilot_producer": str(SOURCED_LIFT_PILOT_PRODUCER.relative_to(ROOT)),
            "sourced_lift_pilot_producer_sha256": _sha256(SOURCED_LIFT_PILOT_PRODUCER),
            "imported_artifacts": imports,
        },
        "exact_symbolic_lambda_result": exact,
        "downstream_gate": missing,
        "claim_flags": {
            "generic_polar_tensor_harmonics_certified": True,
            "generic_polar_bianchi_cascade_certified": True,
            "generic_polar_curvature_carrier_certified": True,
            "generic_polar_operator_rows_certified": True,
            "generic_polar_metric_reconstruction_certified": True,
            "generic_polar_conformal_quotient_certified": True,
            "generic_polar_route_B_identity_certified": False,
            "generic_polar_literal_current_certified": True,
            "generic_polar_depth2_branch_pilot_certified": True,
            "generic_polar_EE_EX_XX_table_certified": False,
            "parity_complete_selection_theorem_certified": False,
            "axial_theorem_modified": False,
            "ell2_promoted_to_generic": False,
            "exponent_only_result": False,
            "timeout_called_obstruction": False,
        },
        "claim_boundary": {
            "establishes": "For Lambda=l(l+1), l>=2, the harmonic basis, Bianchi cascade, seven-row Ricci reconstruction, literal sphere-integrated Lee-Wald F^v slice bilinear, homogeneous metric master, formally reachable traceless Bach-carrier slice, leading source-forcing data, and four finite depth-2 sourced-lift pilots close exactly. The zero-shell pilots have log degree 0 at depth 2; oscillatory index 1 requires log degree 1 at that depth.",
            "does_not_establish": [
                "the route-B gauge-radical identity",
                "generic-Lambda branch-specialized EE/EX/XX leading coefficients",
                "absence of additional RREF pivot walls or stability of the depth-2 log degrees at deeper order",
                "finite radial norm or a parity-complete selection theorem",
                "stability, scattering, quasinormal modes, ringdown, positivity, particles, or quantum claims",
            ],
        },
        "next_gate": {
            "disposition": "SHORTFALL",
            "missing_dependency": "Construct fraction-free per-branch sourced metric jets, verify vv/vr/angP literally, and evaluate the exact F^v EE/EX/XX leading coefficients and exceptional set.",
            "axial_independence": "No terminal axial conclusion is imported or modified; the independent join imports it directly.",
        },
    }


def build_atlas(certificate: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "black_hole",
        "generated_by": str(PRODUCER.relative_to(ROOT)),
        "generated_by_sha256": _sha256(PRODUCER),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [
            {
                "id": "black_hole.schwarzschild.polar.general_l_disposition",
                "scope": {
                    "theory": "linearized four-dimensional pure Weyl C^2 gravity",
                    "background": "Schwarzschild exterior, symbolic m>0",
                    "boundaries": "formal large-radius fixed-representative Lee-Wald slice density",
                    "charge_sector": "no asymptotic charge or phase-space quotient",
                    "carrier": "polar Einstein image and additional Ricci carriers",
                    "degree": 1,
                    "parity": "polar only",
                    "ell": "all integer ell>=2 through Lambda=ell(ell+1)",
                    "m": "axisymmetric representative with exact irreducible harmonic norms",
                    "k": "formal radial 1/r order",
                    "omega": "real omega!=0",
                },
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "CERTIFIED",
                    "nonlinear": "NOT_APPLICABLE",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": {"status": "CERTIFIED", "statement": "The generic polar Bach carrier has exact zero and -2 i omega rates with three powers on each shell; four finite depth-2 sourced lifts are serialized."},
                    "lee_wald": {"status": "CERTIFIED", "statement": "The arbitrary-profile sphere-integrated F^v bilinear and its exact radial-jet filtration are certified; the branch-specialized EE/EX/XX table is open."},
                    "taub_maps": {"status": "NOT_APPLICABLE", "statement": "No compact second-order Taub map is involved."},
                    "resonance": {"status": "OPEN", "statement": "Finite depth-2 log data are certified, but deeper all-seven compatibility and RREF pivot-wall classification remain open."},
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {"status": "NOT_APPLICABLE", "statement": "No nonlinear solution is evaluated."},
                        "smooth_secular": {"status": "NOT_APPLICABLE", "statement": "No quadratic source is evaluated."},
                        "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No retarded propagator or causal phase space is constructed."},
                    },
                },
                "evidence": [
                    {
                        "path": str(OUTPUT.relative_to(ROOT)),
                        "result_id": certificate["result_id"],
                        "sha256": _sha256(OUTPUT),
                    }
                ],
                "claim_boundary": "This LOCAL-ALGEBRAIC + REDUCED-MODE shortfall certifies the symbolic-Lambda polar harmonic/Bianchi/seven-row reconstruction, universal F^v bilinear and filtration, Bach-carrier powers, and four finite depth-2 sourced-lift pilots. It does not certify all-seven sourced jets, a complete pivot-wall exceptional set, branch-specialized EE/EX/XX coefficients, boundary selection, phase space, stability, particles, positivity, or quantum claims.",
            }
        ],
        "verification_commands": [
            "python3 -m black_hole_programme.phase2.general_l_polar.general_l_polar_disposition --check",
            "python3 -m black_hole_programme.phase2.general_l_polar.verify_general_l_polar_disposition",
            "python3 -m pytest black_hole_programme/phase2/general_l_polar/tests -q",
            "python3 residual_atlas/validate_fragment.py residual_atlas/phase2-black-hole-general-l-polar-disposition-fragment-v1.json",
        ],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build_certificate()
    if args.check:
        _require(_load(OUTPUT) == certificate, "certificate regeneration drift")
        _require(_load(ATLAS) == build_atlas(certificate), "atlas regeneration drift")
    else:
        write_json(OUTPUT, certificate)
        write_json(ATLAS, build_atlas(certificate))
    print("generic-l polar harmonic/Bianchi disposition: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
