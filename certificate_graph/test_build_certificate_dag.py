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
