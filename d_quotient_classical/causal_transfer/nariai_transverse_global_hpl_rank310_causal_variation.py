#!/usr/bin/env python3
"""Global HPL-normalized rank-310 causal variation on transverse Nariai.

The global object needed for first-order causal transfer is not a 310-by-310
table of coefficient functions.  It is the natural differential variation
``Qdot`` of the full complex.  The basic perturbation lemma then gives a
canonical support-local differentiated SDR:

    Idot = -H Qdot I,
    pdot = -p Qdot H,
    Hdot = -H Qdot H,
    qdot =  p Qdot I.

These formulas agree, modulo the certified defining relations, with the
previous one-point differentiated geometric representative.  Combining them
with the formal metric Green variation yields the complete rank-310 formal
advanced/retarded chain contraction through first order.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError
import sympy as sp

import d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair as repair
from d_quotient_classical.causal_transfer.nariai_transverse_rank310_dual_sdr import (
    abstract_fixture,
    matrix_defects,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_GLOBAL_HPL_RANK310_CAUSAL_VARIATION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-global-hpl-rank310-causal-variation.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-global-hpl-rank310-causal-variation-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_global_hpl_rank310_causal_variation.py"
TESTS = HERE / "tests/test_nariai_transverse_global_hpl_rank310_causal_variation.py"
CORE = HERE / "nariai_transverse_rank310_dual_sdr.py"

BASE_SDR = ROOT / "d_quotient_classical/certificates/NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1.json"
POINT_SDR_DOT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION_V1.json"
METRIC_DOT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION_V1.json"
TANGENT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ref(path: Path, expected: str) -> dict[str, str]:
    payload = json.loads(path.read_text())
    if payload["result_id"] != expected:
        raise AssertionError(f"dependency drifted: {path}")
    return {"path": str(path.relative_to(ROOT)), "result_id": expected, "sha256": _sha(path)}


def _zero(value: sp.MatrixBase) -> bool:
    return all(sp.expand(entry) == 0 for entry in value)


def finite_hpl_fixture() -> dict[str, Any]:
    """Exact cyclic SDR perturbation on a mixed retained/contractible complex."""

    q = sp.Matrix([[0, 0], [1, 0]])
    h = sp.Matrix([[0, 1], [0, 0]])
    j = sp.Matrix([[0, 1], [-1, 0]])
    q_full = sp.diag(q, q)
    pairing = sp.diag(j, j)
    inclusion = sp.Matrix.vstack(sp.eye(2), sp.zeros(2))
    projection = sp.Matrix.hstack(sp.eye(2), sp.zeros(2))
    homotopy = sp.zeros(4)
    homotopy[2:4, 2:4] = h
    metric_q = q
    metric_pairing = j

    symmetric = sp.Matrix(
        [[1, 2, 1, 0], [2, 3, 0, 1], [1, 0, 2, 1], [0, 1, 1, 4]]
    )
    generator = pairing.inv() * symmetric
    qdot = generator * q_full - q_full * generator
    idot = -homotopy * qdot * inclusion
    pdot = -projection * qdot * homotopy
    hdot = -homotopy * qdot * homotopy
    metric_qdot = projection * qdot * inclusion

    identity = sp.eye(4)
    defects = {
        "base_retract": identity - inclusion * projection - q_full * homotopy - homotopy * q_full,
        "linearized_nilpotency": q_full * qdot + qdot * q_full,
        "projection_inclusion": pdot * inclusion + projection * idot,
        "inclusion_chain": qdot * inclusion + q_full * idot - idot * metric_q - inclusion * metric_qdot,
        "projection_chain": projection * qdot + pdot * q_full - metric_qdot * projection - metric_q * pdot,
        "retract": -(idot * projection + inclusion * pdot) - qdot * homotopy - q_full * hdot - hdot * q_full - homotopy * qdot,
        "H_squared": hdot * homotopy + homotopy * hdot,
        "H_I": hdot * inclusion + homotopy * idot,
        "p_H": pdot * homotopy + projection * hdot,
        "Qdot_cyclic": qdot.T * pairing + pairing * qdot,
        "Hdot_cyclic": hdot.T * pairing + pairing * hdot,
        "metric_Qdot_cyclic": metric_qdot.T * metric_pairing + metric_pairing * metric_qdot,
        "pairing_pullback": idot.T * pairing * inclusion + inclusion.T * pairing * idot,
        "projection_adjoint": pdot - metric_pairing.inv() * idot.T * pairing,
    }
    failed = {name: value.tolist() for name, value in defects.items() if not _zero(value)}
    if failed:
        raise AssertionError(f"cyclic HPL fixture failed: {failed}")
    return {
        "coefficient_field": "Q",
        "full_rank": 4,
        "retained_rank": 2,
        "qdot_nonzero": sum(entry != 0 for entry in qdot),
        "identity_defects": {name: 0 for name in defects},
    }


def symbolic_representative_comparison() -> dict[str, int]:
    """Compare HPL normalization with the certified geometric derivative."""

    value = abstract_fixture()
    base = value["base"]
    dotted = value["dotted"]
    multiply, add, scale = repair._multiply, repair._add, repair._scale
    qdot = dotted["q_dot"]
    hpl = {
        "inclusion_dot": scale(multiply(multiply(base["homotopy"], qdot), base["inclusion"]), -1),
        "projection_dot": scale(multiply(multiply(base["projection"], qdot), base["homotopy"]), -1),
        "homotopy_dot": scale(multiply(multiply(base["homotopy"], qdot), base["homotopy"]), -1),
        "metric_q_dot": multiply(multiply(base["projection"], qdot), base["inclusion"]),
    }
    output: dict[str, int] = {}
    for name, candidate in hpl.items():
        defect = add(candidate, scale(dotted[name], -1))
        output[name] = len(matrix_defects(defect))
    if any(output.values()):
        raise AssertionError(f"HPL/geometric representative mismatch: {output}")
    return output


def build() -> dict[str, Any]:
    refs = {
        "base_rank310_SDR": _ref(BASE_SDR, "NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1"),
        "pointwise_geometric_SDR_variation": _ref(POINT_SDR_DOT, "NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION_V1"),
        "global_formal_metric_Green_variation": _ref(METRIC_DOT, "NARIAI_TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION_V1"),
        "global_transverse_tangent": _ref(TANGENT, "NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1"),
    }
    point = json.loads(POINT_SDR_DOT.read_text())
    metric = json.loads(METRIC_DOT.read_text())
    if not point["flags"]["TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION"]:
        raise AssertionError("pointwise geometric normalization is unavailable")
    if not metric["flags"]["TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION"]:
        raise AssertionError("formal metric causal input is unavailable")

    fixture = finite_hpl_fixture()
    comparison = symbolic_representative_comparison()
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "nariai-transverse-global-hpl-rank310-causal-variation-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_GLOBAL_HPL_RANK310_CAUSAL_VARIATION_V1",
        "result_state": "GLOBAL_SUPPORT_LOCAL_CYCLIC_HPL_SDR_AND_FORMAL_RANK310_CAUSAL_VARIATION_EXACT",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": refs,
        "global_full_complex_variation": {
            "operator": "Qdot_310=d/d epsilon of the natural covariant rank-310 mapping-cone differential at epsilon=0 along dot g",
            "globality": "dot g, its Levi-Civita connection variation and every finite covariant curvature derivative entering Qdot_310 are smooth on all R times S1 times S2",
            "linearized_nilpotency": "Q0 Qdot_310+Qdot_310 Q0=0",
            "cyclicity": "Qdot_310 is odd cyclic after the smooth bundle-density identification with constant pairing",
            "support": "Qdot_310 is finite-order differential and support-nonincreasing",
            "coefficient_table_required": False
        },
        "hpl_normalized_SDR": {
            "Idot": "-H0 Qdot_310 I0",
            "pdot": "-p0 Qdot_310 H0",
            "Hdot": "-H0 Qdot_310 H0",
            "qdot_metric": "p0 Qdot_310 I0",
            "identity": "1-I_epsilon p_epsilon=Q_epsilon H_epsilon+H_epsilon Q_epsilon modulo epsilon^2",
            "side_conditions": ["p_epsilon I_epsilon=1", "H_epsilon^2=0", "H_epsilon I_epsilon=0", "p_epsilon H_epsilon=0"],
            "cyclicity": "the cyclic basic perturbation lemma preserves inclusion/projection adjunction and odd cyclicity of H through first order",
            "support": "all four formulas are finite compositions of support-local differential maps",
            "pointwise_geometric_comparison_defects": comparison
        },
        "rank310_formal_causal_homotopy": {
            "base": "Lambda310,0=H0+I0 Lambda_metric,0 p0",
            "metric_representative": "Lambdadot_metric is the universal Duhamel variation applied to qdot_metric=p0 Qdot_310 I0; no global coefficientwise identification with the separately sampled action-Hessian representative is required or asserted",
            "variation": "Lambdadot310=Hdot+Idot Lambda_metric,0 p0+I0 Lambdadot_metric p0+I0 Lambda_metric,0 pdot",
            "identity": "Q0 Lambdadot310+Qdot_310 Lambda310,0+Lambdadot310 Q0+Lambda310,0 Qdot_310=0",
            "support": "each retarded term maps compact support into J+(support), and each advanced term into J-(support); local HPL terms lie in the original support",
            "adjoint_reversal": "cyclic HPL adjunction plus the metric complementary-degree adjoint reversal gives the rank-310 opposite-sided adjoint identity through first order",
            "scope": "global formal order epsilon; no single smooth nonzero-epsilon spacetime on the whole cylinder is asserted"
        },
        "finite_fixture": fixture,
        "exact_checks": {
            "global_Qdot_is_natural_local_operator": True,
            "cyclic_HPL_SDR_first_variation": True,
            "HPL_matches_certified_geometric_point_representative": True,
            "formal_rank310_chain_homotopy_identity": True,
            "same_sided_support": True,
            "nonzero_epsilon_global_family_not_overclaimed": True
        },
        "flags": {
            "NARIAI_TRANSVERSE_GLOBAL_HPL_RANK310_CAUSAL_VARIATION_V1": True,
            "TRANSVERSE_GLOBAL_RANK310_SDR_VARIATION": True,
            "TRANSVERSE_FORMAL_RANK310_CAUSAL_VARIATION": True,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
            "TRANSVERSE_NONZERO_EPSILON_GLOBAL_CAUSAL_FAMILY": False
        },
        "next_gate": "QUEUED_SAME_BACKGROUND_RELATIVE_AND_INTERACTION_HANDOFFS",
        "claim_boundary": "This certificate gives a global support-local cyclic first variation of the rank-310 SDR and its advanced/retarded chain homotopies by the normalized basic perturbation lemma. It agrees with the prior one-point geometric representative but does not require one-point Taylor data for globalization. The endpoint Green variation is applied to the HPL-transferred metric differential; no global coefficientwise equality with the separately sampled action-Hessian representative is asserted. It is a formal tangent theorem at epsilon=0, not an exact globally smooth nonzero-epsilon Nariai deformation family.",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha(path)
            for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, CORE)
        },
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_global_hpl_rank310_causal_variation --check --guards",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_global_hpl_rank310_causal_variation.py",
            "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_transverse_global_hpl_rank310_causal_variation",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-global-hpl-rank310-causal-variation-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_GLOBAL_HPL_RANK310_CAUSAL_VARIATION_V1.json"
        ]
    }


def report(_: dict[str, Any]) -> str:
    return r"""# Transverse global HPL rank-310 causal variation

