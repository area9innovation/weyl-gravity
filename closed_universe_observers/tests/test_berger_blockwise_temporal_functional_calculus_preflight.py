from fractions import Fraction

from closed_universe_observers.generate_berger_blockwise_temporal_functional_calculus_preflight import (
    INTERNAL_CLOCK_SCALE,
    build,
    microphase_audit,
)


def test_internal_clock_scale_reduces_the_bad_global_tail() -> None:
    value = build()
    audit = value["microphase_remainder_audit"]
    assert INTERNAL_CLOCK_SCALE == Fraction(1, 48)
    assert Fraction(audit["cosine_geometric_ratio"]) < Fraction(1, 100)
    assert Fraction(audit["Delta1_cosine_microphase_remainder_upper"]) < Fraction(1, 10**17)
    assert Fraction(value["mutation_results"][0]["mutated_cosine_remainder_upper"]) > 1


def test_microphase_rejects_full_tau_substitution() -> None:
    value = build()
    row = value["microphase_remainder_audit"]
    lambda0 = Fraction(row["Delta0_infinity_norm_upper"])
    lambda1 = Fraction(row["Delta1_infinity_norm_upper"])
    assert microphase_audit(lambda0, lambda1) == row
    assert value["large_T_disposition"]["no_T_taylor_truncation"] is True
