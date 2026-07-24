# ECS inverse-tortoise and scalar outgoing-tail gate

## Exact inverse branch

Set

\[
x(r)=r+2\Log(r/2-1),\qquad
x(t)=x(45)+e^{i\pi/4}t.
\]

The inverse branch solves

\[
\frac{dr}{dt}=e^{i\pi/4}\frac{r-2}{r},\qquad r(0)=45.
\]

Writing \(r=a+ib\), the region \(a\ge45,\ b\ge0\) is invariant and

\[
\frac{d}{dt}\operatorname{Re}r
\ge\frac{22\sqrt2-1}{45}>\frac23.
\]

The last strict inequality follows from \(22\sqrt2>31\), or
\(968>961\).  Hence

\[
|r(t)|\ge45+\frac23t,\qquad
|r(t)-2|\ge43.
\]

The principal logarithm is analytic throughout this region, so the branch
is an analytic inverse of the Schwarzschild tortoise map along a
neighbourhood of the complete ray and avoids both potential poles.

## Uniform Volterra contraction

For \(y=e^{-i\omega x}v\), use

\[
v(x)=1+\int_x^\infty
\frac{1-e^{2i\omega(x-s)}}{2i\omega}V(r(s))v(s)\,ds.
\]

The imported disk gives \(|\omega|\ge0.34867\ldots\), while the
\(\pi/4\) ray gives exponential decay at rate at least
\((7/5)\delta=0.32859\ldots\).  Exact rational integration of the potential
majorants yields Volterra norm bounds

\[
\|\mathcal V_1\|\le0.306682,\qquad
\|\mathcal V_2\|\le0.310263.
\]

Both channels are therefore uniformly contractive on the closed disk.  The
Neumann-series bounds at \(r=45\) are

\[
|v_1-1|\le0.442339,\qquad |v_1'|\le0.013584,
\]

\[
|v_2-1|\le0.449828,\qquad |v_2'|\le0.013958.
\]

These are coarse but nonzero reduced scalar outgoing initializers.

## Claim boundary

This result is `REDUCED-MODE`.  It does not construct the mixed four-state
or full six-state Bach outgoing frame, validate inward complex transport,
prove an Evans boundary is nonzero, count QNMs, or establish a Smith/EP2
fibre.
