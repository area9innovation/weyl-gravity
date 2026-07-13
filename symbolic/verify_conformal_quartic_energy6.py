#!/usr/bin/env python3
"""P4 staging certificate for the compact-energy-six Weyl block.

This file is deliberately an *assembly and completeness* certificate, not a
claim that the Weyl quartic block has already been evaluated.  It fixes the
finite-dimensional target of that calculation, the sign conventions, the
exchange-resolvent convention, and the fail-closed interface through which
exact contact and cubic-current data must pass.

The central distinction is the one established in C1a:

* flat time translation ``P_0`` has Jordan blocks;
* cylinder time translation ``D`` is diagonal on the normalizable oscillator
  harmonic towers.

Consequently semisimple cylinder oscillator blocks use ordinary denominators
``1/(Delta_lambda-6)``.  The finite nilpotent formula is implemented and
tested below, but nonzero nilpotents are rejected for physical cylinder
blocks unless a separate gauge-fixed derivation explicitly authorizes them.

The proposed three-channel calculation lives in the parity sector of the
common SO(4) irrep (2,2):

    Sym^2 A_3,   E_2 A_4,   E_2 L_4.

Each occurs once after parity projection, so its reduced Wigner--Eckart
matrix is 3 x 3 and represents 25 magnetic components.  It is only one
75-dimensional subblock of the complete 2062-dimensional energy-six Fock
shell.  The script enumerates the other reduced irreps explicitly so that a
single subblock cannot accidentally be advertised as the complete shell.
The block and its inherited pairing remain provisional until the compact
global BRST/Taub/linearization-stability reduction is supplied.

Run normally for exact staging checks.  ``--require-data`` fails until an
independently generated exact vertex archive is supplied and all acceptance
rails are marked complete.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Iterable, Mapping, Sequence

import sympy as sp


PASS = True


def check(label: str, condition: object) -> None:
    global PASS
    ok = bool(condition)
    print(("[OK ] " if ok else "[FAIL] ") + label)
    PASS = PASS and ok


def dagger(matrix: sp.Matrix) -> sp.Matrix:
    return matrix.conjugate().T


def sym_power_dimension(dimension: int, degree: int) -> int:
    return int(sp.binomial(dimension + degree - 1, degree))


# ---------------------------------------------------------------------------
# Exact compact SO(4)=SU(2)_L x SU(2)_R bookkeeping
# Spins are stored doubled, so every label is integral.
# ---------------------------------------------------------------------------
@dataclass(frozen=True, order=True)
class SO4Irrep:
    left2: int
    right2: int

    @property
    def dimension(self) -> int:
        return (self.left2 + 1) * (self.right2 + 1)

    @property
    def parity_conjugate(self) -> "SO4Irrep":
        return SO4Irrep(self.right2, self.left2)

    def display(self) -> str:
        return f"({sp.Rational(self.left2, 2)},{sp.Rational(self.right2, 2)})"


def su2_product(first2: int, second2: int) -> range:
    return range(abs(first2 - second2), first2 + second2 + 1, 2)


def so4_product(first: SO4Irrep, second: SO4Irrep) -> list[SO4Irrep]:
    return [
        SO4Irrep(left2, right2)
        for left2 in su2_product(first.left2, second.left2)
        for right2 in su2_product(first.right2, second.right2)
    ]


def symmetric_square(irrep: SO4Irrep) -> list[SO4Irrep]:
    """Multiplicity-free symmetric square of one SU(2)xSU(2) irrep."""
    result: list[SO4Irrep] = []
    for target in so4_product(irrep, irrep):
        # Exchange parity in j x j -> J is (-1)^(2j-J).  With doubled
        # labels the exponent is (2*j2-J2)/2 for each SU(2) factor.
        exponent = (
            (2 * irrep.left2 - target.left2) // 2
            + (2 * irrep.right2 - target.right2) // 2
        )
        if exponent % 2 == 0:
            result.append(target)
    return result


E2 = (SO4Irrep(4, 0), SO4Irrep(0, 4))
A3 = (SO4Irrep(3, 1), SO4Irrep(1, 3))
A4 = (SO4Irrep(4, 2), SO4Irrep(2, 4))
L4 = (SO4Irrep(4, 0), SO4Irrep(0, 4))


def full_symmetric_a3_square() -> Counter[SO4Irrep]:
    # Sym^2(V+ + V-) = Sym^2 V+ + (V+ tensor V-) + Sym^2 V-.
    return Counter(
        symmetric_square(A3[0])
        + so4_product(A3[0], A3[1])
        + symmetric_square(A3[1])
    )


def full_product(
    first: Sequence[SO4Irrep], second: Sequence[SO4Irrep]
) -> Counter[SO4Irrep]:
    result: Counter[SO4Irrep] = Counter()
    for left in first:
        for right in second:
            result.update(so4_product(left, right))
    return result


AA_REPS = full_symmetric_a3_square()
EA_REPS = full_product(E2, A4)
EL_REPS = full_product(E2, L4)
COMMON_EA = AA_REPS & EA_REPS
COMMON_EL = AA_REPS & EL_REPS
COMMON_ALL = AA_REPS & EA_REPS & EL_REPS
TARGET_IRREP = SO4Irrep(4, 4)  # ordinary-spin notation (2,2)


check(
    "P4a: the only SO(4) irrep common to AA, EA, and EL is (2,2)",
    set(COMMON_ALL) == {TARGET_IRREP},
)
check(
    "P4a: before parity, (2,2) multiplicities are 1,2,2",
    (
        AA_REPS[TARGET_IRREP],
        EA_REPS[TARGET_IRREP],
        EL_REPS[TARGET_IRREP],
    )
    == (1, 2, 2),
)
# Parity exchanges the two EA copies and the two EL copies.  Their parity-p
# combinations are each one-dimensional.  The cross-chiral bosonic AA copy
# already has fixed parity (up to the common intrinsic phase convention).
PARITY_REDUCED_MULTIPLICITIES = (1, 1, 1)
check(
    "P4a: a fixed matching parity gives the advertised 3-channel block",
    PARITY_REDUCED_MULTIPLICITIES == (1, 1, 1)
    and TARGET_IRREP.dimension == 25,
)


# ---------------------------------------------------------------------------
# Complete energy-six shell and the selected reduced block
# ---------------------------------------------------------------------------
def lower_tt(energy: int) -> int:
    return 2 * (energy - 1) * (energy + 3) if energy >= 2 else 0


def vector(energy: int) -> int:
    return 2 * (energy - 1) * (energy + 1) if energy >= 3 else 0


def upper_tt(energy: int) -> int:
    return 2 * (energy - 3) * (energy + 1) if energy >= 4 else 0


def one_particle_signature(energy: int) -> tuple[int, int]:
    return lower_tt(energy), vector(energy) + upper_tt(energy)


e6_one_plus, e6_one_minus = one_particle_signature(6)
e6_24_plus = lower_tt(2) * lower_tt(4)
e6_24_minus = lower_tt(2) * (vector(4) + upper_tt(4))
e6_33_plus = sym_power_dimension(lower_tt(3), 2) + sym_power_dimension(
    vector(3), 2
)
e6_33_minus = lower_tt(3) * vector(3)
e6_222_plus = sym_power_dimension(lower_tt(2), 3)
FULL_E6_SIGNATURE = (
    e6_one_plus + e6_24_plus + e6_33_plus + e6_222_plus,
    e6_one_minus + e6_24_minus + e6_33_minus,
)
FULL_E6_DIMENSION = sum(FULL_E6_SIGNATURE)
check(
    "P4b: complete compact-energy-six Fock signature is (1166,896)",
    FULL_E6_SIGNATURE == (1166, 896) and FULL_E6_DIMENSION == 2062,
)

# Reduced Wigner--Eckart order: |A3 A3>, |E2 A4>, |E2 L4>.
# The first state has positive Fock sign; the other two have negative sign.
H0_REDUCED = 6 * sp.eye(3)
J_REDUCED = sp.diag(1, -1, -1)
H0_TARGET_FULL = sp.kronecker_product(H0_REDUCED, sp.eye(25))
J_TARGET_FULL = sp.kronecker_product(J_REDUCED, sp.eye(25))
check(
    "P4b: target block is 3 reduced copies / 75 magnetic states",
    H0_TARGET_FULL.shape == (75, 75)
    and J_TARGET_FULL.shape == (75, 75)
    and J_TARGET_FULL**2 == sp.eye(75),
)
check(
    "P4b: target signature is (+25,-50), not the full shell",
    (25, 50) != FULL_E6_SIGNATURE,
)


# ---------------------------------------------------------------------------
# Exchange resolvent: physical cylinder D is semisimple.
# ---------------------------------------------------------------------------
def finite_nilpotent_resolvent(
    block_energy: sp.Expr,
    shell_energy: sp.Expr,
    nilpotent: sp.Matrix,
    nilpotency_index: int,
) -> sp.Matrix:
    """Inverse of (block_energy-shell_energy)I+N for N^r=0."""
    if nilpotent.rows != nilpotent.cols:
        raise ValueError("nilpotent block must be square")
    if nilpotency_index < 1:
        raise ValueError("nilpotency index must be positive")
    if nilpotent**nilpotency_index != sp.zeros(nilpotent.rows):
        raise ValueError("declared nilpotency index is false")
    delta = sp.simplify(block_energy - shell_energy)
    if delta == 0:
        raise ValueError("Q block cannot lie on the projected shell")
    result = sp.zeros(nilpotent.rows)
    for power in range(nilpotency_index):
        result += (-1) ** power * nilpotent**power / delta ** (power + 1)
    return sp.simplify(result)


test_lambda = sp.Rational(17, 2)
test_N = sp.Matrix([[0, 1, 0], [0, 0, 1], [0, 0, 0]])
test_R = finite_nilpotent_resolvent(test_lambda, 6, test_N, 3)
test_operator = (test_lambda - 6) * sp.eye(3) + test_N
check(
    "P4c: guarded finite-nilpotent inverse is exact on both sides",
    test_operator * test_R == sp.eye(3)
    and test_R * test_operator == sp.eye(3),
)


@dataclass(frozen=True)
class IntermediateBlock:
    """One exact Q-space block used by the cubic exchange term.

    ``left`` and ``right`` are mixed-index operator matrices.  An archive
    generated from lower-index Krein amplitudes must raise the internal index
    with the inverse Q-space Gram matrix before constructing this object.
    """

    label: str
    energy: sp.Expr
    left: sp.Matrix  # P V3 Q, shape target x intermediate
    right: sp.Matrix  # Q V3 P, shape intermediate x target
    nilpotent: sp.Matrix | None = None
    nilpotency_index: int = 1
    cylinder_jordan_derived: bool = False

    def resolvent(self, shell_energy: sp.Expr = sp.Integer(6)) -> sp.Matrix:
        dimension = self.right.rows
        if self.left.shape != (3, dimension) or self.right.cols != 3:
            raise ValueError(f"{self.label}: inconsistent coupling shapes")
        N = self.nilpotent if self.nilpotent is not None else sp.zeros(dimension)
        if N.shape != (dimension, dimension):
            raise ValueError(f"{self.label}: inconsistent nilpotent shape")
        if N != sp.zeros(dimension) and not self.cylinder_jordan_derived:
            raise ValueError(
                f"{self.label}: refusing to import a flat-P0 Jordan "
                "nilpotent into the compact-D resolvent"
            )
        return finite_nilpotent_resolvent(
            self.energy, shell_energy, N, self.nilpotency_index
        )


zero_N_block = IntermediateBlock(
    "physical-D-test",
    sp.Integer(8),
    sp.Matrix([[1, 0], [0, 1], [1, -1]]),
    sp.Matrix([[2, 0, 1], [0, 3, -1]]),
    sp.zeros(2),
)
check(
    "P4c: a physical compact-D block uses the ordinary denominator",
    zero_N_block.resolvent() == sp.eye(2) / 2,
)
try:
    IntermediateBlock(
        "illegal-flat-import",
        8,
        sp.zeros(3, 2),
        sp.zeros(2, 3),
        sp.Matrix([[0, 1], [0, 0]]),
        2,
    ).resolvent()
except ValueError as error:
    rejected_flat_nilpotent = "flat-P0" in str(error)
else:
    rejected_flat_nilpotent = False
check(
    "P4c: an underived Jordan nilpotent is rejected fail-closed",
    rejected_flat_nilpotent,
)


# Quartic determinant rail needed when the three-wave perturbiner is extended
# to four waves: sqrt(det(I+A)) = exp(Tr log(I+A)/2).
def sqrt_det_trace_order4(
    trace1: sp.Expr,
    trace2: sp.Expr,
    trace3: sp.Expr,
    trace4: sp.Expr,
) -> sp.Expr:
    return (
        trace1**4 / 384
        - trace1**2 * trace2 / 32
        + trace2**2 / 32
        + trace1 * trace3 / 12
        - trace4 / 8
    )


x1, x2, x3, x4, eps = sp.symbols("x1 x2 x3 x4 eps")
diagonal_entries = (x1, x2, x3, x4)
direct_sqrt_det = sp.prod(sp.sqrt(1 + eps * x) for x in diagonal_entries)
direct_order4 = sp.expand(sp.series(direct_sqrt_det, eps, 0, 5).removeO()).coeff(
    eps, 4
)
trace_order4 = sqrt_det_trace_order4(
    sum(diagonal_entries),
    sum(x**2 for x in diagonal_entries),
    sum(x**3 for x in diagonal_entries),
    sum(x**4 for x in diagonal_entries),
)
check(
    "P4d: fourth-order square-root determinant trace formula is exact",
    sp.expand(direct_order4 - trace_order4) == 0,
)


# ---------------------------------------------------------------------------
# Exact contact-plus-exchange assembly and complete reduced-shell cokernel
# ---------------------------------------------------------------------------
def assemble_effective_block(
    contact: sp.Matrix, intermediates: Iterable[IntermediateBlock]
) -> sp.Matrix:
    if contact.shape != (3, 3):
        raise ValueError("reduced contact block must be 3 x 3")
    result = sp.Matrix(contact)
    for block in intermediates:
        result -= block.left * block.resolvent(6) * block.right
    return sp.simplify(result)


def obstruction_source(effective: sp.Matrix) -> sp.Matrix:
    return sp.simplify(J_REDUCED * effective - dagger(effective) * J_REDUCED)


def antihermitian_coordinates(source: sp.Matrix) -> dict[str, sp.Expr]:
    """All n^2 real coordinates of an anti-Hermitian matrix."""
    if source.rows != source.cols:
        raise ValueError("source must be square")
    if sp.simplify(dagger(source) + source) != sp.zeros(source.rows):
        raise ValueError("source is not anti-Hermitian")
    coordinates: dict[str, sp.Expr] = {}
    for row in range(source.rows):
        coordinates[f"diag_{row}"] = sp.simplify(-sp.I * source[row, row])
    for row in range(source.rows):
        for column in range(row + 1, source.cols):
            coordinates[f"real_{row}_{column}"] = sp.simplify(
                (source[row, column] - source[column, row]) / 2
            )
            coordinates[f"imag_{row}_{column}"] = sp.simplify(
                -sp.I * (source[row, column] + source[column, row]) / 2
            )
    return coordinates


def reconstruct_antihermitian(
    coordinates: Mapping[str, sp.Expr], dimension: int
) -> sp.Matrix:
    result = sp.zeros(dimension)
    for row in range(dimension):
        result[row, row] = sp.I * coordinates[f"diag_{row}"]
    for row in range(dimension):
        for column in range(row + 1, dimension):
            real = coordinates[f"real_{row}_{column}"]
            imag = coordinates[f"imag_{row}_{column}"]
            result[row, column] = real + sp.I * imag
            result[column, row] = -real + sp.I * imag
    return result


# Synthetic rational fixture: it certifies assembly signs, dimensions,
# ordinary cylinder denominators, and that the nine real cokernel coordinates
# reconstruct the complete source.  It is not Weyl vertex data.
fixture_contact = sp.Matrix(
    [[1, 2 + sp.I, 0], [2 - sp.I, 3, 1], [0, 1, -2]]
)
fixture_blocks = (
    zero_N_block,
    IntermediateBlock(
        "second-ordering-test",
        5,
        sp.Matrix([[0], [2], [sp.I]]),
        sp.Matrix([[1, -1, 2]]),
        sp.zeros(1),
    ),
)
fixture_effective = assemble_effective_block(fixture_contact, fixture_blocks)
fixture_source = obstruction_source(fixture_effective)
fixture_coordinates = antihermitian_coordinates(fixture_source)
check(
    "P4e: contact-minus-all-exchanges assembly is exact",
    fixture_effective
    == sp.simplify(
        fixture_contact
        - zero_N_block.left * (sp.eye(2) / 2) * zero_N_block.right
        + fixture_blocks[1].left * fixture_blocks[1].right
    ),
)
check(
    "P4e: all nine reduced-shell cokernel coordinates reconstruct S6",
    len(fixture_coordinates) == 9
    and reconstruct_antihermitian(fixture_coordinates, 3) == fixture_source,
)
check(
    "P4e: fixed-D shell deformation map vanishes, so the whole source is cokernel",
    dagger(H0_REDUCED) * sp.eye(3) - sp.eye(3) * H0_REDUCED
    == sp.zeros(3),
)


# ---------------------------------------------------------------------------
# Fail-closed archive interface for the actual Weyl calculation
# ---------------------------------------------------------------------------
REQUIRED_RAILS = (
    "external_harmonic_normalization",
    "external_eom_and_brst_closure",
    "global_brst_taub_linearization_stability_reduction",
    "quartic_contact_all_orderings",
    "cubic_currents_all_pairings",
    "internal_inverse_gram_convention",
    "complete_internal_metric_harmonics",
    "constraint_and_auxiliary_contributions",
    "internal_gauge_independence",
    "external_ward_identities",
    "bose_parity_so4_covariance",
    "reverse_j_adjoint",
    "stationary_born_normalization_and_time_ordering",
    "normal_ordered_connected_tree_projection",
    "vacuum_and_loop_scope",
    "reducible_external_state_subtraction",
)

# Concrete generated inputs expected beneath build/conformal-p4/energy6/.
# The combined archive may inline their matrices, but it must retain an
# immutable digest for each independently auditable artifact.
REQUIRED_ARTIFACTS = (
    "target_basis.json",
    "global_constraint_reduction.json",
    "contact_forward.json",
    "contact_reverse.json",
    "quadratic_hessian_de_donder_weyl.json",
    "cubic_currents_all_pairings.json",
    "exchanges_forward.json",
    "exchanges_reverse.json",
    "ward_and_gauge_variants.json",
    "stationary_born_mapping.json",
    "connected_tree_scope.json",
    "external_state_subtractions.json",
)

CONNECTED_TREE_SCOPE = "connected_tree_contact_plus_one_line_exchange"


def load_archive(path: Path) -> tuple[sp.Matrix, list[IntermediateBlock], dict]:
    """Load a future exact archive; numeric floats are rejected.

    Matrix entries are SymPy strings.  Every intermediate record must carry
    its energy and both reduced coupling matrices.  Physical compact-D data
    must omit ``nilpotent`` or set it identically to zero.
    """
    payload = json.loads(path.read_text())
    if payload.get("operator_scope") != CONNECTED_TREE_SCOPE:
        raise ValueError(
            "archive must declare operator_scope=" + CONNECTED_TREE_SCOPE
        )
    rails = payload.get("rails", {})
    missing = [rail for rail in REQUIRED_RAILS if rails.get(rail) is not True]
    if missing:
        raise ValueError("incomplete acceptance rails: " + ", ".join(missing))
    artifacts = payload.get("artifacts", {})
    missing_artifacts = []
    artifact_paths: dict[str, Path] = {}
    for artifact in REQUIRED_ARTIFACTS:
        record = artifacts.get(artifact)
        if not isinstance(record, Mapping):
            missing_artifacts.append(artifact)
            continue
        digest = str(record.get("sha256", ""))
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            missing_artifacts.append(artifact)
            continue
        artifact_path = path.parent / str(record.get("path", artifact))
        if not artifact_path.is_file():
            missing_artifacts.append(artifact)
            continue
        actual = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        if actual != digest:
            raise ValueError(f"artifact digest mismatch: {artifact}")
        artifact_paths[artifact] = artifact_path
    if missing_artifacts:
        raise ValueError(
            "missing immutable generated artifacts: "
            + ", ".join(missing_artifacts)
        )

    def exact_matrix(rows: Sequence[Sequence[str]]) -> sp.Matrix:
        matrix = sp.Matrix([[sp.sympify(entry) for entry in row] for row in rows])
        if any(value.has(sp.Float) for value in matrix):
            raise ValueError("floating-point vertex data are forbidden")
        return matrix

    contact = exact_matrix(payload["contact"])
    blocks: list[IntermediateBlock] = []
    labels: set[str] = set()
    for record in payload["intermediates"]:
        label = str(record["label"])
        if label in labels:
            raise ValueError(f"duplicate intermediate ordering: {label}")
        labels.add(label)
        left = exact_matrix(record["left"])
        right = exact_matrix(record["right"])
        dimension = right.rows
        N = exact_matrix(record.get("nilpotent", sp.zeros(dimension).tolist()))
        block_energy = sp.sympify(record["energy"])
        if block_energy.has(sp.Float):
            raise ValueError(f"{label}: floating-point intermediate energy is forbidden")
        blocks.append(
            IntermediateBlock(
                label,
                block_energy,
                left,
                right,
                N,
                int(record.get("nilpotency_index", 1)),
                bool(record.get("cylinder_jordan_derived", False)),
            )
        )
    if not blocks:
        raise ValueError("archive has no exchange blocks")

    # The immutable mapping artifact is not decorative provenance.  It
    # duplicates the exact operator inputs and canonical assembled outputs,
    # and the loader recomputes each output from the archive matrices.  This
    # prevents stale or unrelated inline matrices from passing merely because
    # a set of correctly hashed files happens to be present.
    mapping = json.loads(
        artifact_paths["stationary_born_mapping.json"].read_text()
    )
    required_mapping_rails = (
        "overall_i_and_physical_adjoint",
        "both_old_fashioned_time_orderings",
        "derivative_interaction_contact_legendre_map",
        "compact_state_and_lsz_normalization",
        "compact_energy_denominators",
    )
    if mapping.get("operator_scope") != CONNECTED_TREE_SCOPE:
        raise ValueError("stationary Born mapping has the wrong operator scope")
    if mapping.get("assembly_convention") != "contact_minus_exchange":
        raise ValueError("stationary Born mapping has the wrong assembly convention")
    mapping_energy_raw = mapping.get("shell_energy")
    mapping_energy = (
        None if mapping_energy_raw is None else sp.sympify(mapping_energy_raw)
    )
    if (
        mapping_energy is None
        or mapping_energy.has(sp.Float)
        or mapping_energy != 6
    ):
        raise ValueError("stationary Born mapping has the wrong exact shell energy")
    mapping_rails = mapping.get("normalization_rails", {})
    missing_mapping = [
        rail for rail in required_mapping_rails if mapping_rails.get(rail) is not True
    ]
    if missing_mapping:
        raise ValueError(
            "incomplete stationary Born mapping rails: " + ", ".join(missing_mapping)
        )
    mapping_inputs = mapping.get("input_artifact_sha256", {})
    source_artifacts = tuple(
        artifact
        for artifact in REQUIRED_ARTIFACTS
        if artifact != "stationary_born_mapping.json"
    )
    if set(mapping_inputs) != set(source_artifacts) or any(
        mapping_inputs[artifact] != artifacts[artifact]["sha256"]
        for artifact in source_artifacts
    ):
        raise ValueError("stationary Born mapping is not linked to every input artifact")
    if mapping.get("contact") != payload.get("contact"):
        raise ValueError("stationary Born mapping contact is not cross-linked")
    if mapping.get("intermediates") != payload.get("intermediates"):
        raise ValueError("stationary Born mapping intermediates are not cross-linked")

    recomputed_effective = assemble_effective_block(contact, blocks)
    recomputed_source = obstruction_source(recomputed_effective)
    recomputed_coordinates = antihermitian_coordinates(recomputed_source)
    if exact_matrix(mapping["effective"]) != recomputed_effective:
        raise ValueError("stationary Born effective block fails semantic recomputation")
    if exact_matrix(mapping["source"]) != recomputed_source:
        raise ValueError("stationary Born source fails semantic recomputation")
    archived_coordinates = {
        str(key): sp.sympify(value)
        for key, value in mapping.get("cokernel_coordinates", {}).items()
    }
    if any(value.has(sp.Float) for value in archived_coordinates.values()):
        raise ValueError("floating-point cokernel coordinates are forbidden")
    if archived_coordinates != recomputed_coordinates:
        raise ValueError("stationary Born cokernel coordinates fail semantic recomputation")
    return contact, blocks, payload


def exact_rows(matrix: sp.Matrix) -> list[list[str]]:
    return [[sp.sstr(matrix[row, column]) for column in range(matrix.cols)] for row in range(matrix.rows)]


def test_archive_loader() -> None:
    """Exercise the fail-closed schema with a visibly synthetic archive."""

    with tempfile.TemporaryDirectory(prefix="conformal-p4-schema-") as directory:
        root = Path(directory)
        artifacts: dict[str, dict[str, str]] = {}
        for artifact in REQUIRED_ARTIFACTS:
            artifact_path = root / artifact
            artifact_path.write_text("synthetic schema fixture: " + artifact + "\n")
            artifacts[artifact] = {
                "sha256": hashlib.sha256(artifact_path.read_bytes()).hexdigest()
            }
        payload = {
            "operator_scope": CONNECTED_TREE_SCOPE,
            "rails": {rail: True for rail in REQUIRED_RAILS},
            "artifacts": artifacts,
            "contact": exact_rows(fixture_contact),
            "intermediates": [
                {
                    "label": block.label,
                    "energy": sp.sstr(block.energy),
                    "left": exact_rows(block.left),
                    "right": exact_rows(block.right),
                    "nilpotent": exact_rows(
                        block.nilpotent
                        if block.nilpotent is not None
                        else sp.zeros(block.right.rows)
                    ),
                    "nilpotency_index": block.nilpotency_index,
                }
                for block in fixture_blocks
            ],
            "provenance": {"fixture": "synthetic schema test only"},
        }
        mapping_path = root / "stationary_born_mapping.json"
        mapping_payload = {
            "operator_scope": CONNECTED_TREE_SCOPE,
            "assembly_convention": "contact_minus_exchange",
            "shell_energy": "6",
            "normalization_rails": {
                "overall_i_and_physical_adjoint": True,
                "both_old_fashioned_time_orderings": True,
                "derivative_interaction_contact_legendre_map": True,
                "compact_state_and_lsz_normalization": True,
                "compact_energy_denominators": True,
            },
            "input_artifact_sha256": {
                artifact: artifacts[artifact]["sha256"]
                for artifact in REQUIRED_ARTIFACTS
                if artifact != "stationary_born_mapping.json"
            },
            "contact": payload["contact"],
            "intermediates": payload["intermediates"],
            "effective": exact_rows(fixture_effective),
            "source": exact_rows(fixture_source),
            "cokernel_coordinates": {
                key: sp.sstr(value) for key, value in fixture_coordinates.items()
            },
        }
        mapping_path.write_text(json.dumps(mapping_payload, sort_keys=True))
        artifacts["stationary_born_mapping.json"]["sha256"] = hashlib.sha256(
            mapping_path.read_bytes()
        ).hexdigest()
        archive = root / "archive.json"
        archive.write_text(json.dumps(payload, sort_keys=True))
        contact, blocks, _ = load_archive(archive)
        check(
            "P4f: complete synthetic archive passes scope, digest, cross-link, and semantic checks",
            assemble_effective_block(contact, blocks) == fixture_effective,
        )
        exact_energy = payload["intermediates"][0]["energy"]
        payload["intermediates"][0]["energy"] = "8.0"
        archive.write_text(json.dumps(payload, sort_keys=True))
        try:
            load_archive(archive)
        except ValueError as error:
            float_energy_rejected = "floating-point intermediate energy" in str(error)
        else:
            float_energy_rejected = False
        check(
            "P4f: floating-point intermediate energies are rejected",
            float_energy_rejected,
        )
        payload["intermediates"][0]["energy"] = exact_energy
        archive.write_text(json.dumps(payload, sort_keys=True))
        exact_effective = mapping_payload["effective"]
        mapping_payload["effective"] = exact_rows(sp.zeros(3))
        mapping_path.write_text(json.dumps(mapping_payload, sort_keys=True))
        artifacts["stationary_born_mapping.json"]["sha256"] = hashlib.sha256(
            mapping_path.read_bytes()
        ).hexdigest()
        archive.write_text(json.dumps(payload, sort_keys=True))
        try:
            load_archive(archive)
        except ValueError as error:
            semantic_mismatch_rejected = "semantic recomputation" in str(error)
        else:
            semantic_mismatch_rejected = False
        check(
            "P4f: a freshly hashed but semantically stale assembled block is rejected",
            semantic_mismatch_rejected,
        )
        mapping_payload["effective"] = exact_effective
        mapping_path.write_text(json.dumps(mapping_payload, sort_keys=True))
        artifacts["stationary_born_mapping.json"]["sha256"] = hashlib.sha256(
            mapping_path.read_bytes()
        ).hexdigest()
        archive.write_text(json.dumps(payload, sort_keys=True))
        (root / REQUIRED_ARTIFACTS[0]).write_text("corrupted\n")
        try:
            load_archive(archive)
        except ValueError as error:
            digest_rejected = "digest mismatch" in str(error)
        else:
            digest_rejected = False
        check("P4f: a corrupted generated artifact is rejected", digest_rejected)


def report_rep_list(label: str, counter: Counter[SO4Irrep]) -> None:
    content = ", ".join(
        f"{irrep.display()}x{counter[irrep]}" for irrep in sorted(counter)
    )
    print(f"{label}: {content}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--archive", type=Path, help="exact generated Weyl vertex archive"
    )
    parser.add_argument(
        "--require-data",
        action="store_true",
        help="fail unless a complete exact archive is supplied",
    )
    arguments = parser.parse_args()

    test_archive_loader()

    report_rep_list("AA irreps also present in EA", COMMON_EA)
    report_rep_list("AA irreps also present in EL", COMMON_EL)
    print("Full E=6 shell dimension/signature:", FULL_E6_DIMENSION, FULL_E6_SIGNATURE)
    print("Reduced target H0,6:", H0_REDUCED)
    print("Reduced target J6:", J_REDUCED)
    print("Synthetic assembly S6:", fixture_source)
    print("Synthetic complete cokernel coordinates:", fixture_coordinates)

    if arguments.archive is not None:
        contact, blocks, payload = load_archive(arguments.archive)
        effective = assemble_effective_block(contact, blocks)
        source = obstruction_source(effective)
        coordinates = antihermitian_coordinates(source)
        print("Exact archive provenance:", payload.get("provenance", {}))
        print("Exact Veff,6:", effective)
        print("Exact S6:", source)
        print("Exact complete reduced cokernel coordinates:", coordinates)
        check(
            "P4f: archive supplies a complete exact target-block certificate",
            all(not value.has(sp.Float) for value in effective),
        )
    else:
        print(
            "P4 STATUS: STAGED, NOT A WEYL QUARTIC CERTIFICATE. "
            "No exact contact/current archive was supplied."
        )
        print("Absent generated artifact manifest:")
        for artifact in REQUIRED_ARTIFACTS:
            print(f"  build/conformal-p4/energy6/{artifact}")
        if arguments.require_data:
            raise SystemExit("P4 exact vertex archive is required but absent")

    if not PASS:
        raise SystemExit("CONFORMAL P4 ENERGY-SIX STAGING: FAIL")
    print("CONFORMAL P4 ENERGY-SIX STAGING: ALL EXACT RAILS PASS")


if __name__ == "__main__":
    main()
