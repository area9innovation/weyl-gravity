#!/usr/bin/env python3
"""Decide the first filtered V2 lift of the rank-46 physical branch anchor.

This is not the forbidden raw compression ``Pi_TT V2 Pi_TT``.  At the
standard null fibre it solves the invariant filtered lifting equation

    V2 I_phys + V2 K1 B = H4 C + J_phys A,

where ``K1 B`` changes the physical field representatives by arbitrary gauge
vectors, ``H4 C`` changes the image by a principal boundary, and
``J_phys A`` changes the physical equation representatives.  Failure of this
equation is therefore a cohomology-class obstruction to descending the
certified physical projective module through the first nonzero lower PBW/Rees
page.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (
    _matrix_from_record,
    _symbol,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/backreacted_clock"
PHYSICAL = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PHYSICAL_HELICITY_FILTERED_QUOTIENT_V1.json"
PRINCIPAL = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PRINCIPAL_BRANCH_ANCHOR_V1.json"
CARRIER = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1.json"
Q1 = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
RANK36 = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_SUBPRINCIPAL_BRANCH_ANCHOR_OR_OBSTRUCTION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-retained-46-stf2-subprincipal-branch-anchor-or-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-46-stf2-subprincipal-branch-anchor-or-obstruction-v1.schema.json"
VERIFIER = HERE / "verify_berger_retained_46_stf2_subprincipal_branch_anchor_or_obstruction.py"
TESTS = HERE / "tests/test_berger_retained_46_stf2_subprincipal_branch_anchor_or_obstruction.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"dependency is not an object: {path}")
    return value


def _dependency(path: Path, value: dict) -> dict[str, str]:
    return {
        "artifact_id": value.get("result_id", value.get("atomic_flag", value["schema"])),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _sparse_matrix(rows: int, columns: int, entries: list[list[object]]) -> sp.Matrix:
    value = sp.zeros(rows, columns)
    for row, column, coefficient in entries:
        value[int(row), int(column)] = sp.sympify(coefficient)
    return value


def _column_record(vector: sp.Matrix) -> list[str]:
    return [str(sp.factor(entry)) for entry in vector]


def _matrix_record(matrix: sp.Matrix) -> list[list[str]]:
    return [
        [str(sp.factor(matrix[row, column])) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def _exact_data() -> dict[str, object]:
    physical = _load(PHYSICAL)
    principal = _load(PRINCIPAL)
    carrier = _load(CARRIER)
    q1 = _load(Q1)
    rank36 = _load(RANK36)

    if (
        physical.get("result_state")
        != "PHYSICAL_HELICITY_PROJECTIVE_MODULE_CERTIFIED_V2_FILTERED_DESCENT_OPEN"
        or physical.get("null_cone_chart", {}).get("projective_rank") != 2
        or physical.get("claim_flags", {}).get("V2_FILTERED_DESCENT_COMPUTED") is not False
    ):
        raise ValueError("physical filtered-quotient authority drifted")
    if (
        principal.get("result_state")
        != "PRINCIPAL_DIRECT_SUM_ANCHOR_OBSTRUCTED_FILTERED_SUBPRINCIPAL_GATE_REQUIRED"
        or principal.get("claim_flags", {}).get("SUBPRINCIPAL_ANCHOR_REQUIRED") is not True
    ):
        raise ValueError("principal branch-anchor authority drifted")
    if (
        carrier.get("flags", {}).get("CYCLIC_GRAPH_SDR_46_TO_36") is not True
        or carrier.get("graph_construction", {}).get("Schur_complement") != "A10"
    ):
        raise ValueError("rank-46 graph-SDR authority drifted")
    if q1.get("claim_status") != "CERTIFIED_COMPLETE_MINIMAL_Q1":
        raise ValueError("retained q1 authority drifted")

    fibre = physical["normalized_standard_null_fibre"]
    if fibre["covector"] != [1, 1, 0, 0]:
        raise ValueError("standard null fibre drifted")
    field_inclusion = _sparse_matrix(10, 2, fibre["field_inclusion_entries"])
    equation_inclusion = _sparse_matrix(10, 2, fibre["equation_inclusion_entries"])

    p = sp.symbols("p0:4")
    null_point = {p[0]: 1, p[1]: 1, p[2]: 0, p[3]: 0}
    h4 = sp.Matrix(
        _symbol(_matrix_from_record(q1["q1_blocks"]["H_retained"]), 4)
    ).subs(null_point)
    alpha_b = next(symbol for symbol in h4.free_symbols if symbol.name == "alpha_B")
    h4 = h4.subs(alpha_b, 5)
    gauge = sp.Matrix(
        _symbol(_matrix_from_record(q1["q1_blocks"]["K_spatial"]), 1)
    ).subs(null_point)

    artifact = physical["V2_receiving_contract"]["artifact"]
    v2_path = ROOT / artifact["path"]
    if _sha256(v2_path) != artifact["sha256"]:
        raise ValueError("V2 artifact digest drifted")
    v2 = sp.Matrix(_symbol(_matrix_from_record(json.loads(v2_path.read_text())), 2)).subs(null_point)
    u = next(symbol for symbol in v2.free_symbols if symbol.name == "u")
    v = next(symbol for symbol in v2.free_symbols if symbol.name == "v")
    fixture = rank36["normalized_obstruction_witness"]["fixture"]
    u0 = sp.sympify(fixture["u"])
    v0 = sp.sympify(fixture["v"])
    substitutions = {u: u0, v: v0}

    # All allowed first filtered corrections appear in this module: H4 changes
    # the field lift, J_phys changes the equation lift, and V2*K1 accounts for
    # every change of the leading field representative by a gauge vector.
    boundary = h4.row_join(equation_inclusion).row_join(v2 * gauge)
    image = v2 * field_inclusion
    boundary_fixture = boundary.subs(substitutions)
    image_fixture = image.subs(substitutions)
    ranks = {
        "allowed_boundary": int(boundary_fixture.rank()),
        "plus_augmented": int(boundary_fixture.row_join(image_fixture[:, 0]).rank()),
        "cross_augmented": int(boundary_fixture.row_join(image_fixture[:, 1]).rank()),
        "both_augmented": int(boundary_fixture.row_join(image_fixture).rank()),
    }
    if ranks != {
        "allowed_boundary": 4,
        "plus_augmented": 5,
        "cross_augmented": 4,
        "both_augmented": 5,
    }:
        raise ValueError(f"filtered-lift rank ledger drifted: {ranks}")

    # The first canonical left-null vector is already polynomial before the
    # fixture specialization.  Its value on the obstructed image is
    # -8*u*(u-v), which becomes 31/5.  Normalize it to one.
    raw_witness = sp.Matrix([-1, 2, 0, 0, 5, 0, 0, 0, 0, 0])
    raw_values = (raw_witness.T * image).applyfunc(sp.factor)
    if (raw_witness.T * boundary).applyfunc(sp.factor) != sp.zeros(1, boundary.cols):
        raise ValueError("left-null witness does not annihilate allowed boundaries")
    if raw_values != sp.Matrix([[-8 * u * (u - v), 0]]):
        raise ValueError("generic obstruction polynomial drifted")
    fixture_value = sp.simplify(raw_values[0, 0].subs(substitutions))
    if fixture_value != sp.Rational(31, 5):
        raise ValueError("rational Berger obstruction normalization drifted")
    normalized_witness = sp.simplify(raw_witness / fixture_value)
    normalized_values = (normalized_witness.T * image_fixture).applyfunc(sp.simplify)
    if normalized_values != sp.Matrix([[1, 0]]):
        raise ValueError("normalized obstruction witness failed")

    # The unobstructed cross column is exactly a physical equation class.
    cross_coefficient = sp.simplify((u * (2 * v - u)).subs(substitutions))
    if cross_coefficient != sp.Rational(71, 40):
        raise ValueError("cross-column descent coefficient drifted")
    if image_fixture[:, 1] != cross_coefficient * equation_inclusion[:, 1]:
        raise ValueError("cross-column filtered lift drifted")

    return {
        "dependencies": {
            "physical_helicity_filtered_quotient": _dependency(PHYSICAL, physical),
            "principal_branch_anchor": _dependency(PRINCIPAL, principal),
            "rank_46_STF2_graph_carrier": _dependency(CARRIER, carrier),
            "retained_minimal_q1": _dependency(Q1, q1),
            "rank_36_fixture_authority": _dependency(RANK36, rank36),
            "V2_artifact": {
                "artifact_id": "Berger_V2_sparse_operator",
                "path": artifact["path"],
                "sha256": artifact["sha256"],
            },
        },
        "fixture": {"u": str(u0), "v": str(v0), "alpha_B": "5"},
        "ranks": ranks,
        "raw_witness": raw_witness,
        "raw_values": raw_values,
        "fixture_value": fixture_value,
        "normalized_witness": normalized_witness,
        "normalized_values": normalized_values,
        "cross_coefficient": cross_coefficient,
        "boundary": boundary_fixture,
        "image": image_fixture,
    }


def build() -> dict:
    data = _exact_data()
    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-berger-retained-46-stf2-subprincipal-branch-anchor-or-obstruction-v1",
        "result_id": "BERGER_RETAINED_46_STF2_SUBPRINCIPAL_BRANCH_ANCHOR_OR_OBSTRUCTION_V1",
        "result_state": "SUBPRINCIPAL_PHYSICAL_MODULE_LIFT_OBSTRUCTED_AT_STANDARD_NULL_FIBRE",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "method_tags": ["FILTERED-SYMBOL-COMPLEX", "PBW-REES-PAGE", "EXACT-LEFT-NULL-WITNESS"],
        "dependency_refs": data["dependencies"],
        "filtered_lift_problem": {
            "covector": [1, 1, 0, 0],
            "field_basis": ["h_hat_22-h_hat_33", "h_hat_23"],
            "equation_dual_basis": ["(h_hat_star_22-h_hat_star_33)/2", "h_hat_star_23"],
            "equation": "sigma_2(V2) I_phys + sigma_2(V2) sigma_1(K_spatial) B = sigma_4(H_retained) C + J_phys A",
            "unknown_correction_shapes": {"B": [3, 2], "C": [10, 2], "A": [2, 2]},
            "why_this_is_invariant": "the equation includes arbitrary principal gauge changes of the field representatives, every principal Hessian boundary, and every physical-equation representative; testing quotient membership does not choose a complement and is not raw Pi_TT V2 Pi_TT compression",
            "absence_of_intermediate_page": "A10=Box_2^2+V2 in covariant PBW normal form; on q=0 the biwave order-three page is proportional to q and the first nonzero endpoint correction is sigma_2(V2)",
            "rank_ledger": data["ranks"],
        },
        "normalized_obstruction": {
            "fixture": data["fixture"],
            "generic_left_null_covector": _column_record(data["raw_witness"]),
            "generic_evaluation_on_physical_columns": _matrix_record(data["raw_values"]),
            "generic_obstruction_polynomial": "-8*u*(u-v)",
            "fixture_obstruction_value": str(data["fixture_value"]),
            "normalized_left_null_covector": _column_record(data["normalized_witness"]),
            "normalized_evaluation_on_physical_columns": _matrix_record(data["normalized_values"]),
            "first_failed_polarization": "h_hat_22-h_hat_33",
            "first_failed_equation": "sigma_2(V2)(I_plus+sigma_1(K_spatial)B) not in im(sigma_4(H_retained)) + im(J_phys) for every B",
            "cross_polarization_lifts": True,
            "cross_physical_equation_coefficient": str(data["cross_coefficient"]),
        },
        "carrier_consequence": {
            "rank_46_contractible_graph_can_remove_obstruction": False,
            "reason": "the graph shear has exact Schur complement A10 and is a cyclic SDR; a contractible filtered extension cannot change this quotient class",
            "requested_support_local_branch_projector_on_rank_46": False,
            "minimum_standard_fibre_enlargement": "one additional equation cohomology direction and its cyclic-dual field direction (two BV rows)",
            "global_covariant_enlargement_rank_certified": False,
            "next_honest_options": [
                "enlarge the leading filtered cohomology carrier and close its invariant bundle orbit",
                "use a mixed-bundle curvature mapping cylinder",
                "retain the unsplit cyclic causal complex",
                "use a separately tagged nonlocal REDUCED-MODE decomposition",
            ],
        },
        "exact_checks": {
            "all_allowed_filtered_corrections_included": True,
            "gauge_representative_freedom_included": True,
            "allowed_boundary_rank_four": True,
            "plus_column_raises_rank_to_five": True,
            "cross_column_remains_in_allowed_boundary": True,
            "generic_left_null_witness_annihilates_allowed_boundary": True,
            "generic_obstruction_polynomial_exact": True,
            "fixture_obstruction_normalized_to_one": True,
            "cross_descent_coefficient_71_over_40": True,
            "rank_46_graph_SDR_preserves_obstruction_class": True,
        },
        "claim_flags": {
            "V2_FILTERED_DESCENT_COMPUTED": True,
            "SUBPRINCIPAL_BRANCH_ANCHOR_AVAILABLE": False,
            "RANK46_SUPPORT_LOCAL_BRANCH_PROJECTOR_ACCEPTED": False,
            "RANK46_PHYSICAL_FILTERED_LIFT_OBSTRUCTED": True,
            "GLOBAL_ALL_CARRIER_PROJECTOR_NO_GO": False,
            "ELL3_BRANCH_MIXING_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "UNSPLIT_RETAINED_COMPLEX_OR_NONCONTRACTIBLE_FILTERED_ENLARGEMENT",
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_retained_46_stf2_subprincipal_branch_anchor_or_obstruction.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_retained_46_stf2_subprincipal_branch_anchor_or_obstruction.py",
                "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_46_stf2_subprincipal_branch_anchor_or_obstruction",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-retained-46-stf2-subprincipal-branch-anchor-or-obstruction-v1.schema.json -d d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_SUBPRINCIPAL_BRANCH_ANCHOR_OR_OBSTRUCTION_V1.json",
            ],
        },
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC certificate solves the first nonzero filtered V2 lifting equation for the certified rank-two physical helicity projective module. At zeta=(1,1,0,0), the plus polarization has a normalized nonzero quotient class while the cross polarization lifts with coefficient 71/40. Hence the declared physical module does not descend to a closed filtered subcomplex, and the requested support-local Einstein-like/extra-Weyl projector with that principal anchor is obstructed on the exact rank-46 contractible graph carrier. This is not raw TT compression: the calculation quotients by every principal Hessian boundary and every physical-equation representative. It does not rule out a different leading cohomology carrier, a noncontractible or mixed-bundle mapping cylinder, or a nonlocal reduced-mode splitting. It does not authorize ell3 branch mixing, infer a kinetic sign, or make a quantum claim."
        ),
    }


def validate(value: dict) -> None:
    if value.get("result_state") != "SUBPRINCIPAL_PHYSICAL_MODULE_LIFT_OBSTRUCTED_AT_STANDARD_NULL_FIBRE":
        raise ValueError("subprincipal result state drifted")
    if not all(value.get("exact_checks", {}).values()):
        raise ValueError("subprincipal exact check dropped")
    flags = value.get("claim_flags", {})
    if (
        flags.get("V2_FILTERED_DESCENT_COMPUTED") is not True
        or flags.get("RANK46_PHYSICAL_FILTERED_LIFT_OBSTRUCTED") is not True
        or any(
            flags.get(name) is not False
            for name in (
                "SUBPRINCIPAL_BRANCH_ANCHOR_AVAILABLE",
                "RANK46_SUPPORT_LOCAL_BRANCH_PROJECTOR_ACCEPTED",
                "GLOBAL_ALL_CARRIER_PROJECTOR_NO_GO",
                "ELL3_BRANCH_MIXING_AUTHORIZED",
                "QUANTUM_CLAIM",
            )
        )
    ):
        raise ValueError("subprincipal claim boundary drifted")
    if value["normalized_obstruction"]["normalized_evaluation_on_physical_columns"] != [["1", "0"]]:
        raise ValueError("normalized obstruction witness drifted")


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Rank-46 STF2 subprincipal branch-anchor obstruction

The first nonzero filtered endpoint equation is not obtained by compressing
the raw ten-component matrix.  It is the quotient lifting problem

\[
\sigma_2(V_2)I_{\rm phys}
=\sigma_4(H_{\rm retained})C+J_{\rm phys}A.
\]

The complete equation also permits an arbitrary principal gauge change of the
field representative:

\[
\sigma_2(V_2)I_{\rm phys}+\sigma_2(V_2)\sigma_1(K)B
=\sigma_4(H_{\rm retained})C+J_{\rm phys}A.
\]

Thus solvability is gauge- and complement-independent.

At the exact null fibre \(\zeta=(1,1,0,0)\), the allowed correction space has
rank four.  Adjoining the \(V_2\) image of
\(h_{22}-h_{33}\) raises the rank to five, while adjoining the image of
\(h_{23}\) leaves the rank equal to four.  The generic left-null witness

\[
\ell=(-1,2,0,0,5,0,\ldots,0)
\]

annihilates every allowed correction and evaluates on the two physical
columns as

\[
\ell^T\sigma_2(V_2)I_{\rm phys}
=\bigl(-8u(u-v),0\bigr).
\]

At the rational Berger fixture this is \((31/5,0)\).  The normalized witness
is \((-5/31,10/31,0,0,25/31,0,\ldots,0)\) and evaluates to \((1,0)\).  The cross
polarization does lift, with physical equation coefficient \(71/40\).

Therefore the certified rank-two physical helicity module does not descend
through the \(V_2\) page.  The exact rank-46 STF2 graph complement cannot
remove this class because its Schur complement is \(A_{10}\) and it is
cyclically contractible.  The requested support-local Einstein-like/extra-Weyl
projector with this principal anchor is obstructed.

This is scoped.  It does not rule out a noncontractible filtered enlargement,
a mixed-bundle curvature mapping cylinder, or a separately tagged nonlocal
reduced-mode splitting.  At the standard fibre any local repair must add at
least one equation cohomology direction and its cyclic-dual field direction;
the rank of a global invariant bundle closure is not asserted here.
"""


def _guards(value: dict) -> None:
    mutations = [
        ("accept projector", ("claim_flags", "RANK46_SUPPORT_LOCAL_BRANCH_PROJECTOR_ACCEPTED"), True),
        ("drop obstruction", ("claim_flags", "RANK46_PHYSICAL_FILTERED_LIFT_OBSTRUCTED"), False),
        ("authorize mixing", ("claim_flags", "ELL3_BRANCH_MIXING_AUTHORIZED"), True),
        ("drop rank witness", ("exact_checks", "plus_column_raises_rank_to_five"), False),
    ]
    for name, path, replacement in mutations:
        mutant = deepcopy(value)
        mutant[path[0]][path[1]] = replacement
        try:
            validate(mutant)
        except ValueError:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report():
            raise AssertionError("subprincipal branch outputs drifted")
    if args.guards:
        _guards(value)
    print("BERGER_RETAINED_46_STF2_SUBPRINCIPAL_BRANCH_ANCHOR_OR_OBSTRUCTION_V1: PASS")


if __name__ == "__main__":
    main()
