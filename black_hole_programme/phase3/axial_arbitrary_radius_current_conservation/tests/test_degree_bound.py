import json

from black_hole_programme.phase3.axial_arbitrary_radius_current_conservation.produce import (
    RADII,
)
from black_hole_programme.phase3.axial_arbitrary_radius_current_conservation.verify import (
    audit_literal_current_bound,
)


EXPECTED = {
    "maximum_numerator_r_degree": 29,
    "maximum_numerator_omega_degree": 13,
    "r": 7,
    "r_minus_2": 6,
    "omega_r_minus_2I": 4,
    "omega_r_plus_2I": 4,
}


def test_conjugate_factor_bound_and_node_count(capsys):
    audited = audit_literal_current_bound()
    print(json.dumps({
        "localized_ring_bound": audited,
        "node_count": len(RADII),
        "first_radius": int(RADII[0]),
        "last_radius": int(RADII[-1]),
    }, sort_keys=True))
    assert audited == EXPECTED
    assert len(RADII) == 30
    assert RADII == list(range(3, 33))
    output = capsys.readouterr().out
    assert '"omega_r_minus_2I": 4' in output
    assert '"omega_r_plus_2I": 4' in output
    assert '"maximum_numerator_r_degree": 29' in output
    assert '"maximum_numerator_omega_degree": 13' in output
    assert '"node_count": 30' in output
