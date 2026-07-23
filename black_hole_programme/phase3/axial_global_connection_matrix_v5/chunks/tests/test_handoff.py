from __future__ import annotations

import copy
import hashlib
import json
import math
import struct
import tempfile
import unittest
from pathlib import Path

from black_hole_programme.phase3.axial_global_connection_matrix_v5.chunks.verify_handoff import (
    HandoffError,
    canonical_sha256,
    verify_chain,
    verify_handoff,
)


ZERO = "0000000000000000"
ONE = f"{struct.unpack('>Q', struct.pack('>d', 1.0))[0]:016x}"
HASH_A = "a" * 64
HASH_B = "b" * 64


def _matrix_payload():
    center = [["0/1" for _ in range(12)] for _ in range(12)]
    linear = [["0/1" for _ in range(12)] for _ in range(12)]
    remainder = [[[ZERO, ZERO] for _ in range(12)] for _ in range(12)]
    hull = [[[ZERO, ZERO] for _ in range(12)] for _ in range(12)]
    for i in range(12):
        center[i][i] = "1/1"
        hull[i][i] = [ONE, ONE]
    return {
        "center": center,
        "linear": linear,
        "remainder": remainder,
        "hull": hull,
    }


def _artifact(k=0, *, producer_path="producer", input_path="input"):
    matrix = _matrix_payload()
    inputs = [{"path": input_path, "sha256": HASH_B}]
    return {
        "schema": "phase3-axial-global-affine-reset-handoff-v2",
        "artifact_kind": "infinity-standard-fundamental",
        "chunk_id": f"infinity-{k}",
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
            "start": f"{k}/1",
            "end": f"{k+1}/1",
        },
        "state": {
            "rows": 12,
            "cols": 12,
            "chart": "standard-real-12",
            "order": [
                "Re(P)", "Re(Pprime)", "Re(Q)", "Re(Qprime)", "Re(H1)", "Re(F)",
                "Im(P)", "Im(Pprime)", "Im(Q)", "Im(Qprime)", "Im(H1)", "Im(F)",
            ],
        },
        "solver": {
            "panels": 64,
            "resets": 1,
            "local_steps": 64,
            "order": 12,
            "rank_cells": 8,
            "global_panel_start": 64*k,
            "global_panel_end": 64*(k+1),
        },
        "frames": {
            "table_sha256": HASH_A,
            "left_boundary_sha256": f"{k:064x}",
            "right_boundary_sha256": f"{k+1:064x}",
            "generation": "single-global-exact-table-sliced-with-byte-identical-overlap",
        },
        "matrix": matrix,
        "integrity": {
            "producer": {"path": producer_path, "sha256": HASH_A},
            "inputs": inputs,
            "input_sha256": canonical_sha256(inputs),
            "output_sha256": canonical_sha256(matrix),
        },
        "proof": {
            "ok": True,
            "refusal_code": 0,
            "existence_certified": True,
            "uniqueness_certified": True,
            "factor_rank_certified": True,
            "outward_remainders": True,
        },
    }


class HandoffTests(unittest.TestCase):
    def test_valid_handoff_and_complete_chain(self):
        self.assertTrue(verify_handoff(_artifact()))
        self.assertTrue(verify_chain([_artifact(k) for k in range(28)]))

    def test_generator_and_cell_mutations_refuse(self):
        for key, value in (("generator", 7316), ("center", "129/256")):
            bad = _artifact()
            bad["cell"][key] = value
            with self.assertRaises(HandoffError):
                verify_handoff(bad)

    def test_global_panel_offset_mutation_refuses(self):
        bad = _artifact(3)
        bad["solver"]["global_panel_start"] = 0
        with self.assertRaises(HandoffError):
            verify_handoff(bad)

    def test_shape_and_state_order_mutations_refuse(self):
        bad = _artifact()
        bad["matrix"]["center"].pop()
        bad["integrity"]["output_sha256"] = canonical_sha256(bad["matrix"])
        with self.assertRaises(HandoffError):
            verify_handoff(bad)
        bad = _artifact()
        bad["state"]["order"][2], bad["state"]["order"][3] = (
            bad["state"]["order"][3], bad["state"]["order"][2]
        )
        with self.assertRaises(HandoffError):
            verify_handoff(bad)

    def test_output_hash_and_affine_containment_mutations_refuse(self):
        bad = _artifact()
        bad["matrix"]["center"][0][0] = "2/1"
        with self.assertRaises(HandoffError):
            verify_handoff(bad)
        bad = _artifact()
        bad["matrix"]["linear"][0][0] = "1/1"
        bad["integrity"]["output_sha256"] = canonical_sha256(bad["matrix"])
        with self.assertRaises(HandoffError):
            verify_handoff(bad)

    def test_nonfinite_and_reversed_remainders_refuse(self):
        bad = _artifact()
        bad["matrix"]["remainder"][0][0] = ["7ff0000000000000", ZERO]
        bad["integrity"]["output_sha256"] = canonical_sha256(bad["matrix"])
        with self.assertRaises(HandoffError):
            verify_handoff(bad)
        bad = _artifact()
        bad["matrix"]["remainder"][0][0] = [ONE, ZERO]
        bad["integrity"]["output_sha256"] = canonical_sha256(bad["matrix"])
        with self.assertRaises(HandoffError):
            verify_handoff(bad)

    def test_incomplete_chain_and_independently_rounded_frame_refuse(self):
        chain = [_artifact(k) for k in range(28)]
        with self.assertRaises(HandoffError):
            verify_chain(chain[:-1])
        bad = copy.deepcopy(chain)
        bad[3]["frames"]["left_boundary_sha256"] = "f" * 64
        with self.assertRaises(HandoffError):
            verify_chain(bad)

    def test_swapped_adjacent_resets_refuse(self):
        chain = [_artifact(k) for k in range(28)]
        chain[13], chain[14] = chain[14], chain[13]
        with self.assertRaises(HandoffError):
            verify_chain(chain)

    def test_exact_reset_boundary_mutation_refuses(self):
        bad = _artifact(9)
        bad["domain"]["end"] = "11/1"
        with self.assertRaises(HandoffError):
            verify_handoff(bad)

    def test_v1_seven_chunk_artifact_refuses(self):
        bad = _artifact()
        bad["schema"] = "phase3-axial-global-affine-chunk-handoff-v1"
        bad["domain"]["end"] = "4/1"
        bad["solver"].update({
            "panels": 256,
            "resets": 4,
            "global_panel_end": 256,
        })
        with self.assertRaises(HandoffError):
            verify_handoff(bad)

    def test_source_hashes_checked_against_repo_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            producer = root / "producer"
            source = root / "input"
            producer.write_bytes(b"producer")
            source.write_bytes(b"input")
            data = _artifact()
            data["integrity"]["producer"]["sha256"] = hashlib.sha256(
                producer.read_bytes()
            ).hexdigest()
            data["integrity"]["inputs"][0]["sha256"] = hashlib.sha256(
                source.read_bytes()
            ).hexdigest()
            data["integrity"]["input_sha256"] = canonical_sha256(
                data["integrity"]["inputs"]
            )
            self.assertTrue(verify_handoff(data, root))
            source.write_bytes(b"mutated")
            with self.assertRaises(HandoffError):
                verify_handoff(data, root)

    def test_path_traversal_refuses(self):
        bad = _artifact(producer_path="../producer")
        with self.assertRaises(HandoffError):
            verify_handoff(bad)


if __name__ == "__main__":
    unittest.main()
