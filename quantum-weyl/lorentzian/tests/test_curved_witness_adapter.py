from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import sympy as sp

from local_bv.schema_validation import validate_instance
from lorentzian import curved_witness_adapter as ADAPTER
from lorentzian.curved_witness_adapter_certificate import OUTPUT, ROOT, build_certificate
from transfer.berger_gauge_fixed_nonminimal_import import _load_record, _zero


class CurvedWitnessAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.minimal = ADAPTER._git_json(ADAPTER.MINIMAL_CERTIFICATE)
        cls.retained = ADAPTER._git_json(ADAPTER.RETAINED_CERTIFICATE)
        cls.nonminimal = ADAPTER._git_json(ADAPTER.NONMINIMAL_CERTIFICATE)
        cls.gauge = ADAPTER._git_json(ADAPTER.GAUGE_CERTIFICATE)
        cls.source = ADAPTER._validate_source_boundaries(
            cls.minimal, cls.retained, cls.nonminimal, cls.gauge
        )

    def _artifact(
        self, root: Path, name: str, matrix: ADAPTER.OperatorMatrix
    ) -> dict[str, str]:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(ADAPTER._matrix_record(matrix)), encoding="utf-8")
        return {
            "format": "JSON_EXACT_SPARSE_OPERATOR",
            "path": name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

    def _pairing(self) -> ADAPTER.OperatorMatrix:
        pairing = _zero(34, 34)
        for index in range(5):
            pairing[index][29 + index] = {(): sp.S.One}
            pairing[29 + index][index] = {(): -sp.S.One}
        for index in range(12):
            pairing[5 + index][17 + index] = {(): sp.S.One}
            pairing[17 + index][5 + index] = {(): -sp.S.One}
        return pairing

    def _payload(
        self, root: Path, *, target: ADAPTER.OperatorMatrix | None = None
    ) -> dict[str, object]:
        zero = _zero(34, 34)
        if target is None:
            target = zero
        return {
            "schema": ADAPTER.EXPORT_SCHEMA_ID,
            "result_id": "BERGER_CURVED_CLOCK_REATTACHED_WITNESS",
            "result_state": "CURVED_WITNESS_CANDIDATE",
            "classical_commit": "3" * 40,
            "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            "setting_id": ADAPTER.SETTING_ID,
            "row_layout": {"degree_ranks": [5, 12, 12, 5], "total_rows": 34},
            "operators": {
                "W34": self._artifact(root, "operators/W34.json", zero),
                "P34": self._artifact(root, "operators/P34.json", target),
                "pairing34": self._artifact(root, "operators/pairing34.json", self._pairing()),
            },
            "coordinate_transport": self.source["hashes"],
            "claim_boundary": "Exact mechanics fixture, not a physical curved witness.",
        }

    def test_checked_readiness_certificate_reproduces(self) -> None:
        certificate = build_certificate()
        self.assertEqual(json.loads(OUTPUT.read_text()), certificate)
        schema = json.loads(
            (ROOT / "schema" / "berger-curved-witness-adapter-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(certificate, schema))
        self.assertEqual(certificate["verdict"], "INPUT_BLOCKED")
        self.assertFalse(certificate["curved_witness_certified"])

    def test_existing_companion_transport_is_exact(self) -> None:
        self.assertEqual(
            self.source["hashes"]["curved_companion_sha256"],
            "78f449c1819f69afd3f5c793f55dd41a79194c1790fc85e9f1621e0f6fe2cb70",
        )
        self.assertTrue(ADAPTER._is_zero(ADAPTER._multiply(self.source["q34"], self.source["q34"])))

    def test_exact_zero_mechanics_fixture_takes_primitive_branch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root)
            export_schema = json.loads(
                (ROOT / "schema" / "berger-curved-witness-export-v1.schema.json").read_text()
            )
            self.assertFalse(validate_instance(payload, export_schema))
            result = ADAPTER.evaluate_curved_witness_export(
                payload, repository_root=root, source_data=self.source
            )
        self.assertEqual(result["verdict"], "ADMISSIBLE_EXACT_CURVED_WITNESS")
        self.assertTrue(result["curved_witness_certified"])
        self.assertFalse(result["green_execution_authorized"])

    def test_nonzero_fixture_returns_normalized_dual_witness(self) -> None:
        target = _zero(34, 34)
        target[0][0] = {(): sp.Integer(7)}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = ADAPTER.evaluate_curved_witness_export(
                self._payload(root, target=target),
                repository_root=root,
                source_data=self.source,
            )
        witness = result["obstruction_witness"]
        self.assertEqual(result["verdict"], "NONTRIVIAL_NORMALIZED_COEFFICIENT_OBSTRUCTION")
        self.assertEqual(witness["defect_kind"], "QW_PLUS_WQ_MINUS_P")
        self.assertEqual(witness["dual_pairing_on_defect"], "1")
        self.assertEqual(witness["pbw_order"], 0)
        self.assertEqual(witness["D_weight"], 0)
        self.assertEqual(witness["field_content"]["input_field"], "c_spatial_1")
        self.assertEqual(witness["field_content"]["output_field"], "c_spatial_1")
        self.assertEqual(
            result["obstruction_scope"],
            "SUBMITTED_CANDIDATE_ONLY_NOT_GLOBAL_NONEXISTENCE",
        )

    def test_mutated_coordinate_transport_fails_closed(self) -> None:
        forged = deepcopy(self.gauge)
        record = forged["gauge_fermion"]["gauge_condition_A"]
        matrix = _load_record("A", record, (5, 12))
        matrix[0][0] = {(): sp.Integer(123)}
        forged["gauge_fermion"]["gauge_condition_A"] = ADAPTER._matrix_record(matrix)
        with self.assertRaisesRegex(ValueError, "companion transport failed"):
            ADAPTER._validate_source_boundaries(
                self.minimal, self.retained, self.nonminimal, forged
            )

    def test_forged_operator_hash_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self._payload(root)
            payload["operators"]["W34"]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "artifact hash mismatch"):
                ADAPTER.evaluate_curved_witness_export(
                    payload, repository_root=root, source_data=self.source
                )


if __name__ == "__main__":
    unittest.main()
