#!/usr/bin/env python3
"""Certify the classical trace obstruction in the tau-adic causal BV carrier.

The strict vacuum-cylinder endpoint contains the normalized Weyl chain

    sigma -> phi,              phi_star -> -sigma_star,

where ``delta g = g sigma``.  The Wess--Zumino convention instead has
``delta g = 2 omega g`` and ``delta tau = omega``.  Hence ``sigma=2 omega``
and the compensator extension of the scalar endpoint is

    sigma -> phi + tau/2,
    phi_star + tau_hat_star/2 -> -sigma_star.

The canonical dressed change isolates ``u=phi-2 tau`` and its cotangent
partner.  Both have zero unary differential because the classical Weyl
action has identically zero conformal-trace Hessian.  Compactly supported
``u`` is therefore a cycle outside the boundary space, so no advanced or
retarded homotopy can satisfy q Lambda + Lambda q = 1 on the complete
carrier.  This obstruction survives support-local cyclic isomorphisms,
contractible nonminimal/auxiliary additions, and SDR transfers.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT
    / "d_quotient_classical/certificates/"
    "TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1.json"
)
REPORT = (
    ROOT
    / "d_quotient_classical/reports/"
    "tau-adic-vacuum-cylinder-causal-bv-trace-obstruction.md"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "tau-adic-vacuum-cylinder-causal-bv-trace-obstruction-v1.schema.json"
)

DEPENDENCIES = {
    "strict_minimal_BV": (
        ROOT
        / "d_quotient_classical/certificates/"
        "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
    ),
    "WZ_minimal_cotangent_lift": (
        ROOT
        / "quantum-weyl/anomalies/certificates/"
        "WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json"
    ),
    "WZ_D_Cartan_contraction": (
        ROOT
        / "d_quotient_classical/certificates/"
        "WESS_ZUMINO_D_CARTAN_CONTRACTION_V1.json"
    ),
    "strict_386_Green_homotopy": (
        ROOT
        / "covariant_completion/certificates/"
        "curved_full_prolonged_green_homotopy_assembly.json"
    ),
    "strict_30_endpoint": (
        ROOT
        / "covariant_completion/certificates/"
        "curved_prolonged_metric_endpoint_complex.json"
    ),
    "strict_full_BV_inventory": (
        ROOT
        / "covariant_completion/certificates/"
        "curved_deformation_retract_status.json"
    ),
    "strict_action_and_gauge_normalization": (
        ROOT
        / "covariant_completion/certificates/"
        "curved_auxiliary_action_definition.json"
    ),
    "global_CKV_guard": (
        ROOT
        / "covariant_completion/certificates/"
        "auxiliary_full_bv_green_witness.json"
    ),
    "independent_causal_transfer_audit": (
        ROOT
        / "d_quotient_classical/certificates/"
        "GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1.json"
    ),
}

SOURCE_COMMITS = {
    "strict_minimal_BV": "0ebe60ff873bca387d6317ce8354f26bd03cc811",
    "WZ_minimal_cotangent_lift": "69f01998d255455aebe3bbcb0872ae82cc698621",
    "WZ_D_Cartan_contraction": "e15ec011688def11effb9c0b5ca3dc88fc28318b",
    "strict_386_Green_homotopy": "c5f811e120bc05198baa35a9b5491d8a46ae1295",
    "strict_30_endpoint": "6ebd72043d61dd3ca9a8cd571321424408762cd5",
    "strict_full_BV_inventory": "f4ff0e9c686de9e103155b995a8424231c40b424",
    "strict_action_and_gauge_normalization": "2803f3d6ba93c2922a912f276d5c890198045291",
    "global_CKV_guard": "c6e1319ab3d24cddf61bf69ad0f1deeeeedb2d9a",
    "independent_causal_transfer_audit": "59ef411a0d6cbdd079853333c224f57385cbe98f",
}

Matrix = list[list[Fraction]]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object dependency: {path}")
    return value


def _zero(rows: int, columns: int) -> Matrix:
    return [[Fraction() for _ in range(columns)] for _ in range(rows)]


def _identity(dimension: int) -> Matrix:
    value = _zero(dimension, dimension)
    for index in range(dimension):
        value[index][index] = Fraction(1)
    return value


def _transpose(value: Matrix) -> Matrix:
    return [list(row) for row in zip(*value)]


def _add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [a + b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            sum(
                (left[i][k] * right[k][j] for k in range(len(right))),
                Fraction(),
            )
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def _inverse(value: Matrix) -> Matrix:
    dimension = len(value)
    work = [row[:] + unit[:] for row, unit in zip(value, _identity(dimension))]
    for column in range(dimension):
        pivot = next(
            row
            for row in range(column, dimension)
            if work[row][column]
        )
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [item / scale for item in work[column]]
        for row in range(dimension):
            if row == column:
                continue
            scale = work[row][column]
            if scale:
                work[row] = [
                    item - scale * pivot_item
                    for item, pivot_item in zip(work[row], work[column])
                ]
    return [row[dimension:] for row in work]


def _rank(value: Matrix) -> int:
    work = [row[:] for row in value]
    rows = len(work)
    columns = len(work[0]) if work else 0
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [item / scale for item in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            scale = work[row][column]
            if scale:
                work[row] = [
                    item - scale * pivot_item
                    for item, pivot_item in zip(
                        work[row], work[pivot_row]
                    )
                ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def _fraction(value: Fraction) -> int | dict[str, int]:
    if value.denominator == 1:
        return value.numerator
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
    }


def _matrix_payload(value: Matrix) -> dict[str, Any]:
    canonical = {
        "row_count": len(value),
        "column_count": len(value[0]) if value else 0,
        "entries": [
            {
                "row": row,
                "column": column,
                "coefficient": _fraction(coefficient),
            }
            for row, values in enumerate(value)
            for column, coefficient in enumerate(values)
            if coefficient
        ],
    }
    return {**canonical, "sha256": _digest(canonical)}


def _column(dimension: int, index: int) -> Matrix:
    value = _zero(dimension, 1)
    value[index][0] = Fraction(1)
    return value


def _row(dimension: int, index: int) -> Matrix:
    value = _zero(1, dimension)
    value[0][index] = Fraction(1)
    return value


def _scalar_fixture() -> dict[str, Any]:
    # Original normalized basis:
    # (sigma, phi, tau, phi_star, tau_hat_star, sigma_star).
    q = _zero(6, 6)
    q[1][0] = Fraction(1)
    q[2][0] = Fraction(1, 2)
    q[5][3] = Fraction(-1)
    q[5][4] = Fraction(-1, 2)

    pairing = _zero(6, 6)
    for field, antifield in ((0, 5), (1, 3), (2, 4)):
        pairing[field][antifield] = Fraction(1)
        pairing[antifield][field] = Fraction(-1)

    # Columns are the dressed basis
    # (sigma, u=phi-2tau, v=phi, u_star, v_star, sigma_star)
    # expressed in the original basis.  The cotangent block is forced by
    # U^T Omega U=Omega.
    transform = _identity(6)
    transform[1][1] = Fraction(0)
    transform[1][2] = Fraction(1)
    transform[2][1] = Fraction(-1, 2)
    transform[2][2] = Fraction(1, 2)
    transform[3][3] = Fraction(1)
    transform[3][4] = Fraction(1)
    transform[4][3] = Fraction(-2)
    transform[4][4] = Fraction(0)
    inverse = _inverse(transform)
    q_dressed = _multiply(_multiply(inverse, q), transform)
    pairing_dressed = _multiply(
        _multiply(_transpose(transform), pairing), transform
    )

    u_cycle = _column(6, 1)
    u_star_cycle = _column(6, 3)
    u_dual = _row(6, 1)
    u_star_dual = _row(6, 3)

    if _multiply(q, q) != _zero(6, 6):
        raise AssertionError("extended scalar differential is not nilpotent")
    if _add(
        _multiply(_transpose(q), pairing),
        _multiply(pairing, q),
    ) != _zero(6, 6):
        raise AssertionError("extended scalar differential is not cyclic")
    if pairing_dressed != pairing:
        raise AssertionError("dressed scalar change is not canonical")
    if _rank(q) != 2:
        raise AssertionError("unexpected scalar differential rank")
    for cycle, witness in (
        (u_cycle, u_dual),
        (u_star_cycle, u_star_dual),
    ):
        if _multiply(q_dressed, cycle) != _zero(6, 1):
            raise AssertionError("declared dressed trace is not closed")
        if _multiply(witness, q_dressed) != _zero(1, 6):
            raise AssertionError("dual witness does not annihilate boundaries")
        if _multiply(witness, cycle) != [[Fraction(1)]]:
            raise AssertionError("dual witness is not normalized")

    return {
        "fixture_scope": "ZEROTH_ORDER_WEYL_TRACE_SUBQUOTIENT",
        "original_basis": [
            "sigma",
            "phi_trace",
            "tau",
            "phi_trace_star",
            "tau_hat_star",
            "sigma_star",
        ],
        "dressed_basis": [
            "sigma",
            "u=phi_trace-2tau",
            "v=phi_trace",
            "u_star",
            "v_star",
            "sigma_star",
        ],
        "degrees": [-1, 0, 0, 1, 1, 2],
        "Q_original": _matrix_payload(q),
        "odd_pairing_original": _matrix_payload(pairing),
        "canonical_change_old_from_dressed": _matrix_payload(transform),
        "canonical_change_inverse": _matrix_payload(inverse),
        "Q_dressed": _matrix_payload(q_dressed),
        "odd_pairing_dressed": _matrix_payload(pairing_dressed),
        "rank_Q": _rank(q),
        "subquotient_homology_dimension": 6 - 2 * _rank(q),
        "normalized_nonboundary_witnesses": [
            {
                "class_id": "DRESSED_CONFORMAL_TRACE_FIELD",
                "cycle": _matrix_payload(u_cycle),
                "dual": _matrix_payload(u_dual),
                "Q_cycle": "0",
                "dual_Q": "0",
                "dual_cycle": 1,
                "full_carrier_status": (
                    "PROMOTED_BY_COMPACT_SUPPORT_STOKES_WITNESS"
                ),
            },
            {
                "class_id": "DRESSED_CONFORMAL_TRACE_COTANGENT",
                "cycle": _matrix_payload(u_star_cycle),
                "dual": _matrix_payload(u_star_dual),
                "Q_cycle": "0",
                "dual_Q": "0",
                "dual_cycle": 1,
                "full_carrier_status": (
                    "SUBQUOTIENT_ONLY_DIFF_COMPANION_NOT_REMOVED"
                ),
            },
        ],
    }


def _validate_dependencies(values: dict[str, dict[str, Any]]) -> None:
    strict = values["strict_minimal_BV"]
    g_row = next(
        row
        for row in strict["differential"]["Q"]["rows"]
        if row["source_atom"] == "g"
    )
    if {
        (term["coefficient"], tuple(term["factors"]))
        for term in g_row["image"]["terms"]
    } != {(2, ("g", "omega")), (1, ("Lie_g",))}:
        raise ValueError("strict Weyl normalization drifted")

    wz = values["WZ_minimal_cotangent_lift"]
    if (
        wz["master_term"]["derived_rows"]["Q_tau"]
        != "L_xi tau + omega"
        or wz["dressed_cotangent_change"]["g_hat"]
        != "exp(-2 tau) g"
    ):
        raise ValueError("Wess-Zumino normalization drifted")

    action = values["strict_action_and_gauge_normalization"]
    if (
        action["source"]["gauge_transformations"]["Weyl"]
        != "delta g=g sigma, delta b=d sigma, delta phi=0"
    ):
        raise ValueError("causal endpoint Weyl normalization drifted")

    endpoint = values["strict_30_endpoint"]
    if endpoint["dimension"] != 30:
        raise ValueError("unexpected strict endpoint certificate")
    if endpoint["ordered_endpoint_ledger"][0]["dimension"] != 5:
        raise ValueError("strict endpoint ghost dimension drifted")

    green = values["strict_386_Green_homotopy"]
    if (
        green["dimension_ledger"]
        != {
            "algebraically_contracted": 356,
            "causal_endpoint": 30,
            "identity": "386=356+30",
            "prolonged": 386,
        }
        or green["causal_green_homotopy"] is not True
    ):
        raise ValueError("strict 386-row causal input drifted")

    inventory = values["strict_full_BV_inventory"]
    rows = inventory["factorized_actual_curved_Q"]["rows"]
    if not all(
        rows[key]
        for key in (
            "minimal_66_rows_included",
            "trace_Weyl_direct_summand_included",
            "diffeomorphism_nonminimal_direct_summand_included",
            "Weyl_nonminimal_direct_summand_included",
        )
    ):
        raise ValueError("strict full-BV inventory is incomplete")

    cartan = values["WZ_D_Cartan_contraction"]
    if (
        cartan["background"]["setting_id"]
        != "vacuum_cylinder_regular_Bach_chart"
        or cartan["generator"]["generator_id"] != "D_compact"
        or cartan["generator"]["Weyl_component"] != 0
    ):
        raise ValueError("same-background raw-D input drifted")
    ckv = values["global_CKV_guard"]
    if (
        ckv["global_ckv_guard"]
        != "no conformal-Killing projector enters a local operator; the "
        "fifteen non-compactly-supported smooth modes remain global "
        "cohomology and are reattached once through the certified residual "
        "BFV sector"
    ):
        raise ValueError("global conformal-Killing guard drifted")


def build() -> dict[str, Any]:
    values = {name: _load(path) for name, path in DEPENDENCIES.items()}
    _validate_dependencies(values)
    fixture = _scalar_fixture()

    dependencies = {
        name: {
            "artifact_id": (
                values[name].get("result_id")
                or values[name].get("schema")
                or path.stem
            ),
            "path": str(path.relative_to(ROOT)),
            "sha256": _sha256(path),
            "source_commit": SOURCE_COMMITS[name],
        }
        for name, path in DEPENDENCIES.items()
    }

    value = {
        "schema": (
            "pure-weyl-tau-adic-vacuum-cylinder-"
            "causal-bv-trace-obstruction-v1"
        ),
        "result_id": (
            "TAU_ADIC_VACUUM_CYLINDER_"
            "CAUSAL_BV_TRACE_OBSTRUCTION_V1"
        ),
        "result_state": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "background": {
            "setting_id": "vacuum_cylinder_regular_Bach_chart",
            "spacetime": "R_t x S3",
            "metric": "g_bar=-dt^2+dOmega_3^2",
            "boundaries": "closed S3 Cauchy surfaces; no timelike boundary",
            "linearization_point": "tau_bar=0",
        },
        "normalization_bridge": {
            "strict_local_BV": "Q g=L_xi g+2 omega g",
            "causal_endpoint": "delta g=g sigma",
            "compensator": "Q tau=L_xi tau+omega",
            "derived_identification": "sigma=2 omega",
            "derived_compensator_arrow": "sigma -> tau/2",
            "dressed_trace": "u=phi_trace-2 tau",
        },
        "imported_strict_carrier": {
            "full_rank": 386,
            "locally_contracted_rank": 356,
            "endpoint_rank": 30,
            "endpoint_block_ranks": [5, 10, 10, 5],
            "minimal_rank": 66,
            "minimal_and_nonminimal_inventory_complete": True,
            "advanced_retarded_homotopies_certified": True,
            "cyclic_adjoint_reversal_certified": True,
            "support_domains": [
                "Gamma_c",
                "Gamma_sc",
                "standard advanced/retarded Green domains",
            ],
        },
        "declared_extension_class": {
            "name": (
                "CANONICAL_TAU_ADIC_FINITE_DIFFERENTIAL_"
                "CAUSAL_BV_EXTENSIONS"
            ),
            "includes": [
                "the two required tau and tau_hat_star scalar rows",
                "the exact formal tau-adic canonical dressed change linearized at tau_bar=0",
                "finite-order support-local cyclic chain isomorphisms",
                "pointwise contractible nonminimal and generalized-auxiliary pairs",
                "finite differential cyclic SDR lifts and gauge-fermion canonical transforms",
            ],
            "fixed_data": [
                "the classical Weyl action and its trace-free Bach Hessian",
                "the single diagonal Weyl ghost sigma=2omega",
                "the frozen strict q0 outside the mandated compensator rows",
                "the nondegenerate canonical odd pairing and real structure",
            ],
            "excludes": [
                "a second independent Weyl gauge generator",
                "an order-zero R(g_hat)^2 or compensator kinetic term",
                "an hbar^-1 or Laurent-series propagator",
                "a quotient deleting arbitrary compactly supported dressed traces",
                "nonlocal harmonic or Fourier projectors",
            ],
            "completeness_reason": (
                "Every allowed operation is a chain isomorphism, addition of "
                "an acyclic summand, or a deformation retract, hence preserves "
                "the displayed scalar homology. Any repair must change one of "
                "the explicitly excluded gauge/action/domain data."
            ),
        },
        "scalar_trace_obstruction": {
            **fixture,
            "compact_support_witness": {
                "source": (
                    "f u with f in C_c^infinity(R x S3) and "
                    "integral(4f vol)=1, chosen outside the finite "
                    "fifteen-dimensional global CKV conformal-factor span"
                ),
                "support": "supp(f u)=supp(f), compact",
                "cycle_identity": (
                    "q0(f u)=Bach_linearized(f g_bar)=0"
                ),
                "cycle_reason": (
                    "exact conformal invariance of the classical Weyl action"
                ),
                "dual_functional": (
                    "lambda_u(h,tau,aux)=integral "
                    "tr_gbar(h-2tau g_bar) vol after the certified "
                    "endpoint projection kills contractible auxiliaries"
                ),
                "dual_functional_scope": (
                    "independently excludes compactly supported primitives; "
                    "the global CKV argument below excludes the one-sided "
                    "noncompact primitives relevant to Green homotopies"
                ),
                "diffeomorphism_boundary_identity": (
                    "lambda_u(L_xi g_bar)=2 integral div(xi) vol=0 "
                    "for compactly supported xi"
                ),
                "Weyl_boundary_identity": (
                    "lambda_u(g_bar sigma, sigma/2)=0"
                ),
                "lift_to_386": (
                    "compose lambda_u with the certified support-local "
                    "endpoint projection p_end"
                ),
                "global_CKV_nonmembership": (
                    "If q0 a=f u for any smooth primitive a, the tracefree "
                    "metric equation forces K_TF xi=0. The imported global "
                    "kernel has exactly fifteen CKV modes, so the trace "
                    "equation forces f into their finite conformal-factor "
                    "span, contrary to the declared choice of f."
                ),
                "nonboundary_identity": (
                    "f u is outside q0 of every smooth degree-minus-one "
                    "source; lambda_u additionally gives value one and "
                    "annihilates every compactly supported boundary"
                ),
                "consequence": (
                    "q0 Lambda f u+Lambda q0 f u=f u is impossible for "
                    "advanced, retarded or time-slice Lambda because "
                    "Lambda f u would be a forbidden smooth primitive"
                ),
            },
            "principal_symbol": {
                "dressed_trace_Hessian": "0 for every nonzero covector",
                "reason": (
                    "the classical Weyl action is conformally invariant and "
                    "the Bach Hessian has identically zero trace row/column"
                ),
                "Green_inverse_exists": False,
                "defect_is_finite_zero_mode": False,
                "defect_family": (
                    "C_c^infinity(R x S3), hence infinite-dimensional "
                    "and support-local"
                ),
            },
        },
        "carrier_classification": {
            "minimal_extension": "OBSTRUCTED",
            "nonminimal_gauge_fixed_extension": "OBSTRUCTED",
            "finite_auxiliary_cyclic_extension": "OBSTRUCTED",
            "past_compact_complete_carrier": "OBSTRUCTED",
            "future_compact_complete_carrier": "OBSTRUCTED",
            "time_slice_complete_carrier": "OBSTRUCTED",
            "finite_rank_zero_mode_removal": "NOT_APPLICABLE",
            "reason": (
                "the obstruction already has arbitrary compact support and "
                "nonzero homology before any wavefront or boundary issue"
            ),
        },
        "raw_D_and_pairing": {
            "raw_generator": "D_compact=partial_t",
            "Weyl_component": 0,
            "D_commutes_with_scalar_change": True,
            "Cartan_identity_imported": True,
            "odd_pairing_non_degenerate": True,
            "real_structure": (
                "componentwise real conjugation; every scalar matrix is rational"
            ),
            "pairing_on_obstruction": "<u,u_star>=1",
            "effect_on_obstruction": (
                "raw-D compatibility and nondegenerate pairing do not remove "
                "the two scalar homology classes"
            ),
        },
        "repair_boundary": {
            "smallest_algebraic_repairs": [
                (
                    "add the missing independent conformal gauge generator "
                    "and its BV cotangent completion"
                ),
                (
                    "add a classical dressed-trace kinetic term such as a "
                    "nonzero R(g_hat)^2 direction"
                ),
            ],
            "both_change_theory": True,
            "one_loop_WZ_term_is_not_Q0_kinetic_data": True,
            "hbar_adic_inverse_warning": (
                "an order-hbar trace Hessian has no inverse over Q[[hbar]] "
                "when its order-zero coefficient vanishes"
            ),
        },
        "dependencies": dependencies,
        "content_hashes": {
            "scalar_fixture_sha256": _digest(fixture),
            "dependency_manifest_sha256": _digest(dependencies),
        },
        "claim_flags": {
            "STRICT_386_ROW_CAUSAL_COMPLEX_IMPORTED": True,
            "TAU_ADIC_CANONICAL_SCALAR_EXTENSION_ASSEMBLED": True,
            "COMPLETE_DECLARED_FINITE_DIFFERENTIAL_CLASS_OBSTRUCTED": True,
            "FULL_TAU_ADIC_CLASSICAL_CAUSAL_BV_CARRIER": False,
            "FULL_TAU_ADIC_BRST_HADAMARD_KERNEL": False,
            "LORENTZIAN_QME_RESTORED": False,
            "PHYSICAL_POSITIVITY_CERTIFIED": False,
            "PARTICLE_INTERPRETATION_AUTHORIZED": False,
        },
        "next_gate": (
            "Choose explicitly whether to enlarge the gauge algebra by the "
            "missing conformal symmetry or change the classical action by a "
            "dressed-trace kinetic term; then construct and certify the new "
            "causal BV complex before any full tau-adic Hadamard attempt."
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL obstruction "
            "hash-imports the complete strict 386-row vacuum-cylinder causal "
            "BV complex and the formal Wess--Zumino cotangent/Cartan data. "
            "Their convention-correct scalar integration isolates the "
            "compactly supported dressed conformal trace u=phi_trace-2tau "
            "as a nonzero unary homology class. The cotangent trace is "
            "recorded only in the zeroth-order scalar subquotient because "
            "the full Diff companion acts on it. Therefore no "
            "advanced or retarded chain homotopy can satisfy "
            "q0 Lambda+Lambda q0=1 on the complete tau-adic carrier in the "
            "declared class. This is not a no-go for theories with an added "
            "gauge generator or a classical dressed-trace kinetic term, and "
            "it does not establish a Hadamard state, positivity, a "
            "Lorentzian QME, particles, scattering or unitarity."
        ),
    }
    return value


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value),
        key=lambda error: list(error.path),
    )
    if errors:
        raise ValueError(
            "schema failure: "
            + "; ".join(error.message for error in errors[:8])
        )


def _report(value: dict[str, Any]) -> str:
    return f"""# Tau-adic vacuum-cylinder causal BV trace obstruction

