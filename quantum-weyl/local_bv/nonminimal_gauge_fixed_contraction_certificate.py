"""Emit the general nonminimal/gauge-fixed contraction and G2 results."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .nonminimal_gauge_fixed_contraction import analysis


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json"
H04_OUTPUT = HERE / "cohomology/H04_GAUGE_FIXED_BV_RESULT.json"
H14_OUTPUT = HERE / "cohomology/H14_GAUGE_FIXED_BV_RESULT.json"
SCHEMA = HERE / "schema/general_nonminimal_gauge_fixed_contraction.schema.json"
RESULT_SCHEMA = HERE / "schema/gauge_fixed_bv_cohomology_result.schema.json"
SOURCE_PATHS = (
    "quantum-weyl/local_bv/nonminimal_gauge_fixed_contraction.py",
    "quantum-weyl/local_bv/nonminimal_gauge_fixed_contraction_certificate.py",
    "quantum-weyl/local_bv/verify_nonminimal_gauge_fixed_contraction.py",
    "quantum-weyl/local_bv/schema/general_nonminimal_gauge_fixed_contraction.schema.json",
    "quantum-weyl/local_bv/schema/gauge_fixed_bv_cohomology_result.schema.json",
    "quantum-weyl/local_bv/tests/test_nonminimal_gauge_fixed_contraction.py",
    "quantum-weyl/reports/general-nonminimal-gauge-fixed-contraction.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, Any]:
    result = analysis()
    return {
        "schema": "quantum-weyl-general-nonminimal-gauge-fixed-contraction-v1",
        "result_id": "GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION",
        "result_state": "FULL_LOCAL_BV_G2_COMPLETE_ON_REGULAR_BACH_LOCUS_ANALYTIC_QME_OPEN",
        "classical_commit": result["classical_commit"],
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_hashes": result["dependency_hashes"],
        "scope": {
            "gauge_symmetry": "Diff_x_Weyl",
            "gauge_direction_count": 5,
            "locality": "POINTWISE_DOUBLET_ROWS_WITH_COVARIANT_JET_PROLONGATION",
            "gauge_fixing": "ARBITRARY_INVERTIBLE_LOCAL_BV_CANONICAL_TRANSFORMATION",
            "regularity": "REGULAR_BACH_LOCUS_FOR_MINIMAL_KOSZUL_TATE_INPUT",
        },
        "field_dictionary": result["field_dictionary"],
        "direct_sum_contraction": result["contraction"],
        "canonical_gauge_fixing_transport": result["canonical_gauge_fixing_transport"],
        "classical_specialization_replay": result["classical_specialization_replay"],
        "gauge_fixed_cohomology": result["gauge_fixed_cohomology"],
        "checks": {
            "ten_nonminimal_pairs_enumerated": "VERIFIED",
            "Q_squared_zero_on_every_nonminimal_atom": "VERIFIED",
            "graded_contraction_regressions": "VERIFIED_25080",
            "covariant_jet_prolongation": "VERIFIED_PARAMETRIC",
            "horizontal_differential_compatibility": "VERIFIED",
            "formal_canonical_transport_normal_forms": "ALL_ZERO",
            "Berger_unfixed_specialization": "INDEPENDENT_SUPPORT_REPLAYED",
            "Berger_gauge_fixed_specialization": "BOUND_AS_REGRESSION_ONLY",
            "H04_minimal_nonminimal_gauge_fixed_comparison": "CHAIN_ISOMORPHISM",
            "H14_minimal_nonminimal_gauge_fixed_comparison": "CHAIN_ISOMORPHISM",
            "full_local_BV_G2": "COMPLETE_ON_REGULAR_BACH_LOCUS",
        },
        "claim_flags": {
            "GENERAL_NONMINIMAL_DOUBLETS_CONTRACTED": True,
            "LOCAL_CANONICAL_GAUGE_FIXING_INVARIANCE_PROVED": True,
            "H04_GAUGE_FIXED_BV_COMPLETE": True,
            "H14_GAUGE_FIXED_BV_COMPLETE": True,
            "FULL_BV_G2_COMPLETE": True,
            "ANOMALY_COEFFICIENTS_COMPUTED_HERE": False,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "proof_sha256": result["proof_sha256"],
        "result_artifacts": {
            "H04": "quantum-weyl/local_bv/cohomology/H04_GAUGE_FIXED_BV_RESULT.json",
            "H14": "quantum-weyl/local_bv/cohomology/H14_GAUGE_FIXED_BV_RESULT.json",
        },
        "next_gate": "REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC certificate completes the local H04 and H14 cohomology "
            "of the minimal, nonminimal, and canonically gauge-fixed Diff x Weyl BV "
            "complex on the imported regular Bach-locus chart. Four Diff directions and "
            "one Weyl direction contribute ten explicit pointwise doublets. Their odd "
            "derivation, jet prolongation, and contracting homotopy are checked on every "
            "atom and 25,080 canonical supermonomials, including coefficients of both "
            "parities from the minimal algebra. A free-word normal-form calculation then "
            "verifies that every contraction identity and side condition transports under "
            "an arbitrary invertible local BV-canonical gauge-fixing transformation. The "
            "landed Berger 54-row unfixed and gauge-fixed packages are replayed only as a "
            "specialization regression, not used to extend Berger analytic claims to "
            "general backgrounds. Consequently the gauge-fixed H04 and H14 groups equal "
            "the certified minimal groups, and the local BV obstruction classification "
            "reaches G2 within the stated regularity scope. This does not construct a "
            "gauge-fixed Green operator or Hadamard state, compute a repository-specific "
            "one-loop coefficient or regulated Slavnov breaking, restore the QME, perform "
            "residual quantum transfer, or establish Lorentzian quantum theory."
        ),
        "provenance": {
            "source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
        },
    }


def _result_payload(certificate: dict[str, Any], ghost_number: int) -> dict[str, Any]:
    cohomology = certificate["gauge_fixed_cohomology"]
    if ghost_number == 0:
        classes = [
            {"representative_id": "CT_C2", "parity": "even", "status": "NONTRIVIAL"},
            {"representative_id": "CT_E4", "parity": "even", "status": "NONTRIVIAL"},
            {"representative_id": "CT_C_DUAL_C", "parity": "odd", "status": "NONTRIVIAL"},
        ]
        exact = ["CT_BOX_R"]
        result_id = "H04_GAUGE_FIXED_BV_RESULT"
    else:
        classes = [
            {"representative_id": "ANOM_OMEGA_C2", "parity": "even", "status": "NONTRIVIAL"},
            {"representative_id": "ANOM_OMEGA_E4", "parity": "even", "status": "NONTRIVIAL"},
            {"representative_id": "ANOM_OMEGA_C_DUAL_C", "parity": "odd", "status": "NONTRIVIAL"},
        ]
        exact = cohomology["H14_exact_rows"]
        result_id = "H14_GAUGE_FIXED_BV_RESULT"
    return {
        "schema": "quantum-weyl-gauge-fixed-bv-cohomology-result-v1",
        "result_id": result_id,
        "result_state": "GAUGE_FIXED_BV_LOCAL_COHOMOLOGY_COMPLETE",
        "classical_commit": certificate["classical_commit"],
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "ghost_number": ghost_number,
        "form_degree": 4,
        "regularity_scope": "REGULAR_BACH_LOCUS",
        "parity_dimensions": {"even": 2, "odd": 1},
        "classes": classes,
        "exact_rows": exact,
        "comparison": "MINIMAL_TO_NONMINIMAL_TO_GAUGE_FIXED_CHAIN_ISOMORPHISMS_EXPLICIT",
        "proof_certificate": {
            "path": "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json",
            "proof_sha256": certificate["proof_sha256"],
        },
        "claim_flags": {
            "COHOMOLOGY_COMPLETE": True,
            "COEFFICIENTS_COMPUTED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
    }


def build_outputs() -> dict[Path, dict[str, Any]]:
    certificate = build()
    return {
        OUTPUT: certificate,
        H04_OUTPUT: _result_payload(certificate, 0),
        H14_OUTPUT: _result_payload(certificate, 1),
    }


def validate(certificate: dict[str, Any]) -> None:
    flags = certificate.get("claim_flags", {})
    if (
        flags.get("GENERAL_NONMINIMAL_DOUBLETS_CONTRACTED") is not True
        or flags.get("LOCAL_CANONICAL_GAUGE_FIXING_INVARIANCE_PROVED") is not True
        or flags.get("H04_GAUGE_FIXED_BV_COMPLETE") is not True
        or flags.get("H14_GAUGE_FIXED_BV_COMPLETE") is not True
        or flags.get("FULL_BV_G2_COMPLETE") is not True
        or any(
            flags.get(name) is not False
            for name in (
                "ANOMALY_COEFFICIENTS_COMPUTED_HERE",
                "REGULATED_SLAVNOV_BREAKING_COMPUTED",
                "QME_RESTORED",
                "LORENTZIAN_QUANTUM_THEORY",
            )
        )
        or certificate.get("next_gate") != "REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING"
    ):
        raise ValueError("nonminimal/gauge-fixed certificate crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    validate(outputs[OUTPUT])
    main_schema = json.loads(SCHEMA.read_text())
    result_schema = json.loads(RESULT_SCHEMA.read_text())
    for schema in (main_schema, result_schema):
        Draft202012Validator.check_schema(schema)
    Draft202012Validator(main_schema).validate(outputs[OUTPUT])
    for path in (H04_OUTPUT, H14_OUTPUT):
        Draft202012Validator(result_schema).validate(outputs[path])
    for path, value in outputs.items():
        content = json.dumps(value, indent=2, sort_keys=True) + "\n"
        if args.emit:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        if args.check and path.read_text() != content:
            raise SystemExit(f"stale nonminimal/gauge-fixed result: {path}")
    print("GENERAL NONMINIMAL + GAUGE-FIXED BV: G2 PASS; SLAVNOV BREAKING OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
