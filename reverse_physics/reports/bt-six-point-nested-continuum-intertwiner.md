# BT six-point nested continuum intertwiner

## Result

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.  Lifecycle:
`CLASSIFIED`.

The complete positive six-point parent/profile quotient has an exact physical
nested direct-integral realization.  Its conditional Gram and the physical
two-body Källén measure together define a canonical cumulative resolution
coordinate.  In that coordinate the physical measure is ordinary Lebesgue
measure, so the quotient column is unitarily equivalent to one HP resolution
increment.  Composing it with the first-emission Abel column gives an exact
ordered two-noise isometry for edge marks 3 through 14.

Thus the physical continuum affiliation now covers marks 0 through 14: the
three first-emission edges and all twelve second-emission edges.  The sixty
third-level marks remain quotient-only.

## Positive quotient range

Set

\[
 r=\frac{a_1}{a_0},\qquad w=\frac{\tau_1}{a_0},\qquad
 \Delta_r(w)=\sqrt{\lambda(w,1,r)},
\]

and write the six-point quotient parameters as

\[
 q(r,w)=2Q_{\rm inner}
 =\frac{2w(1+r)-(1-r)^2}{2w^2},
 \qquad v=\frac{a_2}{2}.
\]

The exact physical domain is

\[
 w>(1+\sqrt r)^2.
\]

At threshold the numerator of (q) is

\[
 2(1+\sqrt r)^2(1+r)-(1-r)^2=(1+\sqrt r)^4>0,
\]

and it increases with (w).  Hence (q>0) throughout the physical domain.

On the four-component parent-jet times profile carrier, let

\[
 \eta=J\otimes3J,
 \qquad J=\begin{pmatrix}0&1\\1&0\end{pmatrix},
\]

and use the image and kernel bases

\[
 N_+=\begin{pmatrix}
 v&0\\0&v\\q&0\\0&q
 \end{pmatrix},
 \qquad
 N_-=\begin{pmatrix}
 v&0\\0&v\\-q&0\\0&-q
 \end{pmatrix}.
\]

They obey

\[
 N_+^T\eta N_+=6qvJ,
 \qquad
 N_-^T\eta N_-=-6qvJ,
 \qquad
 N_-^T\eta N_+=0.
\]

The profile fundamental symmetry changes the image form to (6qvI_2>0).
Moreover, for the certified diagonal amplitude map (D) and collapse (R),

\[
 RDN_+=2qvI_2,
 \qquad RDN_-=0.
\]

Thus the kernel remains exactly collapse-invisible, while

\[
 E_6(r,w,a_2)=\frac{N_+}{\sqrt{6qv}}
\]

is the normalized positive quotient range.  The nonzero conditional physical
Gram is

\[
 \lambda_6(r,w,a_2)=2qv=a_2q.
\]

This retains the complete arbitrary-vector identity from the six-point
quotient; it is not inferred from the final number (5/3072).

## Canonical physical resolution

The inner two-body measure is

\[
 d\mu_r(w)=\frac{\Delta_r(w)}{w}\,dw.
\]

The large-(w) coefficient of
(lambda_6d\mu_r) is (a_2(1+r)d\log w).  Dividing by this coefficient
therefore fixes, rather than fits, the cumulative physical resolution:

\[
 d\sigma_r(w)
 =\frac{\lambda_6}{a_2(1+r)}d\mu_r(w)
 =\frac{q(r,w)\Delta_r(w)}{(1+r)w}\,dw.
\]

Every factor is positive above threshold.  Also

\[
 \lim_{w\to\infty}\frac{d\sigma_r}{d\log w}=1.
\]

Taking (sigma_r=0) at threshold makes
(sigma_r) continuous and strictly increasing.  It tends to infinity, so
it is a bijection from the threshold ray to (mathbb R_+).

This last statement has an exact primitive.  Put (r=m^2) and

\[
 w=1+m^2+m(z+z^{-1}),
\]

where (z=1) is threshold and (z\to0) is infinity.  With
(A=1+m^2) and (C=m^4+m^2+1), one primitive is

\[
\begin{split}
 F_m(z)={}&
 \frac{m^2(m^2-1)}{4A(m+z)^2}
 -\frac{m^2-1}{4A(mz+1)^2}
 -\frac{2m^2+3}{2A(mz+1)}\\
 &-\frac{m(3m^2+2)}{2A(m+z)}
 +\frac{C}{(m^2-1)A}
   \log\frac{mz+1}{m+z}-\log z.
\end{split}
\]

Exact differentiation gives (dF_m=d\sigma_r), after the displayed
rationalizing substitution, and (F_m(1)=-5/4).  Hence

