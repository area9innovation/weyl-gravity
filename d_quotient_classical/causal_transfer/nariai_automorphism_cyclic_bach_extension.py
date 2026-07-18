#!/usr/bin/env python3
"""Odd-cyclic Bach extension of the Nariai automorphism prolongation.

The curvature-corrected first two rows form the local constraint complex

    C0 --G=(d_aut,Kp0)--> C1+H1 --P=(M,-Phi)--> C1*.

Its canonical odd-cotangent completion retains a multiplier ``lambda`` in
``C1`` and is the Hessian of

    1/2 <h,B h> + <lambda,M a-Phi h>.

In the ordered eight-block carrier

    epsilon ; (a,h,lambda) ; (a#,h#,lambda#) ; epsilon#

the differential is therefore forced by ``G``, the saddle Hessian, and their
formal adjoints.  No inverse curvature map, projector, or fitted cotangent row
is introduced.  The corrected BGG graph embeds the exact four-row metric Bach
complex isometrically and as a strict chain map.

This certificate deliberately stops before an SDR or Green homotopy.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)
from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    FibrePBW,
    _tensor_product_curvature,
)
from d_quotient_classical.causal_transfer.nariai_automorphism_prolongation_first_two_rows import (
    OUTPUT as FIRST_TWO_CERTIFICATE,
    fixture as automorphism_fixture,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    NariaiBackground,
    ROOT,
    _lc_adjoint_curvature,
    _sha256,
    _sparse,
    _sparse_table,
)
from d_quotient_classical.causal_transfer.nariai_metric_bach_cyclic_bv_complex import (
    OUTPUT as METRIC_CERTIFICATE,
    kernel as metric_kernel,
)
from d_quotient_classical.causal_transfer.nariai_linearized_bach_endpoint import (
    endpoint_operator,
)


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_AUTOMORPHISM_CYCLIC_BACH_EXTENSION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-automorphism-cyclic-bach-extension.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-automorphism-cyclic-bach-extension-v1.schema.json"
VERIFIER = HERE / "verify_nariai_automorphism_cyclic_bach_extension.py"
TESTS = HERE / "tests/test_nariai_automorphism_cyclic_bach_extension.py"
FIRST_TWO_PRODUCER = HERE / "nariai_automorphism_prolongation_first_two_rows.py"
METRIC_PRODUCER = HERE / "nariai_metric_bach_cyclic_bv_complex.py"
ACTION_PRODUCER = HERE / "nariai_linearized_bach_endpoint.py"
FORMAL_SOURCE = ROOT / "covariant_completion/minimal_witness/formal_operators.py"
PBW_SOURCE = ROOT / "covariant_completion/curved_operator/adjoint_tractor_bgg_curved_pbw.py"


O = OperatorPolynomial
Matrix = list[list[O]]
BLOCK_NAMES = (
    "epsilon_C0",
    "a_C1",
    "h_H1",
    "lambda_C1",
    "a_sharp_C1dual",
    "h_sharp_H1dual",
    "lambda_sharp_C1dual",
    "epsilon_sharp_C0dual",
)
BLOCK_DEGREES = (-1, 0, 0, 0, 1, 1, 1, 2)
BLOCK_RANKS = (15, 60, 9, 60, 60, 9, 60, 15)
SIZE = len(BLOCK_NAMES)
METRIC_SIZE = 4
Table = dict[tuple[int, ...], sp.Matrix]


def _zero(rows: int = SIZE, columns: int = SIZE) -> Matrix:
    return [[O.zero() for _ in range(columns)] for _ in range(rows)]


def _identity(size: int = SIZE) -> Matrix:
    value = _zero(size, size)
    for index in range(size):
        value[index][index] = O.identity()
    return value


def _add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][column] + right[row][column] for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def _scale(value: Matrix, coefficient: int | Fraction) -> Matrix:
    return [[entry.scale(coefficient) for entry in row] for row in value]


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    if len(left[0]) != len(right):
        raise AssertionError("abstract matrix shapes do not compose")
    value = _zero(len(left), len(right[0]))
    for row in range(len(left)):
        for column in range(len(right[0])):
            for middle in range(len(right)):
                value[row][column] = (
                    value[row][column] + left[row][middle] * right[middle][column]
                )
    return value


def _operator_adjoint(value: O) -> O:
    involution = {
        "d": "dsharp",
        "dsharp": "d",
        "k": "ksharp",
        "ksharp": "k",
        "M": "M",
        "Phi": "Phisharp",
        "Phisharp": "Phi",
        "B": "B",
        "L0": "L0sharp",
        "L0sharp": "L0",
        "L1": "L1sharp",
        "L1sharp": "L1",
        "p0sharp": "p0",
        "p0": "p0sharp",
        "K": "Ksharp",
        "Ksharp": "K",
    }
    return O._from_dict(
        {
            tuple(involution[name] for name in reversed(word)): coefficient
            for word, coefficient in value.terms
        }
    )


def _matrix_adjoint(value: Matrix) -> Matrix:
    return [
        [_operator_adjoint(value[column][row]) for column in range(len(value))]
        for row in range(len(value[0]))
    ]


def _degree_sign() -> Matrix:
    value = _zero()
    for index, degree in enumerate(BLOCK_DEGREES):
        value[index][index] = O.identity(-1 if degree % 2 else 1)
    return value


def _reduce_word(word: tuple[str, ...]) -> tuple[str, ...] | None:
    zero_pairs = {("B", "k"), ("ksharp", "B")}
    if any(word[index : index + 2] in zero_pairs for index in range(len(word) - 1)):
        return None
    replacements = {
        ("M", "d"): ("PG",),
        ("Phi", "k"): ("PG",),
        ("dsharp", "M"): ("PGsharp",),
        ("ksharp", "Phisharp"): ("PGsharp",),
        ("d", "L0"): ("L1", "K"),
        ("k", "L0"): ("K",),
        ("M", "L1"): ("Phi",),
        ("ksharp",): ("p0sharp", "Ksharp"),
        ("p0", "L0"): (),
        ("L0sharp", "p0sharp"): (),
    }
    changed = True
    current = word
    while changed:
        changed = False
        for old, new in replacements.items():
            for index in range(len(current) - len(old) + 1):
                if current[index : index + len(old)] == old:
                    current = current[:index] + new + current[index + len(old) :]
                    changed = True
                    break
            if changed:
                break
    return current


def _reduce(value: O) -> O:
    terms: dict[tuple[str, ...], Fraction] = {}
    for word, coefficient in value.terms:
        reduced = _reduce_word(word)
        if reduced is not None:
            terms[reduced] = terms.get(reduced, Fraction()) + coefficient
    return O._from_dict(terms)


def _matrix_zero(value: Matrix, *, modulo_relations: bool = False) -> bool:
    return all(
        (_reduce(entry) if modulo_relations else entry) == O.zero()
        for row in value
        for entry in row
    )


def _digest(value: Matrix) -> str:
    payload = "\n".join(
        ",".join(entry.display() for entry in row) for row in value
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def _serialize_operator(value: O) -> list[list[object]]:
    return [
        [list(word), coefficient.numerator, coefficient.denominator]
        for word, coefficient in value.terms
    ]


def _serialize_matrix(value: Matrix) -> dict[str, object]:
    return {
        "shape": [len(value), len(value[0])],
        "entries": [
            [row, column, _serialize_operator(value[row][column])]
            for row in range(len(value))
            for column in range(len(value[0]))
            if value[row][column] != O.zero()
        ],
        "sha256": _digest(value),
    }


def _count(table: Table) -> int:
    return sum(entry != 0 for matrix in table.values() for entry in matrix)


def abstract_kernel() -> dict[str, object]:
    q = _zero()
    q[1][0] = O.atom("d")
    q[2][0] = O.atom("k")
    q[4][3] = O.atom("M")
    q[5][2] = O.atom("B")
    q[5][3] = O.atom("Phisharp", -1)
    q[6][1] = O.atom("M")
    q[6][2] = O.atom("Phi", -1)
    q[7][4] = O.atom("dsharp")
    q[7][5] = O.atom("ksharp")

    pairing = _zero()
    for left, right in ((0, 7), (1, 4), (2, 5), (3, 6)):
        pairing[left][right] = O.identity()
        pairing[right][left] = O.identity(-1)

    metric_q = _zero(METRIC_SIZE, METRIC_SIZE)
    metric_q[1][0] = O.atom("K")
    metric_q[2][1] = O.atom("B")
    metric_q[3][2] = O.atom("Ksharp")
    metric_pairing = _zero(METRIC_SIZE, METRIC_SIZE)
    for left, right in ((0, 3), (1, 2)):
        metric_pairing[left][right] = O.identity()
        metric_pairing[right][left] = O.identity(-1)

    inclusion = _zero(SIZE, METRIC_SIZE)
    inclusion[0][0] = O.atom("L0")
    inclusion[1][1] = O.atom("L1")
    inclusion[2][1] = O.identity()
    inclusion[5][2] = O.identity()
    inclusion[7][3] = O.atom("p0sharp")

    square = _multiply(q, q)
    cyclic_defect = _add(
        _multiply(_matrix_adjoint(q), pairing),
        _multiply(_multiply(_degree_sign(), pairing), q),
    )
    chain_defect = _add(
        _multiply(q, inclusion), _scale(_multiply(inclusion, metric_q), -1)
    )
    pairing_pullback = _add(
        _multiply(_multiply(_matrix_adjoint(inclusion), pairing), inclusion),
        _scale(metric_pairing, -1),
    )
    return {
        "q": q,
        "pairing": pairing,
        "metric_q": metric_q,
        "metric_pairing": metric_pairing,
        "inclusion": inclusion,
        "square": square,
        "cyclic_defect": cyclic_defect,
        "chain_defect": chain_defect,
        "pairing_pullback": pairing_pullback,
    }


def coefficient_kernel() -> dict[str, object]:
    automorphism = automorphism_fixture()
    endpoint = endpoint_operator()
    metric = metric_kernel()
    background = NariaiBackground()
    curvature0 = _tensor_product_curvature(
        background, _lc_adjoint_curvature(), 0
    )
    pbw_c0 = FibrePBW(curvature0, background, "Nariai-C0-cyclic-Bach")
    bach_kp0 = pbw_c0.compose(endpoint["action_bach"], automorphism["k_p0"])
    algebraic = automorphism["middle"]["algebraic"]
    return {
        "automorphism": automorphism,
        "endpoint": endpoint,
        "metric": metric,
        "bach_kp0": bach_kp0,
        "pairings": {
            "C0": algebraic.adjoint_pairing,
            "C1": algebraic.one_form_pairing,
            "H0": algebraic.endpoint_ghost_pairing,
            "H1": algebraic.endpoint_field_pairing,
        },
        "p0sharp": algebraic.i_identity,
    }


def build() -> dict[str, object]:
    first_certificate = json.loads(FIRST_TWO_CERTIFICATE.read_text())
    metric_certificate = json.loads(METRIC_CERTIFICATE.read_text())
    if first_certificate["flags"]["AUTOMORPHISM_GAUGE_CONSTRAINT_COMPLEX"] is not True:
        raise ValueError("automorphism first-two-row theorem unavailable")
    if metric_certificate["flags"]["NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1"] is not True:
        raise ValueError("metric Bach cyclic complex unavailable")

    abstract = abstract_kernel()
    coefficient = coefficient_kernel()
    automorphism = coefficient["automorphism"]
    checks = {
        "abstract_Q_squared_mod_certified_relations": _matrix_zero(
            abstract["square"], modulo_relations=True
        ),
        "abstract_odd_cyclicity": _matrix_zero(abstract["cyclic_defect"]),
        "metric_graph_chain_map_mod_certified_relations": _matrix_zero(
            abstract["chain_defect"], modulo_relations=True
        ),
        "metric_pairing_pullback_mod_retract_relations": _matrix_zero(
            abstract["pairing_pullback"], modulo_relations=True
        ),
        "M_daut_minus_Phi_Kp0_entries": _count(automorphism["degree_one_defect"]),
        "B_Kp0_entries": _count(coefficient["bach_kp0"]),
        "daut_L0_minus_L1_K_entries": _count(automorphism["first_square_defect"]),
        "p0_L0_minus_identity_entries": _count(automorphism["projection_defect"]),
        "P_metric_graph_entries": _count(automorphism["graph_constraint_defect"]),
        "metric_BK_entries": coefficient["metric"]["checks"]["B_K_defect_entries"],
        "metric_KsharpB_entries": coefficient["metric"]["checks"]["Ksharp_B_defect_entries"],
    }
    if not all(
        value is True if isinstance(value, bool) else value == 0
        for value in checks.values()
    ):
        raise AssertionError("cyclic Bach extension did not close")

    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (
            Path(__file__).resolve(),
            VERIFIER,
            TESTS,
            SCHEMA,
            FIRST_TWO_PRODUCER,
            METRIC_PRODUCER,
            ACTION_PRODUCER,
            FORMAL_SOURCE,
            PBW_SOURCE,
        )
    }
    pairings = coefficient["pairings"]
    return {
        "schema": "pure-weyl-nariai-automorphism-cyclic-bach-extension-v1",
        "result_id": "NARIAI_AUTOMORPHISM_CYCLIC_BACH_EXTENSION_V1",
        "result_state": "ACTION_DERIVED_ODD_CYCLIC_AUTOMORPHISM_BACH_COMPLEX_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "automorphism_first_two_rows": {
                "artifact_id": first_certificate["result_id"],
                "path": str(FIRST_TWO_CERTIFICATE.relative_to(ROOT)),
                "sha256": _sha256(FIRST_TWO_CERTIFICATE),
            },
            "metric_bach_complex": {
                "artifact_id": metric_certificate["result_id"],
                "path": str(METRIC_CERTIFICATE.relative_to(ROOT)),
                "sha256": _sha256(METRIC_CERTIFICATE),
            },
        },
        "carrier": {
            "block_names": list(BLOCK_NAMES),
            "block_degrees": list(BLOCK_DEGREES),
            "block_ranks": list(BLOCK_RANKS),
            "total_rank": sum(BLOCK_RANKS),
            "interpretation": "odd cotangent saddle of the automorphism constraint complex",
        },
        "action": {
            "quadratic_density": "1/2<h,B_action h>+<lambda,M^D a-Phi h>",
            "B_source": "action-derived Weyl-squared Hessian",
            "Phi_definition": "M^D L1_corrected",
            "no_fitted_cotangent_rows": True,
        },
        "operators": {
            "abstract_Q": _serialize_matrix(abstract["q"]),
            "odd_pairing": _serialize_matrix(abstract["pairing"]),
            "metric_Q": _serialize_matrix(abstract["metric_q"]),
            "metric_pairing": _serialize_matrix(abstract["metric_pairing"]),
            "metric_graph_inclusion": _serialize_matrix(abstract["inclusion"]),
            "d_aut": _sparse_table(automorphism["d_aut"]),
            "K_p0": _sparse_table(automorphism["k_p0"]),
            "M_D": _sparse_table(automorphism["middle"]["yang_mills_middle"]),
            "Phi": _sparse_table(automorphism["phi"]),
            "B_action": _sparse_table(coefficient["endpoint"]["action_bach"]),
            "L0_corrected": _sparse_table(automorphism["corrected_l0"]),
            "L1_corrected": _sparse_table(automorphism["corrected_l1"]),
            "p0": _sparse(automorphism["projection0"]),
            "p0_sharp": _sparse(coefficient["p0sharp"]),
        },
        "pairings": {name: _sparse(matrix) for name, matrix in pairings.items()},
        "checks": checks,
        "formal_adjoint_completion": {
            "d_aut_sharp": "formal adjoint of d_aut with C0/C1 pairings",
            "K_p0_sharp": "formal adjoint of K_p0 with C0/H1 pairings",
            "Phi_sharp": "formal adjoint of Phi with H1/C1dual pairings",
            "M_D_sharp": "M_D by the parent Yang-Mills action",
            "B_action_sharp": "B_action by the Weyl-squared second variation",
            "factorized_variational_authority": True,
        },
        "flags": {
            "NARIAI_AUTOMORPHISM_CYCLIC_BACH_EXTENSION_V1": True,
            "FULL_ODD_CYCLIC_BACH_COMPLEX": True,
            "ACTION_DERIVED_MIDDLE": True,
            "METRIC_BACH_GRAPH_CHAIN_MAP": True,
            "METRIC_PAIRING_PULLBACK": True,
            "SUPPORT_LOCAL_DIFFERENTIAL_COMPLEX": True,
            "FULL_PARENT_METRIC_QUASI_ISOMORPHISM": False,
            "SUPPORT_LOCAL_AUTOMORPHISM_SDR": False,
            "NARIAI_GREEN_HOMOTOPY": False,
            "OPEN_BACKGROUND_CLASS": False,
            "NONLINEAR_EXTENSION": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": {
            "statement": (
                "The curvature-corrected Nariai automorphism constraint complex admits the canonical action-derived odd-cotangent Bach extension. Its 288-component eight-block differential is nilpotent and odd cyclic, and the exact four-row metric Bach complex embeds isometrically as the corrected BGG graph. The middle operator is the Hessian of 1/2<h,B_action h>+<lambda,M^D a-Phi h>; every cotangent and identity arrow is forced by the displayed pairings."
            ),
            "not_claimed": [
                "a deformation retract or quasi-isomorphism",
                "retarded or advanced Green homotopies",
                "an open family of non-conformally-flat backgrounds",
                "nonlinear closure",
                "a quantum theorem",
            ],
        },
        "next_gate": "C_G2_NARIAI_AUTOMORPHISM_SUPPORT_LOCAL_SDR",
        "source_manifest": sources,
    }


def render_report(certificate: dict[str, object]) -> str:
    checks = certificate["checks"]
    return f"""# Nariai automorphism cyclic Bach extension

