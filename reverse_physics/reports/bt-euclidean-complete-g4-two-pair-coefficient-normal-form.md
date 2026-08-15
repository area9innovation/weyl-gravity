# BT complete-g4 two-pair coefficient normal form

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_COEFFICIENT_NORMAL_FORM_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

Lifecycle: `TWO_PAIR_COEFFICIENT_NORMAL_FORMS_PROVED_COMPARISON_OPEN`

## Result

The two surviving inversion pairs now have rigorous limits on the same
normalization. With

\[
 p_L=\frac{2\pi}{L}e_1,\qquad N=L^4,
\]

there are finite constants \(c_4<0<c_7\) such that

\[
 \frac{I_4(L)}{N\omega(p_L)}\longrightarrow c_4,
 \qquad
 \frac{I_7(L)}{N\omega(p_L)}\longrightarrow c_7.
\]

Pair 4 has the explicit soft-lattice normal form

\[
 c_4=-\frac{2\mathcal A_4}{\pi^4}\mathcal S_4,
\]

where

\[
 \mathcal A_4=\int_{[-\pi,\pi]^4}
 \frac{d^4k}{(2\pi)^4\omega(k)}
\]

and

\[
 \mathcal S_4=
 \sum_{n\in\mathbb Z^4\setminus\{0,-e_1\}}
 \frac{(|n|^2-n_1^2)^2}{|n|^6|n+e_1|^4}.
\]

Exact rational truncations, with no floating-point input, prove

\[
 \boxed{c_4<-0.01613.}
\]

Pair 7 has the explicit positive Brillouin-zone normal form

\[
 c_7=48\int\!\!\int
 \frac{\mathcal D_4(q,r)^2}
 {\omega_q^2\omega_r^2\omega_{q+r}^2}
 \frac{d^4q\,d^4r}{(2\pi)^8},
\]

with the unexpectedly simple numerator

\[
 \boxed{
 \mathcal D_4(q,r)=\frac16\left[
 \omega_q\sin q_1+\omega_r\sin r_1
 +\omega_s\sin s_1\right],\qquad s=-q-r.}
\]

This is a real reduction of the barrier: the large-volume problem is no
longer a cancellation between two finite-volume diagram sums. It is the
comparison of one absolutely convergent integer sum with one positive finite
eight-dimensional integral. Noncancellation is not yet proved.

## Pair-4 limit

The finite-volume representative is

\[
 I_4=-\frac{216}{N}\sum_{q\ne0,-p}
 \frac{K_3(p,q,-p-q)^2Y_L(q)}
 {\omega_q^4\omega_{p+q}^2}.
\]

For fixed \(n\in\mathbb Z^4\setminus\{0,-e_1\}\), put
\(q=(2\pi/L)n\). The exact cubic formula gives

\[
 \theta^{-4}K_3(\theta e_1,\theta n,-\theta(n+e_1))
 \longrightarrow-\frac23(|n|^2-n_1^2).
\]

The paired-quartic identity gives

\[
 \frac{Y_L(\theta n)}{N\theta^2}
 \longrightarrow\frac{\mathcal A_4}{3}|n|^2.
\]

The constant cancellation in this limit uses

\[
 \int\frac{\sin^2k_1}{\omega(k)^2}
 =\frac{\mathcal A_4}{2}-\frac1{16},
 \qquad
 \int\frac{\omega_1(k)}{\omega(k)}=\frac14.
\]

After the common \(N\omega(p_L)\) normalization, the cubic soft-leg bound and
the tadpole product bound dominate the \(n\)-summand by a constant times

\[
 \frac1{\rho(n)^2\max\{1,\rho(n+e_1)\}^4}.
\]

Its four-dimensional shell tail is summable, which justifies passage from
the torus sum to the displayed infinite sum.

## Exact negative gap

Write

\[
 \omega(k)=8\left(1-\frac14\sum_{j=1}^4\cos k_j\right).
\]

The geometric series and Fourier orthogonality give the nonnegative random
walk expansion

\[
 \mathcal A_4=\frac18\sum_{m\ge0}\Pr(S_m=0).
\]

The producer independently counts every four-dimensional nearest-neighbour
return through 60 steps. Retaining those nonnegative terms gives

\[
 \mathcal A_4>0.1541096933\ldots.
\]

It also sums the positive terms of \(\mathcal S_4\) exactly over the cube
\([-10,10]^4\), obtaining a rational lower bound larger than
\(5.1087882720\). Combining those fractions with the rigorous elementary
bound \(\pi<22/7\) yields

\[
 \frac{2\mathcal A_4\mathcal S_4}{\pi^4}
 >0.016139099267\ldots>0.01613.
\]

The verifier reconstructs the return probabilities, the 194,479 nonzero
cube terms, the rational coefficient, and a Machin-series enclosure proving
the stated upper bound on \(\pi\).

## Pair-7 collapse

For the directed-edge block define

