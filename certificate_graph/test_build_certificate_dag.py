from __future__ import annotations

from dataclasses import replace
import unittest

from certificate_graph.build_certificate_dag import (
    Certificate,
    Edge,
    _cycles,
    _layout_topic,
    derive_edges,
)


def certificate(path: str, result_id: str, payload: dict) -> Certificate:
    return Certificate(
        key="cert:" + result_id,
        path=path,
        result_id=result_id,
        label=result_id,
        family="test",
        status="CERTIFIED",
        color_state="certified",
        dependency_tags=(),
        payload={"result_id": result_id, **payload},
    )


class CertificateDagTests(unittest.TestCase):
    def test_path_dependency_points_from_input_to_consumer(self) -> None:
        upstream = certificate("certificates/up.json", "UP", {})
        downstream = certificate(
            "certificates/down.json",
            "DOWN",
            {"dependency_refs": {"upstream": "certificates/up.json"}},
        )
        files = {
            upstream.path: b'{"result_id":"UP"}',
            downstream.path: b'{"result_id":"DOWN"}',
        }
        edges, issues = derive_edges([upstream, downstream], files)
        self.assertTrue(
            any(edge.source == upstream.key and edge.target == downstream.key for edge in edges)
        )
        self.assertEqual(issues["hash_mismatches"], [])

    def test_result_id_import_is_typed(self) -> None:
        upstream = certificate("certificates/up.json", "UP", {})
        downstream = certificate(
            "certificates/down.json",
            "DOWN",
            {"imported_result_id": "UP"},
        )
        files = {
            upstream.path: b'{"result_id":"UP"}',
            downstream.path: b'{"result_id":"DOWN"}',
        }
        edges, _ = derive_edges([upstream, downstream], files)
        self.assertIn(Edge(upstream.key, downstream.key, "IMPORTS", "imported_result_id"), edges)

    def test_cycle_detection(self) -> None:
        edges = [
            Edge("a", "b", "DEPENDS_ON", "x"),
            Edge("b", "a", "DEPENDS_ON", "y"),
        ]
        self.assertEqual(_cycles(["a", "b"], edges), [["a", "b"]])
        self.assertEqual(_cycles(["a", "b"], edges[:1]), [])

    def test_mutual_audit_is_not_an_ordering_edge(self) -> None:
        manifest = certificate(
            "certificates/SOURCE_MANIFEST.json",
            "MANIFEST",
            {},
        )
        receipt = certificate(
            "certificates/VERIFICATION_RECEIPT.json",
            "RECEIPT",
            {"source_manifest": "certificates/SOURCE_MANIFEST.json"},
        )
        files = {
            manifest.path: b'{"result_id":"MANIFEST"}',
            receipt.path: b'{"result_id":"RECEIPT"}',
        }
        edges, issues = derive_edges([manifest, receipt], files)
        self.assertEqual(edges, [])
        self.assertEqual(
            issues["nonordering_provenance_cross_links"][0]["relation"],
            "MUTUALLY_AUDITS",
        )

    def test_named_verification_receipt_is_nonordering(self) -> None:
        theorem = certificate(
            "certificates/THEOREM.json",
            "THEOREM",
            {
                "publication": {
                    "verification_receipt_path": (
                        "certificates/THEOREM_VERIFICATION_RECEIPT.json"
                    )
                }
            },
        )
        receipt = certificate(
            "certificates/THEOREM_VERIFICATION_RECEIPT.json",
            "THEOREM_VERIFICATION_RECEIPT",
            {"certificate_path": "certificates/THEOREM.json"},
        )
        files = {
            theorem.path: b'{"result_id":"THEOREM"}',
            receipt.path: b'{"result_id":"THEOREM_VERIFICATION_RECEIPT"}',
        }
        edges, issues = derive_edges([theorem, receipt], files)
        self.assertEqual(edges, [])
        self.assertEqual(len(issues["nonordering_provenance_cross_links"]), 2)

    def test_claim_table_and_signoff_are_nonordering(self) -> None:
        claim_table = certificate(
            "certificates/PAPER_CLAIM_TABLE.json",
            "PAPER_CLAIM_TABLE",
            {
                "signoff_evidence": [
                    {
                        "certificate_path": "certificates/PAPER_TEAM_SIGNOFF.json",
                        "certificate_result_id": "PAPER_TEAM_SIGNOFF",
                    }
                ]
            },
        )
        signoff = certificate(
            "certificates/PAPER_TEAM_SIGNOFF.json",
            "PAPER_TEAM_SIGNOFF",
            {
                "source_manifest": {
                    "claim_table": {
                        "path": "certificates/PAPER_CLAIM_TABLE.json",
                        "result_id": "PAPER_CLAIM_TABLE",
                    }
                }
            },
        )
        files = {
            claim_table.path: b'{"result_id":"PAPER_CLAIM_TABLE"}',
            signoff.path: b'{"result_id":"PAPER_TEAM_SIGNOFF"}',
        }
        edges, issues = derive_edges([claim_table, signoff], files)
        self.assertEqual(edges, [])
        self.assertEqual(len(issues["nonordering_provenance_cross_links"]), 4)

    def test_preflight_and_readiness_coordination_is_nonordering(self) -> None:
        preflight = certificate(
            "certificates/RELATIVE_FUNCTOR_PREFLIGHT.json",
            "RELATIVE_FUNCTOR_PREFLIGHT",
            {
                "dependency_refs": {
                    "quantum_readiness": "certificates/QUANTUM_READINESS.json"
                }
            },
        )
        readiness = certificate(
            "certificates/QUANTUM_READINESS.json",
            "QUANTUM_READINESS",
            {
                "dependency_refs": {
                    "relative_preflight": "certificates/RELATIVE_FUNCTOR_PREFLIGHT.json"
                }
            },
        )
        files = {
            preflight.path: b'{"result_id":"RELATIVE_FUNCTOR_PREFLIGHT"}',
            readiness.path: b'{"result_id":"QUANTUM_READINESS"}',
        }
        edges, issues = derive_edges([preflight, readiness], files)
        self.assertEqual(edges, [])
        self.assertTrue(
            all(
                item["relation"] == "COORDINATES_READINESS"
                for item in issues["nonordering_provenance_cross_links"]
            )
        )

    def test_theorem_consumer_registration_is_nonordering(self) -> None:
        theorem = certificate(
            "certificates/ABSTRACT_THEOREM.json",
            "ABSTRACT_THEOREM",
            {
                "consumer_contract": {
                    "adapter_path": "certificates/CONCRETE_CONSUMER.json"
                }
            },
        )
        consumer = certificate(
            "certificates/CONCRETE_CONSUMER.json",
            "CONCRETE_CONSUMER",
            {
                "dependency_refs": {
                    "abstract_theorem": "certificates/ABSTRACT_THEOREM.json"
                }
            },
        )
        files = {
            theorem.path: b'{"result_id":"ABSTRACT_THEOREM"}',
            consumer.path: b'{"result_id":"CONCRETE_CONSUMER"}',
        }
        edges, issues = derive_edges([theorem, consumer], files)
        self.assertEqual(
            edges,
            [
                Edge(
                    theorem.key,
                    consumer.key,
                    "DEPENDS_ON",
                    "dependency_refs.abstract_theorem",
                )
            ],
        )
        self.assertEqual(
            issues["nonordering_provenance_cross_links"][0]["relation"],
            "REGISTERS_CONSUMER",
        )

    def test_verification_command_reference_is_nonordering(self) -> None:
        theorem = certificate(
            "certificates/THEOREM.json",
            "THEOREM",
            {
                "verification_commands": [
                    "verify --consumer certificates/CONSUMER.json"
                ]
            },
        )
        consumer = certificate(
            "certificates/CONSUMER.json",
            "CONSUMER",
            {"theorem_ref": "certificates/THEOREM.json"},
        )
        files = {
            theorem.path: b'{"result_id":"THEOREM"}',
            consumer.path: b'{"result_id":"CONSUMER"}',
        }
        edges, issues = derive_edges([theorem, consumer], files)
        self.assertEqual(
            edges,
            [Edge(theorem.key, consumer.key, "DEPENDS_ON", "theorem_ref")],
        )
        self.assertEqual(
            issues["nonordering_provenance_cross_links"][0]["relation"],
            "VERIFIES_WITH",
        )

    def test_layout_topic_ignores_programme_root_name(self) -> None:
        q2 = certificate(
            "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json",
            "BERGER_SUPPORT_LOCAL_Q2",
            {},
        )
        q2 = replace(q2, family="Classical / clocks")
        self.assertEqual(_layout_topic(q2), "Nonlinear brackets and D--Cartan")


if __name__ == "__main__":
    unittest.main()
