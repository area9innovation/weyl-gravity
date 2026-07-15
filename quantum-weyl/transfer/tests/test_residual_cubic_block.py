from __future__ import annotations

from copy import deepcopy
import json
import sys
import unittest
from pathlib import Path


QUANTUM_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(QUANTUM_ROOT))

from transfer.residual_cubic_block import (
    OUTPUT_PATH,
    SCHEMA_PATH,
    build_certificate,
    validate_certificate,
    validate_transfer_payload,
)


class ResidualCubicBlockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate(4)

    def test_checked_in_certificate_reproduces(self) -> None:
        checked = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checked, self.certificate)

    def test_selected_residual_cubic_bracket_is_nonzero_and_closed(self) -> None:
        certificate = self.certificate
        self.assertEqual(
            certificate["result_state"],
            "SELECTED_RESIDUAL_CUBIC_BRACKET_COMPUTED",
        )
        self.assertEqual(certificate["cubic_charge"]["component_count"], 15)
        self.assertEqual(certificate["checks"]["conformal_closure"], "VERIFIED_ON_EVERY_INTERIOR_SHELL")
        self.assertEqual(certificate["checks"]["chirality_off_diagonal_nonzero_entries"], 0)
        self.assertEqual(
            certificate["checks"]["common_magnetic_basis"],
            "VERIFIED_ENTRYWISE_BOTH_CHIRALITIES",
        )
        master = certificate["checks"]["cubic_master_equation"]
        self.assertEqual(master["status"], "VERIFIED_EXACT_CUBIC_MASTER_EQUATION")
        self.assertEqual(master["total_nonzero_coefficient_blocks"], 0)

    def test_portable_payload_and_schema_are_present(self) -> None:
        payload = self.certificate["transfer_payload"]
        self.assertEqual(payload["schema_version"], 2)
        self.assertEqual(len(payload["basis"]), 15)
        self.assertEqual(
            len(payload["matter_phase_space"]["ordered_basis"]),
            payload["matter_phase_space"]["dimension"],
        )
        self.assertEqual(
            tuple(payload["q2"]["ghost_matter_to_matter"]["matrices"]),
            tuple(item["name"] for item in payload["basis"]),
        )
        self.assertEqual(
            json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))["$id"],
            "residual-cubic-block-v2.schema.json",
        )

    def test_payload_rejects_basis_permutation(self) -> None:
        payload = deepcopy(self.certificate["transfer_payload"])
        payload["basis"][0], payload["basis"][1] = payload["basis"][1], payload["basis"][0]
        with self.assertRaisesRegex(ValueError, "basis identity or ordering"):
            validate_transfer_payload(payload)

    def test_payload_rejects_action_scale_change(self) -> None:
        payload = deepcopy(self.certificate["transfer_payload"])
        payload["matter_phase_space"]["canonical_action_scale"] = "Rational(1, 2)"
        with self.assertRaisesRegex(ValueError, "action scale"):
            validate_transfer_payload(payload)

    def test_payload_rejects_missing_component(self) -> None:
        payload = deepcopy(self.certificate["transfer_payload"])
        del payload["q2"]["ghost_matter_to_matter"]["matrices"]["D"]
        with self.assertRaisesRegex(ValueError, "missing or reordered"):
            validate_transfer_payload(payload)

    def test_payload_rejects_floating_point_scalar(self) -> None:
        payload = deepcopy(self.certificate["transfer_payload"])
        payload["matter_phase_space"]["canonical_action_scale"] = "Float('-0.5')"
        with self.assertRaisesRegex(ValueError, "exact SymPy"):
            validate_transfer_payload(payload)

    def test_payload_rejects_reduced_master_equation_window(self) -> None:
        payload = deepcopy(self.certificate["transfer_payload"])
        payload["matter_phase_space"]["master_equation_source_indices"].pop()
        with self.assertRaisesRegex(ValueError, "source window"):
            validate_transfer_payload(payload)

    def test_certificate_rejects_modified_upstream_hash(self) -> None:
        certificate = deepcopy(self.certificate)
        first_path = next(iter(certificate["provenance"]["upstream_sha256"]))
        certificate["provenance"]["upstream_sha256"][first_path] = "0" * 64
        with self.assertRaisesRegex(ValueError, "upstream content hash"):
            validate_certificate(certificate)

    def test_matter_self_bracket_and_missing_local_lift_are_distinguished(self) -> None:
        computed = " ".join(self.certificate["computed_taylor_blocks"])
        self.assertIn("ell_2(physical_matter, physical_matter)", computed)
        missing = " ".join(self.certificate["uncomputed_taylor_blocks"])
        self.assertIn("support-local classical q2", missing)
        guards = " ".join(self.certificate["claim_guards"])
        self.assertIn("does not serialize the complete support-local", guards)
        self.assertIn("does not prove that the Pontryagin direction is central", guards)

    def test_centered_one_particle_statement_is_scoped(self) -> None:
        self.assertEqual(self.certificate["checks"]["one_particle_centered_h4"], 0)
        self.assertIn(
            "for this residual cubic charge block",
            self.certificate["scientific_consequences"][-1],
        )


if __name__ == "__main__":
    unittest.main()
