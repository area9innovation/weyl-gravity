# BT periodic-bubble jet gate

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_PERIODIC_BUBBLE_JET_GATE_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

## Result

The simplest smooth periodization of the noncompact BT sphere bubble fails
for an exact local reason.  Replacing squared radius by the standard chordal
torus distance introduces a quartic harmonic defect.  In four dimensions
that defect makes the flat (L^2) norm of the BT Euler gradient diverge as

\[
              \|E_m\|_2^2
              =\frac{128\pi^2}{5}\log(1/m)+O(1),
              \qquad m\downarrow0,
\]

while the residual norm stays bounded and retains the round-bubble
concentration.  The normalized gradient quotient therefore tends to infinity,
not zero.  The naive chord bubble cannot break the volume-uniform barrier.

There is also an exact local repair.  The two-harmonic fourth-order periodic
stencil cancels the quartic jet and replaces it by a sixth-order defect.  Its
local Euler gradient is uniformly square-integrable through the shrinking
bubble limit.  This removes the logarithmic obstruction, but it does not
evaluate the finite contribution from the rest of the torus.  The repaired
global quotient remains open.

## A general denominator identity

On the (2\pi)-periodic four-torus, write

\[
             \Omega_m=\frac1{h_m},\qquad h_m=m+F,qquad m>0.
\]

Put (D=\Delta F), (G=|\nabla F|^2), and
(q=R/\Omega_m^2).  Direct differentiation gives

\[
 q=-h_mD+2G,qquad R=\frac q{h_m^2},qquad
 E=\operatorname{div}(h_m^{-2}\nabla q).
\]

Suppose near the unique minimum

\[
 F(x)=|x|^2+P_d(x)+O(|x|^{d+2}),
\]

where (P_d) is homogeneous of even degree (d>2).  At (m=0), the first
nonradial weighted-scalar defect is

\[
             Q_d=8(d-1)P_d-|x|^2\Delta P_d.
\]

The corresponding leading Euler defect is

\[
        \operatorname{div}(|x|^{-4}\nabla Q_d),
\]

which is homogeneous of degree (d-6).  Degree four is therefore the
borderline logarithmic case in four dimensions; degree six is locally
bounded.

## Exact obstruction to the chord bubble

The standard chord denominator is

\[
                  F_2(x)=2\sum_{\mu=1}^4(1-\cos x_\mu).
\]

Its local expansion is

\[
 F_2=|x|^2-\frac1{12}\sum_\mu x_\mu^4+O(|x|^6).
\]

Substitution into the homogeneous defect rule gives

\[
 Q_4=|x|^4-2\sum_\mu x_\mu^4,
 \qquad \Delta Q_4=0.
\]

Thus, in the annulus (sqrt m\ll|x|\ll1),

\[
                    E_m=-\frac{16Q_4}{|x|^6}+O(1).
\]

On (S^3), exact rotational moments give

\[
 \mathbb E\omega_1^4=\frac18,qquad
 \mathbb E\omega_1^8=\frac7{128},qquad
 \mathbb E\omega_1^4\omega_2^4=\frac3{640},
\]

and hence

\[
 \mathbb E_{S^3}\left(1-2\sum_\mu\omega_\mu^4\right)^2
 =\frac1{10},
 \qquad
 \int_{S^3}Q_4(\omega)^2d\omega=\frac{\pi^2}{5}.
\]

Squaring the singular term and integrating radially from order (sqrt m)
to a fixed radius gives

\[
 \frac{256\pi^2}{5}\int_{\sqrt m}^{r_0}\frac{dr}{r}
 =\frac{128\pi^2}{5}\log(1/m)+O(1).
\]

In contrast, the residual has the local form

\[
 R_m=\frac{-8m+Q_4+O(m|x|^2+|x|^6)}
              {(m+|x|^2+O(|x|^4))^2}.
\]

The first term produces the usual round-bubble concentration
(32\pi^2/3); the other terms are locally square-integrable.  Away from the
minimum all quantities converge smoothly.  Therefore (|R_m|_2^2=O(1)),
whereas (|E_m|_2^2) diverges logarithmically.

