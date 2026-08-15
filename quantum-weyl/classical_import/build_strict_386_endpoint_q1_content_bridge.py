#!/usr/bin/env python3
"""Build the exact Gate-V5 to strict-386 endpoint q1 content bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from strict_386_endpoint_q1_content_bridge import (
    build_exhaustive_witness,
    compare,
    decode_matrix,
    digest,
    rank,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.json"
WITNESS = HERE / "certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_WITNESS_V1.json"
REPORT = HERE / "REPORT_STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.md"
Q1 = HERE / "certificates/STRICT_PORTABLE_LOCAL_Q1_AST_V1.json"
CYCLIC = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
GATE = HERE / "certificates/CLASSICAL_IMPORT_GATE_V5_RECONCILIATION.json"
TRANSPORT = HERE / "certificates/STRICT_386_CAUSAL_SIGN_TRANSPORT_V1.json"
UNIVERSAL = HERE / "certificates/STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1.json"
ENDPOINT = ROOT / "covariant_completion/certificates/curved_prolonged_metric_endpoint_complex.json"
ENDPOINT_PAYLOAD = ROOT / "covariant_completion/certificates/curved_prolonged_metric_endpoint_coefficients.json"
CAUSAL = ROOT / "covariant_completion/certificates/curved_full_prolonged_green_homotopy_assembly.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def source_id(value: Mapping[str, Any]) -> str | None:
    return value.get("result_id") or value.get("schema")


INPUTS = (
    (Q1, "STRICT_PORTABLE_LOCAL_Q1_AST_V1", "portable strict minimal q1 AST"),
    (CYCLIC, "STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1", "canonical minimal pairing and antifield sign translation"),
    (GATE, "CLASSICAL_IMPORT_GATE_V5_RECONCILIATION", "current fail-closed Gate-A disposition"),
    (TRANSPORT, "STRICT_386_CAUSAL_SIGN_TRANSPORT_V1", "causal convention-stability predecessor"),
    (UNIVERSAL, "STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1", "independent 700-column coordinate-jet Bach table"),
    (ENDPOINT, "pure-weyl-prolonged-metric-endpoint-complex-v1", "exact thirty-row covariant endpoint"),
    (ENDPOINT_PAYLOAD, "pure-weyl-prolonged-metric-endpoint-coefficients-v1", "endpoint q1 and pairing coefficient bytes"),
    (CAUSAL, "pure-weyl-full-prolonged-green-homotopy-assembly-v1", "strict 386-row causal Green homotopy"),
)


def build() -> dict[str, Any]:
    values = {path: load(path) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        if source_id(values[path]) != expected:
            raise ValueError(f"dependency identity drift: {path}")
    if not WITNESS.is_file():
        raise FileNotFoundError(
            f"missing {WITNESS}; run with --exhaustive-witness"
        )
    witness = load(WITNESS)
    q1 = values[Q1]
    cyclic = values[CYCLIC]
    gate = values[GATE]
    transport = values[TRANSPORT]
    universal = values[UNIVERSAL]["universal_table"]
    endpoint = values[ENDPOINT]
    endpoint_payload = values[ENDPOINT_PAYLOAD]
    causal = values[CAUSAL]
    if gate["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate A unexpectedly passed")
    if not cyclic["claim_flags"]["CANONICAL_SIGN_TRANSLATION_CERTIFIED"]:
        raise ValueError("canonical sign translation missing")
    if endpoint["dimension"] != 30 or endpoint_payload["schema"] != "pure-weyl-prolonged-metric-endpoint-coefficients-v1":
        raise ValueError("endpoint content drift")
    if causal["dimension_ledger"] != {
        "algebraically_contracted": 356,
        "causal_endpoint": 30,
        "identity": "386=356+30",
        "prolonged": 386,
    } or not causal["causal_green_homotopy"]:
        raise ValueError("causal endpoint provenance drift")
    if not transport["architecture_disposition"]["strict_386_route_convention_stable"]:
        raise ValueError("causal sign transport unavailable")

    errors, comparison = compare(
        q1=q1,
        universal=universal,
        witness=witness,
        endpoint_payload=endpoint_payload,
    )
    if errors:
        raise ValueError("endpoint bridge failed: " + "; ".join(errors))
    counts = comparison["counts"]
    pairing = comparison["pairing"]
    maps = comparison["maps"]
    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-endpoint-q1-content-bridge-v1",
        "result_id": "STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1",
        "result_kind": "SCOPED_SAME_THEORY_ENDPOINT_OPERATOR_CONTENT_BRIDGE",
        "result_state": "UNIT_CYLINDER_ENDPOINT_Q1_CONTENT_IDENTIFIED_CAUSAL_PAIRING_SIGN_AND_FULL_CARRIER_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "764cb8c9",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Do the canonically translated Gate-V5 minimal q1 rows equal the actual thirty-row endpoint operator used by the strict 386-row causal architecture?",
        "answer": "Yes on the unit conformal cylinder, after an explicit exact change from Gate component coordinates to the endpoint DeWitt/ghost coordinates and the certified sign flip on the endpoint identity block. All five gauge-arrow tables, all 700 Bach input columns, and all five Noether-arrow tables agree coefficientwise, producing one common q1 digest. This resolves the earlier type-only bridge for the minimal unary operator. It does not yet identify a common full causal BV datum: when the causal pairing is transported simultaneously with the identity-block sign, its ghost/identity pullback is the negative of the Gate-canonical block. The full 386-row pairing, 356-row complement, q2/D compatibility, Gate A, Hadamard and QME therefore remain open.",
        "scope": {
            "theory": "strict pure-Weyl minimal unary BV complex",
            "background": "unit conformal cylinder",
            "gate_carrier_dimension": 30,
            "causal_endpoint_dimension": 30,
            "causal_full_dimension": 386,
            "coefficient_field": "Q",
            "maximum_q1_order": 4,
            "normal_form": "symmetrized covariant derivatives at a homogeneous orthonormal cylinder frame",
            "globality": "The endpoint coefficients are parallel natural tensors on the homogeneous cylinder; the Gate coordinate table is converted through the exact triangular coordinate-to-covariant four-jet map at the same frame.",
        },
        "ordered_gate_basis": {
            "G": ["c^0", "c^1", "c^2", "c^3", "omega"],
            "M": [f"h_{left}{right}" for left, right in ((0,0),(0,1),(0,2),(0,3),(1,1),(1,2),(1,3),(2,2),(2,3),(3,3))],
            "E": [f"h_star^{left}{right}" for left, right in ((0,0),(0,1),(0,2),(0,3),(1,1),(1,2),(1,3),(2,2),(2,3),(3,3))],
            "I": ["c_star_0", "c_star_1", "c_star_2", "c_star_3", "omega_star"],
        },
        "basis_bridge": {
            "formulae": {
                "A_G": "(xi_0,xi_1,xi_2,xi_3,sigma)=(-c^0,c^1,c^2,c^3,2 omega)",
                "A_M": "h_endpoint=h_gate",
                "A_E": "Ebar_endpoint=J_met^-1 W_component h_star_gate",
                "A_I": "I_endpoint=(A_G^T Y_met)^-1 I_gate",
                "endpoint_q_transport": "C_met is replaced by -C_met, the I-block of T_386 Q T_386",
            },
            "matrices": maps,
            "ranks": {
                key: rank(decode_matrix(matrix))
                for key, matrix in maps.items()
            },
            "witness_path": str(WITNESS.relative_to(ROOT)),
            "witness_sha256": sha(WITNESS),
            "witness_columns": counts["witness_columns"],
            "witness_coordinate_entries": counts["witness_coordinate_entries"],
            "triangular_equations": witness["exhaustive_checks"]["triangular_equations"],
        },
        "coefficientwise_identification": {
            "arrow_table_counts": {"G_to_M": 5, "M_to_E": 70, "E_to_I": 5, "total": counts["arrow_multiindex_tables"]},
            "gate_bach_input_columns": 700,
            "gate_bach_columns_matching": 700,
            "arrow_defect_counts": comparison["arrow_defects"],
            "common_nonzero_coefficients": counts["common_nonzero_coefficients"],
            "endpoint_coordinate_nonzero_coefficients": counts["endpoint_nonzero_coefficients"],
            "gate_arrow_sha256": comparison["gate_arrow_sha256"],
            "endpoint_in_gate_coordinates_sha256": comparison["endpoint_in_gate_coordinates_sha256"],
            "common_q1_sha256": comparison["common_q1_sha256"],
            "same_operator_content_identified": True,
        },
        "pairing_disposition": {
            **pairing,
            "field_block": "J_met A_E=W_component exactly",
            "ghost_block_before_simultaneous_causal_pairing_transport": "A_G^T Y_met A_I=I_5",
            "ghost_block_after_simultaneous_causal_pairing_transport": "A_G^T (-Y_met) A_I=-I_5",
            "conclusion": "The q1 content bridge and the causal paired-transport theorem cannot yet be collapsed into one common canonical BV-pairing certificate. A suspension/pairing convention must be selected and the graded-adjoint Green theorem replayed on those same bytes.",
        },
        "foundational_strength": {
            "finite_content_bridge_base": "PRA",
            "reason": "The bridge is a fixed finite calculation over exact rational matrices and a 700-column triangular jet table.",
            "choice_operation_added": False,
            "infinite_selection_added": False,
            "weakest_base_for_imported_analytic_causal_theorem": "NOT_ESTABLISHED",
        },
        "gate_disposition": {
            "gate_a_status": "FAIL_CLOSED",
            "accepted_common_snapshot_hashes": gate["gate_disposition"]["accepted_common_snapshot_hashes"],
            "scoped_common_minimal_q1_digest_established": True,
            "full_common_carrier_established": False,
            "full_common_pairing_established": False,
            "q2_d_same_carrier_established": False,
        },
        "claim_flags": {
            "UNIT_CYLINDER_30_ROW_ENDPOINT_Q1_COMMON_CONTENT_IDENTIFIED": True,
            "ALL_700_BACH_COLUMNS_MATCH": True,
            "TRANSPORTED_ENDPOINT_Q1_MATCHES_GATE_CANONICAL_Q1": True,
            "STRICT_386_CAUSAL_ENDPOINT_OPERATOR_LINKED": True,
            "SIMULTANEOUSLY_TRANSPORTED_CAUSAL_PAIRING_EQUALS_GATE_CANONICAL": False,
            "FULL_386_PAIRING_SERIALIZED_IN_GATE_CONVENTION": False,
            "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "does_not_establish": [
            "a common Gate-canonical pairing on all 386 causal rows",
            "a resolution of the ghost/identity sign between simultaneous causal pairing transport and the Gate suspension convention",
            "cyclic compatibility of the 356-row algebraic/nonminimal/auxiliary complement",
            "q2 or local D on the same causal carrier",
            "a passed classical import Gate A or a complete common snapshot",
            "a Hadamard state, BRST Ward identity, positivity theorem, renormalized Lorentzian product, QME, residual transfer or Lorentzian quantum theory",
            "a weakest-base calibration of the imported analytic Green theorem",
        ],
        "next_gate": "Choose and serialize one Gate-canonical suspension/pairing convention on the exact 386-row carrier, extend it across the 356-row complement, and independently replay the full Green graded-adjoint identity on those same bytes. Only then bind q2 and local D to the carrier and test nonlinear compatibility.",
        "canonical_hashes": {},
        "provenance": {
            "inputs": [
                {
                    "path": str(path.relative_to(ROOT)),
                    "result_or_schema_id": expected,
                    "sha256": sha(path),
                    "role": role,
                }
                for path, expected, role in INPUTS
            ]
            + [
                {
                    "path": str(WITNESS.relative_to(ROOT)),
                    "result_or_schema_id": witness["schema"],
                    "sha256": sha(WITNESS),
                    "role": "exact 700-column coordinate-to-covariant proof witness",
                }
            ]
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_endpoint_q1_content_bridge.py",
            "checks": [
                "witness identity, exact rationality and triangular normalization",
                "five gauge-arrow coefficient tables",
                "all 700 Bach input columns",
                "five canonically translated Noether-arrow coefficient tables",
                "common q1 digest",
                "pairing sign firewall",
                "provenance hashes and canonical digest",
            ],
            "expected_digest": "",
        },
        "human_report": str(REPORT.relative_to(ROOT)),
    }
    value["canonical_hashes"] = {
        "basis_bridge_sha256": digest(value["basis_bridge"]),
        "coefficientwise_identification_sha256": digest(value["coefficientwise_identification"]),
        "pairing_disposition_sha256": digest(value["pairing_disposition"]),
    }
    value["independent_checker"]["expected_digest"] = digest(
        {
            key: value[key]
            for key in (
                "scope", "ordered_gate_basis", "basis_bridge",
                "coefficientwise_identification", "pairing_disposition",
                "foundational_strength", "gate_disposition", "claim_flags",
                "does_not_establish", "next_gate", "canonical_hashes",
            )
        }
    )
    return value


def render(value: Mapping[str, Any]) -> str:
    content = value["coefficientwise_identification"]
    pairing = value["pairing_disposition"]
    return f"""# Strict 386-row endpoint q1 content bridge v1

