#!/usr/bin/env python3
"""Cyclic all-row analytic realization of the Berger wave prolongation.

The authoritative BV complex remains the 34-row raw complex.  For Green
analysis only, add the scalar prolongation variable ``y`` in degree zero and
its pairing-dual ``y*`` in degree one.  This module constructs the resulting
36-row cyclic operator, the field/source graph SDR, and the formal-adjoint
antifield realization.  No Green operator is asserted here.
"""

from __future__ import annotations

import argparse
import hashlib
import json

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import _matrix_from_record
from d_quotient_classical.backreacted_clock.berger_curved_witness_export import (
    _adjoint_matrix,
    _is_zero,
    _one,
    _record_bytes,
    _sparse_multiply,
    _zero,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT, _matrix_record
from d_quotient_classical.backreacted_clock.berger_raw_clock_reattached_witness_transport import (
    CERTIFICATE_PATH as TRANSPORT_CERTIFICATE,
    _subtract,
)
from d_quotient_classical.backreacted_clock.berger_raw_endpoint_rank_one_wave_extension import (
    CERTIFICATE_PATH as EXTENSION_CERTIFICATE,
)


CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-raw-endpoint-cyclic-green-realization.md"
GENERATED_DIR = ROOT / "d_quotient_classical/generated/berger_raw_endpoint_cyclic_green_realization"
ARTIFACT_PATHS = {
    name: GENERATED_DIR / f"{name}.json"
    for name in (
        "metric_antifield_L13_sharp", "analytic_P36", "analytic_pairing36",
        "field_solution_inclusion", "field_solution_projection",
        "field_source_inclusion", "field_source_projection", "graph_homotopy_H13",
    )
}


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path):
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _load(reference):
    path = ROOT / reference["path"]
    if _sha256(path) != reference["sha256"]:
        raise AssertionError(f"artifact hash mismatch: {path}")
    return _matrix_from_record(json.loads(path.read_text()))


def _identity(rank):
    result = _zero(rank, rank)
    for index in range(rank):
        result[index][index] = _one()
    return result


def _block(matrix, rows, columns):
    return [[matrix[row][column] for column in columns] for row in rows]


def _embed(target, block, row_offset, column_offset):
    for row in range(len(block)):
        for column in range(len(block[0])):
            target[row + row_offset][column + column_offset] = block[row][column]


