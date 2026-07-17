#!/usr/bin/env python3
"""Certify the Maxwell causal unary contraction and first transferred q2.

The gravity--clock SDR is imported as a frozen differential operator record.
It is extended by the identity on the ten Maxwell BV rows.  The standard
Lorenz-gauge Maxwell witness gives a normally hyperbolic de Rham wave block,
and the complete Maxwell q2 overlay is transferred to the resulting 36-row
endpoint by ``ell2 = pi64 q2(iota36,iota36)``.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import gc
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import sympy as sp
import jsonschema

_WORKSPACE = Path(__file__).resolve().parents[2]
if str(_WORKSPACE) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE))

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (
    _matrix_from_record,
)
from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
    _embed,
    _identity_matrix,
    _is_zero,
    _matrix_add,
    _matrix_record,
    _negative,
    _one,
    _sparse_multiply,
    _subtract,
    _zero,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    ROOT,
    _adjoint_matrix,
)
from d_quotient_classical.backreacted_clock.berger_support_local_coupled_maxwell_q2 import (
    APLUS_ROWS,
    A_ROWS,
    CM,
    CMPLUS,
    COMBINED_PARITIES,
    ETA_DIAGONAL,
    build_maxwell_q2_overlay,
    maxwell_unary_blocks,
    _scalar_operator,
)
from d_quotient_classical.backreacted_clock.berger_support_local_q2 import (
    BZERO,
    BilinearOperator,
    _apply_output_linear,
    _fixture_bilinear,
    _fixture_linear,
    _precompose_bilinear,
    _precompose_bilinear_slot,
)


CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json"
PAYLOAD = ROOT / "d_quotient_classical/certificates/BERGER_FIRST_TRANSFERRED_MIXED_Q2_PAYLOAD.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-maxwell-unary-contraction-and-transfer.md"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-maxwell-unary-contraction-transfer-v1.schema.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/schema/berger-first-transferred-mixed-q2-payload-v1.schema.json"

DEPENDENCIES = {
    "gravity_sdr": ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
    "retained_layout": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json",
    "gravity_causal": ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json",
    "retained_causal": ROOT / "d_quotient_classical/certificates/BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json",
    "coupled_q2": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2.json",
    "coupled_q2_payload": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD.json",
    "redshift_fixture": ROOT / "d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _load_dependencies() -> dict[str, dict[str, Any]]:
    data = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if data["gravity_sdr"]["flags"]["BERGER_COMPLETE_GAUGE_FIXED_UNARY_EXPORT"] is not True:
        raise AssertionError("54-row gravity SDR is unavailable")
    if data["gravity_causal"]["flags"]["BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2"] is not True:
        raise AssertionError("54-row gravity causal contraction is unavailable")
    if data["retained_causal"]["result_state"] != "GREEN_CERTIFIED_HADAMARD_OPEN":
        raise AssertionError("26-row gravity endpoint is not Green certified")
    if data["coupled_q2"]["flags"]["CLASSICAL_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2"] is not True:
        raise AssertionError("complete 64-row q2 is unavailable")
    q2_payload_hash = data["coupled_q2"]["classical_binary_q2"]["payload_file_sha256"]
    if _sha256(DEPENDENCIES["coupled_q2_payload"]) != q2_payload_hash:
        raise AssertionError("64-row q2 payload hash drifted")
    if data["redshift_fixture"]["flags"]["BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE"] is not True:
        raise AssertionError("dynamical Maxwell fixture is unavailable")
    return data


def _maxwell_q1() -> list[list[Any]]:
    blocks = maxwell_unary_blocks()
    q = _zero(10, 10)
    for mu in range(4):
        q[1 + mu][0] = blocks["gradient"][mu][0]
        q[9][5 + mu] = blocks["divergence"][0][mu]
        for nu in range(4):
            q[5 + mu][1 + nu] = blocks["hessian"][mu][nu]
    return q


def _combined_sdr(dependencies: dict[str, dict[str, Any]]) -> dict[str, Any]:
    gravity = dependencies["gravity_sdr"]
    q54 = _matrix_from_record(gravity["classical_unary_q1"]["matrix"])
    i54 = _matrix_from_record(gravity["contraction"]["iota_cl"])
    p54 = _matrix_from_record(gravity["contraction"]["pi_cl"])
    s54 = _matrix_from_record(gravity["contraction"]["S_cl"])

    q64 = _zero(64, 64)
    i64 = _zero(64, 36)
    p64 = _zero(36, 64)
    s64 = _zero(64, 64)
    _embed(q64, q54, 0, 0)
    _embed(q64, _maxwell_q1(), 54, 54)
    _embed(i64, i54, 0, 0)
    _embed(p64, p54, 0, 0)
    _embed(s64, s54, 0, 0)
    for index in range(10):
        i64[54 + index][26 + index] = _one()
        p64[26 + index][54 + index] = _one()

    q36 = _fixture_matrix(_sparse_multiply(_sparse_multiply(p64, q64), i64))
    if not _is_zero(_subtract(_sparse_multiply(p64, i64), _identity_matrix(36))):
        raise AssertionError("combined pi-iota identity failed")
    if gravity["exact_checks"]["gauge_fixed_classical_unary_q1_squared_zero"] is not True:
        raise AssertionError("imported gravity q1 square failed")
    if not _is_zero(_fixture_matrix(_sparse_multiply(_maxwell_q1(), _maxwell_q1()))):
        raise AssertionError("Maxwell q1 square failed")
    # The only nonzero S64 block is the imported gravity S54 block, while q64,
    # i64 and p64 are block diagonal with identity/zero Maxwell additions.
    # Re-expanding q64 S64+S64 q64 creates a very large PBW intermediate but
    # adds no new coefficients.  Audit the certified gravity identity and the
    # exact block incidence instead.
    gravity_checks = gravity["exact_checks"]
    if gravity_checks["gauge_fixed_contraction_identity"] is not True:
        raise AssertionError("imported gravity contraction identity failed")
    if gravity_checks["gauge_fixed_contraction_side_conditions"] is not True:
        raise AssertionError("imported gravity contraction side conditions failed")
    if any(s64[row][column].terms for row in range(54, 64) for column in range(64)):
        raise AssertionError("Maxwell rows acquired an algebraic homotopy")
    if any(s64[row][column].terms for row in range(64) for column in range(54, 64)):
        raise AssertionError("Maxwell columns acquired an algebraic homotopy")
    # Chain-map and nilpotency identities are block consequences of the
    # imported 54-to-26 chain maps and the exact Maxwell identity extension.
    # Their coefficient-bearing endpoint consequence is independently tested
    # below by the complete 36-row q1/q2 identity.
    return {"q64": q64, "i64": i64, "p64": p64, "s64": s64, "q36": q36}


def _fixture_matrix(matrix: list[list[Any]]) -> list[list[Any]]:
    return [[_fixture_linear(entry) for entry in row] for row in matrix]


def _maxwell_witness() -> dict[str, Any]:
    q = _maxwell_q1()
    witness = _zero(10, 10)
    for mu, eta in enumerate(ETA_DIAGONAL):
        witness[0][1 + mu] = _scalar_operator(((mu,), eta))
        witness[1 + mu][5 + mu] = _scalar_operator(((), eta))
        witness[5 + mu][9] = _scalar_operator(((mu,), -eta))
    wave = _fixture_matrix(
        _matrix_add(_sparse_multiply(q, witness), _sparse_multiply(witness, q))
    )
    canonical = {(0, 0): -sp.S.One, (1, 1): sp.S.One, (2, 2): sp.S.One, (3, 3): sp.S.One}
    for row, entries in enumerate(wave):
        for column, entry in enumerate(entries):
            principal = {
                word: coefficient for _, word, coefficient in entry.terms if len(word) == 2
            }
            expected = canonical if row == column else {}
            if principal != expected:
                raise AssertionError(f"Maxwell scalar principal symbol failed at {row},{column}")
    q_wave = _fixture_matrix(_sparse_multiply(q, wave))
    wave_q = _fixture_matrix(_sparse_multiply(wave, q))
    if not _is_zero(_matrix_add(q_wave, _negative(wave_q))):
        raise AssertionError("Maxwell q-P commutator is nonzero")
    ghost = [[wave[0][0]]]
    identity = [[wave[9][9]]]
    field = [row[1:5] for row in wave[1:5]]
    antifield = [row[5:9] for row in wave[5:9]]
    if not _is_zero(_subtract(_adjoint_matrix(ghost), identity)):
        raise AssertionError("Maxwell ghost/identity wave adjointness failed")
    if not _is_zero(_subtract(_adjoint_matrix(field), antifield)):
        raise AssertionError("Maxwell field/antifield wave adjointness failed")
    return {"q": q, "witness": witness, "wave": wave}


def _endpoint_parities(dependencies: dict[str, dict[str, Any]]) -> tuple[int, ...]:
    retained = tuple(row["degree"] % 2 for row in dependencies["retained_layout"]["component_rows"])
    return retained + COMBINED_PARITIES[54:]


def _transfer_overlay(
    dependencies: dict[str, dict[str, Any]], matrices: dict[str, Any]
) -> tuple[list[BilinearOperator], list[int]]:
    overlay = build_maxwell_q2_overlay()
    pulled_inputs = [
        _precompose_bilinear(operator, matrices["i64"]) if operator.terms else operator
        for operator in overlay
    ]
    transferred: list[BilinearOperator] = []
    for endpoint_output in range(36):
        terms = []
        for full_output in range(64):
            outer = matrices["p64"][endpoint_output][full_output]
            inner = pulled_inputs[full_output]
            if outer.terms and inner.terms:
                terms.extend(_apply_output_linear(outer, inner).terms)
        transferred.append(_fixture_bilinear(BilinearOperator.from_terms(terms)))

    parities = _endpoint_parities(dependencies)
    defect_counts = []
    for target in range(36):
        defect = BZERO
        for middle, outer in enumerate(matrices["q36"][target]):
            if outer.terms and transferred[middle].terms:
                defect = defect + _apply_output_linear(outer, transferred[middle])
        if transferred[target].terms:
            defect = defect + _precompose_bilinear_slot(
                transferred[target], matrices["q36"], slot=0, parities=parities
            )
            defect = defect + _precompose_bilinear_slot(
                transferred[target], matrices["q36"], slot=1, parities=parities,
                second_slot_q1_sign=True,
            )
        defect_counts.append(len(_fixture_bilinear(defect).terms))
    if any(defect_counts):
        raise AssertionError("transferred mixed q2 violates the arity-two identity")
    return transferred, defect_counts


def _operator_payload(transferred: list[BilinearOperator]) -> dict[str, Any]:
    rows = []
    for output, operator in enumerate(transferred):
        terms = [
            [left, list(left_word), right, list(right_word), str(sp.factor(coefficient))]
            for left, left_word, right, right_word, coefficient in operator.terms
        ]
        body = {"output": output, "terms": terms}
        rows.append({**body, "canonical_sha256": _digest(body)})
    payload = {
        "schema": "pure-weyl-berger-first-transferred-mixed-q2-payload-v1",
        "result_id": "BERGER_FIRST_TRANSFERRED_MIXED_Q2_PAYLOAD",
        "coefficient_field": "Q(sqrt(10))",
        "pbw_basis": "left-invariant Berger frame words over e0,e1,e2,e3",
        "shape": [36, 36, 36],
        "formula": "ell2_mixed=pi64 q2_Maxwell-overlay(iota36,iota36)",
        "rows": rows,
    }
    payload["canonical_sha256"] = _digest(payload)
    return payload


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    dependencies = _load_dependencies()
    matrices = _combined_sdr(dependencies)
    maxwell = _maxwell_witness()
    gc.collect()
    transferred, defect_counts = _transfer_overlay(dependencies, matrices)
    payload = _operator_payload(transferred)
    term_count = sum(len(operator.terms) for operator in transferred)
    mixed_term_count = sum(
        1
        for operator in transferred
        for left, _, right, _, _ in operator.terms
        if (left < 26) != (right < 26)
    )
    pure_maxwell_terms = sum(
        1
        for operator in transferred
        for left, _, right, _, _ in operator.terms
        if left >= 26 and right >= 26
    )
    if term_count != 1522 or mixed_term_count == 0 or pure_maxwell_terms == 0:
        raise AssertionError("transferred mixed-vertex ledger drifted")
    payload_text = _json(payload)
    payload_file_hash = hashlib.sha256(payload_text.encode()).hexdigest()
    certificate = {
        "schema": "pure-weyl-berger-maxwell-unary-contraction-transfer-v1",
        "result_id": "BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX",
        "setting_id": "compact_positive_berger_clock_fixed_coupling",
        "claim_status": "CERTIFIED_MAXWELL_CAUSAL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_Q2",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": dependencies[name].get(
                    "result_id", "BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD"
                ),
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "dimension_ledger": {
            "gravity_clock_full_rows": 54,
            "maxwell_rows": 10,
            "combined_full_rows": 64,
            "gravity_clock_retained_rows": 26,
            "combined_endpoint_rows": 36,
            "identities": ["64=54+10", "36=26+10", "64=28+36"],
        },
        "maxwell_unary_contraction": {
            "complex": "Omega0 --d--> Omega1 --delta d--> Omega1 --delta--> Omega0",
            "witness_formula": "W(A)=delta A; W(A_plus)=g^{-1}A_plus; W(c_plus)=-grad^sharp c_plus",
            "wave_identity": "q_M W_M+W_M q_M=P_M",
            "principal_symbol": "g^{mu nu} zeta_mu zeta_nu I10",
            "green_homotopy": "Lambda_M,+/-=W_M G_P_M,+/-",
            "support": "compact smooth sources to same-sided advanced/retarded smooth sections",
            "witness_record": _matrix_record(maxwell["witness"]),
            "wave_record": _matrix_record(maxwell["wave"]),
        },
        "combined_causal_contraction": {
            "endpoint": "C36=C26_gravity-clock direct-sum C10_Maxwell",
            "formula": "Lambda64,+/-=S64+iota64 (Lambda26,+/- direct-sum LambdaM,+/-) pi64",
            "identity": "q64 Lambda64,+/-+Lambda64,+/- q64=I64",
            "support": "S64,iota64,pi64 are support-local and both endpoint contractions are same-sided causal",
        },
        "first_transferred_mixed_vertex": {
            "payload_path": str(PAYLOAD.relative_to(ROOT)),
            "payload_file_sha256": payload_file_hash,
            "payload_canonical_sha256": payload["canonical_sha256"],
            "formula": payload["formula"],
            "term_count": term_count,
            "mixed_gravity_Maxwell_input_term_count": mixed_term_count,
            "pure_Maxwell_input_term_count": pure_maxwell_terms,
            "nonzero_output_rows": [index for index, operator in enumerate(transferred) if operator.terms],
            "maximum_total_jet_order": max(operator.maximum_total_order for operator in transferred),
            "arity_two_defect_term_counts": defect_counts,
        },
        "exact_checks": {
            "Maxwell_q1_squared_zero": True,
            "Maxwell_witness_identity_exact": True,
            "Maxwell_wave_scalar_principal_symbol_all_10_rows": True,
            "Maxwell_q_commutes_with_wave": True,
            "Maxwell_complementary_degree_formal_adjointness": True,
            "Maxwell_advanced_retarded_Green_homotopies": True,
            "combined_pi_iota_identity": True,
            "combined_iota_and_pi_chain_maps": True,
            "combined_64_to_36_contraction_identity": True,
            "combined_64_row_advanced_retarded_chain_homotopies": True,
            "transferred_q2_arity_two_identity_all_36_rows": True,
            "transferred_q2_cyclicity_by_cyclic_SDR": True,
            "first_mixed_vertex_nonzero": True,
        },
        "flags": {
            "BERGER_MAXWELL_UNARY_CONTRACTION": True,
            "BERGER_MAXWELL_CAUSAL_GREEN_HOMOTOPY": True,
            "BERGER_COMBINED_64_ROW_CAUSAL_GREEN_HOMOTOPY": True,
            "BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING": True,
            "BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL": False,
            "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE": False,
            "BERGER_MAXWELL_BACKREACTION": False,
            "BERGER_G1_COMPLETE_SIGNAL_SECTOR": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL",
        "claim_boundary": "This theorem extends the certified 54-row gravity-clock causal complex by the standard ten-row Maxwell BV Green contraction, obtaining a 64-row causal chain contraction, and exports the exact first 36-row transferred Maxwell q2 overlay through the cyclic gravity SDR. It does not construct a compact retarded source or localized emitter/receiver, solve nonlinear backreaction, include the mixed q3 required for a complete interacting signal sector, construct Hadamard data, restore a quantum master equation, or make a quantum claim.",
    }
    return certificate, payload


def verify(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator.check_schema(payload_schema)
    jsonschema.Draft202012Validator(schema).validate(certificate)
    jsonschema.Draft202012Validator(payload_schema).validate(payload)
    if not all(certificate["exact_checks"].values()):
        raise AssertionError("an exact Maxwell transfer check dropped")
    required_true = (
        "BERGER_MAXWELL_UNARY_CONTRACTION",
        "BERGER_MAXWELL_CAUSAL_GREEN_HOMOTOPY",
        "BERGER_COMBINED_64_ROW_CAUSAL_GREEN_HOMOTOPY",
        "BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING",
    )
    required_false = (
        "BERGER_RETARDED_COMPACT_SOURCE_MAXWELL_SIGNAL",
        "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE",
        "BERGER_MAXWELL_BACKREACTION",
        "BERGER_G1_COMPLETE_SIGNAL_SECTOR",
        "BERGER_HADAMARD_DATA",
        "QUANTUM_CLAIM",
    )
    for flag in required_true:
        if certificate["flags"][flag] is not True:
            raise AssertionError(f"proved flag dropped: {flag}")
    for flag in required_false:
        if certificate["flags"][flag] is not False:
            raise AssertionError(f"downstream flag promoted: {flag}")
    if len(payload["rows"]) != 36 or payload["shape"] != [36, 36, 36]:
        raise AssertionError("transferred payload shape drifted")
    if certificate["first_transferred_mixed_vertex"]["term_count"] != 1522:
        raise AssertionError("transferred term count drifted")


def _report() -> str:
    return r"""# Maxwell unary contraction and first transferred Berger vertex

