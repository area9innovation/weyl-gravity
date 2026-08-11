# BT rigged resolution-Jordan Møller gate

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

**Lifecycle:** `CLASSIFIED`

**Certificate:** `REVERSE_PHYSICS_BT_RIGGED_RESOLUTION_JORDAN_MOLLER_V1`

## Result

The physical collinear map now has a genuine direct-integral realization for
every fixed daughter mass ratio.  It generates an exact finite-regulator
pseudo-unitary block without fitting.  The massless limit of its Gram is
finite, but the family is not differentiable there.  Consequently an
ordinary strongly differentiable Møller column on any fixed Krein carrier
with bounded fundamental symmetry cannot implement the BT delta-prime
external derivative.

The failure has a controlled remainder.  The divided mass germ has a finite
scale cocycle of $1/4$ before normalization and $1/48$ per physical pair.
It is linearized by a two-dimensional nilpotent resolution-Jordan action in
the tempered-distribution dual of the Abel--Naimark resolution carrier.  This
constructs relative changes of resolution, not an endpoint vector or a full
physical S-matrix.

## The regulated physical column

Set

\[
 a_0=1,\qquad a_1=r,\qquad \tau=u,qquad 0<r<1.
\]

The two-body threshold and measure are

\[
 u\ge (1+\sqrt r)^2,
 \qquad
 d\mu_r(u)=\frac{\sqrt{\lambda(u,1,r)}}{u}\,du.
\]

The amplitude-level theorem gives

\[
 T(r,u)=\operatorname{diag}\!\left(
 \frac{2u(1+r)-(1-r)^2}{2u^2},
 -\frac{(1-r)^2}{2u}
 \right)
\]

and, with the fifth delta-prime sign included in the physical sharp,

\[
 T(r,u)^{\sharp_{\rm phys}}T(r,u)=\rho(r,u)I_2,
\]

\[
 \rho(r,u)=
 \frac{(1-r)^2[2u(1+r)-(1-r)^2]}{4u^3}>0.
\]

Thus

\[
 (V_rh)(u)=T(r,u)h,
 \qquad
 V_r^\sharp V_r=I(r)I_2,
 \qquad
 I(r)=\int_{(1+\sqrt r)^2}^{\infty}\rho(r,u)d\mu_r(u).
\]

The integral converges at threshold and infinity.  On the parent plus the
range of $V_r$, the skew block

\[
 \mathcal A_r=
 \begin{pmatrix}0&-V_r^\sharp\\V_r&0\end{pmatrix}
\]

has an exact sharp-unitary exponential.  If $U_r=V_r/\sqrt{I(r)}$, its
nontrivial block is a rotation through $x\sqrt{I(r)}$.  This is a regulated
physical collinear column, not merely a prescribed scalar norm.

## Exact threshold Gram

The integral is related to the independently certified threshold function by

\[
 I(r)=-\frac23H(r)
 =\frac{5r^3-6r^2\log r-3r^2-6r\log r+3r-5}
 {24(r-1)}.
\]

It obeys

\[
 I(0)=\frac5{24},\qquad I(1)=0,
\]

and its massless-axis germ is

\[
 I(r)=\frac5{24}
 +r\left(\frac14\log r+\frac1{12}\right)
 +O(r^2\log r).
\]

The fixed-regulator column therefore has a finite massless Gram limit.  But

\[
 I'(r)=\frac14\log r+\frac13+o(1)\longrightarrow-\infty.
\]

## Why this excludes an ordinary differentiable Møller column

Let $V_r:\mathbb C^2\to\mathcal K$ be strongly differentiable at zero,
where $\mathcal K$ has a fixed bounded fundamental symmetry.  The input is
finite dimensional, so each column has a strong derivative.  The bounded
pairing then gives

\[
 \frac d{dr}(V_r^\sharp V_r)\bigg|_{r=0}
 =V_0'{}^\sharp V_0+V_0^\sharp V_0'.
\]

