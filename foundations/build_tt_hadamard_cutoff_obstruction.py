#!/usr/bin/env python3
"""Exact finite algebra for the reduced TT smooth-repair obstruction.

The all-energy distribution argument is a human proof in the companion report;
this producer does not certify microlocal analysis by sampling frequencies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as s

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "foundations/results/TT_HADAMARD_CUTOFF_OBSTRUCTION_V1.json"
INPUTS = (
    "covariant_completion/certificates/branch_residue_operators.json",
    "covariant_completion/certificates/branch_spectrum.json",
    "covariant_completion/certificates/tt_local_factorization.json",
    "quantum-weyl/lorentzian/certificates/VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD.json",
)


def build() -> dict:
    bridge = json.loads((ROOT / INPUTS[-1]).read_text())
    drift = []
    for key, record in bridge["dependencies"].items():
        actual = hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()
        if actual != record["sha256"]:
            drift.append({"dependency": key, "path": record["path"],
                          "expected_sha256": record["sha256"], "actual_sha256": actual})
    n, z = s.symbols("n z")
    e = n - 2
    gap = s.expand(n**2 - e**2)
    # Action -C^2: effective second-order kinetic residues +gap, -gap.
    c_e, c_l = 1 / (2 * e * gap), -1 / (2 * n * gap)
    filt = s.cancel((e**2 - z**2) / (e**2 - n**2))
    assert s.simplify(filt.subs(z, n) - 1) == 0
    assert s.simplify(filt.subs(z, e)) == 0
    assert s.simplify(filt.subs(z, -e)) == 0
    rows = []
    for energy in (4, 5, 8, 16, 64, 256):
        ce, cl = c_e.subs(n, energy), c_l.subs(n, energy)
        rows.append({
            "L_frequency": energy,
            "E_frequency": energy - 2,
            "curl_squared_eigenvalue": (energy - 1)**2,
            "reference_coefficients": [str(ce), str(cl), "0"],
            "finite_repair_coefficients": ["0", str(-cl), str(-cl)],
            "repaired_coefficients": [str(ce), "0", str(-cl)],
            "filtered_reference_expectation": str(cl),
            "necessary_B_squared_M_for_nonnegative_test": str(-cl * (energy - 1)**4),
        })
    m = s.symbols("m")
    # Positive coefficients after n=m+4 give an exact all-integer sign witness.
    def coefficients(expr):
        return [str(x) for x in reversed(s.Poly(s.expand(expr.subs(n, m + 4)), m).all_coeffs())]
    return {
        "schema_version": "tt-hadamard-cutoff-obstruction-v1",
        "result_id": "TT_HADAMARD_CUTOFF_OBSTRUCTION_V1",
        "input_source_commit": "08bf00a7c15e9593ad64f4a91dd7a03623ae222f",
        "dependency_tags": ["REDUCED-MODE"],
        "evidence_status": "HUMAN_ANALYTIC_PROOF_WITH_EXACT_ALGEBRA_REPLAY",
        "import_audit": {
            "reference_gate": "FAIL_DEPENDENCY_DRIFT" if drift else "HASHES_MATCH_ONLY",
            "drift": drift,
            "consequence": "Proof is for the explicitly stated spectral model; current programme activation is withheld.",
        },
        "scope": "free reduced physical TT metric carrier on unit R x S3; action -alpha_g integral C^2, alpha_g=1",
        "inputs": [{"path": p, "sha256": hashlib.sha256((ROOT / p).read_bytes()).hexdigest()} for p in INPUTS],
        "formulas": {
            "frequency_domain": "integer n >= 4",
            "E_frequency": str(e),
            "gap": str(gap),
            "positive_E_coefficient": str(s.factor(c_e)),
            "negative_L_coefficient": str(s.factor(c_l)),
            "filter_denominator": str(-gap),
            "fourier_filter": str(s.factor(filt)),
            "filter_at_E_plus_minus": ["0", "0"],
            "filter_at_L_plus_minus": ["1", "1"],
            "envelope_L1_bound": "B=1+(2/3)||chi'||_1+(1/12)||chi''||_1",
            "smooth_repair_bound": "abs(S(f_n,f_n)) <= B^2*M/(n-1)^4",
            "strict_negativity_condition": "8*B^2*M*n < (n-1)^3",
            "necessary_repair_cost": "B^2*M >= (n-1)^3/(8*n)",
            "spectral_coefficient_order": ["E_positive_frequency", "L_positive_frequency", "L_negative_frequency"],
        },
        "positive_polynomial_witnesses_n_equals_m_plus_4": {
            "E_frequency": coefficients(e),
            "L_frequency": coefficients(n),
            "gap": coefficients(gap),
            "L_one_chirality_multiplicity": coefficients(n**2 - 2*n - 3),
        },
        "exact_examples": rows,
        "analytic_obligations": [
            "Imported reduced TT spectral reference has the stated commutator and oriented wavefront set.",
            "Same commutator and oriented wavefront set imply a smooth symmetric difference by disjoint transpose cones.",
            "Compactly supported filtered tests annihilate both E frequencies and select L frequency n with unit amplitude.",
            "Two spatial integrations by parts bound every smooth correction by B^2*M/(n-1)^4.",
            "Every finite spectral repair is a smooth symmetric bisolution; its truncated covariance is positive.",
        ],
        "claim_flags": {
            "EXACT_FILTER_AND_FINITE_REPAIR_IDENTITIES": True,
            "REDUCED_TT_NO_SMOOTH_POSITIVITY_REPAIR_HUMAN_PROOF": True,
            "EVERY_FINITE_TT_CUTOFF_ADMITS_POSITIVE_COVARIANCE": True,
            "STATIONARITY_REQUIRED_FOR_OBSTRUCTION": False,
            "FULL_STRICT_386_PHYSICAL_POSITIVITY_DECIDED": False,
            "LORENTZIAN_CERTIFICATE_PROMOTED": False,
            "INFINITE_ANALYSIS_MACHINE_VERIFIED": False,
            "NEW_GHOST_DISCOVERY_CLAIMED": False,
            "CURRENT_PROGRAMME_PHYSICAL_RESULT_ACTIVATED": False,
        },
        "unresolved": [
            "A same-background pairing-preserving distributional observable map from this TT carrier to strict 386 physical cohomology.",
            "Independent expert review of the human microlocal and smooth-kernel argument.",
            "Publication novelty beyond the known higher-derivative ghost obstruction is not established.",
            "Reduced reference verifier fails on causal_pairing_transport hash drift; no upstream certificate repaired or promoted.",
        ],
        "report": "foundations/reports/tt-hadamard-cutoff-obstruction-v1.md",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if OUTPUT.read_text() != rendered:
            raise SystemExit("certificate differs from deterministic producer")
        print("TT cutoff obstruction reproduction: PASS")
    else:
        OUTPUT.write_text(rendered)
        print(OUTPUT.relative_to(ROOT))
