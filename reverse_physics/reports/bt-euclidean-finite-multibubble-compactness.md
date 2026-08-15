# BT finite repaired-multibubble compactness

**Certificate:**
REVERSE_PHYSICS_BT_EUCLIDEAN_FINITE_MULTIBUBBLE_COMPACTNESS_V1

**Dependency tags:** LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL,
REDUCED-MODE

## Result

Splitting the repaired shrinking sphere into any fixed finite number of
periodic bubbles does not make the normalized BT Euler-gradient quotient
collapse.

Let \(F\) be smooth and nonnegative on the \(2\pi\)-periodic four-torus,
positive away from a fixed finite set \(Z\), and suppose that at every
\(z\in Z\),

\[
 F(z+y)=|y|^2+P_{6,z}(y)+O(|y|^8),
\]

where \(P_{6,z}\) is homogeneous of degree six. For

\[
 \Omega_m=(m+F)^{-1},\qquad
 R_m=\frac{\Delta\Omega_m}{\Omega_m},\qquad
 Q_F(m)=\frac{\|E_m\|_2^2}{\|R_m\|_2^2},
\]

where \(E_m\) is the flat \(L^2\) Euler gradient of
\(\frac12\int R_m^2\), there exists a family-dependent constant \(c_F>0\)
such that

\[
 Q_F(m)\geq c_F\qquad(m>0).
\]

The theorem applies to an explicit periodic crystal with sixteen repaired
bubbles. It does not give one constant uniform over all \(F\), and it does not
control a number of bubbles that grows with lattice volume.

## Exact sixteen-bubble crystal

Define

\[
 F_{16}(x)=\sum_{\mu=1}^4\left[
 \sin^2x_\mu+\frac13\sin^4x_\mu\right].
\]

Each summand is
\(\sin^2x(1+\sin^2x/3)\), so \(F_{16}\geq0\) and its zero set is
\(\{0,\pi\}^4\), containing exactly sixteen isolated points. At every zero,

\[
 \sin^2y+\frac13\sin^4y
 =y^2-\frac8{45}y^6+O(y^8).
\]

The quartic jet cancels exactly, so every point has the repaired local form.
At \(x=(\pi/2,0,0,0)\), exact differentiation gives

\[
 F_{16}=\frac43,\qquad
 \Delta F_{16}=\frac83,\qquad
 |\nabla F_{16}|^2=0,\qquad
 q_0=-F_{16}\Delta F_{16}+2|\nabla F_{16}|^2=-\frac{32}{9}.
\]

This fixture independently checks that the limiting scalar \(q_0\) is not
identically zero, although the general proof below does not need to select a
regular point.

## Shrinking endpoint and additive concentration

Put \(h_m=m+F\) and

\[
 q_m=R_m/\Omega_m^2=-h_m\Delta F+2|\nabla F|^2,
 \qquad E_m=\operatorname{div}(h_m^{-2}\nabla q_m).
\]

The repaired jet gives, at each puncture,

\[
 q_0=O(r^6),\qquad R_0=O(r^2),\qquad E_0=O(1).
\]

Splitting each puncture at \(r\sim\sqrt m\) shows that its core contribution
to \(\|E_m-E_0\|_2^2\) tends to zero; outside the cores ordinary dominated
convergence applies. Hence \(E_m\to E_0\) strongly in \(L^2\).

The residual has a concentrating radial core. Disjoint neighborhoods make
the concentrations additive:

\[
 \|R_m\|_2^2\longrightarrow
 |Z|\frac{32\pi^2}{3}+\|R_0\|_2^2.
\]

For the crystal, the concentrated part is \(512\pi^2/3\).

## Why the limiting Euler field cannot vanish

Assume \(E_0=0\). Multiplying
\(E_0=\operatorname{div}(F^{-2}\nabla q_0)\) by \(q_0\) and integrating on
the punctured torus gives

\[
 \int F^{-2}|\nabla q_0|^2=0.
\]

The boundary terms vanish because \(q_0=O(r^6)\) and
\(F^{-2}\nabla q_0=O(r)\). Thus \(q_0\) is constant. It tends to zero at
every puncture, so \(q_0=0\), hence \(R_0=0\) and
\(\Omega_0=1/F\) is harmonic off \(Z\).

This is impossible. Near each puncture \(\Omega_0\sim r^{-2}\). On a small
inner boundary, with the outward normal of the punctured domain,

\[
 \int_{S^3_r}\partial_n(r^{-2})\,dS=4\pi^2.
\]

Every pole has the same positive flux. The finite sum cannot equal the zero
total flux required by the divergence theorem for a harmonic function on the
punctured torus. Therefore \(E_0\neq0\) and the shrinking endpoint of \(Q_F\)
is positive.

## Finite and weak-field parameters

For finite \(m>0\), if \(E_m=0\), testing by
\(q=R/\Omega^2\) forces \(q=c\). Then
\(\Delta\Omega=c\Omega^3\); periodic integration gives \(c=0\), and
\(\Omega\) would be constant. This excludes an interior zero for every
nonconstant member of the family.

At the weak-field endpoint,

\[
 R_m=-\frac{\Delta F}{m}+O(m^{-2}),\qquad
 E_m=-\frac{\Delta^2F}{m}+O(m^{-2}).
\]

For the crystal,

\[
 \sin^2x+\frac13\sin^4x
 =\frac58-\frac23\cos2x+\frac1{24}\cos4x.
\]

Fourier orthogonality therefore gives

\[
 Q_{F_{16}}(\infty)
 =\frac{2^8(2/3)^2+4^8(1/24)^2}
        {2^4(2/3)^2+4^4(1/24)^2}
 =\frac{512}{17}>0.
\]

Compactifying \(m\) by \(t=m/(1+m)\) extends \(Q_F\) to a continuous positive
function on \([0,1]\). Its minimum is the claimed \(c_F>0\).

## Meaning for the barrier

The concentration branch has become narrower. A single repaired bubble and
now every fixed finite repaired multibubble family fail as collapse
mechanisms. Remaining possibilities include:

- a bubble count growing with volume;
- same-point bubble towers or neck regions;
- nonspherical profiles not covered by the repaired jet;
- a delocalized transverse-current configuration.

This result is useful input to a concentration-compactness proof, but it is
not that proof. The direct analytic target remains a connection-corrected
Witten/Schur estimate or a controlled low-Rayleigh sequence. The already
nonuniform fixed-order perturbative expansion should not be used as a
substitute for that nonperturbative step.

## Boundaries

No common lower bound over all \(F\), growing-bubble-gas theorem, all-field
gradient inequality, Witten/Poincare theorem, interacting Gibbs \(H^{-1}\)
estimate, continuum measure, Born rule, Krein reconstruction, or
LORENTZIAN-CAUSAL claim is established.

## Verification

~~~bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_finite_multibubble_compactness.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_finite_multibubble_compactness.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_finite_multibubble_compactness
~~~

The producer check, independent verifier, and eleven focused tests passed in
0.03, 0.09, and 0.11 seconds, using at most 20,548, 30,220, and 30,608 KiB
respectively. Exact planning and higher-tier dispositions are recorded in the
certificate receipt. The two direct predecessor verifiers passed in 0.10 and
0.11 seconds. The planning import folded 1,654 nodes with no invalid item or
malformed event in 6.51 seconds under a 300 MiB Go memory limit. Tier 3 was not
run because this is a fixed-family compactness result, not an all-field
Witten/\(H^{-1}\) promotion, freeze, or release.
