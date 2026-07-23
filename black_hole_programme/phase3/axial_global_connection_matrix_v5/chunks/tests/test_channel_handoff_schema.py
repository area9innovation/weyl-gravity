from __future__ import annotations

import copy
import unittest

from jsonschema import ValidationError

from ..verify_channel_handoff_schema import _realify, load_validator, validate


ZERO = "0000000000000000"
HASH = "a" * 64


def scalar(value: int = 0) -> dict:
    return {
        "center": f"{value}/1",
        "linear": "0/1",
        "remainder": [ZERO, ZERO],
    }


def complex_scalar(value: int = 0) -> dict:
    return {"re": scalar(value), "im": scalar()}


def matrix(rows: int, cols: int) -> list:
    return [[complex_scalar() for _ in range(cols)] for _ in range(rows)]


def valid_document() -> dict:
    connection = matrix(6, 3)
    for rows in ((0, 1, 4), (2, 3, 5)):
        for col, row in enumerate(rows):
            connection[row][col] = complex_scalar(1)
    zero_form = matrix(3, 3)
    rank = {
        "rank": 3, "kernel_dimension": 0, "whole_cell": True,
        "method": "validated interval minor",
        "witness_sha256": HASH,
    }
    inertia = {
        "positive": 0, "negative": 0, "zero": 3, "whole_cell": True,
        "method": "validated congruence pivots",
        "witness_sha256": HASH,
    }
    return {
        "schema": "phase3-axial-global-channel-handoff-v1",
        "status": "CERTIFIED",
        "dependency_tags": ["LORENTZIAN-CAUSAL", "REDUCED-MODE"],
        "cell": {
            "ell": 2, "mass_normalization": "M=1",
            "omega_parameter": "M*omega",
            "omega_interval": ["1/2", "129/256"],
            "affine_generator": 7315,
        },
        "basis": {
            "phase_convention": "exp(+i*omega*v)",
            "complex_infinity_order": ["XI0", "XI1", "XI2", "XI3", "EI0", "EI2"],
            "real_infinity_order": [
                "Re(XI0)", "Re(XI1)", "Re(XI2)", "Re(XI3)", "Re(EI0)", "Re(EI2)",
                "Im(XI0)", "Im(XI1)", "Im(XI2)", "Im(XI3)", "Im(EI0)", "Im(EI2)",
            ],
            "Iminus_selector": [0, 1, 4], "Iplus_selector": [2, 3, 5],
            "raw_horizon_order": [
                "XH0a", "XH0b", "EH0", "XHplus", "EHout", "XHminus",
            ],
            "public_horizon_order": [
                "XH0a", "XH0b", "XHplus", "XHminus", "EH0", "EHout",
            ],
            "public_index_to_raw_index": [0, 1, 3, 5, 2, 4],
            "raw_index_to_public_index": [0, 1, 4, 2, 5, 3],
            "raw_future_regular_selector": [0, 1, 2],
            "public_future_regular_selector": [0, 1, 4],
            "future_regular_origin_order": ["XH0a", "XH0b", "EH0"],
            "standard_r4_real_order": [
                "Re(P)", "Re(Pprime)", "Re(Q)", "Re(Qprime)", "Re(H1)", "Re(F)",
                "Im(P)", "Im(Pprime)", "Im(Q)", "Im(Qprime)", "Im(H1)", "Im(F)",
            ],
        },
        "connection": {
            "complex_6_by_3": connection,
            "realified_12_by_6": _realify(connection),
            "Cminus_3_by_3": [connection[i] for i in (0, 1, 4)],
            "Cplus_3_by_3": [connection[i] for i in (2, 3, 5)],
        },
        "endpoint_forms": {
            "orientation": {
                "radial_current": "F^r/(pi*alpha_W)",
                "Hermitian_flux": "i*F^r/(pi*alpha_W)",
                "Hplus_outward": "minus the +r radial orientation",
                "identity": "GHplus+gplus-gminus=0",
            },
            "Gminus": zero_form, "Gplus": zero_form,
            "GHplus_outward": zero_form,
            "gminus_pullback": zero_form, "gplus_pullback": zero_form,
            "conservation": {
                "identity": "GHplus+gplus-gminus=0",
                "defect": zero_form, "zero_contained_entrywise": True,
                "structural_identity_witness": "exact synthetic zero identity",
                "witness_sha256": HASH,
            },
        },
        "classification_witnesses": {
            "rank": {"connection": rank, "Cminus": rank, "Cplus": rank},
            "inertia": {"GHplus": inertia, "gminus": inertia, "gplus": inertia},
            "exceptional_cell": False,
            "multiplier_bounds": {
                "connection_operator_norm_upper": "1.0",
                "Cminus_inverse_norm_upper": "1.0",
                "frequency_derivative_norm_upper": "1.0",
                "whole_cell": True,
            },
        },
        "provenance": {
            key: HASH for key in (
                "global_frame_table_sha256", "left_boundary_frame_sha256",
                "right_boundary_frame_sha256", "moving_join_artifact_sha256",
                "horizon_transport_artifact_sha256",
                "endpoint_gram_artifact_sha256", "producer_sha256",
                "verifier_sha256", "replay_receipt_sha256",
            )
        },
        "missing_Hminus": {
            "available": False, "full_scattering_matrix_constructed": False,
            "reason": "Past-horizon incoming data are not part of this one-sided future-regular handoff.",
        },
        "does_not_establish": [
            "a past-horizon incoming block",
            "a complete scattering matrix",
            "CPT positivity or unitarity",
            "complex-frequency stability",
        ],
    }


class ChannelHandoffSchemaTest(unittest.TestCase):
    def test_schema_is_valid(self) -> None:
        load_validator()

    def test_synthetic_contract_is_valid(self) -> None:
        validate(valid_document())

    def test_empty_document_is_not_a_handoff(self) -> None:
        with self.assertRaises(ValidationError):
            load_validator().validate({})

    def test_unvalidated_status_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            load_validator().validate({
                "schema": "phase3-axial-global-channel-handoff-v1",
                "status": "UNVALIDATED-NUMERIC",
            })

    def test_missing_hminus_contract_is_frozen(self) -> None:
        definition = load_validator().schema["properties"]["missing_Hminus"]
        self.assertEqual(definition["const"]["available"], False)
        self.assertEqual(
            definition["const"]["full_scattering_matrix_constructed"], False
        )

    def test_wrong_projection_is_rejected(self) -> None:
        document = valid_document()
        document["connection"]["Cminus_3_by_3"] = copy.deepcopy(
            document["connection"]["Cminus_3_by_3"]
        )
        document["connection"]["Cminus_3_by_3"][0][0] = complex_scalar()
        with self.assertRaisesRegex(ValueError, "row projection"):
            validate(document)

    def test_wrong_realification_is_rejected(self) -> None:
        document = valid_document()
        document["connection"]["realified_12_by_6"][0][0] = scalar()
        with self.assertRaisesRegex(ValueError, "realified"):
            validate(document)

    def test_inconsistent_inertia_is_rejected(self) -> None:
        document = valid_document()
        document["classification_witnesses"]["inertia"]["gplus"]["positive"] = 1
        with self.assertRaisesRegex(ValueError, "sum to three"):
            validate(document)


if __name__ == "__main__":
    unittest.main()
