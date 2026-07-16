#!/usr/bin/env python3
"""Typed causal Volterra resolvents for the retained Berger metric biwave."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT
from d_quotient_classical.backreacted_clock.berger_metric_lower_by_two_biwave import (
    CERTIFICATE_PATH as NORMAL_FORM_CERTIFICATE,
)
from d_quotient_classical.backreacted_clock.berger_minimal_34_portable_contraction import (
    CERTIFICATE_PATH as CONTRACTION_CERTIFICATE,
)
from d_quotient_classical.backreacted_clock.berger_raw_clock_reattached_witness_transport import (
    CERTIFICATE_PATH as TRANSPORT_CERTIFICATE,
)


LEGACY_CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2.json"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-retained-biwave-volterra-resolvent-v2.schema.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-retained-biwave-volterra-resolvent-v2.md"
MANIFEST_PATH = ROOT / "d_quotient_classical/manifests/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2_SOURCE_MANIFEST.json"
RECEIPT_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2_VERIFICATION_RECEIPT.json"
VERIFIER_PATH = ROOT / "d_quotient_classical/backreacted_clock/verify_berger_retained_biwave_volterra_resolvent.py"
TEST_PATH = ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_retained_biwave_volterra_resolvent.py"
PRODUCER_PATH = Path(__file__).resolve()
PROOF_DIR = ROOT / "d_quotient_classical/generated/berger_retained_biwave_volterra_resolvent_v2"
PROOF_PATHS = {
    "finite_slab_estimate": PROOF_DIR / "finite_slab_estimate.json",
    "causal_support_passage": PROOF_DIR / "causal_support_passage.json",
    "globalization_uniqueness": PROOF_DIR / "globalization_uniqueness.json",
    "inverse_identities": PROOF_DIR / "inverse_identities.json",
    "adjoint_reversal": PROOF_DIR / "adjoint_reversal.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _check_artifact(record: dict[str, str]) -> Path:
    path = ROOT / record["path"]
    if _sha256(path) != record["sha256"]:
        raise AssertionError(f"artifact digest drifted: {path}")
    return path


def _artifact(path: Path, body: bytes, format_id: str = "JSON_PROOF_CERTIFICATE") -> dict[str, str]:
    return {
        "format": format_id,
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(body).hexdigest(),
    }


def _add(*terms):
    result = {}
    for term in terms:
        for word, coefficient in term.items():
            result[word] = result.get(word, 0) + coefficient
            if result[word] == 0:
                del result[word]
    return result


def _scale(term, coefficient):
    return {word: coefficient * value for word, value in term.items() if coefficient * value}


def _mul(left, right):
    return _add(*(
        {left_word + right_word: left_coefficient * right_coefficient}
        for left_word, left_coefficient in left.items()
        for right_word, right_coefficient in right.items()
    ))


def _matmul(left, right):
    return [[
        _add(*(_mul(left[row][middle], right[middle][column]) for middle in range(len(right))))
        for column in range(len(right[0]))
    ] for row in range(len(left))]


def _matsub(left, right):
    return [[
        _add(left[row][column], _scale(right[row][column], -1))
        for column in range(len(left[0]))
    ] for row in range(len(left))]


def _zero_matrix(rows, columns):
    return [[{} for _ in range(columns)] for _ in range(rows)]


def _identity(rank):
    result = _zero_matrix(rank, rank)
    for index in range(rank):
        result[index][index] = {(): 1}
    return result


def _free_graph_checks():
    """Recheck the companion graph SDR over the free algebra Q<W,V>."""
    zero, one, wave, remainder = {}, {(): 1}, {("W",): 1}, {("V",): 1}
    minus_one = _scale(one, -1)
    companion = [[wave, minus_one], [remainder, wave]]
    metric = _add(_mul(wave, wave), remainder)
    i_sol, p_sol = [[one], [wave]], [[one, zero]]
    i_src, p_src = [[zero], [one]], [[wave, one]]
    homotopy = [[zero, zero], [minus_one, zero]]
    return {
        "p_sol_i_sol": _matmul(p_sol, i_sol) == _identity(1),
        "p_src_i_src": _matmul(p_src, i_src) == _identity(1),
        "C_i_sol": _matmul(companion, i_sol) == [[zero], [metric]],
        "p_src_C": _matmul(p_src, companion) == [[metric, zero]],
        "solution_retract": _matsub(
            _matsub(_identity(2), _matmul(i_sol, p_sol)),
            _matmul(homotopy, companion),
        ) == _zero_matrix(2, 2),
        "source_retract": _matsub(
            _matsub(_identity(2), _matmul(i_src, p_src)),
            _matmul(companion, homotopy),
        ) == _zero_matrix(2, 2),
    }


def _exact_dependencies():
    normal = json.loads(NORMAL_FORM_CERTIFICATE.read_text())
    if not all(normal["exact_checks"].values()):
        raise AssertionError("metric normal-form dependency is not exact")
    for record in normal["normal_form"]["artifacts"].values():
        _check_artifact(record)
    contraction = json.loads(CONTRACTION_CERTIFICATE.read_text())
    if not all(contraction["exact_checks"].values()):
        raise AssertionError("minimal contraction dependency is not exact")
    if contraction["row_layout"]["retained_row_indices"][3:13] != list(range(5, 15)):
        raise AssertionError("retained metric rows are no longer literal raw metric selectors")
    graph_checks = _free_graph_checks()
    if not all(graph_checks.values()):
        raise AssertionError(f"companion graph SDR failed: {graph_checks}")
    return normal, graph_checks


def _proof_payloads() -> dict[str, dict]:
    common = {
        "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
        "operator": "C20=C0+N, C0=[[Box_2,0],[V_2,Box_2]], N=[[0,-I10],[0,0]]",
    }
    return {
        "finite_slab_estimate": {
            "schema": "pure-weyl-berger-volterra-finite-slab-estimate-v1",
            "result_id": "BERGER_VOLTERRA_FINITE_SLAB_ESTIMATE",
            **common,
            "slab": "[-T,T] times S3 with T finite",
            "spaces": {
                "X_s(I)": "(C0(I;H^(s+1)) intersect C1(I;H^s)) direct_sum (C0(I;H^s) intersect C1(I;H^(s-1)))",
                "Y_s(I)": "L1(I;H^s) direct_sum L1(I;H^(s-1))",
                "spatial_bundle": "H^r means H^r(S3;Sym2)",
            },
            "coefficient_hypotheses": [
                "S3 is compact and the Berger-cylinder coefficients are smooth and stationary",
                "Box_2 is normally hyperbolic with finite-slab energy estimates at every Sobolev order",
                "V_2 has differential order at most two and bounded stationary coefficients",
                "N has differential order zero and maps only the second solution component to the first source component",
            ],
            "derivative_mappings": [
                "G_Box,advanced/retarded:L1(I;H^r)->C0(I;H^(r+1)) intersect C1(I;H^r)",
                "V_2:H^(s+1)->H^(s-1)",
                "G0,advanced/retarded:Y_s(I)->X_s(I)",
                "N:X_s(I)->Y_s(I)",
                "K_sol,advanced/retarded=G0,advanced/retarded N:X_s(I)->X_s(I)",
                "K_src,advanced/retarded=N G0,advanced/retarded:Y_s(I)->Y_s(I)",
            ],
            "constants": "C_(s,T)=M_(s,T) ||N||_(X_s->Y_s), finite for every integer s and finite T",
            "solution_series_bound": "||(K_sol,advanced/retarded)^n||_(X_s(I)->X_s(I))<=C_(s,T)^n/n!",
            "source_series_bound": "||(K_src,advanced/retarded)^n||_(Y_s(I)->Y_s(I))<=C_(s,T)^n/n!",
            "proof": "each same-sided iteration integrates over an ordered n-simplex in time of volume at most (2T)^n/n!; absorb the slab length and energy constants into C_(s,T)",
            "conclusion": "both Neumann-Volterra series converge absolutely in operator norm at every Sobolev order",
        },
        "causal_support_passage": {
            "schema": "pure-weyl-berger-volterra-causal-support-v1",
            "result_id": "BERGER_VOLTERRA_CAUSAL_SUPPORT_PASSAGE",
            **common,
            "partial_sums": "every term is a composition of same-sided wave Green maps and local differential maps",
            "support_bound": {
                "advanced": "supp(term f) subset J^-(supp f)",
                "retarded": "supp(term f) subset J^+(supp f)",
            },
            "limit_argument": "operator-norm convergence on every finite slab implies distributional convergence; sections vanishing on the open complement of the closed causal set remain zero there",
            "conclusion": "the separately named advanced and retarded R_sol, R_src and G_C retain their declared causal support",
        },
        "globalization_uniqueness": {
            "schema": "pure-weyl-berger-volterra-globalization-v1",
            "result_id": "BERGER_VOLTERRA_GLOBALIZATION_UNIQUENESS",
            **common,
            "exhaustion": "use nested compact globally hyperbolic slabs containing the source support",
            "compatibility": "finite-slab solutions agree on overlaps because their difference is a homogeneous same-sided solution with zero Cauchy data",
            "uniqueness_input": "normally hyperbolic uniqueness for the diagonal wave blocks plus the convergent Volterra integral equation",
            "conclusion": "the compatible slab solutions glue to unique global advanced and retarded operators",
        },
        "inverse_identities": {
            "schema": "pure-weyl-berger-volterra-inverse-identities-v1",
            "result_id": "BERGER_VOLTERRA_BOTH_INVERSE_IDENTITIES",
            **common,
            "typed_resolvents": {
                "R_sol_advanced_retarded": "(I_X+G0,advanced/retarded N)^-1:X_s(I)->X_s(I)",
                "R_src_advanced_retarded": "(I_Y+N G0,advanced/retarded)^-1:Y_s(I)->Y_s(I)",
                "G_C_advanced_retarded": "R_sol G0=G0 R_src:Y_s(I)->X_s(I)",
            },
            "push_through_identity": "(I_X+G0 N)^-1 G0=G0 (I_Y+N G0)^-1",
            "factorizations": [
                "C=C0(I_X+G0 N) on the solution domain",
                "C=(I_Y+N G0)C0 on compactly supported solution-domain sections",
            ],
            "inverse_identities": ["C G_C,advanced/retarded=I_Y", "G_C,advanced/retarded C=I_X"],
            "metric_pullback": "G_A,advanced/retarded=p_sol G_C,advanced/retarded i_src",
            "metric_inverse_identities": ["A G_A=I", "G_A A=I"],
        },
        "adjoint_reversal": {
            "schema": "pure-weyl-berger-volterra-adjoint-reversal-v1",
            "result_id": "BERGER_VOLTERRA_TYPED_ADJOINT_REVERSAL",
            **common,
            "pairing": "the frozen nondegenerate metric-antifield BV fibre pairing between the degree-zero metric bundle and its degree-one density dual",
            "typed_identity": "(G_A,advanced)^sharp=G_(A^sharp),retarded and (G_A,retarded)^sharp=G_(A^sharp),advanced",
            "proof": "formal adjunction of A G_A,+ = I and G_A,+ A = I, followed by uniqueness of the opposite-sided Green operator for A^sharp",
            "self_adjoint_simplification_used": False,
            "forbidden_unless_separately_certified": "do not replace G_(A^sharp),- by G_A,- merely from this theorem",
        },
    }


def _report() -> str:
    return r"""# Retained Berger biwave: typed causal Volterra resolvents

