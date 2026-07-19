#!/usr/bin/env python3
"""Certify all five stabilizer precompositions of the relative current cone."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from d_quotient_classical.relative.einstein_weyl_relative_five_stabilizer_current import exact_data


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_FIVE_STABILIZER_CURRENT_CONE_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-five-stabilizer-current-cone.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-five-stabilizer-current-cone-v1.schema.json"
CORE = ROOT / "d_quotient_classical/relative/einstein_weyl_relative_five_stabilizer_current.py"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_five_stabilizer_current_cone.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_five_stabilizer_current_cone.py"

DEPENDENCIES = {
    "hessian_current_cone": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_HESSIAN_GREEN_CURRENT_CONE_V1.json",
    "lee_wald_seed": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_POLARIZED_NOETHER_CURRENT_SEED_V1.json",
    "complete_charge_q2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_COMPLETE_STANDARD_FIVE_CHARGE_Q2_V1.json",
    "product_stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def _artifact(path: Path, value: dict) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def build() -> dict:
    dependencies = {name: _load(path) for name, path in DEPENDENCIES.items()}
    cone = dependencies["hessian_current_cone"]
    if cone["classification"]["coefficient_jet_formal_self_adjointness_exact"] is not True:
        raise AssertionError("densitized relative Hessian is not self-adjoint")
    if cone["classification"]["off_shell_relative_hessian_divergence_cone_certified"] is not True:
        raise AssertionError("relative Hessian divergence cone is not certified")
    data = exact_data()
    if data["generator_basis"] != ["H", "P_x", "J_1", "J_2", "J_3"]:
        raise AssertionError("stabilizer basis drifted")
    for name, record in data["records"].items():
        if record["divergence_defect_count"] != 0:
            raise AssertionError(f"{name} divergence defect did not close")
        if record["polarization_symmetric"] is not True:
            raise AssertionError(f"{name} polarization is not symmetric")
    return {
        "schema": "pure-weyl-relative-five-stabilizer-current-cone-v1",
        "result_id": RESULT_ID,
        "result_state": "FIVE_STABILIZER_OFF_SHELL_CURRENT_CONE_CERTIFIED",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product",
            "boundaries": "local coefficient jets; no Cauchy integration",
            "charge_sector": "H,P_x,J_1,J_2,J_3 connected-isometry stabilizers",
            "carrier": "g_stab^*-valued polarized horizontal current/divergence cone",
            "degree": "symmetric arity-two relative Noether-current source",
            "parity": "all fourteen physical metric and Maxwell components",
            "ell": "not harmonic-reduced",
            "m": "not harmonic-reduced",
            "k": "not harmonic-reduced",
            "omega": "not harmonic-reduced",
        },
        "dependencies": {
            name: _artifact(path, dependencies[name]) for name, path in DEPENDENCIES.items()
        },
        "generator_conventions": {
            "H": "partial_t",
            "P_x": "partial_x",
            "J_1": "partial_phi",
            "J_2": "cos(phi)*partial_theta-cot(theta)*sin(phi)*partial_phi",
            "J_3": "sin(phi)*partial_theta+cot(theta)*cos(phi)*partial_phi",
            "metric_lift": "tensor Lie derivative",
            "maxwell_lift": "i_X da=L_X a-d(i_X a)",
        },
        "records": data["records"],
        "classification": {
            "five_generators_killing": True,
            "five_generators_preserve_magnetic_background": True,
            "bundle_covariant_actions_exported": True,
            "five_polarized_current_precompositions_exported": True,
            "all_five_polarizations_symmetric": True,
            "all_five_off_shell_divergence_identities_exact": True,
            "lee_wald_improvement_comparison_certified": False,
            "cyclic_dual_bv_rows_certified": False,
            "slice_integral_matches_complete_five_charge_q2": False,
            "direct_f2_repaired": False,
            "arity_three_authorized": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "COMPARE_FIVE_GREEN_CURRENTS_WITH_LEE_WALD_BY_HORIZONTAL_IMPROVEMENTS",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), CORE, VERIFIER, TESTS, SCHEMA)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_five_stabilizer_current_cone --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_five_stabilizer_current_cone",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_five_stabilizer_current_cone",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-five-stabilizer-current-cone-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_STABILIZER_CURRENT_CONE_V1.json",
            ],
        },
        "claim_boundary": (
            "This artifact certifies the exact local precomposition of the densitized relative Hessian Green current with all five connected product stabilizers, using the tensor Lie derivative for metric perturbations and the fixed-bundle gauge-covariant Cartan lift for Maxwell perturbations. Every polarized current is symmetric and its complete coefficient-jet divergence equals the action-Euler source with zero defect. It does not yet prove that these canonical Green-current representatives equal the action-derived Lee-Wald representatives up to explicit horizontal improvements, construct the cyclic BV-dual rows, reproduce every reduced five-charge block after Cauchy integration, repair the direct f2 obstruction, authorize arity three, or establish causal, observational, particle or quantum claims."
        ),
    }


def validate(value: dict) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Five-stabilizer relative current cone

The densitized relative Hessian Green current is now precomposed with the
complete connected product stabilizer basis

\[
H=\partial_t,\qquad P_x=\partial_x,\qquad J_1,J_2,J_3\in\mathfrak{so}(3).
\]

The metric action is the tensor Lie derivative.  The Maxwell action is the
fixed-bundle Cartan lift \(\iota_Xda={\cal L}_Xa-d(\iota_Xa)\).  Direct
geometric checks show that every declared generator preserves both the metric
and magnetic two-form.  For each generator, exact PBW composition constructs
the symmetric polarized current and independently computes its action-Euler
source.  All five complete coefficient-jet divergence defects vanish.

This is the full local five-generator equation cone.  The remaining bridge is
to exhibit the horizontal improvements relating these canonical Green
representatives to the separately action-derived Lee--Wald currents, then add
the cyclic BV-dual rows and replay the Cauchy-slice charges.
"""


def _guards(value: dict) -> None:
    for key in (
        "lee_wald_improvement_comparison_certified",
        "cyclic_dual_bv_rows_certified",
        "slice_integral_matches_complete_five_charge_q2",
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
    if args.check and (OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report()):
        raise AssertionError("five-stabilizer current-cone outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
