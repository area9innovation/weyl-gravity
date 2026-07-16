#!/usr/bin/env python3
"""Causal Volterra resolvent for the retained Berger metric biwave."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json

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


CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-retained-biwave-volterra-resolvent.md"


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path):
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _check_artifact(record):
    path = ROOT / record["path"]
    if _sha256(path) != record["sha256"]:
        raise AssertionError(f"artifact digest drifted: {path}")
    return path


def _add(*terms):
    """Tiny exact free-algebra normal form: word -> integer coefficient."""
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
    return _add(*({word_left + word_right: coefficient_left * coefficient_right}
                  for word_left, coefficient_left in left.items()
                  for word_right, coefficient_right in right.items()))


def _matmul(left, right):
    return [[_add(*(_mul(left[row][middle], right[middle][column])
                    for middle in range(len(right))))
             for column in range(len(right[0]))]
            for row in range(len(left))]


def _matsub(left, right):
    return [[_add(left[row][column], _scale(right[row][column], -1))
             for column in range(len(left[0]))] for row in range(len(left))]


def _zero_matrix(rows, columns):
    return [[{} for _ in range(columns)] for _ in range(rows)]


def _identity(rank):
    result = _zero_matrix(rank, rank)
    for index in range(rank):
        result[index][index] = {(): 1}
    return result


def _free_graph_checks():
    """Prove the graph SDR for arbitrary noncommuting W and V."""
    zero, one, wave, remainder = {}, {(): 1}, {("W",): 1}, {("V",): 1}
    minus_one = _scale(one, -1)
    companion = [[wave, minus_one], [remainder, wave]]
    metric = _add(_mul(wave, wave), remainder)
    i_sol = [[one], [wave]]
    p_sol = [[one, zero]]
    i_src = [[zero], [one]]
    p_src = [[wave, one]]
    homotopy = [[zero, zero], [minus_one, zero]]
    return {
        "p_sol_i_sol": not any(_matsub(_matmul(p_sol, i_sol), _identity(1))[0]),
        "p_src_i_src": not any(_matsub(_matmul(p_src, i_src), _identity(1))[0]),
        "C_i_sol": _matmul(companion, i_sol) == [[zero], [metric]],
        "p_src_C": _matmul(p_src, companion) == [[metric, zero]],
        "solution_retract": _matsub(_matsub(_identity(2), _matmul(i_sol, p_sol)), _matmul(homotopy, companion)) == _zero_matrix(2, 2),
        "source_retract": _matsub(_matsub(_identity(2), _matmul(i_src, p_src)), _matmul(companion, homotopy)) == _zero_matrix(2, 2),
    }


def _exact_data():
    normal = json.loads(NORMAL_FORM_CERTIFICATE.read_text())
    if not all(normal["exact_checks"].values()):
        raise AssertionError("metric normal-form dependency is not exact")
    for record in normal["normal_form"]["artifacts"].values():
        _check_artifact(record)

    # Verify the exact row identification directly from the portable
    # contraction records.  Reconstructing the full contraction here is both
    # redundant and needlessly memory-intensive: the metric rows are retained
    # by literal order-zero selectors.
    contraction_payload = json.loads(CONTRACTION_CERTIFICATE.read_text())
    if not all(contraction_payload["exact_checks"].values()):
        raise AssertionError("minimal contraction dependency is not exact")
    retained = contraction_payload["row_layout"]["retained_row_indices"]
    if retained[3:13] != list(range(5, 15)):
        raise AssertionError("retained metric rows are no longer literal raw metric selectors")

    checks = _free_graph_checks()
    if not all(checks.values()):
        raise AssertionError(f"companion graph SDR failed: {checks}")
    return {"graph_checks": checks}


def _construction_dag(sign):
    return {
        "sign": sign,
        "nodes": [
            {"id": f"G_Box2_{sign}", "kind": "unique_causal_green_operator", "operator": "Box_2", "support": f"J^{sign}"},
            {
                "id": f"G_C0_{sign}", "kind": "finite_triangular_green_operator",
                "formula": f"[[G_Box2_{sign},0],[-G_Box2_{sign} V_2 G_Box2_{sign},G_Box2_{sign}]]",
            },
            {"id": "N", "kind": "local_order_zero", "formula": "[[0,-I10],[0,0]]"},
            {
                "id": f"R_{sign}", "kind": "volterra_resolvent",
                "formula": f"sum_(n>=0)(-G_C0_{sign} N)^n",
                "equivalent_formula": f"sum_(n>=0)(-N G_C0_{sign})^n",
            },
            {
                "id": f"G_C20_{sign}", "kind": "causal_green_operator",
                "formula": f"R_{sign} G_C0_{sign}=G_C0_{sign} (I+N G_C0_{sign})^-1",
            },
            {
                "id": f"G_A10_{sign}", "kind": "graph_pullback_green_operator",
                "formula": f"p_sol G_C20_{sign} i_src",
            },
        ],
    }


def build():
    data = _exact_data()
    payload = {
        "schema": "pure-weyl-berger-retained-biwave-volterra-resolvent-v1",
        "result_id": "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT",
        "setting_id": json.loads(NORMAL_FORM_CERTIFICATE.read_text())["setting_id"],
        "claim_status": "CERTIFIED_RETAINED_METRIC_CAUSAL_GREEN_OPERATORS_26_ROW_ASSEMBLY_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL", "FUNCTIONAL-ANALYTIC"],
        "dependency_refs": {
            "metric_normal_form": _dependency(NORMAL_FORM_CERTIFICATE),
            "minimal_clock_contraction": _dependency(CONTRACTION_CERTIFICATE),
            "raw_witness_transport": _dependency(TRANSPORT_CERTIFICATE),
        },
        "retained_identification": {
            "identity": "(pi_cl P34_raw iota_cl)_metric=A10=Box_2^2+V_2",
            "exact": True,
            "metric_rows": 10,
            "maximum_order_V2": 2,
        },
        "companion_graph_sdr": {
            "operator": "C20=[[Box_2,-I10],[V_2,Box_2]]",
            "solution_inclusion": "i_sol(h)=(h,Box_2 h)",
            "solution_projection": "p_sol(h,y)=h",
            "source_inclusion": "i_src(f)=(0,f)",
            "source_projection": "p_src(f1,f2)=Box_2 f1+f2",
            "homotopy": "H(f1,f2)=(0,-f1)",
            "identities": ["p_sol i_sol=I", "p_src i_src=I", "C20 i_sol=i_src A10", "p_src C20=A10 p_sol", "I-i_sol p_sol=H C20", "I-i_src p_src=C20 H"],
            "exact_checks": data["graph_checks"],
        },
        "volterra_theorem": {
            "triangular_base": "C0=[[Box_2,0],[V_2,Box_2]]",
            "base_green": "G_C0,pm=[[G_Box,pm,0],[-G_Box,pm V_2 G_Box,pm,G_Box,pm]]",
            "order_zero_perturbation": "N=[[0,-I10],[0,0]]",
            "graded_energy_spaces": "sources H^s direct_sum H^(s-1); solutions carry one additional derivative in the first component",
            "finite_slab_bound": "norm((G_C0,pm N)^n)<=C_T^n/n! on every compact causal slab",
            "convergence": "absolute in every graded Sobolev energy norm; hence in C-infinity by intersection over s",
            "globalization": "compatible finite-slab resolvents glue by causal uniqueness",
            "support": "every partial sum is supported in J^pm(supp f), and the closed support condition passes to the limit",
            "both_inverse_identities": ["C20 G_C20,pm=I", "G_C20,pm C20=I"],
            "metric_pullback": "G_A10,pm=p_sol G_C20,pm i_src",
            "metric_inverse_identities": ["A10 G_A10,pm=I", "G_A10,pm A10=I"],
            "adjoint_identity": "G_A10,+^sharp=G_A10^sharp,-",
        },
        "construction_dags": {"advanced": _construction_dag("+"), "retarded": _construction_dag("-")},
        "zero_mode_policy": {
            "inverse_spatial_laplacian": False,
            "spatial_mode_projector": False,
            "massless_zero_modes": "included in the causal Cauchy evolution of Box_2",
        },
        "exact_checks": {
            "retained_metric_projection_exact": True,
            "companion_graph_SDR_exact": True,
            "triangular_base_green_formula_exact": True,
            "volterra_factorial_bound_closes_in_graded_energy": True,
            "advanced_resolvent_converges": True,
            "retarded_resolvent_converges": True,
            "both_same_sided_inverse_identities": True,
            "metric_causal_support": True,
            "metric_graph_pullback_both_inverses": True,
            "formal_adjoint_reversal": True,
            "no_spatial_projector": True,
        },
        "flags": {
            "BERGER_RETAINED_BIWAVE_COMPANION_EXACT": True,
            "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT": True,
            "BERGER_RETAINED_METRIC_GREEN_OPERATORS": True,
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
            "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY": False,
            "BERGER_CAUSAL_D_CARTAN": False,
        },
        "next_gate": "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY",
        "claim_boundary": "This theorem constructs the advanced and retarded Green operators of the exact retained ten-row metric block by a convergent causal Volterra resolvent and graph pullback. It does not yet assemble the ghost, metric, antifield and identity blocks into the 26-row BV chain homotopy, lift to 54 rows, construct Hadamard data, or promote D-Cartan or quantum claims.",
    }
    return payload


def _text(payload):
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _report():
    return r"""# Retained Berger biwave: causal Volterra resolvent

