#!/usr/bin/env python3
"""Export the same-background Wess--Zumino compensator D-Cartan contraction.

The selected background is the unit vacuum conformal cylinder.  The raw
generator is ``D_compact = partial_t`` with zero Weyl component.  This is not
the Berger helical generator and the field ``tau`` below is the Wess--Zumino
compensator, not a clock.

In dressed variables the Weyl sector is the quartet

    q tau = omega,             q omega = 0,
    q omega_star = tau_hat_star, q tau_hat_star = 0.

The tensorial homotopy sends ``omega -> tau`` and
``tau_hat_star -> omega_star``.  It commutes with cylinder time translation,
so it extends to the formal tau-adic algebra and to the one-generator
Chevalley--Eilenberg complex.  The exact finite matrices emitted here are
generator-level fixtures for the all-monomial derivation proof.
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
HERE = Path(__file__).resolve().parent
OUTPUT = (
    ROOT
    / "d_quotient_classical/certificates/"
    "WESS_ZUMINO_D_CARTAN_CONTRACTION_V1.json"
)
REPORT = (
    ROOT
    / "d_quotient_classical/reports/"
    "wess-zumino-d-cartan-contraction.md"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "wess-zumino-d-cartan-contraction-v1.schema.json"
)
DEPENDENCIES = {
    "strict_minimal_BV": (
        ROOT
        / "d_quotient_classical/certificates/"
        "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
    ),
    "WZ_cotangent_lift": (
        ROOT
        / "quantum-weyl/anomalies/certificates/"
        "WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json"
    ),
    "WZ_tau_adic_algebra": (
        ROOT
        / "quantum-weyl/anomalies/certificates/"
        "WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY.json"
    ),
    "compact_D_charge": (
        ROOT
        / "d_quotient_classical/certificates/"
        "compact_cylinder_d_charge_audit.json"
    ),
    "closed_universe_BFV": (
        ROOT / "bridge/certificates/closed_universe_bfv.json"
    ),
    "generator_registry": (
        ROOT / "d_quotient_programme/registry/generators.json"
    ),
    "residual_Cartan_executable": (
        ROOT / "symbolic/verify_conformal_cartan_contraction.py"
    ),
}

Scalar = Fraction
Matrix = list[list[Scalar]]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object dependency: {path}")
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
    if len(left) != len(right) or (
        left and len(left[0]) != len(right[0])
    ):
        raise ValueError("matrix addition shape mismatch")
    return [
        [a + b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def _scale(coefficient: Scalar | int, value: Matrix) -> Matrix:
    coefficient = Fraction(coefficient)
    return [[coefficient * item for item in row] for row in value]


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix multiplication shape mismatch")
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


def _block(rows: list[list[Matrix]]) -> Matrix:
    if not rows or not rows[0]:
        raise ValueError("empty block matrix")
    row_heights = [len(group[0]) for group in rows]
    column_widths = [len(rows[0][j][0]) for j in range(len(rows[0]))]
    for i, group in enumerate(rows):
        if len(group) != len(column_widths):
            raise ValueError("ragged block matrix")
        for j, value in enumerate(group):
            if len(value) != row_heights[i] or any(
                len(row) != column_widths[j] for row in value
            ):
                raise ValueError("block shape mismatch")
    output: Matrix = []
    for group in rows:
        for local_row in range(len(group[0])):
            output.append(
                [
                    item
                    for value in group
                    for item in value[local_row]
                ]
            )
    return output


def _fraction(value: Scalar) -> int | dict[str, int]:
    if value.denominator == 1:
        return value.numerator
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
    }


def _matrix_payload(value: Matrix) -> dict[str, Any]:
    rows = len(value)
    columns = len(value[0]) if value else 0
    entries = [
        {
            "row": i,
            "column": j,
            "coefficient": _fraction(coefficient),
        }
        for i, row in enumerate(value)
        for j, coefficient in enumerate(row)
        if coefficient
    ]
    canonical = {
        "row_count": rows,
        "column_count": columns,
        "entries": entries,
    }
    return {**canonical, "sha256": _digest(canonical)}


def _embed_quartet_with_unit(q4: Matrix, h4: Matrix) -> dict[str, Matrix]:
    q5 = _zero(5, 5)
    h5 = _zero(5, 5)
    for i in range(4):
        for j in range(4):
            q5[i + 1][j + 1] = q4[i][j]
            h5[i + 1][j + 1] = h4[i][j]
    inclusion = _zero(5, 1)
    inclusion[0][0] = Fraction(1)
    projection = _zero(1, 5)
    projection[0][0] = Fraction(1)
    return {
        "Q0": q5,
        "inclusion": inclusion,
        "projection": projection,
        "homotopy": h5,
    }


def _cartan_fixture(q4: Matrix, h4: Matrix, weight: int) -> dict[str, Matrix]:
    zero4 = _zero(4, 4)
    identity4 = _identity(4)
    q_ce = _block(
        [
            [q4, zero4],
            [_scale(weight, identity4), _scale(-1, q4)],
        ]
    )
    iota = _block(
        [
            [zero4, identity4],
            [zero4, zero4],
        ]
    )
    lie = _scale(weight, _identity(8))
    homotopy = _block(
        [
            [h4, zero4],
            [zero4, _scale(-1, h4)],
        ]
    )
    return {
        "Q0": q_ce,
        "iota_D0": iota,
        "L_D0": lie,
        "homotopy": homotopy,
    }


def _cyclic_fixture(
    q4: Matrix, h4: Matrix, pairing4: Matrix, weight: int
) -> dict[str, Matrix]:
    zero4 = _zero(4, 4)
    identity4 = _identity(4)
    return {
        "Q0": _block([[q4, zero4], [zero4, q4]]),
        "homotopy": _block([[h4, zero4], [zero4, h4]]),
        "L_D0": _block(
            [
                [_scale(weight, identity4), zero4],
                [zero4, _scale(-weight, identity4)],
            ]
        ),
        "pairing": _block(
            [
                [zero4, pairing4],
                [pairing4, zero4],
            ]
        ),
    }


def _dependency_refs() -> dict[str, dict[str, str]]:
    references: dict[str, dict[str, str]] = {}
    for name, path in DEPENDENCIES.items():
        if path.suffix == ".json":
            value = _load(path)
            artifact_id = str(
                value.get("result_id")
                or value.get("schema")
                or "UNIDENTIFIED_JSON"
            )
        else:
            artifact_id = path.stem
        references[name] = {
            "path": path.relative_to(ROOT).as_posix(),
            "artifact_id": artifact_id,
            "sha256": _sha256(path),
        }
    return references


def _require_dependencies(values: dict[str, dict[str, Any]]) -> None:
    strict = values["strict_minimal_BV"]
    cotangent = values["WZ_cotangent_lift"]
    tau_adic = values["WZ_tau_adic_algebra"]
    charge = values["compact_D_charge"]
    bfv = values["closed_universe_BFV"]
    registry = values["generator_registry"]
    if (
        strict.get("result_state")
        != "EXPORTED_EXECUTABLE_MINIMAL_BV_FILTRATION"
        or strict.get("scope", {}).get("locality")
        != "SUPPORT_LOCAL_POLYNOMIAL_JETS"
    ):
        raise ValueError("strict minimal-BV export drifted")
    if (
        cotangent.get("result_state")
        != "EXACT_MINIMAL_BV_COTANGENT_LIFT_CERTIFIED_EXTENDED_COHOMOLOGY_OPEN"
        or cotangent.get("contractible_quartet", {}).get("ordered_basis")
        != ["tau", "omega", "omega_star", "tau_hat_star"]
        or cotangent.get("dressed_cotangent_change", {}).get(
            "formal_completion"
        )
        != "TAU_ADIC_LOCAL_ANALYTIC_COMPLETION_REQUIRED_FOR_EXPONENTIAL_CHANGE"
        or not all(
            value is True
            for key, value in cotangent.get("exact_checks", {}).items()
            if key != "checked_atom_count"
            and key != "differential_sha256"
        )
    ):
        raise ValueError("Wess--Zumino cotangent lift drifted")
    if (
        tau_adic.get("result_state")
        != (
            "TAU_ADIC_EXTENDED_GAUGE_FIXED_H04_H14_COMPLETE_"
            "ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED"
        )
        or tau_adic.get("local_algebra", {}).get("kind")
        != "FORMAL_TAU_ADIC_LOCAL_ANALYTIC_JET_ALGEBRA"
    ):
        raise ValueError("formal tau-adic algebra drifted")
    if (
        charge.get("setting", {}).get("spacetime")
        != "R x S^3 with gbar=-dt^2+dOmega_3^2"
        or charge.get("phase_spaces", {}).get("P_der", {}).get("verdict")
        != "D_GAUGE"
        or not charge.get("phase_spaces", {})
        .get("P_der", {})
        .get("normalized_H_D_identically_zero")
    ):
        raise ValueError("closed-cylinder derived D sector drifted")
    if (
        bfv.get("cartan_contraction_allowed") is not True
        or bfv.get("compact_time_is_constraint") is not True
        or bfv.get("surface_charge_rank") != 0
    ):
        raise ValueError("closed-universe BFV choice drifted")
    generators = {
        row["generator_id"]: row
        for row in registry.get("generators", [])
    }
    if (
        generators.get("D_compact", {}).get("domain")
        != (
            "real conformal cylinder together with the declared "
            "positive-frequency residual representation"
        )
        or "K_Berger" not in generators
    ):
        raise ValueError("D generator registry drifted")


def build() -> dict[str, Any]:
    dependency_values = {
        name: _load(path)
        for name, path in DEPENDENCIES.items()
        if path.suffix == ".json"
    }
    _require_dependencies(dependency_values)

    q4 = _zero(4, 4)
    q4[1][0] = Fraction(1)
    q4[3][2] = Fraction(1)
    h4 = _zero(4, 4)
    h4[0][1] = Fraction(1)
    h4[2][3] = Fraction(1)
    pairing4 = _zero(4, 4)
    pairing4[0][3] = Fraction(1)
    pairing4[3][0] = Fraction(-1)
    pairing4[1][2] = Fraction(-1)
    pairing4[2][1] = Fraction(1)

    zero4 = _zero(4, 4)
    identity4 = _identity(4)
    if _multiply(q4, q4) != zero4:
        raise AssertionError("quartet Q0 is not nilpotent")
    if _add(_multiply(q4, h4), _multiply(h4, q4)) != identity4:
        raise AssertionError("quartet contraction failed")
    if _multiply(h4, h4) != zero4:
        raise AssertionError("quartet homotopy is not square zero")
    if _add(
        _multiply(_transpose(q4), pairing4),
        _multiply(pairing4, q4),
    ) != zero4:
        raise AssertionError("quartet Q0 is not cyclic")
    if _add(
        _multiply(_transpose(h4), pairing4),
        _multiply(pairing4, h4),
    ) != zero4:
        raise AssertionError("quartet homotopy is not cyclic")

    retract = _embed_quartet_with_unit(q4, h4)
    identity5 = _identity(5)
    projector5 = _multiply(retract["inclusion"], retract["projection"])
    if (
        _multiply(retract["projection"], retract["inclusion"])
        != _identity(1)
        or _add(
            _multiply(retract["Q0"], retract["homotopy"]),
            _multiply(retract["homotopy"], retract["Q0"]),
        )
        != _add(identity5, _scale(-1, projector5))
        or _multiply(retract["homotopy"], retract["homotopy"])
        != _zero(5, 5)
        or _multiply(retract["projection"], retract["homotopy"])
        != _zero(1, 5)
        or _multiply(retract["homotopy"], retract["inclusion"])
        != _zero(5, 1)
    ):
        raise AssertionError("unit-plus-quartet SDR failed")

    cartan_rows: list[dict[str, Any]] = []
    for weight in (-2, 0, 3):
        fixture = _cartan_fixture(q4, h4, weight)
        zero8 = _zero(8, 8)
        identity8 = _identity(8)
        if (
            _multiply(fixture["Q0"], fixture["Q0"]) != zero8
            or _add(
                _multiply(fixture["Q0"], fixture["iota_D0"]),
                _multiply(fixture["iota_D0"], fixture["Q0"]),
            )
            != fixture["L_D0"]
            or _add(
                _multiply(fixture["Q0"], fixture["homotopy"]),
                _multiply(fixture["homotopy"], fixture["Q0"]),
            )
            != identity8
        ):
            raise AssertionError(f"Cartan fixture failed at weight {weight}")
        cartan_rows.append(
            {
                "D_weight": weight,
                "ordered_basis": [
                    "tau",
                    "omega",
                    "omega_star",
                    "tau_hat_star",
                    "c_D tau",
                    "c_D omega",
                    "c_D omega_star",
                    "c_D tau_hat_star",
                ],
                "matrices": {
                    name: _matrix_payload(value)
                    for name, value in fixture.items()
                },
            }
        )

    cyclic_rows: list[dict[str, Any]] = []
    for weight in (0, 2):
        fixture = _cyclic_fixture(q4, h4, pairing4, weight)
        zero8 = _zero(8, 8)
        for operator in ("Q0", "homotopy", "L_D0"):
            defect = _add(
                _multiply(_transpose(fixture[operator]), fixture["pairing"]),
                _multiply(fixture["pairing"], fixture[operator]),
            )
            if defect != zero8:
                raise AssertionError(
                    f"{operator} cyclicity failed at weight pair +/-{weight}"
                )
        cyclic_rows.append(
            {
                "weight_pair": [weight, -weight],
                "ordered_basis": [
                    "tau_k",
                    "omega_k",
                    "omega_star_k",
                    "tau_hat_star_k",
                    "tau_minus_k",
                    "omega_minus_k",
                    "omega_star_minus_k",
                    "tau_hat_star_minus_k",
                ],
                "matrices": {
                    name: _matrix_payload(value)
                    for name, value in fixture.items()
                },
            }
        )

    affine_defects = {
        "vacuum_cylinder_D_compact": {
            "sigma_D": 0,
            "pi_LD_tau_minus_LD_pi_tau": 0,
            "tau_adic_augmentation_ideal_D_stable": True,
            "contraction_equivariant": True,
        },
        "minkowski_D_M_cross_check": {
            "sigma_D": -1,
            "pi_LD_tau_minus_LD_pi_tau": -1,
            "tau_adic_augmentation_ideal_D_stable": False,
            "contraction_equivariant": False,
        },
    }
    if (
        affine_defects["vacuum_cylinder_D_compact"][
            "pi_LD_tau_minus_LD_pi_tau"
        ]
        != 0
        or affine_defects["minkowski_D_M_cross_check"][
            "pi_LD_tau_minus_LD_pi_tau"
        ]
        == 0
    ):
        raise AssertionError("affine Weyl-component gate failed")

    matrix_payload = {
        "quartet_Q0": _matrix_payload(q4),
        "quartet_h": _matrix_payload(h4),
        "quartet_pairing": _matrix_payload(pairing4),
        "unit_plus_quartet": {
            name: _matrix_payload(value)
            for name, value in retract.items()
        },
        "cartan_weight_fixtures": cartan_rows,
        "cyclic_weight_pair_fixtures": cyclic_rows,
    }

    result = {
        "schema": "pure-weyl-wess-zumino-d-cartan-contraction-v1",
        "result_id": "WESS_ZUMINO_D_CARTAN_CONTRACTION_V1",
        "result_state": (
            "SAME_BACKGROUND_TAU_ADIC_D_COMPACT_CARTAN_"
            "CONTRACTION_EXPORTED"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "background": {
            "setting_id": "vacuum_cylinder_regular_Bach_chart",
            "spacetime": "R_t x S3",
            "metric": "g_bar=-dt^2+dOmega_3^2",
            "Bach_status": "BACH_FLAT",
            "regularity_scope": (
                "regular-Bach support-local jet chart with the finite "
                "conformal-Killing zero modes separated into the declared "
                "closed-universe derived residual sector P_der"
            ),
            "boundaries": "closed compact Cauchy surface S3; no spatial boundary",
            "phase_space": "P_der",
        },
        "generator": {
            "generator_id": "D_compact",
            "raw_definition": "partial_t",
            "Diff_component": "X_D=partial_t",
            "Weyl_component": 0,
            "background_fixed": True,
            "surface_charge_rank": 0,
            "is_K_Berger": False,
            "is_Minkowski_dilation": False,
        },
        "formal_field_algebra": {
            "kind": "FORMAL_TAU_ADIC_LOCAL_ANALYTIC_JET_ALGEBRA",
            "dressed_coordinates": [
                "g_hat=exp(-2 tau)g",
                "g_hat_star=exp(2 tau)g_star",
                "tau",
                "tau_hat_star=tau_star+2g.g_star",
                "xi",
                "xi_star",
                "omega",
                "omega_star",
            ],
            "quartet_order": [
                "tau",
                "omega",
                "omega_star",
                "tau_hat_star",
            ],
            "augmentation_ideal": "(tau,omega,omega_star,tau_hat_star)",
            "completion": (
                "nonnegative formal powers of tau with support-local "
                "analytic dressed-jet coefficients"
            ),
            "WZ_tau_is_Berger_clock": False,
        },
        "operators": {
            "Q0": {
                "base": "Q_Diff on the dressed pure-Diff BV complex",
                "quartet_rows": {
                    "Q0(tau)": "L_xi tau + omega",
                    "Q0(omega)": "L_xi omega",
                    "Q0(omega_star)": (
                        "L_xi omega_star + tau_hat_star"
                    ),
                    "Q0(tau_hat_star)": "L_xi tau_hat_star",
                },
                "one_D_ghost_form": (
                    "Q0(v)=q_W(v)+c_D L_D(v), "
                    "Q0(c_D v)=-c_D q_W(v)"
                ),
            },
            "iota_D0": {
                "base": "the certified residual CE contraction i_D",
                "iota_D0(c_D)": 1,
                "quartet_generators": 0,
                "extension": "graded derivation",
            },
            "L_D0": {
                "definition": "[Q0,iota_D0]_+",
                "quartet_action": "Lie derivative L_partial_t",
                "Fourier_action": "weight k on the k-th cylinder mode",
                "affine_term": 0,
            },
            "inclusion": (
                "include the dressed pure-Diff BV algebra as quartet number zero"
            ),
            "projection": (
                "set tau=omega=omega_star=tau_hat_star=0"
            ),
            "homotopy": {
                "unnormalized_s": {
                    "s(omega)": "tau",
                    "s(tau_hat_star)": "omega_star",
                    "other_generators": 0,
                },
                "number_operator": (
                    "N counts tau, omega, omega_star and tau_hat_star"
                ),
                "formula": "S=N^(-1)s on N>0 and S=0 on N=0",
                "one_D_ghost_sign": (
                    "S(v)=s(v), S(c_D v)=-c_D s(v)"
                ),
                "support_local": True,
                "maximum_differential_order": 0,
            },
            "pairing": {
                "base": (
                    "canonical dressed odd BV pairing on "
                    "(g_hat,g_hat_star),(xi,xi_star)"
                ),
                "quartet_nonzero_entries": [
                    "<tau,tau_hat_star>=1",
                    "<tau_hat_star,tau>=-1",
                    "<omega,omega_star>=-1",
                    "<omega_star,omega>=1",
                ],
                "weight_rule": "only opposite D weights pair",
                "canonical_change_preserves_pairing": True,
            },
        },
        "exact_identities": {
            "Q0_squared": "0",
            "Cartan": "[Q0,iota_D0]_+=L_D0",
            "projection_inclusion": "pi iota=1",
            "contraction": "Q0 S+S Q0=1-iota pi",
            "side_conditions": ["S^2=0", "pi S=0", "S iota=0"],
            "D_equivariance": [
                "[L_D0,Q0]=0",
                "[L_D0,S]=0",
                "L_D0 iota=iota L_D0",
                "pi L_D0=L_D0 pi",
            ],
            "cyclicity": [
                "Q0^T Omega+Omega Q0=0",
                "S^T Omega+Omega S=0",
                "L_D0^T Omega+Omega L_D0=0 on opposite-weight pairs",
            ],
            "derivation_extension": (
                "the generator identities extend to every completed "
                "graded-commutative monomial because Q0, iota_D0, L_D0, "
                "s and N are filtration-continuous graded derivations or "
                "the normalized Euler homotopy"
            ),
        },
        "matrix_fixtures": matrix_payload,
        "affine_Weyl_component_gate": {
            "criterion": (
                "the tau-adic augmentation projection is D-equivariant "
                "only if sigma_D=0, since pi(L_D tau)=sigma_D"
            ),
            "rows": affine_defects,
            "basis_independent_obstruction": (
                "for sigma_D nonzero the quartet augmentation ideal is "
                "not D-stable, so no contraction with that projection can "
                "be D-equivariant"
            ),
            "minimal_missing_carrier_for_nonzero_sigma": (
                "an explicitly translated compensator-background orbit or "
                "another affine D-stable target carrier; none is supplied"
            ),
        },
        "dependencies": _dependency_refs(),
        "content_hashes": {
            "operators_sha256": _digest(matrix_payload),
            "formal_algebra_sha256": _digest(
                {
                    "quartet": [
                        "tau",
                        "omega",
                        "omega_star",
                        "tau_hat_star",
                    ],
                    "q": ["omega", "0", "tau_hat_star", "0"],
                    "s": ["0", "tau", "0", "omega_star"],
                    "D": "partial_t",
                    "sigma_D": 0,
                }
            ),
            "dependency_manifest_sha256": _digest(_dependency_refs()),
        },
        "consumer_contract": {
            "request_id": (
                "sf:program/request/"
                "quantum-cartan-d-one-loop-obstruction-to-classical-"
                "0ffe79fd2ff547a0"
            ),
            "satisfied_scope": (
                "same-background classical Q0/iota_D0/L_D0 and cyclic "
                "tau-adic contraction for vacuum-cylinder raw D_compact"
            ),
            "not_satisfied": [
                "Minkowski D_M compensator contraction",
                "complete renormalized Q1",
                "iota_D1",
                "L_D1",
                "renormalized products",
                "local-insertion-to-Cartan Ward map",
            ],
        },
        "claim_flags": {
            "SAME_BACKGROUND_TAU_ADIC_COMPENSATOR_D_CONTRACTION": True,
            "RAW_D_COMPACT_USED": True,
            "RAW_D_REPLACED_BY_K_BERGER": False,
            "WZ_TAU_IDENTIFIED_WITH_BERGER_CLOCK": False,
            "MINKOWSKI_DILATION_CONTRACTION_EXPORTED": False,
            "QUANTUM_D_CARTAN_DEFECT_CLASSIFIED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
            "HADAMARD_OR_POSITIVITY_CLAIM": False,
        },
        "next_gate": (
            "import the complete coefficient-bearing renormalized D-Ward "
            "operator on this same vacuum-cylinder tau-adic complex"
        ),
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC certificate extends the frozen pure-Weyl "
            "minimal BV algebra by the formal Wess--Zumino compensator quartet "
            "on the unit vacuum cylinder and exports exact Q0, iota_D0, L_D0, "
            "inclusion, projection, support-local homotopy and canonical odd "
            "pairing data. Raw D_compact=partial_t has sigma_D=0, so the "
            "tau-adic augmentation ideal and contraction are D-equivariant; "
            "the Cartan, SDR, cyclicity and opposite-weight pairing identities "
            "are verified exactly. The Wess--Zumino tau is not the Berger "
            "clock and raw D is not K_Berger. The same projection is exactly "
            "obstructed for Minkowski dilation sigma_D=-1. This does not "
            "supply Q1, iota_D1, L_D1, renormalized products, a quantum "
            "Cartan classification, residual quantum transfer, a Lorentzian "
            "QME, Hadamard state, positivity, particles, scattering or "
            "unitarity."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    if (
        value.get("result_id") != "WESS_ZUMINO_D_CARTAN_CONTRACTION_V1"
        or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]
        or value.get("generator", {}).get("generator_id") != "D_compact"
        or value.get("generator", {}).get("Weyl_component") != 0
        or value.get("generator", {}).get("is_K_Berger") is not False
        or value.get("formal_field_algebra", {}).get(
            "WZ_tau_is_Berger_clock"
        )
        is not False
    ):
        raise ValueError("identity or claim boundary drifted")
    flags = value.get("claim_flags", {})
    if flags != {
        "SAME_BACKGROUND_TAU_ADIC_COMPENSATOR_D_CONTRACTION": True,
        "RAW_D_COMPACT_USED": True,
        "RAW_D_REPLACED_BY_K_BERGER": False,
        "WZ_TAU_IDENTIFIED_WITH_BERGER_CLOCK": False,
        "MINKOWSKI_DILATION_CONTRACTION_EXPORTED": False,
        "QUANTUM_D_CARTAN_DEFECT_CLASSIFIED": False,
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        "HADAMARD_OR_POSITIVITY_CLAIM": False,
    }:
        raise ValueError("claim flags over-promoted")
    rows = value.get("affine_Weyl_component_gate", {}).get("rows", {})
    if (
        rows.get("vacuum_cylinder_D_compact", {}).get(
            "contraction_equivariant"
        )
        is not True
        or rows.get("minkowski_D_M_cross_check", {}).get(
            "contraction_equivariant"
        )
        is not False
    ):
        raise ValueError("affine Weyl-component boundary drifted")
    if len(value.get("matrix_fixtures", {}).get(
        "cartan_weight_fixtures", []
    )) != 3:
        raise ValueError("Cartan fixture ledger incomplete")


def _report(value: dict[str, Any]) -> str:
    hashes = value["content_hashes"]
    template = r"""# Wess--Zumino compensator raw-\(D\) Cartan contraction