\[
 \sigma_r(w)=F_m(z(w))-F_m(1).
\]

The only divergent term as (z\to0) is (-\log z).  At equal daughter mass,
the removable limit is

\[
 F_1(z)=-\log z-\frac4{1+z},
\]

with its threshold value subtracted.

The construction is also exchange-independent.  Under

\[
 r\mapsto r^{-1},\qquad w\mapsto w/r,
\]

(q) is invariant, the pulled-back Källén measure scales by (r^{-1}),
and (1+r) scales by the same factor.  Therefore

\[
 \sigma_{1/r}(w/r)=\sigma_r(w).
\]

All daughter orientations consequently use the same physical resolution
coordinate.

## Conditional direct-integral isometry

On the measurable field of positive quotient ranges define

\[
 (B_rf)(w)=
 \sqrt{\frac{\lambda_6(r,w,a_2)}{a_2(1+r)}}
 E_6(r,w,a_2)f(\sigma_r(w)).
\]

Then

\[
 \|B_rf\|^2
 =\int d\mu_r(w)
   \frac{\lambda_6}{a_2(1+r)}
   \|f(\sigma_r(w))\|^2
 =\int_0^\infty d\sigma\,\|f(\sigma)\|^2.
\]

Because (sigma_r) is bijective and (E_6) has full rank on its
two-dimensional image, (B_r) is unitary onto the quotient-range direct
integral, not merely norm preserving on a selected vector.

Right translation in (sigma) conjugates through (B_r) to a physical
transport along

\[
 w\longmapsto\sigma_r^{-1}(\sigma_r(w)+b).
\]

Written in the (w) coordinate, the transport contains the ratio of the two
square-root Radon--Nikodym factors and the canonical polar transport between
the two quotient ranges.  These factors telescope, so the transports compose
exactly.  This is an auxiliary resolution shift, not Minkowski time
translation.

## Ordered two-noise carrier

The correctly typed HP carrier through two emissions is

\[
 \mathcal H^{\rm phys}_{\mathrm{HP},2}
 =L^2\!\left(\{0<t_1<t_2\},dt_1dt_2\right)
 \otimes\mathbb C^{12}_{\rm edge}
 \otimes\mathbb C^2_{\rm species}.
\]

Let (d=t_2-t_1).  The physical identification is

\[
 d=\sigma_r(w).
\]

Compose (B_r) with the certified first-emission Abel isometry at (t_1).
If (F_{y;r,w,a_2}) denotes the fibrewise composition of the normalized
outer physical column and (E_6), then

\[
\begin{split}
 (A_2f)_e(t_1,y,w)={}&
 \sqrt{p_{t_1}(y)}
 \sqrt{\frac{\lambda_6}{a_2(1+r)}}\\
 &\times F_{y;r,w,a_2}
 f_e(t_1,t_1+\sigma_r(w)).
\end{split}
\]

The Abel mass is one, the conditional change of variables is unitary, and
the normalized polar ranges are isometric.  Therefore

\[
 A_2^\sharp A_2=I,
 \qquad
 A_2A_2^\sharp=P_{\operatorname{Ran}A_2}.
\]

Joint HP shifts of (t_1,t_2) leave their difference fixed and intertwine the
first Abel polar transport.  The standard zero extension at the origin is
understood.  This proves the ordered-shift law on the physical nested range.

The twelve histories are exactly HP marks 3 through 14: each of the three
first-level pair histories has four children.  No unrelated mark is used to
store the quotient species.

## Finite hierarchy and dense domain

At finite hierarchy parameter (epsilon), after the harmless scale choice
(a_2=1), the exact outer threshold imposes

\[
 w\le\frac{(\sqrt U-1)^2}{\epsilon},
 \qquad U>1.
\]

For each fixed (U>1), this endpoint tends to infinity as
(epsilon\to0).  Hence the finite-(epsilon) domains exhaust every compact
(sigma) interval.

A common dense core consists of compactly supported sections in (t_1),
(sigma), the outer invariant (U>1), and the Abel mass-ratio coordinate,
bounded away from threshold endpoints.  On this core the outer parent ratio
is (r_{\rm out}=\epsilon w\) after rescaling the hierarchy parameter.  It
tends uniformly to zero.  The outer physical column has the local limits

\[
 T(r_{\rm out},U)\longrightarrow
 \operatorname{diag}\!\left(
 \frac{2U-1}{2U^2},-\frac1{2U}
 \right),
\]

\[
 d\mu_{r_{\rm out}}(U)\longrightarrow\frac{U-1}{U}\,dU,
 \qquad I(r_{\rm out})\longrightarrow\frac5{24}.
\]

