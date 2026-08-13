# Fully rearranged BT q10 object ledger

**Certificate:** `REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_OBJECT_LEDGER_V1`

**Tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. **Lifecycle:** `CLASSIFIED`.

## Exact decomposition

After the exact q9 selection theorem,

\[
Y=\lambda^4y_4+\lambda^5y_5+\lambda^6y_6+O(\lambda^7)
\]

gives the first unresolved coefficient

\[
\boxed{q_{10}=\langle y_5,y_5\rangle
 +2\operatorname{Re}\langle y_4,y_6\rangle.}
\]

This is a classification, not a computed coefficient.

## Connected graph exhaustion

For six external legs, the identity
\(d_\lambda=E+2L-2\) makes every coupling-degree-six connected graph
one-loop.  Solving \(V_3+2V_4=6\) gives exactly

\[
(V_3,V_4,I)=(6,0,6),(4,1,5),(2,2,4),(0,3,3).
\]

Thus the renormalized loop calculation has four vertex-count classes:
\(V_3^6,V_3^4V_4,V_3^2V_4^2,V_4^3\).  Each still needs symmetry factors,
finite-time kernels, local counterterm classification and a scheme/scale
ledger.

## What support removes

Every externally disconnected six-leg partition continues to vanish on the
fully rearranged packet supports.  The argument is order independent because
each component retains its momentum-conservation distribution and
distributional derivatives do not enlarge support.

Vacuum components are different: a vacuum factor multiplying a connected
external block has the same external support.  It must be treated through
normalized evolution or cumulants and is not silently deleted here.

## Complete missing ledger

The calculation still requires:

- the renormalized connected order-six six-leg kernel;
- the full \(y_5=T_5\psi_0+T_4\psi_1+\) detector correction and its norm;
- the full \(y_6\), including \(T_6\psi_0,T_5\psi_1,T_4\psi_2\) and detector
  corrections;
- vacuum/survival normalization;
- total ghost-\(\kappa\) fixedness of the assembled q10 effect.

Accordingly q8 is common-Born and computed, q9 is exactly zero, and q10 is
only `CLASSIFIED`.  No sign, positivity, Eq. (19), gravity, or Lorentzian
claim follows.

## Next calculation

Start with the \(V_4^3\) one-loop six-leg block: among the four exhaustive
classes it has the fewest vertices and internal lines.  Renormalize and pair
it with the fully rearranged compact packets, retaining its counterterm and
scheme dependence.  It is one block of q10, not the complete coefficient.

## Verification

All Python ran sequentially under the 500 MB virtual-memory ceiling.

- Tier 0 passes: producer, verifier and tests compile; all changed JSON parses;
  the strict Draft-2020-12 schema and certificate validate; an injected
  property is rejected; scoped `git diff --check` is clean.
- Producer: `18/18`, `0.25 s`, `65420 KiB`. Independent verifier: `23/23`,
  `0.24 s`, `65000 KiB`. All `20` mutation tests pass in `0.030 s`
  (`0.28 s` wall), `65720 KiB`.
- The four direct predecessor producer/verifier pairs pass. The eight-command
  affected Tier-2 chain took `0.82 s` at `65716 KiB`.

Tier 3 is unnecessary because this `CLASSIFIED` ledger changes no paper
theorem, shared operator, mathematical input used by another certificate,
lifecycle promotion, freeze, QME state, or causal claim. Papers V/VI are not
updated: the q10 coefficient remains uncomputed.