## Result

The formal Wess--Zumino compensator does **not** extend the certified strict
vacuum-cylinder causal complex to a complete classical causal BV carrier in
the declared finite differential class.

The convention bridge is forced:

```text
strict local BV:  delta g = 2 omega g
causal endpoint:  delta g = sigma g
compensator:      delta tau = omega
therefore:        sigma=2 omega,  delta tau=sigma/2.
```

On the normalized scalar endpoint, the extended unary differential is

```text
sigma -> phi_trace + tau/2,
phi_trace_star + tau_hat_star/2 -> -sigma_star.
```

The exact canonical dressed change isolates

```text
u = phi_trace - 2 tau
```

and its cotangent `u_star` in the zeroth-order Weyl/trace subquotient.  The
serialized six-dimensional matrix has rank
`{value["scalar_trace_obstruction"]["rank_Q"]}` and subquotient homology
dimension
`{value["scalar_trace_obstruction"]["subquotient_homology_dimension"]}`.
The cotangent row is not promoted to full-complex cohomology because the
diffeomorphism companion still acts on it.

The field class *does* promote.  Choose compactly supported `f` outside the
finite fifteen-dimensional span of global conformal-Killing factors, with
`integral(4 f vol)=1`, and define
`lambda_u(h,tau)=integral tr(h-2 tau g_bar) vol`.  Conformal invariance gives
`q0(f u)=0`; Stokes gives `lambda_u(L_xi g_bar)=0` for every compactly
supported diffeomorphism ghost; and the convention-correct Weyl arrow gives
`lambda_u(g_bar sigma,sigma/2)=0`.  Thus `lambda_u` kills the complete
compactly supported endpoint boundary space and evaluates to one on `f u`.
Composition with the certified endpoint projection lifts it to the 386-row
carrier.

