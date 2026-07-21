"""Verifier for BH3_NUMERICAL_VALIDATION_PROTOCOL (specification).

This is a SPECIFICATION artifact, so verification is structural + cross-
consistency (it runs NO numerics -- running a solve is the future rail's job,
explicitly out of scope here):

  0. schema validation + schema/anchor content hashes;
  1. ANCHOR CROSS-CONSISTENCY: every exact real-axis invariant string pinned in
     the protocol (a(omega), its poles/zeros/conjugate law, the horizon indicial
     data + extra residue spectrum, the master ODE + infinity exponents, the
     exceptional angular set) must EQUAL the value in the corresponding anchor
     certificate on disk -- the specification cannot silently drift from the
     certified facts;
  2. protocol completeness: two independent methods declared; the real-axis
     falsification gate present with fail-closed acceptance; the continuation
     domain declared to EXCLUDE the certified poles {i, i/2};
  3. claim-boundary + vocabulary: nothing off the real axis is claimed; no
     spectrum / quasinormal / stability promotion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import jsonschema

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERT = HERE / "certificates" / "BH3_NUMERICAL_VALIDATION_PROTOCOL.json"
SCHEMA = HERE / "schema" / "bh3-numerical-validation-protocol-v1.schema.json"


def _check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_certificate() -> dict:
    payload = json.loads(CERT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    # Rail 0: schema + hashes ---------------------------------------------
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    for key in ("cross_invariant_certificate", "general_l_certificate",
                "all_orders_certificate"):
        base = key.rsplit("_certificate", 1)[0]
        _check(prov[base + "_sha256"] == _sha256(ROOT / prov[key]),
               f"{key} hash mismatch")

    cross = json.loads((ROOT / prov["cross_invariant_certificate"]).read_text())
    genl = json.loads((ROOT / prov["general_l_certificate"]).read_text())
    allord = json.loads((ROOT / prov["all_orders_certificate"]).read_text())

    proto = payload["protocol"]
    anc = proto["real_axis_cross_check_anchors"]

    # Rail 1: anchor cross-consistency ------------------------------------
    aa = anc["a_of_omega"]
    _check(aa["exact_rational"] == cross["a_of_omega"],
           "a(omega) rational drifted from BH2_SYMBOLIC_CROSS_INVARIANT")
    _check(aa["definition"] == cross["a_definition"], "a definition drifted")
    _check(aa["poles"] == cross["poles"], "a(omega) poles drifted")
    _check(aa["zeros"] == cross["zeros"], "a(omega) zeros drifted")
    _check(aa["conjugate_law"] == cross["conjugate_frequency_law"],
           "conjugate law drifted")
    _check(aa["no_real_poles"] is True and cross["no_real_poles"] is True,
           "no_real_poles inconsistent")
    _check(cross["real_exceptional_frequencies"] == [],
           "anchor gained a real exceptional frequency")

    rw = genl["proven_axial_generic_l"]["einstein_rw_branch"]
    hz = anc["horizon_indicial"]
    _check(hz["einstein_rw_exponents"] == rw["horizon_exponents"],
           "horizon exponents drifted from BH2_GENERAL_L_STRUCTURAL")
    _check(hz["indicial_polynomial"] == rw["horizon_indicial_polynomial"],
           "indicial polynomial drifted")
    _check(hz["extra_residue_spectrum"]
           == genl["proven_axial_generic_l"]["extra_branch"][
               "extra_branch_residue_spectrum"],
           "extra residue spectrum drifted")
    _check(anc["exceptional_angular_set"]["exceptional_l"]
           == genl["proven_axial_generic_l"]["exceptional_set"]["exceptional_l"],
           "exceptional l drifted")

    inf = anc["infinity_asymptotics"]
    _check(inf["master_ode"] == allord["master_ode"],
           "master ODE drifted from BH2C_METRIC_ALL_ORDERS")
    _check(inf["exponents"] == allord["exponents"],
           "infinity exponents drifted")
    _check(proto["problem_definition"]["master_ode_unified"]
           == allord["master_ode"], "problem-definition master ODE drifted")

    # Rail 2: protocol completeness ---------------------------------------
    nm = proto["numerical_method"]
    _check(nm["method_A"] and nm["method_B"]
           and "independent" in nm["independent_rail_requirement"].lower(),
           "two independent methods not both declared")
    _check("symbolic producer" in nm["independent_rail_requirement"].lower()
           or "symbolic producers" in nm["independent_rail_requirement"].lower(),
           "independent-rail requirement does not exclude the symbolic producer")
    acc = proto["acceptance_thresholds"]
    for k in ("tau_conv", "tau_resid", "tau_bc", "independent_agreement",
              "fail_closed"):
        _check(k in acc and str(acc[k]).strip(), f"acceptance missing {k}")
    _check("fail" in acc["fail_closed"].lower()
           and "never a pass" in acc["fail_closed"].lower(),
           "acceptance is not fail-closed")
    cd = proto["continuation_domain"]["statement"].lower()
    _check("exclude" in cd and "{i, i/2}" in proto["continuation_domain"]["statement"],
           "continuation domain does not declare exclusion of the poles {i, i/2}")
    # the real-axis gate must be a PRECONDITION for off-axis trust
    _check("before" in anc["statement"].lower()
           and "real-axis" in anc["statement"].lower().replace("real axis",
                                                               "real-axis"),
           "real-axis anchors not stated as an off-axis precondition")

    # Rail 3: claim boundary + vocabulary ---------------------------------
    cf = payload["claim_flags"]
    for t in ("protocol_specified", "real_axis_anchors_pinned_by_hash",
              "independent_rail_required", "continuation_domain_declared"):
        _check(cf[t] is True, f"expected-true flag {t} not true")
    for f in ("spectrum_computed", "quasinormal_mode_computed",
              "off_real_axis_result_established", "numerical_rail_implemented"):
        _check(cf[f] is False, f"forbidden flag {f} not false")
    _check(payload["declaration"]["is_specification_only"] is True
           and payload["declaration"]["no_computation_run"] is True,
           "declaration not specification-only")
    _check(payload["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
           "dependency tags drift (must be REDUCED-MODE real-axis anchors, "
           "never LORENTZIAN-CAUSAL)")
    _check("LORENTZIAN-CAUSAL" not in payload["dependency_tags"],
           "protocol must not carry a LORENTZIAN-CAUSAL tag")
    # positive fields must not PROMOTE a spectrum/QNM as done
    positive = {k: v for k, v in payload.items()
                if k not in ("does_not_establish", "missing_objects")}
    blob = json.dumps(positive).lower()
    for banned in ("spectrum computed", "quasinormal mode computed",
                   "ringdown", "stability certified"):
        _check(banned not in blob, f"promotional phrase '{banned}' present")
    _check(len(payload["does_not_establish"]) >= 1, "empty does_not_establish")

    return {"rails": "PASS", "anchors_cross_consistent": True,
            "numerics_run": False}


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    result = verify_certificate()
    print(json.dumps(result, indent=2))
    print("OK: BH3_NUMERICAL_VALIDATION_PROTOCOL verified (specification, "
          "no numerics run)")


if __name__ == "__main__":
    main()