The independent verifier reconstructs (P_4), (Q_4), its harmonicity, and
its sphere average with exact multivariate polynomial arithmetic.  It does not
reuse the producer's closed moment calculation.

## Fourth-order local repair

Use instead

\[
 F_4(x)=\sum_{\mu=1}^4\left[
 \frac83(1-\cos x_\mu)-\frac16(1-\cos2x_\mu)\right].
\]

Each one-coordinate summand factors as

\[
 \frac13(1-\cos x)(7-\cos x),
\]

so (F_4>0) away from the single periodic minimum.  Its exact Taylor jet is

\[
 F_4=|x|^2-\frac1{90}\sum_\mu x_\mu^6+O(|x|^8).
\]

The quartic term is zero.  The first defect is instead

\[
 Q_6=\frac13|x|^2\sum_\mu x_\mu^4
       -\frac49\sum_\mu x_\mu^6.
\]

Because
(operatorname{div}(|x|^{-4}\nabla Q_6)) has degree zero, its squared
local integral is finite.  A scaling check in the core (x=\sqrt m,y)
shows that the (m)-dependent remainder is also uniformly square-integrable.
Thus

\[
       \sup_{0<m\leq m_0}
       \int_{|x|<\delta}|E_m|^2dx<\infty.
\]

This is a local repair theorem, not a full-torus estimate.  The complement of
the bubble core contributes a finite quantity of exactly the same order as
the desired normalized gap.

## The opposite endpoint

The repaired family also has an exact weak-field limit.  As (m\to\infty),

\[
 R_m=-\frac{\Delta F_4}{m}+O(m^{-2}),
 \qquad
 E_m=-\frac{\Delta^2F_4}{m}+O(m^{-2}).
\]

Fourier orthogonality between the first and second harmonics gives

\[
 \lim_{m\to\infty}\frac{\|E_m\|_2^2}{\|R_m\|_2^2}
 =\frac{(8/3)^2+2^8(1/6)^2}
        {(8/3)^2+2^4(1/6)^2}
 =\frac{32}{17}.
\]

The second harmonic needed for local repair prevents this endpoint from
approaching the sharp lowest-mode coefficient (1) on the (2\pi)-torus.
No claim is made about intermediate (m).

## Research consequence

The noncompact sphere bubble cannot simply be copied onto the torus using the
nearest standard periodic distance.  Periodization must match the Euclidean
squared-radius jet through fourth order.  The repaired stencil supplies the
smallest explicit family that passes that local test.

The next calculation is global rather than local: rigorously enclose
(|E_m|_2^2/|R_m|_2^2) for the repaired family over (m>0).  If it stays
bounded away from zero, the one-bubble collapse route should be retired and
effort returned to the connection-corrected Witten Schur problem.  If it
approaches zero, that sequence must then be tested in the full Witten Rayleigh
quotient before drawing a probabilistic conclusion.

## Boundaries

This certificate does not establish a collapsing smooth periodic sequence, a
positive global gradient gap, Witten/Poincare coercivity or failure, an actual
Gibbs (H^{-1}) bound or divergence, tightness, continuum identification, a
Born rule, Krein reconstruction, or anything `LORENTZIAN-CAUSAL`.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_periodic_bubble_jet_gate.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_periodic_bubble_jet_gate.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_periodic_bubble_jet_gate
```

The measured producer, independent-verifier, and test runs took (0.04),
(0.10), and (0.13) seconds at peak RSS (20{,}560), (30{,}184), and
(30{,}936) KiB.  Planning conformance validated the new sequence-46 event
but refused after 8.50 seconds at 220,068 KiB on ten pre-existing
`forge-requests` lifecycle errors.  The Science Forge shadow rail was not
rerun because this checkpoint changes no registered shadow input and the
immediately preceding bounded attempt failed to produce a disposition after
unrelated indexing subprocesses aborted; it is not counted as a pass.
