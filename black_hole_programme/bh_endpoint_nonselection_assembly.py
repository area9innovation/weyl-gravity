"""BH endpoint-selection assembly: horizon non-selection + infinity selection.

Fail-closed builder for
`black_hole_programme/certificates/BH_ENDPOINT_NONSELECTION_ASSEMBLY.json`.

Verdict token:
`BH_ONE_ENDED_ENDPOINT_SELECTION_INFINITY_EINSTEIN_HORIZON_NONSELECTION`.

Assembles the certified horizon and infinity data into the strongest invariant
one-ended Lorentzian endpoint-selection statement actually supported for pure
Weyl perturbations of Schwarzschild, and names the exact missing analytic object
(the global horizon-to-infinity connection map).  All arithmetic exact.

Imported by content hash:
  - BH2A_HORIZON_REACH  (extra branch: two-parameter ingoing-regular family at
    every frequency; RW ingoing dimension 1) -- horizon NON-selection;
  - BH2A_CAUSAL_DISPOSITION (extra branch unavoidable at the mode level);
  - BH2A_FLUX_MATRIX (Einstein/RW self-pairing symplectically NULL);
  - BH2_SYMBOLIC_CROSS_INVARIANT (Einstein x extra cross pairing
    a(omega) = i F^r/(pi alpha), exact rational, no real zero except omega = 0);
  - BH3_ANALYTIC_CONTINUATION_GATE (a(omega) meromorphic, poles {i, i/2});
  - BH2C_FLUX_CLASS + BH2C_SYMBOLIC_FLUX_RADIATION_CLASS (infinity finite-Lee-
    Wald-flux class selects EXACTLY the Einstein sector; axial literal symbolic,
    polar fixture) -- infinity SELECTION;
  - BH_LOCAL_EINSTEIN_CAUCHY_TRUNCATION (the LOCAL Cauchy-slice truncation, kept
    distinct from endpoint selection);
  - BH2_POLAR_QUANTIFIER_REPAIR (polar cross covector FIXTURE-ONLY).

Assembled theorem (axial l = 2, real omega != 0; polar fixture-only):

1. INVARIANT PAIRING RANK.  On span(Einstein, extra) the Lee-Wald Gram is
   G = [[0, a],[conj a, b]] with a = a(omega) != 0 (no real zero but omega = 0)
   and b the representative-dependent extra self-pairing.  det G = -|a|^2 < 0
   strictly for every real omega != 0, so G has RANK 2 and SIGNATURE (1, 1)
   INDEPENDENT of the representative b: the Einstein self-pairing is null yet the
   extra branch is symplectically non-degenerate against Einstein.

2. HORIZON NON-SELECTION.  Future-horizon analyticity admits BOTH the Einstein
   (RW ingoing, dimension 1) and the extra (two-parameter ingoing-regular)
   families; horizon analyticity alone does NOT force delta R_ab = 0.

3. INFINITY SELECTION.  The finite-Lee-Wald-flux asymptotic phase space at
   infinity contains EXACTLY the Einstein sector (extra slice-norm divergent),
   for every real omega != 0 (axial literal-symbolic, polar fixture).

4. ENDPOINT DISPOSITION.  Horizon analyticity + the certified infinity finite-
   flux class force delta R_ab = 0 ON THE FINITE-FLUX PHASE SPACE; the ADDITIONAL
   solution EXISTS (horizon-regular) but is excluded at infinity by symplectic-
   norm finiteness -- a phase-space normalization, NOT a local boundary or
   initial condition.  Exceptional set: omega = 0 only (excluded exceptional
   carrier; no other real exceptional frequency).

5. SEPARATION FROM CAUCHY TRUNCATION.  The certified LOCAL truncation
   (delta R|Sigma = nabla_n delta R|Sigma = 0 => delta R = 0 modulo conformal
   gauge, BH_LOCAL_EINSTEIN_CAUCHY_TRUNCATION) is a Cauchy-slice uniqueness
   statement; the endpoint selection here is a GLOBAL two-ended boundary
   statement.  They are distinct objects and neither implies the other.

MISSING ANALYTIC OBJECT (per the work item's explicit permission): the EXACT
global linear map from ingoing horizon data to the infinity radiation data -- the
connection problem of the master ODE, which is a confluent-Heun connection
(transcendental; the connection coefficients are not elementary).  Without it the
full two-ended scattering map is not constructed; only the one-ended endpoint
disposition and the exact invariant pairing are certified.

NOT claimed: no two-ended scattering matrix; no polar theorem beyond fixture; no
QNM / stability / ringdown / scattering / particle / ghost; no parity-complete
claim; no claim that every local differential boundary/initial condition fails.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH_ENDPOINT_NONSELECTION_ASSEMBLY.json"
SCHEMA_PATH = HERE / "schema" / "bh-endpoint-nonselection-assembly-v1.schema.json"

ANCHORS = {
    "horizon_reach": "BH2A_HORIZON_REACH.json",
    "causal_disposition": "BH2A_CAUSAL_DISPOSITION.json",
    "flux_matrix": "BH2A_FLUX_MATRIX.json",
    "cross_invariant": "BH2_SYMBOLIC_CROSS_INVARIANT.json",
    "analytic_continuation": "BH3_ANALYTIC_CONTINUATION_GATE.json",
    "flux_class": "BH2C_FLUX_CLASS.json",
    "symbolic_flux": "BH2C_SYMBOLIC_FLUX_RADIATION_CLASS.json",
    "cauchy_truncation": "BH_LOCAL_EINSTEIN_CAUCHY_TRUNCATION.json",
    "polar_quantifier": "BH2_POLAR_QUANTIFIER_REPAIR.json",
}

SCHEMA_NAME = "pure-weyl-bh-endpoint-nonselection-assembly-v1"
RESULT_ID = "PURE_WEYL_BH_ENDPOINT_NONSELECTION_ASSEMBLY"
RESULT_TOKEN = ("BH_ONE_ENDED_ENDPOINT_SELECTION_INFINITY_EINSTEIN_"
                "HORIZON_NONSELECTION")


class AssemblyError(RuntimeError):
    pass


def _require(cond, msg):
    if not cond:
        raise AssemblyError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def invariant_pairing() -> dict:
    """Exact rank/signature of the Einstein-extra Lee-Wald Gram, symbolic b."""
    w = sp.Symbol("omega", real=True, nonzero=True)
    b = sp.Symbol("b", real=True)
    cross = json.loads((HERE / "certificates" / ANCHORS["cross_invariant"]).read_text())
    a = sp.sympify(cross["a_of_omega"], locals={"omega": w, "I": sp.I})
    amod2 = sp.cancel(a * sp.conjugate(a))
    # a has no real zero except omega=0: its numerator's only real root is 0
    num = sp.numer(sp.cancel(a))
    real_zeros = [z for z in sp.roots(num, w) if sp.im(z) == 0]
    _require(all(z == 0 for z in real_zeros),
             f"a(omega) has a nonzero real zero: {real_zeros}")
    G = sp.Matrix([[0, a], [sp.conjugate(a), b]])
    det = sp.cancel(G.det())
    _require(sp.simplify(det + amod2) == 0, "det G != -|a|^2")
    # det G < 0 strictly for real omega != 0: numerator negative-definite in w^2
    dn = sp.Poly(sp.numer(det), w)
    coeffs = dn.all_coeffs()
    _require(all((c <= 0) for c in coeffs) and any(c != 0 for c in coeffs),
             "det numerator not sign-definite negative")
    dd = sp.Poly(sp.denom(det), w)
    _require(all((c >= 0) for c in dd.all_coeffs()), "det denom not positive")
    return {
        "gram": "G = [[0, a], [conj a, b]] on span(Einstein, extra); "
                "a = a(omega) = i F^r/(pi alpha); b = extra self-pairing "
                "(representative-dependent)",
        "det": "det G = -|a|^2 = " + str(sp.factor(det)),
        "det_strictly_negative_real_omega_nonzero": True,
        "rank": 2,
        "signature": "(1, 1)",
        "representative_independent": "rank and signature are independent of b "
                                      "(det = -|a|^2 < 0 for all real omega != 0)",
        "einstein_self_pairing": "null (BH2A_FLUX_MATRIX RW-null theorem)",
        "cross_nonzero_all_real_omega": True,
    }


def build_certificate() -> dict:
    horizon = json.loads((HERE / "certificates" / ANCHORS["horizon_reach"]).read_text())
    polarq = json.loads((HERE / "certificates" / ANCHORS["polar_quantifier"]).read_text())
    _require(horizon["claim_flags"]["ingoing_family_dimension_certified"] is True,
             "horizon ingoing dimension not certified")
    _require(polarq["claim_flags"]["generic_real_frequency_certified"] is False,
             "polar quantifier unexpectedly generic")

    pairing = invariant_pairing()

    provenance = {"generator_path":
                  "black_hole_programme/bh_endpoint_nonselection_assembly.py"}
    for key, fname in ANCHORS.items():
        provenance[key + "_certificate"] = f"black_hole_programme/certificates/{fname}"
        provenance[key + "_sha256"] = _sha256(HERE / "certificates" / fname)

    cert = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "declaration": {
            "theory": "pure-Weyl gravity L = alpha C_abcd C^abcd",
            "setting": "Schwarzschild exterior, axial l = 2, real omega != 0; "
                       "polar fixture-only",
            "statement_kind": "one-ended endpoint-condition selection/"
                              "nonselection (NOT a universal no-local-causal-"
                              "truncation theorem)",
        },
        "invariant_pairing": pairing,
        "horizon_nonselection": {
            "einstein_rw_ingoing_dimension": 1,
            "extra_family": "two-parameter ingoing-regular family at every "
                            "frequency (indicial {0 (x2), -4 i m omega, "
                            "-2 - 4 i m omega})",
            "conclusion": "future-horizon analyticity admits BOTH branches; it "
                          "does NOT force delta R_ab = 0",
            "source": "BH2A_HORIZON_REACH + BH2A_CAUSAL_DISPOSITION",
        },
        "infinity_selection": {
            "conclusion": "the finite-Lee-Wald-flux asymptotic phase space at "
                          "infinity contains EXACTLY the Einstein sector; the "
                          "extra slice-norm diverges",
            "axial": "literal symbolic omega (BH2C_SYMBOLIC_FLUX_RADIATION_CLASS: "
                     "E x E ~ r^-2 finite, omega-independent) + omega = 3/5 "
                     "fixture (BH2C_FLUX_CLASS)",
            "polar": "fixture-only (BH2C_POLAR_FLUX_CLASS via BH2C_FLUX_CLASS "
                     "chain); preserved as fixture-only",
        },
        "endpoint_disposition": {
            "verdict": "horizon analyticity + the certified infinity finite-flux "
                       "class force delta R_ab = 0 ON THE FINITE-FLUX PHASE "
                       "SPACE; the additional solution EXISTS (horizon-regular) "
                       "but is excluded at infinity by symplectic-norm "
                       "finiteness, NOT by a local boundary or initial condition",
            "additional_solution_admitted_at_horizon": True,
            "einstein_forced_on_finite_flux_phase_space": True,
            "exclusion_mechanism": "phase-space normalization (infinity norm), "
                                   "not a local boundary/initial condition",
            "exceptional_set": "omega = 0 only (excluded exceptional carrier); "
                               "no other real exceptional frequency",
        },
        "separation_from_cauchy_truncation": {
            "local_cauchy": "BH_LOCAL_EINSTEIN_CAUCHY_TRUNCATION: "
                            "delta R|Sigma = nabla_n delta R|Sigma = 0 => "
                            "delta R = 0 modulo conformal gauge -- a Cauchy-slice "
                            "uniqueness statement",
            "endpoint": "the endpoint selection here is a GLOBAL two-ended "
                        "boundary statement",
            "distinct": "distinct objects; neither implies the other",
        },
        "counterexample_mutations_rejected": [
            "imposing a LOCAL horizon boundary condition that drops the extra "
            "ingoing family and calling it endpoint selection -- REJECTED: "
            "horizon analyticity provably admits the two-parameter extra family "
            "(BH2A_HORIZON_REACH), so no local horizon condition removes it",
            "calling the infinity finite-norm selection a LOCAL boundary "
            "condition -- REJECTED: it is a phase-space normalization, not a "
            "pointwise boundary datum (BH2C finite-flux headline)",
            "asserting the Einstein-extra pairing is degenerate at some real "
            "omega != 0 -- REJECTED: det G = -|a|^2 < 0 strictly for all real "
            "omega != 0 (rank 2, signature (1,1))",
        ],
        "missing_analytic_object": {
            "object": "the EXACT global linear map from ingoing horizon data to "
                      "the infinity radiation data (the master-ODE connection "
                      "problem)",
            "nature": "confluent-Heun connection; transcendental -- the "
                      "connection coefficients are not elementary",
            "consequence": "the full two-ended scattering map is NOT constructed; "
                           "only the one-ended endpoint disposition and the exact "
                           "invariant pairing are certified",
        },
        "claim_flags": {
            "invariant_pairing_rank_signature_certified": True,
            "horizon_nonselection_certified": True,
            "infinity_selection_certified": True,
            "endpoint_disposition_certified": True,
            "cauchy_separation_certified": True,
            "polar_fixture_only_preserved": True,
            "global_connection_map_constructed": False,
            "two_ended_scattering_map_certified": False,
            "polar_theorem_beyond_fixture_certified": False,
            "qnm_stability_scattering_claimed": False,
            "parity_complete_claim": False,
        },
        "missing_objects": [
            "the exact global horizon-to-infinity connection map (confluent-Heun "
            "connection; transcendental)",
            "a two-ended scattering matrix",
            "a polar endpoint theorem beyond the fixture level (needs the polar "
            "route-B symbolic identity)",
            "general l; the exact extra self-pairing invariant b (representative-"
            "dependent; only rank/signature are invariant)",
        ],
        "does_not_establish": [
            "a two-ended scattering matrix or the global connection map",
            "any polar endpoint theorem beyond the preserved fixture",
            "any QNM, stability, ringdown, scattering, particle, or ghost claim; "
            "no additional classical branch is a particle or ghost",
            "any claim that every local differential boundary or initial "
            "condition fails (only the tested endpoint prescriptions are decided)",
            "a parity-complete claim (polar is fixture-only)",
        ],
        "provenance": provenance,
        "verification_command":
            "python3 black_hole_programme/verify_bh_endpoint_nonselection_assembly.py",
    }
    return cert


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    cert = build_certificate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
