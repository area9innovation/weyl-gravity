from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


TRANSFER_ROOT = Path(__file__).resolve().parents[1]
if str(TRANSFER_ROOT) not in sys.path:
    sys.path.insert(0, str(TRANSFER_ROOT))
MODULE_PATH = TRANSFER_ROOT / "berger_clock_sdr_import_certificate.py"
SPEC = importlib.util.spec_from_file_location(
    "berger_clock_sdr_import_certificate_test",
    MODULE_PATH,
)
assert SPEC is not None and SPEC.loader is not None
CERTIFICATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERTIFICATE
SPEC.loader.exec_module(CERTIFICATE)
IMPORT = sys.modules[CERTIFICATE.build_partial_sdr_import.__module__]


def _operator(operator_id: str, degree: int = 0) -> dict[str, object]:
    value: dict[str, object] = {
        "operator_id": operator_id,
        "domain_basis_indices": [0],
        "codomain_basis_indices": [0],
        "cohomological_degree": degree,
        "maximum_differential_order": 1,
        "entries": [],
    }
    value["canonical_sha256"] = IMPORT._canonical_hash(value)
    return value


def _portable_fixture() -> dict[str, object]:
    contracted = {3, 4, 15, 16, 27, 28, 32, 33}
    basis = []
    for index in range(34):
        if index < 5:
            degree = -1
        elif index < 17:
            degree = 0
        elif index < 29:
            degree = 1
        else:
            degree = 2
        if index in contracted:
            sector = "clock-contractible"
        elif index in {0, 1, 2, 29, 30, 31}:
            sector = "spatial-diffeomorphism"
        else:
            sector = "dressed-metric"
        basis.append(
            {
                "index": index,
                "symbol": f"e{index}",
                "cohomological_degree": degree,
                "parity": degree % 2,
                "sector": sector,
                "retained": index not in contracted,
            }
        )
    operators = {
        operator_id: _operator(
            operator_id,
            1 if operator_id == "q1_clock" else -1 if operator_id == "s_clock" else 0,
        )
        for operator_id in sorted(IMPORT.PORTABLE_OPERATOR_IDS)
    }
    convention = {
        "classical_grading": "shifted-bv-cohomological-v1",
        "transfer_suspension": "suspended-graded-symmetric-factorial-v1",
        "parity_rule": "cohomological-degree-mod-2",
        "derivative_symbol": "p_mu=partial_mu",
        "formal_adjoint": "integration by parts on closed S3",
        "basis_order_is_authoritative": True,
    }
    ring = {
        "ring": "Q[rho_bar,omega,rho_bar^-1,omega^-1]",
        "localized_units": ["rho_bar", "omega"],
        "assumptions": ["rho_bar!=0", "omega!=0"],
        "floating_point_forbidden": True,
    }
    checks = sorted(IMPORT.PORTABLE_BASE_CHECKS)
    manifest = {"producer.py": "1" * 64, "schema.json": "2" * 64, "test.py": "3" * 64}
    return {
        "schema": IMPORT.PORTABLE_SCHEMA_ID,
        "result_id": "BERGER_CLOCK_PARTIAL_SDR_PORTABLE_EXPORT",
        "theorem_source_commit": IMPORT.THEOREM_COMMIT,
        "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
        "phase_space_id": "positive_berger_fixed_coupling_linearized_solutions",
        "generator_id": "D_compact",
        "boundary_conditions_sha256": "4" * 64,
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "convention": convention,
        "coefficient_ring": ring,
        "basis": basis,
        "coverage": {
            "full_minimal_dimension": 34,
            "contracted_clock_dimension": 8,
            "retained_minimal_dimension": 26,
            "contracted_basis_indices": sorted(contracted),
            "complete_classical_contraction": False,
        },
        "operators": operators,
        "D_equivariance": {
            "status": "OPEN",
            "D_action": None,
            "commutators": {
                "D_q1": "OPEN",
                "D_s_cl": "OPEN",
                "D_pi_cl": "OPEN",
                "D_iota_cl": "OPEN",
            },
            "nd2_equivariant_use_authorized": False,
        },
        "proof_checks": checks,
        "canonical_hashes": {
            "basis": IMPORT._canonical_hash(basis),
            "operators": IMPORT._canonical_hash(operators),
            "coefficient_ring": IMPORT._canonical_hash(ring),
            "convention": IMPORT._canonical_hash(convention),
            "proof_checks": IMPORT._canonical_hash(checks),
        },
        "source_manifest": manifest,
        "source_manifest_sha256": IMPORT._canonical_hash(manifest),
        "claim_boundary": "Partial clock-sector SDR only; complete contraction false.",
    }


class BergerClockSDRImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.classical = IMPORT._load_git_json(
            IMPORT.CLASSICAL_CERTIFICATE.relative_to(IMPORT.ROOT).as_posix(),
            commit=IMPORT.THEOREM_COMMIT,
        )

    def test_checked_in_certificate_reproduces(self) -> None:
        checked = json.loads(CERTIFICATE.OUTPUT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checked, CERTIFICATE.build_certificate())

    def test_partial_coverage_is_imported_without_satisfying_nd2(self) -> None:
        result = CERTIFICATE.build_certificate()
        self.assertEqual(result["coverage"]["contracted_clock_dimension"], 8)
        self.assertEqual(result["coverage"]["full_minimal_dimension"], 34)
        self.assertEqual(
            result["coverage"]["coverage_status"],
            "PARTIAL_CLOCK_SECTOR_ONLY",
        )
        self.assertFalse(result["nd2_gate"]["classical_contraction_artifact_satisfied"])
        self.assertFalse(result["nd2_gate"]["physical_execution_authorized"])

    def test_portable_maps_and_D_equivariance_remain_open(self) -> None:
        gate = CERTIFICATE.build_certificate()["portable_map_gate"]
        self.assertEqual(gate["map_payload_status"], "FINGERPRINTS_AND_FORMULAS_ONLY")
        self.assertEqual(
            gate["operator_fingerprint_reconstruction_check"],
            "NOT_COMPUTED",
        )
        self.assertEqual(gate["portable_s_clock"], "NOT_AVAILABLE")
        self.assertEqual(gate["D_action_on_clock_block"], "NOT_AVAILABLE")
        self.assertEqual(gate["D_equivariance_checks"], "NOT_COMPUTED")

    def test_clock_row_or_map_mutation_is_rejected(self) -> None:
        for field in ("ordered_rows", "q1_maps", "homotopy_maps"):
            with self.subTest(field=field):
                payload = deepcopy(self.classical)
                payload["clock_block"][field][0] = "forged"
                with self.assertRaises(ValueError):
                    IMPORT._validate_classical_theorem(payload)

    def test_coverage_or_claim_promotion_is_rejected(self) -> None:
        mutations = (
            ("sdr", "contracted_clock_dimension", 34),
            ("flags", "full_Berger_clock_BV_theorem", True),
            ("flags", "retained_dressed_metric_q1_coefficients_complete", True),
        )
        for section, field, value in mutations:
            with self.subTest(section=section, field=field):
                payload = deepcopy(self.classical)
                payload[section][field] = value
                with self.assertRaises(ValueError):
                    IMPORT._validate_classical_theorem(payload)

    def test_fingerprint_inventory_and_digest_are_checked(self) -> None:
        missing = deepcopy(self.classical)
        missing["operator_fingerprints"].pop("q_clock")
        with self.assertRaises(ValueError):
            IMPORT._validate_classical_theorem(missing)
        forged = deepcopy(self.classical)
        forged["operator_fingerprints"]["q_clock"] = "not-a-hash"
        with self.assertRaises(ValueError):
            IMPORT._validate_classical_theorem(forged)

    def test_theorem_and_registration_commits_are_recorded(self) -> None:
        result = CERTIFICATE.build_certificate()
        self.assertEqual(result["classical_theorem_commit"], IMPORT.THEOREM_COMMIT)
        self.assertEqual(
            result["provenance"]["programme_registration"]["registration_commit"],
            IMPORT.REGISTRATION_COMMIT,
        )

    def test_portable_receiving_contract_accepts_fail_closed_open_D_fixture(self) -> None:
        fixture = _portable_fixture()
        self.assertIs(IMPORT.validate_portable_partial_sdr(fixture), fixture)

    def test_portable_contract_rejects_D_or_completeness_promotion(self) -> None:
        for path in ("D", "coverage"):
            with self.subTest(path=path):
                fixture = _portable_fixture()
                if path == "D":
                    fixture["D_equivariance"]["nd2_equivariant_use_authorized"] = True
                else:
                    fixture["coverage"]["complete_classical_contraction"] = True
                with self.assertRaises(ValueError):
                    IMPORT.validate_portable_partial_sdr(fixture)

    def test_portable_contract_rejects_operator_or_component_hash_drift(self) -> None:
        fixture = _portable_fixture()
        fixture["operators"]["q1_clock"]["entries"] = [
            {
                "output": 0,
                "input": 0,
                "multiindex": [1, 1, 0, 0],
                "coefficient": {"numerator": "1", "denominator": "1"},
            }
        ]
        with self.assertRaises(ValueError):
            IMPORT.validate_portable_partial_sdr(fixture)
        fixture = _portable_fixture()
        fixture["canonical_hashes"]["basis"] = "0" * 64
        with self.assertRaises(ValueError):
            IMPORT.validate_portable_partial_sdr(fixture)


if __name__ == "__main__":
    unittest.main()
