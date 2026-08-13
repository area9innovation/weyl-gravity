# BT positive-local real-structure dichotomy

**Certificate:**
`REVERSE_PHYSICS_BT_POSITIVE_LOCAL_REAL_STRUCTURE_DICHOTOMY_V1`

**Dependency tag:** `LOCAL-ALGEBRAIC`

**Lifecycle:** `CLASSIFIED`

## Result

The positive Hilbert-space assumptions used by the conditional local
quadrupole theorem cannot preserve all of the public Bateman--Turok free
two-field data.  There are two exact alternatives.

1. Keep the public Krein adjoint, under which \(\Omega\) and \(\Upsilon\) are
   individually real fields.  Their public cross Wightman matrix is
   indefinite and cannot be a positive-Hilbert vacuum two-point matrix.
2. Use the public fundamental symmetry \(\kappa\) to define a positive Hilbert
   product.  This succeeds algebraically, but changes the adjoint to
   \(\Omega^*=\Upsilon\).  The two public real fields become a mutually
   adjoint complex pair.

The second alternative is a viable mathematical carrier, not a contradiction.
It gives an exact physical-observable gate: a Krein-selfadjoint operator is
also self-adjoint in the positive Hilbert product if and only if it is
ghost-even.  Its ghost-odd part becomes Hilbert-selfadjoint after multiplication
by \(i\).

This does not prove Eq. (19).  It identifies a missing condition shared by the
Eq. (19) and local-detector routes: Krein-null negative-charge terms are not
automatically null in the positive Hilbert topology.

## Exact positive-type obstruction

Choose a positive-frequency test packet \(f\) for which the ordinary massless
scalar pairing is nonzero,

\[
 w(f,f)>0.
\]

The public two-field Wightman matrix factors into this positive scalar and the
species Gram

\[
 G=\begin{pmatrix}0&1\\1&0\end{pmatrix}.
\]

The exact combinations

\[
 t=(1,1),\qquad x=(1,-1)
\]

obey

\[
 t^T Gt=2,\qquad x^T Gx=-2,
 \qquad \det G=-1.
\]

Thus \(G\) has signature \((1,1)\), not positive type.  There is an even
shorter positive-Hilbert contradiction.  If \(\Omega(f)\lvert0\rangle\) and
\(\Upsilon(f)\lvert0\rangle\) were vectors in a positive Hilbert space and the
two fields were individually Hermitian, the two zero diagonal Wightman entries
would say that both vectors have zero norm.  Both vectors would then vanish,
so their cross product would vanish.  The public cross entry is instead
\(w(f,f)>0\).

Therefore no positive Hilbert vacuum representation can retain simultaneously

- both fields as individually Hermitian real fields; and
- the nonzero public cross Wightman matrix.

The statement is scoped to preservation of those data.  It does not rule out
a different adjoint or a positive completion with different observables.

## What \(\kappa\)-Hilbertization changes

In the ordered \((\Omega,\Upsilon)\) species basis, the public fundamental
symmetry is exactly

\[
 \kappa=G,\qquad \kappa^2=I.
\]

If \([u,v]=u^\dagger Gv\) denotes the Krein product, the associated positive
product is

\[
 (u,v)_\kappa=[u,\kappa v],
 \qquad G\kappa=I.
\]

Let \(A^\sharp\) be the Krein adjoint and \(A^*\) the positive-Hilbert
adjoint.  They are related by

\[
 A^*=\kappa A^\sharp\kappa.
\]

Since ghost parity exchanges the two public fields,

\[
 \Omega^*=\Upsilon,\qquad \Upsilon^*=\Omega.
\]

Equivalently, with

\[
 T={\Omega+\Upsilon\over2},\qquad
 X={\Omega-\Upsilon\over2},
\]

one obtains

\[
 T^*=T,\qquad X^*=-X,\qquad (iX)^*=iX.
\]

The positive carrier therefore exists algebraically.  Its real observables are
not the two original real Krein fields: \(\Omega\) and \(\Upsilon\) are a
complex adjoint pair, or equivalently the ghost coordinate requires the
imaginary contour \(iX\).

## Exact observable-parity theorem

Let \(A^\sharp=A\).  Split it into ghost parity components,

