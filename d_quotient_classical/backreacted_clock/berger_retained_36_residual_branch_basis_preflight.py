#!/usr/bin/env python3
"""Audit the exact input contract for the retained 36-row branch basis."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
from sympy import Matrix, QQ, sqrt
from sympy.polys.polyerrors import CoercionFailed


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_PREFLIGHT.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-36-residual-branch-basis-preflight-v1.schema.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-retained-36-residual-branch-basis-preflight.md"

DEPENDENCIES = {
    "quantum_input_schema": ROOT / "quantum-weyl/transfer/schema/berger-residual-ell3-branch-basis-input-v1.schema.json",
    "quantum_readiness": ROOT / "quantum-weyl/transfer/certificates/BERGER_RESIDUAL_MIXED_ELL3_BRANCH_PROJECTION_READINESS.json",
    "typed_retained_sdr": ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR.json",
    "accepted_retained_ell3": ROOT / "quantum-weyl/transfer/certificates/BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_ACCEPTANCE.json",
}

SOURCE_FILES = {
    "producer": Path(__file__),
    "independent_verifier": ROOT / "d_quotient_classical/backreacted_clock/verify_berger_retained_36_residual_branch_basis_preflight.py",
    "tests": ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_retained_36_residual_branch_basis_preflight.py",
    "schema": SCHEMA,
    "report": REPORT,
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _sqrt2_in_qsqrt10() -> bool:
    field = QQ.algebraic_field(sqrt(10))
    try:
        field.from_sympy(sqrt(2))
    except CoercionFailed:
        return False
    return True


def _matrix_receipt() -> dict[str, Any]:
    swap = Matrix([[0, 1], [1, 0]])
    normalized = Matrix([[1, 1], [1, -1]]) / sqrt(2)
    unnormalized = Matrix([[1, 1], [1, -1]])
    identity = Matrix.eye(2)
    parity = Matrix.diag(1, -1)
    checks = {
        "normalized_gram_is_identity": normalized * normalized.T == identity,
        "normalized_parity_is_even_odd": normalized * swap * normalized.inv() == parity,
        "unnormalized_gram_is_two_identity": unnormalized * unnormalized.T == 2 * identity,
        "unnormalized_parity_is_even_odd": unnormalized * swap * unnormalized.inv() == parity,
    }
    if not all(checks.values()):
        raise AssertionError("even/odd basis matrix receipt failed")
    return {
        "chiral_basis": ["W_plus_squared", "W_minus_squared"],
        "input_chiral_gram_assumption": "I2_FOR_BASIS_CHANGE_RECEIPT_ONLY_NOT_IMPORTED_AS_A_BERGER_BRANCH_ARTIFACT",
        "normalized_even_odd_matrix": [["1/sqrt(2)", "1/sqrt(2)"], ["1/sqrt(2)", "-1/sqrt(2)"]],
        "unnormalized_even_odd_matrix": [["1", "1"], ["1", "-1"]],
        "normalized_gram": [["1", "0"], ["0", "1"]],
        "unnormalized_gram": [["2", "0"], ["0", "2"]],
        "parity_in_even_odd_basis": [["1", "0"], ["0", "-1"]],
        "exact_checks": checks,
    }


def build() -> dict[str, Any]:
    input_schema = json.loads(DEPENDENCIES["quantum_input_schema"].read_text())
    readiness = json.loads(DEPENDENCIES["quantum_readiness"].read_text())
    retained = json.loads(DEPENDENCIES["typed_retained_sdr"].read_text())
    accepted = json.loads(DEPENDENCIES["accepted_retained_ell3"].read_text())

    declared_field = input_schema["properties"]["declared_scope"]["properties"]["coefficient_field"]["const"]
    required_ids = readiness["input_contract"]["required_deformation_vertex_basis_ids"]
    if declared_field != "Q(sqrt(10))":
        raise AssertionError("quantum input field changed; preflight must be rederived")
    if required_ids != ["e_C2_dynamical", "o_C_dual_C_topological"]:
        raise AssertionError("even/odd deformation basis contract drifted")
    if readiness["result_state"] != "CONSUMER_READY_RESIDUAL_BRANCH_BASIS_INPUT_NOT_SUPPLIED":
        raise AssertionError("quantum readiness lifecycle changed")
    if retained["retained_complex"]["total_rows"] != 36:
        raise AssertionError("retained carrier rank drifted")
    if not retained["exact_checks"]["q36_typed_pairing_cyclic"]:
        raise AssertionError("retained pairing is not certified cyclic")
    if accepted["claim_flags"]["RETAINED_MIXED_ELL3_CONTACT_INDEPENDENTLY_REPLAYED"] is not True:
        raise AssertionError("accepted retained ell3 dependency absent")

    membership = _sqrt2_in_qsqrt10()
    if membership:
        raise AssertionError("unexpected field-membership result")
    matrix_receipt = _matrix_receipt()
    dependency_refs = {
        name: {"path": str(path.relative_to(ROOT)), "sha256": _sha(path)}
        for name, path in DEPENDENCIES.items()
    }
    payload = {
        "schema": "pure-weyl-berger-retained-36-residual-branch-basis-preflight-v1",
        "result_id": "BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_PREFLIGHT",
        "result_state": "INPUT_CONTRACT_FIELD_REPAIR_REQUIRED_BRANCH_PROJECTOR_STILL_MISSING",
        "setting_id": "compact_positive_berger_clock_fixed_coupling",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": dependency_refs,
        "available_exact_inputs": {
            "retained_rank": 36,
            "retained_q1": True,
            "retained_typed_cyclic_pairing": True,
            "retained_mixed_ell3": True,
            "deformation_chiral_pairing_gram_imported": False,
            "parity_normalized_deformation_basis_over_declared_field": False,
            "Einstein_like_extra_Weyl_Maxwell_branch_projector": False,
        },
        "field_obstruction": {
            "declared_field": declared_field,
            "required_normalization_coefficient": "1/sqrt(2)",
            "sqrt2_is_member_of_declared_field": membership,
            "proof": "If sqrt(2)=a+b sqrt(10) with rational a,b, squaring gives 2ab=0 and a^2+10b^2=2. If b=0 then a^2=2, impossible over Q; if a=0 then b^2=1/5, also impossible over Q.",
            "sympy_exact_membership_check": "QQ.algebraic_field(sqrt(10)).from_sympy(sqrt(2)) raises CoercionFailed",
            "consequence": "The normalized e/o basis required by the readiness claim boundary cannot be represented by an artifact whose sole coefficient field is Q(sqrt(10)).",
        },
        "even_odd_matrix_receipt": matrix_receipt,
        "minimal_contract_repairs": [
            {
                "repair_id": "EXTEND_DEFORMATION_FIELD",
                "recommended": True,
                "operator_coefficient_field": "Q(sqrt(10))",
                "deformation_coefficient_field": "Q(sqrt(2),sqrt(10))",
                "normalization": "retain e=(W_+^2+W_-^2)/sqrt(2), o=(W_+^2-W_-^2)/sqrt(2), Gram=I2",
            },
            {
                "repair_id": "USE_UNNORMALIZED_PARITY_BASIS",
                "recommended": False,
                "operator_coefficient_field": "Q(sqrt(10))",
                "deformation_coefficient_field": "Q(sqrt(10))",
                "normalization": "use e0=W_+^2+W_-^2, o0=W_+^2-W_-^2, Gram=2 I2 and record the later scalar extension explicitly",
            },
        ],
        "v2_contract_requirements": [
            "split operator_field=Q(sqrt(10)) from deformation_field=Q(sqrt(2),sqrt(10))",
            "import a content-addressed chiral deformation pairing and derive, rather than assume, the even/odd Gram matrix",
            "separate dynamical branch carriers from deformation/vertex carriers with typed domains for pairing, parity and reality",
            "declare the exact mode or support sector, BV degrees, chirality or polarization ranges and multiplicities before asserting branch exhaustiveness",
            "type every artifact by schema, result_id, source and target ranks and degrees, coefficient field and exact chain/intertwining identities",
            "replace free-form Maxwell branch names with canonical carrier IDs and dimensions",
            "declare complexification and the antilinear real structure whenever mode carriers use the scalar i",
            "pin Euler-Lagrange rank normalization, Pontryagin orientation and transgression conventions, plus mutation-tested witnesses for claimed zeros",
        ],
        "separate_missing_carrier": {
            "status": "NOT_EXPORTED_NOT_A_NONEXISTENCE_THEOREM",
            "required_object": "exact Einstein-like/extra-Weyl/Maxwell dynamical carrier with inclusion, projection, pairing, parity, real structure and K_Berger weights",
            "why_q1_and_pairing_are_insufficient": "The 36-row SDR identifies a retained local BV carrier but does not choose a dynamical solution or residual-mode subquotient. Labeling rows cannot replace a q1-intertwining branch projection.",
            "next_mathematical_gate": "construct the exact Berger dynamical branch carrier in a declared mode/support sector and verify projection times inclusion equals identity together with q1, pairing, parity, reality and K_Berger intertwining",
        },
        "flags": {
            "RETAINED_36_Q1_AVAILABLE": True,
            "RETAINED_36_TYPED_PAIRING_AVAILABLE": True,
            "RETAINED_MIXED_ELL3_AVAILABLE": True,
            "CURRENT_INPUT_SCHEMA_FIELD_CONSISTENT_WITH_NORMALIZED_EO_BASIS": False,
            "DYNAMICAL_BRANCH_PROJECTOR_AVAILABLE": False,
            "BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V1_READY": False,
            "ELL3_BRANCH_PROJECTION_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "REISSUE_BRANCH_BASIS_INPUT_SCHEMA_WITH_EXACT_DEFORMATION_FIELD_THEN_CONSTRUCT_DYNAMICAL_BRANCH_PROJECTOR",
        "provenance": {
            "source_manifest": [
                {"role": role, "path": str(path.relative_to(ROOT)), "sha256": _sha(path)}
                for role, path in SOURCE_FILES.items()
            ],
            "dependency_manifest_sha256": _canonical_sha(dependency_refs),
        },
        "claim_boundary": "This exact LOCAL-ALGEBRAIC preflight does not supply BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V1. It proves that the current receiving contract combines the coefficient field Q(sqrt(10)) with a normalized even/odd deformation basis requiring 1/sqrt(2), which is not an element of that field. It gives two exact repairs and independently records that the available 36-row q1, pairing and ell3 artifacts still do not contain an Einstein-like/extra-Weyl/Maxwell dynamical branch projector. The absence of that export is not a global nonexistence theorem. No residual mixing, kinetic-sign, particle, QME, Hadamard or quantum claim is made.",
    }
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise AssertionError("branch-basis preflight certificate drifted")
    print("BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_PREFLIGHT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
