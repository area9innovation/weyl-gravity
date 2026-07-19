#!/usr/bin/env python3
"""Export the reduced standard-radiative relative charge q2 operation."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_STANDARD_RADIATIVE_CHARGE_Q2_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-standard-radiative-charge-q2.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-standard-radiative-charge-q2-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_standard_charge_q2.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_standard_charge_q2.py"

DEPENDENCIES = {
    "receiver_preflight": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CHARGE_KOSZUL_RECEIVER_PREFLIGHT_V1.json",
    "strict_delta2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ARITY_TWO_DEFECT_V1.json",
    "radiative_restriction": ROOT / "bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json",
    "moment_map_taub_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
    "f2_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_F2_TAUB_OBSTRUCTION_V1.json",
}


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: Path, value: dict) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema", "UNIDENTIFIED"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _s(value: sp.Expr) -> str:
    return str(sp.factor(sp.radsimp(sp.simplify(value))))


def build() -> dict:
    records = {name: _load(path) for name, path in DEPENDENCIES.items()}
    preflight = records["receiver_preflight"]
    delta = records["strict_delta2"]
    radiative = records["radiative_restriction"]
    moment = records["moment_map_taub_bridge"]
    stabilizer = records["stabilizer"]
    obstruction = records["f2_obstruction"]

    if preflight["architecture_decision"]["selected"] != (
        "CERTIFIED_UNARY_MAPPING_COFIBER_PLUS_REDUCED_MODE_RELATIVE_CHARGE_KOSZUL_RECEIVER"
    ):
        raise AssertionError("relative charge receiver was not selected")
    if delta["checks"]["maxwell_equation_rows_strict"] is not True:
        raise AssertionError("strict Delta2 acquired Maxwell equation output")
    if moment["classification"]["generic_H_Px_J_selection_rules_certified"] is not True:
        raise AssertionError("generic five-charge selection rules are not certified")
    if stabilizer["classification"]["generic_axial_polar_primary_equivariance_certified"] is not True:
        raise AssertionError("stabilizer equivariance is not certified")
    quotient_domains = {
        "moment_map_taub_bridge": moment["domain"],
        "stabilizer": stabilizer["domain"],
    }
    if any("after local gauge reduction" not in domain for domain in quotient_domains.values()):
        raise AssertionError("standard-radiative input is not certified on the local-gauge quotient")

    lam = sp.symbols("lambda", positive=True)
    weights = [
        sp.sympify(text.replace("lambda", "lam"), locals={"lam": lam})
        for text in radiative["theorem"]["all_ell_ge_2_classification"]["common_relative_weights"]
    ]
    relative_weights = [sp.simplify(weight - 1) for weight in weights]
    expected = [sp.Rational(3, 2) * sp.sqrt(2 * lam), -sp.Rational(3, 2) * sp.sqrt(2 * lam)]
    if any(sp.simplify(got - want) != 0 for got, want in zip(relative_weights, expected)):
        raise AssertionError("relative branch coefficients drifted")

    half_h = sp.sympify(obstruction["taub_pairing"]["relative_half_delta2_pairing"])
    q2_h = sp.simplify(2 * half_h)
    if sp.simplify(q2_h + sp.Rational(108, 5) * (1 + sp.sqrt(3))) != 0:
        raise AssertionError("charge q2 H normalization drifted")

    parity_blocks = radiative["theorem"]["parity_blocks"]
    axial_gram = parity_blocks["axial"]["einstein_coefficient_form"]
    polar_gram = parity_blocks["polar"]["einstein_coefficient_form"]
    if axial_gram != [["lambda", "0"], ["0", "2"]]:
        raise AssertionError("axial Einstein coefficient form drifted")
    if polar_gram != [["1", "-2"], ["-2", "2*lambda"]]:
        raise AssertionError("polar Einstein coefficient form drifted")
    angular_weight = stabilizer["rotation_representation"]["all_ell_proof"]["angular_weight"]
    if angular_weight != "w_m=1/binomial(2*ell,ell+m)":
        raise AssertionError("angular coefficient form drifted")

    charge_basis = ["H", "P_x", "J_1", "J_2", "J_3"]
    return {
        "schema": "pure-weyl-relative-standard-radiative-charge-q2-v1",
        "result_id": RESULT_ID,
        "result_state": "STANDARD_RADIATIVE_FIVE_CHARGE_Q2_EXACT_REDUCED_MODE",
        "lifecycle_status": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["REDUCED-MODE"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product R_t x S1_L x S2",
            "boundaries": "closed Cauchy slice S1_L x S2 before final stabilizer quotient",
            "charge_sector": "fixed compact U(1) bundle P_N with N=2",
            "carrier": "complete standard radiative Einstein q-primary solution carrier",
            "degree": "symmetric arity-two output in the five-dimensional relative charge row",
            "parity": "axial and polar",
            "ell": "ell>=2",
            "m": "all real SO(3) multiplicities",
            "k": "2*pi*n/L for every n in Z",
            "omega": "Einstein plus and minus branches",
        },
        "dependencies": {
            name: _artifact(path, records[name]) for name, path in DEPENDENCIES.items()
        },
        "operation": {
            "name": "q2_relative_charge",
            "input": "two standard-radiative Einstein-Maxwell q1 cohomology classes",
            "output_basis": charge_basis,
            "output_dimension": 5,
            "definition": "q2_charge,X(u,v)=<zeta_X,Delta2(u,v)>=D^2 mu_rel,X|_0(u,v)",
            "quadratic_relation": "mu_rel,X(u)=1/2*q2_charge,X(u,u)",
            "relative_moment_map": "mu_rel,X=mu_WM,X(iota u)-mu_EM,X(u)",
            "branch_rule": "q2_charge,X=2*(w_branch-1)*B_EM,X, where B_EM,X is the symmetric polarization of mu_EM,X",
            "relative_branch_coefficients": [_s(value) for value in relative_weights],
            "component_formulas_on_a_real_branch_mode": {
                "H": "q2_charge,H=-(L/2)*omega^2*r_branch*c^dagger(G_EM tensor W_ell)c",
                "P_x": "q2_charge,Px=(L/2)*k*omega*r_branch*c^dagger(G_EM tensor W_ell)c",
                "J_a": "q2_charge,Ja=(L/2)*omega*r_branch*c^dagger(G_EM tensor W_ell*T_a)c",
                "r_branch": "r_plus=+(3/2)*sqrt(2*lambda), r_minus=-(3/2)*sqrt(2*lambda)",
            },
            "coefficient_data": {
                "axial_G_EM": axial_gram,
                "polar_G_EM": polar_gram,
                "angular_W_ell": angular_weight,
                "rotation_action": stabilizer["rotation_representation"]["action"],
            },
            "selection_rules": moment["generic_moment_maps"]["polarized_rules"],
            "constant_u1_component": "zero: constant U1 reducibility has zero fundamental vector field and Delta2 has strict Maxwell equation rows",
            "h_witness": {
                "mode": "axial ell=2,m=0,k=0 plus branch",
                "half_diagonal_taub_value": _s(half_h),
                "q2_charge_H_diagonal": _s(q2_h),
            },
        },
        "identities": {
            "koszul_symmetry": True,
            "reduced_unary_source_differential": "zero on q1 cohomology classes",
            "reduced_charge_row_q1": "zero",
            "arity_two_chain_identity": "q1*q2_charge+q2_charge(q1,.)+q2_charge(.,q1)=0 on the declared reduced carrier",
            "cohomology_domain_certificate": "the operation is defined in the certified after-local-gauge-reduction q-primary coordinates; no off-shell representative-level lift is claimed",
            "imported_quotient_domains": quotient_domains,
            "stabilizer_equivariance": "H and P_x are central; (J_1,J_2,J_3) transform in the coadjoint SO3 representation",
            "constant_u1_output": "zero",
        },
        "classification": {
            "five_charge_q2_on_standard_radiative_cohomology": True,
            "descends_to_standard_radiative_cohomology": True,
            "all_ell_ge_2_both_parities_all_compact_momenta": True,
            "h_normalization_matches_f2_obstruction": True,
            "constant_u1_charge_output": False,
            "exceptional_and_global_charge_q2_included": False,
            "off_shell_local_jet_charge_q2": False,
            "support_local_bv_koszul_extension": False,
            "direct_f2_repaired": False,
            "arity_three_authorized": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "EXTEND_CHARGE_Q2_TO_EXCEPTIONAL_GLOBAL_COHOMOLOGY_THEN_DERIVE_LOCAL_CURRENT_DENSITY_LIFT",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_standard_charge_q2 --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_standard_charge_q2",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_standard_charge_q2",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-standard-radiative-charge-q2-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_STANDARD_RADIATIVE_CHARGE_Q2_V1.json",
            ],
        },
        "claim_boundary": (
            "This exact REDUCED-MODE operation is the first arity-two bracket on the selected relative charge receiver. It covers the complete standard radiative Einstein q-primary cohomology for ell>=2, both parities and every compact momentum, and records the five stabilizer charge defects. It does not include exceptional/global source cohomology, define an off-shell local jet operator or support-local BV/Koszul extension, repair the obstructed direct f2, authorize arity three, or imply causal, observational, particle or quantum equivalence."
        ),
    }


def validate(value: dict) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["classification"]["five_charge_q2_on_standard_radiative_cohomology"] is not True:
        raise AssertionError("charge q2 theorem dropped")
    if value["classification"]["direct_f2_repaired"] is not False:
        raise AssertionError("charge q2 was confused with a repaired f2")


def _report() -> str:
    return r"""# Standard-radiative relative five-charge q2

