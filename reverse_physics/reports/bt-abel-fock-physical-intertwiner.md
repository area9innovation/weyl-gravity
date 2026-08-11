# BT physical Abel--Fock range intertwiner

## Result

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.  Lifecycle:
`CLASSIFIED`.

The first stochastic BT jump now has an exact physical continuum-range
affiliation, not only a matching scalar rate.  The affiliation requires the
correlated system--noise one-particle sector.  A noise-only formulation loses
one of the two physical external-jet species in every pair channel.

The result has three parts:

1. The raw fixed-regulator physical columns are exactly obstructed from being
   related by isometric resolution translations.
2. Their normalized positive polar ranges possess canonical partial-unitary
   transports and combine isometrically with the Abel purification.
3. This construction physically affiliates edge marks 0, 1, and 2.  The
   remaining 72 HP edge marks still lack measurable nested continuum columns.

## Raw-column covariance obstruction

For daughter mass ratio (r), the certified physical collinear column is

\[
 (V_rh)(u)=T(r,u)h,
 \qquad
 V_r^\sharp V_r=I(r)I_2,
\]

where

\[
 I(r)=\frac{5r^3-6r^2\log r-3r^2-6r\log r+3r-5}
 {24(r-1)}.
\]

If an isometry (Z_b(R)) with (R=-\log r) obeyed

\[
 Z_b(R)V_{e^{-R}}=V_{e^{-(R+b)}},
\]

then the two columns would have the same adjoint Gram.  They do not.  Exact
fixtures give

\[
 I\!\left(\frac14\right)=\frac{31}{128}-\frac5{24}\log2,
 \qquad
 I\!\left(\frac1{16}\right)=\frac{439}{2048}-\frac{17}{240}\log2,
\]

and hence

\[
 I\!\left(\frac1{16}\right)-I\!\left(\frac14\right)
 =\frac{11}{80}\log2-\frac{57}{2048}
 >\frac{419}{10240}>0.
\]

The strict lower bound uses only
(log2=\int_1^2dx/x>\int_1^2dx/2=1/2).  Thus the raw physical columns are
not a stationary resolution-noise field.  This is consistent with the earlier
non-differentiable threshold Gram and prevents hiding an (r)-dependent
normalization inside the word ``intertwiner.''

## Normalized physical polar ranges

Above threshold the pointwise map and Gram are

\[
 T(r,u)=\operatorname{diag}\!\left(
 \frac{2u(1+r)-(1-r)^2}{2u^2},
 -\frac{(1-r)^2}{2u}
 \right),
\]

\[
 -T^\sharp T=\rho(r,u)I_2,
 \qquad
 \rho(r,u)=\frac{(1-r)^2[2u(1+r)-(1-r)^2]}{4u^3}>0.
\]

Writing (r=z^2), the nontrivial numerator at the two-body threshold factors
as ((1+z)^4), proving positivity on the full declared domain.  Therefore the
normalized direct-integral column

\[
 E_R=\frac{V_{e^{-R}}}{\sqrt{I(e^{-R})}}
\]

obeys (E_R^\sharp E_R=I_2).  Its range projection and canonical transport are

\[
 P_R=E_RE_R^\sharp,
 \qquad
 C_b(R)=E_{R+b}E_R^\sharp.
\]

On the physical ranges,

\[
 C_b(R)^\sharp C_b(R)=P_R,
 \qquad
 C_b(R)C_b(R)^\sharp=P_{R+b},
\]

and

\[
 C_c(R+b)C_b(R)=C_{b+c}(R).
\]

The normalization is explicit and (r)-dependent.  It retains the complete
pointwise physical shape and common real amplitude phase, while the scalar
cell intensity is supplied separately by the certified relative Born weight.

Identical-daughter exchange extends the measurable range family across both
orientations of the Abel line.  Under (r\mapsto1/r), (u\mapsto u/r), the
exact scaling relations are

\[
 \frac{I(1/r)}{I(r)}=\frac1{r^2},\quad
 \frac{Q(1/r,u/r)}{Q(r,u)}=1,\quad
 \frac{L(1/r,u/r)}{L(r,u)}=\frac1r,
\]