## Outcome

{value['answer']}

## Exact operator comparison

- Gauge arrow: **5/5** covariant coefficient tables match.
- Bach arrow: **{content['gate_bach_columns_matching']}/{content['gate_bach_input_columns']}** exact metric four-jet columns match.
- Noether arrow: **5/5** coefficient tables match after the certified endpoint identity-block sign transport.
- Total: **{content['arrow_table_counts']['total']}/80** unary multiindex tables match.
- All arrow defect counts are zero: `{content['arrow_defect_counts']}`.
- The common Gate-coordinate q1 digest is `{content['common_q1_sha256']}`.

The basis map is not a label-only permutation.  It lowers the Diff ghost with
the Lorentz metric, sends the endpoint Weyl scalar to `sigma=2 omega`, and
uses `Ebar=J_met^-1 W_component h_star` on the equation row.  The Bach
comparison composes the independent 700-input coordinate-jet table with an
exact 490,000-equation triangular coordinate-to-covariant witness.

## Pairing boundary

The field/equation block pulls back exactly to the Gate canonical component
pairing, and the original endpoint ghost/identity block does too.  But the
causal convention-stability theorem transports the pairing simultaneously
with the identity-block sign.  Its pullback is then `-I_5`, not `I_5`:

- original endpoint ghost pullback canonical: `{pairing['original_endpoint_ghost_pullback_equals_gate_canonical']}`;
- simultaneously transported causal ghost pullback canonical: `{pairing['simultaneously_transported_causal_ghost_pullback_equals_gate_canonical']}`;
- simultaneously transported pullback equals negative canonical: `{pairing['simultaneously_transported_causal_ghost_pullback_equals_negative_gate_canonical']}`.

