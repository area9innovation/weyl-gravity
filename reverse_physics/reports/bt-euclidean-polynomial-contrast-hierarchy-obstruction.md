# BT polynomial-contrast hierarchy obstruction

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_POLYNOMIAL_CONTRAST_HIERARCHY_OBSTRUCTION_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`

Lifecycle:
`GENERIC_BAND_DIAMETER_TRANSPORT_OBSTRUCTED_FOUR_TORUS_COMPATIBILITY_GATE_OPEN`

## Result in ordinary language

The preceding high-contrast theorem shows that one enormous edge ratio cannot
hide a bad Bateman--Turok configuration.  It leaves a tempting next argument:
split a merely polynomial range of ratios into logarithmically many bands and
apply the tropical flow estimate to each band.

That graph-generic argument is false.  There is an exact family of positive
fields on longer and longer cycles for which:

- the largest neighboring-field ratio is only the integer (m);
- the cycle has (4m^4+2) vertices and diameter (2m^4+1);
- the normalized divergence cost of the positive main flow is at most
  (160m^{-6}); and
- the quotient made from the complete BT residual gradient is at most
  (1960m^{-6}) for (mgeq8).

Multiplying either coefficient by the diameter still tends to zero.  Positivity,
acyclic orientation, polynomial contrast, and logarithmically many ratio bands
therefore do not imply an absolute (2/operatorname{diameter})-type transport
bound.

This is a method obstruction on cycles.  It is **not** a counterexample on the
isotropic four-dimensional torus, not a failure of every torus-specific
estimate, and not a result about the actual interacting Gibbs (H^{-1})
moment.

## 1. Exact family

Fix an integer (mgeq2), and set

\[
 r=m^4,\qquad s={m-1\over r}.
\]

On either of two equal paths use the tent-shaped ratio list

\[
 z_i=1+s\min(i,2r-i),\qquad 0\leq i\leq2r.
\]

It starts at one, reaches (m), and returns to one.  Traverse the first
path with (z_0,ldots,z_{2r}), and traverse the second with
(z_{2r}^{-1},ldots,z_0^{-1}).  The two ratio products cancel exactly, so
the list defines a positive periodic field on

\[
 C_{4r+2}=C_{4m^4+2}.
\]

Its maximum unoriented edge ratio is exactly (W=m).  The number of dyadic
ratio bands is at most (1+lceil\log_2m\rceil), logarithmic in the cycle
volume.

## 2. Main positive-flow obstruction

Away from the two unit-ratio plateau edges, put the unnormalized positive
main flow

\[
 k_i=z_i^2
\]

on each side.  Its total mass and divergence energy are

\[
 K_m=2\sum_{i=1}^{2r-1}z_i^2,
\]

\[
 D_m=2\left[z_1^4+z_{2r-1}^4+
       \sum_{i=2}^{2r-1}(z_i^2-z_{i-1}^2)^2\right].
\]

At least (r) indices on either side obey (z_igeq m/2), hence

\[
 K_m\geq2r(m/2)^2={m^6\over2}.
\]

Also (z_1<2), and every adjacent squared-flow difference obeys

\[
 |z_i^2-z_{i-1}^2|\leq2ms.
\]

There are fewer than (2r) such differences on a side.  Therefore

\[
 D_m\leq4\,2^4+2(2r)(2ms)^2\leq80,
\]

and

\[
 {D_m\over K_m}\leq{160\over m^6}.
\]

Since (operatorname{diam}(C_{4m^4+2})=2m^4+1),

\[
 \operatorname{diam}(C_{4m^4+2}){D_m\over K_m}
 \leq {320\over m^2}+{160\over m^6}\longrightarrow0.
\]

Thus the positive-flow component alone already defeats a graph-generic
diameter-scale extension of the tropical integer-flow theorem.

## 3. Complete residual-gradient quotient

Let (q_j) be the complete traversal ratio list and define the exact cycle
objects

\[
 R_j=q_j+q_{j-1}^{-1}-2,
\]

\[
 J_j=R_jq_j-{R_{j+1}\over q_j},\qquad
 g_j=J_{j-1}-J_j.
\]

These are the BT residual, canonical current, and Euclidean action gradient on
the cycle.  Direct substitution on the affine and reciprocal-affine pieces,
including the four slope-change neighborhoods, gives the local bound

\[
 |g_j|\leq7ms=7m{m-1\over m^4}.
\]

The cycle has (4r+2leq5r) sites, so

\[
 \|g\|_2^2\leq5r(7ms)^2\leq245.
\]

For (mgeq8), both traversal halves contain at least (r) sites with a
residual contribution at least (m/2-2geq m/4).  Consequently

\[
 \|R\|_2^2\geq2r(m/4)^2={m^6\over8},
\]

and hence

\[
 \boxed{{\|g\|_2^2\over\|R\|_2^2}\leq{1960\over m^6}.}
\]

The complete-current diameter product is bounded by

\[
 {3920\over m^2}+{1960\over m^6}\longrightarrow0.
\]

This closes the possible objection that the reverse-current terms necessarily
restore a diameter-scale quotient.  No comparison with the cycle's much
smaller free bilaplacian scale is asserted.

## 4. Exact evidence and independent rail

The producer records complete rational fixtures for (m=2,3,4): every ratio,
flow norm, divergence norm, residual norm, gradient norm, quotient, and
pointwise maximum is computed with `Fraction` arithmetic.  The independent
verifier does not import the producer.  It reconstructs the complete cycles
from the family definition, checks the three stored fixtures byte-for-object,
and extends the exact rail to (m=5,8).  It separately checks the elementary
all-(m) mass, divergence, residual, norm, and diameter implications after the
local-calculus lemma.

Mutation tests require the receiver to reject changes to a predecessor hash,
an exact norm, the quotient constant, the four-torus disposition, the
dependency tags, and the certificate's self-check ledger.

## 5. What changes and what remains open

The next viable argument cannot use a graph-generic diameter bound separately
on every positive ratio band.  It must use structure absent from a cycle:

1. isotropic four-torus level-set or isoperimetric geometry;
2. compatibility between bands through the single scalar field;
3. the reverse-current terms rather than discarding them; and
4. a later transfer into the connection-corrected Witten form or the actual
   normalized Gibbs observable.

The sharp next gate is therefore either a torus-scale complete-current
estimate or a torus-compatible polynomial-contrast low-Rayleigh family.

This certificate does not establish:

- collapse relative to the free bilaplacian scale on cycles;
- a polynomial-contrast counterexample on isotropic four-tori;
- failure of every torus-specific flow, corrector, or Witten estimate;
- boundedness or divergence of the interacting (H^{-1}) moment;
- tightness, a continuum Euclidean measure, or continuum OS reconstruction;
- a Born rule or Krein reconstruction; or
- anything `LORENTZIAN-CAUSAL`.

## Verification

Run sequentially under the 500 MB cap:

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_polynomial_contrast_hierarchy_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_polynomial_contrast_hierarchy_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_polynomial_contrast_hierarchy_obstruction
```
