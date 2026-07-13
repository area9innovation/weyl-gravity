#!/usr/bin/env python3
"""C2g-N: the first cutoff-complete global-conformal BRST window.

The existing C2e certificate constructs the universal minimal BRST algebra,
and C2f-A/M construct the exact one-particle ``SO(4,2)`` action through
compact energy four.  A generic finite cutoff is not a BRST complex: a
raising generator acting on the top energy block leaves the cutoff.

There is nevertheless one small window which is complete for a grading
reason.  In the cylinder ghost polarization used by Hamada, the ghost Fock
vacuum contains the four ghosts dual to the four raising generators.  In the
absolute exterior-ghost convention this is ghost number four and compact
degree minus four.  Therefore the coefficient-module problem at total
compact degree zero is

    C^3_0  --d3-->  C^4_0  --d4-->  C^5_0.

For the one-particle Weyl module, whose true lowest compact energy is two,
these cochains use only coefficient energies two, three, and four.  Any
energy-four term already contains all four raising ghosts, so a missing
energy-four-to-five action is killed by exterior saturation.  Thus the
source-energy-four jet is sufficient for this *global-only one-particle*
kernel/image problem even though it is not a finite conformal module.

This executable proves the window and nilpotency exactly.  Good-prime rank
certificates show that the one-particle middle cohomology vanishes and that
the lowest particle-number-two cohomology is exactly the two chiral
Weyl-square scalars.  It deliberately does not identify those global-only
results with physical pure-Weyl BRST cohomology.  Such an identification
would require the local Diff-times-Weyl complex, its zero modes and
contractible sectors, a proof that the global action descends to it, and the
second-quantized coefficient module relevant to the energy-six states.
Fail-closed switches protect those missing statements.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import combinations, combinations_with_replacement
from typing import TypeAlias

import sympy as sp
from sympy.polys.domains import GF
from sympy.polys.matrices import DomainMatrix

try:
    from symbolic import verify_conformal_generator_ansatz as generator_data
    from symbolic.verify_conformal_taub_multiplets import MAGNETIC_COMPONENTS
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    import verify_conformal_generator_ansatz as generator_data
    from verify_conformal_taub_multiplets import MAGNETIC_COMPONENTS


R = sp.Rational
I = sp.I
Monomial = tuple[int, ...]
SparseVector: TypeAlias = dict[int, sp.Expr]

MODULAR_PRIME = 241
MODULAR_ROOTS = {
    -1: 64,  # i
    2: 22,
    3: 56,
    5: 103,
}


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def exact_zero(value: sp.Expr) -> bool:
    return sp.simplify(value) == 0


def add_term(output: dict[object, sp.Expr], key: object, value: sp.Expr) -> None:
    if value == 0:
        return
    output[key] = output.get(key, sp.Integer(0)) + value


def clean(output: dict[object, sp.Expr]) -> dict[object, sp.Expr]:
    cleaned: dict[object, sp.Expr] = {}
    for key, value in output.items():
        value = sp.simplify(value)
        if value != 0:
            cleaned[key] = value
    return cleaned


def wedge(first: Monomial, second: Monomial) -> tuple[int, Monomial] | None:
    if set(first).intersection(second):
        return None
    inversions = sum(left > right for left in first for right in second)
    return (-1 if inversions % 2 else 1), tuple(sorted(first + second))


@dataclass(frozen=True)
class LieData:
    names: tuple[str, ...]
    degrees: tuple[int, ...]
    matrices: tuple[sp.Matrix, ...]
    structure: tuple[tuple[tuple[sp.Expr, ...], ...], ...]
    state_energies: tuple[int, ...]


@dataclass(frozen=True)
class SpanFitter:
    candidates: tuple[sp.Matrix, ...]
    source: tuple[int, ...]
    coordinates: tuple[tuple[int, int], ...]
    pivot_rows: tuple[int, ...]
    pivot_inverse: sp.Matrix
    design: sp.Matrix


def restricted_coordinates(matrix: sp.Matrix, source: tuple[int, ...]) -> dict[tuple[int, int], sp.Expr]:
    return {
        (row, column): value
        for column in source
        for row in range(matrix.rows)
        if (value := sp.simplify(matrix[row, column])) != 0
    }


def make_span_fitter(
    candidates: tuple[sp.Matrix, ...],
    source: tuple[int, ...],
) -> SpanFitter:
    candidate_data = tuple(restricted_coordinates(matrix, source) for matrix in candidates)
    coordinates = tuple(sorted(set().union(*(set(data) for data in candidate_data))))
    design = sp.Matrix(
        [[data.get(coordinate, 0) for data in candidate_data] for coordinate in coordinates]
    )
    pivot_rows = tuple(design.T.rref()[1])
    if len(pivot_rows) != len(candidates):
        raise AssertionError("candidate generator restrictions are not independent")
    square = design.extract(pivot_rows, range(len(candidates)))
    return SpanFitter(
        candidates,
        source,
        coordinates,
        pivot_rows,
        square.inv(),
        design,
    )


def fit_in_span(target: sp.Matrix, fitter: SpanFitter) -> tuple[sp.Expr, ...]:
    """Fit an exact bracket on the complete energy-two/three interior."""

    target_data = restricted_coordinates(target, fitter.source)
    if not set(target_data).issubset(fitter.coordinates):
        raise AssertionError("bracket has support outside the declared conformal-generator span")
    rhs = sp.Matrix(
        [target_data.get(fitter.coordinates[row], 0) for row in fitter.pivot_rows]
    )
    coefficients = tuple(sp.simplify(value) for value in fitter.pivot_inverse * rhs)
    reconstructed = fitter.design * sp.Matrix(coefficients)
    expected = sp.Matrix([target_data.get(coordinate, 0) for coordinate in fitter.coordinates])
    if any(not exact_zero(value) for value in reconstructed - expected):
        raise AssertionError("bracket does not lie in the declared conformal-generator span")
    return coefficients


def build_lie_data(chirality: int = 1) -> LieData:
    space = generator_data.representation_space(chirality)
    ansatz = generator_data.assemble_ansatz(
        space,
        generator_data.CANONICAL_LOWERING,
        generator_data.canonical_raising(),
    )
    names = (
        "D",
        "Lx", "Ly", "Lz",
        "Rx", "Ry", "Rz",
        *(f"K-_{left}_{right}" for left, right in MAGNETIC_COMPONENTS),
        *(f"K+_{left}_{right}" for left, right in MAGNETIC_COMPONENTS),
    )
    matrices = (
        space.energy,
        *(space.left[axis] for axis in ("x", "y", "z")),
        *(space.right[axis] for axis in ("x", "y", "z")),
        *(ansatz.lowering[component] for component in MAGNETIC_COMPONENTS),
        *(ansatz.raising[component] for component in MAGNETIC_COMPONENTS),
    )
    degrees = (0,) * 7 + (-1,) * 4 + (1,) * 4
    state_energies = tuple(int(space.energy[index, index]) for index in range(space.dimension))
    interior = tuple(index for index, energy in enumerate(state_energies) if energy <= 3)
    by_degree = {
        degree: tuple(index for index, value in enumerate(degrees) if value == degree)
        for degree in (-1, 0, 1)
    }
    fitters = {
        degree: make_span_fitter(
            tuple(matrices[index] for index in indices), interior
        )
        for degree, indices in by_degree.items()
    }

    raw = [
        [[sp.Integer(0) for _ in names] for _ in names]
        for _ in names
    ]
    degree_two_zero = True
    for first, first_matrix in enumerate(matrices):
        for second, second_matrix in enumerate(matrices):
            bracket = first_matrix * second_matrix - second_matrix * first_matrix
            degree = degrees[first] + degrees[second]
            candidate_indices = by_degree.get(degree, ())
            if not candidate_indices:
                degree_two_zero = degree_two_zero and not restricted_coordinates(
                    bracket, interior
                )
                continue
            coefficients = fit_in_span(bracket, fitters[degree])
            for target, coefficient in zip(candidate_indices, coefficients):
                raw[first][second][target] = coefficient

    structure = tuple(
        tuple(tuple(component for component in row) for row in matrix)
        for matrix in raw
    )
    check(
        "C2g-N: every same-sign degree-two proper-generator bracket vanishes",
        degree_two_zero,
    )
    check("C2g-N: fitted conformal basis has dimension fifteen", len(names) == 15)
    check(
        "C2g-N: fitted exact structure constants are antisymmetric",
        all(
            exact_zero(structure[a][b][c] + structure[b][a][c])
            for a in range(15) for b in range(15) for c in range(15)
        ),
    )
    check(
        "C2g-N: fitted structure constants obey every Jacobi identity",
        all(
            exact_zero(sum(
                structure[b][c][m] * structure[a][m][t]
                + structure[c][a][m] * structure[b][m][t]
                + structure[a][b][m] * structure[c][m][t]
                for m in range(15)
            ))
            for a in range(15) for b in range(15)
            for c in range(15) for t in range(15)
        ),
    )
    return LieData(names, degrees, matrices, structure, state_energies)


def ghost_width(ghost_number: int) -> int:
    """Maximal absolute compact degree in ``Lambda^q g*``.

    There are four ghosts of degree ``-1``, seven of degree zero, and four
    of degree ``+1``.
    """

    if not 0 <= ghost_number <= 15:
        return -1
    return min(ghost_number, 4, 15 - ghost_number)


def required_upper_energy(total_degree: int, ghost_number: int) -> int:
    return total_degree + max(
        ghost_width(number)
        for number in (ghost_number - 1, ghost_number, ghost_number + 1)
    )


def ghost_energy(monomial: Monomial, degrees: tuple[int, ...]) -> int:
    return -sum(degrees[index] for index in monomial)


def cochain_basis(
    data: LieData,
    ghost_number: int,
    total_degree: int = 0,
) -> tuple[tuple[Monomial, int], ...]:
    states_by_energy: dict[int, list[int]] = {}
    for state, energy in enumerate(data.state_energies):
        states_by_energy.setdefault(energy, []).append(state)
    output: list[tuple[Monomial, int]] = []
    for monomial in combinations(range(15), ghost_number):
        coefficient_energy = total_degree - ghost_energy(monomial, data.degrees)
        output.extend((monomial, state) for state in states_by_energy.get(coefficient_energy, ()))
    return tuple(output)


def ghost_differentials(data: LieData) -> tuple[dict[Monomial, sp.Expr], ...]:
    output: list[dict[Monomial, sp.Expr]] = []
    for target in range(15):
        polynomial: dict[Monomial, sp.Expr] = {}
        for first in range(15):
            for second in range(first + 1, 15):
                # -1/2 times both ordered terms is -f[first,second]^target.
                add_term(polynomial, (first, second), -data.structure[first][second][target])
        output.append(clean(polynomial))
    return tuple(output)


def ce_on_monomial(
    monomial: Monomial,
    dc: tuple[dict[Monomial, sp.Expr], ...],
) -> dict[Monomial, sp.Expr]:
    output: dict[Monomial, sp.Expr] = {}
    for position, ghost in enumerate(monomial):
        prefix = monomial[:position]
        suffix = monomial[position + 1 :]
        for pair, coefficient in dc[ghost].items():
            first = wedge(prefix, pair)
            if first is None:
                continue
            sign_first, partial = first
            second = wedge(partial, suffix)
            if second is None:
                continue
            sign_second, result = second
            add_term(
                output,
                result,
                (-1) ** position * sign_first * sign_second * coefficient,
            )
    return clean(output)


def matrices_to_sparse_actions(
    matrices: tuple[sp.Matrix, ...],
) -> tuple[tuple[tuple[tuple[int, sp.Expr], ...], ...], ...]:
    actions = []
    for matrix in matrices:
        columns = []
        for column in range(matrix.cols):
            columns.append(tuple(
                (row, sp.simplify(matrix[row, column]))
                for row in range(matrix.rows)
                if matrix[row, column] != 0
            ))
        actions.append(tuple(columns))
    return tuple(actions)


def sparse_actions(data: LieData) -> tuple[tuple[tuple[tuple[int, sp.Expr], ...], ...], ...]:
    return matrices_to_sparse_actions(data.matrices)


def differential(
    data: LieData,
    source: tuple[tuple[Monomial, int], ...],
    target: tuple[tuple[Monomial, int], ...],
    dc: tuple[dict[Monomial, sp.Expr], ...],
    actions: tuple[tuple[tuple[tuple[int, sp.Expr], ...], ...], ...],
) -> tuple[SparseVector, ...]:
    target_index = {basis: index for index, basis in enumerate(target)}
    output: list[SparseVector] = []
    for monomial, state in source:
        image: dict[int, sp.Expr] = {}
        for result_monomial, coefficient in ce_on_monomial(monomial, dc).items():
            key = (result_monomial, state)
            if key not in target_index:
                raise AssertionError("ghost differential left the declared grading window")
            add_term(image, target_index[key], coefficient)

        # c^a rho(G_a), with the ghost inserted on the left.
        for ghost in range(15):
            product = wedge((ghost,), monomial)
            if product is None:
                continue
            sign, result_monomial = product
            for result_state, coefficient in actions[ghost][state]:
                key = (result_monomial, result_state)
                if key not in target_index:
                    raise AssertionError(
                        "state action left the cutoff: the proposed BRST window is incomplete"
                    )
                add_term(image, target_index[key], sign * coefficient)
        output.append(clean(image))
    return tuple(output)


def compose(
    first: tuple[SparseVector, ...],
    second: tuple[SparseVector, ...],
) -> tuple[SparseVector, ...]:
    output: list[SparseVector] = []
    for column in first:
        result: dict[int, sp.Expr] = {}
        for middle, first_value in column.items():
            for row, second_value in second[middle].items():
                add_term(result, row, first_value * second_value)
        output.append(clean(result))
    return tuple(output)


def modular_square_root_rational(value: sp.Rational) -> int:
    """A fixed good-prime image of a positive rational square root."""

    value = R(value)

    def integer_root(integer: int) -> int:
        result = 1
        for prime, exponent in sp.factorint(integer).items():
            result = result * pow(prime, exponent // 2, MODULAR_PRIME) % MODULAR_PRIME
            if exponent % 2:
                if prime not in MODULAR_ROOTS:
                    raise ValueError(f"unsupported radical prime {prime}")
                result = result * MODULAR_ROOTS[prime] % MODULAR_PRIME
        return result

    numerator = integer_root(int(value.p))
    denominator = integer_root(int(value.q))
    return numerator * pow(denominator, -1, MODULAR_PRIME) % MODULAR_PRIME


def modular_value(value: sp.Expr) -> int:
    """Evaluate the exact coefficient field in ``GF(241)``.

    The exact matrices lie in ``Q(i,sqrt(2),sqrt(3),sqrt(5))``.  The chosen
    images obey the defining square relations.  Therefore a nonzero minor
    after reduction proves that the corresponding characteristic-zero minor
    is nonzero; modular rank is a rigorous lower bound on exact rank.
    """

    value = sp.sympify(value)
    if value == I:
        return MODULAR_ROOTS[-1]
    if value.is_Integer:
        return int(value) % MODULAR_PRIME
    if value.is_Rational:
        return int(value.p) * pow(int(value.q), -1, MODULAR_PRIME) % MODULAR_PRIME
    if value.is_Add:
        return sum(modular_value(term) for term in value.args) % MODULAR_PRIME
    if value.is_Mul:
        result = 1
        for factor in value.args:
            result = result * modular_value(factor) % MODULAR_PRIME
        return result
    if value.is_Pow:
        base, exponent = value.args
        if exponent.q == 2 and base.is_Rational and base > 0:
            root = modular_square_root_rational(base)
            if exponent.p < 0:
                root = pow(root, -1, MODULAR_PRIME)
            return pow(root, abs(int(exponent.p)), MODULAR_PRIME)
        if exponent.is_Integer:
            return pow(modular_value(base), int(exponent), MODULAR_PRIME)
    raise ValueError(f"coefficient is outside the certified number field: {value}")


def modular_rank(columns: tuple[SparseVector, ...], rows: int) -> int:
    row_data: dict[int, dict[int, int]] = {}
    for column, vector in enumerate(columns):
        for row, value in vector.items():
            reduced = modular_value(value)
            if reduced:
                row_data.setdefault(row, {})[column] = reduced
    matrix = DomainMatrix.from_dict_sympy(rows, len(columns), row_data).convert_to(
        GF(MODULAR_PRIME)
    )
    return matrix.rank()


def verify_rank_certificate(
    d3: tuple[SparseVector, ...],
    d4: tuple[SparseVector, ...],
    middle_dimension: int,
    final_dimension: int,
) -> None:
    check(
        "C2g-N: GF(241) contains the declared images of i,sqrt(2),sqrt(3),sqrt(5)",
        all(
            MODULAR_ROOTS[value] ** 2 % MODULAR_PRIME == value % MODULAR_PRIME
            for value in MODULAR_ROOTS
        ),
    )
    coefficients = tuple(
        value for column in (*d3, *d4) for value in column.values()
    )
    radical_bases = {
        power.base
        for value in coefficients
        for power in value.atoms(sp.Pow)
        if power.exp.q == 2
    }
    check(
        "C2g-N: every differential coefficient lies in Q(i,sqrt(2),sqrt(3),sqrt(5))",
        radical_bases.issubset(
            {sp.Integer(value) for value in (2, 3, 5, 6, 10, 15, 30)}
        )
        and all(
            modular_value(value) == modular_value(sp.expand(value))
            for value in coefficients
        ),
    )
    rank_d3_modular = modular_rank(d3, middle_dimension)
    rank_d4_modular = modular_rank(d4, final_dimension)
    check(
        "C2g-N: exact modular ranks are rank(d3)=260 and rank(d4)=1051",
        (rank_d3_modular, rank_d4_modular) == (260, 1051),
    )
    # A nonzero minor modulo a good prime is a nonzero exact minor, so the
    # two modular ranks are lower bounds.  Exact nilpotency gives the opposite
    # bound rank(d3)+rank(d4)<=dim(C4).  Saturation therefore fixes both exact
    # ranks and the exact cohomology dimension.
    check(
        "C2g-N: modular lower bounds saturate the exact nilpotency bound, so H4 is zero",
        rank_d3_modular + rank_d4_modular == middle_dimension,
    )


def energy_indices(
    space: generator_data.RepresentationSpace, energy: int
) -> tuple[int, ...]:
    return tuple(
        index
        for mode in space.irreps
        if mode.energy == energy
        for index in range(
            space.offsets[mode.label],
            space.offsets[mode.label] + mode.dimension,
        )
    )


def symmetric_square_action(
    matrix: sp.Matrix,
) -> tuple[sp.Matrix, tuple[tuple[int, int], ...]]:
    """Second quantization on normalized two-boson occupation states."""

    pairs = tuple(combinations_with_replacement(range(matrix.rows), 2))
    pair_index = {pair: position for position, pair in enumerate(pairs)}
    output = sp.zeros(len(pairs))
    for column, (first, second) in enumerate(pairs):
        source_normalization = sp.sqrt(1 + int(first == second))
        for target, coefficient in enumerate(matrix[:, first]):
            if coefficient == 0:
                continue
            pair = tuple(sorted((target, second)))
            target_normalization = sp.sqrt(1 + int(pair[0] == pair[1]))
            output[pair_index[pair], column] += sp.simplify(
                coefficient * target_normalization / source_normalization
            )
        for target, coefficient in enumerate(matrix[:, second]):
            if coefficient == 0:
                continue
            pair = tuple(sorted((first, target)))
            target_normalization = sp.sqrt(1 + int(pair[0] == pair[1]))
            output[pair_index[pair], column] += sp.simplify(
                coefficient * target_normalization / source_normalization
            )
    return output, pairs


def two_particle_energy_four_actions(
    data: LieData,
) -> tuple[tuple[sp.Matrix, ...], tuple[tuple[int, int], ...]]:
    """Exact residual action needed on ``Sym^2(E2+ + E2-)``.

    Only the compact action enters the ghost-number-four differential.
    Lowering annihilates both lowest-weight factors.  Raising would leave
    energy four, but its dual ghost is already present in the saturated
    four-raising-ghost monomial, so that contribution vanishes before the
    omitted target action is used.
    """

    plus = generator_data.representation_space(+1)
    minus = generator_data.representation_space(-1)
    plus_indices = energy_indices(plus, 2)
    minus_indices = energy_indices(minus, 2)
    one_particle_compact = (
        2 * sp.eye(10),
        *(
            sp.diag(
                plus.left[axis].extract(plus_indices, plus_indices),
                minus.left[axis].extract(minus_indices, minus_indices),
            )
            for axis in ("x", "y", "z")
        ),
        *(
            sp.diag(
                plus.right[axis].extract(plus_indices, plus_indices),
                minus.right[axis].extract(minus_indices, minus_indices),
            )
            for axis in ("x", "y", "z")
        ),
    )
    induced = tuple(symmetric_square_action(matrix) for matrix in one_particle_compact)
    pairs = induced[0][1]
    check(
        "C2g-N: all compact generators use one normalized 55-state symmetric-square basis",
        len(pairs) == 55 and all(item[1] == pairs for item in induced),
    )
    zero = sp.zeros(55)
    actions = tuple(item[0] for item in induced) + (zero,) * 8
    check(
        "C2g-N: the second-quantized time generator is exactly 4I on the two-particle block",
        actions[0] == 4 * sp.eye(55),
    )
    check(
        "C2g-N: the supplied two-particle action follows the fitted fifteen-generator ordering",
        data.names[:7] == ("D", "Lx", "Ly", "Lz", "Rx", "Ry", "Rz")
        and len(actions) == 15,
    )
    return actions, pairs


def chiral_weyl_square_candidates(
    pairs: tuple[tuple[int, int], ...],
) -> sp.Matrix:
    pair_index = {pair: position for position, pair in enumerate(pairs)}
    plus = sp.zeros(len(pairs), 1)
    minus = sp.zeros(len(pairs), 1)
    # Each E2 chirality is a spin-two irrep in descending magnetic order.
    # The normalized bosonic scalar has coefficients
    # (+sqrt(2),-sqrt(2),+1)/sqrt(5).
    for vector, offset in ((plus, 0), (minus, 5)):
        vector[pair_index[(offset, offset + 4)]] = sp.sqrt(R(2, 5))
        vector[pair_index[(offset + 1, offset + 3)]] = -sp.sqrt(R(2, 5))
        vector[pair_index[(offset + 2, offset + 2)]] = 1 / sp.sqrt(5)
    return sp.Matrix.hstack(plus, minus)


def columns_to_matrix(
    columns: tuple[SparseVector, ...], rows: int
) -> sp.SparseMatrix:
    entries = {
        (row, column): value
        for column, vector in enumerate(columns)
        for row, value in vector.items()
    }
    return sp.SparseMatrix(rows, len(columns), entries)


def verify_two_particle_window(data: LieData, dc: tuple[dict[Monomial, sp.Expr], ...]) -> None:
    actions, pairs = two_particle_energy_four_actions(data)
    sparse = matrices_to_sparse_actions(actions)
    raising_volume = tuple(range(11, 15))
    c3: tuple[tuple[Monomial, int], ...] = ()
    c4 = tuple((raising_volume, state) for state in range(55))
    c5 = tuple(
        (tuple(sorted((*raising_volume, compact))), state)
        for compact in range(7)
        for state in range(55)
    )
    c6 = tuple(
        (tuple(sorted((*raising_volume, *compact))), state)
        for compact in combinations(range(7), 2)
        for state in range(55)
    )
    check(
        "C2g-N: the two-particle absolute window dimensions are 0 -> 55 -> 385 -> 1155",
        (len(c3), len(c4), len(c5), len(c6)) == (0, 55, 385, 1155),
    )
    d4 = differential(data, c4, c5, dc, sparse)
    d5 = differential(data, c5, c6, dc, sparse)
    check(
        "C2g-N: the two-particle cutoff-complete differential obeys d5*d4=0 exactly",
        all(not column for column in compose(d4, d5)),
    )

    candidates = chiral_weyl_square_candidates(pairs)
    d4_matrix = columns_to_matrix(d4, len(c5))
    check(
        "C2g-N: both normalized chiral Weyl-square scalars are exact d4 cocycles",
        d4_matrix * candidates == sp.zeros(len(c5), 2) and candidates.rank() == 2,
    )
    rank_modular = modular_rank(d4, len(c5))
    check(
        "C2g-N: the two-particle d4 has modular rank 53",
        rank_modular == 53,
    )
    # The two displayed exact kernel vectors give rank(d4)<=53, while the
    # good-prime minor gives rank(d4)>=53.  Hence the exact rank is 53.
    # Since C3 is empty, there are no incoming exacts in this particle-number
    # sector and the two cocycles form the complete absolute global H4.
    check(
        "C2g-N: H4 in the global-only particle-number-two sector is exactly the two Weyl-square scalars",
        len(c4) - rank_modular == candidates.cols == 2 and not c3,
    )


def verify_window(data: LieData) -> tuple[
    tuple[tuple[Monomial, int], ...],
    tuple[tuple[Monomial, int], ...],
    tuple[tuple[Monomial, int], ...],
]:
    check(
        "C2g-N: ghost-degree widths are fixed by 4 raising, 7 compact, and 4 lowering ghosts",
        tuple(ghost_width(number) for number in range(16))
        == (0, 1, 2, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 2, 1, 0),
    )
    check(
        "C2g-N: the buffer rule requires E<=4 for (delta,g)=(0,4) and E<=6 for (2,4)",
        required_upper_energy(0, 4) == 4
        and required_upper_energy(2, 4) == 6,
    )
    check(
        "C2g-N: the one-particle module has a true lowest energy two",
        min(data.state_energies) == 2,
    )
    lowering = range(7, 11)
    energy_two = tuple(index for index, energy in enumerate(data.state_energies) if energy == 2)
    check(
        "C2g-N: every lowering generator annihilates the energy-two boundary",
        all(
            all(data.matrices[generator][row, column] == 0 for row in range(len(data.state_energies)))
            for generator in lowering for column in energy_two
        ),
    )

    bases = tuple(cochain_basis(data, number, 0) for number in (3, 4, 5))
    used_energies = tuple(
        tuple(sorted({data.state_energies[state] for _, state in basis}))
        for basis in bases
    )
    check(
        "C2g-N: C3/C4/C5 at total degree zero use only energies (2,3), (2,3,4), (2,3,4)",
        used_energies == ((2, 3), (2, 3, 4), (2, 3, 4)),
    )
    check(
        "C2g-N: every energy-four C4 cochain contains all four raising ghosts",
        all(
            set(range(11, 15)).issubset(monomial)
            for monomial, state in bases[1]
            if data.state_energies[state] == 4
        ),
    )
    check(
        "C2g-N: one chirality has the exact finite window dimensions 290 -> 1311 -> 3657",
        tuple(len(basis) for basis in bases) == (290, 1311, 3657),
    )
    return bases


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-local-brst",
        action="store_true",
        help="fail closed: the local Diff x Weyl complex is not encoded",
    )
    parser.add_argument(
        "--require-energy-six-fock",
        action="store_true",
        help="fail closed: the separate C2g-N6 module is not encoded in this certificate",
    )
    parser.add_argument(
        "--require-physical-cohomology",
        action="store_true",
        help="fail closed: this is only a global free-module CE window",
    )
    args = parser.parse_args()
    if args.require_local_brst:
        raise SystemExit(
            "the local Diff x Weyl ghosts, auxiliaries, zero modes, and contractible pairs are not encoded"
        )
    if args.require_energy_six_fock:
        raise SystemExit(
            "this first-window certificate does not encode the complete energy-six Fock module; see C2g-N6"
        )
    if args.require_physical_cohomology:
        raise SystemExit(
            "global free-module CE cohomology is not the combined local-plus-global physical BRST cohomology"
        )

    data = build_lie_data(1)
    c3, c4, c5 = verify_window(data)
    dc = ghost_differentials(data)
    actions = sparse_actions(data)
    d3 = differential(data, c3, c4, dc, actions)
    d4 = differential(data, c4, c5, dc, actions)
    check(
        "C2g-N: the cutoff-complete global differential obeys d4*d3=0 exactly",
        all(not column for column in compose(d3, d4)),
    )
    verify_rank_certificate(d3, d4, len(c4), len(c5))
    verify_two_particle_window(data, dc)
    print("C2g-N one-chirality cochain dimensions:", len(c3), len(c4), len(c5))
    print(
        "C2g-N STATUS: EXACT CUTOFF-COMPLETE GLOBAL-ONLY "
        "KERNEL/IMAGE WINDOW AT (total degree, ghost number)=(0,4). "
        "The one-particle H4 is zero; the particle-number-two H4 is "
        "exactly two dimensional and is spanned by the chiral Weyl-square "
        "scalars. "
        "No local-plus-global or energy-six physical cohomology is claimed."
    )


if __name__ == "__main__":
    main()