\[
 A_{\rm e}={A+\kappa A\kappa\over2},\qquad
 A_{\rm o}={A-\kappa A\kappa\over2}.
\]

Then

\[
 A_{\rm e}^*=A_{\rm e},\qquad
 A_{\rm o}^*=-A_{\rm o},\qquad
 (iA_{\rm o})^*=iA_{\rm o}.
\]

In particular,

\[
 \boxed{A^*=A\quad\Longleftrightarrow\quad
        \kappa A\kappa=A}
\]

for a Krein-selfadjoint \(A\).  This is the exact extra real-structure
condition required before the previous spectral-truncation theorem can be
read as a positive-Hilbert local detector construction.

For bounded local operators the parity split remains local if \(\kappa\) acts
as an internal automorphism preserving each local algebra.  For the unbounded
compact density one must additionally prove a common \(\kappa\)-invariant
domain and affiliation.  Neither point is supplied merely by an angular
exchange symmetry.

## Hilbertization does not preserve the weak-ghost Born functional

The distinction is not only terminology about adjoints.  It changes the norm
of the nonzero negative-charge remainder used in the weak-ghost construction.

Take the exact two-species fixture

\[
 B=I,\qquad
 Q=E_{21}=\begin{pmatrix}0&0\\1&0\end{pmatrix},
 \qquad A=B+Q.
\]

Here \(Q\) maps the positive-charge species direction into the
negative-charge direction.  Direct exact calculation gives

\[
 Q^\sharp=Q,\qquad Q^2=0,
\]

and hence

\[
 \operatorname{tr}(Q^\sharp Q)=0,
 \qquad
 \operatorname{tr}(B^\sharp Q)=0.
\]

Thus \(Q\) is nonzero but null and orthogonal in the generalized Krein Born
functional.  The generalized process weight is

\[
 \operatorname{tr}(A^\sharp A)=2.
\]

The positive-Hilbert adjoint is instead

\[
 Q^*=E_{12},
\]

so

\[
 \operatorname{tr}(Q^*Q)=1,
 \qquad
 \operatorname{tr}(A^*A)=3.
\]

Therefore the fundamental symmetry supplies a positive topology, but it does
not turn the public generalized Born rule into the ordinary Hilbert Born rule
when a nonzero weak-ghost remainder is present.  This exact fixture does not
challenge the consistency of the generalized rule; it proves that the two
operational prescriptions are different.

## Consequence for Eq. (19)

The advertised form of Eq. (19) is

\[
 R_tP_\chi^{(\phi)}R_t^\dagger
 =P_\chi^{(\Omega\Upsilon)}+Q_\chi^{(\Omega\Upsilon)},
\]

where the first term is neutral and ghost-even, while the second contains
only negative charges and is declared null in the generalized Krein trace.

The neutral term is exactly the right kind of candidate for an ordinary
positive-Hilbert observable.  The present calculation shows why the remainder
cannot be silently ignored in a positive local-net reconstruction:
Krein-nullity does not imply zero positive-Hilbert norm.

A physical positive-Hilbert completion therefore needs one of the following
additional results:

1. prove that the relevant \(Q_\chi\) vanishes;
2. construct a local, dynamics-compatible quotient that removes it;
3. construct a local conditional expectation onto the ghost-even algebra and
   prove that it preserves all declared physical probabilities; or
4. retain the generalized indefinite Born rule as the operational theory,
   without presenting the auxiliary Hilbert product as its replacement.

Eq. (19) by itself would classify the charge support, but a positive local
physical interpretation also owes this quotient or equivalence theorem.

## Consequence for the quadrupole detector

The compact quadrupole certificate proves angular trace-freeness and a nonzero
higher-order response.  Its word ``exchange-even'' refers to exchange of the
two momentum daughters.  It does not certify invariance under the internal
BT ghost parity \(\kappa\).

The next calculation is therefore finite and sharply posed:

\[
 D_{\rm e}={D+\kappa D\kappa\over2},\qquad
 D_{\rm o}={D-\kappa D\kappa\over2}.
\]

On a common invariant packet core, test whether \(D_{\rm e}\) retains

