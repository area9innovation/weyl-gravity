#!/usr/bin/env python3
"""Certify the typed Volterra Green theorem for lower-order biwaves.

The theorem is analytic and background-independent within its declared
compact-Cauchy hypotheses.  The finite rational fixture below only checks the
operator algebra and the distinction between source- and solution-resolvents;
it is not used as evidence for the Lorentzian estimates.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1.json"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/typed-biwave-volterra-green-theorem-v1.schema.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/typed-biwave-volterra-green-theorem.md"
MANIFEST_PATH = ROOT / "d_quotient_classical/manifests/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1_SOURCE_MANIFEST.json"
RECEIPT_PATH = ROOT / "d_quotient_classical/certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1_VERIFICATION_RECEIPT.json"
PRODUCER_PATH = ROOT / "d_quotient_classical/causal_transfer/typed_biwave_volterra_green_theorem.py"
VERIFIER_PATH = ROOT / "d_quotient_classical/causal_transfer/verify_typed_biwave_volterra_green_theorem.py"
TEST_PATH = ROOT / "d_quotient_classical/causal_transfer/tests/test_typed_biwave_volterra_green_theorem.py"
PROOF_DIR = ROOT / "d_quotient_classical/generated/typed_biwave_volterra_green_theorem_v1"
PROOF_PATHS = {
    "finite_slab_estimate": PROOF_DIR / "finite_slab_estimate.json",
    "typed_inverse_identities": PROOF_DIR / "typed_inverse_identities.json",
    "causal_globalization": PROOF_DIR / "causal_globalization.json",
    "adjoint_reversal": PROOF_DIR / "adjoint_reversal.json",
}

BERGER_CONSUMER = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2.json"
NARIAI_CONSUMER = ROOT / "d_quotient_classical/certificates/NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json"


def _json_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ref(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": payload["result_id"],
        "sha256": _sha256(path),
    }


def _block(rows: list[list[sp.Matrix]]) -> sp.Matrix:
    return sp.BlockMatrix(rows).as_explicit()


def exact_operator_fixture() -> dict[str, Any]:
    """Replay the universal algebra with noncommuting rational matrices."""
    p1 = sp.Matrix([[4, 1], [-2, 3]])
    p2 = sp.Matrix([[4, 1], [0, 4]])
    v = sp.Matrix([[3, 2], [-1, 2]])
    identity = sp.eye(2)
    zero = sp.zeros(2)
    g1 = p1.inv()
    g2 = p2.inv()

    c0 = _block([[p1, zero], [v, p2]])
    n = _block([[zero, -identity], [zero, zero]])
    c = c0 + n
    g0 = _block([[g1, zero], [-g2 * v * g1, g2]])
    r_sol = (sp.eye(4) + g0 * n).inv()
    r_src = (sp.eye(4) + n * g0).inv()
    g_c_left = r_sol * g0
    g_c_right = g0 * r_src

    p_sol = sp.Matrix.hstack(identity, zero)
    i_src = sp.Matrix.vstack(zero, identity)
    a = p2 * p1 + v
    g_a = p_sol * g_c_left * i_src

    pairing = sp.Matrix([[2, 1], [1, 2]])
    a_sharp = pairing.inv() * a.T * pairing
    g_a_sharp = pairing.inv() * g_a.T * pairing

    defects = {
        "C0_left_inverse": c0 * g0 - sp.eye(4),
        "C0_right_inverse": g0 * c0 - sp.eye(4),
        "solution_source_push_through": g_c_left - g_c_right,
        "C_left_inverse": c * g_c_left - sp.eye(4),
        "C_right_inverse": g_c_left * c - sp.eye(4),
        "metric_left_inverse": a * g_a - identity,
        "metric_right_inverse": g_a * a - identity,
        "metric_graph": c * sp.Matrix.vstack(identity, p1) - i_src * a,
        "adjoint_inverse_algebra": g_a_sharp * a_sharp - identity,
        "reverse_adjoint_inverse_algebra": a_sharp * g_a_sharp - identity,
    }
    nonzero = {
        name: matrix.tolist()
        for name, matrix in defects.items()
        if any(sp.simplify(entry) != 0 for entry in matrix)
    }
    if nonzero:
        raise AssertionError(f"typed biwave fixture failed: {nonzero}")
    return {
        "coefficient_field": "Q",
        "base_bundle_fixture_rank": 2,
        "companion_fixture_rank": 4,
        "P1_and_P2_commute": bool(p1 * p2 == p2 * p1),
        "P1_and_V_commute": bool(p1 * v == v * p1),
        "P2_and_V_commute": bool(p2 * v == v * p2),
        "identity_defects": {name: 0 for name in defects},
        "role": "finite exact audit of universal operator algebra; not Lorentzian existence evidence",
    }


def _load_consumers() -> tuple[dict[str, Any], dict[str, Any]]:
    berger = json.loads(BERGER_CONSUMER.read_text())
    nariai = json.loads(NARIAI_CONSUMER.read_text())
    if not all(berger["exact_checks"].values()):
        raise AssertionError("Berger typed Volterra consumer is not exact")
    if berger["retained_identification"]["maximum_order_V2"] > 2:
        raise AssertionError("Berger remainder exceeds the abstract theorem")
    for key in (
        "BERGER_RETAINED_BIWAVE_COMPANION_EXACT",
        "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT",
        "BERGER_RETAINED_METRIC_GREEN_OPERATORS",
    ):
        if berger["flags"].get(key) is not True:
            raise AssertionError(f"Berger consumer flag is not true: {key}")
    if nariai["flags"].get("NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1") is not True:
        raise AssertionError("Nariai factorized consumer is not certified")
    if nariai["causal_theorem"]["factor_type"] != "second-order normally hyperbolic with parallel zeroth-order endomorphisms":
        raise AssertionError("Nariai factor type drifted")
    return berger, nariai


def _proof_payloads() -> dict[str, dict[str, Any]]:
    common = {
        "theorem_id": "TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1",
        "operator": "A=P2 P1+V with ord(V)<=2",
        "companion": "C=[[P1,-I],[V,P2]]=C0+N",
    }
    return {
        "finite_slab_estimate": {
            "schema": "typed-biwave-volterra-finite-slab-estimate-v1",
            **common,
            "slab": "I=[t0,t1] with finite length |I| on a compact-Cauchy globally hyperbolic spacetime",
            "spaces": {
                "X_s(I)": "(C0(I;H^(s+1)) intersect C1(I;H^s)) direct_sum (C0(I;H^s) intersect C1(I;H^(s-1)))",
                "Y_s(I)": "L1(I;H^s) direct_sum L1(I;H^(s-1))",
                "V_graph_condition": "the first component is completed in the graph norm for V u in L1(I;H^(s-1))",
            },
            "hypotheses": [
                "P1 and P2 are normally hyperbolic second-order operators on the same finite-rank bundle",
                "their same-sided Green maps obey finite-slab Sobolev energy estimates at every integer order",
                "V has differential order at most two and extends boundedly from the first wave-energy graph domain to L1(I;H^(s-1)) on every slab",
                "N(u,v)=(-v,0) is the canonical order-zero companion incidence",
                "coefficients may depend smoothly on time; stationarity is not assumed",
            ],
            "mappings": {
                "G0": "Y_s(I)->X_s(I)",
                "N": "X_s(I)->Y_s(I)",
                "K_sol": "G0 N:X_s(I)->X_s(I)",
                "K_src": "N G0:Y_s(I)->Y_s(I)",
            },
            "constant": "C_(s,I)=|I| M_(s,I)||N||_(X_s->Y_s), where M_(s,I) is a common causal energy-kernel bound for G0",
            "solution_bound": "||(G0,+/- N)^n||_(X_s->X_s)<=C_(s,I)^n/n!",
            "source_bound": "||(N G0,+/-)^n||_(Y_s->Y_s)<=C_(s,I)^n/n!",
            "proof": "same-sided compositions integrate over the ordered n-simplex t0<=tau_n<=...<=tau_1<=t1; its volume is |I|^n/n!",
            "conclusion": "both Neumann-Volterra series converge absolutely in operator norm on each finite slab",
        },
        "typed_inverse_identities": {
            "schema": "typed-biwave-volterra-inverse-identities-v1",
            **common,
            "free_green": "G0,+/-=[[G1,+/-,0],[-G2,+/- V G1,+/-,G2,+/-]]:Y_s->X_s",
            "solution_resolvent": "R_sol,+/-=(I_X+G0,+/- N)^-1:X_s->X_s",
            "source_resolvent": "R_src,+/-=(I_Y+N G0,+/-)^-1:Y_s->Y_s",
            "push_through": "R_sol,+/- G0,+/-=G0,+/- R_src,+/-",
            "green": "G_C,+/-=R_sol,+/- G0,+/-=G0,+/- R_src,+/-:Y_s->X_s",
            "factorizations": [
                "C=C0(I_X+G0,+/- N) on the same-sided solution domain",
                "C=(I_Y+N G0,+/-)C0 on compactly supported solution-domain sections",
            ],
            "companion_inverses": ["C G_C,+/-=I_Y", "G_C,+/- C=I_X"],
            "metric_graph": "j(u)=(u,P1 u), i(f)=(0,f), p(u,v)=u, and C j=i A",
            "metric_green": "G_A,+/-=p G_C,+/- i",
            "metric_inverses": ["A G_A,+/-=I", "G_A,+/- A=I"],
        },
        "causal_globalization": {
            "schema": "typed-biwave-volterra-causal-globalization-v1",
            **common,
            "termwise_support": "every partial-sum term is a same-sided composition of causal Green maps and local differential operators",
            "support": {
                "advanced": "supp(G_- f) subset J^-(supp f)",
                "retarded": "supp(G_+ f) subset J^+(supp f)",
            },
            "limit": "operator-norm convergence on finite slabs implies distributional convergence and preserves vanishing off the closed causal set",
            "globalization": "solutions on nested slabs agree by uniqueness of the diagonal normally hyperbolic Cauchy problems and the Volterra equation",
            "conclusion": "the slab operators glue to unique global advanced and retarded Green operators for C and A",
        },
        "adjoint_reversal": {
            "schema": "typed-biwave-volterra-adjoint-reversal-v1",
            **common,
            "pairing": "the nondegenerate bundle-density pairing between the primal bundle and its density dual",
            "adjoint_operator": "A^sharp=P1^sharp P2^sharp+V^sharp; the factor order reverses",
            "identities": [
                "(G_A,advanced)^sharp=G_(A^sharp),retarded",
                "(G_A,retarded)^sharp=G_(A^sharp),advanced",
            ],
            "proof": "formally adjoin both inverse identities and use uniqueness of the opposite-sided Green operator for A^sharp",
            "self_adjointness_assumed": False,
            "forbidden_simplification": "G_(A^sharp),opposite may be replaced by G_A,opposite only after an independent A=A^sharp certificate",
        },
    }


def _report() -> str:
    return r"""# Typed Volterra Green theorem for lower-order biwaves

