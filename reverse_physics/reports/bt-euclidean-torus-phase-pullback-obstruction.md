# BT torus phase-pullback obstruction

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_PHASE_PULLBACK_OBSTRUCTION_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`

Lifecycle:
`CYCLE_PHASE_PULLBACK_ROUTE_RULED_OUT_GENUINE_TORUS_CORRECTOR_GATE_OPEN`

## Result in ordinary language

The low-divergence cycle hierarchy cannot be converted into a four-dimensional
counterexample merely by wrapping the same profile around an axial, diagonal,
or helical direction of the torus.

For a positive field (u) on a cycle (C_L), define on (T_L^4)

\[
 \Omega(x)=u(x_1+\cdots+x_k\bmod L),\qquad 1\leq k\leq4.
\]

For (k\geq2), this is genuinely mixed in the original coordinates, but all
of its information still passes through one cyclic phase.  Exact neighbor
counting shows that its complete BT residual-gradient quotient is (k^2)
times the cycle quotient.  Diagonal wrapping makes the candidate more
coercive, not less.

There is a second important scale comparison.  The adopted hierarchy on
(C_{4m^4+2}) has quotient of exact order (m^{-6}):

\[
 {1\over144m^6}\leq
 {\|g_m\|_2^2\over\|\rho_m\|_2^2}
 \leq {1960\over m^6},
\]

with the lower bound valid for (m\geq4) and the predecessor's upper bound
valid for (m\geq8).  The free bilaplacian scale on the same side length is
of order (L^{-4}=m^{-16}).  Therefore every one-phase torus lift obeys

\[
 {Q_{T_L^4}\over\omega_L^2}
 \geq {k^2m^{10}\over9\pi^4}\longrightarrow\infty.
\]

The cycle result remains a valid obstruction to a graph-generic
diameter-scale proof.  It is not remotely a low-Rayleigh family at the torus
free scale.

## 1. Exact phase-pullback identity

Let

\[
 \chi_k(x)=x_1+\cdots+x_k\pmod L
\]

and let the remaining (4-k) coordinates be inactive.  On the cycle put

\[
 \rho_t={u_{t+1}\over u_t}+{u_{t-1}\over u_t}-2,
\]

\[
 j_t=\rho_t{u_{t+1}\over u_t}
      -\rho_{t+1}{u_t\over u_{t+1}},
 \qquad h_t=j_{t-1}-j_t.
\]

Each active positive direction advances (chi_k) by one and each active
negative direction retreats it by one.  Every inactive neighbor has the same
field value.  The inactive residual contributions vanish, while there are
exactly (k) copies of each active cycle contribution.  Hence

\[
 r_T(x)=k\rho_{chi_k(x)}.
\]

Using the complete log-field action gradient, including the reverse-current
term, the same multiplicity calculation gives

\[
 g_T(x)=k^2h_{chi_k(x)}.
\]

Every phase value has (L^3) preimages.  Consequently

\[
 \|r_T\|_2^2=L^3k^2\|\rho\|_2^2,
 \qquad
 \|g_T\|_2^2=L^3k^4\|h\|_2^2,
\]

and therefore

\[
 \boxed{Q_T=k^2Q_C.}
\]

The maximum nearest-neighbor contrast is unchanged: active edges reproduce a
cycle edge and inactive edges have ratio one.

## 2. Matching lower bound for the cycle hierarchy

Set (r=m^4) and use the predecessor's tent ratio list.  At the positive
ramp peak and its opposite inverse peak, the exact cycle currents satisfy

\[
 J_+=-J_-,\qquad J_+\geq {m^2\over4}\quad(m\geq4).
\]

Indeed, with (s=(m-1)/m^4), direct substitution at the positive peak gives

\[
 J_+=m\left(m-2+{1\over m-s}\right)
 -{m-s+m^{-1}-2\over m}.
\]

The last fraction is less than one, so
(J_+>m(m-2)-1\geq m^2/4) for (m\geq4).

The two peak currents are separated by two arcs, each of length (2m^4+1).
Applying Cauchy--Schwarz to the current change on both arcs gives

\[
 \|g\|_2^2
 \geq {8J_+^2\over2m^4+1}
 \geq {1\over6}.
\]

Every traversal ratio and its inverse lie between (m^{-1}) and (m), so
(|\rho_t|\leq2m).  Since (4m^4+2\leq6m^4),

\[
 \|\rho\|_2^2\leq24m^6.
\]

Division proves

\[
 \boxed{Q_C\geq {1\over144m^6}.}
\]

Together with the predecessor's (1960m^{-6}) upper bound, this identifies
the exact asymptotic power rather than merely bounding it from above.

## 3. Comparison with the four-torus infrared scale

For (L=4m^4+2),

\[
 \omega_L=4\sin^2(\pi/L),
 \qquad \omega_L^2\leq{16\pi^4\over L^4}.
\]

Using (L\geq4m^4) and the phase identity,

\[
 {Q_T\over\omega_L^2}
 \geq {k^2L^4\over2304\pi^4m^6}
 \geq {k^2m^{10}\over9\pi^4}.
\]

Thus axial ((k=1)), diagonal, and helical one-phase embeddings all diverge
after free-scale normalization.  Merely making the formula look
multidimensional does not create the transverse cancellation the programme
needs.

## 4. Exact evidence and independent rail

The producer stores exact rational hierarchy fixtures for (m=2,3,4),
including both peak currents, residual and gradient norms, the cycle quotient,
and the two-active-coordinate torus quotient.  A separate (4^4) fixture
enumerates every site for (k=1,2,3,4).

The independent verifier does not import the producer.  It reconstructs all
cycle fixtures from the ratio definition and directly enumerates the four
four-dimensional fields.  Mutation tests require rejection of altered
predecessor hashes, torus norms, scaling factors, lower bounds, research
dispositions, and dependency tags.

## 5. What remains live

The next negative candidate must not factor through one scalar cyclic phase.
It needs at least two independently varying phases or a genuine transverse
corrector capable of placing a large fraction of the canonical current in a
nearly solenoidal torus component.  The positive branch is the matching Hodge
question: use scalar compatibility and four-dimensional cut geometry to bound
that solenoidal fraction.

This certificate does not establish an all-field torus lower bound, exclude
multiphase correctors, prove Witten coercivity, decide the interacting
(H^{-1}) moment, construct a continuum measure or Born/Krein
interpretation, or establish anything `LORENTZIAN-CAUSAL`.

## Verification

Run sequentially under the 500 MB cap:

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_phase_pullback_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_phase_pullback_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_phase_pullback_obstruction
```