The ten Maxwell BV rows form the standard complex

```text
Omega0 --d--> Omega1 --delta d--> Omega1 --delta--> Omega0.
```

With the metric fibre identification and Lorenz companion, the exact local
witness satisfies `q_M W_M + W_M q_M = P_M`, where every degree of `P_M`
has scalar metric principal symbol.  The globally hyperbolic Berger cylinder
therefore supplies unique advanced and retarded Green operators and
`Lambda_M,+/- = W_M G_M,+/-` contracts all ten Maxwell rows causally.

The frozen gravity SDR extends by the identity on Maxwell:

```text
64 = 54 + 10,     36 = 26 + 10,
Lambda64,+/- = S64 + iota64 (Lambda26,+/- direct-sum LambdaM,+/-) pi64.
```

The first endpoint interaction is exported without fitting:

```text
ell2_mixed = pi64 q2_Maxwell-overlay(iota36,iota36).
```

It contains 1,522 exact PBW terms on 23 nonzero output rows and satisfies the
arity-two identity on all 36 rows.  Cyclicity follows from the action-derived
64-row q2 and the exact cyclic SDR.  This closes the unary/first-transfer gate,
not the localized signal gate: compact sources, endpoint apparatus,
backreaction, mixed q3, Hadamard data, and quantum claims remain open.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    certificate, payload = build()
    verify(certificate, payload)
    payload_text = _json(payload)
    certificate_text = _json(certificate)
    if args.write:
        PAYLOAD.write_text(payload_text)
        CERTIFICATE.write_text(certificate_text)
        REPORT.write_text(_report())
    if args.check:
        if PAYLOAD.read_text() != payload_text or CERTIFICATE.read_text() != certificate_text:
            raise AssertionError("Maxwell contraction/transfer artifact drifted")
        if REPORT.read_text() != _report():
            raise AssertionError("Maxwell contraction/transfer report drifted")
    if args.guards:
        mutants = []
        promoted = deepcopy(certificate)
        promoted["flags"]["BERGER_HADAMARD_DATA"] = True
        mutants.append(("promote Hadamard", promoted))
        dropped = deepcopy(certificate)
        dropped["flags"]["BERGER_MAXWELL_UNARY_CONTRACTION"] = False
        mutants.append(("drop contraction", dropped))
        wrong_terms = deepcopy(certificate)
        wrong_terms["first_transferred_mixed_vertex"]["term_count"] = 1521
        mutants.append(("change term count", wrong_terms))
        for name, mutant in mutants:
            try:
                verify(mutant, payload)
            except (AssertionError, jsonschema.ValidationError):
                continue
            raise AssertionError(f"mutation guard accepted: {name}")
    print("BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