\[
 \frac{\rho(1/r,u/r)}{\rho(r,u)}=\frac1r,
 \qquad
 \frac{d\mu_{1/r}(u/r)}{d\mu_r(u)}=\frac1r.
\]

The equal-mass fibre has (I(1)=0) and is a measure-zero null fibre.

## Abel--physical isometry

The correctly typed HP first-emission carrier is

\[
 \mathcal H_{\mathrm{HP},1}^{\mathrm{phys}}
 =L^2(\mathbb R_+,ds)\otimes\mathbb C^3_{\mathrm{pair}}
 \otimes\mathbb C^2_{\mathrm{species}}.
\]

It is the correlated subspace of the level-one system sector tensored with the
one-particle sector of
(Gamma_s(L^2(\mathbb R_+)\otimes\mathbb C^{75}_{\rm edge})).  The pair
channel is recorded by the noise mark; the two species remain in the system.

Let

\[
 p_s(y)=\frac12\operatorname{sech}^2(y-s),
 \qquad \int_{-\infty}^{\infty}p_s(y)\,dy=1.
\]

On the direct integral of the normalized physical ranges define

\[
 (Af)_i(s,y)=\sqrt{p_s(y)}E_yf_i(s).
\]

Its adjoint is

\[
 (A^\sharp\psi)_i(s)=
 \int_{-\infty}^{\infty}\sqrt{p_s(y)}E_y^\sharp\psi_i(s,y)\,dy.
\]

The polar and Abel normalizations give

\[
 A^\sharp A=I,
 \qquad
 AA^\sharp=P_{\operatorname{Ran}A}.
\]

Thus (A^\sharp), restricted to (operatorname{Ran}A), is the requested
physical-to-system--Fock coisometry.  For an interval (I\subset\mathbb R_+),

\[
 A[\mathbf1_Ie_i\otimes h]
 =\mathbf1_I(s)\sqrt{p_s(y)}E_yh,
\]

which is precisely the Abel purified shell with the complete normalized
physical collinear shape attached.

## Translation intertwining

Let the HP right shift be (S_bf(s)=f(s-b)), with zero extension on the
additive half-line.  On the physical range define

\[
 (T_b\psi)(s,y)=E_yE_{y-b}^\sharp\psi(s-b,y-b).
\]

Because (p_{s-b}(y-b)=p_s(y)),

\[
 T_bA=AS_b,
 \qquad
 A^\sharp T_b=S_bA^\sharp
\]

on the transported range, and (T_cT_b=T_{b+c}).  This is covariance in the
auxiliary resolution coordinate.  It is not Minkowski-time evolution or a
spacetime translation theorem.

## First HP jump and the typing obstruction

The certified intensity is

\[
 q_0=\frac1{48}
\]

per unordered pair.  Hence an interval of length (a) has physical norm
(a/48) in each of the three pair ranges and total norm (a/16).  The HP hard
drift is half the total rate, (1/32), exactly as in the stochastic dilation.

The full correlated vacuum column is

\[
 \sqrt{q_0}\sum_{i=1}^3
 |c_i,\sigma\rangle_{\rm sys}\otimes
 \mathbf1_I(s)|e_i\rangle_{\rm noise}.
\]

Under (A), each term becomes
(sqrt{q_0}\mathbf1_I(s)\sqrt{p_s(y)}E_y|\sigma\rangle).  Thus the
affiliation retains the full rank-two physical species and the pointwise
collinear shape, not only the integrated scalar probability.

A noise-only, channel-faithful target cannot do this.  Each pinned pair mark
is one-dimensional, so a map
(mathbb C^2_{\rm species}\to\mathbb Ce_i) has rank at most one, whereas the
physical Gram ((1/48)I_2) has rank two.  Encoding the second species in an
unrelated higher-level mark would violate the certified edge grading.  Keeping
the level-one system species repairs the rank exactly, giving dimension
(3\times2=6).

## The 75-mark boundary

