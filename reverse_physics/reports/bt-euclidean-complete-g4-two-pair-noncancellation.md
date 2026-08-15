# BT complete-$g^4$ two-pair noncancellation

## Result

Certificate `REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_TWO_PAIR_NONCANCELLATION_V1` closes the comparison left open by the two-pair normal-form certificate:

$$
c_4<-0.01613,\qquad 0<c_7<0.016103194,\qquad c_4+c_7<0.
$$

This establishes a strictly negative leading two-loop power coefficient. It does not establish the sign or scaling of complete $M_4$, because the subleading two-loop remainder and lower-loop recombination remain uncontrolled.

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

## Sharp lattice dispersion theorem

For $q+r+s=0$ componentwise, set $A=\omega(q)$, $B=\omega(r)$, and $C=\omega(s)$. Then

$$
\left\|A\sin q+B\sin r+C\sin s\right\|^2\leq 9ABC.
$$

The constant nine is sharp in the collinear all-soft limit.

In one coordinate put $a=2-2\cos q_\mu$, and define $b,c$ cyclically. The global square roots $\sqrt A,\sqrt B,\sqrt C$ obey the triangle inequalities because

$$
\|e^{i(q+r)}-1\|
\leq \|e^{iq}(e^{ir}-1)\|+\|e^{iq}-1\|
=\sqrt B+\sqrt A.
$$

For fixed $A,B$, the difference between $3(BCa+CAb+ABc)$ and
$(A\sin q_\mu+B\sin r_\mu+C\sin s_\mu)^2$ is a concave quadratic in $C$. It is enough to check the endpoints $C=(\sqrt A\pm\sqrt B)^2$.

Write $A=x^2$, $B=y^2$, and $m=(x^2,xy,y^2)$. At either endpoint the remainder is

$$
m^T(R_\epsilon-\ell_\epsilon\ell_\epsilon^T)m,
\qquad
R_\epsilon=3\begin{pmatrix}
b&\epsilon b&0\\
\epsilon b&a+b+c&\epsilon a\\
0&\epsilon a&a
\end{pmatrix}.
$$

The minus case is a diagonal congruence of the plus case. The principal minors of $R_+/3$ are

$$
b,\ a+b+c,\ a,\ b(a+c),\ ab,\ a(b+c),\ abc,
$$

so $R_+$ is positive semidefinite. For positive $a,b,c$, the rank-one downdate criterion becomes

$$
\ell_+^T R_+^{-1}\ell_+
=\frac13\left[
\frac{(\sin q+\sin r)^2}{c}
+\frac{(\sin q+\sin s)^2}{b}
+\frac{(\sin r+\sin s)^2}{a}
\right]\leq1.
$$

The three ratios are squares of half-angle cosines. Zero denominators follow by continuity. Summing the scalar inequality over four axes gives

$$
3ABC\sum_\mu\left(\frac{a_\mu}{A}+\frac{b_\mu}{B}+\frac{c_\mu}{C}\right)=9ABC.
$$

## From the theorem to $c_7$

Axis symmetry and the certified collapsed pair-7 numerator give

$$
c_7=\frac13\iint
\frac{\|A\sin q+B\sin r+C\sin s\|^2}{A^2B^2C^2}
\leq3J_3,
$$

where

$$
J_3=\iint\frac{dq\,dr}{\omega(q)\omega(r)\omega(q+r)}
=\sum_{x\in\mathbb Z^4}G(x)^3.
$$

Let $A_4=G(0)=\int1/\omega$ and $h=1/\omega-A_4$. Hausdorff--Young on the nonzero Fourier coefficients of $h$ yields

$$
J_3\leq A_4^3+M^2,
\qquad M=\int |1/\omega-A_4|^{3/2}.
$$

## Exact outward calculation

The calculation partitions $[0,\pi]^4$ into 96 equal intervals per axis and replaces only the singular origin box by a $16^4$ refinement. Alternating rational Taylor series enclose $4\sin^2(k/2)$ at every endpoint. The result is rounded outward to 60-bit dyadics. Reciprocals and $3/2$ powers use integer division and integer square root.

The lower enclosure for $A_4$ uses 300 nonnegative even-return terms of the four-dimensional nearest-neighbour walk. The unresolved refined origin box uses

$$
\omega(k)\geq\frac4{\pi^2}\|k\|^2
$$

and an enclosing positive-orthant ball. Every claim decision is rational or integer. The certified bounds are

$$
A_4<0.158075512186,\qquad M<0.037653168530,
$$

and therefore

$$
c_7\leq3(A_4^3+M^2)<0.016103194<0.01613.
$$

## Boundaries and next gate

This does not establish a tuned uniform bound on the subleading two-loop remainder, the lower-loop recombination, complete $M_4$ asymptotics, a nonperturbative center/score estimate, the actual interacting $H^{-1}$ second moment, a continuum measure, a Born rule, Krein reconstruction, or a Lorentzian theory.

The next calculation is to restore the lower-loop order-$g^4$ pieces and control the subleading remainder on the tuned branch.

## Verification

```sh
ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_two_pair_noncancellation.py --check
ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_two_pair_noncancellation_decision.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_two_pair_noncancellation.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_two_pair_noncancellation
```

Tier 0 and Tier 1 are sufficient because this adds a content-addressed `EUCLIDEAN-SPECTRAL` certificate downstream of unchanged inputs. It changes no shared core algebra, freeze, classical import, or Lorentzian object.

## Verification receipt

All Python calculations ran under a 500 MB virtual-memory cap; the planning import ran with `GOMEMLIMIT=300MiB`.

- Tier 0: all three changed Python sources compiled, the schema and structured data parsed, two bounded `pdflatex` passes produced a 56-page PDF of 658,309 bytes, and the scoped diff was checked for whitespace errors.
- Tier 1: the exact producer check passed in 5.53 s at 21,300 KB peak; certificate projection passed in 0.04 s at 20,252 KB; the independently enumerated verifier passed in 16.20 s at 29,972 KB; all 11 focused and mutation tests passed in 16.25 s at 31,188 KB. The Paper 21 claim map regenerated and its independent boundary verifier passed.
- The planning import accepted 1,624 nodes with zero invalid items and zero malformed events in 7.6 s.
- The read-only Science Forge shadow rail exited advisory-zero but reported two pre-existing/non-scoped findings rather than a pass: its bridge manifest resolves into the `bp2transformer` tree and cannot import `sympy`, and its July 19 corpus baseline counts 976 certificates versus the current 1,714. Diagnostics are preserved at `/tmp/sf-shadow.fl4vnw`; neither finding is used as evidence for this result.
- Tier 2 did not require rebuilding upstream certificates: their content hashes are unchanged, while this certificate independently reconstructs the complete new dispersion and outward-integration chain.
- Tier 3 was not run because this is not a freeze, release, change to shared core algebra, continuum construction, quantum-master-equation promotion, or Lorentzian lifecycle promotion.

A skipped higher tier is not a pass. The exact reproduction and verification commands are listed above.
