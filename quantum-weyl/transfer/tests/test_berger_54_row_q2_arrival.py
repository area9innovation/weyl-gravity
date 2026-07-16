from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest


TRANSFER_ROOT = Path(__file__).resolve().parents[1]
ROOT = TRANSFER_ROOT.parents[1]
MODULE_PATH = TRANSFER_ROOT / "berger_54_row_q2_arrival.py"
SPEC = importlib.util.spec_from_file_location("berger_54_row_q2_arrival_test", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
ADAPTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ADAPTER
SPEC.loader.exec_module(ADAPTER)
CERTIFICATE_PATH = TRANSFER_ROOT / "berger_54_row_q2_arrival_certificate.py"
CERTIFICATE_SPEC = importlib.util.spec_from_file_location(
    "berger_54_row_q2_arrival_certificate_test", CERTIFICATE_PATH
)
assert CERTIFICATE_SPEC is not None and CERTIFICATE_SPEC.loader is not None
CERTIFICATE = importlib.util.module_from_spec(CERTIFICATE_SPEC)
sys.modules[CERTIFICATE_SPEC.name] = CERTIFICATE
CERTIFICATE_SPEC.loader.exec_module(CERTIFICATE)


def _proof_checks() -> list[dict[str, object]]:
    relative = "quantum-weyl/transfer/schema/berger-54-row-support-local-q2-portable-v1.schema.json"
    digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
    return [
        {
            "check_id": check_id,
            "status": "VERIFIED",
            "proof_artifact": {"path": relative, "sha256": digest},
        }
        for check_id in ADAPTER.REQUIRED_PROOF_CHECKS
    ]


def _rehash(payload: dict[str, object]) -> dict[str, object]:
    q2 = payload["q2"]
    assert isinstance(q2, dict)
    entries = q2["entries"]
    assert isinstance(entries, list)
    layout = payload["row_layout"]
    assert isinstance(layout, dict)
    row_ids = layout["row_ids"]
    counts = [0] * 54
    for entry in entries:
        assert isinstance(entry, dict)
        counts[entry["output"]] += 1
    q2["row_completeness"] = [
        {"output": row_id, "status": "COMPLETE", "entry_count": counts[index]}
        for index, row_id in enumerate(row_ids)
    ]
    q2["sha256"] = ADAPTER.canonical_hash(
        {
            "shape": q2["shape"],
            "entries": entries,
            "row_completeness": q2["row_completeness"],
        }
    )
    proof_checks = payload["proof_checks"]
    payload["canonical_hashes"] = {
        "row_layout_sha256": ADAPTER.canonical_hash(layout),
        "q2_sha256": q2["sha256"],
        "proof_checks_sha256": ADAPTER.canonical_hash(proof_checks),
    }
    return payload


def nonzero_payload() -> dict[str, object]:
    unary, d_action, classical_unary = ADAPTER.load_prerequisites()
    rows = classical_unary["row_layout"]["component_rows"]
    payload: dict[str, object] = {
        "schema": ADAPTER.INPUT_SCHEMA,
        "result_id": "BERGER_54_ROW_SUPPORT_LOCAL_Q2",
        "setting_id": ADAPTER.SETTING_ID,
        "claim_status": "CERTIFIED_COMPLETE_SUPPORT_LOCAL_Q2_ARITY_TWO_IDENTITIES",
        "classical_commit": "1" * 40,
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": ADAPTER.expected_dependency_refs(unary, d_action),
        "operator_semantics": {
            "portable_name": "classical_binary_q2",
            "arity": 2,
            "degree": 1,
            "factorial_convention": ADAPTER.CONVENTION,
            "coefficient_ring": ADAPTER.COEFFICIENT_RING,
            "ordered_pbw_basis": ADAPTER.ORDERED_PBW_BASIS,
            "not_quantum_loop_operator": True,
        },
        "support_category": {
            "spacetime_dimension": 4,
            "locality": "SUPPORT_LOCAL_POLYDIFFERENTIAL",
            "invariant_frame": "berger_left_invariant_frame",
            "maximum_total_jet_order": 1,
        },
        "row_layout": {
            "total_rows": 54,
            "degree_ranks": [5, 22, 22, 5],
            "row_ids": [row["row_id"] for row in rows],
        },
        "q2": {
            "shape": [54, 54, 54],
            "entries": [
                {
                    "output": 27,
                    "left": 5,
                    "right": 5,
                    "terms": [
                        {
                            "left_exponents": [0, 0, 0, 0],
                            "right_exponents": [0, 0, 0, 0],
                            "coefficient": "alpha_B*u/2",
                        }
                    ],
                }
            ],
            "row_completeness": [],
            "sha256": "",
        },
        "proof_checks": _proof_checks(),
        "canonical_hashes": {},
        "flags": {
            "CLASSICAL_SUPPORT_LOCAL_Q2_COMPLETE_54_ROWS": True,
            "ARITY_TWO_IDENTITIES_CLASSICALLY_VERIFIED": True,
            "RESIDUAL_TRANSFER_EXECUTED": False,
            "QUANTUM_CORRECTION_INCLUDED": False,
        },
        "claim_boundary": "Implementation fixture only; no scientific q2 claim.",
    }
    return _rehash(payload)


class Berger54RowQ2ArrivalTests(unittest.TestCase):
    def test_checked_certificate_reproduces(self) -> None:
        self.assertEqual(
            json.loads(CERTIFICATE.OUTPUT.read_text()), CERTIFICATE.build_certificate()
        )

    def test_nonzero_field_field_to_equation_fixture_parses_exactly(self) -> None:
        parsed = ADAPTER.parse_portable_q2(nonzero_payload())
        self.assertEqual(len(parsed.row_ids), 54)
        self.assertEqual(parsed.term_count, 1)
        self.assertEqual(parsed.entries[0].output, 27)
        self.assertEqual(parsed.entries[0].left, 5)
        self.assertEqual(str(parsed.entries[0].terms[0].coefficient), "alpha_B*u/2")

    def test_setting_and_dependency_mutations_fail_closed(self) -> None:
        payload = nonzero_payload()
        payload["setting_id"] = "complexified_flat_pure_weyl_to_einstein_three_point"
        with self.assertRaisesRegex(ValueError, "identity or setting"):
            ADAPTER.parse_portable_q2(payload)

        payload = nonzero_payload()
        refs = payload["dependency_refs"]
        assert isinstance(refs, dict)
        hashes = refs["operator_hashes"]
        assert isinstance(hashes, dict)
        hashes["q1_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "dependency binding"):
            ADAPTER.parse_portable_q2(payload)

    def test_record_hash_and_completeness_mutations_fail_closed(self) -> None:
        payload = nonzero_payload()
        q2 = payload["q2"]
        assert isinstance(q2, dict)
        q2["entries"] = []
        _rehash(payload)
        with self.assertRaisesRegex(ValueError, "shape drifted"):
            ADAPTER.parse_portable_q2(payload)

        payload = nonzero_payload()
        q2 = payload["q2"]
        assert isinstance(q2, dict)
        q2["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "record hash"):
            ADAPTER.parse_portable_q2(payload)

        payload = nonzero_payload()
        q2 = payload["q2"]
        assert isinstance(q2, dict)
        completeness = q2["row_completeness"]
        assert isinstance(completeness, list)
        completeness[27]["entry_count"] = 0
        q2["sha256"] = ADAPTER.canonical_hash(
            {
                "shape": q2["shape"],
                "entries": q2["entries"],
                "row_completeness": completeness,
            }
        )
        hashes = payload["canonical_hashes"]
        assert isinstance(hashes, dict)
        hashes["q2_sha256"] = q2["sha256"]
        with self.assertRaisesRegex(ValueError, "row-completeness"):
            ADAPTER.parse_portable_q2(payload)

        payload = nonzero_payload()
        q2 = payload["q2"]
        assert isinstance(q2, dict)
        q2["entries"].append(deepcopy(q2["entries"][0]))
        _rehash(payload)
        with self.assertRaisesRegex(ValueError, "noncanonical"):
            ADAPTER.parse_portable_q2(payload)

    def test_degree_and_Koszul_symmetry_mutations_fail_closed(self) -> None:
        payload = nonzero_payload()
        q2 = payload["q2"]
        assert isinstance(q2, dict)
        q2["entries"][0]["output"] = 5
        _rehash(payload)
        with self.assertRaisesRegex(ValueError, "degree one"):
            ADAPTER.parse_portable_q2(payload)

        payload = nonzero_payload()
        q2 = payload["q2"]
        assert isinstance(q2, dict)
        q2["entries"][0]["right"] = 6
        _rehash(payload)
        with self.assertRaisesRegex(ValueError, "Koszul symmetry"):
            ADAPTER.parse_portable_q2(payload)

    def test_coefficient_jet_and_proof_mutations_fail_closed(self) -> None:
        payload = nonzero_payload()
        q2 = payload["q2"]
        assert isinstance(q2, dict)
        q2["entries"][0]["terms"][0]["coefficient"] = "forbidden_symbol"
        _rehash(payload)
        with self.assertRaisesRegex(ValueError, "undeclared"):
            ADAPTER.parse_portable_q2(payload)

        payload = nonzero_payload()
        q2 = payload["q2"]
        assert isinstance(q2, dict)
        q2["entries"][0]["terms"][0]["left_exponents"] = [2, 0, 0, 0]
        _rehash(payload)
        with self.assertRaisesRegex(ValueError, "total jet order"):
            ADAPTER.parse_portable_q2(payload)

        payload = nonzero_payload()
        checks = payload["proof_checks"]
        assert isinstance(checks, list)
        checks[0]["proof_artifact"]["sha256"] = "0" * 64
        _rehash(payload)
        with self.assertRaisesRegex(ValueError, "proof artifact hash"):
            ADAPTER.parse_portable_q2(payload)

    def test_readiness_certificate_remains_input_blocked(self) -> None:
        result = ADAPTER.build_readiness_payload()
        self.assertEqual(result["input_gate"]["status"], "INPUT_BLOCKED")
        self.assertFalse(result["input_gate"]["classical_q2_export_available"])
        self.assertFalse(
            result["consumer_capabilities"]["independent_q1_q2_identity_execution"]
        )
        self.assertFalse(result["claim_flags"]["INTERACTING_CARTAN_VERDICT"])


if __name__ == "__main__":
    unittest.main()
