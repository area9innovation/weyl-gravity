"""Emit the fail-closed first-order quantum Cartan-defect precertificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from .classical_import import import_receipt, imported_setting_ledger, load_classical_d_status
from .defect_complex import (
    AdmissibleOperatorComplex,
    ExactMatrix,
    FiniteGradedComplex,
    FirstOrderCartanData,
    HomogeneousOperator,
    LinearConstraint,
    classify_closed_defect,
)


PACKAGE_ROOT = Path(__file__).resolve().parent
QUANTUM_ROOT = PACKAGE_ROOT.parent
REPOSITORY_ROOT = QUANTUM_ROOT.parent
OUTPUT_PATH = PACKAGE_ROOT / "certificates" / "CARTAN_DEFECT_COMPLEX_PRECERTIFICATE.json"
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "cartan_defect_precertificate.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _rational(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _operator_payload(operator: HomogeneousOperator) -> dict[str, Any]:
    entries = []
    for row_index, row in enumerate(operator.matrix.rows):
        for column_index, value in enumerate(row):
            if value:
                entries.append(
                    {
                        "target": row_index,
                        "source": column_index,
                        "coefficient": _rational(value),
                    }
                )
    return {
        "name": operator.name,
        "degree": operator.degree,
        "shape": list(operator.matrix.shape),
        "entries": entries,
    }


def _acyclic_fixture(*, corrected: bool) -> FirstOrderCartanData:
    q = HomogeneousOperator(
        "Q", 1, ExactMatrix.from_rows(((0, 0), (1, 0)))
    )
    complex_ = FiniteGradedComplex((0, 1), q)
    iota = HomogeneousOperator(
        "iota_D", -1, ExactMatrix.from_rows(((0, 1), (0, 0)))
    )
    lie = HomogeneousOperator("L_D", 0, ExactMatrix.identity(2))
    zero_q1 = HomogeneousOperator("Q_1", 1, ExactMatrix.zero(2, 2))
    zero_iota = HomogeneousOperator("iota_1", -1, ExactMatrix.zero(2, 2))
    zero_lie = HomogeneousOperator("L_D_1", 0, ExactMatrix.zero(2, 2))
    return FirstOrderCartanData(
        complex_,
        iota,
        lie,
        zero_q1,
        iota if corrected else zero_iota,
        zero_lie,
    )


def _nontrivial_fixture() -> FirstOrderCartanData:
    q = HomogeneousOperator("Q", 1, ExactMatrix.zero(1, 1))
    complex_ = FiniteGradedComplex((0,), q)
    zero_iota = HomogeneousOperator("iota_D", -1, ExactMatrix.zero(1, 1))
    zero_lie = HomogeneousOperator("L_D", 0, ExactMatrix.zero(1, 1))
    lie_1 = HomogeneousOperator(
        "L_D_1", 0, ExactMatrix.from_rows(((-1,),))
    )
    return FirstOrderCartanData(
        complex=complex_,
        iota_0=zero_iota,
        lie_0=zero_lie,
        q_1=q,
        iota_1=zero_iota,
        lie_1=lie_1,
    )


def _sourced_consistency_fixture() -> FirstOrderCartanData:
    q = HomogeneousOperator(
        "Q", 1, ExactMatrix.from_rows(((0, 0, 0), (1, 0, 0), (0, 0, 0)))
    )
    complex_ = FiniteGradedComplex((0, 1, 2), q)
    iota = HomogeneousOperator(
        "iota_D",
        -1,
        ExactMatrix.from_rows(((0, 0, 0), (0, 0, 1), (0, 0, 0))),
    )
    q_1 = HomogeneousOperator(
        "Q_1",
        1,
        ExactMatrix.from_rows(((0, 0, 0), (0, 0, 0), (0, 1, 0))),
    )
    zero_lie = HomogeneousOperator("L_D", 0, ExactMatrix.zero(3, 3))
    return FirstOrderCartanData(
        complex=complex_,
        iota_0=iota,
        lie_0=zero_lie,
        q_1=q_1,
        iota_1=HomogeneousOperator("iota_1", -1, ExactMatrix.zero(3, 3)),
        lie_1=zero_lie,
    )


def _sourced_consistency_receipt() -> dict[str, Any]:
    data = _sourced_consistency_fixture()
    checks = data.checks()
    if checks["first_order_QME_linearization"]:
        raise AssertionError("sourced fixture unexpectedly has zero QME source")
    if checks["defect_consistency_Q_closed"]:
        raise AssertionError("sourced fixture unexpectedly has a closed defect")
    if not checks["sourced_consistency_identity"]:
        raise AssertionError("sourced consistency identity failed")
    return {
        "fixture_id": "nonzero_qme_source",
        "scope": "FINITE_EXACT_MECHANICS_FIXTURE_ONLY",
        "qme_source": _operator_payload(data.qme_source()),
        "ward_source": _operator_payload(data.ward_source()),
        "consistency_left": _operator_payload(data.consistency_left()),
        "consistency_right": _operator_payload(data.consistency_right()),
        "qme_source_status": "NONZERO",
        "ward_source_status": "ZERO",
        "defect_closure_status": "SOURCED_NONZERO",
        "sourced_identity": "VERIFIED",
    }


def _admissibility_receipt() -> dict[str, Any]:
    data = _acyclic_fixture(corrected=True)
    ambient = classify_closed_defect(data.complex, data.defect())
    admissible_complex = AdmissibleOperatorComplex(
        ambient=data.complex,
        constraints=(
            LinearConstraint.from_row("forbid_iota_direction", -1, (1,)),
        ),
        certified_source_degrees=(-1, 0),
    )
    admissible = classify_closed_defect(admissible_complex, data.defect())
    if ambient.status != "EXACT_REMOVABLE" or admissible.status != "NONTRIVIAL_ANOMALY":
        raise AssertionError("admissibility fixture did not expose false removability")
    if ambient.primitive is None or admissible.dual_witness is None:
        raise AssertionError("admissibility fixture is missing its exact witnesses")
    return {
        "fixture_id": "ambient_exact_primitive_inadmissible",
        "scope": "FINITE_EXACT_MECHANICS_FIXTURE_ONLY",
        "ambient_classification": ambient.status,
        "admissible_classification": admissible.status,
        "ambient_primitive": _operator_payload(ambient.primitive),
        "admissible_dual_witness": [
            _rational(value) for value in admissible.dual_witness or ()
        ],
        "admissible_complex_manifest": admissible_complex.manifest(),
    }


def _fixture_receipt(fixture_id: str, data: FirstOrderCartanData) -> dict[str, Any]:
    checks = data.checks()
    if not all(checks.values()):
        raise AssertionError(f"fixture {fixture_id} failed its consistency checks")
    defect = data.defect()
    classification = classify_closed_defect(data.complex, defect)
    receipt: dict[str, Any] = {
        "fixture_id": fixture_id,
        "scope": "FINITE_EXACT_MECHANICS_FIXTURE_ONLY",
        "basis_degrees": list(data.complex.basis_degrees),
        "checks": {name: "VERIFIED" for name in sorted(checks)},
        "defect": _operator_payload(defect),
        "classification": classification.status,
        "endomorphism_H0_dimension": data.complex.cohomology_dimension(0),
        "primitive": None,
        "dual_witness": None,
    }
    if classification.primitive is not None:
        receipt["primitive"] = _operator_payload(classification.primitive)
    if classification.dual_witness is not None:
        receipt["dual_witness"] = [
            _rational(value) for value in classification.dual_witness
        ]
    return receipt


def _source_manifest() -> dict[str, str]:
    paths = (
        "README.md",
        "__init__.py",
        "certificate.py",
        "classical_import.py",
        "defect_complex.py",
        "schema/cartan_defect_precertificate.schema.json",
        "tests/test_certificate.py",
        "tests/test_classical_import.py",
        "tests/test_defect_complex.py",
    )
    return {path: _sha256(PACKAGE_ROOT / path) for path in paths}


def _dependency_manifest() -> dict[str, str]:
    paths = {
        "commission": REPOSITORY_ROOT / "notes" / "d-quotient-quantum-team-brief.md",
        "classical_cartan_note": REPOSITORY_ROOT / "notes" / "conformal-cartan-contraction.md",
        "classical_cartan_verifier": REPOSITORY_ROOT / "symbolic" / "verify_conformal_cartan_contraction.py",
        "classical_import_certificate": QUANTUM_ROOT / "classical_import" / "certificates" / "CLASSICAL_IMPORT_CERTIFICATE.json",
        "classical_D_quotient_status": REPOSITORY_ROOT / "d_quotient_classical" / "certificates" / "CLASSICAL_D_QUOTIENT_STATUS.json",
        "afn0_production_certificate": QUANTUM_ROOT / "local_bv" / "certificates" / "AFN0_PRODUCTION_RUN_CERTIFICATE.json",
        "euler_transgression_certificate": QUANTUM_ROOT / "local_bv" / "certificates" / "EULER_TRANSGRESSION_CERTIFICATE.json",
    }
    return {name: _sha256(path) for name, path in paths.items()}


def build_certificate() -> dict[str, Any]:
    fixtures = (
        _fixture_receipt("zero_defect", _acyclic_fixture(corrected=False)),
        _fixture_receipt("exact_removable_defect", _acyclic_fixture(corrected=True)),
        _fixture_receipt("nontrivial_defect", _nontrivial_fixture()),
    )
    if tuple(item["classification"] for item in fixtures) != (
        "ZERO",
        "EXACT_REMOVABLE",
        "NONTRIVIAL_ANOMALY",
    ):
        raise AssertionError("the three exact classification fixtures did not separate")

    classical_record = load_classical_d_status()
    classical_settings = imported_setting_ledger(classical_record)
    setting_reasons = {
        "vacuum_cylinder": "no renormalized Q_1, Ward operator, or restored local QME",
        "cylinder_scalar_clock": "scalar BV and relational observable extensions are absent",
        "cylinder_yang_mills": "matter extension is outside the current execution gate",
        "weakly_deformed_background": "background-dependent causal and renormalized complexes are absent",
        "lorentzian_ds_ads": "boundary observable algebra and BRST-compatible Hadamard construction are absent",
        "asymptotically_flat": "renormalized asymptotic charge algebra is absent; contraction is not assumed",
    }
    setting_ledger = [
        {
            "setting": item["setting_id"],
            "D_charge": item["D_charge"],
            "classical_input_status": item["classical_input_status"],
            "verdict": "ANALYTIC_FRAMEWORK_MISSING",
            "reason": setting_reasons[item["setting_id"]],
        }
        for item in classical_settings
    ]

    source_manifest = _source_manifest()
    dependency_manifest = _dependency_manifest()
    return {
        "schema_version": "cartan-defect-precertificate-v1",
        "result_id": "CARTAN_DEFECT_COMPLEX_PRECERTIFICATE",
        "result_state": "ALGEBRAIC_ENGINE_READY_PHYSICAL_CANDIDATES_INPUT_BLOCKED",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "lifecycle_gates": {
            "CLASSIFIED": "NOT_REACHED_FULL_CANDIDATE_BASIS_INCOMPLETE",
            "COEFFICIENT_COMPUTED": "NOT_REACHED",
            "QME_RESTORED": "NOT_REACHED",
            "RESIDUAL_TRANSFERRED": "BLOCKED_PENDING_QME_RESTORED",
            "LORENTZIAN_CERTIFIED": "NOT_REACHED_ANALYTIC_FRAMEWORK_MISSING",
        },
        "operator_complex": {
            "defect_degree": 0,
            "differential": "delta_End(T) = [Q,T]_graded",
            "ambient_obstruction_group": "H^0(Der_adm(C), [Q,-])",
            "local_relative_realization": "PENDING_DECLARED_RENORMALIZED_OBSERVABLE_ALGEBRA_AND_COMPLETE_LOCAL_BV_BASIS",
            "first_order_defect": "A_D^(1)=[Q,iota_1]+[Q_1,iota_D]-L_D^(1)",
            "consistency_hypotheses": [
                "Q^2=0",
                "[Q,Q_1]=0",
                "[Q,iota_D]=L_D",
                "[Q,L_D^(1)]+[Q_1,L_D]=0",
            ],
            "consistency_conclusion": "[Q,A_D^(1)]=0",
            "sourced_consistency_identity": "[Q,A_D^(1)]=[[Q,Q_1],iota_D]-([Q,L_D^(1)]+[Q_1,L_D])",
            "admissible_subcomplex_policy": "classify only after locality, derivation, cyclicity, reality, parity, boundary, and Ward-preservation constraints form a verified delta_End-stable subcomplex",
            "removability_criterion": "A_D^(1)=[Q,X] for an admissible degree-minus-one finite renormalization X preserving the other declared Ward identities",
        },
        "allowed_candidate_statuses": [
            "ZERO",
            "EXACT_REMOVABLE",
            "NONTRIVIAL_ANOMALY",
            "UNDEFINED_ANALYTICALLY",
        ],
        "mechanics_fixtures": list(fixtures),
        "sourced_consistency_fixture": _sourced_consistency_receipt(),
        "admissibility_fixture": _admissibility_receipt(),
        "classical_D_import": import_receipt(),
        "candidate_sector_ledger": [
            {
                "sector": "bulk_local_pure_weyl",
                "status": "UNDEFINED_ANALYTICALLY",
                "classification_gate": "AFN0_LOWER_FORM_AND_EULER_COMPLETION_THEN_MINIMAL_BV_IMPORT",
                "missing_input": "renormalized Q_1, iota_1, and L_D^(1) on a declared observable algebra",
            },
            {
                "sector": "residual_zero_modes_and_central_terms",
                "status": "UNDEFINED_ANALYTICALLY",
                "classification_gate": "FROZEN_EQUIVARIANT_CLASSICAL_CONTRACTION_AND_RESTORED_LOCAL_QME",
                "missing_input": "renormalized residual Ward algebra and zero-mode measure",
            },
            {
                "sector": "boundary_and_corner",
                "status": "UNDEFINED_ANALYTICALLY",
                "classification_gate": "DECLARED_BFV_BOUNDARY_OBSERVABLE_AND_CHARGE_COMPLEX",
                "missing_input": "boundary conditions, charges, corner fields, and renormalized products",
            },
            {
                "sector": "measure_and_jacobian",
                "status": "UNDEFINED_ANALYTICALLY",
                "classification_gate": "ADMISSIBLE_REGULARIZATION_AND_MEASURE_DEFINITION",
                "missing_input": "regularized BV Laplacian or equivalent Slavnov-breaking construction",
            },
            {
                "sector": "conformal_scalar_clock",
                "status": "UNDEFINED_ANALYTICALLY",
                "classification_gate": "SCALAR_BV_EXTENSION_THEN_BULK_AND_RELATIONAL_WARD_CLASSIFICATION",
                "missing_input": "clock field/antifield rows, relational observable algebra, and measure",
            },
        ],
        "setting_ledger": setting_ledger,
        "input_gates": {
            "classical_freeze": "BLOCKED_UNFROZEN",
            "classical_D_charge_setting_ledger": "IMPORTED_HASH_PINNED_NOT_A_QUANTUM_PROMOTION",
            "AFN0_local_relative_basis": "IN_PROGRESS",
            "Euler_intrinsic_descent": "IN_PROGRESS",
            "minimal_BV_antifield_completion": "BLOCKED_PENDING_CLASSICAL_EXPORT",
            "renormalized_operator_algebra": "NOT_CONSTRUCTED",
            "pure_weyl_QME": "NOT_RESTORED",
            "boundary_BFV_complex": "NOT_IMPORTED",
            "scalar_clock_extension": "NOT_IMPLEMENTED",
        },
        "claim_boundary": {
            "established": [
                "the exact first-order Cartan-defect formula and its degree",
                "the sourced Jacobi/Ward consistency identity in finite exact complexes, including nonzero QME or Ward sources",
                "exact ZERO, EXACT_REMOVABLE, and NONTRIVIAL_ANOMALY classification mechanics with primitive or dual witnesses",
                "exact admissible-subcomplex classification that rejects an ambient but forbidden primitive",
                "fail-closed lifecycle, setting, and candidate-sector ledgers",
                "semantically verified and hash-pinned import of the classical compact-cylinder sector split without quantum promotion",
            ],
            "not_established": [
                "a complete pure-Weyl Cartan-obstruction candidate basis",
                "a coefficient of any physical obstruction class",
                "a restored local quantum master equation",
                "a residual quantum transfer or quantum pairing correction",
                "a scalar-clock, boundary, corner, or Lorentzian causal theorem",
            ],
        },
        "provenance": {
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
            "dependency_manifest": dependency_manifest,
            "dependency_manifest_sha256": _canonical_hash(dependency_manifest),
            "schema": str(SCHEMA_PATH.relative_to(REPOSITORY_ROOT)),
        },
        "verification_commands": [
            "PYTHONPATH=quantum-weyl python3 -m unittest discover -s quantum-weyl/cartan/tests -v",
            "PYTHONPATH=quantum-weyl python3 -m cartan.certificate --check",
            "python3 -m py_compile quantum-weyl/cartan/*.py quantum-weyl/cartan/tests/*.py",
        ],
    }


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _render(build_certificate())
    if args.emit:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != content:
            raise SystemExit(f"Cartan defect precertificate is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("CARTAN DEFECT COMPLEX: EXACT MECHANICS PASS, PHYSICAL INPUTS BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