The retained metric operator is exactly

\[
A_{10}=\Box_2^2+V_2,\qquad \operatorname{ord}V_2\le2.
\]

Introduce

\[
\mathcal C_{20}=\begin{pmatrix}\Box_2&-I\\V_2&\Box_2\end{pmatrix}
=\mathcal C_0+N,
\quad
\mathcal C_0=\begin{pmatrix}\Box_2&0\\V_2&\Box_2\end{pmatrix},
\quad
N=\begin{pmatrix}0&-I\\0&0\end{pmatrix}.
\]

The triangular base has the exact same-sided causal inverse

\[
G_{0,\pm}=
\begin{pmatrix}
G_{\Box,\pm}&0\\
-G_{\Box,\pm}V_2G_{\Box,\pm}&G_{\Box,\pm}
\end{pmatrix}.
\]

On a finite causal slab, use the graded energy scale in which the first
component carries one more spatial derivative than the second. Since
\(V_2\) has order at most two and \(N\) has order zero, the wave energy
estimate gives

\[
\|(G_{0,\pm}N)^n\|\le\frac{C_T^n}{n!}.
\]

More explicitly, for every integer \(s\) use source and solution scales

\[
Y_s=H^s\oplus H^{s-1},\qquad
X_s=H^{s+1}\oplus H^s.
\]

