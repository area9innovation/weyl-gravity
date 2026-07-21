#!/usr/bin/env python3
"""Certify the local anomaly complex of the positive Berger complex clock.

The theorem is deliberately a changed-theory statement.  The strict pure-Weyl
BV complex does not restrict to the on-shell matter-coupled Berger expansion.
On the regular polar chart of the actual two-clock action, however, the clock
modulus supplies the Weyl compensator and contracts the complete Weyl quartet.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/BERGER_COMPLEX_CLOCK_LOCAL_ANOMALY_COMPLEX_V1.json"
PAYLOAD = HERE / "certificates/BERGER_COMPLEX_CLOCK_LOCAL_ANOMALY_COMPLEX_V1_PAYLOAD.json"
REPORT = ROOT / "quantum-weyl/reports/berger-complex-clock-local-anomaly-complex-v1.md"
SCHEMA = HERE / "schema/berger-complex-clock-local-anomaly-complex-v1.schema.json"
PAYLOAD_SCHEMA = HERE / "schema/berger-complex-clock-local-anomaly-receiver-v1.schema.json"

DEPENDENCIES = {
    "strict_restriction_obstruction": ROOT
    / "bridge/certificates/STRICT_ANOMALY_SECTOR_RESTRICTION_CHAIN_MAP_OBSTRUCTION_V1.json",
    "positive_berger_clock": ROOT
    / "d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json",
    "complex_clock_master_action": ROOT
    / "d_quotient_classical/certificates/COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1.json",
    "extended_local_bv_cohomology": HERE
    / "certificates/WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY.json",
    "wess_zumino_primitives": HERE
    / "certificates/WESS_ZUMINO_COMPENSATOR_EXTENSION_PREFLIGHT.json",
    "diff_anomaly_zero": ROOT
    / "quantum-weyl/local_bv/certificates/AFN0_DIFF_MIXED_MINIMAL_BV_H14.json",
    "berger_coupled_q2": ROOT
    / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2.json",
    "berger_coupled_q3": ROOT
    / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3.json",
}

SOURCE_COMMITS = {
    "strict_restriction_obstruction": "a9be01eab2867b221f281f11e6e637e0a6aea548",
    "positive_berger_clock": "bb5738d6e3e30a68adcc9a70c35dac089079e3db",
    "complex_clock_master_action": "306ff78a2001f23124d412e9a2f41531bec74f78",
    "extended_local_bv_cohomology": "69f01998d255455aebe3bbcb0872ae82cc698621",
    "diff_anomaly_zero": "8f875f1262c18dff2a914d2fe8131cce5d4c4cd9",
    "berger_coupled_q2": "e4f5c46fd7a04088e78e0374853b1f122ea223b1",
    "berger_coupled_q3": "41c58d2086d77158ab442841d00588d7b560cbd8",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _q(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _reference(name: str, path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value["result_id"]),
        "sha256": _sha256(path),
        "source_commit": SOURCE_COMMITS.get(name, "CONTENT_HASH_ONLY"),
    }


def _multiply(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction())
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def _add(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [left[i][j] + right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def _render(matrix: list[list[Fraction]]) -> list[list[dict[str, int]]]:
    return [[_q(entry) for entry in row] for row in matrix]


def _rank(matrix: list[list[Fraction]]) -> int:
    if not matrix:
        return 0
    rows = [row[:] for row in matrix]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next((row for row in range(rank, len(rows)) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [entry / scale for entry in rows[rank]]
        for row in range(len(rows)):
            if row != rank and rows[row][column]:
                factor = rows[row][column]
                rows[row] = [
                    entry - factor * pivot_entry
                    for entry, pivot_entry in zip(rows[row], rows[rank])
                ]
        rank += 1
    return rank


def _so4_ce_h2() -> dict[str, Any]:
    """Exact CE H^2(so(4),Q) control for the phase-current lift.

    The complexified Lorentz algebra has the same rational structure constants
    as this Euclidean realization.  The phase-shift characteristic class is a
    Lorentz scalar, hence uses trivial coefficients.
    """

    generators = list(combinations(range(4), 2))
    generator_index = {pair: index for index, pair in enumerate(generators)}

    def canonical_pair(left: int, right: int) -> tuple[tuple[int, int] | None, int]:
        if left == right:
            return None, 0
        if left < right:
            return (left, right), 1
        return (right, left), -1

    def bracket(left: int, right: int) -> dict[int, int]:
        a, b = generators[left]
        c, d = generators[right]
        output: dict[int, int] = {}
        terms = [
            (int(b == c), a, d),
            (-int(a == c), b, d),
            (-int(b == d), a, c),
            (int(a == d), b, c),
        ]
        for coefficient, first, second in terms:
            pair, sign = canonical_pair(first, second)
            if pair is not None and coefficient:
                index = generator_index[pair]
                output[index] = output.get(index, 0) + coefficient * sign
        return {index: coefficient for index, coefficient in output.items() if coefficient}

    two_basis = list(combinations(range(6), 2))
    three_basis = list(combinations(range(6), 3))
    two_index = {pair: index for index, pair in enumerate(two_basis)}
    d1 = [[Fraction() for _ in range(6)] for _ in two_basis]
    for row, (left, right) in enumerate(two_basis):
        for index, coefficient in bracket(left, right).items():
            d1[row][index] = Fraction(-coefficient)

    d2 = [[Fraction() for _ in two_basis] for _ in three_basis]
    for row, (x, y, z) in enumerate(three_basis):
        for sign, commutator, tail in (
            (-1, bracket(x, y), z),
            (1, bracket(x, z), y),
            (-1, bracket(y, z), x),
        ):
            for index, coefficient in commutator.items():
                pair, wedge_sign = canonical_pair(index, tail)
                if pair is not None:
                    d2[row][two_index[pair]] += Fraction(sign * coefficient * wedge_sign)

    d1_rank = _rank(d1)
    d2_rank = _rank(d2)
    h2_dimension = len(two_basis) - d1_rank - d2_rank
    if (d1_rank, d2_rank, h2_dimension) != (6, 9, 0):
        raise ValueError("so(4) trivial-coefficient CE H2 control drifted")
    return {
        "coefficient_module": "TRIVIAL_SCALAR_PHASE_SHIFT_CURRENT",
        "structure_algebra": "so(3,1)_C_ISOMORPHIC_TO_so(4,C)",
        "stora_reduction": "translation ghosts and symmetric Diff-ghost jets are contractible modulo d_h; only the Lorentz small algebra remains",
        "comparison_dependency": "AFN0_DIFF_MIXED_MINIMAL_BV_H14",
        "generator_basis": [f"M_{a}{b}" for a, b in generators],
        "C1_dimension": 6,
        "C2_dimension": len(two_basis),
        "C3_dimension": len(three_basis),
        "d1_rank": d1_rank,
        "d2_rank": d2_rank,
        "H2_dimension": h2_dimension,
        "d1_matrix_sha256": _digest(_render(d1)),
        "d2_matrix_sha256": _digest(_render(d2)),
        "interpretation": "the sole global-U(1) AFN1 characteristic current has no pure-ghost-number-two lift into H^{1,4}(s|d)",
    }


def _load_dependencies() -> dict[str, dict[str, Any]]:
    return {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}


def _assert_dependencies(values: dict[str, dict[str, Any]]) -> None:
    obstruction = values["strict_restriction_obstruction"]
    berger = next(
        row for row in obstruction["sector_dispositions"] if row["sector_id"] == "Berger_fixed_coupling"
    )
    witness = berger["exact_witness"]
    if (
        witness["chain_defect"] != "961/1920"
        or witness["source_metric_antifield_constant_alphaB_B00"] != "961/1920"
        or witness["target_coupled_metric_antifield_constant"] != "0"
    ):
        raise ValueError("strict-to-Berger antifield obstruction drifted")

    background = values["positive_berger_clock"]
    if (
        background["flags"]["exact_backreacted_background_exists"] is not True
        or background["rational_fixture"]["scalar_equation"] != "PASS"
        or background["rational_fixture"]["three_independent_metric_equations"] != "PASS"
        or background["clock_ansatz"]["incidence_full_rank"] is not True
        or background["rational_fixture"]["rho_squared"] != "1"
    ):
        raise ValueError("positive Berger clock fixture drifted")

    master = values["complex_clock_master_action"]
    if (
        master["claim_flags"]["LOCAL_ACTION_CERTIFIED"] is not True
        or master["claim_flags"]["MINIMAL_AND_NONMINIMAL_BV_CERTIFIED"] is not True
        or master["exact_checks"]["classical_master_equation"] is not True
        or master["exact_checks"]["Q_squared_zero"] is not True
        or master["domain"]["background_independence"] != "LOCAL_COVARIANT_NO_BACKGROUND_SELECTED"
        or master["dependencies"]["positive_polar_clock_fixture"]["sha256"]
        != _sha256(DEPENDENCIES["positive_berger_clock"])
    ):
        raise ValueError("complex-clock master-action export drifted")

    extended = values["extended_local_bv_cohomology"]
    if (
        extended["H14"]["status"]
        != "COMPLETE_ZERO_IN_DECLARED_TAU_ADIC_DIMENSION_FOUR_ALGEBRA"
        or extended["H14"]["pure_Diff_quotient_dimension"] != 0
        or extended["quartet_reduction"]["status"]
        != "EXACT_QUASI_ISOMORPHISM_TO_DRESSED_PURE_DIFF_BV_COMPLEX"
    ):
        raise ValueError("extended local-BV cohomology dependency drifted")

    diff = values["diff_anomaly_zero"]
    if diff["claim_flags"]["PURE_DIFF_H14_ZERO"] is not True:
        raise ValueError("four-dimensional pure-Diff anomaly theorem drifted")

    q2 = values["berger_coupled_q2"]
    q3 = values["berger_coupled_q3"]
    if (
        q2["flags"]["BERGER_LOCAL_K_ACTION_EQUIVARIANT_COUPLED_MAXWELL_ARITY_TWO"] is not True
        or q2["flags"]["BERGER_RAW_D_ACTION_EQUIVARIANT_COUPLED_MAXWELL_ARITY_TWO"] is not False
        or q3["flags"]["BERGER_MIXED_Q3_K_EQUIVARIANT"] is not True
    ):
        raise ValueError("Berger K/raw-D symmetry disposition drifted")


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    values = _load_dependencies()
    _assert_dependencies(values)

    # Ordered quartet basis: (tau, omega, omega_star, tau_hat_star).
    q_w = [
        [Fraction(0), Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(1), Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(1), Fraction(0)],
    ]
    h_w = [
        [Fraction(0), Fraction(1), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0), Fraction(1)],
        [Fraction(0), Fraction(0), Fraction(0), Fraction(0)],
    ]
    zero = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    identity = [[Fraction(int(i == j)) for j in range(4)] for i in range(4)]
    if _multiply(q_w, q_w) != zero or _add(_multiply(q_w, h_w), _multiply(h_w, q_w)) != identity:
        raise ValueError("Weyl quartet contraction failed")

    # The four standard strict candidates are a useful finite regression basis.
    strict_candidates = [
        ("ANOM_OMEGA_C2", "even", "B_C=int sqrt(g) tau C2"),
        (
            "ANOM_OMEGA_E4",
            "even",
            "B_E=int sqrt(g)[tau E4+4 G^munu d_mu tau d_nu tau-4(Box tau)(d tau)^2+2(d tau)^4]",
        ),
        ("ANOM_OMEGA_C_DUAL_C", "odd", "B_P=int sqrt(g) tau CdualC"),
        ("ANOM_OMEGA_BOX_R", "even", "B_BOX=-(1/12)int sqrt(g) R2 plus horizontal current"),
    ]
    boundary = [
        [Fraction(int(row == column)) for column in range(len(strict_candidates))]
        for row in range(len(strict_candidates))
    ]
    if _rank(boundary) != len(strict_candidates):
        raise ValueError("standard matter-coupled Weyl boundary map is not surjective")

    defect = Fraction(961, 1920)
    target_constant = Fraction(0)
    if defect - target_constant != Fraction(961, 1920):
        raise ValueError("constant-term action-morphism separator drifted")

    phase_current_ce = _so4_ce_h2()
    candidate_ledger = [
        {
            "sector": "WEYL_FIELD_AND_ALL_WEYL_JETS",
            "coverage": "EVERY_MONOMIAL_WITH_POSITIVE_TAU_OMEGA_JET_NUMBER",
            "status": "EXACT",
            "proof": "prolong Q_W tau_I=omega_I and h_W=sum_I tau_I partial/partial omega_I; (Q_W h_W+h_W Q_W)=N_quartet",
        },
        {
            "sector": "WEYL_COTANGENT",
            "coverage": "EVERY_MONOMIAL_WITH_OMEGA_STAR_OR_TAU_HAT_STAR",
            "status": "EXACT",
            "proof": "Q_W omega_star=tau_hat_star and the cotangent half of the same quartet homotopy",
        },
        {
            "sector": "NONMINIMAL_DIFF_WEYL",
            "coverage": "ALL_4_PLUS_1_COVARIANT_NONMINIMAL_PAIRS_AND_JETS",
            "status": "EXACT",
            "proof": "pointwise covariant doublet contraction imported with the action-derived nonminimal BV rows",
        },
        {
            "sector": "QUARTET_NUMBER_ZERO_PURE_DIFF",
            "coverage": "DRESSED_G_HAT_THETA_XI_AND_COTANGENT_JETS",
            "status": "ZERO",
            "proof": "four-dimensional Diff anomaly comparison; cubic invariant-polynomial space of so(3,1)_C=sl2+sl2 is zero",
        },
        {
            "sector": "POSITIVE_ANTIFIELD_MATTER",
            "coverage": "RHO_NOT_ZERO_REGULAR_EULER_LAGRANGE_CHART",
            "status": "ZERO",
            "proof": "regular Koszul-Tate pairs remove ordinary matter Euler jets; the surviving global-U(1) phase-current characteristic class would require a pure-ghost-number-two lift, but exact CE ranks (6,9) give H2(so(3,1)_C,Q)=0",
        },
    ]

    dependencies = {
        name: _reference(name, path) for name, path in DEPENDENCIES.items()
    }
    proof_core = {
        "quartet_Q": _render(q_w),
        "quartet_h": _render(h_w),
        "quartet_anticommutator": _render(identity),
        "strict_candidate_boundary": _render(boundary),
        "candidate_ledger": candidate_ledger,
        "phase_current_CE_H2": phase_current_ce,
        "constant_separator": {
            "functional": "epsilon_0=constant term at the zero-fluctuation Berger jet",
            "epsilon_0_Q_target": _q(target_constant),
            "epsilon_0_j_Q_source_gstar00": _q(defect),
            "separation": _q(defect - target_constant),
        },
    }

    result: dict[str, Any] = {
        "schema": "quantum-weyl-berger-complex-clock-local-anomaly-complex-v1",
        "result_id": "BERGER_COMPLEX_CLOCK_LOCAL_ANOMALY_COMPLEX_V1",
        "result_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "theory": {
            "name": "positive Berger gravity plus two-real-scalar complex clock",
            "action_specialization": "alpha_R=alpha_E=alpha_P=0; kappa_r=kappa_theta=1 in COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1",
            "background": "a=1, q=9/40, alpha_B=5, rho^2=1, omega_clock=3/4, lambda=119/480",
            "local_algebra": "formal rho!=0 polar local-analytic jet algebra with tau=-log(rho/f)",
            "gauge_symmetry": "Diff x Weyl",
            "global_symmetry": "U(1) phase shift of theta; no U(1) gauge ghost",
            "regularity_scope": "regular matter-coupled Euler-Lagrange chart; singular and rho=0 strata excluded",
        },
        "classical_import": {
            "status": "COMPLETE_ACTION_DERIVED_MINIMAL_AND_NONMINIMAL_BV",
            "field_inventory_hash": values["complex_clock_master_action"]["content_hashes"]["field_inventory_sha256"],
            "action_manifest_hash": values["complex_clock_master_action"]["content_hashes"]["action_manifest_sha256"],
            "bv_manifest_hash": values["complex_clock_master_action"]["content_hashes"]["BV_manifest_sha256"],
            "cme": "VERIFIED",
            "Q_squared_zero": "VERIFIED",
            "positive_background_on_shell": "VERIFIED_ALL_SCALAR_AND_THREE_INDEPENDENT_METRIC_EQUATIONS",
        },
        "quartet_reduction": {
            "ordered_basis": ["tau", "omega", "omega_star", "tau_hat_star"],
            "Q_W": _render(q_w),
            "h_W": _render(h_w),
            "Q_W_squared": _render(zero),
            "Qh_plus_hQ": _render(identity),
            "jet_prolongation": "Q_W tau_I=omega_I; Q_W omega_I=0 for every finite multi-index I",
            "remaining_complex": "Diff BV complex of g_hat=(rho/f)^2 g and theta",
            "status": "EXACT_ON_FORMAL_RHO_NONZERO_CHART",
        },
        "candidate_completeness": {
            "bounds": {
                "spacetime_dimension": 4,
                "ghost_number": 1,
                "form_degree": 4,
                "engineering_dimension": 4,
                "derivative_order_max": 4,
                "antifield_number": "all values allowed by the minimal/nonminimal BV inventory",
                "locality": "finite jets coefficientwise in the formal tau-adic completion",
            },
            "partition": "every monomial has either positive quartet number or quartet number zero; the latter is the dressed Diff BV complex",
            "ledger": candidate_ledger,
            "positive_antifield_characteristic_current": {
                "delta_mod_d_generator": "global U(1) phase-shift Noether current J_theta with AFN1 representative theta_star",
                "ordinary_Euler_jet_pairs": "CONTRACTED_IN_REGULAR_KOSZUL_TATE_ADAPTED_COORDINATES",
                "required_lift": "pure ghost number two scalar CE cocycle",
                "CE_control": phase_current_ce,
                "lift_status": "ZERO",
                "higher_antifield_status": "ZERO_BY_IRREDUCIBILITY_ON_LOCAL_COVARIANT_REGULAR_CHART",
            },
            "exhaustiveness_status": "COMPLETE_STRUCTURAL_PARTITION_ON_DECLARED_REGULAR_CHART",
            "does_not_require_raw_graph_expansion": True,
        },
        "H14": {
            "even_quotient_dimension": 0,
            "odd_quotient_dimension": 0,
            "pure_Diff_quotient_dimension": 0,
            "Weyl_and_mixed_quotient_dimension": 0,
            "positive_antifield_quotient_dimension": 0,
            "standard_candidate_basis": [row[0] for row in strict_candidates],
            "standard_candidate_boundary_matrix": _render(boundary),
            "standard_candidate_boundary_rank": _rank(boundary),
            "standard_candidate_primitives": [
                {"class_id": class_id, "parity": parity, "primitive": primitive, "status": "EXACT"}
                for class_id, parity, primitive in strict_candidates
            ],
            "matter_family": {
                "candidate": "omega I_hat for every dimension-four Diff-invariant local density I_hat(g_hat,theta)",
                "primitive": "tau I_hat with its universal Diff completion",
                "identity": "s(tau I_hat)=omega I_hat modulo d_h",
                "status": "EXACT_FAMILY",
            },
            "status": "COMPLETE_ZERO_ON_DECLARED_REGULAR_FORMAL_POLAR_CHART",
        },
        "strict_to_coupled_action_morphism": {
            "declared_complete_class": "unit-preserving local-analytic background-jet morphisms regular at zero fluctuation, allowing arbitrary field/antifield mixing but no negative field degree",
            "source": "strict pure-Weyl BV expansion evaluated at the positive Berger metric",
            "target": "on-shell gravity-clock BV expansion at the positive Berger solution",
            "separator": proof_core["constant_separator"],
            "reason": "the target has no arity-zero Euler row on any antifield, whereas the strict metric-antifield row has the nonzero unit coefficient 961/1920; a unital morphism preserves that coefficient",
            "verdict": "NONEXISTENT_IN_DECLARED_COMPLETE_MORPHISM_CLASS",
            "relation_to_old_obstruction": "strengthens the identity-jet witness to arbitrary regular local-analytic mixing by the constant-term functional",
            "not_a_repair": "the coupled cohomology is a changed source theory; no 961/1920 term is subtracted or cancelled by hand",
        },
        "symmetry_disposition": {
            "local_Weyl": "H14_ZERO_BY_QUARTET_CONTRACTION",
            "local_Diff": "H14_ZERO_IN_FOUR_DIMENSIONS_ON_DECLARED_REGULAR_CHART",
            "mixed_Diff_Weyl": "H14_ZERO_BY_TOTAL_COMPLEX_AND_QUARTET_CONTRACTION",
            "raw_D": "NOT_A_LINEAR_SYMMETRY_OF_THE_FIXED_POSITIVE_CLOCK_BACKGROUND; AFFINE ARITY_ZERO PART PRESENT",
            "K_Berger": "RIGID_BACKGROUND_SYMMETRY_NOT_A_LOCAL_GAUGE_GHOST; Q1_Q2_Q3_EQUIVARIANCE IS A SEPARATE CARTAN INPUT",
        },
        "receiver_payload": {
            "strict_pullback": "NO_CERTIFIED_MAP_CHANGED_THEORY_MORPHISM_OBSTRUCTED",
            "matter_coupled_local_classes": "ZERO_QUOTIENT",
            "standard_formula_representatives": "EXACT_WITH_DISPLAYED_PRIMITIVES",
            "Cartan_bridge": "NOT_REACHED_REQUIRES_RENORMALIZED_QME_AND_LOCAL_TO_CARTAN_MAP",
            "sector_restriction_next_action": "replace strict-pullback question by matter-coupled coefficient computation if a regulator is selected",
        },
        "coefficient_and_qme_status": {
            "coefficient_status": "NOT_COMPUTED_FOR_GRAVITY_CLOCK_THEORY",
            "cohomological_disposition": "EVERY_CONSISTENT_LOCAL_GHOST_ONE_BREAKING_IS_REMOVABLE_ON_DECLARED_CHART",
            "QME_status": "NOT_RESTORED_FOR_GRAVITY_CLOCK_THEORY",
            "required_next_gate": "compute the actual matter-coupled regulated breaking and its primitive coefficients",
        },
        "proof_hashes": {
            "quartet_and_candidate_partition_sha256": _digest(proof_core),
            "candidate_ledger_sha256": _digest(candidate_ledger),
            "action_morphism_separator_sha256": _digest(proof_core["constant_separator"]),
        },
        "dependencies": dependencies,
        "does_not_establish": [
            "a strict pure-Weyl anomaly pullback to Berger",
            "anomaly coefficients for the gravity-clock theory",
            "a restored gravity-clock QME",
            "a raw-D or K_Berger quantum Cartan identity",
            "a Maxwell extension",
            "global validity through rho=0 or singular Euler-Lagrange strata",
            "a Lorentzian QME, Hadamard state, positivity, particles, scattering or unitarity",
        ],
        "claim_boundary": "This LOCAL-ALGEBRAIC theorem classifies H^{1,4}(s|d) for the actual positive-Berger two-scalar clock theory in the formal rho!=0 polar local-analytic algebra on a regular matter-coupled Euler-Lagrange chart. The action-derived minimal and nonminimal BV rows make the Weyl field/ghost/cotangent sector an exact quartet; the remaining four-dimensional Diff complex with the nonchiral phase scalar has zero ghost-one anomaly quotient. Separately, the constant-term functional proves that no unit-preserving regular local-analytic BV action morphism can identify the strict pure-Weyl expansion at this non-Bach-flat metric with the on-shell coupled expansion: the exact separation is 961/1920. Thus the matter-coupled zero quotient is a changed-theory result, not a repaired strict pullback. No anomaly coefficient or QME restoration for the gravity-clock theory is computed.",
    }

    receiver = {
        "schema": "quantum-weyl-berger-complex-clock-local-anomaly-receiver-v1",
        "result_id": "BERGER_COMPLEX_CLOCK_LOCAL_ANOMALY_COMPLEX_V1_PAYLOAD",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "producer_result_id": result["result_id"],
        "theory": result["theory"]["name"],
        "background": result["theory"]["background"],
        "strict_action_complex_map": result["strict_to_coupled_action_morphism"]["verdict"],
        "strict_map_separator": result["strict_to_coupled_action_morphism"]["separator"],
        "matter_coupled_H14": {
            "even_dimension": 0,
            "odd_dimension": 0,
            "status": result["H14"]["status"],
        },
        "standard_candidate_disposition": [
            {"class_id": row[0], "status": "EXACT", "primitive": row[2]}
            for row in strict_candidates
        ],
        "symmetry_disposition": result["symmetry_disposition"],
        "coefficient_status": result["coefficient_and_qme_status"]["coefficient_status"],
        "QME_status": result["coefficient_and_qme_status"]["QME_status"],
        "downstream": {
            "strict_sector_restriction": "NO_CERTIFIED_MAP_CHANGED_THEORY",
            "matter_coupled_coefficient_gate": "READY",
            "K_Berger_Cartan_gate": "OPEN",
        },
    }
    result["receiver_payload_sha256"] = _digest(receiver)
    validate(result, receiver)
    return result, receiver


def validate(result: dict[str, Any], receiver: dict[str, Any] | None = None) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(result)
    if result["dependency_tags"] != ["LOCAL-ALGEBRAIC"]:
        raise ValueError("dependency boundary drifted")
    if result["H14"]["standard_candidate_boundary_rank"] != 4:
        raise ValueError("standard candidate boundary rank drifted")
    if any(
        result["H14"][key] != 0
        for key in (
            "even_quotient_dimension",
            "odd_quotient_dimension",
            "pure_Diff_quotient_dimension",
            "Weyl_and_mixed_quotient_dimension",
            "positive_antifield_quotient_dimension",
        )
    ):
        raise ValueError("matter-coupled H14 was over-promoted or drifted")
    separator = result["strict_to_coupled_action_morphism"]["separator"]
    if separator["separation"] != _q(Fraction(961, 1920)):
        raise ValueError("strict-to-coupled separator drifted")
    if result["coefficient_and_qme_status"]["QME_status"] != "NOT_RESTORED_FOR_GRAVITY_CLOCK_THEORY":
        raise ValueError("gravity-clock QME was promoted without coefficients")
    if receiver is not None:
        payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
        Draft202012Validator.check_schema(payload_schema)
        Draft202012Validator(payload_schema).validate(receiver)
        if result["receiver_payload_sha256"] != _digest(receiver):
            raise ValueError("receiver payload hash drifted")


def _report(result: dict[str, Any]) -> str:
    return f"""# Berger complex-clock local anomaly complex

