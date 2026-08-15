# BT complete-g4 linear bounds for pairs 3 and 6

Certificate:
REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_LINEAR_PAIR_BOUNDS_V1

Dependency tags: LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL

Lifecycle:
TWO_LINEAR_PAIR_BOUNDS_PROVED_TWO_PAIR_POWER_GATE_OPEN

## Result

Inversion pairs 3 and 6 cannot contribute to the leading
\(N\omega_p\asymp L^2\) coefficient. For every integer \(L\ge5\),

\[
 |I_3(L)|\le 5772060\pi^3L
\]

and

\[
 |I_6(L)|\le15360\pi^3L
 \left\{\frac{11}{16}+\frac12\log\lfloor L/2\rfloor\right\}.
\]

Thus pair 3 is \(O(L)\), pair 6 is \(O(L\log L)\), and both are
\(o(N\omega_p)\). Together with the preceding bounds for pairs 1, 2, and 5,
five of the seven inversion pairs are now rigorously absent from the leading
power coefficient. The power decision has reduced to the signed competition
between negative pair 4 and positive pair 7.

These estimates do not prove tuned-\(g_L^4\) uniformity. Multiplication by
\(g_L^4=O(\log^{-2}L)\) leaves upper bounds of order
\(L/\log^2L\) and \(L/\log L\). A growing upper bound proves neither
boundedness nor divergence.

## All-leg quintic estimate

For a set \(S\) of lattice momenta, the directed-edge inclusion-exclusion
block is a sum over four axes and two edge orientations. Each edge factor on
leg \(k_i\) is bounded by \(\sqrt{\omega_{k_i}}\), hence

\[
 |B(S)|\le8\prod_{i\in S}\sqrt{\omega_{k_i}}.
\]

The quintic kernel contains five \(1|4\) and ten \(2|3\) partitions. Each
block product is bounded by \(64\prod_{i=1}^5\sqrt{\omega_{k_i}}\), so

\[
 \boxed{|K_5(k_1,\ldots,k_5)|
 \le\frac{15\cdot64}{5!}\prod_i\sqrt{\omega_{k_i}}
 =8\prod_i\sqrt{\omega_{k_i}}.}
\]

The verifier recomputes the partition count and rational coefficient.

## Pair 6

The pair-6 representative is

\[
 I_6=\frac{180}{N}\sum_{q,r}
 \frac{K_3(-q-p,p,q)K_5(-q,-r,-p,r,q+p)}
 {\omega_r^2\omega_q^2\omega_{q+p}^2}.
\]

Apply the cubic estimate
\(|K_3(-q-p,p,q)|\le(2/3)\omega_p\omega_q\) and the all-leg
quintic estimate. The two \(r\)-legs in \(K_5\) provide one full
\(\omega_r\), leaving

\[
 |I_6|\le960\frac{\omega_p^{3/2}}N
 \left(\sum_{r\ne0}\frac1{\omega_r}\right)
 \left(\sum_{q\ne0,-p}
 \frac1{\sqrt{\omega_q}\omega_{q+p}^{3/2}}\right).
\]

The predecessor certificates give \(G_1(L)\le2N\) and

\[
 J_L\le NB_L,\qquad
 B_L=\frac{11}{16}+\frac12\log\lfloor L/2\rfloor.
\]

Finally \(\omega_p^{3/2}\le8\pi^3/L^3\) and \(N=L^4\), proving the
displayed \(15360\pi^3LB_L\) bound.

## Pair 3

Put \(s=q+r\). Pair 3 is

\[
 I_3=-\frac{432}{N}\sum_{q,r}
 \frac{
 K_3(-s,-p,s+p)K_3(-s,r,q)K_4(-s-p,p,r,q)}
 {\omega_r^2\omega_q^2\omega_s^2\omega_{s+p}^2}.
\]

Select \(\omega_p\omega_s\) from the first cubic,
\(\omega_s\omega_q\) from the second, and use the all-leg quartic bound.
The two \(\omega_s\) factors cancel the \(s\) propagator exactly. The
coefficient is

\[
 432\left(\frac23\right)^2\frac{56}{3}=3584,
\]

and the remaining sum is

