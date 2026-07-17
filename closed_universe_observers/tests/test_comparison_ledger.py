from closed_universe_observers import verify_comparison_ledger as verifier


def test_comparison_ledger_is_fail_closed() -> None:
    assert verifier.main() == 0
