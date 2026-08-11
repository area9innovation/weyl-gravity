# BT semifinite relative Born weight

**Result:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

The normal-trace obstruction in
`REVERSE_PHYSICS_BT_CROSS_KREIN_TRACE_LIMIT_V1` does not end the finite
detector construction.  The completed orbit carrier has a canonical faithful
normal semifinite trace.  It assigns weight one to every localized orbit
projector and infinite weight to the identity.  Conditioning on a finite-trace
incoming projection then gives a normalized Born rule for finite exhaustive
output partitions, provided the process operators satisfy the same weak ghost
symmetry used by Bateman and Turok.

This is not a normalized trace on the full algebra.  The normalized corner
functional is nontracial, and an exact two-matrix-unit witness detects the
failure.  Consequently the construction is compatible with the preceding
no-go rather than a counterexample to it.  It establishes a finite-regulator
probability architecture but does not construct the nonlinear Eq. (19)
pushforward or its thermodynamic limit.

## 1. Semifinite orbit trace

On the orbit Hilbertization

\[
 \mathcal H_0=\ell^2(\mathbb Z),\qquad
 E_{mn}=|e_m\rangle\langle e_n|,
\]

the standard positive trace is

\[
 \operatorname{Tr}_{\!\infty}(T)
 =\sum_{n\in\mathbb Z}\langle e_n,T e_n\rangle_H,
 \qquad T\geq0,
\]

with the value $+\infty$ allowed.  This is faithful, normal, and
semifinite.  Its finite-rank restriction is the algebraic trace used in the
cross-Krein predecessor.  The bilateral shift is Hilbert unitary, so

\[
 \operatorname{Tr}_{\!\infty}(ZTZ^{-1})
 =\operatorname{Tr}_{\!\infty}(T)
\]

on the positive or trace ideal.  In particular,

\[
 \operatorname{Tr}_{\!\infty}(E_{nn})=1,
 \qquad
 \operatorname{Tr}_{\!\infty}(1)=+\infty.
\]

Thus the localized projector is not killed.  What fails is only the demand
that the identity have finite normalized weight.

For the symmetric orbit window

\[
 P_N=\sum_{n=-N}^{N}E_{nn},
 \qquad \operatorname{Tr}_{\!\infty}(P_N)=2N+1,
\]

define

\[
 \omega_N(T)=\frac{\operatorname{Tr}_{\!\infty}(P_NTP_N)}{2N+1}.
\]

Every $\omega_N$ is a normal state, $J_0P_NJ_0=P_N$, and

\[
 \omega_N(Z^k)=\delta_{k0}.
\]

Hence its restriction to the Laurent shift algebra already equals the
coefficient trace.  Conversely,

\[
 \omega_N(E_{00})=\frac{1}{2N+1}\longrightarrow0.
\]

The normalized orbit average and a localized detector are therefore distinct
limits.

## 2. Why the conditional state is not a trace

For any finite-trace projection $P$, one may condition by

\[
 \omega_P(T)=\frac{\operatorname{Tr}_{\!\infty}(PTP)}
 {\operatorname{Tr}_{\!\infty}(P)}.
\]

The underlying $\operatorname{Tr}_{\!\infty}$ is cyclic on its trace ideal,
but $\omega_P$ is not cyclic in general.  The smallest witness is

\[
 P=E_{00},\qquad X=E_{01},\qquad Y=E_{10}.
\]

Then

\[
 \omega_P(XY)=1,
 \qquad
 \omega_P(YX)=0.
\]

This exact defect is load-bearing.  Requiring $\omega_P$ itself to be a
cyclic trace would restore the hypotheses of the preceding normalized-trace
no-go.  Conditional probability does not require that stronger property.

## 3. Conditional Born theorem

Let $P_{\rm in}$ be a finite-rank, $J$-even,
Krein-self-adjoint projection with

\[
 r=\operatorname{Tr}_{\rm fin}(P_{\rm in})>0.
\]

Let $S$ be cross-Krein isometric on its range, and let a finite family of
orthogonal Krein-self-adjoint output projections $P_i$ be exhaustive on
$S\operatorname{Ran}P_{\rm in}$.  Set

\[
 A_i=P_iSP_{\rm in}.
\]

Assume each process has the Bateman--Turok weak ghost decomposition

\[
 A_i=B_i+C_i,
\]

where $B_i$ commutes with $J$, and

\[
 \operatorname{Tr}(C_i^\dagger C_i)
 =\operatorname{Tr}(B_i^\dagger C_i)
 =\operatorname{Tr}(C_i^\dagger B_i)=0.
\]

Then

\[
 p_i=\frac{\operatorname{Tr}_{\rm fin}(A_i^\dagger A_i)}{r}
\]

