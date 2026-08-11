# BT vacuum-orbit zero mode and the Eq. (19) trilemma

**Result:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

The broken-vacuum zero mode can be represented exactly without treating the
background as a numerical spurion.  That construction makes the previously
unprojected soft coefficient neutral and leaves its value at $1/48$ per
unordered pair.  It does **not** establish the physical coefficient.  The same
zero-mode covariance neutralizes an Appendix-C squeeze term that the earlier
fixed-vacuum negative-charge argument discarded.  Fixing the vacuum first
recovers the negative grading, but then the boost-charge derivation is not
defined on the quotient.  The missing zero-mode representation and trace in
the deferred proof of Eq. (19) are therefore a genuine obstruction, not merely
missing notation.

## 1. The vacuum orbit is an operator algebra

Split the scalar into the constant symmetry-orbit coordinate and the remaining
field,

\[
 \phi=\phi_0+\varphi,\qquad Z=e^{\lambda\phi_0}.
\]

Equation (16) of the Letter then factorizes exactly as

\[
 \Omega=\lambda^{-1}Z e^{\lambda\varphi},\qquad
 \Upsilon=Z^{-1}e^{-\lambda\varphi}
 \bigl(\Box\varphi+\lambda(\partial\varphi)^2\bigr).
\]

Because $Z$ is spacetime constant, it cancels from both
$\partial\Omega\,\partial\Upsilon$ and $\Omega^2\Upsilon^2$.  The appropriate
finite-support algebraic carrier is therefore

\[
 {cal A}_0=\mathbb Q[Z,Z^{-1}],\qquad
 \delta Z^n=nZ^n,qquad Z^\dagger=Z,qquad
 \kappa Z\kappa=Z^{-1}.
\]

Here $Z$ is an operator carrying the broken boost orbit, not a c-number with a
charge label attached by hand.  The Laurent algebra admits the normalized
invariant functional $\tau_0(Z^n)=\delta_{n0}$ and corresponding algebraic
pairing $\langle Z^m,Z^n\rangle=\delta_{m+n,0}$.  This is a candidate orbit
pairing, not a derivation of the generalized Born trace on the full dynamical
$p=0$ sector.

## 2. Unique covariant completion of the soft kernel

Let $q(\Omega)=+1$ and $q(\Upsilon)=-1$.  A fixed-vacuum quadratic coefficient
mapping daughter species $d_1,d_2$ to a parent $p$ has one unique Laurent
completion:

\[
 C_{p\leftarrow d_1d_2}\longmapsto
 Z^{q_p-q_{d_1}-q_{d_2}}C_{p\leftarrow d_1d_2}.
\]

The completed output then has charge $q_p$.  Contracting it with the
opposite-species parent creator in the number-lowering generator gives total
charge zero.  All eight ordered quadratic rows pass this check exactly.

For the two logarithmic rows the fixed-vacuum charges and required orbit powers
are

| daughters in $\delta b_\Omega$ | partner in $\delta b_\Upsilon$ | fixed charges | $Z$ powers | completed charges | residue |
|---|---|---:|---:|---:|---:|
| $\Omega\Omega$ | $\Upsilon\Upsilon$ | $(+1,-1)$ | $(-1,+1)$ | $(0,0)$ | $-1/4$ |
| $\Upsilon\Omega$ | $\Omega\Upsilon$ | $(-1,+1)$ | $(+1,-1)$ | $(0,0)$ | $-1/4$ |

The $Z$ powers cancel in each Gram product.  Consequently the raw residue
remains $-1/2$, and the already certified normalization ledger still gives

\[
 \Delta P_{\rm pair}=\frac{1}{48},\qquad
 \sum_{3\ \mathrm{pairs}}\Delta P=\frac{1}{16}.
\]

This is a neutral leading-log coefficient on the covariant orbit algebra
*before* the missing full zero-mode trace is supplied.  It is not yet the
physical coefficient in Eq. (19).

## 3. Why the earlier squeeze exclusion does not transfer

Restoring the orbit weights in the leading Appendix-C oscillator map gives

\[
 R^\dagger b_\Upsilon R=Z^{-1}A_1,
\]

\[
 R^\dagger b_\Omega R=
 \frac{Z}{4E^2}
 \left(A_2+2iEtA_1+e^{2iEt}A_1^\dagger\right).
\]

The first relation implies $A_1=Zb_\Upsilon$.  Therefore the oscillatory term,
when written on the $b$ carrier, is proportional to
$Z^2e^{2iEt}b_\Upsilon^\dagger$.  It has total charge $+1$, as a component of
$b_\Omega$ must.  The associated quadratic squeeze has the form

\[
 Z^2 b_\Upsilon^\dagger b_\Upsilon^\dagger
\]

and total charge $2-1-1=0$.  At the fixed numerical vacuum $Z=1$ it appears to
have charge $-2$.  Thus the prior certificate that places this term in the
strictly negative radical remains correct for the fixed-vacuum oscillator
grading, but that use of the theorem cannot be transferred to the covariant
zero-mode completion.

