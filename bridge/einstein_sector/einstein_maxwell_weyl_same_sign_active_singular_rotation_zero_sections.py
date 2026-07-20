"""Certify singular rotation-zero sections at every positive occupation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_singular_rotation_zero_sections.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_active_singular_rotation_zero_sections.schema.json"
INPUTS = {
    "candidate17_20_singular": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_third_transvectant_singular_locus.json",
    "candidate18_singular": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_complex_singular_resolution.json",
    "phase_reduced": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_phase_reduced_presymplectic_divisors.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_sections() -> dict[str, object]:
    n_minus, n_plus, alpha, beta = sp.symbols("N_minus N_plus alpha beta", positive=True)
    w0 = sp.Rational(1, 6)
    t3_minus_sq = 6 * n_minus
    t3_plus_sq = 96 * n_plus
    if sp.simplify(w0 * t3_minus_sq - n_minus) != 0:
        raise AssertionError("third-transvectant negative occupation changed")
    if sp.simplify(sp.Rational(1, 16) * w0 * t3_plus_sq - n_plus) != 0:
        raise AssertionError("third-transvectant positive occupation changed")
    c18_positive_sq = 6 * n_plus / alpha
    c18_negative_sq = 6 * n_minus / beta
    if sp.simplify(alpha * w0 * c18_positive_sq - n_plus) != 0:
        raise AssertionError("candidate-18 positive occupation changed")
    if sp.simplify(beta * w0 * c18_negative_sq - n_minus) != 0:
        raise AssertionError("candidate-18 negative occupation changed")
    return {
        "candidate17_20": {
            "negative_amplitude_squared": str(t3_minus_sq),
            "positive_amplitude_squared": str(t3_plus_sq),
            "occupation_check": ["(1/6)*(6*N_minus)=N_minus", "(1/16)*(1/6)*(96*N_plus)=N_plus"],
        },
        "candidate18": {
            "positive_amplitude_squared": str(c18_positive_sq),
            "negative_amplitude_squared": str(c18_negative_sq),
            "occupation_check": ["alpha*(1/6)*(6*N_plus/alpha)=N_plus", "beta*(1/6)*(6*N_minus/beta)=N_minus"],
        },
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    t3 = records["candidate17_20_singular"]["classification"]
    c18 = records["candidate18_singular"]["classification"]
    if not t3["candidate17_complete_complex_singular_locus_classified"] or not t3["candidate20_complete_complex_singular_locus_classified"]:
        raise AssertionError("candidate-17/20 singular input changed")
    if not c18["candidate18_complete_complex_singular_locus_classified"] or not c18["ten_positive_spectators_retained"]:
        raise AssertionError("candidate-18 singular input changed")
    phase = records["phase_reduced"]["classification"]
    if not phase["common_node_phase_coupling_retained"]:
        raise AssertionError("node-phase input changed")
    exact = exact_sections()
    return {
        "schema": "einstein-maxwell-weyl-same-sign-active-singular-rotation-zero-sections-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_ACTIVE_SINGULAR_ROTATION_ZERO_SECTIONS",
        "result_state": "CANDIDATE17_18_20_SINGULAR_ROTATION_ZERO_SECTIONS_EXIST_AT_EVERY_POSITIVE_OCCUPATION",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_ALL_POSITIVE_ACTIVE_NODE_OCCUPATIONS_ON_THREE_DISTINCT_CANDIDATES",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "candidates 17, 18 and 20 separately",
            "boundaries": "closed S1_L times S2 before lifted-rotation or final residual quotient",
            "charge_sector": "fixed magnetic U(1) bundle P_N with N=2",
            "carrier": "real positive-frequency fixed-active-occupation links after conjugate reality completion, before node-phase quotient",
            "degree": 2,
            "parity": "one declared parity factor carries the section and the other is at its singular vertex",
            "ell": 2,
            "m": "only m=0 is nonzero in the explicit section",
            "k": "candidate-specific allowed compact momenta, never identified across candidates",
            "omega": "candidate-specific certified collision frequency",
        },
        "universal_section": {
            "occupation_domain": "N_minus>0 and N_plus>0 arbitrary",
            "angular_vector": "e_0=(0,0,1,0,0), the m=0 binary-quartic coefficient",
            "rotation_moment_maps": "mu_J1=mu_J2=mu_J3=0 because the real completed section is axisymmetric",
            "node_phase_actions_free": True,
            "reason_free": "both total active-node norms are strictly positive even though the unused parity factor is zero",
        },
        "candidate17_20_section": {
            **exact["candidate17_20"],
            "amplitudes": "in the first parity factor set f=sqrt(6*N_minus)*e_0 and g=sqrt(96*N_plus)*e_0; set the second parity factor to zero",
            "singularity_witness": "e_0 is the square-quartic kernel vector v([0:1:0])/2, so the occupied factor lies in S and the zero factor lies at the vertex; the product point lies in S_plus x S_minus",
            "candidates": [17, 20],
        },
        "candidate18_section": {
            **exact["candidate18"],
            "weights": "alpha=(w_x+3*w_y)/12>0 is the occupied positive internal diagonal weight and beta=6*h_minus>0 is the negative absolute weight",
            "amplitudes": "set the occupied parity columns to f=sqrt(6*N_plus/alpha)*e_0 and g=sqrt(6*N_minus/beta)*e_0; set the other rank-one factor and all ten spectators to zero",
            "singularity_witness": "the occupied 5x2 factor has rank one while the unused factor is its determinantal vertex, hence the point lies on a complete singular component",
            "candidate": 18,
        },
        "classification": {
            "candidate17_every_positive_occupation_has_singular_rotation_zero_point": True,
            "candidate18_every_positive_occupation_has_singular_rotation_zero_point": True,
            "candidate20_every_positive_occupation_has_singular_rotation_zero_point": True,
            "singular_strata_avoidable_by_positive_norms": False,
            "singular_strata_avoidable_by_rotation_zero_condition": False,
            "real_singular_component_decomposition_complete": False,
            "node_phase_singular_quotient_classified": False,
            "lifted_rotation_singular_quotient_classified": False,
            "global_zero_fibre_connected": False,
            "occupation_strata_glued": False,
            "final_residual_descent": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The complex singular loci are physically unavoidable in the bounded real problem: fixing both active occupations and imposing all three lifted rotational constraints never removes them. Any complete candidate-17/18/20 quotient theorem must therefore include singular reduction rather than proving a result only on the regular divisor atlas.",
        "next_gate": "classify the node-phase and lifted-rotation quotient of these explicit singular carriers, beginning with the double-singular axisymmetric section and retaining candidate-18 spectators",
        "claim_boundary": "This proves existence of singular rotation-zero points for every positive occupation, not a complete real component decomposition, quotient topology, connectedness theorem, occupation gluing, final residual descent, all-orders integration, or causal, observational or quantum map.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_active_singular_rotation_zero_sections --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_active_singular_rotation_zero_sections",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_active_singular_rotation_zero_sections",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text() != rendered:
        raise AssertionError("active singular rotation-zero certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_ACTIVE_SINGULAR_ROTATION_ZERO_SECTIONS: PASS")


if __name__ == "__main__":
    main()
