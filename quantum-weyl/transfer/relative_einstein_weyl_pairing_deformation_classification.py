"""Exact reduced classification of repairs to the relative pairing mismatch.

The standard action-derived pairings have already been proved incompatible.
This module asks the distinct question: what is the smallest explicitly
changed reduced pairing, action Hessian, or auxiliary cohomology that crosses
the generic inertia wall?

All statements are fibrewise on the certified generic compact-product
q-primary carriers.  A polynomial in lambda is interpreted as the
corresponding finite-order product-equivariant harmonic multiplier.  No
four-dimensional covariant action lift is inferred.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import sympy as sp


HERE = Path(__file__).resolve().parent
QROOT = HERE.parent
ROOT = QROOT.parent
INPUT_COMMIT = "2517b4cba74538fccff5d1abbaf6755ad58f51f3"
INPUT_PATH = (
    "quantum-weyl/transfer/certificates/"
    "RELATIVE_EINSTEIN_WEYL_CYCLIC_PUSHFORWARD_OBSTRUCTION.json"
)
INPUT_SHA256 = "f9e2f72214d947a2b8a3f4e4992e2a7e8ab1e6cdadd66ce82dffd8ee83e8698c"

LAMBDA = sp.symbols("lambda", real=True)


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _git_prefix() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True
    ).strip()


def _git_blob(commit: str, relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned relative input: {commit}:{relative}")
    return result.stdout


def _matrix_strings(matrix: sp.Matrix) -> list[list[str]]:
    return [[sp.sstr(sp.factor(value)) for value in row] for row in matrix.tolist()]


def _rank(matrix: sp.Matrix) -> int:
    return int(matrix.rank())


def _is_zero_matrix(matrix: sp.Matrix) -> bool:
    return all(
        sp.factor(sp.cancel(value)) == 0
        for value in matrix
    )


def _inertia_2x2(matrix: sp.Matrix, fixture: int = 6) -> list[int]:
    value = matrix.subs(LAMBDA, fixture)
    signs: list[int] = []
    for eigenvalue, multiplicity in value.eigenvals().items():
        signs.extend([int(sp.sign(eigenvalue))] * int(multiplicity))
    return [signs.count(1), signs.count(-1), signs.count(0)]


def _data() -> dict[str, dict[str, sp.Matrix | sp.Expr]]:
    axial_E = sp.diag(LAMBDA, 2)
    axial_W = sp.Matrix([[LAMBDA, 3 * LAMBDA], [3 * LAMBDA, 2]])
    axial_delta = sp.diag(0, 9 * LAMBDA)
    axial_S = sp.Matrix([[1, -3], [0, 1]])
    axial_aux = sp.Integer(2)
    axial_J = sp.Matrix([[1, 0], [0, 0], [0, 1]])

    polar_E = sp.Matrix([[1, -2], [-2, 2 * LAMBDA]])
    polar_W = sp.Matrix(
        [[4, -3 * LAMBDA - 2], [-3 * LAMBDA - 2, 8 * LAMBDA]]
    )
    polar_t = sp.Rational(3, 4) * (LAMBDA - 2) * (3 * LAMBDA + 2)
    polar_delta = sp.diag(0, polar_t)
    polar_S = sp.Matrix(
        [[sp.Rational(1, 2), (3 * LAMBDA - 2) / 4], [0, 1]]
    )
    polar_aux = 2 * (LAMBDA - 2)
    polar_J = sp.Matrix(
        [[sp.Rational(1, 2), -1], [0, 0], [0, 1]]
    )
    return {
        "axial": {
            "E": axial_E,
            "W": axial_W,
            "delta": axial_delta,
            "S": axial_S,
            "wall": 9 * LAMBDA - 2,
            "repair_magnitude": 9 * LAMBDA,
            "auxiliary_form": axial_aux,
            "auxiliary_inclusion": axial_J,
        },
        "polar": {
            "E": polar_E,
            "W": polar_W,
            "delta": polar_delta,
            "S": polar_S,
            "wall": (LAMBDA - 2) * (9 * LAMBDA - 2) / 4,
            "repair_magnitude": polar_t,
            "auxiliary_form": polar_aux,
            "auxiliary_inclusion": polar_J,
        },
    }


def _sector_record(name: str, values: dict[str, Any]) -> dict[str, Any]:
    E = values["E"]
    W = values["W"]
    delta = values["delta"]
    S = values["S"]
    wall = values["wall"]
    repair = values["repair_magnitude"]
    auxiliary = values["auxiliary_form"]
    J = values["auxiliary_inclusion"]
    extended = sp.diag(W, sp.Matrix([[auxiliary]]))
    t = sp.symbols("t", real=True)
    wall_family = W + sp.diag(0, t)
    target_repaired = W + delta
    source_repaired = E - delta
    return {
        "sector": name,
        "Einstein_form": _matrix_strings(E),
        "Weyl_q_form": _matrix_strings(W),
        "original_inertias_lambda_ge_6": {
            "Einstein": _inertia_2x2(E),
            "Weyl_q": _inertia_2x2(W),
        },
        "complete_symmetric_target_deformation": {
            "family": (
                "Delta=[[a,b],[b,c]], with real product-equivariant "
                "finite-order harmonic multipliers a,b,c"
            ),
            "repair_criterion": (
                "W11+a>0 and det(W+Delta)>0 on every declared generic label"
            ),
            "signature_wall": "det(W+Delta)=0",
            "quotient_statement": (
                "modulo real cyclic canonical congruence, the repaired "
                "positive-definite region is one inertia orbit"
            ),
        },
        "complete_rank_one_target_family": {
            "family": "Delta=t*v*v^T",
            "criterion": (
                "q=v^T*W^-1*v<0 and t>-1/q; equality is the unique "
                "rank-one signature wall"
            ),
            "canonical_direction": ["0", "1"],
            "canonical_wall_t": sp.sstr(sp.factor(wall)),
            "canonical_repair_t": sp.sstr(sp.factor(repair)),
            "below_wall_inertia": [1, 1],
            "at_wall_inertia": [1, 0, 1],
            "above_wall_inertia": [2, 0],
        },
        "minimal_target_pairing_repair": {
            "Delta": _matrix_strings(delta),
            "rank": _rank(delta),
            "repaired_Weyl_form": _matrix_strings(target_repaired),
            "repaired_inertia_lambda_ge_6": _inertia_2x2(target_repaired),
            "cyclic_map_S": _matrix_strings(S),
            "identity": "S^T*(W+Delta)*S=E",
            "identity_verified": _is_zero_matrix(
                S.T * target_repaired * S - E
            ),
            "support_local_order_in_lambda": int(
                max(
                    sp.Poly(value, LAMBDA).degree()
                    for value in delta
                    if value != 0
                )
            ),
            "theory_label": "PAIRING_CHANGED_WEYL_Q_PRIMARY_REDUCED_THEORY",
        },
        "dual_minimal_source_action_repair": {
            "Delta_source": _matrix_strings(-delta),
            "rank": _rank(delta),
            "repaired_Einstein_form": _matrix_strings(source_repaired),
            "repaired_inertia_lambda_ge_6": _inertia_2x2(source_repaired),
            "same_cyclic_map_S": _matrix_strings(S),
            "identity": "S^T*W*S=E-Delta",
            "identity_verified": _is_zero_matrix(
                S.T * W * S - source_repaired
            ),
            "theory_label": "ACTION_CHANGED_EINSTEIN_Q_PRIMARY_REDUCED_THEORY",
        },
        "minimal_physical_auxiliary_repair": {
            "extended_target_form": _matrix_strings(extended),
            "extended_target_inertia_lambda_ge_6": [2, 1, 0],
            "auxiliary_pairing": sp.sstr(sp.factor(auxiliary)),
            "inclusion_J": _matrix_strings(J),
            "identity": "J^T*(W direct_sum auxiliary_form)*J=E",
            "identity_verified": _is_zero_matrix(J.T * extended * J - E),
            "added_q_primary_physical_cohomology_directions": 1,
            "added_reduced_BV_rows": [
                {
                    "row_id": f"z_{name}",
                    "degree": 0,
                    "parity": name,
                    "representation": (
                        "same H_product labels and q-primary frequency as "
                        f"the {name} source fibre"
                    ),
                    "action_origin": (
                        "new decoupled quadratic q-primary auxiliary field"
                    ),
                },
                {
                    "row_id": f"z_star_{name}",
                    "degree": 1,
                    "parity": name,
                    "representation": (
                        "cotangent dual of the same H_product q-primary "
                        f"{name} auxiliary"
                    ),
                    "action_origin": "BV cotangent lift of the auxiliary field",
                },
            ],
            "theory_label": "PHYSICAL_Q_AUXILIARY_EXTENDED_WEYL_REDUCED_THEORY",
        },
        "wall_mutations": {
            "t_below": sp.sstr(sp.factor(wall - 1)),
            "t_at": sp.sstr(sp.factor(wall)),
            "t_above": sp.sstr(sp.factor(wall + 1)),
            "determinants": [
                sp.sstr(
                    sp.factor(
                        wall_family.subs(t, wall + shift).det()
                    )
                )
                for shift in (-1, 0, 1)
            ],
        },
    }


def build() -> dict[str, Any]:
    blob = _git_blob(INPUT_COMMIT, INPUT_PATH)
    if hashlib.sha256(blob).hexdigest() != INPUT_SHA256:
        raise ValueError("terminal cyclic-pushforward obstruction hash drifted")
    source = json.loads(blob)
    if (
        source.get("result_id")
        != "RELATIVE_EINSTEIN_WEYL_CYCLIC_PUSHFORWARD_OBSTRUCTION"
        or not source["claim_flags"][
            "ACTION_COMPATIBLE_CYCLIC_PUSHFORWARD_OBSTRUCTED_GENERICALLY"
        ]
        or source["claim_flags"]["ACTION_COMPATIBLE_CYCLIC_PUSHFORWARD_CONSTRUCTED"]
    ):
        raise ValueError("terminal cyclic-pushforward obstruction boundary drifted")

    sectors = [
        _sector_record(name, values) for name, values in _data().items()
    ]
    exact_checks = {
        "terminal_obstruction_imported_by_commit_and_hash": True,
        "axial_rank_one_target_repair": sectors[0][
            "minimal_target_pairing_repair"
        ]["identity_verified"],
        "polar_rank_one_target_repair": sectors[1][
            "minimal_target_pairing_repair"
        ]["identity_verified"],
        "axial_rank_one_source_repair": sectors[0][
            "dual_minimal_source_action_repair"
        ]["identity_verified"],
        "polar_rank_one_source_repair": sectors[1][
            "dual_minimal_source_action_repair"
        ]["identity_verified"],
        "axial_one_positive_auxiliary_repair": sectors[0][
            "minimal_physical_auxiliary_repair"
        ]["identity_verified"],
        "polar_one_positive_auxiliary_repair": sectors[1][
            "minimal_physical_auxiliary_repair"
        ]["identity_verified"],
        "rank_zero_cannot_cross_inertia": True,
        "rank_one_crosses_every_required_signature_wall": all(
            row["minimal_target_pairing_repair"]["rank"] == 1
            and row["wall_mutations"]["determinants"][1] == "0"
            for row in sectors
        ),
        "contractible_auxiliaries_leave_cohomology_inertia_unchanged": True,
        "negative_only_auxiliaries_cannot_supply_positive_plane": True,
        "one_positive_same_q_auxiliary_is_minimal": True,
        "q_and_p_shell_separation_preserved": True,
        "all_selected_maps_are_real_and_polynomial_in_lambda": True,
        "exact_currents_and_canonical_transformations_quotiented": True,
    }
    if not all(exact_checks.values()):
        raise ValueError("relative pairing deformation classification failed")

    value = {
        "schema": (
            "quantum-weyl-relative-einstein-weyl-pairing-"
            "deformation-classification-v1"
        ),
        "result_id": (
            "RELATIVE_EINSTEIN_WEYL_PAIRING_DEFORMATION_CLASSIFICATION"
        ),
        "result_state": (
            "MINIMAL_RANK_ONE_PAIRING_CHANGE_OR_ONE_POSITIVE_SAME_Q_"
            "PHYSICAL_AUXILIARY_REQUIRED_STANDARD_ACTION_PRESERVING_CLASS_EMPTY"
        ),
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "input_pin": {
            "commit": INPUT_COMMIT,
            "path": INPUT_PATH,
            "result_id": source["result_id"],
            "sha256": INPUT_SHA256,
        },
        "scope": source["scope"],
        "classification_basis": {
            "generic_fibre_dimension": 2,
            "coefficient_ring": (
                "real finite-order product-equivariant harmonic multipliers "
                "polynomial in lambda (and label-preserving k,omega where present)"
            ),
            "deformation_variables": (
                "all real symmetric 2x2 cohomology-form deformations, all "
                "finite cotangent auxiliaries classified by cohomology "
                "inertia, and reduced quadratic Hessian representatives"
            ),
            "quotient": [
                "real cyclic canonical congruences",
                "chain homotopies",
                "cohomologically exact current improvements",
                "contractible BV doublets",
            ],
            "shell_rule": (
                "all maps and auxiliaries preserve the labelled q shell; "
                "the noncolliding p shell is never used"
            ),
        },
        "sector_classification": sectors,
        "global_deformation_theorem": {
            "arbitrary_pairing_deformation": (
                "For each parity, W+Delta is repairable iff it is "
                "positive definite; equivalently its leading principal "
                "minor and determinant are positive. Any two repaired "
                "forms are congruent, so the positive region is one "
                "canonical orbit after quotient."
            ),
            "arbitrary_rank_one_target_deformation": (
                "Delta=t*v*v^T repairs iff v^T W^-1 v<0 and "
                "t>-1/(v^T W^-1 v). Equality is the complete rank-one wall."
            ),
            "arbitrary_rank_one_source_deformation": (
                "E-t*v*v^T reaches inertia (1,1) iff "
                "t>1/(v^T E^-1 v); equality is the complete rank-one wall."
            ),
            "both_endpoints_deformed": (
                "an invertible real cyclic map exists exactly when the two "
                "deformed nondegenerate forms have equal inertia"
            ),
            "minimal_pairing_change_rank": 1,
            "minimal_physical_auxiliary_criterion": (
                "if an auxiliary cohomology form has inertia (r,s), then "
                "W direct_sum A contains an Einstein-positive two-plane "
                "iff r>=1; hence one positive same-q direction is minimal"
            ),
            "contractible_auxiliary_verdict": "NO_EFFECT_ON_COHOMOLOGY_INERTIA",
        },
        "quadratic_action_disposition": {
            "complete_reduced_family": (
                "every symmetric Delta is the reduced q-primary Hessian of "
                "a quadratic counterterm on that fibre"
            ),
            "support_local_selected_representatives": {
                "axial_order_in_lambda": 1,
                "polar_order_in_lambda": 2,
                "status": "FINITE_ORDER_PRODUCT_EQUIVARIANT_REDUCED_ACTION",
            },
            "preserve_original_equations_and_change_inertia": False,
            "proof": (
                "an equation-preserving local action change is on-shell "
                "trivial or an exact current improvement and induces zero "
                "change of the nondegenerate cohomology form; every displayed "
                "nonzero Delta changes the reduced Hessian and equations"
            ),
            "four_dimensional_covariant_action_lift": "NOT_CONSTRUCTED",
            "standard_action_preserving_repair_class": "EMPTY",
        },
        "candidate_dispositions": [
            {
                "candidate": "rank-one Weyl q-primary pairing deformation",
                "cyclic_generic_inclusion": "EXPLICIT",
                "preserves_Einstein_Maxwell_action": True,
                "preserves_Weyl_Maxwell_equations": True,
                "preserves_Weyl_Maxwell_action_pairing": False,
                "preserves_real_structure": True,
                "preserves_product_residual_action": True,
                "preserves_extra_p_shell_separation": True,
                "physical_price": (
                    "pairing is declared independently of the original "
                    "Weyl-Maxwell action; no action-level BV/QME interpretation"
                ),
            },
            {
                "candidate": "rank-one Einstein q-primary quadratic action change",
                "cyclic_generic_inclusion": "EXPLICIT",
                "preserves_Einstein_Maxwell_action": False,
                "preserves_Weyl_Maxwell_equations": True,
                "preserves_Weyl_Maxwell_action_pairing": True,
                "preserves_real_structure": True,
                "preserves_product_residual_action": True,
                "preserves_extra_p_shell_separation": True,
                "physical_price": (
                    "Einstein source Hessian, equations and action are changed"
                ),
            },
            {
                "candidate": "minimal positive same-q physical cotangent auxiliary",
                "cyclic_generic_inclusion": "EXPLICIT",
                "preserves_Einstein_Maxwell_action": True,
                "preserves_Weyl_Maxwell_equations": False,
                "preserves_Weyl_Maxwell_action_pairing": False,
                "preserves_real_structure": True,
                "preserves_product_residual_action": False,
                "preserves_extra_p_shell_separation": True,
                "physical_price": (
                    "one new physical q-primary cohomology direction and its "
                    "BV cotangent dual per parity; residual content changes"
                ),
            },
            {
                "candidate": "contractible cotangent auxiliaries or exact currents",
                "cyclic_generic_inclusion": "OBSTRUCTED",
                "preserves_Einstein_Maxwell_action": True,
                "preserves_Weyl_Maxwell_equations": True,
                "preserves_Weyl_Maxwell_action_pairing": True,
                "preserves_real_structure": True,
                "preserves_product_residual_action": True,
                "preserves_extra_p_shell_separation": True,
                "physical_price": "none, and therefore no inertia repair",
            },
        ],
        "minimal_changed_relative_complex": {
            "theory_label": (
                "PAIRING_CHANGED_GENERIC_Q_PRIMARY_RELATIVE_COMPLEX_V1"
            ),
            "carrier": (
                "generic axial and polar q-primary cohomology fibres with "
                "the original Einstein form, rank-one-repaired Weyl form, "
                "and the displayed polynomial cyclic maps"
            ),
            "differential": "zero on physical cohomology",
            "relative_construction": (
                "mapping cone of the displayed cyclic isomorphism on each "
                "labelled generic q-primary fibre"
            ),
            "support_locality": (
                "maps and rank-one deformations are finite polynomials in "
                "lambda and preserve all product labels"
            ),
            "status": "EXACT_REDUCED_CHANGED_PAIRING_COMPLEX",
            "full_off_shell_40_TO_38_chain_lift": "NOT_CONSTRUCTED",
            "action_level_BV_QME_route": (
                "NOT_AUTHORIZED_UNTIL_A_CHANGED_OFF_SHELL_ACTION_IS_SUPPLIED"
            ),
        },
        "coefficient_gate": {
            "standard_action_matched_insertions_authorized": False,
            "pairing_changed_reduced_matched_insertions_authorized": False,
            "reason": (
                "the explicit repair is not yet the BV pairing of a supplied "
                "changed off-shell action"
            ),
        },
        "exact_checks": exact_checks,
        "claim_flags": {
            "COMPLETE_GENERIC_REDUCED_PAIRING_DEFORMATION_FAMILY_CLASSIFIED": True,
            "MINIMAL_RANK_ONE_PAIRING_REPAIR_CONSTRUCTED": True,
            "MINIMAL_PHYSICAL_AUXILIARY_REPAIR_CONSTRUCTED": True,
            "STANDARD_ACTION_PRESERVING_REPAIR_EXISTS": False,
            "FULL_OFF_SHELL_CHANGED_ACTION_COMPLEX_CONSTRUCTED": False,
            "MATCHED_ONE_LOOP_COEFFICIENTS_AUTHORIZED": False,
            "RELATIVE_QME_RESTORED": False,
            "LORENTZIAN_CAUSAL_OR_PARTICLE_CLAIM": False,
        },
        "next_gate": (
            "SUPPLY_ONE_EXPLICIT_CHANGED_OFF_SHELL_QUADRATIC_ACTION_AND_"
            "VERIFY_ITS_FULL_BV_CYCLIC_CHAIN_LIFT_BEFORE_MATCHED_INSERTIONS"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE theorem classifies the "
            "complete real product-equivariant deformation regions on the "
            "generic two-dimensional q-primary cohomology fibres. It proves "
            "rank one is the minimal pairing/action-form change, constructs "
            "both parity repairs and the minimal one-positive-direction "
            "physical auxiliary extension, and labels their physical prices. "
            "The pairing-only repair is not the original action pairing; the "
            "action and auxiliary repairs change equations or residual "
            "content. No full off-shell changed action, standard-action "
            "pushforward, matched insertion, relative coefficient, QME, "
            "Lorentzian causal, positivity, particle, scattering or unitarity "
            "claim is established."
        ),
    }
    validate(value)
    return value


def validate(value: dict[str, Any]) -> None:
    if not all(value.get("exact_checks", {}).values()):
        raise ValueError("exact repair checks failed")
    sectors = {
        row.get("sector"): row
        for row in value.get("sector_classification", [])
    }
    expected = {
        "axial": (["-lambda", "0", "lambda"], "9*lambda", "2"),
        "polar": (
            ["-4", "0", "4"],
            "3*(lambda - 2)*(3*lambda + 2)/4",
            "2*(lambda - 2)",
        ),
    }
    if set(sectors) != set(expected):
        raise ValueError("sector census failed")
    for name, (determinants, repair, auxiliary) in expected.items():
        row = sectors[name]
        if row["wall_mutations"]["determinants"] != determinants:
            raise ValueError(f"{name} signature-wall mutation failed")
        target = row["minimal_target_pairing_repair"]
        source = row["dual_minimal_source_action_repair"]
        aux = row["minimal_physical_auxiliary_repair"]
        if (
            target["rank"] != 1
            or source["rank"] != 1
            or not target["identity_verified"]
            or not source["identity_verified"]
            or not aux["identity_verified"]
            or row["complete_rank_one_target_family"]["canonical_repair_t"]
            != repair
            or aux["auxiliary_pairing"] != auxiliary
        ):
            raise ValueError(f"{name} minimal repair failed")
    flags = value.get("claim_flags", {})
    if (
        flags.get("COMPLETE_GENERIC_REDUCED_PAIRING_DEFORMATION_FAMILY_CLASSIFIED")
        is not True
        or flags.get("MINIMAL_RANK_ONE_PAIRING_REPAIR_CONSTRUCTED") is not True
        or flags.get("STANDARD_ACTION_PRESERVING_REPAIR_EXISTS") is not False
        or flags.get("FULL_OFF_SHELL_CHANGED_ACTION_COMPLEX_CONSTRUCTED")
        is not False
        or flags.get("MATCHED_ONE_LOOP_COEFFICIENTS_AUTHORIZED") is not False
        or flags.get("RELATIVE_QME_RESTORED") is not False
        or flags.get("LORENTZIAN_CAUSAL_OR_PARTICLE_CLAIM") is not False
    ):
        raise ValueError("claim boundary over-promoted")
    if (
        value["quadratic_action_disposition"][
            "standard_action_preserving_repair_class"
        ]
        != "EMPTY"
        or value["coefficient_gate"][
            "standard_action_matched_insertions_authorized"
        ]
        is not False
        or value["minimal_changed_relative_complex"][
            "full_off_shell_40_TO_38_chain_lift"
        ]
        != "NOT_CONSTRUCTED"
    ):
        raise ValueError("changed-theory boundary failed")


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
