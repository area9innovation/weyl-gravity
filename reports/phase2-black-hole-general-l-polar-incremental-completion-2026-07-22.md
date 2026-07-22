# Phase 2 polar incremental completion: canonical log-free frontier

## Outcome

The exact incremental architecture removes the former depth-2 computational
wall.  For each of the three zero-rate and three oscillatory generic-polar
Bach-carrier powers, it constructs a canonical log-free sourced metric jet
through the conservative depth required by the seven original Ricci rows.
Every coefficient is exact over

\[
\mathbb Q(i)(\Lambda,\omega),\qquad
\Lambda=\ell(\ell+1),\quad \ell\ge2,\quad \omega\in\mathbb R\setminus\{0\},
\]

with Schwarzschild mass normalized to \(M=1\).  The metric depths are
\(3,4,5\) for branch indices \(0,1,2\), and each carrier jet is four orders
deeper.  Direct substitution independently verifies all seven rows

\[
vv, vr, rr, vx, rx, \mathrm{angP}, \mathrm{angW}
\]

through the declared metric depth.

This is a partial exact theorem, not the requested EE/EX/XX current theorem.

## Exact affine witnesses

The producer does not form one global multivariate RREF.  At each radial
order it keeps the old homogeneous freedom, adds the four new metric
coefficients, and solves the resulting compact affine system.  Each branch
artifact serializes:

- the carrier and metric power conventions and field-axis order;
- the compact augmented matrix and its exact RREF at every order;
- pivots, rank, nullity, a particular solution, and a nullspace basis;
- the final affine splitting and its canonical zero-free-parameter
  representative;
- the complete carrier and metric jets consumed by the check;
- the seven direct residual intervals; and
- the exact pivot-denominator factors.

The independent verifier does not import the recurrence producer.  It
recomputes every compact RREF and freshly reconstructs the committed v1 Ricci
rows before substituting the serialized carrier and metric jets.

## Pivot walls

No denominator appearing in these six constructed representatives vanishes
on the declared physical domain.  Besides rational units, the factors are
among

\[
\Lambda,\qquad \Lambda-2,\qquad \Lambda-3,\qquad \omega,
\]

two simple complex factors whose imaginary parts are nonzero for real
\(\omega\ne0\), and one larger factor \(\Delta\).  Writing
\(x=\omega^2>0\),

\[
\operatorname{Im}\Delta
=12\omega(\Lambda-128x^2-24x-3).
\]

On the only possible imaginary-zero locus,

\[
\operatorname{Re}\Delta
=128x^2(16384x^4+6144x^3+1088x^2+112x+1)>0.
\]

Thus \(\Delta\) is also a physical nonwall.

## The old oscillatory logarithm

The v1 depth-2 pilot reported a logarithm for oscillatory branch 1.  A fresh
reconstruction shows that its carrier agrees with the extendible carrier at
orders \(n=0,1\), but differs at its terminal \(n=2\) coefficient.  Testing
that terminal coefficient against the next carrier recurrence produces the
left-null obstruction

\[
3\Lambda-48\omega^2+15+12i\omega.
\]

Its imaginary part is \(12\omega\), so the v1 terminal jet is nowhere
extendible for real \(\omega\ne0\).  The old logarithm is therefore typed as

```text
NONEXTENDIBLE_SHALLOW_SOURCE_ARTIFACT
```

rather than evidence for an extendible logarithmic branch.  The present
result still does not claim an all-order log-module classification.

## Why the current theorem remains open

The universal symbolic-\(\Lambda\) Lee--Wald slice current remains imported from v1,
but a physical EE/EX/XX table requires more than one representative from each
sourced affine class.  The next exact object must supply:

1. the complete extendible resonant/log module;
2. the complete rate-sector homogeneous Einstein basis, independently
   compatibility-projected;
3. the complete rate-sector additional basis and its representative-shift
   law;
4. the branch Gram/congruence table under physical conjugation
   \(i\mapsto-i\), with real \(\Lambda,M,\omega,\alpha\) fixed.

Accordingly, no generic polar finite-norm selection, exceptional-current set,
or parity-complete Schwarzschild theorem is promoted here.

## Claim boundary

The result is `LOCAL-ALGEBRAIC` and `REDUCED-MODE`.  It establishes six
canonical finite-depth log-free all-seven sourced representatives and an
empty physical pivot-wall set for those representatives.  It does not
establish an asymptotically flat phase space, finite norm, flux, scattering,
quasinormal modes, ringdown, stability, positivity, particles, or a quantum
theory.

CLOSE-OUT: PARTIAL — six canonical log-free generic-polar sourced metric jets close all seven original Ricci rows through conservative depths, with exact affine/rank witnesses and no physical pivot wall; the old shallow logarithm is a nowhere-extendible terminal artifact, while the complete extendible log module and representative-shift-invariant EE/EX/XX current table remain open.
EVIDENCE: black_hole_programme/phase2/general_l_polar_completion/certificate.json
MISSING-DEP: POLAR_RESONANT_LOG_MODULE_AND_REPRESENTATIVE_SHIFT_INVARIANT_EE_EX_XX_CURRENT