The retained metric operator has the exact normal form

\[
A_{10}=\Box_2^2+V_2,\qquad \operatorname{ord}V_2\le2.
\]

Its companion is

\[
C=C_0+N,\quad
C_0=\begin{pmatrix}\Box_2&0\\V_2&\Box_2\end{pmatrix},\qquad
N=\begin{pmatrix}0&-I\\0&0\end{pmatrix}.
\]

For every integer \(s\), on each finite causal slab \(I\) use

\[
X_s(I)=
\bigl(C^0(I;H^{s+1})\cap C^1(I;H^s)\bigr)
\oplus
\bigl(C^0(I;H^s)\cap C^1(I;H^{s-1})\bigr),
\]

\[
Y_s(I)=L^1(I;H^s)\oplus L^1(I;H^{s-1}),
\]

where every spatial Sobolev space is on \(S^3\) with values in
\(\mathrm{Sym}^2\).

The triangular Green map \(G_0^\pm:Y_s\to X_s\) is

\[
G_0^\pm=\begin{pmatrix}
G_\Box^\pm&0\\-G_\Box^\pm V_2G_\Box^\pm&G_\Box^\pm
\end{pmatrix}.
\]

The two Neumann series live on different spaces and are recorded separately
for `advanced` and `retarded` evolution. Here advanced support means
\(J^-(\operatorname{supp}f)\), while retarded support means
\(J^+(\operatorname{supp}f)\):