\[
 \langle0,D_{\rm e}X_2\rangle=0,
 \qquad
 \langle0,D_{\rm e}X_4\rangle\ne0.
\]

If it does, the positive-local balanced contrast has the correct real
structure.  If the response sits in the odd part, test \(iD_{\rm o}\) with the
corresponding phase calibration.  If neither projected channel retains the
selection, the previous balanced detector remains only a Krein-formal
construction.

## Claim boundary

This certificate does not establish a positive BT Haag--Kastler net,
Reeh--Schlieder property, self-adjoint affiliation, invariant domain, Eq. (19),
physical quotient of its \(Q\) sector, complete Born/scattering theory,
metric BV--BRST transfer, QME restoration, or anything
`LORENTZIAN-CAUSAL`.  It does not claim that \(\kappa\)-Hilbertization is
impossible or that the public generalized Born rule is inconsistent.  No
literature-priority claim is made.

The public source was checked on 2026-08-13 and remained arXiv:2607.00096v1;
the detailed proof cited for Eq. (19) was still listed as forthcoming.

## Verification

The producer performs 38 exact checks.  The independent verifier reconstructs
the species Gram, its negative direction, the \(\kappa\)-Hilbert Gram, both
adjoints and both Born weights without importing the producer.  The mutation
suite contains 50 tests.  No floating-point arithmetic enters any claim.

Commands:

```text
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_positive_local_real_structure_dichotomy.py --check
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_positive_local_real_structure_dichotomy.py
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_positive_local_real_structure_dichotomy
```

## Verification receipt

All Python, TeX and Tier-3 processes ran sequentially under a 500000 KiB
virtual-memory limit; no out-of-memory event occurred.

- Tier 0 passed: all three changed Python files compiled, all four structured
  planning/schema/certificate files parsed, and the scoped diff check passed.
- The producer passed 38/38 exact checks in 0.03 s wall time at 16752 KiB
  peak resident memory.
- The method-distinct verifier passed 48/48 checks in 0.07 s at 23908 KiB
  peak.  It reconstructs the negative species direction, positive
  \(\kappa\)-Gram, both adjoints and both Born weights without importing the
  producer.
- The mutation suite passed 50/50 tests in 0.16 s wall time at 24968 KiB
  peak (0.087 s unittest time).
- Papers 05 and 06 each compiled repeatedly with halt-on-error until
  cross-reference output stabilized.  Their timed passes both took 0.51 s,
  at 50988 KiB and 50928 KiB peak, respectively.  Paper 05 is 74 pages and
  720300 bytes; its final SHA-256 is
  0acae819d38e4e55a31b09fd12508f20a352e87867516378207c4bf2bda970e1.
  Paper 06 is 64 pages and 681194 bytes; its final SHA-256 is
  0be8c7a59dab899e249fc08bd83aa38ea10542b02620e10d7941ffd3b0f94cbc.
  Neither log has undefined references or citations.  The existing six
  Paper-05 and two Paper-06 overfull boxes remain; the new Paper-06 box found
  on the first pass was removed.
- Tier 3 ran 2883 tests in 803.978 s (13:25.00 wall, peak 391604 KiB).
  All 50 new tests passed.  The repository remains fail-closed with 32
  failures and 9 skips.  The sorted full failure-name list has SHA-256
  aa3bafce92f854ff187965026231c88dd3913d490c610a32a942eee59b68f386,
  exactly matching the predecessor baseline.  These are therefore recorded
  pre-existing failures, not a passing rail and not a regression hidden by
  the new certificate.
- Science Forge planning import wrote 1555 nodes with zero invalid work items
  and zero malformed events in 5.98 s, peak 298864 KiB.
- The advisory Science Forge shadow rail inventoried 1617 certificates and
  1395 verifiers in 1.97 s, peak 345612 KiB.  It again reported the known
  Forge-stdlib mismatch and fail-closed E9118 bridge audit, plus corpus
  drift from the 2026-07-19 baseline.  Its advisory wrapper exited zero, but
  those findings establish no verification pass.  Diagnostics are preserved
  under /tmp/bt-positive-local-shadow.rKt8m2.

The generated certificate SHA-256 is
650b7b246c8cb4cc4dd677271786d0150d6742eccada33f74801108aa98dfe33.