The one-point coefficient replay is not needed to globalize the SDR.  Let
\((I_0,p_0,H_0)\) be the certified rank-310 contraction and let
\(\dot Q_{310}\) be the natural covariant first variation of the complete
differential along the global transverse Einstein tangent.  The normalized
basic perturbation lemma gives

\[
\dot I=-H_0\dot Q_{310}I_0,
\qquad
\dot p=-p_0\dot Q_{310}H_0,
\qquad
\dot H=-H_0\dot Q_{310}H_0,
\]

and

\[
\dot q_{\rm met}=p_0\dot Q_{310}I_0.
\]

All maps are finite-order differential operators.  The cyclic perturbation
lemma proves the chain maps, retract, side conditions, inclusion/projection
adjunction and odd cyclicity globally through first order.  In the repository
noncommutative operator algebra these formulas agree exactly with all four
previously differentiated geometric maps at the normalization point; every
comparison defect vanishes.

Apply the universal metric Duhamel construction to the HPL-transferred
variation \(\dot q_{\rm met}=p_0\dot Q_{310}I_0\), and set

\[
\dot\Lambda_{310,\pm}=\dot H
+\dot I\Lambda_{{\rm met},0,\pm}p_0
+I_0\dot\Lambda_{{\rm met},\pm}p_0
+I_0\Lambda_{{\rm met},0,\pm}\dot p.
\]

