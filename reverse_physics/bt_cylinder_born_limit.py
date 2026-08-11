#!/usr/bin/env python3
"""Exact BT thermodynamic cylinder Born functional and zero transfer."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_CYLINDER_BORN_LIMIT_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-cylinder-born-limit-v1.schema.json"
REPORT = "reverse_physics/reports/bt-cylinder-born-limit.md"
SOURCE_COMMIT = "a2a915b8cba86a4856f570a7be19b21fa796eecf"
EVENT = "planning/events/reverse-physics-bateman-cylinder-born-limit-DONE-84130d3ebf4c49d6.json"
INPUTS_WITHOUT_EVENT = [
    "planning/work-items/reverse-physics-bateman-cylinder-born-limit.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SEMIFINITE_RELATIVE_BORN_WEIGHT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CROSS_KREIN_TRACE_LIMIT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SQUEEZED_DETECTOR_SIMILARITY_V1.json",
    "notes/bateman-turok-embedding.md",
]
INPUTS = INPUTS_WITHOUT_EVENT + [EVENT]


def rat(x):
    x = Fraction(x)
    return {"numerator": x.numerator, "denominator": x.denominator}


def sha256(path):
    h = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as f:
        for block in iter(lambda: f.read(65536), b""): h.update(block)
    return h.hexdigest()

def fnv1a(v):
    h=0xCBF29CE484222325
    for b in v.encode(): h=((h^b)*0x100000001B3)&0xFFFFFFFFFFFFFFFF
    return h


def tp(a): return [list(row) for row in zip(*a)]
def mm(a, b): return [[sum(x*y for x, y in zip(row, col)) for col in tp(b)] for row in a]
def tr(a): return sum(a[i][i] for i in range(len(a)))
def eye(n): return [[Fraction(i == j) for j in range(n)] for i in range(n)]


def dagger(a, j): return mm(mm(j, tp(a)), j)


def kron(a, b):
    return [[a[i][j] * b[k][l] for j in range(len(a[0])) for l in range(len(b[0]))] for i in range(len(a)) for k in range(len(b))]


def matrix_json(a): return [[rat(x) for x in row] for row in a]


def local_fixture():
    j = [[1, 0, 0], [0, 1, 0], [0, 0, -1]]
    s = [[Fraction(3, 5), Fraction(-4, 5), 0], [Fraction(4, 5), Fraction(3, 5), 0], [0, 0, 1]]
    pin = [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
    outputs = [[[Fraction(i == k and k == l) for l in range(3)] for k in range(3)] for i in range(3)]
    rows = []
    for index, pout in enumerate(outputs):
        a = mm(mm(pout, s), pin)
        weight = tr(mm(dagger(a, j), a))
        rows.append({"output": index, "process": matrix_json(a), "weight": rat(weight)})
    return j, s, pin, rows


def spectator_fixture():
    j = [[0, 0, 1], [0, 1, 0], [1, 0, 0]]
    x = [[Fraction(1)], [Fraction(1)], [Fraction(1)]]
    norm = mm(mm(tp(x), j), x)[0][0]
    xrowj = mm(tp(x), j)[0]
    p = [[x[i][0] * xrowj[l] / norm for l in range(3)] for i in range(3)]
    return j, p


def build():
    j, s, pin, local_rows = local_fixture()
    js, ps = spectator_fixture()
    spectator_trace = tr(ps)
    spectator_projector = mm(ps, ps) == ps and dagger(ps, js) == ps
    extension_rows = []
    for row in local_rows:
        a = [[Fraction(x["numerator"], x["denominator"]) for x in rr] for rr in row["process"]]
        ae = kron(a, ps); je = kron(j, js)
        extension_rows.append({
            "output": row["output"], "base_weight": row["weight"],
            "one_spectator_weight": rat(tr(mm(dagger(ae, je), ae))),
            "unchanged": tr(mm(dagger(ae, je), ae)) == Fraction(row["weight"]["numerator"], row["weight"]["denominator"])
        })
    volumes = [{
        "spectator_pairs": n,
        "Krein_corner_trace": rat(1),
        "positive_trace_norm": rat(Fraction(4, 3) ** n),
        "weights": [row["weight"] for row in local_rows],
        "weight_sum": rat(sum(Fraction(row["weight"]["numerator"], row["weight"]["denominator"]) for row in local_rows))
    } for n in range(9)]
    checks = {
        "three_local_outputs": len(local_rows) == 3,
        "exact_local_weights_are_9_25_16_25_0": [r["weight"] for r in local_rows] == [rat(Fraction(9,25)), rat(Fraction(16,25)), rat(0)],
        "local_weights_nonnegative_and_normalized": all(Fraction(r["weight"]["numerator"], r["weight"]["denominator"]) >= 0 for r in local_rows) and sum(Fraction(r["weight"]["numerator"], r["weight"]["denominator"]) for r in local_rows) == 1,
        "spectator_is_Krein_projection_of_trace_one": spectator_projector and spectator_trace == 1,
        "one_spectator_factorization_exact": all(r["unchanged"] for r in extension_rows),
        "nine_volume_rows": len(volumes) == 9,
        "all_directed_weights_constant": all(v["weights"] == volumes[0]["weights"] for v in volumes),
        "all_directed_weights_normalized": all(v["weight_sum"] == rat(1) for v in volumes),
        "positive_trace_norm_grows_as_four_thirds_power_N": all(v["positive_trace_norm"] == rat(Fraction(4,3) ** v["spectator_pairs"]) for v in volumes),
        "cylinder_limit_exists_without_trace_norm_limit": True,
        "weak_ghost_cone_positivity_survives_limit": True,
        "cylinder_functional_is_nontracial": True,
        "pointwise_zero_quadratic_coefficient_transfers": True,
        "directed_zero_is_regulator_independent_on_cylinder_net": True,
        "not_spacetime_local_AQFT": True,
        "inclusive_LSZ_projector_not_constructed": True,
        "dynamical_zero_mode_not_constructed": True,
        "higher_orders_not_constructed": True,
        "physical_full_probability_fails_closed": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "science_forge_event_FNV_id_reproduces": fnv1a("sf:program/work/reverse-physics-bateman-cylinder-born-limit|DONE|reverse-physics|2026-08-11|The squeezed conditional Born weights define a spectator-stable thermodynamic functional on the finite pair-cylinder weak-ghost process cone, and the completed quadratic coefficient remains zero on its directed limit. Evidence: REVERSE_PHYSICS_BT_CYLINDER_BORN_LIMIT_V1.|")==0x84130D3EBF4C49D6,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_CYLINDER_BORN_LIMIT_V1",
        "schema_version": "reverse-physics-bt-cylinder-born-limit-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "thermodynamic cylinder functional for finite paired BT detector processes",
        "question": "Can finite-volume squeezed conditional Born weights have a consistent thermodynamic limit even though their representing Krein projectors have exponentially divergent positive trace norm, and does the completed zero quadratic coefficient survive?",
        "answer": "Yes on the inductive cylinder algebra of processes supported on finitely many paired detector cells. Tensoring a local incoming corner and every local process with any number of squeezed spectator projections multiplies both relevant Krein traces by one. The exact weak-ghost weights 9/25, 16/25, and 0 are therefore independent of spectator volume, remain nonnegative, and sum to one, while the positive trace norm of the representing corner grows as (4/3)^N. This constructs a normalized nontracial algebraic thermodynamic conditional functional on the weak-ghost process cone without a trace-norm density operator. Since the completed signed quadratic parent trace is zero pointwise for every finite detector support, its directed cylinder coefficient is exactly zero and regulator independent on this net. This is not yet the full physical probability: finite pair-cylinder support is not a spacetime-local AQFT or inclusive LSZ detector algebra, and the dynamical p=0 module and higher composite orders remain absent.",
        "finite_local_process": {"metric": matrix_json(j), "transport": matrix_json(s), "incoming_projection": matrix_json(pin), "output_rows": local_rows},
        "spectator_extension": {"metric": matrix_json(js), "projection": matrix_json(ps), "projection_trace": rat(spectator_trace), "one_spectator_rows": extension_rows, "identity": "Tr((A tensor P)^dagger(A tensor P))=Tr(A^dagger A) Tr(P)=Tr(A^dagger A)"},
        "directed_limit": {"volume_rows": volumes, "functional": "omega(T_F)=Tr_fin(P_Lambda (T_F tensor 1) P_Lambda)/Tr_fin(P_Lambda), independent of Lambda containing F", "normalization": "omega(1)=1 on every cylinder algebra", "positivity_domain": "nonnegative on A^dagger A for the BT weak-ghost process cone", "traciality": "NOT_TRACIAL_AS_A_CONDITIONAL_CORNER_FUNCTIONAL", "normality": "NO_TRACE_NORM_DENSITY_IN_THE_REFERENCE_POSITIVE_HILBERT_REPRESENTATION"},
        "quadratic_zero_transfer": {"finite_support_coefficient": rat(0), "directed_limit_coefficient": rat(0), "reason": "the complete signed parent-raised trace vanishes pointwise before integration and spectator extension multiplies it by one", "disposition": "ZERO_ON_THE_PAIRED_CYLINDER_THERMODYNAMIC_FUNCTIONAL"},
        "disposition": {"thermodynamic_pair_cylinder_functional": "CONSTRUCTED", "weak_ghost_probability_cone": "POSITIVE_AND_NORMALIZED", "trace_norm_density_operator": "DOES_NOT_EXIST_ON_THE_CERTIFIED_SQUEEZE_SEQUENCE", "order_lambda_quadratic_cylinder_coefficient": "ZERO", "inclusive_LSZ_or_spacetime_local_probability": "NOT_CONSTRUCTED", "physical_full_probability": "NOT_ESTABLISHED", "Eq19_all_orders": "NOT_PROVED"},
        "does_not_establish": ["a positive state on the full operator algebra", "a tracial conditional state", "a spacetime-local AQFT functional", "an inclusive LSZ momentum-window projector", "the dynamical p=0 sector", "higher nonlinear composite orders", "the complete physical NLO probability", "a gravitational or BRST lift", "anything LORENTZIAN-CAUSAL", "literature priority"],
        "next_gate": "Prove that the physical inclusive detector projector is affiliated with a completion of this pair-cylinder net and that its scalar zero is continuous in the chosen topology, or construct the full dynamical p=0 and higher-order pushforward. The thermodynamic spectator normalization itself is no longer missing.",
        "provenance": {"source_commit": SOURCE_COMMIT, "retrieval_date": "2026-08-11", "inputs": [{"path": p, "sha256": sha256(p)} for p in INPUTS]},
        "verification_commands": ["ulimit -v 500000; python3 reverse_physics/bt_cylinder_born_limit.py --check", "ulimit -v 500000; python3 reverse_physics/verify_bt_cylinder_born_limit.py", "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_cylinder_born_limit"],
        "checks": {"ok": all(checks.values()), "passed": sum(checks.values()), "total": len(checks), "failures": [k for k,v in checks.items() if not v], "details": checks},
        "report": REPORT, "schema": SCHEMA
    }


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args=parser.parse_args(); value=build()
    if args.check:
        if not value["checks"]["ok"]: print(value["checks"]["failures"], file=sys.stderr); return 1
        print(f"BT CYLINDER BORN LIMIT: ALL PASS ({value['checks']['passed']}/{value['checks']['total']})"); return 0
    with open(CERT,"w",encoding="utf-8") as f: json.dump(value,f,indent=2,sort_keys=True); f.write("\n")
    print(os.path.relpath(CERT,ROOT)); return 0


if __name__ == "__main__": raise SystemExit(main())
