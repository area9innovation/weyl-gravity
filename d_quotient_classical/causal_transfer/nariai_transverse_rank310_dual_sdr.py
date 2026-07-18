"""Dual-number replay of the transverse Nariai rank-310 cyclic SDR.

The unit-Nariai mapping-cone repair is an exact ten-block polynomial SDR.
This module differentiates those matrices as operator polynomials and reduces
the result with the differentiated defining relations.  The dotted relations
are bound separately to the coefficient-jet calculations in
``coefficient_fixture``; no new free SDR ansatz is introduced here.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import sympy as sp

from d_quotient_classical.causal_transfer.coefficient_jet_pbw import (
    JetLinearizedOperator,
    jet_add,
    jet_scale,
    parallel_zero_variation,
    point_value_only,
)
import d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair as repair
from d_quotient_classical.causal_transfer.nariai_transverse_corrected_bgg_splitting_coefficient_jets import (
    _deserialize_table,
    _table,
    operator_data as splitting_operator_data,
)


ROOT = Path(__file__).resolve().parents[2]
ACTION = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1.json"

O = repair.O
Matrix = repair.Matrix
Table = repair.Table

DOT = {
    "g": "g_dot",
    "gsharp": "gsharp_dot",
    "J": None,
    "Jsharp": None,
    "d": "d_dot",
    "dsharp": "dsharp_dot",
    "k": None,
    "ksharp": None,
    "M": "M_dot",
    "B": "B_dot",
    "L": "L_dot",
    "Lsharp": "Lsharp_dot",
    "Phi": "Phi_dot",
    "Phisharp": "Phisharp_dot",
    "L0": "L0_dot",
    "L0sharp": "L0sharp_dot",
    "p0": None,
    "p0sharp": None,
    "K": None,
    "Ksharp": None,
}

ADJOINT = {
    "g": "gsharp", "gsharp": "g",
    "J": "Jsharp", "Jsharp": "J",
    "d": "dsharp", "dsharp": "d",
    "k": "ksharp", "ksharp": "k",
    "M": "M", "B": "B",
    "L": "Lsharp", "Lsharp": "L",
    "Phi": "Phisharp", "Phisharp": "Phi",
    "L0": "L0sharp", "L0sharp": "L0",
    "p0": "p0sharp", "p0sharp": "p0",
    "K": "Ksharp", "Ksharp": "K",
    "g_dot": "gsharp_dot", "gsharp_dot": "g_dot",
    "d_dot": "dsharp_dot", "dsharp_dot": "d_dot",
    "M_dot": "M_dot", "B_dot": "B_dot",
    "L_dot": "Lsharp_dot", "Lsharp_dot": "L_dot",
    "Phi_dot": "Phisharp_dot", "Phisharp_dot": "Phi_dot",
    "L0_dot": "L0sharp_dot", "L0sharp_dot": "L0_dot",
}


def operator_derivative(value: O) -> O:
    output = O.zero()
    for word, coefficient in value.terms:
        for index, name in enumerate(word):
            dotted = DOT.get(name)
            if dotted is not None:
                output += O._from_dict(
                    {word[:index] + (dotted,) + word[index + 1 :]: coefficient}
                )
    return output


def matrix_derivative(value: Matrix) -> Matrix:
    return [[operator_derivative(entry) for entry in row] for row in value]


def operator_adjoint(value: O) -> O:
    return O._from_dict(
        {
            tuple(ADJOINT[name] for name in reversed(word)): coefficient
            for word, coefficient in value.terms
        }
    )


def matrix_adjoint(value: Matrix) -> Matrix:
    return [
        [operator_adjoint(value[column][row]) for column in range(len(value))]
        for row in range(len(value[0]))
    ]


def _negative(value: O) -> O:
    return value.scale(-1)


def _dotted_replace_once(value: O) -> tuple[O, bool]:
    zero = {
        ("B_dot", "k"),
        ("ksharp", "B_dot"),
        ("B_dot", "K", "p0"),
        ("p0sharp", "Ksharp", "B_dot"),
        ("g_dot", "J"),
        ("Jsharp", "gsharp_dot"),
        ("p0", "L0_dot"),
        ("L0sharp_dot", "p0sharp"),
    }
    simple = {
        ("g_dot", "L0"): _negative(O.atom("g") * O.atom("L0_dot")),
        ("L0sharp", "gsharp_dot"): _negative(
            O.atom("L0sharp_dot") * O.atom("gsharp")
        ),
        ("d_dot", "L0"): O.atom("L_dot") * O.atom("K")
        + _negative(O.atom("d") * O.atom("L0_dot")),
        ("L0sharp", "dsharp_dot"): O.atom("Ksharp") * O.atom("Lsharp_dot")
        + _negative(O.atom("L0sharp_dot") * O.atom("dsharp")),
        ("M_dot", "L"): O.atom("Phi_dot")
        + _negative(O.atom("M") * O.atom("L_dot")),
        ("Lsharp", "M_dot"): O.atom("Phisharp_dot")
        + _negative(O.atom("Lsharp_dot") * O.atom("M")),
        ("J", "g_dot"): _negative(O.atom("L0_dot") * O.atom("p0")),
        ("gsharp_dot", "Jsharp"): _negative(
            O.atom("p0sharp") * O.atom("L0sharp_dot")
        ),
    }
    for word, coefficient in value.terms:
        for old in zero:
            for index in range(len(word) - len(old) + 1):
                if word[index : index + len(old)] == old:
                    return value + O._from_dict({word: -coefficient}), True
        for old, replacement in simple.items():
            for index in range(len(word) - len(old) + 1):
                if word[index : index + len(old)] != old:
                    continue
                rest = value + O._from_dict({word: -coefficient})
                prefix = O._from_dict({word[:index]: coefficient})
                suffix = O._from_dict({word[index + len(old) :]: 1})
                return rest + prefix * replacement * suffix, True
    return value, False


def reduce_dotted(value: O) -> O:
    for _ in range(300):
        changed_value, changed = repair._replace_once(value)
        if changed:
            value = changed_value
            continue
        changed_value, changed = _dotted_replace_once(value)
        if changed:
            value = changed_value
            continue
        return value
    raise AssertionError(f"dotted relation reduction did not terminate: {value.display()}")


def matrix_defects(value: Matrix) -> list[dict[str, Any]]:
    defects = []
    for row, entries in enumerate(value):
        for column, entry in enumerate(entries):
            reduced = reduce_dotted(entry)
            if reduced != O.zero():
                defects.append(
                    {"row": row, "column": column, "value": reduced.display()}
                )
    return defects


def _variation_of_product(left: Matrix, right: Matrix) -> Matrix:
    return repair._add(
        repair._multiply(matrix_derivative(left), right),
        repair._multiply(left, matrix_derivative(right)),
    )


@lru_cache(maxsize=1)
def abstract_fixture() -> dict[str, Any]:
    value = repair.abstract_kernel()
    q = value["q"]
    inclusion = value["inclusion"]
    projection = value["projection"]
    homotopy = value["homotopy"]
    metric_q = value["metric_q"]
    pairing = value["pairing"]
    metric_pairing = value["metric_pairing"]
    transform = value["transform"]
    transform_inverse = value["transform_inverse"]
    original_q = value["original_q"]
    original_inclusion = value["original_inclusion"]
    original_projection = value["original_projection"]
    original_homotopy = value["original_homotopy"]

    q_dot = matrix_derivative(q)
    inclusion_dot = matrix_derivative(inclusion)
    projection_dot = matrix_derivative(projection)
    homotopy_dot = matrix_derivative(homotopy)
    metric_q_dot = matrix_derivative(metric_q)
    transform_dot = matrix_derivative(transform)
    transform_inverse_dot = matrix_derivative(transform_inverse)
    original_q_dot = matrix_derivative(original_q)
    original_inclusion_dot = matrix_derivative(original_inclusion)
    original_projection_dot = matrix_derivative(original_projection)
    original_homotopy_dot = matrix_derivative(original_homotopy)
    degree_sign = repair._degree_sign(repair.BLOCK_DEGREES)

    add = repair._add
    multiply = repair._multiply
    scale = repair._scale
    checks = {
        "split_Q_squared_first_variation": add(
            multiply(q_dot, q), multiply(q, q_dot)
        ),
        "split_odd_cyclicity_first_variation": add(
            multiply(matrix_adjoint(q_dot), pairing),
            multiply(multiply(degree_sign, pairing), q_dot),
        ),
        "projection_inclusion_first_variation": add(
            multiply(projection_dot, inclusion),
            multiply(projection, inclusion_dot),
        ),
        "inclusion_chain_map_first_variation": add(
            add(multiply(q_dot, inclusion), multiply(q, inclusion_dot)),
            scale(
                add(
                    multiply(inclusion_dot, metric_q),
                    multiply(inclusion, metric_q_dot),
                ),
                -1,
            ),
        ),
        "projection_chain_map_first_variation": add(
            add(multiply(projection_dot, q), multiply(projection, q_dot)),
            scale(
                add(
                    multiply(metric_q_dot, projection),
                    multiply(metric_q, projection_dot),
                ),
                -1,
            ),
        ),
        "retract_first_variation": add(
            add(
                multiply(inclusion_dot, projection),
                multiply(inclusion, projection_dot),
            ),
            add(
                add(multiply(q_dot, homotopy), multiply(q, homotopy_dot)),
                add(multiply(homotopy_dot, q), multiply(homotopy, q_dot)),
            ),
        ),
        "homotopy_odd_cyclicity_first_variation": add(
            multiply(matrix_adjoint(homotopy_dot), pairing),
            scale(
                multiply(multiply(degree_sign, pairing), homotopy_dot), -1
            ),
        ),
        "metric_pairing_pullback_first_variation": add(
            multiply(
                multiply(matrix_adjoint(inclusion_dot), pairing), inclusion
            ),
            multiply(
                multiply(matrix_adjoint(inclusion), pairing), inclusion_dot
            ),
        ),
        "inclusion_projection_adjoint_first_variation": add(
            scale(
                multiply(
                    multiply(metric_pairing, matrix_adjoint(inclusion_dot)),
                    pairing,
                ),
                -1,
            ),
            scale(projection_dot, -1),
        ),
        "canonical_transform_first_variation": add(
            multiply(
                multiply(matrix_adjoint(transform_dot), pairing), transform
            ),
            multiply(
                multiply(matrix_adjoint(transform), pairing), transform_dot
            ),
        ),
        "transform_left_inverse_first_variation": add(
            multiply(transform_inverse_dot, transform),
            multiply(transform_inverse, transform_dot),
        ),
        "transform_right_inverse_first_variation": add(
            multiply(transform_dot, transform_inverse),
            multiply(transform, transform_inverse_dot),
        ),
        "original_Q_squared_first_variation": add(
            multiply(original_q_dot, original_q),
            multiply(original_q, original_q_dot),
        ),
        "original_odd_cyclicity_first_variation": add(
            multiply(matrix_adjoint(original_q_dot), pairing),
            multiply(multiply(degree_sign, pairing), original_q_dot),
        ),
        "original_retract_first_variation": add(
            add(
                multiply(original_inclusion_dot, original_projection),
                multiply(original_inclusion, original_projection_dot),
            ),
            add(
                add(
                    multiply(original_q_dot, original_homotopy),
                    multiply(original_q, original_homotopy_dot),
                ),
                add(
                    multiply(original_homotopy_dot, original_q),
                    multiply(original_homotopy, original_q_dot),
                ),
            ),
        ),
        "split_H_squared_first_variation": _variation_of_product(
            homotopy, homotopy
        ),
        "split_HI_first_variation": _variation_of_product(
            homotopy, inclusion
        ),
        "split_PH_first_variation": _variation_of_product(
            projection, homotopy
        ),
        "original_H_squared_first_variation": _variation_of_product(
            original_homotopy, original_homotopy
        ),
        "original_HI_first_variation": _variation_of_product(
            original_homotopy, original_inclusion
        ),
        "original_PH_first_variation": _variation_of_product(
            original_projection, original_homotopy
        ),
    }
    defects = {name: matrix_defects(matrix) for name, matrix in checks.items()}
    if any(defects.values()):
        failed = {name: defect for name, defect in defects.items() if defect}
        raise AssertionError(f"rank-310 first-variation SDR failed: {failed}")
    dotted = {
        "q_dot": q_dot,
        "metric_q_dot": metric_q_dot,
        "inclusion_dot": inclusion_dot,
        "projection_dot": projection_dot,
        "homotopy_dot": homotopy_dot,
        "transform_dot": transform_dot,
        "transform_inverse_dot": transform_inverse_dot,
        "original_q_dot": original_q_dot,
        "original_inclusion_dot": original_inclusion_dot,
        "original_projection_dot": original_projection_dot,
        "original_homotopy_dot": original_homotopy_dot,
    }
    return {"base": value, "dotted": dotted, "defects": defects}


def _table_count(value: Table) -> int:
    return sum(entry != 0 for matrix in value.values() for entry in matrix)


@lru_cache(maxsize=1)
def coefficient_fixture() -> dict[str, Any]:
    split = splitting_operator_data()
    base = repair.coefficient_kernel()
    l0 = split["L0"]
    l1 = split["L1_corrected"]
    d_aut = split["d_aut"]
    p0 = base["p0"]
    j0 = base["j0"]
    r0 = base["r0"]

    def g_provider(word: tuple[int, ...]) -> Table:
        return repair._table_scale(
            repair._table_left(
                r0, repair._table_right(l0.delta(word), p0)
            ),
            -sp.Integer(1),
        )

    g = JetLinearizedOperator(base["g"], g_provider, "g-complement")
    j0_g = JetLinearizedOperator(
        repair._table_left(j0, g.base),
        lambda word: repair._table_left(j0, g.delta(word)),
        "J0-g",
    )
    k_p0 = parallel_zero_variation(base["k"], "K-p0")
    g_l0 = split["pbw"]["H0"].compose(g, l0, "g-L0")
    gauge_reconstruction = jet_add(
        split["pbw"]["C0"].compose(d_aut, j0_g, "d-J0-g"),
        split["pbw"]["C0"].compose(l1, k_p0, "L1-Kp0"),
        jet_scale(d_aut, -1),
        name="gauge-reconstruction",
    )

    action = json.loads(ACTION.read_text())
    b_dot = _deserialize_table(action["exact_data"]["identified_full_action_variation"])
    bach = point_value_only(base["b"], b_dot, "B-action")
    bach_gauge = split["pbw"]["H0"].compose(bach, split["K"], "B-K")

    coefficient_defects = {
        "p0_L0_dot": repair._table_left(p0, l0.delta(())),
        "g_dot_J0": repair._table_right(g.delta(()), j0),
        "J0_g_dot_plus_L0_dot_p0": repair._table_add(
            repair._table_left(j0, g.delta(())),
            repair._table_right(l0.delta(()), p0),
        ),
        "g_L0_base": g_l0.base,
        "g_L0_first_variation": g_l0.delta(()),
        "gauge_reconstruction_base": gauge_reconstruction.base,
        "gauge_reconstruction_first_variation": gauge_reconstruction.delta(()),
        "B_K_base": bach_gauge.base,
        "B_K_first_variation": bach_gauge.delta(()),
    }
    if any(coefficient_defects.values()):
        failed = {
            name: _table_count(table)
            for name, table in coefficient_defects.items()
            if table
        }
        raise AssertionError(f"coefficient binding failed: {failed}")
    return {
        "d_aut_dot": _table(d_aut.delta(())),
        "g_dot": _table(g.delta(())),
        "coefficient_defect_counts": {
            name: _table_count(table) for name, table in coefficient_defects.items()
        },
        "requested_coefficient_jets": {
            "L0": [
                list(word)
                for word in sorted(l0.requested_words, key=lambda word: (len(word), word))
            ],
            "g": [
                list(word)
                for word in sorted(g.requested_words, key=lambda word: (len(word), word))
            ],
            "B_action": [
                list(word)
                for word in sorted(bach.requested_words, key=lambda word: (len(word), word))
            ],
        },
    }