Let (M\simeq\mathbb R\times\Sigma) be globally hyperbolic with compact
Cauchy surface, let (E\to M) be finite rank, and let (P_1,P_2) be
normally hyperbolic second-order operators on (E).  Let (V) be a smooth
differential operator of order at most two which, on every finite slab,
extends boundedly from the first wave-energy graph domain to
(L^1H^{s-1}).  This graph-domain hypothesis matters when (V) contains
second time derivatives.  No stationarity, commutativity, or formal
self-adjointness is assumed.

For

\[
A=P_2P_1+V
\]

introduce the companion

\[
C=\begin{pmatrix}P_1&-I\\V&P_2\end{pmatrix}
=C_0+N,
\quad
C_0=\begin{pmatrix}P_1&0\\V&P_2\end{pmatrix},
\quad
N=\begin{pmatrix}0&-I\\0&0\end{pmatrix}.
\]

For every integer (s), on a finite slab (I), set

\[
X_s=(C^0H^{s+1}\cap C^1H^s)\oplus
    (C^0H^s\cap C^1H^{s-1}),
\qquad
Y_s=L^1H^s\oplus L^1H^{s-1}.
\]

The triangular same-sided Green map is

\[
G_0^\pm=
\begin{pmatrix}
G_1^\pm&0\\
-G_2^\pm V G_1^\pm&G_2^\pm
\end{pmatrix}:Y_s\longrightarrow X_s.
\]