def _exact_data():
    transport = json.loads(TRANSPORT_CERTIFICATE.read_text())
    extension = json.loads(EXTENSION_CERTIFICATE.read_text())
    p34 = _load(transport["operators"]["P34_raw"])
    artifacts = extension["prolongation"]["artifacts"]
    l13 = _load(artifacts["prolonged_L13"])
    u13 = _load(artifacts["field_shear_U13"])
    e13 = _load(artifacts["equation_shear_E13"])
    identity13 = _identity(13)
    c13 = _subtract(identity13, _subtract(u13, identity13))
    einv13 = _subtract(identity13, _subtract(e13, identity13))
    if not _is_zero(_subtract(_sparse_multiply(u13, c13), identity13)):
        raise AssertionError("field shear inverse failed")
    if not _is_zero(_subtract(_sparse_multiply(e13, einv13), identity13)):
        raise AssertionError("equation shear inverse failed")

    l12 = _block(p34, range(5, 17), range(5, 17))
    direct = _zero(13, 13)
    _embed(direct, l12, 0, 0)
    direct[12][12] = _one()
    if not _is_zero(_subtract(_sparse_multiply(_sparse_multiply(e13, l13), c13), direct)):
        raise AssertionError("13-row direct-sum equivalence failed")

    # Solution graph i(x)=C(x,0), p(x,y)=x.
    i_solution = _zero(13, 12)
    for row in range(13):
        for column in range(12):
            i_solution[row][column] = c13[row][column]
    p_solution = _zero(12, 13)
    for index in range(12):
        p_solution[index][index] = _one()

    # Source graph: inclusion is (f,0), projection is the first twelve rows
    # of E, so the raw modulus source receives Box times the defining source.
    i_source = _zero(13, 12)
    for index in range(12):
        i_source[index][index] = _one()
    p_source = _block(e13, range(0, 12), range(0, 13))

    # H=C P_z E contracts the analytic graph equation.
    pz = _zero(13, 13)
    pz[12][12] = _one()
    homotopy = _sparse_multiply(_sparse_multiply(c13, pz), e13)
    if not _is_zero(_subtract(_sparse_multiply(p_solution, i_solution), _identity(12))):
        raise AssertionError("solution p i failed")
    if not _is_zero(_subtract(_sparse_multiply(p_source, i_source), _identity(12))):
        raise AssertionError("source p i failed")
    if not _is_zero(_subtract(_sparse_multiply(l13, i_solution), _sparse_multiply(i_source, l12))):
        raise AssertionError("solution inclusion does not intertwine")
    if not _is_zero(_subtract(_sparse_multiply(p_source, l13), _sparse_multiply(l12, p_solution))):
        raise AssertionError("source projection does not intertwine")
    field_projector_defect = _subtract(identity13, _sparse_multiply(i_solution, p_solution))
    source_projector_defect = _subtract(identity13, _sparse_multiply(i_source, p_source))
    if not _is_zero(_subtract(field_projector_defect, _sparse_multiply(homotopy, l13))):
        raise AssertionError("field graph homotopy failed")
    if not _is_zero(_subtract(source_projector_defect, _sparse_multiply(l13, homotopy))):
        raise AssertionError("source graph homotopy failed")

    l13_sharp = _adjoint_matrix(l13)
    direct_sharp = _adjoint_matrix(direct)
    # Adjoint of E L C=D is C^sharp L^sharp E^sharp=D^sharp.
    dual_replay = _sparse_multiply(
        _sparse_multiply(_adjoint_matrix(c13), l13_sharp), _adjoint_matrix(e13)
    )
    if not _is_zero(_subtract(dual_replay, direct_sharp)):
        raise AssertionError("formal-adjoint prolongation failed")

    # Analytic row order: ghosts_5, fields_13, antifields_13, identities_5.
    p36 = _zero(36, 36)
    _embed(p36, _block(p34, range(0, 5), range(0, 5)), 0, 0)
    _embed(p36, l13, 5, 5)
    _embed(p36, l13_sharp, 18, 18)
    _embed(p36, _block(p34, range(29, 34), range(29, 34)), 31, 31)
    pairing36 = _zero(36, 36)
    for index in range(5):
        pairing36[index][31 + index] = _one()
        pairing36[31 + index][index] = _one(-1)
    for index in range(13):
        pairing36[5 + index][18 + index] = _one()
        pairing36[18 + index][5 + index] = _one(-1)
    cyclic_defect = _subtract(
        _sparse_multiply(_adjoint_matrix(p36), pairing36),
        _sparse_multiply(pairing36, p36),
    )
    if not _is_zero(cyclic_defect):
        raise AssertionError("analytic P36 is not cyclic/self-adjoint")

    return {
        "transport": transport,
        "extension": extension,
        "l13_sharp": l13_sharp,
        "p36": p36,
        "pairing36": pairing36,
        "i_solution": i_solution,
        "p_solution": p_solution,
        "i_source": i_source,
        "p_source": p_source,
        "homotopy": homotopy,
    }