The curvature-corrected automorphism constraint complex has the canonical
odd-cotangent Bach extension.  In eight blocks its total rank is
`{certificate['carrier']['total_rank']}` and its middle is the Hessian of

```text
1/2 <h,B_action h> + <lambda,M^D a-Phi h>.
```

Exact checks:

- abstract `Q^2` modulo the certified coefficient identities: `{checks['abstract_Q_squared_mod_certified_relations']}`;
- abstract odd cyclicity: `{checks['abstract_odd_cyclicity']}`;
- coefficient defect `M^D d_aut-Phi K p0`: `{checks['M_daut_minus_Phi_Kp0_entries']}`;
- coefficient defect `B_action K p0`: `{checks['B_Kp0_entries']}`;
- strict metric graph chain map: `{checks['metric_graph_chain_map_mod_certified_relations']}`;
- metric odd-pairing pullback: `{checks['metric_pairing_pullback_mod_retract_relations']}`.

The result is local and differential.  Cotangent rows are the forced formal
adjoints of the primal rows under the serialized pairings; they were not fit
independently.  No SDR, quasi-isomorphism, or Green homotopy is claimed.

Next gate: `{certificate['next_gate']}`.
"""


def _validate(certificate: dict[str, object]) -> None:
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    certificate = build()
    _validate(certificate)
    report = render_report(certificate)
    if args.guards:
        if any(
            certificate["flags"][name]
            for name in (
                "FULL_PARENT_METRIC_QUASI_ISOMORPHISM",
                "SUPPORT_LOCAL_AUTOMORPHISM_SDR",
                "NARIAI_GREEN_HOMOTOPY",
                "OPEN_BACKGROUND_CLASS",
                "NONLINEAR_EXTENSION",
                "QUANTUM_CLAIM",
            )
        ):
            raise AssertionError("cyclic Bach extension overpromoted")
    if args.write:
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report)
    if args.check:
        if json.loads(OUTPUT.read_text()) != certificate:
            raise SystemExit("generated cyclic Bach certificate drifted")
        if REPORT.read_text() != report:
            raise SystemExit("generated cyclic Bach report drifted")
    print("NARIAI_AUTOMORPHISM_CYCLIC_BACH_EXTENSION_V1: PASS")


if __name__ == "__main__":
    main()
