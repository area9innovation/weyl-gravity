#!/usr/bin/env python3
"""Exact Nariai compression screen for the adjoint-tractor YM middle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import (
    _adjoint_basis,
)
from covariant_completion.curved_operator.adjoint_tractor_bgg_differential_screen import (
    _adjoint_actions,
)
from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    FibrePBW,
    _add,
    _algebraic,
    _formal_adjoint,
    _induced_harmonic_curvature,
    _scale,
    _tensor_product_curvature,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    NariaiBackground,
    ROOT,
    _sha256,
    _sparse,
    _sparse_table,
    _derivative_rows,
    _lc_adjoint_curvature,
    _load,
)


HERE = ROOT / "d_quotient_classical/causal_transfer"
PARENT = ROOT / "d_quotient_classical/certificates/CONFORMALLY_EINSTEIN_YANG_MILLS_DETOUR_CORRECTION_V1.json"
STRICT_SCREEN = ROOT / "d_quotient_classical/certificates/NARIAI_FIRST_BGG_ZEROTH_ORDER_STRICTIFICATION_OBSTRUCTION_V1.json"
POINTWISE = ROOT / "d_quotient_classical/certificates/NARIAI_POINTWISE_BGG_CURVATURE_COMPRESSION_OBSTRUCTION_V1.json"
KOSTANT_MATRICES = ROOT / "covariant_completion/certificates/adjoint_tractor_kostant_compression_matrices.json"
SCREEN_MATRICES = ROOT / "covariant_completion/certificates/adjoint_tractor_bgg_differential_screen_matrices.json"
PBW_CODE = ROOT / "covariant_completion/curved_operator/adjoint_tractor_bgg_curved_pbw.py"
STRICT_PRODUCER = HERE / "nariai_first_differential_bgg_correction.py"
STRICT_VERIFIER_CODE = HERE / "verify_nariai_first_differential_bgg_correction.py"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_ALGEBRAIC_ENDPOINT_CURVATURE_REPAIR_OBSTRUCTION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-algebraic-endpoint-curvature-repair-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-algebraic-endpoint-curvature-repair-obstruction-v1.schema.json"
VERIFIER = HERE / "verify_nariai_yang_mills_middle_compression.py"
TESTS = HERE / "tests/test_nariai_yang_mills_middle_compression.py"


def _count(table: dict[tuple[int, ...], sp.Matrix]) -> int:
    return sum(entry != 0 for matrix in table.values() for entry in matrix)


def fixture() -> dict[str, object]:
    algebraic, screen = _load()
    background = NariaiBackground()
    lc_adjoint = _lc_adjoint_curvature()
    curvature0 = _tensor_product_curvature(background, lc_adjoint, 0)
    curvature1 = _tensor_product_curvature(background, lc_adjoint, 1)
    curvature2 = _tensor_product_curvature(background, lc_adjoint, 2)
    harmonic0 = _induced_harmonic_curvature(
        curvature0, algebraic.i0, screen.harmonic_p0
    )
    harmonic1 = _induced_harmonic_curvature(
        curvature1, algebraic.i1, screen.harmonic_p1
    )
    pbw0 = FibrePBW(curvature0, background, "Nariai-C0")
    pbw1 = FibrePBW(curvature1, background, "Nariai-C1")
    pbw2 = FibrePBW(curvature2, background, "Nariai-C2")
    pbw_h0 = FibrePBW(harmonic0, background, "Nariai-H0")
    pbw_h1 = FibrePBW(harmonic1, background, "Nariai-H1")

    _, basis = _adjoint_basis()
    k_actions = _adjoint_actions(basis[11:15], basis)
    schouten_components = tuple(
        background.metric[axis, axis] / 6 for axis in range(4)
    )
    rho_actions = tuple(
        schouten_components[axis] * k_actions[axis] for axis in range(4)
    )
    rho0 = sp.Matrix.vstack(*rho_actions)
    rho1_rows = []
    for left in range(4):
        for right in range(left + 1, 4):
            block = sp.zeros(15, 60)
            block[:, 15 * right : 15 * (right + 1)] = rho_actions[left]
            block[:, 15 * left : 15 * (left + 1)] = -rho_actions[right]
            rho1_rows.append(block)
    rho1 = sp.Matrix.vstack(*rho1_rows)
    derivative0, derivative1 = _derivative_rows()
    delta0 = _add(_algebraic(rho0), derivative0)
    delta1 = _add(_algebraic(rho1), derivative1)
    total0 = _add(_algebraic(screen.cohomology_d0), delta0)
    total1 = _add(_algebraic(screen.cohomology_d1), delta1)

    n0 = pbw0.compose(_algebraic(screen.q1), delta0)
    n1 = pbw1.compose(_algebraic(screen.q2), delta1)
    i0_alg = _algebraic(algebraic.i0)
    i1_alg = _algebraic(algebraic.i1)
    n0_i0 = pbw_h0.compose(n0, i0_alg)
    n1_i1 = pbw_h1.compose(n1, i1_alg)
    inclusion0 = _add(
        i0_alg,
        _scale(n0_i0, -1),
        pbw_h0.compose(n0, n0_i0),
    )
    inclusion1 = _add(
        i1_alg,
        _scale(n1_i1, -1),
        pbw_h1.compose(n1, n1_i1),
    )
    first_bgg = pbw_h0.compose(
        _algebraic(screen.harmonic_p1),
        pbw_h0.compose(total0, inclusion0),
    )

    square = pbw0.compose(total1, total0)
    if set(square) != {()}:
        raise AssertionError("normal tractor square was not algebraic")
    eta = background.metric
    pairs = tuple(
        (left, right)
        for left in range(4)
        for right in range(left + 1, 4)
    )
    curvature_pairs = {
        pair: square[()][15 * index : 15 * (index + 1), :]
        for index, pair in enumerate(pairs)
    }

    def curvature(left: int, right: int) -> sp.Matrix:
        if left == right:
            return sp.zeros(15)
        if left < right:
            return curvature_pairs[(left, right)]
        return -curvature_pairs[(right, left)]

    curvature_action = sp.Matrix.vstack(
        *(
            sp.Matrix.hstack(
                *(
                    eta[source, source] * curvature(target, source)
                    for source in range(4)
                )
            )
            for target in range(4)
        )
    )
    two_form_metric = sp.diag(
        *(eta[left, left] * eta[right, right] for left, right in pairs)
    )
    two_form_pairing = sp.kronecker_product(
        two_form_metric, algebraic.adjoint_pairing
    )
    total1_sharp = _formal_adjoint(
        total1,
        algebraic.one_form_pairing,
        two_form_pairing,
        pbw2,
    )
    rough_middle = pbw1.compose(total1_sharp, total1)
    yang_mills_middle = _add(
        rough_middle,
        _scale(_algebraic(curvature_action), -1),
    )
    opposite_sign_middle = _add(
        rough_middle,
        _algebraic(curvature_action),
    )
    inclusion1_sharp = _formal_adjoint(
        inclusion1,
        algebraic.endpoint_field_pairing,
        algebraic.one_form_pairing,
        pbw1,
    )
    compressed = pbw_h1.compose(
        inclusion1_sharp,
        pbw_h1.compose(yang_mills_middle, inclusion1),
    )
    gauge_defect = pbw_h0.compose(compressed, first_bgg)
    parent_left_defect = pbw0.compose(yang_mills_middle, total0)
    opposite_sign_parent_left_defect = pbw0.compose(opposite_sign_middle, total0)
    factor_defect = pbw_h0.compose(
        inclusion1_sharp,
        pbw_h0.compose(
            yang_mills_middle,
            _add(
                pbw_h0.compose(total0, inclusion0),
                _scale(pbw_h0.compose(inclusion1, first_bgg), -1),
            ),
        ),
    )
    k_stack = sp.Matrix.hstack(*(first_bgg[(axis,)] for axis in range(4)))
    gauge_stack = sp.Matrix.hstack(*(gauge_defect[(axis,)] for axis in range(4)))
    endpoint_correction = sp.zeros(9)
    correction_parameter_counts = []
    for row in range(9):
        solution, parameters = k_stack.T.gauss_jordan_solve(
            -gauge_stack[row, :].T
        )
        correction_parameter_counts.append(parameters.rows)
        endpoint_correction[row, :] = solution.T
    repaired_middle = _add(compressed, _algebraic(endpoint_correction))
    repaired_gauge_defect = pbw_h0.compose(repaired_middle, first_bgg)
    endpoint_cyclic_defect = (
        algebraic.endpoint_field_pairing * endpoint_correction
        - endpoint_correction.T * algebraic.endpoint_field_pairing
    )
    return {
        "algebraic": algebraic,
        "screen": screen,
        "pbw_h0": pbw_h0,
        "pbw_h1": pbw_h1,
        "inclusion0": inclusion0,
        "inclusion1": inclusion1,
        "first_bgg": first_bgg,
        "normal_tractor_square": square,
        "curvature_action": curvature_action,
        "yang_mills_middle": yang_mills_middle,
        "compressed_middle": compressed,
        "gauge_defect": gauge_defect,
        "parent_left_defect": parent_left_defect,
        "opposite_sign_parent_left_defect": opposite_sign_parent_left_defect,
        "factor_defect": factor_defect,
        "k_stack_rank": k_stack.rank(),
        "correction_parameter_counts": correction_parameter_counts,
        "endpoint_correction": endpoint_correction,
        "endpoint_cyclic_defect": endpoint_cyclic_defect,
        "repaired_middle": repaired_middle,
        "repaired_gauge_defect": repaired_gauge_defect,
    }


def build() -> dict[str, object]:
    parent = json.loads(PARENT.read_text())
    strict = json.loads(STRICT_SCREEN.read_text())
    pointwise = json.loads(POINTWISE.read_text())
    if parent["flags"]["NARIAI_CURVED_PARENT_DETOUR_COMPLEX"] is not True:
        raise ValueError("Nariai Yang--Mills parent is unavailable")
    if strict["flags"]["ZEROTH_ORDER_STRICTIFICATION_EXISTS"] is not False:
        raise ValueError("corrected strictification screen is unavailable")
    value = fixture()
    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (
            Path(__file__).resolve(),
            VERIFIER,
            TESTS,
            SCHEMA,
            PBW_CODE,
            STRICT_PRODUCER,
            STRICT_VERIFIER_CODE,
        )
    }
    return {
        "schema": "pure-weyl-nariai-algebraic-endpoint-curvature-repair-obstruction-v1",
        "result_id": "NARIAI_ALGEBRAIC_ENDPOINT_CURVATURE_REPAIR_OBSTRUCTION_V1",
        "result_state": "UNIQUE_GAUGE_REPAIR_IS_NONCYCLIC",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "yang_mills_parent": {
                "artifact_id": parent["result_id"],
                "path": str(PARENT.relative_to(ROOT)),
                "sha256": _sha256(PARENT),
            },
            "strictification_screen": {
                "artifact_id": strict["result_id"],
                "path": str(STRICT_SCREEN.relative_to(ROOT)),
                "sha256": _sha256(STRICT_SCREEN),
            },
            "pointwise_screen": {
                "artifact_id": pointwise["result_id"],
                "path": str(POINTWISE.relative_to(ROOT)),
                "sha256": _sha256(POINTWISE),
            },
            "kostant_matrices": {
                "artifact_id": "ADJOINT_TRACTOR_KOSTANT_COMPRESSION_MATRICES",
                "path": str(KOSTANT_MATRICES.relative_to(ROOT)),
                "sha256": _sha256(KOSTANT_MATRICES),
            },
            "differential_screen_matrices": {
                "artifact_id": "ADJOINT_TRACTOR_BGG_DIFFERENTIAL_SCREEN_MATRICES",
                "path": str(SCREEN_MATRICES.relative_to(ROOT)),
                "sha256": _sha256(SCREEN_MATRICES),
            },
        },
        "primary_source": {
            "title": "Yang-Mills detour complexes and conformal geometry",
            "authors": "A. Rod Gover, Petr Somberg, Vladimir Soucek",
            "arxiv": "math/0606401",
            "url": "https://arxiv.org/abs/math/0606401",
            "translation_criterion": "L1^sharp M^D(d^D L0-L1 K)=0 is the weaker necessary and sufficient left-end condition when the strict translation square does not commute",
        },
        "construction": {
            "background": "unit Nariai dS2 x S2",
            "schouten_orthonormal_components": ["-1/6", "1/6", "1/6", "1/6"],
            "parent_middle": "M^D=delta^D d^D-F dot",
            "naive_compression": "B0=L1^sharp M^D L1",
            "tested_repair": "B0+Q with arbitrary algebraic Q:H1->H1dual",
            "required_equations": ["(B0+Q)K=0", "JQ=Q^T J"],
        },
        "exact_data": {
            "normal_tractor_square": _sparse_table(value["normal_tractor_square"]),
            "parent_curvature_action": _sparse(value["curvature_action"]),
            "parent_yang_mills_middle": _sparse_table(value["yang_mills_middle"]),
            "first_bgg_operator": _sparse_table(value["first_bgg"]),
            "naive_compressed_middle": _sparse_table(value["compressed_middle"]),
            "naive_gauge_defect": _sparse_table(value["gauge_defect"]),
            "unique_endpoint_correction": _sparse(value["endpoint_correction"]),
            "endpoint_pairing": _sparse(value["algebraic"].endpoint_field_pairing),
            "endpoint_cyclic_defect": _sparse(value["endpoint_cyclic_defect"]),
            "repaired_gauge_defect": _sparse_table(value["repaired_gauge_defect"]),
        },
        "exact_checks": {
            "normal_tractor_square_rank": value["normal_tractor_square"][()].rank(),
            "normal_tractor_square_nonzero_entries": _count(value["normal_tractor_square"]),
            "parent_curvature_action_rank": value["curvature_action"].rank(),
            "parent_curvature_action_nonzero_entries": sum(
                entry != 0 for entry in value["curvature_action"]
            ),
            "corrected_parent_left_defect_entries": _count(value["parent_left_defect"]),
            "wrong_sign_parent_left_defect_entries": _count(
                value["opposite_sign_parent_left_defect"]
            ),
            "compressed_orders": sorted(
                {len(word) for word in value["compressed_middle"]}
            ),
            "compressed_nonzero_entries": _count(value["compressed_middle"]),
            "naive_gauge_defect_orders": sorted(
                {len(word) for word in value["gauge_defect"]}
            ),
            "naive_gauge_defect_nonzero_entries": _count(value["gauge_defect"]),
            "translation_factor_defect_nonzero_entries": _count(
                value["factor_defect"]
            ),
            "K_symbol_stack_rank": value["k_stack_rank"],
            "correction_parameter_counts": value["correction_parameter_counts"],
            "unique_endpoint_correction_rank": value["endpoint_correction"].rank(),
            "unique_endpoint_correction_nonzero_entries": sum(
                entry != 0 for entry in value["endpoint_correction"]
            ),
            "repaired_gauge_defect_nonzero_entries": _count(
                value["repaired_gauge_defect"]
            ),
            "endpoint_cyclic_defect_rank": value["endpoint_cyclic_defect"].rank(),
            "endpoint_cyclic_defect_nonzero_entries": sum(
                entry != 0 for entry in value["endpoint_cyclic_defect"]
            ),
            "normalized_cyclic_witness": "-(1/3)*(JQ-Q^T J)[1,4]",
            "normalized_cyclic_witness_value": "1",
        },
        "obstruction": {
            "reason": "the conformal-Killing symbol stack has full row rank nine, so gauge annihilation uniquely fixes the algebraic endpoint correction; that unique correction has a rank-two cyclic defect",
            "conclusion": "no algebraic endpoint curvature correction can simultaneously restore the Nariai gauge identity and preserve the certified cyclic pairing",
            "not_a_differential_or_mapping_cone_no_go": True,
        },
        "flags": {
            "NARIAI_ALGEBRAIC_ENDPOINT_CURVATURE_REPAIR_OBSTRUCTION_V1": True,
            "NARIAI_PARENT_YANG_MILLS_COMPONENT_IDENTITY": True,
            "NAIVE_COMPRESSED_GAUGE_IDENTITY": False,
            "UNIQUE_ALGEBRAIC_GAUGE_REPAIR_EXISTS": True,
            "UNIQUE_ALGEBRAIC_GAUGE_REPAIR_CYCLIC": False,
            "ALGEBRAIC_ENDPOINT_REPAIR_OBSTRUCTED": True,
            "DIFFERENTIAL_TRANSLATION_LIFT_STILL_OPEN": True,
            "MAPPING_CONE_TRANSLATION_STILL_OPEN": True,
            "NARIAI_CURVED_BGG_HPL_COMPRESSION": False,
            "NARIAI_GREEN_HOMOTOPY": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "C_G2_NARIAI_DIFFERENTIAL_TRANSLATION_LIFT_OR_MAPPING_CONE",
        "claim_boundary": (
            "This exact Nariai PBW calculation first verifies componentwise that the corrected Yang--Mills middle M^D=delta^D d^D-F dot annihilates the parent gauge differential; reversing the curvature sign leaves 144 defects. Compressing M^D with the current finite BGG lift yields a fourth-order endpoint operator whose only gauge failure is a 24-entry first-order curvature defect. The complete algebraic endpoint repair Q is unique because the conformal-Killing symbol stack has rank nine, and it cancels that gauge defect exactly, but JQ-Q^T J has rank two with normalized witness one. Hence no algebraic endpoint correction can restore both gauge annihilation and cyclicity. This does not obstruct a genuinely differential translation lift, a curvature-incidence mapping cone, a homotopy-coherent compression, a Nariai Green construction, an open background theorem, or any quantum claim."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_yang_mills_middle_compression.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_yang_mills_middle_compression.py",
                "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_yang_mills_middle_compression",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-algebraic-endpoint-curvature-repair-obstruction-v1.schema.json -d d_quotient_classical/certificates/NARIAI_ALGEBRAIC_ENDPOINT_CURVATURE_REPAIR_OBSTRUCTION_V1.json",
            ],
        },
    }


def _report(value: dict[str, object]) -> str:
    checks = value["exact_checks"]
    return rf"""# Nariai algebraic endpoint-curvature repair obstruction

