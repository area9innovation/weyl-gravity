# BT cross-Krein squeeze and the normal-trace limit

**Result:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

The explicit infrared-weighted carrier does support more of the Bateman--Turok
construction than the preceding audit established. The broken-vacuum orbit
has a genuine Krein completion, the covariant Appendix-C squeeze defines a
dense closable operator on a polynomial core, and the algebraic finite-rank
trace is cyclic and invariant under that squeeze. Thus neither the squeeze
factor nor finite-regulator trace cyclicity is the final obstruction.

The obstruction occurs when one asks for a single normalized trace on the
full orbit operator algebra or for a normal trace-class thermodynamic limit.
A finite normalized cyclic trace that is positive on the ghost-even cone must
give every orbit-localized rank-one projection weight zero. The canonical
finite-rank trace gives such a projection weight one, but the identity then has
infinite weight. Independently, the positive trace norm of the transported
vacuum projection grows exponentially with volume, with an exact positive
exponent. A semifinite, relative, or non-normal Born weight is therefore new
required architecture, not a detail supplied by the ordinary operator trace.

## 1. Completing the broken-vacuum orbit

Complete the Laurent orbit algebra on

\[
 \mathcal H_0=\ell^2(\mathbb Z),\qquad
 e_n\longleftrightarrow Z^n.
\]

Define

\[
 [e_m,e_n]_0=\delta_{m+n,0},\qquad
 J_0e_n=e_{-n}.
\]

Then

\[
 [e_m,J_0e_n]_0=\delta_{mn},
\]

so $J_0$ is a bounded fundamental symmetry and the induced Hilbert product is
the standard one on $\ell^2(\mathbb Z)$. Multiplication by the orbit coordinate
is the bilateral shift

\[
 Ze_n=e_{n+1}.
\]

Its Hilbert adjoint is $Z^*=Z^{-1}$, while its Krein adjoint is

\[
 Z^\dagger=J_0Z^*J_0=Z.
\]

The boost generator $Ne_n=ne_n$ obeys $N^\dagger=-N$ on the finite Laurent
core. This is a genuine nondegenerate Krein representation of the orbit data
used in the zero-mode predecessor.

There are already two distinct traces here. The coefficient functional
$\tau_0(Z^n)=\delta_{n0}$ defines the Laurent pairing and is normalized on the
shift algebra. It is not the operator trace on finite-rank endomorphisms of
$\ell^2(\mathbb Z)$. Conflating these two traces hides the obstruction below.

## 2. The covariant squeeze has a cross-Krein implementation

Let the weighted nonzero-mode Hilbertization use the normalized bosons
$A_p,D_p$, with

\[
 [A_p,A_q^*]=[D_p,D_q^*]=\delta_{pq},
 \qquad J_FA_pJ_F=D_p.
\]

For one unordered momentum pair, the zero-mode-completed generator is

\[
 Q_p=z_pZ^2A_p^*A_{-p}^*
     -\overline z_pZ^2D_pD_{-p}.
\]

Because $Z^\dagger=Z$ and the Krein adjoint exchanges the $A$ and $D$
families,

\[
 Q^\dagger=-Q.
\]

All creation terms commute with all $D$-annihilation terms. Hence, on the
Laurent finite-support tensor finite-particle core,

\[
 S=e^Q=e^{Z^2C_A^*}e^{-Z^2C_D}.
\]

The annihilation exponential terminates on every polynomial vector. The
creation exponential is a Hilbert vector precisely under the already
certified conditions

\[
 \sup_p|z_p|<1,\qquad
 \sum_{\{p,-p\}}|z_p|^2<\infty.
\]

The Hilbert adjoint has the corresponding $D^*$ creation exponential and is
defined on the same dense polynomial core. Therefore $S$ is closable. On its
Gaussian image core,

\[
 S^\dagger=S^{-1}=e^{-Q}.
\]

The Baker--Campbell--Hausdorff series stops after one commutator:

\[
 S^{-1}A_pS=A_p+z_pZ^2A_{-p}^*,
\]

\[
 S^{-1}D_p^*S=D_p^*+\overline z_pZ^2D_{-p}.
\]

The two off-diagonal contributions to each cross commutator cancel exactly.
This constructs the covariant Appendix-C squeeze factor as a cross-Krein
canonical operator. It is unbounded in the positive Hilbert topology and is
not the full nonlinear $R_t$.

For the exact fixtures $z=1/2$ and $(z_1,z_2)=(1/2,1/3)$, the positive vacuum
norms squared are respectively

\[
 \frac{1}{1-1/4}=\frac43,
 \qquad
 \frac{1}{(1-1/4)(1-1/9)}=\frac32,
\]