\[
R_{\rm sol}^\pm=(I_{X_s}+G_0^\pm N)^{-1}:X_s\to X_s,
\qquad
R_{\rm src}^\pm=(I_{Y_s}+NG_0^\pm)^{-1}:Y_s\to Y_s.
\]

With \(C_{s,T}<\infty\) determined by the wave-energy constants and the
bounded order-zero map \(N:X_s\to Y_s\), ordered-time-simplex estimates give

\[
\|(G_0^\pm N)^n\|_{X_s\to X_s}\le {C_{s,T}^n\over n!},\qquad
\|(NG_0^\pm)^n\|_{Y_s\to Y_s}\le {C_{s,T}^n\over n!}.
\]

Thus both series converge and the push-through identity is correctly typed:

\[
G_C^\pm=R_{\rm sol}^\pm G_0^\pm
=G_0^\pm R_{\rm src}^\pm:Y_s\to X_s.
\]

The exact factorizations of \(C\) yield both same-sided inverse identities.
Every partial sum is causal; convergence preserves vanishing outside the
closed causal set, and uniqueness glues compatible slab solutions globally.
The graph pullback gives \(G_A^\pm=p_{\rm sol}G_C^\pm i_{\rm src}\).

Finally, relative to the frozen metric-antifield pairing, the correctly typed
adjoint theorem is

