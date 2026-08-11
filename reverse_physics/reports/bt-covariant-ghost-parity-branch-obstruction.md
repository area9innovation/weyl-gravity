# BT covariant ghost-parity branch obstruction

Certificate: `REVERSE_PHYSICS_BT_COVARIANT_GHOST_PARITY_BRANCH_OBSTRUCTION_V1`

Lifecycle: `CLASSIFIED`

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The covariant public Bateman--Turok projector pushforward is charge neutral
and stationary on the complete order-λ resonant block, but it is **not ghost
even**. Its nonzero rank-four first correction has Laurent support (Z^{-1}),
whereas ghost parity sends it to an independent (Z) branch.

Thus the Eq. (19) charge formula still holds, with (Q_{m negative}=0), but
the whole neutral term does not have the ghost parity needed by the published
positivity argument. The canonical ghost-odd remainder is orthogonal to the
even part but is not null:

\[
 \tau_0(C_1^\sharp C_1)=-\frac{7}{288}.
\]

The smallest exact finite repair adds the missing conjugate orbit branch. It
produces a neutral, stationary, ghost-even projector to all formal orders, but
the public (R_t) map does not supply that branch. This is therefore a precise
architecture for an enlarged completion, not a proof of the unpublished BT
construction or of a physical probability.

## The exact resonant block

Take distinct daughter energies (e_1=1), (e_2=2), with parent energy
(E=e_1+e_2=3). Use the one-particle basis

\[
 (\Omega_p,\Upsilon_p)
\]

and the two-particle basis

\[
 (\Omega_1\Omega_2,\Omega_1\Upsilon_2,
   \Upsilon_1\Omega_2,\Upsilon_1\Upsilon_2).
\]

The cross-Fock Grams are

\[
 G_1=\begin{pmatrix}0&1\\1&0\end{pmatrix},\qquad
 G_2=G_1\otimes G_1,
\]

and ghost parity is the same species exchange on each block. The complete
public signed quadratic kernel gives the daughter-to-parent map

\[
 D=\begin{pmatrix}
 0&-1/24&-1/12&0\\
 0&0&0&1/8
 \end{pmatrix}.
\]

With (D^\sharp=G_2D^TG_1), set

\[
 K_+=\begin{pmatrix}0&D\\-D^\sharp&0\end{pmatrix}.
\]

It obeys

\[
 K_+^\sharp=-K_+,
 \qquad [q,K_+]=K_+.
\]

The unique zero-mode dressing imported from the complete quadratic
calculation is therefore

\[
 K_{\rm pub}=Z^{-1}K_+,
 \qquad \delta K_{\rm pub}=0.
\]

Let (P_0=\operatorname{diag}(I_2,0_4)), the standard finite one-particle
projector including both target species. It is idempotent, Krein
self-adjoint, charge neutral, ghost even and stationary. The public first
correction is

\[
 P_1=Z^{-1}[K_+,P_0].
\]

The coefficient ([K_+,P_0]) has rank four. It satisfies the linearized
projector and adjoint identities

\[
 P_0P_1+P_1P_0=P_1,
 \qquad P_1^\sharp=P_1,
\]

and is charge neutral after the (Z^{-1}) dressing.

## Why ghost parity fails

Ghost parity reverses boost charge and the zero-mode orbit:

\[
 \kappa Z\kappa=Z^{-1},
 \qquad \kappa q\kappa=-q.
\]

Consequently

\[
 \kappa P_1\kappa
 =Z\,\kappa[K_+,P_0]\kappa.
\]

The Laurent powers (Z^{-1}) and (Z) are linearly independent. Both
coefficient matrices have rank four, so

\[
 \kappa P_1\kappa-P_1
 =Z\,\kappa[K_+,P_0]\kappa-Z^{-1}[K_+,P_0]\ne0.
\]

This is a coefficientwise formal obstruction: an order-λ defect cannot be
canceled by any term of order λ² or higher.

The all-order charge certificate already proves that the covariant
pushforward is wholly neutral and that its strictly negative component is
zero. Hence the displayed Eq. (19) **charge decomposition** is satisfied
trivially by taking the whole pushforward as its neutral term. But that term
is not ghost even. Charge zero and ghost parity are independent conditions,
and the charge-selection argument cannot discard a neutral odd component.

## The forced odd remainder is not null

Split the first correction canonically into parity even and odd pieces,

\[
 B_1=\frac12(P_1+\kappa P_1\kappa),\qquad
 C_1=\frac12(P_1-\kappa P_1\kappa).
\]

On the finite orbit corner use the relative trace

\[
 \tau_0(X)=\operatorname{tr}_{\rm species}[Z^0]X.
\]

Exact contraction gives

\[
 \tau_0(B_1^\sharp C_1)=0,
\]

but

\[
 \tau_0(B_1^\sharp B_1)=\frac7{288},\qquad
 \tau_0(C_1^\sharp C_1)=-\frac7{288}.
\]

The unsplit one-branch tangent has

\[
 \tau_0(P_1^\sharp P_1)=0,
\]

because it carries only the non-returning orbit power (Z^{-2}). After the
parity split, however, the two opposite branches multiply to an orbit-return
term. The odd remainder is therefore orthogonal but **non-null**. This blocks
the published weak-ghost-symmetry argument on this declared branch. It does
not by itself prove that any complete transition probability is negative.

