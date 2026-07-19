"""Independent verifier for the candidate-13 pure-extra Taub join."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_pure_extra_taub_join.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_pure_extra_taub_join.schema.json"
INCIDENCE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_L4_incidence_reduction.json"
TAUB = ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    value = json.loads(CERTIFICATE.read_text())
    jsonschema.validate(value, json.loads(SCHEMA.read_text()))
    if value["schema_sha256"] != sha(SCHEMA):
        raise AssertionError("candidate-13 Taub-join schema hash changed")
    expected_inputs = {
        str(INCIDENCE.relative_to(ROOT)): sha(INCIDENCE),
        str(TAUB.relative_to(ROOT)): sha(TAUB),
    }
    if value["provenance"]["inputs"] != expected_inputs:
        raise AssertionError("candidate-13 Taub-join provenance changed")
    incidence = json.loads(INCIDENCE.read_text())
    taub = json.loads(TAUB.read_text())
    if not incidence["classification"]["candidate_13_ideal_prime"]:
        raise AssertionError("candidate-13 prime input was demoted")
    if "two multiplicity-two p_extra source branches" not in incidence["scope"]["carrier"]:
        raise AssertionError("candidate-13 carrier is not purely p-primary")
    generic = taub["generic_moment_maps"]["generic_extra_H_Taub"]
    if generic["axial_p_primary_Gram_inertia"] != [2, 0] or generic["polar_p_primary_Gram_inertia"] != [2, 0]:
        raise AssertionError("candidate-13 extra Gram positivity changed")
    omega_1_sq, omega_2_sq = sp.symbols("omega_1_sq omega_2_sq", positive=True)
    norms = sp.symbols("norm_1 norm_2", nonnegative=True)
    mu_h = -(omega_1_sq * norms[0] + omega_2_sq * norms[1])
    if not (mu_h.subs({norms[0]: 1, norms[1]: 0}) < 0 and mu_h.subs({norms[0]: 0, norms[1]: 1}) < 0):
        raise AssertionError("candidate-13 negative-definite sum changed")
    flags = value["classification"]
    if not (
        flags["candidate_13_resonance_Taub_common_zero_is_origin"]
        and flags["candidate_13_nonzero_pure_extra_bounded_extension_obstructed"]
        and flags["candidate_13_nonzero_pure_extra_smooth_secular_extension_obstructed"]
    ):
        raise AssertionError("candidate-13 Taub join was weakened")
    if (
        flags["candidate_13_same_fibre_source_matrices_classified"]
        or flags["mixed_Einstein_extra_two_fibre_cone_classified"]
        or flags["causal_residual_observational_or_quantum_claim"]
    ):
        raise AssertionError("candidate-13 Taub join exceeded scope")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_PURE_EXTRA_TAUB_JOIN independent verification: PASS")


if __name__ == "__main__":
    verify()
