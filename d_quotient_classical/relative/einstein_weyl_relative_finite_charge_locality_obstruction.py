#!/usr/bin/env python3
"""Certify the support-local obstruction for a finite charge receiver."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_FINITE_CHARGE_SUPPORT_LOCAL_LIFT_OBSTRUCTION_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-finite-charge-support-local-lift-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-finite-charge-support-local-lift-obstruction-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_finite_charge_locality_obstruction.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_finite_charge_locality_obstruction.py"

DEPENDENCIES = {
    "complete_charge_q2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_COMPLETE_STANDARD_FIVE_CHARGE_Q2_V1.json",
    "receiver_preflight": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CHARGE_KOSZUL_RECEIVER_PREFLIGHT_V1.json",
    "taub_descent": ROOT / "bridge/certificates/compact_harmonic_domain_taub_descent.json",
    "moment_map_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "strict_delta2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ARITY_TWO_DEFECT_V1.json",
    "f2_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_F2_TAUB_OBSTRUCTION_V1.json",
}


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: Path, value: dict) -> dict[str, str]:
    return {"artifact_id": str(value.get("result_id", value.get("schema"))), "path": str(path.relative_to(ROOT)), "sha256": _sha(path)}


def build() -> dict:
    records = {name: _load(path) for name, path in DEPENDENCIES.items()}
    complete = records["complete_charge_q2"]
    receiver = records["receiver_preflight"]
    descent = records["taub_descent"]
    obstruction = records["f2_obstruction"]
    if complete["classification"]["complete_standard_source_five_charge_q2"] is not True:
        raise AssertionError("complete charge q2 is not certified")
    if receiver["charge_fibre"]["dimension"] != 5:
        raise AssertionError("finite charge receiver dimension drifted")
    if descent["classification"]["gauge_descent_from_noether_identity"] is not True:
        raise AssertionError("Noether current descent is not certified")
    witness = sp.sympify(obstruction["taub_pairing"]["relative_half_delta2_pairing"])
    q2_witness = sp.simplify(2 * witness)
    if q2_witness == 0:
        raise AssertionError("nonzero charge witness disappeared")

    return {
        "schema": "pure-weyl-relative-finite-charge-support-local-lift-obstruction-v1",
        "result_id": RESULT_ID,
        "result_state": "DIRECT_FINITE_CHARGE_SUPPORT_LOCAL_LIFT_OBSTRUCTED",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "connected noncompact-time compact magnetic product M=R_t x S1_L x S2",
            "boundaries": "closed compact Cauchy slice and compactly supported test sections on spacetime",
            "charge_sector": "five connected-isometry charges H,P_x,J_1,J_2,J_3 on fixed P_N",
            "carrier": "direct lift from the local field/BV sheaf to the constant five-dimensional residual charge receiver",
            "degree": "symmetric arity-two charge operation",
            "parity": "all",
            "ell": "all certified standard source blocks",
            "m": "all",
            "k": "all",
            "omega": "all certified standard source branches",
        },
        "dependencies": {name: _artifact(path, records[name]) for name, path in DEPENDENCIES.items()},
        "support_locality_lemma": {
            "domain": "compactly supported sections of a finite-rank local field bundle on connected noncompact M",
            "codomain": "constant sections of M x g_stab^*, with g_stab^*=span{H^*,P_x^*,J_1^*,J_2^*,J_3^*}",
            "hypothesis": "B is a finite-order bilinear differential operator and supp B(u,v) is contained in supp(u) intersect supp(v)",
            "proof": [
                "compactly supported inputs give compactly supported output by differential locality",
                "a nonzero constant section on connected M has support equal to all of noncompact M",
                "therefore B(u,v)=0 for every compactly supported pair",
                "every pair of finite jets at a point is realized by compactly supported bump sections",
                "therefore every coefficient of B vanishes and B=0 identically"
            ],
            "conclusion": "every support-local finite-order lift into the constant finite charge receiver is zero",
        },
        "contradiction_witness": {
            "mode": obstruction["scope"]["parity"] + " " + obstruction["scope"]["ell"] + " plus branch",
            "half_diagonal_charge": str(sp.factor(witness)),
            "q2_diagonal_charge": str(sp.factor(q2_witness)),
            "nonzero": True,
            "consequence": "no direct support-local lift can reproduce the certified reduced charge q2",
        },
        "minimal_admissible_enlargement": {
            "local_carrier": "Omega_H^3(M;g_stab^*) -> Omega_H^4(M;g_stab^*)",
            "field": "the action-derived polarized relative Noether current j_rel,X(u,v)",
            "differential": "horizontal divergence d_H j_rel,X equals the relative equation/Noether source",
            "globalization": "Q_X(u,v)=integral_Sigma j_rel,X(u,v) only after passing to a closed Cauchy slice",
            "cyclic_completion": "adjoin the dual current/divergence rows simultaneously",
            "status": "OPEN_COEFFICIENT_EXPORT",
            "reason": "the formal action Noether identity and slice descent are certified, but no portable coefficientwise current-density/BV cone has been exported",
        },
        "classification": {
            "direct_five_charge_support_local_lift_exists": False,
            "support_locality_obstruction_exact": True,
            "nonzero_reduced_charge_requires_globalization": True,
            "local_noether_current_cone_is_minimal_admissible_carrier": True,
            "local_noether_current_coefficients_exported": False,
            "support_local_bv_koszul_extension_certified": False,
            "direct_f2_repaired": False,
            "arity_three_authorized": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "EXPORT_POLARIZED_RELATIVE_NOETHER_CURRENT_DENSITY_AND_DIVERGENCE_CONE",
        "provenance": {
            "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)},
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_finite_charge_locality_obstruction --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_finite_charge_locality_obstruction",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_finite_charge_locality_obstruction",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-finite-charge-support-local-lift-obstruction-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FINITE_CHARGE_SUPPORT_LOCAL_LIFT_OBSTRUCTION_V1.json",
            ],
        },
        "claim_boundary": (
            "This theorem obstructs only a direct finite-order support-preserving differential lift from local compactly supported field/BV sections into the constant five-dimensional residual charge receiver on connected noncompact spacetime. It does not obstruct the certified global reduced-mode charge operation, a local horizontal Noether-current/divergence cone followed by Cauchy-slice integration, a causal Green construction on an enlarged complex, a modified unary map, another background, observables, particles or quantum theory. The current-density coefficients and cyclic BV completion remain open."
        ),
    }


def validate(value: dict) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _report() -> str:
    return r"""# Finite-charge support-local lift obstruction