Thus the minimal unary operator bytes are identified, while one common
Gate-canonical full causal pairing and its graded-adjoint Green replay remain
open.

## Foundational strength

The finite bridge is a fixed rational calculation formalizable in PRA and
adds neither Choice nor an infinite selection.  This does not calibrate the
analytic theorem imported by the causal Green certificate.

## Does not establish

""" + "\n".join(f"- {item}" for item in value["does_not_establish"]) + f"""

## Next gate

{value['next_gate']}
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (
        (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(),
        render(value).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--exhaustive-witness", action="store_true")
    args = parser.parse_args()
    if args.exhaustive_witness:
        universal = load(UNIVERSAL)["universal_table"]
        witness = build_exhaustive_witness(universal)
        WITNESS.write_text(json.dumps(witness, indent=2) + "\n")
    result, report = generated()
    if args.check:
        errors = []
        if not RESULT.is_file() or RESULT.read_bytes() != result:
            errors.append(str(RESULT.relative_to(ROOT)))
        if not REPORT.is_file() or REPORT.read_bytes() != report:
            errors.append(str(REPORT.relative_to(ROOT)))
        if errors:
            print("STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1: stale " + ", ".join(errors))
            return 1
        print("STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1: generated artifacts current")
        return 0
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print(f"wrote {RESULT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