The advanced/retarded primitive can be one-sided rather than compact, so the
decisive global step is separate.  If any smooth primitive mapped to `f u`,
its metric component would obey the conformal-Killing equation.  The imported
global kernel has exactly fifteen CKV modes, forcing `f` into their finite
conformal-factor span, contrary to its construction.

If an advanced or retarded homotopy satisfied
`q0 Lambda+Lambda q0=1`, that identity on `f u` would produce precisely the
forbidden smooth primitive.  This is algebraic before wavefront questions
arise.

## Complete declared class

The no-go covers the mandated compensator rows followed by finite-order
support-local cyclic changes of variables, contractible nonminimal or
generalized-auxiliary additions, finite differential cyclic SDR lifts, and
gauge-fermion canonical transforms.  These operations preserve homology.
The obstruction is an arbitrary compact-support family, not one of the
finite conformal-Killing zero modes.

There are two smallest structural repairs, and both change the theory:

1. add the missing independent conformal gauge generator and its BV
   cotangent completion; or
2. add an order-zero dressed-trace kinetic term, for example a nonzero
   `R(g_hat)^2` direction.

The one-loop Wess--Zumino term is order `hbar`; it cannot provide an inverse
for a vanishing order-zero trace Hessian over the formal `hbar`-adic ring.

