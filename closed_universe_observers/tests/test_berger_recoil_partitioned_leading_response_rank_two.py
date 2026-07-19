from fractions import Fraction

from closed_universe_observers.berger_recoil_interval_stream import (
    ComplexRationalInterval,
    RationalInterval,
)
from closed_universe_observers.berger_recoil_partitioned_massive_preparation import (
    evaluate_partitioned_matrix_green_endpoint,
)
from closed_universe_observers.generate_berger_recoil_partitioned_leading_response_rank_two import (
    build,
)


def _point(value: int) -> ComplexRationalInterval:
    return ComplexRationalInterval.point(value)


def test_partitioned_endpoint_integrates_polynomial_kernel_exactly():
    result = evaluate_partitioned_matrix_green_endpoint(
        source_coefficients=[[_point(1)], [_point(1)]],
        source_remainder_upper=Fraction(0),
        kernel_stage={
            "label": "K(tau)=tau",
            "coefficient_matrices": [[[_point(0)]], [[_point(1)]]],
            "uniform_remainder_upper": Fraction(0),
        },
        slab_length=Fraction(1),
        cells=[
            (Fraction(0), Fraction(1, 2), RationalInterval.point(2)),
            (Fraction(1, 2), Fraction(1), RationalInterval.point(2)),
        ],
    )
    value = result["endpoint_vector"][0]
    assert value["real"]["lower"] == "4/3"
    assert value["real"]["upper"] == "4/3"
    assert value["imaginary"]["lower"] == "0"
    assert result["uniform_remainder_upper"] == "0"


def test_partition_refinement_certifies_both_diagonal_responses():
    value = build()
    coarse = {detector: rows[0] for detector, rows in value["partition_refinement_rails"].items()}
    refined = {detector: rows[-1] for detector, rows in value["partition_refinement_rails"].items()}
    assert not any(
        row["positive_energy_lower_bound"]["strictly_positive"]
        for row in coarse.values()
    )
    assert all(
        row["positive_energy_lower_bound"]["strictly_positive"]
        for row in refined.values()
    )
    assert value["green_adjoint_response"]["rank"] == 2
    for witness in value["positive_energy_witnesses"].values():
        assert witness["peter_weyl_weight"] == (
            "(two_j+1)/Vol_Berger=1/(16*pi^2*c) for two_j=0"
        )
        assert witness["berger_volume"] == (
            "Vol_Berger=16 pi^2 c with c=3 sqrt(10)/20"
        )
        assert witness["strictly_positive"]
    assert value["flags"][
        "FINITE_DETECTOR_SELECTED_LEADING_RESPONSE_RANK_TWO_ON_MASS_DOMAIN"
    ]
    assert not value["flags"]["ARBITRARY_POSITIVE_MASS_DOMAIN_CERTIFIED"]
    assert not value["flags"]["FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED"]