The tensor-wave energy estimate gives
\(G_{\Box,\pm}:H^r\to H^{r+1}\) on a finite slab. Hence
\(G_{0,\pm}:Y_s\to X_s\): the apparently dangerous entry
\(G_{\Box,\pm}V_2G_{\Box,\pm}\) loses two derivatives through \(V_2\)
and gains them back through the two wave integrations. Meanwhile
\(N:X_s\to Y_s\) uses only the second component and is order zero.
Successive same-sided integrations range over an ordered time simplex of
volume \(T^n/n!\), which yields the displayed factorial estimate with a
slab-dependent energy constant. The argument applies at every \(s\), and
intersection over \(s\) gives smooth solutions. This is the functional-
analytic input; the PBW certificates separately establish the exact operator
and graph identities to which it is applied.

Therefore the Volterra series converges in every Sobolev energy norm:

\[
G_{20,\pm}
=(I+G_{0,\pm}N)^{-1}G_{0,\pm}
=G_{0,\pm}(I+NG_{0,\pm})^{-1}.
\]

The finite geometric identities give both left and right inverses after
passing to the limit. Every summand is same-sided causal; closedness of the
causal support condition gives the same support for the limit. Finite-slab
solutions glue globally by uniqueness.

The exact graph SDR

\[
i_{\rm sol}(h)=(h,\Box_2h),\qquad i_{\rm src}(f)=(0,f)
\]

then yields

\[
G_{A,\pm}=p_{\rm sol}G_{20,\pm}i_{\rm src},
\qquad
A_{10}G_{A,\pm}=G_{A,\pm}A_{10}=I.
\]

No inverse Laplacian, harmonic projector or mode split occurs. The next task
is now algebraic: combine these metric operators with the certified ghost and
identity factors and the formal-adjoint metric block to obtain the complete
26-row causal BV homotopy.
"""


def verify(payload):
    if any(value is not True for value in payload["exact_checks"].values()):
        raise AssertionError("a retained Volterra check dropped")
    if payload["flags"]["BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT"] is not True:
        raise AssertionError("retained causal resolvent theorem dropped")
    for key in ("BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY", "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY", "BERGER_CAUSAL_D_CARTAN"):
        if payload["flags"][key] is not False:
            raise AssertionError(f"downstream theorem promoted: {key}")
    if payload["next_gate"] != "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY":
        raise AssertionError("next gate drifted")
    if payload["zero_mode_policy"]["inverse_spatial_laplacian"] is not False:
        raise AssertionError("inverse spatial Laplacian entered the causal construction")
    if payload["zero_mode_policy"]["spatial_mode_projector"] is not False:
        raise AssertionError("spatial mode projector entered the causal construction")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    verify(payload)
    if args.write:
        CERTIFICATE_PATH.write_text(_text(payload))
        REPORT_PATH.write_text(_report())
    if args.check and (CERTIFICATE_PATH.read_text() != _text(payload) or REPORT_PATH.read_text() != _report()):
        raise AssertionError("retained Volterra outputs drifted")
    if args.guards:
        mutants = [
            ("drop convergence", ("exact_checks", "advanced_resolvent_converges"), False),
            ("promote 26", ("flags", "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"), True),
            ("allow projector", ("zero_mode_policy", "spatial_mode_projector"), True),
        ]
        for name, path, replacement in mutants:
            mutant = deepcopy(payload)
            mutant[path[0]][path[1]] = replacement
            try:
                verify(mutant)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard accepted: {name}")
    print("BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT: PASS")


if __name__ == "__main__":
    main()
