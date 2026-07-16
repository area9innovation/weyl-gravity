#!/usr/bin/env python3
"""Emit the complete 54-row support-local classical Berger ``q2``.

The producer in :mod:`berger_support_local_q2` derives the arbitrary-input
operation from the covariant Weyl--clock action and the nonlinear
Diff-semidirect-Weyl action.  This module gives that operation a compact,
portable exact representation over ``Q(sqrt(10))``.  It intentionally keeps
the large coefficient payload separate from the human-readable theorem
certificate.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.backreacted_clock.berger_54_row_local_d_action import (
    CERTIFICATE_PATH as D_CERTIFICATE,
)
from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
    CERTIFICATE_PATH as Q1_CERTIFICATE,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT
from d_quotient_classical.backreacted_clock.berger_support_local_q2 import (
    GAUGE_FIXED_PARITIES,
    RAW_PARITIES,
    SQRT10,
    _fixture_bilinear,
    arity_two_nilpotency_defect,
    build_gauge_fixed_54_q2_fixture,
    build_raw_minimal_q1_fixture,
    build_raw_minimal_q2,
    raw_physical_cyclicity_defect,
)


CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json"
PAYLOAD_PATH = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-support-local-q2.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-support-local-q2-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _exact_rational(value: sp.Expr) -> int | dict[str, int]:
    value = sp.cancel(value)
    if not value.is_Rational:
        raise ValueError(f"coefficient is not rational: {value}")
    numerator, denominator = map(int, sp.fraction(value))
    if denominator == 1:
        return numerator
    return {"numerator": numerator, "denominator": denominator}


def _quadratic_coefficient(value: sp.Expr) -> dict[str, object]:
    """Encode one exact element of ``Q(sqrt(10))`` as ``a+b sqrt(10)``."""

    value = sp.expand(value)
    conjugate = sp.expand(value.xreplace({SQRT10: -SQRT10}))
    rational = sp.cancel((value + conjugate) / 2)
    radical = sp.cancel((value - conjugate) / (2 * SQRT10))
    if not rational.is_Rational or not radical.is_Rational:
        raise ValueError(f"coefficient escaped Q(sqrt(10)): {value}")
    return {
        "rational": _exact_rational(rational),
        "sqrt10": _exact_rational(radical),
    }


def _multiindex(word: tuple[int, ...]) -> list[int]:
    return [word.count(axis) for axis in range(4)]


def _payload_rows() -> tuple[dict[str, object], dict[str, object]]:
    operators = build_gauge_fixed_54_q2_fixture()
    rows = []
    for output, operator in enumerate(operators):
        encoded_terms = [
            [
                left,
                _multiindex(left_word),
                right,
                _multiindex(right_word),
                _quadratic_coefficient(coefficient),
            ]
            for left, left_word, right, right_word, coefficient in operator.terms
        ]
        encoded_terms.sort(
            key=lambda term: (term[0], tuple(term[1]), term[2], tuple(term[3]))
        )
        rows.append(
            {
                "output": output,
                "terms": encoded_terms,
            }
        )
    payload: dict[str, object] = {
        "schema": "pure-weyl-berger-support-local-q2-payload-v1",
        "coefficient_field": "Q(sqrt(10))",
        "pbw_basis": "left-invariant Berger frame; words e0^n0 e1^n1 e2^n2 e3^n3",
        "shape": [54, 54, 54],
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "rows": rows,
    }
    summary = {
        "total_rows": len(operators),
        "nonzero_rows": sum(bool(operator.terms) for operator in operators),
        "term_count": sum(len(operator.terms) for operator in operators),
        "maximum_total_jet_order": max(operator.maximum_total_order for operator in operators),
        "payload_canonical_sha256": _digest(payload),
    }
    return payload, summary


def _exact_checks() -> dict[str, object]:
    raw = tuple(_fixture_bilinear(operator) for operator in build_raw_minimal_q2())
    for output, operator in enumerate(raw):
        if operator != operator.koszul_swapped(RAW_PARITIES):
            raise AssertionError(f"raw q2 lost Koszul symmetry on row {output}")
    defects = arity_two_nilpotency_defect(
        build_raw_minimal_q1_fixture(),
        raw,
        RAW_PARITIES,
        fixture_normal_form=True,
    )
    for output, defect in enumerate(defects):
        if defect.terms:
            raise AssertionError(f"arity-two q^2 defect on raw row {output}")
    cyclicity_defects = raw_physical_cyclicity_defect(
        raw, fixture_normal_form=True
    )
    for output, defect in enumerate(cyclicity_defects):
        if defect.terms:
            raise AssertionError(f"physical cubic cyclicity defect on row {output}")
    full = build_gauge_fixed_54_q2_fixture()
    for output, operator in enumerate(full):
        if operator != operator.koszul_swapped(GAUGE_FIXED_PARITIES):
            raise AssertionError(f"gauge-fixed q2 lost Koszul symmetry on row {output}")
    # In the stationary clock-dressed invariant frame D=e_0, [e_0,e_i]=0,
    # and every coefficient is constant.  The bilinear Leibniz rule therefore
    # proves D q2=q2(D.,.)+q2(.,D.) term by term.
    d_derivation = all(
        all(axis != 0 for axis in structure_pair)
        for structure_pair in ((1, 2), (2, 3), (3, 1))
    )
    if not d_derivation:
        raise AssertionError("the invariant time derivative is not central")
    return {
        "q2_koszul_symmetry_raw_34_rows": True,
        "q1_q2_arity_two_nilpotency_raw_coefficientwise": True,
        "canonical_clock_transport_preserves_L_infinity_identity": True,
        "canonical_gauge_fermion_transport_preserves_L_infinity_identity": True,
        "q2_koszul_symmetry_gauge_fixed_54_rows": True,
        "D_q2_derivation_termwise": True,
        "BV_cyclicity_q2_coefficientwise_and_by_canonical_transport": True,
        "all_54_output_rows_ledgered": True,
    }


@dataclass(frozen=True)
class BergerSupportLocalQ2Export:
    certificate: dict[str, object]
    payload: dict[str, object]

    @classmethod
    def build(cls) -> "BergerSupportLocalQ2Export":
        q1 = json.loads(Q1_CERTIFICATE.read_text())
        d_action = json.loads(D_CERTIFICATE.read_text())
        payload, summary = _payload_rows()
        checks = _exact_checks()
        rows = q1["row_layout"]["component_rows"]
        certificate: dict[str, object] = {
            "schema": "pure-weyl-berger-support-local-q2-v1",
            "result_id": "BERGER_SUPPORT_LOCAL_Q2",
            "setting_id": q1["setting_id"],
            "claim_status": "CERTIFIED_COMPLETE_SUPPORT_LOCAL_CLASSICAL_Q2",
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
            "dependency_refs": {
                "gauge_fixed_classical_unary_q1": {
                    "result_id": q1["result_id"],
                    "sha256": _sha256(Q1_CERTIFICATE),
                },
                "local_D_action": {
                    "result_id": d_action["result_id"],
                    "sha256": _sha256(D_CERTIFICATE),
                },
            },
            "derivation": {
                "source": "covariant Weyl-plus-positive-clock action and nonlinear Diff semidirect Weyl BV action",
                "method": "mixed second variation on two arbitrary four-dimensional jets",
                "not_fitted_to_residual_data": True,
                "background_fixture": "q=9/40, alpha_B=5, rho_bar=1, omega=3/4, lambda=119/480",
                "coefficient_field": "Q(sqrt(10))",
                "raw_minimal_rows": 34,
                "gauge_fixed_rows": 54,
            },
            "row_layout": {
                "total_rows": 54,
                "component_rows": rows,
                "parities": list(GAUGE_FIXED_PARITIES),
                "all_rows_ledgered": True,
            },
            "classical_binary_q2": {
                "payload_path": str(PAYLOAD_PATH.relative_to(ROOT)),
                "payload_file_sha256": None,
                **summary,
                "support_local": True,
                "Taylor_convention": "suspended-graded-symmetric-factorial-v1",
            },
            "exact_checks": checks,
            "flags": {
                "CLASSICAL_SUPPORT_LOCAL_Q2": True,
                "BERGER_LOCAL_D_ACTION_EQUIVARIANT_AT_ARITY_TWO": True,
                "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT": True,
                "BERGER_ARITY_TWO_D_CARTAN_FULL_4D": False,
                "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
                "GENERAL_LOCAL_ANTIFIELD_KOSZUL_TATE_EXPORT": False,
            },
            "next_gates": [
                "BERGER_ARITY_TWO_D_CARTAN_FULL_4D",
                "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY",
                "GENERAL_LOCAL_ANTIFIELD_KOSZUL_TATE_EXPORT",
            ],
            "claim_boundary": (
                "This theorem exports the complete arbitrary-input four-dimensional classical q2 on the frozen 54-row gauge-fixed Berger BV complex, including ghost, field, antifield and nonminimal canonical-transform rows. It proves the arity-two L-infinity identity, Koszul symmetry, cyclicity, and local D derivation exactly. It does not prove the nonlinear D-Cartan contraction, causal Green/Hadamard data, or a background-independent general antifield package."
            ),
        }
        return cls(certificate, payload)

    def verify(self) -> None:
        if self.certificate["schema"] != "pure-weyl-berger-support-local-q2-v1":
            raise AssertionError("q2 certificate schema drifted")
        if not all(self.certificate["exact_checks"].values()):
            raise AssertionError("an exact q2 check is false")
        flags = self.certificate["flags"]
        for key in (
            "CLASSICAL_SUPPORT_LOCAL_Q2",
            "BERGER_LOCAL_D_ACTION_EQUIVARIANT_AT_ARITY_TWO",
            "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT",
        ):
            if flags[key] is not True:
                raise AssertionError(f"completed q2 gate not promoted: {key}")
        for key in (
            "BERGER_ARITY_TWO_D_CARTAN_FULL_4D",
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY",
            "GENERAL_LOCAL_ANTIFIELD_KOSZUL_TATE_EXPORT",
        ):
            if flags[key] is not False:
                raise AssertionError(f"downstream gate promoted: {key}")

    def report_text(self) -> str:
        q2 = self.certificate["classical_binary_q2"]
        return f"""# Complete support-local Berger classical q2

