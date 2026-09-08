#!/usr/bin/env python3
"""Independent rational replay; does not import the producer or use SymPy.

Polynomial coefficient identities supply the unbounded algebra rail. The
distributional theorem remains the explicitly separated human proof.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "foundations/results/TT_HADAMARD_CUTOFF_OBSTRUCTION_V1.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(value=None):
    v = json.loads(OUTPUT.read_text()) if value is None else value
    require(v["schema_version"] == "tt-hadamard-cutoff-obstruction-v1", "schema")
    require(v["input_source_commit"] == "08bf00a7c15e9593ad64f4a91dd7a03623ae222f", "source provenance")
    require(v["dependency_tags"] == ["REDUCED-MODE"], "dependency boundary")
    require(v["evidence_status"] == "HUMAN_ANALYTIC_PROOF_WITH_EXACT_ALGEBRA_REPLAY", "evidence boundary")
    expected_paths = {
        "covariant_completion/certificates/branch_residue_operators.json",
        "covariant_completion/certificates/branch_spectrum.json",
        "covariant_completion/certificates/tt_local_factorization.json",
        "quantum-weyl/lorentzian/certificates/VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD.json",
    }
    require({r["path"] for r in v["inputs"]} == expected_paths and len(v["inputs"]) == 4, "input set")
    for r in v["inputs"]:
        require(hashlib.sha256((ROOT / r["path"]).read_bytes()).hexdigest() == r["sha256"], "input hash")
    bridge = json.loads((ROOT / "quantum-weyl/lorentzian/certificates/VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD.json").read_text())
    # Audit rather than hide the pre-existing reference's failed import gate.
    # Local replay PASS must never be read as the upstream verifier passing.
    drift = []
    for key, r in bridge["dependencies"].items():
        actual = hashlib.sha256((ROOT / r["path"]).read_bytes()).hexdigest()
        if actual != r["sha256"]:
            drift.append({"dependency": key, "path": r["path"],
                          "expected_sha256": r["sha256"], "actual_sha256": actual})
    require(v["import_audit"]["drift"] == drift, "unreported transitive drift")
    require(v["import_audit"]["reference_gate"] == ("FAIL_DEPENDENCY_DRIFT" if drift else "HASHES_MATCH_ONLY"), "import gate")
    require([r["dependency"] for r in drift] == ["causal_pairing_transport"], "reference drift changed; review required")
    require(bridge["branch_data"]["L"]["krein_sign"] == -1, "imported L sign")
    require(bridge["branch_data"]["L"]["positive_residue"] == "4(N-1)", "imported residue")
    require(bridge["BRST_status"]["exactness"] == "NONEXACT_IN_SELECTED_REDUCED_COMPLEX", "reduced cohomology")

    # Ascending coefficients, n=m+4: e=m+2, l=m+4, gap=4m+12,
    # multiplicity=(m+1)(m+5). These are exact coefficient comparisons,
    # not inference from any number of frequency samples.
    require(v["positive_polynomial_witnesses_n_equals_m_plus_4"] == {
        "E_frequency": ["2", "1"], "L_frequency": ["4", "1"],
        "gap": ["12", "4"], "L_one_chirality_multiplicity": ["5", "6", "1"],
    }, "all-energy polynomial witnesses")
    # Independent polynomial convolution: l^2-e^2=(12,4,0).
    def square(p):
        out = [0] * (2 * len(p) - 1)
        for i, a in enumerate(p):
            for j, b in enumerate(p):
                out[i+j] += a*b
        return out
    require([a-b for a, b in zip(square([4, 1]), square([2, 1]))] == [12, 4, 0], "gap derivation")
    f = v["formulas"]
    require(f == {
        "frequency_domain": "integer n >= 4", "E_frequency": "n - 2", "gap": "4*n - 4",
        "positive_E_coefficient": "1/(8*(n - 2)*(n - 1))",
        "negative_L_coefficient": "-1/(8*n*(n - 1))", "filter_denominator": "4 - 4*n",
        "fourier_filter": "(-n + z + 2)*(n + z - 2)/(4*(n - 1))",
        "filter_at_E_plus_minus": ["0", "0"], "filter_at_L_plus_minus": ["1", "1"],
        "envelope_L1_bound": "B=1+(2/3)||chi'||_1+(1/12)||chi''||_1",
        "smooth_repair_bound": "abs(S(f_n,f_n)) <= B^2*M/(n-1)^4",
        "strict_negativity_condition": "8*B^2*M*n < (n-1)^3",
        "necessary_repair_cost": "B^2*M >= (n-1)^3/(8*n)",
        "spectral_coefficient_order": ["E_positive_frequency", "L_positive_frequency", "L_negative_frequency"],
    }, "formula contract")
    require([r["L_frequency"] for r in v["exact_examples"]] == [4, 5, 8, 16, 64, 256], "example coverage")
    for row in v["exact_examples"]:
        n, e = row["L_frequency"], row["E_frequency"]
        require(e == n-2 and n >= 4, "frequency pair")
        gap = n*n-e*e
        ce, cl = Q(1, 2*e*gap), -Q(1, 2*n*gap)
        require(ce > 0 > cl and gap == 4*(n-1), "signed residues")
        filt = lambda z: Q(e*e-z*z, e*e-n*n)
        require([filt(z) for z in (e, -e, n, -n)] == [0, 0, 1, 1], "filter selection")
        old = list(map(Q, row["reference_coefficients"]))
        repair = list(map(Q, row["finite_repair_coefficients"]))
        new = list(map(Q, row["repaired_coefficients"]))
        require(old == [ce, cl, 0] and repair == [0, -cl, -cl], "repair coefficients")
        require(new == [a+b for a, b in zip(old, repair)] and all(a >= 0 for a in new), "finite positivity")
        require(old[1]-old[2] == new[1]-new[2], "unchanged commutator")
        require(repair[1] == repair[2], "symmetric repair")
        require(Q(row["filtered_reference_expectation"]) == cl, "negative witness")
        require(row["curl_squared_eigenvalue"] == (n-1)**2, "spatial eigenvalue")
        require(Q(row["necessary_B_squared_M_for_nonnegative_test"]) == -cl*(n-1)**4, "repair cost")
        require(Q(2*n, gap) <= Q(2, 3) and Q(1, gap) <= Q(1, 12), "envelope bound")
    require(v["claim_flags"] == {
        "EXACT_FILTER_AND_FINITE_REPAIR_IDENTITIES": True,
        "REDUCED_TT_NO_SMOOTH_POSITIVITY_REPAIR_HUMAN_PROOF": True,
        "EVERY_FINITE_TT_CUTOFF_ADMITS_POSITIVE_COVARIANCE": True,
        "STATIONARITY_REQUIRED_FOR_OBSTRUCTION": False,
        "FULL_STRICT_386_PHYSICAL_POSITIVITY_DECIDED": False,
        "LORENTZIAN_CERTIFICATE_PROMOTED": False,
        "INFINITE_ANALYSIS_MACHINE_VERIFIED": False,
        "NEW_GHOST_DISCOVERY_CLAIMED": False,
        "CURRENT_PROGRAMME_PHYSICAL_RESULT_ACTIVATED": False,
    }, "claim boundary")
    require(len(v["analytic_obligations"]) == 5 and len(v["unresolved"]) == 4, "proof boundary")
    return v


if __name__ == "__main__":
    verify()
    print("TT cutoff algebra/audit: PASS; reference import: FAIL_DEPENDENCY_DRIFT; human analysis not machine verified")
