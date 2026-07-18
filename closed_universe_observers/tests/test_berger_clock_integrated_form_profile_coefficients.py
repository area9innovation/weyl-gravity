import json
from pathlib import Path
from closed_universe_observers.generate_berger_clock_integrated_form_profile_coefficients import build

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "closed_universe_observers/certificates/BERGER_CLOCK_INTEGRATED_FORM_PROFILE_COEFFICIENTS.json"

def test_generated_certificate_is_current():
    assert build() == json.loads(CERT.read_text())

def test_claim_boundary_stays_fail_closed():
    value = json.loads(CERT.read_text()); flags = value["flags"]
    assert flags["SPATIAL_CODERIVATIVE_COEFFICIENTS_TWO_J0_TO_4_EXPORTED"]
    assert not flags["FULL_FOUR_DIMENSIONAL_TIME_KERNEL_WEIGHTED_SOURCE_COEFFICIENTS_EVALUATED"]
    assert not flags["VALIDATED_INFINITE_MODE_TAIL_BOUND_EXPORTED"]
    assert value["mutation_results"][0]["detected"]