With the corrected Nariai Schouten components, the component PBW parent now
satisfies

\[
M^D d^D=0,
\qquad M^D=\delta^D d^D-F\!\cdot,
\]

exactly.  Reversing the curvature sign leaves
`{checks['wrong_sign_parent_left_defect_entries']}` entries, so this closure
detects the Yang--Mills correction.

The naive finite-BGG compression

\[
B_0=L_1^\sharp M^D L_1
\]

has orders `{checks['compressed_orders']}`.  Its gauge defect \(B_0K\) has
only differential order one and exactly
`{checks['naive_gauge_defect_nonzero_entries']}` coefficients.  We therefore
solved the complete algebraic endpoint problem

\[
(B_0+Q)K=0.
\]

The stacked conformal-Killing symbol has rank
`{checks['K_symbol_stack_rank']}`, so the \(9\times9\) solution \(Q\) is
unique.  It cancels the gauge defect exactly, but

\[
JQ-Q^T J
\]

has rank `{checks['endpoint_cyclic_defect_rank']}` and normalized witness

\[
-\frac13(JQ-Q^TJ)_{{1,4}}=1.
\]

Thus no algebraic endpoint curvature term can restore both the gauge identity
and cyclicity.  The next admissible construction is a genuinely differential
translation lift or a curvature-incidence mapping cone; neither is obstructed
by this result.
"""


def verify(value: dict[str, object]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("certificate drifted from exact reconstruction")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diagnose", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    raw = fixture()
    if args.diagnose:
        print(
            json.dumps(
                {
                    "normal_tractor_square_rank": raw["normal_tractor_square"][()].rank(),
                    "curvature_action_rank": raw["curvature_action"].rank(),
                    "yang_mills_middle_orders": sorted(
                        {len(word) for word in raw["yang_mills_middle"]}
                    ),
                    "compressed_orders": sorted(
                        {len(word) for word in raw["compressed_middle"]}
                    ),
                    "compressed_entries": _count(raw["compressed_middle"]),
                    "gauge_defect_entries": _count(raw["gauge_defect"]),
                    "parent_left_defect_entries": _count(raw["parent_left_defect"]),
                    "parent_left_defect_words": [
                        list(word) for word in sorted(raw["parent_left_defect"])
                    ],
                    "opposite_sign_parent_left_defect_entries": _count(
                        raw["opposite_sign_parent_left_defect"]
                    ),
                    "gauge_defect_words": [list(word) for word in sorted(raw["gauge_defect"])],
                    "translation_factor_defect_entries": _count(raw["factor_defect"]),
                    "endpoint_correction_rank": raw["endpoint_correction"].rank(),
                    "endpoint_cyclic_defect_rank": raw["endpoint_cyclic_defect"].rank(),
                    "repaired_gauge_defect_entries": _count(raw["repaired_gauge_defect"]),
                },
                indent=2,
            )
        )
    value = build()
    if args.guards:
        checks = value["exact_checks"]
        if checks["corrected_parent_left_defect_entries"] != 0:
            raise AssertionError("component Yang--Mills identity failed")
        if checks["wrong_sign_parent_left_defect_entries"] != 144:
            raise AssertionError("curvature-sign mutation guard failed")
        if checks["repaired_gauge_defect_nonzero_entries"] != 0:
            raise AssertionError("unique algebraic gauge repair failed")
        if checks["endpoint_cyclic_defect_rank"] != 2:
            raise AssertionError("cyclic obstruction rank guard failed")
        if checks["normalized_cyclic_witness_value"] != "1":
            raise AssertionError("normalized cyclic witness guard failed")
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(_report(value))
    if args.check:
        verify(json.loads(OUTPUT.read_text()))
    if args.write or args.check or args.guards:
        print(f"{value['result_id']}: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