while both Krein norms remain exactly one.

## 3. A cyclic Born trace exists on the finite-rank core

For core vectors $x,y$, define

\[
 \Theta_{x,y}u=x[y,u].
\]

The canonical algebraic operator trace is

\[
 \operatorname{Tr}_{\rm fin}\Theta_{x,y}=[y,x].
\]

It is cyclic whenever one factor is finite rank and the products preserve the
paired cores. Cross-Krein isometry gives

\[
 S\Theta_{x,y}S^{-1}=\Theta_{Sx,Sy},
\]

and therefore

\[
 \operatorname{Tr}_{\rm fin}\Theta_{Sx,Sy}
 =[Sy,Sx]=[y,x].
\]

Finite-rank Krein-self-adjoint projections remain idempotent and
Krein-self-adjoint under this transport. This is a genuine construction of
the finite-regulator cyclic trace. It does not put the identity, continuum
momentum-window projectors, or arbitrary unbounded similarities into a
trace-class ideal.

## 4. A normalized orbit trace must kill localized projectors

Let

\[
 E_n=|e_n\rangle\langle e_n|,
 \qquad E_n=Z^nE_0Z^{-n}.
\]

Suppose a functional $\tau$ is cyclic on an algebra containing $Z,Z^{-1},E_0$
and finite symmetric sums, satisfies $\tau(1)=1$, and is positive on the
$J_0$-even projection cone. Cyclicity implies

\[
 \tau(E_n)=\tau(E_0)=c
\]

for every integer $n$. The symmetric projection

\[
 P_N=\sum_{n=-N}^NE_n
\]

is $J_0$-even. Positivity of $P_N$ and $1-P_N$ gives

\[
 0\le(2N+1)c=\tau(P_N)\le1
\]

for every $N$. Hence

\[
 c=0.
\]

This proof uses only finite sums; normality is not assumed. Consequently, a
finite normalized positive cyclic extension of the coefficient trace can
exist only by making every orbit-localized rank-one projection trace-null.
Conversely, $\operatorname{Tr}_{\rm fin}(E_0)=1$, but
$\operatorname{Tr}_{\rm fin}(1)=\infty$ and the bilateral shifts are outside
its trace-class domain.

Thus the two natural branches cannot be silently identified:

1. the normalized orbit trace has finite identity weight but kills localized
   orbit projectors;
2. the finite-rank Born trace sees those projectors but is semifinite and does
   not trace the identity or shifts.

## 5. Exact thermodynamic trace-norm growth

Let

\[
 \Psi_V=S_V(e_0\otimes|0\rangle),
 \qquad
 P_V=\Theta_{\Psi_V,\Psi_V}.
\]

Krein isometry gives

\[
 [\Psi_V,\Psi_V]=1,
 \qquad
 \operatorname{Tr}_{\rm fin}(P_V)=1.
\]

As a Hilbert rank-one operator,
$P_V=|\Psi_V\rangle\langle J\Psi_V|$, so

\[
 \|P_V\|_1=\|\Psi_V\|_H^2
 =N_V
 =\prod_{\{p,-p\}}(1-|z_p|^2)^{-1}.
\]

For

\[
 z_\mu(p)=\frac{\gamma\mu^2}{p^2+\mu^2},
 \qquad 0<\gamma<1,
\]

the exact logarithmic trace-norm density is

\[
 \ell(\gamma,\mu)
 =\lim_{V\to\infty}\frac{\log N_V}{V}
 =\frac{\mu^3}{12\pi}
 \left[(1+\gamma)^{3/2}+(1-\gamma)^{3/2}-2\right].
\]

One derivation differentiates the radial integral:

\[
 \frac{d}{d\gamma}
 \int_0^\infty x^2
 \left[-\log\left(1-\frac{\gamma^2}{(1+x^2)^2}\right)\right]dx
 =\frac\pi2\left(\sqrt{1+\gamma}-\sqrt{1-\gamma}\right).
\]

The derivative is strictly positive for $\gamma>0$, and the integral vanishes
at zero. Thus $\ell>0$. At the exact fixture $\gamma=1/2$,

\[
 \frac{\ell\pi}{\mu^3}
 =\frac{3\sqrt6+\sqrt2-8}{48},
\]

with

\[
 \frac1{80}<\frac{\ell\pi}{\mu^3}<\frac1{48}.
\]

Writing $y=48\ell\pi/\mu^3+8$, the exact algebraic witness is

\[
 y^4-112y^2+2704=0.
\]

Therefore

\[
 \|P_V\|_1=\exp(V\ell+o(V))
\]

diverges exponentially. There is no trace-norm thermodynamic limit of these
BT-normalized Krein projections.

