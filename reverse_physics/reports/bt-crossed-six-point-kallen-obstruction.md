# BT crossed six-point Källén obstruction

Certificate: `REVERSE_PHYSICS_BT_CROSSED_SIX_POINT_KALLEN_OBSTRUCTION_V1`

Lifecycle: `CLASSIFIED`

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The first missing reversed six-point chamber does not arise by simply
continuing the certified final-pair Källén map to a spacelike invariant.  The
analytic continuation exists and retains the complete two-species quotient,
but its rank-two orientation reverses.  With the already certified physical
sharp, its Hilbertized Gram is negative definite.  Therefore no isometry from
the positive HP reversed chamber exists on this one-branch carrier.

The obstruction is uniform over all twelve six-point histories.  It is not a
failure of the Källén continuum: after taking the absolute orientation, that
continuum has an exact two-sided cumulative coordinate and supplies the
minimal bilateral dilation of the HP half-line shift.  What is missing is the
physical sign that authorizes this orientation change—a crossed adjoint
branch or a complete crossed-detector recombination—not another choice of
coordinates.

## Analytic spacelike sheet

For the certified outgoing final-pair chart, write

\[
 r=\frac{a_1}{a_0},\qquad w=\frac{\tau_1}{a_0},
 \qquad
 q(r,w)=\frac{2w(1+r)-(1-r)^2}{2w^2}.
\]

The outgoing physical domain is the upper Källén sheet

\[
 w>(1+\sqrt r)^2,
\]

where \(q>0\).  Standard all-incoming scalar crossing to the massless
spacelike sheet is

\[
 w=-x,\qquad x>0.
\]

The Källén polynomial becomes

\[
 \Delta_x^2
 =x^2+2(1+r)x+(1-r)^2>0,
\]

and

\[
 q(r,-x)=-q_x(r,x),\qquad
 q_x(r,x)=\frac{2x(1+r)+(1-r)^2}{2x^2}>0.
\]

This is an analytic change of invariant sheet.  It does not change the
number of external Wightman derivatives: there are still six delta-prime
factors, so their previously certified parity remains \(+1\).  No additional
minus sign is inserted merely because a momentum is crossed.

The first physical splitting is not the source of the new obstruction.  Its
continued unequal-regulator norm is

\[
 \rho_\times(r,x)
 =\frac{(1-r)^2[2x(1+r)+(1-r)^2]}{4x^3}>0.
\]

The sign reversal first occurs in the second parent/profile quotient.

## Exact two-species sign

Let

\[
 J=\begin{pmatrix}0&1\\1&0\end{pmatrix},\qquad
 \eta=J\otimes3J,\qquad v=\frac{a_2}{2}.
\]

On the crossed sheet put \(q=-q_x\).  The analytically continued image and
kernel bases are

\[
 N_+=\begin{pmatrix}
 v&0\\0&v\\-q_x&0\\0&-q_x
 \end{pmatrix},\qquad
 N_-=\begin{pmatrix}
 v&0\\0&v\\q_x&0\\0&q_x
 \end{pmatrix}.
\]

The complete identities continue exactly:

\[
 N_+^T\eta N_+=-6q_xvJ,
 \qquad
 N_-^T\eta N_-=+6q_xvJ,
 \qquad
 N_-^T\eta N_+=0.
\]

The certified outgoing profile-swap Hilbertization multiplies the image form
by \(J\).  On the crossed sheet this gives

\[
 (N_+^T\eta N_+)J
 =-6q_xv I_2
 =-3a_2q_x I_2.
\]

Its inertia is therefore \((0,2,0)\).  The amplitude collapse retains the
same sign:

\[
 RDN_+=-2q_xvI_2=-a_2q_xI_2,
 \qquad RDN_-=0.
\]

For every nonzero species vector \(c\), the fixed target norm is

\[
 -3a_2q_x\,c^*c<0,
\]

whereas the positive HP reversed chamber has norm \(c^*c>0\).  Consequently
an isometry satisfying \(B^\sharp B=I\) cannot map the positive HP species
fibre into this rank-two image.

Multiplying instead by \(-J\) changes the crossed image form to

\[
 +3a_2q_xI_2.
\]

This is an exact algebraic repair, but it is new branch data.  The public BT
map, the vacuum physical column, and Eq. (19) do not derive a
kinematic-branch-dependent change from \(J\) to \(-J\).  The certificate
therefore records the repaired carrier conditionally and does not call it a
physical intertwiner.

## The crossed resolution is bilateral

The positive absolute Källén measure and conditional Gram are

\[
 d\mu_x=\frac{\Delta_x}{x}\,dx,
 \qquad \lambda_x=a_2q_x.
\]

Their canonically normalized resolution density is

\[
 d\sigma_x
 =\frac{q_x\Delta_x}{(1+r)x}\,dx.
\]

It is positive and daughter-exchange invariant.  Under

\[
 r\mapsto r^{-1},\qquad x\mapsto x/r,
\]

\(q_x\) is invariant, \(\Delta_x\) scales by \(r^{-1}\), and the full
differential is unchanged.  The geometric reference

\[
 x_0=\sqrt r
\]

has the same covariance, so subtraction there gives

\[
 \sigma_{1/r}(x/r)=\sigma_r(x).
\]

Both endpoints have infinite resolution length:

\[
 \lim_{x\to\infty}x\frac{d\sigma_x}{dx}=1,
\]

and, for unequal regulators,

\[
 \lim_{x\to0^+}x^3\frac{d\sigma_x}{dx}
 =\frac{|1-r|^3}{2(1+r)}.
\]

