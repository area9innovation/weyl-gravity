# BT resolution-local coherent Born process

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

**Lifecycle:** `CLASSIFIED`

**Certificate:** `REVERSE_PHYSICS_BT_RESOLUTION_LOCAL_COHERENT_BORN_PROCESS_V1`

## Result

The rigged $1/48$ cocycle has a positive normalized realization on the
resolution-local observable net.  It is a locally normal coherent state and a
locally inner Weyl Møller automorphism.  It retains the two directions of the
physical external-jet Gram, gives exactly normalized probabilities for every
finite number of emissions, is translation covariant, and needs no endpoint
origin.

There is no global Fock vector or Weyl implementer: the displacement has
constant nonzero density over an infinite resolution line.  The surviving
global object is an algebraic coherent state that is normal on every bounded
resolution interval and non-Fock at infinity.

The all-count probability law is Poisson only under the declared coherent
stationary-independent-increment completion.  Its rate is forced by the
physical one-emission coefficient, but the nonlinear BT multi-emission
amplitudes have not yet been computed.  Thus this is an explicit physical
leading-log completion architecture, not a proof that the unpublished BT
dynamics selects it.

## Relative detector weight

An absolute translation-invariant probability on the whole resolution line
cannot assign a nonzero finite value to a unit cell.  Countably many disjoint
translates would have either infinite total weight or zero local weight.

The correct object is a relative semifinite weight.  For bounded profiles
$f,g$ with $f-g\in L^1(\mathbb R,ds)$, set

\[
 \tau_{\rm rel}(f,g)=\int_{\mathbb R}(f-g)\,ds.
\]

It obeys

\[
 \tau_{\rm rel}(f,g)+\tau_{\rm rel}(g,h)
 =\tau_{\rm rel}(f,h),
\]

is positive when $f\ge g$, and is invariant under simultaneous
translation.  For every admissible resolution profile,

\[
 \tau_{\rm rel}(q_{R+a},q_R)=a.
\]

Calibration by the physical coefficient gives
\(\gamma\tau_{\rm rel}\), with \(\gamma=1/48\) per unordered pair.
Among locally finite countably additive translation-invariant positive Borel
weights, this is uniquely \(\gamma\) times Lebesgue measure.

## Retaining both physical species

The physical amplitude theorem gives the raised response endomorphism

\[
 G_{\rm phys}=\gamma I_2,
 \qquad \gamma=\frac1{48}.
\]

It has rank two.  A rank-one scalar purification would discard one of the
physical jet directions and repeat the public-\(D\) error.  Use instead the
normalized species trace

\[
 \operatorname{tr}_{\rm sp}(X)=\frac12\operatorname{Tr}_2(X)
\]

and the Kolmogorov factor

\[
 k_s(y)=\sqrt{\gamma p_s(y)}I_2,
 \qquad p_s(y)=\frac12\operatorname{sech}^2(y-s).
\]

Then

\[
 k_s(y)^*k_s(y)=\gamma p_s(y)I_2,
 \qquad
 \operatorname{tr}_{\rm sp}(k_s^*k_s)=\gamma p_s(y).
\]

The factor has minimal rank two and is unique up to an isometry of its GNS
range.  It uses the physical Gram, not the rank-one nilpotent public
\(R_tD\) kernel.

## Local coherent Møller process

Take the positive one-particle GNS carrier

\[
 \mathcal K=L^2(\mathbb R_s\times\mathbb R_y)
 \otimes\mathbb C^3_{\rm pair}\otimes
 \operatorname{HS}(\mathbb C^2_{\rm species}),
\]

with normalized Hilbert--Schmidt trace on the last factor.  For a bounded
resolution interval $I$, define

\[
 F_I(i;s,y)=\mathbf1_I(s)\sqrt{\gamma p_s(y)}I_2,
 \qquad i=1,2,3.
\]

Since \(\int p_s(y)dy=1\),

\[
 \|F_I\|^2=3\gamma|I|=\frac{|I|}{16}.
\]

The Weyl displacement

\[
 W(F_I)=\exp\{a^*(F_I)-a(F_I)\}
\]

is unitary on the local bosonic Fock space.  For a local observable $X$,

\[
 \omega_I(X)=
 \langle W(F_I)\Omega,XW(F_I)\Omega\rangle
\]

is positive and normalized.  Enlarging $I$ outside the support of $X$
does not change the state on $X$, so the local states define a consistent
state on the quasi-local resolution CCR algebra.

Equivalently, for compact-resolution Weyl tests,

\[
 \alpha_F(W(g))=e^{2i\operatorname{Im}\langle F,g\rangle}W(g)
\]

