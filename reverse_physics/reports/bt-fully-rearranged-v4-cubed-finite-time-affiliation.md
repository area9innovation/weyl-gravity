# Fully rearranged BT $V_4^3$ finite-time affiliation

**Certificate:**
`REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_FINITE_TIME_AFFILIATION_V1`

**Tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.
**Lifecycle:** `COEFFICIENT_COMPUTED` for the isolated finite-duration block.

## Result

The covariant $V_4^3$ triangle is now affiliated with the actual
third-order sharp-time Dyson graph on the certified fully rearranged compact
packet.  The result includes all six time orderings and retains the transient
spatial loop integral.  It does not replace the finite-time graph by its
covariant limit.

For one chronological ordering, call the vertices earliest, middle and
latest, and write their times as

\[
 t_e=Tt,\qquad t_m=T(t+u),\qquad t_l=T(t+u+v),
 \qquad t,u,v\geq0,\quad t+u+v\leq1.
\]

The exact temporal factor is

\[
 T^3\Phi_3(T\Omega,T\Delta_1,T\Delta_2),
\]

where

\[
 \Phi_3(x,y,z)=
 \int_{t,u,v\geq0\atop t+u+v\leq1}
 e^{ixt+iyu+izv}\,dt\,du\,dv.
\]

If

\[
 f(x)=\int_0^1e^{ixs}\,ds=e^{ix/2}\operatorname{sinc}(x/2),
\]

then

\[
 \boxed{\Phi_3(x,y,z)=-f[x,y,z]}
\]

is the negative symmetric second divided difference.  For distinct
frequencies,

\[
 \Phi_3=-\left(
 {f(x)\over(x-y)(x-z)}+
 {f(y)\over(y-x)(y-z)}+
 {f(z)\over(z-x)(z-y)}\right).
\]

The divided-difference form fills every pairwise and triple collision by an
analytic limit.  In particular,

\[
 \Phi_3(0,0,0)={1\over6}.
\]

This is a two-intermediate-defect kernel.  The one-variable Fejér kernel that
controls the certified second-Dyson bubble does not determine it.

## Independent series reconstruction

The producer and verifier reconstruct the ordered simplex differently.  The
producer recursively enumerates weak compositions.  The verifier enumerates
all triples $(p,q,r)$ and applies the four-coordinate Dirichlet moment

\[
 \int_{t,u,v,w\geq0}\!\delta(1-t-u-v-w)t^pu^qv^r
 ={p!q!r!\over(p+q+r+3)!}.
\]

Multiplication by the exponential coefficient $1/(p!q!r!)$ proves that
every monomial of total degree $N$ has coefficient

\[
 {i^N\over(N+3)!}.
\]

Thus

\[
 \Phi_3(x,y,z)=\sum_{N\geq0}{i^N\over(N+3)!}h_N(x,y,z),
\]

with $h_N$ the complete homogeneous symmetric polynomial.  The certificate
records and independently verifies all coefficients through degree twelve;
the displayed identity proves the general coefficient.

## Six chronological sectors

Let $q_0,q_1,q_2$ be the external pair momenta in all-incoming convention.
For an ordering $(e,m,l)$, the phase becomes

\[
 \Omega=q_0^0+q_1^0+q_2^0,
\]

\[
 \Delta_1=q_m^0+q_l^0-(E_{em}+E_{el}),\qquad
 \Delta_2=q_l^0-(E_{ml}+E_{el}).
\]

The certificate lists all six permutations.  Their open simplexes are
disjoint and fill $[0,T]^3$ up to equal-time faces of measure zero.  Hence
their zero-frequency volumes sum to

\[
 6T^3\Phi_3(0,0,0)=T^3.
\]

This cube decomposition is also the normalization audit: the Dyson $1/3!$
cancels the $3!$ assignments of the identical quartic insertions to the
three labeled external pairs.  No further factor of $1/6$ is present.

## Exact switched triangle

For one fixed cyclic spatial routing use

\[
 E_{01}=|\ell|,\qquad
 E_{12}=|\ell+\mathbf q_1|,\qquad
 E_{02}=|\ell-\mathbf q_0|.
\]

For each of the fifteen external pairings $P$, define

\[
 J_{T,P}=\int {d^3\ell\over(2\pi)^3\,8E_{01}E_{12}E_{02}}
 \sum_{(e,m,l)}T^3
 \Phi_3(T\Omega,T\Delta_1,T\Delta_2).
\]

In the same overall-phase-stripped coefficient convention as the covariant
predecessor,

\[
 \boxed{T_{6,V_4^3,T}=8\sum_{P=1}^{15}J_{T,P}S_P.}
\]

The factor eight is the product of the three public $V/g=2$ tensors.  If the
same common Dyson/Feynman phase is restored on both sides, the standard time
representation

\[
 \Delta_F(t,\mathbf k)={e^{-i|\mathbf k||t|}\over2|\mathbf k|}
\]

shows that the unrestricted translation-invariant boundary is the certified
massless scalar triangle.  The exact finite-window decomposition is recorded
as

\[
 J_{T,P}={F_T(\Omega)\over16\pi^2}
 C_0(q_0^2,q_1^2,q_2^2)+R_{T,P},
\]

where $R_{T,P}$ is defined by the six-ordering spatial integral minus that
translation-invariant comparison term.  The result retains $R_{T,P}$; it
does not set it to zero or claim a closed polylogarithmic evaluation.

## Infrared and ultraviolet control

At the rational fully rearranged packet center, exact recomputation of all
fifteen external-pair spatial norms gives

\[
 \min_{a<b}|\mathbf p_a+\mathbf p_b|^2={32\over625}.
\]

