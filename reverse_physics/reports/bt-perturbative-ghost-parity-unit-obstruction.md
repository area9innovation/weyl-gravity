# BT perturbative ghost-parity unit obstruction

Certificate: `REVERSE_PHYSICS_BT_PERTURBATIVE_GHOST_PARITY_UNIT_OBSTRUCTION_V1`

Lifecycle: `CLASSIFIED`

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The missing ghost-conjugate orbit branch cannot be obtained by a regular
unital hidden-parity automorphism of the same off-shell perturbative
perfect-square local-symbol algebra.

The exact Eq. (16) image of Omega is a unit, while the image of Upsilon is
not. A unital automorphism cannot exchange them, even after an arbitrary
invertible normalization.

This is a same-chart **regular local-symbol** no-go. It also rules out a
filtration-continuous quantum automorphism having that regular classical
symbol. It does not impose a zero-oscillator character on the CCR/Weyl
algebra and does not rule out a singular, nonlocal or unbounded operator
correspondence.

## The algebra and augmentation

Let

\[
 \mathcal A_{\rm sym}
 =\mathbb Q((\lambda))[Z,Z^{-1}][[\mathcal J]]
\]

be the commutative field-degree completion of the off-shell local-jet symbol
algebra. Here $\mathcal J$ contains the nonzero-mode local jets of $\varphi$.
Define the zero-jet augmentation

\[
 \epsilon(Z)=Z,\qquad
 \epsilon(\lambda)=\lambda,\qquad
 \epsilon(\mathcal J)=0.
\]

It is a unital algebra homomorphism to
$\mathbb Q((\lambda))[Z,Z^{-1}]$. If $a$ is a unit, then $\epsilon(a)$ must
be a unit: from $ab=1$ one gets
$\epsilon(a)\epsilon(b)=1$.

This augmentation belongs only to the commutative local-symbol shadow. The
quantum oscillator algebra obeys CCRs, so no claim is made that every
oscillator can be set to zero by a character of the Weyl algebra.

## Unit classes of the exact Eq. (16) images

Write

\[
 F=\Box\varphi+\lambda(\partial\varphi)^2.
\]

The exact covariant factorization is

\[
 O=\alpha(\Omega)=\lambda^{-1}Z e^{\lambda\varphi},
\qquad
 Y=\alpha(\Upsilon)=Z^{-1}e^{-\lambda\varphi}F.
\]

The first element has the explicit inverse

\[
 O^{-1}=\lambda Z^{-1}e^{-\lambda\varphi},
\qquad
 \epsilon(O)=\lambda^{-1}Z.
\]

The certificate replays
$e^{\lambda\varphi}e^{-\lambda\varphi}=1$ coefficientwise through field
degree sixteen; the exponential identity is the all-order proof.

Both terms of $F$ have positive field degree:

\[
 \deg\Box\varphi=1,
 \qquad
 \deg\lambda(\partial\varphi)^2=2.
\]

Therefore $\epsilon(Y)=0$. If $Y$ had an inverse, applying $\epsilon$ to
$YY^{-1}=1$ would give $0=1$. Thus $Y$ is not a unit.

## The automorphism contradiction

The normalization of target ghost parity is immaterial. Its general scaled
exchange would obey

\[
 h(O)=cY,\qquad h(Y)=c^{-1}O,
\]

where $c$ is any coefficient-ring unit. Multiplication by $c$ does not turn
$Y$ into a unit. But every unital algebra automorphism, and every unital
anti-automorphism, preserves units. Hence

\[
 \boxed{\text{no regular same-chart local-symbol automorphism implements ghost parity}}.
\]

This coefficientwise obstruction cannot be repaired at a higher order in
$\lambda$. It also explains the logarithm in the classical hidden-parity
rule,

\[
 h(\phi)=-\phi+\lambda^{-1}\log F:
\]

$\log F$ requires precisely the invertibility that fails on the zero-jet
$F=0$ chart.

## Quantum boundary

Any filtration-continuous quantum automorphism with a regular classical
local-symbol limit would induce a unital automorphism of
$\mathcal A_{\rm sym}$. The unit contradiction rules out that class.

It does **not** decide:

- an unbounded operator correspondence whose domain excludes zeros of $F$;
- a singular or non-filtration-preserving map with no regular classical
  symbol;
