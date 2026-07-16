from d_quotient_classical.backreacted_clock.berger_54_row_causal_homotopy_reduction import (
    Berger54RowCausalHomotopyReduction,
    _guards,
)
from d_quotient_classical.backreacted_clock.verify_berger_54_row_causal_homotopy_reduction import verify


def test_complete_causal_problem_reduces_to_retained_endpoint() -> None:
    result = Berger54RowCausalHomotopyReduction.build()
    assert result.payload["dimension_ledger"]["identity"] == "54=28+26"
    assert result.payload["flags"]["BERGER_54_ROW_CAUSAL_REDUCTION"] is True
    assert result.payload["flags"]["BERGER_CAUSAL_GREEN_HOMOTOPY"] is False


def test_mutation_guards() -> None:
    _guards(Berger54RowCausalHomotopyReduction.build())


def test_independent_consumer() -> None:
    verify()
