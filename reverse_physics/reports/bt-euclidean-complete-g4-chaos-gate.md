# Complete BT order-g4 Wiener-chaos gate

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_CHAOS_GATE_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

Lifecycle: `EXACT_CHAOS_REDUCTION_PROVED_EFFECTIVE_KERNEL_BOUND_OPEN`

## Result

The possible cancellation of the positive order-$g^4$ ultraviolet power has
been reduced to one effective kernel.

After moving the interacting background density into the observable, the
complete coefficient has the exact form

\[
 M_4=\|D\|_0^2+2\langle A,E\rangle_0,
\]

where $A$ is the cubic score coefficient and $D,E$ are the next two
coefficients in the fixed-free-space score.  The first term is nonnegative.
Moreover, $A$ lies entirely in second homogeneous Wiener chaos.  Therefore

\[
 \boxed{M_4=\|D\|_0^2+2\langle A,\Pi_2E\rangle_0.}
\]

Every potentially negative order-$g^4$ contribution is contained in the
single second-chaos projection $\Pi_2E$.  All other chaoses contribute only
through the nonnegative norm.

This does not yet decide the whole-lattice coefficient.  It replaces a large
signed diagram problem by one weighted norm estimate for a translation-
invariant three-leg kernel.

## Fixed-free-space normal form

The zero-fiber score and square root of the normalized background density are

\[
 s_g=gA+g^2B+g^3C+O(g^4)
\]

and

\[
 \sqrt{\frac{d\nu_g}{d\nu_0}}
 =1-\frac g2W_1
 +g^2\left(\frac18W_1^2-\frac12W_2-\frac12z_2\right)
 +O(g^3),
\]

where

\[
 z_2=\mathbb E_0\left[\frac12W_1^2-W_2\right].
\]

Thus

\[
 D=B-\frac12W_1A
\]

and

\[
 E=C-\frac12W_1B
 +\left(\frac18W_1^2-\frac12W_2-\frac12z_2\right)A.
\]

Taking the free squared norm reproduces the complete coefficient derived in
the predecessor certificate.

## Chaos inventory

For $L\geq4$, the actual conditioned covariance cannot close the external
momentum of $A$.  Its translation-invariant part pairs $q$ with $-q$, while
the removed real-cosine rank-one block has both momenta in $\{\pm p\}$.
Neither support solves $\pm p+q+r=0$.  Thus $\mathbb E_0A=0$, and the
quadratic score is pure second chaos even though the one-cosine conditioning
breaks full translation invariance.

The remaining polynomial degrees and parities give:

| object | polynomial parity and degree | possible chaoses |
|---|---|---|
| $A$ | even, degree 2, centered | 2 |
| $B$ | odd, degree 3 | 3, 1 |
| $C$ | even, degree 4 | 4, 2, 0 |
| $W_1$ | odd, degrees 3 and 1 | 3, 1 |
| $W_2$ | even, degrees 4, 2 and 0 | 4, 2, 0 |
| $D$ | odd, maximum degree 5 | 5, 3, 1 |
| $E$ | even, maximum degree 8 | 8, 6, 4, 2, 0 |

Homogeneous Gaussian chaoses of different degree are orthogonal.  Since $A$
is in chaos 2, it pairs with no part of $E$ except $\Pi_2E$.

An independent exact fixture uses probabilists' Hermite polynomials under a
standard Gaussian:

\[
 A=H_2,
 \quad D=2H_1+3H_3+5H_5,
 \quad E=7H_0+11H_2+13H_4+17H_6+19H_8.
\]

Using $\mathbb E[H_mH_n]=n!\delta_{mn}$ gives

\[
 \|D\|^2=3058,
 \quad 2\langle A,E\rangle
 =2\langle A,\Pi_2E\rangle=44,
 \quad M_4=3102.
\]

The fixture checks the algebra only; it is not BT lattice data.

## One sufficient estimate

The cubic-score certificate and exact residue give

\[
 \|A\|_0^2
 \leq C_A N\omega_p^2(1+\log L)
\]

for sufficiently large $L$.  Suppose one proves, for some fixed finite $b$,

\[
 \|\Pi_2E\|_0^2
 \leq C_E N\omega_p(1+\log L)^b.
\]

Cauchy--Schwarz then yields

\[
 \frac{2|\langle A,\Pi_2E\rangle|}{N\omega_p}
 \leq 2\sqrt{C_AC_E}\,sqrt{\omega_p},
       (1+\log L)^{(b+1)/2}
 \longrightarrow0.
\]

The predecessor theorem supplies a fixed-UV block

\[
                         \|D\|_0^2\geq cN\omega_p,
\]

because its third-chaos kernel equals the linearly soft quartic kernel plus
$O(p^2)$ corrections.  The proposed bound would therefore prove

\[
                         M_4\geq c'N\omega_p>0
\]

eventually.  Dividing by the required $N\omega_p^2$ normalization would show
the full order-$g^4$ coefficient grows at least quadratically in $L$.

## Remaining calculation

The only unresolved fixed-order object is

\[
 \Pi_2\left[
 C-\frac12W_1B
 +\left(\frac18W_1^2-\frac12W_2-\frac12z_2\right)A
 \right].
\]

It is an effective three-leg kernel: one external real-cosine leg and two
background legs.  The next calculation must perform its Wick contractions
before applying absolute values, so that the cancellations from $W_1$, $W_2$
and $z_2$ are preserved.  Its weighted free norm should then be split into
hard, one-soft, and all-soft momentum regions.

The Anderson--Bateman--Herzog--Turok theorem proves infrared finiteness for
ordinary off-shell correlators.  It does not directly identify this projected,
fiber-integrated composite or provide the required lattice estimate uniformly
as the external mode tends to zero.

No bound on $\Pi_2E$, whole-lattice order-$g^4$ decision, nonperturbative
annealed score bound, normalized lowest-mode estimate, interacting $H^{-1}$
moment, continuum identification, Born rule, Krein reconstruction, or
`LORENTZIAN-CAUSAL` statement is established.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_chaos_gate.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_chaos_gate.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_chaos_gate
```

## Verification receipt

The final bounded run used the exact commands above under the 500 MB virtual
memory cap.  The producer check took 0.04 s (20,248 KB peak), the independent
verifier 0.10 s (29,472 KB), all nine focused tests 0.16 s (30,836 KB), and
Python compilation 0.05 s.  The generated Paper 21 claim-map check took
0.06 s and its independent verifier 0.07 s.  Two PDF passes took 0.78 s and
0.77 s.  The affected cubic-score, RG-matching, and complete-$g^4$
predecessor verifiers passed in 1.25 s, 0.10 s, and 0.09 s.

The append-only planning import folded 1,613 nodes with zero invalid items and
zero malformed events in 7.24 s under `GOMEMLIMIT=300MiB`.  The advisory
Science Forge shadow rail completed in 3.02 s and reported the existing
bridge-audit environment failure (`sympy` absent in the referenced external
tree) plus corpus-baseline drift (1,664 certificates versus the 2026-07-19
baseline of 976).  These advisory findings are not passes and were not used to
promote the result.

Tier 0 and the scoped Tier 1 suite passed.  Tier 2 was limited to the three
direct mathematical predecessors because no shared operator or schema was
changed.  Tier 3 was not run: the effective-kernel bound, whole-lattice
coefficient, and every continuum, reconstruction, freeze, and release gate
remain open.  The exact staged diff and content hashes are inspected before
the coherent commit.