At equal regulator mass the corresponding limit is

\[
 \lim_{x\to0^+}x^{3/2}\frac{d\sigma_1}{dx}=2.
\]

Thus \(\sigma_r\) maps \((0,\infty)\) bijectively onto \(\mathbb R\), not
onto another half-line.

There is also an exact primitive.  For \(r=m^2\), set

\[
 x=m(z+z^{-1})-(1+m^2),\qquad 0<z<m<1.
\]

With \(A=1+m^2\) and \(C=m^4+m^2+1\), one may take

\[
\begin{split}
 F_m^\times(z)={}&
 \frac{m^2(m^2-1)}{4A(z-m)^2}
 -\frac{m^2-1}{4A(mz-1)^2}
 +\frac{2m^2+3}{2A(mz-1)}\\
 &+\frac{m(3m^2+2)}{2A(z-m)}
 +\frac{C}{(m^2-1)A}\log\frac{1-mz}{m-z}
 -\log z.
\end{split}
\]

Exact differentiation gives

\[
 \frac{dF_m^\times}{dz}
 =\frac{d\sigma_x}{dx}\frac{dx}{dz}.
\]

The direct endpoint estimates above cover the removable equal-mass case and
prove the full range without relying on a formal primitive limit.

## Conditional dilation architecture

If a physical crossed sign supplies the \(-J\) branch, normalize the image
with its positive form and define

\[
 B_x:L^2(\mathbb R,d\sigma)\otimes\mathbb C^2
 \longrightarrow
 \int_{x>0}^{\oplus}\operatorname{Ran}E_x\,d\mu_x
\]

by

\[
 (B_xf)(x)=\sqrt{\frac{q_x}{1+r}}\,
 E_x(r,x,a_2)f(\sigma_r(x)).
\]

The measure identity makes this unitary onto the crossed quotient-range
direct integral.  Zero extension

\[
 j:L^2(\mathbb R_+)\hookrightarrow L^2(\mathbb R)
\]

on \(\sigma\ge0\) intertwines the unilateral right shift with bilateral
translation:

\[
 T_bj=jS_b,\qquad b\ge0.
\]

The translates of the half-line range span \(L^2(\mathbb R)\), so this is the
minimal unitary dilation.  It explains why an incoming crossed branch, if it
exists, naturally carries more domain than the vacuum chronological
half-line.

This construction is conditional on the missing sign.  An abstract
bilateral dilation does not provide the BT crossed adjoint, generalized-Born
trace, or physical detector map.

## Consequence for the twelve chambers

Marks 3 through 14 all have the same crossed rational quotient by external
label covariance.  Their fixed-sharp inertia is consequently the same
\((0,2,0)\).  None of the twelve reversed chambers is physically affiliated
by one-branch analytic continuation.

The next calculation must therefore be the complete crossed \(3\to3\)
detector block.  It must retain:

1. both orientations of the crossed leg;
2. the unequal-regulator timelike pseudothreshold boundary until the
   regulator is removed;
3. the complete pre-trace interference terms;
4. the fixed BT sharp and generalized-Born sign.

The decisive question is whether the conjugate orientation contributes the
missing sign and makes the recombined rank-two Gram positive.  A positive
answer would instantiate the bilateral dilation above.  A negative answer
would promote this one-branch result to a complete crossed-channel no-go.

## Claim boundary

Established exactly:

- the spacelike analytic continuation of the certified six-point quotient;
- its rank-two negative inertia under the fixed certified Hilbertization;
- the resulting no-isometry theorem for a positive HP reversed chamber;
- the positive absolute Källén density, exact primitive, exchange law and
  bilateral real-line range;
- the conditional branch-flipped minimal unitary dilation;
- uniform application of the obstruction to all twelve reversed histories.

Not established:

- a positive crossed six-point probability;
- physical derivation of the branch flip;
- the complete crossed \(3\to3\) detector block;
- the twelve physical reversed intertwiners;
- the 300 seven-point crossed sheets or spectator sectors;
- a spacetime Møller, LSZ, or S operator;
- Eq. (19), a gravity/BRST lift, or anything `LORENTZIAN-CAUSAL`.

## Verification receipt

- Producer: 30/30 checks passed in 0.76 s with 70,048 KiB peak RSS.
- Independent verifier: 32/32 checks passed in 0.67 s with 73,656 KiB peak
  RSS.
- Mutation suite: 22/22 tests passed in 11.00 s (11.03 s including timing
  overhead) with 74,016 KiB peak RSS.
- Python byte compilation passed in 0.02 s with 15,120 KiB peak RSS; all four
  new JSON files parsed in 0.01 s with 13,328 KiB peak RSS.
- Paper V rebuilt in two passes at 0.45 s and 0.46 s, with no new overfull
  boxes; Paper VI rebuilt in two passes at 0.47 s and 0.48 s with no warnings.
- The narrow Science Forge programme import produced 1,437 nodes with zero
  invalid items and zero malformed events in 7.81 s with 255,936 KiB peak RSS.
- `git diff --check` passed with index preloading disabled.  The first default
  invocation could not create its threaded `lstat` workers and was not counted
  as a pass.
- All computations used exact SymPy algebra under a 500 MB virtual-memory
  limit.  No floating-point arithmetic entered the certificate.
- Tier 3 was not run because this is a new isolated reduced-mode certificate,
  not a classical/quantum freeze, theorem-lifecycle promotion, shared core
  change, or release.
