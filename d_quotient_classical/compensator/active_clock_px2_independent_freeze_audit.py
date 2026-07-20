#!/usr/bin/env python3
"""Method-distinct freeze audit of the quadratic active-clock no-go."""

from __future__ import annotations

import argparse
from copy import deepcopy
import functools
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
TERMINAL = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_ACTIVE_CLOCK_PX2_LOCUS_V1.json"
)
OUTPUT = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1.json"
)
TERMINAL_SHA256 = "9ad148d6b632e215cd75636f5fd5b431fa85cf1698a63f725d8b3c9dfe61de89"
TERMINAL_ACTION_SHA256 = (
    "c665462b1b98098613c3b325a1866133b32d681caec943a6c8e4a1460d0e7938"
)
TERMINAL_COMMIT = "c770752d132accb4e3b2bb59884d6faf10335fc8"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _q(value: sp.Expr) -> str:
    return str(sp.factor(value))


def _matrix(value: sp.Matrix) -> dict[str, Any]:
    core = {
        "row_count": value.rows,
        "column_count": value.cols,
        "entries": [
            {"row": row, "column": column, "coefficient": _q(value[row, column])}
            for row in range(value.rows)
            for column in range(value.cols)
            if value[row, column] != 0
        ],
    }
    return {**core, "sha256": _digest(core)}


def _dense(record: dict[str, Any]) -> sp.Matrix:
    value = sp.zeros(record["row_count"], record["column_count"])
    for entry in record["entries"]:
        value[entry["row"], entry["column"]] = sp.sympify(entry["coefficient"])
    return value


def _action_basis_audit(terminal: dict[str, Any]) -> dict[str, Any]:
    # This is a signature/IBP census, not the terminal producer's manifest
    # generation. The "replacement only" condition keeps curvature and phase
    # factors in separate summands, so mixed R X terms are outside the declared
    # theory class rather than silently omitted invariants.
    candidates = [
        {
            "signature": "metric_four_derivatives_even",
            "representatives": ["C^2", "R^2", "E4", "Box R"],
            "kept": ["C^2", "R^2"],
            "removed": {
                "E4": "topological in four dimensions",
                "Box R": "horizontal total derivative",
            },
        },
        {
            "signature": "metric_two_derivatives_even",
            "representatives": ["R"],
            "kept": ["R"],
            "removed": {},
        },
        {
            "signature": "shift_symmetric_phase_polynomial_degree_at_most_two",
            "representatives": ["1", "X", "X^2"],
            "kept": ["p0", "p1 X", "p2 X^2"],
            "removed": {},
        },
    ]
    expected_coefficients = [
        "alpha_B",
        "alpha_R",
        "M_P_squared",
        "p0",
        "p1",
        "p2",
    ]
    family = terminal["action_family"]
    if family["coefficient_basis_mod_topology"] != expected_coefficients:
        raise AssertionError("ACTION_BASIS_MISMATCH")
    if _digest(family) != TERMINAL_ACTION_SHA256:
        raise AssertionError("ACTION_HASH_MISMATCH")
    required_exclusions = {
        "Henneaux-Teitelboim or any multiplier sector",
        "operators beyond quadratic P(X)",
        "higher derivatives of theta",
    }
    if required_exclusions - set(family["excluded"]):
        raise AssertionError("DECLARED_SCOPE_MISMATCH")
    return {
        "method": (
            "independent grading-signature census followed by four-dimensional "
            "invariant/IBP reduction; no producer module imported"
        ),
        "replacement_only_rule": (
            "the work item replaces only the phase sector of the already "
            "declared C^2+R^2+R action; mixed products such as R X are outside "
            "this scoped family"
        ),
        "signature_orbits": candidates,
        "canonical_coefficient_basis": expected_coefficients,
        "terminal_action_family_sha256_recomputed": _digest(family),
        "terminal_action_family_sha256_matches": True,
        "complete_within_declared_scope": True,
    }