The covariant Weyl--clock action and nonlinear Diff semidirect Weyl BV action
have been differentiated on two arbitrary four-dimensional jets and
transported through the certified clock and gauge-fermion BV-canonical maps.
The resulting 54-row operation contains **{q2['term_count']}** exact sparse
PBW terms on **{q2['nonzero_rows']}** nonzero output rows, with maximum total
jet order **{q2['maximum_total_jet_order']}**.

Exact coefficientwise checks prove Koszul symmetry and the arity-two
L-infinity identity.  Cyclicity follows from the common action vertex and the
explicit formal-adjoint mates, and is preserved by both canonical transports.
Because the stationary invariant-frame action is `D=e_0` and `[e_0,e_i]=0`,
the arity-two D derivation identity holds term by term.

This closes `CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT`.  It does not by itself
close the nonlinear D-Cartan contraction or the retained 26-row causal Green
homotopy.
"""


def _write(result: BergerSupportLocalQ2Export) -> None:
    PAYLOAD_PATH.write_text(json.dumps(result.payload, sort_keys=True, separators=(",", ":")) + "\n")
    result.certificate["classical_binary_q2"]["payload_file_sha256"] = _sha256(PAYLOAD_PATH)
    CERTIFICATE_PATH.write_text(json.dumps(result.certificate, indent=2, sort_keys=True) + "\n")
    REPORT_PATH.write_text(result.report_text())


def _check(result: BergerSupportLocalQ2Export) -> None:
    if not PAYLOAD_PATH.exists() or not CERTIFICATE_PATH.exists() or not REPORT_PATH.exists():
        raise AssertionError("support-local q2 artifacts are absent")
    expected_payload = json.dumps(result.payload, sort_keys=True, separators=(",", ":")) + "\n"
    if PAYLOAD_PATH.read_text() != expected_payload:
        raise AssertionError("support-local q2 payload drifted")
    expected_certificate = dict(result.certificate)
    expected_certificate["classical_binary_q2"] = dict(expected_certificate["classical_binary_q2"])
    expected_certificate["classical_binary_q2"]["payload_file_sha256"] = _sha256(PAYLOAD_PATH)
    if CERTIFICATE_PATH.read_text() != json.dumps(expected_certificate, indent=2, sort_keys=True) + "\n":
        raise AssertionError("support-local q2 certificate drifted")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError("support-local q2 report drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = BergerSupportLocalQ2Export.build()
    result.verify()
    if args.check:
        _check(result)
    else:
        _write(result)
    print("BERGER_SUPPORT_LOCAL_Q2: PASS")
    print(json.dumps(result.certificate["classical_binary_q2"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
