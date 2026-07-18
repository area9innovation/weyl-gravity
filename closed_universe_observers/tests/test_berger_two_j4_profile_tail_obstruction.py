import json
from fractions import Fraction

import mpmath as mp

from closed_universe_observers.generate_berger_two_j4_profile_tail_obstruction import (
    CERTIFICATE,
    DEPENDENCIES,
    IV_DPS,
    build,
    tail_audit,
)


def test_generated_certificate_is_current():
    assert json.loads(CERTIFICATE.read_text()) == build()


def test_two_j4_tail_is_quantitatively_obstructed():
    audit = build()["tail_audit"]
    assert audit["retained_fourier_energy_upper"] == "675"
    assert Fraction(audit["omitted_energy_fraction_lower"]) > Fraction(99999, 100000)


def test_cutoff_dimension_mutation_changes_bound():
    values = {
        name: json.loads(path.read_text())
        for name, path in DEPENDENCIES.items()
    }
    assert tail_audit(values, omit_top_retained_representation=True)["retained_fourier_energy_upper"] != "675"


def test_generation_resets_process_global_interval_precision():
    expected = build()
    mp.iv.dps = 15
    try:
        assert build() == expected
    finally:
        mp.iv.dps = IV_DPS
