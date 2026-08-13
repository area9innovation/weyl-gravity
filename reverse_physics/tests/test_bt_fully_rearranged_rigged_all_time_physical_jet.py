from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CERT = os.path.join(
    ROOT, "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PHYSICAL_JET_V1.json"
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_fully_rearranged_rigged_all_time_physical_jet.py"
)
VERIFIER = os.path.join(
    ROOT, "reverse_physics/verify_bt_fully_rearranged_rigged_all_time_physical_jet.py"
)


def set_path(value, path, replacement):
    cursor = value
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = replacement


MUTATIONS = {
    "schema_extra": (("unexpected",), "forbidden"),
    "certificate": (("certificate",), "REVERSE_PHYSICS_BT_FALSE"),
    "tag": (("dependency_tags", 1), "LORENTZIAN-CAUSAL"),
    "disconnected_count": (("selected_physical_domain", "disconnected_partitions"), 201),
    "support_margin": (("selected_physical_domain", "support_margins_squared", 1), "31/625"),
    "orthogonality": (("selected_physical_domain", "input_output_orthogonality"), "P_Y*P_X!=0"),
    "support_status": (("selected_physical_domain", "status"), "PARTIAL"),
    "support_conclusion": (("selected_physical_domain", "support_conclusion"), "some terms vanish"),
    "all_time_conclusion": (("selected_physical_domain", "all_time_conclusion"), "assumed"),
    "coupling": (("complete_amplitude_jet", "coupling"), "g=lambda"),
    "amplitude": (("complete_amplitude_jet", "amplitude"), "missing T6"),
    "amplitude_status": (("complete_amplitude_jet", "status"), "INCOMPLETE"),
    "graph_exhaustion": (("complete_amplitude_jet", "graph_exhaustion"), "triangle only"),
    "probability": (("physical_probability_jet", "formula"), "lambda^8*q8"),
    "q8_sign": (("physical_probability_jet", "q8_sign"), "UNKNOWN"),
    "q10_sign": (("physical_probability_jet", "q10_sign"), "POSITIVE"),
    "probability_status": (("physical_probability_jet", "status"), "PARTIAL"),
    "completeness_scope": (("physical_probability_jet", "completeness_scope"), "all channels"),
    "E8_identity": (("common_Born_operator_identity", "E8"), "E8_public!=E8_Hilbert"),
    "E10_identity": (("common_Born_operator_identity", "E10"), "E10_public!=E10_Hilbert"),
    "witness_tree": (("common_Born_operator_identity", "finite_exact_witness", "tree", 0, 0), 9),
    "witness_loop": (("common_Born_operator_identity", "finite_exact_witness", "loop", 1, 1), 8),
    "witness_E10": (("common_Born_operator_identity", "finite_exact_witness", "E10_public", 0, 0), 0),
    "born_status": (("common_Born_operator_identity", "status"), "SCALAR_ONLY"),
    "safe_radius": (("small_coupling_positivity", "rational_lemma_fixture", "safe_lambda_squared", "numerator"), 34),
    "lower_margin": (("small_coupling_positivity", "rational_lemma_fixture", "lower_margin", "numerator"), 2),
    "positivity_status": (("small_coupling_positivity", "status"), "NOT_PROVED"),
    "RG_status": (("renormalization_group", "status"), "NOT_INVARIANT"),
    "all_channel": (("claim_boundary", "all_channel_probability"), "CONSTRUCTED"),
    "finite_coupling": (("claim_boundary", "finite_coupling_exact_probability"), "PROVED"),
    "S_operator": (("claim_boundary", "Moller_LSZ_S"), "CONSTRUCTED"),
    "Eq19": (("claim_boundary", "general_Eq19"), "PROVED"),
    "gravity": (("claim_boundary", "gravity_BV_BRST_QME"), "CONSTRUCTED"),
    "causal": (("claim_boundary", "Lorentzian_causal_claim"), "ESTABLISHED"),
    "input_hash": (("provenance", "input_hashes", "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_Q10_PACKET_V1.json"), "0" * 64),
    "recorded_check": (("checks", "items", "q10_graph_ledger_is_exhaustive"), False),
}


class AllTimePhysicalJetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def command(self, command):
        return subprocess.run(
            command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, check=False,
        )

    def test_producer_check(self):
        run = self.command([sys.executable, PRODUCER, "--check"])
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_independent_verifier(self):
        run = self.command([sys.executable, VERIFIER])
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def reject_mutation(self, path, replacement):
        mutation = copy.deepcopy(self.certificate)
        set_path(mutation, path, replacement)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(mutation, handle)
            temporary = handle.name
        try:
            run = self.command([sys.executable, VERIFIER, "--verify", temporary])
            self.assertNotEqual(run.returncode, 0, run.stdout + run.stderr)
        finally:
            os.unlink(temporary)


def make_mutation_test(path, replacement):
    def test(self):
        self.reject_mutation(path, replacement)
    return test


for mutation_name, (mutation_path, mutation_value) in MUTATIONS.items():
    setattr(
        AllTimePhysicalJetTests,
        f"test_{mutation_name}_mutation_rejected",
        make_mutation_test(mutation_path, mutation_value),
    )


if __name__ == "__main__":
    unittest.main()