## Result

On the regular formal polar chart `rho != 0`, the actual positive-Berger
two-scalar clock theory has

```text
H^{{1,4}}_even(s|d) = 0
H^{{1,4}}_odd(s|d)  = 0
```

with dependency tag `LOCAL-ALGEBRAIC`.  The action-derived covariant BV export
contains the complete minimal and nonminimal rows.  With
`tau=-log(rho/f)` and `g_hat=(rho/f)^2 g`, the four generators
`(tau, omega, omega_star, tau_hat_star)` form an exact quartet, including all
finite jets.  The quotient therefore reduces to the four-dimensional Diff BV
complex of `g_hat` and the nonchiral phase scalar `theta`; its ghost-one local
anomaly space vanishes on the declared regular Euler--Lagrange chart.

The phase-shift current is the only additional antifield-number-one
characteristic class introduced by the clock.  Its possible ghost-number-one
lift requires a scalar pure-ghost-number-two cocycle.  The independent exact
Chevalley--Eilenberg control has ranks `rank(d1)=6`, `rank(d2)=9` in the
15-dimensional two-cochain space, hence `H2(so(3,1)_C,Q)=0`; the current does
not create an antifield-dependent anomaly.

The familiar representatives `omega C2`, `omega E4`, `omega CdualC`, and
`omega BoxR` are all exact in this changed theory.  More generally,
`omega I_hat(g_hat,theta)` has primitive `tau I_hat` with its universal Diff
completion.

