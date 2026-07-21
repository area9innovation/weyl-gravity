#!/usr/bin/env python3
"""Certify the first exact Berger scalar-Hodge restriction obstruction.

The proposed scalar subcomplex uses exact spatial one-forms ``dY`` for the
spatial Diff ghost and its gauge-fixing partners.  On the selected non-Einstein
Berger sphere the gauge-fixed ghost endpoint does not preserve exact forms.
This module computes the obstruction ``d_1 q_{bar c^*,c} d_0`` directly in the
noncommutative invariant-frame PBW algebra.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    LinearOperator,
    U,
    V,
    ZERO,
    _compose_matrices,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(__file__).with_name(
    "TWO_PHASE_COUNTERFLOW_BERGER_SCALAR_HODGE_BLOCK_OBSTRUCTION_V1.json"
)
PAYLOAD = Path(__file__).with_name(
    "TWO_PHASE_COUNTERFLOW_BERGER_SCALAR_HODGE_BLOCK_OBSTRUCTION_PAYLOAD_V1.json"
)
SCHEMA = Path(__file__).with_name("schema") / (
    "two-phase-counterflow-berger-scalar-hodge-block-obstruction-v1.schema.json"
)
PAYLOAD_SCHEMA = Path(__file__).with_name("schema") / (
    "two-phase-counterflow-berger-scalar-hodge-block-obstruction-payload-v1.schema.json"
)

IMPORTS = {
    "all_hodge_shortfall": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_UNRESTRICTED_ALL_HODGE_HEALTH_SHORTFALL_V1.json",
        "9d9859aaf7a5b7f717d2b81ab1db0d7878ae249681f5859814272b5322af4875",
        "TWO_PHASE_COUNTERFLOW_UNRESTRICTED_ALL_HODGE_HEALTH_SHORTFALL_V1",
        "014f10b9477d762222c724b9eb61ce0d1c46128d",
    ),
    "causal_parent": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json",
        "7d969e7e630f793dfe12fe07b0e98a67b2543f9aa85fa03277e491fb00296db7",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1",
        "951e88307abbea0996513773a33e66b37555272b",
    ),
    "gauge_fixed_q54": (
        "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
        "6e3baf6ecfab2c2854ccfbfb5c69122fe0bbe621ddcf8ab2a5651e3decf113e0",
        "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION",
        "445e26663d06764bc858ff0a004ba6178acce75f",
    ),
    "peter_weyl_engine": (
        "closed_universe_observers/certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
        "e24c860b338188254c4388a7ca660ac454ba7b70c13659ffc36a98bf39250120",
        "BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE",
        "0b8fe045411de64008f55bb551ab3799aa85e77a",
    ),
    "volume_seed": (
        "d_quotient_classical/certificates/BERGER_CLOCK_REDUCED_CHARGE_SEED.json",
        "573381287998b6645b37fcbad0273c23c0e5cff58450cbcf7a2dc1152a8dfcd9",
        "BERGER_CLOCK_REDUCED_CHARGE_SEED",
        "bb5738d6e3e30a68adcc9a70c35dac089079e3db",
    ),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _load_imports() -> tuple[dict[str, Any], dict[str, Any]]:
    records: dict[str, Any] = {}
    values: dict[str, Any] = {}
    for role, (relative, expected, result_id, source_commit) in IMPORTS.items():
        path = ROOT / relative
        value = json.loads(path.read_text())
        actual = _sha(path)
        if actual != expected or value.get("result_id") != result_id:
            raise AssertionError(f"{role} import drifted")
        records[role] = {
            "path": relative,
            "sha256": actual,
            "result_id": result_id,
            "source_commit": source_commit,
            "oracle_fields_consumed": [],
        }
        values[role] = value
    if values["causal_parent"]["complete_parent"]["complete_component_rank"] != 70:
        raise AssertionError("70-row parent rank drifted")
    if values["all_hodge_shortfall"]["terminal_verdict"]["first_undefined_block"] != "retained_gravity_scalar":
        raise AssertionError("scalar successor gate drifted")
    if values["gauge_fixed_q54"]["row_layout"]["total_rows"] != 54:
        raise AssertionError("gauge-fixed parent row layout drifted")
    if values["peter_weyl_engine"]["flags"]["GENERIC_FINITE_PETER_WEYL_DE_RHAM_BLOCK_CONSTRUCTOR"] is not True:
        raise AssertionError("Peter-Weyl engine is unavailable")
    if values["volume_seed"]["conventions"]["spatial_volume"] != "Vol(S3_Berger)=16 pi^2 a^3 sqrt(q)":
        raise AssertionError("Berger volume convention drifted")
    return records, values


def _from_record(record: dict[str, Any], row_start: int, row_stop: int, column_start: int, column_stop: int) -> list[list[LinearOperator]]:
    matrix = [[ZERO for _ in range(column_stop - column_start)] for _ in range(row_stop - row_start)]
    symbols = {"u": U, "v": V, "alpha_B": sp.Symbol("alpha_B")}
    for row, column, terms in record["entries"]:
        if row_start <= row < row_stop and column_start <= column < column_stop:
            matrix[row - row_start][column - column_start] = LinearOperator.from_terms(
                (
                    0,
                    tuple(axis for axis, count in enumerate(exponents) for _ in range(count)),
                    sp.sympify(coefficient, locals=symbols),
                )
                for exponents, coefficient in terms
            )
    return matrix


def _d0() -> list[list[LinearOperator]]:
    return [
        [LinearOperator.from_terms(((0, (axis,), sp.S.One),))]
        for axis in (1, 2, 3)
    ]


def _d1() -> list[list[LinearOperator]]:
    # Row order theta12, theta13, theta23; column order theta1, theta2, theta3.
    pairs = ((1, 2), (1, 3), (2, 3))
    structure = {(1, 2): (3, U), (1, 3): (2, -V), (2, 3): (1, V)}
    matrix = [[ZERO for _ in range(3)] for _ in range(3)]
    for row, (first, second) in enumerate(pairs):
        matrix[row][second - 1] = matrix[row][second - 1] + LinearOperator.from_terms(
            ((0, (first,), sp.S.One),)
        )
        matrix[row][first - 1] = matrix[row][first - 1] + LinearOperator.from_terms(
            ((0, (second,), -sp.S.One),)
        )
        target, coefficient = structure[(first, second)]
        matrix[row][target - 1] = matrix[row][target - 1] + LinearOperator.from_terms(
            ((0, (), -coefficient),)
        )
    return matrix


def _defect(q54: dict[str, Any]) -> list[LinearOperator]:
    # q sends c_spatial[0:3] to bar_c_star_diff[22:25].
    endpoint = _from_record(q54["classical_unary_q1"]["matrix"], 22, 25, 0, 3)
    return [row[0] for row in _compose_matrices(_d1(), _compose_matrices(endpoint, _d0()))]


def _operator_record(operator: LinearOperator) -> list[dict[str, str]]:
    return [
        {
            "word": "".join(f"e{axis}" for axis in word) or "1",
            "coefficient": sp.sstr(sp.factor(coefficient)),
        }
        for _, word, coefficient in operator.terms
    ]


def _expected_defect() -> list[LinearOperator]:
    terms = [
        [
            ((0, 0, 3), 3 * U**2 * (U - V)),
            ((1, 1, 3), -sp.Rational(17, 3) * U**2 * (U - V)),
            ((2, 2, 3), -sp.Rational(17, 3) * U**2 * (U - V)),
            ((3,), 2 * U**3 * (U - V) ** 2),
            ((3, 3, 3), -sp.Rational(11, 3) * U**2 * (U - V)),
        ],
        [
            ((0, 0, 1, 3), -3 * U * (U - V)),
            ((1, 1, 1, 3), sp.Rational(11, 3) * U * (U - V)),
            ((1, 2, 2, 3), sp.Rational(11, 3) * U * (U - V)),
            ((1, 3), -2 * U**2 * (U - V) ** 2),
            ((1, 3, 3, 3), sp.Rational(11, 3) * U * (U - V)),
            ((2, 3, 3), -2 * U**2 * (U - V)),
        ],
        [
            ((0, 0, 2, 3), -3 * U * (U - V)),
            ((1, 1, 2, 3), sp.Rational(11, 3) * U * (U - V)),
            ((1, 3, 3), -sp.Rational(16, 3) * U**2 * (U - V)),
            ((2, 2, 2, 3), sp.Rational(11, 3) * U * (U - V)),
            ((2, 3), -sp.Rational(1, 3) * U**2 * (U - V) * (6 * U + 5 * V)),
            ((2, 3, 3, 3), sp.Rational(11, 3) * U * (U - V)),
        ],
    ]
    return [
        LinearOperator.from_terms((0, word, coefficient) for word, coefficient in row)
        for row in terms
    ]


def _payload(imports: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    defect = _defect(values["gauge_fixed_q54"])
    expected = _expected_defect()
    if defect != expected:
        raise AssertionError("abstract scalar-Hodge closure defect drifted")
    if not all(
        sp.simplify(coefficient.subs(V, U)) == 0
        for operator in defect
        for _, _, coefficient in operator.terms
    ):
        raise AssertionError("round-limit mutation did not remove the defect")

    u0 = 3 * sp.sqrt(10) / 20
    v0 = 2 * sp.sqrt(10) / 3
    leading = sp.factor(3 * U**2 * (U - V))
    leading_target = sp.factor(leading.subs({U: u0, V: v0}))
    if leading_target != -sp.Rational(279, 800) * sp.sqrt(10):
        raise AssertionError("target leading coefficient drifted")
    # e3 Y_jmk=-i v k Y_jmk, hence this is the e0^2 theta12 coefficient.
    k = sp.Symbol("k", real=True)
    mode_leading = sp.factor(leading_target * (-sp.I * v0 * k))
    if mode_leading != sp.Rational(93, 40) * sp.I * k:
        raise AssertionError("mode obstruction coefficient drifted")

    volume = 12 * sp.pi**2 * sp.sqrt(10) / 5
    value: dict[str, Any] = {
        "schema": "pure-weyl-two-phase-counterflow-berger-scalar-hodge-block-obstruction-payload-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_BERGER_SCALAR_HODGE_BLOCK_OBSTRUCTION_PAYLOAD_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": imports,
        "oracle_fields_consumed": [],
        "normalized_scalar_modes": {
            "geometry": "biaxial Berger S3 with a=1, c=3*sqrt(10)/20 and q=c^2=9/40",
            "volume": sp.sstr(volume),
            "label_domain": "two_j in Z_>=0; j=two_j/2; m,k=-j,-j+1,...,j",
            "mode": "Y_jmk=sqrt((2*j+1)/Vol_Berger)*D^j_mk",
            "orthonormality": "integral conjugate(Y_jmk) Y_j'm'k' = delta_jj' delta_mm' delta_kk'",
            "conjugation": "conjugate(Y_jmk)=(-1)^(m-k) Y_j,-m,-k",
            "reality": "real fields obey a_jmk_bar=(-1)^(m-k) a_j,-m,-k",
            "scalar_laplacian_eigenvalue": "lambda_jk=j*(j+1)+(31/9)*k^2",
            "right_fibre_derivative": "e3 Y_jmk=-I*(2*sqrt(10)/3)*k Y_jmk",
        },
        "exact_one_form_maps": {
            "domain": "j>0",
            "inclusion": "iota_exact(a)=a*d_h Y_jmk in the spatial Diff ghost triplet",
            "projection": "pi_exact(alpha)=lambda_jk^(-1)*<d_h Y_jmk,alpha>_L2",
            "identity": "pi_exact iota_exact=1",
            "constant_exception": "j=0 has d_h Y_000=0, so the spatial exact-one-form inclusion has rank zero",
        },
        "first_closure_test": {
            "source_rows": ["c_spatial_1", "c_spatial_2", "c_spatial_3"],
            "target_rows": ["bar_c_star_diff_1", "bar_c_star_diff_2", "bar_c_star_diff_3"],
            "operator": "C_scalar=d_1 q54[bar_c_star_diff,c_spatial] d_0",
            "meaning": "the proposed exact-one-form scalar carrier is closed only if C_scalar=0",
            "two_form_row_order": ["theta1_wedge_theta2", "theta1_wedge_theta3", "theta2_wedge_theta3"],
            "PBW_rows": [_operator_record(operator) for operator in defect],
            "common_round_factor": "u-v",
            "target_values": {"u": sp.sstr(u0), "v": sp.sstr(v0), "u_minus_v": sp.sstr(sp.factor(u0 - v0))},
            "leading_temporal_PBW_term": "3*u^2*(u-v)*e0^2*e3 in theta1_wedge_theta2",
            "leading_mode_coefficient": "93*I*k/40",
            "generic_verdict": "NONZERO_FOR_EVERY_k_NOT_EQUAL_0",
        },
        "exceptional_ledger": [
            {
                "labels": "j=0,m=0,k=0",
                "status": "EXCEPTIONAL_ZERO_GRADIENT",
                "reason": "dY=0; the exact spatial Diff scalar carrier is absent and the global homogeneous sector is handled separately",
            },
            {
                "labels": "integer j>=1, arbitrary m, k=0",
                "status": "FIRST_DEFECT_VANISHES_FULL_SCALAR_BLOCK_NOT_COMPUTED",
                "reason": "every PBW word in C_scalar ends in e3, but vanishing of this first defect is not a full closure or quotient proof",
            },
            {
                "labels": "j>=1/2, arbitrary m, k!=0",
                "status": "EXACT_SCALAR_HODGE_SUBCOMPLEX_OBSTRUCTION",
                "reason": "the e0^2 theta12 coefficient is 93*I*k/40 and is nonzero",
            },
        ],
        "mutation_ledger": [
            {"id": "ROUND_LIMIT_u_EQUALS_v", "detected": True, "effect": "all PBW defect coefficients vanish; this is not the target background"},
            {"id": "RIGHT_NEUTRAL_k_EQUALS_0", "detected": True, "effect": "the leading generic witness vanishes and the label is retained as exceptional/open"},
            {"id": "DROP_HAAR_NORMALIZATION", "detected": True, "effect": "pi_exact iota_exact becomes Vol_Berger/(2*j+1), not one"},
            {"id": "DROP_WIGNER_CONJUGATION_PHASE", "detected": True, "effect": "fails at j=1/2,m=1/2,k=-1/2 where (-1)^(m-k)=-1"},
            {"id": "DELETE_GAUGE_FIXED_ANTIGHOST_DUAL_ROW", "detected": True, "effect": "hides rather than repairs C_scalar and changes the certified q54"},
        ],
        "terminal_verdict": {
            "result_state": "EXACT_GENERIC_SCALAR_HODGE_SUBCOMPLEX_OBSTRUCTION",
            "normalized_scalar_modes_defined": True,
            "exact_one_form_iota_pi_defined_for_j_positive": True,
            "generic_nonzero_k_scalar_subcomplex_closed": False,
            "axisymmetric_k0_full_scalar_block_status": "NOT_COMPUTED_AFTER_FIRST_EXACT_OBSTRUCTION",
            "restricted_unary_status": "NOT_DEFINED_ON_PROPOSED_GENERIC_SCALAR_HODGE_CARRIER",
            "physical_quotient_status": "NOT_DEFINED_NONCLOSED_SUBCOMPLEX",
            "pairing_characteristic_gradient_status": "NOT_REACHED",
            "q70_parent_nilpotency_and_causality_preserved": True,
            "physical_instability_found": False,
            "all_hodge_health_established": False,
            "downstream_vector_tensor_export_activated": False,
        },
        "next_gate": {
            "preferred": "replace round-style scalar/vector/tensor splitting by complete SU(2)_L x U(1)_R isotypical Berger blocks and quotient the full closed block",
            "alternative": "construct and certify a same-background gauge fixing whose ghost endpoint preserves exact/coexact Hodge summands",
            "must_retain": ["unrestricted Q_rel", "physical D", "physical R_rel", "full q70 row content"],
        },
        "claim_boundary": {
            "establishes": [
                "normalized scalar Wigner modes and exact conjugation on the selected Berger sphere",
                "the exact nonzero PBW curl of the gauge-fixed Diff endpoint on scalar exact one-forms",
                "a generic obstruction for every nonzero right weight k and a fail-closed exceptional ledger",
                "the first representation-theoretic reason the requested scalar physical quotient cannot be assembled",
            ],
            "does_not_establish": [
                "failure of the complete 70-row BV complex or its causal homotopy",
                "a full verdict for the right-neutral k=0 exceptional blocks",
                "a vector, tensor or all-Hodge health theorem",
                "a negative-energy, gradient or exponential instability",
                "an observer, Hadamard, particle, QME, positivity or unitarity theorem",
            ],
        },
        "content_sha256": "PENDING",
    }
    value["content_sha256"] = _digest({key: item for key, item in value.items() if key != "content_sha256"})
    return value


def _certificate(imports: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    terminal = payload["terminal_verdict"]
    return {
        "schema": "pure-weyl-two-phase-counterflow-berger-scalar-hodge-block-obstruction-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_BERGER_SCALAR_HODGE_BLOCK_OBSTRUCTION_V1",
        "result_state": terminal["result_state"],
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": payload["dependency_tags"],
        "imports": imports,
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": "PENDING_WRITE",
            "content_sha256": payload["content_sha256"],
        },
        "first_obstruction": payload["first_closure_test"],
        "exceptional_statuses": {row["labels"]: row["status"] for row in payload["exceptional_ledger"]},
        "terminal_verdict": terminal,
        "next_gate": payload["next_gate"],
        "claim_boundary": payload["claim_boundary"],
        "content_hashes": {
            "normalized_modes_sha256": _digest(payload["normalized_scalar_modes"]),
            "one_form_maps_sha256": _digest(payload["exact_one_form_maps"]),
            "obstruction_sha256": _digest(payload["first_closure_test"]),
            "exceptions_sha256": _digest(payload["exceptional_ledger"]),
            "mutations_sha256": _digest(payload["mutation_ledger"]),
            "terminal_sha256": _digest(terminal),
            "boundary_sha256": _digest(payload["claim_boundary"]),
        },
    }


def validate(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    expected_payload = _digest({key: item for key, item in payload.items() if key != "content_sha256"})
    if payload["content_sha256"] != expected_payload or payload["oracle_fields_consumed"] != []:
        raise AssertionError("payload provenance failed")
    terminal = certificate["terminal_verdict"]
    if terminal["generic_nonzero_k_scalar_subcomplex_closed"]:
        raise AssertionError("nonclosed scalar carrier was promoted")
    if terminal["physical_quotient_status"] != "NOT_DEFINED_NONCLOSED_SUBCOMPLEX":
        raise AssertionError("physical quotient silently promoted")
    if not terminal["q70_parent_nilpotency_and_causality_preserved"]:
        raise AssertionError("scoped subcomplex obstruction was misreported as a parent failure")
    if terminal["physical_instability_found"] or terminal["all_hodge_health_established"]:
        raise AssertionError("representation obstruction promoted to physical health")
    if terminal["downstream_vector_tensor_export_activated"]:
        raise AssertionError("downstream export activated across a nonclosed scalar gate")
    expected_hashes = {
        "normalized_modes_sha256": _digest(payload["normalized_scalar_modes"]),
        "one_form_maps_sha256": _digest(payload["exact_one_form_maps"]),
        "obstruction_sha256": _digest(payload["first_closure_test"]),
        "exceptions_sha256": _digest(payload["exceptional_ledger"]),
        "mutations_sha256": _digest(payload["mutation_ledger"]),
        "terminal_sha256": _digest(terminal),
        "boundary_sha256": _digest(payload["claim_boundary"]),
    }
    if certificate["content_hashes"] != expected_hashes:
        raise AssertionError("certificate content hashes drifted")


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    imports, values = _load_imports()
    payload = _payload(imports, values)
    certificate = _certificate(imports, payload)
    validate(certificate, payload)
    return certificate, payload


def write() -> None:
    certificate, payload = build()
    PAYLOAD.write_text(_render(payload))
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
    validate(certificate, payload)
    Draft202012Validator(json.loads(PAYLOAD_SCHEMA.read_text())).validate(payload)
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    OUTPUT.write_text(_render(certificate))


def check() -> None:
    certificate, payload = build()
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
    validate(certificate, payload)
    for path in (SCHEMA, PAYLOAD_SCHEMA):
        Draft202012Validator.check_schema(json.loads(path.read_text()))
    Draft202012Validator(json.loads(PAYLOAD_SCHEMA.read_text())).validate(payload)
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    if json.loads(PAYLOAD.read_text()) != payload or json.loads(OUTPUT.read_text()) != certificate:
        raise AssertionError("stored scalar-Hodge obstruction artifacts drifted")
    print("TWO_PHASE_COUNTERFLOW_BERGER_SCALAR_HODGE_BLOCK_OBSTRUCTION_V1: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()


if __name__ == "__main__":
    main()