\[
 |I_3|\le3584\frac{\omega_p^{3/2}}N S_3(L),
\qquad
 S_3(L)=\sum_{q,r}
 \frac1{\sqrt{\omega_q}\omega_r^{3/2}
 \omega_{q+r+p}^{3/2}}.
\]

Zero covariance modes are omitted before this cancellation and may be
excluded from the upper sum.

## Exact torus convolution lemma

Let \(\rho(k)\) be the max norm of the centered torus representative. The
four-dimensional shell of radius \(m\) has

\[
 (2m+1)^4-(2m-1)^4=64m^3+16m\le80m^3
\]

sites. Define

\[
 C_{33}(x)=\sum_{r\ne0,-x}
 \frac1{\rho(r)^3\rho(r+x)^3}.
\]

For \(M=\rho(x)\ge1\), split the sum into four regions:

1. \(\rho(r)\le M/2\);
2. \(\rho(r+x)\le M/2\);
3. both distances exceed \(M/2\), with \(\rho(r)\le2M\);
4. \(\rho(r)>2M\).

The first two regions contribute at most \(320/M^2\) each. The third
contains at most \((4M+1)^4\le625M^4\) sites and contributes at most
\(40000/M^2\). In the fourth region,
\(\rho(r+x)>\rho(r)/2\); the shell tail contributes at most
\(80/M^2\). At \(x=0\), the bound
\(80\sum m^{-3}<120\) is stronger. Hence

\[
 C_{33}(x)\le\frac{40720}{\max\{1,\rho(x)\}^2}.
\]

For the outer sum, at most \(162m^3\) sites satisfy

\[
 \min\{\rho(q),\max(1,\rho(q+p))\}=m;
\]

the extra two cover the exceptional center at \(q=-p\). Since
\(\lfloor L/2\rfloor\le L/2\),

\[
 \sum_{q\ne0}\frac{C_{33}(q+p)}{\rho(q)}
 \le40720\cdot162\lfloor L/2\rfloor
 \le3298320L.
\]

The dispersion estimate
\(\omega(k)\ge16\rho_2(k)^2/L^2\), together with
\(\rho_2\ge\rho\), therefore gives

\[
 S_3(L)\le\frac{L^7}{4\cdot64\cdot64}(3298320L)
 =\frac{3298320}{16384}N^2.
\]

Substitution and \(\omega_p^{3/2}\le8\pi^3/L^3\) produce
\(5772060\pi^3L\).

## Consequence and next gate

The lower dispersion bound
\(\omega_p\ge16/L^2\) gives \(N\omega_p\ge16L^2\). Therefore both
new bounds divided by \(N\omega_p\) tend to zero. The only terms still
capable of carrying a nonzero leading coefficient are

\[
 I_4(L)+I_7(L),
\]

where \(I_4\) is strictly negative with a certified quadratic-magnitude lower
bound and \(I_7\) is a positive quartic square. The next calculation must put
their one-soft and hard-hard limits on one normalization and decide their
common coefficient before taking absolute values.

## Supporting analysis of the two-pair gate

The next coefficient has a concrete candidate normal form. This subsection is
derivation guidance, not part of the certified theorem.

Let

\[
 {\cal A}_4=\int_{[-\pi,\pi]^4}\frac{d^4k}{(2\pi)^4\,\omega(k)}.
\]

For a fixed nonzero integer soft mode \(n\), expansion of the exact paired
quartic identity gives the candidate limit

\[
 \frac{Y_L(\theta n)}{N\theta^2}
 \longrightarrow \frac{{\cal A}_4}{3}|n|^2,
 \qquad \theta=\frac{2\pi}{L}.
\]

The simplification uses lattice symmetry and periodic integration by parts:

\[
 \int\frac{\omega_1}{\omega}=\frac14,\qquad
 \int\frac{4\sin^2k_1}{\omega^2}=2{\cal A}_4-\frac14.
\]

Together with

\[
 \theta^{-4}K_3(\theta e_1,\theta n,-\theta(e_1+n))
 \longrightarrow-\frac23\bigl(|n|^2-n_1^2\bigr),
\]

this predicts the pair-4 coefficient