\[
 \mathcal D(S)=
 \left.\frac{d}{d\theta}
 B(\{\theta e_1\}\cup S)\right|_{\theta=0}.
\]

Writing \(s=-q-r\), direct differentiation of the seven quartic partitions
first gives

\[
\begin{split}
24\mathcal D_4={}&
\mathcal D(r,q)\omega_s+\mathcal D(s,q)\omega_r
+\mathcal D(s,r)\omega_q\\
&+\mathcal D(s)B(r,q)+\mathcal D(q)B(s,r)
+\mathcal D(r)B(s,q).
\end{split}
\]

Momentum conservation implies

\[
 \mathcal D(r,q)=\mathcal D(s,q)=\mathcal D(s,r)
 =2(\sin q_1+\sin r_1+\sin s_1),
\]

while

\[
 \mathcal D(q)=-2\sin q_1,
 \qquad B(r,q)=\omega_r+\omega_q-\omega_s,
\]

and cyclically. Substitution cancels all cross terms and leaves

\[
 24\mathcal D_4=4(
 \omega_q\sin q_1+\omega_r\sin r_1+\omega_s\sin s_1),
\]

which proves the boxed formula.

The one-soft all-leg estimate

\[
 |K_4(p,q,r,s)|\le\frac{14}{3}
 \sqrt{\omega_p\omega_q\omega_r\omega_s}
\]

dominates the normalized Riemann summand by a constant multiple of
\(1/(\omega_q\omega_r\omega_s)\). This is integrable in eight dimensions;
for example, Young's convolution inequality reduces it to the finite
\(L^{3/2}\) norm of \(1/\omega\). Dominated convergence therefore proves the
pair-7 limit. Its integrand is nonnegative and is nonzero at
\(q=r=(\pi/2)e_1\), so \(c_7>0\).

## Remaining comparison

It is now sufficient to prove

\[
 c_7<0.01613.
\]

One promising route uses axis symmetry. If the sharp lattice vector
inequality

\[
 \sum_{\mu=1}^4
 (\omega_q\sin q_\mu+\omega_r\sin r_\mu+\omega_s\sin s_\mu)^2
 \le9\omega_q\omega_r\omega_s
\]

can be proved, then \(c_7\le3\mathcal A_3\), where

\[
 \mathcal A_3=\int\!\!\int
 \frac{d^4q\,d^4r}{(2\pi)^8\omega_q\omega_r\omega_s}.
\]

Centering \(1/\omega\) before applying Young's inequality then reduces the
remaining bound to four-dimensional scalar quadrature. This route is the next
proof target. The vector inequality is not certified and is not used by this
certificate.

## Claim boundary

This result does not establish \(c_4+c_7\ne0\), tuned-\(g_L^4\) boundedness or
divergence, the sign or scaling of complete \(M_4\), a nonperturbative Gibbs
score estimate, or the actual interacting \(H^{-1}\) moment. It establishes
no tightness or continuum identification and supplies no Born rule, Krein
reconstruction, or `LORENTZIAN-CAUSAL` result.

## Verification

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_two_pair_coefficient_normal_form.py --check
    ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_two_pair_coefficient_normal_form_decision.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_two_pair_coefficient_normal_form.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_two_pair_coefficient_normal_form

## Verification receipt

All Python checks ran under a 500 MB virtual-memory cap.

- Tier 0: the six changed Python sources compiled in 0.05 s (21,984 KB peak),
  every changed JSON and schema parsed, two bounded LaTeX passes completed in
  0.78 s (53,932 KB) and 0.83 s (53,540 KB), and the scoped staged diff passed
  `git diff --check`. The PDF has 56 pages and is 657,236 bytes.
- Tier 1: the deterministic producer check passed in 0.53 s (20,736 KB), the
  certificate projection in 0.03 s (19,824 KB), the independent verifier in
  0.64 s (29,576 KB), and all 12 unit and adversarial-mutation tests in 0.66 s
  (30,716 KB). The Paper 21 claim-map regeneration and independent checks
  passed in 0.06 s (31,752 KB) and 0.07 s (28,404 KB).
- Tier 2: upstream pair representatives and hashes, the exact soft cubic and
  tadpole ledgers, all return probabilities through 60 steps, all 194,479
  retained integer-sum terms, the Machin enclosure for \(\pi<22/7\), and the
  six-to-three-term quartic derivative collapse were independently rebuilt.
  The planning import accepted 1,623 nodes with zero invalid or malformed
  nodes in 6.33 s (251,068 KB) under `GOMEMLIMIT=300MiB`.
- Tier 3 was not run because this working-draft checkpoint does not promote a
  freeze, release, shared-core theorem, or continuum, quantum, or Lorentzian
  lifecycle state.

A skipped higher tier is not recorded as a pass. The exact certificate commands
are listed above; the claim map used its generator's `--check` mode and its
independent verifier, and planning used the repository Science Forge importer.