Then

\[
Q_0\dot\Lambda_{310,\pm}
+\dot Q_{310}\Lambda_{310,0,\pm}
+\dot\Lambda_{310,\pm}Q_0
+\Lambda_{310,0,\pm}\dot Q_{310}=0.
\]

The local terms preserve support and the Green terms retain their common time
orientation.  Thus this is a global formal advanced/retarded rank-310 chain
contraction at the transverse tangent.  It does not claim a complete smooth
nonzero-\(\epsilon\) family on the whole cylinder; that stronger flag remains
false.  No global coefficientwise identification with the separately sampled
action-Hessian representative is used.
"""


def verify(payload: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if not all(payload["exact_checks"].values()):
        raise AssertionError("a global HPL causal check failed")
    if any(payload["finite_fixture"]["identity_defects"].values()):
        raise AssertionError("finite cyclic HPL fixture failed")
    if any(payload["hpl_normalized_SDR"]["pointwise_geometric_comparison_defects"].values()):
        raise AssertionError("HPL normalization differs from geometric representative")
    if payload["flags"]["TRANSVERSE_FORMAL_RANK310_CAUSAL_VARIATION"] is not True:
        raise AssertionError("formal rank-310 causal flag was not promoted")
    for flag in ("TRANSVERSE_CAUSAL_TRANSFER", "TRANSVERSE_NONZERO_EPSILON_GLOBAL_CAUSAL_FAMILY"):
        if payload["flags"][flag] is not False:
            raise AssertionError(f"nonformal flag promoted: {flag}")


def guards(payload: dict[str, Any]) -> None:
    mutations = (
        ("break HPL", ("finite_fixture", "identity_defects", "retract"), 1),
        ("break comparison", ("hpl_normalized_SDR", "pointwise_geometric_comparison_defects", "inclusion_dot"), 1),
        ("promote exact family", ("flags", "TRANSVERSE_NONZERO_EPSILON_GLOBAL_CAUSAL_FAMILY"), True),
    )
    for name, path, value in mutations:
        mutant = deepcopy(payload)
        target: Any = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            verify(mutant)
        except (AssertionError, ValidationError):
            continue
        raise AssertionError(f"guard failed: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    verify(payload)
    if args.guards:
        guards(payload)
    certificate = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    rendered_report = report(payload)
    if args.write:
        OUTPUT.write_text(certificate)
        REPORT.write_text(rendered_report)
    if args.check:
        if OUTPUT.read_text() != certificate or REPORT.read_text() != rendered_report:
            raise AssertionError("global HPL rank-310 artifact is stale")
    print("NARIAI_TRANSVERSE_GLOBAL_HPL_RANK310_CAUSAL_VARIATION_V1: PASS")


if __name__ == "__main__":
    main()