def _artifact(path, body):
    return {"format": "JSON_EXACT_SPARSE_OPERATOR", "path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(body).hexdigest()}


def build():
    data = _exact_data()
    matrices = {
        "metric_antifield_L13_sharp": data["l13_sharp"],
        "analytic_P36": data["p36"],
        "analytic_pairing36": data["pairing36"],
        "field_solution_inclusion": data["i_solution"],
        "field_solution_projection": data["p_solution"],
        "field_source_inclusion": data["i_source"],
        "field_source_projection": data["p_source"],
        "graph_homotopy_H13": data["homotopy"],
    }
    bodies = {ARTIFACT_PATHS[name]: _record_bytes(_matrix_record(matrix)) for name, matrix in matrices.items()}
    payload = {
        "schema": "pure-weyl-berger-raw-endpoint-cyclic-green-realization-v1",
        "result_id": "BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION",
        "setting_id": data["transport"]["setting_id"],
        "claim_status": "CERTIFIED_CYCLIC_ANALYTIC_REALIZATION_GREEN_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {"raw_witness_transport": _dependency(TRANSPORT_CERTIFICATE), "rank_one_wave_extension": _dependency(EXTENSION_CERTIFICATE)},
        "row_layout": {
            "authoritative_BV_degree_ranks": [5, 12, 12, 5],
            "analytic_realization_degree_ranks": [5, 13, 13, 5],
            "authoritative_BV_total_rows": 34,
            "analytic_total_rows": 36,
            "added_rows": ["degree_0:y", "degree_1:y_star"],
            "added_rows_are_analytic_not_new_cohomology": True,
        },
        "graph_SDR": {
            "solution_identity": "p_sol i_sol=I12",
            "source_identity": "p_src i_src=I12",
            "field_homotopy": "I13-i_sol p_sol=H13 L13",
            "source_homotopy": "I13-i_src p_src=L13 H13",
            "intertwining": ["L13 i_sol=i_src L12", "p_src L13=L12 p_sol"],
            "support_local": True,
            "maximum_map_order": 2,
        },
        "cyclic_realization": {
            "metric_antifield_operator": "L13_sharp",
            "formal_adjoint_reduction": "C13^sharp L13^sharp E13^sharp=(L12 direct_sum I1)^sharp",
            "pairing": "canonical degree-0/degree-1 and ghost/identity pairing on 36 analytic rows",
            "P36_self_adjoint_for_pairing": True,
            "green_adjoint_target": "G13_plus^sharp=G13_minus",
        },
        "causal_policy": {
            "support_categories": ["compact", "spacelike_compact", "smooth"],
            "spatial_zero_mode_projector": False,
            "zero_mode_policy": "massless scalar zero modes are evolved by the causal Cauchy problem; no inverse Laplacian or spatial projector is allowed",
            "conditional_green_formula": "G13_pm=C13 (G12_pm direct_sum I1) E13",
            "conditional_pullback_formula": "G12_pm=p_sol G13_pm i_src",
        },
        "artifacts": {name: _artifact(ARTIFACT_PATHS[name], bodies[ARTIFACT_PATHS[name]]) for name in matrices},
        "exact_checks": {
            "field_and_source_graph_SDR_exact": True,
            "metric_antifield_formal_adjoint_exact": True,
            "analytic_pairing_nondegenerate": True,
            "analytic_P36_cyclic": True,
            "support_local_maps_only": True,
            "original_34_row_BV_complex_unchanged": True,
        },
        "flags": {
            "BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION": True,
            "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS": False,
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
            "BERGER_ARITY_TWO_CAUSAL_D_CARTAN": False,
        },
        "next_gate": "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS",
        "claim_boundary": (
            "This certificate completes the cyclic all-row analytic realization needed to seek Green operators. The y,y* rows are support-local graph variables and do not alter the authoritative 34-row BV cohomology. No advanced/retarded inverse, causal chain homotopy, Hadamard state, or arity-two D-Cartan theorem is claimed."
        ),
    }
    return payload, bodies


def _report():
    return r"""# Cyclic all-row Berger Green realization

The scalar wave prolongation is now paired and all-row.  The authoritative BV
complex remains the 34-row complex with ranks ([5,12,12,5]).  The analytic
Green realization has ranks ([5,13,13,5]), adding (y) and its pairing-dual
(y^*) only for propagation.

Exact solution/source maps and a local graph homotopy prove

\[
p_{\rm sol}i_{\rm sol}=1,
\quad
1-i_{\rm sol}p_{\rm sol}=H_{13}L_{13},
\qquad
1-i_{\rm src}p_{\rm src}=L_{13}H_{13}.
\]

The degree-one block is (L_{13}^\sharp), and the 36-row analytic operator is
self-adjoint for the extended cyclic pairing.  Consequently the future Green
operators must satisfy (G_{13,+}^\sharp=G_{13,-}).

No spatial projector is permitted.  The scalar zero mode is to be handled by
causal Cauchy evolution.  The actual advanced and retarded operators remain
the next gate.
"""


def write():
    payload, bodies = build()
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    for path, body in bodies.items():
        path.write_bytes(body)
    CERTIFICATE_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    REPORT_PATH.write_text(_report())
    return payload


def check():
    payload, bodies = build()
    if CERTIFICATE_PATH.read_text() != json.dumps(payload, indent=2, sort_keys=True) + "\n":
        raise AssertionError("cyclic Green realization certificate drifted")
    if REPORT_PATH.read_text() != _report():
        raise AssertionError("cyclic Green realization report drifted")
    for path, body in bodies.items():
        if path.read_bytes() != body:
            raise AssertionError(f"cyclic Green realization artifact drifted: {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        write()
    print("BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION: PASS")
    print("analytic ranks: [5,13,13,5]")
    print("advanced/retarded operators: OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