Positive normalization does not evade the result. If
$\widehat\Psi_V=\Psi_V/\sqrt{N_V}$, then

\[
 [\widehat\Psi_V,\widehat\Psi_V]=N_V^{-1}\longrightarrow0.
\]

The corresponding unrenormalized Krein rank-one operator ceases to be an
idempotent. Dividing by its Krein norm to restore projector idempotence returns
exactly $P_V$ and its divergent trace norm.

## 6. Disposition

Established exactly:

- a nondegenerate $\ell^2(\mathbb Z)$ Krein completion of the vacuum orbit;
- a densely defined closable cross-Krein implementation of the covariant
  Appendix-C squeeze factor on paired cores;
- the cyclic, transport-invariant finite-rank Born trace;
- the normalized orbit-trace extension no-go for nonzero rank-one weight;
- the exact positive thermodynamic trace-norm exponent;
- failure of positive normalization to retain Krein projector idempotence.

Not established:

- a bounded positive-Hilbert unitary or the full nonlinear $R_t$;
- a semifinite, relative, or non-normal generalized-Born weight suitable for
  continuum projectors;
- Eq. (19), the physical $1/48$, or a complete NLO probability;
- a gravitational/BRST lift or anything `LORENTZIAN-CAUSAL`.

The next gate is no longer “find any trace.” It is to choose a trace
architecture explicitly and prove its normalization: a semifinite trace with
relative detector weights, a local thermodynamic weight, or a non-normal
functional. The full zero-mode-completed nonlinear projector must then be
transported on that same domain.

Verification commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_cross_krein_trace_limit.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_cross_krein_trace_limit.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_cross_krein_trace_limit
```

## Verification receipt (2026-08-11)

All scientific commands ran sequentially with `ulimit -v 500000`.

- Python parse/compile: PASS, 0.03 s, 16,184 KB peak RSS.
- Exact producer replay: PASS 27/27, 0.04 s, 20,812 KB peak RSS.
- Method-distinct strict-schema, orbit-adjoint, squeeze-norm, finite-rank
  trace, translate-bound, algebraic-radical, trace-norm, provenance, and claim
  verifier: PASS 15/15, 0.12 s, 30,232 KB peak RSS.
- Producer, verifier, and seven decisive mutations: PASS 9/9, 1.05 s,
  30,572 KB peak RSS. Mutations changed the orbit fundamental symmetry,
  squeeze-core status, finite-rank trace scope, normalized translate bound,
  exact log-density radical, trace-norm limit, and physical claim; every
  mutation was rejected.
- Content-addressed affected chain: inclusive radical PASS 12/12 in 0.38 s
  (30,420 KB), fixed-vacuum oscillatory PASS 4/4 in 0.28 s (29,816 KB), soft
  charge flow PASS 7/7 in 0.70 s (30,588 KB), zero-mode trilemma PASS 7/7 in
  0.69 s (30,364 KB), ordinary squeeze audit PASS 8/8 in 0.81 s (30,292 KB),
  and extended-carrier audit PASS 8/8 in 0.81 s (30,372 KB).
- Papers V and VI: PASS, two `pdflatex -halt-on-error` passes each. Paper V
  took 0.42/0.43 s and Paper VI took 0.45/0.45 s; peak RSS remained below
  51 MB. PDF text witnesses found the cross-Krein core, finite-rank trace,
  normalized-trace no-go, exact thermodynamic exponent, scalar dependency
  tags, and missing nonlinear/causal boundary.
- The new schema, certificate, work item, and append-only event parsed as JSON.
  The event's FNV-1a id reproduced exactly. The manual event-v0 fallback is
  used because the coordinator's Go startup is already certified to exceed the
  mandatory memory cap; no coordinator pass is claimed.
- The official arXiv API was checked on 2026-08-11. Bateman--Turok remains
  `2607.00096v1`; Lill's generic architecture source remains `2208.03487v2`,
  and the journal-length implementation paper is `2204.13407v2`. These are
  provenance checks, not theorem imports for the cross-Krein construction.
- The first default `git diff --check` attempt could not create a threaded
  index scan because the shared host temporarily lacked a thread resource; it
  is recorded as a failed attempt, not a pass. The deterministic retry with
  `git -c core.preloadIndex=false diff --check` completed successfully without
  changing the tree.
- The advisory Science Forge shadow rail was not rerun. Its recent recorded
  path failed/stalled under the mandatory cap and is not a scoped promotion
  criterion for this independent certificate.

Tier 2 stopped at the content-addressed affected chain above. Tier 3 was not
run because this is a `CLASSIFIED` scalar reduced-mode result, not a freeze,
release, shared-core change, or lifecycle theorem promotion.