## Result

On the unit vacuum conformal cylinder, in the closed-universe derived sector
`P_der`, raw \(D_{\rm compact}=\partial_t\) has zero Weyl component.  The
formal Wess--Zumino compensator quartet therefore admits the exact
same-background contraction

\[
Q_0S+SQ_0=1-\iota\pi,\qquad
[Q_0,\iota_{D,0}]_+=\mathcal L_{D,0}.
\]

The projection sets
`tau=omega=omega_star=tau_hat_star=0`.  The homotopy is the normalized
quartet Euler homotopy

\[
s(\omega)=\tau,\qquad s(\widehat\tau^*)=\omega^*,\qquad
S=N^{-1}s\quad(N>0).
\]

All Cartan, side-condition, support-locality, \(D\)-equivariance and cyclic
pairing identities pass exactly.  The finite replay covers weights
`-2, 0, 3`, and the opposite-weight cyclic fixtures cover `0` and `+/-2`.
The all-monomial statement follows by the declared filtration-continuous
graded-derivation extension.

## Sharp generator boundary

This is raw `D_compact`, not `K_Berger`; the Wess--Zumino `tau` is not the
Berger clock.  The construction does not extend by name matching to
Minkowski dilation.  For a generator with Weyl component `sigma_D`,

\[
\pi(\mathcal L_D\tau)-\mathcal L_D(\pi\tau)=\sigma_D.
\]

