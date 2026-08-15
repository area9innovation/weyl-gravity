# Strict 386-row stabilized q2/Green composition preflight v1

## Outcome

Yes, at first nonlinear response order and for the candidate only. The q2 preflight and accepted unary-causal snapshot have identical basis, pairing and graph-q1 hashes. The finite-order support-local candidate maps two compact smooth inputs to a compact smooth source, so each represented Green name accepts its output. The two continuous bilinear names B_plus/minus=Lambda_plus/minus q2_candidate obey sign-oriented causal support and the exact arity-two homotopy-response identity; their difference is q1-compatible. The construction adds no choice operation beyond the imported analytic Green theorem. Its carrier and q2 algebra are finitary exact data, while the Green factor genuinely uses completed LF/Frechet spaces, a countable Hodge-projector limit and classical normally-hyperbolic PDE theory. This does not identify the candidate with the authoritative classical q2, construct recursive nonlinear trees, select a Hadamard state, or restore the QME.

## Common carrier

The candidate and unary-causal snapshot agree exactly on the basis, pairing and graph q1: `True`, `True`, `True`.

## First nonlinear causal response

```text
B_plus(u,v)  = Lambda_graph,plus(q2_candidate(u,v))
B_minus(u,v) = Lambda_graph,minus(q2_candidate(u,v))
B_causal      = B_plus - B_minus
```

Both sign-oriented names are continuous bilinear maps on `Gamma_c^infinity(M,E_386) x Gamma_c^infinity(M,E_386)`. Their support lies in the corresponding causal future or past of `supp(u) intersection supp(v)`. The conservative graph-coordinate differential-order bounds are **10** per input and **13** in total.

The exact structural replay gives

```text
q1 B_sign(u,v)-B_sign(q1 u,v)-(-1)^|u| B_sign(u,q1 v)=q2_candidate(u,v)
q1 B_causal(u,v)-B_causal(q1 u,v)-(-1)^|u| B_causal(u,q1 v)=0
```

## Foundational split

| Layer | What it uses | Status |
|---|---|---|
| `FINITE_EXACT_LOCAL` | 386-row carrier hashes, q2 transport DAG, carrier equality, and formal response identity | PRA conditional on the pinned tensor-natural differential identities |
| `SMOOTH_LOCAL_FUNCTION_SPACES` | Gamma_c^infinity LF steps and continuity of finite-order bilinear differential maps | ordinary classical smooth locally convex analysis |
| `SPECTRAL_CAUSAL_GREEN` | canonical S3 Hodge projectors, countable spectral convergence, Duhamel integration, and unique normally-hyperbolic Green operators | the classical analytic theorems pinned by STRICT_386_GRAPH_GREEN_ACTION_NAME_V1 |
| `NONLINEAR_CAUSAL_COMPOSITION` | B_plus, B_minus, and their causal difference | no new assumptions beyond prior layers |

No selected eigenbasis is required: whole Hodge eigenspace projectors are canonical. Nevertheless, the Green factor uses completed infinite-dimensional spaces and a countable spectral limit. The weakest reverse-mathematical base and the choice strength of the imported analytic theorems remain uncalibrated.

## Why this is still a preflight

Composability with the accepted unary-causal snapshot does not identify a receiver-constructed q2 with the source theory's nonlinear extension.

The result covers one application of the Green homotopy after one local binary interaction. It does not prove that two noncompact causal outputs can be fed back into q2, so it is not an interacting perturbation series.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_stabilized_q2_green_composition_preflight.py --check
python3 quantum-weyl/classical_import/check_strict_386_stabilized_q2_green_composition_preflight.py
python3 quantum-weyl/classical_import/verify_strict_386_stabilized_q2_green_composition_preflight.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_stabilized_q2_green_composition_preflight.py
```

## Boundaries

- This does not establish that the stabilized q2 candidate is the authoritative nonlinear classical Weyl BV operation.
- This does not establish an accepted q2 or q2/Green hash in classical import Gate A.
- This does not establish a flattened distribution kernel or effective numerical Green solver.
- This does not establish a uniform spectral-tail complexity bound.
- This does not establish recursive nonlinear Green trees or closure of q2 on two noncompact causal outputs.
- This does not establish q3 or higher L-infinity compatibility.
- This does not establish a time-slice SDR to the obstructed finite weights-2,3,4 receiver.
- This does not establish a weakest reverse-mathematical or choice-free proof of the analytic Green theorem.
- This does not establish a BRST-compatible Hadamard state, positivity, renormalized Lorentzian products, QME restoration, residual transfer, unitarity or a Lorentzian quantum theory.

## Next gate

Obtain authoritative q2 theory identity. In parallel, define domains for recursive causal trees and prove continuity/support when causal outputs re-enter q2; only after authoritative identity and those analytic closure checks may the strict route advance from first response toward interacting Hadamard/renormalized products and QME.
