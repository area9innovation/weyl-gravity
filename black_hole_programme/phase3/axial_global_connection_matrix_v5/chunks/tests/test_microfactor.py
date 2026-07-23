from __future__ import annotations

import copy
import struct
import unittest

from black_hole_programme.phase3.axial_global_connection_matrix_v5.chunks.verify_handoff import (
    HandoffError,
    canonical_sha256,
)
from black_hole_programme.phase3.axial_global_connection_matrix_v5.chunks.verify_microfactor import (
    verify_microfactor,
    verify_microfactor_chain,
)


ZERO = "0000000000000000"
ONE = f"{struct.unpack('>Q', struct.pack('>d', 1.0))[0]:016x}"
HASH_A = "a" * 64
HASH_B = "b" * 64


def _artifact(j: int = 0) -> dict:
    center = [["0/1" for _ in range(12)] for _ in range(12)]
    linear = [["0/1" for _ in range(12)] for _ in range(12)]
    remainder = [[[ZERO, ZERO] for _ in range(12)] for _ in range(12)]
    hull = [[[ZERO, ZERO] for _ in range(12)] for _ in range(12)]
    for i in range(12):
        center[i][i] = "1/1"
        hull[i][i] = [ONE, ONE]
    matrix = {
        "center": center,
        "linear": linear,
        "remainder": remainder,
        "hull": hull,
    }
    inputs = [{"path": "input", "sha256": HASH_B}]
    from fractions import Fraction
    lo, hi = Fraction(j, 8), Fraction(j + 1, 8)
    return {
        "schema": "phase3-axial-global-affine-microfactor-handoff-v3",
        "artifact_kind": "infinity-moving-frame-microfactor",
        "chunk_id": f"micro-{j:03d}",
        "status": "CERTIFIED",
        "cell": {
            "parameter": "Momega",
            "generator": 7315,
            "lower": "1/2",
            "upper": "129/256",
            "center": "257/512",
            "radius": "1/512",
        },
        "domain": {
            "coordinate": "t=32-r",
            "orientation": "increasing-t/inward-r",
            "start": f"{lo.numerator}/{lo.denominator}",
            "end": f"{hi.numerator}/{hi.denominator}",
        },
        "state": {
            "rows": 12,
            "cols": 12,
            "chart": "global-moving-block-lower-12",
            "order": [
                "Re(P)", "Re(Pprime)", "Re(Q)", "Re(Qprime)",
                "Im(P)", "Im(Pprime)", "Im(Q)", "Im(Qprime)",
                "Re(H1)", "Re(F)", "Im(H1)", "Im(F)",
            ],
        },
        "solver": {
            "panels": 8,
            "resets": 1,
            "local_steps": 8,
            "order": 12,
            "rank_cells": 16,
            "global_panel_start": 8 * j,
            "global_panel_end": 8 * (j + 1),
            "structured_panels": 8,
            "structured_order": 12,
            "structured_rebase_bits": 128,
            "structured_global_panel_start": 8 * j,
            "structured_global_panel_end": 8 * (j + 1),
            "rank_argument": "block-lower-determinant",
        },
        "frames": {
            "table_sha256": HASH_A,
            "left_boundary_sha256": f"{8*j:064x}",
            "right_boundary_sha256": f"{8*(j+1):064x}",
            "generation": "single-global-exact-table-sliced-with-byte-identical-overlap",
        },
        "matrix": matrix,
        "integrity": {
            "producer": {"path": "producer", "sha256": HASH_A},
            "inputs": inputs,
            "input_sha256": canonical_sha256(inputs),
            "output_sha256": canonical_sha256(matrix),
            "generated_source": {
                "manifest_path": "manifest.json",
                "manifest_file_sha256": HASH_A,
                "renderer_path": "renderer.py",
                "renderer_sha256": HASH_B,
                "frame_table_sha256": HASH_A,
                "micro": j,
                "source_sha256": HASH_B,
                "retained_in_git": False,
            },
        },
        "proof": {
            "ok": True,
            "refusal_code": 0,
            "existence_certified": True,
            "uniqueness_certified": True,
            "factor_rank_certified": True,
            "factor_rank": 12,
            "outward_remainders": True,
            "lower_lift_included": True,
            "upper_right_exact_zero": True,
            "structured_lower_recurrence": True,
            "dyadic_rebase_bits": 128,
            "rank_argument": "block-lower-determinant",
            "block_max_width": {
                "carrier": "0.0",
                "lower": "0.0",
                "kernel": "0.0",
            },
            "storage_layout": "contiguous-block-lower-v1",
            "coefficient_layout": "standard-interleaved-v1",
            "transition_extractor": "contiguous-8-plus-4-v1",
        },
    }


class MicrofactorVerifierTests(unittest.TestCase):
    def test_valid_artifact(self):
        self.assertTrue(verify_microfactor(_artifact()))

    def test_wrong_grid_refuses(self):
        bad = _artifact()
        bad["solver"]["structured_panels"] = 16
        with self.assertRaises(HandoffError):
            verify_microfactor(bad)

    def test_interleaved_transition_extractor_mutation_refuses(self):
        bad = _artifact()
        bad["proof"]["transition_extractor"] = "standard-interleaved-v1"
        with self.assertRaises(HandoffError):
            verify_microfactor(bad)

    def test_nonzero_upper_right_mutation_refuses(self):
        bad = _artifact()
        bad["matrix"]["center"][0][8] = "1/1"
        bad["matrix"]["hull"][0][8] = [ONE, ONE]
        bad["integrity"]["output_sha256"] = canonical_sha256(bad["matrix"])
        with self.assertRaises(HandoffError):
            verify_microfactor(bad)

    def test_wrong_exact_boundary_refuses(self):
        bad = _artifact(7)
        bad["domain"]["end"] = "2/1"
        with self.assertRaises(HandoffError):
            verify_microfactor(bad)

    def test_hull_and_hash_mutations_refuse(self):
        bad = _artifact()
        bad["matrix"]["linear"][0][0] = "2/1"
        bad["integrity"]["output_sha256"] = canonical_sha256(bad["matrix"])
        with self.assertRaises(HandoffError):
            verify_microfactor(bad)

    def test_generated_source_pin_mutation_refuses(self):
        bad = _artifact()
        bad["integrity"]["generated_source"]["micro"] = 7
        with self.assertRaises(HandoffError):
            verify_microfactor(bad)

    def test_complete_chain_and_boundary_hash_mutation(self):
        chain = [_artifact(j) for j in range(224)]
        self.assertTrue(verify_microfactor_chain(chain))
        bad = copy.deepcopy(chain)
        bad[91]["frames"]["left_boundary_sha256"] = "f" * 64
        with self.assertRaises(HandoffError):
            verify_microfactor_chain(bad)
        bad = copy.deepcopy(_artifact())
        bad["integrity"]["output_sha256"] = "f" * 64
        with self.assertRaises(HandoffError):
            verify_microfactor(bad)


if __name__ == "__main__":
    unittest.main()