This calculation uses the inverse linear relation only to audit the charge of
the displayed Appendix-C pullback.  It does not substitute that inversion for
the missing nonlinear pushforward $R_tP_2R_t^\dagger$.

## 4. The fixed-vacuum quotient is not charge invariant

The apparent disagreement is exact spontaneous-symmetry-breaking algebra.
Fixing the vacuum corresponds to the ideal

\[
 I=(Z-1).
\]

For the boost derivation to survive on ${\cal A}_0/I$, this ideal would have to
be derivation-stable.  It is not:

\[
 \delta(Z-1)=Z\equiv 1\pmod{Z-1}.
\]

The nonzero remainder is an exact rational calculation.  Hence one cannot both
set $Z=1$ and retain the same boost-charge grading as an invariant quotient.

The resulting trilemma is:

1. Keep the covariant orbit operator: the soft generator and squeeze are both
   neutral; $1/48$ survives, but negative-charge nullity cannot remove the
   squeeze.
2. Fix $Z=1$ first: the squeeze looks charge $-2$, but the charge derivation
   does not descend to that quotient.
3. Supply the missing completion: a full dynamical zero-mode module, state and
   invariant generalized-Born trace can decide how the neutral squeeze and
   soft terms enter $R_tP_2R_t^\dagger$.

The public six-page Letter supplies neither the third object nor the deferred
proof of Eq. (19).  Its official arXiv record was checked on 2026-08-11 and
still listed v1 only.

## 5. Disposition

Established exactly:

- the Laurent vacuum-orbit operator algebra and Eq. (16) factorization;
- the unique $Z$ dressing of every quadratic number-lowering row;
- neutrality of both logarithmic generators after completion;
- preservation of the conditional $1/48$ per-pair coefficient;
- neutral, rather than negative, charge of the covariantly completed squeeze;
- failure of the boost derivation to descend to $Z=1$.

Not established:

- the complete order-$\lambda$ pushforward in Eq. (19);
- whether the neutral squeeze has zero or nonzero generalized-Born trace;
- the physical $1/48$ coefficient or a complete NLO probability;
- a full dynamical $p=0$ representation;
- beyond-tree positivity, a gravitational/BRST lift, or anything
  `LORENTZIAN-CAUSAL`.

The work item therefore closes `OBSTRUCTED`, not `DONE`: the first exact
obstruction is that fixed-vacuum charge selection and covariant zero-mode
completion do not commute.  This does not prove Eq. (19) false in the
unpublished completion.

Verification commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_zero_mode_eq19_trilemma.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_zero_mode_eq19_trilemma.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_zero_mode_eq19_trilemma
```

## Verification receipt (2026-08-11)

All commands ran sequentially with `ulimit -v 500000`.

- Python parse/compile: PASS, 0.11 s, 16,248 KB peak RSS.
- Exact producer replay: PASS 21/21, 0.14 s, 20,684 KB peak RSS.
- Method-distinct schema/algebra/quotient verifier: PASS 9/9, 0.28 s,
  30,260 KB peak RSS.
- Producer, verifier, and five decisive mutations: PASS 7/7, 1.78 s,
  30,304 KB peak RSS.  Mutations changed a $Z$ exponent, the quotient
  remainder, the covariant squeeze charge, $1/48$, and the physical-claim
  boundary; every mutation was rejected.
- Content-addressed direct-consumer chain: inclusive-radical PASS 12/12 in
  1.00 s (30,356 KB), fixed-vacuum oscillatory PASS 4/4 in 0.70 s
  (30,028 KB), soft-charge flow PASS 7/7 in 1.73 s (30,512 KB), and the
  Jordan-kernel predecessor PASS 11/11 in 1.36 s (30,528 KB).
- Papers V and VI: PASS, two `pdflatex -halt-on-error` passes each.  Paper V
  took 1.14/0.95 s; the final Paper VI passes took 1.33/1.19 s.  Peak RSS was
  below 51 MB.  PDF text witnesses found the vacuum-orbit, fixed-vacuum-ideal,
  conditional-$1/48$, dependency-tag, and missing-trace statements.
- All changed structured data parsed.  The first memory-capped Science Forge
  coordinator attempt failed before startup while reserving Go page-summary
  memory and is not counted as a pass.  The append-only `OBSTRUCTED` event was
  therefore written with the documented event-v0 shape and independently
  reproduced FNV-1a id; no coordinator import is claimed.
- The advisory Science Forge shadow rail returned advisory exit zero, but its
  bridge audit is recorded as **FAIL**, not pass: the Go toolchain could not
  reserve page-summary memory under the cap.  Its separate read-only census
  reported corpus drift (1,511 certificates versus the 2026-07-19 baseline of
  976).  Neither finding promotes or invalidates this scoped certificate.

Tier 2 stopped at the content-addressed predecessor and direct-consumer chain
listed above.  Tier 3 was not run because this is a `CLASSIFIED` obstruction,
not a freeze, release or theorem-state promotion.