This is a local inductive limit.  It never differentiates the column at the
massless endpoint.  The certified failure of a strong endpoint derivative is
therefore preserved rather than silently discarded.

## Rates and channel affiliation

The two physical conditional rates are

\[
 q_0=\frac1{48},\qquad q_1=\frac5{64}.
\]

For one labeled two-emission history,

\[
 q_0q_1=\frac5{3072}.
\]

The ordered simplex in an interval of length (a) has volume (a^2/2), so
one history has squared norm

\[
 \frac{5a^2}{6144}.
\]

Summing all twelve histories gives

\[
 12\frac{5a^2}{6144}=\frac{5a^2}{512},
\]

exactly the independently certified six-point coefficient.  Four children
per level-one parent also give the HP drift

\[
 \frac12(4q_1)=\frac5{32}.
\]

The cumulative coordinate fixes the physical shape and common measure.  The
rate (q_1) remains the separately computed threshold/factorial coefficient;
it is not adjusted by rescaling (sigma).

## Claim boundary

This is a physical continuum operator in the certified leading strongly
ordered reduced-mode sector.  It does not construct the sixty seven-point
continuum columns, the full 75-mark intertwiner, a fourth jump, a complete
probability, the non-strongly-ordered six-body sector, a strong massless
endpoint derivative, a spacetime Møller/LSZ/S operator, identification with
the public (R_t), Eq. (19), loop positivity, a metric/BRST lift, a new
physical dimension, anything `LORENTZIAN-CAUSAL`, or literature priority.

## Independent verification

The independent verifier does not import the producer.  It reconstructs the
image, kernel, collapse, and positive quotient Grams with exact rational
matrices at three Källén-rationalized fixtures.  It separately differentiates
the serialized primitive against the rationalized physical density, checks
the equal-mass limit, daughter exchange, Radon--Nikodym identity, hierarchy
exhaustion, outer massless boundary, exact HP edge enumeration, rates, hashes,
schema, and fail-closed boundaries.

The certificate is
`REVERSE_PHYSICS_BT_SIX_POINT_NESTED_CONTINUUM_INTERTWINER_V1`.

## Verification receipt

All scientific Python, SymPy, and TeX processes run sequentially under
`ulimit -v 500000`.

| tier | command or check | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0 | Python compile and JSON/schema parse on scoped artifacts | PASS | at most 0.03 s each | at most 15,524 KB |
| 0 | `git diff --check` on scoped paths | PASS | 0.01 s | 11,148 KB |
| 1 | exact producer and certificate drift check | PASS, 40/40 | 1.30 s | 71,972 KB |
| 1 | method-distinct verifier | PASS, 24/24 | 1.46 s | 76,980 KB |
| 1 | producer/verifier plus sixteen falsifying mutations | PASS, 18/18 | 25.83 s | 78,428 KB |
| 1 | Paper V two-pass PDF build | PASS, no new overfull box | 0.56 s + 0.48 s | 50,516 KB / 50,984 KB |
| 1 | Paper VI two-pass PDF build | PASS, no overfull box or warning | 0.48 s + 0.47 s | 50,484 KB / 50,744 KB |
| advisory | Science Forge planning import | PASS, 1,404 nodes, 0 invalid, 0 malformed | 12.80 s | 558,116 KB |

Tier 2 is unnecessary unless an imported amplitude, threshold, quotient,
stochastic operator, or schema changes.  This package is a new exact consumer
of unchanged content-addressed inputs.  Tier 3 is unnecessary because there
is no freeze, release, shared-core change, lifecycle promotion beyond
`CLASSIFIED`, complete probability, Eq. (19), gravitational transfer, or
Lorentzian theorem.  No skipped or advisory rail is counted as a pass.

The advisory Science Forge shadow rail exited zero but is not scientific
evidence: its cached Forge binary reported a standard-library hash mismatch,
the bridge audit failed closed with `E9118`, and the corpus census found 1,538
certificates against a baseline of 976.  Those drift findings are retained as
advisory diagnostics and are not promoted to a passing verification rail.

## Next gate

Construct the analogous seven-point cumulative physical resolution and
nested direct-integral column for edge marks 15 through 74.  The signed
seven-point quotient already has (u<0<v) and positive physical eigenvalue
(-2uv).  The decisive calculation is whether that eigenvalue times the
third Källén measure again defines a positive, exchange-compatible cumulative
coordinate onto (mathbb R_+).  A pass would physically affiliate all 75
currently available edge marks; a failure would isolate the first continuum
obstruction beyond six points.