\[
 c_4=-\frac{2{\cal A}_4}{\pi^4}
 \sum_{n\in\mathbb Z^4\setminus\{0,-e_1\}}
 \frac{(|n|^2-n_1^2)^2}
 {|n|^6|n+e_1|^4}.
\]

The integer sum is absolutely convergent. A noncertifying binary64 cube
truncation through radius 80 gives approximately \(5.1431\) for the sum and
\(c_4\approx-0.01636\) when the standard numerical value of
\({\cal A}_4\) is inserted. These numbers locate the proof target only.

Pair 7 has a complementary hard--hard candidate. Define

\[
 {\cal D}_4(q,r)=
 \left.\frac{d}{d\theta}
 K_4(-q-r-\theta e_1,\theta e_1,r,q)\right|_{\theta=0}.
\]

Differentiating the directed-edge partition formula before estimating gives
an explicit six-term expression. If
\({\cal D}(S)=\partial_\theta B(\{\theta e_1\}\cup S)|_{\theta=0}\)
and \(s=-q-r\), then

\[
\begin{split}
24{\cal D}_4={}&
{\cal D}(r,q)\omega_s+{\cal D}(s,q)\omega_r
+{\cal D}(s,r)\omega_q\\
&+{\cal D}(s)B(r,q)+{\cal D}(q)B(s,r)
+{\cal D}(r)B(s,q).
\end{split}
\]

The candidate positive coefficient is

\[
 c_7=48\int\!\!\int
 \frac{{\cal D}_4(q,r)^2}
 {\omega_q^2\omega_r^2\omega_{q+r}^2}
 \frac{d^4q\,d^4r}{(2\pi)^8}.
\]

A deterministic supporting Monte Carlo evaluation placed this near
\(9\times10^{-4}\), while the existing finite-volume values approach from
above. Neither numerical estimate proves either limit, controls the
soft/hard overlap, or proves \(c_4+c_7\ne0\). The proof gate is now sharply
defined: establish both limits with a common region decomposition and obtain
disjoint exact bounds for the two constants.

## Claim boundary

This certificate does not establish boundedness or divergence after tuned
\(g_L^4\) multiplication, the pair-4/pair-7 coefficient, the sign or scaling
of the complete seven-kernel sum or complete \(M_4\), the nonperturbative
score, or the actual interacting \(H^{-1}\) moment. It supplies no continuum
identification, Born rule, Krein reconstruction, or LORENTZIAN-CAUSAL result.

## Verification

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_linear_pair_bounds.py --check
    ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_linear_pair_bounds_decision.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_linear_pair_bounds.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_linear_pair_bounds

## Verification receipt

The following deterministic checks were run with a 500 MB virtual-memory cap
where Python was involved:

- Tier 0: the six changed Python sources compiled in 0.05 s (22,052 KB peak);
  all changed JSON files parsed; the scoped diff passed `git diff --check`.
- Tier 1: the data producer check passed in 0.04 s (20,584 KB), the certificate
  projection check in 0.04 s (20,232 KB), the independent verifier in 0.10 s
  (29,812 KB), and all 13 unit and mutation tests in 0.14 s (30,580 KB).
- Direct Paper 21 consumers passed: claim-map regeneration check in 0.08 s
  (31,620 KB), independent claim-map verification in 0.08 s (28,044 KB), and
  two LaTeX passes in 0.82 s (53,716 KB) and 0.81 s (53,516 KB), producing a
  56-page, 656,414-byte PDF.
- Tier 2: the predecessor representatives and hashes, exact convolution
  reconstruction, and append-only event import were checked. The planning
  import accepted 1,622 nodes with zero invalid or malformed nodes in 7.48 s
  (216,796 KB). An earlier launch inherited the Python 500 MB virtual-address
  cap and failed before the Go runtime initialized; it was not counted as a
  pass, and the successful fresh-shell run used `GOMEMLIMIT=300MiB`.
- Tier 3 was not run because this working-draft checkpoint does not promote a
  freeze, release, shared-core theorem, or continuum, quantum, or Lorentzian
  lifecycle state.

A skipped higher tier is not recorded as a pass. The exact commands for the
certificate rail are listed above; Paper 21 was checked with its generator's
`--check` mode and independent verifier, and the planning tree with the
repository planning importer.
