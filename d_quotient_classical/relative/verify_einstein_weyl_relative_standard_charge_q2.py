#!/usr/bin/env python3
"""Independent consumer for the standard-radiative relative charge q2."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_STANDARD_RADIATIVE_CHARGE_Q2_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-standard-radiative-charge-q2-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for relative, expected in value["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != expected:
            raise AssertionError(f"source hash drifted: {relative}")
    for artifact in value["dependencies"].values():
        if _sha(ROOT / artifact["path"]) != artifact["sha256"]:
            raise AssertionError(f"dependency hash drifted: {artifact['path']}")

    radiative = json.loads((ROOT / value["dependencies"]["radiative_restriction"]["path"]).read_text())
    lam = sp.symbols("lambda", positive=True)
    weights = [
        sp.sympify(text.replace("lambda", "lam"), locals={"lam": lam})
        for text in radiative["theorem"]["all_ell_ge_2_classification"]["common_relative_weights"]
    ]
    relative = [sp.simplify(weight - 1) for weight in weights]
    expected = [sp.Rational(3, 2) * sp.sqrt(2 * lam), -sp.Rational(3, 2) * sp.sqrt(2 * lam)]
    if any(sp.simplify(got - want) != 0 for got, want in zip(relative, expected)):
        raise AssertionError("branch coefficient replay failed")
    coefficient_data = value["operation"]["coefficient_data"]
    parity_blocks = radiative["theorem"]["parity_blocks"]
    if coefficient_data["axial_G_EM"] != parity_blocks["axial"]["einstein_coefficient_form"]:
        raise AssertionError("axial coefficient-form replay failed")
    if coefficient_data["polar_G_EM"] != parity_blocks["polar"]["einstein_coefficient_form"]:
        raise AssertionError("polar coefficient-form replay failed")
    stabilizer = json.loads((ROOT / value["dependencies"]["stabilizer"]["path"]).read_text())
    if coefficient_data["angular_W_ell"] != stabilizer["rotation_representation"]["all_ell_proof"]["angular_weight"]:
        raise AssertionError("angular coefficient-form replay failed")

    obstruction = json.loads((ROOT / value["dependencies"]["f2_obstruction"]["path"]).read_text())
    half_h = sp.sympify(obstruction["taub_pairing"]["relative_half_delta2_pairing"])
    full_h = 2 * half_h
    witness = value["operation"]["h_witness"]
    if sp.simplify(sp.sympify(witness["half_diagonal_taub_value"]) - half_h) != 0:
        raise AssertionError("half-diagonal witness drifted")
    if sp.simplify(sp.sympify(witness["q2_charge_H_diagonal"]) - full_h) != 0:
        raise AssertionError("q2 diagonal factor-two replay failed")

    basis = value["operation"]["output_basis"]
    if basis != ["H", "P_x", "J_1", "J_2", "J_3"] or len(set(basis)) != 5:
        raise AssertionError("charge basis drifted")
    flags = value["classification"]
    if flags["descends_to_standard_radiative_cohomology"] is not True:
        raise AssertionError("cohomology descent dropped")
    quotient_domains = value["identities"]["imported_quotient_domains"]
    imported_domains = {
        "moment_map_taub_bridge": json.loads(
            (ROOT / value["dependencies"]["moment_map_taub_bridge"]["path"]).read_text()
        )["domain"],
        "stabilizer": stabilizer["domain"],
    }
    if quotient_domains != imported_domains:
        raise AssertionError("local-gauge quotient domain replay failed")
    if any("after local gauge reduction" not in domain for domain in imported_domains.values()):
        raise AssertionError("imported input is not on the local-gauge quotient")
    if "no off-shell representative-level lift" not in value["identities"]["cohomology_domain_certificate"]:
        raise AssertionError("cohomology-domain boundary drifted")
    forbidden = (
        "constant_u1_charge_output",
        "exceptional_and_global_charge_q2_included",
        "off_shell_local_jet_charge_q2",
        "support_local_bv_koszul_extension",
        "direct_f2_repaired",
        "arity_three_authorized",
        "causal_observable_particle_or_quantum_claim",
    )
    if any(flags[key] is not False for key in forbidden):
        raise AssertionError("forbidden downstream promotion")
    return {
        "status": "PASS",
        "charge_output_dimension": len(basis),
        "relative_branch_coefficients": [str(sp.factor(item)) for item in relative],
        "h_half_diagonal": str(sp.factor(half_h)),
        "h_q2_diagonal": str(sp.factor(full_h)),
        "coefficient_forms_replayed": True,
        "cohomology_descent_replayed": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
