# BT canonical endpoint underdetermination

**Result:** `CLASSIFIED`

The formal perturbative BT range projection is the identity, but that does
not determine the finite endpoint extension.  The preceding distribution
certificate found three independent reflection-even endpoint jets,

\[
\delta_0+\delta_1,
\qquad \delta'_0-\delta'_1,
\qquad \delta''_0+\delta''_1.
\]

To test whether canonical algebra alone removes this freedom, place those
three formal directions beside one hard channel and define

\[
 K(u)=\begin{pmatrix}0&-u^T\\u&0_3\end{pmatrix},
 \qquad
 P(\epsilon)=e^{\epsilon K}P_0e^{-\epsilon K}.
\]

For arbitrary (u=(u_0,u_1,u_2)), the generator is skew, similarity preserves
the canonical commutators, and the transported projector remains idempotent
and trace preserving.  Expanding through second order gives

\[
 P_2|_{\rm hard}=-u^Tu,
 \qquad
 \operatorname{tr}P_2|_{\rm endpoint}=+u^Tu.
\]

Therefore the listed CCR, projector, trace, and exchange identities admit a
three-parameter countermodel to uniqueness.  They do not select the desired
(1/48).  That value is compatible—for example
(u=(\sqrt3/12,0,0)) has (u^Tu=1/48)—but choosing it without another condition
would be fitting the answer.

This is deliberately an underdetermination witness.  It does **not** prove
that every (u) is realized by the actual BT continuum map.  That map is the
missing datum: the deferred construction around Eq. (19), or an independently
justified physical resolution/renormalization prescription, must say which
endpoint extension is realized.  The complete real--virtual quotient trace,
finite virtual terms, positivity, and physical NLO probability remain open.

Verification:

```text
ulimit -v 500000; python3 reverse_physics/bt_canonical_endpoint_ambiguity.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_canonical_endpoint_ambiguity.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_canonical_endpoint_ambiguity
```

This exact `LOCAL-ALGEBRAIC`/`REDUCED-MODE` classification makes no
`LORENTZIAN-CAUSAL`, gravitational, convergence, or literature-priority claim.
Primary source: [Bateman--Turok](https://arxiv.org/abs/2607.00096), Eq. (19)
and Appendix C.

## Verification receipt

All commands ran on 2026-08-10 with `ulimit -v 500000`.

- Producer exact reproduction: **PASS**, 13/13 checks, 0.07 s,
  20,916 KB maximum resident set.
- Method-distinct verifier: **PASS**, 7/7 checks, 0.12 s,
  30,276 KB maximum resident set.
- Scoped unit and mutation tests: **PASS**, 5/5 tests, 0.64 s,
  30,232 KB maximum resident set.
- Paper 05 and Paper 06: **PASS**, two `pdflatex` passes each; final passes
  took 0.49 s/51,088 KB and 0.53 s/50,628 KB.  Paper 05 retains three
  pre-existing small overfull boxes; Paper 06 has none.
- Advisory `ci/science-forge-shadow.sh`: **NOT PASS**.  Two CBP discovery
  subprocesses aborted under the mandatory memory ceiling; the unchanged
  audit was interrupted after 109.05 s instead of relaxing the cap.  This is
  not reported as verification.

Tier 2 was not run because this isolated classification consumes unchanged,
content-addressed inputs and changes no shared operator, schema, or generated
artifact used by an upstream certificate chain.  Tier 3 was not run because
there is no freeze, theorem-lifecycle promotion, release, or shared-core
algebra change.  The exact staged diff and input hashes are inspected at the
commit gate.