- a nonlocal map between selected detector ideals; or
- a correspondence defined only after imposing the equations of motion.

Those possibilities need explicit domains, adjoints and projector action;
none follows from the public Letter.

## The two escape routes

### Localize at $F$

In $\mathcal A_{\rm sym}[F^{-1}]$ the unit mismatch disappears. Defining
Eq. (15) further requires adjoining $\log F$ or expanding around a nonzero
background value of $F$. But the zero-jet augmentation cannot extend to this
localization, since otherwise

\[
 1=\epsilon(FF^{-1})=0\,\epsilon(F^{-1})=0.
\]

This is a different nonvacuum chart. Moreover, $h(F)=F$ and
$h^2\phi=\phi$ use the PS field equation, so it is an on-shell architecture,
not the off-shell projector algebra of the perturbative construction.

### Double the source sheet

An abstract exchange is immediate on

\[
 \mathcal A_{\rm double}
 =\mathcal A_{\rm left}\oplus\mathcal A_{\rm right},
 \qquad
 \kappa_{\rm double}(a,b)=(b,a).
\]

Both copies may retain a zero-jet vacuum, and the exchange is unital and
involutive. But the source and projector multiplicities have been doubled.
No public PS Hamiltonian or $R_t$ map selects the symmetric coupling. This is
a candidate new theory, not a derivation from the original one.

## Consequence for Eq. (19)

The results now fit together:

1. The charge formula holds to all formal orders with
   $Q_{\rm negative}=0$.
2. The public order-$\lambda$ neutral correction is not ghost even, and its
   forced odd remainder is non-null.
3. The two-orbit algebraic repair is ghost even, but it has no regular
   same-chart local-symbol source affiliation.

Thus the regular perturbative-vacuum route to the full Eq. (19) positivity
package is closed using the public data. A successful enlarged BT completion
must be localized/on shell, doubled, singular/unbounded, or genuinely
nonperturbative. None is ruled out here.

The alternative is to bypass Eq. (19) and prove the physical probability
directly from a complete dressed Møller/S-matrix construction. That route
remains open and is now the cleaner continuation inside the current
perturbative vacuum.

## Exact boundary

Established:

- the unit/nonunit classification of the exact Eq. (16) local symbols;
- the normalization-independent automorphism contradiction;
- obstruction of every regular same-chart local-symbol pullback;
- the conditional obstruction for quantum automorphisms with a regular
  classical-symbol limit;
- loss of the zero-jet vacuum under $F$-localization; and
- the exact algebraic availability, but changed-source status, of doubling.

Not established:

- a no-go for singular, nonlocal or unbounded CCR correspondences;
- a no-go for a localized on-shell nonvacuum representation;
- a no-go for a doubled or nonperturbative BT completion;
- a full Eq. (19) theorem or universal refutation;
- a generalized-Born trace or complete physical probability;
- a gravity/BRST lift or anything `LORENTZIAN-CAUSAL`; or
- literature priority.

## Verification receipt

All scientific commands run sequentially under `ulimit -v 500000` with
Python 3.12.13.

- Tier 0 Python compilation and structured-data parsing passed in 0.02 s
  with 14,836 KiB peak RSS.
- The exact producer passed 34/34 checks in 0.02 s with 16,304 KiB peak RSS.
- The independent recurrence/augmentation verifier passed 32/32 checks in
  0.08 s with 23,836 KiB peak RSS.
- The falsification suite passed 22/22 tests in 1.76 s with 24,204 KiB peak
  RSS. Mutations covered the source ring, augmentation scope, field degree,
  both Eq. (16) images, inverse series, unit classes, automorphism lemma,
  localization, doubling, singular quantum boundary, Eq. (19) boundary,
  physical claims and input hashes.
- Paper V compiled twice in 0.49 s per pass with at most 50,620 KiB peak RSS;
  the final PDF has 43 pages. Its four pre-existing overfull boxes remain
  unchanged.
- Paper VI compiled twice in 0.49 s and 0.50 s with at most 50,928 KiB peak
  RSS; the final PDF has 43 pages and no overfull box or undefined reference.

Tier 2 is unnecessary because all predecessor certificates and their
mathematical inputs remain unchanged and content-addressed. Tier 3 is not run
because this is a scoped `CLASSIFIED` local-symbol obstruction, not a freeze,
release, physical theorem or shared-core change.