The selected relative charge receiver now has its first exact arity-two
operation.  On two standard-radiative Einstein--Maxwell cohomology classes,

\[
q^{\rm charge}_{2,X}(u,v)
=\langle\zeta_X,\Delta_2(u,v)\rangle
=D^2\mu_{{\rm rel},X}|_0(u,v),
\qquad X\in\{H,P_x,J_1,J_2,J_3\}.
\]

Thus

\[
\mu_{{\rm rel},X}(u)=\frac12q^{\rm charge}_{2,X}(u,u).
\]

The pulled-back Weyl form has branch weights

\[
w_\pm=1\pm\frac32\sqrt{2\lambda},
\]

so the relative charge coefficient is

\[
r_\pm=w_\pm-1=\pm\frac32\sqrt{2\lambda}.
\]

The exact (H), (P_x) and (J_a) formulas are the Einstein moment-map
polarizations multiplied by (2r_\pm).  All harmonic and parity selection
rules are inherited from the certified product-stabilizer action.  Constant
(U(1)) reducibility contributes zero.

The operation is defined on the already certified, after-local-gauge-reduction
q-primary solution coordinates.  Thus it is a bracket on that reduced
cohomology carrier; this artifact does not claim an off-shell representative-
level or local-current lift.

In the authoritative master bases the Einstein coefficient forms are

