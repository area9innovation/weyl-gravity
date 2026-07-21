"""BH-3 numerical-validation protocol (specification, not a computation).

Fail-closed builder for
`black_hole_programme/certificates/BH3_NUMERICAL_VALIDATION_PROTOCOL.json`.

Verdict token:
`BH3_NUMERICAL_VALIDATION_PROTOCOL_SPECIFIED`.

This item exists so that NO BH-3 complex-frequency / quasinormal-mode successor
is ever created without a pre-declared, independent falsification rail (the
Science Forge independent-rail law).  The deliverable is a SPECIFICATION and a
reproducibility contract -- **no spectrum, no quasinormal mode, no off-real-axis
solve is run here.**  The protocol pins, by content hash, the exact
real-frequency invariants that any prospective numerical complex-omega rail
MUST reproduce on the real axis before it may be trusted off the real axis:

- `BH2_SYMBOLIC_CROSS_INVARIANT`: the axial cross scalar
  a(omega) = i F^r(E,X)/(pi alpha) as an EXACT rational function with poles
  {i, i/2}, zeros {0, 2i, i/4 (double)}, no real poles, no real zeros except
  the excluded origin, and conjugate law a(-omega) = -conj(a(omega));
- `BH2_GENERAL_L_STRUCTURAL`: horizon indicial data -- Einstein RW ingoing
  exponents +-2 i m omega (indicial omega^2 + s^2/(4 m^2) = 0), the extra-branch
  residue spectrum {0 (x2), -4 i m omega, -2 - 4 i m omega}, and the exceptional
  angular set l in {0, 1};
- `BH2C_METRIC_ALL_ORDERS`: the parity-unified master ODE
  c2 F'' + c1 F' + c0 F = 0 and the infinity exponents -3 and -4 i omega + 1.

The generator copies these exact invariant strings verbatim from the three
certificates and pins their content hashes, so the specification cannot silently
drift from the certified real-axis facts; the verifier re-checks both.

NOT established here (fail-closed): any complex-omega mode, symplectic-current
continuation, spectrum, quasinormal mode, stability, scattering, or positivity
result; the protocol is unexecuted.  It is a contract a future rail must satisfy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH3_NUMERICAL_VALIDATION_PROTOCOL.json"
SCHEMA_PATH = HERE / "schema" / "bh3-numerical-validation-protocol-v1.schema.json"

CROSS = HERE / "certificates" / "BH2_SYMBOLIC_CROSS_INVARIANT.json"
GENL = HERE / "certificates" / "BH2_GENERAL_L_STRUCTURAL.json"
ALLORD = HERE / "certificates" / "BH2C_METRIC_ALL_ORDERS.json"

SCHEMA_NAME = "pure-weyl-bh3-numerical-validation-protocol-v1"
RESULT_ID = "PURE_WEYL_BH3_NUMERICAL_VALIDATION_PROTOCOL"
RESULT_TOKEN = "BH3_NUMERICAL_VALIDATION_PROTOCOL_SPECIFIED"


class ProtocolError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ProtocolError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict:
    cross = json.loads(CROSS.read_text())
    genl = json.loads(GENL.read_text())
    allord = json.loads(ALLORD.read_text())

    # --- copy the exact real-axis invariants verbatim from the anchors ------
    a_of_omega = cross["a_of_omega"]
    a_definition = cross["a_definition"]
    poles = cross["poles"]
    zeros = cross["zeros"]
    conj_law = cross["conjugate_frequency_law"]
    _require(cross["no_real_poles"] is True, "cross anchor lost no_real_poles")
    _require(cross["real_exceptional_frequencies"] == [],
             "cross anchor gained a real exceptional frequency")

    rw = genl["proven_axial_generic_l"]["einstein_rw_branch"]
    horizon_exponents = rw["horizon_exponents"]
    horizon_indicial = rw["horizon_indicial_polynomial"]
    extra_spectrum = genl["proven_axial_generic_l"]["extra_branch"][
        "extra_branch_residue_spectrum"]
    exceptional_l = genl["proven_axial_generic_l"]["exceptional_set"][
        "exceptional_l"]

    master_ode = allord["master_ode"]
    inf_exponents = allord["exponents"]

    protocol = {
        "problem_definition": {
            "setting": "Schwarzschild exterior of pure-Weyl gravity "
                       "L = alpha C_abcd C^abcd; m = 1 for the a(omega) anchor, "
                       "symbolic m for the horizon indicial data",
            "domain": "r in (2m, infinity); tortoise r_* = r + 2m ln(r/2m - 1) "
                      "in (-infinity, +infinity)",
            "unknown_bvp": "the exterior complex-omega boundary-value problem "
                           "for the axial (Regge-Wheeler) and polar master "
                           "fields and the fourth-order Bach extra branch; the "
                           "target functional is the cross pairing "
                           "a(omega) = i F^r(E,X)/(pi alpha)",
            "master_ode_unified": master_ode,
            "einstein_boundary_conditions": {
                "horizon": "ingoing selection e^{-2 i m omega r_*} "
                           "(indicial omega^2 + s^2/(4 m^2) = 0, s = +- 2 i m omega)",
                "infinity": "outgoing e^{+ i omega r_*}; master field F = H1' "
                            "(axial) = Ch (polar) decays as the certified "
                            "exponents below",
            },
            "extra_branch": "fourth-order Bach system, extra residue spectrum "
                            + str(extra_spectrum),
            "parities": "axial l = 2 (a(omega) anchor); polar via the "
                        "parity-unified master ODE; general l via Lambda = "
                        "l(l+1), exceptional l in " + str(exceptional_l),
        },
        "numerical_method": {
            "independent_rail_requirement": "TWO independent implementations "
                "are REQUIRED; agreement across them (not agreement with the "
                "exact symbolic producer) is the evidence -- Science Forge "
                "independent-rail law.  Neither implementation may call, import, "
                "or reuse the symbolic producers "
                "(bh2_symbolic_cross_invariant / bh2c_metric_all_orders / "
                "bh2_general_l_structural) as its own check.",
            "method_A": "matched-asymptotic shooting in r_*: factor the certified "
                        "boundary exponents, build analytic Frobenius series at the "
                        "horizon (indicial roots +-2 i m omega) and at infinity "
                        "(exponents from BH2C_METRIC_ALL_ORDERS), integrate to a "
                        "midpoint, and match value/derivative via the Wronskian.",
            "method_B": "hyperboloidal/analytic spectral collocation: compactify "
                        "the radial coordinate, factor the boundary exponents so "
                        "the residual field is analytic on the closed interval, and "
                        "discretize on a Chebyshev-Lobatto grid.",
            "discretization_parameters": {
                "shooting": "step size h (or adaptive tolerance atol/rtol), "
                            "truncation radius R_infty, Frobenius series order K "
                            "at each end",
                "spectral": "collocation order N; compactification map; "
                            "exponent-factorization ansatz",
            },
        },
        "convergence_criterion": {
            "spectral": "geometric (exponential) Cauchy convergence in N: "
                        "|Q_N - Q_{N-dN}| decreasing geometrically until below "
                        "tau_conv",
            "shooting": "algebraic Richardson convergence of declared order p in "
                        "h; extrapolated value stable to tau_conv",
            "tau_conv": "1e-10 relative (declared; a rail may tighten but never "
                        "loosen without a superseding protocol event)",
        },
        "error_control": {
            "ode_residual": "sup-norm of the master-ODE residual on a refined "
                            "grid below tau_resid = 1e-9",
            "boundary_mismatch": "horizon/infinity boundary-condition residual "
                                 "below tau_bc = 1e-9",
            "pairing_consistency": "the Lee-Wald pairing a(omega) recomputed from "
                                   "the numerical modes must be r-independent "
                                   "(on-shell) to tau_conv across at least two "
                                   "evaluation radii",
        },
        "real_axis_cross_check_anchors": {
            "statement": "BEFORE any off-real-axis (complex-omega) value is "
                         "trusted, the numerical rail MUST reproduce ALL of the "
                         "following certified real-axis invariants to tau_conv.",
            "a_of_omega": {
                "definition": a_definition,
                "exact_rational": a_of_omega,
                "poles": poles,
                "zeros": zeros,
                "conjugate_law": conj_law,
                "no_real_poles": True,
                "omega_zero_excluded": True,
                "required_checks": [
                    "match a(omega) at a declared set of real sample "
                    "frequencies omega != 0 to tau_conv",
                    "verify a(-omega) = -conj(a(omega)) numerically to tau_conv",
                    "exhibit NO real pole (regular solve for all real omega != 0)",
                    "recover the exact pole set {i, i/2} and zero set "
                    "{0, 2i, i/4 (double)} as the analytic structure the rail "
                    "must match before continuation",
                ],
            },
            "horizon_indicial": {
                "einstein_rw_exponents": horizon_exponents,
                "indicial_polynomial": horizon_indicial,
                "extra_residue_spectrum": extra_spectrum,
                "required_checks": [
                    "recover the ingoing horizon exponent -2 i m omega to "
                    "tau_conv",
                    "recover the extra-branch residue spectrum "
                    + str(extra_spectrum),
                ],
            },
            "infinity_asymptotics": {
                "master_ode": master_ode,
                "exponents": inf_exponents,
                "required_checks": [
                    "recover the infinity exponents -3 and -4 i omega + 1 of "
                    "the master field to tau_conv",
                ],
            },
            "exceptional_angular_set": {
                "exceptional_l": exceptional_l,
                "note": "the rail must exclude l in {0, 1} (S_l or H2_l "
                        "degenerate) and omega = 0 (excluded exceptional carrier)",
            },
        },
        "continuation_domain": {
            "statement": "the numerical rail may be continued into the "
                         "complex-omega plane ONLY within an explicitly declared "
                         "domain that EXCLUDES the certified poles {i, i/2} of "
                         "a(omega) (and any branch structure the analytic-"
                         "continuation gate isolates).  Reproducing the exact "
                         "pole/zero structure of a(omega) on and near the real "
                         "axis is a NECESSARY precondition for trusting the rail "
                         "off the real axis.",
            "hands_off_to": "black-hole-complex-frequency-analytic-continuation-"
                            "gate (which certifies or obstructs the continuation "
                            "itself; this protocol only validates a numerical "
                            "rail against the real-axis anchors)",
        },
        "acceptance_thresholds": {
            "tau_conv": "1e-10 relative",
            "tau_resid": "1e-9",
            "tau_bc": "1e-9",
            "independent_agreement": "methods A and B must agree to tau_conv on "
                                     "every real-axis anchor above",
            "convergence_order_declared": "spectral: geometric; shooting: "
                                          "declared algebraic order p, verified by "
                                          "Richardson",
            "fail_closed": "any anchor not reproduced to tau_conv, any "
                           "non-converging refinement, any method disagreement, "
                           "or any real pole is a FAIL; a FAIL blocks BH-3 "
                           "vocabulary -- a skip or timeout is never a pass",
        },
        "reproducibility_contract": {
            "pinned_anchors": "the three certificates below, by content hash",
            "deterministic": "fixed grids / step sequences, no randomness in the "
                             "acceptance path; environment (interpreter, linear-"
                             "algebra backend, and precision) recorded with the "
                             "run",
            "record": "each validation run records exact method parameters, the "
                      "achieved residuals, the anchor-by-anchor pass/fail, "
                      "elapsed time, and the environment; agreement is asserted "
                      "across the two independent implementations",
            "supersession": "tightening a tolerance or adding an anchor is a NEW "
                             "protocol event (append-only), never an edit of this "
                             "specification",
        },
    }

    cert = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "artifact_kind": "PROTOCOL_SPECIFICATION",
        "lifecycle": "SPECIFIED",
        "declaration": {
            "theory": "pure-Weyl gravity L = alpha C_abcd C^abcd",
            "purpose": "independent numerical-validation protocol (falsification "
                       "rail) that any prospective BH-3 complex-frequency / "
                       "quasinormal-mode computation MUST pass before its "
                       "vocabulary is admissible",
            "is_specification_only": True,
            "no_computation_run": True,
        },
        "protocol": protocol,
        "claim_flags": {
            "protocol_specified": True,
            "real_axis_anchors_pinned_by_hash": True,
            "independent_rail_required": True,
            "continuation_domain_declared": True,
            "spectrum_computed": False,
            "quasinormal_mode_computed": False,
            "off_real_axis_result_established": False,
            "numerical_rail_implemented": False,
        },
        "missing_objects": [
            "the two independent numerical implementations themselves (this "
            "item delivers the specification only)",
            "any executed real-axis validation run (a future rail runs it)",
            "the analytic-continuation certificate (separate item "
            "black-hole-complex-frequency-analytic-continuation-gate)",
        ],
        "does_not_establish": [
            "any complex-omega mode, symplectic-current continuation, spectrum, "
            "quasinormal mode, stability, scattering, or positivity result",
            "any off-real-axis numerical value (nothing is computed here)",
            "admissibility of BH-3 vocabulary (this protocol is a precondition "
            "on a future rail, not a BH-3 result)",
        ],
        "provenance": {
            "generator_path":
                "black_hole_programme/bh3_numerical_validation_protocol.py",
            "cross_invariant_certificate": str(CROSS.relative_to(ROOT)),
            "cross_invariant_sha256": _sha256(CROSS),
            "general_l_certificate": str(GENL.relative_to(ROOT)),
            "general_l_sha256": _sha256(GENL),
            "all_orders_certificate": str(ALLORD.relative_to(ROOT)),
            "all_orders_sha256": _sha256(ALLORD),
        },
        "verification_command":
            "python3 black_hole_programme/verify_bh3_numerical_validation_protocol.py",
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
