#!/usr/bin/env python3
"""Coefficient-complete metric biwave Green homotopy on unit Nariai.

The principal preflight fixes the universal third-order companion.  On the
Einstein Nariai background the complete parallel-Ricci correction has only one
independent first-order channel.  Exact coefficient comparison fixes it to

    T = Box div - (1/3) d div div + (1/3) div.

The ghost and fibre-identified metric witness blocks then factor exactly into
commuting normally hyperbolic factors.  This supplies advanced and retarded
Green homotopies for the complete four-row metric Bach complex.  Transfer to
the repaired rank-310 cone is deliberately a separate downstream gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    _add,
    _algebraic,
    _formal_adjoint,
    _scale,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    ROOT,
    _sha256,
    _sparse,
    _sparse_table,
)
from d_quotient_classical.causal_transfer.nariai_metric_bach_cyclic_bv_complex import (
    OUTPUT as METRIC_COMPLEX_CERTIFICATE,
    kernel as metric_kernel,
)
from d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair import (
    coefficient_kernel,
    _entry_count,
)
from d_quotient_classical.causal_transfer.nariai_repaired_parent_green_witness_preflight import (
    OUTPUT as PREFLIGHT_CERTIFICATE,
)


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-metric-biwave-green-homotopy.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-metric-biwave-green-homotopy-v1.schema.json"
VERIFIER = HERE / "verify_nariai_metric_biwave_green_homotopy.py"
TESTS = HERE / "tests/test_nariai_metric_biwave_green_homotopy.py"
PREFLIGHT_SOURCE = HERE / "nariai_repaired_parent_green_witness_preflight.py"
METRIC_SOURCE = HERE / "nariai_metric_bach_cyclic_bv_complex.py"
REPAIR_SOURCE = HERE / "nariai_parent_detour_mapping_cone_repair.py"
PBW_SOURCE = ROOT / "covariant_completion/curved_operator/adjoint_tractor_bgg_curved_pbw.py"


Table = dict[tuple[int, ...], sp.Matrix]


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode()).hexdigest()


def _basic_operators(coefficient: dict[str, object]) -> dict[str, Table]:
    automorphism = coefficient["automorphism"]
    middle = automorphism["middle"]
    endpoint = coefficient["endpoint"]
    metric = middle["pbw_h0"].background.metric
    carrier = endpoint["tensor_carrier"]
    ghost_to_covector = sp.diag(
        -sp.Rational(1, 2), sp.Rational(1, 2),
        sp.Rational(1, 2), sp.Rational(1, 2),
    )
    covector_to_ghost = ghost_to_covector.inv()

    divergence: Table = {}
    scalar_divergence: Table = {}
    gradient: Table = {}
    for axis in range(4):
        coefficient_matrix = sp.zeros(4, 9)
        for output in range(4):
            coefficient_matrix[output, :] = (
                metric[axis, axis] * carrier[4 * axis + output, :]
            )
        divergence[(axis,)] = covector_to_ghost * coefficient_matrix

        scalar = sp.zeros(1, 4)
        scalar[0, :] = metric[axis, axis] * ghost_to_covector[axis, :]
        scalar_divergence[(axis,)] = scalar

        grad = sp.zeros(4, 1)
        grad[:, 0] = covector_to_ghost[:, axis]
        gradient[(axis,)] = grad

    box_ghost = {
        (axis, axis): metric[axis, axis] * sp.eye(4) for axis in range(4)
    }
    box_metric = {
        (axis, axis): metric[axis, axis] * sp.eye(9) for axis in range(4)
    }
    return {
        "divergence": divergence,
        "scalar_divergence": scalar_divergence,
        "gradient": gradient,
        "box_ghost": box_ghost,
        "box_metric": box_metric,
    }


def fixture() -> dict[str, object]:
    coefficient = coefficient_kernel()
    automorphism = coefficient["automorphism"]
    middle = automorphism["middle"]
    endpoint = coefficient["endpoint"]
    algebraic = middle["algebraic"]
    basic = _basic_operators(coefficient)
    pbw_h0 = middle["pbw_h0"]
    pbw_h1 = middle["pbw_h1"]
    divergence = basic["divergence"]
    box_ghost = basic["box_ghost"]
    box_metric = basic["box_metric"]

    grad_div = pbw_h0.compose(
        basic["gradient"], basic["scalar_divergence"]
    )
    principal_companion = _add(
        pbw_h1.compose(box_ghost, divergence),
        _scale(pbw_h1.compose(grad_div, divergence), -sp.Rational(1, 3)),
    )

    # Solve the only Einstein-background first-order coefficient by requiring
    # the ghost block to be a polynomial in the rough wave.
    tau, wave_coefficient, constant_coefficient = sp.symbols("tau s p")
    companion_family = _add(principal_companion, _scale(divergence, tau))
    gauge_generator = middle["first_bgg"]
    ghost_family = pbw_h0.compose(companion_family, gauge_generator)
    box_ghost_squared = pbw_h0.compose(box_ghost, box_ghost)
    family_defect = _add(
        ghost_family,
        _scale(box_ghost_squared, -1),
        _scale(box_ghost, -wave_coefficient),
        _algebraic(-constant_coefficient * sp.eye(4)),
    )
    equations = [
        value for matrix in family_defect.values() for value in matrix if value != 0
    ]
    linear, rhs = sp.linear_eq_to_matrix(
        equations, (tau, wave_coefficient, constant_coefficient)
    )
    augmented = linear.row_join(rhs)
    solution_set = sp.linsolve(
        (linear, rhs), (tau, wave_coefficient, constant_coefficient)
    )
    expected_solution = (sp.Rational(1, 3), sp.Rational(4, 3), sp.Rational(1, 3))
    if solution_set != sp.FiniteSet(expected_solution):
        raise AssertionError(f"lower-order companion solution drifted: {solution_set}")

    companion = _add(principal_companion, _scale(divergence, expected_solution[0]))
    ghost_block = pbw_h0.compose(companion, gauge_generator)
    ghost_factor_left = _add(box_ghost, _algebraic(sp.eye(4)))
    ghost_factor_right = _add(
        box_ghost, _algebraic(sp.Rational(1, 3) * sp.eye(4))
    )
    ghost_factorization = pbw_h0.compose(ghost_factor_left, ghost_factor_right)

    field_gram = endpoint["tensor_gram"]
    bach_operator = {
        word: field_gram.inv() * matrix for word, matrix in coefficient["b"].items()
    }
    k_t = pbw_h1.compose(gauge_generator, companion)
    metric_block = _add(bach_operator, _scale(k_t, sp.Rational(1, 2)))
    box_metric_squared = pbw_h1.compose(box_metric, box_metric)
    metric_remainder = _add(
        metric_block, _scale(box_metric_squared, -sp.Rational(1, 2))
    )
    second_order_matrix = (
        metric_remainder[(0, 0)] / middle["pbw_h0"].background.metric[0, 0]
    ).applyfunc(sp.expand)
    zeroth_order_matrix = metric_remainder[()].applyfunc(sp.expand)
    if any(
        metric_remainder.get((axis, axis), sp.zeros(9))
        != middle["pbw_h0"].background.metric[axis, axis] * second_order_matrix
        for axis in range(4)
    ):
        raise AssertionError("metric remainder is not a rough-wave polynomial")
    if any(
        len(word) == 2 and word[0] != word[1]
        for word in metric_remainder
    ) or any(len(word) not in (0, 2) for word in metric_remainder):
        raise AssertionError("metric remainder retained a non-Laplace channel")

    eigenvalues = (
        -sp.Rational(7, 3), sp.Rational(5, 3), -sp.Rational(1, 3)
    )
    identity = sp.eye(9)
    projectors = []
    for eigenvalue in eigenvalues:
        projector = identity
        denominator = sp.Integer(1)
        for other in eigenvalues:
            if other != eigenvalue:
                projector = projector * (second_order_matrix - other * identity)
                denominator *= eigenvalue - other
        projectors.append((projector / denominator).applyfunc(sp.expand))
    factor_a_matrix = (
        -2 * projectors[0] + 2 * projectors[1]
    ).applyfunc(sp.expand)
    factor_b_matrix = (
        -sp.Rational(8, 3) * projectors[0]
        + sp.Rational(4, 3) * projectors[1]
        - sp.Rational(2, 3) * projectors[2]
    ).applyfunc(sp.expand)
    factor_a = _add(box_metric, _algebraic(factor_a_matrix))
    factor_b = _add(box_metric, _algebraic(factor_b_matrix))
    metric_factorization = _scale(pbw_h1.compose(factor_a, factor_b), sp.Rational(1, 2))

    ghost_pairing = algebraic.endpoint_ghost_pairing
    checks = {
        "lower_order_linear_rank": linear.rank(),
        "lower_order_augmented_rank": augmented.rank(),
        "lower_order_solution_unique": linear.rank() == augmented.rank() == 3,
        "ghost_factorization_defect_entries": _entry_count(
            _add(ghost_block, _scale(ghost_factorization, -1))
        ),
        "metric_factorization_defect_entries": _entry_count(
            _add(metric_block, _scale(metric_factorization, -1))
        ),
        "metric_factor_order_commutator_entries": _entry_count(
            _add(
                pbw_h1.compose(factor_a, factor_b),
                _scale(pbw_h1.compose(factor_b, factor_a), -1),
            )
        ),
        "factor_a_formal_adjoint_defect_entries": _entry_count(
            _add(
                _formal_adjoint(factor_a, field_gram, field_gram, pbw_h1),
                _scale(factor_a, -1),
            )
        ),
        "factor_b_formal_adjoint_defect_entries": _entry_count(
            _add(
                _formal_adjoint(factor_b, field_gram, field_gram, pbw_h1),
                _scale(factor_b, -1),
            )
        ),
        "ghost_factor_left_adjoint_defect_entries": _entry_count(
            _add(
                _formal_adjoint(
                    ghost_factor_left, ghost_pairing, ghost_pairing, pbw_h0
                ),
                _scale(ghost_factor_left, -1),
            )
        ),
        "ghost_factor_right_adjoint_defect_entries": _entry_count(
            _add(
                _formal_adjoint(
                    ghost_factor_right, ghost_pairing, ghost_pairing, pbw_h0
                ),
                _scale(ghost_factor_right, -1),
            )
        ),
        "projector_ranks": [projector.rank() for projector in projectors],
        "projector_sum_defect_rank": (
            sum(projectors, sp.zeros(9)) - identity
        ).rank(),
        "factor_a_pairing_defect_rank": (
            field_gram * factor_a_matrix - factor_a_matrix.T * field_gram
        ).rank(),
        "factor_b_pairing_defect_rank": (
            field_gram * factor_b_matrix - factor_b_matrix.T * field_gram
        ).rank(),
    }
    zero_names = (
        "ghost_factorization_defect_entries",
        "metric_factorization_defect_entries",
        "metric_factor_order_commutator_entries",
        "factor_a_formal_adjoint_defect_entries",
        "factor_b_formal_adjoint_defect_entries",
        "ghost_factor_left_adjoint_defect_entries",
        "ghost_factor_right_adjoint_defect_entries",
        "projector_sum_defect_rank",
        "factor_a_pairing_defect_rank",
        "factor_b_pairing_defect_rank",
    )
    if not checks["lower_order_solution_unique"] or any(checks[name] for name in zero_names):
        raise AssertionError("Nariai biwave factorization did not close")
    if checks["projector_ranks"] != [4, 1, 4]:
        raise AssertionError("Nariai curvature-channel ranks drifted")

    metric = metric_kernel()
    return {
        "coefficient": coefficient,
        "metric": metric,
        "companion": companion,
        "ghost_block": ghost_block,
        "metric_block": metric_block,
        "ghost_factors": (ghost_factor_left, ghost_factor_right),
        "metric_factors": (factor_a, factor_b),
        "field_gram": field_gram,
        "second_order_matrix": second_order_matrix,
        "zeroth_order_matrix": zeroth_order_matrix,
        "projectors": projectors,
        "factor_a_matrix": factor_a_matrix,
        "factor_b_matrix": factor_b_matrix,
        "checks": checks,
    }


def build() -> dict[str, object]:
    preflight = json.loads(PREFLIGHT_CERTIFICATE.read_text())
    metric_complex = json.loads(METRIC_COMPLEX_CERTIFICATE.read_text())
    if preflight["flags"]["NARIAI_METRIC_SCALAR_BIWAVE_PRINCIPAL_SYMBOL"] is not True:
        raise ValueError("metric principal preflight unavailable")
    if metric_complex["flags"]["NARIAI_METRIC_BACH_ENDPOINT_CHAIN_COMPLEX"] is not True:
        raise ValueError("metric Bach complex unavailable")
    value = fixture()
    source_paths = (
        Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, PREFLIGHT_SOURCE,
        METRIC_SOURCE, REPAIR_SOURCE, PBW_SOURCE,
    )
    dependencies = {
        "principal_preflight": {
            "artifact_id": preflight["result_id"],
            "path": str(PREFLIGHT_CERTIFICATE.relative_to(ROOT)),
            "sha256": _sha256(PREFLIGHT_CERTIFICATE),
        },
        "metric_bach_complex": {
            "artifact_id": metric_complex["result_id"],
            "path": str(METRIC_COMPLEX_CERTIFICATE.relative_to(ROOT)),
            "sha256": _sha256(METRIC_COMPLEX_CERTIFICATE),
        },
    }
    return {
        "schema": "pure-weyl-nariai-metric-biwave-green-homotopy-v1",
        "result_id": "NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1",
        "result_state": "FOUR_ROW_METRIC_CAUSAL_GREEN_HOMOTOPY_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": dependencies,
        "companion": {
            "formula": "T=Box div-(1/3)d div div+(1/3)div",
            "coefficient_table": _sparse_table(value["companion"]),
            "orders": sorted({len(word) for word in value["companion"]}),
            "normalization_in_witness": "W_M_to_G=T/2",
            "middle_fibre_map": "W_E_to_M=G_H^{-1}",
            "upper_block": "W_I_to_E=T^sharp/2 forced by the action pairing",
        },
        "unique_lower_order_solve": {
            "unknowns": ["tau", "wave_coefficient", "constant_coefficient"],
            "solution": ["1/3", "4/3", "1/3"],
            "coefficient_rank": value["checks"]["lower_order_linear_rank"],
            "augmented_rank": value["checks"]["lower_order_augmented_rank"],
            "unique": value["checks"]["lower_order_solution_unique"],
        },
        "ghost_factorization": {
            "identity": "T K=(Box+1)(Box+1/3) I_4",
            "witness_block": "D_G=(1/2)(Box+1)(Box+1/3) I_4",
            "factor_shifts": ["1", "1/3"],
            "factor_tables": [_sparse_table(table) for table in value["ghost_factors"]],
        },
        "metric_factorization": {
            "identity": "G_H^{-1}B_action+(1/2)K T=(1/2)(Box I_9+A)(Box I_9+B)",
            "factor_a_matrix": _sparse(value["factor_a_matrix"]),
            "factor_b_matrix": _sparse(value["factor_b_matrix"]),
            "factor_a_eigenvalues": {"-2": 4, "0": 4, "2": 1},
            "factor_b_eigenvalues": {"-8/3": 4, "-2/3": 4, "4/3": 1},
            "curvature_channel_projectors": [_sparse(projector) for projector in value["projectors"]],
            "curvature_channel_ranks": value["checks"]["projector_ranks"],
            "factors_commute": True,
            "factors_are_G_H_formally_self_adjoint": True,
        },
        "metric_witness": {
            "complex": "H0 --K--> H1 --B_action--> H1dual --Ksharp--> H0dual",
            "backward_blocks": ["T/2", "G_H^{-1}", "Tsharp/2"],
            "degree_blocks": [
                "(1/2)(Box+1)(Box+1/3) on H0",
                "(1/2)(Box I+A)(Box I+B) on H1",
                "formal dual of the H1 block on H1dual",
                "formal dual of the H0 block on H0dual",
            ],
            "QW_plus_WQ": "degreewise factored Green-hyperbolic operator P_metric",
            "upper_row_authority": "invariant formal adjunction in the action pairing; the known generic post-normal-order PBW adjoint is not used as coefficient authority",
        },
        "causal_theorem": {
            "background": "global unit Nariai R x (S1 x S2)",
            "factor_type": "second-order normally hyperbolic with parallel zeroth-order endomorphisms",
            "factor_Green_operators": "unique advanced and retarded inverses for every primal and formal-dual factor",
            "product_Green_operators": "same-sided reverse-order compositions, multiplied by 2 for the witness normalization",
            "support": "finite same-sided composition preserves supp G_+/- f subset J^+/- supp f",
            "chain_commutation": "QP_metric=P_metric Q and uniqueness imply QG_metric,+/-=G_metric,+/-Q",
            "homotopy": "Lambda_metric,+/-=W_metric G_metric,+/-",
            "homotopy_identity": "Q Lambda_metric,+/-+Lambda_metric,+/- Q=1",
            "adjoint_reversal": "complementary-degree reversal follows from the cyclic witness and primal/formal-dual Green uniqueness",
        },
        "exact_checks": value["checks"],
        "flags": {
            "NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1": True,
            "NARIAI_LOWER_ORDER_FACTOR_COMPLETION": True,
            "NARIAI_METRIC_GREEN_HOMOTOPY": True,
            "NARIAI_METRIC_CAUSAL_SUPPORT": True,
            "NARIAI_METRIC_ADJOINT_REVERSAL": True,
            "NARIAI_REPAIRED_310_GREEN_HOMOTOPY": False,
            "GENERIC_PBW_DUAL_COEFFICIENT_REPLAY_USED_AS_AUTHORITY": False,
            "OPEN_BACKGROUND_CLASS": False,
            "HADAMARD_STATE": False,
        },
        "claim_boundary": {
            "statement": "The complete four-row metric Bach BV complex on global unit Nariai has advanced and retarded Green homotopies obtained from exact commuting normally hyperbolic ghost and metric factors.",
            "not_claimed": [
                "the all-row rank-310 lifted homotopy",
                "uniformity on an open conformally Einstein family",
                "Hadamard wavefront-set control",
                "nonlinear stability",
                "a quantum state or quantum master equation",
            ],
        },
        "next_gate": "C_G2_NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER",
        "source_manifest": {str(path.relative_to(ROOT)): _sha256(path) for path in source_paths},
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_metric_biwave_green_homotopy.py --check --guards",
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_metric_biwave_green_homotopy.py",
            "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_metric_biwave_green_homotopy",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-metric-biwave-green-homotopy-v1.schema.json -d d_quotient_classical/certificates/NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json",
        ],
    }


def _write_report(value: dict[str, object]) -> None:
    REPORT.write_text("""# Nariai metric biwave Green homotopy