is nonnegative because

\[
 \operatorname{Tr}(A_i^\dagger A_i)
 =\operatorname{Tr}(B_i^*B_i)\geq0.
\]

It is normalized without using $\operatorname{Tr}_{\!\infty}(1)$:

\[
 \sum_i\operatorname{Tr}(A_i^\dagger A_i)
 =\operatorname{Tr}\!\left(
 P_{\rm in}S^\dagger\sum_iP_iSP_{\rm in}\right)
 =\operatorname{Tr}(P_{\rm in})=r.
\]

The certificate contains two exact rational controls.

1. On a three-dimensional carrier with $J=\operatorname{diag}(1,1,-1)$,
   the rational positive-sector rotation

   \[
   S=\begin{pmatrix}
   3/5&-4/5&0\\
   4/5& 3/5&0\\
   0&0&1
   \end{pmatrix}
   \]

   is $J$-unitary and ghost symmetric.  A rank-one incoming projection and
   the three coordinate outputs give weights
   $9/25,16/25,0$, which are nonnegative and sum to one.

2. In the null basis with
   $J=\left(\begin{smallmatrix}0&1\\1&0\end{smallmatrix}\right)$, take
   $B=(3/5)1$ and $C=(4/5)E_{01}$.  Then $C\ne0$,
   $C^\dagger=C$, $C^\dagger C=0$, both cross traces vanish, and

   \[
   \operatorname{Tr}((B+C)^\dagger(B+C))
   =\operatorname{Tr}(B^\dagger B)=\frac{18}{25}.
   \]

The second fixture verifies that the theorem genuinely covers a nonzero null
remainder rather than only a positive Hilbert subspace.

## 4. Scope and remaining gate

The finite identity-normalization barrier is bypassed legitimately:

- the cyclic object is the semifinite trace $\operatorname{Tr}_{\!\infty}$;
- the probability normalization is relative to a finite incoming projection;
- the normalized corner state is not asserted to be cyclic;
- positivity still requires the weak ghost decomposition.

The remaining BT gate is consequently sharper.  One must compute the
zero-mode-completed order-$\lambda$ pushforward of a finite two-particle
detector projection and show that its neutral and radical pieces remain in the
$\operatorname{Tr}_{\!\infty}$-finite paired ideal under the weighted squeeze.
Only then can one ask for a local non-normal thermodynamic limit.

This report does not establish control of the unbounded squeeze on the full
trace ideal, a normal thermodynamic state, the nonlinear $R_t$, Eq. (19),
the physical $1/48$, a complete NLO probability, a gravitational or BRST
lift, or any `LORENTZIAN-CAUSAL` claim.

## 5. Verification receipt

All commands were run sequentially under a 500,000 KB virtual-memory cap.

- Producer: `python3 reverse_physics/bt_semifinite_relative_born_weight.py --check`
  — 29/29 pass; 0.04 s; maximum RSS 20,844 KB.
- Independent verifier:
  `python3 reverse_physics/verify_bt_semifinite_relative_born_weight.py`
  — 14/14 pass; 0.12 s; maximum RSS 30,312 KB.
- Scoped mutation suite:
  `python3 -m unittest -v reverse_physics.tests.test_bt_semifinite_relative_born_weight`
  — 8/8 pass; 0.84 s; maximum RSS 30,672 KB.
- Advisory repository-wide shadow rail: `ci/science-forge-shadow.sh` — not a
  pass.  Under the same memory cap, two optional `cbp` call-graph helpers
  aborted and the advisory rail produced no further result for approximately
  107 s; it was interrupted with exit 130.  This does not promote or falsify
  the scoped certificate.

Tier 0 covered Python compilation, JSON parsing, and the scoped diff check.
Tier 1 is the producer, independent verifier, and mutation suite above.  Tier
2 covered the direct paper consumers: Papers V and VI were each compiled twice
and their extracted text was checked.  The unchanged predecessor certificates
are pinned by hash and their transitive chain was not rebuilt.
Tier 3 was not run because this is neither a freeze, theorem-lifecycle
promotion beyond `CLASSIFIED`, shared-core change, nor release.

The repository-local `s-f` resolver selected the unrelated
`bp2transformer` programme, so no mutating `s-f` command was used.  An explicit
attempt to run `sfc work-event` against this planning directory failed to
compile in the external Forge source tree at `alloc/arena.forge:401`.  The DONE
transition is therefore an append-only manual `event-v0` fallback using the
same FNV-1a key and event shape as `sfc work-event`; no successful coordinator
pass is claimed.

CLOSE-OUT: DONE — the complete stop condition is met
EVIDENCE: `REVERSE_PHYSICS_BT_SEMIFINITE_RELATIVE_BORN_WEIGHT_V1`