## Stationarity passes at this order

The parent and the two daughters have the same total free energy (E). The
complete signed-kernel predecessor proves cancellation of every secular and
oscillatory phase, and on the finite block

\[
 [H_0,K_+]=[H_0,P_0]=0.
\]

Therefore

\[
 [H_0,P_1]=0.
\]

The first nonlinear obstruction is ghost parity, not time dependence.
Stationarity of the full public pushforward at all orders and on the
continuum remains open.

## Why the hidden source parity does not repair it perturbatively

Write

\[
 F=\Box\phi+\lambda(\partial\phi)^2.
\]

The hidden source rule is, up to a constant normalization,

\[
 h(\phi)=-\phi+\lambda^{-1}\log F.
\]

At the perturbative Fock vacuum, (F) has zero augmentation: it begins at
positive field degree. A formal power series is invertible only when its
constant coefficient is nonzero. Thus (F) is not a unit and (log F) is
not an element of the Laurent--Fock algebra used by the charge theorem.
Localizing by adjoining (F^{-1}) and (log F) removes the free (F=0)
vacuum chart. Moreover (h(F)=F), and hence (h^2\phi=\phi), only after the
PS field equation is used. The hidden classical parity is therefore not an
off-shell perturbative automorphism of the projector algebra that could
supply the missing (Z) branch for free.

## Minimal exact two-branch repair

The smallest Laurent support closed by ghost parity is

\[
 K_{\rm even}
 =\frac12\left(
 Z^{-1}K_+ + Z\kappa K_+\kappa
 \right).
\]

It obeys exactly

\[
 K_{\rm even}^\sharp=-K_{\rm even},\qquad
 [\kappa,K_{\rm even}]=0,\qquad
 \delta K_{\rm even}=0,\qquad
 [H_0,K_{\rm even}]=0.
\]

Hence

\[
 P_{\rm even}(\lambda)
 =e^{\lambda K_{\rm even}}P_0e^{-\lambda K_{\rm even}}
\]

is, to every formal order, an idempotent, Krein-self-adjoint, charge-neutral,
ghost-even and stationary finite projector. The certificate replays all five
properties coefficientwise through order eight in addition to the all-order
conjugation proof.

This repair is support-minimal: a nonzero κ-invariant Laurent polynomial
containing (Z^{-1}) must also contain its image (Z). But it is not the
public pushforward. It adds the charge-conjugate zero-mode branch, so a
source-affiliation theorem or new dynamical input is required before it can
be called (R_tP_\chi^{(\phi)}R_t^\dagger).

## Exact boundary

Established:

- a nonzero rank-four public projector correction at order λ;
- its exact charge neutrality and finite resonant stationarity;
- its two-power ghost-parity defect;
- the exact relative norms (+7/288) and (-7/288) of the canonical even and
  odd parts;
- failure of the prescribed ghost-even neutral term and charge-nullity
  argument on the declared public covariant branch;
- the nonunit obstruction to importing hidden source parity at the Fock
  vacuum; and
- an exact all-order finite two-branch repair.

Not established:

- source or (R_t) affiliation of the added conjugate branch;
- all-order public-pushforward stationarity;
- (R_{\pm\infty}), continuum domains or the specific continuum projector;
- a generalized-Born trace for the full process;
- a negative or positive complete physical probability;
- a refutation of an unpublished enlarged BT construction;
- a gravity/BRST lift or anything `LORENTZIAN-CAUSAL`; or
- literature priority.

## Next gate

There are now two honest routes.

1. Derive the (Z\kappa K_+\kappa) branch from a doubled/on-shell source
   representation and prove that its projector is the pushforward of the
   physical (P_\chi^{(\phi)}).
2. Stay with the public one-branch map and compute the complete physical
   process directly, without using the failed weak-ghost-symmetry shortcut.

The first route would repair the Eq. (19) positivity architecture. The second
could still establish a physical probability even if that architecture does
not extend.

## Verification receipt

All scientific commands run sequentially under `ulimit -v 500000` with
Python 3.12.13.

- Tier 0 Python compilation and structured-data parsing passed in 0.03 s
  with 15,312 KiB peak RSS.
- The exact producer passed 44/44 checks in 0.34 s with 65,580 KiB peak RSS.
- The independent matrix/Laurent verifier passed 39/39 checks in 0.53 s with
  69,936 KiB peak RSS.
- The falsification suite passed 21/21 tests in 10.90 s with 70,264 KiB peak
  RSS. Mutations covered the Gram, public kernel, projector, Laurent branch,
  parity defect, relative norm, stationarity, Eq. (19) boundary, hidden
  parity domain, repair, affiliation, physical-claim boundary and input
  hashes.
- Paper V compiled twice in 0.49 s per pass with at most 50,728 KiB peak RSS;
  the final PDF has 43 pages. Its four pre-existing overfull boxes remain
  unchanged.
- Paper VI compiled twice in 0.56 s and 0.54 s with at most 50,572 KiB peak
  RSS; the final PDF has 43 pages and no overfull box or undefined reference.

Tier 2 is not required because no predecessor mathematical input or shared
operator changed. Tier 3 is not run because this is a scoped `CLASSIFIED`
reduced-mode result, not a freeze, release, full physical theorem or shared
core change.