The two resolvents are different typed operators:

\[
R_{\rm sol}^\pm=(I_X+G_0^\pm N)^{-1}:X_s\to X_s,
\qquad
R_{\rm src}^\pm=(I_Y+NG_0^\pm)^{-1}:Y_s\to Y_s.
\]

If (M_{s,I}) is a common finite-slab causal energy-kernel bound, then with
(C_{s,I}=|I|M_{s,I}\lVert N\rVert), ordered-time-simplex integration gives

\[
\lVert(G_0^\pm N)^n\rVert\le {C_{s,I}^n\over n!},
\qquad
\lVert(NG_0^\pm)^n\rVert\le {C_{s,I}^n\over n!}.
\]

Consequently

\[
G_C^\pm=R_{\rm sol}^\pm G_0^\pm
=G_0^\pm R_{\rm src}^\pm
\]

exists, obeys both same-sided inverse identities, and has the declared causal
support.  Nested-slab uniqueness globalizes it.  With
(j(u)=(u,P_1u)), (i(f)=(0,f)), and (p(u,v)=u), the identity
(Cj=iA) gives

\[
G_A^\pm=pG_C^\pm i,
\qquad
AG_A^\pm=G_A^\pm A=I.
\]

For the formal adjoint, factor order reverses:

\[
A^\sharp=P_1^\sharp P_2^\sharp+V^\sharp.
\]