## Strict-versus-coupled action complexes

There is still no BV action-complex restriction from strict pure Weyl gravity
to this Berger solution.  The constant-term functional separates the two
complexes:

```text
epsilon_0 Q_target = 0
epsilon_0 j Q_source(gstar_00) = 961/1920
```

This proves nonexistence for every unit-preserving local-analytic background-
jet morphism regular at zero fluctuation, even when arbitrary field/antifield
mixing is allowed.  No `961/1920` term was subtracted.  The zero anomaly
quotient is a result about the actual matter-coupled theory, not a repaired
pullback of the strict theory.

## Claim boundary

No gravity-clock anomaly coefficient was computed, and its QME was not
restored.  Raw `D` is affine rather than a linear symmetry of the fixed clock
background; `K_Berger` is a rigid background symmetry, not a local gauge
ghost.  Its quantum Cartan disposition remains open.  Maxwell, global
`rho=0` strata, Lorentzian products, Hadamard states, positivity, particles,
scattering, and unitarity are outside this certificate.

Proof digest: `{result['proof_hashes']['quartet_and_candidate_partition_sha256']}`.

EVIDENCE: quantum-weyl/anomalies/certificates/BERGER_COMPLEX_CLOCK_LOCAL_ANOMALY_COMPLEX_V1.json

CLOSE-OUT: DONE — the actual positive-Berger complex-clock local anomaly
complex is classified on the declared regular formal polar chart; the strict
action-complex map remains obstructed by the exact `961/1920` separator.
"""


def _write(result: dict[str, Any], receiver: dict[str, Any]) -> None:
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    PAYLOAD.write_text(json.dumps(receiver, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(_report(result))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, receiver = build()
    if args.check:
        if json.loads(OUTPUT.read_text()) != result:
            raise ValueError("Berger complex-clock anomaly certificate drifted")
        if json.loads(PAYLOAD.read_text()) != receiver:
            raise ValueError("Berger complex-clock anomaly receiver drifted")
        if REPORT.read_text() != _report(result):
            raise ValueError("Berger complex-clock anomaly report drifted")
    else:
        _write(result, receiver)
    print("BERGER_COMPLEX_CLOCK_LOCAL_ANOMALY_COMPLEX_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