Only edge marks 0, 1, and 2 now have certified physical continuum-range
intertwiners.  The 12 second-level and 60 third-level marks retain their exact
six- and seven-point amplitude quotient affiliation, but those results do not
supply measurable nested direct-integral columns, common ordered-resolution
measures, or dense continuum domains.  Consequently the full 75-mark physical
operator intertwiner is not constructed.

This changes the optimal next calculation.  Computing the eight-point scalar
fourth rate would add more quotient marks while leaving the already missing 72
continuum domains untouched.  The next physical gate is instead the nested
six-point direct-integral column for the 12 second-level edges.

## Independent verification

The independent verifier does not import the producer.  It reconstructs the
threshold Gram and pointwise map, proves positivity on the full threshold
domain, derives the two exact nonconstant-Gram fixtures, checks the daughter
exchange and measure scaling, and uses separate rational (4\times2) polar
embeddings to verify both partial-unitary identities and their cocycle.  It
then verifies the Abel kernel, translation identity, physical interval rates,
system--noise dimension, edge partition, input hashes, and every fail-closed
claim boundary.

The certificate is
`REVERSE_PHYSICS_BT_ABEL_FOCK_PHYSICAL_INTERTWINER_V1`.

## Claim boundary

This is a first-emission physical continuum-range affiliation on an auxiliary
resolution carrier.  It does not establish raw-column covariance, a noise-only
species encoding, continuum affiliation of the remaining 72 edges, a fourth
jump, complete sectors or probability, a spacetime Møller/LSZ/S operator,
identification with the public (R_t), Eq. (19), a metric/BRST lift, a new
physical dimension, anything `LORENTZIAN-CAUSAL`, or literature priority.

## Verification receipt

All scientific Python, SymPy, and TeX processes run sequentially under
`ulimit -v 500000`.

| tier | command or check | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0 | Python compile and JSON/schema parse on scoped artifacts | PASS | below 1 s | below 75 MB |
| 0 | `git diff --check` on scoped paths | PASS | below 0.1 s | negligible |
| 1 | exact producer and certificate drift check | PASS, 30/30 | 0.68 s | 70,244 KB |
| 1 | method-distinct verifier | PASS, 25/25 | 0.66 s | 74,388 KB |
| 1 | producer/verifier plus sixteen falsifying mutations | PASS, 18/18 | 5.78 s | 74,688 KB |
| 1 | Paper V two-pass PDF build | PASS; no new overfull box | 0.44 / 0.44 s | 50,916 / 50,608 KB |
| 1 | Paper VI final two-pass PDF build | PASS; no warning or overfull box | 0.49 / 0.54 s | 51,064 / 50,748 KB |
| advisory | Science Forge programme import | PASS; 1,402 nodes, 0 invalid items, 0 malformed events | 6.24 s | 589,224 KB |

The advisory Science Forge shadow rail exited zero while reporting, rather
than clearing, two substrate findings: the cached Forge binary's embedded
standard-library hash differs from the current `FORGE_LIB`, and the independent
bridge audit fails closed at Forge diagnostic `E9118`.  Its read-only census
also reports corpus drift to 1,537 certificates from the 2026-07-19 baseline of
976.  These are advisory substrate/corpus findings, not successful verification
of this result; only the independent programme import above is recorded as a
pass.

Tier 2 is unnecessary because this is a new operator-level consumer of
unchanged, content-addressed physical-factorization, rigged, Abel, Born, HP,
branching, and quotient inputs.  Tier 3 is unnecessary because no freeze,
release, shared-core change, lifecycle promotion beyond `CLASSIFIED`, complete
probability, Eq. (19), gravitational transfer, or Lorentzian theorem is
asserted.  No skipped or advisory rail is counted as a pass.

## Successor gate

`REVERSE_PHYSICS_BT_SIX_POINT_NESTED_CONTINUUM_INTERTWINER_V1` constructs the
requested four-component quotient range and uses its positive Gram times the
exact Källén measure to define a common cumulative resolution coordinate.  It
intertwines the ordered two-noise sector and physically affiliates all 12
second-level edges.  Across the two certificates, marks 0 through 14 therefore
have physical continuum ranges.  The next gate is the corresponding
seven-point nested column for the remaining 60 marks.
