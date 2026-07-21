from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_PAYLOAD_V1.json"


def test_retuning_family_is_complete_and_one_shape_dimensional() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    assert certificate["parameter_summary"]["stationary_family_dimension"] == 3
    assert certificate["parameter_summary"]["spectral_shape_dimension"] == 1


def test_hamiltonian_hopf_sector_persists_and_is_physical() -> None:
    payload = json.loads(PAYLOAD.read_text())
    assert payload["terminal_verdict"]["entire_component_Hamiltonian_Hopf"] is True
    assert payload["terminal_verdict"]["stable_exact_retuned_fixture"] is None
    assert payload["unstable_residue_pairing"]["residue_nondegenerate_on_component"] is True
    assert payload["unstable_energy_signature"]["two_copy_inertia_positive_negative_zero"] == [4, 4, 0]


def test_collision_and_causal_boundaries_fail_closed() -> None:
    payload = json.loads(PAYLOAD.read_text())
    assert len(payload["spectral_classification"]["isolated_cross_factor_collisions"]) == 3
    assert payload["charge_and_causal_gates"]["familywide_full_Green_homotopy"] == "NO_CERTIFIED_MAP"
    assert payload["terminal_verdict"]["retuned_all_isotype_programme_activated"] is False
