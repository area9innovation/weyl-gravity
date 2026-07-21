#!/usr/bin/env python3
"""Independent native-coderivation replay of the ell3 witness disposition."""

from __future__ import annotations

import json

import sympy as sp

from d_quotient_classical.backreacted_clock import (
    berger_positive_jet_super_cotangent_redefinition_convention as lift,
)
from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_order_two_full_bv_redefinition as core,
)
from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_positive_jet_full_bv_obstruction as old,
)
from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_second_jet_witness_disposition as disposition,
)


def replay(word: tuple[int, ...]) -> tuple[int, int, sp.Expr]:
    old_value = json.loads(old.OUTPUT.read_text())
    weights = {
        old._actual_first_key(record): old._coefficient(str(record["coefficient"]))
        for record in old_value["obstruction_witness"]["weights"]
        if int(record["page"]) == 1
    }
    column = lift.cotangent_column(4, ((27, word), (28, ())))
    f2, f3 = core.jet_taylor_vectors(column, {})
    q1, q2, _ = core.retained_operations()
    page = core.coderivation_coboundary_page_streaming(f2, f3, 1, q1=q1, q2=q2)
    pairing = sp.factor(sum(weights.get(key, 0) * value for key, value in page.items()))
    return len(column), len(page), pairing


def verify() -> dict[str, object]:
    value = json.loads(disposition.OUTPUT.read_text())
    disposition.validate(value)
    components, terms, pairing = replay((1, 1))
    if (components, terms, pairing) != (5, 252, sp.Rational(755, 9)):
        raise ValueError("independent native counterexample replay failed")
    if replay((0, 0))[2] != 0:
        raise ValueError("control word mutation did not kill the pairing")
    if value["exact_counterexample"]["old_witness_pairing"] != str(pairing):
        raise ValueError("stored pairing drifted")
    if value["full_class_disposition"]["complete_order_two_bounded_cyclic_complex"] != "OPEN":
        raise ValueError("full class was promoted after witness invalidation")
    print("BERGER_RETAINED_MIXED_ELL3_SECOND_JET_WITNESS_DISPOSITION_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