defines the coherent Møller automorphism.  It is inner on each bounded
interval.  Joint translation \((s,y)\mapsto(s+b,y+b)\) leaves the global
density invariant and sends $F_I$ to $F_{I+b}$.

For disjoint intervals, the amplitudes are orthogonal and real.  Their Weyl
phase vanishes, hence

\[
 W(F_I)W(F_J)=W(F_{I\cup J}).
\]

This is the independent-increment factorization.

## Exact probability law

For a resolution length $a=|I|$, the total coherent mean is

\[
 \nu(a)=\|F_I\|^2=\frac a{16}.
\]

The hard no-emission amplitude and probability are

\[
 \langle\Omega,W(F_I)\Omega\rangle=e^{-a/32},
 \qquad P_0(a)=e^{-a/16}.
\]

The total emission count is Poisson:

\[
 P_n(a)=e^{-a/16}\frac{(a/16)^n}{n!},
 \qquad
 \sum_{n=0}^{\infty}P_n(a)=1.
\]

The three pair counts are independent Poisson variables with mean $a/48$.
Consequently

\[
 P_0(a)=1-\frac a{16}+O(a^2),
 \qquad
 P_{\rm real}(a)=\frac a{16}+O(a^2),
\]

which is precisely the certified hard/real response.  Probability is
normalized at every finite $a$, rather than only order by order.

If the count law has stationary independent increments, is continuous at
zero, and has infinitesimal single-emission rate $1/16$ with simultaneous
multiple jumps of smaller order, its generating functions satisfy

\[
 G_{a+b}(z)=G_a(z)G_b(z),
 \qquad \partial_aG_a(z)|_{a=0}=\frac{z-1}{16}.
\]

Therefore \(G_a(z)=\exp[(a/16)(z-1)]\): the Poisson completion is unique
under these assumptions.

## Why no global Fock wave operator exists

On a length-\(L\) interval,

\[
 \|F_{[0,L]}\|^2=\frac L{16}.
\]

The global amplitude has infinite norm.  More sharply, take

\[
 g_L=F_{[0,L]}/\|F_{[0,L]}\|.
\]

Then \(\|g_L\|=1\), but

\[
 |\langle F,g_L\rangle|=\sqrt{L/16}\longrightarrow\infty.
\]

The displacement functional is unbounded on the global one-particle unit
sphere, so no Riesz vector and no global Fock Weyl implementer exists.  The
finite-window vacuum overlap tends to zero as \(e^{-L/32}\).

This is not a failure of the local process.  It says the outgoing coherent
state lies in a non-Fock representation at infinite resolution volume while
remaining normal on every bounded interval.

## Boundary and next calculation

The construction supplies:

- the relative positive detector weight;
- the rank-two physical GNS factor;
- a resolution-local coherent Møller automorphism;
- positive normalized all-count probabilities;
- the exact global Fock obstruction.

It does not prove that nonlinear BT dynamics has coherent independent
increments.  The next falsifying calculation is the physical six-point
external-mass jet in a strongly ordered double-collinear region.  Its
two-emission coefficient must equal one half the square of the one-emission
rate for the Poisson completion to be dynamically selected.

Resolution locality is not spacetime locality.  The complete physical LSZ
S-matrix, finite NLO term, positivity beyond the coherent leading-log model,
and all-order Eq. (19) remain open.

## Verification receipt

All symbolic Python and TeX commands ran sequentially with
`ulimit -v 500000`.

| tier | command or check | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0 | Python byte-compile; JSON parse of work item, event, schema, and certificate | PASS | below 0.5 s | below cap |
| 0 | `git diff --check` on the scoped paths | PASS | below 0.3 s | negligible |
| 1 | producer exact reproduction | PASS, 30/30 | 0.46 s | 67,504 KB |
| 1 | independent relative-weight, three-profile GNS, Poisson, and Riesz verifier | PASS, 23/23 | 0.43 s | 71,940 KB |
| 1 | focused producer/verifier plus nine mutation tests | PASS, 11/11 | 4.35 s | 72,268 KB |
| 1 | two-pass Paper V and Paper VI PDF builds | PASS | 0.82 s / 1.10 s | 51,036 KB / 50,904 KB |
| advisory | Science Forge shadow rail | advisory exit 0; bridge audit not counted as PASS because the installed Forge binary/stdlib mismatch triggers `E9118`; corpus census reports baseline drift | 2.4 s | not measured |

Tier 2 was unnecessary because every imported certificate is unchanged and
content-addressed and this is a new leaf whose only direct generated consumers
are the rebuilt papers.  Tier 3 was not run: there is no freeze, release,
shared-core change, promotion of an existing lifecycle state, physical
multi-emission theorem, or Lorentzian claim.  No skipped or advisory check is
recorded as a pass.
