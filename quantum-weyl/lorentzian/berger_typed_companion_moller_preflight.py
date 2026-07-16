"""Exact typed Møller algebra before distributional Hadamard transport.

The classical Volterra theorem supplies distinct solution- and source-side
resolvents.  This module composes them with the finite triangular reduction
from two diagonal tensor waves to the twenty-row companion and verifies the
intertwining and adjoint identities.  It deliberately does not assert that
the resulting formal action on a Hadamard kernel is distributionally defined.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = HERE / "certificates/BERGER_BASE_WAVE_HADAMARD_PARAMETRIX.json"
VOLTERRA_IMPORT = HERE / "certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_V2_IMPORT.json"
COMPANION = HERE / "certificates/BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT.json"

Word = tuple[str, ...]
Poly = dict[Word, Fraction]
Matrix = list[list[Poly]]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _reduce_word(word: Word) -> Word:
    stack: list[str] = []
    inverse_pairs = {("b", "g"), ("g", "b")}
    for token in word:
        if stack and (stack[-1], token) in inverse_pairs:
            stack.pop()
        else:
            stack.append(token)
    return tuple(stack)


def _poly(terms: dict[Word, int | Fraction] | None = None) -> Poly:
    result: Poly = {}
    for word, coefficient in (terms or {}).items():
        reduced = _reduce_word(word)
        value = result.get(reduced, Fraction(0)) + Fraction(coefficient)
        if value:
            result[reduced] = value
        elif reduced in result:
            del result[reduced]
    return result


def _add(left: Poly, right: Poly, scale: int = 1) -> Poly:
    terms: dict[Word, Fraction] = dict(left)
    for word, coefficient in right.items():
        terms[word] = terms.get(word, Fraction(0)) + scale * coefficient
    return _poly(terms)


def _mul(left: Poly, right: Poly) -> Poly:
    terms: dict[Word, Fraction] = {}
    for lword, lcoefficient in left.items():
        for rword, rcoefficient in right.items():
            word = _reduce_word(lword + rword)
            terms[word] = terms.get(word, Fraction(0)) + lcoefficient * rcoefficient
    return _poly(terms)


def _zero() -> Poly:
    return {}


def _one() -> Poly:
    return {(): Fraction(1)}


def _token(name: str) -> Poly:
    return {(name,): Fraction(1)}


def _matrix_add(left: Matrix, right: Matrix, scale: int = 1) -> Matrix:
    return [
        [_add(left[row][column], right[row][column], scale) for column in range(2)]
        for row in range(2)
    ]


def _matrix_mul(left: Matrix, right: Matrix) -> Matrix:
    result = [[_zero(), _zero()], [_zero(), _zero()]]
    for row in range(2):
        for column in range(2):
            value = _zero()
            for middle in range(2):
                value = _add(value, _mul(left[row][middle], right[middle][column]))
            result[row][column] = value
    return result


def _identity() -> Matrix:
    return [[_one(), _zero()], [_zero(), _one()]]


def _sharp(matrix: Matrix, token_map: dict[str, str]) -> Matrix:
    result = [[_zero(), _zero()], [_zero(), _zero()]]
    for row in range(2):
        for column in range(2):
            terms: dict[Word, Fraction] = {}
            for word, coefficient in matrix[column][row].items():
                sharp_word = tuple(token_map[token] for token in reversed(word))
                terms[sharp_word] = terms.get(sharp_word, Fraction(0)) + coefficient
            result[row][column] = _poly(terms)
    return result


def _rewrite_chain(chain: tuple[str, ...]) -> tuple[str, ...]:
    rules = {
        ("C", "Rsol"): ("C0",),
        ("C0", "Tsol"): ("B",),
        ("Rsrc", "C"): ("C0",),
        ("Tsrc", "C0"): ("B",),
    }
    current = chain
    changed = True
    while changed:
        changed = False
        for index in range(len(current) - 1):
            pair = current[index : index + 2]
            if pair in rules:
                current = current[:index] + rules[pair] + current[index + 2 :]
                changed = True
                break
    return current


def triangular_replay() -> dict[str, Any]:
    """Replay the finite noncommutative triangular and adjoint identities."""

    b, g, v = _token("b"), _token("g"), _token("v")
    identity = _identity()
    diagonal = [[b, _zero()], [_zero(), b]]
    green = [[g, _zero()], [_zero(), g]]
    lower = [[_zero(), _zero()], [v, _zero()]]
    c0 = _matrix_add(diagonal, lower)
    gv = _matrix_mul(green, lower)
    vg = _matrix_mul(lower, green)
    tsol = _matrix_add(identity, gv, -1)
    tsrc = _matrix_add(identity, vg, -1)

    green_ret = [[_token("gret"), _zero()], [_zero(), _token("gret")]]
    lower_plain = [[_zero(), _zero()], [_token("vplain"), _zero()]]
    tsol_ret = _matrix_add(identity, _matrix_mul(green_ret, lower_plain), -1)
    sharp_actual = _sharp(tsol_ret, {"gret": "gsharp_adv", "vplain": "vsharp"})
    green_sharp_adv = [
        [_token("gsharp_adv"), _zero()],
        [_zero(), _token("gsharp_adv")],
    ]
    lower_sharp = [[_zero(), _token("vsharp")], [_zero(), _zero()]]
    sharp_expected = _matrix_add(
        identity, _matrix_mul(lower_sharp, green_sharp_adv), -1
    )

    checks = {
        "V_G_V_zero_by_block_incidence": _matrix_mul(
            _matrix_mul(lower, green), lower
        )
        == [[_zero(), _zero()], [_zero(), _zero()]],
        "Tsol_inverse_finite": _matrix_mul(_matrix_add(identity, gv), tsol)
        == identity,
        "Tsrc_inverse_finite": _matrix_mul(tsrc, _matrix_add(identity, vg))
        == identity,
        "C0_Tsol_equals_B": _matrix_mul(c0, tsol) == diagonal,
        "Tsrc_C0_equals_B": _matrix_mul(tsrc, c0) == diagonal,
        "Tsol_ret_sharp_equals_Tsrc_sharp_adv": sharp_actual == sharp_expected,
        "C_Msol_equals_B": _rewrite_chain(("C", "Rsol", "Tsol")) == ("B",),
        "Msrc_C_equals_B": _rewrite_chain(("Tsrc", "Rsrc", "C")) == ("B",),
    }
    if not all(checks.values()):
        raise ValueError("typed Møller algebra replay failed")
    return {
        "checks": checks,
        "triangular_solution_map": "T_sol^pm=I-G_diag^pm V",
        "triangular_source_map": "T_src^pm=I-V G_diag^pm",
        "full_solution_map": "M_sol^pm=R_sol^pm T_sol^pm:X_B,s(I)->X_C,s(I)",
        "full_source_map": "M_src^pm=T_src^pm R_src^pm:Y_C,s(I)->Y_B,s(I)",
        "intertwiners": ["C M_sol^pm=B", "M_src^pm C=B"],
        "adjoint_reversal": "(M_sol,C,retarded)^sharp=M_src,Csharp,advanced",
    }


def _load_inputs() -> tuple[dict[str, Any], ...]:
    base, imported, companion = (
        json.loads(path.read_text()) for path in (BASE, VOLTERRA_IMPORT, COMPANION)
    )
    if (
        base.get("next_gate") != "BERGER_TYPED_COMPANION_MOLLER_TRANSPORT"
        or base.get("claim_flags", {}).get("BERGER_BASE_WAVE_HADAMARD_PARAMETRIX")
        is not True
        or base.get("claim_flags", {}).get("BERGER_TYPED_COMPANION_HADAMARD")
        is not False
    ):
        raise ValueError("base Hadamard boundary drifted")
    if (
        imported.get("result_id") != "BERGER_RETAINED_BIWAVE_VOLTERRA_V2_IMPORT"
        or imported.get("claim_flags", {}).get(
            "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT_IMPORTED"
        )
        is not True
        or imported.get("claim_flags", {}).get(
            "BERGER_RETAINED_BIWAVE_FORMAL_ADJOINT_BUNDLE_READY"
        )
        is not True
        or imported.get("source_import", {}).get("proof_checks", {}).get(
            "distinct_source_solution_resolvents"
        )
        is not True
        or imported.get("source_import", {}).get("proof_checks", {}).get(
            "typed_metric_antifield_adjoint_reversal"
        )
        is not True
    ):
        raise ValueError("typed Volterra input drifted")
    if (
        companion.get("companion_system", {}).get("operator")
        != "C20=[[Box_2,-I10],[V_2,Box_2]]"
        or companion.get("causal_policy", {}).get("off_diagonal_local_orders")
        != {"lower_left": 2, "upper_right": 0}
    ):
        raise ValueError("companion operator drifted")
    return base, imported, companion


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    base, imported, companion = _load_inputs()
    replay = triangular_replay()
    result = {
        "schema": "quantum-weyl-berger-typed-companion-moller-preflight-v1",
        "result_id": "BERGER_TYPED_COMPANION_MOLLER_PREFLIGHT",
        "result_state": "TYPED_MOLLER_ALGEBRA_CERTIFIED_MICROLOCAL_KERNEL_ACTION_OPEN",
        "lifecycle_layer": "LORENTZIAN_MICROLOCAL_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "classical_commit": base["classical_commit"],
        "setting_id": base["setting_id"],
        "dependency_refs": {
            "base_hadamard_parametrix": _dependency(BASE),
            "typed_volterra_v2": _dependency(VOLTERRA_IMPORT),
            "companion_graph": _dependency(COMPANION),
        },
        "operator_filtration": {
            "B": "diag(Box_2,Box_2)",
            "V": "[[0,0],[V_2,0]], differential order two",
            "C0": "B+V=[[Box_2,0],[V_2,Box_2]]",
            "N": "[[0,-I10],[0,0]], differential order zero",
            "C": "C0+N=[[Box_2,-I10],[V_2,Box_2]]",
        },
        "typed_transport": replay,
        "formal_kernel_candidate": {
            "formula": "H_C,loc^+=M_sol,C,retarded H_B^+ M_src,Csharp,advanced",
            "left_defect_reduction": "C_x H_C,loc^+=B_x H_B^+ M_src,Csharp,advanced",
            "right_defect_reduction": "Csharp_xprime H_C,loc^+=M_sol,C,retarded H_B^+ Bsharp_xprime",
            "status": "FORMAL_UNTIL_DISTRIBUTIONAL_COMPOSITION_IS_CERTIFIED",
        },
        "microlocal_obligations": {
            "Hörmander_kernel_compositions_defined": "OPEN",
            "Volterra_series_extend_to_the_required_distribution_spaces": "OPEN",
            "C_plus_wavefront_relation_preserved": "OPEN",
            "smooth_left_and_right_defects_remain_smooth": "OPEN",
            "ghost_biwave_factor_transport_included": "OPEN",
            "A10_graph_pullback_wavefront_safe": "OPEN",
        },
        "microlocal_diagnosis": {
            "maximum_order_V2": 2,
            "all_Sobolev_Volterra_convergence_is_wavefront_control": False,
            "smooth_potential_Moller_theorem_applies_directly": False,
            "normalized_obstruction": "DISTRIBUTIONAL_COMPOSITION_AND_UNIFORM_WAVEFRONT_CONTROL_NOT_CERTIFIED_FOR_THE_ORDER_TWO_TRIANGULAR_TRANSPORT",
            "accepted_routes": [
                "prove the six listed Hörmander composition obligations",
                "prove null-cone decomposability and a regular GreenHyp transport directly",
            ],
        },
        "claim_flags": {
            "BERGER_TYPED_COMPANION_MOLLER_ALGEBRA": True,
            "BERGER_TYPED_COMPANION_DISTRIBUTIONAL_TRANSPORT": False,
            "BERGER_TYPED_COMPANION_HADAMARD_PARAMETRIX": False,
            "BERGER_TYPED_COMPANION_GLOBAL_HADAMARD": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_TYPED_COMPANION_MICROLOCAL_COMPOSITION",
        "provenance": {
            "base_result_id": base["result_id"],
            "volterra_result_id": imported["result_id"],
            "companion_result_id": companion["result_id"],
        },
        "claim_boundary": (
            "Proves the finite triangular source/solution maps, their exact "
            "intertwiners, the combined Volterra Møller intertwiners and the "
            "advanced/retarded formal-adjoint reversal. The displayed action on "
            "the local Hadamard kernel remains formal until the six distributional "
            "and microlocal composition obligations pass. No companion, 26-row or "
            "54-row Hadamard parametrix, global state, QME or quantum claim is made."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "BERGER_TYPED_COMPANION_MOLLER_PREFLIGHT"
        or result.get("result_state")
        != "TYPED_MOLLER_ALGEBRA_CERTIFIED_MICROLOCAL_KERNEL_ACTION_OPEN"
        or result.get("dependency_tags")
        != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != "BERGER_TYPED_COMPANION_MICROLOCAL_COMPOSITION"
    ):
        raise ValueError("typed Møller preflight identity drifted")
    if not all(result.get("typed_transport", {}).get("checks", {}).values()):
        raise ValueError("typed Møller identity dropped")
    if set(result.get("microlocal_obligations", {}).values()) != {"OPEN"}:
        raise ValueError("microlocal transport was over-promoted")
    diagnosis = result.get("microlocal_diagnosis", {})
    if (
        diagnosis.get("maximum_order_V2") != 2
        or diagnosis.get("all_Sobolev_Volterra_convergence_is_wavefront_control")
        is not False
        or diagnosis.get("smooth_potential_Moller_theorem_applies_directly")
        is not False
    ):
        raise ValueError("order-two microlocal diagnosis drifted")
    true_flags = {
        name for name, value in result.get("claim_flags", {}).items() if value is True
    }
    if true_flags != {"BERGER_TYPED_COMPANION_MOLLER_ALGEBRA"}:
        raise ValueError("Hadamard lifecycle was over-promoted")
