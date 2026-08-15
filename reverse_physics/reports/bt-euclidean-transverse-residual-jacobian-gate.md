# BT transverse residual-Jacobian gate

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_TRANSVERSE_RESIDUAL_JACOBIAN_GATE_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

## Result

The residual-coordinate programme exposes a plausible entropy mechanism that
had not yet been separated cleanly.  Remove the constant mode and the complete
lowest cosine--sine phase plane from the six-cycle.  If \(B\) spans the
remaining three-dimensional space and

\[
 L_\psi=P_H D r(\psi),
\]

then the transverse volume expansion is

\[
 \mathcal J_E(\psi)^2
 =\frac{\det(B^TL_\psi^TL_\psi B)}{\det(B^TB)}.
\]

At the vacuum this equals \(1296=36^2\).  Exact searches suggested that the
vacuum might be the global minimum, which would prevent this transverse
Jacobian from creating an entropic preference for displaced lowest modes.

Two attractive proofs of that statement do **not** work.

1. Before the required output centering, the Laurent expansion has 296 terms,
   all positive.  Its coefficient-weighted exponent barycenter is zero, so
   weighted AM--GM proves the unprojected vacuum minimum.  For the physical
   centered map \(P_HDr\), the polynomial instead has 1293 terms: 951 positive
   and 342 negative.  Their coefficient sums are \(1602\) and \(-306\).
   Centering preserves the vacuum value \(1296\), but destroys the
   coefficientwise AM--GM proof.
2. The squared centered Jacobian is not globally convex in log-field
   coordinates.  At

   \[
   \psi=(1,-1,2,-2,-2,2)\log2,
   \]

   the order-five leading principal minor of its exact Hessian is

   \[
   -\frac{
   370265897082480966556198424275431024210364253456527090595872621
   }{
   133697524242821069689105416192
   }<0.
   \]

   Therefore cyclic translation symmetry cannot be combined with ordinary
   Jensen convexity to prove the minimum.

These are proof-architecture obstructions, not a counterexample to the
Jacobian inequality itself.

## What remains positive

The vacuum is an exact strict local minimum modulo constant scale.  The
Fourier eigenvalues of the Hessian of \(\log\mathcal J_E\) there are

\[
 0,\quad \frac23,\quad \frac{41}{24},\quad \frac{10}{3},
 \quad \frac{41}{24},\quad \frac23.
\]

An exact finite audit also evaluated every mean-zero dyadic point

\[
 \psi_i=n_i\log2,\qquad n_i\in[-3,3]\cap\mathbb Z.
\]

There are 9331 such points.  The unique minimum in this box is the vacuum,
with value \(1296\).  This is exact finite evidence and is deliberately
labelled `EXACT_FINITE_AUDIT_NOT_GLOBAL_PROOF`.

## Meaning for the continuum programme

The calculation identifies a real, sharply stated inequality rather than a
new physical dimension.  A global inequality
\(\mathcal J_E(\psi)\geq\mathcal J_E(0)\) would control one transverse entropy
factor in residual coordinates.  It would still not control the normalized
level-set area or the annealed motion of the conditional center, so it would
not by itself prove the lowest-mode or interacting \(H^{-1}\) bound.

The next plausible exact route is a regrouping by oriented forests or
effective-resistance minors.  The all-minors matrix-tree theorem interprets
non-principal Laplacian minors as signed forest sums; that is the right
structure for investigating whether the 342 negative Laurent coefficients
cancel inside larger sign-definite blocks.  See S. Chaiken,
[*A Combinatorial Proof of the All Minors Matrix Tree
Theorem*](https://doi.org/10.1137/0603033), SIAM J. Algebraic Discrete Methods
3 (1982), 319--329.  This literature theorem motivates the next calculation;
it is not imported as proof of the BT inequality.

If no such regrouping exists, the alternative is a rigorously bounded search
for a positive-field counterexample outside the finite dyadic box.  Either
outcome would decide whether this Jacobian route deserves further effort.

No normalized lowest-mode marginal, interacting \(H^{-1}\) estimate,
continuum measure, continuum OS theorem, Born rule, Krein reconstruction, or
`LORENTZIAN-CAUSAL` statement is established.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_transverse_residual_jacobian_gate.py --check
ulimit -v 500000; mise x python@3.12 -- python3 reverse_physics/verify_bt_euclidean_transverse_residual_jacobian_gate.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_transverse_residual_jacobian_gate
```

## Verification receipt

- Tier 0 and scoped Tier 1 results are recorded in the certificate committed
  with this report.  The planning import accepted 1,687 nodes with zero invalid
  items and zero malformed events in 6.58 s.  A first Git status inherited the
  Python memory cap and failed while reserving threaded `lstat`; the Git-only
  scoped diff check was rerun without that cap and passed.
- The producer and tests use only exact `Fraction` arithmetic.  The independent
  verifier derives both Laurent polynomials with SymPy and then checks their
  hashes, moments, exact nonconvexity witness, and the complete finite dyadic
  audit.  The producer passed in 14.31 s at 21,600 KB peak RSS, the verifier
  passed in 22.92 s at 81,308 KB, and seven tests passed in 15.17 s at 21,676
  KB.  The verifier's first 0.56 s invocation stopped on a self-matching
  non-import guard; that guard was replaced by an AST check, the verifier was
  rerun from the start, and the failed invocation is not counted as a pass.
- The 2.98 s advisory Science Forge wrapper exited zero, but its bridge audit
  failed closed because the external `bp2transformer` Python lacks `sympy`;
  the census also reported baseline drift (1,844 certificates versus 976).
  Those are advisory failures/drift, not evidence for this result.
- Tier 2 is not required because the imported content-addressed residual and
  full-phase certificates are unchanged and are checked by hash.
- Tier 3 is not required because this checkpoint promotes no continuum,
  \(H^{-1}\), reconstruction, QME, freeze, release, or Lorentzian lifecycle.
- Paper 21 is not updated at this checkpoint: the result narrows a proof route
  but establishes no paper-level continuum theorem, and that paper has
  substantial concurrent edits owned by the foundations team.
