# Compensator-generated Einstein--Weyl phase

## Theorem

Consider four-dimensional pure Weyl gravity enlarged by one Weyl
Stueckelberg scalar,

\[
S=S_W+\int\!\sqrt{-g}\,
 \left[\zeta\left(\phi^2R-6\phi\Box\phi\right)-\lambda\phi^4\right].
\]

The transformations are

\[
g_{\mu\nu}\mapsto e^{2\sigma}g_{\mu\nu},\qquad
\phi\mapsto e^{-\sigma}\phi .
\]

On the local chart `phi != 0`, the invariant metric is
`g_hat=(phi/mu)^2 g`.  Around `phi=v+varphi`, the invariant linearized
metric is

\[
\widehat h_{\mu\nu}=h_{\mu\nu}
       +2\frac{\varphi}{v}\eta_{\mu\nu}.
\]

The Weyl parameter `sigma=varphi/v` reaches the constant frame
`varphi=0`.  Thus `v` is a Stueckelberg frame value.  It is not by itself a
gauge-invariant order parameter proving spontaneous breaking of a local
symmetry.

In that frame the action contains

\[
c_1R-\lambda v^4,\qquad c_1=\zeta v^2.
\]

Since the repository's healthy Einstein convention is
`c1=-M_P^2/2`, the induced scale is

\[
M_P^2=-2\zeta v^2.
\]

The constant scalar and metric equations give

\[
\zeta v^2G_{\mu\nu}
 +\frac12\lambda v^4g_{\mu\nu}=0,
\qquad
2\zeta vR-4\lambda v^3=0,
\]

and hence

\[
\Lambda_{\rm eff}=\frac{\lambda v^2}{2\zeta},
\qquad R=4\Lambda_{\rm eff}.
\]

Without another vacuum-energy contribution, a flat nonzero-`v` background
requires `lambda=0`.  For nonzero `lambda`, every four-dimensional Einstein
metric with `Ric=Lambda_eff g` survives: it solves the compensator equations
and is Bach-flat.

## Flat helicity-two factorization

Use the repository conventions

\[
\mathcal L=\sqrt{-g}\left(c_1R+\alpha R_{\mu\nu}R^{\mu\nu}
 +\beta R^2\right),\qquad \alpha=-3\beta .
\]

For either TT polarization, modulo a divergence,

\[
L_{TT}=\frac{\alpha}{4}(\ddot A+k^2A)^2
 -\frac{c_1}{4}(\dot A^2-k^2A^2).
\]

Writing `y` for the massless wave symbol, its kinetic polynomial is

\[
K(y)=\frac12y(c_1+\alpha y)
 =\frac{\alpha}{2}y(y+M^2),
\qquad M^2=\frac{c_1}{\alpha}=\frac{\zeta v^2}{\alpha}.
\]

There are two roots:

1. `y=0`, the massless Einstein helicity-`+/-2` branch;
2. `y=-M^2`, the massive spin-2 branch.

Their action-derived simple-root normalizations are

\[
K'(0)=\frac{c_1}{2},\qquad
K'(-M^2)=-\frac{c_1}{2}.
\]

The compensator therefore repairs the pure-Weyl pairing obstruction: for
`c1 != 0`, the Einstein wave branch is no longer zero-pairing.  But the pole
decomposition

\[
\frac1{K(y)}=\frac2{c_1}
 \left(\frac1y-\frac1{y+M^2}\right)
\]

shows that an opposite-residue massive spin-2 branch remains.  In the
repository healthy-graviton convention `c1=-1`, `alpha<0`, the massless branch
is healthy and the massive branch is the conventional ghost.

The pure-Weyl limit is exact:

\[
v\to0:\qquad c_1\to0,\quad M^2\to0,\quad
K(y)\to\frac\alpha2y^2.
\]

Both simple-root normalizations vanish as the roots coalesce into the Jordan
block.  This recovers, rather than contradicts, the certified vanishing of the
pure-Weyl current on two Einstein tangents.

## Classification

The result fixes the earlier ambiguity:

| Statement | Status |
|---|---|
| A compensator can generate an Einstein-Hilbert scale | Exact on `phi=v!=0`: `c1=zeta v^2`, hence `M_P^2=-2 zeta v^2` in repository conventions. |
| The massless Einstein symplectic pairing is restored | Exact on the flat TT reduced mode sector. |
| The gauge-fixed full theory is Einstein gravity | False when the Weyl-squared coupling remains nonzero. It is Einstein--Weyl gravity. |
| Einstein metrics remain solutions | Exact for `Ric=Lambda_eff g`. |
| Additional modes remain | Exact at linear order: a massive spin-2 branch of opposite residue. |
| Einstein gravity is a low-energy sector | Conditional for `|alpha y/c1| << 1` and a declared prescription for the massive branch. |
| Einstein gravity is an exact boundary-selected sector | Open; requires causal/symplectic removal of the massive branch. |
| The compensator is the D-quotient scalar clock | False. A constant field is not a monotone relational clock. The classical one-scalar clock certificate is separately obstructed on the exact vacuum cylinder. |

Thus the precise interpretation is

\[
\boxed{
\text{constant compensator}
\Longrightarrow
\text{Einstein--Weyl phase with an Einstein massless sector, not pure Einstein theory.}
}
\]

Calling this “spontaneous Weyl breaking” requires additional gauge-invariant
vacuum data.  The minimal calculation itself proves a Weyl frame theorem.

## Relation to the D-quotient programme

This result imports the classical team's
`d_quotient_classical/certificates/SCALAR_CLOCK_VERTICAL_SLICE.json` by hash.
That certificate proves exact local monotone charts for one homogeneous
conformal scalar, but also proves that no nonzero homogeneous clock is
compatible with the exact vacuum cylinder.  The only compatible background is
zero, where the scalar has no linearized clock incidence.  Its next gate is
`BACKREACTED_OR_COMPOSITE_CLOCK_MODEL`.

The constant Stueckelberg compensator supplies no relational time and must not
be relabeled as `compact_scalar_clock`.  Conversely, the imported clock
obstruction does not invalidate the compensator's local Einstein-Hilbert scale
generation: they are different scalar roles and different background
questions.

## What remains

The next theorem should decide whether the massive spin-2 branch can be
excluded by local causal initial/boundary conditions while retaining the
nondegenerate massless Einstein pairing.  It must also complete the scalar BV
count, determine nonlinear preservation of the Einstein submanifold, and
construct the asymptotic charge/scattering comparison.  No such claim follows
from the reduced factorization.

Machine certificate:
`bridge/certificates/compensator_einstein_phase.json`.

Primary comparisons: [Weyl uplift and invariant metric](https://arxiv.org/abs/2307.13531),
[four-dimensional critical curvature-squared gravity](https://arxiv.org/abs/1101.1971),
and [a conformal-matter scale-generation example](https://arxiv.org/abs/hep-th/0603131).