Two internal energies can vanish simultaneously only if one corresponding
external pair has zero spatial momentum.  The margin therefore permits at
most one soft internal factor.  A single $1/E$ singularity is locally
integrable against $d^3\ell$.

For $r=|\ell|$ large, uniformly on a sufficiently small compact external
packet neighborhood,

\[
 \Delta_1=-2r+A,\qquad \Delta_2=-2r+B,
\]

with $A,B$ bounded.  Put $s=u+v$ and $u=sw$.  Then

\[
 \Phi_3=\int_0^1e^{-2irs}h(s)\,ds,
\]

where

\[
 h(s)=sJ_x(1-s)\int_0^1e^{is(Aw+B(1-w))}\,dw,\qquad
 J_x(a)=\int_0^a e^{ixt}\,dt.
\]

Both endpoints vanish: $h(0)=h(1)=0$.  Two integrations by parts therefore
give a uniform $|\Phi_3|\leq C/r^2$.  The three on-shell denominators and
radial measure contribute $O(dr/r)$, leaving

\[
 O\!\left({dr\over r^3}\right).
\]

Thus every $J_{T,P}$ is absolutely convergent for fixed $T>0$ and locally
bounded on the compact packet domain.  After reducing the common momentum
delta, the finite fifteen-tensor sum is Hilbert--Schmidt.  No UV counterterm
or finite scheme parameter is introduced.

## Common Born boundary

The predecessor proves coefficientwise

\[
 \kappa_3S_P\kappa_3=S_P.
\]

The new scalar time kernel acts only on momentum and commutes with total
ghost parity.  Since the certified finite-time tree is also fixed,

\[
 T_{4,T}^{\sharp}T_{6,V_4^3,T}
 +T_{6,V_4^3,T}^{\sharp}T_{4,T}
 =T_{4,T}^{*}T_{6,V_4^3,T}
 +T_{6,V_4^3,T}^{*}T_{4,T}.
\]

The isolated finite-time tree--triangle interference is therefore the same
under the public Krein and positive Hilbert prescriptions.  Its sign is not
determined because the coherent momentum-dependent transient integrals are
complex.

## Claim boundary

This certificate establishes the first actual finite-duration loop block in
the fully rearranged $q_{10}$ programme.  It does not compute:

- the $V_3^2V_4^2$, $V_3^4V_4$, or $V_3^6$ loop classes;
- the complete $y_5$ norm or $y_4$--$y_6$ interference;
- second-order source/detector dressing;
- vacuum, survival, or cumulant normalization;
- the sign or value of complete $q_{10}$;
- finite-coupling or all-order positivity;
- an all-time Møller, LSZ, or scattering operator;
- general Eq. (19), a gravity/BV--BRST transfer, or anything
  `LORENTZIAN-CAUSAL`.

## Verification receipt

All scientific Python and TeX commands ran sequentially below the 500 MB
virtual-memory cap.

- Tier 0 passes.  The three changed Python files compile; all changed JSON
  parses; the Draft-2020-12 schema is valid and rejects an injected top-level
  property; the two papers contain no undefined citation or reference; and
  the scoped diff has no whitespace error.
- The exact producer passes `31/31` checks in `0.02 s` at `16524 KiB`.  The
  method-distinct verifier passes `45/45`, including strict schema validation,
  in `0.06 s` at `24032 KiB`.  The focused suite contains `32` tests: one
  positive certificate check and `31` adversarial mutations.  All pass in
  `0.116 s` (`0.19 s` enclosing wall time) at `24716 KiB`.
- The eight-command Tier-2 predecessor chain passes for the covariant
  $V_4^3$ triangle, finite-time active-loop affiliation, fully rearranged
  common-Born theorem, and fully rearranged physical packet probability.  It
  took `6.07 s` at `79144 KiB`.
- Papers V and VI compile twice with no undefined citation or reference and no
  new overfull box.  Their PDFs are `80` and `69` pages and contain `744714`
  and `702407` bytes, with SHA-256
  `89337a34b4addb342ffebc263ad44ec493cab8b4c8d38360b606c37cba0b8ac9`
  and
  `2ba856b523a610321463cf0e4a21c6fddfac4d22a0d6e552a42c8ecba8e3b509`.
  The four-pass build took `2.13 s` at `50964 KiB`.  Paper V retains six
  known overfull boxes and Paper VI two.
- Tier 3 is fail-closed, not a repository-wide pass.  With system tools ahead
  of semantic-search shims, `3241` tests ran in `705.982 s` (`707.02 s` wall)
  at `391656 KiB`, with the established `31` failures and `9` skips.  All
  `32` new tests pass.  The failures remain older certificate drift and the
  fifteen-path `chain_imports` policy list; none is counted as a pass.
- The append-only planning fold accepts `1575` nodes with zero invalid items
  and zero malformed events in `1.47 s` at `14132 KiB`.
- The advisory Science Forge shadow wrapper exits zero by design in `1.93 s`
  at `341024 KiB`, but its bridge audit remains fail-closed at the known
  toolchain/standard-library `E9118` mismatch.  Its read-only census finds
  `1627` certificates and `1408` verifier files.  This advisory exit is not
  theorem evidence.

Tier 3 was required because Papers V and VI acquire a
`COEFFICIENT_COMPUTED` finite-duration loop theorem.  No classical freeze,
QME state, residual transfer, or `LORENTZIAN-CAUSAL` state changed.  The final
certificate SHA-256 before staging is
`7f2067dc3fe1bd30dbc1598c2e94307a45ccf096234fb8cbaca823402601f9da`.

CLOSE-OUT: DONE -- the isolated $V_4^3$ loop now has an exact finite-duration
third-Dyson realization, compact-packet convergence, covariant boundary, and
common-Born interference class; its sign and complete $q_{10}$ remain open.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_FINITE_TIME_AFFILIATION_V1.json`
