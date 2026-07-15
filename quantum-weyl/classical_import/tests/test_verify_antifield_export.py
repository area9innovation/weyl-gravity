from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


IMPORT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = IMPORT_ROOT / "verify_antifield_export.py"
SPEC = importlib.util.spec_from_file_location("verify_antifield_export", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


def _generator(symbol: str, role: str, ghost: int, antifield: int, parity: int) -> dict[str, object]:
    return {
        "symbol": symbol,
        "role": role,
        "sector": "minimal",
        "tensor_type": {"slots": []},
        "ghost_number": ghost,
        "antifield_number": antifield,
        "form_degree": 4,
        "Grassmann_parity": parity,
        "mass_dimension": 4,
        "Weyl_weight": 0,
        "Q_image": {"terms": [{"coefficient": {"numerator": 1, "denominator": 1}}]},
        "Q_decomposition": {
            "delta": {"antifield_number_shift": -1, "image": {}},
            "gamma": {"antifield_number_shift": 0, "image": {}},
            "Q_gt0": {"antifield_number_shift": 1, "image": {}},
        },
        "canonical_index_symmetry": {"generators": []},
        "equation_or_identity_row": {"row_id": f"{role}_row"},
    }


def _rehash(payload: dict[str, object]) -> dict[str, object]:
    generators = payload["generators"]
    checks = payload["filtration_checks"]
    payload["canonical_hashes"] = {
        "generator_dictionary_hash": VERIFY._digest(
            [
                {key: value for key, value in generator.items() if key not in {"Q_image", "Q_decomposition"}}
                for generator in generators
            ]
        ),
        "q_image_hash": VERIFY._digest([generator["Q_image"] for generator in generators]),
        "filtration_hash": VERIFY._digest(
            {
                "rows": [generator["Q_decomposition"] for generator in generators],
                "checks": checks,
            }
        ),
    }
    return payload


def valid_payload() -> dict[str, object]:
    generators = [
        _generator("g_star", "metric_antifield", -1, 1, 1),
        _generator("xi_star", "diffeomorphism_ghost_antifield", -2, 2, 0),
        _generator("omega_star", "weyl_ghost_antifield", -2, 2, 0),
    ]
    checks = [
        {
            "check_id": check_id,
            "status": "VERIFIED",
            "proof_artifact": {"path": f"proof/{check_id}.json", "sha256": "0" * 64},
        }
        for check_id in sorted(VERIFY.REQUIRED_CHECKS)
    ]
    payload: dict[str, object] = {
        "schema": "quantum-weyl-antifield-export-v1",
        "classical_commit": "0" * 40,
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "expression_schema_version": "test-fixture-v1",
        "generators": generators,
        "filtration_checks": checks,
    }
    return _rehash(payload)


class AntifieldExportPreflightTests(unittest.TestCase):
    def test_complete_exact_fixture_passes(self) -> None:
        result = VERIFY.validate_export(valid_payload())
        self.assertEqual(result["status"], "PREFLIGHT_VERIFIED")
        self.assertEqual(result["generator_count"], 3)

    def test_multiple_nonminimal_or_auxiliary_antifields_are_allowed(self) -> None:
        payload = valid_payload()
        first = _generator("bar_xi_star", "other_antifield", -1, 1, 0)
        first["sector"] = "nonminimal"
        second = _generator("b_star", "other_antifield", -1, 1, 1)
        second["sector"] = "auxiliary"
        payload["generators"].extend((first, second))
        result = VERIFY.validate_export(_rehash(payload))
        self.assertEqual(result["generator_count"], 5)

    def test_missing_minimal_antifield_fails_closed(self) -> None:
        payload = valid_payload()
        payload["generators"] = payload["generators"][:-1]
        with self.assertRaisesRegex(VERIFY.AntifieldExportError, "at least three"):
            VERIFY.validate_export(payload)

    def test_float_payload_fails_closed(self) -> None:
        payload = valid_payload()
        payload["generators"][0]["mass_dimension"] = 4.0
        with self.assertRaisesRegex(VERIFY.AntifieldExportError, "floating-point"):
            VERIFY.validate_export(payload)

    def test_wrong_delta_degree_fails_closed(self) -> None:
        payload = valid_payload()
        payload["generators"][0]["Q_decomposition"]["delta"]["antifield_number_shift"] = 0
        with self.assertRaisesRegex(VERIFY.AntifieldExportError, "wrong delta"):
            VERIFY.validate_export(payload)

    def test_unverified_identity_fails_closed(self) -> None:
        payload = valid_payload()
        payload["filtration_checks"][0]["status"] = "NOT_COMPUTED"
        with self.assertRaisesRegex(VERIFY.AntifieldExportError, "must be VERIFIED"):
            VERIFY.validate_export(payload)

    def test_hash_drift_fails_closed(self) -> None:
        payload = copy.deepcopy(valid_payload())
        payload["generators"][0]["Q_image"]["terms"].append({"coefficient": 2})
        with self.assertRaisesRegex(VERIFY.AntifieldExportError, "hashes do not reproduce"):
            VERIFY.validate_export(payload)


if __name__ == "__main__":
    unittest.main()
