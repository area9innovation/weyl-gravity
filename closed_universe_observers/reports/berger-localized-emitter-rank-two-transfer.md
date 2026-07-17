# Localized-emitter rank-two transfer

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`.

Two compact-time conserved currents can be localized without computing a
Berger Green kernel.  On a Cauchy `S3`, `H1=H2=0`.  Write the C-G4 cosine
mode constraint data using spatial potentials, multiply those potentials by
a bump that is one on the causal predecessor of a detector window, and take
their exterior derivatives again.  The data remain exactly constraint
satisfying, are supported in a proper local region, and agree with the C-G4
data wherever the detector can depend on them.  Domain-of-dependence
uniqueness therefore makes the localized solution equal the C-G4 solution
on that detector window.

A time cutoff produces

```text
J_a = delta d(chi_a A_a),        delta J_a=0.
```

The first switch is immediately before `D0`.  The second lies in the exact
gap `(13/48,23/48)`, after `D0` and before `D1`.  Retarded support makes the
upper-right response vanish.  Agreement with the C-G4 cosine field gives

```text
M = [[-beta S0, 0], [mu, beta C1]],
det M = -beta^2 S0 C1 = -40 S0 C1/9 != 0.
```

Both `S0` and `C1` are strictly positive because the corresponding detector
phases lie in `(0,pi/2)` and the pinned normalized-profile theorem fixes
nonnegative, unit-normalized detector bumps.  The unrestricted cross response
`mu` cannot change the determinant.  Thus the two localized signals produce
two distinguishable persistent records.

These are receiver-adjacent local emitter worldtubes.  This does not yet
realize both signals at the original common Hopf emitter at clock zero, add
dynamical emitter recoil, prove finite-parameter 84-row Green hyperbolicity,
or construct a quantum observer algebra.
