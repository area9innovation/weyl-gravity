"""Verifier for BH3_EXTERIOR_BVP_WELLPOSEDNESS_GATE.

Structural + cross-consistency (no BVP is solved -- forbidden):

  0. schema + six anchor content hashes;
  1. anchor cross-consistency: the additional-branch log tails and the log-free
     homogeneous contrast are the ones certified in BH2C_FLUX_CLASS /
     BH2C_ASYMPTOTIC_JORDAN; the Einstein infinity oscillatory exponent and the
     horizon ingoing exponents match BH2C_METRIC_ALL_ORDERS / BH2_GENERAL_L;
  2. disposition coherence: Einstein well-posed MODULO the discrete W_E zeros
     with W analytic + not-identically-zero; additional branch obstruction is
     the ill-defined outgoing condition (log tail not separated); Einstein and
     additional distinguished;
  3. claim boundary + vocabulary (no Wronskian/spectrum computed; no QNM etc.;
     no single-frequency solve).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import jsonschema

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERT = HERE / "certificates" / "BH3_EXTERIOR_BVP_WELLPOSEDNESS_GATE.json"
SCHEMA = HERE / "schema" / "bh3-exterior-bvp-wellposedness-gate-v1.schema.json"


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
    for key in [k for k in prov if k.endswith("_certificate")
                and k != "generator_path"]:
        base = key.rsplit("_certificate", 1)[0]
        _check(prov[base + "_sha256"] == _sha256(ROOT / prov[key]),
               f"{base} hash mismatch")

    flux = json.loads((ROOT / prov["flux_class_certificate"]).read_text())
    allord = json.loads((ROOT / prov["all_orders_certificate"]).read_text())
    genl = json.loads((ROOT / prov["general_l_certificate"]).read_text())

    # Rail 1: anchor cross-consistency ----------------------------------
    _check("logarithmic tails" in flux["log_tails"]["statement"],
           "additional-branch log tails no longer certified")
    _check("log-free" in flux["log_tails"]["contrast"],
           "log-free homogeneous contrast no longer certified")
    ab = payload["additional_branch"]
    _check("log" in ab["type"].lower() and "inconsistent" in ab["type"].lower(),
           "additional branch not described as log-tailed / pure-power-inconsistent")
    # Einstein oscillatory exponent present and referenced
    _check(allord["exponents"]["oscillatory_branch"] == "-4*I*omega + 1",
           "Einstein oscillatory exponent drift")
    rw = genl["proven_axial_generic_l"]["einstein_rw_branch"]
    _check(rw["horizon_exponents"] == ["-2*I*m*omega", "2*I*m*omega"],
           "horizon ingoing exponents drift")
    _check("-2 i m omega" in payload["bvp_definition"]["horizon_condition"]
           or "2 i m omega" in payload["bvp_definition"]["horizon_condition"],
           "horizon condition not stated via the certified indicial")

    # Rail 2: disposition coherence -------------------------------------
    eb = payload["einstein_branch"]
    _check("log-free" in eb["type"], "Einstein branch not log-free")
    _check("Wronskian" in eb["wellposedness_criterion"]
           and "= 0" in eb["wellposedness_criterion"],
           "Einstein well-posedness criterion not the Wronskian condition")
    _check("analytic" in eb["W_analytic"], "W analyticity not stated")
    _check("not" in eb["W_not_identically_zero"].lower()
           and "discrete" in eb["W_not_identically_zero"].lower(),
           "W not-identically-zero / discreteness not stated")
    _check("MINUS the discrete" in eb["disposition"]
           or "minus the discrete" in eb["disposition"].lower(),
           "Einstein disposition not modulo the discrete set")
    _check("ILL-DEFINED" in ab["first_failed_hypothesis"]
           or "ill-defined" in ab["first_failed_hypothesis"].lower(),
           "additional obstruction not an ill-defined outgoing condition")
    _check("outgoing" in ab["obstruction"].lower()
           and "log" in ab["obstruction"].lower(),
           "obstruction not tied to the log tail vs outgoing condition")
    _check(isinstance(payload["einstein_vs_additional"], str)
           and "distinct" in payload["einstein_vs_additional"].lower(),
           "Einstein-vs-additional distinction not stated")

    # Rail 3: claim boundary + vocabulary -------------------------------
    cf = payload["claim_flags"]
    for t in ("bvp_precisely_stated",
              "einstein_wellposed_modulo_discrete_certified",
              "additional_branch_obstruction_certified",
              "einstein_vs_additional_distinguished"):
        _check(cf[t] is True, f"expected-true flag {t} not true")
    for f in ("connection_wronskian_constructed", "exceptional_set_computed",
              "additional_outgoing_condition_resolved", "discrete_spectrum_claimed",
              "qnm_stability_scattering_claimed", "single_frequency_solve_used"):
        _check(cf[f] is False, f"forbidden flag {f} not false")
    _check(payload["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
           "dependency tags drift")
    positive = {k: v for k, v in payload.items()
                if k not in ("does_not_establish", "missing_objects")}
    blob = json.dumps(positive).lower()
    for banned in ("quasinormal mode computed", "quasinormal spectrum",
                   "ringdown computed", "stability certified",
                   "discrete spectrum computed", "scattering matrix"):
        _check(banned not in blob, f"promotional phrase '{banned}' present")

    return {"rails": "PASS",
            "einstein": "well-posed modulo discrete Wronskian zeros",
            "additional": "OBSTRUCTED (ill-defined outgoing condition; log tail)"}


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    result = verify_certificate()
    print(json.dumps(result, indent=2))
    print("OK: BH3_EXTERIOR_BVP_WELLPOSEDNESS_GATE verified (structural; no solve)")


if __name__ == "__main__":
    main()