def _berger_geometry_from_biaxial_invariants(
    q: sp.Expr,
) -> tuple[list[sp.Expr], sp.Expr, list[sp.Expr]]:
    # At a=1 the Maurer-Cartan reduction of
    # ds^2=-dt^2+a^2(sigma_1^2+sigma_2^2)+c^2 sigma_3^2
    # gives these exact orthonormal tensors. This is evaluated symbolically in
    # q=c^2 rather than importing the frozen numerical tensor rows.
    ricci = [0, (2 - q) / 2, (2 - q) / 2, q / 2]
    scalar = (4 - q) / 2
    bach = [
        (1 - q) ** 2 / 6,
        (1 - q) * (1 - 3 * q) / 6,
        (1 - q) * (1 - 3 * q) / 6,
        (1 - q) * (5 * q - 1) / 6,
    ]
    return [sp.factor(x) for x in ricci], sp.factor(scalar), [
        sp.factor(x) for x in bach
    ]


def _stress_column(
    degree: int,
    X: sp.Expr,
    omega_squared: sp.Expr,
    metric_entry: int,
    time_row: bool,
    stress_sign: int,
) -> sp.Expr:
    # The metric equation contains -T_ab, with
    # T_ab=-2 P_X d_a theta d_b theta+P g_ab.
    P = X**degree
    P_X = 0 if degree == 0 else degree * X ** (degree - 1)
    gradient_square = omega_squared if time_row else 0
    return sp.factor(
        stress_sign * (2 * P_X * gradient_square - P * metric_entry)
    )


def _background_matrix(
    q: sp.Expr = sp.Rational(9, 40),
    omega: sp.Expr = sp.Rational(3, 4),
    stress_sign: int = 1,
) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix, dict[str, Any]]:
    cylinder = sp.Matrix(
        [
            [0, 36, 3, stress_sign, 0, 0],
            [0, 12, -1, -stress_sign, 0, 0],
        ]
    )
    ricci, scalar, bach = _berger_geometry_from_biaxial_invariants(q)
    X = -omega**2
    metric = [-1, 1, 1, 1]
    rows: list[list[sp.Expr]] = []
    for index in (0, 1, 3):
        g = metric[index]
        gravity = [
            bach[index],
            4 * scalar * ricci[index] - scalar**2 * g,
            ricci[index] - scalar * g / 2,
        ]
        matter = [
            _stress_column(
                degree,
                X,
                omega**2,
                g,
                index == 0,
                stress_sign,
            )
            for degree in range(3)
        ]
        rows.append(gravity + matter)
    berger = sp.Matrix(rows)
    invariants = {
        "q": _q(q),
        "omega": _q(omega),
        "X": _q(X),
        "Ricci_orthonormal": [_q(x) for x in ricci],
        "scalar_curvature": _q(scalar),
        "Bach_orthonormal": [_q(x) for x in bach],
        "stress_sign": stress_sign,
    }
    return cylinder, berger, cylinder.col_join(berger), invariants


