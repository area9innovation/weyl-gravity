# Locked all-\(m\) exceptional moment-map intersection

## Result

On the locked pure-extra carrier, the exact intersection of the bounded
resonance incidence with all five compact stabilizer moment maps is the
origin.

For each retained travel direction \(s\), let \(x_{{\rm ax},s}\) and
\(x_{{\rm pol},s}\) be the exceptional \(V_1\) amplitudes and let \(Y_s\) be
the transported polar-extra \(V_2\) STF amplitude.  In the coefficient
normalization fixed by the direct locked source,

\[
\begin{aligned}
 E_s&=16W_1(x_{{\rm ax},s},x_{{\rm ax},s})
      +3W_1(x_{{\rm pol},s},x_{{\rm pol},s}),\\
 Q_s&=22464W_2(Y_s,Y_s),
\end{aligned}
\]

where

\[
 W_1(x,z)=\frac{4\pi}{3}x^\dagger z,\qquad
 W_2(Y,Z)=\frac{8\pi}{15}\operatorname{tr}(Y^\dagger Z).
\]

With \(\omega^2=k^2+4/3\), the five maps are

\[
\begin{aligned}
\mu_H&=-\frac L4\sum_s\left(\omega^2E_s+4\omega^2Q_s\right),\\
\mu_{P_x}&=\frac L4\sum_s s\left(k\omega E_s+4k\omega Q_s\right),\\
\mu_{J_a}&=\frac L4\sum_s\left(\omega A_{s,a}+2\omega B_{s,a}\right).
\end{aligned}
\]

Here \(A_{s,a}\) and \(B_{s,a}\) use the Hermitian Cartesian \(V_1\) and
commutator \(V_2\) rotation generators.  Every coefficient and angular form
in \(-\mu_H\) is strictly positive.  Hence

\[
 \mu_H=0
 \quad\Longleftrightarrow\quad
 x_{{\rm ax},s}=x_{{\rm pol},s}=Y_s=0
\]

for every retained direction.  This remains true when independent
positive-frequency \(+k\) and \(-k\) travellers are both present: momentum and
rotation can cancel between them, but their negative Hamiltonian
contributions add.

## Complex incidence versus the physical slice

Before imposing the physical conjugation and Taub condition, the resonance
incidence is not trivial.  The exceptional self-resonance gives

\[
\operatorname{STF}(x_{\rm ax}x_{\rm ax}^T-q q^T)=0,\qquad
\operatorname{STF}(x_{\rm ax}q^T+q x_{\rm ax}^T)=0,\qquad
q=\frac{\sqrt3}{4}x_{\rm pol},
\]

whose exact complex zero set is \(x_{\rm ax}=x_{\rm pol}=0\).  The locked
difference rows

\[
Y\overline{x_{\rm ax}}=0,\qquad
Y\overline{x_{\rm pol}}=0
\]

then vanish, leaving \(Y\) arbitrary in the co-propagating resonance-only
variety.  Thus complex STF ranks \(0,1,2,3\) all occur there.  A nonzero
complex rank-one example is \(Y=vv^T\) with \(v=(1,i,0)\).

The rank-one stratum is absent already on the real STF slice: a real
symmetric rank-one matrix is \(c\,vv^T\), whose trace cannot vanish unless
the matrix does.  Real ranks two and three exist before the Taub condition,
but strict negativity of \(\mu_H\) excludes them.  The real radical of the
complete physical obstruction ideal is therefore the maximal ideal of the
origin.

## Bounded ledger and boundary

The co-propagating shell census has only the certified exceptional self
\(L=2\) resonance and the locked \(L=1\) difference resonance.  The
\(X+Y\) and \(Y+Y\) invariant masses are respectively \(12\) and \(64/3\)
and miss every angularly allowed target shell.  The generic zero block also
contributes the exact pressure row

\[
R_c(Y)=\frac12(2k)^2\,22464\,W_2(Y,Y),
\]

while the Wilson-acceleration row vanishes.  Every such quadratic row
vanishes at the origin.  Therefore any additional opposite-direction
characteristic-shell coefficient—whose resonance-only complex variety is
not claimed here—is algebraically redundant for the physical common zero.

This gives Paper 13 a scoped corollary, not a complete finite-harmonic freeze:
the locked exceptional/generic pure-extra face has physical bounded tangent
cone \(\{0\}\), even though its complex resonance incidence is nontrivial.

CLOSE-OUT: DONE — the exact physical five-moment and bounded-resonance intersection on the declared locked all-m carrier is the origin
EVIDENCE: EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ALL_M_MOMENT_INTERSECTION_V1
