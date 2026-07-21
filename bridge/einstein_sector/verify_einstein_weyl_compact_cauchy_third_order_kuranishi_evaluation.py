"""Method-distinct replay of the balanced third-order Kuranishi certificate.

The verifier consumes only the committed rational q2/q3 slice.  It does not
import the producer or deserialize the producer's checkpoint objects.
"""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from itertools import product
from math import factorial
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_EVALUATION_V1.json"
SLICE = ROOT / "bridge/einstein_sector/generated/einstein_weyl_compact_cauchy_balanced_q2_q3_resonant_slice_v1.json"
CROSSWALK = ROOT / "bridge/certificates/EINSTEIN_WEYL_ALPHA_B3_OSTROGRADSKY_CANONICAL_CROSSWALK_V1.json"

THETA = sp.symbols("theta", real=True)
R3 = sp.sqrt(3)
WM = sp.sqrt(6 - 2 * R3)
WX = 4 / R3
AX = sp.sqrt(sp.Rational(27, 52) * (5 * R3 - 6))
AXIAL = {12, 17}
POLAR = {6, 7, 10, 19}
OUTPUT = (23, 26, 30, 31)
ORDERS = {23: (1, 3, 5), 26: (1, 3, 5), 30: (0, 2, 4), 31: (0, 2, 4)}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canon(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.sqrtdenest(sp.radsimp(sp.cancel(value))))


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt})


@lru_cache(maxsize=None)
def derivative(ell: int, carrier: str, order: int) -> sp.Expr:
    y = sp.legendre(ell, sp.cos(THETA))
    function = {
        "scalar": y,
        "covector": -sp.sin(THETA) * sp.diff(y, THETA),
        "dual": -sp.diff(y, THETA) / sp.sin(THETA),
    }[carrier]
    return sp.simplify(sp.diff(function, THETA, order).subs(THETA, sp.pi / 2))


def parts(total: int, width: int):
    if width == 1:
        yield (total,)
    else:
        for first in range(total + 1):
            for tail in parts(total - first, width - 1):
                yield (first, *tail)


def choose(partition: tuple[int, ...]) -> int:
    result = factorial(sum(partition))
    for item in partition:
        result //= factorial(item)
    return result


class Mode:
    def __init__(self, label, lattice, frequency, fields):
        self.label = label
        self.lattice = lattice
        self.frequency = frequency
        self.fields = fields


def first_modes():
    result = []
    for sign in (1, -1):
        result.append(Mode(f"E{sign}", (sign, 0), sign * WM, {12: (-1, 2, "covector"), 17: (R3, 2, "scalar")}))
        result.append(Mode(f"X{sign}", (0, sign), sign * WX, {12: (-AX / 3, 2, "covector"), 17: (3 * AX, 2, "scalar")}))
    return tuple(result)


def second_modes():
    lattice = {
        "Einstein_self_sum": (2, 0),
        "extra_self_sum": (0, 2),
        "cross_sum": (1, 1),
        "cross_difference": (-1, 1),
        "combined_zero": (0, 0),
    }
    result = []
    for row in json.loads(CROSSWALK.read_text())["signed_channel_crosswalk"]:
        ell = int(row["ell"])
        values = [parse(value) for value in row["covariant_coefficients"]]
        fields = {}
        if ell == 0:
            assert values[1:] == [0, 0]
            if values[0] != 0:
                fields[10] = (values[0], 0, "scalar")
        else:
            for field_row, value, carrier in zip((6, 7, 10, 19), values, ("scalar", "scalar", "scalar", "covector"), strict=True):
                if value != 0:
                    fields[field_row] = (value, ell, carrier)
        base = lattice[row["channel"]]
        sign = 1 if row["frequency_sign"] == "+" else -1
        if fields:
            result.append(Mode(row["channel"], (sign * base[0], sign * base[1]), parse(row["omega"]), fields))
    return tuple(result)


def field_derivative(mode: Mode, row: int, word: tuple[int, ...]) -> sp.Expr:
    if row not in mode.fields or 1 in word or 3 in word:
        return sp.S.Zero
    amplitude, ell, carrier = mode.fields[row]
    return amplitude * (-sp.I * mode.frequency) ** word.count(0) * derivative(ell, carrier, word.count(2))


def term_value(term: dict, modes: tuple[Mode, ...], order: int, *, suppress_fifth: bool = False) -> sp.Expr:
    coefficient = [parse(value) for value in term["theta_coefficient_derivatives_0_through_5"]]
    value = sp.S.Zero
    for partition in parts(order, len(modes) + 1):
        coefficient_order = partition[0]
        if suppress_fifth and coefficient_order == 5:
            continue
        local = sp.Integer(choose(partition)) * coefficient[coefficient_order]
        if local == 0:
            continue
        for mode, item, extra in zip(modes, term["inputs"], partition[1:], strict=True):
            local *= field_derivative(mode, int(item["row"]), tuple(item["word"]) + (2,) * extra)
            if local == 0:
                break
        value += local
    return value


