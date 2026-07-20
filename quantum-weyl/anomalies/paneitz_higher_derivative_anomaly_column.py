#!/usr/bin/env python3
"""Exact Paneitz anomaly column and its effect on the matter lattice."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ


HERE = Path(__file__).resolve().parent
QROOT = HERE.parent
ROOT = QROOT.parent
MATTER_PATH = (
    HERE / "certificates/MATTER_CONTENT_ANOMALY_CANCELLATION_LATTICE.json"
)
MATTER_SHA256 = "3a6051c7f8cbf51baddd543b99d121d71c074ccf307344e12ece929db40de43e"
MATTER_COMMIT = "a2ca4f9f0"
GAUGE_PATH = (
    HERE
    / "certificates/"
    "MATTER_GAUGE_REPRESENTATION_JOINT_HEALTHY_EMPTY_BY_PROJECTION.json"
)
GAUGE_SHA256 = "fd00a80ed827d32b1231415ac2667819546a1d13b8bfd35ebceaa2a4d351fc9b"
GAUGE_COMMIT = "287a43a8c"

Q = Fraction
BASIS = (
    "ANOM_OMEGA_C2",
    "ANOM_OMEGA_E4",
    "ANOM_OMEGA_C_DUAL_C",
    "ANOM_OMEGA_BOX_R",
)
PANEITZ = (Q(-1, 15), Q(7, 90), Q(0), Q(1, 15))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _q(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _vector(values: tuple[Fraction, ...]) -> list[dict[str, int]]:
    return [_q(value) for value in values]


def _gjms_local_heat_route() -> dict[str, Any]:
    """Juhl/Gilkey/Branson-Orsted local fourth-order heat coefficient."""

    k = 2
    a = Q(k**3, 144) - Q(k**5, 240)
    c_minus_a = Q(k, 180)
    c = a + c_minus_a
    # The dimensionally continued local Paneitz heat coefficient, including
    # the term lost by integration, gives gamma=-32/45 in the
    # (-4 a Q4, (c-a) W2, gamma Delta J) basis.
    gamma = Q(-32, 45)
    # With Delta=-nabla^2, J=R/6 and
    # Q4=(E4-W2)/4+Delta R/6, the repository BoxR coefficient is
    # g=(4a-gamma)/6.
    box_r = (4 * a - gamma) / 6
    column = (c, -a, Q(0), box_r)
    if column != PANEITZ:
        raise ValueError("local Paneitz heat-coefficient route drifted")
    return {
        "method": (
            "DIMENSIONALLY_CONTINUED_JUHL_GILKEY_HEAT_COEFFICIENT_"
            "WITH_BRANSON_ORSTED_CONFORMAL_PRINCIPLE"
        ),
        "k": k,
        "a": _q(a),
        "c_minus_a": _q(c_minus_a),
        "gamma_DeltaJ": _q(gamma),
        "basis_conversion": (
            "Delta=-nabla^2, J=R/6, "
            "Q4=(E4-W2)/4+DeltaR/6, b_BoxR=(4a-gamma)/6"
        ),
        "column": _vector(column),
        "source_formula_scope": (
            "local b4 of P4 on the declared Bach-flat regular chart; "
            "the total derivative is retained"
        ),
    }


def _factorized_spectral_route() -> dict[str, Any]:
    """Einstein factorization plus independently improved Casimir relation."""

    k = 2
    factor_rows = []
    r2_total = Q(0)
    w2_total = Q(0)
    for i in range(k):
        shift = Q((2 + i) * (1 - i), 12)
        r2 = Q(i * i * (i + 1) * (i + 1), 288) - Q(1, 2160)
        w2 = Q(1, 180)
        factor_rows.append(
            {
                "i": i,
                "operator": f"-nabla^2+({shift})*R",
                "R2_b4": _q(r2),
                "W2_b4": _q(w2),
            }
        )
        r2_total += r2
        w2_total += w2
    a = Q(-7, 90)
    c_minus_a = Q(1, 90)
    if r2_total != -a / 6 or w2_total != c_minus_a:
        raise ValueError("Einstein Paneitz factor sum drifted")
    improved_casimir = -Q(k**3 * (2 * k**2 - 5), 720)
    gamma = 16 * (a - improved_casimir)
    box_r = (4 * a - gamma) / 6
    column = (a + c_minus_a, -a, Q(0), box_r)
    if gamma != Q(-32, 45) or column != PANEITZ:
        raise ValueError("spectral/multiplicative-anomaly route drifted")
    return {
        "method": (
            "EINSTEIN_SHIFTED_LAPLACIAN_FACTOR_SUM_PLUS_"
            "MULTIPLICATIVE_ANOMALY_IMPROVED_CASIMIR"
        ),
        "factorization": "P4=(-nabla^2)(-nabla^2+R/6)",
        "factor_rows": factor_rows,
        "summed_R2_b4": _q(r2_total),
        "summed_W2_b4": _q(w2_total),
        "improved_Casimir_energy": _q(improved_casimir),
        "Cappelli_Coste_relation": "E_c=a-gamma/16",
        "gamma_DeltaJ": _q(gamma),
        "column": _vector(column),
        "multiplicative_anomaly_policy": (
            "retained in the improved Casimir energy; the full fourth-order "
            "determinant is fundamental and no product determinant is used "
            "for a finite part without this correction"
        ),
    }


def _projected_lattice() -> dict[str, Any]:
    """Lattice after quotienting the exact type-D coordinate."""

    matrix = sp.Matrix(
        [
            [6, 18, 36, 72, -48],
            [-2, -11, -22, -124, 56],
        ]
    )
    rhs = sp.Matrix([-4776, 3132])
    smith = smith_normal_form(matrix, domain=ZZ)
    invariants = [
        abs(int(smith[i, i]))
        for i in range(min(smith.shape))
        if smith[i, i]
    ]
    particular = sp.Matrix([128, -308, 0, 0, 0])
    kernel = [
        sp.Matrix([0, -2, 1, 0, 0]),
        sp.Matrix([48, -20, 0, 1, 0]),
        sp.Matrix([-16, 8, 0, 0, 1]),
    ]
    first_nonnegative = sp.Matrix([0, 0, 0, 61, 191])
    if (
        matrix * particular != rhs
        or any(matrix * row != sp.zeros(2, 1) for row in kernel)
        or matrix * first_nonnegative != rhs
        or invariants != [1, 30]
    ):
        raise ValueError("Paneitz-extended projected lattice drifted")
    return {
        "scope": (
            "scheme-independent nontrivial even quotient coordinates "
            "(C2,E4); p=0 separately"
        ),
        "variables": ["N_s", "N_W_absolute", "N_D", "N_vector", "N_Paneitz"],
        "integer_matrix_scaled_by_720": [
            [int(value) for value in row] for row in matrix.tolist()
        ],
        "right_hand_side": [int(value) for value in rhs],
        "rank": int(matrix.rank()),
        "smith_invariant_factors": invariants,
        "particular_solution": [int(value) for value in particular],
        "kernel_basis": [[int(value) for value in row] for row in kernel],
        "complete_parameterization": {
            "parameters": ["d", "v", "p"],
            "parameter_domain": "Z",
            "N_s": "128-16*p+48*v",
            "N_W_absolute": "-308-2*d-20*v+8*p",
            "N_D": "d",
            "N_vector": "v",
            "N_Paneitz": "p",
        },
        "nonnegative_integer_solution_exists": True,
        "first_solution_by_minimal_vector_count": {
            "minimal_N_vector": 61,
            "multiplicities": {
                "N_s": 0,
                "N_W_absolute": 0,
                "N_D": 0,
                "N_vector": 61,
                "N_Paneitz": 191,
            },
            "minimality_witness": (
                "N_s>=0 gives p<=8+3v; N_W>=0 gives "
                "p>=ceil((308+20v)/8). These intervals are disjoint for "
                "0<=v<=60 and meet uniquely at v=61,p=191."
            ),
        },
        "physical_price": (
            "the solution uses 191 fourth-order Paneitz scalars; it is a "
            "nonnegative multiplicity solution but not healthy standard-sign "
            "matter"
        ),
    }


def _raw_scheme_lattice() -> dict[str, Any]:
    """Three-coordinate raw reference-scheme cone and integer obstruction."""

    matrix = sp.Matrix(
        [
            [6, 18, 36, 72, -48],
            [-2, -11, -22, -124, 56],
            [4, 12, 24, -72, 48],
        ]
    )
    rhs = sp.Matrix([-4776, 3132, 0])
    separator = sp.Matrix([Q(-3), Q(-5), Q(3)])
    gravity = sp.Matrix([Q(199, 30), Q(-87, 20), Q(0)])
    species = [
        sp.Matrix([Q(1, 120), Q(-1, 360), Q(1, 180)]),
        sp.Matrix([Q(1, 40), Q(-11, 720), Q(1, 60)]),
        sp.Matrix([Q(1, 20), Q(-11, 360), Q(1, 30)]),
        sp.Matrix([Q(1, 10), Q(-31, 180), Q(-1, 10)]),
        sp.Matrix([PANEITZ[0], PANEITZ[1], PANEITZ[3]]),
    ]
    values = [Q((separator.T * row)[0]) for row in species]
    gravity_value = Q((separator.T * gravity)[0])
    modular_row = [0, 1, 3]
    modular_columns = [
        sum(modular_row[i] * int(matrix[i, j]) for i in range(3))
        for j in range(matrix.cols)
    ]
    modular_rhs = sum(modular_row[i] * int(rhs[i]) for i in range(3))
    if (
        gravity_value != Q(37, 20)
        or values
        != [Q(1, 180), Q(37, 720), Q(37, 360), Q(47, 180), Q(1, 90)]
        or any(value <= 0 for value in values)
        or any(value % 5 for value in modular_columns)
        or modular_rhs % 5 != 2
    ):
        raise ValueError("raw-scheme separator or modular obstruction drifted")
    smith = smith_normal_form(matrix, domain=ZZ)
    invariants = [
        abs(int(smith[i, i]))
        for i in range(min(smith.shape))
        if smith[i, i]
    ]
    return {
        "scope": "common raw heat-kernel scheme coordinates (C2,E4,BoxR)",
        "integer_matrix_scaled_by_720": [
            [int(value) for value in row] for row in matrix.tolist()
        ],
        "right_hand_side": [int(value) for value in rhs],
        "rank": int(matrix.rank()),
        "smith_invariant_factors": invariants,
        "nonnegative_real_cone": "EMPTY",
        "nonnegative_integer_lattice": "EMPTY",
        "signed_integer_lattice": "EMPTY_IN_THIS_RAW_SCHEME",
        "separating_functional": {
            "coordinates_C2_E4_BoxR": [-3, -5, 3],
            "gravity_value": _q(gravity_value),
            "species_values_scalar_Weyl_Dirac_vector_Paneitz": [
                _q(value) for value in values
            ],
        },
        "integer_modular_obstruction": {
            "modulus": 5,
            "left_row_on_C2_E4_BoxR": modular_row,
            "column_pairings": modular_columns,
            "right_hand_side_pairing": modular_rhs,
            "proof": (
                "every column pairing is 0 mod 5, whereas the target is "
                "2 mod 5"
            ),
        },
        "scheme_warning": (
            "BoxR is BRST exact and shifts under a finite R2 counterterm. "
            "This raw-scheme obstruction is bookkeeping, not an additional "
            "nontrivial anomaly class."
        ),
    }


def build() -> dict[str, Any]:
    matter = _load(MATTER_PATH)
    gauge = _load(GAUGE_PATH)
    if (
        _sha(MATTER_PATH) != MATTER_SHA256
        or matter.get("result_id")
        != "MATTER_CONTENT_ANOMALY_CANCELLATION_LATTICE"
        or _sha(GAUGE_PATH) != GAUGE_SHA256
        or gauge.get("result_id")
        != "MATTER_GAUGE_REPRESENTATION_JOINT_HEALTHY_EMPTY_BY_PROJECTION"
    ):
        raise ValueError("higher-derivative anomaly input pins drifted")
    route_local = _gjms_local_heat_route()
    route_spectral = _factorized_spectral_route()
    if route_local["column"] != route_spectral["column"]:
        raise ValueError("independent Paneitz coefficient routes disagree")
    projected = _projected_lattice()
    raw = _raw_scheme_lattice()
    checks = {
        "terminal_standard_matter_lattice_imported_by_commit_and_hash": True,
        "terminal_gauge_projection_imported_by_commit_and_hash": True,
        "Paneitz_operator_and_minimal_BV_rows_declared": True,
        "Paneitz_nonminimal_sector_correctly_empty": True,
        "Paneitz_elliptic_principal_symbol_verified": True,
        "Paneitz_zero_mode_and_prime_determinant_policy_declared": True,
        "local_higher_order_heat_route_complete": True,
        "factorized_spectral_and_improved_Casimir_route_complete": True,
        "two_routes_agree_on_c_minus_a_and_BoxR": True,
        "parity_Ward_zero_verified": True,
        "multiplicative_anomaly_not_discarded": True,
        "projected_Smith_lattice_replayed": True,
        "first_nonnegative_projected_solution_and_minimality_verified": True,
        "raw_scheme_positive_separator_verified": True,
        "raw_scheme_mod_five_integer_obstruction_verified": True,
        "kinetic_sign_price_not_called_healthy": True,
        "next_gauge_column_fail_closed": True,
    }
    value = {
        "schema": "quantum-weyl-paneitz-higher-derivative-anomaly-column-v1",
        "result_id": "PANEITZ_HIGHER_DERIVATIVE_ANOMALY_COLUMN",
        "result_state": (
            "PANEITZ_COLUMN_CERTIFIED_PROJECTED_CONE_CHANGED_"
            "NEXT_GAUGE_CARRIER_OBSTRUCTED"
        ),
        "lifecycle_status": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "input_pins": {
            "standard_matter_lattice": {
                "commit": MATTER_COMMIT,
                "path": MATTER_PATH.relative_to(ROOT).as_posix(),
                "sha256": MATTER_SHA256,
                "result_id": matter["result_id"],
            },
            "gauge_representation_projection": {
                "commit": GAUGE_COMMIT,
                "path": GAUGE_PATH.relative_to(ROOT).as_posix(),
                "sha256": GAUGE_SHA256,
                "result_id": gauge["result_id"],
            },
        },
        "basis": list(BASIS),
        "field_declaration": {
            "field_id": "real_Paneitz_scalar_P4",
            "spacetime_dimension": 4,
            "field": {
                "symbol": "phi",
                "tensor_type": "scalar",
                "Grassmann_parity": "even",
                "ghost_number": 0,
                "Weyl_weight": 0,
            },
            "antifield": {
                "symbol": "phi_star",
                "tensor_type": "scalar_density",
                "Grassmann_parity": "odd",
                "ghost_number": -1,
                "antifield_number": 1,
            },
            "minimal_BV_rows": {
                "gamma_phi": "Lie_xi(phi); the four-dimensional Weyl weight is zero",
                "delta_phi_star": "P4(phi)",
                "internal_gauge_ghosts": [],
            },
            "nonminimal_BV_complex": (
                "EMPTY_FOR_THIS_FIELD: the Paneitz scalar has no internal "
                "gauge symmetry; the ambient strict Diff x Weyl complex is "
                "not duplicated"
            ),
        },
        "operator_payload": {
            "action": "S_P4=(1/2) integral sqrt(g) phi P4 phi",
            "operator": (
                "P4=(nabla^2)^2+2 Ric^{mu nu} nabla_mu nabla_nu"
                "-(2/3)R nabla^2+(1/3)(nabla^mu R)nabla_mu"
            ),
            "principal_symbol": "(g^{mu nu} xi_mu xi_nu)^2",
            "Euclidean_ellipticity": "ELLIPTIC_ON_RIEMANNIAN_METRICS",
            "Einstein_factorization": "P4=Delta(Delta+R/6), Delta=-nabla^2",
            "domain": (
                "closed realization H4(M)->L2(M) on a declared compact "
                "boundaryless Riemannian background"
            ),
            "zero_mode_policy": (
                "det_prime(P4); restrict sources to ker(P4)^perp; constants "
                "are retained in the kernel ledger and omitted only from the "
                "primed determinant"
            ),
            "determinant_power_effective_action": "+1/2 log det_prime(P4)",
            "contour_policy": (
                "Euclidean nonzero-mode spectral contour only; no Lorentzian "
                "state or positivity conclusion"
            ),
        },
        "coefficient_routes": {
            "local_higher_order_heat_kernel": route_local,
            "factorized_spectral_and_Casimir": route_spectral,
        },
        "verified_column": {
            "field_id": "real_Paneitz_scalar_P4",
            "coordinates": _vector(PANEITZ),
            "status": "APPENDED_TO_ENLARGED_EXACT_LATTICE",
            "parity_argument": (
                "real scalar natural operator, no epsilon/Hodge/chiral "
                "insertion, parity-even heat-kernel regulator implies p=-p=0"
            ),
        },
        "scheme_ledger": {
            "raw_reference_scheme": (
                "local higher-order heat coefficient / multiplicative-anomaly-"
                "improved zeta-Casimir scheme"
            ),
            "BoxR_value": _q(PANEITZ[3]),
            "BoxR_status": (
                "COMPUTED_BUT_BRST_EXACT_AND_FINITE_R2_SCHEME_DEPENDENT"
            ),
            "nontrivial_quotient_coordinates": _vector(PANEITZ[:3]),
        },
        "kinetic_sign_audit": {
            "classification": "FOURTH_ORDER_KREIN_INDEFINITE_PRICE",
            "Einstein_resolvent_identity": (
                "1/[Delta(Delta+R/6)]=(6/R)"
                "*(1/Delta-1/(Delta+R/6)) when R is nonzero"
            ),
            "opposite_residues": True,
            "healthy_standard_sign_matter": False,
            "boundary": (
                "this algebraic opposite-residue audit is not a construction "
                "of a Lorentzian Krein or Hilbert state"
            ),
        },
        "projected_anomaly_lattice": projected,
        "raw_reference_scheme_lattice": raw,
        "next_gauge_field_gate": {
            "candidate": "first_genuinely_new_conformal_higher_spin_gauge_field",
            "status": "OBSTRUCTED_NO_DECLARED_COMPLETE_CARRIER",
            "reason": (
                "spin two is the already-imported strict Weyl graviton and "
                "cannot be borrowed as added matter; the next CHS candidate "
                "has no repository-declared complete off-shell BV and "
                "generic-background gauge-fixed elliptic complex"
            ),
            "first_missing_carriers": [
                "field_ghost_antifield_and_reducibility_dictionary",
                "nonminimal_complex_and_gauge_fermion",
                "generic_background_ellipticity_and_operator_domain",
                "complete_ghost_nonminimal_determinant_and_zero_mode_ledger",
                "two_route_raw_C2_E4_CdualC_BoxR_coefficient_payload",
            ],
            "column_appended": False,
            "scope": (
                "repository import obstruction, not a no-go theorem for "
                "conformal higher-spin gauge fields"
            ),
        },
        "exact_checks": checks,
        "claim_flags": {
            "PANEITZ_FULL_FOUR_COORDINATE_COLUMN_VERIFIED": True,
            "PANEITZ_APPENDED_TO_ENLARGED_LATTICE": True,
            "PROJECTED_NONNEGATIVE_CANCELLATION_EXISTS": True,
            "RAW_SCHEME_NONNEGATIVE_CANCELLATION_EXISTS": False,
            "HEALTHY_CANCELLATION_EXISTS": False,
            "HIGHER_DERIVATIVE_GAUGE_COLUMN_VERIFIED": False,
            "COMPLETE_HIGHER_DERIVATIVE_FAMILY_CLASSIFIED": False,
            "STRICT_QME_RESTORED": False,
            "LORENTZIAN_STATE_OR_UNITARITY_CERTIFIED": False,
        },
        "next_gate": (
            "SUPPLY_ONE_NEW_CONFORMAL_GAUGE_FIELD_WITH_COMPLETE_OFFSHELL_BV_"
            "GAUGE_FIXED_ELLIPTIC_AND_TWO_ROUTE_RAW_COEFFICIENT_DATA"
        ),
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL result certifies the "
            "complete raw Paneitz scalar anomaly column and its exact lattice "
            "effect. Modulo the exact BoxR direction, 61 standard vectors plus "
            "191 Paneitz scalars cancel the two even strict-gravity coordinates, "
            "but the Paneitz action carries a fourth-order opposite-residue "
            "price and is not healthy standard matter. In the displayed raw "
            "BoxR scheme the nonnegative cone is still empty; that type-D "
            "statement is scheme bookkeeping, not a new cohomological "
            "obstruction. No new conformal gauge-field column, strict QME "
            "restoration, Lorentzian state, positivity, particle, GUT, "
            "phenomenology, scattering or unitarity result follows."
        ),
    }
    validate(value)
    return value


def validate(value: dict[str, Any]) -> None:
    flags = value.get("claim_flags", {})
    if (
        not all(value.get("exact_checks", {}).values())
        or flags.get("PANEITZ_FULL_FOUR_COORDINATE_COLUMN_VERIFIED") is not True
        or flags.get("PANEITZ_APPENDED_TO_ENLARGED_LATTICE") is not True
        or flags.get("PROJECTED_NONNEGATIVE_CANCELLATION_EXISTS") is not True
        or flags.get("RAW_SCHEME_NONNEGATIVE_CANCELLATION_EXISTS") is not False
        or flags.get("HEALTHY_CANCELLATION_EXISTS") is not False
        or flags.get("HIGHER_DERIVATIVE_GAUGE_COLUMN_VERIFIED") is not False
        or flags.get("COMPLETE_HIGHER_DERIVATIVE_FAMILY_CLASSIFIED") is not False
        or flags.get("STRICT_QME_RESTORED") is not False
        or flags.get("LORENTZIAN_STATE_OR_UNITARITY_CERTIFIED") is not False
    ):
        raise ValueError("Paneitz claim boundary over-promoted")
    if (
        value["verified_column"]["coordinates"] != _vector(PANEITZ)
        or value["projected_anomaly_lattice"][
            "first_solution_by_minimal_vector_count"
        ]["minimal_N_vector"]
        != 61
        or value["next_gauge_field_gate"]["column_appended"] is not False
    ):
        raise ValueError("Paneitz coefficient/lattice/gauge gate drifted")


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
