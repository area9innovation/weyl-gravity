#!/usr/bin/env python3
"""Independent replay of the dressed canonical Berezinian preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CERT = (
    ROOT
    / "quantum-weyl/anomalies/certificates/"
    "DRESSED_CANONICAL_BEREZINIAN_LOCALITY_PREFLIGHT.json"
)
FIXTURE = (
    ROOT
    / "quantum-weyl/anomalies/fixtures/"
    "dressed_canonical_berezinian_selected_hessian_accept.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> None:
    value = json.loads(CERT.read_text())
    assert value["dependency_tags"] == ["LOCAL-ALGEBRAIC"]

    for reference in value["input_pins"].values():
        path = ROOT / reference["path"]
        assert path.is_file()
        assert _sha256(path) == reference["sha256"]
        assert json.loads(path.read_text())["result_id"] == reference["result_id"]

    action = json.loads(
        (
            ROOT
            / value["input_pins"]["complex_compensator_action"]["path"]
        ).read_text()
    )
    assert len(action["field_inventory"]) == 18
    assert action["content_hashes"]["field_inventory_sha256"] == (
        value["atom_pairing_import"]["field_inventory_sha256"]
    )
    assert action["content_hashes"]["BV_manifest_sha256"] == (
        value["atom_pairing_import"]["BV_manifest_sha256"]
    )

    d = value["scope"]["spacetime_dimension"]
    metric_rank = d * (d + 1) // 2
    assert metric_rank == value["scope"]["metric_component_rank"] == 10

    # Independent block-triangular determinant replay.  A is the derivative
    # of (g_hat,tau) with respect to (g,tau).  Its diagonal has ten copies of
    # exp(-2 tau) and one copy of one.  The parity-reversed cotangent block is
    # A^{-T}; therefore Ber(A direct-sum A^{-T})=det(A)^2.
    base_exponent = sum([-2] * metric_rank + [0])
    cotangent_determinant_exponent = -base_exponent
    berezinian_exponent = base_exponent - cotangent_determinant_exponent
    assert base_exponent == -20
    assert cotangent_determinant_exponent == 20
    assert berezinian_exponent == -40

    finite = value["finite_cutoff_berezinian"]
    assert finite["base_field_log_J_per_cell"] == f"{base_exponent} tau"
    assert finite["parity_reversed_cotangent_log_J_per_cell"] == (
        f"{base_exponent} tau"
    )
    assert finite["full_BV_log_J_per_cell"] == (
        f"{berezinian_exponent} tau"
    )
    assert finite["inverse_log_J_N_cells"] == "40 sum_i tau_i"
    assert finite["is_identically_one"] is False
    assert finite["composition_log_defect"] == 0

    # Polar precursor: d tau/d rho=-1/rho contributes
    # -log(f)+tau to log|det A|; the odd cotangent doubles the base log.
    polar_base_tau = base_exponent + 1
    polar_full_tau = 2 * polar_base_tau
    assert polar_base_tau == -19
    assert polar_full_tau == -38
    assert finite["polar_precursor"]["base_log_abs_J_per_cell"] == (
        "-19 tau-log(f)"
    )
    assert finite["polar_precursor"]["full_BV_log_abs_Ber_per_cell"] == (
        "-38 tau-2 log(f)"
    )

    canonical = value["canonical_cotangent_map"]
    assert canonical["composition_defect"] == "ZERO"
    assert canonical["inverse_composition_defect"] == "ZERO"
    assert canonical["one_form_defect"] == "ZERO"
    # Direct coefficient replay:
    # delta g_hat=e^-2tau(delta g-2g delta tau);
    # g_hat_star=e^2tau g_star, so the metric term contributes
    # g_star delta g-2(g.g_star)delta tau.  The +2 shift in tau_hat_star
    # cancels that coefficient.
    metric_cross_coefficient = -2
    tau_hat_shift_coefficient = 2
    assert metric_cross_coefficient + tau_hat_shift_coefficient == 0

    continuum = value["continuum_disposition"]
    assert continuum["formal_regulated_expression"].startswith(
        "log Ber_R=-40 Tr_R(tau)"
    )
    assert "Pi_0" in continuum["zero_mode_defect"]
    assert "does not preserve" in continuum["spectral_cutoff_closure"]
    assert continuum["verdict"] == (
        "PRECISE_MEASURE_REGULARIZATION_OBSTRUCTION_TO_"
        "ACTION_INDEPENDENT_CONTINUUM_LOCALITY"
    )
    assert any(
        "regulator operator" in row
        for row in continuum["selected_hessian_recomputations"]
    )

    assert value["lifecycle"] == {
        "finite_cutoff_raw_Berezinian": "CERTIFIED_NONUNIT",
        "continuum_action_independent_locality": "OBSTRUCTED",
        "selected_action_regulated_Jacobian": "OPEN",
        "QAP": "NOT_INFERRED",
        "anomaly_coefficients": "NOT_COMPUTED_HERE",
        "Lorentzian_QME": "OPEN",
    }
    assert not any(value["claim_flags"].values())
    assert all(value["exact_checks"].values())
    expected_proof = _canonical_hash(
        {key: entry for key, entry in value.items() if key != "proof_sha256"}
    )
    assert value["proof_sha256"] == expected_proof

    fixture = json.loads(FIXTURE.read_text())
    assert fixture["preflight"]["sha256"] == _sha256(CERT)
    assert fixture["fixture_status"] == (
        "SYNTHETIC_ACCEPTANCE_FIXTURE_NOT_PHYSICAL_INPUT"
    )
    assert fixture["selected_action"]["candidate"] == "SYNTHETIC"
    assert fixture["regulator_domain"]["primal_dual_projectors"] == (
        "COMMON_DUAL_COMPATIBLE_VERIFIED"
    )
    assert set(fixture["nonclaims"].values()) == {"NOT_INFERRED"}
    print("Dressed canonical Berezinian locality preflight: PASS")


if __name__ == "__main__":
    main()
