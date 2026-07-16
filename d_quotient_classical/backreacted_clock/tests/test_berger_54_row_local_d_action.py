from d_quotient_classical.backreacted_clock.berger_54_row_local_d_action import (
    Berger54RowLocalDAction,
    _guards,
)
from d_quotient_classical.backreacted_clock.verify_berger_54_row_local_d_action import verify


def test_complete_local_d_action() -> None:
    result = Berger54RowLocalDAction.build()
    assert result.payload["row_layout"]["total_rows"] == 54
    assert result.payload["flags"]["BERGER_LOCAL_D_ACTION_EQUIVARIANT"] is True
    assert result.payload["flags"]["CLASSICAL_SUPPORT_LOCAL_Q2"] is False


def test_mutation_guards() -> None:
    _guards(Berger54RowLocalDAction.build())


def test_independent_consumer() -> None:
    verify()
