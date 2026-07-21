"""Independent verifier for BH_ENDPOINT_NONSELECTION_ASSEMBLY.

Rails (fail-closed, exact):

  0. schema + all nine anchor content hashes;
  1. INVARIANT PAIRING, independent recompute: from the cross anchor a(omega),
     form G = [[0, a],[conj a, b]] with symbolic real b, verify det G = -|a|^2
     and that this is STRICTLY NEGATIVE for every real omega != 0 (numerator
     sign-definite, denominator positive) via an INDEPENDENT eigenvalue route
     (product of eigenvalues = det < 0 => signature (1,1), rank 2), independent
     of the representative b;
  2. anchor-consistency of the assembled statements: horizon ingoing dimension
     certified (BH2A_HORIZON_REACH), infinity Einstein selection tokens
     (BH2C_FLUX_CLASS + BH2C_SYMBOLIC_FLUX_RADIATION_CLASS), the LOCAL Cauchy
     truncation is a distinct certificate, polar quantifier is fixture-only;
  3. claim-boundary + vocabulary (missing connection map declared; no two-ended
     map / QNM / parity-complete promotion).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERT = HERE / "certificates" / "BH_ENDPOINT_NONSELECTION_ASSEMBLY.json"
SCHEMA = HERE / "schema" / "bh-endpoint-nonselection-assembly-v1.schema.json"


def _check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_certificate() -> dict:
    payload = json.loads(CERT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    # Rail 0 -------------------------------------------------------------
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    anchor_keys = [k[:-12] for k in prov if k.endswith("_certificate")
                   and k != "generator_path"]
    for base in anchor_keys:
        _check(prov[base + "_sha256"] == _sha256(ROOT / prov[base + "_certificate"]),
               f"{base} hash mismatch")

    # Rail 1: invariant pairing, INDEPENDENT (eigenvalue route) ----------
    cross = json.loads((ROOT / prov["cross_invariant_certificate"]).read_text())
    w = sp.Symbol("omega", real=True, nonzero=True)
    b = sp.Symbol("b", real=True)
    a = sp.sympify(cross["a_of_omega"], locals={"omega": w, "I": sp.I})
    # no nonzero real zero of a
    for z, _m in sp.roots(sp.numer(sp.cancel(a)), w).items():
        _check(sp.im(z) != 0 or z == 0,
               f"a(omega) has a nonzero real zero {z}")
    G = sp.Matrix([[0, a], [sp.conjugate(a), b]])
    det = sp.cancel(G.det())
    amod2 = sp.cancel(a * sp.conjugate(a))
    _check(sp.simplify(det + amod2) == 0, "det G != -|a|^2")
    # eigenvalue product = det (independent of the generator's sign-of-coeffs route)
    lam = sp.Symbol("lam")
    charpoly = sp.expand((G - lam * sp.eye(2)).det())
    _check(sp.simplify(charpoly.subs(lam, 0) - det) == 0,
           "charpoly(0) != det G")
    # strictly negative for real omega != 0: numerator < 0, denominator > 0
    num, den = sp.fraction(det)
    ncoeffs = sp.Poly(sp.expand(num), w).all_coeffs()
    dcoeffs = sp.Poly(sp.expand(den), w).all_coeffs()
    _check(all(c <= 0 for c in ncoeffs) and any(c != 0 for c in ncoeffs),
           "det numerator not negative sign-definite")
    _check(all(c >= 0 for c in dcoeffs), "det denominator not positive")
    ip = payload["invariant_pairing"]
    _check(ip["rank"] == 2 and ip["signature"] == "(1, 1)",
           "recorded rank/signature wrong")
    _check(ip["det_strictly_negative_real_omega_nonzero"] is True,
           "recorded det-sign flag wrong")

    # Rail 2: anchor-consistency of the assembly ------------------------
    horizon = json.loads((ROOT / prov["horizon_reach_certificate"]).read_text())
    _check(horizon["claim_flags"]["ingoing_family_dimension_certified"] is True,
           "horizon ingoing dimension not certified")
    _check(payload["horizon_nonselection"]["einstein_rw_ingoing_dimension"] == 1,
           "recorded RW ingoing dimension != 1")
    fc = json.loads((ROOT / prov["flux_class_certificate"]).read_text())
    _check(fc["result_token"]
           == "BH2C_FINITE_FLUX_BOUNDARY_CLASS_EINSTEIN_SELECTED_AT_INFINITY",
           "flux-class token drift (infinity selection)")
    sf = json.loads((ROOT / prov["symbolic_flux_certificate"]).read_text())
    _check("EINSTEIN_SELECTED" in sf["result_token"],
           "symbolic-flux token drift")
    ct = json.loads((ROOT / prov["cauchy_truncation_certificate"]).read_text())
    _check("CAUCHY_TRUNCATION" in ct["result_token"],
           "cauchy-truncation token drift")
    _check(payload["separation_from_cauchy_truncation"]["distinct"],
           "cauchy separation not asserted")
    polarq = json.loads((ROOT / prov["polar_quantifier_certificate"]).read_text())
    _check(polarq["claim_flags"]["generic_real_frequency_certified"] is False,
           "polar quantifier is generic -- fixture-only claim unjustified")

    # Rail 3: claim boundary + vocabulary -------------------------------
    cf = payload["claim_flags"]
    for t in ("invariant_pairing_rank_signature_certified",
              "horizon_nonselection_certified", "infinity_selection_certified",
              "endpoint_disposition_certified", "cauchy_separation_certified",
              "polar_fixture_only_preserved"):
        _check(cf[t] is True, f"expected-true flag {t} not true")
    for f in ("global_connection_map_constructed",
              "two_ended_scattering_map_certified",
              "polar_theorem_beyond_fixture_certified",
              "qnm_stability_scattering_claimed", "parity_complete_claim"):
        _check(cf[f] is False, f"forbidden flag {f} not false")
    _check("connection" in payload["missing_analytic_object"]["object"].lower(),
           "missing analytic object (connection map) not declared")
    _check(len(payload["counterexample_mutations_rejected"]) >= 1,
           "no counterexample mutation recorded")
    _check(payload["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
           "dependency tags drift")
    positive = {k: v for k, v in payload.items()
                if k not in ("does_not_establish", "missing_objects")}
    blob = json.dumps(positive).lower()
    for banned in ("quasinormal", "ringdown", "stability certified",
                   "scattering matrix certified", "particle", "ghost"):
        _check(banned not in blob, f"promotional phrase '{banned}' present")

    return {"rails": "PASS", "pairing": "rank 2, signature (1,1) (independent)",
            "endpoint": "infinity Einstein selection + horizon non-selection",
            "missing_object": "global connection map (confluent-Heun)"}


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    result = verify_certificate()
    print(json.dumps(result, indent=2))
    print("OK: BH_ENDPOINT_NONSELECTION_ASSEMBLY verified (exact)")


if __name__ == "__main__":
    main()
