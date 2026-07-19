"""Independent verifier for the candidate-13 mixed null witness."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_moment_resonance_null_witness.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_moment_resonance_null_witness.schema.json"
INPUTS = [
    ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.json",
    ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json",
    ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    value = json.loads(CERTIFICATE.read_text())
    jsonschema.validate(value, json.loads(SCHEMA.read_text()))
    if value["schema_sha256"] != sha(SCHEMA):
        raise AssertionError("mixed-witness schema hash changed")
    expected = {str(path.relative_to(ROOT)): sha(path) for path in INPUTS}
    if value["provenance"]["inputs"] != expected:
        raise AssertionError("mixed-witness provenance changed")

    rho = (-sp.Integer(250) + 461 * sp.sqrt(10)) / 2132
    q1 = sp.sqrt(rho + 6 - 2 * sp.sqrt(3))
    q2 = sp.sqrt(4 * rho + 6 - 2 * sp.sqrt(3))
    p1 = sp.sqrt(rho + sp.Rational(16, 3))
    Q1, Q2, P1 = sp.symbols("Q1 Q2 P1", nonzero=True)
    y1 = P1 * (2 * P1 + Q2) / (Q1 * (2 * Q1 + Q2))
    y2 = P1 * (P1 - Q1) / (Q2 * (2 * Q1 + Q2))
    if sp.cancel(Q1**2 * y1 + Q2**2 * y2 - P1**2) != 0:
        raise AssertionError("H cancellation failed")
    if sp.cancel(Q1 * y1 - 2 * Q2 * y2 - P1) != 0:
        raise AssertionError("P_x cancellation failed")
    rho_lower_exact = 461**2 * 10 > 1316**2
    rho_upper_exact = 2305**2 * 10 < 7646**2
    p_exceeds_q_exact = 2**2 * 3 > sp.Rational(2, 3) ** 2
    if not (rho_lower_exact and rho_upper_exact and p_exceeds_q_exact):
        raise AssertionError("exact positivity failed")

    occupation = value["occupation_witness"]
    if occupation["p_primary_n_minus2"] != "0" or value["scope"]["m"] != 0:
        raise AssertionError("resonance-null/rotation support changed")
    flags = value["classification"]
    if not all(
        flags[key]
        for key in [
            "nonzero_real_mixed_witness_certified",
            "all_five_stabilizer_moment_maps_zero",
            "candidate_13_cross_fibre_resonance_functionals_zero",
            "candidate_13_mixed_Taub_resonance_common_zero_nontrivial",
        ]
    ):
        raise AssertionError("mixed witness was weakened")
    if any(
        flags[key]
        for key in [
            "same_fibre_resonance_functionals_classified",
            "complete_mixed_two_fibre_tangent_cone_classified",
            "bounded_or_smooth_second_order_extension_certified",
            "causal_residual_observational_or_quantum_claim",
        ]
    ):
        raise AssertionError("mixed witness exceeded scope")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_MIXED_MOMENT_RESONANCE_NULL_WITNESS independent verification: PASS")


if __name__ == "__main__":
    verify()