def project(jets: dict[int, dict[int, sp.Expr]]) -> sp.Matrix:
    coefficients = []
    for row in OUTPUT:
        orders = ORDERS[row]
        carrier = "dual" if row in (23, 26) else "scalar"
        matrix = sp.Matrix([[derivative(ell, carrier, order) for ell in (2, 4, 6)] for order in orders])
        coefficient = (matrix.inv()[0, :] * sp.Matrix([jets[row][order] for order in orders]))[0]
        coefficients.append(canon(coefficient))
    return sp.Matrix([3 * coefficients[0], 3 * coefficients[1], coefficients[2] / 2, coefficients[3] / 2]).applyfunc(canon)


def replay_target(target: tuple[int, int], *, suppress_fifth: bool = False):
    data = json.loads(SLICE.read_text())["terms"]
    first, second = first_modes(), second_modes()
    components = {}
    for name in ("q2", "q3"):
        raw = defaultdict(lambda: sp.S.Zero)
        for term in data[name]:
            row = int(term["output_row"])
            input_rows = [int(item["row"]) for item in term["inputs"]]
            if name == "q2":
                mode_sets = (first, second) if input_rows[0] in AXIAL else (second, first)
                assignments = product(*mode_sets)
            else:
                assignments = product(first, repeat=3)
            for modes in assignments:
                if tuple(sum(mode.lattice[i] for mode in modes) for i in range(2)) != target:
                    continue
                for order in ORDERS[row]:
                    value = term_value(term, modes, order, suppress_fifth=suppress_fifth)
                    raw[row, order] += value / (6 if name == "q3" else 1)
        jets = {row: {order: raw[row, order] for order in ORDERS[row]} for row in OUTPUT}
        components[name] = project(jets)
    return components["q2"], components["q3"], (components["q2"] + components["q3"]).applyfunc(canon)


def adjoints(target):
    if target[0]:
        return (sp.Matrix([0, -2 * target[0], 0, 2 * R3 * target[0]]),)
    return (sp.Matrix([-6, 0, 6, 0]), sp.Matrix([0, -sp.Rational(2, 3) * target[1], 0, 6 * target[1]]))


def main() -> None:
    value = json.loads(CERT.read_text())
    tensor = json.loads(SLICE.read_text())
    assert tensor["term_counts"] == {"q2": 832, "q3": 579}
    assert tensor["coefficient_derivative_order"] == 5
    assert value["provenance"]["restricted_tensor_slice"]["sha256"] == sha(SLICE)
    assert value["result_state"] == "GLOBAL_KURANISHI_CLASS_ZERO_BUT_FOUR_ORIGINAL_SHELLS_BOUNDED_OBSTRUCTED"
    stored = {tuple(row["target"]): row for row in value["resonant_shells"]}
    assert set(stored) == {(-1, 0), (1, 0), (0, -1), (0, 1)}
    for target in ((1, 0), (0, 1)):
        q2, q3, total = replay_target(target)
        row = stored[target]
        assert [canon(parse(item) - actual) for item, actual in zip(row["source_components"]["mixed_q2"], q2, strict=True)] == [0] * 4
        assert [canon(parse(item) - actual) for item, actual in zip(row["source_components"]["cubic_q3_over_6"], q3, strict=True)] == [0] * 4
        assert [canon(parse(item) - actual) for item, actual in zip(row["source_components"]["total"], total, strict=True)] == [0] * 4
        pairings = [canon((left.T * total)[0]) for left in adjoints(target)]
        assert [canon(parse(item) - actual) for item, actual in zip(row["pairings"], pairings, strict=True)] == [0] * len(pairings)
        assert any(item != 0 for item in pairings)
        negative = stored[(-target[0], -target[1])]
        assert [canon(parse(item) - sp.conjugate(actual)) for item, actual in zip(negative["source_components"]["total"], total, strict=True)] == [0] * 4
    # The fifth coefficient derivative is load-bearing: suppressing it must
    # change at least one certified source row.
    _, _, mutated = replay_target((1, 0), suppress_fifth=True)
    certified = sp.Matrix([parse(item) for item in stored[(1, 0)]["source_components"]["total"]])
    assert any(canon(left - right) != 0 for left, right in zip(mutated, certified, strict=True))
    global_projection = value["global_constraint_projection"]
    assert global_projection["K3_representative"] == ["0"] * 5
    assert global_projection["l2_rank"] == 3
    image = sp.Matrix(global_projection["l2_image_normalized_basis_columns"]).T
    assert image.rank() == 3
    assert global_projection["quotient_basis"] == ["P_x", "J_3"]
    assert value["correction_classes"] == {
        "bounded_or_finite_quasiperiodic": "OBSTRUCTED: every occupied original branch has a nonzero adjoint-shell functional",
        "causal_retarded": "NO_CERTIFIED_MAP",
        "smooth_exponential_polynomial": "CERTIFIED_SOLVABLE_WITH_SECULAR_TERMS: the square axial constant-coefficient pencil has nonzero determinant p^2 q; adjugate reduction and scalar polynomial-exponential surjectivity give a smooth secular preimage (degree at most one on q and at most two on p)",
    }
    print("EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_EVALUATION_V1 independent replay: PASS")


if __name__ == "__main__":
    main()
