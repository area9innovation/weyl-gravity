#!/usr/bin/env python3
"""Export the local polarized relative Noether-current seed."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.relative.einstein_weyl_relative_noether_current import (
    gauge_covariant_lie_derivative_potential,
    polarized_relative_noether_current_component,
)


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_POLARIZED_NOETHER_CURRENT_SEED_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-polarized-noether-current-seed.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-polarized-noether-current-seed-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_polarized_noether_current_seed.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_noether_current.py"
CURRENT = ROOT / "d_quotient_classical/relative/einstein_weyl_relative_noether_current.py"

DEPENDENCIES = {
    "component_evaluator_receipt": ROOT / "d_quotient_classical/receipts/WEYL_MAXWELL_LEE_WALD_COMPONENT_EVALUATOR_V1_TIER_RECEIPT.json",
    "complete_charge_q2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_COMPLETE_STANDARD_FIVE_CHARGE_Q2_V1.json",
    "taub_descent": ROOT / "bridge/certificates/compact_harmonic_domain_taub_descent.json",
    "moment_map_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
}


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: Path, value: dict) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _exact_fixture() -> tuple[sp.Expr, sp.Matrix]:
    coordinates = sp.symbols("t x y z")
    t, x, y, z = coordinates
    metric = sp.diag(-1, 1, 1, 1)
    field = sp.zeros(4)
    generator = sp.Matrix([1, 0, 0, 0])
    zero_potential = sp.zeros(4, 1)
    first_metric = sp.zeros(4)
    second_metric = sp.zeros(4)
    first_metric[1, 2] = first_metric[2, 1] = t * x
    second_metric[1, 2] = second_metric[2, 1] = t**2 * x
    first = (first_metric, zero_potential)
    second = (second_metric, zero_potential)
    forward = polarized_relative_noether_current_component(
        metric, field, first, second, generator, coordinates, 1
    )
    reverse = polarized_relative_noether_current_component(
        metric, field, second, first, generator, coordinates, 1
    )
    if sp.simplify(forward - 3 * x / 8) != 0 or sp.simplify(forward - reverse) != 0:
        raise AssertionError("polarized current fixture drifted")

    potential = sp.Matrix([t * x, t**2 + y, x * z, t * y])
    covariant = gauge_covariant_lie_derivative_potential(potential, generator, coordinates)
    coordinate_lie = potential.applyfunc(lambda entry: sp.diff(entry, t))
    exact = sp.Matrix([sp.diff(potential[0], coordinate) for coordinate in coordinates])
    cartan_defect = (covariant - coordinate_lie + exact).applyfunc(sp.simplify)
    if cartan_defect != sp.zeros(4, 1):
        raise AssertionError("bundle-covariant Cartan formula drifted")
    return sp.factor(forward), cartan_defect


def build() -> dict:
    records = {name: _load(path) for name, path in DEPENDENCIES.items()}
    receipt = records["component_evaluator_receipt"]
    complete = records["complete_charge_q2"]
    descent = records["taub_descent"]
    if receipt["status"] != "PASS":
        raise AssertionError("component evaluator receipt is not passing")
    if complete["classification"]["complete_standard_source_five_charge_q2"] is not True:
        raise AssertionError("complete five-charge q2 is not certified")
    if descent["classification"]["gauge_descent_from_noether_identity"] is not True:
        raise AssertionError("Noether descent input is not certified")
    fixture, _ = _exact_fixture()
    if fixture == 0:
        raise AssertionError("local current fixture unexpectedly vanished")

    return {
        "schema": "pure-weyl-relative-polarized-noether-current-seed-v1",
        "result_id": RESULT_ID,
        "result_state": "LOCAL_CURRENT_SEED_EXPORTED",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "local coordinate presentation, with the magnetic product as the intended global specialization",
            "boundaries": "local compactly supported jets; no Cauchy integration in this artifact",
            "charge_sector": "one arbitrary spacetime stabilizer generator X at a time",
            "carrier": "horizontal relative Noether three-current encoded as a four-component vector density",
            "degree": "symmetric arity-two current seed",
            "parity": "all",
            "ell": "not harmonic-reduced",
            "m": "not harmonic-reduced",
            "k": "not harmonic-reduced",
            "omega": "not harmonic-reduced",
        },
        "dependencies": {name: _artifact(path, records[name]) for name, path in DEPENDENCIES.items()},
        "construction": {
            "relative_current": "omega_Weyl-Maxwell - omega_Einstein-Maxwell",
            "polarized_current": "j_X(u,v)=(omega_rel(u,L_X v)+omega_rel(v,L_X u))/2",
            "metric_action": "ordinary tensor Lie derivative L_X h",
            "maxwell_action": "bundle-covariant lift i_X da = L_X a - d(i_X a)",
            "horizontal_carrier": "Omega_H^3(M;g_stab^*)",
            "global_charge_operation": "integrate the closed current over a Cauchy slice only after the divergence identity is imposed",
        },
        "exact_fixtures": {
            "cartan_formula": True,
            "polarization_symmetric": True,
            "nonzero_spatial_fixture": "j^x_D(t*x dxdy,t^2*x dxdy)=3*x/8 on Minkowski space",
            "component_api": "mu=0,1,2,3 with fail-closed bounds",
        },
        "classification": {
            "all_four_action_current_components_exported": True,
            "bundle_covariant_stabilizer_action": True,
            "polarized_relative_current_exported": True,
            "finite_order_support_local": True,
            "off_shell_divergence_cone_certified": False,
            "slice_integral_matches_complete_five_charge_q2": False,
            "cyclic_dual_rows_certified": False,
            "direct_f2_repaired": False,
            "arity_three_authorized": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "CERTIFY_OFF_SHELL_DIVERGENCE_CONE_AND_CYCLIC_DUAL_ROWS",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), CURRENT, VERIFIER, TESTS, SCHEMA)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_polarized_noether_current_seed --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_polarized_noether_current_seed",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_noether_current",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-polarized-noether-current-seed-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_POLARIZED_NOETHER_CURRENT_SEED_V1.json",
            ],
        },
        "claim_boundary": (
            "This artifact exports a finite-order support-local evaluator for all four components of the action-derived polarized relative Lee-Wald current and a bundle-covariant lift of each stabilizer generator to Maxwell connection perturbations. It verifies the Cartan formula, symmetry of polarization and an exact nonzero spatial-current fixture. It does not yet replay the full off-shell horizontal divergence identity against the Einstein-Maxwell and Weyl-Maxwell equation rows, construct the cyclic dual current/divergence rows, prove that Cauchy integration reproduces every block of the complete five-charge reduced q2, repair the direct f2 obstruction, authorize arity three, or establish causal, observational, particle or quantum claims."
        ),
    }


def validate(value: dict) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Polarized relative Noether-current seed

The local carrier required by the finite-charge locality obstruction is now
explicit.  For a spacetime stabilizer generator (X), define

\[
j_X(u,v)=\frac12\{\omega_{\rm rel}(u,{\cal L}_Xv)
                  +\omega_{\rm rel}(v,{\cal L}_Xu)\},
\qquad
\omega_{\rm rel}=\omega_{\rm WM}-\omega_{\rm EM}.
\]

The metric action is the tensor Lie derivative.  The Maxwell action is the
globally meaningful fixed-bundle lift

\[
{\cal L}^{\rm cov}_X a=\iota_X da
={\cal L}_Xa-d(\iota_Xa).
\]

The exported evaluator returns every vector-density component.  Exact tests
verify this Cartan formula, symmetry in the two inputs, fail-closed component
bounds, and the nonzero local fixture

\[
j_D^x(t x\,dx\,dy,t^2x\,dx\,dy)=\frac{3x}{8}
\]

on Minkowski space.  This establishes a nontrivial support-local current
seed, not the full equation cone.  The off-shell divergence identity, cyclic
dual rows and equality of all integrated five-charge blocks remain the next
gate.
"""


def _guards(value: dict) -> None:
    false_keys = (
        "off_shell_divergence_cone_certified",
        "slice_integral_matches_complete_five_charge_q2",
        "cyclic_dual_rows_certified",
        "direct_f2_repaired",
        "arity_three_authorized",
        "causal_observable_particle_or_quantum_claim",
    )
    for key in false_keys:
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
        raise AssertionError("relative current seed outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
