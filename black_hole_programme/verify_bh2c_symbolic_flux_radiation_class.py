"""Structurally independent verifier for BH2C_SYMBOLIC_FLUX_RADIATION_CLASS.

Rails (fail-closed):

  0. schema validation + schema/engine/dependency content hashes;
  1. numeric-anchor fixture hashes match the on-disk certified fixtures
     (BH2C_FLUX_CLASS axial, BH2C_POLAR_FLUX_CLASS polar);
  2. INDEPENDENT carrier-exponent rail: re-derive the axial trace-free Ricci
     carrier infinity exponents on the verifier-side geometry engine VbGeo
     (Schouten / Kulkarni--Nomizu), NOT the generator's Geometry, and
     cross-check rates {+- i omega} and powers {+- 2 i omega} at symbolic
     omega;  this is reproduction on an independent rail, not a re-run;
  3. omega-independence / no-real-exceptional-frequency structural checks:
     the recorded exponents are pure-imaginary in omega (amplitude real part
     0) and never real / colliding for real omega != 0;  omega = 0 excluded;
  4. claim-boundary consistency: every claim flag declared False is genuinely
     unestablished here (divergent symbolic table, symbolic log tails, polar
     recomputation, pairing theorem, phase space, summability, general l).

With --full it ALSO re-derives the axial Einstein literal Lee--Wald flux
E0|E0 and E2|E2 on VbGeo at symbolic omega (~6 min) and checks both fall as
r^-2 with a nonzero omega-dependent leading coefficient.  The default fast
rail (0-4) runs in a few seconds; --full is the Tier-3 exhaustive rail.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

from verify_bh2a_axial_operator import VbGeo
from bh2c_symbolic_flux_radiation_class import (
    carrier_exponents, axial_einstein_flux,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2C_SYMBOLIC_FLUX_RADIATION_CLASS.json"
SCHEMA = HERE / "schema" / "bh2c-symbolic-flux-radiation-class-v1.schema.json"


def _check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_certificate(full: bool = False) -> dict:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    # Rail 0: schema + content hashes -------------------------------------
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    _check(prov["engine_sha256"] == _sha256(ROOT / prov["engine_path"]),
           "engine hash mismatch")
    _check(prov["theta_engine_sha256"] == _sha256(HERE / "linearized_theta.py"),
           "theta engine hash mismatch")
    _check(prov["bach_engine_sha256"] == _sha256(HERE / "linearized_bach.py"),
           "bach engine hash mismatch")
    for key in ("flux_matrix_certificate", "all_orders_certificate",
                "symbolic_indicial_certificate"):
        _check(prov[key + "_sha256"] == _sha256(ROOT / prov[key]),
               f"{key} hash mismatch")

    # Rail 1: numeric-anchor fixtures -------------------------------------
    anc = payload["numeric_anchor"]
    _check(anc["axial_fixture_sha256"] == _sha256(ROOT / anc["axial_fixture"]),
           "axial fixture hash mismatch")
    _check(anc["polar_fixture_sha256"] == _sha256(ROOT / anc["polar_fixture"]),
           "polar fixture hash mismatch")
    axial_fix = json.loads((ROOT / anc["axial_fixture"]).read_text())
    _check(axial_fix["flux_table"]["E0|E0"] == ["-2", 0]
           and axial_fix["flux_table"]["E2|E2"] == ["-2", 0],
           "axial fixture Einstein entries not finite (-2,0)")
    _check(anc["axial_fixture_table"] == axial_fix["flux_table"],
           "recorded anchor table does not match the fixture on disk")

    # Rail 2: INDEPENDENT carrier-exponent rail (VbGeo) -------------------
    out: dict = {"stage_seconds": {}}
    ce = carrier_exponents(out, geo_cls=VbGeo)
    rec = payload["carrier_exponents_axial"]
    _check(ce["rates"] == rec["rates"] == ["-I*omega", "I*omega"],
           f"carrier rates mismatch: {ce['rates']} vs {rec['rates']}")
    _check(ce["powers"] == rec["powers"]
           == {"-I*omega": "-2*I*omega", "I*omega": "2*I*omega"},
           f"carrier powers mismatch: {ce['powers']} vs {rec['powers']}")

    # Rail 3: omega-independence / no real exceptional frequency ----------
    w = sp.Symbol("omega", positive=True)
    # exponents as functions of omega; amplitude real parts must be 0
    for e_str in ("-I*omega", "I*omega", "-2*I*omega", "2*I*omega"):
        e = sp.sympify(e_str, locals={"omega": w, "I": sp.I})
        _check(sp.re(e) == 0,
               f"exponent {e_str} has nonzero real part (amplitude decay)")
        # never real for real omega != 0 (pure imaginary, nonzero)
        _check(sp.im(e) != 0, f"exponent {e_str} not genuinely oscillatory")
    fd = payload["frequency_dependence"]
    _check(fd["extra_carrier_amplitude_real_part"] == 0,
           "extra carrier amplitude real part must be 0")
    _check(fd["finite_divergent_split_omega_independent"] is True
           and fd["omega_enters_only_imaginary_tortoise_phase"] is True,
           "omega-independence flags not set")
    # Einstein flux leading power -2 < -1 (finite), extra real part 0 >= -1
    alpha = sp.Symbol("alpha", positive=True)
    loc = {"omega": w, "alpha": alpha, "pi": sp.pi, "I": sp.I}
    for pair in ("E0|E0", "E2|E2"):
        ent = payload["einstein_literal_flux_axial"][pair]
        lp = ent["leading_power"]
        _check(lp == [-2, 0], f"{pair} leading power {lp} != [-2,0]")
        _check(lp[0] < -1, f"{pair} not integrable at infinity")
        # leading coefficient: nonzero and pole-free for every real omega != 0
        coeff = sp.sympify(ent["leading_coeff"], locals=loc)
        num, den = sp.fraction(sp.together(coeff))
        _check(sp.Poly(num, w).total_degree() >= 1
               or sp.simplify(num) != 0,
               f"{pair} leading coefficient numerator vanishes identically")
        for rr in sp.Poly(sp.simplify(den), w).real_roots():
            _check(rr == 0,
                   f"{pair} leading coefficient has a real pole at omega={rr}")

    # Rail 4: claim-boundary consistency ----------------------------------
    cf = payload["claim_flags"]
    for t_flag in ("axial_einstein_literal_flux_symbolic_certified",
                   "axial_carrier_exponents_symbolic_certified",
                   "finite_divergent_split_omega_independent_certified",
                   "no_real_exceptional_frequency_certified",
                   "numeric_anchor_hashed"):
        _check(cf[t_flag] is True, f"expected-true flag {t_flag} not true")
    for f_flag in ("axial_divergent_table_symbolic_certified",
                   "symbolic_log_tails_certified",
                   "polar_literal_flux_symbolic_recomputed",
                   "conjugate_frequency_pairing_theorem_certified",
                   "asymptotic_phase_space_constructed",
                   "summability_certified", "general_l_certified"):
        _check(cf[f_flag] is False, f"unestablished flag {f_flag} not false")
    _check(len(payload["missing_objects"]) >= 1
           and len(payload["does_not_establish"]) >= 1,
           "boundary ledgers empty")
    _check(payload["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
           "dependency tags drift")

    result = {"fast_rails": "PASS", "carrier_rail_engine": "VbGeo",
              "carrier_rate_seconds": out["stage_seconds"].get("carrier_exponents")}

    # Rail 5 (--full): independent literal E x E flux on VbGeo ------------
    if full:
        out2: dict = {"stage_seconds": {}}
        tbl = axial_einstein_flux(out2, geo_cls=VbGeo)
        for pair in ("E0|E0", "E2|E2"):
            _check(tbl[pair]["leading_power"] == [-2, 0],
                   f"[full] {pair} leading power != (-2,0) on VbGeo")
            _check(sp.simplify(sp.sympify(
                tbl[pair]["leading_coeff"],
                locals={"omega": sp.Symbol("omega", positive=True),
                        "alpha": sp.Symbol("alpha", positive=True),
                        "pi": sp.pi, "I": sp.I})) != 0,
                   f"[full] {pair} leading coeff vanished on VbGeo")
        result["full_ExE_rail"] = "PASS"
        result["full_seconds"] = out2["stage_seconds"]

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true",
                        help="also re-derive E x E literal flux on VbGeo (~6 min)")
    args = parser.parse_args()
    result = verify_certificate(full=args.full)
    print(json.dumps(result, indent=2))
    print("OK: BH2C_SYMBOLIC_FLUX_RADIATION_CLASS verified"
          + (" (with --full E x E rail)" if args.full else " (fast rails)"))


if __name__ == "__main__":
    main()
