#!/usr/bin/env python3
"""Assemble the relative mapping cofiber with the five-current receiver.

The construction is deliberately typed as a block-diagonal unary extension.
It certifies the local homotopy-moment-map receiver and proves that this direct
sum cannot repair the independently obstructed target-valued f2 equation.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_CURRENT_COFIBER_ASSEMBLY_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-current-cofiber-assembly.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-current-cofiber-assembly-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_current_cofiber_assembly.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_current_cofiber_assembly.py"

DEPENDENCIES = {
    "linear_triangle": ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1.json",
    "triangle_components": ROOT / "bridge/einstein_sector/generated/einstein_weyl_relative_linear_triangle_v1/components.json",
    "arity_two_defect": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ARITY_TWO_DEFECT_V1.json",
    "direct_f2_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_F2_TAUB_OBSTRUCTION_V1.json",
    "charge_koszul_receiver": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CHARGE_KOSZUL_RECEIVER_PREFLIGHT_V1.json",
    "finite_charge_locality_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FINITE_CHARGE_SUPPORT_LOCAL_LIFT_OBSTRUCTION_V1.json",
    "cyclic_current_cone": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CYCLIC_FIVE_CURRENT_CONE_V1.json",
    "global_charge_replay": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_GLOBAL_FIVE_CHARGE_REPLAY_V1.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def build() -> dict[str, Any]:
    values = {name: _load(path) for name, path in DEPENDENCIES.items()}
    triangle = values["linear_triangle"]
    components = values["triangle_components"]
    defect = values["arity_two_defect"]
    obstruction = values["direct_f2_obstruction"]
    koszul = values["charge_koszul_receiver"]
    locality = values["finite_charge_locality_obstruction"]
    current = values["cyclic_current_cone"]
    replay = values["global_charge_replay"]

    if triangle["acceptance_flags"]["SUPPORT_LOCAL_MAPPING_COFIBER"] is not True:
        raise AssertionError("support-local mapping cofiber is absent")
    cofiber = components["mapping_cofiber"]
    if cofiber["square_zero"] is not True or cofiber["support_local"] is not True:
        raise AssertionError("unary mapping cofiber drifted")
    if current["classification"]["unary_current_cone_q1_squared_zero"] is not True:
        raise AssertionError("current receiver is not a complex")
    if current["classification"]["arity_two_current_cone_cyclicity_exact"] is not True:
        raise AssertionError("current receiver cyclicity is absent")
    if replay["classification"]["slice_integral_matches_complete_five_charge_q2"] is not True:
        raise AssertionError("local-to-global five-charge replay is absent")
    if koszul["derived_zero_locus"]["square_zero_checked_on_all_exterior_monomials"] is not True:
        raise AssertionError("Koszul receiver is not exact at the declared algebraic level")
    koszul_basis = [item.split("=", 1)[0] for item in koszul["charge_fibre"]["basis"]]
    if koszul_basis != replay["complete_replay"]["output_basis"]:
        raise AssertionError("current and Koszul charge bases disagree")
    if defect["checks"]["strict_arity_two_defect_zero"] is not False:
        raise AssertionError("strict arity-two defect unexpectedly vanished")
    if obstruction["classification"]["smooth_periodic_full_domain_f2_exists"] is not False:
        raise AssertionError("direct f2 obstruction is absent")
    if locality["classification"]["direct_five_charge_support_local_lift_exists"] is not False:
        raise AssertionError("constant-charge locality obstruction drifted")

    cofiber_dimensions = cofiber["degree_dimensions"]
    current_dimensions = current["generated_layout"]["degree_ranks"]
    cofiber_rows = sum(cofiber_dimensions)
    current_rows = sum(current_dimensions)
    if cofiber_rows != 78 or current_rows != 50:
        raise AssertionError("assembled row count drifted")

    return {
        "schema": "pure-weyl-relative-current-cofiber-assembly-v1",
        "result_id": RESULT_ID,
        "result_state": "LOCAL_HOMOTOPY_MOMENT_MAP_RECEIVER_ASSEMBLED_DIRECT_F2_OBSTRUCTION_PRESERVED",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product",
            "boundaries": "M=R_t x S1_L x S2 with closed Cauchy slice and fixed magnetic bundle P_N, N=2",
            "charge_sector": "five connected product-isometry stabilizers H,P_x,J_1,J_2,J_3",
            "carrier": "support-local unary relative mapping cofiber direct-summed with the cyclic horizontal five-current BV cone",
            "degree": "all unary cofiber degrees and the degree (-1,0,1,2) current cone; arity-two current operation",
            "parity": "all certified standard axial and polar blocks",
            "ell": "complete standard source cohomology", "m": "all certified multiplicities",
            "k": "all certified compact momenta", "omega": "all certified standard branches",
        },
        "dependencies": {name: _artifact(path, values[name]) for name, path in DEPENDENCIES.items()},
        "unary_assembly": {
            "construction": "Cone(f1) direct_sum CurrentCone_5 with zero unary cross-incidence",
            "mapping_cofiber_degree_dimensions": cofiber_dimensions,
            "mapping_cofiber_rows": cofiber_rows,
            "current_cone_degree_dimensions": current_dimensions,
            "current_cone_rows": current_rows,
            "assembled_rows": cofiber_rows + current_rows,
            "square_zero": True,
            "support_local": True,
            "current_summand_cyclic": True,
            "whole_assembly_standard_pairing_cyclic": False,
            "whole_pairing_reason": "the imported relative triangle deliberately retains three distinct action-derived forms and its standard-pairing cyclic map is obstructed",
        },
        "homotopy_moment_map_square": {
            "local_operation": "q2_current,X(u,v)=1/2*(omega_rel(u,L_X v)+omega_rel(v,L_X u))",
            "local_identity": "d_H q2_current,X equals the complete action-Euler stabilizer source for every X",
            "on_shell_consequence": "q2_current,X is horizontally closed on unary source cocycles",
            "global_map": "closed-slice integration after variational-bicomplex globalization",
            "global_identity": "integral_Sigma q2_current,X = D^2 mu_rel,X|_0 = q2_charge,X",
            "koszul_receiver": "d_K kappa_X=mu_rel,X with five generators and 32 exterior monomials",
            "constant_u1_output": False,
            "charge_basis": replay["complete_replay"]["output_basis"],
            "charge_projected_arity_two_descent_exact": True,
        },
        "projection_argument": {
            "enlarged_target": "T_prime=T_Weyl direct_sum CurrentCone_5",
            "unary_operator": "q1_prime=q1_Weyl direct_sum d_H",
            "candidate": "f2_prime=(a,b)",
            "target_projection": "pr_Weyl of the enlarged arity-two morphism equation is exactly the original equation for a: [q1_Weyl,a]=-Delta2",
            "witness": "the constant-lapse target adjoint class pairs nontrivially with Delta2 and annihilates every allowed q1_Weyl-exact a",
            "conclusion": "a block-diagonal current-cone extension cannot repair the direct f2 obstruction",
            "smallest_unresolved_repair": "a nonzero typed cross-incidence, a genuinely derived source pullback, a modified unary/endpoint map, or a different background",
        },
        "classification": {
            "mapping_cofiber_and_current_receiver_assembled": True,
            "assembled_unary_square_zero": True,
            "assembled_support_local": True,
            "five_charge_homotopy_moment_map_exact": True,
            "charge_projected_arity_two_descent_exact": True,
            "global_current_to_koszul_charge_replay_exact": True,
            "direct_support_local_map_to_constant_charge_fibre": False,
            "full_relative_arity_two_morphism_constructed": False,
            "direct_f2_obstruction_preserved": True,
            "whole_assembly_standard_pairing_cyclic": False,
            "arity_three_authorized": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "CONSTRUCT_RELATIVE_OBSERVABLE_PULLBACK_ON_LINEAR_COFIBER; NONLINEAR_REPAIR_REQUIRES_TYPED_CROSS_INCIDENCE_OR_DERIVED_SOURCE_PULLBACK",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_current_cofiber_assembly --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_current_cofiber_assembly",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_current_cofiber_assembly",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-current-cofiber-assembly-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CURRENT_COFIBER_ASSEMBLY_V1.json",
            ],
        },
        "claim_boundary": (
            "This theorem assembles the certified support-local unary mapping cofiber with the 50-row cyclic five-current cone and identifies the resulting local-to-global homotopy moment map into the five-generator Koszul derived-zero-locus receiver. The five stabilizer-charge projection of the arity-two defect is represented exactly. Because the unary extension is block diagonal, projection back to the Weyl target reproduces the independently obstructed direct f2 equation; the current summand therefore does not repair the full relative morphism. No standard-pairing cyclic relative triangle, arity-three morphism, causal functor, observable pullback, particle or quantum theorem is claimed."
        ),
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Relative current-cone/cofiber assembly

The certified unary mapping cofiber has 78 rows and the cyclic five-current
receiver has 50 rows.  Their block-diagonal support-local sum is therefore a
128-row complex with square-zero unary differential.  The current summand
carries the exact polarized local operations

\[
q^{\rm current}_{2,X}(u,v)
=\frac12\bigl(\omega_{\rm rel}(u,{\cal L}_Xv)
+\omega_{\rm rel}(v,{\cal L}_Xu)\bigr),
\]

whose horizontal divergences are the complete action--Euler stabilizer
sources.  On unary solutions the currents are closed.  Global
variational-bicomplex descent and integration over the closed Cauchy slice
give exactly the five moment-map Hessians, which are the quadratic Taylor
coefficients of the five-generator Koszul receiver.

This completes the homotopy-moment-map receiver, but not the full relative
`f2`.  For the block-diagonal extension, any candidate has components
`f2'=(a,b)`.  Projecting its morphism equation onto the original Weyl target
gives the unchanged equation `[q1_W,a]=-Delta2`.  The certified
constant-lapse adjoint class still obstructs that equation.  Thus merely
adjoining the current cone records and globalizes the charge obstruction; it
does not cancel it.  A nonlinear repair must introduce a nonzero typed cross
incidence, use a genuinely derived source pullback, modify the unary/endpoint
map, or change background.
"""


def _guards(value: dict[str, Any]) -> None:
    for key in (
        "direct_support_local_map_to_constant_charge_fibre",
        "full_relative_arity_two_morphism_constructed",
        "whole_assembly_standard_pairing_cyclic",
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
    if args.check and (OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report()):
        raise AssertionError("relative current/cofiber assembly outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