The five-dimensional residual charge receiver cannot be the direct target of
a nonzero support-local finite-order field operation.  A differential
bilinear map sends compactly supported inputs to a compactly supported
section.  A nonzero constant section of the connected noncompact cylinder has
full support.  Hence such a map to constant charge rows vanishes on compact
inputs; compactly supported jet realization then forces every coefficient to
vanish.

This contradicts the exact relative witness

\[
q^{\rm charge}_{2,H}(u,u)=-\frac{108}{5}(1+\sqrt3)\ne0.
\]

Thus the global Koszul receiver is legitimate only after globalization.  The
minimal local carrier is instead the horizontal Noether-current cone

\[
\Omega_H^3(M;\mathfrak g_{\rm stab}^*)
\xrightarrow{d_H}
\Omega_H^4(M;\mathfrak g_{\rm stab}^*),
\]

with the charge obtained by integrating the closed current over a Cauchy
slice.  The formal Noether identity and slice descent already exist, but the
portable coefficientwise relative current and its cyclic BV dual rows remain
to be exported.
"""


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _guards(value: dict) -> None:
    for key in ("direct_five_charge_support_local_lift_exists", "local_noether_current_coefficients_exported", "support_local_bv_koszul_extension_certified", "direct_f2_repaired", "arity_three_authorized", "causal_observable_particle_or_quantum_claim"):
        mutant = deepcopy(value)
        mutant["classification"][key] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check and (OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report()):
        raise AssertionError("finite-charge locality obstruction outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