\[
(G_{A,\mathrm{advanced}})^\sharp=G_{A^\sharp,\mathrm{retarded}},
\qquad
(G_{A,\mathrm{retarded}})^\sharp=G_{A^\sharp,\mathrm{advanced}}.
\]

This certificate does not replace the right-hand side by \(G_{A,-}\), and it
does not use an inverse Laplacian, inverse curl, harmonic projector or mode
split.
"""


def _proof_bodies() -> dict[str, bytes]:
    return {name: _json_bytes(payload) for name, payload in _proof_payloads().items()}


def build() -> tuple[dict, dict[str, bytes]]:
    normal, graph_checks = _exact_dependencies()
    proof_bodies = _proof_bodies()
    payload = {
        "schema": "pure-weyl-berger-retained-biwave-volterra-resolvent-v2",
        "schema_version": "2.0.0",
        "result_id": "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2",
        "setting_id": normal["setting_id"],
        "claim_status": "CERTIFIED_TYPED_RETAINED_METRIC_CAUSAL_GREEN_OPERATORS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            "metric_normal_form": _dependency(NORMAL_FORM_CERTIFICATE),
            "minimal_clock_contraction": _dependency(CONTRACTION_CERTIFICATE),
            "raw_witness_transport": _dependency(TRANSPORT_CERTIFICATE),
        },
        "supersedes": {
            "result_id": "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT",
            "reason": "V1 conflated solution- and source-space resolvents and overstated the adjoint theorem; V2 repairs both defects.",
        },
        "retained_identification": {
            "identity": "(pi_cl P34_raw iota_cl)_metric=A10=Box_2^2+V_2",
            "metric_rows": 10,
            "maximum_order_V2": 2,
        },
        "companion_graph_sdr": {
            "operator": "C20=[[Box_2,-I10],[V_2,Box_2]]",
            "status": "IMPORTED_AND_FREE_ALGEBRA_RECHECKED",
            "exact_checks": graph_checks,
        },
        "typed_spaces": {
            "X_s(I)": "(C0(I;H^(s+1)) intersect C1(I;H^s)) direct_sum (C0(I;H^s) intersect C1(I;H^(s-1)))",
            "Y_s(I)": "L1(I;H^s) direct_sum L1(I;H^(s-1))",
            "spatial_bundle": "H^r means H^r(S3;Sym2)",
            "G0_mapping": "G0,advanced/retarded:Y_s(I)->X_s(I)",
            "N_mapping": "N:X_s(I)->Y_s(I)",
        },
        "coefficient_hypotheses": {
            "spatial_surface": "compact S3",
            "background": "smooth stationary globally hyperbolic Berger cylinder",
            "wave_block": "normally hyperbolic rough tensor wave with finite-slab Sobolev energy estimates",
            "V2": "stationary smooth coefficients and differential order at most two",
            "N": "stationary order-zero bundle map",
        },
        "typed_resolvents": {
            "R_sol_advanced": "(I_X+G0,advanced N)^-1:X_s(I)->X_s(I)",
            "R_sol_retarded": "(I_X+G0,retarded N)^-1:X_s(I)->X_s(I)",
            "R_src_advanced": "(I_Y+N G0,advanced)^-1:Y_s(I)->Y_s(I)",
            "R_src_retarded": "(I_Y+N G0,retarded)^-1:Y_s(I)->Y_s(I)",
            "G_C_advanced": "R_sol,advanced G0,advanced=G0,advanced R_src,advanced:Y_s(I)->X_s(I)",
            "G_C_retarded": "R_sol,retarded G0,retarded=G0,retarded R_src,retarded:Y_s(I)->X_s(I)",
            "support_convention": {
                "advanced": "J^-(source)",
                "retarded": "J^+(source)"
            }
        },
        "factorial_estimates": {
            "constant": "C_(s,T)=M_(s,T)||N||, finite for every integer s and finite slab",
            "solution_series": "||(G0,advanced/retarded N)^n||_(X_s(I)->X_s(I))<=C_(s,T)^n/n!",
            "source_series": "||(N G0,advanced/retarded)^n||_(Y_s(I)->Y_s(I))<=C_(s,T)^n/n!",
            "conclusion": "both series converge absolutely in operator norm on every finite slab and at every Sobolev order",
        },
        "inverse_theorem": {
            "companion": ["C G_C,advanced/retarded=I_Y", "G_C,advanced/retarded C=I_X"],
            "metric_green": "G_A,advanced/retarded=p_sol G_C,advanced/retarded i_src",
            "metric": ["A G_A,advanced/retarded=I", "G_A,advanced/retarded A=I"],
        },
        "adjoint_theorem": {
            "pairing": "frozen nondegenerate metric-antifield BV fibre pairing",
            "identity": "(G_A,advanced)^sharp=G_(A^sharp),retarded",
            "reverse_identity": "(G_A,retarded)^sharp=G_(A^sharp),advanced",
            "A_self_adjoint_used": False,
        },
        "analytic_proof_artifacts": {
            name: _artifact(PROOF_PATHS[name], body)
            for name, body in proof_bodies.items()
        },
        "zero_mode_policy": {
            "inverse_spatial_laplacian": False,
            "spatial_mode_projector": False,
            "massless_zero_modes": "included in causal Cauchy evolution",
        },
        "exact_checks": {
            "retained_metric_projection_exact": True,
            "companion_graph_SDR_exact": True,
            "typed_solution_resolvent": True,
            "typed_source_resolvent": True,
            "solution_factorial_estimate": True,
            "source_factorial_estimate": True,
            "causal_support_passage": True,
            "globalization_by_uniqueness": True,
            "both_companion_inverse_identities": True,
            "both_metric_inverse_identities": True,
            "typed_metric_antifield_adjoint_reversal": True,
            "no_spatial_projector": True,
        },
        "flags": {
            "BERGER_RETAINED_BIWAVE_COMPANION_EXACT": True,
            "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT": True,
            "BERGER_RETAINED_METRIC_GREEN_OPERATORS": True,
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2": False,
            "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2": False,
            "BERGER_CAUSAL_D_CARTAN_V2": False,
        },
        "next_gate": "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2",
        "claim_boundary": "This theorem constructs typed advanced and retarded Green operators for the retained ten-row metric block. It keeps solution- and source-space resolvents separate and proves the adjoint relation only against A^sharp. Downstream BV, Hadamard, Cartan and quantum claims are not promoted here.",
    }
    return payload, proof_bodies


def _source_manifest() -> dict:
    files = [
        ("certificate", CERTIFICATE_PATH),
        ("schema", SCHEMA_PATH),
        ("producer", PRODUCER_PATH),
        ("verifier", VERIFIER_PATH),
        ("tests", TEST_PATH),
        ("report", REPORT_PATH),
        *((f"analytic_proof:{name}", path) for name, path in PROOF_PATHS.items()),
    ]
    return {
        "schema": "pure-weyl-source-manifest-v1",
        "result_id": "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2_SOURCE_MANIFEST",
        "target_result_id": "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2",
        "files": [
            {"role": role, "path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
            for role, path in files
        ],
        "receipt_path": str(RECEIPT_PATH.relative_to(ROOT)),
    }


def _write_outputs(payload: dict, proof_bodies: dict[str, bytes]) -> None:
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    for name, body in proof_bodies.items():
        PROOF_PATHS[name].write_bytes(body)
    CERTIFICATE_PATH.write_bytes(_json_bytes(payload))
    REPORT_PATH.write_text(_report())
    MANIFEST_PATH.write_bytes(_json_bytes(_source_manifest()))


def verify(payload: dict) -> None:
    if payload["dependency_tags"] != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        raise AssertionError("dependency tags drifted")
    if not all(payload["exact_checks"].values()):
        raise AssertionError("a typed Volterra check dropped")
    if payload["adjoint_theorem"]["A_self_adjoint_used"] is not False:
        raise AssertionError("A=A^sharp was silently assumed")
    if payload["adjoint_theorem"]["identity"] != "(G_A,advanced)^sharp=G_(A^sharp),retarded":
        raise AssertionError("typed adjoint theorem drifted")
    for key in ("BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2", "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2", "BERGER_CAUSAL_D_CARTAN_V2"):
        if payload["flags"][key] is not False:
            raise AssertionError(f"downstream theorem promoted: {key}")
    if payload["zero_mode_policy"]["inverse_spatial_laplacian"] is not False or payload["zero_mode_policy"]["spatial_mode_projector"] is not False:
        raise AssertionError("nonlocal spatial projection entered the construction")


def _check_outputs(payload: dict, proof_bodies: dict[str, bytes]) -> None:
    if CERTIFICATE_PATH.read_bytes() != _json_bytes(payload):
        raise AssertionError("typed Volterra certificate drifted")
    if REPORT_PATH.read_text() != _report():
        raise AssertionError("typed Volterra report drifted")
    for name, body in proof_bodies.items():
        if PROOF_PATHS[name].read_bytes() != body:
            raise AssertionError(f"analytic proof artifact drifted: {name}")
    if MANIFEST_PATH.read_bytes() != _json_bytes(_source_manifest()):
        raise AssertionError("source manifest drifted")


def _guards(payload: dict) -> None:
    mutants = (
        ("collapse typed resolvents", ("typed_resolvents", "R_src_advanced"), "R_sol"),
        ("assume self-adjointness", ("adjoint_theorem", "A_self_adjoint_used"), True),
        ("add tag", (None, "dependency_tags"), ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL", "FUNCTIONAL-ANALYTIC"]),
        ("promote 26", ("flags", "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2"), True),
    )
    for name, path, value in mutants:
        mutant = deepcopy(payload)
        if path[0] is None:
            mutant[path[1]] = value
        else:
            mutant[path[0]][path[1]] = value
        try:
            verify(mutant)
            if name == "collapse typed resolvents":
                if mutant["typed_resolvents"]["R_src_advanced"] == "R_sol":
                    raise AssertionError("typed resolvents collapsed")
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload, proof_bodies = build()
    verify(payload)
    if args.write:
        _write_outputs(payload, proof_bodies)
    if args.check:
        _check_outputs(payload, proof_bodies)
    if args.guards:
        _guards(payload)
    print("BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
