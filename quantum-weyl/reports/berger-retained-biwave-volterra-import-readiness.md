# Berger retained biwave: Volterra import readiness

The retained metric block and its twenty-row companion are now checked against
the certified helical derivation (D=e_0), not merely against the unary BV
contraction. Exact PBW arithmetic gives

\[
[D_{10},\Box_2]=[D_{10},V_2]=[D_{10},A_{10}]=0,
\qquad [D_{20},\mathcal C_{20}]=0.
\]

Both solution and source graph maps, and the graph homotopy, are exactly
(D)-equivariant. The formal-adjoint bundle is also explicit:

\[
A_{10}^{\sharp}=(\Box_2^{\sharp})^2+V_2^{\sharp},
\qquad
\mathcal C_{20}^{\sharp}=
\begin{pmatrix}\Box_2^{\sharp}&V_2^{\sharp}\\-I&\Box_2^{\sharp}\end{pmatrix}.
\]

This removes two avoidable ambiguities from the incoming causal theorem. It
does not construct a cyclic companion pairing, and formal adjoints alone do
not prove advanced/retarded cyclic adjointness.

The classical Volterra package is pinned at commit `512545b7`. This is the
first commit where its producer reproduces the committed certificate; the
initial `c2f4bf65` certificate carried a dependency absent from that commit's
producer. Pinning and structural reproduction pass, but analytic import is
rejected fail-closed.

Eight defects prevent promotion:

1. `FUNCTIONAL-ANALYTIC` is outside the frozen dependency-tag vocabulary.
2. No strict Draft 2020-12 source schema exists at the pinned commit.
3. A single `R_pm` node conflates the distinct solution and source resolvents
   `(I+G0 N)^-1` and `(I+N G0)^-1`.
4. The formal-adjoint identity is malformed and is not bound to the declared
   metric/antifield pairing.
5. The analytic checks are unreferenced booleans rather than proof artifacts.
6. The source has no content-addressed manifest or verification-time receipt.
7. The factorial bound is stated only for `(G0 N)^n`, not for both typed
   resolvents.
8. The graded energy spaces and derivative mapping properties are
   underspecified.

Consequently no advanced or retarded metric Green operator is imported, and
the downstream 26- and 54-row causal homotopy claims remain unavailable to the
quantum programme. The exact PBW work here remains valid: it independently
proves the graph, formal-adjoint bundle, and (D)-equivariance compatibility
needed by a repaired analytic theorem.

The acceptance route, once repaired, is the retained companion Volterra
resolvent followed by exact graph pullback. The old raw rank-one clock
extension and any arbitrary-source metric-cone `G13` theorem are explicitly
rejected by the certified raw principal-symbol obstruction.

```text
PYTHONPATH=quantum-weyl python -m lorentzian.retained_biwave_volterra_import_readiness_certificate --check
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_retained_biwave_volterra_import_readiness.py -v
```

Verification receipt (2026-07-16): Tier 1 passed in 13.477 s. The affected
source/companion chain passed in 17.22 s with
`berger_retained_biwave_volterra_resolvent.py --check --guards` and the
companion certificate check. Tier 3 was not run because this audit rejects a
promotion and changes no shared algebra or freeze state.