\[
G_{\rm EM}^{\rm ax}=\begin{pmatrix}\lambda&0\\0&2\end{pmatrix},
\qquad
G_{\rm EM}^{\rm pol}=\begin{pmatrix}1&-2\\-2&2\lambda\end{pmatrix},
\]

and the invariant angular weight is
(w_m=\binom{2\ell}{\ell+m}^{-1}).

On the axial (ell=2,m=0,k=0) plus witness,

\[
\frac12q^{\rm charge}_{2,H}(u,u)
=-\frac{54}{5}(1+\sqrt3),
\qquad
q^{\rm charge}_{2,H}(u,u)
=-\frac{108}{5}(1+\sqrt3).
\]

This operation records the obstruction; it does not cancel it.  It is a
global reduced-mode charge bracket, not a support-local field operation.  The
next gate is its exceptional/global extension followed by a local
current-density BV lift.  The original (f_2) remains obstructed and arity
three remains closed.
"""


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _guards(value: dict) -> None:
    for key in (
        "exceptional_and_global_charge_q2_included",
        "off_shell_local_jet_charge_q2",
        "support_local_bv_koszul_extension",
        "direct_f2_repaired",
        "arity_three_authorized",
        "causal_observable_particle_or_quantum_claim",
    ):
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
    if args.check:
        if OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report():
            raise AssertionError("relative standard charge q2 outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
