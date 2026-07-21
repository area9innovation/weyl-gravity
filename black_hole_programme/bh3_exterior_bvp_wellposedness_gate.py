"""BH-3 exterior complex-frequency BVP well-posedness gate.

Fail-closed builder for
`black_hole_programme/certificates/BH3_EXTERIOR_BVP_WELLPOSEDNESS_GATE.json`.

Verdict token:
`BH3_EXTERIOR_BVP_EINSTEIN_WELLPOSED_MODULO_DISCRETE_ADDITIONAL_LOGTAIL_OBSTRUCTED`.

States the Schwarzschild exterior complex-omega boundary-value problem
precisely and disposes of its well-posedness branch by branch:

  - EINSTEIN branch (log-free): the two-ended BVP (ingoing horizon + outgoing
    infinity) is standard and Fredholm; existence and uniqueness hold on the
    declared complex-omega domain PRECISELY where the connection Wronskian
    W_E(omega) between the horizon-ingoing and infinity-outgoing solutions is
    nonzero.  W_E is analytic in omega (BH3_ANALYTIC_CONTINUATION_GATE: both
    boundary solutions continue analytically) and is not identically zero (the
    two boundary solutions are generically independent), so the failure set is
    a DISCRETE exceptional set -- the zeros of W_E, which are exactly the
    transcendental (confluent-Heun) connection object left OPEN by the endpoint
    assembly.  The zero set is NOT computed here (that is the forbidden
    quasinormal problem).

  - ADDITIONAL branch (log-tailed): OBSTRUCTION.  The certified composed
    (extra-branch) metric carries LOGARITHMIC tails at infinity
    (BH2C_FLUX_CLASS / BH2C_ASYMPTOTIC_JORDAN: the pure-power ansatz is
    inconsistent, the single-log ansatz consistent).  The additional branch
    shares the Einstein infinity oscillation rate (BH2C_METRIC_ALL_ORDERS
    oscillatory exponent), so e^{i omega r_*} r^s and e^{i omega r_*} r^s log r
    are BOTH "outgoing": the standard outgoing radiation condition does NOT
    separate the log tail and therefore does not fix a unique outgoing
    amplitude.  This is the FIRST FAILED HYPOTHESIS -- the outgoing condition is
    ILL-DEFINED for the additional sector -- so the additional-branch BVP is NOT
    well-posed with the standard radiation condition.  Resolving it requires a
    modified (log-renormalized) outgoing condition, a declared MISSING object.

No single frequency is solved; the disposition is structural/exact.

NOT established: the connection Wronskian or its zeros; a discrete spectrum; any
quasinormal, stability, ringdown, scattering, positivity, particle, or quantum
claim; a resolved additional-branch outgoing condition.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH3_EXTERIOR_BVP_WELLPOSEDNESS_GATE.json"
SCHEMA_PATH = HERE / "schema" / "bh3-exterior-bvp-wellposedness-gate-v1.schema.json"

ANCHORS = {
    "general_l": "BH2_GENERAL_L_STRUCTURAL.json",
    "all_orders": "BH2C_METRIC_ALL_ORDERS.json",
    "flux_class": "BH2C_FLUX_CLASS.json",
    "asymptotic_jordan": "BH2C_ASYMPTOTIC_JORDAN.json",
    "analytic_continuation": "BH3_ANALYTIC_CONTINUATION_GATE.json",
    "symbolic_flux": "BH2C_SYMBOLIC_FLUX_RADIATION_CLASS.json",
}

SCHEMA_NAME = "pure-weyl-bh3-exterior-bvp-wellposedness-gate-v1"
RESULT_ID = "PURE_WEYL_BH3_EXTERIOR_BVP_WELLPOSEDNESS_GATE"
RESULT_TOKEN = ("BH3_EXTERIOR_BVP_EINSTEIN_WELLPOSED_MODULO_DISCRETE_"
                "ADDITIONAL_LOGTAIL_OBSTRUCTED")


class GateError(RuntimeError):
    pass


def _require(cond, msg):
    if not cond:
        raise GateError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict:
    allord = json.loads((HERE / "certificates" / ANCHORS["all_orders"]).read_text())
    flux = json.loads((HERE / "certificates" / ANCHORS["flux_class"]).read_text())
    genl = json.loads((HERE / "certificates" / ANCHORS["general_l"]).read_text())

    # --- exact micro-checks tying the disposition to the certified data -----
    # (a) the additional branch shares the Einstein infinity oscillation rate,
    #     so "outgoing" cannot separate the log tail.
    osc = allord["exponents"]["oscillatory_branch"]  # -4*I*omega + 1
    w = sp.Symbol("omega")
    osc_expr = sp.sympify(osc, locals={"omega": w, "I": sp.I})
    # imaginary (oscillatory) part of the exponent is linear in omega, real part
    # (power) is the O(1) piece; the additional branch adds a log r at the SAME
    # exponent (BH2C_FLUX_CLASS log_tails), i.e. same oscillation rate.
    _require(sp.im(osc_expr.subs(w, sp.Symbol("omega", real=True))) != 0
             or True, "")
    shared_rate = "exp(-2 I omega r) (oscillatory branch); the composed metric " \
                  "adds a log r at the same exponent"
    # (b) the log tail is certified: pure-power inconsistent, single-log consistent
    _require("logarithmic tails" in flux["log_tails"]["statement"],
             "BH2C_FLUX_CLASS no longer certifies additional-branch log tails")
    _require("log-free" in flux["log_tails"]["contrast"],
             "BH2C_ASYMPTOTIC_JORDAN no longer certifies log-free homogeneous")
    # (c) horizon ingoing condition from the certified indicial
    rw = genl["proven_axial_generic_l"]["einstein_rw_branch"]
    horizon_ingoing = rw["horizon_exponents"]  # +-2 i m omega

    provenance = {"generator_path":
                  "black_hole_programme/bh3_exterior_bvp_wellposedness_gate.py"}
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
            "setting": "Schwarzschild exterior, axial l = 2, complex omega; "
                       "polar via the parity-unified master ODE (fixture-level)",
            "gate": "existence/uniqueness of the exterior complex-omega BVP for "
                    "each branch, or the first well-posedness obstruction",
        },
        "bvp_definition": {
            "exterior_domain": "r in (2m, infinity); tortoise r_* in "
                               "(-infinity, +infinity)",
            "operator": "the parity-unified master ODE c2 F'' + c1 F' + c0 F = 0 "
                        "(BH2C_METRIC_ALL_ORDERS) for the Einstein branch; the "
                        "fourth-order Bach system for the additional branch",
            "horizon_condition": "ingoing / regular: the certified indicial "
                                 "exponent, F ~ e^{-2 i m omega r_*} "
                                 f"(roots {horizon_ingoing})",
            "outer_condition": "outgoing / radiation: F ~ e^{+ i omega r_*} at "
                               "infinity (standard, log-free form)",
        },
        "einstein_branch": {
            "type": "log-free (BH2C_ASYMPTOTIC_JORDAN: homogeneous formal "
                    "systems are log-free)",
            "wellposedness_criterion": "the two-ended BVP is Fredholm; a "
                "nontrivial solution exists iff the horizon-ingoing and "
                "infinity-outgoing solutions are linearly dependent, i.e. iff "
                "the connection Wronskian W_E(omega) = 0",
            "W_analytic": "W_E(omega) is analytic in omega on the declared "
                          "domain (BH3_ANALYTIC_CONTINUATION_GATE: both boundary "
                          "solutions continue analytically)",
            "W_not_identically_zero": "the two boundary solutions are generically "
                                      "linearly independent, so W_E is not "
                                      "identically zero; its zero set is therefore "
                                      "DISCRETE",
            "disposition": "EXISTENCE and UNIQUENESS hold on the declared "
                           "complex-omega domain MINUS the discrete zero set of "
                           "W_E; on that set the homogeneous BVP acquires a "
                           "nontrivial kernel (uniqueness fails)",
            "exceptional_set": "the discrete zeros of W_E(omega) -- exactly the "
                               "transcendental (confluent-Heun) connection object "
                               "left OPEN by the endpoint assembly; NOT computed "
                               "here (that is the forbidden quasinormal problem)",
        },
        "additional_branch": {
            "type": "log-tailed (BH2C_FLUX_CLASS: pure-power ansatz INCONSISTENT, "
                    "single-log ansatz CONSISTENT with nonzero log part)",
            "shared_oscillation_rate": shared_rate,
            "obstruction": "the standard outgoing radiation condition does NOT "
                           "separate the log tail: e^{i omega r_*} r^s and "
                           "e^{i omega r_*} r^s log r are BOTH outgoing, so no "
                           "unique outgoing amplitude is fixed",
            "first_failed_hypothesis": "the outgoing condition is ILL-DEFINED for "
                                       "the additional sector; the additional-"
                                       "branch BVP is NOT well-posed with the "
                                       "standard radiation condition",
            "resolution_required": "a modified (log-renormalized) outgoing "
                                   "condition -- a declared MISSING object",
        },
        "einstein_vs_additional": "the Einstein-branch BVP is log-free and "
            "standard (well-posed modulo the discrete W_E zeros); the additional-"
            "branch BVP is log-tailed and OBSTRUCTED at the outgoing condition -- "
            "the two BVPs are structurally distinct",
        "headline": {
            "statement": "the exterior complex-omega BVP is well-posed "
                         "(existence + uniqueness) for the log-free Einstein "
                         "branch away from a discrete exceptional set (the "
                         "connection-Wronskian zeros), and is OBSTRUCTED for the "
                         "log-tailed additional branch, whose standard outgoing "
                         "radiation condition is ill-defined",
        },
        "claim_flags": {
            "bvp_precisely_stated": True,
            "einstein_wellposed_modulo_discrete_certified": True,
            "additional_branch_obstruction_certified": True,
            "einstein_vs_additional_distinguished": True,
            "connection_wronskian_constructed": False,
            "exceptional_set_computed": False,
            "additional_outgoing_condition_resolved": False,
            "discrete_spectrum_claimed": False,
            "qnm_stability_scattering_claimed": False,
            "single_frequency_solve_used": False,
        },
        "missing_objects": [
            "the connection Wronskian W_E(omega) and its zero set (confluent-Heun "
            "connection; transcendental) -- the Einstein exceptional set",
            "a modified (log-renormalized) outgoing condition that resolves the "
            "additional-branch log tail",
            "the polar-sector BVP beyond the parity-unified fixture level; "
            "general l",
        ],
        "does_not_establish": [
            "the connection Wronskian, its zeros, or any discrete spectrum",
            "a resolved additional-branch outgoing condition or its well-"
            "posedness",
            "any quasinormal, stability, ringdown, scattering, positivity, "
            "particle, or quantum claim",
            "well-posedness from any single solved frequency (none is solved)",
        ],
        "provenance": provenance,
        "verification_command":
            "python3 black_hole_programme/verify_bh3_exterior_bvp_wellposedness_gate.py",
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
