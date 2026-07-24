# Infinity-tail gate on the proposed QNM disk

## Result

The exact infinity recurrence is

\[
2i\omega(m+1)g_{m+1}
+p_mg_m+q_mg_{m-1}+s_mg_{m-2}=0.
\]

At \(R=45\), set \(t_m=g_m/R^m\).  The coefficient carrying \(t_m\)
directly into \(t_{m+1}\) is

\[
\alpha_m=-\frac{p_m}{2i\omega(m+1)R}.
\]

On the closed seed disk, the exact \(L^1\) enclosure

\[
\lvert\omega\rvert\le
\Omega=
\frac{51263400010697753407395293}
{10^{26}}
\]

gives

\[
\lvert p_m\rvert
\ge
m^2+m-6-4m\Omega-8\Omega^2.
\]

At \(m=49\),

\[
\lvert\alpha_{49}\rvert
\ge
\frac{
2926776733793133697727717754495682162398275817241444151
}{
2883566250601748629165985231250000000000000000000000000
}
>1.
\]

The lower bound increases thereafter.  Consequently the naive independent
forward recurrence cannot close an infinite geometric tail enclosure.
Finite asymptotic truncation may still be useful; this result says that its
remainder needs a different analytic argument.

## Replacement contract

Factor the outgoing phase in tortoise coordinate,
\(y=e^{-i\omega x}v\), and use the ray

\[
x=x_0+e^{i\pi/4}t.
\]

For every frequency in the disk,

\[
\left|
e^{-2i\omega e^{i\pi/4}t}
\right|
\le
e^{-\sqrt2\delta t},
\qquad
\delta=
\frac{23470936872910613751303107}{10^{26}}>0.
\]

This makes an exterior-complex-scaled Volterra equation the next viable
validated representation.  A successful package must still certify:

1. an analytic inverse-tortoise branch on the ray;
2. avoidance of \(r=0,2\);
3. a complex potential-integral norm below one;
4. a truncated-ray tail and inward complex-ball transport.

## Claim boundary

This package proves noncontractivity of one recurrence enclosure and a
uniform phase-damping inequality.  It does not enclose an infinity
remainder, construct a complex Jost column, certify an Evans boundary, count
roots, or establish a QNM/Smith/EP2 result.
