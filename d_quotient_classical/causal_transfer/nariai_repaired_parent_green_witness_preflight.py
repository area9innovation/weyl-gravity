#!/usr/bin/env python3
"""Principal-symbol preflight for the repaired Nariai metric witness.

The rank-310 mapping cone retracts locally to the metric Bach complex, not to
the bare Yang--Mills parent.  Consequently the parent Green homotopy cannot be
transported by simply reversing that SDR.  This module identifies the correct
leading metric companion before any lower-order Green claim is attempted.

The action Bach row is stored in evaluation-dual coordinates.  If ``G_H`` is
the trace-free tensor Gram matrix, ``K`` the conformal-Killing symbol and
``T_pr`` the universal third-order conformal companion, then the exact typed
identities are

    T_pr K = (zeta^2)^2 I_4,
    B_action + (1/2) G_H K T_pr = (1/2) (zeta^2)^2 G_H.

Thus the field block has scalar biwave symbol only after the certified fibre
identification.  The tempting parent-divergence candidate ``p0 delta^D L1``
has zero cubic principal symbol (it is a Bianchi operator) and is rejected.
No lower-order factorization or Green operator is claimed here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_differential_screen import (
    _adjoint_actions,
)
from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    FibrePBW,
    _add,
    _algebraic,
    _formal_adjoint,
    _tensor_product_curvature,
)
from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import (
    _adjoint_basis,
)
from covariant_completion.minimal_witness.principal_symbols import (
    MinimalWitnessPrincipalSymbols,
    TRACEFREE_COORDINATES,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    NariaiBackground,
    ROOT,
    _derivative_rows,
    _lc_adjoint_curvature,
    _sha256,
)
from d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair import (
    OUTPUT as REPAIR_CERTIFICATE,
    coefficient_kernel,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_parent_green_homotopy import (
    OUTPUT as PARENT_GREEN_CERTIFICATE,
)


HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_REPAIRED_PARENT_GREEN_WITNESS_PREFLIGHT_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-repaired-parent-green-witness-preflight.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-repaired-parent-green-witness-preflight-v1.schema.json"
VERIFIER = HERE / "verify_nariai_repaired_parent_green_witness_preflight.py"
TESTS = HERE / "tests/test_nariai_repaired_parent_green_witness_preflight.py"
MINIMAL_SOURCE = ROOT / "covariant_completion/minimal_witness/principal_symbols.py"
REPAIR_SOURCE = HERE / "nariai_parent_detour_mapping_cone_repair.py"
PARENT_GREEN_SOURCE = HERE / "nariai_yang_mills_parent_green_homotopy.py"
PBW_SOURCE = ROOT / "covariant_completion/curved_operator/adjoint_tractor_bgg_curved_pbw.py"


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode()).hexdigest()


def _sparse(matrix: sp.MatrixBase) -> dict[str, object]:
    return {
        "shape": list(matrix.shape),
        "entries": [
            [row, column, str(value)]
            for (row, column), value in sorted(matrix.todok().items())
        ],
        "sha256": _digest(matrix),
    }


def _principal(table: dict[tuple[int, ...], sp.Matrix], order: int, zeta: sp.Matrix) -> sp.Matrix:
    sample = next(iter(table.values()))
    value = sp.zeros(sample.rows, sample.cols)
    for word, matrix in table.items():
        if len(word) == order:
            value += sp.prod(zeta[axis] for axis in word) * matrix
    return value.applyfunc(sp.expand)


def _normal_tractor_differential(middle: dict[str, object]) -> dict[tuple[int, ...], sp.Matrix]:
    screen = middle["screen"]
    background = NariaiBackground()
    _, basis = _adjoint_basis()
    k_actions = _adjoint_actions(basis[11:15], basis)
    schouten = tuple(background.metric[axis, axis] / 6 for axis in range(4))
    rho0 = sp.Matrix.vstack(*(schouten[axis] * k_actions[axis] for axis in range(4)))
    derivative0, _ = _derivative_rows()
    return _add(
        _algebraic(screen.cohomology_d0),
        _add(_algebraic(rho0), derivative0),
    )


def fixture() -> dict[str, object]:
    coefficient = coefficient_kernel()
    automorphism = coefficient["automorphism"]
    middle = automorphism["middle"]
    endpoint = coefficient["endpoint"]
    algebraic = middle["algebraic"]

    universal = MinimalWitnessPrincipalSymbols.build()
    universal.verify()
    zeta = universal.covector
    zeta_square = universal.covector_square

    # H1 coordinates are the certified BGG harmonic coordinates.  C sends
    # them to the standard nine trace-free tensor coordinates.
    tensor_carrier = endpoint["tensor_carrier"]
    coordinate_map = sp.Matrix.vstack(
        *(tensor_carrier[4 * left + right, :] for left, right in TRACEFREE_COORDINATES)
    )
    if coordinate_map.det() == 0:
        raise AssertionError("trace-free coordinate map is singular")

    # The H0 harmonic coordinates are twice the contravariant vector
    # coordinates.  V sends them to the lower covector convention used by the
    # universal conformal-Killing symbol.
    ghost_to_covector = sp.diag(
        -sp.Rational(1, 2),
        sp.Rational(1, 2),
        sp.Rational(1, 2),
        sp.Rational(1, 2),
    )
    field_pairing = endpoint["tensor_gram"]

    k_symbol = (
        coordinate_map.inv()
        * universal.conformal_killing
        * ghost_to_covector
    ).applyfunc(sp.expand)
    t_symbol = (
        ghost_to_covector.inv()
        * universal.companion
        * coordinate_map
    ).applyfunc(sp.expand)
    bach_operator_symbol = (
        coordinate_map.inv() * universal.bach * coordinate_map
    ).applyfunc(sp.expand)
    actual_k_symbol = _principal(middle["first_bgg"], 1, zeta)
    actual_bach_covector_symbol = _principal(coefficient["b"], 4, zeta)

    ghost_biwave = (t_symbol * k_symbol).applyfunc(sp.expand)
    field_biwave = (
        actual_bach_covector_symbol
        + sp.Rational(1, 2) * field_pairing * k_symbol * t_symbol
    ).applyfunc(sp.expand)

    # Screen the superficially natural parent divergence.  Its cubic symbol
    # vanishes because delta^D L1 is the Bianchi operator, so it cannot supply
    # the fourth-order gauge completion.
    background = NariaiBackground()
    pbw_c1 = FibrePBW(
        _tensor_product_curvature(background, _lc_adjoint_curvature(), 1),
        background,
        "Nariai-C1-parent-divergence-preflight",
    )
    total0 = _normal_tractor_differential(middle)
    delta_d = _formal_adjoint(
        total0,
        algebraic.adjoint_pairing,
        algebraic.one_form_pairing,
        pbw_c1,
    )
    parent_candidate = {
        word: automorphism["projection0"] * matrix
        for word, matrix in middle["pbw_h1"].compose(
            delta_d, automorphism["corrected_l1"]
        ).items()
    }
    parent_candidate_symbol = _principal(parent_candidate, 3, zeta)

    expected_ghost = (zeta_square**2 * sp.eye(4)).applyfunc(sp.expand)
    expected_field = (
        sp.Rational(1, 2) * zeta_square**2 * field_pairing
    ).applyfunc(sp.expand)
    checks = {
        "coordinate_map_invertible": coordinate_map.det() != 0,
        "field_pairing_nondegenerate": field_pairing.det() != 0,
        "actual_K_matches_universal_K": actual_k_symbol == k_symbol,
        "action_Bach_is_evaluation_dual_operator": (
            actual_bach_covector_symbol
            == (field_pairing * bach_operator_symbol).applyfunc(sp.expand)
        ),
        "ghost_symbol_is_scalar_biwave": ghost_biwave == expected_ghost,
        "field_symbol_is_scalar_biwave_after_fibre_identification": field_biwave == expected_field,
        "parent_divergence_cubic_symbol_zero": parent_candidate_symbol == sp.zeros(4, 9),
    }
    if not all(checks.values()):
        raise AssertionError([name for name, value in checks.items() if not value])

    null_substitution = {zeta[0]: 1, zeta[1]: 1, zeta[2]: 0, zeta[3]: 0}
    return {
        "coordinate_map": coordinate_map,
        "ghost_to_covector": ghost_to_covector,
        "field_pairing": field_pairing,
        "k_symbol": k_symbol,
        "t_symbol": t_symbol,
        "bach_operator_symbol": bach_operator_symbol,
        "bach_covector_symbol": actual_bach_covector_symbol,
        "ghost_biwave": ghost_biwave,
        "field_biwave": field_biwave,
        "parent_candidate_symbol": parent_candidate_symbol,
        "zeta_square": zeta_square,
        "checks": checks,
        "null_checks": {
            "ghost_completed_symbol_rank": ghost_biwave.subs(null_substitution).rank(),
            "field_completed_symbol_rank": field_biwave.subs(null_substitution).rank(),
        },
    }


def build() -> dict[str, object]:
    repair = json.loads(REPAIR_CERTIFICATE.read_text())
    parent = json.loads(PARENT_GREEN_CERTIFICATE.read_text())
    if repair["flags"]["NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1"] is not True:
        raise ValueError("rank-310 repair unavailable")
    if parent["flags"]["NARIAI_PARENT_GREEN_HOMOTOPY"] is not True:
        raise ValueError("parent causal input unavailable")
    value = fixture()
    source_paths = (
        Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, MINIMAL_SOURCE,
        REPAIR_SOURCE, PARENT_GREEN_SOURCE, PBW_SOURCE,
    )
    dependencies = {
        "rank_310_repair": {
            "artifact_id": repair["result_id"],
            "path": str(REPAIR_CERTIFICATE.relative_to(ROOT)),
            "sha256": _sha256(REPAIR_CERTIFICATE),
        },
        "parent_green_homotopy": {
            "artifact_id": parent["result_id"],
            "path": str(PARENT_GREEN_CERTIFICATE.relative_to(ROOT)),
            "sha256": _sha256(PARENT_GREEN_CERTIFICATE),
        },
    }
    return {
        "schema": "pure-weyl-nariai-repaired-parent-green-witness-preflight-v1",
        "result_id": "NARIAI_REPAIRED_PARENT_GREEN_WITNESS_PREFLIGHT_V1",
        "result_state": "METRIC_AND_GHOST_SCALAR_BIWAVE_PRINCIPAL_SYMBOL_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": dependencies,
        "typed_coordinates": {
            "metric_coordinate_map": _sparse(value["coordinate_map"]),
            "ghost_to_covector_map": _sparse(value["ghost_to_covector"]),
            "metric_fibre_pairing": _sparse(value["field_pairing"]),
            "metric_pairing_determinant": str(value["field_pairing"].det()),
        },
        "principal_witness": {
            "K_sha256": _digest(value["k_symbol"]),
            "T_pr_sha256": _digest(value["t_symbol"]),
            "B_operator_sha256": _digest(value["bach_operator_symbol"]),
            "B_action_covector_sha256": _digest(value["bach_covector_symbol"]),
            "T_pr": "Box div-(1/3)d div div in Nariai H0/H1 coordinates",
            "ghost_identity": "T_pr K=(zeta^2)^2 I_4",
            "field_identity": "B_action+(1/2)G_H K T_pr=(1/2)(zeta^2)^2 G_H",
            "fibre_identified_field_identity": "G_H^{-1}D_M=(1/2)(zeta^2)^2 I_9",
        },
        "rejected_candidate": {
            "operator": "p0 delta^D L1_corrected",
            "nominal_order": 3,
            "cubic_symbol_sha256": _digest(value["parent_candidate_symbol"]),
            "cubic_symbol_rank": 0,
            "reason": "the parent divergence is a Bianchi operator and has no cubic gauge-companion symbol",
            "scope": "rejection of this canonical candidate only; not a no-go for lower-order completions of T_pr",
        },
        "exact_checks": {**value["checks"], **value["null_checks"]},
        "flags": {
            "NARIAI_REPAIRED_PARENT_GREEN_WITNESS_PREFLIGHT_V1": True,
            "NARIAI_METRIC_SCALAR_BIWAVE_PRINCIPAL_SYMBOL": True,
            "NARIAI_GHOST_SCALAR_BIWAVE_PRINCIPAL_SYMBOL": True,
            "NARIAI_PARENT_DIVERGENCE_COMPANION_REJECTED": True,
            "NARIAI_REPAIRED_310_GREEN_HOMOTOPY": False,
            "NARIAI_METRIC_GREEN_HOMOTOPY": False,
            "NARIAI_LOWER_ORDER_FACTOR_COMPLETION": False,
        },
        "claim_boundary": {
            "statement": "The correctly typed universal third-order companion gives scalar metric and ghost biwave principal symbols for the Nariai Bach complex after the action fibre identification.",
            "not_claimed": [
                "a coefficient-complete lower-order companion on Nariai",
                "factorization into normally hyperbolic operators",
                "advanced or retarded Green operators for the metric block",
                "the repaired rank-310 all-row Green homotopy",
                "an open background class",
            ],
        },
        "next_gate": "C_G2_NARIAI_LOWER_ORDER_BIWAVE_FACTOR_COMPLETION",
        "source_manifest": {str(path.relative_to(ROOT)): _sha256(path) for path in source_paths},
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_repaired_parent_green_witness_preflight.py --check --guards",
            "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_repaired_parent_green_witness_preflight.py",
            "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_repaired_parent_green_witness_preflight",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-repaired-parent-green-witness-preflight-v1.schema.json -d d_quotient_classical/certificates/NARIAI_REPAIRED_PARENT_GREEN_WITNESS_PREFLIGHT_V1.json",
        ],
    }


def _write_report(value: dict[str, object]) -> None:
    REPORT.write_text("""# Nariai repaired-parent Green-witness preflight