The unique Einstein-background completion of the third-order companion is

```text
T = Box div - (1/3) d div div + (1/3) div.
```

It produces the exact ghost factorization

```text
T K = (Box+1)(Box+1/3) I_4.
```

After the action fibre identification, the metric block factors as

```text
G_H^{-1} B_action + (1/2) K T
  = (1/2)(Box I_9+A)(Box I_9+B).
```

The parallel curvature endomorphisms `A` and `B` commute, are formally
self-adjoint for `G_H`, and have channel multiplicities `4+1+4`.  Every
factor is normally hyperbolic.  Same-sided compositions of their unique
advanced or retarded Green operators therefore give Green operators for all
four witness degrees, including the formal-dual blocks.

With backward witness `(T/2,G_H^{-1},Tsharp/2)`, uniqueness gives chain
commutation and

```text
Q Lambda_metric,+/- + Lambda_metric,+/- Q = 1.
```

The rank-310 lift remains a separate, now purely homological, gate.
""")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    if args.check:
        if json.loads(OUTPUT.read_text()) != value:
            raise SystemExit("certificate drift")
    else:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        _write_report(value)
    if args.guards and value["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"] is not False:
        raise SystemExit("rank-310 Green flag overpromoted")
    print(value["result_id"])


if __name__ == "__main__":
    main()
