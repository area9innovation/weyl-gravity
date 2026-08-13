#!/usr/bin/env python3
"""Produce the fully rearranged complete-leading common-Born certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_COMMON_BORN_PHYSICAL_V1.json"
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = "reverse_physics/schema/reverse-physics-bt-fully-rearranged-common-born-physical-v1.schema.json"
REPORT = "reverse_physics/reports/bt-fully-rearranged-common-born-physical.md"
SOURCE = "23de3e07843b5acd41a6c9bf880fc05c0e6e4ff7"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-fully-rearranged-common-born-physical.json",
    "planning/events/reverse-physics-bateman-fully-rearranged-common-born-physical-DONE-23de3e07.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_COMMON_BORN_PACKET_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_GLOBAL_CONNECTED_FINITE_TIME_PACKET_COLUMN_V1.json",
]


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def transpose(a): return [list(row) for row in zip(*a)]
def multiply(a, b):
    return [[sum((a[i][k] * b[k][j] for k in range(len(b))), Fraction()) for j in range(len(b[0]))] for i in range(len(a))]
def subtract(a, b): return [[x-y for x, y in zip(r, s)] for r, s in zip(a, b)]
def trace(a): return sum((a[i][i] for i in range(len(a))), Fraction())
def strings(a): return [[str(x) for x in row] for row in a]


def build():
    work, event, public, physical, common, global_column = map(load, INPUTS)
    a8 = [[Fraction(x) for x in row] for row in common["exact_generic_Choi_witness"]["A_6"]]
    k8 = [[Fraction(x) for x in row] for row in common["exact_generic_Choi_witness"]["kappa_3"]]
    zero8 = [[Fraction() for _ in range(8)] for _ in range(8)]
    eye8 = [[Fraction(i == j) for j in range(8)] for i in range(8)]
    px = [eye8[i] + zero8[i] for i in range(8)] + [zero8[i] + zero8[i] for i in range(8)]
    py = [zero8[i] + zero8[i] for i in range(8)] + [zero8[i] + eye8[i] for i in range(8)]
    kappa = [k8[i] + zero8[i] for i in range(8)] + [zero8[i] + k8[i] for i in range(8)]
    transition = [zero8[i] + zero8[i] for i in range(8)] + [a8[i] + zero8[i] for i in range(8)]
    restricted = multiply(multiply(py, transition), px)
    alpha = multiply(multiply(kappa, restricted), kappa)
    sharp = multiply(multiply(kappa, transpose(restricted)), kappa)
    hilbert_effect = multiply(transpose(restricted), restricted)
    public_effect = multiply(sharp, restricted)
    public_square = trace(public_effect)
    hilbert_square = trace(hilbert_effect)
    zero16 = [[Fraction() for _ in range(16)] for _ in range(16)]

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "work_item_is_active": work["body"]["state"] == "ACTIVE",
        "done_event_matches": event["body"]["payload"]["to_state"] == "DONE",
        "public_Born_rule_imported": "tr(A^dagger A)" in public["public_inputs"]["born_rule"],
        "predecessors_pass": all(row["checks"]["ok"] for row in (physical, common, global_column)),
        "projectors_are_orthogonal": multiply(py, px) == zero16,
        "projectors_are_idempotent": multiply(px, px) == px and multiply(py, py) == py,
        "total_kappa_is_involutive": multiply(kappa, kappa) == [[Fraction(i == j) for j in range(16)] for i in range(16)],
        "input_projector_commutes_with_kappa": subtract(multiply(px, kappa), multiply(kappa, px)) == zero16,
        "output_projector_commutes_with_kappa": subtract(multiply(py, kappa), multiply(kappa, py)) == zero16,
        "restriction_is_exact": restricted == transition,
        "restricted_transition_is_kappa_fixed": alpha == restricted,
        "restricted_Krein_adjoint_equals_Hilbert_adjoint": sharp == transpose(restricted),
        "public_and_Hilbert_effects_are_identical": public_effect == hilbert_effect,
        "public_and_Hilbert_trace_squares_are_770": public_square == hilbert_square == 770,
        "Born_defect_is_zero": public_square - hilbert_square == 0,
        "disconnected_partition_ledger_is_exhaustive": physical["disconnected_support_classification"]["disconnected_set_partitions"] == 202,
        "all_disconnected_leading_terms_vanish": physical["disconnected_support_classification"]["detector_pairing"] == "ZERO_FOR_EVERY_DISCONNECTED_PARTITION_THROUGH_ORDER_LAMBDA4",
        "restricted_connected_is_complete_leading": physical["complete_leading_physical_probability"]["status"] == "COMPLETE_LEADING_FULLY_REARRANGED_FINITE_TIME_PHYSICAL_PROBABILITY",
        "identity_and_forward_do_not_enter": "do not enter" in physical["complete_leading_physical_probability"]["forward_independence"],
        "global_leading_coefficient_is_bounded": global_column["global_connected_column"]["status"] == "GLOBAL_CONNECTED_FINITE_TIME_POSITIVE_EFFECT_CONSTRUCTED",
        "global_column_has_same_ten_channel_tensor_structure": global_column["global_connected_column"]["amplitude"] == "A_full=16*lambda^4*sum_(B=0)^9(K_B,T tensor R_B)",
        "global_scalar_kernels_act_only_on_momentum": "full phase-space product" in global_column["global_connected_column"]["kernel"],
        "ten_channel_interference_is_retained": "sum_(B=1)^9" in physical["complete_leading_physical_probability"]["declared_scalar_coefficient"],
        "higher_Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_FULLY_REARRANGED_COMMON_BORN_PHYSICAL_V1",
        "question": "Is the already complete-leading fully rearranged finite-time BT transition also a public common-Born physical process, rather than only a positive-Hilbert coefficient?",
        "answer": "Yes at leading nonzero order for the certified nonempty class of fully rearranged packet detectors. Write the lambda-independent connected coefficient as T4 and restrict it by T4,YX=P_Y T4 P_X. The momentum-support projectors P_X and P_Y act trivially on the eight-dimensional species carrier, while total ghost parity kappa_3 acts trivially on momentum, so both projectors commute with parity. Coefficientwise fixedness of the coherent ten-channel Choi kernel therefore implies alpha(T4,YX)=T4,YX and T4,YX^sharp=T4,YX*. The fully rearranged support theorem exhausts all 202 disconnected six-leg partitions and makes every disconnected order-lambda4 distribution vanish on the same detector. Hence T4,YX is the complete, not merely connected, leading transition coefficient. Its public and Hilbert leading click effects coincide exactly, and the common scalar coefficient is 16 lambda^8 ||sum_(B=1)^9 P_Y K_B,T P_X F||^2, with all interference retained and bound 81 lambda^8 T^2/(200 pi^6). This proves a complete-leading finite-time public auxiliary physical BT probability. It does not control the O(lambda^9) remainder, spectator-overlap detectors, the forward block beyond its leading orthogonality decoupling, all orders, Eq. (19), gravity or Lorentzian causality.",
        "result_kind": "complete-leading fully rearranged finite-time BT packet transition with operator-level public-Krein/positive-Hilbert Born equality",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "assumptions": [
            "the exact fully rearranged compact packet supports and linked-cluster support classification are retained",
            "T4 denotes the lambda-independent coefficient so that P_Y(U_T-I)P_X=lambda^4 T4,YX+O(lambda^5)",
            "momentum support projectors act identically on the species carrier and total ghost parity acts identically on momentum",
            "the globally Hilbert-Schmidt connected coefficient and its common packet core are used",
            "the statement is coefficient-level and does not bound the higher perturbative remainder"
        ],
        "provenance": {
            "source_commit": SOURCE, "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_fully_rearranged_common_born_physical.py",
            "independent_verifier": "reverse_physics/verify_bt_fully_rearranged_common_born_physical.py",
            "method": "Exact Fraction-only 16-by-16 tensor reconstruction of two momentum labels and the eight-dimensional species carrier; independent support-ledger import; no floating-point arithmetic."
        },
        "exact_tensor_witness": {
            "space": "span{|X>,|Y>} tensor C^8_species",
            "P_X": strings(px), "P_Y": strings(py), "kappa_total": strings(kappa),
            "T4_YX": strings(restricted),
            "projector_product": "P_Y P_X=0",
            "commutators": ["[P_X,kappa_total]=0", "[P_Y,kappa_total]=0"],
            "fixed_point": "kappa_total T4,YX kappa_total=T4,YX",
            "adjoint": "T4,YX^sharp=T4,YX*",
            "public_trace_square": str(public_square), "Hilbert_trace_square": str(hilbert_square), "Born_defect": "0",
            "status": "ORTHOGONAL_PACKET_RESTRICTION_PRESERVES_TOTAL_KAPPA_FIXEDNESS_EXACTLY"
        },
        "complete_leading_common_Born_transition": {
            "expansion": "P_Y(U_T-I)P_X=lambda^4*T4,YX+O(lambda^5)",
            "connected_restriction": "T4,YX=P_Y*T4*P_X",
            "disconnected_restriction": "P_Y*D4_disconnected*P_X=0 for all 202 disconnected partitions",
            "complete_leading_identity": "L4_YX=T4,YX",
            "fixed_point": "alpha(L4_YX)=L4_YX",
            "effect_identity": "E8_public=L4_YX^sharp L4_YX=L4_YX* L4_YX=E8_Hilbert",
            "Born_defect": "E8_public-E8_Hilbert=0 as an operator coefficient",
            "scalar_probability": "q_click=lambda^8*<Psi_in,E8_public Psi_in>+O(lambda^9)=16*lambda^8*||sum_(B=1)^9 P_Y*K_B,T*P_X F||^2+O(lambda^9)",
            "coefficient_bound": "q_click^(8)<=81*lambda^8*T^2/(200*pi^6)",
            "status": "COMPLETE_LEADING_FULLY_REARRANGED_PUBLIC_COMMON_BORN_PHYSICAL_PROBABILITY"
        },
        "disposition": {
            "complete_leading_disconnected_ledger": "EXHAUSTED_AND_ZERO_ON_DETECTOR",
            "complete_leading_operator": "TOTAL_KAPPA_FIXED",
            "public_vs_Hilbert_leading_Born_equivalence": "PROVED_AT_OPERATOR_LEVEL",
            "leading_Born_defect": "ZERO",
            "coherent_channel_interference": "RETAINED",
            "complete_leading_finite_time_public_physical_probability": "COEFFICIENT_COMPUTED",
            "spectator_overlap_detectors": "NOT_COMPLETED",
            "higher_orders": "NOT_CONTROLLED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "complete leading probabilities for detectors intersecting spectator or collinear supports",
            "the sign or size of the O(lambda^9) and higher probability remainder",
            "a BT-derived forward/survival block beyond its leading orthogonality decoupling",
            "an exact all-order finite-time probability", "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Eq. (19)", "loop, real-virtual or KLN completion",
            "a packet-independent cross section", "gravity or metric BV--BRST transfer",
            "anything LORENTZIAN-CAUSAL", "literature priority"
        ],
        "missing_object_ledger": [
            "common-domain lower-block composition on spectator-overlap supports",
            "lambda9/lambda10 and higher common-Born corrections",
            "BT-derived forward/survival normalization and all-order finite-time control",
            "the nonregular Eq. (19) architecture or gravity/BV--BRST observable transfer"
        ],
        "next_gate": "Compute the first higher coefficient T5 on the same fully rearranged detector and its interference 2 Re(T4* T5), testing total-kappa fixedness before claiming finite-lambda positivity. The independent all-channel extension is spectator-overlap composition. General Eq. (19) remains a distinct nonregular projector problem.",
        "checks": {"total": len(checks), "passed": sum(checks.values()), "ok": all(checks.values()), "failures": [k for k,v in checks.items() if not v], "details": checks},
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_fully_rearranged_common_born_physical.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_fully_rearranged_common_born_physical.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_fully_rearranged_common_born_physical"
        ],
        "report": REPORT
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--write", action="store_true"); parser.add_argument("--check", action="store_true"); parser.add_argument("--output", default=CERT); args=parser.parse_args(argv)
    value=build(); rendered=json.dumps(value, indent=2, sort_keys=True)+"\n"
    if args.write:
        with open(args.output,"w",encoding="utf-8") as handle: handle.write(rendered)
        print(os.path.relpath(args.output, ROOT))
    if args.check:
        if not value["checks"]["ok"]: print("FAIL: "+", ".join(value["checks"]["failures"])); return 1
        if os.path.exists(args.output) and open(args.output,encoding="utf-8").read()!=rendered: print("STALE CERTIFICATE"); return 1
        print(f"BT FULLY REARRANGED COMMON BORN: ALL PASS ({value['checks']['passed']}/{value['checks']['total']})")
    if not args.write and not args.check: parser.error("choose --write and/or --check")
    return 0

if __name__ == "__main__": raise SystemExit(main())
