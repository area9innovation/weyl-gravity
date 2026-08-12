# Hardy's continuity axiom: the finite-discrete step

## Result

`FOUNDATIONAL_HARDY_CONTINUITY_KN_AUDIT_V1` audits one load-bearing step of
Hardy's operational reconstruction: Axiom 5 rules out `K=N`, because a finite
set of pure classical states cannot contain a continuous reversible path
between two distinct states.

The dependency is `REPRESENTATION_SENSITIVE`:

```text
path supplied with uniform modulus  -> RCA_0 SUFFICIENT_OVER_BASE
pointwise continuity alone          -> modulus extraction is an extra theorem
```

The physical axiom does not imply `RCA_0`, `WKL_0`, compactness, or a
set-existence principle.  It supplies path existence inside the chosen
mathematical representation.  No reversal is proved.

## Coded proof

For `K=N`, the normalized pure states are the `N` standard probability basis
vectors.  In `l1` distance distinct pure states are separated by exactly two.
Suppose a path `gamma:[0,1]->P` includes a uniform modulus `mu`, so that

```text
|s-t| < 2^-mu(0)  implies  distance(gamma(s),gamma(t)) < 1.
```

Partition the interval with mesh denominator `2^(mu(0)+1)`.  Adjacent images
are less than one apart; the separation-two fact forces them to be equal.
Bounded induction along the mesh makes both endpoints equal, contradicting
the distinct endpoints demanded by Axiom 5.

This uses finite rational vectors, a supplied modulus, a rational mesh and
bounded equality induction.  `RCA_0` is a sufficient upper bound for this
coded route, not the weakest-base claim.  The independent checker exercises
42 combinations of `N=2,...,8` and modulus values zero through five.

## Why the formulation matters

Hardy's paper says “continuous”; it does not specify a reverse-mathematical
code or a modulus.  If the formalization starts only with pointwise
continuity, obtaining a uniform modulus on `[0,1]` uses compactness machinery.
That extraction is `USED_ONLY_IF_MODULUS_NOT_SUPPLIED` and its exact strength
is deliberately not classified by this certificate.

Supplying the modulus is an `AVOIDED_BY_REFORMULATION` route for the selected
finite-discrete conclusion.  It is legitimate only if the strengthened data
is stated explicitly; it cannot be silently read into every physical use of
the word continuous.

## Dependencies not used here

The extreme-value theorem, extrema of general convex bodies, the later
compact Lie group argument for the `N=2,K=4` state space, matrix
diagonalization, Hilbert-space spectral theory, and infinite-dimensional
completion are `NOT_USED_BY_SELECTED_STEP`.  They require separate audits.

This narrow result neither derives `K=N^2` nor reconstructs quantum theory.
It does not show empirical superiority of Axiom 5, classify continuous-
dimensional systems, or establish anything `LORENTZIAN-CAUSAL`.

## Source and next gate

The source is Lucien Hardy, *Quantum Theory From Five Reasonable Axioms*,
[arXiv:quant-ph/0101012](https://arxiv.org/abs/quant-ph/0101012), especially
Axiom 5 and the `K=N` exclusion in Section 8.1.

The next nontrivial reconstruction audit is the later Bloch-ball step.  It
uses compact-group representation and convex geometry and must not inherit
the weak bound proved for this finite-discrete lemma.
