#!/usr/bin/env python3
"""Independent, process-isolated replay of the repaired-q70 low-j theorem.

The producer is intentionally not imported.  Each expensive exact-algebra
stage is executed in a fresh Python process so algebraic-number caches cannot
turn a finite verification into an operationally unbounded one.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp
from sympy import QQ


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SELF = Path(__file__).resolve()
CERT = HERE / "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_V1.json"
PAYLOAD = HERE / "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_PAYLOAD_V1.json"
CERT_SCHEMA = HERE / "schema/two-phase-counterflow-repaired-q70-low-j-stabilizer-health-v1.schema.json"
PAYLOAD_SCHEMA = HERE / "schema/two-phase-counterflow-repaired-q70-low-j-stabilizer-health-payload-v1.schema.json"
PARENT = HERE / "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V2.json"
OPERATOR = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"

Z = sp.Symbol("z")
Y = sp.Symbol("y")
SQRT10 = sp.sqrt(10)
C = 3 * SQRT10 / 20
U = C
V = 2 * SQRT10 / 3

FACTOR_DATA = {
    0: [
        (9 * Z**2 + 58, 2),
        (3240 * Z**4 + 106533 * Z**2 + 872836, 2),
        (3200 * Z**6 + 12600 * Z**4 + 7605 * Z**2 - 7812, 1),
    ],
    2: [
        (Z**2 + 2, 1),
        (9 * Z**2 + 196, 2),
        (40 * Z**4 + 3013 * Z**2 + 56574, 2),
        (3240 * Z**4 + 113013 * Z**2 + 986578, 2),
        (3200 * Z**8 + 44600 * Z**6 + 189205 * Z**4 + 235096 * Z**2 + 82944, 1),
        (
            7558272000 * Z**10
            + 268203182400 * Z**8
            + 3648301495200 * Z**6
            + 23672119906305 * Z**4
            + 73066019605029 * Z**2
            + 85345353120218,
            2,
        ),
    ],
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _expr(value: Any) -> str:
    return sp.sstr(sp.factor(value))


def _generators(two_j: int) -> list[sp.Matrix]:
    """Independent skew-Hermitian spin-j representation in the Berger frame."""
    n = two_j + 1
    spin = sp.Rational(two_j, 2)
    weights = [-spin + index for index in range(n)]
    raising = sp.zeros(n)
    for index, weight in enumerate(weights[:-1]):
        raising[index + 1, index] = sp.sqrt((spin - weight) * (spin + weight + 1))
    lowering = raising.T
    return [
        -sp.I * (raising + lowering) / 2,
        (lowering - raising) / 2,
        -sp.I * sp.diag(*weights) / C,
    ]


def _finite(record: dict[str, Any], two_j: int, alpha_b: sp.Expr = sp.Integer(1)) -> sp.Matrix:
    n = two_j + 1
    spatial = _generators(two_j)
    result = sp.MutableSparseMatrix(record["shape"][0] * n, record["shape"][1] * n, {})
    for row, column, terms in record["entries"]:
        block = sp.zeros(n)
        for exponents, raw in terms:
            word = sp.eye(n) * Z ** exponents[0]
            for axis in range(3):
                word *= spatial[axis] ** exponents[axis + 1]
            coefficient = sp.sympify(raw, locals={"u": U, "v": V, "alpha_B": alpha_b})
            block += coefficient * word
        for left in range(n):
            for right in range(n):
                if block[left, right] != 0:
                    result[row * n + left, column * n + right] = sp.expand(block[left, right])
    return sp.Matrix(result)


def _conjugation(two_j: int) -> sp.Matrix:
    n = two_j + 1
    spin = sp.Rational(two_j, 2)
    value = sp.zeros(n)
    for column, weight in enumerate([-spin + index for index in range(n)]):
        value[n - 1 - column, column] = (-1) ** int(spin - weight)
    return value


def _pairing(record: dict[str, Any], two_j: int) -> sp.Matrix:
    n = two_j + 1
    conjugation = _conjugation(two_j)
    result = sp.MutableSparseMatrix(record["shape"][0] * n, record["shape"][1] * n, {})
    for row, column, terms in record["entries"]:
        coefficient = sp.sympify(terms[0][1])
        for left in range(n):
            for right in range(n):
                if conjugation[left, right] != 0:
                    result[row * n + left, column * n + right] = coefficient * conjugation[left, right]
    return sp.Matrix(result)


def _matrix_hash(matrix: sp.Matrix) -> str:
    core = {
        "shape": [matrix.rows, matrix.cols],
        "entries": [
            [row, column, _expr(value)]
            for (row, column), value in matrix.todok().items()
            if value != 0
        ],
    }
    return _digest(core)


def _physical(two_j: int, operator: dict[str, Any]) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix]:
    blocks = operator["q1_blocks"]
    gauge = _finite(blocks["K_spatial"], two_j)
    hessian = _finite(blocks["H_retained"], two_j)
    identity = _finite(blocks["minus_K_spatial_sharp"], two_j)
    _, gauge_pivots = gauge.subs(Z, 1).T.rref()
    _, identity_pivots = identity.subs(Z, 1).rref()
    if gauge_pivots != identity_pivots or len(gauge_pivots) != 3 * (two_j + 1):
        raise AssertionError("independent localized quotient chart failed")
    free = [index for index in range(hessian.rows) if index not in gauge_pivots]
    return gauge, hessian, identity, hessian.extract(free, free)


def _nullspace_mod(matrix: sp.Matrix, polynomial: sp.Expr) -> tuple[list[list[Any]], Any, Any, int]:
    field = QQ.algebraic_field(sp.sqrt(2), sp.sqrt(5), SQRT10, sp.I)
    ring = field.poly_ring(Z)
    modulus = ring.from_sympy(polynomial)
    rows = [
        [ring.rem(ring.from_sympy(sp.expand(matrix[row, column])), modulus) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]
    pivot_row = 0
    pivots: list[int] = []
    for column in range(matrix.cols):
        found = next((row for row in range(pivot_row, matrix.rows) if rows[row][column]), None)
        if found is None:
            continue
        rows[pivot_row], rows[found] = rows[found], rows[pivot_row]
        inverse = ring.invert(rows[pivot_row][column], modulus)
        rows[pivot_row] = [ring.rem(value * inverse, modulus) for value in rows[pivot_row]]
        for row in range(matrix.rows):
            if row != pivot_row and rows[row][column]:
                multiplier = rows[row][column]
                rows[row] = [
                    ring.rem(rows[row][entry] - multiplier * rows[pivot_row][entry], modulus)
                    for entry in range(matrix.cols)
                ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == matrix.rows:
            break
    free = [column for column in range(matrix.cols) if column not in pivots]
    basis = [[ring.zero for _ in free] for _ in range(matrix.cols)]
    for basis_column, free_column in enumerate(free):
        basis[free_column][basis_column] = ring.one
        for row, pivot in enumerate(pivots):
            basis[pivot][basis_column] = ring.rem(-rows[row][free_column], modulus)
    return basis, ring, modulus, len(pivots)


def _residue_nondegenerate(matrix: sp.Matrix, polynomial: sp.Expr, expected_nullity: int) -> tuple[int, bool]:
    right, ring, modulus, rank = _nullspace_mod(matrix, polynomial)
    left, _, _, left_rank = _nullspace_mod(matrix.T, polynomial)
    if matrix.cols - rank != expected_nullity or matrix.rows - left_rank != expected_nullity:
        raise AssertionError("left/right factor-field nullity failed")
    derivative = [
        [ring.rem(ring.from_sympy(sp.expand(matrix.diff(Z)[row, column])), modulus) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]

    def multiply(left_matrix: list[list[Any]], right_matrix: list[list[Any]]) -> list[list[Any]]:
        return [
            [
                ring.rem(
                    sum((left_matrix[row][middle] * right_matrix[middle][column] for middle in range(len(right_matrix))), ring.zero),
                    modulus,
                )
                for column in range(len(right_matrix[0]))
            ]
            for row in range(len(left_matrix))
        ]

    residue = multiply(multiply([list(row) for row in zip(*left)], derivative), right)
    determinant = residue[0][0]
    if expected_nullity == 2:
        determinant = ring.rem(residue[0][0] * residue[1][1] - residue[0][1] * residue[1][0], modulus)
    if not determinant:
        raise AssertionError("descended residue pairing degenerated")
    numerator = sp.together(ring.to_sympy(determinant)).as_numer_denom()[0]
    if sp.gcd(sp.Poly(numerator, Z), sp.Poly(polynomial, Z)).degree() != 0:
        raise AssertionError("residue determinant is not a factor-field unit")
    return rank, True


def _stage_parent(two_j: int, parent: dict[str, Any], payload: dict[str, Any]) -> None:
    key = "j0" if two_j == 0 else "j1"
    operators = parent["operators"]
    q = _finite(operators["q70"], two_j)
    stored = payload["exceptional_blocks"][key]["finite_parent"]["q70"]
    if _matrix_hash(q) != stored["sha256"] or len(q.todok()) != stored["nonzero_entry_count"]:
        raise AssertionError("finite q70 manifest failed")
    if any(sp.simplify(value) != 0 for value in (q * q).todok().values()):
        raise AssertionError("finite q70 square failed")
    homotopy = _finite(operators["S70"], two_j)
    inclusion = _finite(operators["iota70_from_26"], two_j)
    projection = _finite(operators["pi26_from_70"], two_j)
    full = 70 * (two_j + 1)
    retained = 26 * (two_j + 1)
    if projection * inclusion != sp.eye(retained):
        raise AssertionError("projection/inclusion failed")
    if q * homotopy + homotopy * q != sp.eye(full) - inclusion * projection:
        raise AssertionError("homotopy identity failed")
    if (
        homotopy * homotopy != sp.zeros(full)
        or homotopy * inclusion != sp.zeros(full, retained)
        or projection * homotopy != sp.zeros(retained, full)
    ):
        raise AssertionError("contraction side condition failed")
    pairing = _pairing(operators["pairing70"], two_j)
    cyclic = q.subs(Z, -Z).T * pairing + pairing * q
    if pairing.rank() != full or any(sp.simplify(value) != 0 for value in cyclic.todok().values()):
        raise AssertionError("cross-m cyclicity failed")


def _complement(ambient: list[sp.Matrix], image: list[sp.Matrix]) -> list[sp.Matrix]:
    columns = list(image)
    rank = sp.Matrix.hstack(*columns).rank() if columns else 0
    result: list[sp.Matrix] = []
    for vector in ambient:
        trial = sp.Matrix.hstack(*(columns + [vector]))
        if trial.rank() > rank:
            result.append(vector)
            columns.append(vector)
            rank += 1
    return result


def _stage_zero(two_j: int, parent: dict[str, Any], operator: dict[str, Any], payload: dict[str, Any]) -> None:
    key = "j0" if two_j == 0 else "j1"
    gauge, hessian, identity, physical = _physical(two_j, operator)
    if _finite(operator["q1_blocks"]["H_retained"], two_j, sp.Integer(5)) != 5 * hessian:
        raise AssertionError("selected alpha_B normalization failed")
    if sp.simplify(hessian * gauge) != sp.zeros(hessian.rows, gauge.cols) or sp.simplify(identity * hessian) != sp.zeros(identity.rows, hessian.cols):
        raise AssertionError("Noether complex failed")
    ranks = [matrix.subs(Z, 0).rank() for matrix in (gauge, hessian, identity)]
    zero = payload["exceptional_blocks"][key]["zero_frequency_full_complex"]
    if ranks != zero["specialized_ranks_K_H_Ksharp"]:
        raise AssertionError("z=0 ranks failed")
    n = two_j + 1
    dimensions = [3 * n - ranks[0], 10 * n - ranks[0] - ranks[1], 10 * n - ranks[1] - ranks[2], 3 * n - ranks[2]]
    if dimensions != [1, 1, 1, 1] or dimensions != zero["cohomology_dimensions_Hminus1_H0_H1_H2"]:
        raise AssertionError("z=0 cohomology failed")
    stored = payload["exceptional_blocks"][key]["localized_nonzero_frequency_quotient"]["physical_matrix"]
    if _matrix_hash(physical) != stored["sha256"]:
        raise AssertionError("physical matrix manifest failed")

    gauge0, hessian0, identity0 = (matrix.subs(Z, 0) for matrix in (gauge, hessian, identity))
    representatives = (
        gauge0.nullspace(),
        _complement(hessian0.nullspace(), gauge0.columnspace()),
        _complement(identity0.nullspace(), hessian0.columnspace()),
        _complement([sp.eye(3 * n)[:, index] for index in range(3 * n)], identity0.columnspace()),
    )
    parent_pairing = _pairing(parent["operators"]["pairing70"], two_j)
    inclusion = _finite(parent["operators"]["iota70_from_26"], two_j)
    pairing26 = inclusion.subs(Z, -Z).T * parent_pairing * inclusion
    offsets = [0, 3 * n, 13 * n, 23 * n]
    widths = [3 * n, 10 * n, 10 * n, 3 * n]
    embedded = []
    for offset, width, vectors in zip(offsets, widths, representatives):
        for vector in vectors:
            full = sp.zeros(26 * n, 1)
            full[offset : offset + width, 0] = vector
            embedded.append(full)
    basis = sp.Matrix.hstack(*embedded)
    descended = sp.simplify(basis.T * pairing26 * basis)
    if descended.rank() != 4 or zero["pairing_rank"] != 4 or zero["pairing_radical_dimension"] != 0:
        raise AssertionError("z=0 descended pairing failed")
    if zero["ordinary_inertia"] != "NOT_APPLICABLE_TO_GRADED_PAIRING":
        raise AssertionError("graded-pairing inertia boundary failed")


def _expected_determinant(two_j: int) -> sp.Expr:
    if two_j == 0:
        return -Y**2 * (9 * Y + 58) ** 2 * (3240 * Y**2 + 106533 * Y + 872836) ** 2 * (3200 * Y**3 + 12600 * Y**2 + 7605 * Y - 7812) / sp.Integer(185752092672000000)
    return -Y**8 * (Y + 2) * (9 * Y + 196) ** 2 * (40 * Y**2 + 3013 * Y + 56574) ** 2 * (3240 * Y**2 + 113013 * Y + 986578) ** 2 * (3200 * Y**4 + 44600 * Y**3 + 189205 * Y**2 + 235096 * Y + 82944) * (7558272000 * Y**5 + 268203182400 * Y**4 + 3648301495200 * Y**3 + 23672119906305 * Y**2 + 73066019605029 * Y + 85345353120218) ** 2 / sp.Integer(79125437933256602109650097143808000000000000000000)


def _stage_determinant(two_j: int, operator: dict[str, Any], payload: dict[str, Any]) -> None:
    key = "j0" if two_j == 0 else "j1"
    _, _, _, physical = _physical(two_j, operator)
    expected_y = sp.factor(_expected_determinant(two_j))
    stored = sp.sympify(payload["exceptional_blocks"][key]["spectrum"]["determinant_in_y"], locals={"y": Y})
    if sp.expand(stored - expected_y) != 0:
        raise AssertionError("stored determinant factorization failed")
    expected_z = sp.expand(expected_y.subs(Y, Z**2))
    actual_z = sp.factor(physical.det(method="domain-ge"))
    if sp.expand(actual_z - expected_z) != 0:
        raise AssertionError("direct polynomial determinant identity failed")


def _stage_rank(two_j: int, factor_index: int, operator: dict[str, Any], payload: dict[str, Any]) -> None:
    key = "j0" if two_j == 0 else "j1"
    _, _, _, physical = _physical(two_j, operator)
    factor, exponent = FACTOR_DATA[two_j][factor_index]
    rank, residue_nondegenerate = _residue_nondegenerate(physical, factor, exponent)
    audit = payload["exceptional_blocks"][key]["spectrum"]["nonzero_factor_audits"][factor_index]
    if rank != physical.rows - exponent or rank != audit["physical_rank_over_factor_field"]:
        raise AssertionError("factor-field rank/nullity failed")
    if audit["H0_dimension"] != exponent or audit["H1_dimension"] != exponent:
        raise AssertionError("factor cohomology multiplicity failed")
    if not residue_nondegenerate or audit["residue_nondegenerate"] is not True or audit["pairing_radical_dimension"] != 0:
        raise AssertionError("descended residue pairing failed")


def _stage_census(operator: dict[str, Any], payload: dict[str, Any]) -> None:
    rows = payload["representation_census"]["direct_matrix_rows"]
    observed = []
    for two_j in range(7):
        gauge = _finite(operator["q1_blocks"]["K_spatial"], two_j).subs(Z, 0)
        nullity = gauge.cols - gauge.rank()
        observed.append(two_j) if nullity else None
        if rows[two_j]["stabilizer_nullity_per_fixed_m"] != nullity:
            raise AssertionError("representation census failed")
    if observed != [0, 2]:
        raise AssertionError("exceptional representation list failed")
    if sum((two_j + 1) * rows[two_j]["stabilizer_nullity_per_fixed_m"] for two_j in observed) != 4:
        raise AssertionError("Berger stabilizer dimension failed")
    disposition = payload["representation_census"]["absent_tensor_harmonic_disposition"]
    if disposition["j0_field_rows_retained"] != 10 or disposition["j1_field_rows_retained"] != 30:
        raise AssertionError("low-j invariant-coframe row census failed")
    if disposition["row_deletion_policy"] != "NO_ROW_IS_DELETED_BY_TT_OR_VECTOR_TENSOR_HARMONIC_AVAILABILITY":
        raise AssertionError("absent tensor-harmonic policy failed")


def _stage_mutations(payload: dict[str, Any]) -> None:
    generators = _generators(2)
    if generators[0][0, 1] == 0 or generators[0][2, 1] == 0:
        raise AssertionError("isolated j=1 k=0 mutation unexpectedly closed")
    expected = {
        "isolated_k0_at_j1": "REJECTED_BY_NONZERO_E1_E2_LADDER_BOUNDARY",
        "generic_rank_substitution": "REJECTED_BY_EXACT_NULLITY_ONE_AT_TWO_J_0_AND_2",
        "stabilizer_deleted_as_gauge": "REJECTED_BY_NONDEGENERATE_FOUR_DIMENSIONAL_SPECIALIZED_COHOMOLOGY_PAIRING",
    }
    for key, value in expected.items():
        if payload["mutations"][key] != value:
            raise AssertionError(f"mutation verdict drifted: {key}")


def _stage_charges(parent: dict[str, Any], payload: dict[str, Any]) -> None:
    ledger = payload["charge_actions"]
    if ledger["spatial_Killing_stabilizers"]["K"] != "D-(3/4)R_rel=D on these rows":
        raise AssertionError("D/R_rel/K stabilizer action failed")
    diagonal = ledger["repaired_diagonal_U1"]
    if diagonal["classification"] != "contractible local gauge generator with zero local Gauss charge":
        raise AssertionError("diagonal-U1 classification failed")
    if diagonal["physical_cohomology"] != "ZERO" or diagonal["local_Gauss_charge"] != "ZERO":
        raise AssertionError("diagonal-U1 charge/cohomology failed")
    for two_j in (0, 2):
        n = two_j + 1
        q16 = _finite(parent["operators"]["u1_q16"], two_j)
        s16 = _finite(parent["operators"]["u1_S16"], two_j)
        pairing16 = _pairing(parent["operators"]["u1_pairing16"], two_j)
        if any(sp.simplify(value) != 0 for value in (q16 * q16).todok().values()):
            raise AssertionError("diagonal-U1 square failed")
        if q16 * s16 + s16 * q16 != sp.eye(16 * n):
            raise AssertionError("diagonal-U1 contraction failed")
        cyclic = q16.subs(Z, -Z).T * pairing16 + pairing16 * q16
        if pairing16.rank() != 16 * n or any(sp.simplify(value) != 0 for value in cyclic.todok().values()):
            raise AssertionError("diagonal-U1 cyclic pairing failed")
    if ledger["nonzero_characteristic_modes"]["unrestricted_vs_fixed_charge"] != "IDENTICAL":
        raise AssertionError("fixed/unrestricted nonzero-frequency comparison failed")


def _stage_roots(payload: dict[str, Any]) -> None:
    for two_j, factors in FACTOR_DATA.items():
        key = "j0" if two_j == 0 else "j1"
        audits = payload["exceptional_blocks"][key]["spectrum"]["nonzero_factor_audits"]
        for (factor, _), audit in zip(factors, audits):
            polynomial = sp.Poly(factor.subs(Z**2, Y), Y)
            negative = int(polynomial.count_roots(-sp.oo, 0))
            positive = int(polynomial.count_roots(0, sp.oo))
            real = int(polynomial.count_roots(-sp.oo, sp.oo))
            counts = audit["root_counts"]
            if [negative, positive, polynomial.degree() - real] != [counts["negative_real_y_roots"], counts["positive_real_y_roots"], counts["nonreal_y_roots"]]:
                raise AssertionError("exact root classification failed")
    if payload["exceptional_blocks"]["j0"]["spectrum"]["unstable_sector"]["energy"]["inertia_positive_negative_zero"] != [3, 3, 0]:
        raise AssertionError("j0 energy inertia failed")
    unstable = payload["exceptional_blocks"]["j1"]["spectrum"]["unstable_sectors"]
    if [entry["two_copy_inertia_positive_negative_zero"] for entry in unstable] != [[4, 4, 0], [8, 12, 0]]:
        raise AssertionError("j1 energy inertia failed")


def _load() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return tuple(json.loads(path.read_text()) for path in (CERT, PAYLOAD, PARENT, OPERATOR))  # type: ignore[return-value]


def _manifest(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    Draft202012Validator(json.loads(CERT_SCHEMA.read_text())).validate(certificate)
    Draft202012Validator(json.loads(PAYLOAD_SCHEMA.read_text())).validate(payload)
    if certificate["payload_ref"]["sha256"] != _sha(PAYLOAD):
        raise AssertionError("payload file hash failed")
    if payload["content_sha256"] != _digest({key: value for key, value in payload.items() if key != "content_sha256"}):
        raise AssertionError("payload content hash failed")
    for record in payload["imports"].values():
        imported = json.loads((ROOT / record["path"]).read_text())
        if _sha(ROOT / record["path"]) != record["sha256"] or imported["result_id"] != record["result_id"]:
            raise AssertionError("pinned import drifted")
    if payload["normalization"]["selected_action_alpha_B"] != "5" or payload["normalization"]["computed_monic_representative_alpha_B"] != "1":
        raise AssertionError("action normalization drifted")


def _run_children() -> None:
    commands = ["census", "mutations", "charges", "roots", "parent:0", "parent:2", "zero:0", "zero:2", "det:0", "det:2"]
    commands.extend(f"rank:{two_j}:{index}" for two_j in (0, 2) for index in range(len(FACTOR_DATA[two_j])))
    for stage in commands:
        subprocess.run([sys.executable, str(SELF), "--stage", stage], cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage")
    args = parser.parse_args()
    certificate, payload, parent, operator = _load()
    _manifest(certificate, payload)
    if args.stage is None:
        _run_children()
        print("independent repaired q70 low-j/stabilizer health: PASS")
        return
    parts = args.stage.split(":")
    if parts[0] == "parent":
        _stage_parent(int(parts[1]), parent, payload)
    elif parts[0] == "zero":
        _stage_zero(int(parts[1]), parent, operator, payload)
    elif parts[0] == "det":
        _stage_determinant(int(parts[1]), operator, payload)
    elif parts[0] == "rank":
        _stage_rank(int(parts[1]), int(parts[2]), operator, payload)
    elif parts[0] == "census":
        _stage_census(operator, payload)
    elif parts[0] == "mutations":
        _stage_mutations(payload)
    elif parts[0] == "charges":
        _stage_charges(parent, payload)
    elif parts[0] == "roots":
        _stage_roots(payload)
    else:
        raise SystemExit(f"unknown verifier stage: {args.stage}")


if __name__ == "__main__":
    main()