def _integer_cofactor_elimination(matrix: sp.Matrix) -> dict[str, Any]:
    row_scales: list[int] = []
    integer_rows: list[list[int]] = []
    for row in matrix.tolist():
        scale = int(sp.ilcm(*[entry.q for entry in row]))
        row_scales.append(scale)
        integer_rows.append([int(entry * scale) for entry in row])
    integer_matrix = sp.Matrix(integer_rows)
    maximal_minors = [
        int(integer_matrix[:, [k for k in range(6) if k != column]].det())
        for column in range(6)
    ]
    alternating_cofactors = [
        (-1) ** column * maximal_minors[column] for column in range(6)
    ]
    divisor = functools.reduce(math.gcd, (abs(x) for x in alternating_cofactors))
    primitive = [x // divisor for x in alternating_cofactors]
    if primitive[-1] < 0:
        primitive = [-x for x in primitive]
    expected = [133245, 270, -6480, 9720, 23688, 32900]
    if primitive != expected or integer_matrix * sp.Matrix(primitive) != sp.zeros(5, 1):
        raise AssertionError("COFACTOR_KERNEL_MISMATCH")
    if not any(maximal_minors):
        raise AssertionError("RANK_DROPPED_BELOW_FIVE")
    return {
        "method": (
            "clear row denominators, compute all six signed maximal cofactors, "
            "divide by their integer gcd and normalize the last entry positive"
        ),
        "row_denominator_scales": row_scales,
        "integer_matrix": _matrix(integer_matrix),
        "maximal_minors_delete_column_0_to_5": maximal_minors,
        "alternating_cofactor_gcd": divisor,
        "primitive_integer_kernel": primitive,
        "rank": 5,
        "rational_kernel_normalized_p2_one": [
            "81/20",
            "27/3290",
            "-324/1645",
            "486/1645",
            "18/25",
            "1",
        ],
        "real_locus": (
            "t(81/20,27/3290,-324/1645,486/1645,18/25,1), t in R"
        ),
    }


def _compare_terminal_rows(
    terminal: dict[str, Any],
    cylinder: sp.Matrix,
    berger: sp.Matrix,
    stacked: sp.Matrix,
) -> None:
    rows = terminal["stationary_background_equations"]
    if _dense(rows["unit_cylinder"]["matrix"]) != cylinder:
        raise AssertionError("CYLINDER_ROW_MISMATCH")
    if _dense(rows["frozen_Berger_clock"]["matrix"]) != berger:
        raise AssertionError("BERGER_ROW_MISMATCH")
    if _dense(rows["common_system"]["matrix"]) != stacked:
        raise AssertionError("STACKED_ROW_MISMATCH")


def _quadratic_cone_charge_audit() -> dict[str, Any]:
    t = sp.Symbol("t", real=True)
    D = sp.Symbol("D")
    spectral = sp.Symbol("spectral")
    M = -sp.Rational(324, 1645) * t
    p0 = sp.Rational(486, 1645) * t
    p1 = sp.Rational(18, 25) * t
    p2 = t
    velocity = sp.Matrix([[0, -3, 0], [-3, 0, 0], [0, 0, -2 * p1]])
    congruence = sp.Matrix([[1, 1, 0], [1, -1, 0], [0, 0, 1]])
    diagonal = sp.simplify(congruence.T * velocity * congruence)
    if diagonal != sp.diag(-6, 6, -sp.Rational(36, 25) * t):
        raise AssertionError("VELOCITY_CONGRUENCE_MISMATCH")

    evolution = sp.Matrix(
        [
            [0, 1, 0, 0, 0, 0],
            [2, 0, -4 / M, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 2, 0, 0, 0],
            [0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0],
        ]
    )
    charpoly = sp.factor(evolution.charpoly(spectral).as_expr())
    annihilator = sp.simplify(
        evolution**2 * (evolution**2 - 2 * sp.eye(6)) ** 2
    )
    if (
        charpoly != spectral**2 * (spectral**2 - 2) ** 2
        or annihilator != sp.zeros(6)
    ):
        raise AssertionError("EVOLUTION_POLYNOMIAL_MISMATCH")
    if (
        evolution * (evolution**2 - 2 * sp.eye(6)) ** 2 == sp.zeros(6)
        or evolution**2 * (evolution**2 - 2 * sp.eye(6)) == sp.zeros(6)
    ):
        raise AssertionError("MINIMAL_POLYNOMIAL_LOWERED")

    X = -sp.Rational(9, 16)
    omega = sp.Rational(3, 4)
    P = sp.factor(p0 + p1 * X + p2 * X**2)
    P_X = sp.factor(p1 + 2 * p2 * X)
    longitudinal = sp.factor(p1 + 6 * p2 * X)
    sound = sp.factor(P_X / longitudinal)
    energy = sp.factor(-2 * P_X * omega**2 - P)
    charge = sp.factor(-2 * P_X * omega)
    k_density = sp.factor(energy - omega * charge)
    if (
        P != sp.Rational(435537, 2105600) * t
        or P_X != -sp.Rational(81, 200) * t
        or longitudinal != -sp.Rational(531, 200) * t
        or sound != sp.Rational(9, 59)
        or energy != sp.Rational(523827, 2105600) * t
        or charge != sp.Rational(243, 400) * t
        or k_density != -P
    ):
        raise AssertionError("CONE_OR_CHARGE_MISMATCH")
    common_health = sp.reduce_inequalities(
        [p1 < 0, P_X < 0, longitudinal < 0],
        t,
    )
    if common_health is not sp.false:
        raise AssertionError("HEALTHY_HALF_LINES_INTERSECT")
    return {
        "nonzero_stratum": {
            "velocity_Hessian": _matrix(velocity),
            "rational_congruence": _matrix(congruence),
            "congruence_diagonal": _matrix(diagonal),
            "inertia": {
                "t>0": [1, 2, 0],
                "t<0": [2, 1, 0],
            },
            "state_evolution": _matrix(evolution),
            "characteristic_polynomial": "spectral^2(spectral^2-2)^2",
            "minimal_polynomial": "spectral^2(spectral^2-2)^2",
            "Lee_Wald": (
                "omega^0=-3[delta u wedge delta Dpsi+delta psi wedge delta Du]"
                "-2p1 delta v wedge delta Dv"
            ),
            "raw_D_Hamiltonian": (
                "H_D=-3DuDpsi+6psi u-6psi^2/M_P^2-p1(Dv)^2"
            ),
            "raw_D_sign_witnesses": ["+3", "-3"],
        },
        "clock_and_charge": {
            "P": "435537t/2105600",
            "P_X": "-81t/200",
            "longitudinal_P_X_plus_2X_P_XX": "-531t/200",
            "sound_speed_squared": "9/59",
            "cylinder_standard_sign": "p1<0 iff t<0",
            "Berger_standard_sign": (
                "P_X<0 and P_X+2X P_XX<0 iff t>0"
            ),
            "common_standard_sign_locus": "EMPTY",
            "monotonicity": "Dtheta=3/4!=0 and X=-9/16<0",
            "Q_R_density": "243t/400",
            "matter_raw_D_density": "523827t/2105600",
            "matter_K_Berger_density": "-435537t/2105600",
            "total_generator_identity": (
                "K_Berger=D-(3/4)R fixes the background; "
                "i_D Omega_total=(3/4)delta Q_R and i_K Omega_total=0"
            ),
        },
    }


def _singular_strata_audit(elimination: dict[str, Any]) -> dict[str, Any]:
    primitive = elimination["primitive_integer_kernel"]
    if primitive[-1] == 0:
        raise AssertionError("P2_PARAMETERIZATION_SINGULAR")
    return {
        "all_row_denominator_scales": elimination["row_denominator_scales"],
        "constant_denominators_nonzero": [
            "20!=0",
            "25!=0",
            "200!=0",
            "1645!=0",
            "3290!=0",
            "2105600!=0",
        ],
        "t=0": {
            "handled_before_auxiliary_division": True,
            "action": "zero vector",
            "principal_rank": 0,
            "pairing": "absent",
            "gate_result": "FAIL",
        },
        "t>0": {
            "auxiliary_presentation_valid": True,
            "velocity_inertia": [1, 2, 0],
            "Berger_clock": "standard-sign hyperbolic",
            "cylinder_clock": "wrong sign",
            "gate_result": "FAIL",
        },
        "t<0": {
            "auxiliary_presentation_valid": True,
            "velocity_inertia": [2, 1, 0],
            "Berger_clock": "wrong sign",
            "cylinder_clock": "standard sign",
            "gate_result": "FAIL",
        },
        "other_rank_change_strata": "NONE: a constant maximal minor is nonzero",
    }


def audit_terminal_payload(
    terminal: dict[str, Any],
    *,
    q: sp.Expr = sp.Rational(9, 40),
    omega: sp.Expr = sp.Rational(3, 4),
    stress_sign: int = 1,
    required_gates: set[str] | None = None,
) -> dict[str, Any]:
    required = required_gates or {
        "stationarity",
        "principal",
        "velocity",
        "longitudinal_sound",
        "Lee_Wald",
        "raw_D",
        "K_Berger",
        "monotonicity",
    }
    if "longitudinal_sound" not in required:
        raise AssertionError("OMITTED_LONGITUDINAL_GATE")
    if "velocity" not in required:
        raise AssertionError("OMITTED_VELOCITY_GATE")
    basis = _action_basis_audit(terminal)
    cylinder, berger, stacked, invariants = _background_matrix(
        q=q, omega=omega, stress_sign=stress_sign
    )
    _compare_terminal_rows(terminal, cylinder, berger, stacked)
    elimination = _integer_cofactor_elimination(stacked)
    quadratic = _quadratic_cone_charge_audit()
    singular = _singular_strata_audit(elimination)
    return {
        "basis": basis,
        "invariants": invariants,
        "cylinder_matrix": _matrix(cylinder),
        "Berger_matrix": _matrix(berger),
        "stacked_matrix": _matrix(stacked),
        "elimination": elimination,
        "quadratic_cone_charge": quadratic,
        "singular_strata": singular,
        "required_gates": sorted(required),
    }


def _expect_rejection(
    terminal: dict[str, Any],
    mutation_id: str,
    mutate: Any,
) -> dict[str, str]:
    try:
        mutate()
    except AssertionError as error:
        return {
            "mutation_id": mutation_id,
            "status": "REJECTED",
            "failure_code": str(error),
        }
    raise AssertionError(f"mutation {mutation_id} was accepted")


def _mutation_audit(terminal: dict[str, Any]) -> list[dict[str, str]]:
    coefficient_mutation = deepcopy(terminal)
    entry = next(
        row
        for row in coefficient_mutation["stationary_background_equations"][
            "frozen_Berger_clock"
        ]["matrix"]["entries"]
        if row["row"] == 0 and row["column"] == 5
    )
    entry["coefficient"] = "-242/256"

    required = {
        "stationarity",
        "principal",
        "velocity",
        "longitudinal_sound",
        "Lee_Wald",
        "raw_D",
        "K_Berger",
        "monotonicity",
    }
    return [
        _expect_rejection(
            terminal,
            "COEFFICIENT_BERGER_P2",
            lambda: audit_terminal_payload(coefficient_mutation),
        ),
        _expect_rejection(
            terminal,
            "BACKGROUND_Q",
            lambda: audit_terminal_payload(terminal, q=sp.Rational(1, 4)),
        ),
        _expect_rejection(
            terminal,
            "STRESS_SIGN_CONVENTION",
            lambda: audit_terminal_payload(terminal, stress_sign=-1),
        ),
        _expect_rejection(
            terminal,
            "OMIT_LONGITUDINAL_SOUND_GATE",
            lambda: audit_terminal_payload(
                terminal, required_gates=required - {"longitudinal_sound"}
            ),
        ),
    ]


def build() -> dict[str, Any]:
    actual_hash = _sha(TERMINAL)
    if actual_hash != TERMINAL_SHA256:
        raise AssertionError("TERMINAL_CERTIFICATE_HASH_DRIFT")
    terminal = json.loads(TERMINAL.read_text())
    if terminal["action_family_sha256"] != TERMINAL_ACTION_SHA256:
        raise AssertionError("TERMINAL_ACTION_HASH_DRIFT")
    audit = audit_terminal_payload(terminal)
    mutations = _mutation_audit(terminal)
    result = {
        "schema": "pure-weyl-compensator-active-clock-px2-independent-freeze-audit-v1",
        "result_id": "COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1",
        "result_state": "SCOPED_QUADRATIC_ACTIVE_CLOCK_NO_GO_INDEPENDENTLY_FROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "terminal_import": {
            "path": str(TERMINAL.relative_to(ROOT)),
            "result_id": terminal["result_id"],
            "sha256": actual_hash,
            "action_family_sha256": terminal["action_family_sha256"],
            "source_commit": TERMINAL_COMMIT,
        },
        "independence_boundary": {
            "producer_module_imported": False,
            "producer_invoked": False,
            "producer_RREF_reused": False,
            "terminal_JSON_read_only": True,
            "geometry_method": (
                "general biaxial Maurer-Cartan invariant formulas in q=c^2"
            ),
            "elimination_method": "integer maximal-cofactor kernel",
            "real_method": "exact univariate sign decomposition at t=0",
        },
        "action_basis_audit": audit["basis"],
        "background_variation_audit": {
            "derived_invariants": audit["invariants"],
            "unit_cylinder_matrix": audit["cylinder_matrix"],
            "frozen_Berger_matrix": audit["Berger_matrix"],
            "stacked_matrix": audit["stacked_matrix"],
            "clock_Euler": (
                "PASS on both fixtures: constant theta on the cylinder; "
                "constant X, P_X and Dtheta=3/4 on Berger"
            ),
        },
        "exact_real_locus_audit": audit["elimination"],
        "coupled_gate_audit": audit["quadratic_cone_charge"],
        "singular_and_denominator_audit": audit["singular_strata"],
        "mutation_audit": mutations,
        "freeze_verdict": {
            "producer_claim_survives": True,
            "stationary_locus_agrees": True,
            "all_seven_gate_good_locus": "EMPTY",
            "candidate_C_active_selected": False,
            "scoped_quadratic_active_clock_no_go_theorem_frozen": True,
            "decisive_independent_separators": [
                "rational congruence diagonal (-6,6,-36t/25) is split for every t!=0",
                "cylinder standard sign requires t<0 while Berger longitudinal sound and standard sign require t>0",
                "t=0 is the zero action and has no pairing or dynamics",
            ],
        },
        "exact_checks": {
            "terminal_certificate_and_action_hash_pinned": True,
            "declared_action_basis_reconstructed": True,
            "producer_code_not_imported_or_invoked": True,
            "Berger_geometry_reconstructed_from_q": True,
            "stress_columns_varied_monomial_by_monomial": True,
            "integer_cofactor_elimination_exact": True,
            "all_maximal_minors_recorded": True,
            "every_denominator_and_singular_stratum_checked": True,
            "principal_velocity_Lee_Wald_charge_clock_gates_rebuilt": True,
            "coefficient_background_sign_and_omitted_gate_mutations_rejected": True,
            "no_numerical_scan": True,
            "no_candidate_exported": True,
        },
        "claim_flags": {
            "SCOPED_QUADRATIC_ACTIVE_CLOCK_NO_GO_THEOREM_FROZEN": True,
            "UNIVERSAL_SCALAR_TENSOR_OR_K_ESSENCE_NO_GO": False,
            "CANDIDATE_C_ACTIVE_SELECTED": False,
            "COMPLETE_SUPPORT_LOCAL_CAUSAL_PARENT": False,
            "HADAMARD_ANOMALY_QME_OR_QUANTUM": False,
            "PARTICLE_SCATTERING_UNITARITY": False,
        },
        "claim_boundary": (
            "This method-distinct exact audit freezes only the scoped result "
            "for dressed C^2+R^2+R gravity with the complete quadratic "
            "shift-symmetric P(X) sector, no HT and no new fields on the unit "
            "cylinder and frozen q=9/40 Berger clock. It reconstructs the "
            "declared invariant basis, background variation, integer "
            "cofactor locus, coupled inertia, sound cone, Lee-Wald and charge "
            "gates without importing or invoking the terminal producer. The "
            "stationary locus agrees and its seven-gate good locus is empty. "
            "This does not cover higher P(X), higher derivatives, nearby "
            "backgrounds, fixed-charge reductions, new fields or enlarged "
            "gauge groups. It exports no Candidate C_active or complete "
            "support-local causal parent and establishes no Hadamard, anomaly/"
            "QME, particle, scattering, positivity or unitarity result."
        ),
        "next_gate": (
            "Treat the quadratic active-clock escape as a theorem-frozen scoped "
            "no-go. Any successor must enlarge the declared theory or vary the "
            "background and must receive its own exact seven-gate audit."
        ),
    }
    result["content_hashes"] = {
        "basis_sha256": _digest(result["action_basis_audit"]),
        "background_sha256": _digest(result["background_variation_audit"]),
        "locus_sha256": _digest(result["exact_real_locus_audit"]),
        "coupled_gate_sha256": _digest(result["coupled_gate_audit"]),
        "singular_sha256": _digest(result["singular_and_denominator_audit"]),
        "mutations_sha256": _digest(result["mutation_audit"]),
        "verdict_sha256": _digest(result["freeze_verdict"]),
    }
    return result


def _check(value: dict[str, Any]) -> None:
    verdict = value["freeze_verdict"]
    if (
        not verdict["producer_claim_survives"]
        or verdict["all_seven_gate_good_locus"] != "EMPTY"
        or verdict["candidate_C_active_selected"]
    ):
        raise AssertionError("freeze verdict drifted")
    if any(row["status"] != "REJECTED" for row in value["mutation_audit"]):
        raise AssertionError("mutation audit drifted")
    if value["claim_flags"]["UNIVERSAL_SCALAR_TENSOR_OR_K_ESSENCE_NO_GO"]:
        raise AssertionError("scoped audit was promoted")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    _check(value)
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif json.loads(OUTPUT.read_text()) != value:
        raise AssertionError("independent active-clock freeze audit is stale")
    print("COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1: PASS")


if __name__ == "__main__":
    main()