Every Gram entry must therefore have a finite derivative.  The exact identity
\(V_r^\sharp V_r=I(r)I_2\) contradicts this because
\(I'(0+)=-\infty\).

The conclusion is scoped but strong:

- a fixed regulator is harmless;
- a finite massless Gram limit is not enough;
- the delta-prime derivative cannot be an ordinary strong derivative of an
  amplitude column on a fixed bounded-pairing carrier.

An unbounded metric, regulator-dependent topology, rigged distributional
derivative, non-normal weight, or resummed construction is not excluded.

## The finite scale cocycle

Define the divided germ

\[
 D(r)=\frac{I(r)-I(0)}r.
\]

It diverges, but differences at two resolutions have a finite limit:

\[
 D(r)=\frac14\log r+\frac1{12}+O(r\log r),
\]

\[
 \lim_{r\to0}[D(cr)-D(r)]=\frac14\log c.
\]

The exact physical normalization is $1/12$, so this becomes
\(\log(c)/48\) per unordered pair and \(\log(c)/16\) over all three
pairs.  The coefficient is thus a relative scale cocycle even though no
absolute endpoint derivative exists.

## Rigged resolution-Jordan lift

Put $R=-\log r$.  Then

\[
 D(e^{-R})=-\frac R4+\frac1{12}+o(1),
\]

so $R\mapsto R+a$ gives the affine translation

\[
 d\longmapsto d-\frac a4.
\]

It is linearized by

\[
 U_a=
 \begin{pmatrix}1&-a/4\\0&1\end{pmatrix}
 =e^{aN},
 \qquad
 N=\begin{pmatrix}0&-1/4\\0&0\end{pmatrix},
 \qquad N^2=0.
\]

After physical normalization, the off-diagonal entry is $-1/48$ per pair.
This nilpotent is a resolution-renormalization generator; it is not the
rank-one public $R_tD$ Gram and does not repair that operator.

The natural carrier is the rigged triple

\[
 \mathcal S(\mathbb R_s)\subset L^2(\mathbb R_s,ds)
 \subset\mathcal S'(\mathbb R_s).
\]

Translations preserve the affine distribution sector
\(\operatorname{span}\{1,s\}\subset\mathcal S'\) and act there by the
displayed Jordan matrices.  Neither $1$ nor $s$ is an $L^2$ vector.
Therefore the Abel--Naimark translation has exactly the required rigged
affine moment representation, but it does not create a strong endpoint state.
The positive Naimark shell is the orientation-reversed finite resolution
increment of this affine germ.

The added rigged coordinate is resolution data, not a spacetime or physical
dimension.

## What remains

The next constructive object is a generalized-Born functional continuous on
the rigged affine sector and normalized on compact detector differences.  It
must reproduce the $1/48$ cocycle without choosing an absolute endpoint
origin.  Only after that functional is affiliated with a physical asymptotic
Hamiltonian can the construction be called a complete Møller/S operator.

The public $R_tD$ mismatch, the complete finite NLO probability, positivity
beyond tree level, and all-order Eq. (19) remain open or obstructed exactly as
stated in their own result kinds.

## Verification receipt

All symbolic Python and TeX commands ran sequentially with
`ulimit -v 500000`.

| tier | command or check | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0 | Python byte-compile; JSON parse of work item, event, schema, and certificate | PASS | below 0.5 s | below cap |
| 0 | `git diff --check` on the scoped paths | PASS | below 0.3 s | negligible |
| 1 | producer exact reproduction | PASS, 25/25 | 0.60 s | 69,328 KB |
| 1 | independent $z=e^{-y}$ threshold integration with `--exhaustive` | PASS, 19/19 | 8.60 s | 95,632 KB |
| 1 | focused producer/verifier plus nine mutation tests | PASS, 11/11 | 5.59 s | 71,880 KB |
| 1 | two-pass Paper V and Paper VI PDF builds | PASS | 0.88 s / 0.92 s | 50,976 KB / 50,920 KB |
| advisory | Science Forge shadow rail | advisory exit 0; bridge audit not counted as PASS because the installed Forge binary/stdlib mismatch triggers `E9118`; corpus census reports baseline drift | 2.3 s | not measured |

Tier 2 was unnecessary because all imported certificates are unchanged and
content-addressed and the package is a new leaf whose only direct generated
consumers are the rebuilt papers.  Tier 3 was not run: there is no freeze,
release, shared-core change, promotion of an existing lifecycle state, or
Lorentzian theorem.  No skipped or advisory check is recorded as a pass.