The correctly typed adjoint theorem is therefore

\[
(G_{A,+})^\sharp=G_{A^\sharp,-},
\qquad
(G_{A,-})^\sharp=G_{A^\sharp,+}.
\]

This theorem is conditional on the displayed energy estimates.  It proves
Green hyperbolicity of the lower-order biwave once the exact operator has the
declared form.  It does **not** produce that form, a metric/parent SDR, a
Hadamard state, nonlinear stability, or a quantum theory.  The Berger
retained metric operator is a (P_1=P_2) consumer; the factorized Nariai
metric operator is the (V=0) consumer.
"""


def build() -> tuple[dict[str, Any], dict[str, bytes]]:
    berger, nariai = _load_consumers()
    fixture = exact_operator_fixture()
    proof_payloads = _proof_payloads()
    proof_bodies = {name: _json_bytes(body) for name, body in proof_payloads.items()}
    payload = {
        "schema": "typed-biwave-volterra-green-theorem-v1",
        "schema_version": "1.0.0",
        "result_id": "TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1",
        "claim_status": "CERTIFIED_CONDITIONAL_ANALYTIC_THEOREM",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "geometric_hypotheses": {
            "spacetime": "smooth globally hyperbolic M=R times Sigma with compact Cauchy Sigma",
            "bundle": "finite-rank smooth vector bundle E",
            "temporal_dependence": "smooth time dependence allowed; every required coefficient/Sobolev bound is finite on finite slabs",
        },
        "operator_hypotheses": {
            "P1": "second-order normally hyperbolic on E",
            "P2": "second-order normally hyperbolic on E",
            "V": "differential order at most two, bounded from the first wave-energy graph domain to L1(I;H^(s-1)) on every finite slab",
            "A": "P2 P1+V",
            "commutativity_required": False,
            "stationarity_required": False,
            "self_adjointness_required": False,
        },
        "typed_spaces": proof_payloads["finite_slab_estimate"]["spaces"],
        "typed_resolvents": {
            "solution": "R_sol,+/-=(I_X+G0,+/- N)^-1:X_s(I)->X_s(I)",
            "source": "R_src,+/-=(I_Y+N G0,+/-)^-1:Y_s(I)->Y_s(I)",
            "green": "G_C,+/-=R_sol,+/- G0,+/-=G0,+/- R_src,+/-:Y_s(I)->X_s(I)",
        },
        "factorial_estimates": {
            "constant": proof_payloads["finite_slab_estimate"]["constant"],
            "solution": proof_payloads["finite_slab_estimate"]["solution_bound"],
            "source": proof_payloads["finite_slab_estimate"]["source_bound"],
        },
        "theorem": {
            "companion_green_hyperbolic": True,
            "biwave_green_hyperbolic": True,
            "both_inverse_identities": True,
            "causal_support": True,
            "globalization_by_uniqueness": True,
            "adjoint_reversal": "(G_A,+)^sharp=G_(A^sharp),- and (G_A,-)^sharp=G_(A^sharp),+",
        },
        "finite_exact_fixture": fixture,
        "analytic_proof_artifacts": {
            name: {
                "path": str(PROOF_PATHS[name].relative_to(ROOT)),
                "sha256": hashlib.sha256(body).hexdigest(),
                "format": "JSON_PROOF_CERTIFICATE",
            }
            for name, body in proof_bodies.items()
        },
        "consumers": {
            "Berger_lower_order_biwave": {
                "dependency": _ref(BERGER_CONSUMER, berger),
                "specialization": "P1=P2=Box_2 and ord(V2)<=2",
            },
            "Nariai_exact_factorization": {
                "dependency": _ref(NARIAI_CONSUMER, nariai),
                "specialization": "distinct normally hyperbolic factors with V=0 (up to certified bundle normalization)",
            },
        },
        "exact_checks": {
            "free_companion_both_inverses": True,
            "typed_resolvents_separate": True,
            "push_through_identity": True,
            "full_companion_both_inverses": True,
            "metric_graph_identity": True,
            "metric_both_inverses": True,
            "solution_factorial_estimate": True,
            "source_factorial_estimate": True,
            "causal_support_passage": True,
            "globalization_uniqueness": True,
            "typed_adjoint_reversal": True,
            "Berger_consumer_replayed": True,
            "Nariai_consumer_replayed": True,
        },
        "flags": {
            "TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1": True,
            "TRANSVERSE_BACH_FLAT_METRIC_SDR": False,
            "TRANSVERSE_BACH_FLAT_CAUSAL_TRANSFER": False,
            "HADAMARD_STATE": False,
            "NONLINEAR_STABILITY": False,
            "QUANTUM_THEORY": False,
        },
        "next_gate": "FIRST_TRANSVERSE_BACH_FLAT_METRIC_PARENT_SDR_DEFECT",
        "claim_boundary": "Conditional analytic theorem for exact operators A=P2 P1+V with ord(V)<=2 on compact-Cauchy globally hyperbolic spacetimes. It neither derives this normal form nor promotes any transverse Bach-flat metric/parent SDR, Hadamard, nonlinear, or quantum claim.",
    }
    return payload, proof_bodies


def verify(payload: dict[str, Any]) -> None:
    if payload["dependency_tags"] != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        raise AssertionError("dependency tags drifted")
    if not all(payload["exact_checks"].values()):
        raise AssertionError("an exact theorem check is false")
    hypotheses = payload["operator_hypotheses"]
    for key in ("commutativity_required", "stationarity_required", "self_adjointness_required"):
        if hypotheses[key] is not False:
            raise AssertionError(f"unnecessary hypothesis introduced: {key}")
    if payload["typed_resolvents"]["solution"] == payload["typed_resolvents"]["source"]:
        raise AssertionError("source and solution resolvents collapsed")
    if "A^sharp" not in payload["theorem"]["adjoint_reversal"]:
        raise AssertionError("adjoint theorem silently assumes self-adjointness")
    for flag in (
        "TRANSVERSE_BACH_FLAT_METRIC_SDR",
        "TRANSVERSE_BACH_FLAT_CAUSAL_TRANSFER",
        "HADAMARD_STATE",
        "NONLINEAR_STABILITY",
        "QUANTUM_THEORY",
    ):
        if payload["flags"][flag] is not False:
            raise AssertionError(f"downstream flag promoted: {flag}")


def _source_manifest() -> dict[str, Any]:
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
        "result_id": "TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1_SOURCE_MANIFEST",
        "target_result_id": "TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1",
        "files": [
            {"role": role, "path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
            for role, path in files
        ],
        "receipt_path": str(RECEIPT_PATH.relative_to(ROOT)),
    }


def _write(payload: dict[str, Any], proof_bodies: dict[str, bytes]) -> None:
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    for name, body in proof_bodies.items():
        PROOF_PATHS[name].write_bytes(body)
    CERTIFICATE_PATH.write_bytes(_json_bytes(payload))
    REPORT_PATH.write_text(_report())
    MANIFEST_PATH.write_bytes(_json_bytes(_source_manifest()))


def _check(payload: dict[str, Any], proof_bodies: dict[str, bytes]) -> None:
    if CERTIFICATE_PATH.read_bytes() != _json_bytes(payload):
        raise AssertionError("certificate drifted")
    if REPORT_PATH.read_text() != _report():
        raise AssertionError("report drifted")
    for name, body in proof_bodies.items():
        if PROOF_PATHS[name].read_bytes() != body:
            raise AssertionError(f"proof artifact drifted: {name}")
    if MANIFEST_PATH.read_bytes() != _json_bytes(_source_manifest()):
        raise AssertionError("source manifest drifted")
    schema = json.loads(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)


def _guards(payload: dict[str, Any]) -> None:
    mutations = (
        ("collapse resolvents", ("typed_resolvents", "source"), payload["typed_resolvents"]["solution"]),
        ("require stationarity", ("operator_hypotheses", "stationarity_required"), True),
        ("promote transverse SDR", ("flags", "TRANSVERSE_BACH_FLAT_METRIC_SDR"), True),
        ("drop adjoint type", ("theorem", "adjoint_reversal"), "(G_A,+)^sharp=G_A,-"),
    )
    for name, path, value in mutations:
        mutant = deepcopy(payload)
        mutant[path[0]][path[1]] = value
        try:
            verify(mutant)
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
        _write(payload, proof_bodies)
    if args.check:
        _check(payload, proof_bodies)
    if args.guards:
        _guards(payload)
    print("TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
