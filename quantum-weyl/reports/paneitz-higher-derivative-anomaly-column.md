# Paneitz higher-derivative anomaly column

The first genuinely higher-derivative conformal matter column is now exact.
For one real four-dimensional Paneitz scalar,

\[
(c,-a,p,b_{\Box R})
=
\left(-\frac1{15},\frac7{90},0,\frac1{15}\right)
\]

in the same raw heat-kernel scheme used by the standard-matter lattice.

Two independent routes agree.  The first uses the dimensionally continued
local Juhl/Gilkey heat coefficient and the Branson--Orsted conformal
principle, retaining the total derivative.  The second combines the Einstein
factorization

\[
P_4=\Delta(\Delta+R/6)
\]

with the multiplicative-anomaly-improved Casimir energy.  They independently
give

\[
a=-\frac7{90},\qquad c-a=\frac1{90},\qquad
\gamma_{\Delta J}=-\frac{32}{45},
\]

and the exact basis conversion

\[
b_{\Box R}=\frac{4a-\gamma}{6}=\frac1{15}.
\]

The parity-odd coordinate vanishes for the declared real scalar natural
operator and parity-even regulator.

## BV, determinant, and sign price

The added minimal BV sector is the scalar \(\phi\) and its antifield
\(\phi^*\).  The scalar has Weyl weight zero, no internal gauge symmetry, no
new ghosts, and no nonminimal sector.  Its Koszul--Tate row is
\(\delta\phi^*=P_4\phi\); the ambient diffeomorphism row is
\(\gamma\phi=\mathcal L_\xi\phi\).

On a compact boundaryless Riemannian background the declared realization is
\(P_4:H^4\to L^2\), with effective-action power
\(+\frac12\log\det'P_4\).  The prime is explicit: sources are restricted to
\(\ker(P_4)^\perp\), and constant zero modes are retained in the kernel
ledger rather than silently discarded.

The higher-derivative price is also explicit.  On an Einstein background
with nonzero \(R\),

\[
\frac1{\Delta(\Delta+R/6)}
=\frac6R\left(\frac1\Delta-\frac1{\Delta+R/6}\right),
\]

so the two second-order poles have opposite residues.  This is classified as
a fourth-order Krein-indefinite price.  It is not advertised as a healthy
standard-sign field or as a constructed Lorentzian state.

## Exact lattice effect

Modulo the BRST-exact type-D coordinate, the Paneitz-extended integer
lattice has Smith invariant factors \((1,30)\) and the complete
parameterization

\[
\begin{aligned}
N_s&=128-16p+48v,\\
N_W&=-308-2d-20v+8p,\\
N_D&=d,\qquad N_V=v,\qquad N_{P_4}=p .
\end{aligned}
\]

Unlike the healthy standard-matter cone, this enlarged nonnegative
multiplicity cone is nonempty.  The first solution by vector count is

\[
\boxed{N_V=61,\qquad N_{P_4}=191}
\]

with all other multiplicities zero.  Minimality follows from

\[
p\leq 8+3v,\qquad
p\geq \left\lceil\frac{308+20v}{8}\right\rceil.
\]

The intervals are disjoint for \(0\leq v\leq60\) and meet uniquely at
\((v,p)=(61,191)\).

In the displayed raw \(\Box R\) scheme the three-coordinate nonnegative cone
remains empty.  The exact separator is

\[
\ell(c,-a,b)= -3c-5(-a)+3b.
\]

It is \(37/20\) on the strict gravity vector and strictly positive on every
standard and Paneitz matter ray.  A separate mod-five witness shows that
even the signed raw integer equations have no solution.  This is only
scheme bookkeeping: \(\Box R\) is an exact class shifted by a finite
\(R^2\) counterterm.

## Fail-closed successor

No new conformal gauge-field column has been appended.  Spin two is the
already-imported strict Weyl graviton and cannot be borrowed as added matter.
The next genuinely new conformal higher-spin candidate lacks a
repository-declared complete off-shell BV/reducibility complex, nonminimal
gauge fixing, generic-background elliptic operator/domain, complete
ghost/zero-mode ledger, and two-route raw anomaly payload.

That is the first missing-carrier obstruction.  It is not a no-go theorem for
conformal higher-spin fields.

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

This result does not restore the strict QME and establishes no Lorentzian
state, positivity, particle, GUT, phenomenology, scattering, or unitarity
claim.

CLOSE-OUT: OBSTRUCTED — Paneitz is complete and changes the projected cone,
but no qualifying higher-derivative conformal gauge carrier is declared.

EVIDENCE:
`quantum-weyl/anomalies/certificates/PANEITZ_HIGHER_DERIVATIVE_ANOMALY_COLUMN.json`