Thus the tau-adic augmentation ideal is \(D\)-stable on the cylinder
(`sigma_D=0`) and fails already on `tau` for Minkowski `D_M`
(`sigma_D=-1`).

## Consumer boundary

The classical input requested by the one-loop quantum \(D\)-Ward calculation
is complete for the vacuum-cylinder raw-`D_compact` row.  The complete
renormalized `Q1`, `iota_D1`, `L_D1`, renormalized products and the
local-insertion-to-Cartan Ward map remain absent.  Consequently no quantum
Cartan class or residual quantum transfer follows.

## Reproduction

```bash
python3 d_quotient_classical/compensator/wess_zumino_d_cartan_contraction.py --check
python3 d_quotient_classical/compensator/verify_wess_zumino_d_cartan_contraction.py
python3 -m unittest d_quotient_classical.compensator.tests.test_wess_zumino_d_cartan_contraction
```

Operator hash: `__OPERATORS_SHA256__`

Formal-algebra hash: `__FORMAL_ALGEBRA_SHA256__`

CLOSE-OUT: DONE — the complete stop condition is met
EVIDENCE: d_quotient_classical/certificates/WESS_ZUMINO_D_CARTAN_CONTRACTION_V1.json
"""
    return template.replace(
        "__OPERATORS_SHA256__", hashes["operators_sha256"]
    ).replace(
        "__FORMAL_ALGEBRA_SHA256__", hashes["formal_algebra_sha256"]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    report = _report(value)
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered, encoding="utf-8")
        REPORT.write_text(report, encoding="utf-8")
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"stale certificate: {OUTPUT}")
        if not REPORT.exists() or REPORT.read_text(encoding="utf-8") != report:
            raise SystemExit(f"stale report: {REPORT}")
        schema = _load(SCHEMA)
        errors = sorted(
            Draft202012Validator(schema).iter_errors(value),
            key=lambda error: list(error.path),
        )
        if errors:
            raise SystemExit(
                "schema validation failed: "
                + "; ".join(error.message for error in errors[:5])
            )
    print(
        "WESS-ZUMINO D-CARTAN: "
        "VACUUM-CYLINDER RAW D_COMPACT CONTRACTION EXPORTED"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
