#!/usr/bin/env python3
"""Independent exact verifier for STRUCTURED_METRIC_QUARTET_NO_GO_V1.

This rail does not import the producer.  It reconstructs the companion matrix
from the hash-pinned classical payload and redoes the spectral and nilpotent
arguments with separate code paths.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError
import sympy as sp


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificates/STRUCTURED_METRIC_QUARTET_NO_GO_V1.json"
SCHEMA = HERE / "schema/structured-metric-quartet-no-go-v1.schema.json"
RECEIPT = HERE / "receipts/STRUCTURED_METRIC_QUARTET_NO_GO_V1_TIER_RECEIPT.json"
REPORT = ROOT / "reports/phase2-cpt-quartet-negative-control-2026-07-22.md"

EXPECTED_INPUTS = {
    "selected_jhalf": (
        ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_PAYLOAD_V1.json",
        "43595d6e974dd3ff852db658014fb34dcd1521f050a752e5732fb0c3b5f27797",
        "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_PAYLOAD_V1",
    ),
    "healthy_family": (
        ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_PAYLOAD_V1.json",
        "88e5f9a25ff3a5cfbbdbbbe1492ec879f6bfb1f495aed3aa4241b8e58e413508",
        "TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_PAYLOAD_V1",
    ),
    "retained_operator": (
        ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json",
        "296bd46e4d94320a6a5b227167d722da1793d1f81891dcf2e494f9b631dcdd77",
        "BERGER_RETAINED_MINIMAL_OPERATOR",
    ),
}

OUTPUTS = {
    "generator": HERE / "structured_metric_quartet_no_go.py",
    "verifier": Path(__file__),
    "schema": SCHEMA,
    "certificate": CERTIFICATE,
    "tests": HERE / "tests/test_structured_metric_quartet_no_go.py",
    "report": REPORT,
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(value, locals={"I": sp.I}) for value in row] for row in rows])


def _load_sources() -> dict[str, Any]:
    values: dict[str, Any] = {}
    for role, (path, expected_hash, result_id) in EXPECTED_INPUTS.items():
        if _sha(path) != expected_hash:
            raise AssertionError(f"{role} input hash drift")
        value = json.loads(path.read_text())
        if value.get("result_id") != result_id:
            raise AssertionError(f"{role} result id drift")
        values[role] = value
    return values


def _verify_nilpotent_gate(certificate: dict[str, Any]) -> None:
    theorem = certificate["nilpotent_positive_metric_no_go"]
    q_matrix = _matrix(theorem["nonzero_nilpotent_fixture_Q"])
    if q_matrix == sp.zeros(2) or q_matrix**2 != sp.zeros(2):
        raise AssertionError("nonzero nilpotent fixture invalid")

    # Independent coordinate obstruction.  For eta=[[a,b+ic],[b-ic,d]],
    # Q^dagger eta=eta Q forces a=0, contradicting strict positivity.
    a, b, c, d = sp.symbols("a b c d", real=True)
    eta = sp.Matrix([[a, b + sp.I * c], [b - sp.I * c, d]])
    defect = q_matrix.conjugate().T * eta - eta * q_matrix
    equations = [sp.expand(entry) for entry in defect if entry != 0]
    solutions = sp.solve(equations, [a, c], dict=True)
    if not solutions or any(solution.get(a) != 0 for solution in solutions):
        raise AssertionError("nilpotent coordinate obstruction did not force a=0")
    if theorem["nontrivial_BRST_positive_self_adjoint_gate_feasible"] is not False:
        raise AssertionError("positive self-adjoint nonzero BRST mutation accepted")

    brst = certificate["structured_metric_contract"]["BRST_compatibility"]
    if "chain map" not in brst["accepted_chain_gate"] or "pi*i=1" not in brst["accepted_cohomology_gate"]:
        raise AssertionError("corrected BRST compatibility contract missing")
    if "forces ||Qv||" not in brst["rejection_reason"]:
        raise AssertionError("nilpotent no-go reason weakened")


def _verify_selected_quartet(certificate: dict[str, Any], source: dict[str, Any]) -> None:
    row = certificate["selected_counterflow_negative_control"]
    unstable = source["unstable_sector"]
    a = sp.Rational(unstable["principal_time_order_four_matrix"][0][0])
    b = sp.Rational(unstable["time_order_two_matrix"][0][0])
    c = sp.Rational(unstable["fixed_isotype_spatial_potential_matrix"][0][0])
    expected_a = sp.Matrix(
        [[0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [-c / a, 0, -b / a, 0]]
    )
    actual_a = _matrix(row["real_companion_generator_A"])
    actual_h = _matrix(row["Schrodinger_generator_H_equals_iA"])
    if actual_a != expected_a or actual_h != sp.I * expected_a:
        raise AssertionError("companion or Schrodinger generator mismatch")

    z = sp.symbols("z")
    characteristic = sp.factor((z * sp.eye(4) - expected_a).det())
    source_factor = a * z**4 + b * z**2 + c
    retained = source["imports"]["retained_operator"]
    if (
        retained["sha256"] != EXPECTED_INPUTS["retained_operator"][1]
        or retained["result_id"] != EXPECTED_INPUTS["retained_operator"][2]
    ):
        raise AssertionError("physical quotient retained-operator provenance mismatch")
    physical_h_hash = source["physical_quotient"]["maps"]["physical_H"]["sha256"]
    if row["source_physical_H_sha256"] != physical_h_hash:
        raise AssertionError("physical Hessian hash not preserved")
    complete_characteristic = sp.sympify(
        source["physical_quotient"]["characteristic_determinant_monic"],
        locals={"z": z},
    )
    if sp.rem(sp.Poly(complete_characteristic, z), sp.Poly(source_factor**2, z)) != 0:
        raise AssertionError("quartet multiplicity in full physical determinant failed")
    if row["source_complete_characteristic_determinant_monic"] != source["physical_quotient"]["characteristic_determinant_monic"]:
        raise AssertionError("complete physical characteristic was not imported exactly")
    if sp.factor(a * characteristic - source_factor) != 0:
        raise AssertionError("independent characteristic reconstruction failed")
    stored_characteristic = sp.sympify(
        row["characteristic_polynomial_A_monic"], locals={"z": z}
    )
    if sp.simplify(stored_characteristic - characteristic) != 0:
        raise AssertionError("stored monic characteristic mismatch")

    discriminant = sp.factor(b**2 - 4 * a * c)
    if discriminant != -2151 or row["y_equals_z_squared_discriminant"] != "-2151":
        raise AssertionError("complex-quartet discriminant mutation")
    if sp.factor(-discriminant - 9 * 239) != 0:
        raise AssertionError("algebraic splitting-field witness failed")
    if row["root_class"] != "HAMILTONIAN_HOPF_QUARTET_NONZERO_REAL_AND_IMAGINARY_PARTS":
        raise AssertionError("real-spectrum mutation accepted")

    # If y=z^2 is nonreal, z is neither real nor purely imaginary.  Thus i*z
    # is nonreal, contradicting the necessary real spectrum of every H that
    # is self-adjoint in a strictly positive eta metric.
    if row["positive_eta_feasible"] is not False:
        raise AssertionError("positive eta mutation accepted")
    if row["norm_only_rescue_possible"] is not False:
        raise AssertionError("norm-only rescue mutation accepted")
    if row["C_operator_claimed"] is not False:
        raise AssertionError("eta was promoted to a C operator")


def _verify_family(certificate: dict[str, Any], source: dict[str, Any]) -> None:
    row = certificate["family_counterflow_negative_control"]
    q = sp.symbols("q", positive=True, real=True)
    a = 16 * q**2
    b = 24 * q * (3 - 2 * q**2)
    c = 32 * q**3 - 108 * q**2 + 81
    discriminant = sp.factor(b**2 - 4 * a * c)
    if discriminant != 256 * q**5 * (9 * q - 8):
        raise AssertionError("family discriminant reconstruction failed")
    if row["discriminant"] != "256*q**5*(9*q - 8)":
        raise AssertionError("stored family discriminant drifted")
    imported_reason = source["terminal_verdict"]["structural_reason"]
    if "for every 0<q<1/4" not in imported_reason:
        raise AssertionError("imported family interval weakened")
    if row["positive_eta_feasible_everywhere_on_component"] is not False:
        raise AssertionError("family positive eta mutation accepted")


def verify_certificate(certificate: dict[str, Any], *, verify_hashes: bool = True) -> None:
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    sources = _load_sources()
    if verify_hashes:
        for role, reference in certificate["source_refs"].items():
            path, expected_hash, result_id = EXPECTED_INPUTS[role]
            if reference != {
                "path": str(path.relative_to(ROOT)),
                "sha256": expected_hash,
                "result_id": result_id,
                "input_commit": "4a212883aefa5525cc847d0c12763c74c1c3411a",
            }:
                raise AssertionError(f"{role} source reference drift")
    _verify_nilpotent_gate(certificate)
    _verify_selected_quartet(certificate, sources["selected_jhalf"])
    _verify_family(certificate, sources["healthy_family"])

    contract = certificate["structured_metric_contract"]
    if not contract["C_operator_additional_required_data"]["eta_is_not_C_by_definition"]:
        raise AssertionError("eta/C distinction removed")
    decision = certificate["decision"]
    if decision["Mannheim_C_operator"] != "NOT_CONSTRUCTED":
        raise AssertionError("Mannheim construction overpromotion")
    if decision["field_theoretic_state_or_unitarity"] != "NOT_ESTABLISHED":
        raise AssertionError("finite block promoted to unitarity")


def verify_receipt(receipt: dict[str, Any], certificate: dict[str, Any]) -> None:
    if receipt["subject_result_id"] != certificate["result_id"]:
        raise AssertionError("receipt subject mismatch")
    for role, reference in certificate["source_refs"].items():
        if receipt["source_pins"][role] != reference["sha256"]:
            raise AssertionError(f"receipt source pin mismatch: {role}")
    if set(receipt["output_hashes"]) != set(OUTPUTS):
        raise AssertionError("receipt output manifest mismatch")
    for role, path in OUTPUTS.items():
        if receipt["output_hashes"][role] != _sha(path):
            raise AssertionError(f"receipt output hash mismatch: {role}")


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    verify_certificate(certificate)
    mutations = [
        lambda value: value["selected_counterflow_negative_control"].update(
            root_class="PURELY_IMAGINARY_REAL_SPECTRUM"
        ),
        lambda value: value["selected_counterflow_negative_control"].update(
            positive_eta_feasible=True
        ),
        lambda value: value["selected_counterflow_negative_control"].update(
            norm_only_rescue_possible=True
        ),
        lambda value: value["nilpotent_positive_metric_no_go"].update(
            nontrivial_BRST_positive_self_adjoint_gate_feasible=True
        ),
        lambda value: value["selected_counterflow_negative_control"].update(
            C_operator_claimed=True
        ),
        lambda value: value["decision"].update(
            field_theoretic_state_or_unitarity="CERTIFIED"
        ),
    ]
    for mutate in mutations:
        mutant = copy.deepcopy(certificate)
        mutate(mutant)
        try:
            verify_certificate(mutant, verify_hashes=False)
        except (AssertionError, KeyError, TypeError, ValidationError):
            continue
        raise AssertionError("decisive mutation was accepted")
    receipt = json.loads(RECEIPT.read_text())
    verify_receipt(receipt, certificate)
    print(
        "STRUCTURED_METRIC_QUARTET_NO_GO_V1 independent verification: "
        f"PASS ({len(mutations)} decisive mutations rejected)"
    )


if __name__ == "__main__":
    main()