## Scope

The strict 386-row advanced/retarded complex, its complete minimal and
nonminimal inventory, the formal tau-adic cotangent lift, and raw
`D_compact=partial_t` Cartan data are consumed by exact hashes.  Raw-D
compatibility and the nondegenerate odd pairing remain true, but do not
remove the scalar homology.

This result supplies no full tau-adic Hadamard kernel, positivity,
Lorentzian QME, particle, scattering or unitarity claim.

## Reproduction

```bash
python3 d_quotient_classical/compensator/tau_adic_vacuum_cylinder_causal_bv_trace_obstruction.py --check
python3 d_quotient_classical/compensator/verify_tau_adic_vacuum_cylinder_causal_bv_trace_obstruction.py
python3 -m unittest d_quotient_classical.compensator.tests.test_tau_adic_vacuum_cylinder_causal_bv_trace_obstruction
```

CLOSE-OUT: OBSTRUCTED — the exact first obstruction is certified for the complete declared finite differential carrier class
EVIDENCE: d_quotient_classical/certificates/TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1.json
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.emit:
        OUTPUT.write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        REPORT.write_text(_report(value), encoding="utf-8")
    elif args.check:
        stored = _load(OUTPUT)
        if stored != value:
            raise AssertionError("stored certificate differs from exact build")
        if REPORT.read_text(encoding="utf-8") != _report(value):
            raise AssertionError("stored report differs from exact build")
    else:
        print(json.dumps(value, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
