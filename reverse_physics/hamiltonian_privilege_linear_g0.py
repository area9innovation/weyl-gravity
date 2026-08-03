"""Rail A: the G0 necessity separation for Hamiltonian privilege.

Reverse-physics question (Carcassi--Aidala shape).  Deterministic and reversible
evolution is standardly said to conserve information, and Hamiltonian structure
is standardly said to follow.  Which assumption actually does the work?

This certificate answers that on the smallest honest carrier -- linear vector
fields ``dx/dt = A x`` on a 2n-dimensional state space with a declared
degree-of-freedom split -- by computing three exact dimensions:

    sp(2n, Q)          Hamiltonian generators          (Omega A symmetric)
    marginal(2n, Q)    per-DOF area preserving         (tr A_kk = 0 for each k)
    sl(2n, Q)          globally volume preserving      (tr A = 0)

and the codimensions of the inclusion chain sp <= marginal <= sl.

The generator computes each dimension as ``(2n)^2 - rank(constraints)`` by
Gauss--Jordan elimination over Q.  The independent verifier reaches the same
three numbers from explicit spanning bases and a fraction-free integer
elimination; agreement across the two rails is the evidence, not the rerun.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.hamiltonian_privilege_linear_g0 --check
    PYTHONPATH=. python3 -m reverse_physics.hamiltonian_privilege_linear_g0 --write
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from reverse_physics import carriers
from reverse_physics.exact_linalg import (
    add,
    determinant,
    identity,
    is_zero,
    matmul,
    rank_fraction,
    render,
    subtract,
    transpose,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_HAMILTONIAN_PRIVILEGE_LINEAR_G0_V1.json"
SCHEMA = ROOT / "reverse_physics/schema/reverse-physics-hamiltonian-privilege-linear-g0-v1.schema.json"

RESULT_ID = "REVERSE_PHYSICS_HAMILTONIAN_PRIVILEGE_LINEAR_G0_V1"
SCHEMA_NAME = "reverse-physics-hamiltonian-privilege-linear-g0-v1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


# --- constraint families ---------------------------------------------------
#
# Every condition is a linear constraint on the (2n)^2 entries of A, flattened
# row-major so that entry (i, j) sits at coordinate 2n*i + j.


def _zero_row(size: int) -> list[Fraction]:
    return [Fraction(0)] * (size * size)


def liouville_constraints(dof: int) -> list[list[Fraction]]:
    """Global volume preservation: tr A = 0."""
    size = 2 * dof
    row = _zero_row(size)
    for i in range(size):
        row[size * i + i] = Fraction(1)
    return [row]


def marginal_constraints(dof: int) -> list[list[Fraction]]:
    """Per-degree-of-freedom area preservation: tr A_kk = 0 for every k."""
    size = 2 * dof
    rows = []
    for k in range(dof):
        row = _zero_row(size)
        row[size * (2 * k) + (2 * k)] = Fraction(1)
        row[size * (2 * k + 1) + (2 * k + 1)] = Fraction(1)
        rows.append(row)
    return rows


def symplectic_constraints(dof: int) -> list[list[Fraction]]:
    """Hamiltonian generator: Omega A is symmetric.

    (Omega A)[i][j] = sum_k Omega[i][k] A[k][j], so antisymmetrising gives one
    linear row per unordered pair i < j.
    """
    size = 2 * dof
    omega = carriers.symplectic_form(dof)
    rows = []
    for i in range(size):
        for j in range(i + 1, size):
            row = _zero_row(size)
            for k in range(size):
                row[size * k + j] += omega[i][k]
                row[size * k + i] -= omega[j][k]
            rows.append(row)
    return rows


CONSTRAINTS = {
    "liouville": liouville_constraints,
    "marginal": marginal_constraints,
    "symplectic": symplectic_constraints,
}


def solution_dimension(name: str, dof: int) -> int:
    size = (2 * dof) ** 2
    return size - rank_fraction(CONSTRAINTS[name](dof))


def implies(outer: str, inner: str, dof: int) -> bool:
    """True when every solution of ``inner`` also solves ``outer``.

    Adding the outer constraints to the inner ones must not cut the solution
    space, i.e. must not raise the rank.
    """
    inner_rows = CONSTRAINTS[inner](dof)
    combined = inner_rows + CONSTRAINTS[outer](dof)
    return rank_fraction(combined) == rank_fraction(inner_rows)


# --- witness predicates ----------------------------------------------------


def is_liouville(matrix, dof: int) -> bool:
    return sum((matrix[i][i] for i in range(2 * dof)), Fraction(0)) == 0


def is_marginal(matrix, dof: int) -> bool:
    return all(
        matrix[2 * k][2 * k] + matrix[2 * k + 1][2 * k + 1] == 0 for k in range(dof)
    )


def is_hamiltonian(matrix, dof: int) -> bool:
    product = matmul(carriers.symplectic_form(dof), matrix)
    return is_zero(subtract(product, transpose(product)))


def finite_flow_defect(matrix, dof: int) -> dict[str, object]:
    """Strengthen the infinitesimal statement to the finite-time flow map.

    The marginal witness is nilpotent (A^2 = 0), so exp(A) = I + A exactly and
    the whole check stays rational -- no exponential series, no truncation, no
    floating point.
    """
    square = matmul(matrix, matrix)
    require(is_zero(square), "finite-flow shortcut assumed A^2 = 0")
    flow = add(identity(2 * dof), matrix)
    omega = carriers.symplectic_form(dof)
    defect = subtract(matmul(transpose(flow), matmul(omega, flow)), omega)
    return {
        "flow_map_at_t_equals_one": render(flow),
        "nilpotent_A_squared_is_zero": True,
        "determinant_of_flow_map": str(determinant(flow)),
        "volume_preserving": determinant(flow) == 1,
        "symplectic_defect_M_transpose_Omega_M_minus_Omega": render(defect),
        "flow_map_is_symplectic": is_zero(defect),
    }


# --- assembly --------------------------------------------------------------


def build() -> dict[str, object]:
    dimensions = {}
    for dof in (1, 2):
        size = (2 * dof) ** 2
        dim_sp = solution_dimension("symplectic", dof)
        dim_marginal = solution_dimension("marginal", dof)
        dim_liouville = solution_dimension("liouville", dof)

        # The inclusion chain is checked, not assumed.
        require(implies("liouville", "symplectic", dof), f"sp <= sl failed at n={dof}")
        require(implies("marginal", "symplectic", dof), f"sp <= marginal failed at n={dof}")
        require(implies("liouville", "marginal", dof), f"marginal <= sl failed at n={dof}")

        dimensions[f"dof_{dof}"] = {
            "ambient_gl_dimension": size,
            "hamiltonian_sp_dimension": dim_sp,
            "marginal_dimension": dim_marginal,
            "liouville_sl_dimension": dim_liouville,
            "codimension_sp_in_liouville": dim_liouville - dim_sp,
            "codimension_sp_in_marginal": dim_marginal - dim_sp,
            "codimension_marginal_in_liouville": dim_liouville - dim_marginal,
            "liouville_implies_hamiltonian": dim_liouville == dim_sp,
            "marginal_implies_hamiltonian": dim_marginal == dim_sp,
        }

    one, two = dimensions["dof_1"], dimensions["dof_2"]
    require(one["liouville_implies_hamiltonian"], "n=1 degeneracy lost")
    require(not two["liouville_implies_hamiltonian"], "n=2 separation lost")
    require(not two["marginal_implies_hamiltonian"], "n=2 marginal separation lost")

    witnesses = {}
    for name, factory in sorted(carriers.WITNESSES.items()):
        matrix = factory()
        witnesses[name] = {
            "matrix": render(matrix),
            "satisfies_liouville": is_liouville(matrix, 2),
            "satisfies_marginal": is_marginal(matrix, 2),
            "satisfies_hamiltonian": is_hamiltonian(matrix, 2),
        }

    # The separating witnesses must actually separate, and the control must
    # actually be Hamiltonian, or the predicates are vacuous.
    marginal_witness = witnesses["marginal_not_hamiltonian"]
    require(marginal_witness["satisfies_marginal"], "marginal witness is not marginal")
    require(marginal_witness["satisfies_liouville"], "marginal witness is not Liouville")
    require(not marginal_witness["satisfies_hamiltonian"], "marginal witness is Hamiltonian")

    global_witness = witnesses["global_not_marginal"]
    require(global_witness["satisfies_liouville"], "global witness is not Liouville")
    require(not global_witness["satisfies_marginal"], "global witness is marginal")

    control = witnesses["hamiltonian_control"]
    require(control["satisfies_hamiltonian"], "control is not Hamiltonian")
    require(control["satisfies_marginal"] and control["satisfies_liouville"], "control broke the chain")

    flow = finite_flow_defect(carriers.witness_marginal_not_hamiltonian(), dof=2)
    require(flow["volume_preserving"], "finite flow is not volume preserving")
    require(not flow["flow_map_is_symplectic"], "finite flow turned out symplectic")

    return {
        "schema": SCHEMA_NAME,
        "result_id": RESULT_ID,
        "result_state": "MARGINAL_INFORMATION_CONSERVATION_IS_NECESSARY_BUT_NOT_SUFFICIENT_ON_THE_LINEAR_CARRIER",
        "generality_level": "G0_LINEAR_VECTOR_FIELDS_ONE_AND_TWO_DEGREES_OF_FREEDOM",
        "lifecycle_ladder": "reverse-physics-v0",
        "lifecycle_state": "SEPARATION_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "assumption_tags": {
            "consumed": [
                carriers.RP_DETERMINISTIC,
                carriers.RP_REVERSIBLE,
                carriers.RP_LINEAR_CARRIER,
            ],
            "under_test": [
                carriers.RP_INFORMATION_CONSERVING,
                carriers.RP_MARGINAL_INFORMATION_CONSERVING,
            ],
            "gloss": carriers.ASSUMPTION_GLOSS,
            "namespace_note": "RP-* names physical postulates and is disjoint from the programme's computational-regime tags (LOCAL-ALGEBRAIC / EUCLIDEAN-SPECTRAL / REDUCED-MODE / LORENTZIAN-CAUSAL). The two namespaces are never mixed in one field.",
        },
        "scope": {
            "carrier": "linear vector fields dx/dt = A x with A in gl(2n, Q)",
            "state_space": "R^{2n} with coordinates (q_1, p_1, ..., q_n, p_n)",
            "degrees_of_freedom": [1, 2],
            "symplectic_form": "Omega = diag(J, ..., J), J = [[0, 1], [-1, 0]]",
            "dof_split": "fixed and part of the carrier; the marginal condition is only statable relative to it",
            "arithmetic": "exact rational (fractions.Fraction); no floating point anywhere",
        },
        "assumptions": [
            "The degree-of-freedom split is given, fixed, and not itself derived.",
            "Determinism and reversibility are imposed at the level of the carrier: the evolution is the one-parameter group exp(tA), which is deterministic and invertible for every A.",
            "'Conserves information' is read as preservation of Liouville measure, globally for RP-INFORMATION-CONSERVING and per degree of freedom for RP-MARGINAL-INFORMATION-CONSERVING.",
            "Hamiltonian means: A generates a flow preserving the fixed Omega above, equivalently A = Omega S for a symmetric S.",
        ],
        "theorem": {
            "inclusion_chain": "sp(2n, Q) <= marginal(2n, Q) <= sl(2n, Q), each inclusion checked by rank, not assumed",
            "one_dof_degeneracy": "At n = 1 all three spaces have dimension 3: global volume preservation is equivalent to Hamiltonian structure, so the assumption under test is INVISIBLE on a one-degree-of-freedom carrier.",
            "two_dof_separation": "At n = 2 the dimensions are 10 (sp), 14 (marginal), 15 (sl). Global information conservation leaves a 5-dimensional gap to Hamiltonian structure.",
            "necessity": "Marginal information conservation is NECESSARY: it is implied by Hamiltonian structure (sp <= marginal) and it strictly cuts the Liouville space (15 -> 14), so it is not a vacuous strengthening.",
            "insufficiency": "Marginal information conservation is NOT SUFFICIENT: a 4-dimensional gap survives at n = 2, exhibited by the explicit witness marginal_not_hamiltonian.",
            "residual_obstruction": "The surviving 4 dimensions are exactly the inter-DOF block condition J A_12 = -(A_21)^T J. It couples distinct degrees of freedom, so NO condition formulated per degree of freedom can close the gap.",
            "minimal_separating_carrier": "n = 2 is the smallest number of degrees of freedom at which the separation exists at all.",
        },
        "dimensions": dimensions,
        "witnesses": witnesses,
        "finite_flow_strengthening": flow,
        "exact_checks": {
            "all_dimensions_from_exact_rank": True,
            "inclusion_chain_checked_by_rank": True,
            "no_floating_point": True,
            "witness_predicates_evaluated_directly": True,
            "control_witness_is_hamiltonian": True,
            "finite_flow_defect_exact": True,
        },
        "claim_flags": {
            "MARGINAL_CONDITION_NECESSARY": True,
            "MARGINAL_CONDITION_SUFFICIENT": False,
            "SEPARATION_EXHIBITED_BY_EXPLICIT_WITNESS": True,
            "NONLINEAR_CARRIER_COVERED": False,
            "INFINITE_DIMENSIONAL_CARRIER_COVERED": False,
            "GENERAL_N_DOF_COVERED": False,
            "CARCASSI_AIDALA_DERIVATION_REPRODUCED": False,
            "EQUIVALENCE_OVER_A_BASE_THEORY_ESTABLISHED": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": (
            "This is a complete exact separation on the declared G0 carrier: linear vector fields on R^2 and R^4 "
            "with a fixed degree-of-freedom split and a fixed symplectic form. It establishes that global "
            "information conservation does not entail Hamiltonian structure once there are two degrees of freedom, "
            "that per-degree-of-freedom information conservation is a necessary and non-vacuous strengthening, and "
            "that it is still not sufficient, with the residual obstruction located exactly in the inter-DOF block."
        ),
        "does_not_establish": [
            "any statement about nonlinear vector fields, where the dimension count has no direct analogue",
            "any statement at n >= 3 or at general n; only n = 1 and n = 2 were computed",
            "any statement about infinite-dimensional or field-theoretic state spaces",
            "that Carcassi--Aidala's own derivation is correct or incorrect; this certificate does not reproduce their argument, it tests one candidate assumption on one carrier",
            "an equivalence over a base theory in the reverse-mathematics sense; there is no reversal here, only implication and separation",
            "that the degree-of-freedom split is itself physically forced; it is an input to the carrier",
            "any quantum, causal, or field-theoretic claim of any kind",
        ],
        "next_gate": "REVERSE_PHYSICS_HAMILTONIAN_PRIVILEGE_GENERAL_N_DOF: prove dim sp(2n) = n(2n+1), dim marginal = 4n^2 - n, dim sl = 4n^2 - 1 for all n, so that the codimension 2n^2 - 2n survives as a general-n statement rather than an n = 2 datum.",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): sha(path)
                for path in sorted(
                    [
                        Path(__file__),
                        ROOT / "reverse_physics/carriers.py",
                        ROOT / "reverse_physics/exact_linalg.py",
                        ROOT / "reverse_physics/verify_hamiltonian_privilege_linear_g0.py",
                        ROOT / "reverse_physics/tests/test_hamiltonian_privilege_linear_g0.py",
                        SCHEMA,
                    ]
                )
            },
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "independent_rail": "reverse_physics/verify_hamiltonian_privilege_linear_g0.py",
            "independence_argument": (
                "Rail A derives each dimension as ambient minus the rank of the defining constraint rows, "
                "eliminated over Q. Rail B derives the same dimensions as the rank of an explicit spanning set "
                "built from an independent parametrisation (S -> Omega S for sp; explicit generators for marginal "
                "and sl), eliminated fraction-free over Z by Bareiss. The two rails share only the declarations "
                "in carriers.py, which compute nothing."
            ),
        },
        "verification_commands": [
            "PYTHONPATH=. python3 -m reverse_physics.hamiltonian_privilege_linear_g0 --check",
            "PYTHONPATH=. python3 -m reverse_physics.verify_hamiltonian_privilege_linear_g0",
            "PYTHONPATH=. python3 -m unittest reverse_physics.tests.test_hamiltonian_privilege_linear_g0 -v",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = build()

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        pass
    else:
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(payload)

    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered, encoding="utf-8")
    elif not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
        raise AssertionError(f"{RESULT_ID} certificate is stale")
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