The rank-310 local SDR retracts to the metric Bach complex, so the certified
Yang--Mills parent homotopy cannot simply be transported backwards.  The
first necessary metric calculation nevertheless closes exactly.

Let `G_H` be the trace-free tensor Gram matrix, `K` the metric gauge symbol,
and

```text
T_pr = Box div - (1/3) d div div.
```

In the certified Nariai harmonic coordinates,

```text
T_pr K = (zeta^2)^2 I_4,
B_action + (1/2) G_H K T_pr = (1/2) (zeta^2)^2 G_H.
```

Hence the ghost block is a scalar biwave and the field block becomes a scalar
biwave after applying the action fibre identification `G_H^{-1}`.  The raw
Bach row must not be compared directly with an identity matrix because it is
stored in evaluation-dual equation coordinates.

The tempting parent candidate `p0 delta^D L1` is rejected: its cubic
principal symbol is exactly zero.  It is a Bianchi operator, not a gauge
companion.

This is a principal-symbol theorem only.  The next gate must derive the
complete Nariai lower-order companion and factor, triangularize, or otherwise
construct Green operators for the resulting fourth-order blocks.
""")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    if args.check:
        existing = json.loads(OUTPUT.read_text())
        if existing != value:
            raise SystemExit("certificate drift")
    else:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        _write_report(value)
    if args.guards:
        if value["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"] is not False:
            raise SystemExit("rank-310 Green flag overpromoted")
    print(value["result_id"])


if __name__ == "__main__":
    main()
