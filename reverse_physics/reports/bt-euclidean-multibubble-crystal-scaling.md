# BT growing multibubble-crystal scaling

**Certificate:**
REVERSE_PHYSICS_BT_EUCLIDEAN_MULTIBUBBLE_CRYSTAL_SCALING_V1

**Dependency tags:** LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL,
REDUCED-MODE

## Result

The simplest bubble gas whose number of bubbles grows with four-volume is
not a collapse mechanism. It becomes more coercive.

Starting from

\[
 F_{16}(y)=\sum_{\mu=1}^4
 \left(\sin^2y_\mu+\frac13\sin^4y_\mu\right),
\]

define, for every integer \(K\geq1\),

\[
 F_K(x)=K^{-2}F_{16}(Kx),\qquad
 \Omega_{K,m}(x)=\frac1{m+F_K(x)}.
\]

The denominator has

\[
 |Z_K|=(2K)^4=16K^4
\]

repaired zeros on the \(2\pi\)-periodic four-torus. Nevertheless, if

\[
 Q_K(m)=\frac{\|E_{K,m}\|_2^2}{\|R_{K,m}\|_2^2},
\]

then the exact identity is

\[
 \boxed{Q_K(m)=K^4Q_{16}(mK^2).}
\]

The predecessor proves \(Q_{16}(M)\geq c_{16}>0\) for every \(M>0\).
Therefore

\[
 Q_K(m)\geq K^4c_{16}.
\]

Thus a synchronized bubble density proportional to the four-volume moves
away from zero in the normalized Euler quotient.

## Local repair and bubble count

The zeros occur when every \(Kx_\mu\) is \(0\) or \(\pi\) modulo \(2\pi\).
There are \(2K\) choices per coordinate. Near any zero \(z\),

\[
 F_K(z+y)
 =|y|^2-\frac8{45}K^4\sum_\mu y_\mu^6
  O(K^6|y|^8).
\]

The quadratic coefficient remains one and the quartic term remains exactly
zero. Increasing \(K\) therefore produces more genuine repaired bubbles,
not shallower zeros or a different local singularity class.

## Exact operator scaling

Put \(M=mK^2\). Then

\[
 \Omega_{K,m}(x)=K^2\Omega_{16,M}(Kx).
\]

The overall factor \(K^2\) drops out of the residual, while the coordinate
rescaling supplies two derivatives:

\[
 R_{K,m}(x)=K^2R_{16,M}(Kx).
\]

For \(q=R/\Omega^2\),

\[
 q_{K,m}(x)=K^{-2}q_{16,M}(Kx).
\]

Since

\[
 E=\operatorname{div}(\Omega^2\nabla q),
\]

the factors combine to give

\[
 E_{K,m}(x)=K^4E_{16,M}(Kx).
\]

For integer \(K\), the map \(x\mapsto Kx\) is a degree-\(K^4\) torus covering
whose sheets cancel its Jacobian in an integral:

\[
 \int_{\mathbb T^4}f(Kx)\,dx=\int_{\mathbb T^4}f(y)\,dy.
\]

Consequently,

\[
 \|R_{K,m}\|_2^2=K^4\|R_{16,M}\|_2^2,\qquad
 \|E_{K,m}\|_2^2=K^8\|E_{16,M}\|_2^2,
\]

which proves the boxed quotient identity.

## Endpoint consistency

At the shrinking endpoint, every one of the \(16K^4\) bubbles contributes
\(32\pi^2/3\). The total concentrated residual energy is

\[
 \frac{512\pi^2}{3}K^4,
\]

consistent with the residual norm scaling. At the weak-field endpoint,

\[
 Q_K(\infty)=\frac{512}{17}K^4.
\]

For the exact \(K=3\) fixture, the crystal has 1,296 zeros, the residual and
Euler squared-norm factors are 81 and 6,561, the concentration coefficient is
13,824, and

\[
 Q_3(\infty)=\frac{41472}{17}.
\]

All values are reconstructed independently with integer and rational
arithmetic.

## Meaning for the barrier

The regular growing-gas branch is closed: neither a fixed collection of
repaired bubbles nor a synchronized collection whose count is proportional
to volume can collapse the quotient. The remaining concentration
possibilities are less symmetric and more specific:

- correlated or irregular bubble centers and scales;
- multiple scales at the same point;
- necks joining concentration regions;
- nonspherical or delocalized transverse-current profiles.

The next sharp calculation is a two-scale same-point tower. Simple frequency
replication cannot help because it multiplies the quotient by \(K^4\).
This remains input to, not a replacement for, the connection-corrected Witten
estimate.

## Boundaries

No irregular-gas theorem, tower or neck exclusion, all-field gradient bound,
Witten/Poincare theorem, interacting Gibbs \(H^{-1}\) estimate, continuum
measure, Born rule, Krein reconstruction, or LORENTZIAN-CAUSAL statement is
established.

## Verification

~~~bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_multibubble_crystal_scaling.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_multibubble_crystal_scaling.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_multibubble_crystal_scaling
~~~

The producer check, independent verifier, and ten focused tests passed in
0.03, 0.10, and 0.12 seconds, using at most 20,248, 30,032, and 30,688 KiB.
The direct predecessor verifier passed in 0.12 seconds. The planning import
folded 1,655 nodes with no invalid item or malformed event in 7.45 seconds
under a 300 MiB Go limit. Tier 3 was not run because this is a structured
family theorem, not an all-field Witten/\(H^{-1}\) promotion, freeze, or
release.
